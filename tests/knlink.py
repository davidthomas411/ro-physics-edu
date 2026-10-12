"""Must know lines and the passages they summarise: every line of a section's Must know box has at least one passage marked [[n|...]] in that section, and
every marker names a line that exists. Markers sit in running text, list items, table cells, equation lines, and figure captions of the same section."""
import sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
MK = re.compile(r"\[\[(\d+)\|(.*?)\]\]", re.S)
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
def strings(x):
    if isinstance(x, str): yield x
    elif isinstance(x, (list, tuple)):
        for y in x: yield from strings(y)
lines = linked = 0
for t in TOPICS:
    take = t.get("take") or []; per = {}; sec = -1
    for b in t["guide"]:
        if b[0] == "h2": sec += 1; continue
        if b[0] in ("ex", "more", "key", "photo", "avf"): 
            check(not any(MK.search(s) for s in strings(b)), f"{t['id']}: a marker sits inside a {b[0]} block, where it is not drawn")
            continue
        for s in strings(b[1:]):
            for m in MK.finditer(s):
                per.setdefault(sec, []).append(int(m.group(1)))
                check(len(m.group(2).strip()) > 0 and m.group(2).count("<") == m.group(2).count(">") and not MK.search(m.group(2)), f"{t['id']} section {sec + 1}: marker {m.group(1)} is empty, cuts a tag, or is nested")
    for i, items in enumerate(take):
        if not items: continue
        have = set(per.get(i, [])); lines += len(items)
        for j in range(1, len(items) + 1):
            if j in have: linked += 1
            else: check(False, f"{t['id']} section {i + 1}: Must know line {j} has no marked passage")
    for i, ms in per.items():
        check(i < len(take) and take[i] and all(1 <= k <= len(take[i]) for k in ms), f"{t['id']} section {i + 1}: a marker names a Must know line that does not exist {sorted(set(ms))}")
print(f"knlink: {linked} of {lines} Must know lines have a marked passage")
print(f"knlink: {n} checks"); print("knlink: PASS" if not bad else f"knlink: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
