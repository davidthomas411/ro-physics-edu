"""Course plan: every ABR subsection has topics, no planned title duplicates a built one, and the Reference page shows the same counts as the data."""
import sys, os, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import blueprint, syllabus
from playwright.sync_api import sync_playwright
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
subs = {s[0]: s[1] for d in blueprint.DOMAINS for s in d["subs"]}
built = {}; [built.setdefault(t["sub"], []).append(t["title"]) for t in TOPICS]; planned = {}; [planned.setdefault(s, []).append(t) for s, f, t in syllabus.PLAN]
check(all(s in subs for s in planned) and all(s in subs for s in built), "every built and planned topic names a real ABR subsection")
check(all(built.get(s) or planned.get(s) for s in subs), f"all {len(subs)} ABR subsections have at least one built or planned topic")
titles = [t for _, _, t in syllabus.PLAN]; norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
check(len({norm(t) for t in titles}) == len(titles), "no title is planned twice")
check(not {norm(t["title"]) for t in TOPICS} & {norm(t) for t in titles}, "no planned title duplicates a built topic")
heads = re.compile(r"\b(is|are|has|have|was|were|too|why|what|how|which|when|you|your|we|matters|works)\b|[?!]", re.I)
check(all(len(t.split()) <= 8 and not heads.search(t) for t in titles), "planned titles are short noun phrases")
check(all(re.fullmatch(r"\d+(–\d+)?", f) for _, f, _ in syllabus.PLAN), "Ford chapter references are numbers or ranges")
nb, np_ = len(TOPICS), len(syllabus.PLAN); print(f"plan: {nb} built, {np_} to build, {nb + np_} in all")
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    for w, h, name in ((1280, 900, "desktop"), (390, 844, "phone")):
        pg = b.new_page(viewport={"width": w, "height": h}); pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(U + "#home"); pg.goto(U + "#ref"); pg.wait_for_timeout(300)
        txt = pg.locator("#ref-plan + p").inner_text(); check(f"{nb} of {nb + np_} planned topics are built" in txt, f"{name}: the plan summary states {nb} of {nb + np_} ({txt[:70]!r})")
        rows = pg.evaluate("[...document.querySelectorAll('.plan .sub')].map(r=>[r.dataset.sub, +r.dataset.b, +r.dataset.p])")
        tot_b = sum(r[1] for r in rows); tot_p = sum(r[2] for r in rows); check((tot_b, tot_p) == (nb, np_) and len(rows) == len(subs), f"{name}: the rows add up to {tot_b} built and {tot_p} to build over {len(rows)} subsections")
        det = pg.locator(".plan details").first
        if np_: det.locator("summary").click(); check(det.evaluate("d=>d.open") and det.locator("li").count() >= 1 and det.locator("ul").bounding_box()["width"] > (w * 0.6 if name == "phone" else 300), f"{name}: a subsection opens to a full-width list of its remaining topics")
        sw = pg.evaluate("[document.documentElement.scrollWidth, innerWidth]"); check(sw[0] <= sw[1], f"{name}: no sideways scroll on the Reference page {sw}")
        if name == "phone": pg.locator("#ref-plan").scroll_into_view_if_needed(); pg.screenshot(path="/tmp/shots/plan_phone.png")
        else: pg.locator("#ref-plan").scroll_into_view_if_needed(); pg.screenshot(path="/tmp/shots/plan_desktop.png")
    check(not errs, f"no page errors {errs[:2]}"); b.close()
print(f"plan: {n} checks"); print("plan: PASS" if not bad else f"plan: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
