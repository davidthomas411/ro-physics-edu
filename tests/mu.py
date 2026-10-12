"""MU calculation module: the engine against an independent Python solver for every case, and the worksheet, checking, solutions, random cases, tables, progress, and phone layout."""
import sys, os, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import mudata as M, mucases, beamdata as bd
from playwright.sync_api import sync_playwright
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri(); bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
# ---------------------------------------------------------------- the reference solver: the same tables, read depth first and then field size, nothing rounded in between
def ref(c):
    T = M.tables(c["E"]); dm = T["dmax"]; ssd = c["tech"] == "SSD"; f = c["f"] if ssd else 100; a, b = c["field"]; sq = 2 * a * b / (a + b); scs = sq * 100 / f if ssd else sq
    def read(depths, rows, d, s): return bd.interp(s, T["sizes"], [bd.interp(d, depths, [r[j] for r in rows]) for j in range(len(T["sizes"]))])
    Sc, Sp = bd.interp(scs, T["sizes"], T["sc"]), bd.interp(sq, T["sizes"], T["sp"])
    DD = read(T["depths"], T["pdd"], c["d"], sq) / 100 if ssd else read(T["tmr_depths"], T["tmr"], c["d"], sq)
    F = (((f + dm) / (f + c["d"])) / ((100 + dm) / (100 + c["d"]))) ** 2 if ssd and f != 100 else 1.0
    dcal = (100 + dm) if c["cal"] == "SSD" else 100; ISF = (dcal / ((f + dm) if ssd else 100)) ** 2
    WF = bd.interp(scs, T["wf_sizes"], T["wf"][c["wedge"]]) if c["wedge"] else 1.0; TF = T["tf"] if c["tray"] else 1.0
    per = Sc * Sp * DD * F * ISF * WF * TF; return dict(Sc=Sc, Sp=Sp, DD=DD, F=F, ISF=ISF, WF=WF, TF=TF, sq=sq, scs=scs, per=per, mu=c["dose"] * c["w"] / per)
cases = mucases.CASES
check(len(cases) == 32 and [c["id"] for c in cases] == list(range(1, 33)), "there are 32 numbered cases")
lv = [c["level"] for c in cases]; check(lv.count("Easy") == 12 and lv.count("Moderate") == 12 and lv.count("Challenging") == 8, f"12 easy, 12 moderate, and 8 challenging cases {lv.count('Easy'), lv.count('Moderate'), lv.count('Challenging')}")
check(all(c["d"] >= M.ENERGY[c["E"]]["dmax"] and 0 < c["d"] <= 30 and all(4 <= x <= 40 for x in c["field"]) for c in cases), "every case lies inside the tables: depth between d_max and 30 cm, field sides between 4 and 40 cm")
check({c["E"] for c in cases} == {6, 10, 15, 18} and {c["tech"] for c in cases} == {"SSD", "SAD"} and any(c["wedge"] for c in cases) and any(c["tray"] for c in cases) and any(c["f"] != 100 for c in cases) and any(c["cal"] == "SAD" for c in cases) and any(c["w"] < 1 for c in cases) and any(c["field"][0] != c["field"][1] for c in cases), "the cases cover every energy, both techniques, wedges, trays, extended SSD, both calibrations, opposed fields, and rectangles")
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    ctx = b.new_context(viewport={"width": 1280, "height": 1000}); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    def go(h): pg.goto(U + "#ref"); pg.goto(U + h); pg.wait_for_timeout(250)
    go("#home")
    # ---- the engine against the reference solver
    js = pg.evaluate("MUC().map(c=>{const o=muSolve(c); return {id:c.id,Sc:o.Sc,Sp:o.Sp,DD:o.ssd?o.DD/100:o.DD,F:o.F,ISF:o.ISF,WF:o.WF,TF:o.TF,sq:o.sq,scs:o.scs,per:o.perMU,mu:o.mu}})")
    worst = {k: 0.0 for k in ("Sc", "Sp", "DD", "F", "ISF", "WF", "TF", "sq", "scs", "per", "mu")}; diffs = []
    for c, o in zip(cases, js):
        r = ref(c)
        for k in worst:
            e = abs(o[k] - r[k]) / max(abs(r[k]), 1e-9); worst[k] = max(worst[k], e)
            if e > (0.002 if k in ("per", "mu", "DD") else 0.0006): diffs.append((c["id"], k, o[k], r[k]))
    check(not diffs, f"the page's engine and the independent solver agree on every factor and every MU for all 32 cases (worst: " + ", ".join(f"{k} {100 * v:.3f}%" for k, v in worst.items() if v > 0) + f") {diffs[:2]}")
    mus = [o["mu"] for o in js]; check(all(40 < m < 1500 for m in mus), f"every MU is a plausible number ({min(mus):.0f} to {max(mus):.0f})")
    # physics relations the engine must obey
    chk = lambda id_: next(o for o in js if o["id"] == id_)
    check(abs(chk(1)["ISF"] - 1.0) < 1e-9 and abs(chk(5)["ISF"] - 1.0302) < 1e-4 and abs(chk(10)["ISF"] - 1.0609) < 1e-4 and abs(chk(12)["ISF"] - 1.0712) < 1e-4, "inverse-square terms: 1 at SSD 100 with an SSD calibration, and (100 + d_max)²/100² for the SAD technique")
    check(abs(chk(22)["ISF"] - (101.5 / 111.5) ** 2) < 1e-4 and abs(chk(23)["ISF"] - (101.5 / 121.5) ** 2) < 1e-4 and abs(chk(23)["scs"] - 10.0) < 1e-6 and abs(chk(23)["sq"] - 12.0) < 1e-6, "SSD 110 and 120: the inverse-square terms, and a 12 × 12 cm field at SSD 120 has a 10 × 10 cm collimator opening")
    check(abs(chk(21)["ISF"] - 1.0) < 1e-9 and abs(chk(30)["ISF"] - (100 / 101.5) ** 2) < 1e-4, "SAD calibration: 1 for the SAD technique, (100/(100 + d_max))² for the SSD technique at 100 cm")
    check(chk(31)["F"] < 1 and chk(31)["ISF"] > 1 and chk(22)["F"] > 1 and chk(22)["ISF"] < 1, "Mayneord F is above 1 at an extended SSD and below 1 at a short one, and the inverse-square term goes the other way")
    check(abs(chk(15)["sq"] - 9.6) < 1e-9 and abs(chk(16)["sq"] - 9.6) < 1e-9, "the equivalent square of 8 × 12 cm is 9.6 cm")
    check(chk(17)["WF"] < 1 and chk(18)["WF"] < 1 and chk(18)["TF"] < 1 and chk(1)["WF"] == 1 and chk(1)["TF"] == 1, "wedge and tray factors are below 1 where they apply and exactly 1 where they do not")
    # ---- the menu and the page
    go("#home"); tabs = pg.evaluate("[...document.querySelectorAll('.tabs a')].map(a=>a.textContent)"); check(tabs == ["Home", "Flash cards", "Questions", "MU calc", "Reference"], f"MU calc is in the top menu {tabs}")
    pg.click('.tabs a[data-tab="mu"]'); pg.wait_for_timeout(300); check(pg.evaluate("location.hash") == "#mu/1" and pg.locator(".tabs a.on").inner_text() == "MU calc" and pg.evaluate("getComputedStyle(document.querySelector('#side')).display") == "none", "the menu item opens the first case, is highlighted, and the page has no left list")
    check(pg.locator(".mc").count() == 32 and pg.locator(".mu-slot").count() == 5 and pg.locator(".mpane").count() == 2, "the page has 32 case buttons, the five entries of an open SSD field, and a PDD pane and a scatter pane")
    # ---- case 1: fill the entries by clicking table cells, type the rest, check
    T = M.tables(6); di = T["depths"].index(5); ci = T["sizes"].index(10); r1 = ref(cases[0])
    pg.click('.mcell[data-slot="DD"][data-r="%d"][data-c="%d"]' % (di, ci)); pg.click('.mtab[data-tab="scat"]'); pg.click('.mcell[data-slot="Sc"][data-r="0"][data-c="%d"]' % ci); pg.click('.mcell[data-slot="Sp"][data-r="1"][data-c="%d"]' % ci)
    check(pg.input_value("#mu-DD") == str(T["pdd"][di][ci]) and pg.input_value("#mu-Sc") == "1.000" and pg.locator('.mcell.pick').count() == 3, f"clicking a table cell fills the matching entry and marks the cell ({pg.input_value('#mu-DD')})")
    pg.fill("#mu-ISF", "1"); pg.fill("#mu-MU", str(round(r1["mu"]))); pg.click("#mu-check"); pg.wait_for_timeout(120)
    check(pg.locator(".mu-slot.good").count() == 5 and pg.locator(".mu-slot.bad").count() == 0 and "All 5 entries are correct" in pg.locator("#mu-fb").inner_text(), f"a correct case is marked right: {pg.locator('#mu-fb').inner_text()!r}")
    check(pg.locator(".mc.on.ok").count() == 1 and json.loads(pg.evaluate("localStorage.getItem('ro.mu')"))["1"]["ok"] is True, "the case is recorded as correct and shows a tick")
    pg.reload(); pg.wait_for_timeout(300); check(pg.locator(".mc.ok").count() == 1, "the tick survives a reload")
    # ---- wrong entries, empty entries, and the percent trap
    go("#mu/2"); pg.click("#mu-check"); pg.wait_for_timeout(100); check("Fill in all" in pg.locator("#mu-fb").inner_text() and json.loads(pg.evaluate("localStorage.getItem('ro.mu')") or "{}").get("2") is None, "checking an empty worksheet asks for every entry and records nothing")
    r2 = ref(cases[1]); vals = {"Sc": "0.5", "Sp": f"{r2['Sp']:.4f}", "DD": "0.837", "ISF": f"{r2['ISF']:.4f}", "MU": "100"}
    for k, v in vals.items(): pg.fill("#mu-" + k, v)
    pg.click("#mu-check"); pg.wait_for_timeout(120); badk = pg.evaluate("[...document.querySelectorAll('.mu-slot.bad')].map(e=>e.dataset.k)")
    check(set(badk) == {"Sc", "DD", "MU"} and "percent" in pg.locator("#muh-DD").inner_text() and "collimator opening" in pg.locator("#muh-Sc").inner_text() and not pg.locator("#muh-Sp").is_visible(), f"wrong entries are marked with hints that say where to look, the right ones are not {badk}")
    check(json.loads(pg.evaluate("localStorage.getItem('ro.mu')"))["2"]["ok"] is False and pg.locator(".mc.try").count() == 1, "a wrong attempt is recorded as tried, not correct")
    pg.fill("#mu-DD", f"{r2['DD'] * 100:.1f}"); pg.fill("#mu-Sc", f"{r2['Sc']:.4f}"); pg.fill("#mu-MU", f"{r2['mu'] * 1.03:.0f}"); pg.click("#mu-check"); pg.wait_for_timeout(100)
    check(pg.evaluate("[...document.querySelectorAll('.mu-slot.bad')].map(e=>e.dataset.k)") == ["MU"] and "final division" in pg.locator("#mu-fb").inner_text(), "an MU 3% off is wrong when every factor is right")
    pg.fill("#mu-MU", f"{r2['mu'] * 1.008:.0f}"); pg.press("#mu-MU", "Enter"); pg.wait_for_timeout(100); check(pg.locator(".mu-slot.bad").count() == 0 and pg.locator(".mc.on.ok").count() == 1, "an MU within 1% is accepted, and Enter checks")
    # ---- the solution
    go("#mu/5"); pg.click("#mu-sol"); pg.wait_for_timeout(120); steps = pg.locator("#mu-solution li").count(); txt = pg.locator("#mu-solution").inner_text()
    check(steps >= 6 and "1.0302" in txt and "MU" in txt.split("\n")[-2:][0] + txt and pg.locator(".mcell.near").count() >= 3 and pg.locator(".mc.on.view").count() == 1, f"the solution lists {steps} steps with the inverse-square term of the SAD technique, marks the cells to read, and records that it was viewed")
    # ---- interpolation, rectangles, and an extended SSD with a wedge and a tray, filled from the reference solver
    def fill_all(id_, scale=1.0):
        c = cases[id_ - 1]; r = ref(c); go(f"#mu/{id_}"); keys = pg.evaluate("[...document.querySelectorAll('.mu-slot')].map(e=>e.dataset.k)")
        val = {"Df": c["dose"] * c["w"], "sq": r["sq"], "scs": r["scs"], "Sc": r["Sc"], "Sp": r["Sp"], "DD": r["DD"] * (100 if c["tech"] == "SSD" else 1), "F": r["F"], "ISF": r["ISF"], "WF": r["WF"], "TF": r["TF"], "MU": r["mu"]}
        for k in keys: pg.fill("#mu-" + k, f"{val[k]:.4f}")
        pg.click("#mu-check"); pg.wait_for_timeout(100); return keys, pg.locator(".mu-slot.bad").count()
    for id_ in (13, 14, 15, 16, 22, 23, 25, 26, 27, 32):
        keys, nbad = fill_all(id_); check(nbad == 0, f"case {id_} ({cases[id_ - 1]['level']}): the entries {keys} worked out independently are all accepted")
    keys, nbad = fill_all(25); check({"sq", "scs", "F", "WF", "TF"} <= set(keys), f"the hardest case asks for the equivalent square, the collimator opening, F, WF, and TF {keys}")
    go("#mu/13"); r13 = ref(cases[12])
    for k, v in (("Sc", r13["Sc"] + 0.0015), ("Sp", r13["Sp"] - 0.0015), ("DD", r13["DD"] * 100 + 0.2), ("ISF", 1.0), ("MU", r13["mu"])): pg.fill("#mu-" + k, f"{v:.4f}")
    pg.click("#mu-check"); pg.wait_for_timeout(100); check(pg.locator(".mu-slot.bad").count() == 0, "a hand interpolation within the tolerance is accepted")
    pg.fill("#mu-Sc", f"{r13['Sc'] + 0.01:.4f}"); pg.click("#mu-check"); pg.wait_for_timeout(100); check(pg.evaluate("[...document.querySelectorAll('.mu-slot.bad')].map(e=>e.dataset.k)") == ["Sc"], "a value 1% off is rejected")
    pg.click('.mtab[data-tab="scat"]'); pg.click("#mu-sol"); check("interpolated between 6 and 8" in pg.locator("#mu-solution").inner_text(), "the solution of an interpolated case says between which entries it interpolated")
    # ---- random cases
    go("#mu/1"); pg.click('.mrand[data-lvl="Challenging"]'); pg.wait_for_timeout(250); keys = pg.evaluate("[...document.querySelectorAll('.mu-slot')].map(e=>e.dataset.k)")
    check(pg.evaluate("location.hash") == "#mu/r" and pg.locator(".mu-case .meta").inner_text().strip() == "Random case" and pg.locator('.mrand[data-lvl="Challenging"]').inner_text() == "Two modifiers" and len(pg.evaluate("[...document.querySelectorAll('.mu-slot')]")) > 5, "a random case with two modifiers opens, and the buttons describe what is in the case, not how hard it is")
    rc = pg.evaluate("muCtx.c"); rr = ref(rc); before = pg.evaluate("localStorage.getItem('ro.mu')")
    val = {"Df": rc["dose"] * rc["w"], "sq": rr["sq"], "scs": rr["scs"], "Sc": rr["Sc"], "Sp": rr["Sp"], "DD": rr["DD"] * (100 if rc["tech"] == "SSD" else 1), "F": rr["F"], "ISF": rr["ISF"], "WF": rr["WF"], "TF": rr["TF"], "MU": rr["mu"]}
    for k in keys: pg.fill("#mu-" + k, f"{val[k]:.4f}")
    pg.click("#mu-check"); pg.wait_for_timeout(100); check(pg.locator(".mu-slot.bad").count() == 0 and pg.evaluate("localStorage.getItem('ro.mu')") == before, "a random case is solved by the same engine and is not saved")
    seen = set()
    for lvl in ("Easy", "Moderate", "Challenging"):
        for _ in range(25):
            pg.evaluate("(l)=>{muRandCase=muRandom(l)}", lvl); c = pg.evaluate("muRandCase"); o = pg.evaluate("(()=>{const o=muSolve(muRandCase); return {mu:o.mu,sq:o.sq}})()")
            seen.add((c["E"], c["tech"])); assert 20 < o["mu"] < 3000, (lvl, c, o)
            rr = ref(c); assert abs(o["mu"] - rr["mu"]) / rr["mu"] < 0.002, (lvl, c, o, rr["mu"]); assert c["d"] >= M.ENERGY[c["E"]]["dmax"]
    check(len(seen) >= 7, f"75 random cases across the levels all solve and agree with the reference solver, covering {len(seen)} of 8 energy and technique pairs")
    # ---- the tables page
    for E in (6, 10, 15, 18):
        go(f"#mu/tables/{E}"); T = M.tables(E); rows = pg.evaluate("[...document.querySelectorAll('.mut')].map(t=>t.querySelectorAll('tbody tr').length)")
        pdd10 = pg.evaluate("(E)=>{const T=MUD()[E]; return T.pdd[T.depths.indexOf(10)][T.sizes.indexOf(10)]}", E)
        check(rows[:2] == [len(T["depths"]), len(T["tmr_depths"])] and rows[2] == 3 and rows[3] == 4 and rows[4] == 1 and pdd10 == T["pdd"][T["depths"].index(10)][T["sizes"].index(10)], f"{E} MV tables page: PDD {rows[0]} rows, TMR {rows[1]}, scatter 3, wedge 4, tray 1, and the numbers are the tables")
    go("#mu/tables/9"); check(pg.locator('.mu-en .btn.primary').inner_text() == "6 MV", "an unknown energy shows the 6 MV tables")
    go("#mu/tables/10"); cell = pg.locator(".mut").first.locator("tbody tr").nth(T["depths"].index(10)).locator("td").nth(T["sizes"].index(10)).inner_text(); check(cell == "73.5", f"the 10 MV PDD at 10 cm for 10 × 10 cm reads {cell}")
    check(pg.locator(".mu-nav a.on").inner_text() == "Tables" and pg.locator('.mu-nav a[href="#mu"]').count() == 1, "the tables page and the practice page link to each other")
    # ---- navigation between cases and progress
    go("#mu/1"); check(pg.locator(".endrow a", has_text="Previous").count() == 0 and pg.locator(".endrow a", has_text="Next case").get_attribute("href") == "#mu/2", "the first case has no Previous and links to case 2")
    go("#mu/32"); check(pg.locator(".endrow a", has_text="Next case").count() == 0 and pg.locator(".endrow a", has_text="Previous").get_attribute("href") == "#mu/31", "the last case has no Next and links to case 31")
    go("#mu/99"); check(pg.evaluate("location.hash").startswith("#mu/") and pg.evaluate("location.hash") != "#mu/99", "an unknown case number falls back to a real case")
    go("#mu/7"); go("#mu"); check(pg.evaluate("location.hash") == "#mu/7", "the MU address returns to the case last opened")
    st = pg.evaluate("(()=>{const s=courseStats(); const nq=DATA.cards.filter(c=>c.opts).length, m=MUC().filter(c=>muDone(c.id)).length; return {q:s.q, m, nq, n:MUC().length}})()")
    check(abs(st["q"] - st["m"] / (st["nq"] + st["n"])) < 1e-9 and st["m"] >= 3, f"the total progress counts MU cases tried with the questions ({st['m']} of {st['n']} cases)")
    go("#ref"); rt = pg.locator("#ref-progress + p").inner_text(); check(f"{st['m']} of {st['n']} MU cases tried" in rt and pg.locator('a[href="#mu/tables/6"]').count() >= 1 and pg.locator("#main table.dt").count() == 0, f"the Reference page reports the MU cases and points to the tables instead of repeating them: {rt[-60:]!r}")
    pg.once("dialog", lambda d: d.accept()); pg.click("#clr"); pg.wait_for_timeout(200); go("#mu/1"); check(pg.locator(".mc.ok, .mc.try, .mc.view").count() == 0 and pg.evaluate("localStorage.getItem('ro.mu')") in ("{}", None), "Clear on the Reference page resets the MU cases")
    # ---- a phone
    pm = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True).new_page(); pm.on("pageerror", lambda e: errs.append(str(e))); wide = []
    for h in ("#mu/1", "#mu/22", "#mu/25", "#mu/tables/6", "#mu/tables/18"):
        pm.goto(U + "#ref"); pm.goto(U + h); pm.wait_for_timeout(200); w = pm.evaluate("[document.documentElement.scrollWidth, innerWidth, Math.max(0,...[...document.querySelectorAll('.mu-slot input')].map(i=>i.getBoundingClientRect().right-innerWidth))]")
        if w[0] > w[1] or w[2] > 0: wide.append((h, w))
    check(not wide, f"the MU pages fit a 390 px phone without sideways scroll {wide[:2]}")
    pm.goto(U + "#ref"); pm.goto(U + "#mu/22"); pm.wait_for_timeout(200); tw = pm.evaluate("(()=>{const t=document.querySelector('.mpane .tblwrap'); return [t.scrollWidth>t.clientWidth, getComputedStyle(t).overflowX]})()"); check(tw[0] and tw[1] in ("auto", "scroll"), "on a phone a table scrolls inside its own box")
    pm.fill("#mu-Sc", "1.0"); pm.click("#mu-check"); pm.wait_for_timeout(100); check(pm.locator("#mu-fb").is_visible(), "the worksheet works by touch on a phone")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"mu: {n} checks"); print("mu: PASS" if not bad else f"mu: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
