# GI Symptom Scrape — finding what actually helps post-dose GI issues

## The objective

Build a ranked, evidence-backed list of interventions that may help **acute
GI symptoms (diarrhea + nausea) on dose night** for a specific person, and rate
how likely each intervention is to help her.

**Subject profile (the target we score everything against):**

| Field | Value |
|---|---|
| Sex | Female |
| Age | ~26 |
| Dose | 2mg / week |
| Duration | ~4 weeks in |
| Symptom | Diarrhea + some nausea the **night she injects** (Fri night), acute/post-dose |
| Drug | Retatrutide |

The closer a real person is to this profile **and** the more clearly they
*personally tried something that worked*, the more their report is worth. A
stranger who's 6 months in at 8mg giving advice they never tested is worth very
little. A 26-year-old woman at 2mg who fixed the exact same dose-night diarrhea
is the gold standard.

**Overriding goal: keep her ON reta and make it tolerable.** The whole point is
to find out whether reta can work for her, so interventions that *keep her on
reta* (diet, timing, dose tweaks, anti-emetics, reta-compatible adjuncts like
cagrilintide) are what we want. "Just switch to tirzepatide/semaglutide" is a
valid thing people say, but it's **deprioritized here** — it abandons the goal.
We'll record it, flag it, and rank it last.

Two deliverables come out of this:

1. **`gi_raw.csv`** — one row per reported symptom→intervention data point.
2. **`gi_interventions.csv`** — one row per *intervention*, rated **High / Med /
   Low** likelihood of helping her, with the reasoning.

---

## How the tools work

### The scraper (`rss_scrape.py`)
Reddit's data API and `.json` endpoints are dead in 2026 (see `README.md`). We
pull **Reddit RSS feeds through rotating ISP/residential proxies** — the one channel
still open. Every request exits from a residential IP; we rotate all proxies and
retry on a fresh one. This is already built and working.

**Comment-level permalinks are now captured** (recent change): each comment
stores its own `url` (`/comments/<post>/<slug>/<comment_id>/`), so when a
*commenter* — not the OP — is the one with the useful remedy, we can link
straight to their comment. This matters a lot here: **most remedy gold is in the
comments**, not the posts.

### New capability needed: keyword search
The scraper currently pulls whole-subreddit listings (`new.rss`, `top.rss`).
For a symptom-targeted hunt that's wasteful — we want to **search by keyword**.
Reddit exposes a search RSS endpoint that works the same proxied way:

```
https://www.reddit.com/r/<sub>/search.rss?q=<query>&restrict_sr=1&sort=relevance&t=year
https://www.reddit.com/search.rss?q=<query>&sort=relevance&t=year     # all-of-reddit
```

Plan: add a `search()` path that runs each query below, dedupes the post hits,
then fetches each post's comment RSS (reusing the existing comment logic). Same
proxy rotation, same parser.

---

## Search strategy

Two layers. **Symptom searches** find people *having* the problem (their threads
are full of commenters offering fixes). **Remedy searches** find people *naming*
the fix directly.

**Scope: r/Retatrutide only** (decided). Staying reta-specific keeps every
report on-drug and maximizes proximity — we want to know what works *for reta
users like her*, not the general GLP-1 population. Cross-drug remedies (tirz,
sema) will still appear incidentally whenever reta users mention having tried
them; that's fine and gets logged with a `drug` note, but we are not searching
the other subreddits.

**Symptom / discovery queries**
- `diarrhea`
- `nausea`
- `GI side effects`
- `sulfur burps` / `sulphur burps`
- `stomach issues` / `upset stomach`
- `day after injection` / `night of pin` / `post injection`
- `diarrhea every week` / `nausea after dose`
- `women side effects` / `female side effects` (helps surface same-sex reports)

**Remedy / solution queries**
- `what helps nausea` / `nausea remedy` / `anti nausea`
- `what helps diarrhea` / `imodium` / `loperamide`
- `zofran` / `ondansetron`
- `dramamine` / `meclizine` / `motion sickness`
- `ginger` / `peppermint` / `pepto` / `bismol`
- `electrolytes` / `hydration`
- `pin in the morning` / `pin at night` / `dose timing`
- `split dose` / `lower dose` / `titrate down`
- `eat before pin` / `low fat meal` / `bland food`

---

## Raw extraction schema (`gi_raw.csv`)

One row per (person × intervention) data point. Blanks where unstated.

| Column | Meaning |
|---|---|
| `gender` | reporter's sex if stated |
| `age` | if stated |
| `dose` | their reta (or other GLP-1) dose |
| `time_on_it` | how long they'd been on it |
| `drug` | reta / tirz / sema / etc. (cross-drug flagged) |
| `symptom` | which GI symptom this addresses (diarrhea / nausea / both / sulfur burps…) |
| `symptom_timing` | acute post-dose / general / unstated — **acute post-dose matches her best** |
| `intervention` | the specific thing (e.g. "low-fat meal before pin", "Imodium", "split dose") |
| `outcome` | **worked / partial / didn't work / unstated** |
| `evidence_type` | **personal (tried it) / advice (untested) / cited** |
| `proximity` | Tier 1 / 2 / 3 (see below) |
| `source_link` | **comment-level** permalink where possible, else post |
| `quote` | short supporting snippet (optional) |

---

## Proximity tiers (how a data point earns its weight)

Score each report on three axes, then bucket:

1. **Evidence quality** — did they actually do it?
   `worked (personal)` ≫ `partial (personal)` > `didn't work (personal, still
   informative)` > `untested advice` > `vague`.
2. **Profile proximity** — matches on **sex**, **age (~20–32)**, **dose
   (1–3mg)**, **duration (~2–8wk)**.
3. **Symptom match** — same cluster: **acute post-dose diarrhea/nausea**.

**Tier 1 (gold):** female, ~20–32, low dose (1–3mg), early (≤~2mo), same
post-dose diarrhea/nausea, **personally tried something that worked.**
**Tier 2:** strong on evidence + symptom, but off on demographics/dose/duration
(e.g. male, or 8mg, or different GLP-1), or a near-profile "helped somewhat."
**Tier 3:** relevant symptom but **untested advice**, vague, or only loosely related.
**Discard:** no real GI-symptom relevance.

> Negative results are kept on purpose — "Imodium did nothing for me at 2mg" is
> real signal, not noise.

---

## Intervention rating (`gi_interventions.csv`)

Aggregate `gi_raw.csv` up to one row per intervention and assign a likelihood.

| Column | Meaning |
|---|---|
| `intervention` | the fix |
| `targets` | diarrhea / nausea / both |
| `mechanism` | short biological reasoning for *why* it would work |
| `n_reports` | total people who mentioned it |
| `n_worked` | how many *personally* said it worked |
| `closest_profile` | best-matching reporter (e.g. "F, 25, 2mg, 5wk — worked") |
| `likelihood` | **High / Med / Low** |
| `rationale` | one line tying prevalence + proximity + mechanism together |
| `examples` | 1–3 source links (comment-level) |
| `caveats` | confounders, conflicting reports, risks |

**How `likelihood` is assigned** — it's prevalence **and** proximity **and**
plausibility, not a raw vote count:

- **High** — multiple independent *personal* successes, **≥1 near her profile**,
  and a sound mechanism. (e.g. low-fat meal before pinning; split/timing change.)
- **Med** — some personal successes but thin or profile-distant, OR strong
  mechanism but mostly untested advice, OR helps one symptom not both.
- **Low** — rare, only untested advice, weak/hand-wavy mechanism, or reports
  conflict.

**Staying-on-reta preference:** interventions that keep her on reta are what we
optimize for. Any "switch off reta to another drug" intervention is capped at
**Low** and labeled as off-goal, regardless of how many people swear by it —
it's recorded for completeness, not recommended. Reta-compatible adjuncts
(cagrilintide, anti-emetics, etc.) are rated on the normal scale.

---

## Caveats (carry into any conclusion)
- All self-reported, grey-market, anecdotal. **Not medical advice.** A doctor /
  pharmacist beats Reddit for anything Rx (e.g. ondansetron) or persistent.
- GLP-1 GI effects usually ease as the body adapts — some "fixes" may just be
  time. We note duration to partly control for this.
- Cross-drug remedies are biologically reasonable but get a proximity penalty.
- Sample is whatever the search surfaces; we log query coverage, not a census.

---

## Decisions (locked)
- **Subreddit scope:** r/Retatrutide only.
- **Dose/timing changes:** on the table — lowering dose, splitting to 2x/week,
  and shifting pin timing (morning vs night, which day) are all candidate
  interventions.
- **Intervention types:** all of them — diet & timing, OTC/supplements,
  prescription anti-emetics (flagged "ask a doctor"), and reta-compatible
  peptide adjuncts — plus anything else that genuinely helps.
- **Priority:** keeping her on reta and proving it can work is the goal;
  drug-switching interventions are deprioritized (capped Low, off-goal).
