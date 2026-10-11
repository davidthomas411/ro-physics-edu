"""Tap-the-figure questions: each correct region is re-derived from the physics and from the plotted curve, then tap, touch, keyboard, persistence, and layout are tested."""
import sys, re, math, os, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
from playwright.sync_api import sync_playwright
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
FIGS = [(t["id"], p) for t in TOPICS for p in t["problems"] if p.get("kind") == "fig"]
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
def fig(phrase):
    h = [p for i, p in FIGS if phrase in plain(p["q"])]; assert len(h) == 1, (phrase, len(h)); return h[0]
def inside(p, x, y=None):
    return any((t[0] is None or x >= t[0]) and (t[1] is None or x <= t[1]) and (y is None or ((t[2] is None or y >= t[2]) and (t[3] is None or y <= t[3]))) for t in p["targets"])
def crossing(pts, level):                                                      # x where the plotted curve first reaches this y, by linear interpolation
    for (a, b), (c, d) in zip(pts, pts[1:]):
        if (b - level) * (d - level) <= 0 and b != d: return a + (c - a) * (level - b) / (d - b)
def argmax(pts): return max(pts, key=lambda q: q[1])[0]
def width(p): return min((t[1] - t[0]) for t in p["targets"] if t[0] is not None)
# ---------------------------------------------------------------- independent answers
p = fig("its activity has fallen to 25%"); s = p["spec"]["series"][0]["pts"]; x = 2 * 59.4
check(inside(p, x) and abs(crossing(s, 25) - x) < 0.5 and not any(inside(p, w) for w in (59.4, 89.1, 178.2, 30)), f"I-125 at 25%: two half-lives = {x:.1f} d, read off the plotted curve {crossing(s, 25):.1f} d")
p = fig("mean life"); s = p["spec"]["series"][0]["pts"]; x = 59.4 / math.log(2)
check(inside(p, x) and abs(crossing(s, 100 / math.e) - x) < 0.5 and not any(inside(p, w) for w in (59.4, 118.8)), f"I-125 mean life: 1.44 T1/2 = {x:.1f} d, where the curve reaches 1/e ({crossing(s, 100 / math.e):.1f} d); half-life and 2 half-lives are rejected")
p = fig("Tap the depth of dmax"); s = p["spec"]["series"][0]["pts"]
check(inside(p, argmax(s)) and abs(argmax(s) - 1.5) < 0.06 and not any(inside(p, w) for w in (0.3, 3.0, 5.0)) and width(p) <= 1.01, f"PDD d_max: the plotted curve peaks at {argmax(s):.2f} cm; target {p['targets'][0][:2]}")
p = fig("PDD is 50%"); s = p["spec"]["series"][0]["pts"]; d50 = crossing(s[40:], 50)
check(inside(p, d50) and not any(inside(p, w) for w in (10, 20, 5)) and 15 < d50 < 17.5 and width(p) <= 2.5 and abs(sum(p["targets"][0][:2]) / 2 - d50) < 0.1, f"PDD 50% depth: the curve reaches 50% at {d50:.2f} cm; the target is centred on it")
p = fig("Tc-99m activity is greatest"); lp, ld = math.log(2) / 65.94, math.log(2) / 6.0067; f = lambda t: math.exp(-lp * t) - math.exp(-ld * t); a, b = 0.0, 200.0; g = (math.sqrt(5) - 1) / 2
for _ in range(200):
    c, d = b - g * (b - a), a + g * (b - a)
    if f(c) > f(d): b = d
    else: a = c
tm = (a + b) / 2; lp, ld = math.log(2) / 65.94, math.log(2) / 6.0067; tf = math.log(ld / lp) / (ld - lp)
check(inside(p, tm) and abs(tm - tf) < 0.05 and len(p["spec"]["series"]) == 1 and not any(inside(p, w) for w in (6, 48, 72, 120)), f"Tc-99m peak: maximum by search {tm:.2f} h, formula {tf:.2f} h, and only the Mo-99 curve is plotted")
p = fig("halves the beam"); x = math.log(2) / 0.2; s = p["spec"]["series"][0]["pts"]
check(inside(p, x) and abs(crossing(s, 50) - x) < 0.1 and not inside(p, 11.5) and not inside(p, 5.0), f"HVL: ln2/mu = {x:.2f} cm, the plotted curve reaches 50% at {crossing(s, 50):.2f} cm")
p = fig("leaves one eighth of the beam"); x = 3 * math.log(2) / 0.2; s = p["spec"]["series"][0]["pts"]
check(inside(p, x) and abs(crossing(s, 12.5) - x) < 0.1 and not inside(p, 3.47) and not inside(p, 7.0) and not inside(p, 11.51), f"one eighth: 3 HVL = {x:.2f} cm, the plotted curve reaches 12.5% at {crossing(s, 12.5):.2f} cm, and the TVL (11.5 cm) is rejected")
p = fig("Compton scattering dominates")
check(all(inside(p, e) for e in (0.1, 1, 6, 20)) and not any(inside(p, e) for e in (0.011, 0.02, 50, 90)), "Compton band in water: 30 keV to 24 MeV accepted, the photoelectric and pair regions rejected")
p = fig("threshold energy for pair production")
check(inside(p, 2 * 0.511) and not any(inside(p, e) for e in (0.511, 0.3, 2.5, 6, 24)), "pair-production threshold: 2 x 0.511 = 1.022 MeV accepted; 0.511, 2.5, and 24 MeV rejected")
p = fig("mean energy"); s = p["spec"]["series"][0]["pts"]; tot = sum(y for _, y in s); mean = sum(x * y for x, y in s) / tot; mode = argmax(s)
check(abs(mean - 1 / 3) < 0.006 and inside(p, mean) and not inside(p, mode) and not any(inside(p, w) for w in (0.6, 0.9)) and abs(mode - 0.2) < 0.01, f"beta spectrum: the plotted shape has mean {mean:.3f} (E_max/3) and peak {mode:.2f}; the peak is rejected as the mean")
cells = {(c[0], c[1]): c[2] for c in fig("isotone of C-14")["spec"]["cells"]}; Zc, Nc = 6, 8
iso = [k for k, v in cells.items() if k[1] == 7 and k[0] == Nc]; bar = [k for k, v in cells.items() if k[1] == 7 and k[0] + 7 == Zc + Nc]
p = fig("isotone of C-14"); q = fig("isobar of C-14")
check(iso == [(8, 7)] and cells[(8, 7)] == "N-15" and inside(p, 8, 7) and not any(inside(p, a, b) for (a, b) in cells if (a, b) != (8, 7)), "isotone of C-14 in the nitrogen row is N-15: same N = 8; every other square is rejected")
check(bar == [(7, 7)] and cells[(7, 7)] == "N-14" and inside(q, 7, 7) and not any(inside(q, a, b) for (a, b) in cells if (a, b) != (7, 7)), "isobar of C-14 in the nitrogen row is N-14: same A = 14; every other square is rejected")
check(all(cells[(nn, z)] == f"{'BCNO'[z - 5]}-{z + nn}" for (nn, z) in cells), "every square in the chart is labelled with its own element and mass number A = Z + N")
lin = [(i, p_) for i, p_ in FIGS if p_["spec"].get("cells") is None and p_["spec"]["x"].get("log") is not True]; share = {i + str(k): width(p_) / (p_["spec"]["x"]["max"] - p_["spec"]["x"]["min"]) for k, (i, p_) in enumerate(lin)}
check(all(v <= 0.18 for v in share.values()), f"every target on a linear axis is at most 18% of the axis, so the figure has to be read (widest {max(share.values()):.0%})")
# ---------------------------------------------------------------- browser
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
def qid(pg, phrase): return pg.evaluate("ph=>{const c=DATA.cards.find(c=>c.opts&&(c.q||'').replace(/<[^>]+>/g,'').includes(ph)); return c&&c.id}", phrase)
def open_q(pg, phrase):
    pg.goto(U + "#ref"); c = qid(pg, phrase); assert c, phrase; pg.goto(U + "#home"); pg.goto(U + "#t/" + c.split(":")[0]); pg.wait_for_timeout(250)
    q = pg.locator(f'.pq[data-id="{c}"]'); pg.evaluate("el=>{const r=el.querySelector('.fgb').getBoundingClientRect(); window.scrollTo(0, r.top+scrollY-140)}", q.element_handle()); pg.wait_for_timeout(80); return c, q
def uniq(p):                                                                     # the shortest prefix of the question text, at least 60 characters, that no other tap question shares
    s = plain(p["q"]); others = [plain(o["q"]) for _, o in FIGS if o is not p]; n = 60
    while n < len(s) and any(o.startswith(s[:n]) for o in others): n += 1
    return s[:n]
def centre(p):                                                                   # the middle of the first target, in data coordinates
    t = p["targets"][0]; S = p["spec"]; x0 = t[0] if t[0] is not None else S["x"]["min"]; x1 = t[1] if t[1] is not None else S["x"]["max"]
    xm = math.sqrt(x0 * x1) if S["x"].get("log") else (x0 + x1) / 2
    y0 = t[2] if t[2] is not None else S["y"]["min"]; y1 = t[3] if t[3] is not None else S["y"]["max"]; return xm, (y0 + y1) / 2
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    ctx = b.new_context(viewport={"width": 1100, "height": 900}, color_scheme="light"); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    for tid, p in FIGS:
        ph = uniq(p)
        c, q = open_q(pg, ph); x, y = centre(p); pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [x, y])
        pg.mouse.click(pos[0], pos[1]); pg.wait_for_timeout(60); q.locator(".chk").click(); res = q.locator(".res").inner_text()
        check(res == "Correct." and q.locator(".tgt").count() >= 1 and "You tapped" in q.locator(".tapped").inner_text(), f"{tid}: a tap in the middle of the target is correct, the region is shown, and the tap is reported ('{q.locator('.tapped').inner_text()}')")
    # one full cycle on a single question: wrong tap, try again, persistence, keyboard
    p = fig("its activity has fallen to 25%"); c, q = open_q(pg, plain(p["q"])[:60])
    if q.evaluate("el=>el.classList.contains('done')"): q.locator(".again").click()
    pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [30, 60]); pg.mouse.click(pos[0], pos[1]); q.locator(".chk").click()
    check(q.locator(".res").inner_text().startswith("Not quite") and q.locator(".mk.wrong").count() == 1 and q.locator(".tgt").count() == 1, "a wrong tap says so, marks the tap, and shades the correct region")
    pg.reload(); pg.wait_for_timeout(250); q = pg.locator(f'.pq[data-id="{c}"]'); check(q.evaluate("el=>el.classList.contains('done')") and q.locator(".res").inner_text().startswith("Not quite") and pg.evaluate("id=>!!qSel(id)", c), "the tap is saved and the result restored after a reload")
    q.locator(".again").click(); check(q.locator(".tgt").count() == 0 and q.locator(".chk").is_disabled() and pg.evaluate("id=>!qSel(id)", c), "Try again clears the tap, the shading, and the saved answer")
    q.locator("svg").focus(); pg.keyboard.press("ArrowRight"); check(q.locator(".chk").is_enabled() and q.evaluate("el=>el._fig.marker()!==null"), "keyboard: an arrow key places the marker and enables Check")
    m0 = q.evaluate("el=>el._fig.marker()[0]"); [pg.keyboard.press("ArrowRight") for _ in range(5)]; m1 = q.evaluate("el=>el._fig.marker()[0]"); pg.keyboard.press("Shift+ArrowLeft"); m2 = q.evaluate("el=>el._fig.marker()[0]")
    check(m1 > m0 and m2 < m1, f"keyboard: arrows move the marker, Shift moves it further ({m0:.1f} -> {m1:.1f} -> {m2:.1f})")
    # a moved marker is scored where it is, not where it started
    pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [10, 50]); pg.mouse.click(pos[0], pos[1]); pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [118.8, 50]); pg.mouse.click(pos[0], pos[1]); q.locator(".chk").click()
    check(q.locator(".res").inner_text() == "Correct.", "tapping again moves the marker: the last tap is the one scored")
    # a logarithmic axis maps decades evenly
    c, q = open_q(pg, "Compton scattering dominates"); pts = [q.evaluate("(el,v)=>el._fig.toClient(v,0.5).x", v) for v in (0.01, 1, 100)]
    check(abs((pts[0] + pts[2]) / 2 - pts[1]) < 1.0, f"log axis: 1 MeV sits exactly between 0.01 and 100 MeV ({pts[1]:.1f} vs {(pts[0] + pts[2]) / 2:.1f} px)")
    check(not errs, f"no page errors on desktop {errs[:2]}")
    # phone: touch taps and layout
    mc = b.new_context(viewport={"width": 390, "height": 844}, color_scheme="light", has_touch=True, is_mobile=True); mp = mc.new_page(); merrs = []; mp.on("pageerror", lambda e: merrs.append(str(e)))
    p = fig("isotone of C-14"); c, q = open_q(mp, plain(p["q"])[:50]); x, y = centre(p); sb = q.locator("svg").bounding_box(); pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [x, y])
    q.locator("svg").tap(position={"x": pos[0] - sb["x"], "y": pos[1] - sb["y"]}); mp.wait_for_timeout(80); q.locator(".chk").tap(); check(q.locator(".res").inner_text() == "Correct." and "N = 8, Z = 7" in q.locator(".tapped").inner_text(), f"phone: a touch tap on the N-15 square is correct and reported as '{q.locator('.tapped').inner_text()}'")
    cw = q.evaluate("el=>{const r=el._fig; const a=r.toClient(7.5,7.5), b2=r.toClient(8.5,6.5); return [b2.x-a.x, b2.y-a.y]}"); check(cw[0] >= 40 and cw[1] >= 40, f"phone: each nuclide square is at least 40 px across for a finger ({cw[0]:.0f} x {cw[1]:.0f})")
    for tid in ("decay-law", "equilibrium", "pdd", "photon-interactions", "decay-schemes", "nuclear-structure"):
        mp.goto(U + "#ref"); mp.goto(U + "#t/" + tid); mp.wait_for_timeout(200)
        w = mp.evaluate("[document.documentElement.scrollWidth, innerWidth, Math.max(0,...[...document.querySelectorAll('.pq.figq')].map(e=>e.scrollWidth-e.clientWidth))]"); check(w[0] <= w[1] and w[2] <= 0, f"{tid}: no sideways scroll at 390 px, figure cards fit {w}")
    check(not merrs, f"no page errors on the phone {merrs[:2]}"); b.close()
print(f"figq: {n} checks"); print("figq: PASS" if not bad else f"figq: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
