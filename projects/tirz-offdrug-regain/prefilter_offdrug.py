#!/usr/bin/env python3
"""
Pre-filter the off-drug corpus (data/tirz_offdrug_full.json) for hand-read.

Counts the FULL corpus (posts + comments = the "scanned" denominator), then
surfaces CANDIDATE units that plausibly contain a PERSONAL off-drug outcome or a
metabolism/appetite remark — keeping recall high so the subagent reviewers (not
regex) make the credibility call. Each candidate carries its comment-level
permalink so every future citation is traceable.

Writes:
  - data/offdrug_candidates.jsonl      one record per candidate unit, full text + signal tags
  - data/offdrug_batches/batch_NN.jsonl  the same, split into review batches
  - prints corpus + candidate stats (the report's numbers-summary denominator)

Signal tags (regex, generous — for triage only, NOT the final classification):
  offdrug   stopped / came off / maintenance-dose / graduated
  regain    gained it back / crept up / rebound
  maintain  kept it off / stayed stable / no regain
  metab     appetite / hunger / food noise / metabolism / energy / satiety
  attr_life lifestyle credited (diet, exercise, lifting, protein, habits)
  attr_drug another drug credited (microdose, switch, reta/sema, metformin, etc.)
  personal  first-person "I stopped / I gained / I kept"
  duration  a stated timeframe (n weeks/months/years, "a year off")
  magnitude a quantified amount (lb/kg/%)
"""
import json, re, html, os
from collections import Counter

POSTS = json.load(open("data/tirz_offdrug_full.json"))

OFFDRUG  = re.compile(r"\b(stopped|came off|got off|went off|quit|gave up|off (it|the|tirz|mounjaro|zep|sema|glp|ozempic|wegovy|shot|med|drug)|been off|after stopping|stopped taking|once i stopped|since stopping|no longer (on|taking)|maintenance (dose|phase)|graduat|off the (shot|med|drug)|came off|weaned)", re.I)
REGAIN   = re.compile(r"\b(regain|gain(ed|ing)? .{0,15}(back|again)|put .{0,12}back on|crept? .{0,8}back|coming back|came back|bounced back|rebound|back to (my )?(starting|sw|original|highest)|every (single )?pound|all of it back|gained it all|creeping up|piled back)", re.I)
MAINTAIN = re.compile(r"\b(maintain|kept (it|the weight|them) off|keeping it off|stayed (the same|off|stable)|held (steady|my weight)|no regain|didn'?t gain|haven'?t gained .{0,12}back|hasn'?t come back|still (down|off)|weight (is )?stable|same weight|maintenance)", re.I)
METAB    = re.compile(r"\b(metabol|appetite|hunger|hungry|food noise|cravings?|tdee|maintenance cal|set ?point|slower|burn(s|ing|ed)?|energy|satiet|full(ness)?|stomach (shrunk|growl)|never been able|always hungry|insatiab)", re.I)
ATTR_LIFE= re.compile(r"\b(diet|calorie|deficit|exercise|workout|gym|lift(ing|ed|s)?|weight train|resistance|protein|walk|steps|habit|portion|whole food|clean eating|intermittent fast|cardio|macros?)", re.I)
ATTR_DRUG= re.compile(r"\b(microdos|maintenance dose|lower(ed)? dose|smaller dose|switch\w* to|went on|started (sema|reta|wegovy|ozempic|mounjaro|zepbound|another)|naltrexone|metformin|contrave|bupropion|phentermine|stimulant|\breta\b|retatrutide|cagri)", re.I)
PERSONAL = re.compile(r"\bi (stopped|came off|got off|went off|quit|gained|regained|lost|maintain\w*|kept|was off|have been off|stayed|am off|went back|started|weaned|got to|hit (my )?goal)\b|for me\b|my experience|in my case|happened to me|i'?ve been off|when i stopped|i'?m off|i was on", re.I)
DURATION = re.compile(r"\b\d+\s*(week|month|year|yr|mo)s?\b|\ba year\b|six months|couple (of )?(month|year)|\bmonths? (off|later|after|ago|in)|year(s)? (off|later|ago|in)|since (last|i|january|february|march|april|may|june|july|august|september|october|november|december)", re.I)
MAGNITUDE= re.compile(r"\b\d{2,3}\s?(lb|lbs|pound|pounds|kg|kilos?)\b|\b\d{1,3}\s?%|gained \d|lost \d|down \d|up \d", re.I)

SIGNALS = [("offdrug",OFFDRUG),("regain",REGAIN),("maintain",MAINTAIN),("metab",METAB),
           ("attr_life",ATTR_LIFE),("attr_drug",ATTR_DRUG),("personal",PERSONAL),
           ("duration",DURATION),("magnitude",MAGNITUDE)]

def clean(t):
    return html.unescape(t or "").replace("\r"," ").strip()

def units():
    for p in POSTS:
        body = clean(p.get("title","")) + " . " + clean(p.get("body",""))
        yield dict(where="post", post_id=p.get("id"), subreddit=p.get("subreddit"),
                   buckets=p.get("buckets"), query=p.get("query"), link=p.get("url"),
                   author=p.get("author"), created=p.get("created"), text=body)
        for c in p.get("comments", []):
            yield dict(where="comment", post_id=p.get("id"), subreddit=p.get("subreddit"),
                       buckets=p.get("buckets"), query=p.get("query"), link=c.get("url"),
                       author=c.get("author"), created=c.get("created"),
                       text=clean(c.get("body","")))

all_units = list(units())
n_posts = len(POSTS)
n_comments = sum(len(p.get("comments",[])) for p in POSTS)

candidates = []
for u in all_units:
    t = u["text"]
    if len(t) < 25:
        continue
    tags = [name for name, rx in SIGNALS if rx.search(t)]
    has_ctx = any(x in tags for x in ("offdrug","regain","maintain"))
    has_hook = any(x in tags for x in ("personal","magnitude","duration","metab"))
    # candidate: an off-drug/regain/maintain context with a personal/quantified/metabolic hook,
    # OR a clearly personal metabolism remark (Q2 breadth) even without an explicit stop word.
    if (has_ctx and has_hook) or ("metab" in tags and "personal" in tags):
        u["signals"] = tags
        candidates.append(u)

os.makedirs("data/offdrug_batches", exist_ok=True)
with open("data/offdrug_candidates.jsonl","w") as f:
    for u in candidates:
        f.write(json.dumps(u, ensure_ascii=False) + "\n")

BATCH = 60
nbatches = 0
for i in range(0, len(candidates), BATCH):
    nbatches += 1
    with open(f"data/offdrug_batches/batch_{nbatches:02d}.jsonl","w") as f:
        for u in candidates[i:i+BATCH]:
            f.write(json.dumps(u, ensure_ascii=False) + "\n")

sig = Counter(s for u in candidates for s in u["signals"])
print(f"=== CORPUS (scanned) ===")
print(f"threads(posts)={n_posts}  comments={n_comments}  total text units={len(all_units)}")
print(f"=== CANDIDATES (to hand-read) ===")
print(f"candidate units={len(candidates)}  -> {nbatches} batches of {BATCH}")
print(f"signal coverage among candidates: {dict(sig.most_common())}")
print(f"\nwrote data/offdrug_candidates.jsonl and data/offdrug_batches/batch_*.jsonl")
