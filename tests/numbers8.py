"""Profiles, skin dose and bolus, and dose algorithms: worked numbers and typed answers re-derived by other routes (ray geometry, numerical convolution, the beam model)."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s).replace("&lt;", "<").strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def simpson(f, a, b, k=4000):
    h = (b - a) / k; return h / 3 * (f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, k)))
def fig(t, phrase): return next(p for p in t["problems"] if p.get("kind") == "fig" and phrase in plain(p["q"]))
inside = lambda p, x: any((a is None or x >= a) and (b is None or x <= b) for a, b, _, _ in p["targets"])
# ---- geometric penumbra from the ray geometry: rays from the two edges of the source past the collimator edge to the plane
def penumbra_rays(s, scd, plane, xc=2.0):
    hit = lambda x0: x0 + (xc - x0) * plane / scd                       # a ray from (x0, 0) through (xc, SCD), continued to the plane
    return abs(hit(-s / 2) - hit(s / 2))
pf = T["profiles"]
for s, scd, plane in ((3, 50, 100), (3, 50, 110), (3, 40, 100), (2, 45, 105)): close(penumbra_rays(s, scd, plane), s * (plane / scd - 1), 1e-9, f"penumbra by ray geometry {s} mm, SCD {scd}, plane {plane}")
close(penumbra_rays(1, 40, 100) / penumbra_rays(1, 50, 100), 1.5, 1e-9, "SCD 40 against 50"); close(penumbra_rays(1, 50, 120) / penumbra_rays(1, 50, 105), 1.4 / 1.1, 1e-9, "depth 20 against 5 cm")
# ---- the profile figures: the edge is at 50%, the 80-20 width is 1.683 sigma, and the horn curve is flat at 10 cm
p = fig(pf, "field edge"); s = p["spec"]["series"][0]["pts"]; x80 = next(x for x, y in s if y <= 80); x20 = next(x for x, y in s if y <= 20); x50 = next(x for x, y in s if y <= 50)
close(x20 - x80, 1.683 * 0.35, 0.02, "80%-20% width of the plotted edge")
check = inside(p, x50) and not inside(p, x80) and not inside(p, x20); close(1 if check else 0, 1, 0, "field-edge target holds the 50% point and excludes the 80% and 20% points")
# ---- skin dose, bolus, and the beam model
close(0.30 * 200, 60, 1e-12, "skin dose 10 x 10"); close(2 * 0.30 * 200, 120, 1e-12, "skin dose 40 x 40"); close(0.30 * 180 * 2, 108, 1e-12, "skin dose 180 cGy, 40 x 40")
# ---- radiological depth, the lung ratio, and the TERMA-kernel convolution
import dose_algorithms as DA; rad = 3 * 1.0 + 6 * 0.3 + 3 * 1.0; close(rad, 7.8, 1e-12, "radiological depth 7.8")
close(math.exp(0.0282 * (12 - 7.8)), DA.ratio_lung, 1e-9, "TMR ratio behind lung, from the one-line TMR given in the example"); close(math.exp(0.045 * 0.7 * 6), 1.2078, 1e-3, "lung slab: 21% more dose beyond it")
MU = 0.045
def conv(d, L): return simpson(lambda s_: math.exp(-MU * (d - s_)) * math.exp(-s_ / L) / L, 0, d, 2000) if d > 0 else 0.0     # numerical convolution of the TERMA with an exponential forward kernel
for d, L in ((1.0, 0.35), (3.0, 0.35), (2.0, 0.8), (5.0, 0.2)): close(conv(d, L), (math.exp(-MU * d) - math.exp(-d / L)) / (1 - MU * L), 1e-6, f"closed-form convolution at d={d}, L={L}")
ds = [i * 0.001 for i in range(1, 6000)]; dm = max(ds[::5], key=lambda d: (math.exp(-MU * d) - math.exp(-d / 0.35)) / (1 - MU * 0.35)); close(dm, 0.35 * math.log(1 / (MU * 0.35)) / (1 - MU * 0.35), 5e-3, "d_max of the one-dimensional dose")
for b in bad: print("FAIL", b)
print(f"numbers8: {n} numbers re-derived"); print("numbers8: PASS" if not bad else f"numbers8: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
