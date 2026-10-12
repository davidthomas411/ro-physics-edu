"""Dose limits and ALARA: every number the chapter prints or keys, re-derived by another route
(exact fractions for the tissue weights, limits converted from their rem values in the regulation, mrem arithmetic,
bisection for distances, step-by-step dose accumulation in time, and half-value layers for the apron)."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard numbers module that fractions uses
import re, math
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import blocks, nistdata as N
import dose_limits as D
plain = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
tp = next(t for t in TOPICS if t["id"] == "dose-limits"); bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what,))
def prob(phrase):
    hits = [p for p in tp["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def accumulate(rate, target, dt=1e-4):                                          # hours of exposure at a constant rate until the dose reaches target, step by step
    steps, dose = 0, 0.0
    while dose < target - 1e-12: dose += rate * dt; steps += 1
    return steps * dt
text = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()       # page text with a space where each tag was, so table cells stay apart
GUIDE = text(blocks.render(tp["guide"], {}, tid=tp["id"]))
TAKE = " ".join(text(x) for items in tp["take"] for x in items)
CARDS = " ".join(text(a) for c in tp["cards"] for a in c["a"] + c["w"])
def shown(s, where=GUIDE, what=""): check(s in where, f"printed: {what or s}")

# ---- ICRP 103 tissue weighting factors, typed here from the publication as exact fractions
W103 = {**{t: Fr(12, 100) for t in ("red bone marrow", "colon", "lung", "stomach", "breast", "remainder tissues")}, "gonads": Fr(8, 100),
        **{t: Fr(4, 100) for t in ("bladder", "oesophagus", "liver", "thyroid")}, **{t: Fr(1, 100) for t in ("bone surface", "brain", "salivary glands", "skin")}}
check(sum(W103.values()) == 1, "the ICRP 103 weights sum to exactly 1")
check(set(D.W) == set(W103) and all(abs(D.W[t] - float(W103[t])) < 1e-12 for t in W103), "the chapter's weights match ICRP 103 tissue by tissue")
check("lens" not in " ".join(W103), "the lens has no tissue weighting factor")
groups = {}
for t, w in W103.items(): groups[w] = groups.get(w, 0) + w
for w, tot in groups.items(): shown(f"{float(w):.2f} {', '.join(x for x, v in W103.items() if v == w).capitalize()}", what=f"group {float(w):.2f}"); shown(f"{float(tot):.2f}", what=f"group total {float(tot):.2f}")
shown("All tissues 1.00"); check(f"= {float(sum(W103.values())):.2f}" in CARDS, "the card working sums the groups to 1.00")
close(D.skin_e, float(W103["skin"] * 500), 1e-12, "500 mSv to the whole skin adds 5 mSv to E"); shown("500 mSv to the whole skin adds 5 mSv to E")

# ---- neutron radiation weighting factor (ICRP 103, eq. 4.3), written here as a table of branch constants
BR = [(0.0, 1.0, 2.5, 18.2, 1.0), (1.0, 50.0, 5.0, 17.0, 2.0), (50.0, math.inf, 2.5, 3.25, 0.04)]   # E from, E to, a, b, c in w = a + b exp(-ln(cE)^2 / 6)
def wr(e, branch=None):
    lo, hi, a, b, c = branch or next(x for x in BR if x[0] <= e < x[1] or (x[1] == 50.0 and e == 50.0))
    return a + b * math.exp(-math.log(c * e) ** 2 / 6)
for e in (1e-8, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 1000.0): close(D.wr_neutron(e), wr(e), 1e-12, f"w_R at {e} MeV")
close(wr(1.0, BR[0]), wr(1.0, BR[1]), 2e-3, "the branches meet at 1 MeV"); close(wr(50.0, BR[1]), wr(50.0, BR[2]), 2e-3, "the branches meet at 50 MeV")
gold = (math.sqrt(5) - 1) / 2; lo_, hi_ = math.log(0.01), math.log(50.0)                       # golden-section search for the peak on a log energy axis
for _ in range(200):
    x1, x2 = hi_ - gold * (hi_ - lo_), lo_ + gold * (hi_ - lo_)
    if wr(math.exp(x1)) > wr(math.exp(x2)): hi_ = x2
    else: lo_ = x1
e_pk = math.exp((lo_ + hi_) / 2); close(e_pk, 1.0, 1e-4, "the peak lies at 1 MeV"); shown(f"a peak of {wr(e_pk):.1f} at 1 MeV")
shown(f"{wr(2.53e-8):.1f} for thermal neutrons"); close(wr(2.53e-8), 2.5, 1e-9, "thermal neutrons: 2.5"); shown(f"{wr(10.0):.1f} at 10 MeV")
check(f"a peak of {wr(1.0):.1f} at 1 MeV" in CARDS and f"peaks at {wr(1.0):.1f} at 1 MeV" in TAKE, "the card and the take-away quote the same peak")
check(all(f"{float(w):.2f} " in TAKE for w in groups), "the take-away lists every weight group")

# ---- worked example: effective dose from organ doses
ex1 = {"lung": Fr(60, 10), "red bone marrow": Fr(20, 10), "thyroid": Fr(100, 10), "skin": Fr(200, 10)}
e1 = sum(W103[t] * h for t, h in ex1.items()); close(D.e1, float(e1), 1e-12, "effective dose of the example"); shown(f"{float(e1):.2f} mSv. The skin")
contrib = {t: W103[t] * h for t, h in ex1.items()}
check(max(ex1, key=ex1.get) == "skin" and min(contrib, key=contrib.get) == "skin", "the skin has the largest equivalent dose and the smallest contribution")
shown(f"= {float(contrib['lung'] + contrib['red bone marrow']):.2f} mSv"); shown(f"0.04 × 10.0 = {float(contrib['thyroid']):.2f} mSv"); shown(f"0.01 × 20.0 = {float(contrib['skin']):.2f} mSv")

# ---- worked example: equivalent dose with neutrons, in mrad and mrem (1 mGy = 100 mrad; 1 mrem = 0.01 mSv)
mrem = 40 * 1 + 3 * 10; close(D.h2, mrem / 100, 1e-12, "0.40 mGy photons and 0.030 mGy neutrons with w_R = 10"); shown(f"{mrem / 100:.2f} mSv. The neutrons give {100 * 30 / mrem:.0f}% of it from {100 * 3 / 43:.0f}% of the absorbed dose")

# ---- limits: each 10 CFR 20 value in mSv is its rem value in the regulation times 0.01 Sv/rem
CFR_REM = dict(tede=5, organ=50, lens=15, skin=50, fetus=0.5, public=0.1, hour=0.002)
for k, r in CFR_REM.items(): close(D.NRC[k], r * 0.01 * 1000, 1e-12, f"10 CFR 20 {k}: {r} rem")
pairs = re.findall(r"(\d+(?:\.\d+)?) mSv \((\d+(?:\.\d+)?) rem\)", GUIDE + " " + CARDS + " " + " ".join(plain(b) for p in tp["problems"] if p.get("kind") == "sort" for b in p["bins"]))
check(len(pairs) >= 12, f"{len(pairs)} limits are printed with both units"); [close(float(a), float(b) * 0.01 * 1000, 1e-12, f"{a} mSv = {b} rem") for a, b in pairs]
close(D.NRC["minor"] * D.NRC["tede"], 0.1 * 5 * 10, 1e-12, "a minor: 10% of 5 rem = 0.5 rem = 5 mSv"); check(keyed(prob("17-year-old")).startswith("5 mSv per year"), "the keyed limit for a minor is 5 mSv")
close(D.NRC["fetus"] - D.NRC["fetus_near"], (0.5 - 0.05) * 10, 1e-12, "within 0.05 rem of 0.5 rem: 4.5 mSv"); shown("0.5 mSv more if 4.5 mSv or more")
check(keyed(prob("declares her pregnancy")).startswith(f"{(0.5 * 10) - 1.0:.1f} mSv"), "5 mSv over the pregnancy less 1.0 mSv received: 4.0 mSv left")
shown("20 mSv averaged over 5 years, at most 50 mSv in one year"); close(D.ICRP["avg"] * D.ICRP["years"], 100.0, 1e-12, "ICRP: 100 mSv in 5 years")
check(D.ICRP["avg"] * D.ICRP["years"] <= D.ICRP["max1"] * D.ICRP["years"] and D.ICRP["avg"] < D.NRC["tede"], "the ICRP average is below the NRC annual limit and below its own one-year cap")
weeks = 50; close(sum(D.GOAL["ctrl"] for _ in range(weeks)), 5.0, 1e-9, "0.1 mSv a week for 50 weeks is 5 mSv"); close(sum(D.GOAL["unctrl"] for _ in range(weeks)), 1.0, 1e-9, "0.02 mSv a week for 50 weeks is 1 mSv")
shown("0.1 mSv per week (5 mSv per year)"); shown("0.02 mSv per week (1 mSv per year)")
SORTQ = prob("Match each person or organ"); lim = {0: 5, 1: 15, 2: 50, 3: 0.1, 4: 0.5}                     # rem values of the five bins, from the regulation
for c in SORTQ["chips"]: check(f"{lim[c['b']] * 10:g} mSv" in plain(SORTQ["bins"][c["b"]]), f"bin of '{plain(c['t'])}'")

# ---- NCRP 116 cumulative guidance: 10 mSv for each year of age
age = 45; close(value(prob("45 years old")), sum(10 for _ in range(age)), 1e-12, "lifetime limit at 45: 450 mSv")
vals = prob("45 years old")["vals"]; check(sum(50 for _ in range(age)) in vals and sum(10 for _ in range(19, age + 1)) in vals, "decoys: 50 mSv a year of age, and 10 mSv a year since 18")

# ---- investigation levels, in mrem per quarter
q_lim = 5000 / 4; l1, l2 = 0.10 * q_lim / 100, 0.30 * q_lim / 100                                     # mrem -> mSv
close(D.l1, l1, 1e-12, "level I: 125 mrem per quarter"); close(D.l2, l2, 1e-12, "level II: 375 mrem per quarter"); shown(f"{l1:.2f} and {l2:.2f} mSv for the TEDE")
check(l1 < D.badge_q < l2 and keyed(prob("badge shows a deep dose")).startswith("Level I is exceeded but level II is not"), "2.0 mSv lies between the levels, so level I applies")

# ---- worked example: time to reach 0.5 mSv at 2.0 m, by accumulating dose hour by hour
S = 0.40 * 4 * math.pi * 0.50 ** 2                                                                   # source term: rate × 4πr² is the same at every distance
r2 = S / (4 * math.pi * 2.0 ** 2); close(D.rate3, r2, 1e-12, "rate at 2.0 m"); t = accumulate(r2, 0.5); close(D.t3, t, 1e-3, "20 h to 0.5 mSv")
shown(f"{t:.0f} h. At 4.0 m the time would be {accumulate(S / (4 * math.pi * 16), 0.5):.0f} h")

# ---- worked example: collar and under-apron dose, in mrem
c_mrem = 200 / 1.5 ** 2 * 0.1; u_mrem = c_mrem * 2 ** (-math.log2(1 / 0.05))                       # 2.0 mSv/h = 200 mrem/h at 1 m
close(D.collar4 * 100, c_mrem, 1e-12, "collar dose"); close(D.under4 * 100, u_mrem, 1e-12, "dose under the apron")
shown(f"{c_mrem * 10:.0f} µSv at the collar and {u_mrem * 10:.1f} µSv under the apron, 1/{round(c_mrem / u_mrem)}")

# ---- question: effective dose, with exact fractions
qe = {"stomach": Fr(4), "colon": Fr(3), "liver": Fr(5), "gonads": Fr(2)}
close(value(prob("stomach = 4.0")), float(sum(W103[t] * h for t, h in qe.items())), 1e-12, "effective dose: 1.20 mSv")
check(set(prob("stomach = 4.0")["vals"]) == {float(sum(W103[t] * h for t, h in qe.items())), float(sum(qe.values())), float(Fr(12, 100) * sum(qe.values())), float(sum(qe.values()) / 4)}, "decoys: no weights, all 0.12, the mean")

# ---- question: equivalent dose with 2 MeV neutrons
w2 = round(wr(2.0), 1); close(w2, 17.3, 1e-12, "w_R at 2 MeV, as printed"); close(value(prob("2 MeV neutrons")), 1.2 + 0.040 * w2, 1e-12, "1.2 + 0.040 × 17.3")
check(set(prob("2 MeV neutrons")["vals"]) >= {1.2 + 0.040, 1.2 + 0.040 * 20}, "decoys: no weighting, and w_R = 20")

# ---- question: typed dose at 3 m for 40 min, by accumulation in µSv
close(value(prob("time = 40 min")), accumulate(0.90 / 9 * 1000, 0.90 / 9 * 1000 * 40 / 60, 1e-5) * 0.90 / 9 * 1000, 1e-3, "66.7 µSv")

# ---- question: distance to the hourly limit, by bisection
for want, r_ in ((0.02, D.r_hr), (0.002, D.r_hr_rem), (0.2, D.r_hr_tenx)): close(bisect(lambda r: 0.50 / r ** 2 - want, 0.1, 100), r_, 1e-9, f"distance where 0.50 mSv/h at 1 m falls to {want} mSv/h")
close(bisect(lambda r: 0.50 / r - 0.02, 0.1, 100), D.r_hr_lin, 1e-9, "the 1/r decoy"); close(value(prob("unshielded point source")), 5.0, 1e-9, "5.0 m")

# ---- question: apron transmission at 0.4 MeV, by half-value layers
mu = N.LEAD[0.4][0] * N.DENS["lead"]; hvl = math.log(2) / mu
close(value(prob("Ir-192 seed ribbons")), 0.5 ** (0.05 / hvl), 1e-12, "transmission of 0.5 mm of lead"); close(round(0.5 ** (0.05 / hvl), 2), 0.88, 1e-12, "0.88")
check({round(v, 2) for v in prob("Ir-192 seed ribbons")["vals"]} == {round(0.5 ** (0.05 / hvl), 2), round(1 - 0.5 ** (0.05 / hvl), 2), round(0.5 ** (0.5 / hvl), 2), round(0.5 ** (0.05 / (math.log(2) / N.LEAD[0.4][0])), 2)}, "decoys: removed fraction, mm as cm, no density")
check(f"{N.LEAD[0.4][0]:.4f} cm²/g" in plain(prob("Ir-192 seed ribbons")["q"]), "the stem quotes the NIST value")

# ---- question: 120 mrem in mSv, through the sievert
close(value(prob("120 mrem")), 120 / 1000 * 0.01 * 1000, 1e-12, "120 mrem = 1.2 mSv")

for b in bad: print("FAIL", b)
print(f"numbers_dose_limits: {n} numbers re-derived"); print("numbers_dose_limits: PASS" if not bad else f"numbers_dose_limits: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
