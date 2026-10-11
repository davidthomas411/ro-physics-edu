"""Swipe in the card review, sent as real touch events. Usage: python tests/swipe.py [path-to-html]"""
import os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ro-physics.html"
U = PAGE.resolve().as_uri(); fails, errors = [], []
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e))); cdp = ctx.new_cdp_session(pg)
    def swipe(x0, y0, x1, y1, steps=8):
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]})
        for i in range(1, steps + 1): cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * i / steps, "y": y0 + (y1 - y0) * i / steps}]})
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); pg.wait_for_timeout(120)
    h = lambda: pg.evaluate("location.hash")
    pg.goto(U + "#ref"); pg.goto(U + "#t/waves-photons/c"); pg.wait_for_timeout(60)
    check(h() == "#t/waves-photons/c", "starts on card 1")
    check(pg.locator(".kbd .sw").is_visible() and pg.locator(".kbd .kb").is_hidden(), "touch devices see the swipe hint, not the keyboard hint")
    swipe(300, 420, 90, 430); check(h() == "#t/waves-photons/c/2", f"swipe left goes to the next card ({h()})")
    swipe(90, 420, 300, 425); check(h() == "#t/waves-photons/c", f"swipe right goes back ({h()})")
    swipe(90, 420, 300, 425); check(h() == "#t/waves-photons/c", "swipe right on the first card stays put")
    swipe(200, 640, 200, 300); check(h() == "#t/waves-photons/c", "a vertical swipe (scrolling) does not change card")
    swipe(220, 420, 190, 424); check(h() == "#t/waves-photons/c", "a short horizontal movement does not change card")
    swipe(300, 420, 120, 620); check(h() == "#t/waves-photons/c", "a diagonal swipe does not change card")
    swipe(300, 420, 90, 430)
    seen = pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('ro.cards')||'{}'))")
    check(h() == "#t/waves-photons/c/2" and "waves-photons:1" in seen and "waves-photons:2" in seen, "a fact counts as seen when it is shown, so swiping on marks both cards")
    check(not errors, f"no page errors {errors[:2]}")
    b.close()
print("swipe: PASS" if not fails else f"swipe: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
