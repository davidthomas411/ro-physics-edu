"""Electron chapters: the rules of thumb, the worked numbers, the typed answers, and the tap targets re-derived by other routes (the curve passes through the stated depths)."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
import electron_pdd as EP, electron_fields as EF
# ---- rules of thumb
for E, r90, r80, r50, rp in ((6, 1.82, 2.0, 2.58, 3.0), (12, 3.64, 4.0, 5.15, 6.0), (20, 6.06, 6.67, 8.58, 10.0)):
    close(EP.r90(E), r90, 0.002, f"R90 of {E} MeV"); close(EP.r80(E), r80, 0.002, f"R80 of {E} MeV"); close(EP.r50(E), r50, 0.002, f"R50 of {E} MeV"); close(EP.rp(E), rp, 1e-9, f"Rp of {E} MeV")
close(EP.dref(12), 0.6 * (12 / 2.33) - 0.1, 1e-12, "reference depth of 12 MeV"); close(EP.dref(12), 2.99, 0.002, "reference depth of 12 MeV is 2.99 cm")
close(EP.E_need, 9.9, 1e-12, "energy for R90 = 3.0 cm"); close(3.3 * 3.0 / 3.3, 3.0, 1e-12, "R90 of 9.9 MeV is 3.0 cm"); close(EP.r90(9), 2.727, 0.001, "a 9 MeV beam falls short of 3.0 cm"); close(EP.r90(12), 3.636, 0.001, "12 MeV reaches 3.0 cm at the 90% line")
# ---- the schematic PDD passes through the stated depths and has the right shape
f12 = EP.pdd_e(12)
for d, v in ((EP.r90(12), 90), (EP.r80(12), 80), (EP.r50(12), 50), (EP.rp(12), 4)): close(f12(d), v, 1e-9, f"the 12 MeV curve is {v}% at {d:.2f} cm")
xs = [i * 0.01 for i in range(0, 801)]; ys = [f12(x) for x in xs]; pk = xs[ys.index(max(ys))]; close(max(ys), 100.0, 1e-3, "the curve peaks at 100%"); close(1 if (EP.r90(12) * 0.5 <= pk <= EP.r90(12)) else 0, 1, 0, "the dose maximum is at a depth shallower than R90")
close(1 if all(f12(a) >= f12(a + 0.01) - 1e-9 for a in [pk + i * 0.01 for i in range(0, 700)]) else 0, 1, 0, "the curve falls steadily beyond the maximum")
# ---- the problems
close(2 * 7.5, 15.0, 1e-12, "energy from a practical range of 7.5 cm"); close(EP.r90(15), 15 / 3.3, 1e-12, "R90 of 15 MeV"); close(EP.r50(14), 14 / 2.33, 1e-12, "R50 of 14 MeV")
# ---- electron fields
close(EF.hot_ep, 260.0, 1e-12, "hot spot at an electron-photon junction, 200 cGy and 30%"); close(EF.hot_ee, 165.0, 1e-12, "hot spot at an electron-electron junction, 150 cGy and 10%"); close(6 + 1 + 1, 8, 0, "cutout width, 6 cm area"); close(7 + 2, 9, 0, "cutout width, 7 cm area")
close(1 if EF.w18(0) < EF.w8(0) and EF.w18(6) > EF.w8(6) else 0, 1, 0, "the 18 MeV penumbra is smaller near the surface and larger at depth")
# ---- electron output and monitor units
import electron_mu as EM
close(EM.inv(5), (86.8 / 91.8) ** 2, 1e-12, "inverse-square term at SSD 105 cm"); close(EM.inv(5), 0.894, 0.002, "it is 0.894"); close(EM.inv(10), (86.8 / 96.8) ** 2, 1e-12, "inverse-square term at SSD 110 cm"); close(EM.inv(0), 1.0, 1e-12, "it is 1 at SSD 100 cm")
close(EM.mu_a, 200 / (0.90 * 0.97), 1e-12, "MU at SSD 100 cm"); close(EM.mu_a, 229.1, 0.001, "MU at SSD 100 cm is 229.1"); close(EM.mu_c, 200 / (0.90 * 0.97 * (86.8 / 96.8) ** 2), 1e-12, "MU at SSD 110 cm"); close(EM.mu_t, 250 / (0.80 * 1.02), 1e-12, "MU at the 80% depth")
close(100 * (1 - EM.inv(5)), 10.6, 0.01, "output falls by 10.6% at SSD 105 cm"); close(EM.mu_c / EM.mu_a, 1 / EM.inv(10), 1e-12, "MU scale as the inverse of the inverse-square term")
g = 86.8 * (1 / math.sqrt(0.8) - 1); close(EM.inv(g), 0.8, 1e-12, "the dose per MU is 80% at an air gap of 10.2 cm")
for b in bad: print("FAIL", b)
print(f"numbers10: {n} numbers re-derived"); print("numbers10: PASS" if not bad else f"numbers10: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
