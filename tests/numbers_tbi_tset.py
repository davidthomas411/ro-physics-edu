"""Total body and total skin irradiation: every worked number and keyed answer re-derived by another route.
The chapter uses closed forms; here distances and monitor units are found by bisection on the delivered dose, the TMR by summing the
attenuation in thin slabs, the course doses by adding fraction by fraction, and each result is checked against the printed text."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import tbi_tset as M
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T_ = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def close_all(xs, ys, tol=1e-6, what=""):
    if len(xs) != len(ys): bad.append((what, "lengths differ", xs, ys)); return
    for a, b in zip(sorted(xs), sorted(ys)): close(a, b, tol, what)
def prob(phrase):
    hits = [p for p in T_["tbi-tset"]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
G = T_["tbi-tset"]["guide"]
GUIDE = " ".join(plain(b[1]) if b[0] in ("h2", "p") else " ".join(plain(x) for x in b[1]) if b[0] in ("ul", "ol", "eq") else
                 " ".join(plain(x) for x in [b[1], b[2], b[4], *b[3]]) if b[0] == "ex" else " ".join(plain(c) for r in b[2] for c in r) if b[0] == "table" else "" for b in G)
CARDS = " ".join(plain(" ".join(c["a"] + c["w"])) for c in T_["tbi-tset"]["cards"])
def shown(s, what, where=None):                                                # a re-derived number, formatted, appears on the page
    global n; n += 1
    if s not in (GUIDE if where is None else where): bad.append((what, "not found in the text", s))
def tmr_slabs(d, mu=0.020, dmax=3.0, k=20000):                                 # attenuation summed over thin slabs beyond d_max, then rounded as printed
    x = max(0.0, d - dmax); h = x / k; s = 1.0
    for _ in range(k): s *= 1.0 - mu * h + (mu * h) ** 2 / 2
    return round(s, 3)
def midline_dose(mu, o100, spd, tmr, fields=2):                                # dose at the midline from `fields` opposed fields of `mu` MU each, the output carried from 100 cm to the point
    fluence = (100.0 / spd) ** 2                                               # point-source fluence at spd relative to 100 cm
    return fields * mu * o100 * fluence * tmr

# ---- field size at the extended distance: the diagonal of a 40 × 40 cm field, projected
d100 = math.hypot(40.0, 40.0); close(M.DIAG, d100, 1e-12, "diagonal at 100 cm"); close(M.diag4, d100 * 400.0 / 100.0 / 100.0, 1e-12, "diagonal at 4 m, in metres")
shown(f"{d100 * 4 / 100:.2f} m at 4 m", "diagonal printed in the text"); shown(f"{d100:.1f} cm", "diagonal at 100 cm in the card working", CARDS); shown(f"{d100 * 4:.0f} cm", "diagonal at 400 cm in the card working", CARDS)

# ---- the illustrative TMR values: thin-slab attenuation gives the same rounded numbers
for name, sep in M.SITES:
    close(tmr_slabs(sep / 2), M.tmr_ill(sep / 2), 1e-12, f"TMR at half the separation, {name}")
rows = next(b for b in G if b[0] == "table")[2]
umb = next(float(r[2]) for r in rows if r[0].startswith("Abdomen"))
for r in rows:                                                                 # the percentage column follows from the printed TMR column
    close(float(r[3]), round(100 * float(r[2]) / umb), 1e-12, f"uniformity row {r[0]}")
close(1 if [r[0] for r in rows if abs(float(r[3]) - 100) > 10] == ["Head", "Neck", "Knees, legs together"] else 0, 1, 0, "head, neck, and knees are outside ±10%, the chest inside")

# ---- monitor units of the worked example: bisection on the delivered midline dose
mu_b = bisect(lambda m: midline_dose(m, M.O100, 400.0, 0.756) - 200.0, 0.0, 1e5)
close(M.mu1, mu_b, 1e-9, "MU per field by bisection"); shown(f"{mu_b:.0f} MU per field", "MU printed")
close(M.o1, bisect(lambda o: o * (400.0 / 100.0) ** 2 - M.O100, 0.0, 2.0), 1e-9, "output at 400 cm: the value that the inverse square carries back to 1.07 at 100 cm")
shown(f"{M.O100 * 0.0625:.5f} cGy/MU", "output at 400 cm printed"); shown(f"{M.O100 * 0.0625 * 0.756:.5f} cGy/MU", "dose per MU at the midline printed")

# ---- dose rate and beam-on time: rate × time returns the dose per field
close(M.rate1 * M.time1, 100.0, 1e-9, "rate × time = 100 cGy per field"); close(M.rate1, 200.0 * midline_dose(1.0, M.O100, 400.0, 0.756, fields=1), 1e-12, "dose rate from one MU at 200 MU/min")
shown(f"{M.rate1:.1f} cGy/min", "dose rate printed"); shown(f"{M.time1:.1f} min per field", "beam-on time printed"); close(1 if 5 <= M.rate1 <= 15 else 0, 1, 0, "inside 5 to 15 cGy/min")
t_frac = 0.0
for _ in range(2): t_frac += 100.0 / M.rate1                                   # two fields, each delivering 100 cGy at the midline dose rate
shown(f"about {t_frac:.0f} min of beam", "beam time of the fraction printed")

# ---- lung dose under blocks: fraction by fraction
def lung_by_fraction(factor, trans, blocked, n_fx=6, per_fx=2.0):
    return sum(per_fx * factor * (trans if k in blocked else 1.0) for k in range(n_fx))
close(M.lung1, lung_by_fraction(1.10, 0.50, {0, 1, 2, 3}), 1e-12, "lung dose, blocks for 4 of 6"); shown(f"{lung_by_fraction(1.10, 0.50, {0, 1, 2, 3}):.1f} Gy, inside", "lung dose printed")
close(M.lung1_open, lung_by_fraction(1.10, 0.50, set()), 1e-12, "lung dose without blocks"); shown(f"{lung_by_fraction(1.10, 0.50, set()):.1f} Gy without blocks", "open lung dose printed")

# ---- TSET worked example: the six contributions added one by one, then D_p by bisection
b_sum = 0.0
for pos in M.POS: b_sum += M.CH[pos]
close(M.B1, b_sum, 1e-12, "multiplication factor at the anterior chest"); shown(f"B = {b_sum:.2f}", "B printed")
dp = bisect(lambda d: d * b_sum - 2.0, 0.0, 5.0); close(M.dp1, dp, 1e-9, "D_p by bisection"); shown(f"{dp:.3f} Gy per dual field", "D_p printed")
shown(f"{100 * 1.0 / b_sum:.0f}% of the dose", "anterior share printed")

# ---- inverse square question: bisection for the distance that gives the keyed output, and the three slips
p = prob("By the inverse square law"); v = value(p)
close(bisect(lambda d: M.O100 * (100.0 / d) ** 2 - v, 101.0, 2000.0), 400.0, 1e-9, "keyed output belongs to 400 cm")
close_all(p["vals"], ([v, M.O100 / 4, M.O100 * 16, M.O100 * (103.0 / 400.0) ** 2]), 1e-12, "distractors: ratio not squared, ratio inverted, d_max added")

# ---- monitor units question: bisection on the dose at 420 cm with a 30 cm separation
p = prob("How many monitor units per field"); v = value(p)
close(v, bisect(lambda m: midline_dose(m, M.O100, 420.0, tmr_slabs(15.0)) - 200.0, 0.0, 1e5), 1e-9, "keyed MU per field")
close(M.q_mu_nohalf, 2 * v, 1e-12, "distractor: the full dose from each field"); close(M.q_mu_notmr, v * tmr_slabs(15.0), 1e-12, "distractor: no TMR")
close(M.q_mu_lin, 100.0 / (M.O100 * (100.0 / 420.0) * tmr_slabs(15.0)), 1e-12, "distractor: distance ratio not squared")

# ---- dose rate question: dose delivered in one minute
p = prob("What is the dose rate at the midline"); v = value(p)
close(v, midline_dose(300.0, M.O100, 420.0, tmr_slabs(15.0), fields=1), 1e-9, "dose in one minute at 300 MU/min"); close(1 if v < 20 else 0, 1, 0, "under 20 cGy/min")
close_all(p["vals"], [v, midline_dose(300.0, M.O100, 420.0, 1.0, fields=1), 300.0 * M.O100, v / 2], 1e-9, "distractors: no TMR, output at 100 cm, halved for two fields")
shown(f"{midline_dose(1.0, M.O100, 420.0, tmr_slabs(15.0), fields=1):.5f} cGy/MU", "dose per MU at 420 cm in the stem", plain(p["q"]))

# ---- head and knees without compensators: the percentages quoted in the explanation
p = prob("midline doses at the head and the knees"); why = plain(p["a"][1])
for sep in (16.0, 22.0): shown(f"{100 * tmr_slabs(sep / 2) / tmr_slabs(17.0):.0f}%", f"percentage for separation {sep:.0f} cm", why)

# ---- lung question: blocks for 3 of the 6 fractions, and the three slips
p = prob("fractions with blocks = 3 of 6"); v = value(p)
close(v, lung_by_fraction(1.12, 0.45, {1, 3, 5}), 1e-12, "keyed lung dose")
close_all(p["vals"], ([v, lung_by_fraction(1.0, 0.45, {1, 3, 5}), lung_by_fraction(1.12, 0.45, set(range(6))), lung_by_fraction(1.12, 0.45, set())]), 1e-12, "distractors: no lung factor, all blocked, none blocked")

# ---- transmission for 8 Gy with blocks in every fraction: bisection
p = prob("lung dose wanted = 8.0 Gy"); v = value(p)
close(v, 100 * bisect(lambda t: lung_by_fraction(1.10, t, set(range(6))) - 8.0, 0.0, 1.0), 1e-9, "transmission in percent"); shown(f"or {v:.1f}%", "transmission printed", plain(p["a"][1]))

# ---- compensator at the neck: bisection on the compensated dose, and the three slips
p = prob("What compensator transmission"); v = value(p); r = 0.942 / 0.756
close(M.r_neck, r, 1e-12, "neck over umbilicus from the printed TMRs"); shown(f"{100 * r:.1f}% of the umbilicus", "neck percentage in the stem", plain(p["q"]))
close(v, bisect(lambda t: r * t - 1.0, 0.0, 1.0), 1e-9, "both fields compensated")
close(M.q_comp_one, bisect(lambda t: r * (1.0 + t) / 2 - 1.0, 0.0, 1.0), 1e-9, "one field compensated"); close(M.q_comp_sqrt ** 2, v, 1e-12, "square-root slip"); close(M.q_comp_sub, 2.0 - r, 1e-12, "subtraction slip")

# ---- in vivo answer: lowering every MU for the neck leaves the umbilicus at 82%
close(round(M.q_low), round(100.0 / 1.22), 0, "82% at the umbilicus"); shown("= 82% of the prescription", "82% printed", plain(prob("entrance and exit diodes")["a"][1]))

# ---- TSET photon dose of a course: cycle by cycle
p = prob("What photon dose does the course give"); v = value(p)
tot = 0.0
for _ in range(18): tot += 2.0 * 0.015
close(v, tot, 1e-12, "photon dose of 18 cycles"); close(1 if v < 0.7 else 0, 1, 0, "under the EORTC 0.7 Gy"); close(M.q_x_one, 2.0 * 0.015, 1e-12, "one cycle slip"); close(M.q_x_six, 6 * tot, 1e-12, "six positions slip")

# ---- TSET point on the side: contributions added one by one
p = prob("point on the right side of the chest"); v = value(p)
s = 0.0
for pos in M.POS: s += M.SIDE[pos]
close(v, s * 2.0 / b_sum, 1e-12, "dose per cycle at the side"); shown(f"{100 * v / 2.0:.0f}% of the dose on the anterior chest", "side percentage printed", plain(p["a"][1]))

# ---- the sort questions: each chip keyed to its own bin, ranks in order
for phrase in ("Rank the steps", "Match each device"):
    p = prob(phrase); close(1 if [c["b"] for c in p["chips"]] == list(range(len(p["bins"]))) else 0, 1, 0, f"{phrase}: keyed bins")

for b in bad: print("FAIL", b)
print(f"numbers_tbi_tset: {n} numbers re-derived"); print("numbers_tbi_tset: PASS" if not bad else f"numbers_tbi_tset: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
