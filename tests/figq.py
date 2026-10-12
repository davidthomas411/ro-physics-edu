"""Tap-the-figure questions: each correct region is re-derived from the physics and from the plotted curve, then tap, touch, keyboard, persistence, and layout are tested."""
import sys, re, math, os, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
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
p = fig("Tap the depth of dmax"); s = p["spec"]["series"][0]["pts"]
check(inside(p, argmax(s)) and abs(argmax(s) - 1.5) < 0.06 and not any(inside(p, w) for w in (0.3, 3.0, 5.0)) and width(p) <= 1.01, f"PDD d_max: the plotted curve peaks at {argmax(s):.2f} cm; target {p['targets'][0][:2]}")
p = fig("leaves one eighth of the beam"); x = 3 * math.log(2) / 0.2; s = p["spec"]["series"][0]["pts"]
check(inside(p, x) and abs(crossing(s, 12.5) - x) < 0.1 and not inside(p, 3.47) and not inside(p, 7.0) and not inside(p, 11.51), f"one eighth: 3 HVL = {x:.2f} cm, the plotted curve reaches 12.5% at {crossing(s, 12.5):.2f} cm, and the TVL (11.5 cm) is rejected")
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
    p = fig("leaves one eighth of the beam"); c, q = open_q(pg, plain(p["q"])[:60])
    if q.evaluate("el=>el.classList.contains('done')"): q.locator(".again").click()
    q.locator("svg").scroll_into_view_if_needed()
    pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [2, 60]); pg.mouse.click(pos[0], pos[1]); q.locator(".chk").click()
    check(q.locator(".res").inner_text().startswith("Not quite") and q.locator(".mk.wrong").count() == 1 and q.locator(".tgt").count() == 1, "a wrong tap says so, marks the tap, and shades the correct region")
    pg.reload(); pg.wait_for_timeout(250); q = pg.locator(f'.pq[data-id="{c}"]'); check(q.evaluate("el=>el.classList.contains('done')") and q.locator(".res").inner_text().startswith("Not quite") and pg.evaluate("id=>!!qSel(id)", c), "the tap is saved and the result restored after a reload")
    q.locator(".again").click(); check(q.locator(".tgt").count() == 0 and q.locator(".chk").is_disabled() and pg.evaluate("id=>!qSel(id)", c), "Try again clears the tap, the shading, and the saved answer")
    q.locator("svg").focus(); pg.keyboard.press("ArrowRight"); check(q.locator(".chk").is_enabled() and q.evaluate("el=>el._fig.marker()!==null"), "keyboard: an arrow key places the marker and enables Check")
    m0 = q.evaluate("el=>el._fig.marker()[0]"); [pg.keyboard.press("ArrowRight") for _ in range(5)]; m1 = q.evaluate("el=>el._fig.marker()[0]"); pg.keyboard.press("Shift+ArrowLeft"); m2 = q.evaluate("el=>el._fig.marker()[0]")
    check(m1 > m0 and m2 < m1, f"keyboard: arrows move the marker, Shift moves it further ({m0:.1f} -> {m1:.1f} -> {m2:.1f})")
    # a moved marker is scored where it is, not where it started
    pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [2, 50]); pg.mouse.click(pos[0], pos[1]); pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [10.4, 50]); pg.mouse.click(pos[0], pos[1]); q.locator(".chk").click()
    check(q.locator(".res").inner_text() == "Correct.", "tapping again moves the marker: the last tap is the one scored")
    check(not errs, f"no page errors on desktop {errs[:2]}")
    # phone: touch taps and layout
    mc = b.new_context(viewport={"width": 390, "height": 844}, color_scheme="light", has_touch=True, is_mobile=True); mp = mc.new_page(); merrs = []; mp.on("pageerror", lambda e: merrs.append(str(e)))
    p = fig("leaves one eighth of the beam"); c, q = open_q(mp, plain(p["q"])[:50]); x, y = centre(p); sb = q.locator("svg").bounding_box(); pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", [x, y])
    q.locator("svg").tap(position={"x": pos[0] - sb["x"], "y": pos[1] - sb["y"]}); mp.wait_for_timeout(80); q.locator(".chk").tap(); check(q.locator(".res").inner_text() == "Correct." and "You tapped" in q.locator(".tapped").inner_text(), f"phone: a touch tap on the N-15 square is correct and reported as '{q.locator('.tapped').inner_text()}'")
    for tid in ("pdd", "photon-interactions", "profiles", "dvh-metrics", "tg43"):
        mp.goto(U + "#ref"); mp.goto(U + "#t/" + tid); mp.wait_for_timeout(200)
        w = mp.evaluate("[document.documentElement.scrollWidth, innerWidth, Math.max(0,...[...document.querySelectorAll('.pq.figq')].map(e=>e.scrollWidth-e.clientWidth))]"); check(w[0] <= w[1] and w[2] <= 0, f"{tid}: no sideways scroll at 390 px, figure cards fit {w}")
    check(not merrs, f"no page errors on the phone {merrs[:2]}"); b.close()
print(f"figq: {n} checks"); print("figq: PASS" if not bad else f"figq: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
