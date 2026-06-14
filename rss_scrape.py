"""
RSS-based Reddit scraper for retatrutide ("reta") research.

Why RSS: as of 2026 Reddit's data API requires approval (Responsible Builder
Policy), the public .json endpoints return 403, and redlib mirrors are behind
anti-bot walls. Reddit's RSS feeds are the one channel still open — and they
work through residential/ISP proxies.

Every HTTP request is routed through a rotating pool of ISP/residential proxies
(loaded from .env). Two feeds per request type are pulled to maximize coverage:
  - subreddit listing:  /r/<sub>/new.rss  and  /r/<sub>/top.rss?t=year
  - per-post comments:  <permalink>.rss

Two modes:
  - listing  (default): pull whole-subreddit feeds (new + top) for SUBREDDITS
  - search   (--search): keyword search via Reddit's search.rss, e.g. to hunt
             for a specific symptom/remedy. Restricts to one subreddit by
             default (--sub, default r/Retatrutide); --sub all searches reddit.

Outputs (in ./data/, named by --out PREFIX; default "reta_posts"):
  <prefix>.json           structured: posts with nested comments
  <prefix>_posts.csv      one row per post
  <prefix>_comments.csv   one row per comment (with per-comment permalink)
  <prefix>.md             readable dump (easy to hand to an LLM)

Usage:
  python rss_scrape.py                              # listing mode, 100 posts
  python rss_scrape.py --limit 25
  python rss_scrape.py --search "nausea" "diarrhea" --limit 50 --out gi_symptoms
  python rss_scrape.py --search-file queries.txt --sub Retatrutide --out gi_symptoms
"""

import argparse
import csv
import html
import json
import os
import random
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests

ATOM = "{http://www.w3.org/2005/Atom}"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Subreddits where retatrutide is discussed. r/Retatrutide is dedicated; the
# rest are broader GLP-1 / peptide communities where it comes up.
SUBREDDITS = [
    "Retatrutide",
    "tirzepatide",
    "Mounjaro",
    "GLP1",
    "Semaglutide",
    "Ozempic",
    "Peptides",
]


def load_proxies():
    """Read proxy creds from .env and build the rotating proxy pool."""
    env = {}
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    user = env.get("PROXY_USER") or os.getenv("PROXY_USER")
    pwd = env.get("PROXY_PASS") or os.getenv("PROXY_PASS")
    port = env.get("PROXY_PORT") or os.getenv("PROXY_PORT")
    hosts = (env.get("PROXY_HOSTS") or os.getenv("PROXY_HOSTS", "")).split(",")
    hosts = [h.strip() for h in hosts if h.strip()]
    if not (user and pwd and port and hosts):
        raise SystemExit("Missing proxy config in .env (PROXY_USER/PASS/PORT/HOSTS).")
    pool = [f"http://{user}:{pwd}@{h}:{port}" for h in hosts]
    print(f"Loaded {len(pool)} ISP proxies; rotating across all of them.")
    return pool


PROXIES = load_proxies()


def fetch(url, tries=4):
    """GET a URL through a randomly chosen proxy, retrying on a fresh proxy."""
    for attempt in range(tries):
        proxy = random.choice(PROXIES)
        try:
            r = requests.get(
                url,
                headers={"User-Agent": UA},
                proxies={"http": proxy, "https": proxy},
                timeout=25,
            )
            if r.status_code == 200:
                return r.text
            # 429/5xx → back off and rotate to a different proxy
            time.sleep(1.5 * (attempt + 1))
        except requests.RequestException:
            time.sleep(1.0 * (attempt + 1))
    return None


def clean(text):
    """Unescape + strip HTML, drop the Reddit RSS 'submitted by' footer."""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)  # entities can survive one pass
    # Reddit appends "submitted by /u/.. to r/.. [link] [comments]" — cut it.
    text = re.split(r"\bsubmitted by\b", text)[0]
    return re.sub(r"\s+", " ", text).strip()


def parse_entries(xml_text):
    """Yield (id, title, author, date, link, body) from an Atom feed."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return
    for e in root.findall(f"{ATOM}entry"):
        eid = (e.findtext(f"{ATOM}id") or "").strip()
        title = (e.findtext(f"{ATOM}title") or "").strip()
        author = (e.findtext(f"{ATOM}author/{ATOM}name") or "").strip()
        date = (
            e.findtext(f"{ATOM}published")
            or e.findtext(f"{ATOM}updated")
            or ""
        ).strip()[:10]
        link_el = e.find(f"{ATOM}link")
        link = link_el.get("href") if link_el is not None else ""
        body = clean(e.findtext(f"{ATOM}content") or "")
        yield eid, title, author, date, link, body


def scrape(limit):
    posts = {}
    # 1) Collect post listings from each subreddit (new + top of the year).
    for sub in SUBREDDITS:
        if len(posts) >= limit:
            break
        for feed in (
            f"https://www.reddit.com/r/{sub}/new.rss?limit=100",
            f"https://www.reddit.com/r/{sub}/top.rss?t=year&limit=100",
        ):
            xml_text = fetch(feed)
            if not xml_text:
                print(f"  ! no data from {feed}")
                continue
            found = 0
            for eid, title, author, date, link, body in parse_entries(xml_text):
                if not link or "/comments/" not in link:
                    continue
                pid = eid or link
                if pid in posts:
                    continue
                posts[pid] = {
                    "id": pid,
                    "subreddit": sub,
                    "title": title,
                    "author": author,
                    "created": date,
                    "url": link,
                    "body": body,
                    "comments": [],
                }
                found += 1
                if len(posts) >= limit:
                    break
            print(f"  r/{sub} [{feed.split('/')[-1].split('?')[0]}]: "
                  f"+{found} (total {len(posts)})")
            time.sleep(0.4)
            if len(posts) >= limit:
                break

    posts = dict(list(posts.items())[:limit])

    # 2) Fetch comments for each post via its per-post .rss feed.
    fetch_comments(posts.values())
    return list(posts.values())


def fetch_comments(posts):
    """Fetch + attach comments (with per-comment permalinks) for each post."""
    posts = list(posts)
    print(f"\nFetching comments for {len(posts)} posts...")
    for i, p in enumerate(posts, 1):
        crss = p["url"].rstrip("/") + ".rss?limit=100"
        xml_text = fetch(crss)
        if xml_text:
            for eid, title, author, date, link, body in parse_entries(xml_text):
                # The first entry (t3_…) is the post itself, not a comment.
                if eid.startswith("t3_") or link == p["url"]:
                    continue
                # Backstop in case the post entry lacks a t3_ id.
                if body and body[:120] == p["body"][:120]:
                    continue
                if body:
                    p["comments"].append({
                        "id": eid,          # t1_<comment_id>
                        "author": author,
                        "created": date,
                        "url": link,        # per-comment permalink we can revisit
                        "body": body,
                    })
        if i % 10 == 0:
            print(f"  {i}/{len(posts)} posts "
                  f"({sum(len(x['comments']) for x in posts)} comments so far)")
        time.sleep(0.4)
    return posts


def search(queries, sub, limit):
    """Keyword-search mode via Reddit's search.rss.

    queries: list of query strings.
    sub:     subreddit name to restrict to, or None to search all of Reddit.
    Dedupes post hits across queries, caps at `limit`, then fetches comments.
    """
    posts = {}
    for q in queries:
        if len(posts) >= limit:
            break
        qenc = urllib.parse.quote(q)
        if sub:
            feed = (f"https://www.reddit.com/r/{sub}/search.rss"
                    f"?q={qenc}&restrict_sr=1&sort=relevance&t=year&limit=100")
        else:
            feed = (f"https://www.reddit.com/search.rss"
                    f"?q={qenc}&sort=relevance&t=year&limit=100")
        xml_text = fetch(feed)
        if not xml_text:
            print(f"  ! no data for query '{q}' in r/{sub or 'all'}")
            continue
        found = 0
        for eid, title, author, date, link, body in parse_entries(xml_text):
            if not link or "/comments/" not in link:
                continue
            pid = eid or link
            if pid in posts:
                continue
            posts[pid] = {
                "id": pid,
                "subreddit": sub or "(search)",
                "title": title,
                "author": author,
                "created": date,
                "url": link,
                "query": q,          # which query surfaced this post
                "body": body,
                "comments": [],
            }
            found += 1
            if len(posts) >= limit:
                break
        print(f"  r/{sub or 'all'} q='{q}': +{found} (total {len(posts)})")
        time.sleep(0.4)

    posts = dict(list(posts.items())[:limit])
    fetch_comments(posts.values())
    return list(posts.values())


def write_outputs(posts, prefix="reta_posts"):
    os.makedirs("data", exist_ok=True)
    base = os.path.join("data", prefix)

    with open(f"{base}.json", "w") as f:
        json.dump(posts, f, indent=2)

    with open(f"{base}_posts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "subreddit", "title", "author", "created", "url",
                    "query", "body", "num_comments"])
        for p in posts:
            w.writerow([p["id"], p["subreddit"], p["title"], p["author"],
                        p["created"], p["url"], p.get("query", ""), p["body"],
                        len(p["comments"])])

    with open(f"{base}_comments.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["post_id", "post_url", "subreddit", "query", "comment_id",
                    "author", "created", "comment_url", "body"])
        for p in posts:
            for c in p["comments"]:
                w.writerow([p["id"], p["url"], p["subreddit"], p.get("query", ""),
                            c.get("id", ""), c["author"], c.get("created", ""),
                            c.get("url", ""), c["body"]])

    lines = [f"# Reddit RSS pull — {len(posts)} posts\n"]
    for p in posts:
        lines.append(f"\n---\n\n## {p['title']}")
        meta = f"*r/{p['subreddit']} · {p['created']} · u/{p['author']}*"
        if p.get("query"):
            meta += f" · search: \"{p['query']}\""
        lines.append(f"{meta}  \n{p['url']}\n")
        if p["body"]:
            lines.append(p["body"] + "\n")
        if p["comments"]:
            lines.append("\n**Comments:**\n")
            for c in p["comments"]:
                link = f" — [link]({c['url']})" if c.get("url") else ""
                lines.append(f"- (u/{c['author']}{link}) {c['body']}")
    with open(f"{base}.md", "w") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="Reddit RSS scraper (proxied).")
    ap.add_argument("--limit", type=int, default=100, help="max posts")
    ap.add_argument("--search", nargs="+", metavar="QUERY",
                    help="search mode: one or more keyword queries")
    ap.add_argument("--search-file", metavar="PATH",
                    help="search mode: file with one query per line "
                         "(combined with any --search queries)")
    ap.add_argument("--sub", default="Retatrutide",
                    help="subreddit to search/restrict (default: Retatrutide; "
                         "use 'all' to search all of Reddit)")
    ap.add_argument("--out", metavar="PREFIX",
                    help="output filename prefix under data/ (default: "
                         "reta_posts in listing mode, gi_symptoms in search mode)")
    args = ap.parse_args()

    queries = list(args.search or [])
    if args.search_file:
        queries += [q.strip() for q in Path(args.search_file).read_text().splitlines()
                    if q.strip() and not q.strip().startswith("#")]

    started = datetime.now(timezone.utc)
    if queries:
        sub = None if args.sub.lower() == "all" else args.sub
        prefix = args.out or "gi_symptoms"
        print(f"Search mode: {len(queries)} queries in r/{sub or 'all'}, "
              f"up to {args.limit} posts (proxied)...")
        posts = search(queries, sub, args.limit)
    else:
        prefix = args.out or "reta_posts"
        print(f"Pulling up to {args.limit} posts via RSS (proxied)...")
        posts = scrape(args.limit)
    write_outputs(posts, prefix)

    total_comments = sum(len(p["comments"]) for p in posts)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(
        f"\nDone in {elapsed:.0f}s. {len(posts)} posts, {total_comments} comments.\n"
        f"  -> data/{prefix}.json\n"
        f"  -> data/{prefix}_posts.csv\n"
        f"  -> data/{prefix}_comments.csv\n"
        f"  -> data/{prefix}.md"
    )


if __name__ == "__main__":
    main()
