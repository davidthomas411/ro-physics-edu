"""Menu numbering and the section list under the open chapter: full numbers (1.5), the sections of the chapter being read, the current one marked,
the ones already reached in the accent colour, and the Must know marker; phones keep the heading of the section being read under the top bar."""
import sys, os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    pg = b.new_page(viewport={"width": 1280, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U + "#t/decay-modes"); pg.wait_for_timeout(400)
    nums = pg.eval_on_selector_all("#side a.wk .n", "els=>els.map(e=>e.textContent)")
    check(nums[:5] == ["1.1", "1.2", "1.3", "1.4", "1.5"], f"the menu shows full numbers {nums[:5]}")
    secs = pg.eval_on_selector_all("#side ol.secs a.sec .sn", "els=>els.map(e=>e.textContent)")
    heads = pg.eval_on_selector_all(".guide h2[id]", "els=>els.map(e=>e.id)")
    check(len(secs) >= 4 and secs[0] == "1.5.1" and len(pg.query_selector_all("#side ol.secs")) == 1, f"the open chapter lists its sections {secs}")
    check(all(pg.query_selector(f"#{h}") for h in pg.eval_on_selector_all("#side ol.secs a.sec", "els=>els.map(e=>e.dataset.sec)")), "every section link points at a heading on the page")
    check(pg.locator("#side ol.secs a.sec .mk").count() >= 1 and pg.locator("aside.take .hd").first.inner_text().strip().lower() == "must know", "Must know boxes carry the heading and the menu marks the sections that have one")
    pg.goto(U + "#t/pdd"); pg.wait_for_timeout(300)
    check(pg.locator("#side ol.secs").get_attribute("data-topic") == "pdd" and pg.locator("#side ol.secs").count() == 1, "another chapter shows its own sections, and only that one")
    pg.goto(U + "#t/decay-modes"); pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('decay-modes-s3').scrollIntoView()"); pg.wait_for_timeout(600)
    on = pg.eval_on_selector_all("#side a.sec.on", "els=>els.map(e=>e.dataset.sec)"); rd = pg.eval_on_selector_all("#side a.sec.rd", "els=>els.map(e=>e.dataset.sec)")
    check(on == ["decay-modes-s3"] and "decay-modes-s1" in rd and "decay-modes-s2" in rd, f"scrolling marks the current section and the ones reached ({on}, {rd})")
    c_rd = pg.evaluate("getComputedStyle(document.querySelector('#side a.sec.rd')).color"); c_off = pg.evaluate("getComputedStyle(document.querySelector('#side a.sec:not(.rd):not(.on)')).color")
    check(c_rd != c_off, f"reached sections have their own colour ({c_rd} vs {c_off})")
    pg.locator("#side a.sec[data-sec='decay-modes-s2']").click(); pg.wait_for_timeout(900)
    top = pg.evaluate("document.getElementById('decay-modes-s2').getBoundingClientRect().top")
    check(0 <= top < 200, f"a section link scrolls to its heading (top {top:.0f})")
    check(pg.evaluate("[document.documentElement.scrollWidth, innerWidth]")[0] <= 1280, "no sideways scroll")
    pm = b.new_page(viewport={"width": 390, "height": 844}); pm.on("pageerror", lambda e: errs.append(str(e)))
    pm.goto(U + "#t/decay-modes"); pm.wait_for_timeout(300)
    check(pm.evaluate("getComputedStyle(document.querySelector('.guide h2[id]')).position") == "sticky", "on a phone the heading of the section stays under the top bar")
    check(pm.evaluate("[document.documentElement.scrollWidth, innerWidth]")[0] <= 390, "no sideways scroll on a phone")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"secnav: {n} checks"); print("secnav: PASS" if not bad else f"secnav: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
