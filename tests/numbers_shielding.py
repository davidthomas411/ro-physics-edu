"""Shielding design for linac vaults: every worked number and keyed answer re-derived by another route.
The chapter inverts B = P d² / (W U T) in closed form; here each thickness is found by bisection on the weekly dose behind the barrier,
with the attenuation written as natural exponentials, and each transmission is checked by putting it back into the dose."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import shielding as S
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T_ = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def prob(phrase):
    hits = [p for p in T_["shielding"]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def opt_values(p): return sorted(p["vals"])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
LN10 = math.log(10.0)
def att(t, tvl1, tvle):                                                        # broad-beam transmission as natural exponentials: mu1 = ln 10 / TVL1 over the first layer, mue = ln 10 / TVLe after it
    return math.exp(-LN10 / tvl1 * t) if t <= tvl1 else math.exp(-LN10 - LN10 / tvle * (t - tvl1))
def t_for_dose(dose_at, P):                                                    # thickness at which the weekly dose behind the barrier equals P
    return bisect(lambda t: dose_at(t) - P, 0.0, 600.0)
GUIDE = " ".join(plain(b[1]) if b[0] in ("h2", "p") else " ".join(plain(x) for x in b[1]) if b[0] in ("ul", "ol", "eq") else
                 " ".join(plain(x) for x in [b[1], b[2], b[4], *b[3]]) if b[0] == "ex" else " ".join(plain(c) for r in b[2] for c in r) if b[0] == "table" else "" for b in T_["shielding"]["guide"])
def shown(s, what):                                                            # a re-derived number, formatted, appears on the page
    global n; n += 1
    if s not in GUIDE: bad.append((what, "not found in the text", s))
PRI6, LEAK6, PRI18 = (37.0, 33.0), (34.0, 29.0), (45.0, 43.0)

# ---- design goals and workload
close(S.P_C, 5e-3 / 50, 1e-12, "controlled goal 5 mSv over 50 weeks"); close(S.P_U * 50, 1e-3, 1e-12, "uncontrolled goal times 50 weeks is 1 mSv")
shown("0.1 mSv per week", "controlled goal printed"); shown("0.02 mSv per week", "uncontrolled goal printed")
w_sum = sum(sum(3.0 for _ in range(30)) for _ in range(5))                     # each day's patients, each at 3 Gy at 1 m
close(S.W1, w_sum, 1e-12, "workload 450 Gy/week"); shown("450 Gy/week", "workload printed")
close(value(prob("30 patients a day")), w_sum, 1e-12, "keyed workload"); close(opt_values(prob("30 patients a day"))[-1], 4 * w_sum, 1e-12, "distractor: the 4 fields counted again")
close(value(prob("spread over 50 working weeks")), 1.0 / 50, 1e-12, "keyed weekly goal in mSv")

# ---- primary barrier, worked example: dose behind the wall equals P at the computed thickness
dose1 = lambda t: S.W1 * 0.25 * 1.0 * att(t, *PRI6) / 6.0 ** 2
t1 = t_for_dose(dose1, S.P_U)
close(S.t1, t1, 1e-9, "primary thickness by bisection"); shown(f"{t1:.0f} cm of ordinary concrete", "primary thickness printed")
close(S.B1, dose1(t1) * 6.0 ** 2 / (S.W1 * 0.25), 1e-9, "B at that thickness"); shown(plain(S.sci(att(t1, *PRI6), 3)), "B printed")
close(S.n1, -math.log(att(t1, *PRI6)) / LN10, 1e-9, "number of TVLs")

# ---- the transmission of an existing 200 cm wall and the weekly dose behind it
B2 = att(200.0, *PRI6); H2 = S.W1 * 0.25 * B2 / 36.0
close(S.B2, B2, 1e-9, "transmission of 200 cm"); close(S.n2, -math.log(B2) / LN10, 1e-9, "TVLs in 200 cm");close(S.H2, H2, 1e-9, "weekly dose at the point"); close(S.H2T, H2 / 5, 1e-9, "times T = 1/5")
shown(f"{H2 * 1e6:.1f} µSv per week at the point", "dose at the point printed"); shown(f"{H2 / 5 * 1e6:.2f} µSv per week for the most exposed person", "dose to the person printed")
close(1 if H2 / 5 < S.P_U else 0, 1, 0, "the existing wall meets the goal")

# ---- doubled workload and a corridor: bisection again, and the log rule
t4 = t_for_dose(lambda t: 2 * S.W1 * 0.25 * 0.2 * att(t, *PRI6) / 36.0, S.P_U)
close(S.t4, t4, 1e-9, "new thickness"); close(t4 - t1, 33.0 * math.log(2 / 5) / LN10, 1e-6, "change = TVLe log10(2/5)"); shown(f"{t4:.0f} cm. A factor of 10", "new thickness printed")
close(S.dW, 33.0 * math.log(2) / LN10, 1e-12, "one HVL of concrete at 6 MV"); close(S.dT, 33.0 * math.log(5) / LN10, 1e-12, "log10 5 TVLs")
close(round(S.dW), 10, 0, "the card says about 10 cm")

# ---- barrier width and slant thickness
half = math.hypot(0.20, 0.20) * 7.0 + 0.3                                      # half the diagonal at 1 m, projected, plus the margin
close(S.width, 2 * half, 1e-12, "width by halves"); shown(f"{2 * half:.1f} m at d", "width printed"); shown(f"{math.hypot(0.4, 0.4):.2f} m at 1 m", "diagonal printed")
slant = math.hypot(150.0, 150.0 * math.tan(math.radians(30)))
close(value(prob("30° from the normal")), slant, 1e-12, "slant thickness by Pythagoras")

# ---- transmission question: the keyed B gives exactly P behind the barrier
p = prob("staff work area (controlled)"); qb = value(p)
close(500.0 * 0.25 * 1.0 * qb / 5.5 ** 2, 1e-4, 1e-12, "keyed B returns P = 0.1 mSv")
for got, want in zip(sorted(p["vals"]), sorted([qb, qb / 4, qb / 5.5, qb * 50])): close(got / want, 1.0, 1e-12, "distractors: U left out, d in place of d², annual goal")

# ---- which of two walls is thicker
tA = t_for_dose(lambda t: 450.0 * 0.25 * 1.0 * att(t, *PRI6) / 49.0, S.P_U); tB = t_for_dose(lambda t: 450.0 * 0.25 * 0.2 * att(t, *PRI6) / 16.0, S.P_U)
close(S.q_two, tA - tB, 1e-6, "wall A thicker by the difference of two bisections"); close(round(tA - tB), 7, 0, "about 7 cm")
close(S.q_two_T, 33.0 * math.log(5) / LN10, 1e-12, "occupancy alone"); close(S.q_two_d, 33.0 * math.log(49 / 16) / LN10, 1e-12, "distance alone")
close(1 if "Wall A, by about 7 cm" in plain(prob("Two primary walls")["a"][0]) else 0, 1, 0, "the keyed option is wall A by 7 cm")

# ---- doubling the workload adds one HVL
p = prob("The workload will double"); keyed = plain(p["a"][0])
close(1 if f"About {round(t_for_dose(lambda t: 900.0 * 0.25 * att(t, *PRI6) / 36.0, S.P_U) - t1)} cm" in keyed else 0, 1, 0, "keyed: about 10 cm")
close(S.q_ln2, 33.0 * math.log(2), 1e-12, "the ln 2 distractor")

# ---- leakage with IMRT: bisection on the leakage dose
leak = lambda W, CI, d, T: (lambda t: 1e-3 * W * CI * T * att(t, *LEAK6) / d ** 2)
qL = t_for_dose(leak(400.0, 4.0, 6.0, 1.0), S.P_U)
close(value(prob("head leakage.")), qL, 1e-9, "keyed leakage thickness")
close(S.qL_noCI, t_for_dose(leak(400.0, 1.0, 6.0, 1.0), S.P_U), 1e-9, "distractor without C_I")
close(S.qL_pri, t_for_dose(lambda t: 1e-3 * 400.0 * 4.0 * att(t, *PRI6) / 36.0, S.P_U), 1e-9, "distractor with primary TVLs")
close(S.qL_no1000, t_for_dose(lambda t: 400.0 * 4.0 * att(t, *LEAK6) / 36.0, S.P_U), 1e-9, "distractor without the leakage fraction")
close(qL - S.qL_noCI, 29.0 * math.log(4) / LN10, 1e-6, "C_I = 4 adds log10 4 equilibrium TVLs")
bL = S.P_U / leak(400.0, 4.0, 6.0, 1.0)(0.0); close(bL, 4.5e-4, 1e-9, "leakage B printed in the explanation"); close(-math.log(bL) / LN10, 3.35, 2e-3, "n = 3.35")
close(S.dA, math.log(80 / 49) / LN10, 1e-12, "wall A needs log10(80/49) more TVLs"); close(round(S.dA, 2), 0.21, 1e-12, "0.21 TVL")

# ---- secondary wall at 90 degrees: scatter and leakage by bisection, then the rule
sca = lambda t: S.A6 * S.W1 * (400.0 / 400.0) * 1.0 * math.exp(-LN10 * t / 17.0) / (1.0 ** 2 * 5.0 ** 2)
ts = t_for_dose(sca, S.P_C); tL = t_for_dose(leak(S.W1, 5.0, 5.0, 1.0), S.P_C); tLc = t_for_dose(leak(S.W1, 1.0, 5.0, 1.0), S.P_C)
close(S.ts3, ts, 1e-9, "scatter thickness"); close(S.tL3, tL, 1e-9, "leakage thickness"); close(S.tL3c, tLc, 1e-9, "leakage thickness without IMRT")
close(S.Bs3, S.P_C / sca(0.0), 1e-9, "scatter transmission = P over the unshielded scatter dose"); close(S.BL3, S.P_C / leak(S.W1, 5.0, 5.0, 1.0)(0.0), 1e-9, "leakage transmission = P over the unshielded leakage dose")
close(S.ns3, ts / 17.0, 1e-9, "scatter TVLs"); close(S.nL3, 1 + (tL - 34.0) / 29.0, 1e-9, "leakage TVLs")
close(1 if tL - ts > 34.0 else 0, 1, 0, "the two differ by more than one TVL, so the larger is used")
close((leak(S.W1, 5.0, 5.0, 1.0)(tL) + sca(tL)) / S.P_C, 1.0, 1e-3, "at the leakage thickness the scatter adds under 0.1% to the dose")
shown(f"{tL:.0f} cm, set by leakage", "secondary thickness printed"); shown(f"{tL - tLc:.1f} cm", "IMRT increment printed"); shown(f"{tLc:.1f} cm", "without IMRT printed")

# ---- the two-source rule: one HVL halves both components
hvl = 29.0 * math.log(2) / LN10
close(value(prob("calculated for each component separately")), 80.0 + hvl, 1e-12, "80 cm plus one HVL")
close(att(34.0 + 50.0 + hvl, *LEAK6) / att(34.0 + 50.0, *LEAK6), 0.5, 1e-12, "one HVL halves the leakage dose")

# ---- the ranking: four thicknesses by bisection in descending order
r = [t_for_dose(lambda t: 450.0 * 0.25 * 1.0 * att(t, *PRI6) / 36.0, S.P_U), t_for_dose(lambda t: 450.0 * 0.25 * (1 / 40) * att(t, *PRI6) / 36.0, S.P_U),
     t_for_dose(leak(450.0, 1.0, 6.0, 1.0), S.P_U), t_for_dose(lambda t: S.A6 * 450.0 * math.exp(-LN10 * t / 17.0) / 36.0, S.P_U)]
for (txt, v), w in zip(S.RANK, r): close(v, w, 1e-9, f"rank thickness: {plain(txt)[:30]}")
close(1 if r == sorted(r, reverse=True) else 0, 1, 0, "thickest to thinnest")
p = prob("Rank the barriers"); close(1 if [c["b"] for c in p["chips"]] == [0, 1, 2, 3] else 0, 1, 0, "each item is keyed to its rank")
close(math.log(40) / LN10, 1.6, 0.02, "log10 40 is 1.6 TVL")

# ---- the 18 MV typed question
t18 = t_for_dose(lambda t: 500.0 * 0.25 * 0.2 * att(t, *PRI18) / 49.0, S.P_U)
close(value(prob("18 MV primary barrier")), t18, 1e-9, "18 MV thickness by bisection")
close(S.q_B18, S.P_U * 49.0 / (500.0 * 0.25 * 0.2), 1e-12, "18 MV transmission"); close(S.q_B18 * 500.0 * 0.25 * 0.2 / 49.0, S.P_U, 1e-12, "and it returns P")

for b in bad: print("FAIL", b)
print(f"numbers_shielding: {n} numbers re-derived"); print("numbers_shielding: PASS" if not bad else f"numbers_shielding: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
