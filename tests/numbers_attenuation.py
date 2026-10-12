"""Attenuation coefficients and mixtures: every worked number and keyed answer re-derived by another route.
Cross-sections per atom come from the linear coefficient over the number of atoms per cm³; the mixture rule is redone as a sum of
cross-sections per molecule and checked against the NIST table for water; electrons per gram are counted per mole with exact fractions,
and the compositions are checked against the mean Z/A that NIST publishes for them; effective atomic numbers are found by bisection;
the Klein–Nishina cross-section by numerical integration of the differential cross-section; the maximum Compton electron energy from
energy and momentum conservation solved by bisection; transmissions by counting half-value layers; and ratios with exact fractions."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard module
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import attenuation as M
import nistdata as nd
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T_ = {t["id"]: t for t in TOPICS}; bad = []; n = 0
assert "attenuation" in T_, "attenuation is not registered in src/topics/__init__.py"
TOP = T_["attenuation"]
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in TOP["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed(p): return [plain(p["opts"]["ABCDEFG".index(k)]) for k in p["key"]]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def block_text(b):
    if b[0] in ("h2", "p"): return plain(b[1])
    if b[0] in ("ul", "ol", "eq"): return " ".join(plain(x) for x in b[1])
    if b[0] == "ex": return " ".join(plain(x) for x in [b[1], b[2], b[4], *b[3]])
    if b[0] == "table": return " ".join(plain(c) for r in b[2] for c in r)
    return ""
GUIDE = " ".join(block_text(b) for b in TOP["guide"])
CARDS = " ".join(plain(x) for c in TOP["cards"] for x in [c["q"], *c["a"], *c["w"]])
TAKE = " ".join(plain(x) for sec in TOP["take"] for x in sec)
def shown(s, what, where=None):
    global n; n += 1
    if s not in (GUIDE if where is None else where): bad.append((what, "not found", s))

NA = 6.02214076e23
A = {"H": Fr("1.008"), "Li": Fr("6.94"), "C": Fr("12.011"), "N": Fr("14.007"), "O": Fr("15.999"), "F": Fr("18.998"), "Na": Fr("22.990"), "Mg": Fr("24.305"), "P": Fr("30.974"),
     "S": Fr("32.06"), "Cl": Fr("35.45"), "Ar": Fr("39.948"), "K": Fr("39.098"), "Ca": Fr("40.078"), "Pb": Fr("207.2")}
Z = {"H": 1, "Li": 3, "C": 6, "N": 7, "O": 8, "F": 9, "Na": 11, "Mg": 12, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20, "Pb": 82}
for e in A: close(float(A[e]), M.A[e], 1e-12, f"atomic weight of {e}"); check(Z[e] == M.Z[e], f"Z of {e}")
W, B, L = nd.WATER, nd.BONE, nd.LEAD

# ---- electrons per mole of mass: count electrons per formula unit or per mole of each element, with exact fractions
def e_per_mole_of_mass(fracs):                                                # electrons per gram divided by N_A, from mass fractions
    return sum(Fr(str(w)) * Z[e] / A[e] for e, w in fracs.items())
M_W = 2 * A["H"] + A["O"]
zoa_w = Fr(10) / M_W                                                          # 10 electrons per molecule of 18.015 g/mol
close(M.zoa(M.COMP["water"]), float(zoa_w), 1e-12, "Z/A of water from its formula")
close(M.EG["water"], NA * float(zoa_w), 1e-12, "electrons per gram of water")
for k in ("air", "adipose", "muscle", "bone"):
    close(sum(M.COMP[k].values()), 1.0, 1e-9, f"{k}: the mass fractions add to 1")
    close(M.EG[k], NA * float(e_per_mole_of_mass(M.COMP[k])), 1e-12, f"{k}: electrons per gram counted with exact fractions")
NIST_ZA = {"water": 0.55508, "air": 0.49919, "adipose": 0.55579, "bone": 0.51478}   # mean Z/A that NIST lists for these materials (an outside check on the compositions)
for k, v in NIST_ZA.items(): close(M.zoa(M.COMP[k]), v, 3e-5, f"{k}: Z/A agrees with the NIST value {v}")

# ---- effective atomic number by bisection: Z_eff^m equals the electron-weighted mean of Z^m
def zeff_bis(shares, m=2.94):
    target = sum(a * z ** m for z, a in shares); return bisect(lambda x: x ** m - target, 0.5, 100)
def shares_from_mass(fracs):
    tot = e_per_mole_of_mass(fracs); return [(Z[e], float(Fr(str(w)) * Z[e] / A[e] / tot)) for e, w in fracs.items()]
zw = zeff_bis([(1, 0.2), (8, 0.8)])
close(M.zw, zw, 1e-9, "Z_eff of water"); close(round(zw, 2), 7.42, 0, "printed 7.42"); close(M.ZE["water"], zw, 1e-9, "Z_eff of water from its mass fractions")
close(M.sum_w, 0.2 + 0.8 * 8 ** 2.94, 1e-12, "sum under the root"); shown(f"({0.2 + 0.8 * 8 ** 2.94:.1f})", "sum shown in the example")
for k in ("air", "adipose", "muscle", "bone"): close(M.ZE[k], zeff_bis(shares_from_mass(M.COMP[k])), 1e-9, f"Z_eff of {k} by bisection")
check(abs(M.ZE["muscle"] / zw - 1) < 0.01 and abs(M.EG["muscle"] / M.EG["water"] - 1) < 0.01, "muscle is within 1% of water in Z_eff and in electrons per gram")
check(round(M.ZE["bone"]) == 13 and 12 <= M.ZE["bone"] <= 14, "cortical bone: Z_eff about 13, inside the published 12 to 14")

# ---- the material table, cell by cell
rows = [r for b in TOP["guide"] if b[0] == "table" and "Material" in b[1] for r in b[2]]
check(len(rows) == 6, "six materials in the table")
want = {"Water": (1.00, "water"), "Air, dry": (0.001205, "air"), "Adipose tissue": (0.95, "adipose"), "Skeletal muscle": (1.05, "muscle"), "Cortical bone": (1.92, "bone"), "Lead": (11.35, "lead")}
for r in rows:
    rho, k = want[plain(r[0])]
    close(float(r[1]), rho, 0.05, f"{k}: density cell"); close(float(r[2]), NA * float(e_per_mole_of_mass(M.COMP[k])) / 1e23, 0.0051 / 3, f"{k}: electrons per gram cell")
    z = 82.0 if k == "lead" else zeff_bis(shares_from_mass(M.COMP[k])); close(float(r[3]), z, 0.051 / z if k != "lead" else 0, f"{k}: Z_eff cell")

# ---- worked example: water at 1.25 MeV, per molecule and per electron
mr = Fr(str(W[1.25][0]))
mol_per_g = NA / float(M_W)
s_mol = float(mr) / mol_per_g / 1e-24
close(M.s_mol, s_mol, 1e-12, "cross-section per molecule"); close(round(M.s_mol, 3), 1.892, 0, "1.892 b")
close(M.s_el, float(mr) / (NA * float(zoa_w)) / 1e-24, 1e-12, "cross-section per electron, from electrons per gram"); close(round(M.s_el, 3), 0.189, 0, "0.189 b")
shown("3.343 × 1022", "molecules per gram"); shown("1.892 × 10−24 cm² = 1.892 b", "per molecule in cm² and b"); shown("0.1892 b", "per electron")
# Klein–Nishina, by integrating dσ/dΩ over cos θ with Simpson's rule (the module uses the closed form)
RE, MEC2 = 2.8179403262e-13, 0.51099895
def kn_simpson(e, n=4000):
    a = e / MEC2; h = 2 / n; s = 0.0
    for i in range(n + 1):
        c = -1 + i * h; P = 1 / (1 + a * (1 - c)); f = math.pi * RE ** 2 * P ** 2 * (P + 1 / P - (1 - c * c))
        s += f * (1 if i in (0, n) else (4 if i % 2 else 2))
    return s * h / 3
kn125 = kn_simpson(1.25) / 1e-24
close(M.kn125, kn125, 1e-9, "Klein–Nishina at 1.25 MeV by Simpson's rule"); shown(f"{kn125:.4f} b", "Klein–Nishina value printed")
check(abs(M.s_el / kn125 - 1) < 0.005, "water per electron at 1.25 MeV is within 0.5% of the Klein–Nishina value (nearly all Compton)")
shown(f"{M.s_el:.3f} b", "per-electron value on the card", CARDS); shown(f"{kn125:.3f} b", "Klein–Nishina value in the take away", TAKE)

# ---- worked example: water from hydrogen and oxygen, redone as cross-sections per molecule
H, O = M.EL125["H"], M.EL125["O"]
sig_mol = lambda i: (2 * H[i] * float(A["H"]) + O[i] * float(A["O"])) / NA          # cm² per molecule
mu_mol, en_mol = sig_mol(0) * NA / float(M_W), sig_mol(1) * NA / float(M_W)
close(M.mu_mix, mu_mol, 1e-12, "μ/ρ of water from cross-sections per molecule"); close(M.en_mix, en_mol, 1e-12, "μen/ρ of water from cross-sections per molecule")
close(mu_mol, W[1.25][0], 5e-4, "the mixture value agrees with the NIST water table (μ/ρ)"); close(en_mol, W[1.25][1], 5e-4, "and with μen/ρ")
shown(f"{mu_mol:.5f} and {en_mol:.5f} cm²/g", "mixture answers"); shown(f"{float(2 * A['H'] / M_W):.4f}", "w_H"); shown(f"{float(A['O'] / M_W):.4f}", "w_O")
close(M.share_H, 2 * H[0] * float(A["H"]) / (sig_mol(0) * NA), 1e-12, "hydrogen's share of μ/ρ"); check(round(100 * M.share_H) == 20 and round(100 * M.wH) == 11, "20% of μ/ρ from 11% of the mass")
check(abs(M.share_H - 0.2) < 0.005, "hydrogen's share of μ/ρ equals its share of the electrons, 2 of 10 (Compton region)")
check(abs((H[0] / float(Fr(1) / A["H"])) / (O[0] / float(Fr(8) / A["O"])) - 1) < 0.01, "per electron, hydrogen and oxygen attenuate alike at 1.25 MeV")
# electrons per gram of water and its Z_eff, as printed
shown("3.343 × 1023 g−1", "electrons per gram in the steps"); shown("3.34 × 1023 electrons per gram and Zeff = 7.42", "example answer")

# ---- energy transfer and absorption: fractions absorbed per interaction, from exact fractions of the table
fa = lambda e: Fr(str(W[e][1])) / Fr(str(W[e][0]))
shown(f"{float(fa(0.01)):.2f} at 10 keV", "0.93 at 10 keV"); shown(f"{float(min(fa(0.06), fa(0.08), fa(0.1))):.2f} to {float(max(fa(0.06), fa(0.08), fa(0.1))):.2f} between 60 and 100 keV", "60 to 100 keV range")
shown(f"{float(fa(1.25)):.2f} at 1.25 MeV and {float(fa(10.0)):.2f} at 10 MeV", "1.25 and 10 MeV values")
check(float(fa(0.08)) == min(float(fa(e)) for e in W), "the lowest fraction absorbed in water lies in the 60 to 100 keV band (at 80 keV)")
# the largest Compton electron energy from a 100 keV photon, from energy and momentum conservation (backscatter)
def tmax(e):                                                                   # E' found so that the electron's kinetic energy matches its momentum (E + E')
    mc2 = 0.511                                                                # the value used by the module's Compton formula
    return e - bisect(lambda ep: (math.sqrt((e + ep) ** 2 + mc2 ** 2) - mc2) - (e - ep), 1e-9, e)
close(M.tmax100, 1000 * tmax(0.1), 1e-7, "largest Compton electron energy at 100 keV"); shown(f"at most {1000 * tmax(0.1):.0f} keV", "28 keV in the text")
p = prob("A 100 keV photon interacts in water")
close(value(p), 100 * float(fa(0.1)), 1e-12, "typed: energy absorbed per interaction"); close(round(value(p), 1), 14.9, 0, "14.9 keV")
check(abs(100 / value(p) - 1) > p["tol"] and abs(1000 * tmax(0.1) / value(p) - 1) > p["tol"], "100 keV and the largest Compton electron energy fall outside the tolerance")
def kn_tr_fraction(e, n=4000):                                                 # mean fraction of hν given to the Compton electron (Simpson in cos θ)
    a = e / MEC2; h = 2 / n; s = st = 0.0
    for i in range(n + 1):
        c = -1 + i * h; P = 1 / (1 + a * (1 - c)); f = P ** 2 * (P + 1 / P - (1 - c * c)); wgt = 1 if i in (0, n) else (4 if i % 2 else 2)
        s += f * wgt; st += (1 - P) * f * wgt
    return st / s
check(kn_tr_fraction(0.1) < float(fa(0.1)) < 0.2, "at 100 keV the fraction absorbed (0.149) exceeds the Compton transfer alone (about 0.14): a little photoelectric absorption")
shown(f"about {100 * float(fa(0.1)):.0f} keV for a 100 keV photon and {1250 * float(fa(1.25)):.0f} keV", "card: energy absorbed per interaction", CARDS)

# ---- lead: the minimum of μ/ρ and both ends of the spectrum
es = sorted(e for e in L if e >= 0.5); vals = [L[e][0] for e in es]
k = vals.index(min(vals)); check((es[k - 1], es[k], es[k + 1]) == (3.0, 4.0, 5.0), "lead's tabulated μ/ρ is lowest at 4 MeV, between 3 and 5 MeV")
check(all(x > y for x, y in zip(vals[:k], vals[1:k + 1])) and all(x < y for x, y in zip(vals[k:], vals[k + 1:])), "lead's μ/ρ falls to the minimum and rises after it")
check(all(W[a][0] > W[b][0] for a, b in zip(sorted(W), sorted(W)[1:])), "water's μ/ρ falls with energy across the whole table, so water only hardens")
shown("between 3 and 5 MeV", "lead minimum in the text"); p = prob("A thick lead absorber"); check(keyed(p)[0].endswith("3 to 5 MeV"), "keyed option names 3 to 5 MeV")
close(M.PB_AZ, float(A["Pb"] / 82), 1e-12, "A/Z of lead"); shown("2.5Z for lead", "A/Z of lead in the text")

# ---- lead at 1.25 MeV: cross-section per atom from μ over the number of atoms per cm³
p = prob("Lead in a Co-60 beam")
mu_pb = L[1.25][0] * 11.35; atoms_cm3 = 11.35 * NA / float(A["Pb"])
close(value(p), mu_pb / atoms_cm3 / 1e-24, 1e-12, "atomic cross-section of lead"); close(round(value(p), 1), 20.2, 0, "20.2 b")
v = sorted(p["vals"]); close(v[0], value(p) / 82, 1e-12, "trap: per electron"); close(v[1], L[1.25][0] * 82 / NA / 1e-24, 1e-12, "trap: Z in place of A"); close(v[3], value(p) * 11.35, 1e-12, "trap: density left in")
share_c = (11.35 * NA * 82 / float(A["Pb"])) * kn125 * 1e-24 / mu_pb            # electrons per cm³ × σ_KN / μ
close(M.p_kn, share_c, 1e-6, "Compton share of lead's attenuation at 1.25 MeV"); check(f"about {100 * (1 - share_c):.0f}%" in plain(p["a"][1]), "explanation: about 23% from other processes")

# ---- beam hardening: the share of 60 keV photons, written as a logistic function of the difference in μ
p = prob("equal numbers of 30 keV and 60 keV photons")
share = 100 / (1 + math.exp((W[0.06][0] - W[0.03][0]) * 5.0))
close(value(p), share, 1e-9, "60 keV share after 5.0 cm of water"); close(round(value(p), 1), 70.0, 0, "70.0%")
v = sorted(p["vals"]); check([round(x, 1) for x in v] == [30.0, round(100 * math.exp(-W[0.06][0] * 5), 1), 50.0, 70.0], "options: 30.0 (30 keV share), 35.7 (60 keV transmission), 50.0, 70.0")

# ---- two layers, by counting half-value layers of each
p = prob("crosses 3.0 cm of cortical bone and 12.0 cm of soft tissue")
hvl_b, hvl_w = math.log(2) / (B[1.25][0] * 1.92), math.log(2) / (W[1.25][0] * 1.00)
t = 100 * 2 ** -(3.0 / hvl_b + 12.0 / hvl_w)
close(value(p), t, 1e-9, "transmission through bone and water"); close(round(value(p), 1), 33.4, 0, "33.4%")
check(abs(100 * 2 ** -(15.0 / hvl_w) / value(p) - 1) > p["tol"] and abs(100 * math.exp(-(B[1.25][0] * 3 + W[1.25][0] * 12)) / value(p) - 1) > p["tol"], "bone as water, and bone without its density, fall outside the tolerance")
close(100 * 2 ** -(12.0 / hvl_w + 3.0 / hvl_b), t, 1e-12, "the order of the layers does not change a narrow-beam transmission")
check(round(100 * (1 - B[1.25][0] / W[1.25][0])) == 7 and round(100 * (B[1.25][0] * 1.92 / W[1.25][0] - 1)) == 78, "per gram 7% less, per cm 78% more")

# ---- electrons per gram, ranked (exact fractions per mole)
p = prob("Five materials are compared"); pe = (Fr(6) + 2) / (A["C"] + 2 * A["H"])
order = [("Lead", Fr(82) / A["Pb"]), ("Oxygen", Fr(8) / A["O"]), ("Water", zoa_w), ("Polyethylene", pe), ("Hydrogen", Fr(1) / A["H"])]
check(all(a[1] < b[1] for a, b in zip(order, order[1:])), "lead < oxygen < water < polyethylene < hydrogen")
check([plain(c["t"]).split(",")[0] for c in sorted(p["chips"], key=lambda c: c["b"])] == [x for x, _ in order], "the ranking key follows the exact values")
for name, v in order: check(f"{name.lower()} {NA * float(v) / 1e23:.2f}" in plain(p["a"][1]), f"explanation gives {name.lower()}")

# ---- LiF effective atomic number by bisection, and its distractors
p = prob("Lithium fluoride")
z_lif = zeff_bis([(3, 0.25), (9, 0.75)]); close(value(p), z_lif, 1e-9, "Z_eff of LiF"); close(round(value(p), 2), 8.20, 0, "8.20")
wl = float(A["Li"] / (A["Li"] + A["F"]))
v = sorted(p["vals"]); close(v[0], zeff_bis([(3, 0.5), (9, 0.5)]), 1e-9, "trap: atom fractions"); close(v[1], 0.25 * 3 + 0.75 * 9, 1e-12, "trap: m = 1"); close(v[2], zeff_bis([(3, wl), (9, 1 - wl)]), 1e-9, "trap: mass fractions")
check(len({f"{x:.2f}" for x in v}) == 4, "four distinct options at two decimals")

# ---- spongy bone mixture at 30 keV, exact fractions
p = prob("Spongy bone is modelled")
mix = Fr(2, 5) * Fr(str(B[0.03][1])) + Fr(3, 5) * Fr(str(W[0.03][1]))
close(value(p), float(mix), 1e-12, "mixture μen/ρ"); close(round(value(p), 3), 0.521, 0, "0.521 cm²/g")
v = sorted(p["vals"]); close(v[1], float((Fr(str(B[0.03][1])) + Fr(str(W[0.03][1]))) / 2), 1e-12, "trap: plain mean"); close(v[2], float(Fr(3, 5) * Fr(str(B[0.03][1])) + Fr(2, 5) * Fr(str(W[0.03][1]))), 1e-12, "trap: fractions swapped")
close(v[3], float(Fr(2, 5) * Fr(str(B[0.03][0])) + Fr(3, 5) * Fr(str(W[0.03][0]))), 1e-12, "trap: attenuation columns")

# ---- relative electron density of cortical bone: electrons per cm³ of each, then the ratio
p = prob("relative electron density of cortical bone")
ecm_b, ecm_w = 1.92 * NA * 0.5148, 1.00 * NA * 0.5551
close(value(p), ecm_b / ecm_w, 1e-12, "relative electron density"); close(round(value(p), 2), 1.78, 0, "1.78")
close(M.ZA_B, round(float(e_per_mole_of_mass(M.COMP["bone"])), 4), 0, "printed Z/A of bone is the composition value"); close(M.ZA_W, round(float(zoa_w), 4), 0, "printed Z/A of water")
check(abs(value(p) / (B[1.25][0] * 1.92 / W[1.25][0]) - 1) < 0.005, "in the Compton region μ of bone over μ of water matches the relative electron density")

# ---- bone and water: dose ratios, exact fractions of the table
r = lambda e: Fr(str(B[e][1])) / Fr(str(W[e][1]))
close(M.q30, float(r(0.03)), 1e-12, "ratio at 30 keV"); close(M.q125, float(r(1.25)), 1e-12, "ratio at 1.25 MeV")
shown(f"{2 * float(r(0.03)):.1f} Gy at 30 keV and {2 * float(r(1.25)):.2f} Gy at 1.25 MeV", "bone-dose example answer")
ratio_e = float(e_per_mole_of_mass(M.COMP["bone"]) / zoa_w); close(M.re_bw, ratio_e, 1e-12, "ratio of electrons per gram, bone to water")
mv = [float(r(e)) for e in (0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0)]
check(all(abs(x / ratio_e - 1) < 0.005 for x in mv), "from 0.5 to 2 MeV every ratio is within 0.5% of the electron ratio")
shown(f"{min(mv):.3f} to {max(mv):.3f}, close to the ratio of electrons per gram, {ratio_e:.3f}", "0.5 to 2 MeV range in the text")
for row in [rr for b in TOP["guide"] if b[0] == "table" and "Photon energy" in b[1] for rr in b[2]]:
    e = float(plain(row[0]).split()[0]) / (1000 if "keV" in row[0] else 1); x = float(r(e))
    close(float(row[1]), x, (0.005 if x > 1.5 else 0.0005) / x, f"table ratio at {plain(row[0])}")
cross = bisect(lambda lnE: (math.log(float(r(6.0))) + (lnE - math.log(6.0)) * (math.log(float(r(8.0))) - math.log(float(r(6.0)))) / (math.log(8.0) - math.log(6.0))), math.log(6.0), math.log(8.0))
close(M.E_CROSS, math.exp(cross), 1e-9, "the ratio crosses 1 between 6 and 8 MeV (log-log interpolation)"); shown("Above about 7 MeV", "crossing in the text")
check(all(float(r(e)) > 1 for e in (10.0, 15.0, 20.0)) and float(r(6.0)) < 1, "above 10 MeV bone absorbs more than water; at 6 MeV less")
shown(f"about {float(r(0.1)):.0f} to {float(r(0.03)):.0f} times", "kilovoltage range 2 to 7 in the text")
check(all(abs(float(r(a)) / float(r(b)) - 1) > 0.3 for a, b in ((0.06, 0.1), (0.1, 0.15))) and abs(float(r(0.15)) / float(r(0.2)) - 1) < 0.15, "the ratio changes steeply below about 150 keV")
shown(f"{100 * (1 - ratio_e):.0f}% fewer electrons per gram", "bone has 7% fewer electrons per gram"); shown(f"{100 * (1 - float(e_per_mole_of_mass(M.COMP['air']) / zoa_w)):.0f}% fewer", "air 10% fewer")
p = prob("A piece of cortical bone")
close(value(p), float(3 * r(0.08)), 1e-12, "bone dose at 80 keV"); close(round(value(p), 2), 7.97, 0, "7.97 Gy")
v = sorted(p["vals"]); close(v[0], float(3 / r(0.08)), 1e-12, "trap: ratio inverted"); close(v[1], 3 * B[0.08][0] / W[0.08][0], 1e-12, "trap: attenuation columns"); close(v[3], float(3 * r(0.08)) * 1.92, 1e-12, "trap: density ratio")
p = prob("Cortical bone and water receive the same photon energy fluence")
ok = {f"At 30 keV bone absorbs about {round(float(r(0.03)))} times as much as water": 6.5 < float(r(0.03)) < 7.5,
      f"From 0.5 to 2 MeV bone absorbs about {100 * (1 - ratio_e):.0f}% less than water": all(0.065 < 1 - x < 0.075 for x in mv),
      "Above about 10 MeV bone absorbs more than water": all(float(r(e)) > 1 for e in (10.0, 15.0, 20.0))}
check(sorted(keyed(p)) == sorted(ok) and all(ok.values()), "the three keyed statements are the true ones")
check(not (1.8 < float(r(1.25)) < 2.0) and not (0.9 < float(r(0.06)) < 0.96) and not (6.5 < float(r(0.2)) < 7.5), "the three wrong statements are false")

# ---- the rest of the stated numbers
check(f"{float(Fr(1) / A['H']):.2f}" == "0.99" and all(f"{float(Fr(Z[e]) / A[e]):.2f}" == "0.50" for e in ("C", "N", "O", "Ca")) and f"{float(Fr(82) / A['Pb']):.2f}" == "0.40", "Z/A: 0.99, 0.50 for C, N, O, Ca, and 0.40")
shown("0.99 for hydrogen, 0.50 for carbon, nitrogen, oxygen, and calcium, and 0.40 for lead", "Z/A in the text")
check(M.EG["adipose"] / M.EG["water"] - 1 < 0.005 and M.ZE["adipose"] < M.ZE["water"] - 1, "fat: about the same electrons per gram as water, Z_eff lower by more than 1")
for q in TOP["problems"]:
    if q.get("vals"): check(len(set(round(x, 6) for x in q["vals"])) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_attenuation: {n} numbers re-derived"); print("numbers_attenuation: PASS" if not bad else f"numbers_attenuation: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
