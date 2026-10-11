"""The data-table questions: read each table as printed in the question, apply the stated procedure with independent code, and require the marked-correct option to match.
Also checks that the illustrative 6 MV data set is physically consistent and that its PDD and TMR tables agree through the conversion formula."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import beamdata
BY = {t["id"]: t for t in TOPICS}
plain = lambda s: re.sub(r"<[^>]+>", "", s)
fails = []; n = 0
def check(name, got, want, tol=1e-6):
    global n; n += 1
    if abs(got - want) > tol * max(abs(want), 1e-12): fails.append(f"{name}: got {got!r}, independent {want!r}")
def tables_in(html):
    """Every data table in a stem as {caption, cols, rows}, parsed from the printed HTML."""
    out = []
    for m in re.finditer(r'<div class="dt"><div class="dtc">(.*?)</div><div class="tblwrap"><table><thead><tr>(.*?)</tr></thead><tbody>(.*?)</tbody>', html, re.S):
        head = [plain(x) for x in re.findall(r"<th>(.*?)</th>", m.group(2))]
        rows = {}
        for lab, cells in re.findall(r'<tr><th scope="row">(.*?)</th>(.*?)</tr>', m.group(3), re.S):
            rows[float(re.match(r"[\d.]+", plain(lab)).group(0))] = [float(c) for c in re.findall(r"<td>(.*?)</td>", cells)]
        out.append(dict(cap=plain(m.group(1)), cols=[float(re.match(r"[\d.]+", h).group(0)) if re.match(r"[\d.]+", h) else h for h in head[1:]], rows=rows))
    return out
def tab(html, key): return [t for t in tables_in(html) if key in t["cap"]][0]
def col(t, size): j = t["cols"].index(size); return {d: r[j] for d, r in t["rows"].items()}
def lin(x, pts):
    pts = sorted(pts)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError((x, pts))
def find(tid, phrase):
    hits = [p for p in BY[tid]["problems"] if plain(phrase) in plain(p["q"])]; assert len(hits) == 1, (tid, phrase, len(hits)); return hits[0]
def right(p): i = "ABCDEFG".index(re.search(r"<b>([A-G])\.", p["a"][0]).group(1)); return p["vals"][i]
def scatter(html):
    t = tab(html, "scatter"); sc = {k: v for k, v in zip([r for r in t["rows"]], [x[0] for x in t["rows"].values()])}; sp = {k: x[1] for k, x in t["rows"].items()}; return sc, sp
# ---------------------------------------------------------------- the data set
D = beamdata
SC, SP = dict(D.SC), dict(D.SP); ks = sorted(SC)
check("Sc(10) = 1", SC[10], 1.0); check("Sp(10) = 1", SP[10], 1.0)
for name, T in (("Sc", SC), ("Sp", SP)):
    n += 1
    if any(T[a] >= T[b] for a, b in zip(ks, ks[1:])): fails.append(f"{name} is not increasing with field size")
for s in D.SIZES:
    check(f"TMR at d_max, {s} cm", D.TMR[(1.5, s)], 1.0); check(f"PDD at d_max, {s} cm", D.PDD[(1.5, s)], 100.0)
    for d0, d1 in zip(D.TMR_DEPTHS, D.TMR_DEPTHS[1:]):
        n += 1
        if D.TMR[(d1, s)] >= D.TMR[(d0, s)]: fails.append(f"TMR does not fall with depth at {s} cm, {d0} to {d1}")
    for d0, d1 in zip(D.PDD_DEPTHS, D.PDD_DEPTHS[1:]):
        n += 1
        if D.PDD[(d1, s)] >= D.PDD[(d0, s)]: fails.append(f"PDD does not fall with depth at {s} cm, {d0} to {d1}")
for d in D.TMR_DEPTHS[1:]:
    n += 1
    if any(D.TMR[(d, a)] > D.TMR[(d, b)] for a, b in zip(D.SIZES, D.SIZES[1:])): fails.append(f"TMR does not rise with field size at {d} cm")
for d in D.PDD_DEPTHS[1:]:
    n += 1
    if any(D.PDD[(d, a)] > D.PDD[(d, b)] for a, b in zip(D.SIZES, D.SIZES[1:])): fails.append(f"PDD does not rise with field size at {d} cm")
n += 1
if not 64 <= D.PDD[(10, 10)] <= 70: fails.append(f"PDD(10 cm, 10 x 10) = {D.PDD[(10, 10)]} is not a 6 MV value")
n += 1
if not 0.77 <= D.TMR[(10, 10)] <= 0.80: fails.append(f"TMR(10 cm, 10 x 10) = {D.TMR[(10, 10)]} is not a 6 MV value")
# PDD <-> TMR through the conversion formula in the TMR chapter, using only the printed tables and linear interpolation
tmr_cols = {s: [(d, D.TMR[(d, s)]) for d in D.TMR_DEPTHS] for s in D.SIZES}
def tmr_printed(d, s):
    rows = {dd: lin(s, [(k, D.TMR[(dd, k)]) for k in D.SIZES]) for dd in D.TMR_DEPTHS}; return lin(d, list(rows.items()))
worst = 0.0
for s in D.SIZES:
    for d in D.PDD_DEPTHS[1:]:
        ad, am = s * (100 + d) / 100, s * (100 + 1.5) / 100
        sp_d, sp_m = lin(ad, [(k, SP[k]) for k in ks]), lin(am, [(k, SP[k]) for k in ks])
        t_est = D.PDD[(d, s)] / 100 * ((100 + d) / 101.5) ** 2 * sp_m / sp_d
        if ad <= 30: worst = max(worst, abs(t_est - tmr_printed(d, ad)))
n += 1
if worst > 0.004: fails.append(f"printed PDD and TMR disagree through the conversion formula by up to {worst:.4f}")
print(f"data set: PDD and TMR tables agree through the conversion formula to within {worst:.4f}")
# ---------------------------------------------------------------- the questions
p = find("pdd", "PDD at 9 cm depth"); t = tab(p["q"], "percent depth dose"); c = col(t, 10.0); check("PDD at 9 cm by interpolation", right(p), lin(9, list(c.items())), 1e-9)
p = [x for x in BY["pdd"]["problems"] if "180 cGy at 12 cm depth" in plain(x["q"])][0]; c = col(tab(p["q"], "percent depth dose"), 15.0); check("dose at dmax from the PDD table", right(p), 180 / (c[12.0] / 100), 1e-9)
p = find("pdd", "fall to 50%"); c = col(tab(p["q"], "percent depth dose"), 10.0); its = sorted(c.items()); (d0, v0), (d1, v1) = next((x, y) for x, y in zip(its, its[1:]) if x[1] >= 50 > y[1]); check("depth of the 50% PDD", right(p), d0 + (v0 - 50) / (v0 - v1) * (d1 - d0), 1e-9)
p = find("tmr", "10 cm setup to the 20 cm setup"); c = col(tab(p["q"], "TMR"), 10.0); check("dose change from the TMR ratio", right(p), c[20.0] / c[10.0] - 1, 1e-9)
p = find("tmr", "TMR equal to 0.600"); c = col(tab(p["q"], "TMR"), 10.0); its = sorted(c.items()); (d0, v0), (d1, v1) = next((x, y) for x, y in zip(its, its[1:]) if x[1] >= 0.6 > y[1]); check("depth where TMR = 0.600", right(p), d0 + (v0 - 0.6) / (v0 - v1) * (d1 - d0), 1e-9)
p = find("scatter", "open rectangular field of 10 × 20 cm"); sc, sp = scatter(p["q"]); es = 2 * 10 * 20 / (10 + 20)
check("Scp of 10 x 20 from the table", right(p), lin(es, list(sc.items())) * lin(es, list(sp.items())), 1e-9)
p = find("scatter", "equivalent square of 8 × 8 cm"); sc, sp = scatter(p["q"]); check("Scp of the blocked field", right(p), sc[15.0] * sp[8.0], 1e-9)
p = find("scatter", "open rectangular field of 5 × 20 cm"); sc, sp = scatter(p["q"]); es = 2 * 5 * 20 / 25; check("Scp of 5 x 20 from the table", right(p), sc[es] * sp[es], 1e-9)
p = find("mu-calc", "250 cGy at 8 cm depth"); sc, sp = scatter(p["q"]); pdd = col(tab(p["q"], "percent depth dose"), 20.0); check("MU, SSD technique from tables", right(p), 250 / (sc[20.0] * sp[20.0] * pdd[8.0] / 100), 1e-9)
p = find("mu-calc", "patient separation = 28 cm"); sc, sp = scatter(p["q"]); tm = col(tab(p["q"], "TMR"), 15.0); check("MU per field, SAD pair with SSD calibration, from tables", right(p), 100 / (sc[15.0] * sp[15.0] * tm[14.0] * (101.5 / 100) ** 2), 1e-9)
p = find("mu-calc", "Only the SSD 100 PDD is tabulated"); sc, sp = scatter(p["q"]); pdd = col(tab(p["q"], "percent depth dose"), 15.0)[10.0]
f = lambda ssd, x: 1 / (ssd + x) ** 2
F = (f(120, 10) / f(120, 1.5)) / (f(100, 10) / f(100, 1.5)); sc125 = lin(12.5, list(sc.items())); iv = f(120, 1.5) / f(100, 1.5)
check("MU, extended SSD from tables", right(p), 200 / (sc125 * sp[15.0] * pdd * F / 100 * iv), 1e-9)
hits = [x for x in BY["mu-calc"]["problems"] if "SAD calibration" in plain(x["q"]) and "200 cGy at 12 cm depth" in plain(x["q"])]; assert len(hits) == 1; p = hits[0]
sc, sp = scatter(p["q"]); pdd = col(tab(p["q"], "percent depth dose"), 15.0)[12.0]; check("MU, SSD technique on a SAD-calibrated machine, from tables", right(p), 200 / (sc[15.0] * sp[15.0] * pdd / 100 * (100 / 101.5) ** 2), 1e-9)
p = find("mu-calc", "wedge factor = 0.71"); sc, sp = scatter(p["q"]); tm = col(tab(p["q"], "TMR"), 15.0); check("MU, wedge and tray from tables", right(p), 120 / (sc[15.0] * sp[15.0] * tm[10.0] * 0.71 * 0.97), 1e-9)
# every table printed in a question is a faithful copy of the data set
for t in TOPICS:
    for q in t["problems"]:
        for tb in tables_in(q["q"]):
            for d, row in tb["rows"].items():
                for s, v in zip(tb["cols"], row):
                    n += 1
                    if "TMR" in tb["cap"]: ok = D.TMR[(d if d != 1.5 else 1.5, int(s))] == v
                    elif "percent depth dose" in tb["cap"]: ok = D.PDD[(d, int(s))] == v
                    else: ok = None
                    if ok is False: fails.append(f"{t['id']}: a printed table value {v} at depth {d}, size {s} differs from the data set")
print(f"numbers4: {n} checks")
for x in fails: print("FAIL", x)
print("numbers4: PASS" if not fails else f"numbers4: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
