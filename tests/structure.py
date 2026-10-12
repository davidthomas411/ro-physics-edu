"""Question and text structure: one question line per question, the quantity to find marked, no raw markers, every key term placed."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import blocks, figs
from topics import TOPICS
FIGS = figs.build()
bad = []
def one(where, html):
    h = blocks._mark(blocks.autostem(html))
    if h.count('class="ask"') != 1: bad.append((where, "question lines", h.count('class="ask"')))
    if "<v>" in h or "<f>" in h or "<t>" in h or "</v>" in h or "</f>" in h: bad.append((where, "unconverted marker", h[:80]))
    return h
n_prn = n_ex = 0
for t in TOPICS:
    for i, p in enumerate(t["problems"], 1):
        h = one(f"{t['id']} problem {i}", p["q"])
        if p.get("vals") is not None:
            n_prn += 1
            if 'class="f"' not in h: bad.append((f"{t['id']} problem {i}", "numeric question without a marked quantity to find", re.sub(r"<[^>]+>", "", h)[:70]))
    for b in t["guide"]:
        if b[0] == "ex":
            n_ex += 1; h = one(f"{t['id']} example '{b[1]}'", b[2])
            if 'class="f"' not in h: bad.append((f"{t['id']} example '{b[1]}'", "worked example without a marked quantity to find", ""))
    if t.get("terms"):
        html = blocks.render(t["guide"], FIGS, tid=t["id"], terms=t["terms"])
        got = re.findall(r'<span class="t">(.*?)</span>', html, re.S)
        miss = [x for x in t["terms"] if x.lower() not in {g.lower() for g in got}]
        if miss: bad.append((t["id"], "key terms not found in the text", miss))
        if len(got) != len(set(g.lower() for g in got)): bad.append((t["id"], "a key term wrapped twice", got))
print(f"structure: {n_prn} numeric questions and {n_ex} worked examples checked")
for b in bad: print("FAIL", b)
print("structure: PASS" if not bad else f"structure: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
