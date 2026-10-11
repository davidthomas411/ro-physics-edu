"""Smoke test for dist/ro-physics.html. Usage: python tests/smoke.py [path-to-html]
Needs: pip install -r requirements-dev.txt && playwright install chromium (or set CHROME_PATH to an existing Chromium)."""
import json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ro-physics.html"
U = PAGE.resolve().as_uri()
errors, failures = [], []

def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: failures.append(msg)

def fresh(pg, h):
    pg.goto(U + "#ref"); pg.goto(U + h); pg.wait_for_timeout(30)

def walk(pg, hash_, n):
    fresh(pg, hash_); steps = 0
    while pg.query_selector("#nextq") and steps < n + 2:
        prev = pg.evaluate("document.querySelector('#fc').dataset.id")
        pg.click("#nextq"); steps += 1
        pg.wait_for_function("p=>{const f=document.querySelector('#fc'); return !f || f.dataset.id!==p;}", arg=prev)
    return steps

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("dialog", lambda d: d.accept())
    pg.goto(U); pg.wait_for_timeout(200)
    topics = pg.evaluate("DATA.topics.map(t=>t.id)")
    doms = pg.evaluate("activeDoms().map(d=>d.n)")
    ncards = {t: pg.evaluate(f"flashOf('{t}').length") for t in topics}
    subs_with_topics = pg.evaluate("new Set(DATA.topics.map(t=>t.sub)).size")
    total_subs = pg.evaluate("DATA.domains.reduce((a,d)=>a+d.subs.length,0)")

    # content integrity
    check(pg.evaluate("DATA.cards.every(c=>c.q&&c.a.length&&c.id)") and pg.evaluate("new Set(DATA.cards.map(c=>c.id)).size") == pg.evaluate("DATA.cards.length"), "every card has a question, an answer, and a unique id")
    check(pg.evaluate("DATA.cards.every(c=>!c.fig||FIG[c.fig])"), "every card figure exists")
    check(total_subs == 20, f"blueprint lists 20 ABR subsections ({total_subs})")

    # topic pages
    bad = 0
    for t in topics:
        fresh(pg, f"#t/{t}")
        txt = pg.evaluate("document.querySelector('#main').innerText")
        bad += (not pg.query_selector(".guide h2")) or any(w in txt for w in ("undefined", "NaN", "[object"))
    check(bad == 0, f"{len(topics)} topic pages render with a guide")

    # every deck opens at slide 1
    decks = [f"#t/{t}/c" for t in topics] + ["#mix"]
    opened = 0
    for d in decks:
        fresh(pg, d); opened += bool(pg.query_selector("#fc")) and "Card 1 of" in pg.evaluate("document.querySelector('#main').innerText")
    check(opened == len(decks), f"{len(decks)} decks open at card 1 ({opened})")

    # one deck walks to the end screen; progress is stored
    t0 = topics[1]; steps = walk(pg, f"#t/{t0}/c", ncards[t0])
    check(steps == ncards[t0] and "Restart" in pg.evaluate("document.querySelector('#main').innerText"), f"{t0} walks {ncards[t0]} cards to the end screen ({steps})")
    check(pg.evaluate(f"seenCount(flashOf('{t0}'))") == ncards[t0], "every fact in the deck is marked seen after clicking through it")

    # keyboard
    fresh(pg, f"#t/{topics[3]}/c")
    pg.keyboard.press(" "); pg.wait_for_timeout(180); check(pg.evaluate("location.hash").endswith("/c/2"), "Space goes to the next card")
    pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(180); check(pg.evaluate("location.hash").endswith("/c"), "Left arrow goes back")
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(180); check(pg.evaluate("location.hash").endswith("/c/2"), "Right arrow goes to the next card")

    # reference: coverage audit, export, import, clear
    fresh(pg, "#ref")
    gaps = pg.locator("table.cov tr.gap").count()
    check(gaps == total_subs - subs_with_topics, f"coverage table marks {total_subs - subs_with_topics} subsections without cards ({gaps})")
    with pg.expect_download() as dl: pg.click("#exp")
    exported = json.loads(Path(dl.value.path()).read_text())
    check(len(exported) == pg.evaluate("Object.keys(prog).length") and all(k in exported for k in pg.evaluate("Object.keys(prog)")), f"export holds every seen card ({len(exported)})")
    pg.click("#clr"); pg.wait_for_timeout(60)
    check("0 flash cards seen" in pg.evaluate("document.querySelector('#main').innerText"), "Clear empties progress")
    exported["not-a-card"] = {"s": 1}
    pg.set_input_files("#impf", files=[{"name": "p.json", "mimeType": "application/json", "buffer": json.dumps(exported).encode()}]); pg.wait_for_timeout(120)
    check(pg.evaluate("Object.keys(prog).length") == len(exported) - 1, "Import restores known cards and ignores unknown ones")

    # stale or hostile stored values must not break the page
    for val in ("[]", "5", '"x"', "null", "not json", '{"decay-law:1":"yes"}', '{"nope":{"s":1}}', '[1,2]'):
        pg.goto(U + "#home"); pg.evaluate("v=>{localStorage.setItem('ro.cards',v);localStorage.setItem('ro.theme','purple')}", val)
        for h in ("#home", "#d1", "#ref", f"#t/{topics[0]}", f"#t/{topics[0]}/c"):
            pg.goto(U + h); pg.reload(); pg.wait_for_timeout(30)
            if not pg.query_selector("#main h1, #main .fc"): failures.append(f"page broke with stored value {val!r} at {h}")
    check(not [f for f in failures if "stored value" in f], "stale or malformed stored progress never breaks a page")
    pg.evaluate("localStorage.clear()")

    # dial
    fresh(pg, "#home")
    check(pg.locator(".dial.big .seg").count() == 7 and pg.locator(".dial.big a.seg").count() == len(doms), f"dial has 7 sections, {len(doms)} linked")
    pg.dispatch_event(".dial.big a.seg", "mouseenter"); pg.wait_for_timeout(80)
    check(not pg.evaluate("document.querySelector('.dial.big').classList.contains('spin')"), "hovering a section turns the gantry (idle sweep stops)")

    # dark mode follows the system and the toggle overrides it
    dk = b.new_context(viewport={"width": 1280, "height": 900}, color_scheme="dark").new_page()
    dk.on("pageerror", lambda e: errors.append(str(e)))
    dk.goto(U + "#ref"); dk.wait_for_timeout(100)
    check(dk.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(18, 18, 18)", "dark system setting gives the dark palette")
    dk.click("[data-theme-btn]"); dk.wait_for_timeout(60)
    check(dk.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(255, 255, 255)", "theme toggle switches to light")

    # phone: nothing scrolls sideways; the phone dial and the dropdown are used
    pm = b.new_context(viewport={"width": 390, "height": 844}).new_page()
    pm.on("pageerror", lambda e: errors.append(str(e)))
    pm.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    wide = []
    for h in ["#home", "#ref", "#questions", "#mix", "#mix/2"] + [f"#t/{t}" for t in topics] + [f"#t/{t}/c" for t in topics] + [f"#t/{t}/q" for t in topics] + [f"#d{n}" for n in doms]:
        pm.goto(U + "#ref"); pm.goto(U + h); pm.wait_for_timeout(40)
        if pm.evaluate("document.documentElement.scrollWidth") != 390: wide.append(h)
    check(not wide, "390 px width, no sideways scroll on every route" + (f": {wide}" if wide else ""))
    pm.goto(U + "#home"); pm.wait_for_timeout(60)
    check(pm.is_visible(".dial.m") and not pm.is_visible(".dial.big") and pm.is_visible("#jump") and not pm.is_visible("#side"), "phone shows the phone dial and the dropdown, not the sidebar")
    check(pm.evaluate("[...document.querySelectorAll('#jump option')].map(o=>o.value).every(v=>v.startsWith('#'))"), "dropdown lists real destinations")
    b.close()

check(not errors, "no console or page errors" + (f": {errors[:3]}" if errors else ""))
sys.exit(1 if failures else 0)
