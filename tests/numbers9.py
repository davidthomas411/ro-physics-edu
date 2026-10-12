"""Multi-field plans, wedges, and field shaping: worked numbers re-derived by other routes (summing the two PDD curves along the axis, ray geometry of the wedge tilt, attenuation by half-value layers)."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import beamdata as bd
bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
# ---- parallel-opposed pair: sum the two beams along the axis, scale to the midplane, read the dose at the first d_max
def hot_by_sum(S, s=10):
    dose = lambda d: bd.pdd_model(d, s) + bd.pdd_model(S - d, s)             # the second beam is counted from the other surface
    return dose(bd.DMAX) / dose(S / 2)
import multifield as M
for S in (10, 20, 30, 40, 50): close(hot_by_sum(S), M.hs(S), 1e-12, f"hot spot ratio by summing two beams, S = {S}")
close(M.h20, (100 + round(bd.pdd_model(18.5, 10), 1)) / (2 * round(bd.pdd_model(10, 10), 1)), 1e-12, "hot spot of the worked example from printed values")
close(0.20 * 240, 48, 1e-12, "lateral field dose in the four-field box"); close(0.30 * 240, 72, 1e-12, "AP field dose in the four-field box"); close(2 * 72 + 2 * 48, 240, 1e-12, "the four fields add to the prescription")
close(1 if all(M.hs(S, 10) < M.hs(S + 1, 10) for S in range(10, 50)) else 0, 1, 0, "hot spot ratio rises with separation")
close(1 if all(M.hs(S, 20) < M.hs(S, 10) for S in (20, 30, 40, 50)) else 0, 1, 0, "a larger field gives a smaller hot spot")
# ---- wedges: the hinge-angle rule, MU, and the tilt of the dose profile from the isodose geometry
import wedges as W
for phi, want in ((60, 60), (90, 45), (100, 40), (120, 30), (150, 15), (180, 0)): close(W.hinge(phi), want, 1e-12, f"wedge angle for hinge angle {phi}")
close(150 / 0.55, W.mu_w, 1e-12, "MU with the wedge"); close(180 / (0.66 * 0.97), W.mu_both, 1e-12, "MU with wedge and tray")
for deg in (15, 30, 45, 60):
    shift = 10 * math.tan(math.radians(deg))                                  # an isodose tilted by deg is displaced by x tan(deg) over a width x
    close(W.tilt(deg), math.exp(-W.MU_EFF * shift), 1e-12, f"dose tilt across 10 cm for a {deg} degree wedge")
close(math.exp(-0.045 * 8 + 0.045 * 10 * math.tan(math.radians(math.degrees(math.atan(0.8))))), 1.0, 1e-9, "a wedge of atan(0.8) = 38.7 degrees exactly flattens the breast profile")
# ---- blocks and MLC: attenuation by half-value layers
import field_shaping as FS
close(FS.tr5, 100 / 32, 1e-12, "five HVL transmit 3.125%"); close(1.2 * math.log(1 / 0.05) / math.log(2), FS.t5, 1e-12, "thickness for 5% with HVL 1.2 cm")
close(0.0125 * 200, 2.5, 1e-12, "dose behind a leaf"); close(0.025 * 200, 5.0, 1e-12, "dose between leaves"); close(math.exp(-math.log(2) * 4), 0.0625, 1e-12, "four HVL transmit 6.25%")
for b in bad: print("FAIL", b)
print(f"numbers9: {n} numbers re-derived"); print("numbers9: PASS" if not bad else f"numbers9: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
