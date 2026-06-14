# tirz-offdrug-regain

**Questions (Reddit experience only, no clinical data):** after people stop
**tirzepatide** (Mounjaro / Zepbound / grey-market tirz) —
1. Do they regain the weight? How much, how fast?
2. Does metabolism get *worse* — do they become metabolically "dependent," worse off than before they started?

## Deliverables (start here)
- **`reports/tirz_discon_research.md`** — methodology + TL;DR tying both reports together (how we asked the questions, how we fought bias/noise). Read this first.
- `reports/tirz_reddit_discon_report.md` — the **Reddit** report (1,000 threads, 328 verified first-hand reports).
- `reports/tirz_clinical_discon_report.md` — the **clinical-trial** report (SURMOUNT-4 + 2024–26 meta-analyses), web-sourced — not Reddit.
- `spec/2026-06-12-tirz-reddit-regain-design.md` — the design (bias countermeasures, credibility rules, tier scheme).

## Findings
- **Q1 (regain):** real, common, often fast (10–20 lb in 1–2 mo) but **not inevitable**. Of 234 determinate reports: 100 maintained / 91 regained / 43 still losing. Differentiator = **lifestyle/system** (197/328 cited a non-drug factor).
- **Q2 (metabolism):** little support for permanent damage. "Dependency" signal ≈ counter-signal; reports describe appetite returning to *baseline*, not below it. True "worse than before" = ~6–8 reports, mostly non-tirz/subjective.
- **Big caveat:** NOT a prevalence estimate — r/GLPGrad ("graduates") supplies ~62% of reports because that's where off-drug stories concentrate. Qualitative.

## Pipeline
1. `scrape_offdrug.py` (round 1, 500 threads) + `scrape_offdrug_v2.py` (round 2, +500 *new* threads). Both reuse `rss_scrape.py`. **Crash-safe:** checkpoint `data/tirz_offdrug_full.json` every 10 posts (atomic rename) and **resume-merge by thread id** — re-running never re-fetches.
2. `prefilter_offdrug.py` / `_v2.py` — tag candidate text units → `data/offdrug_batches/batch_NN.jsonl` (60/batch).
3. Hand-read by parallel sub-agents → `data/offdrug_rows/rows_NN.jsonl`, aggregated (url-deduped) → `data/offdrug_rows_all.json` (the 328-row dataset).

**Credibility rule (the whole point):** a report counts only if first-person AND
they actually stopped/reduced; speculation/fear/hearsay/still-on-drug excluded
(~17% of candidates survived). Every cited report carries its exact comment URL.

Scripts read/write a local `data/`; run from this folder (`PYTHONPATH=../.. python scrape_offdrug.py`).
