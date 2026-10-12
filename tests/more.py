"""'Show more details' and 'Explain further': every explanation is attached to exactly one question or section, its numbers match the answer, and the buttons work (right and wrong answers, reset, the question-only page, and a phone)."""
import sys, os, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import more_content as MC
from playwright.sync_api import sync_playwright
plain = lambda s: re.sub(r"<[^>]+>", " ", s)
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri(); bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
LET = "ABCDEFG"; T = {t["id"]: t for t in TOPICS}
# ---------------------------------------------------------------- static: what is attached to what
with_more = [(t["id"], k, p) for t in TOPICS for k, p in enumerate(t["problems"], 1) if p.get("more")]
entries = sum(1 for tid, v in MC.QM.items() for e in v if any(MC.plain(p.get("stem0", p["q"])).startswith(e["start"]) for p in T[tid]["problems"]))      # an explanation whose question was removed is held and not counted
check(len(with_more) == entries and entries > 0, f"every one of the {entries} question explanations is attached to exactly one question")
blocks = [(t["id"], b) for t in TOPICS for b in t["guide"] if b[0] == "more"]
check(len(blocks) == sum(len(v) for v in MC.GM.values()) and blocks, f"every one of the {len(blocks)} chapter explanations sits at the end of its section")
for tid, b in blocks:
    g = T[tid]["guide"]; i = g.index(b); prev = [x for x in g[:i] if x[0] == "h2"]; nxt = g[i + 1] if i + 1 < len(g) else None
    check(prev and (nxt is None or nxt[0] == "h2") and b[1] and len(plain(b[2] or "").split()) >= 20, f"{tid}: '{b[1]}' follows the text of '{plain(prev[-1][1]).strip()}', before the next heading, and begins with a plain-language restatement")
words = [len(plain(p["more"]).split()) for _, _, p in with_more]
check(min(words) >= 25 and max(words) <= 260, f"each question explanation is a sensible length ({min(words)} to {max(words)} words)")
check(all(plain(p["more"]).strip() != plain(p["a"][1]).strip() for _, _, p in with_more) and not any("plainer" in p["more"] for _, _, p in with_more), "each explanation says more than the short explanation already shown, and none is introduced with a label about its own simplicity")
d1 = [(t["id"], k) for t in TOPICS if t["domain"] == 1 for k, p in enumerate(t["problems"], 1)]; d1m = [(t["id"], k) for t in TOPICS if t["domain"] == 1 for k, p in enumerate(t["problems"], 1) if p.get("more")]
check(len(d1) == len(d1m), f"every one of the {len(d1)} Basic physics questions has an Explain further button ({len(d1m)} have)")
worst = 0.0; nchk = 0
for (tid, start), val in MC.CHECKS.items():
    p = next((x for x in T[tid]["problems"] if MC.plain(x["q"]).startswith(start)), None)
    if p is None: continue                                                                    # the question was removed
    if p.get("kind") != "num" and not p.get("vals"): bad.append(("a numeric explanation is attached to a question without a number", tid, start)); print("FAIL", tid, start); continue
    right = p["ans"] if p.get("kind") == "num" else p["vals"][LET.index(p["key"][0])]
    worst = max(worst, abs(val - right) / abs(right)); nchk += 1
check(nchk > 0 and worst < 0.005, f"the number each calculation reaches is the answer of its question, for all {nchk} numeric explanations (worst difference {100 * worst:.3f}%)")
# ---------------------------------------------------------------- browser
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    def go(h): pg.goto(U + "#ref"); pg.goto(U + h); pg.wait_for_timeout(300)
    tid = "particles-energy"; go(f"#t/{tid}")
    ids = {p["more"]: k for _, k, p in with_more if _ == tid}; n_with = pg.locator(".pq:has(.more)").count(); mine = len([1 for x in with_more if x[0] == tid])
    check(n_with == mine, f"the chapter shows an Explain further button on exactly the {mine} questions that have an explanation, inside their feedback")
    q = pg.locator(".pq", has_text="What is the total energy, including rest energy, of an electron").first
    check(not q.locator(".more-btn").is_visible(), "the button is hidden until the question is answered")
    key = q.get_attribute("data-key"); wrong = next(o for o in q.locator(".opt").all() if o.get_attribute("data-k") != key)
    wrong.click(); q.locator(".chk").click(); pg.wait_for_timeout(150)
    btn = q.locator(".more-btn"); check(btn.is_visible() and btn.inner_text() == "Explain further" and q.locator(".more.wrong").count() == 1 and btn.get_attribute("aria-expanded") == "false" and not q.locator(".more-body").is_visible(), "after a wrong answer, Explain further appears, emphasised, and the explanation is still closed")
    check(pg.evaluate("(()=>{const b=document.querySelector('.pq .more.wrong .more-btn'); const s=getComputedStyle(b); return s.backgroundColor!==getComputedStyle(document.body).backgroundColor})()"), "after a wrong answer the button is visibly emphasised (filled)")
    btn.click(); pg.wait_for_timeout(100); body = q.locator(".more-body")
    check(body.is_visible() and "How the calculation is done" in body.inner_text() and "2.511" in body.inner_text() and btn.inner_text() == "Hide explanation" and btn.get_attribute("aria-expanded") == "true", "clicking opens the plain-language restatement and the calculation steps, and the button offers to hide them")
    btn.click(); check(not body.is_visible() and btn.inner_text() == "Explain further", "clicking again closes it")
    q.locator(".again").click(); pg.wait_for_timeout(100); check(not q.locator(".fb").is_visible(), "Try again closes the feedback")
    right = next(o for o in q.locator(".opt").all() if o.get_attribute("data-k") == key); right.click(); q.locator(".chk").click(); pg.wait_for_timeout(100)
    check(q.locator(".more-btn").is_visible() and q.locator(".more.wrong").count() == 0 and not q.locator(".more-body").is_visible() and q.locator(".more-btn").inner_text() == "Explain further", "after a right answer the button is still offered, not emphasised, and starts closed")
    go("#t/kerma-dose"); bare = len([p for p in T["kerma-dose"]["problems"] if not p.get("more")])
    check(bare > 0 and pg.locator(".pq:not(:has(.more))").count() == bare and pg.locator(".pq:not(:has(.more)) .more-btn").count() == 0, f"a question without an explanation has no button ({bare} in this chapter)")
    go(f"#t/{tid}")
    # ---- the chapter section
    sec = pg.locator(".more").filter(has=pg.locator(".mh", has_text="Using the relativistic formulas")).first; mb = sec.locator(".more-btn")
    check(mb.is_visible() and not sec.locator(".more-body").is_visible() and mb.get_attribute("aria-expanded") == "false", "a chapter section offers Show more details, closed")
    mb.click(); pg.wait_for_timeout(100); body = sec.locator(".more-body")
    check(body.is_visible() and "Using the relativistic formulas" in body.inner_text() and body.locator("table").count() == 1 and mb.inner_text() == "Hide details", "it opens a plain-language restatement, the steps, and a table, and the button offers to hide them")
    mb.focus(); pg.keyboard.press("Enter"); pg.wait_for_timeout(80); check(not body.is_visible(), "the button works from the keyboard")
    # ---- the question-only page
    go(f"#t/{tid}/q"); q2 = pg.locator(".pq", has_text="What is the total energy, including rest energy, of an electron").first; key = q2.get_attribute("data-key")
    check(q2.locator(".fb").is_visible() and q2.locator(".more-btn").is_visible() and q2.locator(".more.wrong").count() == 0, "an answered question comes back with its feedback and its Explain further button on the questions-only page")
    q2.locator(".again").click(); pg.wait_for_timeout(80)
    next(o for o in q2.locator(".opt").all() if o.get_attribute("data-k") != key).click(); q2.locator(".chk").click(); pg.wait_for_timeout(100); q2.locator(".more-btn").click(); pg.wait_for_timeout(80)
    check(q2.locator(".more-body").is_visible() and q2.locator(".more.wrong").count() == 1, "the questions-only page has the same button, emphasised after a wrong answer")
    # ---- the other kinds of question
    go("#t/nuclear-structure"); s = pg.locator(".pq.sortq", has_text="Is each pair of nuclides isotopes, isotones, isobars, or isomers?").first
    for _ in range(s.locator(".chip").count()):
        s.locator(".tray .chip").first.click(); s.locator('.bin[data-b="0"] .bh').click()
    s.locator(".chk").click(); pg.wait_for_timeout(150)
    check(s.locator(".more.wrong").count() == 1 and s.locator(".more-btn").is_visible() and not s.locator(".more-body").is_visible(), "a sorting question gets the emphasised button after a wrong answer")
    s.locator(".more-btn").click(); pg.wait_for_timeout(80); check(s.locator(".more-body").is_visible() and "How to decide" in s.locator(".more-body").inner_text(), "it opens the rule for each pair under the heading How to decide")
    go("#t/decay-law"); nq = pg.locator(".pq.numq", has_text="A Co-60 source with").first
    nq.locator(".numin").fill("1"); nq.locator(".chk").click(); pg.wait_for_timeout(120)
    check(nq.locator(".more.wrong").count() == 1 and nq.locator(".more-btn").is_visible(), "a typed-number question gets the emphasised button after a wrong answer")
    nq.locator(".more-btn").click(); pg.wait_for_timeout(80); check("1.8975" in nq.locator(".more-body").inner_text() and "26.84" in nq.locator(".more-body").inner_text(), "it shows the calculation with that question's numbers")
    nq.locator(".again").click(); nq.locator(".numin").fill("26.84"); nq.locator(".chk").click(); pg.wait_for_timeout(120); check(nq.locator(".more.wrong").count() == 0 and nq.locator(".more-btn").is_visible(), "after a right typed answer the button is offered without emphasis")
    go("#t/photon-interactions"); fq = pg.locator(".pq.figq", has_text="thickness that leaves one eighth").first; fq.scroll_into_view_if_needed(); svg = fq.locator(".fgb svg").first; bx = svg.bounding_box()
    svg.click(position={"x": bx["width"] * 0.25, "y": bx["height"] * 0.45}); pg.wait_for_timeout(100); fq.locator(".chk").click(); pg.wait_for_timeout(150)
    check(fq.locator(".more.wrong").count() == 1 and fq.locator(".more-btn").is_visible(), "a tap-the-figure question gets the emphasised button after a wrong tap")
    # ---- a phone
    pm = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True).new_page(); pm.on("pageerror", lambda e: errs.append(str(e)))
    pm.goto(U + "#ref"); pm.goto(U + f"#t/{tid}"); pm.wait_for_timeout(300); pm.locator(".more").filter(has=pm.locator(".mh", has_text="Using the relativistic formulas")).first.locator(".more-btn").click(); pm.wait_for_timeout(100)
    q3 = pm.locator(".pq", has_text="What is the total energy, including rest energy, of an electron").first; key = q3.get_attribute("data-key"); next(o for o in q3.locator(".opt").all() if o.get_attribute("data-k") != key).click(); q3.locator(".chk").click(); pm.wait_for_timeout(100); q3.locator(".more-btn").click(); pm.wait_for_timeout(100)
    w = pm.evaluate("[document.documentElement.scrollWidth, innerWidth]"); check(w[0] <= w[1], f"with a section and an explanation open, nothing scrolls sideways on a 390 px phone {w}")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"more: {n} checks"); print("more: PASS" if not bad else f"more: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
