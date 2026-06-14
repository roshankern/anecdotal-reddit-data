#!/usr/bin/env python3
"""
Analyze data/gi_all.json -> intervention prevalence + efficacy signal + example
comments. Heuristic NLP (keyword/regex) over post bodies + comments. Outputs:
  - prints a corpus + per-intervention stats table
  - data/gi_analysis.json  (machine-readable rollup)
  - data/gi_examples.md    (top candidate comments per intervention, with links)
This is decision-support, not ground truth: a human reads gi_examples.md to
confirm ratings. See gi_symptom_scrape.md.
"""
import json, re, math, html, collections

POSTS = json.load(open("data/gi_all.json"))

# ---- intervention taxonomy: name -> (targets, regex of trigger terms) ----
INTERVENTIONS = [
    ("Imodium / loperamide", "diarrhea", r"imodium|loperamide|lopermide"),
    ("Fiber (psyllium/Metamucil)", "diarrhea", r"psyllium|metamucil|\bfiber\b|fibre|benefiber|fiber supplement"),
    ("Pepto-Bismol / bismuth", "both", r"pepto|bismol|bismuth"),
    ("Zofran / ondansetron (Rx)", "nausea", r"zofran|ondansetron|ondansatron"),
    ("Dramamine / meclizine / antihistamine", "nausea", r"dramamine|meclizine|meclazine|dimenhydrinate|bonine|antihistamine|benadryl"),
    ("Ginger", "nausea", r"\bginger\b|gravol ginger|ginger chew|ginger ale|ginger tea"),
    ("Peppermint", "nausea", r"peppermint|\bmint tea\b|altoid"),
    ("Vitamin B6 (pyridoxine)", "nausea", r"\bb6\b|b-6|pyridoxine|unisom"),
    ("Electrolytes / hydration", "both", r"electrolyt|\blmnt\b|hydrat|liquid iv|liquid i\.v|pedialyte|drink water|salt"),
    ("Probiotics", "diarrhea", r"probiotic|\bkefir\b|yogurt|kombucha"),
    ("Simethicone / Gas-X", "gas", r"simethicone|gas-x|gas x|gasx"),
    ("Lower dose / titrate down", "both", r"lower(ed)? (the )?dose|lower dosage|drop(ped)? (down|the dose)|smaller dose|micro ?dose|titrat\w* down|go(ing)? back down|dial(ed)? back|reduc\w+ (the )?dose|went down to|back to \d"),
    ("Split dose / 2x per week", "both", r"split\w* (the |my )?dose|split dosing|twice a week|2x ?(a|per)? ?week|two doses|split it|dosing twice|half twice"),
    ("Pin timing (night/morning/day shift)", "both", r"pin at night|inject at night|dose at night|before bed|nighttime dose|morning (pin|dose|inject)|pin in the morning|switch\w* (the )?day|change\w* (the )?day|different day"),
    ("Eat before pin / not fasted", "nausea", r"eat before (you )?pin|eat before (the |my )?(shot|inject|dose)|don'?t (pin|inject|dose) (on )?(an )?empty|full stomach|never pin fasted|food before"),
    ("Low-fat diet / avoid fatty/greasy", "diarrhea", r"low ?fat|avoid\w* (fatty|greasy|fried)|fatty food|greasy food|fried food|too much fat|high fat"),
    ("Bland diet / small meals", "both", r"bland (diet|food)|brat diet|small(er)? meals|smaller portion|eat less|smaller meal|light meals|don'?t overeat"),
    ("Cagrilintide adjunct", "nausea", r"cagri|cagrilintide|amylin"),
    ("Switch drug (tirz/sema) [off-goal]", "both", r"switch\w* to (tirz|sema|mounjaro|ozempic|zepbound|wegovy)|tirzepatide instead|semaglutide instead|went back to (tirz|sema)|moved to (tirz|sema)"),
    ("Fasting / wait to eat", "nausea", r"\bfast\w*\b|intermittent fasting|skip\w* (breakfast|meals)|wait to eat"),
]

POS = re.compile(r"help(ed|s)?\b|work(ed|s)?\b|stop(ped|s)?\b|went away|no more|cleared (it )?up|cleared up|got rid|fixed|saved (me|my)|life ?saver|game ?changer|does the trick|did the trick|took care of|subsid\w+|manageable|better now|no (more )?(diarrhea|nausea|issues|problems)|huge difference|made it bearable|tolerable now|a godsend|miracle")
NEG = re.compile(r"didn'?t help|did(n'?t| not) (help|work|do)|no help|doesn'?t help|does not help|made it worse|made me worse|worse\b|useless|no difference|nothing (helped|worked|works)|waste of|not help|stopped working|made me sick")
# first-person "I actually did this"
PERSONAL = re.compile(r"\bi (take|took|takes|use|used|tried|did|do|started|start|switched|switch|eat|ate|inject|injected|pin|pinned|drink|drank|add(ed)?|run|ran|swear by|found|lowered|dropped|split|reduced|moved|go|went)\b|works for me|helped me|saved me|for me\b|my go.?to|i'?ve been (taking|using|doing)")
ADVICE = re.compile(r"\byou (should|could|can|might|need to|want to)\b|\btry\b|\bgive .* a (try|shot)\b|i (would|'?d) (try|take|do|suggest|recommend)|suggest|recommend|just take|have you tried")

# profile signals (proximity to: female, ~26, 1-3mg, ~4wk, acute post-dose)
FEMALE = re.compile(r"\b(i'?m a (woman|girl|female))|as a (woman|female)|\bfemale\b|\bwoman\b|\b\d{2}\s?f\b|\bf\s?\d{2}\b|\b\d{2}/?f\b|\bf/?\d{2}\b|i'?m female|my wife|my girlfriend|my (sister|fiance|fiancee)")
LOWDOSE = re.compile(r"\b1\.?5?\s?mg|\b1\s?mg|\b2\s?mg|\b3\s?mg\b|0\.5\s?mg")
EARLY = re.compile(r"\bweek (one|two|three|four|five|1|2|3|4|5|6|7|8)\b|\b[1-8] weeks?\b|first month|month in|just started|new to|starter dose|few weeks")
ACUTE = re.compile(r"\bthat night\b|same night|night of (the |my )?(shot|pin|dose|injection)|next day|day after|day of (the )?(shot|pin|dose)|dose night|injection (night|day)|hours after (pinning|injecting|my shot)|after i pin")

SYMPTOM = re.compile(r"diarrh|nausea|nauseous|vomit|throw\w* up|sick to my stomach|upset stomach|sulfur burp|sulphur burp|the runs|loose stool|stomach (issue|problem|cramp|pain)|gi (issue|problem|symptom|side)")

def clean(t):
    return html.unescape(t or "").replace("\n", " ").strip()

def score_unit(text):
    t = text.lower()
    return {
        "symptom": bool(SYMPTOM.search(t)),
        "pos": bool(POS.search(t)),
        "neg": bool(NEG.search(t)),
        "personal": bool(PERSONAL.search(t)),
        "advice": bool(ADVICE.search(t)),
        "female": bool(FEMALE.search(t)),
        "lowdose": bool(LOWDOSE.search(t)),
        "early": bool(EARLY.search(t)),
        "acute": bool(ACUTE.search(t)),
    }

# iterate every text unit (post body + each comment)
units = []  # (where, link, author, text, scores)
for p in POSTS:
    body = clean(p.get("body"))
    blob = clean(p.get("title")) + " . " + body
    units.append(("post", p.get("url"), p.get("author"), blob, score_unit(blob)))
    for c in p.get("comments", []):
        cb = clean(c.get("body"))
        units.append(("comment", c.get("url"), c.get("author"), cb, score_unit(cb)))

n_posts = len(POSTS)
n_comments = sum(len(p.get("comments", [])) for p in POSTS)
n_units = len(units)
n_symptom_units = sum(1 for u in units if u[4]["symptom"])

rows = []
examples = {}
for name, targets, pat in INTERVENTIONS:
    rx = re.compile(pat, re.I)
    hits = [u for u in units if rx.search(u[3].lower())]
    # require the intervention to co-occur with a GI symptom OR clear efficacy
    rel = [u for u in hits if u[4]["symptom"] or u[4]["pos"] or u[4]["neg"]]
    pers_pos = [u for u in rel if u[4]["personal"] and u[4]["pos"] and not u[4]["neg"]]
    pers_neg = [u for u in rel if u[4]["personal"] and u[4]["neg"]]
    advice_only = [u for u in rel if u[4]["advice"] and not u[4]["personal"]]
    # proximity: a personal-positive report carrying female + (lowdose or early or acute)
    def prox(u):
        s = u[4]; score = 0
        score += 2 if s["female"] else 0
        score += 1 if s["lowdose"] else 0
        score += 1 if s["early"] else 0
        score += 1 if s["acute"] else 0
        return score
    gold = sorted(pers_pos, key=prox, reverse=True)
    rows.append({
        "intervention": name, "targets": targets,
        "n_mention": len(hits), "n_relevant": len(rel),
        "n_personal_pos": len(pers_pos), "n_personal_neg": len(pers_neg),
        "n_advice": len(advice_only),
        "n_female_pos": sum(1 for u in pers_pos if u[4]["female"]),
        "n_acute_pos": sum(1 for u in pers_pos if u[4]["acute"]),
        "best_prox": prox(gold[0]) if gold else 0,
    })
    # keep top example units for human read
    ex = []
    for u in gold[:6] + pers_neg[:2] + advice_only[:2]:
        ex.append({"where": u[0], "link": u[1], "author": u[2],
                   "flags": {k: v for k, v in u[4].items() if v},
                   "text": u[3][:600]})
    examples[name] = ex

# ---- Wilson 95% CI + binomial sign test on personal pos vs neg ----
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (p, max(0, c-h), min(1, c+h))

def binom_p_two_sided(k, n, p=0.5):
    # exact two-sided binomial test, P(X>=k or symmetric tail)
    if n == 0: return 1.0
    from math import comb
    def pmf(i): return comb(n, i) * p**i * (1-p)**(n-i)
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n+1) if pmf(i) <= obs + 1e-12))

print(f"\n=== CORPUS ===")
print(f"posts={n_posts}  comments={n_comments}  text_units(post+comments)={n_units}")
print(f"units mentioning a GI symptom: {n_symptom_units} ({100*n_symptom_units/n_units:.0f}%)")
qs = collections.Counter(p.get("query") for p in POSTS)
print(f"contributing queries: {len(qs)}")

print(f"\n=== INTERVENTIONS (sorted by personal-positive reports) ===")
rows.sort(key=lambda r: (r["n_personal_pos"], r["n_relevant"]), reverse=True)
hdr = f"{'intervention':40s} {'tgt':8s} {'ment':>5s} {'rel':>4s} {'P+':>4s} {'P-':>4s} {'adv':>4s} {'F+':>3s} {'acu':>3s} {'pos%':>9s} {'binom_p':>8s}"
print(hdr); print("-"*len(hdr))
for r in rows:
    k, nn = r["n_personal_pos"], r["n_personal_pos"] + r["n_personal_neg"]
    p, lo, hi = wilson(k, nn)
    bp = binom_p_two_sided(k, nn)
    pct = f"{100*p:.0f}%" if nn else "  -"
    print(f"{r['intervention']:40s} {r['targets']:8s} {r['n_mention']:5d} {r['n_relevant']:4d} "
          f"{r['n_personal_pos']:4d} {r['n_personal_neg']:4d} {r['n_advice']:4d} "
          f"{r['n_female_pos']:3d} {r['n_acute_pos']:3d} {pct:>9s} {bp:8.3f}")
    r["pos_frac"], r["pos_lo"], r["pos_hi"], r["binom_p"] = p, lo, hi, bp

json.dump({"corpus": {"posts": n_posts, "comments": n_comments, "units": n_units,
                       "symptom_units": n_symptom_units},
           "interventions": rows}, open("data/gi_analysis.json", "w"), indent=2)

with open("data/gi_examples.md", "w") as f:
    f.write("# GI intervention — top candidate comments (auto-surfaced)\n\n")
    f.write("Each block = highest-proximity *personal positive* reports, then a "
            "couple of *negative* and *advice-only* for balance. Links are "
            "comment-level where the unit is a comment.\n\n")
    for r in rows:
        name = r["intervention"]
        f.write(f"\n## {name}  (targets {r['targets']})\n")
        f.write(f"mentions={r['n_mention']} relevant={r['n_relevant']} "
                f"personal+={r['n_personal_pos']} personal-={r['n_personal_neg']} "
                f"advice={r['n_advice']} female+={r['n_female_pos']} acute+={r['n_acute_pos']}\n\n")
        for e in examples[name]:
            flags = ",".join(k for k in e["flags"] if k in
                             ("pos","neg","personal","advice","female","lowdose","early","acute"))
            f.write(f"- **[{e['where']}]** ({flags}) {e['link']}\n")
            f.write(f"  > {e['text']}\n\n")
print("\nwrote data/gi_analysis.json and data/gi_examples.md")
