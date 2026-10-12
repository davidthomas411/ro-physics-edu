"""Risk management and TG-100: every worked number and numeric answer re-derived by another route.
RPNs by counting the cells of an O × S × D grid; fault trees and independent checks by enumerating every combination of the basic events;
deviations in exact fractions and through a unit conversion (mCi); the wrong-site threshold by bisection; the medical event decisions by a
separate reading of 10 CFR 35.3045 applied to the numbers printed in the options."""
import sys, re, math, itertools
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # tests/numbers.py would shadow the standard numbers module that fractions imports
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import risk_management as R
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; TID = "risk-management"; bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def truth(c, what):
    global n; n += 1
    if not c: bad.append((what, "false", "true"))
def prob(phrase):
    hits = [p for p in T[TID]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def shown(p):                                                                   # every value offered as an option
    return sorted(p["vals"]) if p.get("vals") else []
def keyed_text(p): return [plain(p["opts"]["ABCDEFG".index(k)]) for k in p["key"]]
def cells(o, s, d): return sum(1 for _ in itertools.product(range(o), range(s), range(d)))     # an RPN counted as the cells of an O × S × D grid
def enum(probs, event):
    """Probability of an event, summed over every combination of independent basic events (1 = occurs)."""
    tot = 0.0
    for bits in itertools.product((0, 1), repeat=len(probs)):
        w = math.prod(p if b else 1 - p for b, p in zip(bits, probs))
        if event(bits): tot += w
    return tot
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(m): b = m
        else: a = m
    return b
guide = " ".join(plain(b[1]) if b[0] in ("p", "h2") else " ".join(plain(x) for x in (b[2], b[4], *b[3])) if b[0] == "ex" else "" for b in T[TID]["guide"])
cards = " ".join(plain(x) for c in T[TID]["cards"] for x in (*c["a"], *c["w"]))

# ---- the regulatory and accreditation constants quoted in the text (10 CFR 35.3045; Joint Commission sentinel event list)
for got, want, what in ((R.ME_TOTAL, 20, "total dose or dosage: 20% or more"), (R.ME_FRAC, 50, "single fraction: 50% or more"), (R.ME_SV, 0.5, "0.5 Sv to an organ or tissue"),
                        (R.ME_SITE, 50, "wrong site: 50% or more above the expected dose"), (R.REPORT_DAYS, 15, "written report within 15 days"), (R.TELL_HOURS, 24, "physician and patient within 24 hours"), (R.TJC, 25, "sentinel event: more than 25% above the planned dose")):
    close(got, want, 0, what)
truth("by the next calendar day" in guide and "within 15 days" in guide and "within 24 hours" in guide, "the deadlines are stated in the text")

# ---- worked example: two failure modes, ranked by RPN and by severity
ra, rb = cells(*R.FA[1:]), cells(*R.FB[1:])
close(R.ra, ra, 0, "RPN of the bolus error, counted"); close(R.rb, rb, 0, "RPN of the source-strength error, counted"); close(ra, 120, 0, "120"); close(rb, 108, 0, "108")
by_rpn = sorted([R.FA, R.FB], key=lambda f: -cells(*f[1:]))[0][0]; by_s = sorted([R.FA, R.FB], key=lambda f: -f[2])[0][0]
truth(by_rpn == R.FA[0] and by_s == R.FB[0], "the bolus error ranks first by RPN and the source-strength error first by severity")
truth(f"{ra} and {rb}" in guide, "the example prints both RPNs")
truth(f"= {ra}, with S = {R.FA[2]}" in cards and f"= {rb}, with S = {R.FB[2]}" in cards, "the card's working steps print the same RPNs")

# ---- worked example: top event of an OR gate over two AND branches, by enumeration of the four basic events
top = enum([R.a1, R.m1, R.a2, R.m2], lambda b: (b[0] and b[1]) or (b[2] and b[3]))
close(R.top, top, 1e-12, "top event"); close(top, 0.002998, 1e-9, "0.002998")
close(R.b1 + R.b2 - R.b1 * R.b2, top, 1e-12, "inclusion and exclusion give the same OR")
truth(f"{top:.4f}, about {top * 1000:.0f} plans in 1000" in guide and f"{top:.6f}" in guide, "the example prints the top-event probability")

# ---- worked example: error rate after one and after two independent checks
r1 = enum([R.e0, R.d1], lambda b: b[0] and not b[1]); r2 = enum([R.e0, R.d1, R.d2], lambda b: b[0] and not b[1] and not b[2])
close(R.r1, r1, 1e-12, "after one check"); close(R.r2, r2, 1e-12, "after two checks"); close(1 / r1, 1000, 1e-9, "1 in 1000"); close(1 / r2, 2500, 1e-9, "1 in 2500")
truth(f"1 in {1 / r1:,.0f} plans" in guide and f"1 in {1 / r2:,.0f}" in guide, "the example prints 1 in 1,000 and 1 in 2,500")
truth(f"= {r1:.4f} after one check" in cards and f"= {r2:.4f} after two" in cards, "the card's working steps print the same rates")

# ---- worked example: one wrong HDR fraction, in exact fractions, and the decision by a separate reading of the rule
def me_course(fr, per):
    """10 CFR 35.3045(a)(1)(i): the dose differs by more than 0.5 Sv (photons: 1 Gy = 1 Sv), and the total differs by 20% or more or one fraction by 50% or more."""
    fr = [Fr(str(x)) for x in fr]; per = Fr(str(per)); presc = per * len(fr); tot = sum(fr)
    differs = max(abs(tot - presc), *(abs(x - per) for x in fr)) > Fr(1, 2)
    return differs and (abs(tot - presc) / presc >= Fr(1, 5) or max(abs(x - per) / per for x in fr) >= Fr(1, 2))
fd = 100 * (Fr(str(R.hx)) - Fr(str(R.hp))) / Fr(str(R.hp)); td = 100 * (Fr(str(sum(R.h_del))) - 3 * Fr(str(R.hp))) / (3 * Fr(str(R.hp)))
close(R.h_fd, float(fd), 1e-12, "fraction deviation"); close(R.h_td, float(td), 1e-12, "course deviation"); close(float(fd), 54.2857, 1e-5, "+54.3%"); close(float(td), 18.0952, 1e-5, "+18.1%")
truth(me_course(R.h_del, R.hp) and R.h_me and td < 20 <= 50 <= fd, "a medical event under the single-fraction criterion, not under the total")
truth(f"+{float(fd):.1f}%" in guide and f"+{float(td):.1f}%" in guide and "A medical event, under the single-fraction criterion" in guide, "the example prints both deviations and the decision")

# ---- question: RPN with the classic slips as distractors
p = prob("scored on the TG-100 scales")
close(value(p), cells(R.q_o, R.q_s, R.q_d), 0, "keyed RPN"); close(value(p), 96, 0, "96")
truth(shown(p) == sorted([cells(R.q_o, R.q_s, R.q_d), R.q_o + R.q_s + R.q_d, R.q_o * R.q_s, cells(R.q_o, R.q_s, 11 - R.q_d)]) == [15, 32, 96, 256], "options: 15 (sum), 32 (no D), 96, 256 (D inverted)")
p = prob("have the same RPN")
truth(cells(*R.EQA) == cells(*R.EQB) == 120 and R.EQB[0] / R.EQA[0] == 3 and "three times" in " ".join(plain(o) for o in p["opts"]), "two failure modes with RPN 120, one occurring three times as often")
truth(keyed_text(p) == ["Failure mode 1, because its effect is catastrophic"] and R.EQA[1] == 10, "the keyed failure mode is the one with S = 10")

# ---- question: two checks on a 2% error rate, per 1000 plans
p = prob("before two independent checks"); g = [R.g0, R.g1, R.g2]
close(value(p), 1000 * enum(g, lambda b: b[0] and not b[1] and not b[2]), 1e-9, "error rate after both checks"); close(value(p), 2.4, 1e-9, "2.4 per 1000")
close(sorted(shown(p))[1], 1000 * enum(g[:2], lambda b: b[0] and not b[1]), 1e-9, "distractor: first check only (6.0)")
close(sorted(shown(p))[2], 1000 * enum(g, lambda b: b[0] and b[1] and b[2]), 1e-9, "distractor: detection probabilities multiplied (8.4)")
close(sorted(shown(p))[3], 1000 * enum([R.g0, R.g1 * R.g2], lambda b: b[0] and not b[1]), 1e-9, "distractor: the pair treated as one check (11.6)")


# ---- typed: three independent failures for a wrong-patient treatment
p = prob("Treating the wrong patient needs three")
close(value(p), 1e6 * math.exp(sum(math.log(x) for x in (R.w0, R.w1, R.w2))), 1e-9, "AND gate by logarithms"); close(value(p), 10, 1e-9, "10 per million fractions")
close(value(p), 1e6 * enum([R.w0, R.w1, R.w2], all), 1e-9, "AND gate by enumeration")

# ---- question: I-131 dosage, also in mCi (1 mCi = 37 MBq)
p = prob("radioactive iodine therapy"); mci = (R.i_rx / 37, R.i_giv / 37)
close(mci[0], 15, 1e-12, "555 MBq is 15 mCi"); close(mci[1], 20, 1e-12, "740 MBq is 20 mCi")
close(value(p), 100 * (mci[1] - mci[0]) / mci[0], 1e-9, "deviation in mCi"); close(value(p), 100 / 3, 1e-9, "33.3%")
truth(all(abs(a - b) < 1e-9 for a, b in zip(shown(p), [100 * 5 / 20, 100 / 3, 100 * 15 / 20, 100 * 20 / 15])), "options: 25.0 (wrong denominator), 33.3, 75.0 and 133.3 (ratios)")
truth(value(p) >= 20, "at or above the 20% dosage criterion")

# ---- question: lowest dose to an organ outside the treatment site that meets the wrong-site criterion, by bisection on the rule
p = prob("lowest dose to the organ"); site = lambda x: (x - R.s_exp >= 0.5 - 1e-12) and (x - R.s_exp) / R.s_exp >= 0.5 - 1e-12
thr = bisect(site, R.s_exp, 10.0)
close(value(p), thr, 1e-9, "threshold by bisection"); close(value(p), 1.1, 1e-9, "1.1 Gy")
truth(all(abs(a - b) < 1e-9 for a, b in zip(shown(p), [0.5, 0.9, 1.1, 1.4])), "options: 0.5 (0.5 Sv read as a dose), 0.9 (50% alone), 1.1, 1.4 (both increments added)")

# ---- question: one wrong HDR fraction in a five-fraction course
p = prob("An HDR cervix course")
f8 = 100 * (Fr(str(R.q8x)) - Fr(str(R.q8p))) / Fr(str(R.q8p)); t8 = 100 * (Fr(str(sum(R.q8_del))) - 5 * Fr(str(R.q8p))) / (5 * Fr(str(R.q8p)))
close(float(f8), 60, 1e-12, "fraction 60% high"); close(float(t8), 12, 1e-12, "course 12% high")
truth(me_course(R.q8_del, R.q8p) and keyed_text(p) == [f"Yes: one fraction differs by {float(f8):.0f}%, at or above the 50% limit"], "keyed: a medical event under the single-fraction criterion")

# ---- select two: which errors are medical events, decided from the numbers printed in the options
def nrc_me(text):
    pct = [int(x) for x in re.findall(r"(\d+)%", text)]
    if "linac" in text: return False                                             # no byproduct material: state rules
    if "wrong side" in text: return True                                         # a site outside the target far above its expected dose
    if "fraction" in text: return pct[0] >= 50 or pct[1] >= 20                   # one fraction, then the course
    return pct[0] >= 20                                                          # total dose or dosage
p = prob("Five errors are found in one year")
truth(sorted(keyed_text(p)) == sorted(plain(o) for o in p["opts"] if nrc_me(plain(o))), f"the keyed options are the medical events {keyed_text(p)}")
close(100 * (21 - sum(Fr(str(x)) for x in R._hdr_u)) / 21, 21.9047619, 1e-6, "HDR course 21.9% short, printed as 22%")
close(float(100 * (Fr("7.8") - 6) / 6), 30, 1e-12, "one fraction 30% high"); close(float(100 * (sum(Fr(str(x)) for x in R._hdr_o) - 30) / 30), 6, 1e-12, "course 6% high")
close(4255 / 37 / (3700 / 37) * 100 - 100, 15, 1e-9, "I-131 dosage 15% high (115 against 100 mCi)")

# ---- deadlines question: the keyed option carries the three time limits
p = prob("discovers a medical event")
truth(keyed_text(p) == ["NRC by telephone by the next calendar day; written report within 15 days; physician and patient within 24 hours"], "keyed deadlines: next calendar day, 15 days, 24 hours")

for b in bad: print("FAIL", b)
print(f"numbers_risk_management: {n} numbers re-derived"); print("numbers_risk_management: PASS" if not bad else f"numbers_risk_management: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
