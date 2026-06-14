# reta-gi-symptoms

**Question:** What actually helps retatrutide ("reta") GI side effects
(nausea + diarrhea), and how do they track with dose? Built as an intervention
report for a friend (F, ~26, 2mg/week, diarrhea+nausea the night she pins).

## Deliverables (start here)
- **`reports/gi_report_full.md`** — the final report (hand-verified; supersedes `gi_report.md`).
- **`data/gi_interventions_full.csv`** — 31 interventions rated by prevalence/proximity/mechanism.
- **`data/gi_raw_full.csv`** — 792 person×intervention rows (320 threads), with source links.
- `reports/gi_symptom_scrape.md` — the design doc. `gi_report.md` / `gi_raw.csv` / `gi_interventions.csv` — first-pass (kept for the diff).

## Key finding
GI symptoms are **dose-dependent**: up-titration (esp. jumps to 3–4mg) is the #1
reported trigger; holding/lowering is the #1 fix. Going to "2× 2mg = 4mg/week" is
*doubling* the dose, not the side-effect-reducing split-dose. Survivorship bias
means ~85–95% of everything reads "positive" — only robust signal is the
within-person dose-response.

## How it was built
1. Scraped r/Retatrutide via `rss_scrape.py` (search + listing) → `data/gi_all.json` (600 posts / 14,939 comments) plus the per-topic scrapes `data/gi_{symptoms,remedies,fixes}.*` from `queries*.txt`.
2. `analyze_gi.py` — keyword/regex rollup over post+comment text → prevalence/efficacy/proximity + example dump.
3. `extract_core.py` → `data/gi_core.jsonl`, hand-read by parallel sub-agents (`data/batches/out_NN.json`) into the `*_full` deliverables.

Scripts read/write a local `data/`; run from this folder (`PYTHONPATH=../.. python analyze_gi.py`).
