"""Browser test of the interactive questions on topic pages. Usage: python tests/textbook.py [path-to-html]"""
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
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page()
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(U + "#ref"); pg.goto(U + "#t/waves-photons"); pg.wait_for_timeout(50)
    n_all, n_inline = pg.locator(".pq").count(), pg.locator(".checks .pq").count()
    check(n_all == 14 and n_inline == 5, f"waves-photons: 14 questions, 5 inline after sections ({n_all}, {n_inline})")
    check(pg.locator("h2.practice").count() == 1 and pg.locator("h2.practice ~ h3").count() == 0 and pg.locator("h2.practice ~ .pq").count() == 9, "practice set follows the reading as one list, with no difficulty headings")
    check(pg.locator(".pq .chk:not([disabled])").count() == 0, "Check answer is disabled until an option is chosen")
    check(pg.locator(".pq .fb:visible").count() == 0, "no feedback shown before checking")
    q = pg.locator(".pq").first; key = q.get_attribute("data-key")
    q.locator(f".opt:not([data-k='{key}'])").first.click()
    check(q.locator(".chk").is_enabled(), "choosing an option enables Check answer")
    q.locator(".chk").click()
    check(q.evaluate("e=>e.classList.contains('done')") and q.locator(".res").inner_text().startswith("Not correct. The answer is " + key), "wrong answer: marked not correct and names the right one")
    check(q.locator(".opt.right .tag").inner_text() == "Correct answer" and q.locator(".opt.wrong .tag").inner_text() == "Your answer", "options carry text labels, not colour alone")
    check(q.locator(".fb .key").inner_text().strip().startswith("Explanation"), "explanation appears after checking")
    check(pg.locator(".crumb").count() == 1 and "questions checked" not in pg.locator("main").inner_text(), "the heading has a breadcrumb and no status line")
    pg.reload(); pg.wait_for_timeout(50)
    check(pg.locator(".pq.done").count() == 1, "checked question is restored after reload")
    pg.locator(".pq.done .again").click()
    check(pg.locator(".pq.done").count() == 0, "Try again clears the question")
    q = pg.locator(".pq").nth(1); key = q.get_attribute("data-key"); q.locator(f".opt[data-k='{key}']").click(); q.locator(".chk").click()
    check(q.locator(".res").inner_text() == "Correct.", "correct answer: marked correct")
    multi = pg.locator(".pq[data-multi='1']").first
    for k in multi.get_attribute("data-key").split(","): multi.locator(f".opt[data-k='{k}']").click()
    multi.locator(".chk").click()
    check(multi.locator(".res").inner_text() == "Correct.", "select-all question: choosing every correct option is correct")
    q2 = pg.locator(".pq:not(.done):not([data-multi='1'])").first; o = q2.locator(".opt").nth(1); o.focus(); pg.keyboard.press("Space")
    check(o.get_attribute("aria-pressed") == "true", "keyboard: Space selects the focused option")
    seen = pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('ro.cards')||'{}'))")
    check(any(s.startswith("waves-photons:") for s in seen), "checked questions count as seen cards")
    pg.evaluate("localStorage.setItem('ro.q', JSON.stringify({'waves-photons:10': {sel: ['Z']}, 'waves-photons:11': 7, 'x': null}))"); pg.reload(); pg.wait_for_timeout(50)
    check(pg.locator(".pq").count() == 14 and pg.locator(".pq.done").count() == 0, "malformed stored answers are ignored")
    pg.evaluate("localStorage.setItem('ro.q', 'not json')"); pg.reload(); pg.wait_for_timeout(50)
    check(pg.locator(".pq").count() == 14, "unparseable stored answers are ignored")
    n_ans = pg.evaluate("Object.keys(qs).filter(k=>k.startsWith('waves-photons:')).length"); pg.evaluate("localStorage.removeItem('ro.q')"); pg.reload()
    sg = pg.evaluate("[sigOf('waves-photons:10'), sigOf('waves-photons:11'), sigOf('waves-photons:12')]")
    pg.evaluate("s=>{localStorage.setItem('ro.cards', JSON.stringify({'waves-photons:10': {s:1}, 'waves-photons:11': {s:1}})); localStorage.setItem('ro.q', JSON.stringify({'waves-photons:10': {sel: ['A'], ok: false, sig: s[0]}, 'waves-photons:11': {sel: ['B'], ok: false, sig: s[1]}, 'waves-photons:12': {sel: ['A'], ok: false, sig: 'stale'}}))}", sg); pg.goto(U + "#ref"); pg.reload(); pg.goto(U + "#questions"); pg.wait_for_timeout(60)
    pg.goto(U + "#t/waves-photons/q"); pg.wait_for_timeout(60); lead = pg.locator(".lead").inner_text()
    check("14 questions, 2 answered" in lead, f"a topic's question set states its progress: {lead!r}")
    pg.goto(U + "#t/waves-photons"); pg.wait_for_timeout(40)
    check(pg.locator(".pq.done").count() == 2, "answers saved against different options (stale signature) are ignored")
    pg.evaluate("localStorage.removeItem('ro.q'); localStorage.removeItem('ro.cards')"); pg.reload(); pg.wait_for_timeout(40)
    topics = pg.evaluate("DATA.topics.map(t=>[t.id, DATA.cards.filter(c=>c.topic===t.id&&c.opts).length])"); bad = []
    for tid, nq in topics:
        pg.goto(U + "#ref"); pg.goto(U + f"#t/{tid}"); pg.wait_for_timeout(20)
        if pg.locator(".pq").count() != nq: bad.append((tid, nq, pg.locator(".pq").count()))
    check(not bad, f"each topic page shows exactly its problems ({len(topics)} topics) {bad}")
    pg.goto(U + "#t/waves-photons"); q = pg.locator(".pq").first; q.locator(".opt").first.click(); q.locator(".chk").click()
    pg.goto(U + "#ref"); pg.once("dialog", lambda d: d.accept()); pg.click("#clr"); pg.goto(U + "#t/waves-photons"); pg.wait_for_timeout(30)
    check(pg.locator(".pq.done").count() == 0, "Clear on the reference page also clears answers")
    ph = b.new_context(viewport={"width": 390, "height": 844}); pp = ph.new_page(); pp.on("pageerror", lambda e: errors.append(str(e))); worst = 0
    for tid, nq in topics:
        pp.goto(U + "#ref"); pp.goto(U + f"#t/{tid}"); pp.wait_for_timeout(20)
        if pp.locator(".pq").count():
            f = pp.locator(".pq").first; f.locator(".opt").first.click(); f.locator(".chk").click()
        worst = max(worst, pp.evaluate("document.documentElement.scrollWidth"))
    check(worst <= 390, f"390 px: no sideways scroll on any topic page (widest {worst})")
    check(not errors, f"no console or page errors {errors[:2]}")
    b.close()
print("textbook: PASS" if not fails else f"textbook: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
