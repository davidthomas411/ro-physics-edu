"""Image guidance and treatment verification: every worked number and keyed answer re-derived by another route
(shift lengths in two steps, rotations by a rotation matrix, the offline residual by simulation, the weighted dose by integrating
a radial dose profile over the phantom, imaging-dose shares by unit conversion, and electron radii from SI constants)."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]     # before the imports below: statistics imports the standard module numbers, which tests/numbers.py would shadow
import re, math, random, statistics
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
import igrt as G
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in G.PROBLEMS if phrase in plain(p["q"])]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                   # the number behind the keyed option, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def example(title):
    hits = [b for b in G.TOPIC["guide"] if b[0] == "ex" and b[1] == title]; assert len(hits) == 1, title; return hits[0]
text = " ".join(plain(b[1]) for b in G.TOPIC["guide"] if b[0] == "p")

# ---- shift length: the hypotenuse taken in two steps
def length2(dx, dy, dz): return math.hypot(math.hypot(dx, dy), dz)
d = G.ex_d
close(G.ex_len, length2(*d), 1e-12, "worked example: shift length")
check(all(abs(x) < G.ex_al for x in d) and length2(*d) > G.ex_al, "every component is below the action level and the length is above it")
check(plain(example("Length of a shift")[4]).startswith(f"{length2(*d):.1f} mm"), "the printed length matches")
p = prob("length of the shift vector"); q = G.q_d
close(value(p), length2(*q), 1e-12, "question: shift length"); close(length2(*q), 4.031, 1e-3, "about 4.0 mm")
close(sorted(p["vals"])[0], q[0] + q[1] + q[2], 1e-12, "decoy: the signed sum"); check(abs(q[0]) + abs(q[1]) + abs(q[2]) in p["vals"] and max(map(abs, q)) in p["vals"], "decoys: the sum of magnitudes and the largest component")

# ---- rotations: rotate a point with a rotation matrix and measure how far it moves
def rotate_z(pt, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a); x, y, z = pt
    return (c * x - s * y, s * x + c * y, z)
def moved(r, deg):
    p0 = (0.0, r, 0.0); p1 = rotate_z(p0, deg)
    return math.dist(p0, p1), abs(p1[0] - p0[0])                               # the chord, and the component across the original radius
chord, across = moved(G.ex_r, G.ex_th)
close(G.ex_rot, across, 1e-12, "worked example: r sin θ is the component across the radius"); close(G.ex_rot, chord, 2e-4, "and agrees with the chord within 0.02%")
check(plain(example("Rotation left uncorrected")[4]).startswith(f"{chord:.1f} mm"), "the printed displacement matches the chord")
chord, across = moved(G.t_r, G.t_th)
close(value(prob("point displaced")), chord, 2e-4, "typed question: 2.0° at 10 cm"); check(abs(value(prob("point displaced")) - chord) < 0.01, "the chord differs by less than 0.01 mm, as the explanation says")
chord, across = moved(100.0, 1.0)
close(G.card_rot, chord, 2e-4, "card: 1° at 10 cm"); check(f"{chord:.1f} mm at 10 cm for 1°" in plain(G.TOPIC["cards"][4]["a"][0]), "the card prints the same value")

# ---- offline correction: the mean, and the systematic error left, by simulation of many patients
close(G.ex_mean, statistics.fmean(G.ex_sh), 1e-12, "worked example: mean shift")
close(G.ex_res, math.sqrt(len(G.ex_sh) * G.ex_sig ** 2) / len(G.ex_sh), 1e-12, "worked example: SD of the mean of n random errors")
def simulate(sigma, n_img, big=2.5, patients=200000, seed=7):
    rng = random.Random(seed); left = []
    for _ in range(patients):
        s = rng.gauss(0, big)                                                   # the patient's systematic error
        m = statistics.fmean(s + rng.gauss(0, sigma) for _ in range(n_img))     # the mean of the imaged fractions
        left.append(s - m)                                                      # what stays after the correction
    return statistics.pstdev(left)
sim = simulate(G.s_sig, G.s_n)
close(value(prob("standard deviation of the systematic error")), sim, 0.01, f"question: residual systematic error against a simulation ({sim:.3f} mm)")
close(G.o_sig, sim, 0.01, "online-against-offline question: the offline residual")
close(G.ex_res, simulate(G.ex_sig, 3, seed=11), 0.01, "worked example: residual against a simulation")
check(sorted(prob("standard deviation of the systematic error")["vals"]) == sorted([G.s_sig / G.s_n, G.s_sig / math.sqrt(G.s_n), G.s_sig, G.s_sig * math.sqrt(G.s_n)]), "decoys: σ/n, σ, and σ√n")

# ---- weighted dose: the mean of a dose that changes linearly from the centre to the edge, integrated over the disc
def disc_mean(dc, dp, steps=20000):
    R = 1.0; h = R / steps; num = den = 0.0
    for i in range(steps):
        r = (i + 0.5) * h; ring = 2 * math.pi * r * h
        num += (dc + (dp - dc) * r / R) * ring; den += ring
    return num / den
close(G.ex_dw, disc_mean(G.ex_dc, G.ex_dp), 1e-7, "worked example: weighted dose")
close(G.ex_tot / 100 / G.ex_rx * 100, G.ex_pct, 1e-12, "worked example: share of the prescription, in Gy"); close(G.ex_pct, 0.80, 1e-9, "0.80%")
check(G.ex_pct < G.TG180_PCT, "below the TG-180 threshold")
p = prob("weighted dose of the scan")
close(value(p), disc_mean(G.w_dc, G.w_dp), 1e-7, "question: weighted dose"); close(value(p), 1.6, 1e-9, "1.60 cGy")
close(sorted(p["vals"])[3], G.w_dp, 1e-12, "decoy: the periphery alone"); close(sorted(p["vals"])[0], disc_mean(G.w_dp, G.w_dc), 1e-7, "decoy: the weights swapped"); close(sorted(p["vals"])[1], (G.w_dc + G.w_dp) / 2, 1e-12, "decoy: the plain mean")
gy = G.f_n * G.f_d / 100
close(value(prob("percentage of the prescription")), 100 * gy / G.f_rx, 1e-9, "typed question: imaging share of a course"); close(100 * (G.f_d / 100) / (G.f_rx / G.f_n), 100 * gy / G.f_rx, 1e-12, "the same share per fraction")

# ---- electron radius in the field: relativistic momentum from SI constants
M, C, E, MEV = 9.1093837015e-31, 299792458.0, 1.602176634e-19, 1.602176634e-13
def r_si(t_mev, b, kind="rel"):
    t = t_mev * MEV; mc2 = M * C * C
    p = {"rel": math.sqrt((t + mc2) ** 2 - mc2 ** 2) / C, "classical": math.sqrt(2 * M * t), "ke": t / C}[kind]
    return 1000 * p / (E * b)                                                  # mm
p = prob("radius of its path")
close(value(p), r_si(G.m_t, G.m_b), 1e-4, "question: radius of a 2 MeV electron at 1.5 T")
close(G.m_cl, r_si(G.m_t, G.m_b, "classical"), 1e-4, "decoy: classical momentum"); close(G.m_ke, r_si(G.m_t, G.m_b, "ke"), 1e-4, "decoy: kinetic energy as pc")
close(G.m_lo, r_si(G.m_t, 0.35), 1e-4, "decoy: the radius at 0.35 T"); check(sorted(p["vals"]) == sorted([G.m_r, G.m_cl, G.m_ke, G.m_lo]), "the options are the answer and the three decoys")
close(G.r1_15, r_si(1.0, 1.5), 1e-4, "text: 1 MeV at 1.5 T"); close(G.r1_035, r_si(1.0, 0.35), 1e-4, "text: 1 MeV at 0.35 T")
check(f"{r_si(1.0, 1.5):.1f} mm at 1.5 T and {r_si(1.0, 0.35):.1f} mm at 0.35 T" in text, "the text prints the radii")
close(r_si(1.0, 0.35) / r_si(1.0, 1.5), 1.5 / 0.35, 1e-9, "the radius goes as 1/B")

# ---- TG-142: the keyed tolerance, with the conventional value among the options
p = prob("daily coincidence of the imaging and treatment isocenters")
close(value(p), 1.0, 0, "SRS/SBRT tolerance 1 mm"); check(G.TG142_ISO in p["vals"] and len(p["opts"]) == 5, "the 2 mm conventional value is an option")

for b in bad: print("FAIL", b)
print(f"numbers_igrt: {n} numbers re-derived"); print("numbers_igrt: PASS" if not bad else f"numbers_igrt: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
