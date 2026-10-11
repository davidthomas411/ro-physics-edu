"""ABR item-writing style: select-several questions say how many to pick and have at least twice as many options as correct answers; no negative stems, no 'all of the above', no 'none of the above'."""
import sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
NUMW = {2: "two", 3: "three", 4: "four", 5: "five"}; bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
multi = [(t["id"], k, p) for t in TOPICS for k, p in enumerate(t["problems"], 1) if p.get("multi")]
check(len(multi) >= 20, f"{len(multi)} select-several questions were checked")
for tid, k, p in multi:
    nc, no = len(p["key"]), len(p["opts"]); q = plain(p["q"])
    check(no >= 2 * nc, f"{tid}:{k} has {no} options for {nc} correct answers (the ABR asks for at least twice as many options)")
    check(f"(Please select {NUMW[nc]} options.)" in q, f"{tid}:{k} ends with '(Please select {NUMW[nc]} options.)'")
    if re.match(r"Which (?:of (?:these|the following))\b", plain(p["stem0"])): check(re.match(rf"Which {NUMW[nc]} of (?:these|the following)\b", q) is not None, f"{tid}:{k} says in the stem how many to pick")
    check(len(set(plain(o) for o in p["opts"])) == no, f"{tid}:{k} has no repeated options")
neg = re.compile(r"\b(NOT|EXCEPT|FALSE|INCORRECT|LEAST)\b|\b(?i:not true|not correct|which of the following is false)\b")
for t in TOPICS:
    for k, p in enumerate(t["problems"], 1):
        if p.get("opts") is not None: check(not neg.search(plain(p["q"])), f"{t['id']}:{k} asks for what is not true: {plain(p['q'])[:80]}")
        for o in (p.get("opts") or []): check(not re.search(r"\b(all|none) of the above\b", plain(o), re.I), f"{t['id']}:{k} has an 'all or none of the above' option")
print(f"abrstyle: {n} checks"); print("abrstyle: PASS" if not bad else f"abrstyle: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
