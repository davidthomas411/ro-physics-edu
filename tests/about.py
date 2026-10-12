"""The About page (browser): every section, the counts, the citation texts and their copy buttons, the links, the privacy section, the placeholders in a development build,
the link from the Reference page, and five header tabs. Builds the page with a made-up complete configuration, so it does not depend on site_config.json."""
import datetime, os, re, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _release as R
ROOT = R.ROOT
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import siteinfo as A, analytics_schema as AS

bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)

rc, out, FULL = R.build();                                  assert rc == 0, out
rc, out, OFF = R.build(dict(analytics_mode="none"));        assert rc == 0, out
rc, out, DEV = R.build(release=False, base=A.load_config()); assert rc == 0, out
cfg = dict(R.FULL); top = A.changelog()[0]
SECS = [("about-what", "What this is"), ("about-authors", "Authors and acknowledgments"), ("about-version", "Version"), ("about-cite", "How to cite"), ("about-license", "License"), ("about-basis", "Content basis"),
        ("about-images", "Images"), ("about-ai", "AI assistance"), ("about-use", "Use and limits"), ("about-privacy", "Privacy and data"), ("about-changelog", "Changelog")]
sha = (os.environ.get("GITHUB_SHA") or subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(ROOT)).stdout.strip())[:7]
CLIP = "Object.defineProperty(navigator,'clipboard',{value:{writeText:async t=>{window.__copied=t;}},configurable:true});"

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    def open_page(path, hash_, w=1280, h=900, scheme="light"):
        ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme); ctx.add_init_script(CLIP); ctx.route("http://127.0.0.1:8099/**", lambda r: r.fulfill(status=204)); pg = ctx.new_page(); errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(path.resolve().as_uri() + hash_); pg.wait_for_timeout(300); return ctx, pg, errs

    SECT = "(id=>{let t='',e=document.getElementById(id).nextElementSibling; while(e&&e.tagName!=='H2'){t+=e.innerText+'\\n'; e=e.nextElementSibling;} return t;})"
    # ---------------------------------------------------------------- release build with a complete configuration
    ctx, pg, errs = open_page(FULL, "#about")
    sect = lambda i: pg.evaluate(SECT + "('%s')" % i)
    check(pg.locator("h1").inner_text() == "About and how to cite", "the page title is 'About and how to cite'")
    ids = pg.evaluate("[...document.querySelectorAll('.about h2')].map(h=>[h.id,h.textContent])")
    check(ids == [list(x) for x in SECS], f"the 11 sections are there, in order: {ids}")
    check(all(pg.locator("#" + i).is_visible() for i, _ in SECS), "every section heading is visible")
    toc = pg.evaluate("[...document.querySelectorAll('nav.toc a')].map(a=>a.textContent)"); check(toc == [t for _, t in SECS], f"the contents list names the sections: {toc}")
    # counts
    text = pg.inner_text("#about-what + p"); m = re.search(r"It has ([\d,]+) chapters, ([\d,]+) flash cards, and ([\d,]+) questions", text)
    js = pg.evaluate("[DATA.topics.length, DATA.cards.filter(c=>!c.opts).length, DATA.cards.filter(c=>c.opts).length]")
    check(m and [int(x.replace(",", "")) for x in m.groups()] == js, f"the counts match the data: page {m.groups() if m else text[:80]}, data {js}")
    check("radiation oncology residents" in text and "ABR Medical Physics for Radiation Oncology" in text and "seven ABR content domains" in text, "section 1 names the purpose, the audience, and the domains")
    # authors and acknowledgments
    sec2 = sect("about-authors")
    for a in cfg["authors"]: check(a["given_names"] in sec2 and a["family_names"] in sec2 and a["affiliation"] in sec2 and a["role"] in sec2, f"the author {a['family_names']} is listed with affiliation and role")
    check(all(pg.locator(f'a[href="https://orcid.org/{a["orcid"]}"]').count() == 1 for a in cfg["authors"]), "each ORCID links to orcid.org")
    check("Grace Hopper" in sec2 and "Lectures that gave the first list of topics" in sec2, "the acknowledgments are listed")
    check("Marie Curie" in sec2 and "reviewed 2026-10-01" in sec2 and "Chapters on the basic physics" in sec2, "the physics reviewer is listed with the review date and scope")
    # version
    kv = pg.evaluate("Object.fromEntries([...document.querySelectorAll('#about-version ~ table.kv tr')].slice(0,4).map(r=>[r.cells[0].textContent,r.cells[1].textContent]))")
    check(kv.get("Version") == top["version"], f"the version is {top['version']}: {kv}")
    check(kv.get("Build date") == datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"), f"the build date is today: {kv}")
    check(kv.get("Commit") == sha, f"the commit is {sha}: {kv}")
    check(kv.get("DOI") == cfg["doi"] and pg.locator(f'a[href="https://doi.org/{cfg["doi"]}"]').count() >= 1, f"the DOI is shown and links to doi.org: {kv}")
    # citations and copy buttons
    want = A.citations(cfg, top["version"], top["date"][:4]); got = {k: pg.inner_text(f"#cite-{k}") for k in ("ama", "apa", "bibtex")}
    check(got == want, f"the citation texts are the ones that src/about.py writes: {got}")
    for k, t in got.items():
        check(cfg["title"] in t and top["version"] in t and "Lovelace" in t and "Babbage" in t and top["date"][:4] in t, f"the {k} citation names the title, the version, the authors, and the year")
    check("[Computer software]" in got["apa"] and got["bibtex"].startswith("@software{") and "doi:10.5281/zenodo.1234567" in got["ama"], "the three formats have their usual form")
    for k in ("ama", "apa", "bibtex"):
        pg.evaluate("window.__copied=null"); pg.click(f'[data-copy="{k}"]'); pg.wait_for_timeout(100)
        check(pg.evaluate("window.__copied") == got[k] and pg.inner_text(f'[data-copy="{k}"]') == "Copied", f"the {k} copy button returns the text shown")
    pg.wait_for_timeout(2000); check(pg.inner_text('[data-copy="ama"]') == "Copy", "a copy button goes back to Copy")
    # license and third-party table
    lic = sect("about-license")
    repo = cfg["repository_url"]
    check(pg.locator(f'a[href="{repo}/blob/main/LICENSE"]').count() == 1 and pg.locator(f'a[href="{repo}/blob/main/LICENSE-CONTENT.md"]').count() == 1, "the code and content licenses link to their files")
    check("MIT" in lic and "CC BY 4.0" in lic and "Third-party material keeps its own terms" in lic, "the license section names both licenses")
    rows = pg.evaluate("(()=>{const o=[]; let e=document.getElementById('about-license').nextElementSibling; while(e&&e.tagName!=='H2'){e.querySelectorAll('tr').forEach(r=>o.push([...r.cells].map(c=>c.textContent))); e=e.nextElementSibling;} return o.slice(1);})()")
    notes = [r for r in A.notices() if not r["status"].startswith("Not part of the site") and not r["what"].startswith("TCIA collection") and r["confirm"] != "photos"]   # the photographs row shows only when a chapter uses a photo
    check(len(rows) == len(notes) + 1 + sum(r[0].startswith("Photographs") for r in rows) and any("OpenKBP" in r[0] for r in rows) and any("NIST" in r[0] for r in rows) and any("Collections of The Cancer Imaging Archive" in r[0] for r in rows), f"the third-party table lists the sources in THIRD_PARTY_NOTICES.md ({len(rows)} rows)")
    check(all(len(r) == 3 and all(c.strip() for c in r) for r in rows), "every cell of the third-party table is filled")
    # content basis, images, AI, use
    s6, s7, s8, s9 = sect("about-basis"), sect("about-images"), sect("about-ai"), sect("about-use")
    check("not affiliated with or endorsed by the ABR, AAPM, ASTRO, or the publisher" in s6 and "Ford" in s6 and "AAPM reports" in s6 and "own words" in s6, "the content basis names the sources and says there is no affiliation")
    names = pg.evaluate("DATA.real.sources.map(s=>s.collection)"); check(all(c in s7 for c in names) and "OpenKBP" in s7 and "ICBM152" in s7 and "simulated" in s7, "the images section names every real data set and says that computed images are simulated")
    check("Claude" in s8 and "Claude Code" in s8 and "Anthropic" in s8 and "Faculty reviewed" in s8 and "automated tests" in s8.lower(), "the AI assistance statement")
    check("education only" in s9.lower() and "Not for clinical decisions" in s9, "the limits statement")
    check(pg.locator(f'a[href="{repo}/issues"]').count() == 1 and pg.locator(f'a[href="mailto:{cfg["contact_email"]}"]').count() == 1, "the issues link and the contact email are the configured ones")
    # privacy section, generated from the event schema, with the study block
    priv = sect("about-privacy")
    check("There are no accounts" in priv and "stored only in this browser" in priv and "Clear" in priv, "the privacy section says there are no accounts and where progress is kept")
    shown = pg.evaluate("[...document.querySelectorAll('#about-privacy ~ .tblwrap tr')].slice(1).map(r=>[r.cells[0].textContent, [...r.cells[2].querySelectorAll('b')].map(x=>x.textContent)])")
    check({e: sorted(p) for e, p in shown} == {e["name"]: sorted(p["name"] for p in e["props"]) for e in AS.EVENTS}, f"section 10 lists exactly the events and properties of the schema: {shown}")
    check(cfg["study_notice"] in priv and cfg["irb_number"] in priv and pg.locator(f'a[href="{cfg["survey_url"]}"]').count() == 1, "the study notice, the IRB number, and the survey link are shown")
    # changelog
    ch = pg.evaluate("[...document.querySelectorAll('#about-changelog ~ h3')].map(h=>h.textContent)"); check(ch and ch[0] == f"{top['version']}, {top['date']}" and ch == [f"{e['version']}, {e['date']}" for e in A.changelog()], f"the changelog lists the versions newest first: {ch}")
    check(pg.locator("#about-changelog ~ ul li").first.inner_text() == top["items"][0], "the changelog bullets are the text of CHANGELOG.md")
    # house style for what the page shows
    allt = pg.inner_text(".about")
    check("site_config" not in allt and "third_party_confirmed" not in allt and ".py" not in allt, "the page names no internal file or setting")
    check(not re.search(r"\b(you|your|we|our|let's)\b", allt, re.I), "the page addresses no reader and speaks in no first person")
    check(pg.evaluate("document.querySelector('meta[name=robots]')&&document.querySelector('meta[name=robots]').content") == "noindex", "allow_indexing false puts noindex in the page")
    check(A.license_notice(cfg) in pg.inner_text("#main"), "the one-line license notice is on the About page")
    check(not errs, f"no console errors on the About page {errs[:2]}")
    # header tabs and the Reference link
    for h in ("#about", "#ref", "#home", "#t/pdd", "#t/pdd/q", "#mu"):
        pg.goto(FULL.resolve().as_uri() + "#home"); pg.goto(FULL.resolve().as_uri() + h); pg.wait_for_timeout(150)
        check(pg.locator(".tabs a").count() == 5, f"five header tabs on {h}")
    pg.goto(FULL.resolve().as_uri() + "#ref"); pg.wait_for_timeout(150)
    check(pg.locator('.lead a[href="#about"]').count() == 1 and A.license_notice(cfg) in pg.inner_text("#main"), "the Reference page links to About and shows the license notice")
    pg.click('.lead a[href="#about"]'); pg.wait_for_timeout(200)
    check(pg.evaluate("location.hash") == "#about" and pg.locator(".tabs a.on").inner_text() == "Reference" and pg.evaluate("document.getElementById('jump').value") == "#ref", "the link opens About, under the Reference tab")
    ctx.close()
    # ---------------------------------------------------------------- phone width, dark mode
    for scheme in ("light", "dark"):
        ctx, pg, errs = open_page(FULL, "#about", 390, 844, scheme)
        check(pg.evaluate("document.documentElement.scrollWidth") == 390, f"no sideways scroll at 390 px, {scheme}")
        check(not errs and pg.locator("#about-cite").is_visible(), f"the About page opens at 390 px without errors, {scheme}")
        ctx.close()
    # ---------------------------------------------------------------- analytics off: the privacy section says nothing is sent
    ctx, pg, errs = open_page(OFF, "#about"); priv = pg.evaluate(SECT + "('about-privacy')")
    check("records no usage data" in priv and "There are no accounts" in priv and pg.locator("#about-privacy ~ .tblwrap").count() == 0, "with analytics off the privacy section says that no usage data are recorded and lists no events")
    check(pg.evaluate("ANALYTICS") is None and "IRB protocol: IRB-TEST-0001" in priv, "analytics off: no collector in the page, and the study block still shows"); ctx.close()
    # ---------------------------------------------------------------- development build with the real configuration: placeholders are visible
    ctx, pg, errs = open_page(DEV, "#about"); miss = pg.evaluate("[...document.querySelectorAll('.about .miss')].map(e=>e.textContent)")
    expect = ("author names", "acknowledgments", "physics reviewers", "contact email", "DOI", "set by the release build")
    check(all(any(e in m for m in miss) for e in expect), f"missing values show as visible placeholders: {miss}")
    check(pg.locator(".about .miss").first.evaluate("e=>getComputedStyle(e).color") != pg.locator(".about p").first.evaluate("e=>getComputedStyle(e).color"), "a placeholder is drawn in the warning color")
    check(pg.evaluate("ANALYTICS") is None, "a development build never carries a collector")
    check(not errs, f"no console errors in the development build {errs[:2]}"); ctx.close()
    b.close()
print(f"about: {n} checks, {len(bad)} failed"); sys.exit(1 if bad else 0)
