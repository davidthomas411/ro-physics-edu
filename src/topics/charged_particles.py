from blocks import *
import math

# ---------------------------------------------------------------- constants and the relations used in this chapter
ME = 0.51099895                 # electron rest energy (MeV)
MP = 938.27209                  # proton rest energy (MeV)
MALPHA = 3727.3794              # α-particle rest energy (MeV)
K_E = 0.153537                  # 2π r_e² m c² N_A (MeV cm²/mol)
ZA_WATER = 10 / 18.015          # Z/A of water
RULE = 800.0                    # MeV: the approximate rule S_rad/S_col ≈ Z T / 800
Z_WATER, Z_TUNG, Z_LEAD, Z_ACRYL = 7.4, 74, 82, 6.5

def layer_loss(s_mass, rho, t_cm):
    """Energy (MeV) lost in a thin layer: mass stopping power (MeV cm²/g) × density (g/cm³) × thickness (cm)."""
    return s_mass * rho * t_cm

def rad_ratio(z, t):
    """S_rad/S_col by the approximate rule Z T / 800, T in MeV."""
    return z * t / RULE

def rad_share(z, t):
    """Radiative share of the total stopping power, S_rad/S_tot = r / (1 + r)."""
    r = rad_ratio(z, t)
    return r / (1 + r)

def e_crit(z):
    """Critical energy (MeV) by the rule: the energy at which S_rad = S_col."""
    return RULE / z

def yield_rule(z, t0):
    """Radiation yield Y = (1/T0) ∫ S_rad/S_tot dT from 0 to T0, with the share taken from the rule: 1 − ln(1 + a T0)/(a T0), a = Z/800."""
    a = z * t0 / RULE
    return 1 - math.log(1 + a) / a

def hard_loss(t, delta, za=ZA_WATER):
    """Mass collision stopping power (MeV cm²/g) from collisions that give the struck electron more than delta (MeV),
    for an electron of kinetic energy t (MeV): the Møller cross section for free electrons, integrated in closed form from delta to t/2."""
    tau = t / ME; g = tau + 1; b2 = 1 - 1 / g ** 2; eta = delta / t
    c, d = (tau / g) ** 2, (2 * tau + 1) / g ** 2
    bracket = (math.log(1 / (2 * eta)) + 2 - math.log(2) - 1 / (1 - eta) - math.log(1 - eta)
               + c * (1 / 8 - eta ** 2 / 2) - d * (math.log(2) + math.log(1 - eta)))
    return K_E * za / b2 * bracket

def let_kev_um(s_mass, rho=1.0):
    """LET in keV/µm from a mass stopping power in MeV cm²/g: 1 MeV/cm = 0.1 keV/µm."""
    return s_mass * rho / 10

def w_max(t, m, exact=True):
    """Largest energy (MeV) a heavy particle of kinetic energy t and rest energy m can give one free electron at rest."""
    g = 1 + t / m
    top = 2 * ME * (g * g - 1)
    return top / (1 + 2 * g * ME / m + (ME / m) ** 2) if exact else top

def beta2(t, m):
    g = 1 + t / m
    return 1 - 1 / g ** 2

# ---------------------------------------------------------------- worked examples
# tissue and lung
T1, S1, TH1, RHO_T, RHO_L = 6.0, 2.0, 0.80, 1.04, 0.25
mt1, ml1 = RHO_T * TH1, RHO_L * TH1
de_t1, de_l1 = layer_loss(S1, RHO_T, TH1), layer_loss(S1, RHO_L, TH1)
# radiative share in water and tungsten at 10 MeV
r_w10, r_t10 = rad_ratio(Z_WATER, 10), rad_ratio(Z_TUNG, 10)
s_w10, s_t10 = rad_share(Z_WATER, 10), rad_share(Z_TUNG, 10)
ec_t, ec_pb, ec_w = e_crit(Z_TUNG), e_crit(Z_LEAD), e_crit(Z_WATER)
y_w10, y_w1 = yield_rule(Z_WATER, 10), yield_rule(Z_WATER, 1)
# restricted against unrestricted at 10 MeV
SCOL10 = 1.97
h10 = round(hard_loss(10, 0.010), 2)
l10 = SCOL10 - h10
let10, letinf = let_kev_um(l10), let_kev_um(SCOL10)
fr10 = h10 / SCOL10
# heavy particles
w100 = w_max(100, MP)
r_ap = (MALPHA / 4) / MP

TOPIC = dict(
    id="charged-particles", domain=1, sub="I.E", title="Charged-particle interactions and stopping power",
    ref=dict(aapm="", khan="", ford="6"),
    guide=[
        H("Collision losses"),
        P("A charged particle slows down through many collisions with atomic electrons. In a soft collision it passes an atom at a distance large compared with its size and excites or ionizes it with a small energy transfer. In a hard collision it meets one atomic electron at close range and gives it enough energy to leave with a track of its own: a delta ray. Soft collisions are far more numerous, yet each kind accounts for roughly half of the collision loss. An electron can lose at most half its kinetic energy in one hard collision, a positron all of it."),
        P("The linear stopping power S = dE/dx is the mean energy lost per unit path length (MeV/cm). Divided by the density it becomes the mass stopping power S/ρ (MeV cm²/g), which depends little on density and has a collision part and a radiative part."),
        EQ("S/ρ = S<sub>col</sub>/ρ + S<sub>rad</sub>/ρ   (MeV cm²/g)", "energy lost in a thin layer: ΔE = (S/ρ) × ρ × t"),
        TABLE(["", "Collision (electronic), S<sub>col</sub>/ρ", "Radiative, S<sub>rad</sub>/ρ"], [
            ["Process", "Soft and hard collisions with atomic electrons", "Bremsstrahlung, mostly in the field of a nucleus"],
            ["Medium", "Proportional to Z/A (0.555 for water, about 0.5 for other light elements, 0.40 for lead); falls slowly as the mean excitation energy I rises (water 75 eV in ICRU 37, 78 eV in ICRU 90; lead 823 eV)", "About proportional to Z (to Z² per atom)"],
            ["Energy", "Falls as 1/v² at low energy, has a broad minimum near 1 to 2 MeV for electrons, then rises slowly", "Rises nearly in proportion to the energy"],
            ["Electrons in water", "About 1.8 to 2.1 MeV cm²/g from 0.5 to 20 MeV", "Under 10% of the total up to 10 MeV"],
            ["Energy deposited", "Near the track, apart from energetic delta rays", "Away from the track, by photons"]]),
        P("With fewer electrons per gram and a higher mean excitation energy, lead has about half the S<sub>col</sub>/ρ of water at 1 MeV. In liquids and solids the polarization of nearby atoms limits the rise of S<sub>col</sub>/ρ at high energy (the density effect). A therapy electron loses about 2 MeV per centimetre of water."),
        EX("Energy lost in tissue and in lung",
           STEM("A 6 MeV electron crosses a layer of soft tissue, or a layer of lung of the same thickness.",
                [f"thickness t = {TH1:.2f} cm", f"total mass stopping power S/ρ = {S1:.1f} MeV cm²/g in both", f"soft tissue: ρ = {RHO_T:.2f} g/cm³", f"lung: ρ = {RHO_L:.2f} g/cm³ (illustrative)"],
                "Find the [[energy lost]] in each layer."),
           [f"Mass thickness: tissue {RHO_T:.2f} × {TH1:.2f} = {mt1:.3f} g/cm²; lung {RHO_L:.2f} × {TH1:.2f} = {ml1:.2f} g/cm²",
            f"Tissue: ΔE = {S1:.1f} × {mt1:.3f} = {de_t1:.2f} MeV",
            f"Lung: ΔE = {S1:.1f} × {ml1:.2f} = {de_l1:.2f} MeV"],
           f"{de_t1:.2f} MeV in tissue and {de_l1:.2f} MeV in lung. The loss per gram is the same; the loss per centimetre follows the density, so the electron travels about {RHO_T / RHO_L:.0f} times farther per MeV in this lung."),

        H("Radiative losses"),
        P("Above 1 MeV the collision loss changes little while the radiative loss keeps rising, so bremsstrahlung takes a growing share of the loss as the energy and the atomic number rise. An approximate rule gives the ratio; sources differ in the constant."),
        EQ("S<sub>rad</sub>/S<sub>col</sub> ≈ Z T / 800   (T: kinetic energy in MeV; approximate)", "E<sub>c</sub> ≈ 800 / Z MeV"),
        P(f"The critical energy E<sub>c</sub>, at which the two losses are equal, is by the rule about 10 MeV for lead and tungsten and of the order of 100 MeV for water (Z ≈ {Z_WATER}). The radiation yield is the fraction of an electron's initial kinetic energy emitted as bremsstrahlung while it slows to rest; it is below the radiative share at the start, because that share falls as the electron slows. Pure β emitters are shielded with low-Z material such as acrylic, which stops the particles while radiating little, with lead outside if needed."),
        EX("Radiative share in water and tungsten",
           STEM("A 10 MeV electron slows down in water or in tungsten.", ["S<sub>rad</sub>/S<sub>col</sub> ≈ Z T / 800, with T in MeV", f"Z ≈ {Z_WATER} for water,   Z = {Z_TUNG} for tungsten"],
                "Find the [[radiative share of the total stopping power]] in each medium and the [[critical energy]] of tungsten."),
           [f"Water: S<sub>rad</sub>/S<sub>col</sub> = {Z_WATER} × 10 / 800 = {r_w10:.4f}; S<sub>rad</sub>/S<sub>tot</sub> = {r_w10:.4f} / {1 + r_w10:.4f} = {s_w10:.4f}",
            f"Tungsten: S<sub>rad</sub>/S<sub>col</sub> = {Z_TUNG} × 10 / 800 = {r_t10:.3f}; S<sub>rad</sub>/S<sub>tot</sub> = {r_t10:.3f} / {1 + r_t10:.3f} = {s_t10:.3f}",
            f"E<sub>c</sub> = 800 / {Z_TUNG} = {ec_t:.1f} MeV"],
           f"About {100 * s_w10:.1f}% in water and {100 * s_t10:.0f}% in tungsten. Tungsten's critical energy is about {ec_t:.0f} MeV, so at 10 MeV its two losses are nearly equal."),

        H("Restricted stopping power and LET"),
        P("Radiation effects depend on the energy deposited near a particle's track; energetic delta rays and bremsstrahlung photons carry energy away from it. The restricted collision stopping power L<sub>Δ</sub> is the part of the collision loss from energy transfers below a cutoff Δ, so it leaves out the energy that delta rays above Δ carry away; as a measure of radiation quality it is called the linear energy transfer, LET<sub>Δ</sub> (ICRU 85). With no cutoff, L<sub>∞</sub> = S<sub>col</sub>, so for electrons L<sub>Δ</sub> &lt; S<sub>col</sub> &lt; S<sub>tot</sub>."),
        P("10 keV is a common cutoff. Unrestricted LET is about 0.2 keV/µm for therapy electrons and about 100 keV/µm for α particles of a few MeV."),
        EQ("1 keV/µm = 10 MeV/cm;   in water, 1 MeV cm²/g gives 0.1 keV/µm"),
        EX("Restricted and unrestricted LET at 10 MeV",
           STEM("A 10 MeV electron slows down in water.", [f"S<sub>col</sub>/ρ = {SCOL10:.2f} MeV cm²/g", f"loss to delta rays above 10 keV = {h10:.2f} MeV cm²/g", "ρ = 1.00 g/cm³"],
                "Find [[L<sub>10 keV</sub>]] and the [[unrestricted LET]], in keV/µm."),
           [f"L<sub>10 keV</sub>/ρ = {SCOL10:.2f} − {h10:.2f} = {l10:.2f} MeV cm²/g",
            f"Times ρ: {l10:.2f} MeV/cm = {let10:.3f} keV/µm",
            f"Unrestricted: L<sub>∞</sub> = S<sub>col</sub> = {SCOL10:.2f} MeV/cm = {letinf:.3f} keV/µm"],
           f"LET<sub>10 keV</sub> ≈ {let10:.2f} keV/µm against {letinf:.2f} keV/µm unrestricted; about {100 * fr10:.0f}% of the collision loss leaves the track in delta rays above 10 keV."),

        H("Range, straggling, and scattering"),
        P("The CSDA range is the mean path length of a particle that loses energy continuously at the rate of its total stopping power. In g/cm² it changes little between media of similar composition."),
        EQ("R<sub>CSDA</sub> = ∫<sub>0</sub><sup>T₀</sup> dT / (S/ρ)   (g/cm²)", "path length in cm = R<sub>CSDA</sub> / ρ"),
        TABLE(["Range", "Definition", "Kind"], [
            ["CSDA range", "∫ dT/(S/ρ) over the slowing-down: the mean path length", "Calculated"],
            ["Projected range", "Mean of the deepest point each particle reaches along its initial direction", "Calculated or measured"],
            ["Practical range R<sub>p</sub>", "Depth where the tangent at the steepest fall-off of the depth–dose curve meets the bremsstrahlung background", "Measured"],
            ["Extrapolated range", "Thickness where the tangent at the steepest point of the transmission curve (the fraction of electrons passing a slab against its thickness) meets zero", "Measured"]]),
        P("Electron paths bend, so their projected range is shorter than the CSDA range; for a clinical beam in water the practical range, about E/2 cm for E in MeV, is close to the CSDA range at the beam energy. Energy loss is random, so electrons of one energy travel different path lengths (range straggling) and stop over a wide spread of depths."),
        P("Elastic deflections by nuclei add up along the path (multiple scattering). In a thin layer the mean square angle grows in proportion to the path length and falls as the energy rises. The mass scattering power rises about as Z, so per unit energy lost high-Z materials scatter most. Electrons scatter far more than protons: an electron beam spreads with depth."),

        H("Positrons and heavy charged particles"),
        P("A positron slows like an electron and ends by annihilating, usually almost at rest, into two 511 keV photons that carry 1.022 MeV away from the track. For a heavy particle of charge ze and speed v, S<sub>col</sub> varies as z²/v² and, at a given speed, not with the mass; the range at a given speed scales as M/z². An α particle therefore loses energy 4 times as fast as a proton of the same speed and travels about as far. Heavy particles travel almost straight, straggle little, and emit negligible bremsstrahlung."),
        EQ("S<sub>col</sub> ∝ z²/v²;   R ∝ M/z² at a given speed"),
    ],
    cards=[
        F("Soft and hard collisions", ["Soft: a distant atom is excited or ionized; by far the most frequent.", "Hard: one atomic electron is released as a delta ray.", "Each kind carries roughly half the collision loss."]),
        F("Collision stopping power and the medium", "Proportional to the electrons per gram (Z/A) and lower for a higher mean excitation energy I. At 1 MeV, lead's S<sub>col</sub>/ρ is about half of water's."),
        F("Electron energy loss in water", "About 2 MeV per cm: S<sub>col</sub>/ρ stays near 1.8 to 2.1 MeV cm²/g from 0.5 to 20 MeV."),
        F("Radiative to collision stopping power", "S<sub>rad</sub>/S<sub>col</sub> ≈ Z T / 800, with T in MeV (approximate). Bremsstrahlung grows with Z and with energy.",
          w=[f"10 MeV in tungsten: {Z_TUNG} × 10 / 800 = {r_t10:.3f}"]),
        F("Critical energy", "The energy at which collision and radiative losses are equal: E<sub>c</sub> ≈ 800/Z MeV, about 10 MeV for lead and of the order of 100 MeV for water.",
          w=[f"Lead: 800 / {Z_LEAD} = {ec_pb:.1f} MeV"]),
        F("Radiation yield", "The fraction of an electron's initial kinetic energy emitted as bremsstrahlung while it slows to rest. Lower than the radiative share at the start."),
        F("Restricted collision stopping power, L<sub>Δ</sub>", "The part of the collision loss from energy transfers below a cutoff Δ; also called LET<sub>Δ</sub>. L<sub>∞</sub> = S<sub>col</sub>. Therapy electrons about 0.2 keV/µm, α particles about 100 keV/µm."),
        F("CSDA range", "The mean path length if energy is lost continuously: R = ∫ dT/(S/ρ), in g/cm². Electron paths bend, so the depth reached is shorter."),
        F("Multiple scattering of electrons", "The mean square angle grows with the path length, falls as the energy rises, and per g/cm² rises about as Z."),
        F("Heavy charged particles at one speed", "S<sub>col</sub> ∝ z², independent of mass; range ∝ M/z². An α particle loses energy 4 times as fast as a proton of the same speed and travels about as far."),
    ],
)

# ---------------------------------------------------------------- practice questions
T6, S6, TH6, RHO6 = 9.0, 1.9, 0.60, 1.92
q_bone = layer_loss(S6, RHO6, TH6)
q_bone_nr, q_bone_div, q_bone_cm = S6 * TH6, S6 * TH6 / RHO6, S6 * RHO6
q_share = 100 * rad_share(Z_WATER, 20)
q_share_r, q_share_col, q_share_z2 = 100 * rad_ratio(Z_WATER, 20), 100 - q_share, 100 * rad_share(Z_WATER ** 2, 20)
SCOL1 = 1.85
q_let1 = let_kev_um(SCOL1)
pb_acryl = Z_LEAD / Z_ACRYL

PROBLEMS = [
    PR(STEM("A 6 MeV electron slows down in water.", [], "Which [[interaction]] releases a delta ray?"),
       "A hard collision with one atomic electron",
       ["A soft collision with a distant atom", "Elastic scattering in the field of a nucleus", "Emission of a bremsstrahlung photon near a nucleus"],
       "In a hard collision one atomic electron receives enough energy to leave with a track of its own, a delta ray. A soft collision gives a small amount of energy to a distant atom as a whole, elastic scattering changes the direction with almost no loss of energy, and bremsstrahlung releases a photon rather than an electron.", lvl="Easy"),
    PR(STEM("Stopping powers of electrons are tabulated for water, bone, and lead.", [], "In what [[unit]] is the mass stopping power given?"),
       "MeV cm²/g", ["MeV/cm", "cm²/g", "MeV/g"],
       "S/ρ = (MeV/cm) ÷ (g/cm³) = MeV cm²/g. MeV/cm is the linear stopping power before division by the density, and cm²/g is the unit of a mass attenuation coefficient, which carries no energy.", lvl="Easy"),
    PRN(STEM(f"A {T6:.0f} MeV electron crosses a slab of cortical bone.", [f"thickness = {TH6:.2f} cm", f"ρ = {RHO6:.2f} g/cm³", f"total mass stopping power = {S6:.1f} MeV cm²/g"], "How much [[energy]] does the electron lose in the slab?"),
        q_bone, [q_bone_nr, q_bone_div, q_bone_cm], "{:.2f} MeV",
        f"ΔE = (S/ρ) × ρ × t = {S6:.1f} × {RHO6:.2f} × {TH6:.2f} = {q_bone:.2f} MeV. Leaving out the density gives {q_bone_nr:.2f} MeV, dividing by it gives {q_bone_div:.2f} MeV, and leaving out the thickness gives {q_bone_cm:.2f}, the linear stopping power in MeV/cm.", lvl="Moderate"),
    PR(STEM("Electrons of 1 MeV slow down in lead and in water.", ["lead: Z/A = 0.40,   I = 823 eV", "water: Z/A = 0.555,   I = 75 eV"], "Why is the [[mass collision stopping power]] of lead about half that of water?"),
       "Lead has fewer electrons per gram and a higher mean excitation energy",
       ["Lead has more electrons per gram, but its density lowers the mass stopping power", "Bremsstrahlung in lead takes energy that would otherwise go to collisions", "Elastic scattering in lead turns the electrons back before they collide"],
       "S<sub>col</sub>/ρ is proportional to Z/A, here 0.40 against 0.555, and its logarithm falls as I rises, 823 eV against 75 eV. Density cancels in a mass stopping power, and radiative loss adds to the total stopping power without reducing the collision part.", lvl="Moderate"),
    PRN(STEM("A 20 MeV electron slows down in water.", ["S<sub>rad</sub>/S<sub>col</sub> ≈ Z T / 800, with T in MeV", f"Z ≈ {Z_WATER}"], "What [[fraction of the total stopping power]] is radiative?"),
        q_share, [q_share_r, q_share_col, q_share_z2], "{:.1f}%",
        f"S<sub>rad</sub>/S<sub>col</sub> = {Z_WATER} × 20 / 800 = {q_share_r / 100:.3f}, so S<sub>rad</sub>/S<sub>tot</sub> = {q_share_r / 100:.3f} / {1 + q_share_r / 100:.3f} = {q_share:.1f}%. Reporting the ratio itself gives {q_share_r:.1f}%, and the collision share is {q_share_col:.1f}%. Using Z² gives {q_share_z2:.1f}%: the radiative loss per atom grows as Z², but the collision loss grows as Z, so their ratio grows only as Z.", lvl="Moderate"),
    PR(STEM("A vial of Y-90, a pure β emitter with a maximum β energy of 2.28 MeV, is to be shielded for handling.", [], "Which [[shield]] keeps the dose rate outside it lowest?"),
       "Acrylic thick enough to stop the β particles, with lead outside it if needed",
       ["Lead alone, thick enough to stop the β particles", "Lead next to the vial, with acrylic outside it", "Tungsten alone, since its density stops the β particles in less thickness"],
       f"Bremsstrahlung rises with Z: by the rule S<sub>rad</sub>/S<sub>col</sub> ≈ Z T / 800, an electron slowing in lead (Z = {Z_LEAD}) radiates about {pb_acryl:.0f} times as much per unit of collision loss as in acrylic (effective Z about {Z_ACRYL}). Acrylic stops the β particles with little bremsstrahlung, and lead outside attenuates the photons that remain. Lead or tungsten next to the source turns more of the β energy into penetrating photons.", lvl="Challenging"),
    PR(STEM("For a 10 MeV electron in water, the restricted collision stopping power with Δ = 10 keV is compared with the collision stopping power.", [], "Why is [[L<sub>10 keV</sub>]] the smaller of the two?"),
       "It leaves out the kinetic energy carried off by delta rays of more than 10 keV",
       ["It leaves out the energy lost in soft collisions", "It counts ionization and leaves out excitation", "It is divided by the density of water"],
       f"L<sub>Δ</sub> counts the collision loss except the energy that delta rays above Δ carry away from the track, about {100 * fr10:.0f}% of S<sub>col</sub> at 10 MeV in water. Soft collisions, excitation included, are counted in full, and both quantities are losses per unit path.", lvl="Moderate"),
    PRN(STEM("A 1 MeV electron slows down in water.", [f"S<sub>col</sub>/ρ = {SCOL1:.2f} MeV cm²/g", "ρ = 1.00 g/cm³"], "What is its [[unrestricted LET]] in keV/µm?"),
        q_let1, [SCOL1, 10 * SCOL1, SCOL1 / 100], lambda v: f"{v:.3g} keV/µm",
        f"L<sub>∞</sub> = S<sub>col</sub> = {SCOL1:.2f} MeV/cm, and 1 MeV/cm = 1000 keV / 10,000 µm = 0.1 keV/µm, so the LET is {q_let1:.3f} keV/µm. Reading MeV/cm as keV/µm gives a value 10 times too high.", lvl="Easy"),
    PR(STEM("A narrow beam of 10 MeV electrons enters water, where their CSDA range is about 5 cm.", [], "Why is the [[mean depth]] that the electrons reach shorter than 5 cm?"),
       "Multiple scattering bends their paths, and the CSDA range is a path length",
       ["Range straggling makes every electron stop short of its CSDA range", "The CSDA range is measured from the depth of maximum dose", "The CSDA range leaves out the energy lost in hard collisions"],
       "The CSDA range is the mean length of the path, and multiple scattering makes each path zigzag, so its deepest point lies short of its length. Straggling spreads the path lengths on both sides of the mean, the range is counted from the surface, and the total stopping power includes hard collisions.", lvl="Challenging"),
    PRM(STEM("A narrow electron beam passes through a thin foil.", [], "Which of these [[increase the mean square scattering angle]] of the electrons?"),
        ["A thicker foil of the same material", "A foil of higher atomic number with the same mass thickness", "A lower electron energy"],
        ["A higher electron energy", "A foil of lower atomic number with the same mass thickness", "A higher beam current"],
        "The mean square angle grows in proportion to the path length, falls as the energy rises, and per g/cm² rises about as Z. The beam current changes the number of electrons, not the angle each is deflected through.", lvl="Moderate"),
    PR(STEM("An α particle and a proton enter water with the same speed.", [], "How do the α particle's [[collision stopping power and range]] compare with the proton's?"),
       "4 times the stopping power, about the same range",
       ["4 times the stopping power, a quarter of the range", "2 times the stopping power, half the range", "The same stopping power, 4 times the range"],
       f"At a given speed S<sub>col</sub> ∝ z², so the α particle (z = 2) loses energy 4 times as fast. The range at a given speed scales as M/z²: ({MALPHA:.0f}/4) / {MP:.0f} = {r_ap:.3f} of the proton's. A quarter of the range would follow if the α particle had the proton's mass.", lvl="Challenging"),
    SORT(STEM("Several quantities describe how charged particles lose energy.", [], "Which [[definition]] belongs to each quantity?"),
         ["Mass collision stopping power", "Radiation yield", "Restricted collision stopping power L<sub>Δ</sub>", "CSDA range", "Critical energy"],
         [("Energy lost to atomic electrons per unit mass thickness", 0), ("Fraction of an electron's initial kinetic energy emitted as bremsstrahlung", 1),
          ("Part of the collision loss from energy transfers below a cutoff", 2), ("Mean path length when energy is lost continuously", 3), ("Energy at which collision and radiative losses are equal", 4)],
         "The collision stopping power is a rate of loss to atomic electrons, and the restricted one keeps only what stays near the track. The radiation yield and the CSDA range follow the electron over its whole slowing-down, and the critical energy compares the two kinds of loss at one energy.", lvl="Easy", mode="match", cap=1),
]

INLINE = {0: [1, 2, 3], 1: [5, 6], 2: [7, 8], 3: [9, 10]}       # questions on the last section, and the rest, form the practice set

TERMS = ["soft collision", "hard collision", "delta ray", "mass stopping power", "critical energy", "radiation yield", "restricted collision stopping power", "CSDA range"]

TAKE = [
    ["Soft collisions excite or ionize distant atoms; hard collisions release delta rays. Each kind carries roughly half the collision loss.",
     "S<sub>col</sub>/ρ follows Z/A and falls as I rises: about 2 MeV cm²/g for therapy electrons in water.",
     "Energy lost in a thin layer: ΔE = (S/ρ) × ρ × t."],
    ["S<sub>rad</sub>/S<sub>col</sub> ≈ Z T / 800 (approximate); E<sub>c</sub> ≈ 800/Z MeV: about 10 MeV in lead, of the order of 100 MeV in water.",
     "Shield β emitters with low-Z material first, then lead."],
    ["L<sub>Δ</sub> leaves out delta rays above Δ and bremsstrahlung; L<sub>∞</sub> = S<sub>col</sub>.",
     "1 keV/µm = 10 MeV/cm. Therapy electrons about 0.2 keV/µm; α particles about 100 keV/µm."],
    ["R<sub>CSDA</sub> = ∫ dT/(S/ρ): a mean path length in g/cm²; electron paths bend, so the depth reached is shorter.",
     "Mean square scattering angle grows with path length, falls with energy, and rises about as Z per g/cm²."],
    ["Heavy particles: S<sub>col</sub> ∝ z²/v², independent of mass at a given speed; range ∝ M/z².",
     "A positron annihilates, usually near rest, into two 511 keV photons."],
]
