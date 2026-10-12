"""Stereotactic radiosurgery and SBRT: every number the chapter prints or keys, re-derived by another route
(numerical integration, bisection, rotation matrices, a breathing simulation, absolute readings, and fraction-by-fraction sums)."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import srs_sbrt as S
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
TOP = T["srs-sbrt"]
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def holds(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in TOP["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def options(p): return sorted(p["vals"])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
TEXT = " ".join(plain(b[1]) for b in TOP["guide"] if b[0] == "p") + " " + " ".join(plain(i) for b in TOP["guide"] if b[0] == "ul" for i in b[1])
EXS = {b[1]: b for b in TOP["guide"] if b[0] == "ex"}
def shown(s, what): holds(s in TEXT, f"the text prints {s!r} ({what})")

# ---- a 1 mm shift of a spherical target: slice the sphere along the shift; each slice of the two spheres is a pair of concentric discs
def outside(R, d, steps=200000):
    h = 2 * R / steps; acc = 0.0
    for i in range(steps):
        z = -R + (i + 0.5) * h                                                 # midpoint rule
        a2 = R * R - z * z; b2 = max(0.0, R * R - (z - d) ** 2)
        acc += math.pi * max(0.0, a2 - b2) * h
    return acc / (4 / 3 * math.pi * R ** 3)
close(outside(5.0, 1.0), S.out10, 1e-6, "10 mm target, 1 mm shift: fraction outside by slicing"); close(S.out10, 0.1495, 1e-9, "exactly 299/2000")
close(outside(10.0, 1.0), S.out20, 1e-6, "20 mm target, 1 mm shift"); shown("15% of a 10 mm spherical target", "rounded"); shown("7.5% of a 20 mm", "rounded")
card = next(c for c in TOP["cards"] if c["q"] == "Geometric accuracy in radiosurgery")
close(math.pi * 21 * 81 / 12, 4 / 3 * math.pi * 125 * (1 - outside(5.0, 1.0)), 1e-5, "overlap volume in the card's working, 445.3 mm3")
holds("445.3 mm³ of 523.6 mm³, so 15% lies outside" in plain(" ".join(card["w"])), "the card's working prints the overlap and the sphere volume")

# ---- the range of lateral charged-particle equilibrium: invert the line for the TPR that gives each printed range
tpr_for = lambda r: bisect(lambda t: 8.369 * t - 4.382 - r, 0.5, 0.9)
close(tpr_for(S.r66), 0.66, 1e-9, "r_LCPE 1.142 cm belongs to TPR 0.66"); close(tpr_for(S.r68), 0.68, 1e-9, "r_LCPE 1.309 cm belongs to TPR 0.68")
close(round(S.r66, 1), 1.1, 1e-12, "printed 1.1 cm"); close(round(S.r68, 1), 1.3, 1e-12, "printed 1.3 cm")
close(round(2 * S.r66, 1), 2.3, 1e-12, "printed 2.3 cm"); close(round(2 * S.r68, 1), 2.6, 1e-12, "printed 2.6 cm")
shown("1.1 to 1.3 cm", "r_LCPE"); shown("2.3 to 2.6 cm", "field width without equilibrium")
p = prob("smallest FWHM"); r68 = 8.369 * 0.680 - 4.382
w = bisect(lambda w: (w / 2 - 0.30 / 2) - r68, 0.0, 10.0)                       # the detector edge sits exactly r_LCPE inside the field edge
close(value(p), w, 1e-9, "smallest FWHM for a 3 mm detector, by bisection"); close(value(p), 2.918, 2e-4, "2.92 cm")
close(options(p)[1], 2 * r68, 1e-9, "decoy without the detector"); close(options(p)[0], r68 + 0.30, 1e-9, "decoy with r_LCPE once"); close(options(p)[3], 2 * r68 + 0.60, 1e-9, "decoy with the width twice")

# ---- field output factors: absolute readings and a dose per reading that differs between the fields by the factor k
def omega(ratio, k, m_msr=20.0, d_msr=1.0):
    m_clin = ratio * m_msr                                                     # nC
    n_msr = d_msr / m_msr; n_clin = k * n_msr                                  # Gy per nC in each field
    return (m_clin * n_clin) / (m_msr * n_msr)
e = EXS["Output factor from two detectors"]
close(omega(0.684, 0.958), S.om_dio, 1e-12, "diode output factor"); close(omega(0.622, 1.053), S.om_ich, 1e-12, "chamber output factor")
holds(abs(S.om_dio - S.om_ich) / S.om_ich < 0.001 and f"{S.om_dio:.3f}" == f"{S.om_ich:.3f}" == "0.655", "both detectors give 0.655 after correction")
close(100 * (0.684 / omega(0.684, 0.958) - 1), 4.38, 2e-3, "the diode reading alone is 4.4% high"); close(100 * (1 - 0.622 / omega(0.622, 1.053)), 5.03, 2e-3, "the chamber reading alone is 5.0% low")
holds("0.655 from both" in plain(e[4]) and "4.4% high" in plain(e[4]) and "5.0% low" in plain(e[4]), "the worked answer prints 0.655, 4.4%, and 5.0%")
p = prob("unshielded diode measures a 6 MV field of 10 mm")
close(value(p), omega(0.742, 0.965), 1e-12, "output factor of the question"); close(value(p), 0.716, 1e-3, "0.716")
close(options(p)[3], 0.742 / 0.965, 1e-12, "decoy dividing by k"); close(options(p)[0], 0.742 * 0.965 ** 2, 1e-12, "decoy applying k twice")
mu = lambda omega_used: 100.0 / (omega_used * 1.0)                                # MU for 100 cGy at 1 cGy/MU in the reference field
close(mu(0.622) * omega(0.622, 1.053) / 100.0, 1.053, 1e-12, "an uncorrected chamber output factor delivers the planned dose times k")

# ---- equivalent square of a rectangle: the square of the same area
p = prob("equivalent square field size")
close(value(p) ** 2, 8.4 * 11.2, 1e-12, "the square has the area of the rectangle"); close(value(p), 9.70, 1e-3, "9.70 mm")
holds((8.4 + 11.2) / 2 > value(p), "the arithmetic mean is larger"); holds("9.8 mm" in plain(p["a"][1]), "the explanation prints the arithmetic mean 9.8 mm")

# ---- conformity and gradient: coverage times selectivity, and equivalent spheres by bisection on the volume
e = EXS["Conformity and gradient"]
close((2.02 / 2.10) * (2.02 / 2.40), S.pad_a, 1e-12, "Paddick CI = coverage x selectivity"); close(S.pad_a, 0.810, 1e-3, "0.810")
close(1 / (2.10 / 2.40), S.ci_a, 1e-12, "RTOG CI"); close(1 / (2.40 / 7.70), S.gi_a, 1e-12, "gradient index")
rad = lambda v: bisect(lambda r: 4 / 3 * math.pi * r ** 3 - v, 0.0, 10.0)
close(10 * (rad(7.70) - rad(2.40)), S.fall_a, 1e-9, "fall-off between the equivalent spheres, 3.9 mm"); close(S.fall_a, 3.94, 3e-3, "3.9 mm")
holds(all(s in plain(" ".join([e[4], *e[3]])) for s in ("1.143", "0.810", "3.208", "4.0804", "5.04", "CI 1.14", "Paddick CI 0.81", "GI 3.21", "3.9 mm")), "the worked steps and answer print the computed values")
p = prob("volume inside half the prescription dose = 5.90")
close(value(p), 1 / (1.85 / 5.90), 1e-12, "gradient index of the question"); close(value(p), 3.19, 2e-3, "3.19")
close(options(p)[0], 1.85 / 5.90, 1e-12, "inverted decoy"); close(options(p)[1], 1.85 / 1.60, 1e-12, "RTOG CI decoy"); close(options(p)[3], 5.90 / 1.60, 1e-12, "target-volume decoy")

# ---- BED, fraction by fraction
bed_sum = lambda n, d, ab: sum(d + d * d / ab for _ in range(n))
e = EXS["BED of three regimens"]
for (nf, d), want, txt in (((1, 24), S.b24, "81.6"), ((3, 18), S.b54, "151.2"), ((5, 11), S.b55, "115.5")):
    close(bed_sum(nf, d, 10), want, 1e-12, f"BED of {nf} x {d} Gy"); holds(txt in plain(e[4]), f"the worked answer prints {txt}")
eqd2 = lambda n, d, ab: n * d * (d + ab) / (2 + ab)
close(eqd2(3, 18, 10) * (1 + 2 / 10), S.b54, 1e-12, "BED from EQD2 for 3 x 18 Gy")
p = prob("4 fractions of 12 Gy")
close(value(p), bed_sum(4, 12, 10), 1e-12, "BED of 4 x 12 Gy"); close(value(p), 105.6, 1e-9, "105.6 Gy")
close(options(p)[1], 48 * (1 + 10 / 12), 1e-12, "inverted-ratio decoy 88.0 Gy"); close(options(p)[3], bed_sum(4, 12, 3), 1e-12, "alpha/beta 3 decoy 240 Gy")
p = prob("Which of these regimens reaches it")
beds = {f"{nf} × {d:g} Gy": bed_sum(nf, d, 10) for nf, d in S.REG}
holds([k for k, v in beds.items() if v >= 100] == ["8 × 7.5 Gy"] and plain(p["a"][0]).endswith("8 × 7.5 Gy"), "only 8 x 7.5 Gy reaches 100 Gy, and it is the key")
holds(all(f"{v:.1f} Gy for {k}" in plain(p["a"][1]) for k, v in beds.items()), "the explanation prints each regimen's BED")
p = prob("prescribed to the 50% isodose")
holds("2.00 times" in plain(p["a"][1]) and "1.25 times" in plain(p["a"][1]) and abs(40.0 / 20.0 - 2.0) < 1e-12 and abs(25.0 / 20.0 - 1.25) < 1e-12, "a 20 Gy margin dose at 50% and 80% gives maxima of 40 and 25 Gy")

# ---- couch axis offset: rotate the target about a vertical axis with a rotation matrix
def moved(r, deg):
    th = math.radians(deg); x, y = r, 0.0                                      # target relative to the couch axis
    xr, yr = math.cos(th) * x - math.sin(th) * y, math.sin(th) * x + math.cos(th) * y
    return math.dist((x, y), (xr, yr))
e = EXS["Couch axis offset"]
close(moved(1.0, 90), S.ch_a, 1e-12, "1.0 mm offset, couch at 90 degrees"); close(moved(1.0, 180), S.ch_180, 1e-12, "and at 180 degrees")
holds("1.41 mm" in plain(e[4]) and "2.0 mm" in plain(e[4]), "the worked answer prints 1.41 mm and 2.0 mm")
p = prob("couch rotation axis passes 0.7 mm")
close(value(p), moved(0.7, 90), 1e-12, "0.7 mm offset at 90 degrees"); close(value(p), 0.990, 2e-4, "0.99 mm")
close(options(p)[2], 0.7 * math.radians(90), 1e-12, "arc-length decoy"); close(options(p)[3], moved(0.7, 180), 1e-12, "half-turn decoy")

# ---- gated delivery: step through breaths with the beam on for the first 30% of each 4 s cycle
def gated_minutes(mu_total, rate_per_min, duty, period=4.0, dt=0.0005):
    t = done = 0.0; rate = rate_per_min / 60.0
    while done < mu_total:
        if (t % period) < duty * period: done += rate * dt
        t += dt
    return t / 60.0
p = prob("respiratory gating")
for want, duty, what in ((value(p), 0.30, "delivery time 4.3 min"), (options(p)[2], 0.70, "beam-off fraction decoy 1.8 min"), (options(p)[1], 1.0, "without gating 1.3 min")):
    sim = gated_minutes(1800, 1400, duty); off = (1 - duty) * 4.0 / 60.0          # the simulation stops inside the last breath, so it can be short by one beam-off window
    holds(-1e-4 <= want - sim <= off + 1e-4 and f"{want:.1f}" == f"{sim:.1f}", f"{what}: the formula ({want:.4f}) and the breath-by-breath simulation ({sim:.4f}) agree within one beam-off window and print alike")
close(options(p)[0], 1800 * 0.30 / 1400, 1e-12, "multiplied decoy")

# ---- total targeting error: the length of the offset vector is unchanged by a rotation of the axes
v = (0.42, 0.38, 0.55); a, b = math.radians(30), math.radians(50)
rz = [[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]]; rx = [[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]]
mat = lambda m, u: [sum(m[i][j] * u[j] for j in range(3)) for i in range(3)]
w3 = mat(rx, mat(rz, v)); p = prob("total targeting error")
close(value(p), math.dist((0, 0, 0), w3), 1e-12, "total targeting error from the rotated vector"); close(value(p), 0.789, 1e-3, "0.79 mm")
holds(value(p) < 0.95 and "1.35 mm" in plain(p["a"][1]), "within 0.95 mm, and the sum of the components 1.35 mm is printed")

for x in bad: print("FAIL", x)
print(f"numbers_srs_sbrt: {n} numbers re-derived"); print("numbers_srs_sbrt: PASS" if not bad else f"numbers_srs_sbrt: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
