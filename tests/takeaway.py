"""Every section ends with a short take-away, except sections that only hold worked examples; no chapter-level key points remain."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
strip = lambda s: re.sub(r"<[^>]+>", "", s)
line = lambda x: x[0] if isinstance(x, tuple) else x
EXEMPT = {("decay-law", "Worked examples"), ("mu-calc", "Worked examples")}   # these sections only repeat a method
bad, n, words = [], 0, []
for t in TOPICS:
    secs = [strip(b[1]) for b in t["guide"] if b[0] == "h2"]; take = t.get("take") or []
    if len(take) != len(secs): bad.append((t["id"], "one entry per section", len(take), len(secs)))
    if any(b[0] == "key" for b in t["guide"]): bad.append((t["id"], "chapter-level key points still present"))
    for i, s in enumerate(secs):
        items = take[i] if i < len(take) else None
        if not items:
            if (t["id"], s) not in EXEMPT: bad.append((t["id"], "section without a take away", s))
            continue
        n += 1; w = sum(len(strip(line(x)).split()) for x in items); words.append((w, t["id"], s))
        if len(items) > 3: bad.append((t["id"], s, "more than three lines", len(items)))
        if any(len(strip(line(x)).split()) > 42 for x in items): bad.append((t["id"], s, "a line over 42 words"))
        if w > 80: bad.append((t["id"], s, "box over 80 words", w))
html = (ROOT / "dist" / "ro-physics.html").read_text()
if html.count('class=\\"take\\"') + html.count('class="take"') != n: bad.append(("page", "take-away boxes in the built page", html.count('class=\\"take\\"'), n))
if "Key points" in html: bad.append(("page", "the words 'Key points' still appear"))
print(f"takeaway: {n} sections have a take away; longest box {max(words)[0]} words ({max(words)[1]}: {max(words)[2]}); mean {sum(w for w, _, _ in words) / len(words):.0f} words")
for b in bad: print("FAIL", b)
print("takeaway: PASS" if not bad else f"takeaway: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
