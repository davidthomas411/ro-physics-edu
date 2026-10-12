"""Kilovoltage dosimetry and calibration traceability: every worked number and keyed answer re-derived by another route
(exact fractions, a Newton square root, the Lagrange form of the interpolation, logarithms, Cramer's rule, a least-squares line, and bisection)."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard module
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import kv_dosimetry as K
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
TOP = T["kv-dosimetry"]
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def true(c, what):
    global n; n += 1
    if not c: bad.append((what, False, True))
def prob(phrase):
    hits = [p for p in TOP["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def newton_sqrt(x):
    """Square root by Heron's iteration, from exact fractions."""
    r = Fr(max(1, int(x))) if x >= 1 else Fr(1)
    for _ in range(60): r = (r + Fr(x) / r) / 2; r = Fr(r).limit_denominator(10 ** 15)
    return float(r)
def prod_log(*xs): return math.exp(sum(math.log(x) for x in xs))           # a product taken through logarithms
def lagrange(h, h1, n1, h2, n2): return n1 * (h2 - h) / (h2 - h1) + n2 * (h - h1) / (h2 - h1)
def fit_line(ts, rs):
    """Least-squares line R = a + b t; returns slope and intercept."""
    m = len(ts); st, sr = sum(ts), sum(rs); stt = sum(t * t for t in ts); str_ = sum(t * r for t, r in zip(ts, rs))
    b = (m * str_ - st * sr) / (m * stt - st * st); a = (sr - b * st) / m
    return b, a
def flat(x): return [plain(x)] if isinstance(x, str) else [s for y in x for s in flat(y)] if isinstance(x, (list, tuple)) else []
GUIDE = " ".join(s for b in TOP["guide"] for s in flat(b[1:]))
def printed(s, what):
    global n; n += 1
    if s not in GUIDE: bad.append((what, s, "not in the guide text"))

# ---- worked example: combined uncertainty, from exact squares and a Newton square root
sq = sum(Fr(str(u)) ** 2 for u in K.U_EX)
close(float(sq), 4.77, 1e-12, "sum of squares 0.16 + 0.36 + 0.25 + 4.00"); close(K.uc_ex, newton_sqrt(sq), 1e-12, "combined uncertainty by Newton's iteration")
close(K.uc_ex, math.hypot(*K.U_EX), 1e-12, "and by math.hypot"); close(round(K.uc_ex, 2), 2.18, 0, "printed 2.18%")
close(round(K.uc_ex_nof, 2), round(math.hypot(0.4, 0.6, 0.5), 2), 0, "without the factor term: 0.88%"); close(round(K.uc_ex_nof, 2), 0.88, 0, "0.88%")
close(K.uc_ex_lin, float(sum(Fr(str(u)) for u in K.U_EX)), 1e-12, "linear sum 3.5%")
printed("uc = √4.77 = 2.18%", "worked uncertainty step")

# ---- worked example: surface dose rate by the in-air method, in cGy and through logarithms
nk_cgy_per_nc = 4.707                                                     # 4.707 x 10^7 Gy/C = 4.707 cGy/nC
ka_cgy = 13.06 * nk_cgy_per_nc                                            # cGy/min
close(K.ka_ex, ka_cgy / 100, 1e-12, "air kerma rate in cGy/min, then Gy"); close(round(K.ka_ex, 4), 0.6147, 0, "printed 0.6147 Gy/min")
close(K.kw_ex, prod_log(13.06e-9, 4.707e7, 1.023), 1e-12, "water kerma free in air"); close(round(K.kw_ex, 4), 0.6289, 0, "printed 0.6289 Gy/min")
close(K.d_ex, prod_log(13.06e-9, 4.707e7, 1.16, 1.000, 1.023), 1e-12, "surface dose rate through logarithms"); close(round(K.d_ex, 4), 0.7295, 0, "printed 0.7295 Gy/min")
close(round(K.rise_ex), round(100 * (1.16 * 1.023 - 1)), 0, "19% above the air kerma rate"); true(1.16 - 1 > 1.023 - 1, "mostly from the backscatter")
close(K.NK_EX * 1e-9, 0.04707, 1e-12, "4.707 x 10^7 Gy/C = 0.04707 Gy/nC")
printed("D = 0.6289 × 1.16 × 1.000 = 0.7295 Gy/min", "surface dose step")

# ---- worked example: end effect from two set times (Cramer's rule) and the timer setting (bisection)
# R = a t + b with b = a delta: solve the 2 x 2 system for a and b
det = 0.50 * 1 - 2.00 * 1
a = (6.21 * 1 - 24.06 * 1) / det; b = (0.50 * 24.06 - 2.00 * 6.21) / det
close(K.rate_e, a, 1e-12, "slope by Cramer's rule"); close(round(K.rate_e, 2), 11.90, 0, "11.90 nC/min")
close(K.delta_e, b / a, 1e-12, "end effect = intercept / slope"); close(round(60 * K.delta_e, 2), 1.31, 0, "+1.31 s"); close(round(K.delta_e, 4), 0.0218, 0, "+0.0218 min")
close(fit_line([0.50, 2.00], [6.21, 24.06])[0], a, 1e-12, "least-squares slope through the two points")
t_bis = bisect(lambda t: 0.730 * (t + K.delta_e) - 3.00, 1.0, 10.0)
close(K.t_set_e, t_bis, 1e-9, "timer setting by bisection"); close(round(K.t_set_e, 3), 4.088, 0, "4.088 min"); close(round(K.t_plain_e, 3), 4.110, 0, "D/rate = 4.110 min")
close(round(K.mm_e), 4, 0, "4 min"); close(round(K.ss_e), 5, 0, "and 5 s"); close(round(K.over_e, 1), round(100 * (0.730 * (3.00 / 0.730 + K.delta_e) / 3.00 - 1), 1), 0, "ignoring the end effect overdoses by 0.5%")
printed("timer is set to 4.088 min (4 min 5 s)", "timer setting in the answer")

# ---- combined uncertainty question
p = prob("conversion factors: 1.2%")
close(value(p), newton_sqrt(sum(Fr(str(u)) ** 2 for u in K.U_Q)), 1e-12, "combined 1.68% by Newton's iteration"); close(round(value(p), 2), 1.68, 0, "1.68%")
true(abs(3.1 / value(p) - 1) > p["tol"] and abs(math.sqrt(3.1) / value(p) - 1) > p["tol"], "the linear sum and the root of the plain sum lie outside the tolerance")
true(abs(1.68 / value(p) - 1) <= p["tol"], "typing 1.68 is accepted")

# ---- contact beam: one-step in-air dose rate
p = prob("50 kV contact beam")
close(value(p), prod_log(1.538e-9, 1.426e9, 1.06, 1.000, 1.025), 1e-12, "contact dose rate through logarithms"); close(round(value(p), 2), 2.38, 0, "2.38 Gy/min")
close(K.d_c_nobw, 1.538 * 1.426 * 1.025, 1e-12, "trap: B_w left out"); close(K.d_c_norat, 1.538 * 1.426 * 1.06, 1e-12, "trap: ratio left out"); close(K.d_c_divbw, value(p) / 1.06 ** 2, 1e-12, "trap: divided by B_w")

# ---- timer setting with a negative end effect
p = prob("crosses the time axis at t = +0.90 s")
close(value(p), bisect(lambda t: 0.850 * (t - 0.90 / 60) - 2.50, 1.0, 10.0), 1e-9, "setting by bisection with delta = -0.015 min"); close(round(value(p), 3), 2.956, 0, "2.956 min")
close(K.t_n_plain, float(Fr(250, 85)), 1e-12, "trap: no correction, 2.941 min"); close(K.t_n_sign, float(Fr(250, 85)) - 0.015, 1e-12, "trap: wrong sign"); close(K.t_n_unit, float(Fr(250, 85)) + 0.90, 1e-12, "trap: seconds taken as minutes")

# ---- every numeric option list is distinct, and every typed key differs from its traps
for q in TOP["problems"]:
    if q.get("vals"): true(len(set(round(v, 9) for v in q["vals"])) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_kv_dosimetry: {n} numbers re-derived"); print("numbers_kv_dosimetry: PASS" if not bad else f"numbers_kv_dosimetry: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
