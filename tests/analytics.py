"""Usage events. Static: the schema, the IRB description, the report tool, the item identifier. Browser: a development build and a build with analytics off send nothing; with analytics on and the collector stubbed,
each kind of question sends exactly one ans event that matches the screen, Explain further and Show more details send their events, no cookie and no new storage key appears, and the GoatCounter path decodes to the same event."""
import csv, html as H, io, json, math, os, re, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _release as R
ROOT = R.ROOT
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]; sys.path.insert(0, str(ROOT / "tools"))
import analytics_schema as AS, siteinfo as A, blocks, item_report as IR
from topics import TOPICS

bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)

# ---------------------------------------------------------------- static: the schema
EXAMPLE = {e["name"]: AS.example_props(e["name"]) for e in AS.EVENTS}
check([e["name"] for e in AS.EVENTS] == ["view", "ans", "more_q", "more_s", "card", "mu", "about"], "the schema holds exactly the seven events")
check(all(AS.clean(k, v) == v for k, v in EXAMPLE.items()), "every example payload passes its own checks")
check(AS.clean("ans", dict(EXAMPLE["ans"], extra="x")) == EXAMPLE["ans"], "a property that is not listed is dropped")
check(AS.clean("ans", dict(EXAMPLE["ans"], choice="my own words")) is None and AS.clean("ans", dict(EXAMPLE["ans"], item="a b:1:abcdef")) is None, "a value with free text is refused")
check(AS.clean("ans", {k: v for k, v in EXAMPLE["ans"].items() if k != "secs"}) is None and AS.clean("login", {}) is None, "an event with a missing property, and an unknown event, are not sent")
check(all(AS.decode(AS.path(k, v)) == (k, v) for k, v in EXAMPLE.items()), "the GoatCounter path of every example decodes to the same event and values")
check(AS.path("ans", EXAMPLE["ans"]) == "ev/ans/pdd:12:3fa9c1/mc/w/1/B/15-30/0", f"the ans path has the documented form: {AS.path('ans', EXAMPLE['ans'])}")
check({e["name"]: [p["name"] for p in e["props"]] for e in AS.EVENTS}["ans"] == ["item", "kind", "ok", "attempt", "choice", "secs", "help"], "ans carries item, kind, ok, attempt, choice, secs, help and nothing else")
check(AS.SECS == ["lt5", "5-15", "15-30", "30-60", "gt60"], "the time bins are under 5, 5 to 15, 15 to 30, 30 to 60, over 60")
# ---------------------------------------------------------------- static: the code, the IRB description
code = "\n".join((ROOT / "src" / f).read_text(encoding="utf-8") for f in ("app.js", "mu.js"))
called = set(re.findall(r"track\('([a-z_]+)'", code)); names = {e["name"] for e in AS.EVENTS}
check(called == names, f"every event in the schema is sent by the code, and the code sends no other: code {sorted(called)}, schema {sorted(names)}")
irb = (ROOT / "docs" / "irb-data-description.md").read_text(encoding="utf-8")
tab = [l for l in irb.splitlines() if l.startswith("| ") and not l.startswith("| Event") and not l.startswith("|---")]
ev_in_doc = {m.group(1) for l in tab for m in [re.match(r"\| `([a-z_]+)` \|", l)] if m}
props_in_doc = {m.group(1) for l in tab for m in [re.match(r"\| (?:`[a-z_]+`)? \| .*? \| `([a-z_]+)` \|", l)] if m}
check(ev_in_doc == names, f"the IRB description lists every event and no other: {sorted(ev_in_doc)}")
check(props_in_doc == {p["name"] for e in AS.EVENTS for p in e["props"]}, f"the IRB description lists every property and no other: {sorted(props_in_doc)}")
for sec in ("## What is not collected", "## Where the data are stored", "## Who can access the data", "## Retention", "## Anonymity in a small cohort", "## Example payloads"): check(sec in irb, f"the IRB description has the section {sec[3:]}")
check("```json" in irb and AS.path("ans", EXAMPLE["ans"]) in irb and "aggregates" in irb and "not linked" in irb and "fewer than 5" in irb, "the IRB description has example payloads and the small-cohort note")
check(all(f"| `{p['name']}` |" in irb for e in AS.EVENTS for p in e["props"]), "every property of every event has a row in the IRB table")
check("linked" in irb.split("## Not built")[1], "the IRB description says that linked analytics is not built")
# ---------------------------------------------------------------- static: the item identifier
s1 = blocks.PR("Which quantity is measured in gray?", "absorbed dose", ["activity", "exposure", "kerma"], "Gray is the unit of absorbed dose.")
s2 = blocks.PR("Which quantity is measured in grays?", "absorbed dose", ["activity", "exposure", "kerma"], "Gray is the unit of absorbed dose.")
s3 = blocks.PR("Which quantity is measured in gray?", "absorbed dose", ["activity", "exposure", "kerma"], "Gray is the unit of absorbed dose.")
check(s1["sig"][:6] != s2["sig"][:6] and s1["sig"][:6] == s3["sig"][:6], "the item identifier changes when the question text changes, and not otherwise")
o4 = blocks.PR("Which quantity is measured in gray?", "absorbed dose", ["activity", "exposure", "kerma"], "x"); o5 = blocks.PR("Which quantity is measured in gray?", "absorbed dose", ["activity", "kerma", "exposure"], "x")
check(o4["sig"][:6] != o5["sig"][:6], "reordering the options changes the identifier too")
# ---------------------------------------------------------------- static: the report tool, in each input format
cur = IR.current_items(); mc = [(t["id"], j, p) for t in TOPICS for j, p in enumerate(t["problems"], 1) if p.get("opts") and not p.get("multi") and len(p["opts"]) == 4][:3]
def item(x): return f"{x[0]}:{x[1]}:{x[2]['sig'][:6]}"
(a, b_, c_) = mc; key = a[2]["key"][0]; wrong = [l for l in "ABCD" if l != key]
EVS = []
def add(it, kind, ok, att, ch, secs, help_=False, k=1): EVS.append(("ans", dict(item=it, kind=kind, ok=ok, attempt=att, choice=ch, secs=secs, help=help_), k))
add(item(a), "mc", False, 1, wrong[0], "lt5", k=6); add(item(a), "mc", False, 1, wrong[1], "5-15", k=3); add(item(a), "mc", True, 1, key, "5-15", k=3); add(item(a), "mc", True, 2, key, "lt5", True, k=4)
EVS.append(("more_q", dict(item=item(a), state="after_wrong"), 5))
add(item(b_), "mc", True, 1, b_[2]["key"][0], "lt5", k=12)
add(item(c_), "mc", True, 1, c_[2]["key"][0], "gt60", k=4)
def as_jsonl(ev): return "\n".join(json.dumps(dict(event=e, props=p)) for e, p, k in ev for _ in range(k)) + "\n"
def as_csv(ev, count=False):
    o = io.StringIO(); w = csv.writer(o); w.writerow(["Path", "Title", "Event"] + (["Count"] if count else []))
    for e, p, k in ev:
        for _ in range(1 if count else k): w.writerow(["/" + AS.path(e, p), "", "true"] + ([k] if count else []))
    return o.getvalue()
def as_api(ev): return json.dumps(dict(hits=[dict(path="/" + AS.path(e, p), event=True, count=k) for e, p, k in ev], total=len(ev)))
tmp = Path(tempfile.mkdtemp(prefix="ev_")); files = {"a.jsonl": as_jsonl(EVS), "b.csv": as_csv(EVS), "c.csv": as_csv(EVS, True), "d.json": as_api(EVS)}
rows_by = {}
for f, t in files.items():
    (tmp / f).write_text(t, encoding="utf-8"); rows_by[f] = {r["item"]: r for r in IR.rows(IR.aggregate(IR.read_events(tmp / f)), cur)}
ra = rows_by["a.jsonl"][item(a)]
check(all(rows_by[f] == rows_by["a.jsonl"] for f in files), "JSON lines, a GoatCounter CSV with one row per hit, a CSV with a count column, and API JSON give the same report")
check(ra["n1"] == 12 and ra["n_all"] == 16 and ra["pct_correct"] == 25.0 and ra["options"] == " ".join(f"{k}:{v}" for k, v in sorted({wrong[0]: 6, wrong[1]: 3, key: 3}.items())), f"first-attempt n, percent correct, and the option counts: {ra}")
check(ra["explain_opens"] == 5 and ra["pct_explain"] == 42 and ra["secs_lt5"] == 6 and ra["secs_5-15"] == 6, f"Explain further opens and the time-bin counts: {ra}")
fl = ra["flags"].split(); un = [f"unchosen:{l}" for l in "ABCD" if l not in (key, wrong[0], wrong[1])]
check("low" in fl and all(u in fl for u in un) and f"above_key:{wrong[0]}" in fl and f"above_key:{wrong[1]}" not in fl, f"flags for an item with 12 first answers: {fl}")
check("high" in rows_by["a.jsonl"][item(b_)]["flags"].split(), "an item over 95% correct is flagged high")
check(rows_by["a.jsonl"][item(c_)]["flags"] == "" and rows_by["a.jsonl"][item(c_)]["n1"] == 4, "an item with fewer than 10 first answers gets no flag")
ext = IR.rows(IR.aggregate(IR.read_events(tmp / "a.jsonl")), cur, external=True)
check([r["item"] for r in ext] == [item(a), item(b_)], "with --external an item with fewer than 5 first answers is left out")
r = subprocess.run([sys.executable, str(ROOT / "tools" / "item_report.py"), str(tmp / "d.json"), "--out", str(tmp / "r.csv"), "--external"], capture_output=True, text=True, cwd=str(ROOT))
check(r.returncode == 0 and (tmp / "r.csv").exists() and len(list(csv.DictReader(open(tmp / "r.csv")))) == 2 and item(c_) not in (tmp / "r.csv").read_text(), "the command line writes the CSV without the suppressed item")
check(IR.rows(IR.aggregate([("ans", dict(EXAMPLE["ans"], item="zz-gone:3:abcdef"), 1)]), cur)[0]["flags"] == "not_in_this_version", "an item that is not in this version of the site is marked")

# ---------------------------------------------------------------- browser
rc, out, EP = R.build();                                                       assert rc == 0, out
rc, out, GC = R.build(dict(analytics_backend="goatcounter", analytics_site_code="teststudy"));  assert rc == 0, out
rc, out, OFF = R.build(dict(analytics_mode="none"));                           assert rc == 0, out
rc, out, DEV = R.build(release=False);                                         assert rc == 0, out
STUB, GCSTUB = "http://127.0.0.1:8099/**", "https://teststudy.goatcounter.com/**"
QS = []                                                                        # one entry per question: (card id, topic id, problem number, problem)
for t in TOPICS:
    for j, p in enumerate(t["problems"], 1): QS.append((f"{t['id']}:{len(t['cards']) + j}", t["id"], j, p))
def find(pred): return next(q for q in QS if pred(q[3]))
KINDS = {"mc": find(lambda p: p.get("opts") and not p.get("multi") and p.get("kind") is None and p.get("more")), "multi": find(lambda p: p.get("multi")), "typed": find(lambda p: p.get("kind") == "num"),
         "sort": find(lambda p: p.get("kind") == "sort" and p["mode"] == "sort"), "match": find(lambda p: p.get("kind") == "sort" and p["mode"] == "match"),
         "rank": find(lambda p: p.get("kind") == "sort" and p["mode"] == "rank"), "fig": find(lambda p: p.get("kind") == "fig" and not p["spec"].get("cells"))}
if any(q[3].get("kind") == "sort" and q[3]["mode"] == "tf" for q in QS): KINDS["tf"] = find(lambda p: p.get("kind") == "sort" and p["mode"] == "tf")      # true or false questions, if the bank has any
inside = lambda p, x, y: any((t[0] is None or x >= t[0]) and (t[1] is None or x <= t[1]) and (t[2] is None or y >= t[2]) and (t[3] is None or y <= t[3]) for t in p["targets"])

def session(b, path, stub=STUB, w=1280, h=900):
    ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme="light"); ev, reqs, errs = [], [], []
    def hit(route):
        r = route.request; reqs.append((r.method, r.url, r.headers))
        if r.method == "POST": ev.append(json.loads(r.post_data))
        else:
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(r.url).query); d = AS.decode(q["p"][0]); ev.append(dict(event=d[0], props=d[1], _q=sorted(q))) if d else ev.append(dict(event="?", props={}, _q=q))
        route.fulfill(status=204)
    ctx.route(stub, hit); ctx.on("request", lambda r: reqs.append(("ALL", r.url, {})) if not r.url.startswith(("file:", "data:")) and "127.0.0.1:8099" not in r.url and "goatcounter" not in r.url else None)
    pg = ctx.new_page(); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(path.resolve().as_uri() + "#home"); pg.wait_for_timeout(150); return ctx, pg, ev, reqs, errs

def goto(pg, path, hash_): pg.goto(path.resolve().as_uri() + "#home"); pg.goto(path.resolve().as_uri() + hash_); pg.wait_for_timeout(250)
def screen_ok(q): return q.locator(".res").inner_text() in ("Correct.", "All correct.")

def place(pg, q, mapping):
    for i, bn in mapping.items():
        q.locator(f'.chip[data-i="{i}"]').click(); q.locator(f'.bin[data-b="{bn}"] .bh').click()

def answer(pg, q, kind, p, wrong, tap=None):
    """Answer one question, right or wrong, and return what was chosen in terms the event should report."""
    if kind in ("mc", "multi"):
        key = p["key"]; L = "ABCDEFGH"[:len(p["opts"])]
        pick = ([next(l for l in L if l not in key)] if kind == "mc" else (key[:1] if len(key) > 1 else [next(l for l in L if l not in key)])) if wrong else list(key)
        for l in pick: q.locator(f'.opt[data-k="{l}"]').click()
        q.locator(".chk").click(); return "".join(sorted(pick))
    if kind == "typed":
        v = p["ans"] * (3.7 if wrong else 1); q.locator(".numin").fill(f"{v:.6g}"); q.locator(".chk").click(); return float("%.3g" % v)
    if kind in ("sort", "tf", "match", "rank"):
        want = [c["b"] for c in p["chips"]]; nb = len(p["bins"]); cur = dict(enumerate(want))
        if wrong:
            if p.get("cap") == 1 and len(want) >= 2: cur[0], cur[1] = want[1], want[0]
            else: cur[0] = next(b for b in range(nb) if b != want[0])
        place(pg, q, cur); q.locator(".chk").click(); return sum(1 << i for i in range(len(want)) if cur[i] == want[i])
    if kind == "fig":
        S = p["spec"]; t = p["targets"][0]; x0 = t[0] if t[0] is not None else S["x"]["min"]; x1 = t[1] if t[1] is not None else S["x"]["max"]; y0 = t[2] if t[2] is not None else S["y"]["min"]; y1 = t[3] if t[3] is not None else S["y"]["max"]
        pt = ((math.sqrt(x0 * x1) if S["x"].get("log") else (x0 + x1) / 2), (y0 + y1) / 2)
        if wrong:
            xr, yr = S["x"]["max"] - S["x"]["min"], S["y"]["max"] - S["y"]["min"]
            pt = next((S["x"]["min"] + fx * xr, S["y"]["min"] + fy * yr) for fx, fy in ((.03, .03), (.97, .03), (.03, .97), (.97, .97), (.5, .03)) if not inside(p, S["x"]["min"] + fx * xr, S["y"]["min"] + fy * yr))
        q.locator(".fgb").scroll_into_view_if_needed(); pg.wait_for_timeout(80)
        pos = q.evaluate("(el,a)=>{const r=el._fig.toClient(a[0],a[1]); return [r.x,r.y]}", list(pt)); pg.mouse.click(pos[0], pos[1]); pg.wait_for_timeout(40); q.locator(".chk").click()
        lg = lambda a, v: math.log10(v) if S[a].get("log") else v
        pc = lambda a, v: (lg(a, v) - lg(a, S[a]["min"])) / (lg(a, S[a]["max"]) - lg(a, S[a]["min"])) * 100
        return (pc("x", pt[0]), pc("y", pt[1]))

def reset(q): q.locator(".again").click()
def open_q(pg, path, card): goto(pg, path, "#t/" + card.split(":")[0] + "/q"); q = pg.locator(f'.pq[data-id="{card}"]'); q.scroll_into_view_if_needed(); pg.wait_for_timeout(120); return q

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    # ---------------------------------------------------------------- off: development build and a release build with analytics none
    for name, page in (("development build", DEV), ("release build with analytics off", OFF)):
        ctx, pg, ev, reqs, errs = session(b, page)
        check(pg.evaluate("ANALYTICS") is None and pg.evaluate("document.querySelectorAll('script[src],link[rel=stylesheet],iframe').length") == 0, f"{name}: no collector in the page, no external script")
        card, tid, j, p = KINDS["mc"]; q = open_q(pg, page, card); q.locator('.opt[data-k="A"]').click(); q.locator(".chk").click(); q.locator(".more-btn").click(); pg.wait_for_timeout(100)
        goto(pg, page, "#t/waves-photons/c/2"); goto(pg, page, "#mu/1"); pg.click("#mu-sol"); goto(pg, page, "#about"); goto(pg, page, "#ref")
        pg.evaluate("track('view',{route:'home'}); track('ans',{})"); pg.wait_for_timeout(200)
        check(not [r for r in reqs] and not ev, f"{name}: answering, flash cards, the MU case, About, and a direct call of track() send no request ({len(reqs)} requests)")
        check(ctx.cookies() == [] and pg.evaluate("document.cookie") == "" and not errs, f"{name}: no cookie, no console error {errs[:2]}"); ctx.close()
    # ---------------------------------------------------------------- on, endpoint backend
    ctx, pg, ev, reqs, errs = session(b, EP); ALLOWED = {"ro.cards", "ro.q", "ro.read", "ro.last", "ro.theme", "ro.mu", "ro.mulast"}
    check(pg.evaluate("ANALYTICS") == dict(backend="endpoint", url="http://127.0.0.1:8099/collect"), "the release build with anonymous analytics carries the collector settings")
    check(pg.evaluate("DATA.aschema") == json.loads(json.dumps(AS.js_schema())), "the schema in the page is the schema in src/analytics_schema.py")
    check([e["event"] for e in ev] == ["view"] and ev[0]["props"] == {"route": "home"}, f"opening the site sends one view event with the route: {ev}")
    # every kind of question: exactly one ans event, matching the screen
    for kind, (card, tid, j, p) in KINDS.items():
        q = open_q(pg, EP, card); del ev[:]
        want_item = f"{tid}:{j}:{p['sig'][:6]}"; ek = "sort" if kind == "tf" else kind
        if q.evaluate("el=>el.classList.contains('done')"): reset(q); del ev[:]
        ch = answer(pg, q, kind, p, wrong=True); pg.wait_for_timeout(150); sc = screen_ok(q); e = [x for x in ev if x["event"] == "ans"]
        check(len(e) == 1 and len([x for x in ev if x["event"] != "ans"]) == 0, f"{kind}: one wrong answer sends exactly one ans event and no other ({[x['event'] for x in ev]})")
        pr = e[0]["props"]
        check(set(pr) == {"item", "kind", "ok", "attempt", "choice", "secs", "help"} and AS.clean("ans", pr) == pr, f"{kind}: the keys of the event are the schema's, and the values pass their checks {pr}")
        check(pr["item"] == want_item and pr["kind"] == ek and pr["ok"] is False and sc is False and pr["attempt"] == 1 and pr["help"] is False and pr["secs"] in AS.SECS, f"{kind}: item {want_item}, ok false as on the screen, attempt 1, no help: {pr}")
        if kind in ("mc", "multi"): check(pr["choice"] == ch, f"{kind}: choice is what was chosen ({ch}): {pr['choice']}")
        elif kind == "typed": check(float(pr["choice"]) == ch, f"typed: choice is the value rounded to 3 digits ({ch}): {pr['choice']}")
        elif kind in ("sort", "tf", "match", "rank"): check(int(pr["choice"]) == ch and ch != (1 << len(p["chips"])) - 1, f"{kind}: choice is the bitmask of correctly placed items ({ch}): {pr['choice']}")
        else:
            px, py = (int(v) for v in pr["choice"].split(",")); check(all(v % 2 == 0 and 0 <= v <= 100 for v in (px, py)) and abs(px - ch[0]) <= 4 and abs(py - ch[1]) <= 4, f"fig: choice is the tap as a percentage of each axis, to the nearest 2 ({ch[0]:.1f}, {ch[1]:.1f}): {pr['choice']}")
        del ev[:]; reset(q); ch2 = answer(pg, q, kind, p, wrong=False); pg.wait_for_timeout(150); e = [x for x in ev if x["event"] == "ans"]; pr = e[0]["props"] if e else {}
        check(len(e) == 1 and pr.get("ok") is True and screen_ok(q) and pr.get("attempt") == 2 and pr.get("help") is False, f"{kind}: the retry sends one event with ok true as on the screen and attempt 2: {pr}")
        if kind in ("mc", "multi"): check(pr.get("choice") == ch2, f"{kind}: the retry's choice is the key {ch2}")
        reset(q)
    # attempts: 3 and then 3 or more; help only after Explain further
    card, tid, j, p = KINDS["mc"]; pg.evaluate("localStorage.removeItem('ro.q')"); pg.reload(); pg.wait_for_timeout(200); q = open_q(pg, EP, card); key = p["key"][0]; wrongl = next(l for l in "ABCD" if l != key); del ev[:]
    for k in range(1, 5):
        if q.evaluate("el=>el.classList.contains('done')"): reset(q)
        q.locator(f'.opt[data-k="{wrongl}"]').click(); q.locator(".chk").click(); pg.wait_for_timeout(60)
        if k == 2: q.locator(".more-btn").click(); pg.wait_for_timeout(60)
    an = [x["props"] for x in ev if x["event"] == "ans"]; mq = [x["props"] for x in ev if x["event"] == "more_q"]
    check([a["attempt"] for a in an] == [1, 2, 3, 3], f"the attempt number rises on a retry and stays at 3 for the third and later: {[a['attempt'] for a in an]}")
    # explain further: help is true only for the answer after it was opened (order of events: ans1, ans2, more_q, ans3, ans4)
    order = [(x["event"], x["props"].get("help")) for x in ev if x["event"] in ("ans", "more_q")]
    check(order == [("ans", False), ("ans", False), ("more_q", None), ("ans", True), ("ans", False)], f"help is true only on the answer that follows Explain further: {order}")
    check(mq and mq[0]["state"] == "after_wrong" and mq[0]["item"] == f"{tid}:{j}:{p['sig'][:6]}", f"opening Explain further after a wrong answer sends more_q after_wrong: {mq}")
    reset(q); q.locator(f'.opt[data-k="{key}"]').click(); q.locator(".chk").click(); del ev[:]; q.locator(".more-btn").click(); pg.wait_for_timeout(60); q.locator(".more-btn").click(); pg.wait_for_timeout(60)
    check([x["props"].get("state") for x in ev if x["event"] == "more_q"] == ["after_correct"], f"opening Explain further after a correct answer sends after_correct, and closing it sends nothing: {[x['props'] for x in ev]}")
    pg.reload(); pg.wait_for_timeout(250); del ev[:]; pg.wait_for_timeout(100)
    check(pg.locator(f'.pq[data-id="{card}"]').evaluate("el=>el.classList.contains('done')") is False or not [x for x in ev if x["event"] == "ans"], "a stored answer that is restored on load sends no ans event")
    # Show more details in a chapter
    tp = next(t for t in TOPICS if any(x[0] == "more" for x in t["guide"])); goto(pg, EP, "#t/" + tp["id"]); del ev[:]
    pg.locator(".guide .more-btn").first.click(); pg.wait_for_timeout(80); ms = [x["props"] for x in ev if x["event"] == "more_s"]
    sec = pg.evaluate("(()=>{let e=document.querySelector('.guide .more'); while(e&&e.tagName!=='H2') e=e.previousElementSibling; return e&&e.id;})()")
    check(len(ms) == 1 and sec == f"{tp['id']}-s{ms[0]['section']}" and ms[0]["topic"] == tp["id"] and AS.clean("more_s", ms[0]) == ms[0], f"Show more details sends more_s with the chapter and the section: {ms} {sec}")
    pg.locator(".guide .more-btn").first.click(); pg.wait_for_timeout(60); check(len([x for x in ev if x["event"] == "more_s"]) == 1, "closing the details sends nothing")
    # flash cards, MU cases, About, and views
    goto(pg, EP, "#t/waves-photons/c/3"); del ev[:]; pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(200)
    check([(x["event"], x["props"]) for x in ev] == [("card", {"card": "waves-photons:4", "action": "seen"})], f"a flash card sends card and the next card sends another, with no new view: {ev}")
    goto(pg, EP, "#mu/1"); del ev[:]; pg.click("#mu-sol"); pg.wait_for_timeout(80)
    for el in pg.locator(".mu-slot input").all(): el.fill("1")
    pg.click("#mu-check"); pg.wait_for_timeout(100)
    check([(x["event"], x["props"]) for x in ev] == [("mu", {"case": "1", "action": "solution"}), ("mu", {"case": "1", "action": "tried"})], f"the MU case sends solution and tried: {ev}")
    goto(pg, EP, "#ref"); del ev[:]; pg.click('.lead a[href="#about"]'); pg.wait_for_timeout(150)
    check([(x["event"], x["props"]) for x in ev] == [("view", {"route": "about"}), ("about", {})], f"opening About sends view and about: {ev}")
    goto(pg, EP, "#t/pdd"); check(ev and ev[-1] == dict(event="view", props={"route": "t/pdd"}), f"a chapter sends view with its route: {ev[-1:]}")
    # privacy of the transport and the browser
    posts = [r for r in reqs if r[0] == "POST"]; others = [r for r in reqs if r[0] == "ALL"]
    check(posts and all(r[1] == "http://127.0.0.1:8099/collect" and "cookie" not in {k.lower() for k in r[2]} and "referer" not in {k.lower() for k in r[2]} for r in posts), "every event is a POST to the configured collector with no cookie and no referrer")
    check(not others, f"no request goes anywhere else {others[:2]}")
    check(all(AS.clean(x["event"], x["props"]) == x["props"] and set(x) == {"event", "props"} for x in ev), "every event sent so far passes the schema checks, with no other key")
    keys = pg.evaluate("Object.keys(localStorage)"); check(all(k in ALLOWED for k in keys) and pg.evaluate("sessionStorage.length") == 0, f"no storage key other than the existing ro.* keys: {keys}")
    check(ctx.cookies() == [] and pg.evaluate("document.cookie") == "", "no cookie is set")
    check(not errs, f"no console errors {errs[:2]}")
    # stored values are untrusted: a bad attempt count is ignored
    sig = KINDS["mc"][3]["sig"]; cardid = KINDS["mc"][0]; pg.evaluate("a=>localStorage.setItem('ro.q',JSON.stringify({[a[0]]:{sig:a[1],n:'many'}}))", [cardid, sig]); pg.reload(); pg.wait_for_timeout(200); q = open_q(pg, EP, cardid); del ev[:]
    q.locator('.opt[data-k="A"]').click(); q.locator(".chk").click(); pg.wait_for_timeout(80); check([x["props"]["attempt"] for x in ev if x["event"] == "ans"] == [1], "a stored attempt count that is not a whole number is treated as none")
    ctx.close()
    # ---------------------------------------------------------------- time bins
    ctx, pg, ev, reqs, errs = session(b, EP); card, tid, j, p = KINDS["mc"]
    q = open_q(pg, EP, card); pg.wait_for_timeout(5400); q.locator('.opt[data-k="A"]').click(); q.locator(".chk").click(); pg.wait_for_timeout(80)
    check([x["props"]["secs"] for x in ev if x["event"] == "ans"] == ["5-15"], f"a question that was in view for 5.4 s is in the 5 to 15 bin: {[x['props'].get('secs') for x in ev if x['event'] == 'ans']}")
    reset(q); del ev[:]; pg.evaluate("Object.defineProperty(document,'hidden',{get:()=>true,configurable:true}); document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(5400)
    pg.evaluate("Object.defineProperty(document,'hidden',{get:()=>false,configurable:true}); document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(100)
    q.locator('.opt[data-k="A"]').click(); q.locator(".chk").click(); pg.wait_for_timeout(80)
    check([x["props"]["secs"] for x in ev if x["event"] == "ans"] == ["lt5"], f"time with the tab hidden is not counted: {[x['props'].get('secs') for x in ev if x['event'] == 'ans']}")
    ctx.close()
    # ---------------------------------------------------------------- on, GoatCounter backend
    ctx, pg, ev, reqs, errs = session(b, GC, GCSTUB); card, tid, j, p = KINDS["mc"]
    q = open_q(pg, GC, card); del ev[:]; q.locator('.opt[data-k="A"]').click(); q.locator(".chk").click(); pg.wait_for_timeout(100)
    gets = [r for r in reqs if r[0] == "GET"]
    check(pg.evaluate("ANALYTICS") == dict(backend="goatcounter", url="https://teststudy.goatcounter.com/count"), "the GoatCounter settings come from the site code")
    check(gets and all(r[1].startswith("https://teststudy.goatcounter.com/count?") for r in gets), "events go to the site's count address")
    check(all(x["_q"] == ["e", "p", "rnd"] for x in ev if "_q" in x), f"a request carries a path, the event flag, and a cache-busting value, with no referrer, screen size, or title: {[x.get('_q') for x in ev][:3]}")
    a = [x for x in ev if x["event"] == "ans"]; check(len(a) == 1 and a[0]["props"]["item"] == f"{tid}:{j}:{p['sig'][:6]}" and a[0]["props"]["choice"] == "A" and AS.clean("ans", a[0]["props"]) == a[0]["props"], f"the path decodes to the ans event: {a}")
    check(ctx.cookies() == [] and pg.evaluate("document.cookie") == "" and not errs, f"GoatCounter backend: no cookie, no console error {errs[:2]}"); ctx.close()
    b.close()
print(f"analytics: {n} checks, {len(bad)} failed"); sys.exit(1 if bad else 0)
