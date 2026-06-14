#!/usr/bin/env python3
"""
Extract the "useful core" from data/gi_all.json: every text unit (post body or
comment) that mentions BOTH a GI symptom AND at least one candidate
intervention. Writes:
  - data/gi_core.jsonl  : one JSON record per unit, FULL text + tags (for an LLM)
  - data/gi_core.md     : same, human-readable
Each record carries the comment-level permalink so any claim is traceable.
Mirrors the taxonomy in analyze_gi.py. See gi_symptom_scrape.md for the goal.
"""
import json, re, html

POSTS = json.load(open("data/gi_all.json"))

INTERVENTIONS = [
    ("imodium_loperamide", r"imodium|loperamide|lopermide"),
    ("fiber_psyllium", r"psyllium|metamucil|\bfiber\b|fibre|benefiber"),
    ("pepto_bismuth", r"pepto|bismol|bismuth"),
    ("zofran_ondansetron", r"zofran|ondansetron|ondansatron"),
    ("dramamine_meclizine_antihistamine", r"dramamine|meclizine|meclazine|dimenhydrinate|bonine|antihistamine|benadryl"),
    ("ginger", r"\bginger\b"),
    ("peppermint", r"peppermint|\bmint tea\b|altoid"),
    ("vitb6", r"\bb6\b|b-6|pyridoxine|unisom"),
    ("electrolytes_hydration", r"electrolyt|\blmnt\b|hydrat|liquid iv|pedialyte|drink water|\bsalt\b"),
    ("probiotics", r"probiotic|\bkefir\b|yogurt|kombucha"),
    ("simethicone_gasx", r"simethicone|gas-x|gas x|gasx"),
    ("lower_titrate_down", r"lower(ed)? (the )?dose|lower dosage|drop(ped)? (down|the dose)|smaller dose|micro ?dose|titrat\w* down|go(ing)? back down|dial(ed)? back|reduc\w+ (the )?dose|went down to|back to \d"),
    ("split_2x_week", r"split\w* (the |my )?dose|split dosing|twice a week|2x ?(a|per)? ?week|two doses|split it|dosing twice|half twice"),
    ("pin_timing", r"pin at night|inject at night|dose at night|before bed|nighttime dose|morning (pin|dose|inject)|pin in the morning|switch\w* (the )?day|change\w* (the )?day|different day"),
    ("eat_before_pin", r"eat before (you )?pin|eat before (the |my )?(shot|inject|dose)|don'?t (pin|inject|dose) (on )?(an )?empty|full stomach|never pin fasted|food before"),
    ("low_fat_avoid_greasy", r"low ?fat|avoid\w* (fatty|greasy|fried)|fatty food|greasy food|fried food|too much fat|high fat"),
    ("bland_small_meals", r"bland (diet|food)|brat diet|small(er)? meals|smaller portion|eat less|smaller meal|light meals|don'?t overeat"),
    ("cagrilintide", r"cagri|cagrilintide|amylin"),
    ("switch_drug_offgoal", r"switch\w* to (tirz|sema|mounjaro|ozempic|zepbound|wegovy)|tirzepatide instead|semaglutide instead|went back to (tirz|sema)|moved to (tirz|sema)"),
    ("fasting", r"\bfast\w*\b|intermittent fasting|skip\w* (breakfast|meals)|wait to eat"),
]
RX = [(name, re.compile(p, re.I)) for name, p in INTERVENTIONS]
SYM = re.compile(r"diarrh|nausea|nauseous|vomit|throw\w* up|sick to my stomach|upset stomach|sulfur burp|sulphur burp|the runs|loose stool|stomach (issue|problem|cramp|pain)|gi (issue|problem|symptom|side)", re.I)
POS = re.compile(r"help(ed|s)?\b|work(ed|s)?\b|stop(ped|s)?\b|went away|no more|cleared (it )?up|got rid|fixed|saved (me|my)|life ?saver|game ?changer|did the trick|subsid\w+|manageable|better now", re.I)
NEG = re.compile(r"didn'?t help|did(n'?t| not) (help|work|do)|no help|doesn'?t help|made it worse|worse\b|useless|no difference|nothing (helped|worked)", re.I)
PERSONAL = re.compile(r"\bi (take|took|use|used|tried|did|do|started|switched|eat|ate|inject|injected|pin|pinned|drink|drank|added|swear by|found|lowered|dropped|split|reduced)\b|works for me|helped me|for me\b|my go.?to", re.I)
FEMALE = re.compile(r"(i'?m a (woman|girl|female))|as a (woman|female)|\bfemale\b|\bwoman\b|\b\d{2}\s?f\b|\bf\s?\d{2}\b|i'?m female|my wife|my girlfriend", re.I)
LOWDOSE = re.compile(r"\b1\.?5?\s?mg|\b1\s?mg|\b2\s?mg|\b3\s?mg\b|0\.5\s?mg", re.I)
EARLY = re.compile(r"\bweek [1-8]\b|\b[1-8] weeks?\b|first month|month in|just started|new to|few weeks", re.I)
ACUTE = re.compile(r"that night|same night|night of (the |my )?(shot|pin|dose|injection)|next day|day after|dose night|injection (night|day)|after i pin", re.I)

def clean(t):
    return html.unescape(t or "").replace("\r", " ").strip()

def flags(t):
    return {k: bool(rx.search(t)) for k, rx in
            [("pos", POS), ("neg", NEG), ("personal", PERSONAL),
             ("female", FEMALE), ("lowdose", LOWDOSE), ("early", EARLY), ("acute", ACUTE)]}

def emit_units():
    for p in POSTS:
        body = clean(p.get("title", "")) + " . " + clean(p.get("body", ""))
        yield dict(where="post", post_id=p.get("id"), subreddit=p.get("subreddit"),
                   query=p.get("query"), link=p.get("url"), author=p.get("author"),
                   created=p.get("created"), text=body)
        for c in p.get("comments", []):
            yield dict(where="comment", post_id=p.get("id"), subreddit=p.get("subreddit"),
                       query=p.get("query"), link=c.get("url"), author=c.get("author"),
                       created=c.get("created"), text=clean(c.get("body", "")))

core = []
for u in emit_units():
    t = u["text"]
    if not SYM.search(t):
        continue
    matched = [name for name, rx in RX if rx.search(t)]
    if not matched:
        continue
    u["interventions"] = matched
    u["flags"] = {k: v for k, v in flags(t).items() if v}
    core.append(u)

with open("data/gi_core.jsonl", "w") as f:
    for u in core:
        f.write(json.dumps(u, ensure_ascii=False) + "\n")

with open("data/gi_core.md", "w") as f:
    f.write(f"# GI core — {len(core)} units mentioning a symptom AND an intervention\n\n")
    f.write("One block per unit. `interventions` = which candidate fixes were name-matched; "
            "`flags` = efficacy/proximity signals. Link is comment-level where where=comment.\n\n")
    for i, u in enumerate(core, 1):
        f.write(f"### {i}. [{u['where']}] q='{u['query']}' — {', '.join(u['interventions'])}\n")
        f.write(f"flags: {', '.join(u['flags']) or '(none)'}  |  {u['link']}\n\n")
        f.write(f"> {u['text']}\n\n")

print(f"core units: {len(core)}")
print("wrote data/gi_core.jsonl and data/gi_core.md")
