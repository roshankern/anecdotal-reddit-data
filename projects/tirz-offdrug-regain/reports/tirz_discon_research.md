# Stopping tirzepatide — how this research was done

We asked the same two questions twice, with two independent methods, to see whether
lived experience and trial data tell the same story.

**The two questions**
1. **Regain** — after stopping tirzepatide (Mounjaro / Zepbound / grey-market tirz), do people put the weight back? How much, how fast?
2. **"Dependency"** — does metabolism get *worse* after stopping — do people end up metabolically worse off than before they ever started?

Two separate reports answer them from two angles:
- **[`tirz_clinical_discon_report.md`](tirz_clinical_discon_report.md)** — the clinical-trial / peer-reviewed evidence (SURMOUNT-4 and 2024–26 meta-analyses).
- **[`tirz_reddit_discon_report.md`](tirz_reddit_discon_report.md)** — what real people on Reddit who actually stopped say (1,000 threads, 328 verified first-hand reports).

---

## TL;DR — the results

**The two methods agree, and that agreement is the main result.**

- **Q1 — Regain is real, substantial, and fast.** Clinical: the average person regains ~half their lost weight within a year of stopping, fastest in the first months, then plateauing still somewhat below their starting weight (SURMOUNT-4: +14% weight and reversal of cardiometabolic gains on placebo vs −5.5% continuing). Reddit: regain is common and often fast (10–20 lb in the first 1–2 months recurs) **but not inevitable** — durable multi-year maintenance is abundantly documented. The Reddit-only signal the trials don't show: **what separates maintainers from regainers is behavior** — maintainers describe a *system* (calorie tracking, protein, resistance training, sometimes a maintenance microdose); regainers most often describe *no system*.
- **Q2 — "Metabolic dependency / damage" is not supported.** Clinical: no excess adaptive thermogenesis, lean-mass loss is the normal ~75/25 fat/lean ratio, and you stay *below* baseline, not worse than it — weight returns because the underlying obesity biology resumes, not because the drug broke anything. Reddit: matches this almost exactly — people describe appetite/"food noise" returning *to pre-drug baseline*, not below it; a genuine "worse than before" group exists but is a small minority (~6–8 reports, mostly non-tirz/subjective), and a roughly equal-sized group reports appetite and fullness returning to normal.

**One honest divergence in framing:** the clinical data is a *population average* (you can read "half comes back" as a rate); the Reddit data is **not a prevalence estimate** (see below) — it shows the *range* of real outcomes and what drives them, not how common each is.

---

## How we asked Q1 & Q2 with clinical data

Run as an automated **deep-research pass** over the published literature:

1. **Decompose** the two questions into distinct search angles (withdrawal RCTs, regain trajectory/meta-analyses, adaptive thermogenesis/calorimetry, body composition / lean mass, counter-regulatory hormone mechanisms).
2. **Search & fetch** in parallel across those angles; dedupe URLs; pull the primary sources (SURMOUNT-4 in *JAMA* + its *JAMA Int Med* post hoc, *Cell Metabolism* calorimetry RCT, *eClinicalMedicine* regain meta-analyses, DOM body-composition analysis, mechanism reviews).
3. **Extract falsifiable claims** from each source rather than vibes.
4. **Adversarially verify** each claim — multiple independent skeptics try to *refute* it against its own cited source; a claim only stands if it survives. This is the key noise filter, and it changed a conclusion: a "regain keeps progressively accelerating past baseline" claim was **refuted 0–3** and corrected to "a one-time bounce that plateaus."
5. **Synthesize** only surviving claims into the report, each line carrying its citation.

**How bias/noise was addressed, honestly:**
- Every quantitative claim is tied to a numbered primary source; the report **separates strong evidence from weak/extrapolated evidence** explicitly.
- Stated limits we did *not* paper over: **no RCT has tracked anyone beyond ~1 year off-drug** (the "plateaus below baseline" claim is extrapolated); the reassuring thermogenesis finding rests on **one small n=55, 18-week** study that measured adaptation *during* loss, not after stopping; some dose/lean-mass figures come from SURMOUNT-1 / SURMOUNT-CN, **not the withdrawal trial**; the hormone-rebound mechanism is **borrowed from class-wide GLP-1 / post-loss physiology**, not measured after tirzepatide withdrawal specifically.

---

## How we asked Q1 & Q2 with Reddit

Run as a **scrape-then-hand-read** pipeline (all scraping proxied RSS — see the
repo-root [`README.md`](../../../README.md)):

1. **Scrape**, two rounds, into one resume-safe dataset: **1,000 unique threads / 36,774 comments**. Round 1 targeted regain/maintain/metabolism queries plus wholesale sweeps of "graduate" subs; round 2 deliberately **broadened into the big active drug subs** (Mounjaro, Zepbound, Ozempic, Semaglutide, loseit) and new query angles (cost-forced stops, tolerance, long-haul, recomp, set-point, pauses) to widen coverage and find only *new* threads.
2. **Machine pre-filter** the ~37,800 text units down to **1,940 candidates** that plausibly describe a personal off-drug experience.
3. **Hand-read** every candidate with **34 parallel reviewer agents** applying one strict credibility bar.
4. **Aggregate** the survivors (deduped by URL) → **328 verified personal off-drug reports**, each tagged with outcome, timeline, metabolism commentary, attribution, and a tier.

**The credibility rule (the whole point):** a report counts **only** if it is
first-person lived experience **and** the person actually stopped or reduced the
drug. Speculation, fear, "I heard," "studies show," "my doctor said," and
still-on-the-drug posts were excluded — **only ~17% of candidates survived**, the
top exclusion reason being "still on the drug / never actually stopped." Every
cited report links to its exact post or comment. Evidence was tiered: **Tier A**
= timeline + quantified, **Tier B** = clear direction but vaguer; "maintained"
with <3 months off was downgraded to *too-soon*.

**How bias/noise was addressed, honestly:**
- **The big caveat, stated up front in the report: this is NOT a prevalence estimate.** r/GLPGrad ("graduates") supplies ~62% of reports because that's simply where off-drug stories concentrate — round 2 confirmed the active drug subs are mostly *current* users with few off-drug stories at all. So the maintain-vs-regain counts show the *range and drivers* of outcomes, not a real-world rate.
- **Survivorship bias cuts both ways** and we say so: graduate subs over-represent invested maintainers; drug subs over-represent current users.
- **~53% of the corpus is non-tirzepatide GLP-1**, kept only as supporting context and labeled where quoted; the tirz-only slice (155 reports) tells the same story.
- **No objective measures** — "metabolism" claims are self-perceived (almost no DEXA/RMR; the one TDEE figure is self-calculated, n=1), and **RSS carries no upvote data**, so we can't weight by community agreement.
- Counterpoints were sought deliberately (separate query buckets for *maintain* as well as *regain*), so the corpus isn't stacked toward the scarier answer.

---

## Where to go next
- Numbers, quotes, and the pro/against scorecard → **[`tirz_reddit_discon_report.md`](tirz_reddit_discon_report.md)**.
- Trial tables, mechanisms, and references → **[`tirz_clinical_discon_report.md`](tirz_clinical_discon_report.md)**.
- The pipeline scripts and raw data → the project [`README.md`](../README.md).
