"""The multileaf collimator figures: where they are placed, that every drawn element lies inside its panel, and that what the captions claim follows from the drawn geometry
(band widths of the leaf ends by a second method, equal area of the leaf-gap profile and its dashed opening, no straight path through the tongue-and-groove joint)."""
import re, sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
import figs
from topics import TOPICS
T = {t["id"]: t for t in TOPICS}; F = figs.build(); bad = []; n = 0
def check(ok, *what):
    global n; n += 1
    if not ok: bad.append(what)

# ---- placement: each figure once, in the chapter and section that discuss it, with a caption that says it is a schematic
PLACE = dict(mlc_bank=("field-shaping", "Multileaf collimators"), mlc_leaf_ends=("field-shaping", "Edges and penumbra"), mlc_dlg=("mlc-imrt", "Rounded leaf ends"), mlc_tg=("mlc-imrt", "Tongue and groove"))
PANELS = dict(mlc_bank=3, mlc_leaf_ends=3, mlc_dlg=2, mlc_tg=2)
for fid, (tid, sec) in PLACE.items():
    here, cur, caps = [], None, []
    for b in T[tid]["guide"]:
        if b[0] == "h2": cur = re.sub(r"<[^>]+>", "", b[1])
        if b[0] == "fig" and b[1] == fid: here.append(cur); caps.append(b[2])
    check(here == [sec], fid, "placed in", here, "expected", sec)
    check(all(c.startswith("Schematic") for c in caps), fid, "caption does not say schematic")
    for other in TOPICS:
        if other["id"] != tid: check(not any(b[0] == "fig" and b[1] == fid for b in other["guide"]), fid, "also in", other["id"])
    check(F[fid].count("<svg") == PANELS[fid], fid, "panels", F[fid].count("<svg"))

# ---- every drawn element lies inside the viewBox of its panel
num = lambda s: float(s)
def path_points(d):
    toks = re.findall(r"[MLAZ]|-?\d+(?:\.\d+)?", d); pts = []; i = 0
    while i < len(toks):
        c = toks[i]
        if c in "ML": pts.append((num(toks[i + 1]), num(toks[i + 2]))); i += 3
        elif c == "A": pts.append((num(toks[i + 6]), num(toks[i + 7]))); i += 8; pts.append(None)   # None: the arc bulges, its extreme is checked through the radius below
        else: i += 1
    return [p for p in pts if p]
def attrs(tag): return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
for fid in PLACE:
    for svg in re.findall(r"<svg .*?</svg>", F[fid], re.S):
        h = attrs(re.match(r"<svg [^>]*>", svg).group(0)); vb = [num(v) for v in h["viewBox"].split()]; W, Hh = vb[2], vb[3]
        check(h.get("role") == "img" and len(h.get("aria-label", "")) > 30, fid, "panel without a label")
        def inside(x, y, what): check(-1 <= x <= W + 1 and -1 <= y <= Hh + 1, fid, what, round(x, 1), round(y, 1), "outside", (W, Hh))
        for tag in re.findall(r"<(?:line|rect|circle|path|text)\b[^>]*>", svg):
            a = attrs(tag)
            if tag.startswith("<line"): inside(num(a["x1"]), num(a["y1"]), "line"); inside(num(a["x2"]), num(a["y2"]), "line")
            elif tag.startswith("<rect"): inside(num(a["x"]), num(a["y"]), "rect"); inside(num(a["x"]) + num(a["width"]), num(a["y"]) + num(a["height"]), "rect")
            elif tag.startswith("<circle"): r = num(a["r"]); inside(num(a["cx"]) - r, num(a["cy"]) - r, "circle"); inside(num(a["cx"]) + r, num(a["cy"]) + r, "circle")
            elif tag.startswith("<path"):
                for x, y in path_points(a["d"]): inside(x, y, "path")
            elif tag.startswith("<text"): inside(num(a["x"]), num(a["y"]), "text anchor")
        for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)" text-anchor="(\w+)"[^>]*>([^<]*)</text>', svg):         # a label must not run out of the panel: about 0.55 em per character
            x, y, anc, s = float(m.group(1)), float(m.group(2)), m.group(3), m.group(4); wd = 0.58 * 13 * len(s)
            lo, hi = {"start": (x, x + wd), "middle": (x - wd / 2, x + wd / 2), "end": (x - wd, x)}[anc]
            check(lo >= -1 and hi <= W + 1, fid, "label may run out of the panel", s, round(lo), round(hi), W)

# ---- leaf ends: the band that crosses only part of an end, by a second method (sampling rays and the thickness each crosses)
E = figs.MLC_END; ys, y1, y2 = E["ys"], E["y1"], E["y2"]; ym = (y1 + y2) / 2; R = E["R"]
def band_by_sampling(design, side, e):
    kx = lambda y: (y - ys) / (y1 - ys); yy = [y1 + (y2 - y1) * i / 700 for i in range(701)]
    def inside_leaf(x, y):                                                                  # is the point (lateral offset x at height y) inside the leaf?
        if design == "straight": face = e
        elif design == "divergent": face = e * kx(y)
        else:
            em = e * kx(ym); cx = em - R if side < 0 else em + R; r2 = R * R - (y - ym) ** 2
            face = cx + math.sqrt(r2) if side < 0 else cx - math.sqrt(r2)
        return x <= face if side < 0 else x >= face
    step = 0.005; partial = 0; t0 = -80.0
    while t0 <= 100.0:
        f = sum(inside_leaf(t0 * kx(y), y) for y in yy) / len(yy)
        if 0 < f < 1: partial += 1
        t0 += step
    return partial * step
B = figs.mlc_end_bands()
for d in ("straight", "divergent", "rounded"):
    for side, e in E["edges"].items():
        check(abs(band_by_sampling(d, side, e) - B[d][side]) < 0.05, d, side, "band by sampling", round(band_by_sampling(d, side, e), 3), "against", round(B[d][side], 3))
for side, e in E["edges"].items():
    check(abs(B["straight"][side] - abs(e) * (y2 - y1) / (y2 - ys)) < 1e-6, "straight end band is |e| (y2 - y1) / (y2 - ys)", side)
    check(B["divergent"][side] < 1e-6, "a divergent end leaves no partly crossing band", side)
check(B["straight"][1] > 3 * B["straight"][-1], "straight end: wide far from the axis, narrow near it", B["straight"])
check(B["rounded"][1] < 1.5 * B["rounded"][-1], "rounded end: nearly the same width at both positions", B["rounded"])
check(min(B["rounded"].values()) > max(B["straight"].values()), "a rounded end gives a wider band than a straight end", B)

# ---- leaf gap: the dashed opening has the area of the fluence above the leaf transmission, and its width is g plus the sum of the two rounded ends
panels = re.findall(r"<svg .*?</svg>", F["mlc_dlg"], re.S)
widths = []
for svg in panels:
    prof = [a for a in re.findall(r"<path [^>]*>", svg) if 'stroke="var(--c1)"' in a][0]; pts = path_points(attrs(prof)["d"])
    dash = [attrs(r) for r in re.findall(r"<rect [^>]*>", svg) if 'stroke="var(--c2)"' in r][0]
    floor = pts[0][1]; area = sum((pts[i + 1][0] - pts[i][0]) * ((floor - pts[i][1]) + (floor - pts[i + 1][1])) / 2 for i in range(len(pts) - 1))
    check(abs(area - num(dash["width"]) * num(dash["height"])) < 0.01 * area, "equal area of the profile and the dashed opening", round(area, 1), round(num(dash["width"]) * num(dash["height"]), 1))
    widths.append(num(dash["width"]))
    tips = [p[0] for p in pts if abs(p[1] - min(q[1] for q in pts)) < 1e-6]; plateau = max(tips) - min(tips)       # the width at full fluence is the nominal gap g
    foot = [p[0] for p in pts if abs(p[1] - floor) < 1e-6 and p != pts[0] and p != pts[-1]]; ext = (max(foot) - min(foot) - plateau) / 2   # each rounded end ramps over its lateral extent
    check(abs(num(dash["width"]) - plateau - ext) < 1e-6, "dashed opening = g + (sum of the two ramps) / 2", num(dash["width"]), plateau, ext)
check(widths[1] > widths[0], "the opening with a gap is wider than the closed one", widths)

# ---- tongue and groove: no straight path through the joint, and neighbouring leaves do not overlap
svg = re.findall(r"<svg .*?</svg>", F["mlc_tg"], re.S)[0]
polys = [path_points(attrs(t)["d"]) for t in re.findall(r"<path [^>]*>", svg) if 'fill="var(--gr)"' in t]
check(len(polys) == 3, "three leaves in the end view", len(polys))
def inpoly(x, y, P):
    c = False
    for i in range(len(P)):
        (x1, y1_), (x2, y2_) = P[i], P[(i + 1) % len(P)]
        if (y1_ > y) != (y2_ > y) and x < (x2 - x1) * (y - y1_) / (y2_ - y1_) + x1: c = not c
    return c
ytop = min(p[1] for p in polys[0]); ybot = max(p[1] for p in polys[0]); xs0 = min(p[0] for p in polys[0]); xs1 = max(p[0] for p in polys[2])
overlap = open_cols = 0
for xi in range(int(xs0 * 2) + 1, int(xs1 * 2)):
    x = xi / 2 + 0.01
    col = [sum(inpoly(x, ytop + 0.37 + k * 0.5, P) for P in polys) for k in range(int((ybot - ytop - 0.74) / 0.5))]
    if any(c > 1 for c in col): overlap += 1
    if not any(c >= 1 for c in col): open_cols += 1
check(overlap == 0, "leaves overlap", overlap); check(open_cols == 0, "a straight path through the joint", open_cols)
for P in polys: check(len({round(p[0] - polys[0][0][0] - (P[0][0] - polys[0][0][0]), 3) for p in P}) > 1, "leaf polygon is not degenerate")

for b in bad: print("FAIL", b)
print(f"mlcfigs: {n} checks"); print("mlcfigs: PASS" if not bad else f"mlcfigs: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
