# Retatrutide GI — Full Hand-Verified Read (698 units) — what changed

**For:** the friend — F, ~26, 2 mg/week, ~4 weeks in, **diarrhea + nausea the night she
injects (Friday)**. **Goal:** keep her **on reta** and make dose-night tolerable.
**Date:** 2026-06-10. **Not medical advice** — anecdotal, grey-market, self-reported.

This report supersedes the first-pass `gi_report.md`. It is built from a **hand read of
all 698 units** in `data/gi_core.jsonl` (12 reviewers, one per batch), not a keyword
rollup. Outputs:

- **`data/gi_raw_full.csv`** — **792 hand-verified (person × intervention) rows** (vs 45 in
  the first pass), covering **320 distinct posts/threads**. Negatives kept.
- **`data/gi_interventions_full.csv`** — **31 interventions** rated High/Med/Low.

---

## 1. Headline: the fuller read CONFIRMS the core recommendation — and makes it stronger

The first pass's central message was right and the bigger sample reinforces it:

> **Her week-5 plan ("two 2 mg shots = 4 mg/week") is a dose DOUBLING, not a split, and
> up-titration is the single most reliable cause of exactly her symptoms.**

In the hand read this is the **cleanest signal in the entire corpus**. I split the dose
lever into its two real halves and counted them honestly:

| Signal | Personal reports | Direction |
|---|---|---|
| **Going UP in dose triggered/worsened GI** | **65** (60 "it wrecked me", incl. many 2→4 mg jumps) | overwhelming |
| **Holding / lowering relieved GI** | 95 (51 worked + 10 partial vs **11 said it didn't**) | strong but not guaranteed |

The "going up wrecks me" half is **more uniform** (60 of 65) than the "lowering fixes me"
half — i.e. the evidence that her 4 mg plan will backfire is even firmer than the evidence
that any given remedy will rescue her. **Hold at 2 mg until she has 2+ tolerable Friday
nights; do not double.** That's the whole report in one line.

---

## 2. Where the fuller read CHANGES the first-pass conclusions

The first pass leaned on keyword positive-rates (82–100% for everything). Hand-reading the
outcomes surfaced **many more personal negatives**, which moves several ratings:

| Intervention | First pass | **Now** | Why it changed |
|---|---|---|---|
| **Loperamide (Imodium)** | High ("10/10") | **Med** | Hand read = 4 worked / **5 partial** / **3 didn't**. Relief is usually *temporary* (hours) and masks dehydration. Good as-needed rescue, not a reliable fix. |
| **Split same dose 2×/wk** | High (clean) | **High, but flagged mixed** | Real: ~**10 personal "didn't help / prolonged low-grade symptoms"** (half-life ~5–8 d means you never fully clear). Still High (targets her peak, keeps weekly total flat, Tier-1 win) — but it's "try and see," not a sure thing. |
| **Electrolytes/hydration** | High (85%) | **High, reframed** | **24 personal misses** — it does NOT stop the diarrhea/nausea for many. Keep High for *prevalence + treating the real danger (dehydration)*, but it's **supportive, not curative.** |
| **Fiber (psyllium)** | Med | **Med (confirmed double-edged)** | Now an even split: **12 worked / 12 didn't**, plus detailed reports of high fiber *worsening* stasis. Daily low-dose, never on a bad night. |
| **Smaller/bland meals** | Med | **High** | Cleanest diet signal (14 worked / 7 partial / **1 didn't**) **plus a Tier-1 near-profile woman** (1 mg, wk6: smaller meals → "none of those issues"). Deserves a bump. |
| **Avoid fatty/greasy food** | High | **High (reaffirmed)** | 31 worked / 5 didn't, crisp mechanism for her burp→diarrhea chain. Unchanged. |
| **Zofran** | High | **High (reaffirmed)** | 14 worked / 10 partial / 3 didn't for nausea; Rx. Best taken *on* dose day. |

### New interventions the first pass missed (now in the table)
- **Antacid / acid reducer (famotidine, omeprazole)** — **Med.** 6 worked / 2 partial / 1
  didn't, all personal. Specifically for the **reflux / heartburn / "acid" nausea and
  sulfur-burp** flavor that a slowed stomach produces. Cheap, very relevant to her.
- **Digestive enzymes** — **Med.** Aimed at the **fermentation → sulfur-burp → diarrhea**
  root; one detailed user said enzymes "changed everything" where simethicone barely did.
- **"Don't lie down after eating" / upright after the Friday meal** — Low but mechanistic:
  it's the exact lever behind the gastroparesis→fermentation→diarrhea cascade described in
  the corpus's single best mechanistic comment.
- **Avoid alcohol on dose day** — Med, clean co-trigger, free.
- **Promethazine (Rx)** — Med, named as the stronger backup when Zofran isn't enough.
- **Magnesium / MiraLAX** — flagged **Low / off-target**: these are for the *opposite*
  problem (reta constipation) and would worsen her diarrhea. Listed so they aren't confused
  as a diarrhea fix.

### The one statistical nuance, reaffirmed
Positive rates are still **survivorship-inflated** and **not** separable between
interventions. The only semi-controlled signal remains the **within-person dose change**.
The hand read also found a real **counter-signal**: a handful of people got a GI flare
1–2 days *after* lowering, consistent with a **falling-drug-level** trigger rather than
dose magnitude alone. So "lower the dose" helps most people but isn't universal — another
reason to **hold steady at 2 mg** (steady level) rather than bounce the dose around.

---

## 3. Ranked by how likely each is to help HER (relative), with evidence quality

Full detail in `data/gi_interventions_full.csv`. Ranked for her specific case (acute Friday
diarrhea+nausea, keep on reta), best first.

1. **Manage the dose — hold 2 mg, don't jump to 4 mg (or lower).** *Strongest evidence in
   the corpus:* 160 personal dose↔symptom reports, **60 of 65 say going UP triggered her
   exact symptoms**; the only semi-controlled (within-person) signal. Lowering isn't
   guaranteed (11 misses) — favor a steady dose. **This is her #1 lever.**
2. **Avoid fatty/greasy/fried food (+ alcohol) on Friday.** *Strong, clean:* 31 worked / 5
   didn't, and the mechanism directly explains her burp→diarrhea chain. Free.
3. **Electrolytes + aggressive hydration Fri–Sun.** *Most prevalent (98 personal) but
   supportive, not curative:* 24 personally said it didn't stop the GI. Prevents the real
   danger (dehydration / ER visits). Near-zero downside.
4. **Split the *same* 2 mg into 1 mg ×2/wk.** *Good mechanism, mixed evidence:* 19 worked
   but ~10 misses (half-life prolongs low-grade symptoms). Lowers her Friday peak, weekly
   total flat. Try-and-see. (NOT 2 mg ×2 = 4 mg.)
5. **Smaller / bland meals on dose day.** *Clean:* 14 worked / 7 partial / 1 didn't, plus a
   Tier-1 near-profile match. Cheap, on-goal.
6. **Zofran (ondansetron, Rx) for nausea.** *Strong for nausea:* 14 worked / 10 partial / 3
   didn't; gold-standard mechanism. Ask a doctor; take on dose day.
7. **Imodium (loperamide) as-needed diarrhea rescue.** *Works but often temporary:* 4 worked
   / 5 partial / 3 didn't. Pair with electrolytes (it masks fluid loss).
8. **Pepto-Bismol.** *OK all-rounder incl. sulfur burps, milder:* 10 worked / 8 partial / 7
   didn't.
9. **Antacid / famotidine (or omeprazole).** *Small but clean, NEW:* 6 worked / 2 partial /
   1 didn't — for the reflux/heartburn/"acid" nausea + sulfur-burp flavor.
10. **Ginger / Dramamine-meclizine for nausea.** *Decent personal support, mild:* ginger 9
    worked/2 didn't; Dramamine 3 worked/3 partial/0 misses (sedating = good at night).
11. **Digestive enzymes.** *Modest, targets the fermentation/sulfur-burp root:* 4 worked / 2
    partial / 1 didn't.
12. **Fiber (psyllium).** *Genuinely double-edged:* 12 worked / 12 didn't; can worsen stasis.
    Daily low-dose only — never on an already-bad night.
13. **Probiotics / kefir / yogurt.** *Slow baseline, not an acute fix:* 6 worked / 3 partial,
    0 misses, but days-to-weeks to matter.
14. **Pin at night + light low-fat pre-pin meal.** She *already* pins at night (good);
    sensible but advice-heavy. Stay upright after eating.
15. **Thin / off-goal adjuncts (lowest):** simethicone/Gas-X (gas only) · promethazine (Rx
    backup) · peppermint (n=7) · B6 (thin, safe) · injection-site change (mixed) · magnesium/
    MiraLAX (off-target — *worsens* diarrhea) · gut-repair peptides (adds a grey-market
    peptide) · **cagrilintide** (added for appetite, can *add* nausea) · **switching off reta
    to tirz/sema** (capped lowest — abandons the goal of proving reta works for her).

---

## 4. Final recommendation for her (unchanged in substance, firmer in evidence)

1. **Do NOT go to 4 mg/week.** Her "split into two 2 mg shots" = **doubling** her weekly
   dose, which is the #1 reported cause of her exact dose-night symptoms (60/65 personal
   "going up wrecked me"). Hold **2 mg** until she's had **2+ tolerable Friday nights.**
2. **If she wants smoother Fridays at the same exposure, genuinely split:** **1 mg Mon +
   1 mg Thu** (= 2 mg/week). Same weekly dose, lower peak. Helped a near-profile woman; ~1 in
   3 splitters found it didn't help much, so it's try-and-see.
3. **Stack the cheap dose-day habits:** electrolytes + water Fri–Sun; **light, low-fat,
   smaller** Friday meal, no fried food/alcohol; stay upright a while after eating; she
   already **pins at night** (good).
4. **As-needed:** Imodium for the acute diarrhea **with** electrolytes (it masks fluid loss);
   ginger/Dramamine or an **antacid (famotidine)** if the nausea is reflux-y; **ask her
   doctor about Zofran.**
5. **Red flags = doctor, not Reddit:** diarrhea/vomiting that won't stop, dizziness, very
   dark/low urine, fainting. The corpus has multiple ER/dehydration stories, including a
   collapse-with-seizure. Not a tough-it-out situation.

---

## 5. Honest limits of this fuller read
- 792 rows is a big anecdotal sample but still **survivorship-biased and uncontrolled.**
  Ranking is prevalence + proximity + mechanism, **not** the (uniformly high) success rates.
- **True Tier-1 matches stay rare: 7 rows across 4 people** (F20 and F23 who lowered/held and
  resolved; an F who preferred a 1 mg split; a 1 mg wk-6 woman helped by smaller meals). Her
  gold-standard evidence is thin — which is itself a finding, not a failure of the search.
- Interventions are bundled (people change 3 things at once); credit can't be cleanly assigned.
- Drug spread: 778 reta rows, ~14 cross-drug (tirz/sema/cagri) flagged. r/Retatrutide only.
- Nothing here overrides her own clinician.
