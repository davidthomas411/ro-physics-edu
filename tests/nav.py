"""Navigation: Home, Flash cards, Questions, and Reference in the header, a page for each domain, no dead ends, and tap distances from Home."""
import os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ro-physics.html"
U = PAGE.resolve().as_uri(); fails, errors = [], []
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)
ROUTE = re.compile(r"^#(home|ref|mix)$|^#t/[^/]+(/c|/q)?$")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(U); pg.wait_for_timeout(150)
    topics = pg.evaluate("DATA.topics.map(t=>t.id)")
    def go(h): pg.goto(U + "#ref"); pg.goto(U + h); pg.wait_for_timeout(40)
    links = lambda: pg.evaluate("[...new Set([...document.querySelectorAll('a[href^=\"#\"]')].map(a=>a.getAttribute('href')))]")
    text = lambda: pg.evaluate("document.querySelector('#main').innerText")
    go("#home"); tabs = pg.evaluate("[...document.querySelectorAll('.tabs a')].map(a=>a.textContent)")
    check(tabs == ["Home", "Flash cards", "Questions", "MU calc", "Reference"], f"the header has Home first, MU calc, and no Contents tab: {tabs}")
    bad = []
    for h, want in {"#home": "Home", "#cards": "Flash cards", "#questions": "Questions", "#ref": "Reference", f"#t/{topics[0]}": None, f"#t/{topics[0]}/c": "Flash cards", f"#t/{topics[0]}/q": "Questions", "#mix": "Flash cards"}.items():
        go(h); got = pg.evaluate("document.querySelector('.tabs a.on')&&document.querySelector('.tabs a.on').textContent")
        if got != want: bad.append((h, got, want))
    check(not bad, f"the current section is highlighted on every kind of page, and on none for a chapter or a domain page {bad}")
    bad = []
    for t in topics:
        go(f"#t/{t}"); nq = pg.locator(".pq").count(); want = pg.evaluate(f"quizOf('{t}').length"); inl = pg.locator(f'a[href="#t/{t}/c"]').count()
        if nq != want or inl < 2: bad.append((t, nq, want, inl))
    check(not bad, f"each topic page holds all its practice questions and links to its flash cards twice {bad}")
    check(pg.evaluate("DATA.topics.every(t=>flashOf(t.id).length>0&&flashOf(t.id).every(c=>!c.opts))"), "every deck holds flash cards only, and every topic has a deck")
    go(f"#t/{topics[0]}/c"); l = links()
    check(f"#t/{topics[0]}" in l and "Card 1 of" in text() and "Flash cards ›" in text(), "a deck links back to its chapter")
    go("#cards"); h_c = pg.evaluate("location.hash"); go("#questions"); h_q = pg.evaluate("location.hash"); n_rows = pg.locator("a.w").count()
    check(h_c == f"#t/{topics[0]}/c" and h_q == f"#t/{topics[0]}/q" and n_rows == 0, f"there is no page listing the decks or the question sets: the old addresses open the first topic's deck ({h_c}) and set ({h_q})")
    go(f"#t/{topics[3]}"); mid = pg.evaluate("[...document.querySelectorAll('.tabs a')].map(a=>[a.dataset.tab,a.getAttribute('href')])"); pg.click('.tabs a[data-tab="cards"]'); pg.wait_for_timeout(150); a1 = pg.evaluate("location.hash"); go(f"#t/{topics[3]}"); pg.click('.tabs a[data-tab="questions"]'); pg.wait_for_timeout(150); a2 = pg.evaluate("location.hash")
    check(a1 == f"#t/{topics[3]}/c" and a2 == f"#t/{topics[3]}/q", f"from a chapter, Flash cards and Questions open that topic's own deck and question set {mid}")
    go(f"#t/{topics[2]}/c"); go("#ref"); pg.click('.tabs a[data-tab="questions"]'); pg.wait_for_timeout(150); a3 = pg.evaluate("location.hash"); go("#home"); pg.click('.tabs a[data-tab="cards"]'); pg.wait_for_timeout(150); a4 = pg.evaluate("location.hash")
    check(a3 == f"#t/{topics[2]}/q" and a4 == f"#t/{topics[2]}/c", "from Home or Reference they open the last topic visited")
    go("#d1"); first1 = pg.evaluate("topicsOfDom(1)[0].id"); h1 = pg.evaluate("location.hash"); pg.goto(U + "#d1/c"); pg.wait_for_timeout(80); h2 = pg.evaluate("location.hash"); go("#d9"); h3 = pg.evaluate("location.hash")
    check(h1 == f"#t/{first1}" and h2.endswith("/c") and h3 == "#home", f"a domain address opens that domain's first topic ({h1}), old domain decks land on a deck ({h2}), and an address of a domain that does not exist goes Home ({h3})")
    go("#study"); check(pg.evaluate("location.hash") == "#home" and pg.locator("h1").inner_text() == "Home", "the old Contents address now opens Home")
    bad = [h for h in ("#home", "#questions", "#cards", "#ref", f"#t/{topics[0]}", f"#t/{topics[0]}/c") if (go(h), "Mixed practice" in text())[1]]
    check(not bad, f"no page still says Mixed practice {bad}")
    # the front page is the dial and nothing else: no description, no continue button, no repeat of the top menu
    pg.evaluate("localStorage.clear()"); go("#home"); h1 = pg.locator("h1").inner_text(); doors = pg.evaluate("""[...document.querySelectorAll('#main a[href="#cards"], #main a[href="#questions"], #main a[href="#ref"], #main .door')].map(a=>a.getAttribute('href'))""")
    check(h1 == "Home" and doors == [], f"Home does not repeat the top menu: no links in the page to Flash cards, Questions, or Reference, and no door cards {doors}")
    vis_h1 = pg.evaluate("(()=>{const r=document.querySelector('#main h1').getBoundingClientRect(); return r.width*r.height})()"); text = pg.locator("#main").inner_text()
    check(vis_h1 <= 1.5 and "Study guide" not in text and pg.locator(".cont").count() == 0 and pg.locator("#main .btn").count() == 0 and pg.locator("#main a:not(.seg)").count() == 0, "Home has no visible Home heading, no description, and no button: the page links only to the domains on the dial")
    go("#t/decay-law"); go("#home"); check(pg.locator("#main .btn").count() == 0, "later visits show no continue button either")
    check(pg.locator(".dial.big a.seg").count() == pg.evaluate("activeDoms().length") and pg.locator("h2").first.inner_text() == "Exam domains", "the dial sits under an Exam domains heading, one link per domain with topics")
    pg.evaluate('''document.querySelector('.dial.big a.seg[data-dom="3"]').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))'''); pg.wait_for_timeout(250)
    first3 = pg.evaluate("topicsOfDom(3)[0].id"); title3 = pg.evaluate("topic('%s').title" % first3)
    check(pg.evaluate("location.hash") == f"#t/{first3}" and title3 in pg.locator("h1").inner_text(), "selecting a domain on the dial goes straight into its first topic")
    # tap distance from Home on a phone, following only what is visible
    pm = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True).new_page(); pm.on("pageerror", lambda e: errors.append(str(e)))
    vis = lambda: pm.evaluate("[...new Set([...document.querySelectorAll('a[href^=\"#\"]')].filter(a=>a.getClientRects().length).map(a=>a.getAttribute('href')).concat(document.querySelector('#jump')&&document.querySelector('#jump').getClientRects().length?[...document.querySelectorAll('#jump option')].map(o=>o.value):[]))]")      # the jump menu is the phone's list of topics, one step
    dist, queue = {"#home": 0}, ["#home"]
    while queue:
        h = queue.pop(0); pm.goto(U + "#ref"); pm.goto(U + h); pm.wait_for_timeout(30)
        for l in vis():
            if ROUTE.match(l) and l not in dist: dist[l] = dist[h] + 1; queue.append(l)
    chap = [dist.get(f"#t/{t}") for t in topics]; decks = [dist.get(f"#t/{t}/c") for t in topics]; qsets = [dist.get(f"#t/{t}/q") for t in topics]
    check(all(d is not None and d <= 2 for d in qsets), f"every topic's question set is at most two taps from Home ({sorted(set(qsets), key=str)})")
    firsts = pm.evaluate("activeDoms().map(d=>topicsOfDom(d.n)[0].id)")
    check(all(dist.get(f"#t/{i}") == 1 for i in firsts) and dist.get(f"#t/{topics[0]}/c") == 1 and dist.get(f"#t/{topics[0]}/q") == 1 and dist.get("#ref") == 1, "from Home, the first topic of each domain (the dial), a deck, a question set, and Reference are one tap away")
    check(all(d is not None and d <= 2 for d in chap) and all(d is not None and d <= 2 for d in decks) and dist.get("#mix") == 2, f"every topic page and every deck is at most two steps from Home, the jump menu counting as one, and the mix deck two (topics {sorted(set(chap))}, decks {sorted(set(decks))}, mix {dist.get('#mix')})")
    print("taps from Home on a phone:", {k: v for k, v in dist.items() if not k.startswith("#t/")}, "| topic pages:", sorted(set(chap)), "| decks:", sorted(set(decks)))
    # dial labels must not touch the screen edge at any phone width
    edge = []
    for w, h in ((320, 700), (360, 780), (390, 844), (430, 900)):
        q = b.new_context(viewport={"width": w, "height": h}, has_touch=True, is_mobile=True).new_page(); q.goto(U + "#ref"); q.goto(U + "#home"); q.wait_for_timeout(150)
        bad = q.evaluate("(()=>{const W=innerWidth; return [...document.querySelectorAll('.dial.m text')].filter(t=>{const r=t.getBoundingClientRect(); return r.left<6||r.right>W-6;}).map(t=>t.textContent.trim())})()")
        if bad: edge.append((w, bad))
    check(not edge, f"phone dial labels stay at least 6 px from the screen edge at 320, 360, 390, and 430 px {edge}")
    ph = b.new_context(viewport={"width": 390, "height": 844}); pp = ph.new_page(); pp.on("pageerror", lambda e: errors.append(str(e)))
    pp.goto(U + "#ref"); pp.goto(U + "#home"); pp.wait_for_timeout(80)
    tw = pp.evaluate("(()=>{const t=document.querySelector('.tabs');return [t.scrollWidth,t.clientWidth,document.documentElement.scrollWidth]})()")
    check(tw[0] <= tw[1] + 1 and tw[2] <= 390, f"390 px: the five tabs fit without scrolling ({tw})")
    check(not errors, f"no console or page errors {errors[:2]}")
    b.close()
print("nav: PASS" if not fails else f"nav: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
