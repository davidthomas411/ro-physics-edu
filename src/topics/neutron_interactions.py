from blocks import *
import math, calc

# ---------------------------------------------------------------- data quoted in the text (cross sections for 0.025 eV neutrons)
BARN = 1e-24                                         # cm² per barn
MEV_J = 1e6 * calc.E_CHG                             # J per MeV
MN_MEV = 939.565                                     # neutron rest energy (MeV)
E_TH = 0.025                                         # eV, the thermal reference energy
S_H, S_N, S_O = 0.332, 1.83, 0.00019                 # H(n,γ), N(n,p), O(n,γ) (b)
S_B, S_HE, S_LI = 3840.0, 5330.0, 940.0              # B-10(n,α), He-3(n,p), Li-6(n,α) (b)
S_CD, S_GD, S_GD157 = 2500.0, 49000.0, 2.5e5         # natural Cd, natural Gd, Gd-157 (b), approximate
Q_H, Q_N, Q_HE, Q_LI = 2.224, 0.626, 0.764, 4.78     # MeV released: the γ ray of H capture; to charged particles in the others
Q_B0, Q_B1, G_B, F_B1 = 2.792, 2.310, 0.478, 0.94    # B-10: to Li-7 in its ground state, to its excited state (then a 0.478 MeV γ ray), and the share of that branch
TISSUE = dict(H=0.101, C=0.111, N=0.026, O=0.762)    # ICRU four-element soft tissue, fractions by mass
MOLAR = dict(H=1.008, C=12.011, N=14.007, O=15.999, B10=10.013, Cd=112.41, Gd=157.25)   # g/mol
RHO_CD, RHO_GD = 8.65, 7.90                          # g/cm³
XI_W = 0.92                                          # ξ of water: the H and O values weighted by their scattering cross sections
EX_C, EX_W = 4.44, 0.111                             # first excited levels (MeV) of C-12 and W-184
H_FAT, H_MUS, H_BONE = "11", "10", "3 to 6"          # hydrogen, % by mass: adipose tissue, muscle, bone (ICRU 46 and 44)

# ---------------------------------------------------------------- formulas
def e_max(A):
    """Largest fraction of the neutron energy given to a nucleus of mass number A at rest (head-on collision; masses in neutron masses)."""
    return 4 * A / (1 + A) ** 2

def alpha(A):
    """Smallest fraction of its energy the neutron keeps after an elastic collision."""
    return ((A - 1) / (A + 1)) ** 2

def mean_loss(A):
    """Mean fraction of the energy lost per collision, for scattering isotropic in the centre-of-mass frame."""
    return (1 - alpha(A)) / 2

def xi(A):
    """Mean logarithmic energy decrement, the mean of ln(E/E') per collision."""
    a = alpha(A)
    return 1.0 if A == 1 else 1 + a * math.log(a) / (1 - a)

def n_coll(e0, e1, x):
    """Collisions needed to slow a neutron from e0 to e1 (same unit) in a medium of decrement x."""
    return math.log(e0 / e1) / x

def per_cm3(rho, molar):
    """Nuclei per cm³ of an element of density rho (g/cm³) and molar mass M (g/mol)."""
    return rho * calc.NA / molar

def sig_1v(s0, e_ev, e0=E_TH):
    """Cross section at e_ev from its value s0 at e0, where it varies as 1/v."""
    return s0 * math.sqrt(e0 / e_ev)

def speed(e_ev):
    """Speed (m/s) of a neutron of kinetic energy e_ev."""
    return 2.99792458e8 * math.sqrt(2 * e_ev / (MN_MEV * 1e6))

def split(q, m_self, m_other):
    """Kinetic energy of one of two fragments that share q from a reaction at rest: equal and opposite momenta."""
    return q * m_other / (m_self + m_other)

def thr(e_star, A):
    """Neutron energy needed to excite a level e_star in a nucleus of mass number A: the energy in the centre-of-mass frame must reach it."""
    return e_star * (A + 1) / A

def capture_gy(phi, w, molar, s_b, e_mev):
    """Energy released per kg (Gy if it stays local) by captures in an element of mass fraction w, for a thermal fluence phi (cm⁻²)."""
    return phi * w * calc.NA / molar * 1000 * s_b * BARN * e_mev * MEV_J

def wr_n(e):
    """ICRP 103 radiation weighting factor for neutrons of energy e in MeV: one continuous function in three branches."""
    if e < 1.0: return 2.5 + 18.2 * math.exp(-math.log(e) ** 2 / 6)
    if e <= 50.0: return 5.0 + 17.0 * math.exp(-math.log(2 * e) ** 2 / 6)
    return 2.5 + 3.25 * math.exp(-math.log(0.04 * e) ** 2 / 6)

def q_l(L):
    """ICRP 60 quality factor against unrestricted LET in water (keV/µm)."""
    return 1.0 if L < 10 else (0.32 * L - 2.2 if L <= 100 else 300 / math.sqrt(L))

# ---------------------------------------------------------------- values in the text and the worked examples
v_th = speed(E_TH)
f_c, f_o, f_pb = e_max(12), e_max(16), e_max(208)
ml_c, ml_o, ml_pb = mean_loss(12), mean_loss(16), mean_loss(208)
xi_c, xi_pb = xi(12), xi(208)
L2 = math.log(2.0e6 / E_TH)                                              # 2 MeV to 0.025 eV
n_h, n_w, n_c, n_pb = L2 / xi(1), L2 / XI_W, L2 / xi_c, L2 / xi_pb
thr_c, thr_w = thr(EX_C, 12), thr(EX_W, 184)
e_pn, e_c14 = split(Q_N, 1, 14), split(Q_N, 14, 1)
e_a, e_li = split(Q_B1, 4, 7), split(Q_B1, 7, 4)
e_p3, e_t3 = split(Q_HE, 1, 3), split(Q_HE, 3, 1)
e_t6, e_a6 = split(Q_LI, 3, 4), split(Q_LI, 4, 3)
e_b = F_B1 * Q_B1 + (1 - F_B1) * Q_B0                                    # mean energy to charged particles per B-10 capture
n_cd = per_cm3(RHO_CD, MOLAR["Cd"]); sig_cd = n_cd * S_CD * BARN; mfp_cd = 1e4 / sig_cd; x_cd = 0.050; t_cd = math.exp(-sig_cd * x_cd)
mol = {k: TISSUE[k] / MOLAR[k] for k in TISSUE}                          # mol per g of tissue
h_more = mol["H"] / (mol["C"] + mol["N"] + mol["O"])                     # hydrogen nuclei per gram over all the others
e_hcap = capture_gy(1.0, TISSUE["H"], MOLAR["H"], S_H, Q_H)              # J/kg per unit fluence, as 2.2 MeV γ rays
k_ncap = capture_gy(1.0, TISSUE["N"], MOLAR["N"], S_N, Q_N)              # J/kg per unit fluence, local
r_hn = e_hcap / k_ncap
PHI_B, C_B = 1.0e12, 30e-6                                               # thermal fluence (cm⁻²) and B-10 mass fraction (30 µg/g)
nb_kg = C_B * 1000 * calc.NA / MOLAR["B10"]; cap_b = nb_kg * S_B * BARN * PHI_B
nn_kg = TISSUE["N"] * 1000 * calc.NA / MOLAR["N"]
d_b = capture_gy(PHI_B, C_B, MOLAR["B10"], S_B, e_b); d_n = capture_gy(PHI_B, TISSUE["N"], MOLAR["N"], S_N, Q_N)
wr_th, wr_01, wr_1, wr_100, wr_200 = wr_n(E_TH * 1e-6), wr_n(0.1), wr_n(1.0), wr_n(100.0), wr_n(200.0)
q_100 = q_l(100)

ROWS_CLASS = [
    ["Thermal", f"Below about 0.5 eV; 0.025 eV (about {round(v_th, -2):,.0f} m/s) at 20 °C", "Scattering with no net energy loss, then capture by <sup>1</sup>H(n,γ) or <sup>14</sup>N(n,p)"],
    ["Epithermal", "About 0.5 eV to 10 keV", "Elastic scattering on hydrogen, which slows them to thermal energies"],
    ["Fast", "Above about 10 keV", "Elastic scattering, mostly on hydrogen; above a few MeV also inelastic scattering and (n,α)"]]
ROWS_CAPTURE = [
    ["<sup>1</sup>H(n,γ)<sup>2</sup>H", f"{S_H:.2f}", f"{Q_H:.2f} MeV γ ray", "Main capture in water and tissue"],
    ["<sup>14</sup>N(n,p)<sup>14</sup>C", f"{S_N:.1f}", f"{Q_N:.2f} MeV; proton {e_pn:.2f} MeV", "Local thermal-neutron dose in tissue"],
    ["<sup>10</sup>B(n,α)<sup>7</sup>Li", f"{S_B:,.0f}", f"{Q_B0:.2f} MeV; in {100 * F_B1:.0f}% of captures {Q_B1:.2f} MeV (α {e_a:.2f}, Li {e_li:.2f} MeV) and a {G_B:.2f} MeV γ ray", "BF<sub>3</sub> counters, BNCT, borated absorbers"],
    ["<sup>3</sup>He(n,p)<sup>3</sup>H", f"{S_HE:,.0f}", f"{Q_HE:.2f} MeV (p {e_p3:.2f}, t {e_t3:.2f} MeV)", "He-3 counters"],
    ["<sup>6</sup>Li(n,α)<sup>3</sup>H", f"{S_LI:.0f}", f"{Q_LI:.2f} MeV (t {e_t6:.2f}, α {e_a6:.2f} MeV)", "TLD-600 chips, scintillators"],
    ["Cd and Gd (n,γ)", f"About {S_CD:,.0f} (natural Cd); about {sci(S_GD157, 2)} (<sup>157</sup>Gd)", "γ rays", "Absorbers of slow neutrons"]]

TOPIC = dict(
    id="neutron-interactions", domain=1, sub="I.E", title="Neutron interactions and dose",
    ref=dict(aapm="", khan="", ford="6"),
    guide=[
        H("Energy classes and cross sections"),
        P("A neutron carries no charge, so it passes atomic electrons without ionizing and interacts only with nuclei, through the short-range nuclear force. A fast neutron travels a few centimetres in tissue between collisions. Like a photon it is indirectly ionizing, but its charged secondaries are recoil nuclei, mostly protons, and reaction products, all densely ionizing."),
        TABLE(["Class", "Energy (boundaries vary between sources)", "Main interactions in tissue"], ROWS_CLASS),
        P("The cross section σ, in barns (1 b = 10<sup>−24</sup> cm²), is the effective target area of one nucleus. The macroscopic cross section Σ = Nσ, with N the nuclei per cm³, corresponds to μ for photons: uncollided neutrons fall as e<sup>−Σx</sup>, and 1/Σ is the mean free path. At low energies, away from resonances, capture cross sections vary as 1/v, so slow neutrons are captured far more readily."),
        EQ("Σ = N σ,   N = ρ N<sub>A</sub> / M   (nuclei per cm³)", "Φ(x) = Φ<sub>0</sub> e<sup>−Σx</sup>,   mean free path = 1/Σ", "σ(E) = σ<sub>0</sub> √(0.025 eV / E)   (1/v region)"),

        H("Elastic scattering and moderation"),
        P(f"In elastic scattering the struck nucleus stays in its ground state and the kinetic energy is shared. With nuclear masses taken as A neutron masses, the largest transfer, in a head-on collision, depends only on A. For scattering isotropic in the centre-of-mass frame, the energy after a collision is spread evenly from αE to E, so on average a neutron loses half its energy to hydrogen but {100 * ml_o:.0f}% to oxygen."),
        EQ("ΔE<sub>max</sub> / E = 4A / (1 + A)² = 1 − α,   α = [(A − 1) / (A + 1)]²", "mean fraction lost = (1 − α) / 2", "ξ = mean of ln(E / E′) = 1 + α ln α / (1 − α),   ξ = 1 for hydrogen", "collisions from E<sub>0</sub> to E:   n = ln(E<sub>0</sub> / E) / ξ"),
        P(f"The logarithmic energy decrement ξ, the mean drop in ln E per collision, does not depend on the energy: a 2 MeV neutron reaches 0.025 eV after about {n_h:.0f} collisions in hydrogen, {n_c:.0f} in carbon, and {round(n_pb, -2):,.0f} in lead. A moderator, a material that slows neutrons, works best when rich in hydrogen, like water, polyethylene, and tissue, in which fast neutrons give their energy mostly to recoil protons."),
        EX("Largest energy given to a nucleus", STEM("A 2.0 MeV neutron strikes a nucleus at rest head-on. Take the nuclear mass as A neutron masses.", ["targets: hydrogen (A = 1), carbon (A = 12), oxygen (A = 16)"], "Find the [[largest energy each nucleus can receive]]."),
           [f"Hydrogen: 4 × 1 / 2² = {e_max(1):.0f}, so {2.0 * e_max(1):.1f} MeV",
            f"Carbon: 4 × 12 / 13² = 48/169 = {f_c:.3f}, so {2.0 * f_c:.2f} MeV",
            f"Oxygen: 4 × 16 / 17² = 64/289 = {f_o:.3f}, so {2.0 * f_o:.2f} MeV"],
           f"{2.0 * e_max(1):.1f}, {2.0 * f_c:.2f}, and {2.0 * f_o:.2f} MeV. Only a proton can take the whole energy."),
        EX("Collisions to thermal energy", STEM("A 2.0 MeV neutron slows to 0.025 eV by elastic scattering, isotropic in the centre-of-mass frame.", ["ξ = 1 for hydrogen", "ξ = 0.92 for water (H and O weighted by their scattering cross sections)", "carbon: A = 12"], "Find the [[number of collisions]] in hydrogen, in water, and in carbon."),
           [f"ln(2.0 × 10<sup>6</sup> eV / 0.025 eV) = ln(8.0 × 10<sup>7</sup>) = {L2:.2f}",
            f"Hydrogen: {L2:.2f} / 1 = {n_h:.1f};   water: {L2:.2f} / 0.92 = {n_w:.1f}",
            f"Carbon: α = (11/13)² = {alpha(12):.3f}, ξ = 1 + {alpha(12):.3f} × ln {alpha(12):.3f} / {1 - alpha(12):.3f} = {xi_c:.3f}",
            f"Carbon: {L2:.2f} / {xi_c:.3f} = {n_c:.0f}"],
           f"About {n_h:.0f} in hydrogen, {n_w:.0f} in water, and {n_c:.0f} in carbon, {n_c / n_h:.0f} times as many as in hydrogen. The oxygen in water adds few collisions."),

        H("Inelastic scattering, capture, and activation"),
        P(f"In inelastic scattering, (n,n′), the nucleus is left excited and emits a γ ray. The neutron needs a little more than the excitation energy: about {thr_w:.1f} MeV for tungsten, in which this is the main way fast neutrons lose energy, but {thr_c:.1f} MeV for carbon and over 6 MeV for oxygen, so in tissue it matters only above a few MeV, as do (n,α) reactions."),
        P("In radiative capture, (n,γ), a nucleus absorbs a slow neutron and emits the binding energy as γ rays; in water and tissue most captures are by hydrogen, each giving a 2.2 MeV γ ray. A few light nuclides emit charged particles instead. A cadmium sheet under a millimetre thick absorbs nearly all neutrons below about 0.5 eV and passes most above, the cadmium cutoff. Fission of U-235 or Pu-239 after capture releases about 200 MeV and two or three neutrons."),
        TABLE(["Reaction", "Thermal σ (b)", "Energy released", "Use or effect"], ROWS_CAPTURE),
        P("Capture often leaves a radioactive nucleus (activation): Co-60 and Ir-192 are made this way, gold or indium foils measure a fluence by their induced activity, and a linac head holds short-lived activity after high-energy beams."),
        EX("Thermal neutrons through cadmium", STEM("A narrow beam of 0.025 eV neutrons meets a cadmium sheet. Count only absorption.", ["thickness = 0.50 mm", f"σ = {S_CD:,.0f} b (natural cadmium, approximate)", f"density = {RHO_CD} g/cm³,   M = {MOLAR['Cd']} g/mol"], "Find the [[mean free path]] and the [[fraction transmitted]]."),
           [f"N = {RHO_CD} × 6.022 × 10<sup>23</sup> / {MOLAR['Cd']} = {sci(n_cd, 3)} nuclei/cm³",
            f"Σ = N σ = {sci(n_cd, 3)} × {S_CD:,.0f} × 10<sup>−24</sup> cm² = {sig_cd:.0f} cm<sup>−1</sup>",
            f"Mean free path = 1/Σ = {1 / sig_cd:.5f} cm = {mfp_cd:.0f} µm",
            f"Transmission = e<sup>−{sig_cd:.0f} × 0.050</sup> = e<sup>−{sig_cd * x_cd:.2f}</sup>"],
           f"{mfp_cd:.0f} µm, and {100 * t_cd:.2f}% transmitted. Above about 0.5 eV the cross section is far smaller and most neutrons pass."),

        H("Kerma, dose, and radiation weighting"),
        P("Kerma, the kinetic energy given to charged particles per unit mass, is the fluence times a kerma factor for the material and energy. Away from surfaces and interfaces it equals the dose, since the secondaries travel micrometres to millimetres."),
        P(f"Hydrogen, about 10% of soft tissue by mass, gives about 90% or more of the fast-neutron kerma below a few MeV: per gram it has {h_more:.1f} times as many nuclei as the other elements together and takes half the energy per collision. Fat therefore absorbs more per gram than muscle, and bone less, the reverse of a kilovoltage photon beam."),
        P(f"Thermal neutrons give dose through two captures. N(n,p) releases a {e_pn:.2f} MeV proton that stops within about 10 µm; H(n,γ) releases about {r_hn:.0f} times as much energy as 2.2 MeV γ rays that travel tens of centimetres, which dominate the dose to a whole body but not to a small sample."),
        P(f"In ICRP 103 the neutron radiation weighting factor w<sub>R</sub> varies continuously with energy, from about {wr_th:.1f} for thermal neutrons to a peak near {wr_1:.0f} at about 1 MeV. Above the peak the recoil protons are faster and less densely ionizing; below it, hydrogen-capture γ rays give more of the dose in the body. The older quality factor Q depends on the LET at a point (1 below 10 keV/µm, about {q_100:.0f} near 100 keV/µm, ICRP 60) and gives H = QD in the operational quantities that survey meters estimate."),

        H("Neutrons in radiotherapy and detection"),
        P(f"Photons above about 10 MV release neutrons of about 1 MeV in the linac head. In proton therapy, reactions in the patient and, with passive scattering, the nozzle give neutrons up to the proton energy. Fast neutron beams, of high LET and low oxygen enhancement ratio, have treated salivary gland tumours, but late normal-tissue damage has kept them rare."),
        P("Boron neutron capture therapy (BNCT) loads tumour cells with B-10, carried by boronophenylalanine (BPA) or sodium borocaptate (BSH), and irradiates them with epithermal neutrons from a reactor or an accelerator, which become thermal within a few centimetres. The α particle and lithium ion of each capture travel 5 to 9 µm, about one cell diameter, so the boron dose stays in the cells that hold boron."),
        EX("Boron and nitrogen doses", STEM("A tumour containing B-10 receives a fluence of thermal neutrons. Both capture reactions deposit their energy within micrometres.",
                                            ["thermal fluence = 1.0 × 10<sup>12</sup> cm<sup>−2</sup>", f"B-10 in the tumour = 30 µg/g (illustrative),   σ = {S_B:,.0f} b,   M = {MOLAR['B10']:.2f} g/mol", f"energy to charged particles per B-10 capture = {Q_B1:.2f} MeV ({100 * F_B1:.0f}%) or {Q_B0:.2f} MeV ({100 * (1 - F_B1):.0f}%)", f"nitrogen = 2.6% by mass,   σ(n,p) = {S_N} b,   {Q_N} MeV per capture"],
                                            "Find the [[boron dose]] and the [[nitrogen dose]]."),
           [f"B-10 nuclei per kg = 30 × 10<sup>−6</sup> × 1000 g × 6.022 × 10<sup>23</sup> / {MOLAR['B10']:.2f} = {sci(nb_kg, 3)}",
            f"Captures per kg = {sci(nb_kg, 3)} × {sci(S_B * BARN, 3)} cm² × 10<sup>12</sup> cm<sup>−2</sup> = {sci(cap_b, 3)}",
            f"Mean energy per capture = {F_B1:.2f} × {Q_B1:.2f} + {1 - F_B1:.2f} × {Q_B0:.2f} = {e_b:.2f} MeV; the {G_B:.2f} MeV γ ray escapes",
            f"Boron dose = {sci(cap_b, 3)} × {e_b:.2f} MeV × 1.602 × 10<sup>−13</sup> J/MeV = {d_b:.2f} Gy",
            f"Nitrogen: {sci(nn_kg, 3)} nuclei/kg × {sci(S_N * BARN, 3)} cm² × 10<sup>12</sup> cm<sup>−2</sup> × {Q_N} MeV × 1.602 × 10<sup>−13</sup> J/MeV = {d_n:.3f} Gy"],
           f"{d_b:.1f} Gy from boron and {d_n:.2f} Gy from nitrogen: the boron dose is about {d_b / d_n:.0f} times larger, before any biological weighting."),
        P("In a BF<sub>3</sub> or He-3 counter each neutron capture gives about 2.3 or 0.76 MeV to charged particles in the gas, far above photon pulses, which a pulse-height threshold rejects. A bare counter responds mainly to slow neutrons; a moderator sets the energy response, and spheres of several diameters (Bonner spheres) unfold a spectrum. In the pulsed field of a linac, passive detectors serve: activation foils, bubble detectors, and TLD-600 (enriched in Li-6) with TLD-700 (Li-7) chips, whose difference is the neutron signal."),
    ],
    cards=[
        F("Neutron interactions with matter", "Uncharged, so a neutron interacts only with nuclei, through the nuclear force. Its charged secondaries are recoil nuclei and reaction products, all densely ionizing."),
        F("Neutron energy classes", ["Thermal: below about 0.5 eV; 0.025 eV at about 2,200 m/s at 20 °C", "Epithermal: about 0.5 eV to 10 keV", "Fast: above about 10 keV"]),
        F("Macroscopic cross section", "Σ = Nσ (cm<sup>−1</sup>), the neutron counterpart of μ. Uncollided neutrons fall as e<sup>−Σx</sup>, and 1/Σ is the mean free path. 1 b = 10<sup>−24</sup> cm²."),
        F("Capture cross section and speed", "At low energies, away from resonances, σ varies as 1/v, that is as E<sup>−1/2</sup>: slow neutrons are captured far more readily than fast ones."),
        F("Largest energy transfer in elastic scattering", f"4A/(1 + A)² of the neutron energy, in a head-on collision: all of it to hydrogen, {100 * f_c:.0f}% to carbon, {100 * f_o:.0f}% to oxygen, {100 * f_pb:.0f}% to lead.",
          w=[f"Carbon: 48/169 = {f_c:.3f}", f"Oxygen: 64/289 = {f_o:.3f}", f"Lead: 832/209² = {f_pb:.4f}"]),
        F("Mean energy loss per elastic collision", f"(1 − α)/2, with α = [(A − 1)/(A + 1)]², for scattering isotropic in the centre-of-mass frame: half the energy for hydrogen, {100 * ml_c:.0f}% for carbon, {100 * ml_o:.0f}% for oxygen."),
        F("Collisions to thermal energy", f"n = ln(E<sub>0</sub>/E)/ξ. From 2 MeV to 0.025 eV: about {n_h:.0f} in hydrogen, {n_w:.0f} in water, {n_c:.0f} in carbon.",
          w=[f"ln(8.0 × 10<sup>7</sup>) = {L2:.2f}", f"ξ: hydrogen 1, water 0.92, carbon {xi_c:.3f}"]),
        F("Inelastic neutron scattering", f"(n,n′): the nucleus is left excited and emits a γ ray. It needs a little more than the excitation energy: about {thr_w:.1f} MeV in tungsten, {thr_c:.1f} MeV in carbon."),
        F("Thermal-neutron capture in tissue", f"<sup>1</sup>H(n,γ), {S_H:.2f} b: a {Q_H:.1f} MeV γ ray that travels far. <sup>14</sup>N(n,p), {S_N:.1f} b: a {e_pn:.2f} MeV proton that stops within about 10 µm."),
        F("Capture reactions with charged products", [f"<sup>10</sup>B(n,α)<sup>7</sup>Li: {S_B:,.0f} b, {Q_B1:.2f} MeV in {100 * F_B1:.0f}% of captures", f"<sup>3</sup>He(n,p)<sup>3</sup>H: {S_HE:,.0f} b, {Q_HE:.2f} MeV", f"<sup>6</sup>Li(n,α)<sup>3</sup>H: {S_LI:.0f} b, {Q_LI:.2f} MeV"]),
        F("Cadmium and gadolinium", f"Absorbers of slow neutrons by (n,γ). Natural cadmium, about {S_CD:,.0f} b, absorbs nearly all neutrons below about 0.5 eV (the cadmium cutoff); Gd-157, about {sci(S_GD157, 2)} b."),
        F("Fast-neutron kerma in soft tissue", "Mostly from recoil protons: about 90% or more from hydrogen below a few MeV. Fat absorbs more per gram than muscle, and bone less."),
        F("Shape of the neutron w<sub>R</sub> curve", f"Peaks near {wr_1:.0f} at about 1 MeV and falls to about {math.floor(wr_200):.0f} to {math.ceil(wr_100):.0f} at 100 to 200 MeV, as the recoil protons get faster. Below the peak, more of the dose in the body comes from 2.2 MeV capture γ rays (ICRP 103)."),
        F("Quality factor against w<sub>R</sub>", f"Q(L) depends on the LET at a point (1 below 10 keV/µm, about {q_100:.0f} near 100 keV/µm, ICRP 60) and gives H = QD for operational quantities. w<sub>R</sub> is set by the radiation reaching the body."),
        F("Boron neutron capture therapy", f"B-10 carried into tumour cells (BPA or BSH) and an epithermal beam that becomes thermal in tissue. The α particle ({e_a:.2f} MeV) and Li-7 ion ({e_li:.2f} MeV) travel 5 to 9 µm, about one cell diameter."),
        F("Detection of neutrons by capture", "BF<sub>3</sub> and He-3 counters: each capture deposits 2.3 or 0.76 MeV, far above photon pulses. TLD-600 (Li-6) read against TLD-700 (Li-7) gives the neutron signal."),
    ],
)

# ---------------------------------------------------------------- numbers in the questions
s_1ev = sig_1v(S_B, 1.0); s_1ev_e = S_B * E_TH / 1.0; s_1ev_inv = S_B * math.sqrt(1.0 / E_TH)        # 1/v; 1/E; square root inverted
L1 = math.log(1.0e6 / E_TH)                                                                          # 1 MeV to 0.025 eV
n_g, n_g_log10, n_g_mean, n_g_h = L1 / xi_c, math.log10(1.0e6 / E_TH) / xi_c, L1 / ml_c, L1
n_gd = per_cm3(RHO_GD, MOLAR["Gd"]); sig_gd = n_gd * S_GD * BARN; x_gd = 1e4 * math.log(100) / sig_gd; x_gd_log10 = 1e4 * math.log10(100) / sig_gd   # µm
cap_h_frac = 2 * S_H / (2 * S_H + S_O)                                                               # share of captures in water that are on hydrogen
r_hn_sig = (S_H * Q_H) / (S_N * Q_N)                                                                  # amounts of each element left out
r_hn_mass = (TISSUE["H"] * S_H * Q_H) / (TISSUE["N"] * S_N * Q_N)                                    # mass fractions not divided by the molar masses
r_hn_count = (mol["H"] * S_H) / (mol["N"] * S_N)                                                     # numbers of captures only
W3 = [(0.010, round(wr_th, 1)), (0.020, round(wr_01, 1)), (0.030, round(wr_1, 1))]                   # mGy and w_R by energy group
D3 = sum(d for d, _ in W3)
h_q = sum(d * w for d, w in W3); h_q10 = 10 * D3; h_mean = sum(w for _, w in W3) / 3 * D3; h_peak = round(wr_1, 1) * D3
RANK = [("Hydrogen gas", n_h), ("Water", n_w), ("Graphite", n_c), ("Lead", n_pb)]
assert [x[1] for x in RANK] == sorted(x[1] for x in RANK)

PROBLEMS = [
    # ---- 1-2: energy classes and cross sections
    PR(STEM("A 2 MeV neutron and a 2 MeV electron enter soft tissue.", [], "Why does the neutron travel centimetres between interactions while the electron ionizes all along its track?"),
       "It has no charge, so it interacts only with nuclei, a small target",
       ["Its larger mass keeps atomic electrons from deflecting it", "It moves too fast for atomic electrons to respond", "Its magnetic moment repels the atomic electrons"],
       "Ionization along a track needs the Coulomb force, which acts on every electron a charged particle passes. The neutron feels only the short-range nuclear force, so it interacts only when it comes close to a nucleus. Mass alone does not prevent ionization, since a proton of nearly the same mass ionizes densely, and the 2 MeV neutron is far slower than the 2 MeV electron.", lvl="Easy"),
    PRN(STEM("The capture cross section of B-10 follows the 1/v law at low energies.", [f"σ at 0.025 eV = {S_B:,.0f} b", "neutron energy = 1.0 eV"], "What is the [[capture cross section]] at 1.0 eV?"), s_1ev, [s_1ev_e, S_B, s_1ev_inv], "{:,.0f} b",
        f"σ varies as 1/v, that is as E<sup>−1/2</sup>, so σ = {S_B:,.0f} × √(0.025 / 1.0) = {S_B:,.0f} × {math.sqrt(E_TH):.4f} = {s_1ev:,.0f} b. Scaling with 1/E gives {s_1ev_e:,.0f} b, leaving the value unchanged gives {S_B:,.0f} b, and inverting the square root gives {s_1ev_inv:,.0f} b.", lvl="Moderate"),
    # ---- 3-6: elastic scattering and moderation
    PR(STEM(ask="Why is hydrogen the most effective nucleus for slowing fast neutrons?"),
       "Its mass nearly equals the neutron's, so one collision can transfer all the energy",
       ["Its electron absorbs the neutron's energy by ionization", "It captures fast neutrons more readily than other nuclei", "Its charge repels the neutron and brakes it"],
       f"The largest transfer in an elastic collision is 4A/(1 + A)², which is 1 for A = 1 and {f_o:.2f} for oxygen. A neutron does not ionize, hydrogen captures mainly slow neutrons and with a small cross section ({S_H:.2f} b), and an uncharged neutron feels no Coulomb repulsion.", lvl="Easy"),
    PRN(STEM("A fast neutron scatters elastically from a Pb-208 nucleus (Z = 82).", [], "What is the [[largest fraction of its energy]] that the neutron can lose in one collision?"), 100 * f_pb, [100 * ml_pb, 100 * e_max(82), 100 * alpha(208)], "{:.2f}%",
        f"4A/(1 + A)² = 4 × 208 / 209² = {f_pb:.4f}, or {100 * f_pb:.2f}%. The mean loss, (1 − α)/2, is half of that ({100 * ml_pb:.2f}%); using Z = 82 in place of A gives {100 * e_max(82):.2f}%; and {100 * alpha(208):.2f}% is the fraction the neutron keeps.", lvl="Moderate"),
    PRN(STEM("A 1.0 MeV neutron slows to 0.025 eV in graphite by elastic scattering.", [f"ξ for carbon = {xi_c:.3f}"], "About how many [[collisions]] does it need?"), n_g, [n_g_log10, n_g_mean, n_g_h], "{:.0f}",
        f"n = ln(1.0 × 10<sup>6</sup> / 0.025) / ξ = {L1:.2f} / {xi_c:.3f} = {n_g:.0f}. Using log<sub>10</sub> gives {n_g_log10:.0f}, using the mean fractional loss ({ml_c:.3f}) in place of ξ gives {n_g_mean:.0f}, and taking ξ = 1, the value for hydrogen, gives {n_g_h:.0f}.", lvl="Moderate"),
    SORT(STEM("A 2 MeV neutron slows to 0.025 eV by elastic scattering in each material.", [], "Rank the [[materials]] by the number of collisions needed, from fewest to most."),
         ["1st (fewest)", "2nd", "3rd", "4th (most)"], [(t, i) for i, (t, _) in enumerate(RANK)],
         f"n = ln(E<sub>0</sub>/E)/ξ = {L2:.1f}/ξ: hydrogen {n_h:.0f}, water {n_w:.0f} (ξ = 0.92), graphite {n_c:.0f} (ξ = {xi_c:.3f}), and lead about {round(n_pb, -2):,.0f} (ξ = {xi_pb:.4f}). Water needs slightly more collisions than pure hydrogen because a collision with oxygen removes little energy.", lvl="Challenging", mode="rank", cap=1),
    # ---- 7-12: inelastic scattering, capture, and activation
    PR(STEM(ask="What distinguishes inelastic from elastic scattering of a neutron?"),
       "The struck nucleus is left excited and emits a γ ray",
       ["The neutron is absorbed and a proton leaves the nucleus", "The neutron gives its energy to the atomic electrons", "The total kinetic energy of the pair is conserved"],
       f"In inelastic scattering, (n,n′), part of the energy excites the nucleus, which then emits a γ ray, so kinetic energy is not conserved and the neutron needs more than the excitation energy, about {thr_c:.1f} MeV for carbon. Kinetic energy is conserved in elastic scattering, absorption with a proton leaving is an (n,p) reaction, and neutrons do not interact with electrons.", lvl="Easy"),
    PR(STEM("Slowed neutrons are captured in a water phantom.", [], "Which capture produces most of the [[capture γ rays]]?"),
       "Capture by hydrogen, emitting a 2.2 MeV γ ray",
       ["Capture by oxygen, emitting a 4.1 MeV γ ray", "Capture by hydrogen, emitting a 0.48 MeV γ ray", "Capture by oxygen, emitting a 0.58 MeV proton"],
       f"Hydrogen captures thermal neutrons with a cross section of {S_H:.2f} b and oxygen with about {S_O:.4f} b, so {100 * cap_h_frac:.2f}% of the captures in water are H(n,γ)H-2, each with a 2.2 MeV γ ray. The 0.48 MeV γ ray belongs to B-10 capture, and a 0.58 MeV proton to N-14(n,p).", lvl="Easy"),
    PRM(STEM(ask="Which of these nuclides detect slow neutrons through the charged particles of a capture reaction?"),
        ["B-10", "He-3", "Li-6"], ["Cd-113", "H-1", "C-12"],
        f"B-10(n,α)Li-7, He-3(n,p)H-3, and Li-6(n,α)H-3 give {Q_HE:.2f} to {Q_LI:.2f} MeV to charged particles, with cross sections of {S_LI:.0f} to {S_HE:,.0f} b. Cd-113 and H-1 capture by (n,γ) and emit γ rays, and C-12 hardly captures at all.", lvl="Easy"),
    SORT("Match each capture reaction to the effect or use it accounts for.", ["<sup>10</sup>B(n,α)<sup>7</sup>Li", "<sup>3</sup>He(n,p)<sup>3</sup>H", "<sup>6</sup>Li(n,α)<sup>3</sup>H", "<sup>1</sup>H(n,γ)<sup>2</sup>H", "<sup>14</sup>N(n,p)<sup>14</sup>C"],
         [("The tumour dose in boron neutron capture therapy", 0), (f"A gas counter whose capture releases {Q_HE:.2f} MeV", 1), ("A thermoluminescent chip that responds to slow neutrons", 2), (f"{Q_H:.1f} MeV γ rays from water and tissue", 3), (f"{e_pn:.2f} MeV protons that give the local thermal-neutron dose in tissue", 4)],
         f"B-10 capture releases an α particle and a lithium ion inside the tumour cell. He-3 counters use the {Q_HE:.2f} MeV reaction, and TLD-600 chips are enriched in Li-6. Hydrogen capture gives the {Q_H:.1f} MeV γ rays, and nitrogen capture the {e_pn:.2f} MeV protons.", lvl="Easy", mode="match", cap=1),
    TYPED(STEM("A gadolinium foil is chosen to absorb thermal neutrons. Count only absorption.", [f"σ = {S_GD:,.0f} b (natural gadolinium, approximate)", f"density = {RHO_GD:.2f} g/cm³,   M = {MOLAR['Gd']} g/mol", "transmission wanted = 1%"], "What [[thickness]] is needed?"), x_gd, 0.02, "µm",
          f"N = {RHO_GD:.2f} × 6.022 × 10<sup>23</sup> / {MOLAR['Gd']} = {sci(n_gd, 3)} cm<sup>−3</sup>, Σ = N σ = {sig_gd:,.0f} cm<sup>−1</sup>, and x = ln(100)/Σ = {x_gd / 1e4:.5f} cm = {x_gd:.0f} µm. Using log<sub>10</sub>(100) in place of ln(100) gives {x_gd_log10:.0f} µm.", lvl="Moderate"),
    TYPED(STEM("A thermal neutron, whose momentum is negligible, is captured by N-14, which emits a proton and leaves C-14.", [f"energy released = {Q_N} MeV", "masses in proportion to the mass numbers, 1 and 14"], "What [[kinetic energy]] does the proton carry?"), e_pn, 0.02, "MeV",
          f"The proton and the C-14 nucleus leave with equal and opposite momenta, so their energies are in the inverse ratio of their masses: E<sub>p</sub> = {Q_N} × 14/15 = {e_pn:.3f} MeV, and C-14 takes {e_c14:.3f} MeV. Splitting the energy equally gives {Q_N / 2:.3f} MeV.", lvl="Challenging"),
    # ---- 13-18: kerma, dose, and radiation weighting
    PR(STEM("Adipose tissue, muscle, and cortical bone receive the same fluence of 1 MeV neutrons.", [], "How does the [[absorbed dose per gram]] compare?"),
       "Fat > muscle > bone, following the hydrogen content",
       ["Bone > muscle > fat, following the atomic number", "About equal, following the electrons per gram", "Muscle > fat > bone, following the water content"],
       f"Fast neutrons give most of their kerma to recoil protons, so the dose per gram follows the hydrogen per gram: about {H_FAT}% in fat, {H_MUS}% in muscle, and {H_BONE}% in bone. The atomic-number order belongs to kilovoltage photons and the near-equal doses to megavoltage photons, and water holds only part of the hydrogen in fat.", lvl="Moderate"),
    PRM(STEM("A beam of 1 MeV neutrons irradiates a large tissue phantom.", [], "Which of these contribute to the absorbed dose in the phantom?"),
        ["Recoil protons from elastic scattering on hydrogen", "Recoil carbon and oxygen nuclei", "Protons from nitrogen capture of neutrons that have slowed"],
        ["Electrons ejected directly by the neutrons", "Bremsstrahlung emitted by the slowing neutrons", "Positrons from pair production by the neutrons"],
        "A neutron interacts only with nuclei: elastic collisions set protons and heavier nuclei in motion, and neutrons that slow to thermal energies are captured, nitrogen giving protons and hydrogen γ rays. An uncharged neutron neither ejects electrons directly nor radiates bremsstrahlung, and pair production is a photon process.", lvl="Moderate"),
    PRN(STEM("Thermal neutrons are captured in ICRU four-element soft tissue.", [f"hydrogen: 10.1% by mass, σ(n,γ) = {S_H} b, {Q_H} MeV γ ray", f"nitrogen: 2.6% by mass, σ(n,p) = {S_N} b, {Q_N} MeV"], "Per unit fluence, how many [[times as much energy]] does hydrogen capture release as nitrogen capture?"),
        r_hn, [r_hn_sig, r_hn_mass, r_hn_count], "{:.2g}",
        f"The energy per gram per unit fluence is (w/M) N<sub>A</sub> σ E for each element: (0.101/1.008) × {S_H} × {Q_H} = {mol['H'] * S_H * Q_H:.4f} for hydrogen and (0.026/14.007) × {S_N} × {Q_N} = {mol['N'] * S_N * Q_N:.5f} for nitrogen, a ratio of {r_hn:.0f}. Leaving out the amounts of each element gives {r_hn_sig:.2f}, mass fractions not divided by the molar masses give {r_hn_mass:.1f}, and counting only the captures gives {r_hn_count:.1f}.", lvl="Challenging"),
    PR(STEM("Thermal neutrons irradiate a 1 g tissue sample and, in a separate exposure, the trunk of an adult.", [], "Which reaction gives most of the [[energy absorbed]] in each?"),
       "N(n,p) protons in the sample; H(n,γ) γ rays in the trunk",
       ["H(n,γ) γ rays in both the sample and the trunk", "N(n,p) protons in both the sample and the trunk", "H(n,γ) γ rays in the sample; N(n,p) protons in the trunk"],
       f"Hydrogen capture releases about {r_hn:.0f} times as much energy as nitrogen capture, but as 2.2 MeV γ rays that travel tens of centimetres: they escape a 1 g sample and are largely absorbed in a trunk. The {e_pn:.2f} MeV proton from nitrogen deposits its energy within about 10 µm wherever the capture occurs, so it dominates only where the γ rays escape.", lvl="Challenging"),
    PR(STEM(ask="How does the radiation weighting factor w<sub>R</sub> differ from the quality factor Q?"),
       "w<sub>R</sub> is set by the radiation reaching the body; Q by the LET at a point",
       ["w<sub>R</sub> is set by the tissue irradiated; Q by the radiation type", "w<sub>R</sub> applies only to neutrons; Q applies to every radiation", "w<sub>R</sub> is measured with a survey meter; Q is calculated"],
       "ICRP 60 and 103 assign w<sub>R</sub> by the type and energy of the radiation incident on the body, and it multiplies the mean absorbed dose in an organ. Q(L) depends on the LET of the charged particles at a point and gives the dose equivalent used for operational quantities, which survey meters estimate. The tissue enters through w<sub>T</sub>, not w<sub>R</sub>, and w<sub>R</sub> covers every radiation.", lvl="Moderate"),
    PRN(STEM("The neutron absorbed dose in an organ is split into three energy groups.", [f"thermal: 0.010 mGy, w<sub>R</sub> = {W3[0][1]:.1f}", f"near 0.1 MeV: 0.020 mGy, w<sub>R</sub> = {W3[1][1]:.1f}", f"near 1 MeV: 0.030 mGy, w<sub>R</sub> = {W3[2][1]:.1f}"],
             "With these ICRP 103 values, what is the [[equivalent dose]] from the neutrons?"), h_q, [h_q10, h_mean, h_peak], "{:.3f} mSv",
        f"H = Σ w<sub>R</sub> D = {W3[0][1]:.1f} × 0.010 + {W3[1][1]:.1f} × 0.020 + {W3[2][1]:.1f} × 0.030 = {h_q:.3f} mSv, a dose-weighted mean w<sub>R</sub> of {h_q / D3:.1f}. A single factor of 10 gives {h_q10:.3f} mSv, the plain mean of the three factors gives {h_mean:.3f} mSv, and the peak value for every group gives {h_peak:.3f} mSv.", lvl="Challenging"),
    # ---- 19-21: neutrons in radiotherapy and detection
    PR(STEM("In boron neutron capture therapy, thermal neutrons are captured throughout the irradiated tissue.", [], "Why is the dose from boron capture concentrated in the cells that take up B-10?"),
       "The α particle and lithium ion stop within about one cell diameter",
       ["Thermal neutrons are captured only inside the tumour cells", "The 0.48 MeV γ ray deposits its energy inside the cell", "Boron slows the neutrons until they stop inside the cell"],
       f"The {e_a:.2f} MeV α particle and the {e_li:.2f} MeV lithium ion travel about 5 to 9 µm, so their energy stays in or next to the cell where the capture happened. Neutrons are captured everywhere, mostly by hydrogen and nitrogen in normal tissue; the {G_B:.2f} MeV γ ray leaves the cell; and boron absorbs neutrons rather than slowing them.", lvl="Moderate"),
    PR(STEM("A BNCT beam is designed for a tumour about 4 cm deep.", [], "Why does it deliver epithermal rather than thermal neutrons?"),
       "Epithermal neutrons penetrate several centimetres before slowing to thermal energies",
       ["B-10 captures epithermal neutrons more readily than thermal ones", "Epithermal neutrons give no dose to the skin or the scalp", "An accelerator cannot produce neutrons as slow as thermal ones"],
       "A thermal beam is captured within the first centimetres, mostly by hydrogen and nitrogen near the surface. Epithermal neutrons slow by scattering on hydrogen as they go deeper and become thermal at a few centimetres, where B-10 captures them. The B-10 cross section falls as 1/v, so it is smaller for epithermal neutrons; the skin still receives dose; and neutrons from an accelerator can be moderated to thermal energies.", lvl="Moderate"),
    PR(STEM("A pair of LiF chips, one TLD-600 (enriched in Li-6) and one TLD-700 (almost pure Li-7), lies beside a patient during an 18 MV treatment.", [], "How does the pair give the [[neutron signal]]?"),
       "TLD-600 responds to slow neutrons and photons, TLD-700 to photons; the difference is the neutron part",
       ["TLD-700 responds to slow neutrons and photons, TLD-600 to photons; the difference is the neutron part", "Both respond to neutrons alone, and the mean of their two readings is the neutron part", "Both respond to photons alone, and the ratio of their readings gives the neutron energy"],
       f"Li-6 captures slow neutrons ({S_LI:.0f} b, {Q_LI:.2f} MeV to charged particles), while Li-7 hardly captures them, and both respond almost equally to photons. Subtracting the TLD-700 reading from the TLD-600 reading leaves the neutron signal, which a moderator around the chips extends to faster neutrons.", lvl="Moderate"),
]

INLINE = {0: [1, 2], 1: [3, 4, 5, 6], 2: [7, 8, 9, 10, 11], 3: [13, 14, 16, 17]}   # questions on the last section, and the rest, form the practice set

TERMS = ["macroscopic cross section", "logarithmic energy decrement", "moderator", "inelastic scattering", "radiative capture", "activation", "kerma factor", "quality factor"]

TAKE = [
    ["A neutron interacts only with nuclei. Its charged secondaries are recoil nuclei and reaction products, all densely ionizing.",
     f"Thermal below about 0.5 eV (0.025 eV, about {round(v_th, -2):,.0f} m/s), epithermal to about 10 keV, fast above.",
     "Σ = Nσ, with 1 b = 10<sup>−24</sup> cm². Capture cross sections rise as 1/v at low energies."],
    [f"Largest transfer per collision 4A/(1 + A)²: all of it to hydrogen, {100 * f_c:.0f}% to carbon, {100 * f_pb:.0f}% to lead.",
     f"n = ln(E<sub>0</sub>/E)/ξ: about {n_h:.0f} collisions in hydrogen and {n_c:.0f} in carbon from 2 MeV to thermal.",
     "Hydrogen-rich materials moderate best, and in tissue the energy goes to recoil protons."],
    ["Inelastic scattering leaves the nucleus excited and emitting γ rays; in tissue it needs several MeV.",
     f"Thermal capture in tissue: H(n,γ) gives a {Q_H:.1f} MeV γ ray, N(n,p) a {e_pn:.2f} MeV proton.",
     f"B-10 ({S_B:,.0f} b) and He-3 ({S_HE:,.0f} b) capture with charged products; cadmium absorbs nearly all neutrons below about 0.5 eV."],
    ["Fast-neutron dose comes mostly from recoil protons: fat absorbs more per gram than muscle, and bone less.",
     "Thermal neutrons: local dose from N(n,p), but more energy leaves as 2.2 MeV capture γ rays.",
     f"Neutron w<sub>R</sub> runs from about {wr_th:.1f} (thermal) to a peak near {wr_1:.0f} at 1 MeV. Q depends on the LET at a point."],
    ["Neutrons come from linac heads above about 10 MV and from proton nozzles and patients; BNCT uses epithermal beams.",
     "B-10 capture products travel 5 to 9 µm, about one cell diameter.",
     "BF<sub>3</sub> and He-3 counters reject photons by pulse height; a TLD-600 and TLD-700 pair separates neutrons from photons."],
]
