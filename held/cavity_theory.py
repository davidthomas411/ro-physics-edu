from blocks import *
import math

# ---------------------------------------------------------------- relations used in this chapter
W_E = 33.97                                     # J/C, W_air/e for dry air
RHO_AIR_STP = 1.293                             # mg/cm³, dry air at 0 °C and 101.325 kPa


def rho_air(t_c, p_kpa):
    """Density of dry air (mg/cm³) at t_c °C and p_kpa, scaled from 1.293 mg/cm³ at 0 °C and 101.325 kPa."""
    return RHO_AIR_STP * 273.15 / (273.15 + t_c) * p_kpa / 101.325


def d_air(q_nc, m_mg):
    """Dose to the air of a cavity (Gy) from the fully corrected charge (nC) and the mass of air (mg): (Q/m) W/e."""
    return (q_nc * 1e-9) / (m_mg * 1e-6) * W_E


def sw_air_e(z, r50):
    """Water-to-air Spencer–Attix stopping-power ratio (Δ = 10 keV) at depth z (cm) in an electron beam of R50 (cm):
    the fit of Burns, Ding, and Rogers (1996), for 1 ≤ R50 ≤ 19 cm and 0.02 ≤ z/R50 ≤ 1.2."""
    x, y = math.log(r50), z / r50
    return (1.0752 - 0.50867 * x + 0.08867 * x * x - 0.08402 * y) / (1 - 0.42806 * x + 0.06463 * x * x + 0.003085 * x ** 3 - 0.12460 * y)


# electron collision stopping power, Rohrlich–Carlson form of the Bethe formula (ICRU 37) without the density effect,
# which is negligible below about 0.5 MeV in water and air; used here for electrons of tens of keV only
MEC2 = 0.51099895                                                   # MeV
K_COL = 2 * math.pi * 2.8179403262e-13 ** 2 * MEC2 * 6.02214076e23  # MeV cm² mol⁻¹
AIR = (0.49919, 85.7e-6)                                            # Z/A (mol/g) and mean excitation energy I (MeV)
WATER = (0.55509, 75.0e-6)


def s_col(t, mat):
    """Mass collision stopping power (MeV cm²/g) of an electron of kinetic energy t (MeV)."""
    za, i = mat; tau = t / MEC2; g = 1 + tau; b2 = 1 - 1 / g ** 2; ii = i / MEC2
    f = 1 - b2 + (tau * tau / 8 - (2 * tau + 1) * math.log(2)) / g ** 2
    return K_COL * za / b2 * (math.log(tau * tau * (tau + 2) / (2 * ii * ii)) + f)


def csda(t, mat, t0=0.001, n=2000):
    """CSDA range (g/cm²): Simpson's rule for the integral of 1/S in ln T from t0 to t, plus t0/S(t0)/(1 + p) below t0, where S ∝ T^−p near t0."""
    a, b = math.log(t0), math.log(t); h = (b - a) / n
    tot = sum((1 if k in (0, n) else 4 if k % 2 else 2) * math.exp(a + k * h) / s_col(math.exp(a + k * h), mat) for k in range(n + 1)) * h / 3
    p = -math.log(s_col(1.1 * t0, mat) / s_col(t0, mat)) / math.log(1.1)
    return tot + t0 / s_col(t0, mat) / (1 + p)




# ---------------------------------------------------------------- worked example: dose to water from a cavity reading (Co-60)
Q1, M1, S_CO = 20.00, 0.718, 1.133                       # nC, mg of air, Spencer–Attix water-to-air ratio in Co-60
DA1 = d_air(Q1, M1)
DW1 = DA1 * S_CO

# ---------------------------------------------------------------- worked example: the two limits for an air cavity in Co-60
MEN_W, MEN_AIR = 0.02965, 0.02666                        # cm²/g at 1.25 MeV (NIST)
LARGE3 = round(MEN_W / MEN_AIR, 3)                       # printed to three decimals, 1.112
LOW3 = 100 * (1 - LARGE3 / S_CO)                         # % by which the large-cavity ratio falls below the Spencer–Attix ratio

# ---------------------------------------------------------------- water-to-air ratio in an electron beam with R50 = 5.0 cm
R50A = 5.0
S_SURF, S_REF, S_R50 = sw_air_e(0.02 * R50A, R50A), sw_air_e(0.6 * R50A - 0.1, R50A), sw_air_e(R50A, R50A)
Z4A, Z4B, M4B = 3.0, 4.5, 0.600
S4A, S4B = round(sw_air_e(Z4A, R50A), 3), round(sw_air_e(Z4B, R50A), 3)
DR4 = M4B * S4B / S4A
UP4 = 100 * (S4B / S4A - 1)

TOPIC = dict(
    id="cavity-theory", domain=2, sub="II.A", title="Cavity theory and stopping-power ratios",
    ref=dict(aapm="TG-21, TG-51", khan="", ford="7"),
    guide=[
        H("Bragg–Gray cavities"),
        P("A detector records the dose to its own sensitive material: the air of an ion chamber, the silicon of a diode, the lithium fluoride of a TLD. Cavity theory converts it into the dose to the medium at that point without the detector. For the air of a chamber:"),
        EQ("D<sub>air</sub> = (Q / m<sub>air</sub>) × (W<sub>air</sub>/e)",
           "Q = fully corrected charge,   m<sub>air</sub> = mass of air in the cavity,   W<sub>air</sub>/e = 33.97 J/C (dry air)"),
        P("The mass collision stopping power S<sub>col</sub>/ρ is the energy an electron loses per unit path length in collisions with atomic electrons, divided by the density. The Bragg–Gray conditions are:"),
        UL("the cavity is small compared with the ranges of the electrons that cross it, so it leaves their fluence unchanged;",
           "its dose comes from electrons set in motion in the medium around it, not from photons interacting in the gas."),
        P("No charged-particle equilibrium is needed, so the relation holds in electron and photon beams alike."),
        EQ("D<sub>med</sub> = D<sub>gas</sub> × s<sub>med,gas</sub>",
           "s<sub>med,gas</sub> = (S̄<sub>col</sub>/ρ)<sub>med</sub> / (S̄<sub>col</sub>/ρ)<sub>gas</sub>, each averaged over the electron fluence spectrum at the point"),
        EX("Dose to water from a cavity reading",
           STEM("An air cavity in water is treated as a Bragg–Gray cavity in a Co-60 beam, with every perturbation factor equal to 1.",
                [f"fully corrected charge Q = {Q1:.2f} nC", f"mass of air in the cavity = {M1:.3f} mg", f"W<sub>air</sub>/e = {W_E} J/C", f"s<sub>w,air</sub> = {S_CO:.3f} (Spencer–Attix, Δ = 10 keV)"],
                "Find the [[dose to air]] and the [[dose to water]]."),
           [f"D<sub>air</sub> = ({sci(Q1 * 1e-9, 3)} C / {sci(M1 * 1e-6, 3)} kg) × {W_E} J/C = {DA1:.4f} Gy",
            f"D<sub>w</sub> = {DA1:.4f} × {S_CO:.3f} = {DW1:.4f} Gy"],
           f"{DA1:.3f} Gy to the air and {DW1:.3f} Gy to water, {100 * (S_CO - 1):.0f}% more, because water takes more energy per gram from the same electron fluence."),

        H("Delta rays and Spencer–Attix theory"),
        P("Bragg–Gray theory treats all energy lost in the cavity as deposited there, but some collisions launch delta rays, electrons energetic enough to leave the cavity or to enter it from the medium."),
        P("Spencer and Attix divide the electrons at a cutoff energy Δ, the energy of an electron whose range equals the size of the cavity, usually its mean chord length. The restricted collision stopping power L<sub>Δ</sub>/ρ, the part of the collision stopping power from energy transfers below Δ, counts the energy that stays near each track, and a track-end term adds the energy of electrons that slow below Δ. The ratio depends only weakly on Δ, and TG-51 and TRS-398 use Δ = 10 keV for every chamber."),

        H("Chamber perturbation factors"),
        P("Four factors close to 1 correct a real chamber:"),
        UL("P<sub>wall</sub>: the wall is not water, and in a photon beam some electrons crossing the cavity start in it.",
           "P<sub>cel</sub>: an aluminium central electrode raises the reading slightly.",
           "P<sub>fl</sub>, the fluence perturbation: in an electron beam more electrons scatter into the low-density cavity than out of it, so P<sub>fl</sub> is below 1, more so at low energy and for a wide cavity; near 1 in photon beams and for a well-guarded plane-parallel chamber.",
           "P<sub>dis</sub> (P<sub>gr</sub> in TG-51): the cavity displaces water, so in a dose gradient its reading belongs to a point upstream of its center."),
        P("In practice a Co-60 calibration coefficient replaces m<sub>air</sub>, and k<sub>Q</sub> carries the ratio and the perturbation factors to the user's beam; W<sub>air</sub>/e is constant with energy and cancels."),
        EQ("k<sub>Q</sub> = [s<sub>w,air</sub> P<sub>wall</sub> P<sub>fl</sub> P<sub>gr</sub> P<sub>cel</sub>]<sub>Q</sub> / [s<sub>w,air</sub> P<sub>wall</sub> P<sub>fl</sub> P<sub>gr</sub> P<sub>cel</sub>]<sub>Co-60</sub>   (TG-51)"),

        H("Water-to-air ratios in clinical beams"),
        P(f"The density effect lowers the stopping power of condensed water at high electron energies, so the water-to-air ratio falls as electron energy rises. A photon beam sets electrons in motion at every depth, so beyond the build-up region the ratio changes little with depth; it falls slowly with photon energy, from about 1.13 in Co-60 to about 1.10 at 18 MV. In an electron beam the electrons slow down with depth and the ratio rises: for R<sub>50</sub> = {R50A:.1f} cm, from about {S_SURF:.2f} near the surface to {S_REF:.2f} at d<sub>ref</sub> and {S_R50:.2f} at R<sub>50</sub> (fit of Burns et al., 1996)."),
        P("TG-51 takes the ratio at d<sub>ref</sub> into k<sub>ecal</sub> and k′<sub>R50</sub>. At other depths each reading of a depth-ionization curve is multiplied by the ratio at its depth, and for a cylindrical chamber by P<sub>fl</sub>, to give a depth-dose curve."),
        EX("Dose ratio between two depths in an electron beam",
           STEM(f"A well-guarded plane-parallel chamber reads on the axis of an electron beam with R<sub>50</sub> = {R50A:.1f} cm. Perturbation factors are taken as equal at both depths.",
                [f"reading at {Z4A:.1f} cm = 1.000 (relative)", f"reading at {Z4B:.1f} cm = {M4B:.3f}", f"s<sub>w,air</sub> at {Z4A:.1f} cm = {S4A:.3f}", f"s<sub>w,air</sub> at {Z4B:.1f} cm = {S4B:.3f}"],
                f"Find the [[dose at {Z4B:.1f} cm relative to the dose at {Z4A:.1f} cm]]."),
           [f"D({Z4B:.1f}) / D({Z4A:.1f}) = {M4B:.3f} × {S4B:.3f} / {S4A:.3f} = {DR4:.3f}"],
           f"{DR4:.3f}, {UP4:.1f}% above the ratio of the readings. The uncorrected ionization curve understates the relative dose at depth."),

        H("Large cavities and solid detectors"),
        P("A cavity much larger than the ranges of the electrons set in motion in it reaches charged-particle equilibrium within itself; its dose is the collision kerma of its own material, and the ratio of mass energy-absorption coefficients converts it. Burlin's general cavity theory weights the two limits by d, the fraction of the cavity dose from electrons entering from the medium: 1 for a small cavity, toward 0 for a large one."),
        EQ("Large cavity:   D<sub>med</sub> / D<sub>cav</sub> = (μ̄<sub>en</sub>/ρ)<sub>med</sub> / (μ̄<sub>en</sub>/ρ)<sub>cav</sub>",
           "Burlin:   D<sub>cav</sub> / D<sub>med</sub> = d s<sub>cav,med</sub> + (1 − d) (μ̄<sub>en</sub>/ρ)<sub>cav,med</sub>"),
        EX("Two limits for an air cavity in Co-60",
           STEM("An air cavity in water in a Co-60 beam is compared under the two limits of cavity theory.",
                [f"μ<sub>en</sub>/ρ at 1.25 MeV: water {MEN_W:.5f} cm²/g,   air {MEN_AIR:.5f} cm²/g (NIST)", f"s<sub>w,air</sub> = {S_CO:.3f} (Spencer–Attix, Δ = 10 keV)"],
                "Find the [[large-cavity ratio]] and how far it falls [[below the Spencer–Attix ratio]]."),
           [f"Large cavity: {MEN_W:.5f} / {MEN_AIR:.5f} = {LARGE3:.3f}", f"1 − {LARGE3:.3f} / {S_CO:.3f} = {LOW3 / 100:.4f}"],
           f"{LARGE3:.3f}, {LOW3:.1f}% below {S_CO:.3f}. The secondary electrons of Co-60 travel metres in air, so the cavity is small and the Spencer–Attix ratio applies."),
        UL("Ion chamber in a megavoltage beam: a small cavity, converted by the Spencer–Attix ratio.",
           "Diode: a small cavity in an electron beam, converted by the water-to-silicon stopping-power ratio (about 1.2), which changes less with depth than the water-to-air ratio. In photon beams it over-responds to low-energy scatter, which silicon absorbs far more than water.",
           "TLD: a LiF chip about 1 mm thick is an intermediate cavity in megavoltage beams and nearly a large one at low photon energies, such as those of I-125; it is calibrated in a similar beam."),
    ],
    cards=[
        F("Cavity theory", "Converts the dose to a detector's sensitive material, the cavity, into the dose the surrounding medium would receive at that point without the detector."),
        F("Bragg–Gray conditions", ["The cavity is small against the ranges of the electrons crossing it, and it leaves their fluence unchanged.", "Its dose comes from electrons set in motion in the medium; photon interactions in the cavity are negligible."]),
        F("Bragg–Gray relation", "D<sub>med</sub> = D<sub>gas</sub> × (S̄<sub>col</sub>/ρ)<sub>med</sub> / (S̄<sub>col</sub>/ρ)<sub>gas</sub>, the mass collision stopping powers averaged over the electron spectrum. No charged-particle equilibrium is needed."),
        F("Chamber perturbation factors", ["P<sub>wall</sub>: a wall that is not water.", "P<sub>cel</sub>: the central electrode.", "P<sub>fl</sub>: electrons scattered into the cavity in electron beams; below 1.", "P<sub>dis</sub> (TG-51 P<sub>gr</sub>): water displaced in a dose gradient."]),
    ],
)

# ---------------------------------------------------------------- numbers behind the questions
R50B = 3.0
Z10A, Z10B, M10B = 0.6 * R50B - 0.1, 2.7, 0.550
S10A, S10B = round(sw_air_e(Z10A, R50B), 3), round(sw_air_e(Z10B, R50B), 3)
DR10 = M10B * S10B / S10A
R125_UM = csda(0.0355, WATER) * 1e4                     # µm in water (density 1 g/cm³) for the 35.5 keV gamma ray
R125_BOUND = 10 * math.ceil(R125_UM / 10)               # printed bound: less than 30 µm
DA17 = 0.950
LARGE17 = LARGE3
DW17 = DA17 * S_CO
DW17_large, DW17_inv, DW17_linv = DA17 * LARGE17, DA17 / S_CO, DA17 / LARGE17

PROBLEMS = [
    # ---- Bragg–Gray cavities
    PR(STEM("An air cavity in a water phantom is to be treated as a Bragg–Gray cavity in a 6 MV beam.", [], "Which [[condition]] must the cavity meet?"),
       "It is small against the electron ranges, so it leaves their fluence unchanged",
       ["It is large enough for charged-particle equilibrium to form in its air", "Its wall stops every electron that enters it from the water", "Its gas has the same density as the water around it"],
       "A Bragg–Gray cavity samples the electron fluence of the medium without changing it, and its dose comes from electrons set in motion outside it. Equilibrium inside the gas describes the opposite, large-cavity limit; a wall that stopped the electrons from the water would itself become the medium; and the gas need not match the water, which is why a stopping-power ratio is applied.", lvl="Easy"),
    PR(STEM("A Bragg–Gray air cavity sits in water in an electron beam.", [], "Which [[ratio]] converts the dose to the air into the dose to water?"),
       "Mass collision stopping powers, water to air, averaged over the electron spectrum",
       ["Mass energy-absorption coefficients, water to air, averaged over the photon spectrum", "Mass attenuation coefficients, water to air, at the mean photon energy", "Densities, water to air, at the temperature of the cavity"],
       "The same electron fluence crosses the cavity and the water, and each material absorbs energy from it in proportion to its collision stopping power. The ratio of energy-absorption coefficients belongs to a cavity large enough for charged-particle equilibrium, and in an electron beam the dose comes from the electrons, not from photons interacting in the cavity.", lvl="Easy"),

    # ---- delta rays and Spencer–Attix theory

    # ---- chamber perturbation factors
    SORT(STEM("Four factors correct an ion chamber's reading for the ways it departs from a Bragg–Gray cavity.", [], "What does each [[factor]] correct for?"),
         ["P<sub>wall</sub>", "P<sub>cel</sub>", "P<sub>fl</sub>", "P<sub>dis</sub> (P<sub>gr</sub> in TG-51)"],
         [("A wall made of a material other than water", 0), ("An aluminium electrode on the axis of the cavity", 1), ("Electrons scattered into the low-density cavity", 2), ("Water displaced by the cavity in a dose gradient", 3)],
         "P<sub>wall</sub> allows for electrons that start in the wall, P<sub>cel</sub> for the extra signal from the electrode, P<sub>fl</sub> for in-scatter into the air in electron beams, and P<sub>dis</sub> for the shift of the reading to a point upstream of the cavity center.", lvl="Easy", mode="match", cap=1),

    # ---- water-to-air ratios in clinical beams

    # ---- large cavities and solid detectors
]

INLINE = {0: [1, 2], 2: [3]}

TERMS = ["cavity theory", "mass collision stopping power", "Bragg–Gray conditions", "delta rays", "restricted collision stopping power", "fluence perturbation", "general cavity theory"]

TAKE = [
    ["Bragg–Gray: D<sub>med</sub> = D<sub>gas</sub> × (S̄<sub>col</sub>/ρ)<sub>med</sub> / (S̄<sub>col</sub>/ρ)<sub>gas</sub>, for a cavity too small to change the electron fluence and dosed only by electrons from the medium.",
     "D<sub>air</sub> = (Q / m<sub>air</sub>)(W<sub>air</sub>/e). No charged-particle equilibrium is needed."],
    ["Spencer–Attix adds delta rays: the restricted stopping power L<sub>Δ</sub>/ρ for electrons above Δ, plus a track-end term for those that slow below it.",
     "Δ is the energy of an electron whose range spans the cavity; TG-51 and TRS-398 use 10 keV."],
    ["P<sub>wall</sub>: wall material. P<sub>cel</sub>: central electrode. P<sub>fl</sub>: in-scatter in electron beams, below 1. P<sub>dis</sub> (TG-51 P<sub>gr</sub>): displaced water in a gradient.",
     "TG-51: k<sub>Q</sub> is the ratio of s<sub>w,air</sub> × perturbation factors in the beam and in Co-60; W<sub>air</sub>/e is constant and cancels."],
    ["Water-to-air ratio: about 1.13 in Co-60 to 1.10 at 18 MV, nearly constant with depth in a photon beam.",
     f"In an electron beam it rises with depth (R<sub>50</sub> = {R50A:.0f} cm: about {S_SURF:.2f} to {S_R50:.2f}), so a depth-ionization curve is converted depth by depth."],
    ["Large cavity: D<sub>med</sub> / D<sub>cav</sub> = ratio of μ̄<sub>en</sub>/ρ. Burlin weights the two limits by d, from 1 (small) to 0 (large).",
     "Chamber: Spencer–Attix. Diode: water-to-silicon ratio in electron beams, over-response to low-energy photons. TLD: intermediate in megavoltage beams, near the large-cavity limit at low energy."],
]
