"""Typed-answer questions: each answer is re-derived here by a different route, and the tolerance must accept rounding but reject the documented wrong approaches."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
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
NA, CI = 6.02214076e23, 3.7e10
S = (math.log(2) / (100 * 86400)) * (NA / 100) / CI                                   # lambda x atoms per gram, in Ci/g
check("specific-activity", "hypothetical nuclide", S, accept=(S * 1.01, S * 0.99), reject=(S / math.log(2), S * math.log(2), S * 24, S * CI))
check("decay-law", "Co-60 source", 100 * 0.5 ** (10 / 5.27), accept=(26.5, 27.1), reject=(100 * math.exp(-10 / 5.27), 100 * 0.5 ** (10 / 5.27) * 1.03))
check("decay-law", "loses 2.0% of its activity each day", math.log(2) / -math.log(0.98), accept=(34.2, 34.4), reject=(0.693 / 0.02, 34.0, 35.0))
def peak(tp, td):                                                                      # golden-section search for the maximum of exp(-lp t) - exp(-ld t)
    lp, ld = math.log(2) / tp, math.log(2) / td; f = lambda t: math.exp(-lp * t) - math.exp(-ld * t); a, b = 0.0, 200.0; g = (math.sqrt(5) - 1) / 2
    for _ in range(200):
        c, d = b - g * (b - a), a + g * (b - a)
        if f(c) > f(d): b = d
        else: a = c
    return (a + b) / 2
check("equilibrium", "generator immediately after elution", peak(65.94, 6.0067), accept=(22.8, 23.0), reject=(65.94, 6.0067, 20.0, 25.0))
# lead at 1.5 MeV: NIST mu/rho = 0.05222 cm2/g (Z = 82), density 11.35 g/cm3
pb = 100 * math.exp(-0.05222 * 11.35 * 5.0)
check("photon-interactions", "lead shield", pb, accept=(pb * 1.01, pb * 0.99), reject=(100 * math.exp(-0.05222 * 5.0), pb * 1.1, pb * 0.9))
hc, lc = 1.239842e-12, 2.426310e-12                                                    # MeV m, Compton wavelength: recoil energy from the wavelength shift
lam = hc / 2.0; Ep = hc / (lam + lc * (1 - math.cos(math.radians(60)))); T = 2.0 - Ep
check("photon-interactions", "recoil electron", T, accept=(1.31, 1.33), reject=(Ep, 0.9, 1.5))
check("kerma-dose", "exposure in", 120 * 2.58e-4, accept=(0.031, 3.1e-2), reject=(120 * 0.876, 120 / 2.58e-4, 0.0258))
check("scatter", "12 × 30 cm", 4 * 12 * 30 / (2 * (12 + 30)), accept=(17.1, 17.2), reject=(math.sqrt(12 * 30), 21.0, 17.6))
check("mu-calc", "prescription = 300 cGy", 300 / (1.017 * 1.014 * 0.680), accept=(428, 427, 430), reject=(300 / (1.017 * 1.014 * 0.680) * 1.030, 300 / (1.017 * 1.014 * 0.680) / 1.030, 300 / (1.017 * 0.680)))
check("mu-calc", "dose = 120 cGy at 12 cm", 120 / (1.021 * 1.013 * 0.738 * 1.015 ** 2), accept=(152.6, 153), reject=(120 / (1.021 * 1.013 * 0.738), 120 / (1.021 * 1.013 * 0.738 / 1.015 ** 2), 150.0))
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
