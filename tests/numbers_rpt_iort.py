"""Radiopharmaceutical therapy and intraoperative radiotherapy: every worked number and keyed answer re-derived by another route.
The chapter uses closed forms (1/T_eff = 1/T_p + 1/T_b, Ã = 1.443 A0 T_eff, the NRC factor 34.6, BED and EQD2). Here effective half-lives come from
bisection on the retained fraction, cumulated activities and release doses from numerical integration of the activity, the Y-90 constant from counting
decays and energy in SI units, EQD2 from bisection on equal BED with BED taken from the surviving fraction, the 50 kV fall-off from fluence through
spherical shells, and the β ranges of the table from the Katz–Penfold range–energy relation."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import rpt_iort as M
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
TOP = {t["id"]: t for t in TOPICS}["rpt-iort"]; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "condition false", ""))
def prob(phrase):
    hits = [p for p in TOP["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def integral(f, a, b, steps=20000):                                            # Simpson's rule
    h = (b - a) / steps; s = f(a) + f(b)
    for i in range(1, steps): s += (4 if i % 2 else 2) * f(a + i * h)
    return s * h / 3
GUIDE = " ".join(plain(b[1]) if b[0] in ("h2", "p") else " ".join(plain(x) for x in b[1]) if b[0] in ("ul", "ol", "eq") else
                 " ".join(plain(x) for x in [b[1], b[2], b[4], *b[3]]) if b[0] == "ex" else " ".join(plain(c) for r in b[2] for c in r) if b[0] == "table" else "" for b in TOP["guide"])
TAKE = " ".join(plain(x) for items in TOP["take"] for x in items)
def shown(s, what, where=None):                                                # a re-derived number, formatted, appears on the page
    global n; n += 1
    if s not in (GUIDE if where is None else where): bad.append((what, "not found in the text", s))
retained = lambda tp, tb: (lambda t: 0.5 ** (t / tp) * 0.5 ** (t / tb))       # fraction left after physical decay and biological removal

check((TOP["domain"], TOP["sub"], TOP["ref"]["ford"]) == (6, "VI.A", "27"), "domain 6, subsection VI.A, Ford chapter 27")

# ---- worked example: effective half-life by bisection, cumulated activity by integration, dose
te1 = bisect(lambda t: retained(6.65, 10.0)(t) - 0.5, 0.0, 10.0)
close(M.TE_1, te1, 1e-9, "T_eff of 6.65 d and 10.0 d"); shown(f"{te1:.2f} d", "T_eff printed")
ca1 = integral(lambda t: 50.0 * retained(6.65 * 24, 10.0 * 24)(t), 0.0, 40 * 24 * te1)       # MBq h over 40 effective half-lives
close(M.CA_1, ca1, 1e-6, "cumulated activity by Simpson's rule"); shown(f"{ca1:,.0f} MBq h", "cumulated activity printed")
close(M.D_1, ca1 * 3.4 / 1000, 1e-6, "dose = Ã S"); shown(f"D = {ca1 * 3.4 / 1000:.1f} Gy", "dose printed")
check(te1 < min(6.65, 10.0), "the effective half-life is shorter than either")

# ---- Y-90 dose per GBq per kg: decays counted by integration, energy in joules from eV
lam = math.log(2) / (64.1 * 3600.0)
decays = integral(lambda t: 1e9 * math.exp(-lam * t), 0.0, 50 * 64.1 * 3600.0)
close(M.NDEC, decays, 1e-6, "decays per GBq left in place"); close(decays, 1e9 / lam, 1e-9, "the integral equals A0/λ")
k_y = decays * 0.93e6 * 1.602176634e-19                                       # J per GBq, so Gy per GBq per kg
close(M.K_Y90, k_y, 1e-6, "Y-90 constant from E_mean = 0.93 MeV"); shown(f"{k_y:.1f} Gy per GBq per kg", "Y-90 constant printed")
check(abs(k_y - 50.0) / 50.0 < 0.01, f"within 1% of the quoted 50 Gy per GBq per kg ({k_y:.2f})")
lo, hi = decays * 0.927e6 * 1.602176634e-19, decays * 0.937e6 * 1.602176634e-19
check(49.4 <= lo and hi <= 50.0 + 1e-9, f"the quoted range of mean energies, 0.927 to 0.937 MeV, gives {lo:.2f} to {hi:.2f}, inside the published 49.4 to 50")

# ---- microspheres: the activity solved by bisection on the dose to the liver, the lung dose from the activity in the lungs
a2 = bisect(lambda a: 50.0 * a * (1 - 0.08) / 0.80 - 120.0, 0.0, 20.0)
close(M.A_2, a2, 1e-9, "activity for 120 Gy to 0.80 kg"); shown(f"{a2:.3f} GBq", "activity printed")
lung_gbq = a2 * 0.08; close(M.DL_2, 50.0 * lung_gbq / 1.0, 1e-9, "lung dose"); shown(f"the lungs receive {50.0 * lung_gbq:.1f} Gy", "lung dose printed")
check(50.0 * lung_gbq < 30.0, "the example stays within the 30 Gy lung limit")

# ---- release: the dose rate at 1 m integrated over complete decay, with 1 R taken as 1 rem
def rel(q, occ=0.25, tp=8.02):                                                # rem
    return integral(lambda t: 2.2 * q * occ / 100.0 ** 2 * 0.5 ** (t / (tp * 24)), 0.0, 60 * tp * 24)
close(34.6, 24 / math.log(2), 2e-3, "34.6 = 24 h/d × 1.443")
d33 = rel(33.0); close(M.D_3, d33, 2e-3, "release dose for 33 mCi, integrated"); shown(f"{d33:.3f} rem", "release dose printed")
check(abs(d33 - 0.5) < 0.01, f"33 mCi reproduces about 0.5 rem ({d33:.4f})")
q5 = bisect(lambda q: 34.6 * 2.2 * q * 8.02 * 0.25 / 100 ** 2 - 0.5, 1.0, 100.0)
close(M.Q_5, q5, 1e-9, "activity for 0.5 rem by bisection"); shown(f"{q5:.1f} mCi gives exactly 5 mSv", "activity for 5 mSv printed")
close(bisect(lambda q: rel(q) - 0.5, 1.0, 100.0), q5, 2e-3, "the integrated equation gives the same activity within 0.2%")
shown(f"{q5 * 37 / 1000:.2f} GBq", "that activity in GBq"); close(round(33 * 37 / 1000, 2), 1.22, 1e-12, "33 mCi is 1.22 GBq")
close(round(2.2 * 33 / 100 ** 2 * 10, 2), 0.07, 1e-12, "the 0.07 mSv/h at 1 m in the guide follows from Γ Q / r² for 33 mCi")
p = prob("100 mCi (3.7 GBq)"); d100 = 10 * rel(100.0)
close(value(p), d100, 2e-3, "release dose for 100 mCi, integrated, in mSv")
for got, want in zip(sorted(p["vals"]), sorted([value(p), 4 * value(p), value(p) * 24 / 34.6, value(p) * 3.7 / 100])): close(got, want, 1e-9, "distractors: occupancy 1, 24 in place of 34.6, activity in GBq")
check(d100 > 5.0, "100 mCi fails the default release estimate")

# ---- BED from the surviving fraction, EQD2 by bisection on equal BED
alpha = 0.35
def bed_sf(n_fr, d, ab):
    beta = alpha / ab; return -math.log(math.exp(-n_fr * (alpha * d + beta * d * d))) / alpha
def eqd2_b(B, ab): return bisect(lambda x: x * (1 + 2 / ab) - B, 0.0, 500.0)
for ab, b_m, e_m in ((10, M.B10, M.E10), (3, M.B3, M.E3)):
    b1 = bed_sf(1, 10, ab); close(b_m, b1, 1e-9, f"BED of 10 Gy at α/β = {ab}"); close(e_m, eqd2_b(b1, ab), 1e-9, f"EQD2 of 10 Gy at α/β = {ab}")
    shown(f"{eqd2_b(b1, ab):.1f} Gy", f"EQD2 at α/β = {ab} printed")
close(M.B10F, bed_sf(5, 2, 10), 1e-9, "five 2 Gy fractions, α/β = 10"); close(M.B3F, bed_sf(5, 2, 3), 1e-9, "five 2 Gy fractions, α/β = 3")
close(eqd2_b(bed_sf(5, 2, 3), 3), 10.0, 1e-9, "2 Gy fractions have an EQD2 equal to their dose")
p = prob("dose = 12 Gy"); b12 = bed_sf(1, 12, 10)
close(value(p), eqd2_b(b12, 10), 1e-9, "EQD2 of 12 Gy, α/β = 10")
for got, want in zip(sorted(p["vals"]), sorted([eqd2_b(b12, 10), 12.0, b12, eqd2_b(bed_sf(1, 12, 3), 3)])): close(got, want, 1e-9, "distractors: physical dose, BED, late tissue")
shown(f"{eqd2_b(bed_sf(1, 10, 10), 10):.1f} Gy for α/β = 10 Gy", "take-away EQD2", TAKE)

# ---- 50 kV applicator: fluence spread over spherical shells, attenuated beyond the surface
def shell(ds, a, r, mu): return ds * (math.exp(-mu * (r - a)) / (4 * math.pi * r * r)) / (1 / (4 * math.pi * a * a))
close(M.D_X, shell(20.0, 1.5, 2.5, 0.3), 1e-12, "3 cm applicator at 1 cm"); shown(f"{shell(20.0, 1.5, 2.5, 0.3):.1f} Gy", "dose at 1 cm printed")
close(M.D_X_IS, shell(20.0, 1.5, 2.5, 0.0), 1e-12, "inverse square alone"); shown(f"inverse square alone: {shell(20.0, 1.5, 2.5, 0.0):.1f} Gy", "inverse square printed")
check(5.0 <= M.D_X <= 7.0, "the illustrative value falls inside the 5 to 7 Gy that TARGIT reported at 1 cm")

# ---- effective half-life, cumulated activity, and dose questions
p = prob("Radioiodine is retained"); close(value(p), bisect(lambda t: retained(8.02, 6.0)(t) - 0.5, 0.0, 10.0), 1e-9, "T_eff of 8.02 d and 6.0 d")
ca_a = integral(retained(6.65, 3.0), 0.0, 400.0); ca_b = integral(retained(6.65, 6.0), 0.0, 400.0)     # per unit A0, in days
p = prob("A new ligand raises the biological half-life"); r = ca_b / ca_a
check(f"It rises by a factor of {r:.2f}" == plain(p["a"][0])[3:], f"keyed: Ã rises by a factor of {r:.3f}"); close(M.r_ca, r, 1e-6, "ratio of integrated activities")
p = prob("takes up a β-emitting agent at once"); ca8 = integral(lambda t: 40.0 * 0.5 ** (t / 60.0), 0.0, 2400.0)
close(value(p), ca8 * 2.5 / 1000, 1e-6, "dose from 40 MBq, 60 h, and S = 2.5")

# ---- the table: half-lives to three significant digits, and maximum β ranges against Katz–Penfold
REF = {"I-131": (8.0207, 8.0252), "Lu-177": (6.647, 6.647), "Sm-153": (46.284, 46.284), "Sr-89": (50.563, 50.563), "Y-90": (64.05, 64.05), "Ra-223": (11.43, 11.43), "Ac-225": (9.920, 9.920)}   # evaluated half-lives (d or h as printed); I-131 differs between evaluations
for name, t, unit, *_ in M.NUC:
    s = f"{t:g}"; digits = len(s.replace(".", "").lstrip("0"))
    ulp = 10 ** (math.floor(math.log10(t)) - 2)
    check(digits == 3, f"{name}: half-life printed to three significant digits ({s} {unit})")
    check(any(abs(t - ref) <= 0.5 * ulp + 1e-9 for ref in REF[name]), f"{name}: {s} {unit} rounds an evaluated value {REF[name]}")
def kp_mm(E):                                                                 # Katz–Penfold maximum range, mg/cm² → mm at unit density
    return 412 * E ** (1.265 - 0.0954 * math.log(E)) / 100
rows = {r[0]: r for r in M.NUC}
for k, E in M.EMAX.items():
    check(abs(M.RMAX[k] - kp_mm(E)) / kp_mm(E) <= 0.15, f"{k}: maximum range {M.RMAX[k]:g} mm within 15% of Katz–Penfold {kp_mm(E):.2f} mm")
    check(rows[k][4].endswith(f"/ {M.RMAX[k]:g} mm"), f"{k}: the table prints the maximum range {M.RMAX[k]:g} mm")
check(kp_mm(2.28) > 10.5, f"Y-90 reaches about 11 mm ({kp_mm(2.28):.1f})")
for k, s in M.EMAX_TXT.items(): check(abs(float(s) - M.EMAX[k]) <= 0.5 * 10 ** (-len(s.split(".")[1])) + 1e-9, f"{k}: E_max printed as {s} MeV rounds {M.EMAX[k]} MeV")

# ---- the matching question: emissions entered a second time here
FACT = {"Ra-223": "α particles", "Y-90": "Pure β", "I-131": "364 keV", "Lu-177": "113 and 208 keV", "Sm-153": "103 keV"}
p = prob("Match each radionuclide"); got = {plain(p["bins"][c["b"]]): plain(c["t"]) for c in p["chips"]}
check(len(got) == 5 and all(FACT[k] in v for k, v in got.items()), "each radionuclide is matched to its own emissions")
for k in ("364 keV", "208 and 113 keV", "103 keV"): shown(k, f"γ energy {k} in the text")

for b in bad: print("FAIL", b)
print(f"numbers_rpt_iort: {n} numbers re-derived"); print("numbers_rpt_iort: PASS" if not bad else f"numbers_rpt_iort: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
