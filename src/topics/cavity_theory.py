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


def chord_cyl(r, l):
    """Mean chord length 4V/S of a right circular cylinder of radius r and length l (same unit)."""
    return 4 * (math.pi * r * r * l) / (2 * math.pi * r * l + 2 * math.pi * r * r)


def lin(x, x0, x1, y0, y1):
    """Straight-line interpolation of y at x between (x0, y0) and (x1, y1)."""
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def sw_air_e(z, r50):
    """Water-to-air Spencer–Attix stopping-power ratio (Δ = 10 keV) at depth z (cm) in an electron beam of R50 (cm):
    the fit of Burns, Ding, and Rogers (1996), for 1 ≤ R50 ≤ 19 cm and 0.02 ≤ z/R50 ≤ 1.2."""
    x, y = math.log(r50), z / r50
    return (1.0752 - 0.50867 * x + 0.08867 * x * x - 0.08402 * y) / (1 - 0.42806 * x + 0.06463 * x * x + 0.003085 * x ** 3 - 0.12460 * y)


def burlin(d, s_cav_med, men_cav_med):
    """Burlin's general cavity theory: D_cav / D_med = d s + (1 − d) (μen/ρ ratio), cavity to medium."""
    return d * s_cav_med + (1 - d) * men_cav_med


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


def two_fig(v): return float(f"{v:.2g}")


def sci2(v):
    """2.9e-4 -> '2.9 × 10<sup>−4</sup>'."""
    return sci(v, 2)


# ---------------------------------------------------------------- worked example: dose to water from a cavity reading (Co-60)
RHO22 = round(rho_air(22.0, 101.33), 3)                  # 1.197 mg/cm³
V1, Q1, S_CO = 0.6000, 20.00, 1.133                      # cm³, nC, Spencer–Attix water-to-air ratio in Co-60
M1 = V1 * RHO22                                          # mg
QM1 = Q1 * 1e-9 / (M1 * 1e-6)                            # C/kg
DA1 = d_air(Q1, M1)
DW1 = DA1 * S_CO

# ---------------------------------------------------------------- worked example: cutoff energy of a Farmer-type cavity
R_FARMER, L_FARMER = 3.1, 23.0                           # mm
RANGE_AIR = {e: two_fig(csda(e / 1000, AIR)) for e in (10, 15, 20)}     # keV -> CSDA range in air (g/cm²), two figures
CH2 = chord_cyl(R_FARMER, L_FARMER)                      # mm
T2 = CH2 / 10 * RHO22 * 1e-3                             # g/cm²
DELTA2 = lin(T2, RANGE_AIR[15], RANGE_AIR[20], 15, 20)  # keV
assert RANGE_AIR[15] <= T2 <= RANGE_AIR[20]

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
        P("A detector records the dose to its own sensitive material: the air of an ion chamber, the silicon of a diode, the lithium fluoride of a TLD. Cavity theory converts it into the dose the medium would receive at that point without the detector. For the air of a chamber:"),
        EQ("D<sub>air</sub> = (Q / m<sub>air</sub>) × (W<sub>air</sub>/e)",
           "Q = fully corrected charge,   m<sub>air</sub> = mass of air in the cavity,   W<sub>air</sub>/e = 33.97 J/C (dry air)"),
        P("The mass collision stopping power S<sub>col</sub>/ρ is the energy an electron loses per unit path length in collisions with atomic electrons, divided by the density (MeV cm²/g). The Bragg–Gray conditions are:"),
        UL("the cavity is small compared with the ranges of the electrons that cross it;",
           "its dose comes from electrons set in motion in the medium around it, not from photons interacting in the gas;",
           "it leaves the number, energy, and direction of those electrons unchanged."),
        P("The same fluence deposits energy in each material in proportion to its stopping power. No charged-particle equilibrium is needed, so the relation holds in electron beams as well as photon beams."),
        EQ("D<sub>med</sub> = D<sub>gas</sub> × s<sub>med,gas</sub>",
           "s<sub>med,gas</sub> = (S̄<sub>col</sub>/ρ)<sub>med</sub> / (S̄<sub>col</sub>/ρ)<sub>gas</sub>, each averaged over the electron fluence spectrum at the point"),
        EX("Dose to water from a cavity reading",
           STEM("An air cavity of known volume in water is treated as a Bragg–Gray cavity in a Co-60 beam, with every perturbation factor equal to 1.",
                [f"fully corrected charge Q = {Q1:.2f} nC", f"cavity volume = {V1:.4f} cm³", f"air density in the cavity = {RHO22:.3f} mg/cm³ (22 °C, 101.33 kPa)", f"W<sub>air</sub>/e = {W_E} J/C", f"s<sub>w,air</sub> = {S_CO:.3f} (Spencer–Attix, Δ = 10 keV)"],
                "Find the [[dose to air]] and the [[dose to water]]."),
           [f"m<sub>air</sub> = {V1:.4f} cm³ × {RHO22:.3f} mg/cm³ = {M1:.4f} mg = {sci(M1 * 1e-6, 4)} kg",
            f"Q / m<sub>air</sub> = {sci(Q1 * 1e-9, 4)} C / {sci(M1 * 1e-6, 4)} kg = {sci(QM1, 4)} C/kg",
            f"D<sub>air</sub> = {sci(QM1, 4)} C/kg × {W_E} J/C = {DA1:.4f} Gy",
            f"D<sub>w</sub> = {DA1:.4f} × {S_CO:.3f} = {DW1:.4f} Gy"],
           f"{DA1:.3f} Gy to the air and {DW1:.3f} Gy to water, {100 * (S_CO - 1):.0f}% more, because water takes more energy per gram from the same electron fluence."),

        H("Delta rays and Spencer–Attix theory"),
        P("Bragg–Gray theory treats all the energy an electron loses in the cavity as deposited there. Some collisions launch delta rays, atomic electrons with enough energy to leave the cavity, while delta rays made in the medium enter it."),
        P("Spencer and Attix divide the electrons at a cutoff energy Δ, the energy of an electron whose range equals the mean chord length of the cavity, 4V/S for a convex cavity of volume V and surface area S. Electrons above Δ, delta rays included, form the fluence that crosses the cavity. The restricted collision stopping power L<sub>Δ</sub>/ρ, the part of the collision stopping power from energy transfers below Δ, counts the energy that stays near each track. Electrons that slow below Δ deposit their remaining energy on the spot, and the track-end term adds it."),
        EQ("s<sub>med,gas</sub> = [∫<sub>Δ</sub><sup>T<sub>max</sub></sup> Φ<sub>T</sub> (L<sub>Δ</sub>/ρ)<sub>med</sub> dT + TE<sub>med</sub>] / [∫<sub>Δ</sub><sup>T<sub>max</sub></sup> Φ<sub>T</sub> (L<sub>Δ</sub>/ρ)<sub>gas</sub> dT + TE<sub>gas</sub>]",
           "Φ<sub>T</sub> = fluence spectrum of all electrons in the medium, delta rays included,   TE = Φ<sub>T</sub>(Δ) (S<sub>col</sub>(Δ)/ρ) Δ"),
        P("The ratio depends only weakly on Δ, and TG-51 and TRS-398 use Spencer–Attix ratios with Δ = 10 keV for every chamber."),
        EX("Cutoff energy of a Farmer-type cavity",
           STEM("The air cavity of a Farmer-type chamber is a cylinder.",
                [f"radius = {R_FARMER:.1f} mm,   length = {L_FARMER:.0f} mm", f"air density = {RHO22:.3f} mg/cm³",
                 "CSDA range in air: " + ";   ".join(f"{e} keV, {sci2(RANGE_AIR[e])} g/cm²" for e in (10, 15, 20))],
                "Find the [[mean chord length]] and the [[cutoff energy Δ]]."),
           [f"4V/S = 2rL / (r + L) = 2 × {R_FARMER:.1f} × {L_FARMER:.0f} / {R_FARMER + L_FARMER:.1f} = {CH2:.2f} mm",
            f"Mass thickness = {CH2 / 10:.3f} cm × {sci(RHO22 * 1e-3, 4)} g/cm³ = {sci(T2, 3)} g/cm²",
            f"It lies between the ranges at 15 and 20 keV: Δ = 15 + 5 × ({T2 * 1e4:.2f} − {RANGE_AIR[15] * 1e4:.1f}) / ({RANGE_AIR[20] * 1e4:.1f} − {RANGE_AIR[15] * 1e4:.1f}) = {DELTA2:.1f} keV"],
           f"A mean chord length of {CH2:.2f} mm and Δ of about {DELTA2:.0f} keV. TG-51 and TRS-398 still use 10 keV, since the ratio changes little with Δ."),

        H("Chamber perturbation factors"),
        P("A real chamber departs from a Bragg–Gray cavity in four ways, each corrected by a factor close to 1:"),
        UL("P<sub>wall</sub>: the wall is not water, and in a photon beam some electrons crossing the cavity start in it; of the order of 1% in Co-60, less at higher energies.",
           "P<sub>cel</sub>: an aluminium central electrode raises the reading, by under 1% for a diameter of 1 mm.",
           "P<sub>fl</sub>, the fluence perturbation: in an electron beam more electrons scatter into the low-density cavity than out of it, so P<sub>fl</sub> is below 1, more so at lower energy and for a wider cavity; close to 1 in photon beams beyond the build-up region and for a well-guarded plane-parallel chamber.",
           "P<sub>dis</sub> (P<sub>gr</sub> in TG-51): the cavity displaces water, so in a dose gradient its reading belongs to a point upstream of its center."),
        P("A field chamber's air mass is not known closely enough for this relation, so a Co-60 calibration coefficient replaces it, and the TG-51 factor k<sub>Q</sub> carries the ratio and the perturbation factors to the user's beam. W<sub>air</sub>/e is taken as constant with energy and cancels."),
        EQ("D<sub>w</sub> = (Q / m<sub>air</sub>) (W<sub>air</sub>/e) s<sub>w,air</sub> P<sub>wall</sub> P<sub>cel</sub> P<sub>fl</sub> P<sub>dis</sub>",
           "k<sub>Q</sub> = [s<sub>w,air</sub> P<sub>wall</sub> P<sub>fl</sub> P<sub>gr</sub> P<sub>cel</sub>]<sub>Q</sub> / [s<sub>w,air</sub> P<sub>wall</sub> P<sub>fl</sub> P<sub>gr</sub> P<sub>cel</sub>]<sub>Co-60</sub>   (TG-51)"),

        H("Water-to-air ratios in clinical beams"),
        P("For electrons of one energy the water-to-air ratio is about 1.13 to 1.14 up to a few hundred keV. At higher energies the polarization of condensed water, the density effect, lowers its stopping power relative to the gas, and the ratio falls to about 1 near 10 MeV."),
        P(f"A photon beam sets electrons in motion at every depth, so beyond the build-up region the electron spectrum and the ratio change little with depth; the ratio falls slowly with photon energy, from about 1.13 in Co-60 to about 1.10 at 18 MV. In an electron beam the electrons slow down with depth and the ratio rises: for R<sub>50</sub> = {R50A:.1f} cm (about 12 MeV), from about {S_SURF:.2f} near the surface to {S_REF:.2f} at d<sub>ref</sub> and {S_R50:.2f} at R<sub>50</sub> (fit of Burns et al., 1996)."),
        P("TG-51 takes the ratio at d<sub>ref</sub> into k<sub>ecal</sub> and k′<sub>R50</sub>, and P<sub>gr</sub>, measured in each beam, corrects for the gradient across the cavity. At other depths each reading of a depth-ionization curve is multiplied by the ratio at its depth, and for a cylindrical chamber by P<sub>fl</sub>, to give a depth-dose curve."),
        EQ("D<sub>w</sub>(z<sub>2</sub>) / D<sub>w</sub>(z<sub>1</sub>) = [M(z<sub>2</sub>) / M(z<sub>1</sub>)] × [s<sub>w,air</sub>(z<sub>2</sub>) / s<sub>w,air</sub>(z<sub>1</sub>)]   (perturbation factors equal at both depths)"),
        EX("Dose ratio between two depths in an electron beam",
           STEM(f"A well-guarded plane-parallel chamber reads on the axis of an electron beam with R<sub>50</sub> = {R50A:.1f} cm. Perturbation factors are taken as equal at both depths.",
                [f"reading at {Z4A:.1f} cm = 1.000 (relative)", f"reading at {Z4B:.1f} cm = {M4B:.3f}", f"s<sub>w,air</sub> at {Z4A:.1f} cm = {S4A:.3f}", f"s<sub>w,air</sub> at {Z4B:.1f} cm = {S4B:.3f}"],
                f"Find the [[dose at {Z4B:.1f} cm relative to the dose at {Z4A:.1f} cm]]."),
           [f"D({Z4B:.1f}) / D({Z4A:.1f}) = {M4B:.3f} × {S4B:.3f} / {S4A:.3f}", f"= {M4B:.3f} × {S4B / S4A:.4f} = {DR4:.3f}"],
           f"{DR4:.3f}, {UP4:.1f}% above the ratio of the readings. The uncorrected ionization curve understates the relative dose at depth."),

        H("Large cavities and solid detectors"),
        P("A cavity much larger than the ranges of the electrons set in motion in it reaches charged-particle equilibrium within itself; its dose is then the collision kerma of its own material, and the ratio of mass energy-absorption coefficients converts it. Burlin's general cavity theory weights the two limits by d, the fraction of the cavity dose from electrons entering from the medium: 1 for a small cavity, toward 0 for a large one."),
        EQ("Large cavity:   D<sub>med</sub> / D<sub>cav</sub> = (μ̄<sub>en</sub>/ρ)<sub>med</sub> / (μ̄<sub>en</sub>/ρ)<sub>cav</sub>",
           "Burlin:   D<sub>cav</sub> / D<sub>med</sub> = d s<sub>cav,med</sub> + (1 − d) (μ̄<sub>en</sub>/ρ)<sub>cav,med</sub>"),
        EX("Two limits for an air cavity in Co-60",
           STEM("An air cavity in water in a Co-60 beam is compared under the two limits of cavity theory.",
                [f"μ<sub>en</sub>/ρ at 1.25 MeV: water {MEN_W:.5f} cm²/g,   air {MEN_AIR:.5f} cm²/g (NIST)", f"s<sub>w,air</sub> = {S_CO:.3f} (Spencer–Attix, Δ = 10 keV)"],
                "Find the [[large-cavity ratio]] and how far it falls [[below the Spencer–Attix ratio]]."),
           [f"Large cavity: {MEN_W:.5f} / {MEN_AIR:.5f} = {LARGE3:.3f}", f"1 − {LARGE3:.3f} / {S_CO:.3f} = {LOW3 / 100:.4f}"],
           f"{LARGE3:.3f}, {LOW3:.1f}% below {S_CO:.3f}. The secondary electrons of Co-60 travel metres in air, so the cavity is small and the Spencer–Attix ratio applies; the large-cavity ratio would understate the dose to water by {LOW3:.1f}%."),
        P("Detectors sit at different places between the limits:"),
        UL("Ion chamber in a megavoltage beam: millimetres of air, small against the electron ranges, so the Spencer–Attix ratio and the perturbation factors apply.",
           "Diode: a small cavity in an electron beam, converted by the water-to-silicon stopping-power ratio (about 1.2), which changes less with depth than the water-to-air ratio. In a photon beam low-energy scatter interacts in the silicon itself, whose μ<sub>en</sub>/ρ far exceeds that of water at low energy.",
           "TLD: a LiF chip about 1 mm thick is an intermediate cavity in megavoltage beams and nearly a large one at low photon energies, such as those of I-125, where the μ<sub>en</sub>/ρ ratio applies; it is calibrated in a beam of similar quality or corrected for the difference."),
    ],
    cards=[
        F("Cavity theory", "Converts the dose to a detector's sensitive material, the cavity, into the dose the surrounding medium would receive at that point without the detector."),
        F("Mass collision stopping power", "The energy an electron loses per unit path length in collisions with atomic electrons, divided by the density of the material, in MeV cm²/g."),
        F("Bragg–Gray conditions", ["The cavity is small against the ranges of the electrons crossing it, and it leaves their fluence unchanged.", "Its dose comes from electrons set in motion in the medium; photon interactions in the cavity are negligible."]),
        F("Bragg–Gray relation", "D<sub>med</sub> = D<sub>gas</sub> × (S̄<sub>col</sub>/ρ)<sub>med</sub> / (S̄<sub>col</sub>/ρ)<sub>gas</sub>, the stopping powers averaged over the electron spectrum at the point. No charged-particle equilibrium is needed."),
        F("Delta rays in a cavity", "Energetic secondary electrons carry energy out of the cavity or in from the medium. Bragg–Gray theory, with the unrestricted stopping power of the primary electrons, leaves them out."),
        F("Restricted collision stopping power", "L<sub>Δ</sub>/ρ: the part of the collision stopping power from energy transfers below Δ, the energy that stays near the track."),
        F("Spencer–Attix cutoff Δ", f"The energy of an electron whose range equals the mean chord length 4V/S of the cavity: about {DELTA2:.0f} keV for a Farmer-type cavity. TG-51 and TRS-398 use 10 keV for every chamber.",
          w=[f"Mean chord of a {2 * R_FARMER:.1f} mm × {L_FARMER:.0f} mm cylinder = {CH2:.2f} mm, or {sci(T2, 2)} g/cm² of air", f"The CSDA range in air reaches that between 15 and 20 keV: Δ ≈ {DELTA2:.0f} keV"]),
        F("Track-end term", "The energy deposited on the spot by electrons that slow below Δ: Φ<sub>T</sub>(Δ) (S<sub>col</sub>(Δ)/ρ) Δ in each material."),
        F("Chamber perturbation factors", ["P<sub>wall</sub>: a wall that is not water.", "P<sub>cel</sub>: the central electrode.", "P<sub>fl</sub>: electrons scattered into the cavity in electron beams; below 1.", "P<sub>dis</sub> (TG-51 P<sub>gr</sub>): water displaced in a dose gradient."]),
        F("k<sub>Q</sub> from cavity theory", "k<sub>Q</sub> = [s<sub>w,air</sub> P<sub>wall</sub> P<sub>fl</sub> P<sub>gr</sub> P<sub>cel</sub>]<sub>Q</sub> / [s<sub>w,air</sub> P<sub>wall</sub> P<sub>fl</sub> P<sub>gr</sub> P<sub>cel</sub>]<sub>Co-60</sub> (TG-51). W<sub>air</sub>/e is constant and cancels."),
        F("Density effect on the water-to-air ratio", "Polarization of condensed water lowers its stopping power at high electron energies, so the ratio falls from about 1.13 up to a few hundred keV to about 1 near 10 MeV."),
        F("Water-to-air ratio in photon beams", "About 1.13 in Co-60, falling to about 1.10 at 18 MV; nearly constant with depth beyond the build-up region."),
        F("Water-to-air ratio in electron beams", f"Rises with depth as the electrons slow down. For R<sub>50</sub> = {R50A:.1f} cm: about {S_SURF:.2f} near the surface, {S_REF:.2f} at d<sub>ref</sub>, and {S_R50:.2f} at R<sub>50</sub>."),
        F("Large-cavity limit", f"For a cavity larger than the electron ranges, D<sub>med</sub> / D<sub>cav</sub> = (μ̄<sub>en</sub>/ρ)<sub>med</sub> / (μ̄<sub>en</sub>/ρ)<sub>cav</sub>. For water and air in Co-60 it is {LARGE3:.3f}, against the Spencer–Attix {S_CO:.3f}."),
        F("Burlin general cavity theory", "D<sub>cav</sub> / D<sub>med</sub> = d s<sub>cav,med</sub> + (1 − d) (μ̄<sub>en</sub>/ρ)<sub>cav,med</sub>, with d from 1 for a small cavity to 0 for a large one."),
        F("Conversion by detector", ["Ion chamber, megavoltage beam: Spencer–Attix water-to-air ratio and perturbation factors.", "Diode: water-to-silicon stopping-power ratio in electron beams; over-response to low-energy photons.", "TLD: intermediate cavity in megavoltage beams, near the large-cavity limit at low photon energies."]),
    ],
)

# ---------------------------------------------------------------- numbers behind the questions
# dose to water from a cavity reading in a 6 MV beam
Q7, S6 = 16.50, 1.119
M7 = V1 * RHO22
DA7 = d_air(Q7, M7)
DW7 = DA7 * S6
DW7_nos, DW7_div, DW7_now = DA7, DA7 / S6, (Q7 * 1e-9) / (M7 * 1e-6) * S6
# mean chord length (typed)
R5, L5 = 2.5, 7.0
CH5 = chord_cyl(R5, L5)
# depth ionization to depth dose, R50 = 3.0 cm
R50B = 3.0
Z10A, Z10B, M10B = 0.6 * R50B - 0.1, 2.7, 0.550
S10A, S10B = round(sw_air_e(Z10A, R50B), 3), round(sw_air_e(Z10B, R50B), 3)
DR10 = M10B * S10B / S10A
DR10_inv, DR10_one = M10B * S10A / S10B, M10B * S10B
# ranking of water-to-air ratios
R50C = 8.0
S9_SURF, S9_REF = sw_air_e(0.02 * R50C, R50C), sw_air_e(0.6 * R50C - 0.1, R50C)
# k_Q from the ratio of products (illustrative factors for one Farmer-type chamber)
KQ_CO = dict(s=1.133, wall=0.991, gr=0.992, cel=0.993, fl=1.000)
KQ_6 = dict(s=1.119, wall=0.996, gr=0.995, cel=0.993, fl=1.000)
prodf = lambda f: f["s"] * f["wall"] * f["gr"] * f["cel"] * f["fl"]
pf = lambda f: f["wall"] * f["gr"] * f["cel"] * f["fl"]
KQ21 = prodf(KQ_6) / prodf(KQ_CO)
KQ21_s, KQ21_inv, KQ21_p = KQ_6["s"] / KQ_CO["s"], prodf(KQ_CO) / prodf(KQ_6), pf(KQ_6) / pf(KQ_CO)
# electrons set in motion by I-125 photons
R125_UM = csda(0.0355, WATER) * 1e4                     # µm in water (density 1 g/cm³) for the 35.5 keV gamma ray
R125_BOUND = 10 * math.ceil(R125_UM / 10)               # printed bound: less than 30 µm
# the two limits for an air chamber in Co-60
DA17 = 0.950
LARGE17 = LARGE3
DW17 = DA17 * S_CO
DW17_large, DW17_inv, DW17_linv = DA17 * LARGE17, DA17 / S_CO, DA17 / LARGE17
# Burlin
D18, S18, MEN18, DCAV18 = 0.40, 0.85, 1.20, 2.120
B18 = burlin(D18, S18, MEN18)
DW18 = DCAV18 / B18
DW18_swap, DW18_large, DW18_mult = DCAV18 / burlin(1 - D18, S18, MEN18), DCAV18 / MEN18, DCAV18 * B18

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
    PRN(STEM("An air cavity of known volume in water is treated as a Bragg–Gray cavity in a 6 MV beam, with every perturbation factor equal to 1.",
             [f"fully corrected charge Q = {Q7:.2f} nC", f"cavity volume = {V1:.4f} cm³", f"air density in the cavity = {RHO22:.3f} mg/cm³", f"W<sub>air</sub>/e = {W_E} J/C", f"s<sub>w,air</sub> = {S6:.3f}"],
             "What is the [[dose to water]]?"),
        DW7, [DW7_nos, DW7_div, DW7_now], "{:.3f} Gy",
        f"m<sub>air</sub> = {V1:.4f} × {RHO22:.3f} = {M7:.4f} mg, so D<sub>air</sub> = ({Q7:.2f} × 10<sup>−9</sup> C / {sci(M7 * 1e-6, 4)} kg) × {W_E} J/C = {DA7:.4f} Gy, and D<sub>w</sub> = {DA7:.4f} × {S6:.3f} = {DW7:.3f} Gy. Stopping at the dose to air gives {DW7_nos:.3f}, dividing by the ratio gives {DW7_div:.3f}, and leaving out W<sub>air</sub>/e gives {DW7_now:.3f}, a charge per mass rather than a dose.",
        w=[f"m<sub>air</sub> = {V1:.4f} cm³ × {RHO22:.3f} mg/cm³ = {M7:.4f} mg", f"D<sub>air</sub> = {sci(Q7 * 1e-9 / (M7 * 1e-6), 4)} C/kg × {W_E} J/C = {DA7:.4f} Gy", f"D<sub>w</sub> = {DA7:.4f} × {S6:.3f} = {DW7:.4f} Gy"], lvl="Moderate"),

    # ---- delta rays and Spencer–Attix theory
    PR(STEM("Spencer–Attix theory divides the electrons crossing a cavity at a cutoff energy Δ.", [], "What sets the [[value of Δ]]?"),
       "The energy of an electron whose range equals the size of the cavity",
       ["The mean energy spent in the gas for each ion pair formed", "The mean energy of the photons in the incident beam", "The maximum energy of the electrons in the incident beam"],
       f"Δ is the energy of an electron whose range equals the mean chord length 4V/S of the cavity; for a Farmer-type cavity that is about {DELTA2:.0f} keV, and TG-51 and TRS-398 use 10 keV. The mean energy per ion pair is W<sub>air</sub>, about 34 eV, and the beam energies set the electron spectrum, not the cutoff.", lvl="Easy"),
    PRM(STEM("Spencer–Attix theory refines the Bragg–Gray relation for an ion chamber.", [], "Which of these does it [[add]]?"),
        ["Delta rays above the cutoff energy counted in the electron fluence", "A stopping power restricted to energy transfers below the cutoff", "A track-end term for electrons that slow below the cutoff"],
        ["Photon interactions in the air of the cavity", "The ratio of mass energy-absorption coefficients", "A correction for ions that recombine in the gas"],
        "Spencer and Attix follow every electron above Δ, delta rays included, count only energy transfers below Δ as deposited locally, and add the energy of electrons that fall below Δ. Photon interactions in the gas remain negligible, the energy-absorption ratio belongs to large cavities, and recombination is corrected by P<sub>ion</sub>.", lvl="Moderate"),
    TYPED(STEM("A small cylindrical air cavity is described by its mean chord length, 4V/S.", [f"radius = {R5:.1f} mm", f"length = {L5:.1f} mm"], "What is the [[mean chord length]]?"), CH5, 0.01, "mm",
          f"V = πr²L and S = 2πrL + 2πr², so 4V/S = 2rL / (r + L) = 2 × {R5:.1f} × {L5:.1f} / {R5 + L5:.1f} = {CH5:.2f} mm. Leaving out the two end faces gives 2r = {2 * R5:.1f} mm, outside the tolerance.",
          w=[f"V = π × {R5:.1f}² × {L5:.1f} = {math.pi * R5 * R5 * L5:.1f} mm³", f"S = 2π × {R5:.1f} × {L5:.1f} + 2π × {R5:.1f}² = {2 * math.pi * R5 * L5 + 2 * math.pi * R5 * R5:.1f} mm²", f"4V/S = 4 × {math.pi * R5 * R5 * L5:.1f} / {2 * math.pi * R5 * L5 + 2 * math.pi * R5 * R5:.1f} = {CH5:.2f} mm"], lvl="Moderate"),

    # ---- chamber perturbation factors
    SORT(STEM("Four factors correct an ion chamber's reading for the ways it departs from a Bragg–Gray cavity.", [], "What does each [[factor]] correct for?"),
         ["P<sub>wall</sub>", "P<sub>cel</sub>", "P<sub>fl</sub>", "P<sub>dis</sub> (P<sub>gr</sub> in TG-51)"],
         [("A wall made of a material other than water", 0), ("An aluminium electrode on the axis of the cavity", 1), ("Electrons scattered into the low-density cavity", 2), ("Water displaced by the cavity in a dose gradient", 3)],
         "P<sub>wall</sub> allows for electrons that start in the wall, P<sub>cel</sub> for the extra signal from the electrode, P<sub>fl</sub> for in-scatter into the air in electron beams, and P<sub>dis</sub> for the shift of the reading to a point upstream of the cavity center.", lvl="Easy", mode="match", cap=1),
    PR(STEM("A cylindrical chamber is read at d<sub>ref</sub> in a 6 MeV electron beam, and its fluence perturbation correction P<sub>fl</sub> is below 1.", [], "Why does the chamber [[read high]] without this correction?"),
       "More electrons scatter into the low-density cavity than out of it",
       ["Air scatters electrons more strongly than the water it replaces", "Electrons lose more energy per gram in air than in water", "The aluminium electrode adds electrons to the cavity"],
       "Water scatters electrons out of any small region as often as into it, but the air of the cavity scatters few out, so electrons scattered in from the surrounding water raise the fluence. Air scatters less than water, not more; at these energies an electron loses less energy per gram in air, which is why s<sub>w,air</sub> exceeds 1; and the electrode is corrected by P<sub>cel</sub>.", lvl="Moderate"),
    PR(STEM("TG-51 writes k<sub>Q</sub> as a ratio of stopping-power ratios and perturbation factors in the user's beam and in Co-60.", [], "What happens to [[W<sub>air</sub>/e]] in this ratio?"),
       "It cancels, because it is taken as constant over therapy electron energies",
       ["It is replaced by P<sub>TP</sub>, which corrects the mass of air", "It drops out, because it applies only to photons below 3 MeV", "It is folded into P<sub>ion</sub> for each beam"],
       f"W<sub>air</sub>/e, {W_E} J/C, is the same in Co-60 and in the user's beam, so it divides out of k<sub>Q</sub>. P<sub>TP</sub> corrects the mass of air for its temperature and pressure, the 3 MeV limit belongs to exposure, and P<sub>ion</sub> corrects recombination.", lvl="Easy"),
    PRM(STEM("The fluence perturbation correction P<sub>fl</sub> of an ion chamber depends on the conditions of the measurement.", [], "Which of these move P<sub>fl</sub> [[further from 1]]?"),
        ["A lower mean electron energy at the point of measurement", "A wider cylindrical cavity"],
        ["A photon beam, beyond the build-up region", "A well-guarded plane-parallel chamber", "A thicker central electrode"],
        "In-scatter grows as the electrons scatter more readily at low energy and as the cavity widens. Beyond the build-up region of a photon beam, and in a well-guarded plane-parallel chamber, P<sub>fl</sub> is close to 1, and the electrode is corrected by P<sub>cel</sub>.", lvl="Moderate"),
    PRN(STEM("TG-51 writes k<sub>Q</sub> as a ratio of products of the water-to-air ratio and the perturbation factors. The values are illustrative for one Farmer-type chamber.",
             [f"Co-60: s<sub>w,air</sub> = {KQ_CO['s']:.3f},   P<sub>wall</sub> = {KQ_CO['wall']:.3f},   P<sub>gr</sub> = {KQ_CO['gr']:.3f},   P<sub>cel</sub> = {KQ_CO['cel']:.3f},   P<sub>fl</sub> = {KQ_CO['fl']:.3f}",
              f"6 MV: s<sub>w,air</sub> = {KQ_6['s']:.3f},   P<sub>wall</sub> = {KQ_6['wall']:.3f},   P<sub>gr</sub> = {KQ_6['gr']:.3f},   P<sub>cel</sub> = {KQ_6['cel']:.3f},   P<sub>fl</sub> = {KQ_6['fl']:.3f}"],
             "What is [[k<sub>Q</sub>]] for the 6 MV beam?"),
        KQ21, [KQ21_s, KQ21_inv, KQ21_p], "{:.4f}",
        f"k<sub>Q</sub> = ({KQ_6['s']:.3f} × {KQ_6['wall']:.3f} × {KQ_6['gr']:.3f} × {KQ_6['cel']:.3f}) / ({KQ_CO['s']:.3f} × {KQ_CO['wall']:.3f} × {KQ_CO['gr']:.3f} × {KQ_CO['cel']:.3f}) = {prodf(KQ_6):.5f} / {prodf(KQ_CO):.5f} = {KQ21:.4f}; P<sub>cel</sub> and P<sub>fl</sub> cancel here. The stopping-power ratios alone give {KQ21_s:.4f}, the perturbation factors alone {KQ21_p:.4f}, and the inverted ratio {KQ21_inv:.4f}.",
        w=[f"Product at 6 MV = {prodf(KQ_6):.5f}", f"Product in Co-60 = {prodf(KQ_CO):.5f}", f"k<sub>Q</sub> = {prodf(KQ_6):.5f} / {prodf(KQ_CO):.5f} = {KQ21:.4f}"], lvl="Challenging"),

    # ---- water-to-air ratios in clinical beams
    PR(STEM("The water-to-air stopping-power ratio is followed with depth in a 6 MV photon beam and in a 12 MeV electron beam.", [], "Why does the ratio change far more with depth in the [[electron beam]]?"),
       "Its electrons slow down with depth, while photons set new electrons in motion at every depth",
       ["Photon beams produce no delta rays in water, so their ratio stays fixed", "The in-scatter of electrons into the cavity grows with depth", "The air in the cavity becomes denser at greater depth"],
       f"The ratio follows the electron spectrum. In an electron beam the spectrum shifts to lower energies with depth, where the ratio is higher: for R<sub>50</sub> = {R50A:.1f} cm it rises from about {S_SURF:.2f} near the surface to {S_R50:.2f} at R<sub>50</sub>. A photon beam keeps setting electrons in motion, so beyond the build-up region its spectrum, and the ratio, barely change. Photon beams do produce delta rays, and in-scatter is the separate factor P<sub>fl</sub>.", lvl="Moderate"),
    PR(STEM("A well-guarded plane-parallel chamber measures a depth-ionization curve on the axis of a 9 MeV electron beam.", [], "Which [[step]] turns the curve into a depth-dose curve?"),
       "Multiply each reading by the water-to-air ratio at its depth, then renormalize",
       ["Multiply every reading by the water-to-air ratio at d<sub>ref</sub>, then renormalize", "Divide each reading by the water-to-air ratio at its depth, then renormalize", "Use the readings as they are, since the guard removes the perturbation"],
       "The dose is the reading times the stopping-power ratio at each depth, and that ratio rises with depth. A single ratio for every depth cancels on renormalization and changes nothing, dividing inverts the correction, and the guard ring makes P<sub>fl</sub> close to 1 but leaves the change of the stopping-power ratio.", lvl="Moderate"),
    PRN(STEM(f"A well-guarded plane-parallel chamber reads on the axis of an electron beam with R<sub>50</sub> = {R50B:.1f} cm. Perturbation factors are taken as equal at both depths.",
             [f"reading at d<sub>ref</sub> = {Z10A:.1f} cm: 1.000 (relative)", f"reading at {Z10B:.1f} cm: {M10B:.3f}", f"s<sub>w,air</sub> at {Z10A:.1f} cm = {S10A:.3f}", f"s<sub>w,air</sub> at {Z10B:.1f} cm = {S10B:.3f}"],
             f"What is the [[dose at {Z10B:.1f} cm relative to the dose at d<sub>ref</sub>]]?"),
        DR10, [M10B, DR10_inv, DR10_one], "{:.3f}",
        f"Each reading times the ratio at its depth: {M10B:.3f} × {S10B:.3f} / {S10A:.3f} = {DR10:.3f}. The uncorrected reading gives {M10B:.3f}, the ratio inverted gives {DR10_inv:.3f}, and multiplying by the deeper ratio alone, without the one at d<sub>ref</sub>, gives {DR10_one:.3f}.", lvl="Challenging"),
    SORT(STEM("The water-to-air stopping-power ratio is read at four points in water.", [], "What is the order of their [[ratios]], lowest first?"), ["1st (lowest)", "2nd", "3rd", "4th (highest)"],
         [(f"Near the surface of an electron beam with R<sub>50</sub> = {R50C:.1f} cm", 0), ("At d<sub>ref</sub> in that electron beam", 1), ("At 10 cm depth in an 18 MV photon beam", 2), ("At 10 cm depth in a Co-60 beam", 3)],
         f"The ratio rises as the electron energy at the point falls, because the density effect lowers the stopping power of water at high energies. In the electron beam it is about {S9_SURF:.2f} near the surface and {S9_REF:.2f} at d<sub>ref</sub>; the photon beams set electrons in motion at far lower energies, giving about 1.10 at 18 MV and 1.13 in Co-60.", lvl="Challenging", mode="rank", cap=1),

    # ---- large cavities and solid detectors
    PR(STEM(f"A LiF TLD chip 0.9 mm thick measures the dose at 1 cm from an I-125 seed, whose photons have energies from about 27 to 35 keV. The electrons they set in motion travel less than {R125_BOUND} µm in water.", [], "Which [[relation]] converts the dose to the LiF into the dose to water?"),
       "The ratio of mass energy-absorption coefficients, water to LiF",
       ["The Spencer–Attix stopping-power ratio, water to LiF", "The ratio of mass attenuation coefficients, water to LiF", "The ratio of densities, water to LiF"],
       "The electrons stop well inside the chip, so charged-particle equilibrium holds within the LiF: a large cavity, whose dose is the collision kerma of LiF. A stopping-power ratio applies only when electrons cross the cavity from the medium, and neither attenuation nor density sets the energy absorbed per gram.", lvl="Moderate"),
    PRN(STEM("The dose to the air of a small chamber in water in a Co-60 beam is known.", [f"D<sub>air</sub> = {DA17:.3f} Gy", f"Spencer–Attix s<sub>w,air</sub> = {S_CO:.3f}", f"(μ<sub>en</sub>/ρ)<sub>water</sub> / (μ<sub>en</sub>/ρ)<sub>air</sub> = {LARGE17:.3f}"], "What is the [[dose to water]]?"),
        DW17, [DW17_large, DW17_inv, DW17_linv], "{:.3f} Gy",
        f"The air cavity is small against the ranges of the Co-60 electrons, so the Spencer–Attix ratio applies: {DA17:.3f} × {S_CO:.3f} = {DW17:.3f} Gy. The large-cavity ratio gives {DW17_large:.3f} Gy, {100 * (1 - LARGE17 / S_CO):.1f}% low, and dividing by either ratio gives {DW17_inv:.3f} or {DW17_linv:.3f} Gy.", lvl="Moderate"),
    SORT(STEM("Four detectors measure dose in water.", [], "Which [[conversion]] suits each one?"),
         ["Spencer–Attix water-to-air ratio with perturbation factors", "Water-to-silicon stopping-power ratio", "Burlin weighting of the two limits", "Ratio of mass energy-absorption coefficients"],
         [("Farmer chamber in a 6 MV beam", 0), ("Diode in a 12 MeV electron beam", 1), ("LiF chip 1 mm thick in a Co-60 beam", 2), ("LiF chip near an I-125 seed", 3)],
         "The air of a chamber is a small cavity in a megavoltage beam, and so is a diode in an electron beam. A 1 mm LiF chip is an intermediate cavity in Co-60, between the limits, and a large one near an I-125 seed, where its electrons stop inside the chip.", lvl="Easy", mode="match", cap=1),
    PRN(STEM("A solid detector of intermediate size is read in a photon beam, and Burlin's theory converts its dose. The values are illustrative.", [f"dose to the detector = {DCAV18:.3f} Gy", f"d = {D18:.2f}", f"stopping-power ratio, detector to water = {S18:.2f}", f"(μ<sub>en</sub>/ρ) ratio, detector to water = {MEN18:.2f}"], "What is the [[dose to water]]?"),
        DW18, [DW18_swap, DW18_large, DW18_mult], "{:.3f} Gy",
        f"D<sub>det</sub> / D<sub>w</sub> = {D18:.2f} × {S18:.2f} + {1 - D18:.2f} × {MEN18:.2f} = {B18:.3f}, so D<sub>w</sub> = {DCAV18:.3f} / {B18:.3f} = {DW18:.3f} Gy. Swapping d and 1 − d gives {DW18_swap:.3f}, the large-cavity limit alone gives {DW18_large:.3f}, and multiplying by the weighted ratio gives {DW18_mult:.3f} Gy.",
        w=[f"D<sub>det</sub> / D<sub>w</sub> = {D18 * S18:.3f} + {(1 - D18) * MEN18:.3f} = {B18:.3f}", f"D<sub>w</sub> = {DCAV18:.3f} / {B18:.3f} = {DW18:.3f} Gy"], lvl="Challenging"),
    PR(STEM("A 9 MeV electron beam is scanned on its axis with an unshielded diode and with a well-guarded plane-parallel chamber. Each curve is normalized to 100% at its own maximum, and neither is corrected.", [], "Beyond the maximum, how does the [[chamber curve]] compare with the diode curve?"),
       "Lower, because the water-to-air ratio rises with depth more than the water-to-silicon ratio",
       ["Higher, because the water-to-air ratio falls with depth", "The same, because both detectors are small cavities", "Higher, because the diode under-responds to electrons at depth"],
       "A chamber reading is proportional to the dose divided by s<sub>w,air</sub>, which rises with depth, so the uncorrected ionization curve falls below the dose curve. The water-to-silicon ratio changes less with depth, so the diode curve lies closer to the dose. Both detectors are small cavities, but their stopping-power ratios change by different amounts.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4, 5, 6], 2: [7, 8, 9], 3: [12, 13, 14], 4: [16, 17, 18]}

TERMS = ["cavity theory", "mass collision stopping power", "Bragg–Gray conditions", "delta rays", "restricted collision stopping power", "track-end term", "fluence perturbation", "general cavity theory"]

TAKE = [
    ["Bragg–Gray: D<sub>med</sub> = D<sub>gas</sub> × (S̄<sub>col</sub>/ρ)<sub>med</sub> / (S̄<sub>col</sub>/ρ)<sub>gas</sub>, for a cavity too small to change the electron fluence and dosed only by electrons from the medium.",
     "D<sub>air</sub> = (Q / m<sub>air</sub>)(W<sub>air</sub>/e). No charged-particle equilibrium is needed."],
    ["Spencer–Attix adds delta rays: the restricted stopping power L<sub>Δ</sub>/ρ for electrons above Δ, plus a track-end term for those that slow below it.",
     "Δ is the energy of an electron whose range spans the cavity (mean chord 4V/S); TG-51 and TRS-398 use 10 keV."],
    ["P<sub>wall</sub>: wall material. P<sub>cel</sub>: central electrode. P<sub>fl</sub>: in-scatter in electron beams, below 1. P<sub>dis</sub> (TG-51 P<sub>gr</sub>): displaced water in a gradient.",
     "TG-51: k<sub>Q</sub> is the ratio of s<sub>w,air</sub> × perturbation factors in the beam and in Co-60; W<sub>air</sub>/e is constant and cancels."],
    ["Water-to-air ratio: about 1.13 in Co-60 to 1.10 at 18 MV, nearly constant with depth in a photon beam.",
     f"In an electron beam it rises with depth (R<sub>50</sub> = {R50A:.0f} cm: about {S_SURF:.2f} to {S_R50:.2f}), so a depth-ionization curve is converted depth by depth."],
    ["Large cavity: D<sub>med</sub> / D<sub>cav</sub> = ratio of μ̄<sub>en</sub>/ρ. Burlin weights the two limits by d, from 1 (small) to 0 (large).",
     "Chamber: Spencer–Attix. Diode: water-to-silicon ratio in electron beams, over-response to low-energy photons. TLD: intermediate in megavoltage beams, near the large-cavity limit at low energy."],
]
