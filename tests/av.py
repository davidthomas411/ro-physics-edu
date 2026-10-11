"""Animated diagrams in the take-aways: they build, respond to their controls, move, respect reduced motion, and fit a phone."""
import os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ro-physics.html"
U = PAGE.resolve().as_uri(); fails, errors = [], []
IDS = ["wave-energy", "photon-origin", "intensity-energy", "ev-gain", "length-units", "matter-wave"]
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)
def fig(pg, i): return pg.locator(f'figure.av[data-av="{i}"]')
def finish(pg): pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av.finish())")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page()
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(U + "#ref"); pg.goto(U + "#t/waves-photons"); pg.wait_for_timeout(120)
    check(pg.locator("figure.av").count() == 6, "chapter 1.1 has six diagrams, one per take-away line")
    for i in IDS: check(fig(pg, i).locator("svg").count() == 1 and len(fig(pg, i).locator("figcaption").inner_text()) > 20, f"{i}: a drawing and a caption")
    f = fig(pg, "wave-energy"); f.scroll_into_view_if_needed(); d0 = f.locator("svg path").get_attribute("d"); pg.wait_for_timeout(600); d1 = f.locator("svg path").get_attribute("d")
    check(d0 != d1, "the wave moves when it scrolls into view")
    finish(pg); out = f.locator("output")
    check(all(x in out.inner_text() for x in ("25 keV", "0.0496 nm", "0.496 Å")), f"final state is the 25 keV example: {out.inner_text()!r}")
    bad = []
    for pos in (0, 25, 50, 75, 100):
        f.locator("input").evaluate(f"e=>{{e.value={pos};e.dispatchEvent(new Event('input'))}}"); t = out.inner_text()
        m = re.search(r"λ = 1240 / (\d+) = ([\d.]+) nm = ([\d.]+) Å", t)
        if not m or abs(float(m.group(1)) * float(m.group(2)) - 1240) > 0.02 * 1240 or abs(float(m.group(3)) - 10 * float(m.group(2))) > 0.01 * float(m.group(3)) + 1e-9: bad.append((pos, t))
    check(not bad, f"at five slider positions E × λ = 1240 eV·nm and 1 nm = 10 Å {bad}")
    f.locator("input").evaluate("e=>{e.value=0;e.dispatchEvent(new Event('input'))}"); check("1 keV" in out.inner_text() and "1.24 nm" in out.inner_text(), "slider at the low end: 1 keV, 1.24 nm")
    check(pg.locator("figure.av .btn:has-text('Replay')").count() == 4, "four diagrams have Replay; the slider and the voltage diagrams use their own controls")
    g = fig(pg, "ev-gain"); g.scroll_into_view_if_needed(); pg.wait_for_timeout(300); finish(pg)
    check("1.602 × 10⁻¹³ J" in g.inner_text(), "ev-gain final state: 1 MeV = 1.602 × 10⁻¹³ J")
    g.locator("button:has-text('1 kV')").click(); pg.wait_for_timeout(1700); check("gains 1 keV" in g.inner_text() and "1.602 × 10⁻¹⁶ J" in g.inner_text(), "1 kV gives 1 keV = 1.602 × 10⁻¹⁶ J")
    g.locator("button:has-text('1 V')").click(); pg.wait_for_timeout(1700); check("gains 1 eV" in g.inner_text() and "1.602 × 10⁻¹⁹ J" in g.inner_text(), "1 V gives 1 eV = 1.602 × 10⁻¹⁹ J")
    check(g.locator("button[aria-pressed='true']").count() == 1, "exactly one voltage button is pressed")
    h = fig(pg, "length-units"); h.scroll_into_view_if_needed(); finish(pg)
    vis = lambda: h.evaluate("f=>[...f.querySelectorAll('svg text')].filter(t=>t.style.display!=='none').map(t=>t.textContent)")
    check({"1 nm", "10 Å", "1000 pm"} <= set(vis()), f"length-units final state names all three units {vis()}")
    h.locator("button:has-text('Replay')").click(); pg.wait_for_timeout(250); early = vis()
    pg.wait_for_timeout(3700); check("1000 pm" not in early and "1000 pm" in vis(), "Replay restarts the sequence, and it ends complete")
    for i in ("photon-origin", "intensity-energy", "matter-wave"):
        x = fig(pg, i); x.scroll_into_view_if_needed(); x.locator("button:has-text('Replay')").click(); a = x.locator("svg").inner_html(); pg.wait_for_timeout(500)
        check(x.locator("svg").inner_html() != a, f"{i}: moves after Replay")
    # reduced motion: the final state shows at once, nothing moves, no Replay
    rc = b.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce"); rp = rc.new_page(); rp.on("pageerror", lambda e: errors.append(str(e)))
    rp.goto(U + "#ref"); rp.goto(U + "#t/waves-photons"); rp.wait_for_timeout(120); w = fig(rp, "wave-energy"); w.scroll_into_view_if_needed(); s0 = w.locator("svg path").get_attribute("d"); rp.wait_for_timeout(500)
    check("25 keV" in w.locator("output").inner_text() and w.locator("svg path").get_attribute("d") == s0, "reduced motion: static 25 keV state, nothing moves")
    check(rp.locator("figure.av .btn:has-text('Replay'):visible").count() == 0, "reduced motion: no Replay buttons")
    check("1.602 × 10⁻¹³ J" in fig(rp, "ev-gain").inner_text(), "reduced motion: the electron-volt diagram shows its final state")
    # phone: fits, tappable controls
    ph = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pp = ph.new_page(); pp.on("pageerror", lambda e: errors.append(str(e)))
    pp.goto(U + "#ref"); pp.goto(U + "#t/waves-photons"); pp.wait_for_timeout(120); finish(pp)
    sw = pp.evaluate("document.documentElement.scrollWidth"); over = pp.evaluate("[...document.querySelectorAll('figure.av')].filter(f=>f.getBoundingClientRect().right>innerWidth+1).length")
    small = pp.evaluate("[...document.querySelectorAll('figure.av button, figure.av input')].filter(e=>e.getBoundingClientRect().height<28).length")
    check(sw <= 390 and over == 0, f"390 px: no sideways scroll, every diagram inside the screen ({sw}, {over} overflowing)")
    check(small == 0, f"390 px: every control is at least 28 px tall ({small} smaller)")
    check(not errors, f"no console or page errors {errors[:2]}")
    b.close()
print("av: PASS" if not fails else f"av: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
