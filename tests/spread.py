"""Answer spread: the position of the correct option is not biased toward any letter, and the correct option is not given away by its length.
Single-answer questions with four options: every letter holds 20 to 30 percent, overall and among the numeric questions (whose options are sorted ascending, so the
authored wrong values decide the position); a chi-square test against an even spread is not significant. Questions with text options: the correct option is the
strictly longest in at most 35 percent, and in at most 8 percent is it more than 1.5 times the mean length of the other options."""
import sys, re, math, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s)
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
    else: print("ok  ", m)
def pval(x, df):
    a = df / 2.0; xx = x / 2.0
    if xx <= 0: return 1.0
    s = 1.0 / a; term = s; k = 1
    while abs(term) > 1e-12 * abs(s): term *= xx / (a + k); s += term; k += 1
    return max(0.0, 1 - s * math.exp(-xx + a * math.log(xx) - math.lgamma(a)))
rows = []
for t in TOPICS:
    for p in t["problems"]:
        if not p.get("opts") or p["multi"] or len(p["opts"]) != 4: continue
        opts = [plain(o) for o in p["opts"]]; k = "ABCD".index(p["key"][0])
        numeric = all(re.fullmatch(r"[−\-+]?[\d.,]+(\s*[^\s\d].*)?", o.strip()) for o in opts)
        rows.append((k, numeric, opts))
def spread(name, rs):
    c = collections.Counter(r[0] for r in rs); N = len(rs); sh = [100 * c[i] / N for i in range(4)]
    x = sum((c[i] - N / 4) ** 2 / (N / 4) for i in range(4)); p = pval(x, 3)
    check(all(20 <= s <= 30 for s in sh) and p > 0.05, f"{name}: A {sh[0]:.0f}%, B {sh[1]:.0f}%, C {sh[2]:.0f}%, D {sh[3]:.0f}% of {N} (chi-square p = {p:.2f})")
spread("all single-answer questions", rows); spread("numeric options", [r for r in rows if r[1]]); spread("text options", [r for r in rows if not r[1]])
txt = [r for r in rows if not r[1]]; longest = 0; big = 0; ratios = []
for k, _, opts in txt:
    ls = [len(o) for o in opts]; oth = [l for j, l in enumerate(ls) if j != k]; r = ls[k] / (sum(oth) / len(oth)); ratios.append(r)
    longest += ls[k] == max(ls) and ls.count(max(ls)) == 1; big += r > 1.5
check(longest / len(txt) <= 0.35, f"the correct text option is the strictly longest in {100 * longest / len(txt):.0f}% of {len(txt)} questions (limit 35%)")
check(big / len(txt) <= 0.08, f"the correct text option is over 1.5 times the others' mean length in {100 * big / len(txt):.0f}% (limit 8%); median ratio {sorted(ratios)[len(ratios) // 2]:.2f}")
print(f"spread: {n} checks"); print("spread: PASS" if not bad else f"spread: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
