"""House-style guard for body text. The patterns catch mechanical cases only (reader address, instructions to the reader,
signposting, sentence-like headings). They do not replace reading the text."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS

strip = lambda s: re.sub(r"<[^>]+>", "", s)
BAN = re.compile(r"\b(you|your|we|let's|remember|know that|keep in mind|note that|that is why|this is why|that's why|what matters|tells you|simply|just|actually|basically|"
                 r"essentially|obviously|clearly|of course|the one to|in other words|it turns out|worth|a lot of|a bit|cold)\b", re.I)
HEAD_BAD = re.compile(r"\b(is|are|has|have|was|were|too|why|what|how|which|when|you|your|we|matters|works)\b|[?!:]", re.I)
NUM = re.compile(r"\d(\.\d+)?e[+-]\d")   # Python exponent notation leaking into text
bad = []
def scan(where, s):
    m = BAN.search(strip(s))
    if m: bad.append((where, m.group(0), strip(s)[max(0, m.start() - 40):m.end() + 40]))
    n = NUM.search(strip(s))
    if n: bad.append((where, "exponent notation", strip(s)[max(0, n.start() - 30):n.end() + 20]))
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
        elif k == "ex": [scan(f"{tid} example '{b[1][:20]}'", x) for x in [b[2], b[4], *b[3]]]
        elif k == "more":
            scan(f"{tid} more details '{b[1][:20]}'", b[1]); scan(f"{tid} more details '{b[1][:20]}'", b[2] or "")
            for x in b[3]:
                if x[0] == "p": scan(f"{tid} more details '{b[1][:20]}'", x[1])
                elif x[0] in ("ul", "ol"): [scan(f"{tid} more details '{b[1][:20]}'", y) for y in x[1]]
                elif x[0] == "table": [scan(f"{tid} more details '{b[1][:20]}'", c) for r in x[2] for c in r]
    for items in (t.get("take") or []):
        for x in (items or []): scan(f"{tid} take away", x[0] if isinstance(x, tuple) else x)
    for c in t["cards"]: [scan(f"{tid} card", x) for x in [c["q"], *c["a"], *c["w"]]]
    for p in t["problems"]: [scan(f"{tid} problem", x) for x in [p["q"], p["a"][1], *p["w"], p.get("more") or ""]]
app = (ROOT / "src" / "app.js").read_text()
for w in ("Welcome", "Congratulations", "Great job", "Oops", "Let's", "Awesome", "Hooray"):
    if w in app: bad.append(("interface", w, ""))
print(f"style: {sum(len(t['guide']) for t in TOPICS)} guide blocks, {sum(len(t['cards']) for t in TOPICS)} cards, {sum(len(t['problems']) for t in TOPICS)} problems scanned")
for b in bad: print("FAIL", b)
print("style: PASS" if not bad else f"style: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
