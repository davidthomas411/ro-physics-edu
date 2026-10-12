"""Linac QA chapter (qa-linac): every worked number and keyed answer re-derived by another route.
Gap errors come from a simulated sweep of the two leaves, gamma from a bisection on the ellipse of the criteria, passing rates from counting
a list of points, and tolerance limits from a bisection on the deviation. The quoted TG-142 and TG-218 values are checked for agreement
between the table, the cards, the take-aways, and the questions."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import qa_linac as Q
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}["qa-linac"]; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def true(c, what):
    global n; n += 1
    if not c: bad.append((what, "not true", ""))
def prob(phrase):
    hits = [p for p in T["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                   # the number behind the keyed option, or the typed answer
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def ex(title): return next(b for b in T["guide"] if b[0] == "ex" and b[1] == title)
def ex_text(title): b = ex(title); return plain(" ".join([b[2], *b[3], b[4]]))
num = lambda s: [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]

# ---- sliding window: time a point spends between the two leaves, by stepping the leaves across it
def sweep(gap, lead_off=0.0, trail_off=0.0, x0=20.0, v=10.0, dt=1e-5):
    """Seconds that the point x0 (mm) is open while a gap of nominal width gap (mm) sweeps at v (mm/s), and the time it opens.
    lead_off moves the leading bank and trail_off the trailing bank (mm)."""
    t, end, open_t, first = (x0 - gap - 5) / v, (x0 + 5) / v + gap / v, 0.0, None
    while t < end:
        lead, trail = v * (t + dt / 2) + lead_off, v * (t + dt / 2) - gap + trail_off
        if trail < x0 < lead:
            open_t += dt
            if first is None: first = t
        t += dt
    return open_t, first
def change(gap, lead_off=0.0, trail_off=0.0):
    """Percent change of the dose at a point when the banks are offset, from the simulated open times."""
    return 100 * (sweep(gap, lead_off, trail_off)[0] / sweep(gap)[0] - 1)

# worked example: a 5 mm effective gap, one bank 1 mm open, and both banks shifted 1 mm
close(change(5.0, lead_off=1.0), Q.ex_gap, 2e-3, "one bank opening a 5 mm gap by 1 mm raises the dose 20%"); close(Q.ex_gap, 20.0, 1e-9, "20%")
o0, f0 = sweep(5.0); o1, f1 = sweep(5.0, 1.0, 1.0)
close(o1 / o0, 1.0, 1e-4, "both banks shifted the same way: no change in dose"); close((f0 - f1) * 10.0, 1.0, 1e-3, "and the pattern moves 1 mm")
txt = ex_text("Leaf bank error"); true("+20%" in txt and "6 mm" in txt and "1.20" in txt, "the worked example prints 6 mm, 1.20, and +20%")
# question: nominal 8.5 mm plus a 1.5 mm leaf gap, one bank opens 0.5 mm
p = prob("By what percentage does the dose through the gap change")
close(value(p), change(10.0, lead_off=0.5), 2e-3, "keyed 5.0% from the sweep of a 10 mm effective gap")
close(Q.s_nodlg, change(8.5, lead_off=0.5), 2e-3, "distractor: the gap without the dosimetric leaf gap"); close(Q.s_both, change(10.0, 0.5, -0.5), 2e-3, "distractor: both banks opening")
true(0.0 in p["vals"] and abs(change(10.0, 0.5, 0.5)) < 1e-2, "distractor 0%: the change when the error is a shift of both banks")
# question: both banks displaced 0.5 mm in a 5 mm gap
p = prob("QA finds both leaf banks displaced")
close(Q.b_one, change(5.0, lead_off=0.5), 2e-3, "one bank 0.5 mm in a 5 mm gap: 10%"); close(Q.b_two, change(5.0, 0.5, -0.5), 2e-3, "both banks opening: 20%")
true(keyed(p).startswith("The same dose") and abs(change(5.0, 0.5, 0.5)) < 1e-2, "the keyed answer is no change in dose")
true(sorted(num(" ".join(plain(o) for o in p["opts"]))) == sorted([0.5, round(Q.b_one), round(Q.b_two), round(Q.b_one)]), "the options print 0.5 mm, 10%, 20%, and 10%")
# ---- gamma: the scale s at which a measured-calculated pair lies on the ellipse of the criteria
def gam(r, d, dta, dd):
    return bisect(lambda s: (r / (s * dta)) ** 2 + (d / (s * dd)) ** 2 - 1, 1e-6, 100.0) if (r or d) else 0.0
gA, gB = gam(0.0, 4.2, 2, 3), gam(1.2, 1.5, 2, 3)
close(Q.gA, gA, 1e-9, "worked example: point A, 4.2% at 0 mm"); close(Q.gB, gB, 1e-9, "point B, 1.5% at 1.2 mm"); close(Q.g_ex, min(gA, gB), 1e-9, "γ is the smaller")
txt = ex_text("Gamma at one point"); true(f"{gA:.2f}" in txt and f"{gB:.2f}" in txt and "0.36" in txt and "0.25" in txt and gB <= 1 < gA, "the example prints 1.40 and 0.78; B passes and A alone would fail")
p = prob("is described below")
close(value(p), gam(1.0, 2.4, 2, 3), 1e-9, "keyed γ for 2.4% at 1.0 mm"); close(value(p), 0.9434, 1e-4, "0.94")
wrong = sorted(v for v in p["vals"] if v != value(p))
close(wrong[0], 1.0 / 2, 1e-12, "distance term alone"); close(wrong[1], 2.4 / 3, 1e-12, "dose term alone"); close(wrong[2], 0.25 + 0.64, 1e-12, "no square root"); close(wrong[3], 0.5 + 0.8, 1e-12, "the two ratios added")
# local against global, with doses in cGy: maximum 200 cGy, point 30 cGy, difference 2 cGy
dmax, dpt, ddiff = 200.0, 30.0, 2.0
close(Q.loc_gg, gam(0, 100 * ddiff / dmax, 2, 3), 1e-9, "global γ"); close(Q.loc_pct, 100 * ddiff / dpt, 1e-9, "local difference 6.7%"); close(Q.loc_gl, gam(0, 100 * ddiff / dpt, 2, 3), 1e-9, "local γ")
p = prob("How does the point fare"); true(keyed(p).startswith("It passes with global") and Q.loc_gg <= 1 < Q.loc_gl and dpt / dmax * 100 > Q.THR, "passes globally, fails locally, and lies above the threshold")

# ---- passing rates, by counting a list of points
def count(n_all, n_eval, n_fail):
    pts = [("low", 0.4)] * (n_all - n_eval) + [("eval", 1.6)] * n_fail + [("eval", 0.6)] * (n_eval - n_fail)
    ev = [g for k, g in pts if k == "eval"]; ok = sum(1 for g in ev if g <= 1)
    return 100 * ok / len(ev), 100 * ok / len(pts), 100 * sum(1 for k, g in pts if g <= 1) / len(pts), 100 * (len(ev) - ok) / len(ev)
r, r_all, r_low, r_fail = count(1386, 1240, 75)
close(Q.pr_ex, r, 1e-12, "worked example passing rate"); true(Q.AL <= r < Q.TL and f"{r:.1f}%" in ex_text("Passing rate and limits") and "146" in ex_text("Passing rate and limits") and "1,165" in ex_text("Passing rate and limits"), "94.0%: between the action and tolerance limits; 146 excluded, 1,165 passing")
r, r_all, r_low, r_fail = count(1386, 1108, 50)
p = prob("What is the passing rate")
close(value(p), r, 1e-12, "keyed passing rate"); true(r >= Q.TL, "95.5% passes the tolerance limit")
close(Q.n_all_den, r_all, 1e-12, "distractor: every diode in the denominator"); close(Q.n_low_pass, r_low, 1e-12, "distractor: low-dose diodes counted as passing"); close(Q.n_failpct, r_fail, 1e-12, "distractor: the failing fraction")
true(r_all < Q.AL, "the wrong denominator would put the plan below the action limit")

# ---- output constancy: deviation as a ratio, and the limit by bisection
close(Q.ex_d6, (1.013 / 1.000 - 1) * 100, 1e-9, "6 MV +1.3%"); close(Q.ex_d10, (0.977 / 1.000 - 1) * 100, 1e-9, "10 MV −2.3%")
true(abs(Q.ex_d6) <= Q.OUT_M < abs(Q.ex_d10) and "+1.3%" in ex_text("Monthly output check") and "−2.3%" in ex_text("Monthly output check"), "6 MV passes and 10 MV fails the 2% monthly tolerance")
hi = bisect(lambda m: (m / 60.0 - 1) * 100 - Q.OUT_D, 60.0, 70.0)
p = prob("highest reading"); close(value(p), hi, 1e-9, "highest daily reading within 3%"); close(value(p), 61.8, 1e-9, "61.8")
for t, v in ((Q.OUT_A, 60.6), (Q.OUT_M, 61.2)): close(bisect(lambda m: (m / 60.0 - 1) * 100 - t, 60.0, 70.0), v, 1e-9, f"limit at {t}%")
true(sorted(round(v, 9) for v in p["vals"]) == [60.6, 61.2, 61.8, 63.0], "the options are 60.6, 61.2, 61.8, and 63.0")
true(2.6 > Q.OUT_M and 2.6 < Q.OUT_D, "the monthly scenario at +2.6% is outside the monthly tolerance and inside the daily one")

# ---- the quoted tolerances agree everywhere they appear
rows = {r[0]: r for r in Q.TG142}
freq = dict(zip(rows["Photon output"][1].split("; "), (float(x.rstrip("%")) for x in rows["Photon output"][2].split("; "))))
true(freq == {"Daily": 3.0, "monthly": 2.0, "annual": 1.0} and rows["Backup monitor chamber constancy"][1:] == ["Monthly", "2%"], "table: output 3% daily, 2% monthly, 1% annual; backup monitor 2% monthly")
close(value(prob("daily photon output constancy check")), freq["Daily"], 0, "the keyed daily tolerance is the table value")
true(rows["Lasers"][2] == "2 mm; IMRT 1.5 mm; SRS/SBRT 1 mm" and keyed(prob("Which daily laser tolerance")).startswith("1 mm"), "lasers: 2, 1.5, and 1 mm, and the SRS value is keyed")
true(rows["MLC leaf position (IMRT)"][2].startswith("1 mm;") and 1.5 > Q.MLC, "the 1.5 mm picket-fence offset exceeds the 1 mm leaf tolerance")
cards = {plain(c["q"]): plain(" ".join(c["a"])) for c in T["cards"]}
true(cards["TG-142 photon output tolerances"].startswith("3% daily, 2% monthly, and 1%"), "the output card matches the table")
true(cards["TG-142 daily laser tolerance"].startswith("2 mm for a conventional machine, 1.5 mm for IMRT, and 1 mm"), "the laser card matches the table")
true("tolerance limit 95%" in cards["TG-218 universal limits"] and "action limit 90%" in cards["TG-218 universal limits"] and "3%/2 mm" in cards["TG-218 universal limits"], "the TG-218 card")
take = " ".join(plain(x) for sec in Q.TAKE for x in sec)
true("3% daily and 2% monthly; annual calibration 1%" in take and "tolerance limit 95%, action limit 90%" in take and "Lasers 2 mm daily (1 mm for SRS/SBRT)" in take, "the take-aways quote the same values")
guide = " ".join(plain(b[1]) for b in T["guide"] if b[0] == "p")
true("tolerance limit of 95%" in guide and "action limit of 90%" in guide and "3% and 2 mm" in guide and "10% of the maximum" in guide, "the text quotes the TG-218 values")

for b in bad: print("FAIL", b)
print(f"numbers_qa_linac: {n} numbers re-derived"); print("numbers_qa_linac: PASS" if not bad else f"numbers_qa_linac: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
