"""Independent re-derivation of every worked-example number. Run: python tests/numbers.py"""
import math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import decay_law, equilibrium, pdd, tmr, scatter, mu_calc, photon_interactions, kerma_dose

fails = []
def check(name, got, want, tol=1e-9):
    ok = abs(got - want) <= tol * max(1, abs(want))
    print(("ok   " if ok else "FAIL ") + f"{name}: {got:.6g} (expected {want:.6g})")
    if not ok: fails.append(name)

ln2 = math.log(2)
# decay law
check("Tc-99m 10:30 activity (MBq)", decay_law.a_tc, 740 * math.exp(-ln2 * 3.5 / 6.0))
check("I-125 time to 10% (d)", decay_law.t10, 59.4 * math.log(10) / ln2)
check("Ir-192 lambda (1/d)", decay_law.lam_ir, ln2 / 73.8)
check("I-125 total dose (cGy)", decay_law.dinf, 7.0 * (59.4 / ln2) * 24)
check("10%/h lambda", decay_law.lam10, -math.log(0.9))
check("Co-60 loss per month", (1 - math.exp(-ln2 / (5.27 * 12))) * 100, 1.09, 0.01)
check("Cs-137 loss per year", (1 - math.exp(-ln2 / 30.1)) * 100, 2.28, 0.01)
# equilibrium: solve dN/dt numerically and compare with the closed form
tp, td = equilibrium.TP, equilibrium.TD
lp, ld = ln2 / tp, ln2 / td
Np, Nd, t, dt = 1.0 / lp, 0.0, 0.0, 0.0005
while t < 4.0:
    dNd = lp * Np - ld * Nd; Np += -lp * Np * dt; Nd += dNd * dt; t += dt
check("Tc-99m growth at 4 h (numerical integration, relative to initial parent)", ld * Nd, equilibrium.ad / 18.5, 5e-4)
check("Mo/Tc equilibrium ratio", equilibrium.ratio, tp / (tp - td))
check("Tc-99m peak time (h)", equilibrium.tmax, math.log(ld / lp) / (ld - lp))
x = equilibrium.tmax
check("daughter = parent at peak", ld / (ld - lp) * (math.exp(-lp * x) - math.exp(-ld * x)), math.exp(-lp * x))
# photon dose
f1 = ((100 + 1.5) / 110) ** 2; f2 = ((120 + 1.5) / 130) ** 2
check("Mayneord F (100 to 120 cm, d = 10)", pdd.F, f2 / f1)
check("PDD at SSD 120 (%)", pdd.p2, 67.0 * f2 / f1)
check("TMR from PDD", tmr.tmr10, 0.670 * (110 / 101.5) ** 2)
check("equivalent square 6 x 18", scatter.es, 2 * 6 * 18 / (6 + 18))
check("MU example 1 (SSD 100)", mu_calc.mu1, 200 / (1.012 * 1.008 * 0.748))
check("MU example 2 (SSD 120)", mu_calc.mu2, 200 / (1.000 * 1.008 * 0.762 * (101.5 / 121.5) ** 2))
check("MU example 3 (SAD technique, SSD calibration, per field)", mu_calc.mu3, 100 / (1.021 * 1.013 * 0.776 * (101.5 / 100) ** 2))
check("MU example 3 under SAD calibration", mu_calc.mu3_sad, 100 / (1.021 * 1.013 * 0.776))
check("MU example 4 (example 1 under SAD calibration)", mu_calc.mu4, 200 / (1.012 * 1.008 * 0.748 * (100 / 101.5) ** 2))
check("inverse-square terms: SSD calibration, SAD technique", mu_calc.cal, (101.5 / 100) ** 2); check("inverse-square terms: SAD calibration, SSD 100", mu_calc.cal_inv, (100 / 101.5) ** 2)
check("inverse-square terms: SAD calibration, SSD 120", mu_calc.iv120_sad, (100 / 121.5) ** 2)
check("SSD-calibration factor at isocenter", mu_calc.cal, (101.5 / 100) ** 2)
check("extended-SSD collimator setting", mu_calc.ac2, 12 * 100 / 120)
# photon interactions and dose quantities
check("HVLs to reach 1%", photon_interactions.n1, math.log(100) / ln2)
check("shield thickness for 1% (cm)", photon_interactions.x1, 1.5 * math.log(100) / ln2)
check("TVL = 3.32 HVL (cm)", photon_interactions.tvl, 1.5 * math.log(10) / ln2)
check("5 HVL transmission (%)", photon_interactions.t5, 100 / 32)
a = 1.0 / 0.511
check("Compton 1.0 MeV at 90 deg", photon_interactions.e90, 1.0 / (1 + a))
check("Compton 1.0 MeV at 180 deg", photon_interactions.e180, 1.0 / (1 + 2 * a))
check("50 R in C/kg", kerma_dose.xr, 50 * 2.58e-4)
check("1 R in cGy of air (W/e = 33.97 J/C)", 2.58e-4 * 33.97 * 100, 0.876, 2e-3)
check("50 R in cGy of air", kerma_dose.xc, 50 * 0.876)
check("Co-60 collision kerma (Gy)", kerma_dose.k, 0.50 * 0.0297 * 0.1)
print("\n" + ("all numbers verified" if not fails else f"{len(fails)} FAILED: {fails}"))
sys.exit(1 if fails else 0)
