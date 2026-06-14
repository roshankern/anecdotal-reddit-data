# Tirzepatide off-drug — Reddit regain & metabolism report (design)

**Date:** 2026-06-12
**Author:** Roshan + Claude
**Status:** approved, proceeding to test scrape

## Goal

Answer two questions **purely from Reddit personal experience** (no clinical data):

1. **Regain:** After people stop tirzepatide (Mounjaro / Zepbound / grey-market tirz),
   do they tend to gain the weight back? How much, how fast?
2. **Metabolism / "dependency":** Is there any sign metabolism gets worse after stopping —
   i.e. people become metabolically "dependent," worse off than before they started
   (faster regain than loss, harder to lose now, hungrier than ever, above starting weight)?

Plus two sub-asks folded into both questions:
- **Any metabolism mention at all** — capture *every* comment on appetite, hunger, "food
  noise," cravings, energy, "metabolism," maintenance calories/TDEE, regain *speed* — even
  neutral ones — so Q2 is answered as fully as the data allows.
- **Attribution / confounders** — when people do or don't regain (or report metabolism
  changes), do they credit **non-drug factors**? Lifestyle (diet/calorie counting, exercise,
  resistance training/protein to keep muscle) or **other drugs** (switched to another GLP-1,
  microdose/maintenance dose, naltrexone/metformin/etc.). This tells us how drug-attributable
  the outcomes actually are.

## The bias problem and how this design fights it

Reddit is biased three ways on this topic; the pipeline counters each.

| Bias | Countermeasure |
|---|---|
| **Survivorship/distress** — regainers panic-post; quiet maintainers post less | Run **separate query sets** for regain *and* "kept-it-off" stories; sample **drug subs** (active users) *and* **maintenance subs** (people who stopped). Report both populations separately. |
| **Speculation noise** — "I'm scared I'll regain", "my doctor said" | Hard gate: **not personal + not actually off-drug → excluded** from all counts (rule #1). Counted only as "scanned, not useful." |
| **Unverifiable claims** — regex can't tell a real off-drug story from a fear post | Mandatory **subagent hand-read**; regex only narrows the haystack. |

## Credibility rules (non-negotiable)

1. A report counts **only** if it is **personal experience** AND the person **actually
   stopped** the drug. Speculation, fear, hearsay, "I heard," still-on-drug → excluded.
2. **Every cited report carries a URL** (per-comment permalink where possible) so we can read it.

## Tier scheme (evidential strength, not raw months)

| Tier | Definition | Use |
|---|---|---|
| **A — Strong** | Personal, confirmed stopped, **usable timeline + clear/quantified outcome** ("off 11 mo, regained 30 of 50 lb") | Stands alone; drives headline |
| **B — Supporting** | Personal, confirmed stopped, clear *direction* but vague timeframe / unquantified | Corroborates; weighted lighter |
| **Excluded** | Not personal / still on / speculation / fear / hearsay | Counts only as "scanned, not useful" |

**Durability gate** (the one place timeframe is load-bearing): a "kept it off" claim only
counts as evidence of *durable* maintenance if off **≥3 months** (ideally 6+). "Still down
after 3 weeks" proves nothing — regain is gradual. Regain claims need no gate (regain shows
fast). The report will state how sensitive the answer is to this threshold.

## Per-row tags

- **Q1 outcome:** Regained-most / Partial / Maintained / Still-losing-off-drug — with
  **magnitude** (lb/kg or %) and **time off**.
- **Q2 metabolism:** dependency-signal (worse than baseline) / counter-signal (fine off-drug)
  / neutral-mention (any appetite/hunger/energy/metabolism comment) / none.
- **Attribution:** lifestyle (diet, exercise, lifting/protein) / other-drug (switch,
  microdose/maintenance, other meds) / none-stated.

## Pipeline (reuses the reta GI tooling)

0. **Test scrape** — `rss_scrape.py` search mode, ~50 posts, draft queries across
   r/tirzepatide + r/Mounjaro + r/Zepbound (drug name in the query so `--sub all` stays
   on-topic). Eyeball the `.md`, confirm real off-drug stories surface, tune queries.
   **Show Roshan the test result before scaling.**
1. **Full scrape** — three query files → three runs into `data/tirz_offdrug_*`:
   - `queries_regain.txt` — gained it back, regained, creeping back up, off and gaining
   - `queries_maintain.txt` — maintained after stopping, off a year kept it off, no regain
   - `queries_metab.txt` — harder to lose now, gained back faster than before, metabolism,
     hungrier than ever, food noise back, heavier than when I started
   - Subs: tirzepatide, Mounjaro, Zepbound + GLP1, Maintenance, loseit
     (`--sub all` with drug-named queries; per-sub for the dedicated subs).
2. **Pre-filter / merge** — script merges corpora into text units (post + each comment),
   dedupes, **counts total scanned** (denominator), tags candidate units with regex signals
   (off-drug, regain/maintain, metabolism, attribution, personal markers, duration), writes
   batches as JSONL for review.
3. **Hand-read** — fan out parallel subagent reviewers (one per batch, like the 12 reta
   reviewers). Each extracts verified rows: `url, drug, what-they-did, time-off, outcome,
   magnitude, tier, Q1-tag, Q2-tag, attribution`. Strict on the credibility rules.
4. **Synthesize** — `tirz-reddit-regain-report.md`:
   - **Numbers summary:** posts + comments scanned → useful → by tier → pro/against per
     question, split by drug and by source population (drug subs vs maintenance subs).
   - **Definitive answers** to Q1 and Q2, graded by evidence strength, every claim backed by
     a clickable URL.
   - **Attribution findings:** how often outcomes were credited to lifestyle / other drugs.
   - **Honest bias & limits** section. Reddit only — no clinical data.

## Deliverables

- `data/tirz_offdrug_*.{json,csv,md}` — raw scrape
- `data/tirz_offdrug_rows.csv` — verified person-level rows (the dataset)
- `tirz-reddit-regain-report.md` — the report

## Out of scope

- No clinical-trial data (separate report already exists).
- No upvote/score data (RSS doesn't expose it).
- Not medical advice; anecdotal, self-reported, partly grey-market.
