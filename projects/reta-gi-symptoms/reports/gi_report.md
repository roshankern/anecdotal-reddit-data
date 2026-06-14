# Retatrutide GI Symptoms — What Actually Helps (Peer-Data Report)

**For:** a friend — F, ~26, 2 mg/week, ~4 weeks in, **diarrhea + nausea the night she
injects (Friday)**.
**Goal:** find what keeps her **on reta** and makes dose-night tolerable, ranked by
how likely it is to help *her*.
**Source:** r/Retatrutide, scraped via Reddit RSS through proxies (see `README.md`).
**Date:** 2026-06-10. **Not medical advice** — all anecdotal, grey-market, self-reported.

---

## 1. Where the data came from (and how much was actually useful)

| Stage | Count | Note |
|---|---:|---|
| Unique posts scraped | **600** | 25 symptom+remedy search queries, deduped |
| Comments scraped | **14,939** | each with its own permalink |
| Total text units (posts + comments) | **15,539** | the analyzable corpus |
| …units mentioning a **GI symptom** | **1,366 (8.8%)** | the rest is dosing/results/sourcing chatter |
| …units mentioning **any intervention** | **2,669 (17.2%)** | |
| **Symptom AND intervention in same unit** | **639 (4.1%)** | **the useful core** |
| …of those, **first-person "I tried it & it worked"** | **~674 mentions** | across 19 interventions (a unit can name several) |
| **Hand-verified rows** in `gi_raw.csv` | **45** | each one I read and can vouch for, with a link |

**Honest read on usefulness:** ~96% of the raw corpus is *not* directly about fixing GI
symptoms — it's progress posts, dosing/sourcing talk, etc. The signal lives in ~640
symptom×remedy text units. That's still a large, rich sample for an anecdotal question,
and because comments carry their own permalinks, every claim is traceable to a person.
The highest-value bucket — *someone close to her profile who personally tried something
and it worked* — is **thin** (a handful of near-exact matches; see Tier 1 rows), which is
expected: young women at 2 mg who solved dose-night diarrhea and wrote it up are rare.

Outputs: **`data/gi_interventions.csv`** (ranked), **`data/gi_raw.csv`** (per-report),
`data/gi_examples.md` (the underlying quotes), `data/gi_analysis.json` (raw counts).

---

## 2. Can we claim statistical significance? Mostly no — and here's why

I ran it so you can see the numbers, but I want to be straight about what they mean.

**The headline stat per intervention** — "of people who tried it and reported an outcome,
what % were positive" — comes out at **82–100% for literally every intervention.** Wilson
95% CIs and exact binomial tests vs. a 50/50 coin all return p < 0.001 for the common
ones. That looks impressive and is **almost entirely an artifact of reporting bias:**

- **Survivorship/publication bias** — people post "X saved me," not "I took X, nothing
  happened." Negative trials are mostly unwritten, so the numerator is inflated everywhere.
- **No control group, no randomization, no placebo** — GLP-1 GI effects *naturally fade
  as the body adapts*, so "I did X in week 5 and felt better in week 6" can't separate X
  from time.
- **Keyword classification is fuzzy** — I'm inferring "personal" and "worked" from text;
  some are misread.
- **Confounding bundles** — people change 3 things at once (drop dose + electrolytes +
  bland food), so credit can't be assigned to one.

Because the positive rate is ~uniformly high, a test *comparing interventions to each
other* is the meaningful one — and there the differences are **not** statistically
separable: the CIs overlap heavily (e.g. Imodium 10/10 vs Zofran 28/33 vs ginger 13/15 —
all consistent with "most people who bother to report felt helped"). **So I am not
ranking by these percentages.** Ranking is **prevalence + profile-proximity + biological
mechanism**, exactly as designed.

**The one signal that *is* relatively robust** is the **dose–symptom relationship**,
because it shows up as *within-person before/after* observations (same person, dose
changed, symptoms changed) — which partially controls for individual confounders:

> Across the corpus, **going UP in dose (especially jumps to 3–4 mg+) is the single most
> common trigger of new/worse diarrhea + nausea, and lowering or holding the dose is the
> single most common thing that relieved it** (101 personal "lowering/holding helped"
> reports vs 5 that it didn't; and a long tail of "I jumped to 4 mg and got wrecked"
> stories). This is the closest thing to a real dose-response finding in the data.

That finding is the crux of her decision (Section 4).

---

## 3. Ranked interventions (full table in `data/gi_interventions.csv`)

### HIGH likelihood (do these)
| Intervention | Targets | Why it ranks High |
|---|---|---|
| **Hold / lower dose; titrate slowly** | both | Most-reported & most-consistent fix (101 personal wins / 5 fails); dose-dependent mechanism; keeps her on reta. |
| **Split the *same* weekly dose into 2 pins** | both | Lowers the per-shot peak that causes her Friday-night spike, weekly total unchanged. *Must mean 1 mg ×2, not 2 mg ×2.* |
| **Electrolytes + aggressive hydration** | both | Most-mentioned remedy overall; treats the actual danger (dehydration); zero downside. |
| **Avoid fatty/greasy/fried food on dose day** | diarrhea | Fat is the #1 named trigger; mechanism explains her exact symptom (burps → diarrhea); free. |
| **Loperamide (Imodium)** — acute rescue | diarrhea | 10/10 personal wins incl. a near-exact-profile young woman; textbook antidiarrheal. *Pair with electrolytes.* |
| **Ondansetron (Zofran)** — Rx | nausea | Gold-standard anti-emetic, many wins. **Ask a doctor.** |

### MED likelihood (reasonable additions)
Fiber (psyllium) · Pepto-Bismol · smaller/bland meals on dose day · pin-at-night + light
low-fat meal before · ginger · Dramamine/meclizine · probiotics (slow, baseline) ·
simethicone/Gas-X (for the sulfur-burp/gas part).

### LOW likelihood (weak evidence or off-goal)
Peppermint (n=2) · B6 (n=2, but very safe) · **cagrilintide** (people add it for appetite,
not GI; can *add* nausea) · **switching off reta to tirz/sema** (capped Low by design — it
abandons the goal of seeing whether reta works for her).

---

## 4. Final recommendation for her

**The most important thing in this whole report: her week-5 plan works *against* her
symptoms.**

She's at 2 mg/week, already getting dose-night diarrhea + nausea at week 4, and plans to
go to **two 2 mg shots = 4 mg/week** at week 5. In community language that's described as
"split dosing," but it is actually **doubling her weekly dose.** The data is about as
clear as anecdotal data gets: **up-titration — especially a jump to 4 mg — is the single
most common cause of exactly the symptoms she's having**, with multiple near-identical
stories ("2 mg for 4 weeks, jumped to 4 mg, got wrecked / quit"). Doubling now will very
likely make her Friday nights worse, not better.

Two different ideas are getting conflated:
- **Splitting a dose** (e.g. 1 mg Mon + 1 mg Thu) — keeps the weekly total flat and
  *lowers* each peak. This **helps** side effects. ✅
- **Increasing the dose** (2 → 4 mg/week) — raises exposure. This **drives** side effects. ❌

Her plan does the second while calling it the first.

**What the peer data supports instead (in order):**

1. **Don't increase to 4 mg yet.** Hold 2 mg/week until she's had **2+ consecutive
   tolerable dose nights.** "Don't go up until sides subside" is the most repeated advice
   in the sub. Increase later, slowly (e.g. 2 → 2.5 → 3), not a doubling.
2. **If she wants smoother dose nights at her current exposure, *split* it:** 1 mg twice a
   week (e.g. Mon + Thu) instead of 2 mg once. Same weekly dose, lower peaks. Several
   people did exactly this to tame side effects. (One or two found splitting kept low-grade
   symptoms around longer due to reta's ~5–8 day half-life — so it's "try and see.")
3. **Stack the cheap, high-confidence supportive habits on dose day:**
   - **Electrolytes + lots of water** Fri–Sun (the near-universal first move).
   - **Eat light & low-fat** Friday — no fatty/greasy/fried dinner before the pin; alcohol
     is a named co-trigger.
   - Keep **Imodium** on hand for the acute diarrhea (and keep drinking electrolytes so it
     doesn't just mask dehydration).
   - She already **pins at night** — good; that lets her sleep through the peak.
4. **For nausea specifically:** ginger or Dramamine OTC; **ask her doctor about Zofran**
   (ondansetron) — it's the standard and many reta users rely on it.
5. **Red flags = see a doctor, not Reddit:** diarrhea/vomiting that won't stop, signs of
   dehydration (dizziness, very dark/low urine, fainting) — there are several ER stories in
   this data, including a dehydration-related collapse. This is not a tough-it-out situation.

**One-line version:** the data says *hold at 2 mg (or split into 1 mg ×2), load up on
electrolytes, keep Friday's meal light and low-fat, Imodium/ginger as needed* — and
specifically **not** to jump to 4 mg while she's still reacting to 2 mg.

---

## 5. Caveats (carry these into any decision)
- All self-reported, anecdotal, grey-market. A doctor/pharmacist beats Reddit for anything
  Rx or persistent.
- GLP-1 GI effects often ease with time regardless of intervention — some "fixes" are just
  adaptation.
- The sample is whatever the searches surfaced, not a census; very-close-profile success
  stories are few, so her gold-standard matches are limited.
- Nothing here overrides her own clinician.
