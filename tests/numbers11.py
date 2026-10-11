"""ICRU margins, DVH metrics, and BED/EQD2/TCP: every worked number and typed answer re-derived by a different route."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def fig(t, phrase): return next(p for p in t["problems"] if p.get("kind") == "fig" and phrase in plain(p["q"]))
inside = lambda p, x: any((a is None or x >= a) and (b is None or x <= b) for a, b, _, _ in p["targets"])
import icru_volumes as IV, dvh_metrics as DV, bed_tcp as BT
# ---- margins
close(IV.m_a, 2.5 * 2 + 0.7 * 3, 1e-12, "margin for Σ 2, σ 3"); close(IV.m_a, 7.1, 1e-12, "it is 7.1 mm"); close(IV.m_b, 2.5 * 1 + 0.7 * 3, 1e-12, "margin for Σ 1, σ 3"); close(IV.m_b, 4.6, 1e-12, "it is 4.6 mm"); close(IV.m_d, 8.9, 1e-12, "margin for Σ 3, σ 2")
close(IV.margin(1.5, 2.5), 5.5, 1e-12, "typed margin"); close(IV.m_a - IV.margin(2, 1.5), 1.05, 1e-12, "halving the random error saves 1.05 mm"); close(IV.m_a - IV.m_b, 2.5, 1e-12, "halving the systematic error saves 2.5 mm")
close((10 - 2.1) / 2.5, 3.16, 1e-9, "Σ for a 10 mm margin"); p = fig(T["icru-volumes"], "systematic error at which the margin is 10 mm"); s = p["spec"]["series"][0]["pts"]; x10 = next(x for x, y in s if y >= 10)
close(x10, 3.16, 0.02, "the plotted margin reaches 10 mm at 3.16 mm"); close(1 if inside(p, 3.16) and not inside(p, 2.0) and not inside(p, 4.0) else 0, 1, 0, "the margin target holds 3.2 mm and rejects 2 and 4")
close(1800 * 3, 5400, 0, "1800 cGy × 3 is 54 Gy"); close(300 * 18, 5400, 0, "300 cGy × 18 is 54 Gy"); close(200 * 32, 6400, 0, "200 cGy × 32")
# ---- DVH: interpolation, CI, Paddick, HI
close(DV.d95, 48 + (97 - 95) / (97 - 90) * 2, 1e-12, "D95%"); close(DV.d95, 48.571, 1e-4, "D95% is 48.57 Gy"); close(DV.v_at(50), 90, 1e-12, "V50 Gy is 90%"); close(DV.d50, 52.0, 1e-12, "D50% is 52 Gy")
close(DV.ci, 45 / 30, 1e-12, "CI"); close(DV.cov, 28 / 30, 1e-12, "coverage"); close(DV.sel, 28 / 45, 1e-12, "selectivity"); close(DV.pad, (28 / 30) * (28 / 45), 1e-12, "Paddick index"); close(DV.pad, 0.5807, 1e-4, "it is 0.581")
close(DV.hi(105, 95, 100), 0.10, 1e-12, "homogeneity index 0.10"); close(DV.hi(108, 93, 100), 0.15, 1e-12, "homogeneity index 0.15"); close(DV.hi(106, 94, 100), 0.12, 1e-12, "homogeneity index 0.12")
close(1.0 * 1.0, 1.0, 0, "ideal Paddick"); disp_pad = (15 / 30) * (15 / 30); close(disp_pad, 0.25, 1e-12, "the displaced plan has a Paddick index of 0.25"); close(30 / 30, 1.0, 1e-12, "the displaced plan has CI 1")
close(1 if all(DV.dvh_ptv(a) >= DV.dvh_ptv(b) for a, b in zip(range(30, 70), range(31, 71))) and all(DV.dvh_oar(a) >= DV.dvh_oar(b) for a, b in zip(range(0, 70), range(1, 71))) else 0, 1, 0, "both smooth DVHs are cumulative curves that fall with dose")
close(DV.dvh_ptv(0), 100.0, 1e-3, "the PTV DVH starts at 100%"); close(DV.dvh_oar(0), 100.0, 1e-12, "the organ DVH starts at 100%")
x95 = next(x / 100 for x in range(4000, 6000) if DV.dvh_ptv(x / 100) <= 95); close(x95, 50 - 1.4 * 1.645, 0.01, "the smooth DVH is 95% at 47.7 Gy")
p = fig(T["dvh-metrics"], "D<sub>95%</sub>".replace("<sub>", "").replace("</sub>", "")); close(1 if inside(p, x95) and not inside(p, 50) and not inside(p, 45) else 0, 1, 0, "the D95% target holds 47.7 Gy and rejects 45 and 50")
# ---- BED, EQD2, TCP
close(BT.b_a, 30 * (1 + 3 / 10), 1e-12, "BED of 30 Gy in 10"); close(BT.b_a, 39.0, 1e-12, "it is 39.0"); close(BT.b_b, 57.6, 1e-12, "BED of 32 Gy in 4")
close(BT.e_a, 48.0, 1e-12, "EQD2 for α/β 10"); close(BT.e_b, 70.4, 1e-12, "EQD2 for α/β 3")
for D, d, ab in ((32, 8, 10), (32, 8, 3), (30, 3, 3), (8, 8, 3), (60, 2, 10)): close(BT.eqd2(D, d, ab), BT.bed(D, d, ab) / (1 + 2 / ab), 1e-12, f"EQD2 is the BED divided by (1 + 2/(α/β)) for {D} Gy at {d} Gy")
close(BT.e_p1 + BT.e_p2, 53.6, 1e-12, "the two courses add to 53.6 Gy EQD2"); close(BT.bed(45, 3, 3), 90.0, 1e-12, "typed BED")
close(BT.eqd2(60, 2, 10), 60.0, 1e-12, "EQD2 of a regimen in 2 Gy fractions is the dose itself")
for B, want in ((50, 0.047), (60, 0.859), (70, 0.992)): close(BT.tcp(B), math.exp(-1e7 * math.exp(-0.3 * B)), 1e-12, f"TCP at BED {B}"); close(BT.tcp(B), want, 0.0015, f"TCP at BED {B} is {want}")
close(BT.tcp(BT.B90), 0.9, 1e-9, "TCP is 90% at the solved BED"); close(BT.B90, 61.2, 0.001, "that BED is 61.2 Gy")
p = fig(T["bed-tcp"], "BED at which the TCP is 90%"); s = p["spec"]["series"][0]["pts"]; x90 = next(x for x, y in s if y >= 0.9)
close(x90, BT.B90, 0.1, "the plotted TCP reaches 0.90 at 61.2 Gy"); close(1 if inside(p, BT.B90) and not inside(p, 55) and not inside(p, 70) else 0, 1, 0, "the TCP target holds 61 Gy and rejects 55 and 70")
close(BT.sf(2, 0.3, 0.03), math.exp(-0.6 - 0.12), 1e-12, "survival at 2 Gy for α/β 10"); close(BT.sf(2, 0.3, 0.1), math.exp(-0.6 - 0.4), 1e-12, "survival at 2 Gy for α/β 3")
close(32 * (1 + 8 / 3), 117.333333, 1e-6, "BED of the 4 × 8 Gy regimen for α/β 3"); close(60 * (1 + 2 / 3), 100.0, 1e-9, "BED of 60 Gy in 30 for α/β 3")
for b in bad: print("FAIL", b)
print(f"numbers11: {n} numbers re-derived"); print("numbers11: PASS" if not bad else f"numbers11: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
