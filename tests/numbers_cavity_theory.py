"""Cavity theory and stopping-power ratios: every printed number and keyed answer re-derived by another route
(exact fractions, the exposure route to the dose to air, logarithms, a Monte Carlo of isotropic chords, bisection on a range table,
electron densities for the large-cavity ratio, the d_ref closed form for the electron-beam ratios, and a second stopping-power integration)."""
import sys, re, math, random
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard module
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import cavity_theory as C
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def true(c, what):
    global n; n += 1
    if not c: bad.append((what, False, True))
def prob(phrase):
    hits = [p for p in T["cavity-theory"]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed_text(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def prod_log(*xs): return math.exp(sum(math.log(x) for x in xs))
GUIDE = " ".join(plain(b[2]) + " " + " ".join(plain(s) for s in b[3]) + " " + plain(b[4]) if b[0] == "ex" else plain(b[1]) if b[0] in ("p", "h2") else " ".join(plain(x) for x in b[1]) if b[0] in ("ul", "eq") else "" for b in T["cavity-theory"]["guide"])
W = Fr(3397, 100)                                                                      # J/C

# ---- air density at 22 °C and 101.33 kPa: from the 20 °C, 101.3 kPa value used on the site, and from the ideal gas law
rho_from20 = 1.205 * (273.15 + 20) / (273.15 + 22) * 101.33 / 101.3
close(round(rho_from20, 3), C.RHO22, 0, "1.205 mg/cm³ at 20 °C and 101.3 kPa scales to the printed 1.197 mg/cm³")
rho_ideal = 101330 * 0.0289647 / (8.314462618 * 295.15)                               # kg/m³ = mg/cm³
close(rho_ideal, C.RHO22, 1e-3, "the ideal gas law gives the same density within 0.1%")

# ---- worked example: dose to water from a cavity reading (Co-60)
m1 = Fr(6000, 10000) * Fr(1197, 1000)                                                  # mg
x1_R = (Fr(2000, 100) * Fr(1, 10 ** 9)) / (m1 * Fr(1, 10 ** 6)) / Fr(258, 10 ** 6)     # the charge per mass expressed in roentgens
da1 = x1_R * Fr(258, 10 ** 6) * W                                                      # roentgens times the dose to air per roentgen
close(C.DA1, float(da1), 1e-12, "dose to air by the exposure route"); close(round(C.DA1, 3), 0.946, 0, "printed 0.946 Gy")
close(C.DW1, float(da1 * Fr(1133, 1000)), 1e-12, "dose to water"); close(round(C.DW1, 3), 1.072, 0, "printed 1.072 Gy")
close(round(C.M1, 4), 0.7182, 0, "printed 0.7182 mg"); true("13% more" in GUIDE, "the dose to water is 13% above the dose to air (s - 1 = 0.133)")

# ---- the stopping-power and range machinery: a second implementation (in terms of gamma and beta, trapezoid in linear energy) checked against ESTAR
ME = 0.51099895
def scol2(T_, za, I_ev):
    g = 1 + T_ / ME; b2 = (g * g - 1) / (g * g); tau = g - 1; I = I_ev * 1e-6 / ME
    F = 1 - b2 + (tau * tau / 8 - (2 * tau + 1) * math.log(2)) / (g * g)
    return 0.1535375 * za / b2 * (2 * math.log(tau * math.sqrt(tau + 2) / (math.sqrt(2) * I)) + F)
def range2(T_, za, I_ev, t0=0.0005, n_=60000):
    h = (T_ - t0) / n_
    s = sum(1 / scol2(t0 + k * h, za, I_ev) * (0.5 if k in (0, n_) else 1) for k in range(n_ + 1)) * h
    return s + t0 / scol2(t0, za, I_ev) / 1.75                                          # below t0, S falls about as T^-0.75
for T_, s_ref in ((0.010, 22.56), (0.020, 13.17), (0.100, 4.115)):
    close(scol2(T_, 0.55509, 75.0), s_ref, 2e-3, f"water collision stopping power at {T_ * 1000:.0f} keV matches ESTAR")
close(scol2(0.010, 0.49919, 85.7), 19.75, 2e-3, "air collision stopping power at 10 keV matches ESTAR")
for T_, r_ref in ((0.010, 2.515e-4), (0.020, 8.575e-4), (0.100, 1.431e-2)):
    close(range2(T_, 0.55509, 75.0), r_ref, 1e-2, f"water CSDA range at {T_ * 1000:.0f} keV matches ESTAR within 1%")
for e, printed in ((10, 2.9e-4), (15, 5.9e-4), (20, 9.8e-4)):
    r = range2(e / 1000, 0.49919, 85.7)
    close(float(f"{r:.2g}"), printed, 0, f"CSDA range in air at {e} keV rounds to the printed {printed}"); close(C.RANGE_AIR[e], printed, 0, f"module table at {e} keV")
    true(abs(r / printed - 1) < 0.02, f"the {e} keV air range lies within 2% of its two-figure value")

# ---- worked example: mean chord length and the Spencer–Attix cutoff of a Farmer-type cavity
def mc_chord(r, l, n_=200000, seed=7):
    """Mean chord of a cylinder over isotropic uniform random lines: random direction, random point on the projected plane of a bounding sphere."""
    rng = random.Random(seed); R = math.sqrt(r * r + (l / 2) ** 2); tot = hits = 0
    for _ in range(n_):
        u = 2 * rng.random() - 1; ph = 2 * math.pi * rng.random(); s = math.sqrt(1 - u * u)
        d = (s * math.cos(ph), s * math.sin(ph), u)
        a = (-d[1], d[0], 0.0) if abs(d[2]) < 0.9 else (0.0, -d[2], d[1]); na = math.sqrt(sum(x * x for x in a)); a = tuple(x / na for x in a)
        b = (d[1] * a[2] - d[2] * a[1], d[2] * a[0] - d[0] * a[2], d[0] * a[1] - d[1] * a[0])
        while True:
            p, q = (2 * rng.random() - 1) * R, (2 * rng.random() - 1) * R
            if p * p + q * q <= R * R: break
        o = tuple(p * a[k] + q * b[k] for k in range(3))
        lo, hi = -math.inf, math.inf                                                     # line o + t d against the cylinder x² + y² ≤ r², |z| ≤ l/2
        A = d[0] ** 2 + d[1] ** 2; B = 2 * (o[0] * d[0] + o[1] * d[1]); Cc = o[0] ** 2 + o[1] ** 2 - r * r
        if A < 1e-15:
            if Cc > 0: continue
        else:
            disc = B * B - 4 * A * Cc
            if disc <= 0: continue
            t1, t2 = (-B - math.sqrt(disc)) / (2 * A), (-B + math.sqrt(disc)) / (2 * A); lo, hi = max(lo, t1), min(hi, t2)
        if abs(d[2]) < 1e-15:
            if abs(o[2]) > l / 2: continue
        else:
            t1, t2 = sorted(((-l / 2 - o[2]) / d[2], (l / 2 - o[2]) / d[2])); lo, hi = max(lo, t1), min(hi, t2)
        if hi > lo: tot += hi - lo; hits += 1
    return tot / hits
ch2 = Fr(2) * Fr(31, 10) * Fr(23) / (Fr(31, 10) + Fr(23))
close(C.CH2, float(ch2), 1e-12, "Farmer chord 2rL/(r+L) as an exact fraction"); close(round(C.CH2, 2), 5.46, 0, "printed 5.46 mm")
close(mc_chord(3.1, 23.0), C.CH2, 1e-2, "Monte Carlo of isotropic chords gives the same mean chord within 1%")
t2 = float(ch2) / 10 * 1.197e-3
close(C.T2, t2, 1e-12, "mass thickness of the chord"); close(float(f"{C.T2:.3g}"), 6.54e-4, 0, "printed 6.54 × 10^-4 g/cm²")
tab = [(10, 2.9e-4), (15, 5.9e-4), (20, 9.8e-4)]
def range_lin(e):
    for (e0, r0), (e1, r1) in zip(tab, tab[1:]):
        if e0 <= e <= e1: return r0 + (r1 - r0) * (e - e0) / (e1 - e0)
delta = bisect(lambda e: range_lin(e) - t2, 10, 20)
close(C.DELTA2, delta, 1e-9, "cutoff by bisection on the printed range table"); close(round(C.DELTA2), 16, 0, "about 16 keV"); close(round(C.DELTA2, 1), 15.8, 0, "printed 15.8 keV")
d_phys = bisect(lambda e: range2(e / 1000, 0.49919, 85.7, n_=6000) - t2, 10, 20)
true(abs(d_phys - C.DELTA2) < 1.0, f"the energy whose computed air range equals the chord ({d_phys:.1f} keV) agrees within 1 keV")

# ---- typed: mean chord of a small cavity
p = prob("described by its mean chord length")
close(value(p), float(Fr(2) * Fr(25, 10) * 7 / (Fr(25, 10) + 7)), 1e-12, "mean chord 2rL/(r+L)"); close(round(value(p), 2), 3.68, 0, "3.68 mm")
close(mc_chord(2.5, 7.0, seed=11), value(p), 1e-2, "Monte Carlo agrees within 1%")
true(abs(5.0 / value(p) - 1) > p["tol"], "2r, leaving out the end faces, lies outside the tolerance")

# ---- worked example: the two limits for an air cavity in Co-60
za_w = 2 * 1.008 / 18.015 * (1 / 1.008) + 15.999 / 18.015 * (8 / 15.999)             # electrons per gram per mole of water: (2 + 8) / 18.015
za_air = 0.000124 * 6 / 12.011 + 0.755268 * 7 / 14.007 + 0.231781 * 8 / 15.999 + 0.012827 * 18 / 39.948
close(za_w / za_air, 0.02965 / 0.02666, 1e-3, "in the Compton region the energy-absorption ratio is the ratio of electrons per gram")
close(C.LARGE3, round(za_w / za_air, 3), 0, "large-cavity ratio 1.112 from electron densities"); close(C.LARGE3, 1.112, 0, "printed 1.112")
close(C.LOW3, float(100 * (1 - Fr(1112, 1000) / Fr(1133, 1000))), 1e-12, "gap below the Spencer–Attix ratio"); close(round(C.LOW3, 1), 1.9, 0, "printed 1.9%")

# ---- the electron-beam ratios: the fit against its closed form at d_ref, and the printed values
for r50 in (2.5, 3.0, 4.0, 5.0, 6.0, 7.5, 8.0, 9.0):                                    # the beams used here have R50 from 3 to 8 cm
    close(C.sw_air_e(0.6 * r50 - 0.1, r50), 1.253 - 0.1487 * r50 ** 0.214, 2e-3, f"Burns fit at d_ref matches the closed form 1.253 - 0.1487 R50^0.214 (R50 = {r50} cm)")
close(round(1.253 - 0.1487 * 5.0 ** 0.214, 2), 1.04, 0, "d_ref ratio for R50 = 5 cm prints as 1.04 by the closed form too")
close(round(C.S_SURF, 2), 0.99, 0, "surface ratio for R50 = 5 cm, 0.99"); close(round(C.S_R50, 2), 1.10, 0, "ratio at R50, 1.10")
zs = [0.1 + 0.1 * k for k in range(50)]
true(all(C.sw_air_e(a, 5.0) < C.sw_air_e(b, 5.0) for a, b in zip(zs, zs[1:])), "the ratio rises steadily with depth for R50 = 5 cm")
true("0.99 near the surface to 1.04 at dref and 1.10 at R50" in GUIDE, "the text quotes 0.99, 1.04, and 1.10 for R50 = 5 cm")

# ---- worked example: dose ratio between two depths (R50 = 5.0 cm)
close(C.S4A, round(C.sw_air_e(3.0, 5.0), 3), 0, "s at 3.0 cm"); close(C.S4B, round(C.sw_air_e(4.5, 5.0), 3), 0, "s at 4.5 cm")
dr4 = Fr(600, 1000) * Fr(round(C.S4B * 1000), 1000) / Fr(round(C.S4A * 1000), 1000)
close(C.DR4, float(dr4), 1e-12, "dose ratio from the printed values, as a fraction"); close(round(C.DR4, 3), 0.621, 0, "printed 0.621")
close(round(C.UP4, 1), round(100 * float(Fr(1083, 1046) - 1), 1), 0, "3.5% above the ratio of the readings"); close(round(C.UP4, 1), 3.5, 0, "printed 3.5%")

# ---- dose to water from a cavity reading in a 6 MV beam
p = prob("16.50 nC")
m7 = Fr(6000, 10000) * Fr(1197, 1000)
da7 = Fr(1650, 100) * Fr(1, 10 ** 9) / (m7 * Fr(1, 10 ** 6)) * W
close(value(p), float(da7 * Fr(1119, 1000)), 1e-12, "keyed dose to water"); close(round(value(p), 3), 0.873, 0, "0.873 Gy")
close(C.DW7_nos, float(da7), 1e-12, "trap: dose to air"); close(C.DW7_div, float(da7 / Fr(1119, 1000)), 1e-12, "trap: divided by s"); close(C.DW7_now, float(da7 / W * Fr(1119, 1000)), 1e-12, "trap: W/e left out")

# ---- k_Q from the ratio of products
p = prob("ratio of products of the water-to-air ratio")
kq = prod_log(1.119, 0.996, 0.995, 0.993, 1.000) / prod_log(1.133, 0.991, 0.992, 0.993, 1.000)
close(value(p), kq, 1e-12, "k_Q through logarithms"); close(round(value(p), 4), 0.9956, 0, "0.9956")
close(value(p), (1.119 / 1.133) * (0.996 / 0.991) * (0.995 / 0.992), 1e-12, "k_Q as a product of ratios, P_cel and P_fl cancelling")
close(C.KQ21_s, 1.119 / 1.133, 1e-12, "trap: stopping-power ratios alone"); close(C.KQ21_inv, 1 / kq, 1e-12, "trap: inverted"); close(C.KQ21_p, (0.996 * 0.995) / (0.991 * 0.992), 1e-12, "trap: perturbation factors alone")

# ---- depth conversion for R50 = 3.0 cm
p = prob("R50 = 3.0 cm")
close(C.Z10A, 1.7, 1e-12, "d_ref = 0.6 x 3.0 - 0.1 = 1.7 cm"); close(C.S10A, 1.253 - 0.1487 * 3.0 ** 0.214, 2e-3, "s at d_ref within 0.2% of the closed form")
close(value(p), float(Fr(550, 1000) * Fr(1096, 1000) / Fr(1064, 1000)), 1e-12, "keyed relative dose as a fraction"); close(round(value(p), 3), 0.567, 0, "0.567")
close(C.DR10_inv, float(Fr(550, 1000) * Fr(1064, 1096)), 1e-12, "trap: ratio inverted"); close(C.DR10_one, 0.550 * 1.096, 1e-12, "trap: deeper ratio alone")
close(C.S10A, 1.064, 0, "printed 1.064"); close(C.S10B, 1.096, 0, "printed 1.096")

# ---- ranking of four ratios
close(round(C.S9_SURF, 2), 0.96, 0, "surface of the R50 = 8 cm beam, about 0.96"); close(round(C.S9_REF, 2), 1.02, 0, "d_ref of that beam, about 1.02")
close(round(1.253 - 0.1487 * 8.0 ** 0.214, 2), 1.02, 0, "the closed form also gives 1.02 at d_ref")
true(C.S9_SURF < C.S9_REF < 1.10 < 1.13, "the ranked order is strict")

# ---- I-125: electrons stop far inside a 0.9 mm chip
r125 = range2(0.0355, 0.55509, 75.0) * 1e4
close(r125, C.R125_UM, 5e-3, "range of a 35.5 keV electron in water by the second integration"); true(r125 < 30 and C.R125_BOUND == 30, "below the printed 30 µm")
true(30 / 900 < 0.05, "the bound is under 5% of the chip thickness")

# ---- the two limits for an air chamber in Co-60 (choose the limit)
p = prob("dose to the air of a small chamber")
close(value(p), float(Fr(950, 1000) * Fr(1133, 1000)), 1e-12, "keyed dose to water"); close(round(value(p), 3), 1.076, 0, "1.076 Gy")
close(C.DW17_large, 0.950 * 1.112, 1e-12, "trap: large-cavity ratio"); close(C.DW17_inv, 0.950 / 1.133, 1e-12, "trap: divided by s"); close(C.DW17_linv, 0.950 / 1.112, 1e-12, "trap: divided by the large-cavity ratio")
true("1.9% low" in plain(p["a"][1]), "explanation quotes 1.9%, as the worked example does")

# ---- Burlin
p = prob("Burlin's theory converts its dose")
b = Fr(40, 100) * Fr(85, 100) + Fr(60, 100) * Fr(120, 100)
close(value(p), float(Fr(2120, 1000) / b), 1e-12, "keyed dose to water as a fraction"); close(value(p), 2.0, 1e-12, "exactly 2.000 Gy")
close(C.DW18_swap, float(Fr(2120, 1000) / (Fr(60, 100) * Fr(85, 100) + Fr(40, 100) * Fr(120, 100))), 1e-12, "trap: d swapped")
close(C.DW18_large, 2.120 / 1.20, 1e-12, "trap: large-cavity limit alone"); close(C.DW18_mult, 2.120 * float(b), 1e-12, "trap: multiplied")

# ---- explanations quote the same values as the guide; no keyed value repeats an option
true(f"about {round(C.DELTA2)} keV" in plain(prob("cutoff energy Δ")["a"][1]), "the cutoff explanation quotes 16 keV")
for q in T["cavity-theory"]["problems"]:
    if q.get("vals"): true(len(set(round(v, 6) for v in q["vals"])) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b_ in bad: print("FAIL", b_)
print(f"numbers_cavity_theory: {n} numbers re-derived"); print("numbers_cavity_theory: PASS" if not bad else f"numbers_cavity_theory: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
