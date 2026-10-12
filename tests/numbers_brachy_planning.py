"""Brachytherapy planning and applicators: every number the chapter prints or keys, re-derived by another route
(BED sums fraction by fraction, bisection, time stepping of a dwell and of a decaying plaque, Euler steps of the decay law, the line-source geometry, and seed-by-seed sums)."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import brachy_planning as B, calc
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
TOP = T["brachy-planning"]
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
EXS = {b[1]: b for b in TOP["guide"] if b[0] == "ex"}
def ex_text(title): b = EXS[title]; return plain(" ".join([b[2], *b[3], b[4]]))
TEXT = " ".join(plain(b[1]) for b in TOP["guide"] if b[0] == "p") + " " + " ".join(ex_text(k) for k in EXS) + " " + " ".join(plain(x) for b in TOP["guide"] if b[0] == "eq" for x in b[1])
def shown(s, what): holds(s in TEXT, f"the page prints {s!r} ({what})")
def bed_sum(doses, ab): return sum(x * (1 + x / ab) for x in doses)           # BED added fraction by fraction
def eqd2_of_bed(bed, ab): return bisect(lambda x: x * (1 + 2 / ab) - bed, 0.0, 1000.0)   # the 2 Gy-fraction dose with that BED

# ---- external beam with HDR: EQD2 through the BED of every fraction
ext, hdr7, rect4 = [1.8] * 25, [7.0] * 4, [4.0] * 4
close(B.eb_t, eqd2_of_bed(bed_sum(ext, 10), 10), 1e-9, "external beam, tumour"); close(B.hdr_t, eqd2_of_bed(bed_sum(hdr7, 10), 10), 1e-9, "HDR, tumour")
close(B.eb_o, eqd2_of_bed(bed_sum(ext, 3), 3), 1e-9, "external beam, rectum"); close(B.hdr_o, eqd2_of_bed(bed_sum(rect4, 3), 3), 1e-9, "HDR, rectum")
close(B.tot_t, eqd2_of_bed(bed_sum(ext + hdr7, 10), 10), 1e-9, "worked example: total for the high-risk CTV"); close(B.tot_t, 83.92, 1e-3, "about 83.9 Gy")
close(B.tot_o, eqd2_of_bed(bed_sum(ext + rect4, 3), 3), 1e-9, "worked example: total for the rectum"); close(B.tot_o, 65.6, 1e-9, "65.6 Gy")
holds(80 <= B.tot_t <= 90 and B.tot_o < 70, "the answer's claims: the tumour total is inside 80 to 90 Gy and the rectum below 70 Gy")
for s in (f"{B.eb_t:.2f} Gy", f"{B.hdr_t:.2f} Gy", f"{B.eb_o:.2f} Gy", f"{B.hdr_o:.2f} Gy", f"{B.tot_t:.1f} Gy", f"{B.tot_o:.1f} Gy"): shown(s, "EQD2 example")

# ---- one dwell position: dose by time stepping at the point-source dose rate; the decay by Euler steps of dA/dt = -lambda A
rate_1cm = 40000 * 1.11                                                        # cGy/h at 1 cm: S_K Lambda, the TG-43 reference point
rate_s = rate_1cm * (1.0 / 2.0) ** 2 / 3600                                    # cGy/s at 2 cm
dt, t, dose = 0.001, 0.0, 0.0
while dose < 500.0: dose += rate_s * dt; t += dt
close(B.t0, t, 1e-4, "dwell time by time stepping"); close(B.rate2, rate_1cm / 4, 1e-12, "dose rate at 2 cm")
A, steps = 1.0, 45000; lam = math.log(2) / 73.8
for _ in range(steps): A -= lam * A * (45.0 / steps)
close(B.f45, A, 1e-4, "strength left after 45 d, by Euler steps"); close(B.t45 * B.f45 * rate_s, 500.0, 1e-9, "the longer time gives the same 500 cGy")
close(B.trak0, 40000 * B.t0 / 3600, 1e-12, "TRAK in µGy at 1 m"); close(B.trak45, B.trak0, 1e-12, "TRAK unchanged after the decay")
close(1e-6 * 1e4 * 1e2, 1.0, 1e-12, "1 U = 1 µGy m² h⁻¹ = 1 cGy cm² h⁻¹: 10⁻⁴ cGy per µGy times 10⁴ cm² per m²")
for s in (f"{B.rate2:,.0f} cGy/h", f"{B.rate2 / 3600:.3f} cGy/s", f"{B.t0:.1f} s", f"{B.f45:.4f}", f"{B.t45:.1f} s", f"{B.t0 / 3600:.5f} h", f"{B.trak0:,.0f} µGy"): shown(s, "dwell example")
close(40000 * round(B.t0 / 3600, 5), B.trak0, 5e-4, "the printed time in hours multiplies out to the printed TRAK")
L = 0.36                                                                       # HDR source active length, cm
dev = max(abs(calc.tg43_gl(r, 90, L) / calc.tg43_gl(1, 90, L) * r * r - 1) for r in (1.0, 1.5, 2.0, 3.0, 5.0, 8.0))
holds(dev < 0.011, f"on the transverse axis beyond 1 cm the point form is within about 1% of the line-source geometry ({100 * dev:.2f}%)")

# ---- seeds: strength summed seed by seed, and the activity conversion from W/e and the exposure rate constant
close(33.97 * 2.58e-4 * 100, 0.876, 1e-3, "W/e in cGy/R: 33.97 J/C × 2.58 × 10⁻⁴ C/kg per R")
close(B.sk_tot, sum(0.50 for _ in range(80)), 1e-12, "80 seeds of 0.50 U"); close(B.a_tot, sum(0.50 / (0.876 * 1.45) for _ in range(80)), 1e-12, "apparent activity")
holds(B.a_tot < 50 < 2 * B.a_tot, "one implant is below the 50 mCi limit and two are above it")
for s in (f"{B.sk_tot:.1f} U", f"{B.U_MCI:.3f}", f"{B.a_tot:.1f} mCi", f"{2 * B.a_tot:.1f} mCi"): shown(s, "seed example")

# ---- skin: inverse square from a single dwell position, with the distances in cm
for h_mm, val in ((10, B.skin10), (5, B.skin5)):
    h, z = h_mm / 10, 0.3
    close(val, 1 / (1 + z / h) ** 2, 1e-12, f"dose at 3 mm over the surface dose, source {h_mm} mm above the skin")
    shown(f"{100 * val:.0f}%", f"skin depth dose, h = {h_mm} mm")
holds(B.skin5 < B.skin10 < 1, "the nearer source gives the steeper fall with depth")

# ---- plaque: the decaying dose rate integrated numerically (Simpson), and the time found by bisection
def plaque_dose(t, rate0, th):
    m = 2000; h = t / m; f = lambda x: rate0 * 2 ** (-x / th)
    return h / 3 * (f(0) + f(t) + sum((4 if i % 2 else 2) * f(i * h) for i in range(1, m)))
th = 59.4 * 24
close(B.tp_decay, bisect(lambda x: plaque_dose(x, 0.75, th) - 85, 1, 1000), 1e-7, "worked example: plaque time with the decay")
close(B.tp_simple, 85 / 0.75, 1e-12, "plaque time at a constant rate"); holds(3 <= B.tp_simple / 24 <= 7 and 3 <= B.tp_decay / 24 <= 7, "both times are inside 3 to 7 days")
close(B.tau_h, th * 1.4427, 1e-4, "mean life 1.44 half-lives")
for s in (f"{B.tp_simple:.1f} h", f"{B.tp_simple / 24:.2f} d", f"{B.tau_h:,.0f} h", f"{B.tp_decay:.1f} h", f"{100 * (B.tp_decay / B.tp_simple - 1):.0f}% longer"): shown(s, "plaque example")

# ---- questions
p = prob("7 Gy × 4 fractions")
close(value(p), eqd2_of_bed(bed_sum(hdr7, 10), 10), 1e-9, "EQD2 of 7 Gy × 4 for alpha/beta 10")
close(options(p)[0], 28.0, 1e-12, "physical dose"); holds(any(abs(v - bed_sum(hdr7, 10)) < 1e-9 for v in p["vals"]), "the BED is offered"); holds(any(abs(v - eqd2_of_bed(bed_sum(hdr7, 3), 3)) < 1e-9 for v in p["vals"]), "alpha/beta 3 is offered")
p = prob("4.2 Gy, in 4 fractions")
r42 = [4.2] * 4
close(value(p), eqd2_of_bed(bed_sum(ext + r42, 3), 3), 1e-9, "rectum total with 4.2 Gy per fraction"); close(value(p), 67.39, 1e-3, "67.4 Gy")
holds(sorted(round(v, 6) for v in p["vals"]) == sorted(round(v, 6) for v in (eqd2_of_bed(bed_sum(ext + r42, 3), 3), 45 + 16.8, eqd2_of_bed(bed_sum(ext + r42, 10), 10), bed_sum(ext + r42, 3))), "options: EQD2, physical sum, alpha/beta 10, and the BED sum")
p = prob("largest rectal")
d_b = bisect(lambda d: eqd2_of_bed(bed_sum(ext, 3), 3) + eqd2_of_bed(bed_sum([d] * 4, 3), 3) - 75, 0, 20)
close(value(p), d_b, 1e-7, "largest rectal D2cc per fraction, by bisection"); holds(abs(B.r_left / 4 / d_b - 1) > p["tol"], "dividing the remaining EQD2 by four falls outside the tolerance")
p = prob("distance = 1.5 cm")
rate_q = 36000 * 1.11 / 1.5 ** 2 / 3600; t = 0.0; dose = 0.0
while dose < 600.0: dose += rate_q * 0.001; t += 0.001
close(value(p), t, 1e-4, "dwell time at 1.5 cm by time stepping")
holds(sorted(round(v, 6) for v in p["vals"]) == sorted(round(600 / (36000 * 1.11 * k / 3600), 6) for k in (1 / 2.25, 1, 1 / 1.5, 2.25)), "options: 1/r², none, 1/r, and r²")
p = prob("two dwell positions")
per_s = 40000 * 1.11 / 3600                                                    # cGy/s at 10 mm
doses = [per_s * (10.0 / r_mm) ** 2 * t for r_mm, t in ((20.0, 100.0), (25.0, 150.0))]   # distances in mm
close(value(p), sum(doses) / 100, 1e-12, "point dose from two dwells, in Gy"); close(value(p), 6.04, 1e-3, "6.04 Gy")
holds(sorted(round(v, 9) for v in p["vals"]) == sorted(round(v, 9) for v in (sum(doses) / 100, per_s * 250 / 100, per_s * (100 / 2.0 + 150 / 2.5) / 100, doses[0] / 100)), "options: summed, no inverse square, 1/r, and the first dwell alone")
p = prob("seeds = 90")
close(value(p), sum(0.45 / (0.876 * 1.45) for _ in range(90)), 1e-12, "apparent activity of 90 seeds"); close(value(p), 31.88, 1e-3, "31.9 mCi")
holds(sorted(round(v, 9) for v in p["vals"]) == sorted(round(v, 9) for v in (40.5 / 1.2702, 40.5, 40.5 * 1.2702, 0.45 / 1.2702)), "options: converted, unconverted, multiplied, and one seed")
p = prob("initial dose rate at the apex = 0.65 Gy/h")
tb = bisect(lambda x: plaque_dose(x, 0.65, th) - 85, 1, 1000)
close(value(p), tb, 1e-7, "plaque time with the decay, by numerical integration"); holds(abs(85 / 0.65 / tb - 1) > p["tol"], "ignoring the decay falls outside the tolerance")
p = prob("calculated in water with the TG-43 formalism")
holds(any("75 Gy" in plain(o) and "85 Gy" in plain(o) for o in p["opts"]) and any("42.5 Gy" in plain(o) for o in p["opts"]) and any("95 Gy" in plain(o) for o in p["opts"]), "the plaque options print 75 and 85 Gy, half of 85, and 95 Gy")
p = prob("Where is point A")
holds("2 cm lateral to the tandem" in plain(p["a"][0]), "the keyed point A option")

for b in bad: print("FAIL", b)
print(f"numbers_brachy_planning: {n} numbers re-derived"); print("numbers_brachy_planning: PASS" if not bad else f"numbers_brachy_planning: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
