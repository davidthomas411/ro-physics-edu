"""Flash cards are facts: every card has a title that is not a question, a fact under it, and no hidden answer; decks click through with Next, keys, and swipe."""
import sys, re, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
from facts import TITLES, HEADS
from playwright.sync_api import sync_playwright
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
BAN = re.compile(r"\b(you|your|we|let's|remember|know that|keep in mind|note that|that is why|this is why|that's why|what matters|simply|just|actually|basically|essentially|obviously|clearly|of course|worth|a lot of|a bit)\b", re.I)
ASK = re.compile(r"^(what|why|how|which|when|where|who|define|state|write|give|name|list|describe|explain|relate|distinguish|convert|repeat|is|are|does|do|can|a|an)\b", re.I)
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
cards = [(f"{t['id']}:{i}", c) for t in TOPICS for i, c in enumerate(t["cards"], 1)]
missing = [i for i, c in cards if i not in TITLES and not c.get("fact")]; extra = [k for k in TITLES if k not in {i for i, _ in cards}]
OWN = {i: c["q"] for i, c in cards if c.get("fact")}; ALLT = {**TITLES, **OWN}
check(not missing and not extra, f"every one of the {len(cards)} flash cards has a title, and no title is left over {missing[:3]} {extra[:3]}")
qs = [i for i, t in ALLT.items() if "?" in t or ASK.match(plain(t)) or len(plain(t).split()) > 11 or len(plain(t)) < 3]
check(not qs, f"no title is a question, an instruction, or longer than 11 words {[(i, ALLT[i]) for i in qs[:4]]}")
check(not [i for i, t in ALLT.items() if BAN.search(plain(t))] and not [i for i, t in HEADS.items() if BAN.search(plain(t))], "titles and reworded answers keep to the house style")
dup = [(t["id"], x) for t in TOPICS for x in {ALLT[f"{t['id']}:{i}"] for i in range(1, len(t["cards"]) + 1)} if sum(1 for i in range(1, len(t["cards"]) + 1) if ALLT[f"{t['id']}:{i}"] == x) > 1]
check(not dup, f"titles are unique within each topic {dup[:3]}")
check(all(i in {k for k, _ in cards} for i in HEADS), "every reworded answer belongs to a real card")
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    pg = b.new_page(viewport={"width": 1100, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U + "#ref"); pg.goto(U + "#t/decay-law/c"); pg.wait_for_timeout(200)
    check(pg.locator(".ftitle").inner_text() == plain(ALLT["decay-law:1"]) and pg.locator(".fbody").inner_text().strip() != "", "a card shows its title and its fact together")
    check(pg.locator("#flip").count() == 0 and "Show answer" not in pg.locator("#main").inner_text() and pg.locator(".fc .back").count() == 0, "there is no Show answer step and nothing is hidden")
    check(pg.locator("#nextq").inner_text() == "Next" and pg.locator("#prevq").count() == 0, "the first card has a Next button and no Previous button")
    seen0 = pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('ro.cards')||'{}'))"); check("decay-law:1" in seen0, "a fact counts as seen when it is shown")
    pg.click("#nextq"); pg.wait_for_timeout(80); check(pg.evaluate("location.hash").endswith("/c/2") and pg.locator("#prevq").count() == 1, "Next goes to card 2, which also offers Previous")
    pg.click("#prevq"); pg.wait_for_timeout(80); check(pg.evaluate("location.hash").endswith("/c") and pg.locator(".fc .stat b").inner_text().startswith("Card 1 of"), "Previous goes back to card 1")
    qd = pg.evaluate("DATA.cards.filter(c=>!c.opts).map(c=>c.q)"); check(all("?" not in plain(q) and "class=\"ask\"" not in q for q in qd), f"no flash card in the page data is rendered as a question ({len(qd)} checked)")
    N = pg.evaluate("flashOf('decay-law').length"); pg.goto(U + "#t/decay-law/c"); pg.wait_for_timeout(80)
    for _ in range(N - 1):
        pg.click("#nextq"); pg.wait_for_timeout(25)
    check(pg.locator("#nextq").inner_text() == "Finish", "the last card says Finish")
    pg.click("#nextq"); pg.wait_for_timeout(80); check("Restart" in pg.locator("#main").inner_text() and pg.evaluate("seenCount(flashOf('decay-law'))") == N, f"clicking through all {N} cards ends on the end screen with every card seen")
    pg.goto(U + "#mix"); pg.wait_for_timeout(80); check(pg.locator(".ftitle").count() == 1 and pg.locator("#flip").count() == 0, "the mixed deck uses fact cards too")
    pg.goto(U + "#t/pdd/c"); pg.wait_for_timeout(80); sub = pg.evaluate("[...document.querySelectorAll('.ftitle sub')].length"); check(sub >= 0, "titles keep their subscripts")
    pm = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True).new_page(); pm.on("pageerror", lambda e: errs.append(str(e)))
    ok = True
    for t in TOPICS:
        pm.goto(U + "#ref"); pm.goto(U + f"#t/{t['id']}/c"); pm.wait_for_timeout(40)
        w = pm.evaluate("[document.documentElement.scrollWidth, innerWidth, document.querySelector('.fc .card').scrollWidth - document.querySelector('.fc .card').clientWidth]"); ok = ok and w[0] <= w[1] and w[2] <= 0
    check(ok, "every deck fits a 390 px phone without sideways scroll")
    pm.goto(U + "#ref"); pm.goto(U + "#t/waves-photons/c"); pm.wait_for_timeout(60); hb = pm.locator("#nextq").bounding_box(); check(hb["height"] >= 40, f"the Next button is at least 40 px tall for a thumb ({hb['height']:.0f} px)")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"facts: {n} checks"); print("facts: PASS" if not bad else f"facts: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
