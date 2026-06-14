# Anecdotal Reddit Data

Tooling for scraping **anecdotal biological / health data on Reddit** and
hand-reading the results into reports. Built around real-world, self-reported
experiences people post in niche health communities.

The current reports happen to cover GLP-1 / peptide drugs (retatrutide,
tirzepatide), but nothing here is peptide-specific — point it at any subreddit
or search and it works the same.

Everything shares one scraper (`rss_scrape.py`) and one set of proxy creds
(`.env`, gitignored). Each piece of work lives under `projects/`.

## Projects

| Project | Question | Deliverables |
|---|---|---|
| [`projects/reta-gi-symptoms/`](projects/reta-gi-symptoms/) | What helps GI side effects (nausea/diarrhea)? Dose vs. symptoms. | `reports/gi_report_full.md`, `data/*.csv` |
| [`projects/tirz-offdrug-regain/`](projects/tirz-offdrug-regain/) | After stopping the drug: do people regain weight? Does metabolism get worse? | `reports/tirz_discon_research.md` (methodology + TL;DR) → Reddit + clinical reports |

Each project folder has its own `README.md`, scripts, `reports/`, and `data/`.

## Shared scraper — `rss_scrape.py`

The one tool every project imports. Pulls Reddit **RSS feeds** through a
rotating pool of proxies and writes `data/<prefix>.{json,csv,md}`. Two modes:

```bash
python rss_scrape.py --limit 100                            # listing: sweep whole subs
python rss_scrape.py --search "nausea" --out gi_symptoms    # search: keyword hunt
python rss_scrape.py --search-file queries.txt --sub Retatrutide
```

Run `python rss_scrape.py --help` for all flags. Project scripts are thin
wrappers that `import rss_scrape` and reuse its `fetch` / `parse_entries` /
`fetch_comments` / `write_outputs`.

> **Running a project's scripts:** they `import rss_scrape` (at repo root) and
> read/write a local `data/` dir. Run them *from inside the project folder* with
> the repo root on the path:
> ```bash
> cd projects/tirz-offdrug-regain
> PYTHONPATH=../.. python scrape_offdrug.py
> ```

---

## Scraping notes (read before any big run)

### What's dead in 2026
Reddit locked down. **Do not** bother with these — they all fail now:
- **Official Data API / PRAW** — gated behind the Responsible Builder Policy (Nov 2025); self-serve app creation silently captcha-loops.
- **Public `.json` endpoints** (`/r/x/.json`, `old.reddit.com/…json`) — HTTP 403 to everyone, *even through proxies*. Killed ~May 2026.
- **redlib / libreddit mirrors** — behind anti-bot walls.

### What works: RSS through proxies
Reddit's **RSS** feeds are official and still open:
- `https://www.reddit.com/r/<sub>/new.rss?limit=100` — recent posts (title, body, author, date)
- `https://www.reddit.com/r/<sub>/top.rss?t=year|all&limit=100` — top posts
- `https://www.reddit.com/search.rss?q=<query>&restrict_sr=1&sort=new|relevance&t=week|year` — keyword search
- `<post-permalink>.rss?limit=100` — a post's comments (**capped at ~top 100, not the full tree**; each comment has its own permalink for citation)

Feeds are Atom XML; bodies are HTML-escaped in `<content>` with a "submitted by
…" footer to strip. `rss_scrape.py` handles all of it.

### Proxy rules (the load-bearing part)
1. **Always proxy. Never go direct.** Reddit 403s datacenter/home IPs. Every request — feeds *and* comments — must exit a residential/ISP IP.
2. **HTTP mode, not SOCKS5.** URL: `http://USER:PASS@HOST:PORT`. Set **both** `http` and `https` in the proxies dict. Provider + port live in `.env` only.
3. **Rotate across all IPs**, one random pick per request; on failure retry on a *different* IP. (`rss_scrape.py` does `random.choice(POOL)` + retry-on-fresh-proxy.)
4. **Real Chrome User-Agent.** Blank/bot UAs raise block odds.
5. **Creds stay in `.env`** (gitignored). Never commit them. See `.env.example`.
6. **Sanity-check before a big run** — confirm RSS returns 200 through a proxy (`.json` will still 403; that's expected, test against RSS).

### How long it takes
Baseline, all through rotating proxies, zero blocks:
- **~100 posts + ~800 comments ≈ 90 seconds.** Time is dominated by per-post comment fetches (one proxied request each), not the listing pull.
- A full project sweep (the tirz off-drug run: **1,000 threads / ~37k comments**, in resume-safe batches) takes on the order of an hour. For runs that big, **checkpoint to disk incrementally and resume by thread id** so a dropped laptop/Wi-Fi never loses progress — see `projects/tirz-offdrug-regain/scrape_offdrug.py`.

### Limits
- Sub feeds return ~100 most-recent posts; `search.rss` ~top 100 hits per query. Go deeper by adding queries/subreddits, not by paging.
- Comment RSS is capped per post; no score/upvote data in RSS.
