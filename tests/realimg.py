"""The real clinical images in the page: every figure builds as one drawing with its caption, shows the stored panels and labels, the buttons switch the views, the images decode at their stored size,
nothing is distorted or outside the drawing, a phone shows no sideways scroll in either theme, and the Reference page lists every source."""
import json, os, re, sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import real
from topics import TOPICS
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ro-physics.html"
U = PAGE.resolve().as_uri(); errors, bad = [], []; n = 0
def check(c, m):
    global n; n += 1
    print(("ok   " if c else "FAIL ") + m)
    if not c: bad.append(m)
place = {b[1]: t["id"] for t in TOPICS for b in t["guide"] if b[0] == "avf" and b[1].startswith("real-")}
plain = lambda s: re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").strip()
DEC = """async sel => { const out = []; for (const im of document.querySelectorAll(sel + ' svg image')) { out.push(await new Promise(r => { const m = new Image(); m.onload = () => r([m.naturalWidth, m.naturalHeight]); m.onerror = () => r(null); m.src = im.getAttribute('href'); })); } return out; }"""
GEO = """sel => { const s = document.querySelector(sel + ' svg'), vb = s.viewBox.baseVal, r = []; for (const im of s.querySelectorAll('image')) r.push([+im.getAttribute('x'), +im.getAttribute('y'), +im.getAttribute('width'), +im.getAttribute('height')]); return {vb: [vb.width, vb.height], img: r, texts: [...s.querySelectorAll('text')].map(t => t.textContent)}; }"""
def expected_texts(v): return [t for p in v["panels"] for t in (p.get("label"), p.get("sub")) if t]
def check_view(pg, sel, f, v, k):
    g = pg.evaluate(GEO, sel); hrefs = [i.get_attribute("href") for i in pg.locator(sel + " svg image").all()]
    check(hrefs == [p["img"] for p in v["panels"]] and g["texts"] == expected_texts(v), f"{f}: view '{v['label']}' draws its {len(v['panels'])} panels with their labels in order")
    ok = len(g["img"]) == len(v["panels"]) and all(x >= 0 and y >= 0 and x + w <= g["vb"][0] + 0.01 and y + h <= g["vb"][1] + 0.01 for x, y, w, h in g["img"])
    check(ok and all(abs((w / h) / (p["w"] / p["h"]) - 1) < 0.01 for (x, y, w, h), p in zip(g["img"], v["panels"])), f"{f}: '{v['label']}' lies inside the drawing and keeps the aspect ratio of every image")
    dec = pg.evaluate(DEC, sel); check(dec == [[p["w"], p["h"]] for p in v["panels"]], f"{f}: '{v['label']}' images decode in the browser at their stored size {dec[:2]}")
    if v.get("facts"): check(plain(pg.locator(sel + " output.avo").inner_text()) == plain(v["facts"]).replace(" ", " ") or plain(v["facts"]) in plain(pg.locator(sel + " output.avo").inner_html()), f"{f}: '{v['label']}' shows its facts")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    for tag, vw, scheme in (("desktop, light", 1280, "light"), ("phone, light", 390, "light"), ("phone, dark", 390, "dark")):
        ctx = b.new_context(viewport={"width": vw, "height": 900}, color_scheme=scheme); pg = ctx.new_page()
        pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        for tid in sorted(set(place.values())):
            pg.goto(U + "#ref"); pg.goto(U + f"#t/{tid}"); pg.wait_for_timeout(450)
            sw = pg.evaluate("document.documentElement.scrollWidth"); check(sw <= vw, f"{tag}: #t/{tid} has no sideways scroll ({sw} of {vw} px)")
            for fid in [i for i, t in place.items() if t == tid]:
                f = real.FIGS[fid]; sel = f'figure.av[data-av="{fid}"]'; fig = pg.locator(sel); fig.scroll_into_view_if_needed(); pg.wait_for_timeout(120)
                if tag != "desktop, light":                                                                       # the full check once; the phone runs check that the figure still draws
                    check(fig.locator("svg image").count() == len(f["views"][0]["panels"]) and fig.locator("figcaption").inner_text().strip() != "", f"{tag}: {fid} draws"); continue
                check(fig.locator("svg").count() == 1 and plain(fig.locator("figcaption").inner_text()) == plain(f["cap"]), f"{fid}: one drawing, and its caption is the stored caption")
                check(fig.locator("svg").get_attribute("role") == "img" and fig.locator("svg").get_attribute("aria-label") == f["label"], f"{fid}: the drawing has its description")
                vs = f["views"]; btns = fig.locator("button")
                check(btns.count() == (len(vs) if len(vs) > 1 else 0), f"{fid}: {len(vs)} view(s), so {btns.count()} button(s)")
                check_view(pg, sel, fid, vs[0], 0)
                if len(vs) > 1:
                    seen = set()
                    for k, v in enumerate(vs):
                        btns.nth(k).click(); pg.wait_for_timeout(60); check_view(pg, sel, fid, v, k); seen.add(pg.locator(sel + " svg image").first.get_attribute("href"))
                        check(btns.nth(k).get_attribute("aria-pressed") == "true" and fig.locator("button[aria-pressed='true']").count() == 1 and btns.nth(k).inner_text() == v["label"], f"{fid}: the button '{v['label']}' is the one pressed")
                    check(len(seen) == len(vs), f"{fid}: each view shows different images")
        ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(U + "#ref"); pg.wait_for_timeout(400); items = pg.locator("ul.realsrc li")
    check(items.count() == len(real.SOURCES), f"Reference: {len(real.SOURCES)} sources are listed (found {items.count()})")
    for k, s in enumerate(real.SOURCES):
        li = items.nth(k); a = li.locator("a").first
        check(a.get_attribute("href") == f"https://doi.org/{s['doi']}" and s["license"] in li.inner_text() and s["citation"][:40] in li.inner_text(), f"Reference: {s['collection']} has its DOI link, licence, and citation")
        for fid in s["figs"]: check(li.locator(f'a[href="#t/{place[fid]}"]').count() == 1, f"Reference: {s['collection']} links to the chapter with {fid}")
    sw = pg.evaluate("document.documentElement.scrollWidth"); check(sw <= 390, f"Reference at 390 px has no sideways scroll ({sw})")
    b.close()
check(not errors, f"no console or page errors {errors[:2]}")
print(f"realimg: {n} checks"); print("realimg: PASS" if not bad else f"realimg: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
