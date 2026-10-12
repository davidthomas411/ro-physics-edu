"""Builds dist/ro-physics.html (one self-contained page).
Usage: python build.py             a development build: values missing from site_config.json show as placeholders, and no usage data is ever sent
       python build.py --release   a release build: stops with a list of what is missing, then adds the build date, the commit id, and the usage counts the configuration asks for
Set SITE_CONFIG to read another configuration file, and OUT to write another output file."""
import base64, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
import siteinfo, analytics_schema
RELEASE = "--release" in sys.argv
CFG = siteinfo.load_config()
if RELEASE:
    P = siteinfo.release_problems(CFG)
    for w in P["warnings"]: print("warning:", w)
    stop = [(h, P[k]) for h, k in (("Values missing from site_config.json", "missing"), ("Confirmations needed in site_config.json", "unconfirmed"), ("Repository", "tracked"), ("Changelog", "changelog")) if P[k]]
    if stop:
        print("Release build stopped. Fix these, then run it again:")
        for h, items in stop:
            print(f"  {h}:")
            for x in items: print("   -", x)
        sys.exit(1)
import figs, blocks, blueprint, photolib
from topics import TOPICS
try:
    from facts import TITLES as FACTS, HEADS
except ImportError:
    FACTS, HEADS = {}, {}

FIGS = figs.build()
LINAC = {k: "data:image/webp;base64," + base64.b64encode((ROOT / "assets" / "linac" / f"{k}.webp").read_bytes()).decode()
         for k in ("base", "gantry", "couch")}

subcodes = {code for d in blueprint.DOMAINS for code, _ in d["subs"]}
domains = [dict(n=d["n"], roman=d["roman"], name=d["name"], short=d["short"], lines=d["lines"], linesM=d["linesM"], weight=d["weight"], subs=[list(s) for s in d["subs"]]) for d in blueprint.DOMAINS]

ids = [t["id"] for t in TOPICS]
assert len(ids) == len(set(ids)), "duplicate topic id"
order = {n: [] for n in range(1, 8)}
for t in TOPICS: order[t["domain"]].append(t)
topics, cards = [], []
for n in sorted(order):                                   # study order: by domain, then file order in src/topics/__init__.py
    for k, t in enumerate(order[n], 1):
        assert t["sub"] in subcodes, (t["id"], t["sub"])
        num = f"{n}.{k}"
        tk = t.get("take") or ()
        secs = [dict(id=f'{t["id"]}-s{i}', n=f"{num}.{i}", t=b[1], mk=bool(i - 1 < len(tk) and tk[i - 1])) for i, b in enumerate((x for x in t["guide"] if x[0] == "h2"), 1)]
        topics.append(dict(id=t["id"], dom=t["domain"], sub=t["sub"], title=t["title"], ref=t["ref"], num=num, secs=secs,
                           html=blocks.render(t["guide"], FIGS, tid=t["id"], ncards=len(t["cards"]), problems=t.get("problems", []), inline=t.get("inline"), num=num, terms=t.get("terms") or (), take=t.get("take") or ())))
        for i, c in enumerate(list(t["cards"]) + list(t.get("problems", [])), 1):
            if c["fig"]: assert c["fig"] in FIGS, (t["id"], c["fig"])
            cid = f'{t["id"]}:{i}'; is_q = c.get("opts") is not None; title = c["q"] if is_q else FACTS.get(cid, c["q"])
            ans = [HEADS[cid]] + list(c["a"][1:]) if (not is_q and cid in HEADS) else c["a"]
            cards.append(dict(id=cid, topic=t["id"], dom=t["domain"], q=blocks._mark(blocks.autostem(title) if is_q else title), a=ans, w=c["w"], fig=c["fig"], opts=c.get("opts"), lvl=c.get("lvl"), sig=c.get("sig")))
import re as _re
for _t in topics: _t["words"] = len(_re.sub(r"<[^>]+>", " ", _t["html"]).split())      # the length of each chapter page, which weights the reading progress
import beamdata, nistdata, real as _real
BUILD = siteinfo.build_info(RELEASE)
_used = {b[1] for t in TOPICS for b in t["guide"] if b[0] == "photo"}                    # only the photos that a chapter uses are embedded
ABOUT = siteinfo.build_about(CFG, BUILD, siteinfo.counts_from(topics, cards), _real.SOURCES, [e for e in photolib.load() if e["id"] in _used])
ANALYTICS = siteinfo.analytics_config(CFG, RELEASE)
import syllabus
plan = [dict(sub=s, ford=f, title=t) for s, f, t in syllabus.PLAN]
assert all(p['sub'] in subcodes for p in plan), [p for p in plan if p['sub'] not in subcodes]
_E = [0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
import beamdata as _bd
bm = dict(MUINF=_bd.MUINF, DELTA=_bd.DELTA, BETA=_bd.BETA, LAM=_bd.LAM, DMAX=_bd.DMAX, SC=sorted(_bd.SC.items()), SP=sorted(_bd.SP.items()))
import mudata, mucases, cases, gal, mrdata, real
DATA = dict(bm=bm, plan=plan, domains=domains, topics=topics, cards=cards, mu=dict(energies=mudata.all_tables(), cases=mucases.CASES), case=cases.CASE, gal=gal.GAL, drr=gal.DRR, mr=mrdata.MR, mrg=mrdata.GAL_MR, real=real.REAL, nist=nistdata.reference_html(), nistarr=dict(E=_E, w=[nistdata.WATER[e][0] for e in _E], b=[nistdata.BONE[e][0] for e in _E]),
            about=ABOUT, aschema=analytics_schema.js_schema())
print(len(topics), "topics,", len(cards), "cards")
if not RELEASE:
    _m = siteinfo.missing(CFG) + siteinfo.unconfirmed(CFG)
    if _m: print(f"site_config.json: {len(_m)} values missing or unconfirmed; they show as placeholders (python build.py --release lists them)")
_js = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")                # a string in the data can never end the script element

ROBOTS = "" if CFG.get("allow_indexing") else '<meta name="robots" content="noindex">\n'
CSS = (ROOT / "src" / "style.css").read_text()
JS = (ROOT / "src" / "app.js").read_text().replace("// @@MU@@", (ROOT / "src" / "mu.js").read_text())
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{ROBOTS}<title>Radiation oncology physics</title>
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="in"><a class="brand" href="#home">Radiation oncology physics</a>
<nav class="tabs"><a href="#home" data-tab="home">Home</a><a href="#cards" data-tab="cards">Flash cards</a><a href="#questions" data-tab="questions">Questions</a><a href="#mu" data-tab="mu">MU calc</a><a href="#ref" data-tab="ref">Reference</a></nav></div></header>
<div class="wrap" id="wrap"><aside class="side" id="side"></aside><main><div class="topbar-m"><div id="lpm"></div><select id="jump" aria-label="Go to"></select></div><div id="main"></div></main></div>
<script>
const DATA={_js(DATA)};
const FIG={_js(FIGS)};
const LINAC={json.dumps(LINAC)};
const ANALYTICS={_js(ANALYTICS)};
{JS}
</script>
</body>
</html>"""
out = os.environ.get("OUT", str(ROOT / "dist" / "ro-physics.html"))
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, round(os.path.getsize(out) / 1e6, 2), "MB")
