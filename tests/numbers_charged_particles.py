"""Charged-particle interactions and stopping power: every worked number and keyed answer re-derived by another route
(SI units, exact fractions, numerical integration of the Møller cross section and of the radiative share, a slowing-down march,
bisection, and the relativistic kinematics of a head-on collision solved numerically)."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard module
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import charged_particles as G
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def true(c, what):
    global n; n += 1
    if not c: bad.append((what, False, True))
def prob(phrase):
    hits = [p for p in T["charged-particles"]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed_text(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def bisect(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2; fm = f(m)
        if (fm > 0) == (fa > 0): a, fa = m, fm
        else: b = m
    return (a + b) / 2
def simpson(f, a, b, k=4000):
    h = (b - a) / k
    return h / 3 * sum((1 if i in (0, k) else 4 if i % 2 else 2) * f(a + i * h) for i in range(k + 1))
GUIDE = " ".join(plain(x) for b in T["charged-particles"]["guide"] for x in ([b[1]] if b[0] in ("p", "h2") else b[1] if b[0] in ("ul", "ol", "eq") else
                 [b[2], b[4], *b[3]] if b[0] == "ex" else [c for r in b[2] for c in r] if b[0] == "table" else []))
def shown(s, what): true(s in GUIDE, f"printed in the chapter: {what} ({s!r})")

# ---- physical constants, written out again
RE, MEC2, NA = 2.8179403262e-13, 0.51099895, 6.02214076e23       # cm, MeV, 1/mol
K = 2 * math.pi * RE ** 2 * MEC2 * NA
close(G.K_E, K, 1e-5, "2π r_e² m c² N_A = 0.153537 MeV cm²/mol from r_e, m c², and N_A")
close(G.ZA_WATER, 10 / (2 * 1.008 + 15.999), 1e-3, "Z/A of water from the atomic masses of H and O")
MEV_J = 1.602176634e-13

# ---- worked example: energy lost in tissue and in lung, in SI units
def loss_si(s_mev_cm2_g, rho_g_cm3, t_cm):
    s_si = s_mev_cm2_g * MEV_J * 1e-4 / 1e-3                       # J m²/kg
    return s_si * (rho_g_cm3 * 1000) * (t_cm / 100) / MEV_J         # MeV
close(G.de_t1, loss_si(2.0, 1.04, 0.80), 1e-12, "tissue: (S/ρ) ρ t in SI units"); close(round(G.de_t1, 2), 1.66, 0, "printed 1.66 MeV")
close(G.de_l1, loss_si(2.0, 0.25, 0.80), 1e-12, "lung: (S/ρ) ρ t in SI units"); close(round(G.de_l1, 2), 0.40, 0, "printed 0.40 MeV")
close(G.de_t1 / G.de_l1, 1.04 / 0.25, 1e-12, "the two losses stand in the ratio of the densities"); shown("about 4 times farther", "lung against tissue")
shown("0.832 g/cm²", "mass thickness of the tissue layer")

# ---- worked example: radiative share and critical energy, as exact fractions and by bisection
r_w, r_t = Fr(74, 10) * 10 / 800, Fr(74) * 10 / 800
close(G.r_w10, float(r_w), 1e-12, "water: Z T / 800"); close(G.r_t10, float(r_t), 1e-12, "tungsten: Z T / 800")
close(G.s_w10, float(1 - 1 / (1 + r_w)), 1e-12, "water: S_rad/S_tot = 1 − 1/(1 + r)"); close(G.s_t10, float(1 - 1 / (1 + r_t)), 1e-12, "tungsten: S_rad/S_tot = 1 − 1/(1 + r)")
close(G.ec_t, bisect(lambda e: 74 * e / 800 - 1, 1, 100), 1e-9, "tungsten: energy where the rule gives equal losses, by bisection")
close(G.ec_pb, bisect(lambda e: 82 * e / 800 - 1, 1, 100), 1e-9, "lead: E_c by bisection"); close(G.ec_w, bisect(lambda e: 7.4 * e / 800 - 1, 1, 1000), 1e-9, "water: E_c by bisection")
true(9.5 < G.ec_pb < 10.5 and 9.5 < G.ec_t < 11 and 90 < G.ec_w < 120, "the text's 'about 10 MeV for lead and tungsten, of the order of 100 MeV for water'")
shown("8.5% in water and 48% in tungsten", "the radiative shares"); shown("about 11 MeV", "tungsten's critical energy, rounded"); shown("= 10.8 MeV", "tungsten's critical energy")
true(G.s_w10 < 0.10, "the table's 'under 10% of the total up to 10 MeV' in water")

# ---- radiation yield: the share integrated numerically over the slowing-down
def yield_num(z, t0): return simpson(lambda t: (z * t / 800) / (1 + z * t / 800), 0, t0) / t0
close(G.y_w10, yield_num(7.4, 10), 1e-9, "Y at 10 MeV in water: (1/T0) ∫ S_rad/S_tot dT by Simpson's rule"); close(G.y_w1, yield_num(7.4, 1), 1e-9, "Y at 1 MeV")
true(G.y_w10 < G.s_w10, "the yield lies below the starting share"); true(G.y_w1 < 0.01, "under 1% at 1 MeV")
shown("it is below the radiative share at the start", "yield against share")

# ---- restricted collision stopping power: the Møller cross section integrated numerically (in ln ε, from Δ/T to 1/2)
def hard_num(t, delta, za=10 / 18.015):
    tau = t / MEC2; g = tau + 1; b2 = 1 - 1 / g ** 2; c, d = (tau / g) ** 2, (2 * tau + 1) / g ** 2
    integrand = lambda u: (lambda e: 1 + e * e / (1 - e) ** 2 + c * e * e - d * e / (1 - e))(math.exp(u))     # ε² dσ/dε × β² T / (2π r_e² m c²), integrated in u = ln ε
    return K * za / b2 * simpson(integrand, math.log(delta / t), math.log(0.5), 6000)
close(G.hard_loss(10, 0.010), hard_num(10, 0.010), 1e-5, "loss to delta rays above 10 keV at 10 MeV: closed form against the numerical integral")
close(G.hard_loss(10, 0.100), hard_num(10, 0.100), 1e-5, "loss to delta rays above 100 keV at 10 MeV")
close(G.hard_loss(1, 0.010), hard_num(1, 0.010), 1e-5, "loss to delta rays above 10 keV at 1 MeV")
close(G.hard_loss(10, 5.0), 0.0, 1e-12, "no loss is left above Δ = T/2")
close(G.h10, 0.56, 0, "printed 0.56 MeV cm²/g"); close(round(hard_num(10, 0.010), 2), G.h10, 0, "the integral also rounds to 0.56")
true(G.hard_loss(1, 0.01) < G.hard_loss(10, 0.01) < G.hard_loss(20, 0.01), "the gap between S_col and L_Δ grows with energy")
close(G.l10, float(Fr(197, 100) - Fr(56, 100)), 1e-12, "L_10keV/ρ = 1.97 − 0.56 = 1.41")
KEV_UM_PER_MEV_CM = float(Fr(1000, 10 ** 4))                                    # 1 MeV/cm = 1000 keV per 10^4 µm
close(G.let10, G.l10 * KEV_UM_PER_MEV_CM, 1e-12, "LET_10keV in keV/µm"); close(G.letinf, 1.97 * KEV_UM_PER_MEV_CM, 1e-12, "unrestricted LET in keV/µm")
close(round(100 * G.fr10), 28, 0, "28% carried by delta rays above 10 keV"); shown("0.14 keV/µm against 0.20 keV/µm", "LET values of the example")

# ---- largest energy given to an electron: head-on collision solved from energy and momentum conservation
def wmax_kin(t, m_heavy, m=MEC2):
    e1, p1 = t + m_heavy, math.sqrt(t * t + 2 * t * m_heavy)
    pe = lambda w: math.sqrt(w * w + 2 * w * m)
    return bisect(lambda w: (e1 - w) ** 2 - (p1 - pe(w)) ** 2 - m_heavy ** 2, 1e-9, t)
close(G.w100, wmax_kin(100, G.MP), 1e-7, "W_max of a 100 MeV proton from the kinematics of a head-on collision"); close(round(G.w100, 2), 0.23, 0, "printed 0.23 MeV")

# ---- heavy particles: range at the same speed, integrated for an α particle and a proton with S = z² f(v)
def range_same_speed(m_heavy, z, beta0, beta_end=0.05, k=4000):
    f = lambda b2: (math.log(2 * MEC2 * b2 / (1 - b2) / 75e-6) - b2) / b2        # Bethe form without corrections; the same for both particles
    t_of = lambda b: m_heavy * (1 / math.sqrt(1 - b * b) - 1)
    return simpson(lambda b: (m_heavy * b / (1 - b * b) ** 1.5) / (z * z * f(b * b)), beta_end, beta0, k)     # ∫ dT / S with dT = M γ³ β dβ
ratio_num = range_same_speed(G.MALPHA, 2, 0.30) / range_same_speed(G.MP, 1, 0.30)
close(G.r_ap, ratio_num, 1e-9, "α/proton range at the same speed from the integral"); close(round(G.r_ap, 3), 0.993, 0, "printed 0.993")
def bethe_full(t, m_heavy, z):
    g = 1 + t / m_heavy; b2 = 1 - 1 / g ** 2; wm = G.w_max(t, m_heavy)
    return z * z / b2 * (0.5 * math.log(2 * MEC2 * b2 * g * g * wm / (75e-6) ** 2) - b2)
t_alpha = 20.0; t_p = t_alpha * G.MP / G.MALPHA                                     # the same speed
close(bethe_full(t_alpha, G.MALPHA, 2) / bethe_full(t_p, G.MP, 1), 4.0, 2e-3, "stopping power ratio at one speed is z² = 4 (full Bethe expression, mass-dependent W_max included)")
p = prob("enter water with the same speed"); true(keyed_text(p) == "4 times the stopping power, about the same range", "keyed: 4 times, about the same range")

# ---- energy lost in a bone slab
p = prob("slab of cortical bone")
close(value(p), loss_si(1.9, 1.92, 0.60), 1e-12, "bone: (S/ρ) ρ t in SI units"); close(round(value(p), 2), 2.19, 0, "2.19 MeV")
close(G.q_bone_nr, 1.9 * 0.60, 1e-12, "trap: density left out"); close(G.q_bone_div, 1.9 * 0.60 / 1.92, 1e-12, "trap: divided by the density"); close(G.q_bone_cm, 1.9 * 1.92, 1e-12, "trap: thickness left out")

# ---- radiative share at 20 MeV in water
p = prob("A 20 MeV electron slows down in water")
close(value(p), float(100 * (1 - 1 / (1 + Fr(74, 10) * 20 / 800))), 1e-9, "share 15.6% as an exact fraction"); close(round(value(p), 1), 15.6, 0, "15.6%")
close(G.q_share_r, 18.5, 1e-12, "trap: the ratio itself"); close(G.q_share_col, 100 - value(p), 1e-12, "trap: the collision share")
close(G.q_share_z2, float(100 * (1 - 1 / (1 + Fr(74, 10) ** 2 * 20 / 800))), 1e-9, "trap: Z² in place of Z")

# ---- yield against share, and the β shield
p = prob("Y-90, a pure β emitter"); close(G.pb_acryl, 82 / 6.5, 1e-12, "lead against acrylic by the rule"); true(G.pb_acryl > 10 and "about 13 times" in plain(p["a"][1]), "about 13 times, more than ten")

# ---- LET of a 1 MeV electron
p = prob("A 1 MeV electron slows down in water"); close(value(p), 1.85 * KEV_UM_PER_MEV_CM, 1e-12, "0.185 keV/µm")
true(len(p["vals"]) == 4 and min(p["vals"]) > 0, "four positive options")

# ---- distinct options
for q in T["charged-particles"]["problems"]:
    if q.get("vals"): true(len(set(round(v, 6) for v in q["vals"])) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_charged_particles: {n} numbers re-derived"); print("numbers_charged_particles: PASS" if not bad else f"numbers_charged_particles: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
