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
    ["<sup>10</sup>B(n,α)<sup>7</sup>Li", f"{S_B:,.0f}", f"{Q_B0:.2f} MeV; in {100 * F_B1:.0f}% of captures {Q_B1:.2f} MeV (α {e_a:.2f}, Li {e_li:.2f} MeV) and a {G_B:.2f} MeV γ ray", "BF<sub>3</sub> counters, BNCT"],
    ["<sup>3</sup>He(n,p)<sup>3</sup>H", f"{S_HE:,.0f}", f"{Q_HE:.2f} MeV", "He-3 counters"],
    ["<sup>6</sup>Li(n,α)<sup>3</sup>H", f"{S_LI:.0f}", f"{Q_LI:.2f} MeV", "TLD-600 chips"],
    ["Cd (n,γ)", f"About {S_CD:,.0f} (natural Cd)", "γ rays", "Absorbs nearly all neutrons below about 0.5 eV"]]

TOPIC = dict(
    id="neutron-interactions", domain=1, sub="I.E", title="Neutron interactions and dose",
    ref=dict(aapm="", khan="", ford="6"),
    guide=[
        H("Energy classes and cross sections"),
        P("A neutron carries no charge, so it passes atomic electrons without ionizing and interacts only with nuclei, through the short-range nuclear force. A fast neutron travels a few centimetres in tissue between collisions. Like a photon it is indirectly ionizing, but its charged secondaries are recoil nuclei, mostly protons, and reaction products, all densely ionizing."),
        TABLE(["Class", "Energy (boundaries vary between sources)", "Main interactions in tissue"], ROWS_CLASS),
        P("The macroscopic cross section Σ = Nσ, the cross section per nucleus (in barns, 1 b = 10<sup>−24</sup> cm²) times the nuclei per cm³, corresponds to μ for photons: uncollided neutrons fall as e<sup>−Σx</sup>. At low energies capture cross sections vary as 1/v, so slow neutrons are captured far more readily."),
        EQ("Σ = N σ,   Φ(x) = Φ<sub>0</sub> e<sup>−Σx</sup>,   mean free path = 1/Σ", "σ(E) = σ<sub>0</sub> √(0.025 eV / E)   (1/v region)"),

        H("Elastic scattering and moderation"),
        P(f"In elastic scattering the struck nucleus stays in its ground state and the kinetic energy is shared. With nuclear masses taken as A neutron masses, the largest transfer, in a head-on collision, depends only on A. For scattering isotropic in the centre-of-mass frame, the energy after a collision is spread evenly from αE to E, so on average a neutron loses half its energy to hydrogen but {100 * ml_o:.0f}% to oxygen."),
        EQ("ΔE<sub>max</sub> / E = 4A / (1 + A)² = 1 − α,   α = [(A − 1) / (A + 1)]²", "ξ = mean of ln(E / E′) = 1 + α ln α / (1 − α),   ξ = 1 for hydrogen", "collisions from E<sub>0</sub> to E:   n = ln(E<sub>0</sub> / E) / ξ"),
        P(f"The logarithmic energy decrement ξ, the mean drop in ln E per collision, does not depend on the energy: a 2 MeV neutron reaches 0.025 eV after about {n_h:.0f} collisions in hydrogen, {n_c:.0f} in carbon, and {round(n_pb, -2):,.0f} in lead. A moderator, a material that slows neutrons, works best when rich in hydrogen, like water, polyethylene, and tissue, in which fast neutrons give their energy mostly to recoil protons."),
        EX("Largest energy given to a nucleus", STEM("A 2.0 MeV neutron strikes a nucleus at rest head-on. Take the nuclear mass as A neutron masses.", ["targets: hydrogen (A = 1), carbon (A = 12), oxygen (A = 16)"], "Find the [[largest energy each nucleus can receive]]."),
           [f"Hydrogen: 4 × 1 / 2² = {e_max(1):.0f}, so {2.0 * e_max(1):.1f} MeV",
            f"Carbon: 4 × 12 / 13² = 48/169 = {f_c:.3f}, so {2.0 * f_c:.2f} MeV",
            f"Oxygen: 4 × 16 / 17² = 64/289 = {f_o:.3f}, so {2.0 * f_o:.2f} MeV"],
           f"{2.0 * e_max(1):.1f}, {2.0 * f_c:.2f}, and {2.0 * f_o:.2f} MeV. Only a proton can take the whole energy."),
        EX("Collisions to thermal energy", STEM("A 2.0 MeV neutron slows to 0.025 eV by elastic scattering, isotropic in the centre-of-mass frame.", ["ξ = 1 for hydrogen", "ξ = 0.92 for water (H and O weighted by their scattering cross sections)", f"ξ = {xi_c:.3f} for carbon"], "Find the [[number of collisions]] in hydrogen, in water, and in carbon."),
           [f"ln(2.0 × 10<sup>6</sup> eV / 0.025 eV) = ln(8.0 × 10<sup>7</sup>) = {L2:.2f}",
            f"Hydrogen: {L2:.2f} / 1 = {n_h:.1f};   water: {L2:.2f} / 0.92 = {n_w:.1f};   carbon: {L2:.2f} / {xi_c:.3f} = {n_c:.0f}"],
           f"About {n_h:.0f} in hydrogen, {n_w:.0f} in water, and {n_c:.0f} in carbon, {n_c / n_h:.0f} times as many as in hydrogen."),

        H("Capture and other reactions"),
        P(f"In inelastic scattering, (n,n′), the nucleus is left excited and emits a γ ray. It needs several MeV in tissue nuclei ({thr_c:.1f} MeV for carbon) and is the main way fast neutrons lose energy in heavy metals."),
        P("In radiative capture, (n,γ), a nucleus absorbs a slow neutron and emits the binding energy as γ rays; in water and tissue most captures are by hydrogen, each giving a 2.2 MeV γ ray. B-10, He-3, and Li-6 emit charged particles instead, and cadmium absorbs nearly all neutrons below about 0.5 eV. Capture often leaves a radioactive nucleus (activation), as in the production of Co-60 and Ir-192. Fission of U-235 after capture releases about 200 MeV and two or three neutrons."),
        TABLE(["Reaction", "Thermal σ (b)", "Energy released", "Use or effect"], ROWS_CAPTURE),

        H("Kerma, dose, and radiation weighting"),
        P("Neutron kerma, the kinetic energy given to charged particles per unit mass, equals the dose away from surfaces and interfaces, since the secondaries travel micrometres to millimetres."),
        P(f"Hydrogen, about 10% of soft tissue by mass, gives about 90% or more of the fast-neutron kerma below a few MeV: per gram it has {h_more:.1f} times as many nuclei as the other elements together and takes half the energy per collision. Fat therefore absorbs more per gram than muscle, and bone less, the reverse of a kilovoltage photon beam."),
        P(f"Thermal neutrons give dose through N(n,p), whose {e_pn:.2f} MeV proton stops within about 10 µm, and H(n,γ), which releases about {r_hn:.0f} times as much energy as 2.2 MeV γ rays that travel tens of centimetres and dominate the dose to a whole body."),
        P(f"In ICRP 103 the radiation weighting factor w<sub>R</sub> is set by the energy of the neutrons reaching the body, from about {wr_th:.1f} for thermal neutrons to a peak near {wr_1:.0f} at about 1 MeV. It falls above the peak as the recoil protons get faster, and below it as capture γ rays give more of the dose. The older quality factor Q depends on the LET at a point and gives H = QD in the operational quantities that survey meters estimate."),

        H("Neutrons in radiotherapy and detection"),
        P("Photons above about 10 MV release neutrons of about 1 MeV in the linac head, and proton beams release neutrons in the patient and, with passive scattering, in the nozzle. Boron neutron capture therapy (BNCT) loads tumour cells with B-10 and irradiates them with epithermal neutrons, which become thermal within a few centimetres; the α particle and lithium ion of each capture travel 5 to 9 µm, about one cell diameter, so the dose stays in cells that hold boron."),
        P("In a BF<sub>3</sub> or He-3 counter each capture gives about 2.3 or 0.76 MeV to charged particles in the gas, far above photon pulses, which a pulse-height threshold rejects. A bare counter responds mainly to slow neutrons, so a hydrogen-rich moderator surrounds it for fast ones."),
    ],
    cards=[
        F("Neutron interactions with matter", "Uncharged, so a neutron interacts only with nuclei, through the nuclear force. Its charged secondaries are recoil nuclei and reaction products, all densely ionizing."),
        F("Neutron energy classes", [f"Thermal: below about 0.5 eV; 0.025 eV at about {round(v_th, -2):,.0f} m/s at 20 °C", "Epithermal: about 0.5 eV to 10 keV", "Fast: above about 10 keV"]),
        F("Largest energy transfer in elastic scattering", f"4A/(1 + A)² of the neutron energy, in a head-on collision: all of it to hydrogen, {100 * f_c:.0f}% to carbon, {100 * f_o:.0f}% to oxygen, {100 * f_pb:.0f}% to lead.",
          w=[f"Carbon: 48/169 = {f_c:.3f}", f"Oxygen: 64/289 = {f_o:.3f}", f"Lead: 832/209² = {f_pb:.4f}"]),
        F("Collisions to thermal energy", f"n = ln(E<sub>0</sub>/E)/ξ. From 2 MeV to 0.025 eV: about {n_h:.0f} in hydrogen, {n_w:.0f} in water, {n_c:.0f} in carbon.",
          w=[f"ln(8.0 × 10<sup>7</sup>) = {L2:.2f}", f"ξ: hydrogen 1, water 0.92, carbon {xi_c:.3f}"]),
        F("Thermal-neutron capture in tissue", f"<sup>1</sup>H(n,γ), {S_H:.2f} b: a {Q_H:.1f} MeV γ ray that travels far. <sup>14</sup>N(n,p), {S_N:.1f} b: a {e_pn:.2f} MeV proton that stops within about 10 µm."),
        F("Capture reactions with charged products", [f"<sup>10</sup>B(n,α)<sup>7</sup>Li: {S_B:,.0f} b, {Q_B1:.2f} MeV in {100 * F_B1:.0f}% of captures", f"<sup>3</sup>He(n,p)<sup>3</sup>H: {S_HE:,.0f} b, {Q_HE:.2f} MeV"]),
        F("Fast-neutron kerma in soft tissue", "Mostly from recoil protons: about 90% or more from hydrogen below a few MeV. Fat absorbs more per gram than muscle, and bone less."),
        F("Shape of the neutron w<sub>R</sub> curve", f"About {wr_th:.1f} for thermal neutrons, peaking near {wr_1:.0f} at about 1 MeV, lower above as the recoil protons get faster (ICRP 103)."),
        F("Boron neutron capture therapy", f"B-10 carried into tumour cells and an epithermal beam that becomes thermal in tissue. The α particle ({e_a:.2f} MeV) and Li-7 ion ({e_li:.2f} MeV) travel 5 to 9 µm, about one cell diameter."),
        F("Neutron detection by capture", "BF<sub>3</sub> and He-3 counters: each capture deposits 2.3 or 0.76 MeV, far above photon pulses. A hydrogen-rich moderator slows fast neutrons so the counter can capture them."),
    ],
)

# ---------------------------------------------------------------- numbers in the questions
s_1ev = sig_1v(S_B, 1.0); s_1ev_e = S_B * E_TH / 1.0; s_1ev_inv = S_B * math.sqrt(1.0 / E_TH)        # 1/v; 1/E; square root inverted
L1 = math.log(1.0e6 / E_TH)                                                                          # 1 MeV to 0.025 eV
n_g, n_g_log10, n_g_mean, n_g_h = L1 / xi_c, math.log10(1.0e6 / E_TH) / xi_c, L1 / ml_c, L1
cap_h_frac = 2 * S_H / (2 * S_H + S_O)                                                               # share of captures in water that are on hydrogen

PROBLEMS = [
    # ---- 1-2: energy classes and cross sections
    PR(STEM("A 2 MeV neutron and a 2 MeV electron enter soft tissue.", [], "Why does the neutron travel centimetres between interactions while the electron ionizes all along its track?"),
       "It has no charge, so it interacts only with nuclei, a small target",
       ["Its larger mass keeps atomic electrons from deflecting it", "It moves too fast for atomic electrons to respond", "Its magnetic moment repels the atomic electrons"],
       "Ionization along a track needs the Coulomb force, which acts on every electron a charged particle passes. The neutron feels only the short-range nuclear force, so it interacts only when it comes close to a nucleus. Mass alone does not prevent ionization, since a proton of nearly the same mass ionizes densely, and the 2 MeV neutron is far slower than the 2 MeV electron.", lvl="Easy"),
    PRN(STEM("The capture cross section of B-10 follows the 1/v law at low energies.", [f"σ at 0.025 eV = {S_B:,.0f} b", "neutron energy = 1.0 eV"], "What is the [[capture cross section]] at 1.0 eV?"), s_1ev, [s_1ev_e, S_B, s_1ev_inv], "{:,.0f} b",
        f"σ varies as 1/v, that is as E<sup>−1/2</sup>, so σ = {S_B:,.0f} × √(0.025 / 1.0) = {S_B:,.0f} × {math.sqrt(E_TH):.4f} = {s_1ev:,.0f} b. Scaling with 1/E gives {s_1ev_e:,.0f} b, leaving the value unchanged gives {S_B:,.0f} b, and inverting the square root gives {s_1ev_inv:,.0f} b.", lvl="Moderate"),
    # ---- 3-5: elastic scattering and moderation
    PR(STEM(ask="Why is hydrogen the most effective nucleus for slowing fast neutrons?"),
       "Its mass nearly equals the neutron's, so one collision can transfer all the energy",
       ["Its electron absorbs the neutron's energy by ionization", "It captures fast neutrons more readily than other nuclei", "Its charge repels the neutron and brakes it"],
       f"The largest transfer in an elastic collision is 4A/(1 + A)², which is 1 for A = 1 and {f_o:.2f} for oxygen. A neutron does not ionize, hydrogen captures mainly slow neutrons and with a small cross section ({S_H:.2f} b), and an uncharged neutron feels no Coulomb repulsion.", lvl="Easy"),
    PRN(STEM("A fast neutron scatters elastically from a Pb-208 nucleus (Z = 82).", [], "What is the [[largest fraction of its energy]] that the neutron can lose in one collision?"), 100 * f_pb, [100 * ml_pb, 100 * e_max(82), 100 * alpha(208)], "{:.2f}%",
        f"4A/(1 + A)² = 4 × 208 / 209² = {f_pb:.4f}, or {100 * f_pb:.2f}%. The mean loss, (1 − α)/2, is half of that ({100 * ml_pb:.2f}%); using Z = 82 in place of A gives {100 * e_max(82):.2f}%; and {100 * alpha(208):.2f}% is the fraction the neutron keeps.", lvl="Challenging"),
    PRN(STEM("A 1.0 MeV neutron slows to 0.025 eV in graphite by elastic scattering.", [f"ξ for carbon = {xi_c:.3f}"], "About how many [[collisions]] does it need?"), n_g, [n_g_log10, n_g_mean, n_g_h], "{:.0f}",
        f"n = ln(1.0 × 10<sup>6</sup> / 0.025) / ξ = {L1:.2f} / {xi_c:.3f} = {n_g:.0f}. Using log<sub>10</sub> gives {n_g_log10:.0f}, using the mean fractional loss ({ml_c:.3f}) in place of ξ gives {n_g_mean:.0f}, and taking ξ = 1, the value for hydrogen, gives {n_g_h:.0f}.", lvl="Moderate"),
    # ---- 6-8: capture and other reactions
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
    # ---- 9-11: kerma, dose, and radiation weighting
    PR(STEM("Adipose tissue, muscle, and cortical bone receive the same fluence of 1 MeV neutrons.", [], "How does the [[absorbed dose per gram]] compare?"),
       "Fat > muscle > bone, following the hydrogen content",
       ["Bone > muscle > fat, following the atomic number", "About equal, following the electrons per gram", "Muscle > fat > bone, following the water content"],
       f"Fast neutrons give most of their kerma to recoil protons, so the dose per gram follows the hydrogen per gram: about {H_FAT}% in fat, {H_MUS}% in muscle, and {H_BONE}% in bone. The atomic-number order belongs to kilovoltage photons and the near-equal doses to megavoltage photons, and water holds only part of the hydrogen in fat.", lvl="Challenging"),
    PR(STEM("Thermal neutrons irradiate a 1 g tissue sample and, in a separate exposure, the trunk of an adult.", [], "Which reaction gives most of the [[energy absorbed]] in each?"),
       "N(n,p) protons in the sample; H(n,γ) γ rays in the trunk",
       ["H(n,γ) γ rays in both the sample and the trunk", "N(n,p) protons in both the sample and the trunk", "H(n,γ) γ rays in the sample; N(n,p) protons in the trunk"],
       f"Hydrogen capture releases about {r_hn:.0f} times as much energy as nitrogen capture, but as 2.2 MeV γ rays that travel tens of centimetres: they escape a 1 g sample and are largely absorbed in a trunk. The {e_pn:.2f} MeV proton from nitrogen deposits its energy within about 10 µm wherever the capture occurs, so it dominates only where the γ rays escape.", lvl="Challenging"),
    PR(STEM(ask="How does the radiation weighting factor w<sub>R</sub> differ from the quality factor Q?"),
       "w<sub>R</sub> is set by the radiation reaching the body; Q by the LET at a point",
       ["w<sub>R</sub> is set by the tissue irradiated; Q by the radiation type", "w<sub>R</sub> applies only to neutrons; Q applies to every radiation", "w<sub>R</sub> is measured with a survey meter; Q is calculated"],
       "ICRP 60 and 103 assign w<sub>R</sub> by the type and energy of the radiation incident on the body, and it multiplies the mean absorbed dose in an organ. Q(L) depends on the LET of the charged particles at a point and gives the dose equivalent used for operational quantities, which survey meters estimate. The tissue enters through w<sub>T</sub>, not w<sub>R</sub>, and w<sub>R</sub> covers every radiation.", lvl="Moderate"),
    # ---- 12: neutrons in radiotherapy
    PR(STEM("In boron neutron capture therapy, thermal neutrons are captured throughout the irradiated tissue.", [], "Why is the dose from boron capture concentrated in the cells that take up B-10?"),
       "The α particle and lithium ion stop within about one cell diameter",
       ["Thermal neutrons are captured only inside the tumour cells", "The 0.48 MeV γ ray deposits its energy inside the cell", "Boron slows the neutrons until they stop inside the cell"],
       f"The {e_a:.2f} MeV α particle and the {e_li:.2f} MeV lithium ion travel about 5 to 9 µm, so their energy stays in or next to the cell where the capture happened. Neutrons are captured everywhere, mostly by hydrogen and nitrogen in normal tissue; the {G_B:.2f} MeV γ ray leaves the cell; and boron absorbs neutrons rather than slowing them.", lvl="Moderate"),
]

INLINE = {0: [1, 2], 1: [3, 4, 5], 2: [6, 7, 8], 3: [9, 10, 11]}   # the question on the last section forms the practice set

TERMS = ["macroscopic cross section", "logarithmic energy decrement", "moderator", "inelastic scattering", "radiative capture", "activation", "quality factor"]

TAKE = [
    ["A neutron interacts only with nuclei. Its charged secondaries are recoil nuclei and reaction products, all densely ionizing.",
     f"Thermal below about 0.5 eV (0.025 eV, about {round(v_th, -2):,.0f} m/s), epithermal to about 10 keV, fast above.",
     "Σ = Nσ, with 1 b = 10<sup>−24</sup> cm². Capture cross sections rise as 1/v at low energies."],
    [f"Largest transfer per collision 4A/(1 + A)²: all of it to hydrogen, {100 * f_c:.0f}% to carbon, {100 * f_pb:.0f}% to lead.",
     f"n = ln(E<sub>0</sub>/E)/ξ: about {n_h:.0f} collisions in hydrogen and {n_c:.0f} in carbon from 2 MeV to thermal.",
     "Hydrogen-rich materials moderate best, and in tissue the energy goes to recoil protons."],
    ["Inelastic scattering leaves the nucleus excited and emitting γ rays; in tissue it needs several MeV.",
     f"Thermal capture in tissue: H(n,γ) gives a {Q_H:.1f} MeV γ ray, N(n,p) a {e_pn:.2f} MeV proton.",
     "B-10, He-3, and Li-6 capture with charged products; cadmium absorbs nearly all neutrons below about 0.5 eV."],
    ["Fast-neutron dose comes mostly from recoil protons: fat absorbs more per gram than muscle, and bone less.",
     "Thermal neutrons: local dose from N(n,p), but more energy leaves as 2.2 MeV capture γ rays.",
     f"Neutron w<sub>R</sub> runs from about {wr_th:.1f} (thermal) to a peak near {wr_1:.0f} at 1 MeV. Q depends on the LET at a point."],
    ["Neutrons come from linac heads above about 10 MV and from proton nozzles and patients; BNCT uses epithermal beams.",
     "B-10 capture products travel 5 to 9 µm, about one cell diameter.",
     "BF<sub>3</sub> and He-3 counters reject photons by pulse height; a moderator lets them count fast neutrons."],
]
