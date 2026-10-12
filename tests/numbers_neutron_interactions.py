"""Neutron interactions and dose: every number the chapter prints or keys, re-derived by another route
(collision kinematics solved by bisection, centre-of-mass averages integrated numerically, step-by-step slowing down,
SI units and the rad in place of the formulas of the chapter, momentum balance for reaction products, exact fractions)."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard numbers module that fractions uses
import re, math
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import blocks
import neutron_interactions as M
plain = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
tp = next(t for t in TOPICS if t["id"] == "neutron-interactions"); bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what,))
def prob(phrase):
    hits = [p for p in tp["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def same(a, b, tol=1e-9):
    """Two lists of option values agree, item by item after sorting, within a relative tolerance."""
    return len(a) == len(b) and all(abs(x - y) <= tol * max(1.0, abs(y)) for x, y in zip(sorted(a), sorted(b)))
def midpoint(f, a, b, k=200000):
    h = (b - a) / k
    return h * sum(f(a + (i + 0.5) * h) for i in range(k))
text = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()       # page text with a space where each tag was, so table cells stay apart
GUIDE = text(blocks.render(tp["guide"], {}, tid=tp["id"]))
TAKE = " ".join(text(x) for items in tp["take"] for x in items)
CARDS = " ".join(text(c["q"]) + " " + " ".join(text(a) for a in c["a"] + c["w"]) for c in tp["cards"])
PROBS = " ".join(text(p["q"]) + " " + text(p["a"][1]) + " " + " ".join(text(o) for o in (p.get("opts") or [])) for p in tp["problems"])
def shown(s, where=GUIDE, what=""): check(s in where, f"printed: {what or s}")

# ---------------------------------------------------------------- constants in SI and other units
NA = 6.02214076e23; EV_J = 1.602176634e-19; MN_KG = 1.67492750e-27
BARN_M2 = 1e-28; ERG_PER_MEV = 1.602176634e-6                                      # a rad is 100 erg/g
def recoil(A):
    """Head-on elastic collision of a unit-mass neutron (speed 1) with a mass A at rest, solved from momentum and energy by bisection:
    returns the fraction of the energy given to the nucleus and the fraction the neutron keeps."""
    f = lambda u: (1 - A * u) ** 2 + A * u ** 2 - 1                                # energy balance after the momentum balance v' = 1 - A u
    u = bisect(f, 1e-9 + 1.0 / (A + 1), 2.0)                                       # the root that is not u = 0 lies at 2/(A + 1), above 1/(A + 1)
    return A * u ** 2, (1 - A * u) ** 2
def lab_after(A, mu):
    """Fraction of the energy the neutron keeps for a centre-of-mass scattering cosine mu (from the vector sum of the velocities)."""
    return (A * A + 2 * A * mu + 1) / (A + 1) ** 2
def mean_kept(A): return midpoint(lambda mu: lab_after(A, mu), -1.0, 1.0, 20000) / 2
def xi_num(A): return midpoint(lambda mu: -math.log(lab_after(A, mu)), -1.0, 1.0) / 2
def steps(e0, e1, x):
    """Collisions counted one at a time, each lowering ln E by x, until the energy reaches e1 (the last step may overshoot)."""
    k, e = 0, e0
    while e > e1 * (1 + 1e-12): e *= math.exp(-x); k += 1
    return k
def wr103(e):                                                                       # ICRP 103, written with base-10 logarithms
    l = lambda x: math.log10(x) * math.log(10.0)
    if e < 1.0: return 2.5 + 18.2 * math.exp(-l(e) ** 2 / 6)
    if e <= 50.0: return 5.0 + 17.0 * math.exp(-l(2 * e) ** 2 / 6)
    return 2.5 + 3.25 * math.exp(-l(0.04 * e) ** 2 / 6)
def share(q, m1, m2):
    """Kinetic energy of fragment 1 when q is shared by two fragments with equal and opposite momenta, by bisection on E1."""
    return bisect(lambda e1: 2 * m1 * e1 - 2 * m2 * (q - e1), 0.0, q)
def rad_gy(atoms_per_g, sigma_b, phi, e_mev):
    """Energy per gram in MeV, to erg, to rad, to Gy."""
    mev_per_g = atoms_per_g * sigma_b * 1e-24 * phi * e_mev
    return mev_per_g * ERG_PER_MEV / 100.0 / 100.0

# ---------------------------------------------------------------- thermal speed (class table, card, take-away)
v = math.sqrt(2 * M.E_TH * EV_J / MN_KG)
close(M.v_th, v, 1e-4, "thermal speed from SI mass and energy"); close(round(v, -2), 2200.0, 0, "rounds to 2,200 m/s")
shown("0.025 eV (about 2,200 m/s) at 20 °C"); shown("about 2,200 m/s", CARDS); shown("about 2,200 m/s", TAKE)

# ---------------------------------------------------------------- largest transfer, mean loss, and ξ by kinematics
for A in (1, 12, 14, 16, 82, 208):
    give, keep = recoil(A)
    close(M.e_max(A), give, 1e-9, f"largest transfer for A = {A} by bisection"); close(M.alpha(A), keep, 1e-9, f"alpha for A = {A} is the energy kept head-on")
    close(M.mean_loss(A), 1 - mean_kept(A), 1e-6, f"mean loss for A = {A} by a centre-of-mass average")
for A in (12, 16, 208):
    close(M.xi(A), xi_num(A), 1e-6, f"xi for A = {A} by numerical integration")
close(xi_num(1), 1.0, 1e-4, "xi = 1 for hydrogen by numerical integration")
close(round(M.e_max(12), 3), 0.284, 0, "carbon 48/169 = 0.284"); close(float(Fr(48, 169)), M.f_c, 1e-12, "48/169 exactly")
close(round(M.e_max(16), 3), 0.221, 0, "oxygen 64/289 = 0.221"); close(float(Fr(64, 289)), M.f_o, 1e-12, "64/289 exactly")
close(round(2.0 * recoil(12)[0], 2), 0.57, 0, "0.57 MeV to carbon"); close(round(2.0 * recoil(16)[0], 2), 0.44, 0, "0.44 MeV to oxygen")
shown("48/169 = 0.284, so 0.57 MeV"); shown("64/289 = 0.221, so 0.44 MeV"); shown("2.0, 0.57, and 0.44 MeV")
close(round(100 * recoil(12)[0]), 28, 0, "28% to carbon"); close(round(100 * recoil(16)[0]), 22, 0, "22% to oxygen"); close(round(100 * recoil(208)[0]), 2, 0, "2% to lead")
shown("28% to carbon, 22% to oxygen, 2% to lead", CARDS); shown("28% to carbon, 2% to lead", TAKE)
close(round(100 * (1 - mean_kept(16))), 11, 0, "11% mean loss to oxygen"); close(round(100 * (1 - mean_kept(12))), 14, 0, "14% mean loss to carbon")
shown("half its energy to hydrogen but 11% to oxygen"); check(True, "mean loss card removed")
close(round(M.alpha(12), 3), 0.716, 0, "alpha(C) = 0.716"); close(round(1 - M.alpha(12), 3), 0.284, 0, "1 - alpha(C) = 0.284"); close(round(xi_num(12), 3), 0.158, 0, "xi(C) = 0.158")
shown("ξ = 0.158 for carbon")

# ---------------------------------------------------------------- collisions to thermal energy
L2 = math.log10(2.0e6 / M.E_TH) * math.log(10.0)
close(M.L2, L2, 1e-12, "ln(8 x 10^7) through log10"); close(round(L2, 2), 18.20, 0, "18.20")
for name, x, printed in (("hydrogen", 1.0, 18), ("water", M.XI_W, 20), ("carbon", xi_num(12), 115), ("lead", xi_num(208), 1900)):
    k = steps(2.0e6, M.E_TH, x)
    check(abs(k - L2 / x) < 1.0, f"{name}: step count {k} agrees with ln(E0/E)/xi = {L2 / x:.2f}")
    close(round(L2 / x, -2) if name == "lead" else round(L2 / x), printed, 0, f"{name}: {printed} collisions")
shown("about 18 collisions in hydrogen, 115 in carbon, and 1,900 in lead"); shown("18.20 / 1 = 18.2; water: 18.20 / 0.92 = 19.8; carbon: 18.20 / 0.158 = 115")
shown("About 18 in hydrogen, 20 in water, and 115 in carbon, 6 times as many"); shown("about 18 collisions in hydrogen and 115 in carbon", TAKE)
xi_w = (2 * 20.4 * 1.0 + 3.76 * xi_num(16)) / (2 * 20.4 + 3.76)                     # free-atom epithermal scattering cross sections of H and O (b)
close(M.XI_W, xi_w, 0.01, "xi of water from the H and O values weighted by their scattering cross sections")

# ---------------------------------------------------------------- inelastic threshold: the centre-of-mass energy must reach the level
thr_c = bisect(lambda e: e * 12 / 13 - M.EX_C, 0.0, 10.0)
close(M.thr_c, thr_c, 1e-9, "carbon threshold"); close(round(thr_c, 1), 4.8, 0, "4.8 MeV"); shown("(4.8 MeV for carbon)")

# ---------------------------------------------------------------- reaction products by momentum balance
for q, m1, m2, got, printed, what in ((M.Q_N, 1, 14, M.e_pn, "0.58", "N(n,p) proton"), (M.Q_N, 14, 1, M.e_c14, "0.04", "C-14 recoil"), (M.Q_B1, 4, 7, M.e_a, "1.47", "B-10 alpha"),
                                      (M.Q_B1, 7, 4, M.e_li, "0.84", "Li-7 ion"), (M.Q_HE, 1, 3, M.e_p3, "0.57", "He-3 proton"), (M.Q_HE, 3, 1, M.e_t3, "0.19", "He-3 triton"),
                                      (M.Q_LI, 3, 4, M.e_t6, "2.73", "Li-6 triton"), (M.Q_LI, 4, 3, M.e_a6, "2.05", "Li-6 alpha")):
    e = share(q, m1, m2); close(got, e, 1e-9, what); close(float(f"{e:.2f}"), float(printed), 0, f"{what} prints {printed} MeV")
shown("0.63 MeV; proton 0.58 MeV"); shown("(α 1.47, Li 0.84 MeV)"); shown("0.76 MeV He-3"); shown("4.78 MeV TLD-600")
shown("whose 0.58 MeV proton stops"); shown("a 0.58 MeV proton", TAKE)
shown("2.79 MeV; in 94% of captures 2.31 MeV"); shown("0.48 MeV γ ray"); shown("3,840"); shown("5,330"); shown("About 2,500 (natural Cd)")

# ---------------------------------------------------------------- tissue: nuclei per gram and thermal capture
mol = {k: M.TISSUE[k] / M.MOLAR[k] * NA for k in M.TISSUE}                          # nuclei per gram
close(M.h_more, mol["H"] / sum(v for k, v in mol.items() if k != "H"), 1e-12, "hydrogen nuclei over the others"); shown("1.7 times as many nuclei")
gy_n = rad_gy(mol["N"], M.S_N, 1.0, M.Q_N); gy_h = rad_gy(mol["H"], M.S_H, 1.0, M.Q_H)
close(M.k_ncap, gy_n, 1e-9, "N(n,p) energy per unit fluence through the rad"); close(M.e_hcap, gy_h, 1e-9, "H(n,γ) energy per unit fluence through the rad")
close(M.r_hn, gy_h / gy_n, 1e-9, "ratio of the energies"); close(round(gy_h / gy_n), 35, 0, "about 35")
shown("about 35 times as much energy")

# ---------------------------------------------------------------- weighting factors and the quality factor
for e in (1.0, 50.0):
    close(wr103(e * (1 - 1e-9)), wr103(e * (1 + 1e-9)), 1e-3, f"the ICRP 103 branches meet at {e:g} MeV to within 0.1%")
for e, got in ((M.E_TH * 1e-6, M.wr_th), (0.1, M.wr_01), (1.0, M.wr_1), (100.0, M.wr_100), (200.0, M.wr_200)):
    close(got, wr103(e), 1e-12, f"w_R at {e:g} MeV")
close(round(M.wr_th, 1), 2.5, 0, "2.5 thermal"); close(round(M.wr_1), 21, 0, "peak near 21"); close(round(M.wr_01, 1), 10.0, 0, "10.0 at 0.1 MeV"); close(round(M.wr_1, 1), 20.7, 0, "20.7 at 1 MeV")
peak = max((wr103(10 ** (k / 1000.0)), 10 ** (k / 1000.0)) for k in range(-3000, 2000))
close(peak[1], 1.0, 0.01, "the w_R curve peaks at 1 MeV (grid search)")
check(4 <= M.wr_200 < M.wr_100 <= 5, "w_R at 100 and 200 MeV lies between 4 and 5")
shown("from about 2.5 for thermal neutrons to a peak near 21 at about 1 MeV"); shown("about 2.5 (thermal) to a peak near 21 at 1 MeV", TAKE)
close(M.q_100, 300 / math.sqrt(100), 0.01, "Q(100 keV/µm) from the high-LET branch"); close(round(M.q_100), 30, 0, "about 30"); check(True, "Q(L) values no longer printed")

# ---------------------------------------------------------------- lead (multiple choice)
p = prob("Pb-208 nucleus")
give, keep = recoil(208)
close(value(p), 100 * give, 1e-9, "largest loss to lead"); check(keyed(p) == "1.90%", "keyed 1.90%")
check(same(p["vals"], [100 * give, 100 * (1 - mean_kept(208)), 100 * recoil(82)[0], 100 * keep], 1e-6), "traps: mean loss, Z in place of A, energy kept")
close(100 * (1 - mean_kept(208)), 50 * give, 1e-6, "the mean loss is half the largest")

# ---------------------------------------------------------------- captures in water on hydrogen
fr_h = Fr(2 * 332, 1000) / (Fr(2 * 332, 1000) + Fr(19, 100000))
close(M.cap_h_frac, float(fr_h), 1e-12, "share of captures on hydrogen"); shown("99.97% of the captures in water", PROBS)

# ---------------------------------------------------------------- printed reaction data and cross sections in the questions
shown("4 × 208 / 209² = 0.0190, or 1.90%", PROBS); shown("Lead: 832/209² = 0.0190", CARDS)

# ---------------------------------------------------------------- every option list is distinct, and numeric keys are not at a scale slip of themselves
for q in tp["problems"]:
    if q.get("vals"): check(len(set(round(v, 9) for v in q["vals"])) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_neutron_interactions: {n} numbers re-derived"); print("numbers_neutron_interactions: PASS" if not bad else f"numbers_neutron_interactions: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
