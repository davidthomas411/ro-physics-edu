"""Left list: collapsed until selected, one section open (the current one). The linac at the top of it is the total progress through the course (chapters read, flash cards seen, questions answered), in the list on a wide screen and in a sticky bar on a phone. Home is in the header, and a domain opens its first topic."""
import sys, os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri(); bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
OPEN = "[...document.querySelectorAll('#side .blk.open')].map(b=>+b.dataset.dom)"
SHOW = "[...document.querySelectorAll('#side .blk')].map(b=>[+b.dataset.dom, b.querySelector('.nm').getAttribute('aria-expanded'), [...b.querySelectorAll('a.wk')].some(a=>a.getClientRects().length>0&&getComputedStyle(a).visibility==='visible')])"
VAL = "+document.querySelector('#side .lp').getAttribute('aria-valuenow')"
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    pg = b.new_page(viewport={"width": 1280, "height": 900}, color_scheme="light"); pg.on("pageerror", lambda e: errs.append(str(e)))
    def go(h): pg.goto(U + "#ref"); pg.goto(U + h); pg.wait_for_timeout(350)
    go("#t/pdd"); dom_pdd = pg.evaluate("topic('pdd').dom")
    # ---- the header
    tabs = pg.evaluate("[...document.querySelectorAll('.tabs a')].map(a=>[a.textContent, a.getAttribute('href')])")
    check(tabs[0] == ["Home", "#home"] and ["Contents", "#study"] not in tabs, f"Home is the first item in the top menu and there is no Contents item {tabs}")
    pg.click('.tabs a[href="#home"]'); pg.wait_for_timeout(250); check(pg.evaluate("location.hash") == "#home" and pg.locator("h1").inner_text() == "Home" and pg.locator(".tabs a.on").inner_text() == "Home", "the Home item opens Home and is highlighted there")
    # ---- the accordion on a chapter page
    go("#t/pdd"); check(pg.evaluate(OPEN) == [dom_pdd], f"a chapter page opens only its own section, domain {dom_pdd}: {pg.evaluate(OPEN)}")
    vis = pg.evaluate(SHOW); check(all((dn == dom_pdd) == (ex == "true") and (dn == dom_pdd) == shown for dn, ex, shown in vis), f"the other sections are collapsed: their topics are hidden and aria-expanded is false {vis}")
    first_other = pg.evaluate("activeDoms().map(d=>d.n).find(n=>n!==%d)" % dom_pdd)
    pg.click(f'#side .blk[data-dom="{first_other}"] .nm'); pg.wait_for_timeout(400); check(pg.evaluate(OPEN) == [first_other], f"opening another section closes the current one: {pg.evaluate(OPEN)}")
    pg.click(f'#side .blk[data-dom="{first_other}"] .nm'); pg.wait_for_timeout(400); check(pg.evaluate(OPEN) == [], "clicking the open section collapses it")
    pg.focus(f'#side .blk[data-dom="{dom_pdd}"] .nm'); pg.keyboard.press("Enter"); pg.wait_for_timeout(400); check(pg.evaluate(OPEN) == [dom_pdd], "a heading opens from the keyboard with Enter")
    pg.keyboard.press("Space"); pg.wait_for_timeout(400); check(pg.evaluate(OPEN) == [], "and closes with Space")
    h_closed = pg.evaluate("document.querySelector('#side .acc').getBoundingClientRect().height")
    pg.evaluate("document.querySelectorAll('#side .blk').forEach(b=>b.classList.add('open'))"); pg.wait_for_timeout(450); h_all = pg.evaluate("document.querySelector('#side .acc').getBoundingClientRect().height")
    check(h_closed < 0.35 * h_all and h_closed < 300, f"collapsed, the list is {h_closed:.0f} px tall, against {h_all:.0f} px with every section open")
    go("#t/pdd"); sc = pg.evaluate("(()=>{const s=document.querySelector('#side'); return [s.scrollHeight, s.clientHeight]})()"); check(sc[0] <= sc[1] + 2 or sc[0] < 1.6 * sc[1], f"with the current section open the list fits the page, or nearly: {sc}")
    # ---- the other pages
    go("#ref"); check(pg.evaluate(OPEN) == [], "other pages start with every section collapsed")
    go("#d3"); check(pg.evaluate("location.hash") == "#t/" + pg.evaluate("topicsOfDom(3)[0].id") and pg.evaluate(OPEN) == [3], "a domain address opens its first topic, with that section open in the list")
    go("#d6"); check(pg.evaluate("location.hash") == "#home", "a domain with no topics goes Home")
    # ---- a topic list is never shown twice on one page
    for h in ("#home", "#ref", "#t/pdd", "#t/pdd/c", "#t/pdd/q", "#mix"):
        go(h); side_n = pg.evaluate("[...document.querySelectorAll('#side a.wk')].filter(a=>a.getClientRects().length>0&&getComputedStyle(a).visibility==='visible').length"); main_n = pg.evaluate("document.querySelectorAll('#main a.w').length")
        check(not (side_n and main_n), f"{h}: the topics are listed in one place only, the left list ({side_n} shown) or the page ({main_n} rows)")
    for h in ("#t/pdd", "#t/pdd/c", "#t/pdd/q", "#home"):
        go(h); check(pg.evaluate("getComputedStyle(document.querySelector('#side')).display") != "none", f"{h}: the left list is shown")
    # ---- the linac is the total progress through the course, not progress on one page
    def fresh():
        q = b.new_context(viewport={"width": 1280, "height": 900}, color_scheme="light").new_page(); q.on("pageerror", lambda e: errs.append(str(e))); return q
    def vgo(q, h): q.goto(U + "#ref"); q.goto(U + h); q.wait_for_timeout(350)
    num = lambda q: float(q.locator("#side .lp b").inner_text().rstrip("%"))
    pp = fresh(); vgo(pp, "#t/pdd")
    W = pp.evaluate("DATA.topics.reduce((a,t)=>a+t.words,0)"); w_pdd = pp.evaluate("topic('pdd').words"); w_tmr = pp.evaluate("topic('tmr').words"); NC = pp.evaluate("allFlash().length"); NQ = pp.evaluate("DATA.cards.filter(c=>c.opts).length+MUC().length")      # the MU cases count with the questions
    check(pp.locator("#side .lp").count() == 1 and pp.locator("#side .lp svg .gantry").count() == 1 and pp.locator("#side .lp span").inner_text() == "of the course", "a chapter shows the linac at the top of the list, labelled as the share of the course")
    check(num(pp) == 0 and pp.evaluate(VAL) == 0, "with nothing read, the course progress is 0")
    exp = lambda f, extra=0.0: round(100 * ((w_pdd / W) * f + extra) / 3, 1)
    seen = []
    for f in (0.5, 1.0, 0.25):
        pp.evaluate("f=>window.scrollTo(0,(document.documentElement.scrollHeight-innerHeight)*f)", f); pp.wait_for_timeout(900); seen.append(num(pp))
    check(abs(seen[0] - exp(0.5)) <= 0.1 and abs(seen[1] - exp(1.0)) <= 0.1, f"reading half of a chapter and then all of it adds its share of the course: {seen[:2]} against {exp(0.5)} and {exp(1.0)} ({w_pdd} of {W} words, a third for the chapters)")
    check(seen[2] == seen[1], f"scrolling back up does not lower the total {seen}")
    tip = pp.evaluate("document.querySelector('#side .lp').title"); check("Chapters read" in tip and "flash cards seen" in tip and "questions answered" in tip, f"hovering the linac gives the breakdown: {tip!r}")
    ang = pp.evaluate("gantryAngle(document.querySelector('#side .lp .gantry'))"); check(abs(ang - 180 * (exp(1.0) / 100)) <= 1.2, f"the gantry turns with the total, half a turn at 100% ({ang})")
    vgo(pp, "#t/tmr"); start = num(pp); check(start == seen[1], f"the total carries over to the next chapter instead of starting again: {start}")
    pp.evaluate("window.scrollTo(0,document.documentElement.scrollHeight)"); pp.wait_for_timeout(900); both = num(pp); check(abs(both - round(100 * ((w_pdd + w_tmr) / W) / 3, 1)) <= 0.1, f"a second chapter adds its own share: {both}")
    pp.reload(); pp.wait_for_timeout(500); check(num(pp) == both, "the total survives a reload")
    # ---- flash cards and questions count toward it too
    pc = fresh(); vgo(pc, "#t/waves-photons/c"); one = num(pc); check(abs(one - round(100 * (1 / NC) / 3, 1)) <= 0.1 and pc.locator("#side .lp span").inner_text() == "of the course", f"showing a flash card adds a flash card's share of the course ({one}%)")
    pc.evaluate("(n)=>{const o={}; allFlash().slice(0,n).forEach(c=>o[c.id]={s:1}); localStorage.setItem('ro.cards',JSON.stringify(o));}", 100); pc.reload(); pc.wait_for_timeout(500)
    check(abs(num(pc) - 100 * (100 / NC) / 3) <= 0.5, f"100 flash cards seen: {num(pc)}% of the course (shown to the nearest whole number from 10%)")
    pq = fresh(); vgo(pq, "#t/pdd/q"); check(num(pq) == 0, "a question set starts at 0")
    q = pq.locator(".pq").first; q.locator(".opt").first.click(); q.locator(".chk").click(); pq.wait_for_timeout(500)
    check(abs(num(pq) - round(100 * (1 / NQ) / 3, 1)) <= 0.1, f"answering a question moves the linac at once, without leaving the page ({num(pq)}%)")
    pq.goto(U + "#ref"); pq.once("dialog", lambda d: d.accept()); pq.click("#clr"); pq.wait_for_timeout(300); vgo(pq, "#t/pdd"); check(num(pq) == 0 and pq.evaluate("localStorage.getItem('ro.read')") in ("{}", None), "Clear on the Reference page resets the chapters read as well")
    go("#mix"); check(pg.locator("#side .lp").count() == 1, "the mixed deck has the linac too")
    for h in ("#home", "#ref"): go(h); check(pg.locator(".lp").count() == 0, f"{h} has no progress linac")
    # ---- a phone: a sticky bar with the linac and the jump menu
    pm = b.new_context(viewport={"width": 390, "height": 800}, has_touch=True, is_mobile=True).new_page(); pm.on("pageerror", lambda e: errs.append(str(e)))
    pm.goto(U + "#ref"); pm.goto(U + "#t/pdd"); pm.wait_for_timeout(400)
    check(pm.locator("#lpm .lp").is_visible() and not pm.locator("#side").is_visible() and pm.locator("#side .lp").count() == 1, "on a phone the linac sits in the bar at the top, and the list is not shown")
    pm.evaluate("window.scrollTo(0,document.documentElement.scrollHeight)"); pm.wait_for_timeout(900)
    top = pm.evaluate("Math.round(document.querySelector('.topbar-m').getBoundingClientRect().top)"); txt = pm.locator("#lpm .lp b").inner_text(); side_txt = pm.evaluate("document.querySelector('#side .lp b').textContent")
    check(0 <= top <= 2 and txt == side_txt and float(txt.rstrip("%")) > 0, f"the bar stays at the top while scrolling and shows the same total as the list ({txt}, bar top {top})")
    bw = pm.evaluate("(()=>{const b=document.querySelector('.topbar-m'); return [document.documentElement.scrollWidth, innerWidth, b.scrollWidth, b.clientWidth]})()"); check(bw[0] <= bw[1] and bw[2] <= bw[3] + 1, f"the bar fits a 390 px phone {bw}")
    pm.goto(U + "#ref"); pm.goto(U + "#t/pdd/c/4"); pm.wait_for_timeout(400); check(pm.evaluate("document.querySelector('#lpm b').getBoundingClientRect().height") < 24, "the percentage stays on one line in the bar")
    pm.goto(U + "#ref"); pm.goto(U + "#home"); pm.wait_for_timeout(300); check(pm.locator("#lpm .lp").count() == 0 and pm.evaluate("getComputedStyle(document.querySelector('.topbar-m')).position") != "sticky", "Home on a phone has no bar of its own to keep at the top")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"sidebar: {n} checks"); print("sidebar: PASS" if not bad else f"sidebar: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
