"""The Questions section: an index of topics, and for each topic a page with only its questions, in one list, sharing answers with the chapter page."""
import sys, os, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
from playwright.sync_api import sync_playwright
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri(); bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    pg = b.new_page(viewport={"width": 1280, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
    def go(h): pg.goto(U + "#ref"); pg.goto(U + h); pg.wait_for_timeout(60)
    go("#home"); topics = pg.evaluate("DATA.topics.map(t=>t.id)"); total = pg.evaluate("DATA.cards.filter(c=>c.opts).length")
    go("#questions"); check(pg.evaluate("location.hash") == f"#t/{topics[0]}/q" and pg.locator(".tabs a.on").inner_text() == "Questions" and pg.locator("a.w").count() == 0, "there is no page of question sets: Questions opens the first topic's set, and the Questions tab is on")
    check(sum(pg.evaluate(f"quizOf('{t}').length") for t in topics) == total, f"every one of the {total} questions belongs to a topic's set")
    bad_pages = []
    for t in topics:
        go(f"#t/{t}/q"); want = pg.evaluate(f"quizOf('{t}').length"); got = pg.locator(".pq").count()
        heads = pg.locator("h2.qh").count()
        extra = pg.evaluate("document.querySelectorAll('#main .take, #main figure.av, #main .ex, #main .toc, #main .eq, #main .tbl, #main h3, #main aside').length")
        paras = pg.evaluate("[...document.querySelectorAll('.guide > p')].length")
        if got != want or heads or extra or paras: bad_pages.append((t, got, want, heads, extra, paras))
    check(not bad_pages, f"every topic's page holds exactly its questions in one list, with no difficulty headings, notes, take-aways, diagrams, or examples {bad_pages[:2]}")
    words = []
    for h in ("#t/pdd", "#t/pdd/q", "#t/waves-photons", "#t/waves-photons/q", "#mu/1", "#mu/22", "#ref"):
        go(h); txt = pg.evaluate("[document.querySelector('#main').innerText, ...[...document.querySelectorAll('#main [title],#main [aria-label]')].map(e=>(e.title||'')+' '+(e.getAttribute('aria-label')||''))].join(' ')")
        m = re.findall(r"\b(?:Easy|Moderate|Challenging)\b", txt)
        if m: words.append((h, m[:3]))
    check(not words, f"no page tells the reader how hard a question is: no Easy, Moderate, or Challenging in the text, titles, or labels {words}")
    go("#t/pdd/q"); pg.locator(".pq .opt").first.click(); pg.locator(".pq .chk").first.click(); cid = pg.locator(".pq.done").first.get_attribute("data-id")
    check(bool(cid) and pg.evaluate(f"!!qSel('{cid}')"), f"answering a question on its question page saves the answer ({cid})")
    go("#t/pdd"); check(pg.locator(f'.pq[data-id="{cid}"]').first.evaluate("e=>e.classList.contains('done')"), "the same question shows as answered on the chapter page")
    go("#t/pdd/q"); check(pg.locator(".lead").inner_text().count("answered") == 1 and pg.locator(f'.pq[data-id="{cid}"]').evaluate("e=>e.classList.contains('done')"), "reopening the set restores the answered question")
    nxt = pg.locator(".endrow a.btn.primary").get_attribute("href"); prv = pg.locator(".endrow a.btn").first.get_attribute("href"); i = topics.index("pdd")
    check(nxt == f"#t/{topics[i + 1]}/q" and prv == f"#t/{topics[i - 1]}/q", "Previous and Next topic stay inside the question sets")
    check(pg.locator(".crumb").inner_text().startswith("Questions ›") and pg.locator('.tocx a[href="#t/pdd"]').count() == 1 and pg.locator('.tocx a[href="#t/pdd/c"]').count() == 1, "each set links to its chapter and to its flash cards")
    go("#t/pdd"); check(pg.locator('a[href="#t/pdd/q"]').count() >= 2, "a chapter page links to its question set at the top and at the end")
    go("#home"); pg.click('.tabs a[data-tab="questions"]'); pg.wait_for_timeout(200); check(pg.locator("#main a[href=\"#questions\"]").count() == 0 and pg.locator(".pq").count() == pg.evaluate("quizOf(location.hash.split('/')[1]).length"), "the Questions item in the top menu opens a set of questions, and Home does not repeat it")
    pm = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True).new_page(); pm.on("pageerror", lambda e: errs.append(str(e))); wide = []
    for h in ["#questions"] + [f"#t/{t}/q" for t in topics]:
        pm.goto(U + "#ref"); pm.goto(U + h); pm.wait_for_timeout(50)
        w = pm.evaluate("[document.documentElement.scrollWidth, innerWidth, Math.max(0,...[...document.querySelectorAll('.pq')].map(e=>e.scrollWidth-e.clientWidth))]")
        if w[0] > w[1] or w[2] > 0: wide.append((h, w))
    check(not wide, f"the Questions pages fit a 390 px phone without sideways scroll {wide[:2]}")
    pm.goto(U + "#t/pdd/q"); pm.wait_for_timeout(60); opts = pm.evaluate("[...document.querySelectorAll('#jump option')].map(o=>o.value)")
    check("#questions" in opts and "#t/pdd/q" in opts and "#t/pdd/c" not in opts, "on a phone the dropdown offers Questions and the question sets")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"questions: {n} checks"); print("questions: PASS" if not bad else f"questions: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
