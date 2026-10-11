"""Replays the intended solution of every 'Work it out' spec through the page, then checks the error messages and controls."""
import os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import blocks
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ro-physics.html"
U = PAGE.resolve().as_uri(); fails, errors = [], []
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)
specs = [(t["id"], f"{t['id']}:{len(t['cards']) + n}", p) for t in TOPICS for n, p in enumerate(t["problems"], 1) if p.get("calc")]

def press(q, item, spec):
    ids = {t["id"] for t in spec["tiles"]}
    q.locator((f'.tile[data-id="{item}"]' if item in ids else f'.tile.op[data-op="{item}"]')).click()

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page()
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errors.append(str(e)))
    bad = []
    for tid, pid, prob in specs:
        pg.goto(U + "#ref"); pg.goto(U + f"#t/{tid}"); pg.wait_for_timeout(30)
        q = pg.locator(f'.pq[data-id="{pid}"]'); q.locator("details.calc summary").click()
        for item in prob["calc"]["solution"]: press(q, item, prob["calc"])
        res = q.locator(".cres").inner_text(); key = prob["key"][0]
        if f"Matches option {key}." not in res: bad.append((pid, res, key)); continue
        q.locator('[data-act="use"]').click(); q.locator(".chk").click()
        if q.locator(".res").inner_text() != "Correct.": bad.append((pid, "not marked correct", key))
    check(not bad, f"{len(specs)} calculations: the intended route reaches the right option and is marked correct {bad}")
    # error messages and controls (start from clean storage: a checked question hides its panel by design)
    pg.evaluate("localStorage.clear()"); pg.goto(U + "#t/waves-photons"); pg.reload(); pg.wait_for_timeout(60)
    pq = [s for s in specs if s[0] == "waves-photons"]
    freq = next(s for s in pq if "known frequency" in s[2]["q"]); joule = next(s for s in pq if "joules" in s[2]["q"])
    q = pg.locator(f'.pq[data-id="{freq[1]}"]'); q.locator("details.calc summary").click(); spec = freq[2]["calc"]
    for it in ("hc", "÷", "nu"): press(q, it, spec)
    r = q.locator(".cres"); check("The answer must be a length" in r.inner_text() and "bad" in (r.get_attribute("class") or ""), "wrong units: says what kind of quantity the answer must be")
    q.locator('[data-act="clear"]').click(); check(q.locator(".expr span").count() == 1 and r.inner_text() == "", "Clear empties the calculation")
    press(q, "hc", spec); press(q, "÷", spec); check("incomplete" in r.inner_text() and "soft" in (r.get_attribute("class") or ""), "incomplete expression: muted hint, not an error")
    q.locator('[data-act="undo"]').click(); check(q.locator(".expr span").count() == 1 and "eV·nm" in r.inner_text(), "Remove last removes one tile")
    q2 = pg.locator(f'.pq[data-id="{joule[1]}"]'); q2.locator("details.calc summary").click(); spec2 = joule[2]["calc"]
    press(q2, "E", spec2); r2 = q2.locator(".cres")
    check("convert" in r2.inner_text() and q2.locator('[data-act="use"]').is_hidden(), "result in the wrong unit asks for a conversion and offers no option")
    press(q2, "×", spec2); press(q2, "MeV→eV", spec2)
    check("10⁶ eV" in r2.inner_text(), "a conversion tile cancels the unit and shows the new unit")
    press(q2, "×", spec2); press(q2, "eV→J", spec2)
    check(q2.locator('[data-act="use"]').is_visible(), "a matching result offers Select")
    q2.locator('[data-act="use"]').click(); check(q2.locator(".opt[aria-pressed='true']").count() == 1 and q2.locator(".chk").is_enabled(), "Select chooses the matching option")
    q2.locator(".chk").click(); check(q2.locator("details.calc").is_hidden(), "the panel is hidden once the question is checked")
    deut = next(s for s in specs if s[0] == "nuclear-structure"); pg.goto(U + "#ref"); pg.goto(U + "#t/nuclear-structure"); pg.wait_for_timeout(40)
    q3 = pg.locator(f'.pq[data-id="{deut[1]}"]'); q3.locator("details.calc summary").click()
    for it in ("H1", "+", "u→MeV"): press(q3, it, deut[2]["calc"])
    check("Cannot add u and MeV/u" in q3.locator(".cres").inner_text(), "adding quantities with different units is refused")
    # phone: panel fits, nothing scrolls sideways, tiles are tappable
    ph = b.new_context(viewport={"width": 390, "height": 844}); pp = ph.new_page(); pp.on("pageerror", lambda e: errors.append(str(e))); worst = 0; small = 0
    for tid2 in sorted({s[0] for s in specs}):
        pp.goto(U + "#ref"); pp.goto(U + f"#t/{tid2}"); pp.wait_for_timeout(30)
        for d in pp.locator("details.calc summary").all(): d.click()
        worst = max(worst, pp.evaluate("document.documentElement.scrollWidth"))
        small += pp.evaluate("[...document.querySelectorAll('.tile')].filter(b=>b.getBoundingClientRect().height<28).length")
    check(worst <= 390, f"390 px: every panel open, no sideways scroll (widest {worst})")
    check(small == 0, f"390 px: every tile is at least 28 px tall ({small} smaller)")
    check(not errors, f"no console or page errors {errors[:2]}")
    b.close()
print("calc: PASS" if not fails else f"calc: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
