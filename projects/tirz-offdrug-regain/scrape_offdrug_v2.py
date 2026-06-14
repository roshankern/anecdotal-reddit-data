"""
Round 2 of the tirzepatide off-drug scrape — find NEW threads only, merge into
the same dataset (data/tirz_offdrug_full.json).

Diversity strategy (deliberately disjoint from round 1 to avoid re-pulling the
same threads):
  - NEW wholesale feeds: the big drug subs by TOP-of-all-time / top-of-year
    (their biggest "stopped / regain / maintenance" megathreads) — skipping the
    noisy new.rss active-user stream — plus deeper all-time top on the graduate
    subs we already know are gold, and r/loseit's all-time top.
  - NEW query angles we never mined: cost/insurance-forced stops, tolerance /
    "stopped working", long-haul (2-years-off) updates, lifting/recomp, set-point
    / appetite, and surgery/pregnancy pauses.

Reuses round 1's proxied, checkpointing machinery (scrape_offdrug helpers): the
existing 500 threads load from the checkpoint already marked `fetched` and are
SKIPPED — only newly-found threads get their comments fetched. Crash-safe/resumable
exactly as before. All requests proxied + rotating.
"""
import time
import urllib.parse
from collections import OrderedDict

import rss_scrape as rs
import scrape_offdrug as base

CAP_TOTAL = 1000      # dataset size after this run (≈500 existing + ≈500 new)
MAX_NEW = 520         # stop collecting once we have this many NEW threads

# sub -> list of feed suffixes (TOP feeds, not new.rss, for the active drug subs)
NEW_WHOLESALE = {
    "GLPGrad": ["top.rss?t=all&limit=100"],
    "GLP1microdosing": ["top.rss?t=all&limit=100"],
    "Zepbound": ["top.rss?t=year&limit=100", "top.rss?t=all&limit=100"],
    "Mounjaro": ["top.rss?t=year&limit=100", "top.rss?t=all&limit=100"],
    "tirzepatide": ["top.rss?t=year&limit=100", "top.rss?t=all&limit=100"],
    "Semaglutide": ["top.rss?t=year&limit=100", "top.rss?t=all&limit=100"],
    "Ozempic": ["top.rss?t=all&limit=100"],
    "loseit": ["top.rss?t=all&limit=100"],
}

NEW_BUCKETS = {
    "cost_stop": [
        "stopped Mounjaro because of cost gained weight",
        "lost insurance coverage Zepbound regained",
        "couldn't afford tirzepatide stopped weight back",
    ],
    "tolerance": [
        "tirzepatide stopped working weight regain",
        "Mounjaro plateau came off losing again",
        "Zepbound stopped losing quit",
    ],
    "longhaul": [
        "two years off Mounjaro weight update",
        "a year after stopping Zepbound maintained",
        "long term after stopping tirzepatide",
    ],
    "recomp": [
        "kept weight off lifting after Mounjaro",
        "maintained muscle protein after stopping Zepbound",
        "body recomposition after stopping GLP-1 weight",
    ],
    "setpoint": [
        "set point after stopping tirzepatide appetite",
        "appetite never came back after Zepbound",
        "metabolism reset after stopping Mounjaro",
    ],
    "pause": [
        "stopped Mounjaro for pregnancy weight regain",
        "paused Zepbound for surgery gained",
        "took a break from tirzepatide weight came back",
    ],
}


def collect_new(existing_ids):
    """Collect NEW threads (not already in the dataset) from the v2 feeds."""
    posts = OrderedDict()

    def n_new():
        return sum(1 for pid in posts if pid not in existing_ids)

    # 1) New wholesale TOP feeds.
    for sub, suffixes in NEW_WHOLESALE.items():
        for suf in suffixes:
            if n_new() >= MAX_NEW:
                break
            xml = rs.fetch(f"https://www.reddit.com/r/{sub}/{suf}")
            if not xml:
                print(f"  ! no data r/{sub}/{suf}")
                continue
            before = n_new()
            for e in rs.parse_entries(xml):
                base.add_post(posts, "v2_topsub", f"r/{sub}", *e)
            print(f"  r/{sub} [{suf.split('?')[0]} {suf.split('t=')[-1].split('&')[0]}]: "
                  f"+{n_new() - before} new (new total {n_new()})")
            time.sleep(0.4)

    # 2) New site-wide query angles.
    for bucket, queries in NEW_BUCKETS.items():
        for q in queries:
            if n_new() >= MAX_NEW:
                break
            feed = ("https://www.reddit.com/search.rss"
                    f"?q={urllib.parse.quote(q)}&sort=relevance&t=all&limit=100")
            xml = rs.fetch(feed)
            if not xml:
                print(f"  ! no data [{bucket}] '{q}'")
                continue
            before = n_new()
            for e in rs.parse_entries(xml):
                base.add_post(posts, bucket, q, *e)
            print(f"  [{bucket}] '{q[:40]}': +{n_new() - before} new (new total {n_new()})")
            time.sleep(0.4)

    return posts


def main():
    started = time.time()
    prev = base.load_checkpoint()
    print(f"Round 1 dataset: {len(prev)} threads "
          f"({sum(1 for p in prev.values() if p.get('fetched'))} fetched).")
    existing_ids = set(prev.keys())

    print("Collecting NEW threads only (proxied, rotating)...")
    collected = collect_new(existing_ids)

    by_id = dict(prev)
    added = 0
    for pid, p in collected.items():
        if pid in by_id:
            for b in p["buckets"]:
                if b not in by_id[pid]["buckets"]:
                    by_id[pid]["buckets"].append(b)
        else:
            by_id[pid] = p
            added += 1
    posts = list(by_id.values())[:CAP_TOTAL]
    base.save_checkpoint(posts)
    new_unfetched = sum(1 for p in posts if not p.get("fetched"))
    print(f"\n{len(posts)} threads total (+{added} new this round; "
          f"{new_unfetched} to comment-fetch). Checkpointed.")

    base.fetch_comments_ckpt(posts)         # only fetches the new ones
    rs.write_outputs(posts, "tirz_offdrug_full")
    ncom = sum(len(p["comments"]) for p in posts)
    print(f"\nDone in {time.time() - started:.0f}s. {len(posts)} threads, "
          f"{ncom} comments.\n  -> data/tirz_offdrug_full.{{json,csv,md}}")


if __name__ == "__main__":
    main()
