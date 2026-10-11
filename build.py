"""Builds dist/ro-physics.html (one self-contained page). Usage: python build.py"""
import base64, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
import figs, blocks, blueprint
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
        secs = [dict(id=f'{t["id"]}-s{i}', n=f"{num}.{i}", t=b[1]) for i, b in enumerate((x for x in t["guide"] if x[0] == "h2"), 1)]
        topics.append(dict(id=t["id"], dom=t["domain"], sub=t["sub"], title=t["title"], ref=t["ref"], num=num, secs=secs,
                           html=blocks.render(t["guide"], FIGS, tid=t["id"], ncards=len(t["cards"]), problems=t.get("problems", []), inline=t.get("inline"), num=num, terms=t.get("terms") or (), take=t.get("take") or ())))
        for i, c in enumerate(list(t["cards"]) + list(t.get("problems", [])), 1):
            if c["fig"]: assert c["fig"] in FIGS, (t["id"], c["fig"])
            cid = f'{t["id"]}:{i}'; is_q = c.get("opts") is not None; title = c["q"] if is_q else FACTS.get(cid, c["q"])
            ans = [HEADS[cid]] + list(c["a"][1:]) if (not is_q and cid in HEADS) else c["a"]
            cards.append(dict(id=cid, topic=t["id"], dom=t["domain"], q=blocks._mark(blocks.autostem(title) if is_q else title), a=ans, w=c["w"], fig=c["fig"], opts=c.get("opts"), lvl=c.get("lvl"), sig=c.get("sig")))
import re as _re
for _t in topics: _t["words"] = len(_re.sub(r"<[^>]+>", " ", _t["html"]).split())      # the length of each chapter page, which weights the reading progress
import beamdata, nistdata
import syllabus
plan = [dict(sub=s, ford=f, title=t) for s, f, t in syllabus.PLAN]
assert all(p['sub'] in subcodes for p in plan), [p for p in plan if p['sub'] not in subcodes]
_E = [0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
import beamdata as _bd
bm = dict(MUINF=_bd.MUINF, DELTA=_bd.DELTA, BETA=_bd.BETA, LAM=_bd.LAM, DMAX=_bd.DMAX, SC=sorted(_bd.SC.items()), SP=sorted(_bd.SP.items()))
import mudata, mucases, cases, gal, mrdata, real
DATA = dict(bm=bm, plan=plan, domains=domains, topics=topics, cards=cards, mu=dict(energies=mudata.all_tables(), cases=mucases.CASES), case=cases.CASE, gal=gal.GAL, drr=gal.DRR, mr=mrdata.MR, mrg=mrdata.GAL_MR, real=real.REAL, nist=nistdata.reference_html(), nistarr=dict(E=_E, w=[nistdata.WATER[e][0] for e in _E], b=[nistdata.BONE[e][0] for e in _E]))
print(len(topics), "topics,", len(cards), "cards")

CSS = (ROOT / "src" / "style.css").read_text()
JS = (ROOT / "src" / "app.js").read_text().replace("// @@MU@@", (ROOT / "src" / "mu.js").read_text())
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Radiation oncology physics</title>
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="in"><a class="brand" href="#home">Radiation oncology physics</a>
<nav class="tabs"><a href="#home" data-tab="home">Home</a><a href="#cards" data-tab="cards">Flash cards</a><a href="#questions" data-tab="questions">Questions</a><a href="#mu" data-tab="mu">MU calc</a><a href="#ref" data-tab="ref">Reference</a></nav></div></header>
<div class="wrap" id="wrap"><aside class="side" id="side"></aside><main><div class="topbar-m"><div id="lpm"></div><select id="jump" aria-label="Go to"></select></div><div id="main"></div></main></div>
<script>
const DATA={json.dumps(DATA, ensure_ascii=False)};
const FIG={json.dumps(FIGS, ensure_ascii=False)};
const LINAC={json.dumps(LINAC)};
{JS}
</script>
</body>
</html>"""
out = os.environ.get("OUT", str(ROOT / "dist" / "ro-physics.html"))
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, round(os.path.getsize(out) / 1e6, 2), "MB")
