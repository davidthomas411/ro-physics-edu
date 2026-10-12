"""Independent re-derivation of the numbers in the treatment-planning practice questions (PDD, TMR, scatter, MU), by routes that share no code with calc.py or the topic files."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import pdd, tmr, scatter, mu_calc
from topics import TOPICS
TOPICS_BY = {x['id']: x for x in TOPICS}
fails = []; n = 0
def check(name, got, want, tol=1e-6):
    global n; n += 1
    if abs(got - want) > tol * max(abs(want), 1e-12): fails.append(f"{name}: got {got!r}, independent {want!r}")
I = lambda f, x: 1.0 / (f + x) ** 2                                     # fluence at distance f + x from a point source
def pdd_at(pdd1, f1, f2, d, dmax):                                    # carry the dose ratio between two points through the fluence at each SSD
    r1 = I(f1, d) / I(f1, dmax); r2 = I(f2, d) / I(f2, dmax); return pdd1 * r2 / r1
# ---- PDD
check("dose at 10 cm", pdd.q_dose10, 100.5); check("dose at dmax", pdd.q_dmaxdose, 298.5074627, 1e-7); check("field at 15 cm", pdd.q_fld15, 11.5)
check("PDD 6 MV SSD 140", pdd.q_p140, pdd_at(67.0, 100, 140, 10, 1.5)); check("PDD 10 MV SSD 80", pdd.q_p80, pdd_at(71.0, 100, 80, 12, 2.5))
check("PDD 140 is about 70.0", pdd.q_p140, 70.0, 1e-3); check("dmax dose ratio 70/67", pdd.q_ratio, (200 / 0.67) / (200 / 0.70), 1e-12)
# ---- TMR: the same point, so the dose ratio is the PDD ratio times the fluence at dmax over the fluence at d
def tmr_from(pdd_pct, f, d, dmax, sp=1.0): return pdd_pct / 100 * I(f, dmax) / I(f, d) * sp
check("TMR 15 cm", tmr.q_tmr15, tmr_from(58.0, 100, 15, 1.5)); check("TMR 12 cm SSD 80", tmr.q_tmr80, tmr_from(71.0, 80, 12, 2.5, 0.99))
check("TMR 10 cm SSD 100", tmr.tmr10, tmr_from(67.0, 100, 10, 1.5))
check("TMR from the SSD 120 PDD equals the SSD 100 value", tmr.q_tmr120, tmr.tmr10, 1e-9)
check("PDD at SSD 120 is 68.7", tmr.q_pdd120, 68.7, 1e-3)
mu_used = 1 / 0.670; mu_true = 1 / tmr.tmr10; check("PDD used for TMR: delivered dose too high", tmr.q_wk, mu_used / mu_true - 1, 1e-9)
check("PDD used for TMR is about 17% high", tmr.q_wk, 0.1745, 3e-3)
# ---- scatter: S_cp is a product, S_p a quotient; the equivalent square from the area-to-perimeter ratio
check("Scp", scatter.q_scp, 0.940 * 0.975); check("Sp", scatter.q_sp, 1.072 / 1.028)
ap = lambda a, b: (a * b) / (2 * (a + b)); check("8 x 20 equivalent square (4 x A/P)", scatter.q_es820, 4 * ap(8, 20)); check("6 x 18 equivalent square", scatter.q_es618, 9.0)
slope = (1.000 - 0.976) / (10 - 8); check("S_cp(6 x 18) by interpolation", scatter.q_interp, 0.976 + slope * (9.0 - 8)); check("S_cp(6 x 18) = 0.988", scatter.q_interp, 0.988, 1e-9)
# ---- monitor units
MU = lambda d, d0, *f: d / (d0 * math.prod(f))
check("MU SSD 100, 250 cGy at 10 cm", mu_calc.q_mua, MU(250, 1, 1.017, 1.014, 0.680))
iv = (1 / 121.5 ** 2) / (1 / 101.5 ** 2)                              # fluence at 121.5 cm over fluence at 101.5 cm
check("MU extended SSD 120", mu_calc.q_muc, MU(200, 1, 1.009, 1.014, 0.714, iv))
check("MU SAD single field, SSD calibration", mu_calc.q_mub, MU(100, 1, 1.021, 1.013, 0.738, 1.030225)); check("MU SAD pair, 15 x 15 row", mu_calc.q_mud, MU(100, 1, 1.011, 1.010, 0.742))
check("equivalent square of 12 x 20 is 15", 4 * ap(12, 20), 15.0)
check("SSD calibration factor", mu_calc.q_cal, 1.030225); check("MU on the SAD-calibrated machine", mu_calc.q_mue, MU(100, 1, 1.021, 1.013, 0.738))
check("SAD calibration needs 3.0% more MU than SSD calibration", mu_calc.q_mue / mu_calc.q_mub - 1, 0.030225, 1e-6)
check("MU, SSD technique on a SAD-calibrated machine", mu_calc.q_mun2, MU(250, 1, 1.017, 1.014, 0.680, (100 / 101.5) ** 2))
check("the chapter example under SAD calibration", mu_calc.mu4, MU(200, 1, 1.012, 1.008, 0.748, (100 / 101.5) ** 2))
check("the pair example under SSD calibration", mu_calc.mu3, MU(100, 1, 1.021, 1.013, 0.776, 1.030225))
check("the pair example under SAD calibration", mu_calc.mu3_sad, MU(100, 1, 1.021, 1.013, 0.776))
check("wedge MU", mu_calc.q_muw, 120 / 0.62); check("tray MU", mu_calc.q_mut, 200 / 0.97); check("collimator opening", mu_calc.q_ac, 12.0)
mu1_i = 200 / (1.012 * 1.008 * 0.748); mu2_i = 200 / (1.000 * 1.008 * 0.762 * (1 / 121.5 ** 2) / (1 / 101.5 ** 2))
check("chapter example: MU at SSD 100", mu_calc.mu1, mu1_i); check("chapter example: MU at SSD 120", mu_calc.mu2, mu2_i)
pc = round((mu2_i / mu1_i - 1) * 100); ext = [p for p in TOPICS_BY["mu-calc"]["problems"] if "SSD 120 cm instead of SSD 100 cm" in re.sub(r"<[^>]+>", "", p["q"])][0]; n += 1
if f"{pc}% more" not in re.sub(r"<[^>]+>", "", ext["a"][1]): fails.append(f"extended-SSD explanation does not state {pc}% more: {ext['a'][1][-120:]!r}")
# ---- the correct option holds the right value, and the stem prints the numbers it uses
byid = {t["id"]: t for t in TOPICS}
plain = lambda x: re.sub(r"<[^>]+>", "", x)
def find(tid, phrase):
    hits = [p for p in byid[tid]["problems"] if plain(phrase) in plain(p["q"])]
    assert len(hits) == 1, (tid, phrase, len(hits)); return hits[0]
def right(p): i = "ABCDEFG".index(re.search(r"<b>([A-G])\.", p["a"][0]).group(1)); return p["vals"][i]
CASES = [("pdd", "dose at d<sub>max</sub> = 150 cGy", pdd.q_dose10, ["150", "67.0%"]), ("pdd", "prescription = 200 cGy at 10 cm depth", pdd.q_dmaxdose, ["200", "67.0%"]),
         ("pdd", "new SSD = 140 cm", pdd.q_p140, ["1.5 cm", "67.0%", "SSD 100"]), 
         ("tmr", "PDD = 58.0% at 15 cm", tmr.q_tmr15, ["58.0%", "1.5 cm"]), 
         ("tmr", "SSD-100 PDD in place of the TMR", tmr.q_wk, ["0.670", "0.787"]),
         ("scatter", "S<sub>c</sub> = 0.940", scatter.q_scp, ["0.940", "0.975"]), 
         ("scatter", "8 × 20 cm", scatter.q_es820, ["8 × 20"]), 
         ("scatter", "S<sub>c</sub>(14 × 14) = 1.010", scatter.q_blocked, ["1.010", "1.012", "1.000"]),
         ("mu-calc", "surface at 100 cm.prescription = 250 cGy at 10 cm depth", mu_calc.q_mua, ["250", "1.017", "1.014", "68.0%"]), ("mu-calc", "S<sub>c</sub>(12.5 × 12.5", mu_calc.q_muc, ["200", "1.009", "1.014", "71.4%", "120 cm"]),
         ("mu-calc", "dose per field = 100 cGy at 12 cm", mu_calc.q_mub, ["100", "1.021", "1.013", "0.738"]), 
         ("mu-calc", "MU without the wedge = 120", mu_calc.q_muw, ["120", "0.62"]), 
         ]
for tid, phrase, want, shown in CASES:
    p = find(tid, phrase); n += 1
    got = right(p)
    if abs(got - want) > 1e-6 * max(abs(want), 1): fails.append(f"{tid} '{phrase[:30]}': marked-correct option holds {got!r}, expected {want!r}")
    for s in shown:
        n += 1
        if plain(s) not in plain(p["q"]): fails.append(f"{tid} '{phrase[:30]}': stem does not print {s!r}")
print(f"numbers3: {n} checks on {len(CASES)} treatment-planning questions")
for f in fails: print("FAIL", f)
print("numbers3: PASS" if not fails else f"numbers3: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
