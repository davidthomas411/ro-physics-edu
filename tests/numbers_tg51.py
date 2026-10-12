"""TG-51 beam calibration: every worked number and keyed answer re-derived by another route
(logarithms, exact fractions, a bisection that adjusts the output, a Taylor series, and the conversions written out in another order)."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard module
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import tg51 as G
import beamdata as bd
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def true(c, what):
    global n; n += 1
    if not c: bad.append((what, False, True))
def prob(phrase):
    hits = [p for p in T["tg51"]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed_text(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def prod_log(*xs): return math.exp(sum(math.log(x) for x in xs))           # a product taken through logarithms
def exp_series(x, terms=60):                                                # e^x from its Taylor series
    s, term = 1.0, 1.0
    for k in range(1, terms): term *= x / k; s += term
    return s
def adjusted_output(read_over_true):
    """The physicist scales the output by s until the calculated dose per MU at d_max reads 1.000. With the true dose per MU
    before the change taken as 1, s is the true dose per MU delivered afterwards. read_over_true = calculated dose / true dose."""
    return bisect(lambda s: s * read_over_true - 1.0, 0.5, 1.5)
GY_PER_NC = lambda gy_per_c: gy_per_c / 1e9

# ---- worked example: 6 MV dose at 10 cm (M = P_ion P_TP P_elec P_pol M_raw, D = M k_Q N)
M1 = prod_log(G.MRAW1, G.PION1, G.PTP1, G.PELEC1, G.PPOL1)
close(G.M1, M1, 1e-12, "corrected reading by logarithms"); close(round(G.M1, 3), 12.599, 0, "printed M = 12.599 nC")
d1_gy_100mu = M1 * G.KQ1 * GY_PER_NC(G.NDW)                                 # Gy for 100 MU, N converted to Gy/nC first
close(G.D1, d1_gy_100mu * 100 / 100, 1e-12, "dose per MU at 10 cm: Gy per 100 MU equals cGy per MU"); close(round(G.D1, 4), 0.6749, 0, "printed 0.6749 cGy/MU")
close(G.NDW_NC, 0.0540, 1e-12, "5.40 x 10^7 Gy/C is 0.0540 Gy/nC")
close(G.PDD10, 67.0, 0, "the illustrative 6 MV PDD(10 cm, 10 x 10) is 67.0%"); close(G.TMR10, 0.782, 0, "and its TMR(10 cm, 10 x 10) is 0.782")
close(bd.pdd_model(10, 10), 67.0, 1e-4, "the beam model gives 67.0% at 10 cm")

# ---- worked example: dose per MU at d_max and the percent difference, in exact fractions
dmax_exact = Fr(6749, 10000) / Fr(670, 1000)
close(G.DMAX1, float(dmax_exact), 1e-12, "dose per MU at d_max as an exact fraction"); close(round(G.DMAX1, 3), 1.007, 0, "printed 1.007 cGy/MU")
close(bisect(lambda x: x * 0.670 - 0.6749, 0.5, 1.5), G.DMAX1, 1e-12, "d_max dose by bisection: x times the PDD gives the 10 cm dose")
close(G.PD1, float(100 * (dmax_exact - 1)), 1e-9, "percent difference"); close(round(G.PD1, 2), 0.73, 0, "printed +0.73%")

# ---- worked example: electron beam quality and reference depth
close(G.I50E, 6.65 - 0.5 * 0.30, 1e-12, "I50 after the 0.5 r_cav shift")
lin = lambda x: 1.998 + (x - 2) * (10.23 - 1.998) / (10 - 2)                 # the line through its end points I50 = 2 cm and 10 cm
close(G.R50E, lin(G.I50E), 1e-12, "R50 from the line through the end points of its range"); close(round(G.R50E, 2), 6.63, 0, "printed R50 = 6.63 cm")
close(G.DREFE, 0.6174 * G.I50E - 0.136, 1e-12, "d_ref = 0.6174 I50 - 0.136, the two TG-51 relations composed"); close(round(G.DREFE, 2), 3.88, 0, "printed d_ref = 3.88 cm")
close(0.6 * round(G.R50E, 2) - 0.1, 3.878, 1e-12, "the step as printed, 0.6 x 6.63 - 0.1, also rounds to 3.88")
true(G.R50E <= 8.5, "R50 is below 8.5 cm, so the 10 x 10 cm field is enough")

# ---- worked example: electron dose at d_ref
kr_series = 0.9905 + 0.0710 * exp_series(-G.R50E / 3.67)
close(G.KRE, round(kr_series, 3), 0, "k'_R50 from the Taylor series of the exponential rounds to 1.002"); close(G.KRE, 1.002, 0, "printed 1.002")
close(G.KQE, prod_log(G.PGRE, G.KRE, G.KECAL), 1e-12, "k_Q = P_gr k'_R50 k_ecal"); close(round(G.KQE, 4), 0.9003, 0, "printed 0.9003")
close(G.DE, prod_log(G.ME, G.KQE, GY_PER_NC(G.NDW)), 1e-12, "electron dose per MU at d_ref"); close(round(G.DE, 4), 0.9772, 0, "printed 0.9772 cGy/MU")

# ---- %dd(10)_x from a lead-foil reading (typed)
p = prob("%dd(10)Pb = 79.0%")
close(value(p), 0.00150 * 79.0 ** 2 + 0.8905 * 79.0, 1e-12, "%dd(10)_x as the expanded quadratic"); close(round(value(p), 2), 79.71, 0, "79.71%")
close(G.ddx_from_pb(73.0, 50), 73.0, 1e-12, "the 50 cm equation is continuous at its 73% threshold")
close(G.ddx_from_pb(71.0, 30), 71.0, 2e-3, "the 30 cm equation meets its 71% threshold within 0.1%")
true(abs(79.0 / value(p) - 1) > p["tol"], "the unconverted foil value lies outside the tolerance")

# ---- 10 MV dose at 10 cm
p = prob("A 10 MV beam is calibrated")
close(value(p), prod_log(13.85, 0.984, GY_PER_NC(5.36e7)), 1e-12, "10 MV dose per MU at 10 cm"); close(round(value(p), 4), 0.7305, 0, "0.7305 cGy/MU")
close(G.d_n1_nokq, 13.85 * 0.0536, 1e-12, "trap: k_Q left out"); close(G.d_n1_divkq, 13.85 * 0.0536 / 0.984, 1e-12, "trap: divided by k_Q"); close(G.d_n1_xpdd, value(p) * 0.735, 1e-12, "trap: multiplied by %dd(10)_x")
true(sorted(p["vals"]).index(value(p)) == 1, "the keyed 10 MV dose is not at an end of the option list")

# ---- chamber shifted 0.6 r_cav deeper for the photon reference reading
p = prob("places the center of its cavity")
ratio = 66.4 / 67.0                                                         # from the PDD values printed in the stem
s = adjusted_output(ratio)
close(G.over_shift, 100 * (s - 1), 1e-9, "output error after adjusting to the low reading, by bisection"); true(f"about {100 * (s - 1):.1f}%" in keyed_text(p) and keyed_text(p).startswith("Higher"), "the keyed option says higher by about 0.9%")
close(round(bd.pdd_model(10.18, 10), 1), 66.4, 0, "printed PDD(10.18 cm) = 66.4%")
slope = (bd.pdd_model(10.2, 10) - bd.pdd_model(9.8, 10)) / 0.4                # central difference, % per cm
close(100 * (-slope * 0.18 / 67.0), 100 * (s - 1), 0.12, "the unrounded beam model gives about the same error (within 0.12 percentage points)")
close(G.grad_mm, 100 * (1 - ratio) / 1.8, 1e-12, "fall per mm quoted in the explanation"); close(round(G.grad_mm, 2), 0.50, 0, "0.50% per mm")

# ---- d_ref from I50 (typed)
p = prob("I50 on the shifted curve = 4.75 cm")
close(value(p), 0.6174 * 4.75 - 0.136, 1e-12, "d_ref composed in one step"); close(round(value(p), 2), 2.80, 0, "2.80 cm")
true(abs((0.6 * 4.75 - 0.1) / value(p) - 1) > p["tol"], "using I50 for R50 lies outside the tolerance")

# ---- electron dose with P_gr, k'_R50, k_ecal
p = prob("R50 = 5.40 cm")
close(G.KR_N5, round(0.9905 + 0.0710 * exp_series(-5.40 / 3.67), 3), 0, "k'_R50 at 5.40 cm from the series"); close(G.KR_N5, 1.007, 0, "1.007")
close(value(p), prod_log(20.25, 0.996, 1.007, 0.903, GY_PER_NC(5.40e7)), 1e-12, "electron dose per MU at d_ref"); close(round(value(p), 4), 0.9904, 0, "0.9904 cGy/MU")
close(G.d_n5_nopgr, value(p) / 0.996, 1e-12, "trap: P_gr left out"); close(G.d_n5_nokr, value(p) / 1.007, 1e-12, "trap: k'_R50 left out"); close(G.d_n5_noke, value(p) / 0.903, 1e-12, "trap: k_ecal left out")
true(2 <= 5.40 <= 9, "R50 lies in the range of the k'_R50 expression"); true(sorted(p["vals"]).index(value(p)) == 1, "the keyed electron dose is not at an end of the option list")
close(round(100 * (G.d_n5_noke / value(p) - 1)), 11, 0, "leaving out k_ecal is about 11% high")

# ---- 6 MV transfer to d_max
p = prob("0.6655 cGy/MU")
close(value(p), bisect(lambda x: x * 0.670 - 0.6655, 0.5, 1.5), 1e-12, "d_max dose by bisection"); close(round(value(p), 3), 0.993, 0, "0.993 cGy/MU")
close(G.dmax_n2_tmr, 0.6655 / 0.782, 1e-12, "trap: SAD factor"); close(G.dmax_n2_mult, 0.6655 * 0.670, 1e-12, "trap: multiplied"); close(G.dmax_n2_isq, value(p) * 1.015 ** 2, 1e-12, "trap: the isocentric factor (101.5/100)^2")

# ---- SAD convention: dividing by the PDD instead of the TMR
close(G.sad_over, 100 * (float(Fr(782, 1000) / Fr(670, 1000)) - 1), 1e-9, "overstatement from using the PDD in an SAD setup"); close(round(G.sad_over), 17, 0, "about 17%")

# ---- 18 MV transfer: clinical %dd(10) against %dd(10)_x
close(G.DDX_N3, round(1.267 * 78.8 - 20.0, 1), 0, "%dd(10)_x of the 18 MV beam from the open-beam relation"); close(G.DDX_N3, 79.8, 0, "79.8%")
close(G.low_n3, 100 * (1 - 78.8 / 79.8), 1e-9, "using %dd(10)_x is low by the ratio of the two depth doses"); close(round(G.low_n3, 1), 1.3, 0, "1.3% low")
close(adjusted_output(78.8 / 79.8), 79.8 / 78.8, 1e-9, "an output raised to match that low value overdoses by about as much")

# ---- polarity correction left out, then the output adjusted
p = prob("left out of M")
close(adjusted_output(1 / 1.004), 1.004, 1e-9, "the output settles at P_pol times the intended dose"); true(keyed_text(p).startswith("1.004 cGy/MU, 0.4% more"), "keyed option 1.004 cGy/MU, 0.4% more")
close(G.low_p5, 1 / 1.004, 1e-12, "trap value 0.996"); close(G.dbl_p5, 1.004 ** 2, 1e-12, "trap value 1.008")


# ---- no keyed value falls on the scale slips that the numeric-option engine may add
for q in T["tg51"]["problems"]:
    if q.get("vals"): true(len(set(round(v, 6) for v in q["vals"])) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_tg51: {n} numbers re-derived"); print("numbers_tg51: PASS" if not bad else f"numbers_tg51: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
