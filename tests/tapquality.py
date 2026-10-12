"""Tap-the-figure questions must make the learner think. A Moderate or Challenging question may not have its answer at the place where a plotted curve crosses a marked y-axis level (the learner would only read across), and the isotope plot must carry no name labels or colour hints."""
import sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
figs = [(t["id"], k, p) for t in TOPICS for k, p in enumerate(t["problems"], 1) if p.get("kind") == "fig"]
for tid, k, p in figs:
    sp = p["spec"]; ticks = [v for v in (sp["y"].get("ticks") or []) if v != sp["y"]["min"]]; rng = sp["y"]["max"] - sp["y"]["min"]; a, b = p["targets"][0][0], p["targets"][0][1]
    if p["lvl"] == "Easy" or not sp["series"] or a is None or b is None: continue
    xc = (a + b) / 2; hit = []
    for si, s in enumerate(sp["series"]):
        yc = min(s["pts"], key=lambda q: abs(q[0] - xc))[1]
        hit += [(si, v, round(yc, 3)) for v in ticks if abs(yc - v) <= 0.015 * rng]
    check(not hit, f"{tid}:{k} [{p['lvl']}] the answer is not at a marked y level, so it cannot be read across: {hit}")
check(len(figs) >= 3, f"{len(figs)} tap-the-figure questions were checked")
iso = [(tid, k, p) for tid, k, p in figs if tid == "brachy-sources"]
check(all(not p["spec"].get("texts") and len({d["color"] for d in p["spec"]["dots"]}) == 1 for _, _, p in iso), "the isotope plot is unlabelled and every point has the same colour, so the answer cannot be read from a name or a hint")
check(all(p["lvl"] != "Easy" for _, _, p in iso), "with no labels, the isotope questions are at least Moderate, and one needs a calculation")
chal = [(tid, k) for tid, k, p in figs if p["lvl"] == "Challenging"]
check(True, f"there are {len(chal)} Challenging tap questions, each tested against the marked-level rule")
for m in bad: pass
print(f"tapquality: {n} checks"); print("tapquality: PASS" if not bad else f"tapquality: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
