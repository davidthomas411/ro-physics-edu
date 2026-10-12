"""Structure checks on every multiple-choice problem: options, answer letters, tiers, balanced tags, position balance."""
import sys, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS

strip = lambda s: re.sub(r"<[^>]+>", "", s).strip()
bad, n, tiers, letters = [], 0, collections.Counter(), collections.Counter()
for t in TOPICS:
    per = collections.Counter(p["lvl"] for p in t["problems"])
    if t["problems"] and (len(t["problems"]) < 6): bad.append((t["id"], "tier balance", dict(per)))
    for p in t["problems"]:
        n += 1; tiers[p["lvl"]] += 1; o = p["opts"]; q = strip(p["q"])[:60]
        if p.get("kind"):
            if p["lvl"] not in ("Easy", "Moderate", "Challenging"): bad.append((t["id"], "tier", p["lvl"], q))
            if not strip(p["a"][1]): bad.append((t["id"], "empty explanation", q))
            for tag in ("sup", "sub", "b", "i"):
                if p["a"][1].count(f"<{tag}>") != p["a"][1].count(f"</{tag}>") or p["q"].count(f"<{tag}>") != p["q"].count(f"</{tag}>"): bad.append((t["id"], f"unbalanced <{tag}>", q))
            continue
        if not (4 <= len(o) <= 5 or (p.get("multi") and 4 <= len(o) <= 2 * len(p["key"]))): bad.append((t["id"], "option count", len(o), q))      # select-several questions may have six options: the ABR asks for twice as many options as correct answers
        if len({strip(x) for x in o}) != len(o): bad.append((t["id"], "duplicate options", q))
        if p["lvl"] not in ("Easy", "Moderate", "Challenging"): bad.append((t["id"], "tier", p["lvl"], q))
        ans = strip(p["a"][0]); m = re.match(r"^([A-G])\.\s*(.*)$", ans)
        if m:
            i = "ABCDEFG".index(m.group(1)); letters[m.group(1)] += 1
            if i >= len(o) or strip(o[i]) != m.group(2): bad.append((t["id"], "answer letter does not match option", ans[:40], q))
        else:
            ls = [x.strip() for x in ans.split(",")]
            if not ls or any(x not in list("ABCDEFG") or "ABCDEFG".index(x) >= len(o) for x in ls): bad.append((t["id"], "select-all letters", ans, q))
        why = p["a"][1]
        if not strip(why): bad.append((t["id"], "empty explanation", q))
        for tag in ("sup", "sub", "b", "i"):
            if why.count(f"<{tag}>") != why.count(f"</{tag}>") or p["q"].count(f"<{tag}>") != p["q"].count(f"</{tag}>"): bad.append((t["id"], f"unbalanced <{tag}>", q))
tot = sum(letters.values()); worst = max(letters.values()) / tot
if worst > 0.40: bad.append(("all", "answer letter imbalance", dict(letters)))
print(f"{n} problems in {sum(1 for t in TOPICS if t['problems'])} topics; tiers {dict(tiers)}; single-answer letters {dict(sorted(letters.items()))} (max share {worst:.0%})")
for b in bad: print("FAIL", b)
print("problems: PASS" if not bad else f"problems: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
