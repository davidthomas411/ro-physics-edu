"""Multi-field plans, wedges, and field shaping: worked numbers re-derived by other routes (summing the two PDD curves along the axis, ray geometry of the wedge tilt, attenuation by half-value layers)."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import beamdata as bd
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def typed(t, phrase): return next(p for p in t["problems"] if p.get("kind") == "num" and phrase in plain(p["q"]))
def fig(t, phrase): return next(p for p in t["problems"] if p.get("kind") == "fig" and phrase in plain(p["q"]))
inside = lambda p, x: any((a is None or x >= a) and (b is None or x <= b) for a, b, _, _ in p["targets"])
# ---- parallel-opposed pair: sum the two beams along the axis, scale to the midplane, read the dose at the first d_max
mf = T["multifield"]
def hot_by_sum(S, s=10):
    dose = lambda d: bd.pdd_model(d, s) + bd.pdd_model(S - d, s)             # the second beam is counted from the other surface
    return dose(bd.DMAX) / dose(S / 2)
import multifield as M
for S in (10, 20, 30, 40, 50): close(hot_by_sum(S), M.hs(S), 1e-12, f"hot spot ratio by summing two beams, S = {S}")
close(M.h20, (100 + round(bd.pdd_model(18.5, 10), 1)) / (2 * round(bd.pdd_model(10, 10), 1)), 1e-12, "hot spot of the worked example from printed values")
close(0.20 * 240, 48, 1e-12, "lateral field dose in the four-field box"); close(0.30 * 240, 72, 1e-12, "AP field dose in the four-field box"); close(2 * 72 + 2 * 48, 240, 1e-12, "the four fields add to the prescription")
close(typed(mf, "separation = 30 cm")["ans"], M.h30, 1e-12, "typed hot spot at 30 cm")
p = fig(mf, "dose that beam B adds"); s = p["spec"]["series"][0]["pts"]; S_ = 24.0; need = S_ - bd.DMAX; at = lambda pts, x0: min(pts, key=lambda q: abs(q[0] - x0))[1]
close(need, 22.5, 1e-12, "beam B is 22.5 cm from its surface at the d_max depth of beam A"); close(1 if inside(p, need) and not any(inside(p, x) for x in (1.5, 12.0, 24.0, 10.0)) else 0, 1, 0, "exit-beam target holds 22.5 cm and rejects d_max, the midplane, and the exit surface")
close(at(s, need), bd.pdd_model(need, 10), 0.01, "the plotted curve is the 6 MV PDD")
close(1 if all(M.hs(S, 10) < M.hs(S + 1, 10) for S in range(10, 50)) else 0, 1, 0, "hot spot ratio rises with separation")
close(1 if all(M.hs(S, 20) < M.hs(S, 10) for S in (20, 30, 40, 50)) else 0, 1, 0, "a larger field gives a smaller hot spot")
# ---- wedges: the hinge-angle rule, MU, and the tilt of the dose profile from the isodose geometry
import wedges as W
for phi, want in ((60, 60), (90, 45), (100, 40), (120, 30), (150, 15), (180, 0)): close(W.hinge(phi), want, 1e-12, f"wedge angle for hinge angle {phi}")
close(typed(T["wedges"], "hinge angle")["ans"], 55.0, 1e-12, "typed wedge angle for 70 degrees"); close(150 / 0.55, W.mu_w, 1e-12, "MU with the wedge"); close(180 / (0.66 * 0.97), W.mu_both, 1e-12, "MU with wedge and tray")
for deg in (15, 30, 45, 60):
    shift = 10 * math.tan(math.radians(deg))                                  # an isodose tilted by deg is displaced by x tan(deg) over a width x
    close(W.tilt(deg), math.exp(-W.MU_EFF * shift), 1e-12, f"dose tilt across 10 cm for a {deg} degree wedge")
close(math.exp(-0.045 * 8 + 0.045 * 10 * math.tan(math.radians(math.degrees(math.atan(0.8))))), 1.0, 1e-9, "a wedge of atan(0.8) = 38.7 degrees exactly flattens the breast profile")
p = fig(T["wedges"], "under the heel"); s = p["spec"]["series"][0]["pts"]; heel_ok = all(y < 100 for x, y in s if inside(p, x)) and s[0][1] > 100        # below the axis value on the heel side, above it at the toe
close(1 if heel_ok and not inside(p, -3) else 0, 1, 0, "the heel-side target lies where the wedged dose is lowest")
# ---- blocks and MLC: attenuation by half-value layers
fs = T["field-shaping"]; import field_shaping as FS
close(FS.tr5, 100 / 32, 1e-12, "five HVL transmit 3.125%"); close(1.2 * math.log(1 / 0.05) / math.log(2), FS.t5, 1e-12, "thickness for 5% with HVL 1.2 cm"); close(typed(fs, "transmission wanted = 2%")["ans"], 1.5 * math.log(50) / math.log(2), 1e-12, "typed thickness for 2%")
close(0.0125 * 200, 2.5, 1e-12, "dose behind a leaf"); close(0.025 * 200, 5.0, 1e-12, "dose between leaves"); close(math.exp(-math.log(2) * 4), 0.0625, 1e-12, "four HVL transmit 6.25%")
p = fig(fs, "five half-value layers"); s = p["spec"]["series"][0]["pts"]; x50 = next(x for x, y in s if y <= 50)
close(x50, 1.2, 0.02, "the plotted curve reaches 50% at the half-value layer, 1.2 cm"); close(5 * x50, 6.0, 0.02, "five half-value layers are 6.0 cm"); close(1 if inside(p, 6.0) and not any(inside(p, x) for x in (1.2, 4.0, 5.0, 7.0)) else 0, 1, 0, "block figure target holds 6.0 cm and rejects 1 and 4 half-value layers")
for b in bad: print("FAIL", b)
print(f"numbers9: {n} numbers re-derived"); print("numbers9: PASS" if not bad else f"numbers9: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
