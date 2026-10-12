"""House-style guard for body text. The patterns catch mechanical cases only (reader address, instructions to the reader, signposting,
intensifiers, colloquial phrasing, references to another question or example, exponent notation, sentence-like headings).
They do not replace reading the text."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
from facts import TITLES, HEADS

strip = lambda s: re.sub(r"<[^>]+>", "", s)
BAN = re.compile(r"\b(you|your|we|let's|remember|know that|keep in mind|note that|that is why|this is why|that's why|what matters|tells you|simply|just(?! culture)|actually|basically|"
                 r"essentially|obviously|clearly|of course|the one to|in other words|it turns out|worth|a lot of|a bit|cold|"
                 r"very|highly|slips?|wanders?|tuck(?:s|ed)? in|rough rule|common currency|ready-made|notice|observe|beware|imagine|be sure)\b", re.I)
HEAD_BAD = re.compile(r"\b(is|are|has|have|was|were|too|why|what|how|which|when|you|your|we|matters|works)\b|[?!:]", re.I)
NUM = re.compile(r"\d(\.\d+)?e[+-]\d")   # Python exponent notation leaking into text
PURPOSE = re.compile(r"\b(makes?|helps?|lets?) (the )?(terms?|ideas?|concepts?|principles?|definitions?) (concrete|clear|clearer|tangible|real)\b|\bto teach\b|"
                     r"\billustrates? the (idea|principle|point)\b|\bshown to\b|\b(is|are) the point of\b", re.I)
DANGLE = re.compile(r"\b(previous|preceding|earlier|above) (question|questions|example|examples|problem|problems|calculation|calculations|card|cards)\b|"
                    r"\b(the|this) chapter\b|\b(figures?|images?|diagrams?|graphs?|tables?|plots?|pictures?) (below|above)\b|\bsection \d", re.I)
EXN = re.compile(r"\bExample \d")        # worked examples carry titles, not numbers
SAME = re.compile(r"(the same|same)\b", re.I)    # a question stem or an example stem that starts this way depends on another one
bad = []
def scan(where, s):
    s = strip(s)
    m = BAN.search(s)
    if m: bad.append((where, m.group(0), s[max(0, m.start() - 40):m.end() + 40]))
    n = NUM.search(s)
    if n: bad.append((where, "exponent notation", s[max(0, n.start() - 30):n.end() + 20]))
    for name, pat in (("purpose statement", PURPOSE), ("reference to other content", DANGLE), ("reference to a numbered example", EXN)):
        k = pat.search(s)
        if k: bad.append((where, name, s[max(0, k.start() - 40):k.end() + 40]))
def stem(where, s):
    s = strip(s)
    if SAME.match(s): bad.append((where, "a stem that starts by pointing at another one", s[:60]))
for t in TOPICS:
    tid = t["id"]
    for b in t["guide"]:
        k = b[0]
        if k in ("h2", "h3"):
            h = strip(b[1])
            if HEAD_BAD.search(h) or len(h.split()) > 6: bad.append((f"{tid} heading", h, ""))
        elif k == "p": scan(f"{tid} paragraph", b[1])
        elif k in ("ul", "ol"): [scan(f"{tid} list", x) for x in b[1]]
        elif k == "key":
            for x in b[1]:
                scan(f"{tid} key point", x)
                if re.match(r"(know|remember|understand)\b", strip(x), re.I): bad.append((f"{tid} key point", "instruction to the reader", strip(x)[:60]))
        elif k == "fig": scan(f"{tid} caption", b[2])
        elif k == "ex": stem(f"{tid} example '{b[1][:20]}'", b[2]); [scan(f"{tid} example '{b[1][:20]}'", x) for x in [b[1], b[2], b[4], *b[3]]]
        elif k == "more":
            scan(f"{tid} more details '{b[1][:20]}'", b[1]); scan(f"{tid} more details '{b[1][:20]}'", b[2] or "")
            for x in b[3]:
                if x[0] == "p": scan(f"{tid} more details '{b[1][:20]}'", x[1])
                elif x[0] in ("ul", "ol"): [scan(f"{tid} more details '{b[1][:20]}'", y) for y in x[1]]
                elif x[0] == "table": [scan(f"{tid} more details '{b[1][:20]}'", c) for r in x[2] for c in r]
    for items in (t.get("take") or []):
        for x in (items or []): scan(f"{tid} take away", x[0] if isinstance(x, tuple) else x)
    for i, c in enumerate(t["cards"], 1):
        cid = f"{tid}:{i}"
        title = TITLES.get(cid, c["q"]); scan(f"{cid} card title", title)       # a flash card shows its title and its fact; the question is not shown
        answer = [HEADS[cid]] + list(c["a"][1:]) if cid in HEADS else list(c["a"])
        [scan(f"{cid} card", x) for x in [*answer, *c["w"]]]
    for p in t["problems"]:
        stem(f"{tid} problem", p["q"]); [scan(f"{tid} problem", x) for x in [p["q"], p["a"][1], *p["w"], *(p.get("opts") or []), p.get("more") or ""]]
# ---------------------------------------------------------------- the About page, the privacy text, the changelog, and the configuration's own text
sys.path.insert(0, str(ROOT / "tests"))
import siteinfo as ABOUT, analytics_schema as AS, _release as REL
def about_text(blocks):
    for b in blocks:
        if b[0] in ("p", "h3"): yield b[1]
        elif b[0] == "ul": yield from b[1]
        elif b[0] == "table": yield from (c for r in b[2] for c in r)
        elif b[0] == "kv": yield from (c for r in b[1] for c in r)
for cfg_name, cfg in (("site_config.json", ABOUT.load_config()), ("a complete configuration", REL.FULL)):
    for rel in (False, True):
        A = ABOUT.build_about(cfg, ABOUT.build_info(False) if not rel else dict(ABOUT.build_info(False), release=True, built="2026-10-12", commit="0" * 40), dict(chapters=42, flash=505, questions=714), [dict(collection="CMB-LCA", doi="10.7937/3cx3-s132", license="CC BY 4.0")])
        for sec in A["sections"]:
            scan(f"About, {sec['title']}", sec["title"])
            for bl in ([sec["blocks"]] if not sec.get("variants") else list(sec["variants"].values())):
                for x in about_text(bl):
                    if "<span class=\"miss\">" in x and not rel: x = re.sub(r"<span class=\"miss\">.*?</span>", "", x)          # a placeholder names a missing value; it is not text of the page
                    scan(f"About, {sec['title']}", x)
        scan("About, license notice", A["notice"])
    for k in ("title", "abstract", "study_notice"): scan(f"{cfg_name}, {k}", cfg.get(k) or "")
for e in AS.EVENTS:
    scan(f"event {e['name']}", e["what"])
    for p_ in e["props"]: scan(f"event {e['name']}, {p_['name']}", p_["what"])
for x in AS.NEVER: scan("events never recorded", x)
for e in ABOUT.changelog():
    for x in e["items"]: scan(f"CHANGELOG {e['version']}", x)
for r in ABOUT.notices():
    for k in ("source", "what", "terms"): scan(f"THIRD_PARTY_NOTICES {r['source'][:20]}", r[k])
app = (ROOT / "src" / "app.js").read_text()
for w in ("Welcome", "Congratulations", "Great job", "Oops", "Let's", "Awesome", "Hooray"):
    if w in app: bad.append(("interface", w, ""))
print(f"style: {sum(len(t['guide']) for t in TOPICS)} guide blocks, {sum(len(t['cards']) for t in TOPICS)} cards, {sum(len(t['problems']) for t in TOPICS)} problems scanned")
for b in bad: print("FAIL", b)
print("style: PASS" if not bad else f"style: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
