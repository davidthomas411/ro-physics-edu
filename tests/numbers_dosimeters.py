"""Diodes, luminescent dosimeters, and film: every number the chapter prints or keys, re-derived by another route
(counting charge pairs and ions, solving the calibration equations by bisection, natural logarithms for the optical density,
the Faraday constant for the G value, and a photoelectric scaling model for the low-energy over-response)."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import dosimeters as M
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def prob(tid, phrase):
    hits = [p for p in T[tid]["problems"] if phrase in plain(p["q"])]; assert len(hits) == 1, (tid, phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def has(p, v, tol=1e-9):                                                       # a value is among the options of a numeric choice
    return any(abs(x - v) <= tol * abs(v) for x in p["vals"])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
E, NA, F = 1.602176634e-19, 6.02214076e23, 96485.33212                        # C, 1/mol, C/mol
TID = "dosimeters"; G = T[TID]
txt = " ".join(plain(b[1]) for b in G["guide"] if b[0] == "p")

# ---- diode sensitivity: count the charge pairs freed by 1 Gy in 1 cm³ of silicon and of air
def charge_1cc(rho_g_cm3, w_ev):
    energy = rho_g_cm3 / 1000 * 1.0                                            # J deposited in 1 cm³ (kg) by 1 Gy
    return energy / (w_ev * E) * E                                             # pairs times the charge of each
ratio = charge_1cc(2.33, 3.6) / charge_1cc(0.001205, 33.97)
close(M.sens, ratio, 1e-12, "charge per unit volume, silicon over air"); close(ratio, 18246, 1e-4, "about 18,000")
close(M.sens_r, 18000, 0, "the text rounds it to 18,000"); close(M.dens_r, 1900, 0, "and the density ratio to 1,900")
close(2.33 / 0.001205, 1933.6, 1e-4, "density ratio"); close(33.97 / 3.6, 9.436, 1e-3, "energy per pair, air over silicon")
close(1 if f"{M.sens_r:,}" in txt and f"{M.dens_r:,}" in txt else 0, 1, 0, "both rounded ratios appear in the text")
p = prob(TID, "how many times more charge per unit volume")
close(value(p), ratio, 1e-9, "keyed value"); close(1 if has(p, 33.97 / 3.6) and has(p, 2.33 / 0.001205) and has(p, (2.33 / 0.001205) / (33.97 / 3.6)) else 0, 1, 0, "distractors: each ratio alone, and one ratio inverted")
close(1 if p["opts"] == sorted(p["opts"], key=lambda o: float(o.split()[0].replace(",", ""))) else 0, 1, 0, "numeric options ascend")

# ---- in vivo diode: solve for the dose that makes a warm diode give the reading
def true_dose(r, n_cal, cfs, alpha, dt):
    gain = 1 + alpha * dt                                                      # the warm diode reads high by this factor
    return bisect(lambda d: d * gain / (n_cal * math.prod(cfs)) - r, 0, 1000)
d_ex = true_dose(184.0, 1.065, [0.993, 1.024], 0.0030, 9)
close(M.ex_d, d_ex, 1e-9, "worked example: entrance dose"); close(round(d_ex, 1), 194.0, 1e-12, "194.0 cGy")
close(M.ex_cft, 1 / 1.027, 1e-12, "CF_T for 9 °C at 0.30% per °C"); close(M.ex_diff, 100 * (d_ex / 198.0 - 1), 1e-9, "difference from the plan"); close(round(M.ex_diff, 1), -2.0, 1e-12, "−2.0%")
d_q = true_dose(191.5, 1.048, [0.991], 0.0040, 8)
p = prob(TID, "skin warms it to 31 °C")
close(value(p), d_q, 1e-9, "typed in vivo dose"); close(round(d_q, 1), 192.7, 1e-12, "192.7 cGy")
close(M.q_iv_mult, 191.5 * 1.048 * 0.991 * 1.032, 1e-12, "the multiplied decoy"); close(M.q_iv_none, 191.5 * 1.048 * 0.991, 1e-12, "the uncorrected decoy")
close(1 if abs(M.q_iv_mult / d_q - 1) > p["tol"] and abs(M.q_iv_none / d_q - 1) > p["tol"] else 0, 1, 0, "both decoys fall outside the typed tolerance")

# ---- TLD: the chip's own sensitivity, from the calibration chips and its ECF
def tld(m, ecf, d_cal, m_cal):
    s_chip = (m_cal / d_cal) / ecf                                             # nC per Gy for this chip
    return m / s_chip
close(M.tl_d, tld(26.4, 1.037, 1.00, 25.1), 1e-12, "worked example: TLD dose"); close(round(M.tl_d, 2), 1.09, 1e-12, "1.09 Gy")
p = prob(TID, "What dose did the chip receive")
close(value(p), tld(18.6, 0.955, 2.00, 42.0), 1e-12, "keyed TLD dose"); close(round(value(p), 3), 0.846, 1e-12, "0.846 Gy")
close(1 if has(p, tld(18.6, 1 / 0.955, 2.00, 42.0)) and has(p, tld(18.6, 1.0, 2.00, 42.0)) else 0, 1, 0, "decoys: the ECF divided, and the ECF left out")
ecf = bisect(lambda x: 19.2 * x - 20.0, 0.5, 2.0)                              # the factor that brings the chip to the batch mean
p = prob(TID, "element correction factor of that chip")
close(value(p), ecf, 1e-9, "ECF"); close(round(ecf, 3), 1.042, 1e-12, "1.042"); close(1 if has(p, 19.2 / 20.0) else 0, 1, 0, "the inverted ratio is a decoy")

# ---- optical density by natural logarithms, and transmission by bisection
od = lambda i0, i: math.log(i0 / i) / math.log(10)
close(M.od_u, od(1000, 800), 1e-12, "OD of unexposed film"); close(M.od_e, od(1000, 160), 1e-12, "OD of exposed film")
close(M.od_net, od(800, 160), 1e-12, "net OD equals log(I_unexposed / I_exposed)"); close(round(M.od_net, 3), 0.699, 1e-12, "0.699")
close(10 ** -M.od_e, 0.16, 1e-12, "the irradiated part transmits 16%")
t13 = bisect(lambda t: od(1, t) - 1.3, 1e-6, 1.0)
p = prob(TID, "optical density of 1.3")
close(value(p), 100 * t13, 1e-9, "transmission at OD 1.3 (%)"); close(round(100 * t13, 1), 5.0, 1e-12, "5.0%")
close(1 if has(p, 100 * math.exp(-1.3)) and has(p, 100 - 100 * t13) else 0, 1, 0, "decoys: e^−OD and the fraction absorbed")
close(10 ** -1, 0.10, 1e-12, "card: OD 1 transmits 10%"); close(10 ** -2, 0.01, 1e-12, "card: OD 2 transmits 1%")
p = prob(TID, "net optical density of the irradiated part")
close(value(p), od(850, 120), 1e-12, "typed net OD"); close(round(od(850, 120), 3), 0.850, 1e-12, "0.850")
close(1 if abs(od(1000, 120) / od(850, 120) - 1) > p["tol"] else 0, 1, 0, "the OD without the unexposed film is outside the tolerance")

# ---- Fricke: count the ferric ions and charge each with the energy that makes one
def fricke(da, eps, l_cm, rho, ions_per_100ev=None, g_mol_j=None):
    mol_per_kg = da / (eps * l_cm) / rho                                       # mol/L of Fe³⁺ over kg/L of solution
    ions = mol_per_kg * NA
    ev_per_ion = 100 / ions_per_100ev if ions_per_100ev else 1 / (g_mol_j * NA * E)
    return ions * ev_per_ion * E                                               # J/kg
close(M.fr_d, fricke(0.150, 2174, 1.00, 1.024, g_mol_j=1.61e-6), 1e-12, "worked example: Fricke dose"); close(round(M.fr_d, 1), 41.9, 1e-12, "41.9 Gy")
close(M.fr_c, 0.150 / 2174, 1e-12, "ferric ion concentration")
g_f = 15.5 / (100 * F)                                                         # mol/J through the Faraday constant
close(M.g_mol_per_j(15.5), g_f, 1e-9, "15.5 per 100 eV in mol/J"); close(round(1e6 * g_f, 2), 1.61, 1e-12, "1.61 μmol/J, as the text and the card say")
p = prob(TID, "ions per 100 eV")
d_fr = fricke(0.090, 2174, 1.00, 1.024, ions_per_100ev=15.5)
close(value(p), d_fr, 1e-9, "keyed Fricke dose"); close(round(d_fr, 1), 25.2, 1e-12, "25.2 Gy")
close(1 if has(p, fricke(0.090, 2174, 1.00, 1.0, ions_per_100ev=15.5)) and has(p, fricke(0.090, 2174, 1.00, 1.024, g_mol_j=15.5e-6)) else 0, 1, 0, "decoys: no density, and G read as 15.5 μmol/J")

# ---- calorimetry: the temperature rise of water per gray, with c = 1 cal g⁻¹ K⁻¹
close(M.cal_mk, 1 / 4.184, 2e-3, "about 0.24 mK per Gy"); close(1 if f"{M.cal_mk:.2f} mK" in txt else 0, 1, 0, "the text prints 0.24 mK")

# ---- effective atomic numbers (power law over the electron fractions) and the low-energy over-response they imply
COMP = {"water": [(1, 2), (8, 1)], "LiF": [(3, 1), (9, 1)], "Al2O3": [(13, 2), (8, 3)], "Si": [(14, 1)], "AgBr": [(47, 1), (35, 1)]}
MASS = {1: 1.008, 3: 6.94, 8: 15.999, 9: 18.998, 13: 26.982, 14: 28.085, 35: 79.904, 47: 107.868}
def zeff(mat, m):
    el = sum(z * k for z, k in COMP[mat]); return sum(z * k / el * z ** m for z, k in COMP[mat]) ** (1 / m)
def e_per_g(mat):
    return NA * sum(z * k for z, k in COMP[mat]) / sum(MASS[z] * k for z, k in COMP[mat])
close(round(zeff("water", 2.94), 1), 7.4, 1e-12, "water 7.4"); close(round(zeff("LiF", 2.94), 1), 8.2, 1e-12, "LiF 8.2")
close(1 if 10.8 < zeff("Al2O3", 2.94) < zeff("Al2O3", 3.5) < 11.5 else 0, 1, 0, f"Al2O3 about 11 ({zeff('Al2O3', 2.94):.2f} to {zeff('Al2O3', 3.5):.2f})")
def kn_tr(k):                                                                  # Klein-Nishina energy-transfer cross section per electron (cm²), by integration over angle
    re2, s, steps = 2.8179403e-13 ** 2, 0.0, 4000
    for i in range(steps):
        c = -1 + (i + 0.5) * 2 / steps; f = 1 / (1 + k * (1 - c))
        s += math.pi * re2 * f * f * (f + 1 / f - (1 - c * c)) * (1 - f) * 2 / steps
    return s
mu_c = e_per_g("water") * kn_tr(30 / 511)                                      # Compton energy-absorption part for water at 30 keV (cm²/g)
pe_w = 0.1557 - mu_c                                                           # photoelectric part, from the NIST total μen/ρ of water at 30 keV
def over(mat, m):                                                              # μen ratio to water at 30 keV over the ratio at megavoltage energies (electrons per gram)
    rel_e = e_per_g(mat) / e_per_g("water")
    pe = pe_w * rel_e * (zeff(mat, m) / zeff("water", m)) ** m
    return (pe + mu_c * rel_e) / 0.1557 / rel_e
for m in (3.0, 3.5):
    close(1 if 1.2 < over("LiF", m) < 1.45 else 0, 1, 0, f"LiF over-response about 1.2 to 1.4 (model, exponent {m}: {over('LiF', m):.2f})")
    close(1 if 2.9 < over("Al2O3", m) < 4.2 else 0, 1, 0, f"Al2O3 over-response three to four (model, exponent {m}: {over('Al2O3', m):.2f})")
    close(1 if 1 < over("LiF", m) < over("Al2O3", m) < over("AgBr", m) else 0, 1, 0, "the rank question's order follows the model")
p = [q for q in G["problems"] if q.get("kind") == "sort" and q["mode"] == "rank"][0]
order = [c["t"] for c in sorted(p["chips"], key=lambda c: c["b"])]
close(1 if order == ["Radiochromic film", "LiF TLD", "Al<sub>2</sub>O<sub>3</sub>:C OSLD", "Silver-halide film"] else 0, 1, 0, "the keyed rank order")

for b in bad: print("FAIL", b)
print(f"numbers_dosimeters: {n} numbers re-derived"); print("numbers_dosimeters: PASS" if not bad else f"numbers_dosimeters: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
