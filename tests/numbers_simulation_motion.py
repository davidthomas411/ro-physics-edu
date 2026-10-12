"""Simulation and motion management: every number the chapter prints or keys, re-derived by another route
(rotation matrices and the exact chord for registration errors, slice integration and Monte Carlo sampling for swept volumes,
time-stepped breathing for gated and breath-hold deliveries, a bisection for the 4D-CT pitch, sampling of a sinusoid for an amplitude gate,
and exact fractions and random sampling for errors that add in quadrature)."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard numbers module that fractions uses
import re, math, random
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import blocks
import simulation_motion as M
plain = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
tp = next(t for t in TOPICS if t["id"] == "simulation-motion"); bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what,))
def prob(phrase):
    hits = [p for p in tp["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def fsqrt(q):                                                                   # exact square root of a fraction that is a perfect square
    a, b = math.isqrt(q.numerator), math.isqrt(q.denominator); assert a * a == q.numerator and b * b == q.denominator, q; return Fr(a, b)
text = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()       # page text with a space where each tag was
GUIDE = re.sub(r"<[^>]+>", "", blocks.render(tp["guide"], {}, tid=tp["id"])); GUIDE = re.sub(r"\s+", " ", GUIDE)
CARDS = " ".join(plain(x) for c in tp["cards"] for x in c["a"] + c["w"])
def shown(s, where=None, what=""): check(s in (GUIDE if where is None else where), f"printed: {what or s}")

# ---- registration: a rotation error, by a rotation matrix and by the exact chord
def rotate(x, y, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return c * x - s * y, s * x + c * y
def moved(r, deg):                                                              # sideways (perpendicular to the radius) and radial parts of the displacement, and the chord
    x, y = rotate(r, 0.0, deg); return y, r - x, math.hypot(x - r, y)
for r, d in ((M.RA, M.dA), (M.RB, M.dB)):
    side, radial, chord = moved(r, M.TH_EX)
    close(d, side, 1e-12, f"sideways displacement at {r} mm, from the rotation matrix")
    close(d, chord, 2e-4, f"r sin θ is within 0.02% of the exact chord 2 r sin(θ/2) at {r} mm")
    close(chord, 2 * r * math.sin(math.radians(M.TH_EX) / 2), 1e-12, "the chord formula")
shown(f"{M.dA:.2f} mm at A and {M.dB:.2f} mm at B"); close(round(M.dB, 2), 3.14, 1e-12, "3.14 mm at 90 mm"); check(M.dB > 3.0 > 2.0 > M.dA, "B lies beyond 2 to 3 mm and A inside it")

# ---- 4D-CT: the highest pitch, by bisection on the time a point spends in the beam
W, TROT, TB = 24.0, 0.5, 4.0
in_beam = lambda p: W / (p * W / TROT)                                          # coverage divided by the table speed
p_max = bisect(lambda p: in_beam(p) - TB, 1e-4, 10)
close(p_max, 0.125, 1e-9, "0.125")
close(300 / (p_max * W / TROT), 50.0, 1e-9, "300 mm takes 50 s at that pitch"); close(300 / (1.0 * W / TROT), 6.25, 1e-12, "and 6.25 s at pitch 1")
close(in_beam(TB / TROT), 0.0625, 1e-12, "the inverted ratio leaves a point in the beam for 0.0625 s")

# ---- swept volume of a moving sphere: slices along the path, and Monte Carlo
def slice_volume(r, d, steps=20000):                                            # Simpson's rule over the cross-sections of the capsule along its axis
    L = d + 2 * r; h = L / steps
    def area(z):
        u = z - r                                                               # u runs from -r to d + r
        if u < 0: return math.pi * max(0.0, r * r - u * u)
        if u > d: return math.pi * max(0.0, r * r - (u - d) ** 2)
        return math.pi * r * r
    s = area(0) + area(L) + sum((4 if i % 2 else 2) * area(i * h) for i in range(1, steps))
    return s * h / 3
def mc_volume(r, a, b, N=200000, seed=7):                                       # sphere of radius r whose centre moves from the origin to (a, b, 0) in a straight line
    rng = random.Random(seed); xs = (-r, a + r) if a >= 0 else (a - r, r); ys = (-r, b + r); zs = (-r, r); box = (xs[1] - xs[0]) * (ys[1] - ys[0]) * (zs[1] - zs[0]); hit = 0
    L2 = a * a + b * b
    for _ in range(N):
        x, y, z = rng.uniform(*xs), rng.uniform(*ys), rng.uniform(*zs)
        t = max(0.0, min(1.0, (x * a + y * b) / L2)); dx, dy = x - t * a, y - t * b
        hit += dx * dx + dy * dy + z * z <= r * r
    return box * hit / N
close(M.path1, 13.0, 1e-12, "the 5-12-13 path"); close(M.v_itv1, slice_volume(M.R1, M.path1), 1e-6, "ITV of the worked example by slices")
close(M.v_itv1, mc_volume(M.R1, M.SI1, M.AP1), 0.02, "and by Monte Carlo within 2%"); close(M.v_sph1, 4 / 3 * math.pi * 15 ** 3, 1e-12, "the tumour volume")
shown(f"{M.v_itv1 / 1000:.1f} cm³, {M.v_itv1 / M.v_sph1:.2f} times the {M.v_sph1 / 1000:.1f} cm³"); close(round(M.v_itv1 / 1000, 1), 23.3, 1e-12, "23.3 cm³")
shown("30 + 12 = 42 mm superior–inferior, 30 + 5 = 35 mm anterior–posterior, 30 mm left–right", what="the extents of the worked example")

# ---- gating: the worked example by stepping through the breaths
def gated(t_on, period, gate, dt=1e-3):                                         # seconds until t_on seconds of beam are given, with the gate open for the first `gate` seconds of each breath
    t = done = 0.0; steps = 0
    while done < t_on - 1e-9:
        if (steps * dt) % period < gate - 1e-12: done += dt
        steps += 1
    return steps * dt
ton_s = M.MU_G / M.RATE_G * 60; sim = gated(ton_s, M.T_B, M.GATE)
close(M.ton_g, 1.5, 1e-12, "600 MU at 400 MU/min is 1.5 min"); close(M.duty_g, sum(1 for i in range(40000) if (i * 1e-4) % 4.0 < 1.2) / 40000, 1e-9, "duty cycle by sampling one breath")
check(abs(sim - M.tdel_g * 60) <= M.T_B, f"the stepped delivery ({sim:.1f} s) is within one breath of beam-on time / duty cycle ({M.tdel_g * 60:.0f} s)")
shown(f"{M.tdel_g:.1f} min, {M.tdel_g - M.ton_g:.1f} min longer than the {M.ton_g:.1f} min without gating"); close(M.tdel_g, 5.0, 1e-12, "5.0 min")
shown(f"Gate open {M.GATE:.1f} s of a {M.T_B:.1f} s breath: duty cycle 30%", CARDS, "the duty-cycle card")

# ---- an amplitude gate on a sinusoid, by sampling the signal
N = 600000; frac = sum(1 for i in range(N) if 0.5 * (1 - math.cos(2 * math.pi * (i + 0.5) / N)) < 0.25) / N
q = prob("lowest 25% of its range"); close(value(q), 100 * frac, 1e-4, "33.3% by sampling"); close(value(q), 100 / 3, 1e-12, "a third of the cycle")
check(set(round(v, 6) for v in q["vals"]) == {round(100 / 3, 6), 25.0, round(100 / 6, 6), round(200 / 3, 6)}, "decoys: the amplitude share, one side only, and the time outside")

# ---- ranking of deliveries, by stepping through each
def holds(t_on, hold, rest, dt=1e-3):                                           # beam during holds, free breathing between them, nothing after the last
    t = done = 0.0; steps = 0
    while done < t_on - 1e-9:
        if (steps * dt) % (hold + rest) < hold - 1e-12: done += dt
        steps += 1
    return steps * dt
sims = {"Free breathing with an ITV, beam on throughout": M.T_ON, "Gating with a duty cycle of 50%": gated(M.T_ON, 4.0, 2.0),
        "Breath holds of 20 s, with 40 s of free breathing between holds": holds(M.T_ON, 20, 40), "Gating with a duty cycle of 30%": gated(M.T_ON, 4.0, 1.2)}
rk = prob("Rank the deliveries"); want = sorted(sims, key=sims.get)
check(all(want.index(c["t"]) == c["b"] for c in rk["chips"]), f"the keyed order matches the stepped times {[round(sims[k]) for k in want]}")
close(holds(M.T_ON, 20, 40), M.t_hold, 1e-3, "five holds and four breaks: 250 s"); close(M.t_hold, 250.0, 1e-12, "250 s")
check(f"{M.T_ON} + 4 × 40 = 250 s" in plain(rk["a"][1]) and "180 s" in plain(rk["a"][1]) and "300 s" in plain(rk["a"][1]), "the explanation prints the times")

# ---- margins: exact fractions, and random sampling of independent errors
S2 = sum(Fr(str(x)) ** 2 for x in M.SYS_EX); s2 = sum(Fr(str(x)) ** 2 for x in M.RND_EX)
S, s = fsqrt(S2), fsqrt(s2); m = Fr(5, 2) * S + Fr(7, 10) * s
close(M.S_ex, float(S), 1e-12, "Σ = 2.9 mm exactly"); close(M.s_ex, float(s), 1e-12, "σ = 3.0 mm exactly"); close(M.m_ex, float(m), 1e-12, "margin 9.35 mm exactly")
close(M.m_lin, float(Fr(5, 2) * sum(Fr(str(x)) for x in M.SYS_EX) + Fr(7, 10) * sum(Fr(str(x)) for x in M.RND_EX)), 1e-12, "linear sums: 15.19 mm")
shown(f"{M.m_ex:.2f} mm. Adding the components directly gives Σ = {sum(M.SYS_EX):.1f} mm and σ = {sum(M.RND_EX):.1f} mm, and a margin of {M.m_lin:.1f} mm")
rng = random.Random(11); K = 200000
tot = [sum(rng.gauss(0, x) for x in M.SYS_EX) for _ in range(K)]; sd = math.sqrt(sum(v * v for v in tot) / K)
close(sd, M.S_ex, 0.01, "the standard deviation of a sum of independent errors, sampled, is the quadrature sum")
q = prob("Three independent systematic errors"); close(value(q), float(fsqrt(Fr(1) + Fr(4) + Fr(4))), 1e-12, "Σ of 1, 2, and 2 mm is 3 mm")
q = prob("lung site"); Sq, sq = fsqrt(Fr("1.5") ** 2 + Fr(2) ** 2), fsqrt(Fr("2.4") ** 2 + Fr("3.2") ** 2)
close(value(q), float(Fr(5, 2) * Sq + Fr(7, 10) * sq), 1e-12, "9.05 mm"); close(round(value(q), 2), 9.05, 1e-12, "as printed")
check({round(v, 6) for v in q["vals"]} == {9.05, round(2.5 * 3.5 + 0.7 * 5.6, 6), round(2.5 * 4.0 + 0.7 * 2.5, 6), 6.25}, "decoys: linear sums, Σ and σ exchanged, and the random part left out")
q = prob("both 3 mm"); check("0.7 × 3 = 2.1 mm" in plain(q["a"][1]) and "2.5 × 3 = 7.5 mm" in plain(q["a"][1]), "the two contributions of 3 mm")

# ---- quoted tolerances agree between the table and the take-aways
TAKE = " ".join(plain(x) for items in tp["take"] for x in items)
for s_ in ("±2 mm", "0 ± 5 HU", "±1 mm"): shown(s_, what=f"{s_} in the table")
check("±2 mm" in TAKE and "0 ± 5 HU" in TAKE and "30% to 50%" in TAKE and "30% to 50%" in GUIDE and "30% to 50%" in CARDS, "the same tolerances and duty cycles throughout")

for b in bad: print("FAIL", b)
print(f"numbers_simulation_motion: {n} numbers re-derived"); print("numbers_simulation_motion: PASS" if not bad else f"numbers_simulation_motion: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
