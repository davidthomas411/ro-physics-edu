"""Typed-answer questions: each answer is re-derived here by a different route, and the tolerance must accept rounding but reject the documented wrong approaches."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s)
ALL = [(t["id"], p) for t in TOPICS for p in t["problems"] if p.get("kind") == "num"]
bad, n = [], 0
def find(tid, phrase):
    hits = [p for i, p in ALL if i == tid and phrase in plain(p["q"])]; assert len(hits) == 1, (tid, phrase, len(hits)); return hits[0]
def ok(p, x): return abs(x - p["ans"]) <= p["tol"] * abs(p["ans"]) + 1e-12
def check(tid, phrase, expect, accept=(), reject=()):
    global n; p = find(tid, phrase); n += 1
    if abs(p["ans"] - expect) > 1e-6 * abs(expect): bad.append((tid, phrase, "answer", p["ans"], "expected", expect))
    for x in (expect,) + tuple(accept):
        if not ok(p, x): bad.append((tid, phrase, "should accept", x, f"(answer {p['ans']:.5g}, tol {p['tol']})"))
    for x in reject:
        if ok(p, x): bad.append((tid, phrase, "should reject", x, f"(answer {p['ans']:.5g}, tol {p['tol']})"))
# ---- independent derivations
check("decay-law", "Co-60 source", 100 * 0.5 ** (10 / 5.27), accept=(26.5, 27.1), reject=(100 * math.exp(-10 / 5.27), 100 * 0.5 ** (10 / 5.27) * 1.03))
check("mu-calc", "wedge and a blocking tray", 180 / (0.66 * 0.97), accept=(281, 282), reject=(180 / 0.66, 180 / 0.97, 180 * 0.66 * 0.97))
# every typed question: one ask, a marked quantity to find, a sensible tolerance and a unit
DIMENSIONLESS = ("net optical density", "γ at the measured point")                 # answers that have no unit
for tid, p in ALL:
    q = p["q"]
    if q.count('class="ask"') != 1 or "<f>" not in q: bad.append((tid, "stem needs one ask with a marked quantity", plain(q)[:60]))
    if not 0.002 <= p["tol"] <= 0.03: bad.append((tid, "tolerance", p["tol"]))
    if not (p["unit"].strip() or any(d in plain(q) for d in DIMENSIONLESS)) or not math.isfinite(p["ans"]) or p["ans"] <= 0: bad.append((tid, "unit or answer", p["unit"], p["ans"]))
print(f"numbers6: {n} typed answers re-derived, accepted and rejected values checked; {len(ALL)} typed questions"); [print("FAIL", b) for b in bad]
print("numbers6: PASS" if not bad else f"numbers6: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
