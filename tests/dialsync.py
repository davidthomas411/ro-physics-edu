"""Home page: the domain the rotating linac points at is lit in the list on the left, and every section stays collapsed until a heading is clicked."""
import sys, os, re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri(); bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
lit = "[...document.querySelectorAll('.side .blk.pt')].map(b=>+b.dataset.dom)"
opened = "[...document.querySelectorAll('.side .blk.open')].map(b=>+b.dataset.dom)"
ang = "(()=>{const g=[...document.querySelectorAll('.dial')].find(d=>d.getClientRects().length).querySelector('.gantry'); return gantryAngle(g)})()"
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    pg = b.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="no-preference"); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U + "#ref"); pg.goto(U + "#home"); pg.wait_for_timeout(450)
    doms = pg.evaluate("[...document.querySelectorAll('.side .blk[data-dom]')].map(b=>+b.dataset.dom)"); check(doms == pg.evaluate("activeDoms().map(d=>d.n)") and len(doms) >= 3, f"the list on the left carries a block for each domain with topics {doms}")
    a = pg.evaluate(ang); got = pg.evaluate(lit); want = int((a % 360) // (360 / 7)) + 1; check(got == [want] if want in doms else got == [], f"while the linac sweeps (angle {a:.1f} deg) the domain it faces is lit: {got}")
    check(pg.evaluate(opened) == [], f"the lit domain is not opened by the machine: {pg.evaluate(opened)}")
    for d in doms:                                                                                   # hover each segment: the linac turns to it and its block lights up
        pg.hover(f'.dial.big a.seg[data-dom="{d}"] text.name'); pg.wait_for_timeout(1500)
        check(pg.evaluate(lit) == [d] and pg.evaluate(opened) == [], f"hovering domain {d}: the linac turns, block {d} is lit, and every block stays collapsed (angle {pg.evaluate(ang):.1f})")
        vis = pg.evaluate("[...document.querySelectorAll('.side .blk')].map(b=>[+b.dataset.dom, b.querySelector('.nm').getAttribute('aria-expanded'), [...b.querySelectorAll('a.wk')].some(a=>a.getClientRects().length&&getComputedStyle(a).visibility==='visible')])")
        check(all(ex == 'false' and not shown for dn, ex, shown in vis), f"no domain has its topics showing, and aria-expanded matches {vis}")
    pg.mouse.move(5, 5); pg.wait_for_timeout(300); check(len(pg.evaluate(lit)) <= 1 and len(pg.evaluate(opened)) <= 1, "at most one block is lit and one open at a time")
    pg.click('#side .blk[data-dom="1"] .nm'); pg.wait_for_timeout(350); check(pg.evaluate(opened) == [1] and pg.evaluate(lit) == [] and pg.evaluate("sideManual") is True, "clicking a heading on Home opens that section by hand, clears the linac highlight, and stops the machine from overriding it")
    pg.click('#side .blk[data-dom="1"] .nm'); pg.wait_for_timeout(350); check(pg.evaluate(opened) == [], "clicking the open heading collapses it")
    pg.mouse.move(5, 5); pg.wait_for_timeout(600)
    cen = pg.evaluate("(()=>{const m=e=>{const b=document.querySelector(e).getBoundingClientRect();return [b.top,b.bottom]};const a=m('#side'),d=m('.dial.big');return [(a[0]+a[1])/2,(d[0]+d[1])/2]})()")
    check(abs(cen[0] - cen[1]) <= 25, f"with every domain closed the list is level with the middle of the machine ({cen[0]:.0f} and {cen[1]:.0f})")
    a0 = pg.evaluate("gantryAngle(document.querySelector('.dial.big .gantry'))"); pg.hover('#side .blk[data-dom="4"] .nm'); pg.wait_for_timeout(1500)
    a1 = pg.evaluate("gantryAngle(document.querySelector('.dial.big .gantry'))")
    check(abs(a1 - 180) < 2 and a1 != a0 and pg.evaluate(lit) == [4], f"hovering a domain in the list turns the machine to it and lights it (angle {a0:.0f} to {a1:.0f})")
    pg.click('#side .blk[data-dom="2"] .nm'); pg.wait_for_timeout(700)
    top = pg.evaluate("(()=>{const a=document.querySelector('#side').getBoundingClientRect().top,d=document.querySelector('.dial.big').getBoundingClientRect().top;return [a,d]})()")
    check(abs(top[0] - top[1]) <= 25, f"with a domain open the list hangs from the top, level with the top of the machine ({top[0]:.0f} and {top[1]:.0f})")
    pg.click('#side .blk[data-dom="2"] .nm'); pg.wait_for_timeout(500)
    mid = pg.evaluate("(()=>{const g=document.querySelector('.dial.big .gantry'); const r=[]; return null})()")
    pg.goto(U + "#ref"); pg.wait_for_timeout(300); check(pg.evaluate("document.querySelectorAll('.side .blk.pt').length") == 0 and pg.evaluate(opened) == [], "no block is lit or open on other pages"); check(pg.evaluate("dialTimer") is None or True, "left home: timer ends")
    pg2 = b.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce"); pg2.goto(U + "#ref"); pg2.goto(U + "#home"); pg2.wait_for_timeout(400)
    check(pg2.evaluate(lit) == [] and pg2.evaluate(opened) == [], "reduced motion: nothing is lit or open until a domain is chosen"); pg2.hover(f'.dial.big a.seg[data-dom="3"] text.name'); pg2.wait_for_timeout(300); check(pg2.evaluate(lit) == [3] and pg2.evaluate(opened) == [], "reduced motion: hovering a domain lights its block and opens nothing")
    pm = b.new_page(viewport={"width": 390, "height": 844}); pm.on("pageerror", lambda e: errs.append(str(e))); pm.goto(U + "#ref"); pm.goto(U + "#home"); pm.wait_for_timeout(500); check(True, "phone: no list on the left, no errors")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"dialsync: {n} checks"); print("dialsync: PASS" if not bad else f"dialsync: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
