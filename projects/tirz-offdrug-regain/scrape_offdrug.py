"""
Tirzepatide OFF-DRUG scrape — regain / maintenance / metabolism.

Goal: a large, varied corpus of PERSONAL off-drug experiences (Mounjaro,
Zepbound, grey-market tirz) to answer (1) do people regain, (2) does metabolism
get worse / do they become "dependent" — purely from Reddit.

Strategy to beat noise & bias and exceed the reta run's 320 threads:
  - FOUR query buckets, each tagged on every post it surfaces:
      regain   — stories of gaining it back
      maintain — stories of keeping it off (counter-bias to the regain crowd)
      metab    — appetite / hunger / food-noise / metabolism after stopping
      asks     — QUESTION / anchor threads ("has anyone stopped…?") that pull
                 dozens of high-quality personal replies in one place
  - WHOLESALE sweep of the graduate/maintenance subs (r/GLPGrad,
    r/GLP1microdosing, r/Maintenance) where ~every thread is an off-drug story.
  - Global dedupe by post id across every source; each post keeps the LIST of
    buckets that surfaced it (provenance) and its best query.

Everything is fetched through rss_scrape's proxied primitives (rotating
ISP/residential proxies, retry-on-fresh-proxy). No request ever goes direct.

CRASH-SAFE: nothing lives only in memory. The collected thread list is written
to the checkpoint the moment collection finishes, and comments are flushed to
disk (atomic temp-file rename) every CKPT_EVERY posts during the long
comment-fetch phase. Re-running RESUMES: already-fetched threads are loaded from
the checkpoint and skipped, so an interrupt costs at most a few posts.

Output: data/tirz_offdrug_full.{json,csv,md}  (same schema as rss_scrape).
Checkpoint: data/tirz_offdrug_full.json (the live JSON, rewritten as we go).
"""
import json
import os
import time
import urllib.parse
from collections import OrderedDict

import rss_scrape as rs

CAP = 500          # max unique threads to keep (we then fetch comments for all)
CKPT = "data/tirz_offdrug_full.json"
CKPT_EVERY = 10    # flush the full JSON to disk every N posts during comment fetch


def save_checkpoint(posts):
    """Atomically rewrite the checkpoint JSON (temp file + rename)."""
    os.makedirs("data", exist_ok=True)
    tmp = CKPT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(posts, f, ensure_ascii=False)
    os.replace(tmp, CKPT)


def load_checkpoint():
    """Return {id: post} from a prior run, or {} if none."""
    if not os.path.exists(CKPT):
        return {}
    try:
        with open(CKPT) as f:
            prev = json.load(f)
        return {p["id"]: p for p in prev}
    except (json.JSONDecodeError, KeyError):
        return {}

# Drug names are embedded in --sub all queries so site-wide relevance stays on
# topic (lesson from the test run: bare phrases drift into PCOS/misc subs).
BUCKETS = {
    "regain": [
        "tirzepatide stopped gained weight back",
        "Mounjaro regained weight after stopping",
        "Zepbound weight came back after stopping",
        "tirzepatide off the weight is coming back",
        "stopped Mounjaro gaining weight again",
        "Zepbound regain after quitting",
        "tirzepatide rebound weight after stopping",
        "gained it all back after Mounjaro",
        "stopped Zepbound and gaining",
    ],
    "maintain": [
        "maintained weight after stopping tirzepatide",
        "Mounjaro kept the weight off after stopping",
        "off Zepbound a year kept it off",
        "maintenance after stopping GLP-1 success",
        "stopped tirzepatide no regain",
        "weight stable after stopping Mounjaro",
        "graduated GLP-1 maintaining weight",
        "kept weight off after Zepbound",
    ],
    "metab": [
        "tirzepatide metabolism after stopping",
        "harder to lose weight after stopping Mounjaro",
        "appetite came back after stopping Zepbound",
        "food noise returned after tirzepatide",
        "hungrier after stopping Mounjaro",
        "gained back faster than I lost it Zepbound",
        "metabolism slower after stopping GLP-1",
        "heavier than before I started Mounjaro",
    ],
    "asks": [
        "has anyone stopped tirzepatide and kept it off",
        "did you regain after stopping Mounjaro",
        "what happened when you stopped Zepbound",
        "anyone successfully off GLP-1 long term",
        "months off GLP-1 update weight",
        "life after stopping tirzepatide",
        "stopping Mounjaro experiences regain",
        "reached goal weight then stopped tirzepatide",
    ],
}

# Subs where ~every thread is an off-drug / maintenance experience → sweep them
# wholesale (new + top of the year), tag as bucket "gradsub".
WHOLESALE_SUBS = ["GLPGrad", "GLP1microdosing", "Maintenance"]


def add_post(posts, bucket, query, eid, title, author, date, link, body):
    if not link or "/comments/" not in link:
        return
    pid = eid or link
    if pid in posts:
        p = posts[pid]
        if bucket not in p["buckets"]:
            p["buckets"].append(bucket)
        return
    posts[pid] = {
        "id": pid, "subreddit": link.split("/r/")[1].split("/")[0],
        "title": title, "author": author, "created": date, "url": link,
        "query": query, "buckets": [bucket], "body": body, "comments": [],
    }


def collect():
    posts = OrderedDict()

    # 1) Wholesale graduate/maintenance subs first (highest relevance density).
    for sub in WHOLESALE_SUBS:
        for feed in (
            f"https://www.reddit.com/r/{sub}/new.rss?limit=100",
            f"https://www.reddit.com/r/{sub}/top.rss?t=year&limit=100",
        ):
            xml = rs.fetch(feed)
            if not xml:
                print(f"  ! no data {feed}")
                continue
            before = len(posts)
            for e in rs.parse_entries(xml):
                add_post(posts, "gradsub", f"r/{sub}", *e)
            print(f"  r/{sub} [{feed.split('/')[-1].split('?')[0]}]: "
                  f"total {len(posts)} (+{len(posts) - before})")
            time.sleep(0.4)

    # 2) Bucketed site-wide searches.
    for bucket, queries in BUCKETS.items():
        for q in queries:
            if len(posts) >= CAP:
                break
            qenc = urllib.parse.quote(q)
            feed = (f"https://www.reddit.com/search.rss"
                    f"?q={qenc}&sort=relevance&t=year&limit=100")
            xml = rs.fetch(feed)
            if not xml:
                print(f"  ! no data [{bucket}] '{q}'")
                continue
            before = len(posts)
            for e in rs.parse_entries(xml):
                add_post(posts, bucket, q, *e)
            print(f"  [{bucket}] '{q[:42]}': total {len(posts)} "
                  f"(+{len(posts) - before})")
            time.sleep(0.4)

    return list(posts.values())[:CAP]


def fetch_comments_ckpt(posts):
    """Fetch comments per post via its .rss feed, flushing to disk as we go.

    Skips posts already marked 'fetched' (resume). Proxied via rs.fetch.
    """
    todo = [p for p in posts if not p.get("fetched")]
    print(f"Fetching comments: {len(todo)} to do, "
          f"{len(posts) - len(todo)} already done (resumed).")
    for i, p in enumerate(todo, 1):
        crss = p["url"].rstrip("/") + ".rss?limit=100"
        xml = rs.fetch(crss)
        if xml:
            for eid, title, author, date, link, body in rs.parse_entries(xml):
                if eid.startswith("t3_") or link == p["url"]:
                    continue
                if body and body[:120] == p["body"][:120]:
                    continue
                if body:
                    p["comments"].append({"id": eid, "author": author,
                                          "created": date, "url": link, "body": body})
        p["fetched"] = True
        if i % CKPT_EVERY == 0:
            save_checkpoint(posts)
            done = len(posts) - sum(1 for x in posts if not x.get("fetched"))
            print(f"  {done}/{len(posts)} posts fetched "
                  f"({sum(len(x['comments']) for x in posts)} comments) — checkpointed")
        time.sleep(0.4)
    save_checkpoint(posts)
    return posts


def main():
    started = time.time()
    prev = load_checkpoint()
    if prev:
        print(f"Resuming: {len(prev)} threads in checkpoint, "
              f"{sum(1 for p in prev.values() if p.get('fetched'))} already fetched.")

    print("Collecting off-drug threads (proxied, rotating)...")
    collected = collect()
    # Union freshly-collected threads with the checkpoint (keep prior comments).
    by_id = dict(prev)
    for p in collected:
        if p["id"] in by_id:
            # preserve any buckets discovered this run
            for b in p["buckets"]:
                if b not in by_id[p["id"]]["buckets"]:
                    by_id[p["id"]]["buckets"].append(b)
        else:
            by_id[p["id"]] = p
    posts = list(by_id.values())[:CAP]
    save_checkpoint(posts)   # thread list is now safe on disk before any comment fetch
    print(f"\n{len(posts)} unique threads (checkpointed). Fetching comments (proxied)...")

    fetch_comments_ckpt(posts)
    rs.write_outputs(posts, "tirz_offdrug_full")   # final json + csv + md
    ncom = sum(len(p["comments"]) for p in posts)
    print(f"\nDone in {time.time() - started:.0f}s. {len(posts)} threads, "
          f"{ncom} comments.\n  -> data/tirz_offdrug_full.{{json,csv,md}}")


if __name__ == "__main__":
    main()
