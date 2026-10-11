from blocks import *

xr, xc = 50 * 2.58e-4, 50 * 0.876
psi, men = 0.50, 2.97e-3          # J/m^2, m^2/kg (0.0297 cm^2/g)
k = psi * men

TOPIC = dict(
    id="kerma-dose", domain=2, sub="II.A", title="Kerma, absorbed dose, and exposure",
    ref=dict(aapm="6.1, 6.2", khan="6, 8", ford="7"),
    guide=[
        H("Fluence and energy fluence"),
        P("Fluence Φ is the number of particles crossing a small sphere per unit cross-sectional area (1/m²). Energy fluence Ψ is the energy those particles carry per unit area (J/m²). For monoenergetic photons Ψ = Φ E."),

        H("Kerma"),
        EQ("K = dE<sub>tr</sub> / dm   (unit: Gy = J/kg)", "K = Ψ (μ<sub>tr</sub>/ρ)"),
        P("Kerma is the kinetic energy transferred to charged particles per unit mass at a point. Some of that energy is then radiated as bremsstrahlung, so kerma has a collision part and a radiative part:"),
        EQ("K = K<sub>col</sub> + K<sub>rad</sub>", "K<sub>col</sub> = K (1 − g) = Ψ (μ<sub>en</sub>/ρ)"),
        P("g is the fraction of the electron energy lost radiatively. It is small in low-Z media at therapy energies and grows with energy. μ<sub>en</sub> = μ<sub>tr</sub> (1 − g)."),

        H("Absorbed dose"),
        EQ("D = dE / dm   (unit: Gy = J/kg; 1 Gy = 100 cGy = 100 rad)"),
        P("Absorbed dose is the energy deposited locally per unit mass. It depends on where the charged particles stop, so dose and kerma differ near surfaces and interfaces."),
        FIG("kerma_dose", "Schematic. Kerma falls from the surface with the photon fluence. Dose builds up as electrons travel downstream, peaks at d<sub>max</sub>, and then stays slightly above kerma. The gap is exaggerated."),
        UL("Build-up region: D < K<sub>col</sub>, because electrons set in motion upstream have not yet arrived.",
           "Charged-particle equilibrium (CPE): D = K<sub>col</sub> = Ψ (μ<sub>en</sub>/ρ).",
           "Beyond d<sub>max</sub> in a megavoltage beam there is transient CPE: D = β K<sub>col</sub> with β slightly above 1, because the electrons come from slightly shallower points where the fluence was higher."),

        H("Exposure"),
        EQ("X = dQ / dm   (C/kg of air)", "1 R = 2.58 × 10<sup>−4</sup> C/kg", "W<sub>air</sub>/e = 33.97 J/C, so 1 R = 0.876 cGy in air"),
        P("Exposure is the charge of one sign produced in air per unit mass by photons, once the secondary electrons have stopped. It is defined for photons below about 3 MeV, because the free-air chamber needs the electrons to stop within the air. The roentgen is the legacy unit; the SI quantity is C/kg."),
        P("W is the mean energy that a charged particle spends in air for each ion pair it forms, about 33.97 eV, so that W/e = 33.97 J/C. Under charged-particle equilibrium the dose in another medium follows from the dose in air: it is the dose to air multiplied by the ratio of the mass energy-absorption coefficients, medium to air. The f-factor combines this ratio with the conversion of 0.876 cGy/R, so that D<sub>med</sub> = f X."),
        EQ("D<sub>med</sub> = f X,   f = 0.876 cGy/R × (μ<sub>en</sub>/ρ)<sub>med</sub> / (μ<sub>en</sub>/ρ)<sub>air</sub>"),
        EX("Exposure to dose in air", STEM("A free-air chamber records an exposure.", ["X = 50 R"], "Find the exposure in [[C/kg]] and the [[dose to air]]."),
           [f"50 × 2.58 × 10<sup>−4</sup> = {xr:.4f} C/kg.", f"50 × 0.876 = {xc:.1f} cGy."], f"{xr:.4f} C/kg, and {xc:.1f} cGy in air."),
        EX("Kerma from energy fluence", STEM("Co-60 photons irradiate water.", ["energy fluence Ψ = 0.50 J/m²", "μ<sub>en</sub>/ρ = 0.0297 cm²/g at 1.25 MeV"], "Find the collision kerma [[K<sub>col</sub>]]."),
           ["μ<sub>en</sub>/ρ = 0.0297 cm²/g = 2.97 × 10<sup>−3</sup> m²/kg.", f"K<sub>col</sub> = 0.50 × 2.97 × 10<sup>−3</sup> = {sci(k, 3)} Gy."], f"{k*100:.2f} cGy."),

        H("Protection quantities"),
        TABLE(["Quantity", "Definition", "Unit"], [
            ["Equivalent dose H<sub>T</sub>", "Σ w<sub>R</sub> D<sub>T,R</sub>: dose in a tissue weighted by the radiation type", "Sv (1 Sv = 100 rem)"],
            ["Effective dose E", "Σ w<sub>T</sub> H<sub>T</sub>: equivalent doses weighted by tissue sensitivity", "Sv"]]),
        TABLE(["Radiation", "w<sub>R</sub> (ICRP 103)"], [["Photons, electrons", "1"], ["Protons", "2"], ["α particles", "20"], ["Neutrons", "2.5 to 20, depending on energy"]]),

    ],
    cards=[
        C("Define fluence and energy fluence, with units.", "Fluence Φ: particles per unit cross-sectional area (1/m²). Energy fluence Ψ: energy carried by those particles per unit area (J/m²). Ψ = Φ E for monoenergetic photons."),
        C("Define kerma and give its relation to energy fluence.", "Kinetic energy transferred to charged particles per unit mass, in Gy (J/kg). K = Ψ (μ<sub>tr</sub>/ρ)."),
        C("How do kerma and absorbed dose differ?", "Kerma is energy transferred to charged particles at a point. Absorbed dose is energy deposited at the point. The electrons travel, so the two differ near surfaces and interfaces."),
        C("How are K and K<sub>col</sub> related?", "K<sub>col</sub> = K (1 − g), where g is the fraction of the electron energy radiated as bremsstrahlung. K<sub>col</sub> = Ψ (μ<sub>en</sub>/ρ)."),
        C("In which region is D = K<sub>col</sub>, and what is D relative to K<sub>col</sub> in the build-up region?", "D = K<sub>col</sub> where charged-particle equilibrium holds. In the build-up region D < K<sub>col</sub>, because electrons from upstream have not yet arrived.", fig="kerma_dose"),
        C("Beyond d<sub>max</sub> in a megavoltage beam, why does D stay slightly above K<sub>col</sub>?", "Transient CPE: the electrons depositing dose at a point were set in motion at slightly shallower points, where the photon fluence was higher. D = β K<sub>col</sub> with β slightly above 1."),
        C("Define exposure, give its SI unit, and state its energy limit.", "Charge of one sign produced in air per unit mass by photons, once secondary electrons have stopped. SI unit C/kg; 1 R = 2.58 × 10<sup>−4</sup> C/kg. Defined for photons below about 3 MeV."),
        C("A free-air chamber records 50 R. What is the dose to air?", f"{xc:.1f} cGy.", w=["1 R = 0.876 cGy in air.", f"50 × 0.876 = {xc:.1f} cGy."]),
        C("How does W<sub>air</sub>/e = 33.97 J/C give the dose per roentgen?", "1 R = 2.58 × 10<sup>−4</sup> C/kg, and each coulomb of ionization corresponds to 33.97 J absorbed. 2.58 × 10<sup>−4</sup> × 33.97 = 8.76 × 10<sup>−3</sup> J/kg = 0.876 cGy."),
        C("Co-60 photons give 0.50 J/m² in water, with μ<sub>en</sub>/ρ = 0.0297 cm²/g. What is K<sub>col</sub>?", f"{k*100:.2f} cGy.", w=["0.0297 cm²/g = 2.97 × 10<sup>−3</sup> m²/kg.", f"K<sub>col</sub> = Ψ μ<sub>en</sub>/ρ = 0.50 × 2.97 × 10<sup>−3</sup> = {sci(k, 3)} Gy."]),
        C("Distinguish equivalent dose from effective dose, and give w<sub>R</sub> for photons, protons, and α particles.", "Equivalent dose weights absorbed dose by radiation type: H = Σ w<sub>R</sub> D. Effective dose weights equivalent doses by tissue sensitivity: E = Σ w<sub>T</sub> H<sub>T</sub>. Both are in Sv. w<sub>R</sub>: photons 1, protons 2, α 20 (ICRP 103)."),
        C("Convert: 1 Gy in cGy and in rad; 1 Sv in rem.", "1 Gy = 100 cGy = 100 rad. 1 Sv = 100 rem."),
    ],
)

TERMS = ['fluence', 'energy fluence', 'kerma', 'absorbed dose', 'exposure', 'charged-particle equilibrium']

TAKE = [
    [('Fluence Φ is particles per area; energy fluence Ψ is energy per area.', 'fluence-box')],
    [('Kerma K = Ψ μ<sub>tr</sub>/ρ is the energy transferred. K<sub>col</sub> = K(1 − g) = Ψ μ<sub>en</sub>/ρ.', 'kerma-split')],
    [('Absorbed dose is the energy deposited. D &lt; K<sub>col</sub> in build-up, D = K<sub>col</sub> at CPE, and D = βK<sub>col</sub> (β slightly above 1) beyond d<sub>max</sub>.', 'buildup-kerma-dose')],
    [('1 R = 2.58 × 10<sup>−4</sup> C/kg = 0.876 cGy in air.', 'exposure-chain')],
    [('1 Gy = 100 cGy = 100 rad. Equivalent and effective dose are in Sv. w<sub>R</sub>: photons and electrons 1, protons 2, α 20.', 'equivalent-dose')],
]


# ---------------------------------------------------------------- practice questions
import math, nistdata as nd
EJ = 1.602176634e-13                                   # J per MeV
q_psi = 3.0e12 * 1.25 * EJ
q_kw = 0.80 * nd.WATER[1.0][1] * 0.1 * 1000            # mGy: psi (J/m^2) x mu_en/rho (cm^2/g -> m^2/kg) x 1000
q_k2 = 5.0e11 * 2.0 * EJ * nd.WATER[2.0][1] * 0.1 * 1000
q_dbeta = 1.03 * 0.50 * nd.WATER[2.0][1] * 0.1 * 1000
q_bw = nd.BONE[0.1][1] / nd.WATER[0.1][1]
q_air = 25 * 0.876
q_h = 0.50 * 1 + 0.10 * 20

PROBLEMS = [
    PR("Fluence Φ is defined as:", "the number of particles crossing a small sphere per unit cross-sectional area", ["the energy deposited per unit mass", "the energy carried by the particles per unit area", "the number of particles per unit mass"],
       "Fluence counts particles per unit area (1/m²). Energy fluence Ψ is the energy those particles carry per unit area (J/m²), and for monoenergetic photons Ψ = Φ E.", lvl="Easy"),
    PRN(STEM("Monoenergetic photons.", ["fluence Φ = 3.0 × 10<sup>12</sup> m<sup>−2</sup>", "photon energy = 1.25 MeV"], "What is the [[energy fluence Ψ]]?"), q_psi, [q_psi * 1e-3, 3.0e12 * EJ, q_psi * 10], lambda v: f"{v:.3g} J/m²",
        f"Ψ = Φ E = 3.0 × 10<sup>12</sup> × 1.25 MeV × 1.602 × 10<sup>−13</sup> J/MeV = {q_psi:.3f} J/m². Dropping the factor of 1.25 gives {3.0e12 * EJ:.3f} J/m², and the other two options are powers of ten away from slips in the MeV-to-joule conversion.", lvl="Moderate",
        calc=CALC("J/m²", [TILE("Φ", 3.0e12, "m⁻²", disp="3.0 × 10¹²"), TILE("E", 1.25, "MeV"), CONV("MeV", "J", EJ, disp="1.602 × 10⁻¹³")], solution=["Φ", "×", "E", "×", "MeV→J"])),
    PR("Kerma is:", "the kinetic energy transferred to charged particles per unit mass at a point", ["the energy deposited per unit mass at a point", "the charge of one sign produced per unit mass of air", "the number of photons per unit area"],
       "Kerma (kinetic energy released per unit mass) counts the energy transferred to charged particles at the point where the photons interact. Absorbed dose counts the energy deposited at the point, which can differ because the charged particles travel.", lvl="Easy"),
    PRN(STEM("A 1.0 MeV photon beam irradiates water. Use the table.", ["energy fluence Ψ = 0.80 J/m²"], "Find the [[collision kerma]] in water.", tables=[nd.table_one("water", [0.5, 1.0, 1.25, 1.5])]),
        q_kw, [0.80 * nd.WATER[1.0][0] * 0.1 * 1000, q_kw * 10, 0.80 * nd.WATER[1.25][1] * 0.1 * 1000], "{:.2f} mGy",
        f"Collision kerma uses the energy-absorption coefficient: μ<sub>en</sub>/ρ = {nd.WATER[1.0][1]} cm²/g = {nd.WATER[1.0][1] * 0.1:.5f} m²/kg at 1.0 MeV. K<sub>col</sub> = Ψ × μ<sub>en</sub>/ρ = 0.80 × {nd.WATER[1.0][1] * 0.1:.5f} = {q_kw / 1000:.5f} Gy = {q_kw:.2f} mGy. The attenuation column gives {0.80 * nd.WATER[1.0][0] * 0.1 * 1000:.2f} mGy, skipping the cm²/g to m²/kg conversion gives {q_kw * 10:.1f} mGy, and the 1.25 MeV row gives {0.80 * nd.WATER[1.25][1] * 0.1 * 1000:.2f} mGy.", lvl="Moderate"),
    PRN(STEM("Monoenergetic 2.0 MeV photons irradiate water. Use the table.", ["fluence Φ = 5.0 × 10<sup>11</sup> m<sup>−2</sup>"], "What is the [[collision kerma]] in water?", tables=[nd.table_one("water", [1.0, 1.25, 1.5, 2.0, 3.0])]),
        q_k2, [5.0e11 * 2.0 * EJ * nd.WATER[2.0][0] * 0.1 * 1000, q_k2 * 10, 5.0e11 * 2.0 * EJ * nd.WATER[1.0][1] * 0.1 * 1000], "{:.3f} mGy",
        f"Ψ = Φ E = 5.0 × 10<sup>11</sup> × 2.0 × 1.602 × 10<sup>−13</sup> = {5.0e11 * 2.0 * EJ:.4f} J/m². Read μ<sub>en</sub>/ρ = {nd.WATER[2.0][1]} cm²/g at 2.0 MeV = {nd.WATER[2.0][1] * 0.1:.5f} m²/kg. K<sub>col</sub> = {5.0e11 * 2.0 * EJ:.4f} × {nd.WATER[2.0][1] * 0.1:.5f} = {sci(q_k2 / 1000, 3)} Gy = {q_k2:.3f} mGy. Using μ/ρ gives {5.0e11 * 2.0 * EJ * nd.WATER[2.0][0] * 0.1 * 1000:.3f} mGy, and reading the 1.0 MeV row gives {5.0e11 * 2.0 * EJ * nd.WATER[1.0][1] * 0.1 * 1000:.3f} mGy.", lvl="Challenging"),
    PRN(STEM("The same energy fluence of 100 keV photons irradiates cortical bone and water. Use the table.", [], "Energy is absorbed per gram in bone at how many [[times the rate]] in water?", tables=[nd.table_two(["bone", "water"], [0.1, 0.5, 1.0, 6.0])]),
        q_bw, [nd.WATER[0.1][1] / nd.BONE[0.1][1], nd.BONE[0.1][0] / nd.WATER[0.1][0], nd.BONE[0.1][1] * 1.92 / nd.WATER[0.1][1]], "{:.2f}",
        f"Energy absorbed per gram is Ψ × μ<sub>en</sub>/ρ, so the ratio is the ratio of the energy-absorption coefficients: {nd.BONE[0.1][1]} / {nd.WATER[0.1][1]} = {q_bw:.2f}. Inverting gives {nd.WATER[0.1][1] / nd.BONE[0.1][1]:.2f}, using the attenuation column gives {nd.BONE[0.1][0] / nd.WATER[0.1][0]:.2f}, and multiplying by the density ratio (per cm³ instead of per gram) gives {nd.BONE[0.1][1] * 1.92 / nd.WATER[0.1][1]:.2f}. At 6 MeV the two media absorb almost equally per gram ({nd.BONE[6.0][1] / nd.WATER[6.0][1]:.2f}).", lvl="Challenging"),
    PR("In the build-up region of a megavoltage photon beam, the absorbed dose is:", "less than the collision kerma, because electrons set in motion upstream have not yet arrived", ["equal to the collision kerma", "greater than the collision kerma", "unrelated to the kerma"],
       "Kerma is highest at the surface and falls with the photon fluence. Dose starts low and rises as the electrons travel downstream, so in the build-up region D < K<sub>col</sub>. At d<sub>max</sub> the two are about equal.", lvl="Easy"),
    PR("Beyond d<sub>max</sub> in a megavoltage beam, the absorbed dose stays slightly above the collision kerma because:", "the electrons depositing dose at a point started at slightly shallower points, where the photon fluence was higher", ["the electrons are absorbed more strongly at depth", "the beam hardens with depth", "scatter adds dose that kerma does not include"],
       "This is transient charged-particle equilibrium: D = β K<sub>col</sub> with β slightly above 1. The electrons come from upstream, where there were more photons. Kerma at the point itself is lower.", lvl="Moderate"),
    PRN(STEM("A point beyond d<sub>max</sub> in a 6 MV beam, where transient charged-particle equilibrium holds with β = 1.03. Take the effective photon energy as 2.0 MeV. Use the table.", ["energy fluence Ψ = 0.50 J/m²"], "Find the [[absorbed dose]] in water.", tables=[nd.table_one("water", [1.0, 1.5, 2.0, 3.0])]),
        q_dbeta, [0.50 * nd.WATER[2.0][1] * 0.1 * 1000, 1.03 * 0.50 * nd.WATER[2.0][0] * 0.1 * 1000, q_dbeta * 10], "{:.3f} mGy",
        f"D = β K<sub>col</sub> = β Ψ (μ<sub>en</sub>/ρ) = 1.03 × 0.50 × {nd.WATER[2.0][1] * 0.1:.5f} = {sci(q_dbeta / 1000, 3)} Gy = {q_dbeta:.3f} mGy. Leaving out β gives {0.50 * nd.WATER[2.0][1] * 0.1 * 1000:.3f} mGy, using the attenuation column gives {1.03 * 0.50 * nd.WATER[2.0][0] * 0.1 * 1000:.3f} mGy, and skipping the unit conversion gives {q_dbeta * 10:.2f} mGy.", lvl="Challenging"),
    PR("1 Gy is equal to:", "100 cGy, or 100 rad", ["1 cGy", "10 rad", "1000 cGy"],
       "1 Gy = 1 J/kg = 100 cGy = 100 rad. Equivalent dose uses the sievert, and 1 Sv = 100 rem.", lvl="Easy"),
    PRN(STEM("A free-air chamber records an exposure.", ["X = 25 R"], "What is the [[dose to air]]?"), q_air, [25 * 0.0876, 25 * 33.97, 25.0], "{:.1f} cGy",
        f"1 R deposits 0.876 cGy in air, so 25 R gives 25 × 0.876 = {q_air:.1f} cGy. The factor comes from 2.58 × 10<sup>−4</sup> C/kg × 33.97 J/C = 8.76 × 10<sup>−3</sup> Gy. A decimal slip gives {25 * 0.0876:.2f} cGy, using W<sub>air</sub>/e directly gives {25 * 33.97:.0f}, and treating 1 R as 1 cGy gives 25.0 cGy.", lvl="Moderate",
        calc=CALC("cGy", [TILE("X", 25, "R"), TILE("k", 0.876, "cGy/R", disp="0.876")], solution=["X", "×", "k"])),
    PR("Exposure is defined for:", "photons in air, below about 3 MeV", ["any radiation in any medium", "photons in water up to 20 MeV", "charged particles in air"],
       "Exposure is the charge of one sign produced in air by photons once the secondary electrons have stopped. Above about 3 MeV the electrons travel too far to be stopped within a practical air volume. The roentgen is the legacy unit, and the SI quantity is C/kg.", lvl="Moderate"),
    PRN(STEM("A tissue is irradiated by two radiations.", ["photon dose = 0.50 Gy", "α-particle dose = 0.10 Gy", "w<sub>R</sub>: photons 1, α particles 20"], "What is the [[equivalent dose]]?"), q_h, [0.50 + 0.10, 0.50 + 0.10 * 2, 0.50 * 20 + 0.10 * 1], "{:.2f} Sv",
        f"H = Σ w<sub>R</sub> D = 1 × 0.50 + 20 × 0.10 = {q_h:.2f} Sv. Adding the doses gives 0.60, using 2 for the α particles gives 0.70, and swapping the weights gives {0.50 * 20 + 0.10:.2f} Sv.", lvl="Moderate"),
]
INLINE = {0: [0, 1], 1: [2, 3], 2: [6, 7], 3: [11], 4: [13]}


# ---------------------------------------------------------------- matching and typed-number questions
_n0 = len(PROBLEMS)
q_cpk = 120 * 2.58e-4
PROBLEMS += [
    SORT("Match each region of a megavoltage photon beam to the relation between the absorbed dose D and the collision kerma K<sub>col</sub>.", ["Build-up region", "Where charged-particle equilibrium holds", "Beyond d<sub>max</sub>"],
         [("D &lt; K<sub>col</sub>", 0), ("D = K<sub>col</sub>", 1), ("D = β K<sub>col</sub>, with β slightly above 1", 2)],
         "In the build-up region the electrons have not yet reached equilibrium, so the dose is below the kerma. Where charged-particle equilibrium holds, the dose equals the collision kerma. Beyond d<sub>max</sub> the beam is attenuating, so the electrons come from slightly upstream (more energetic) and the dose stays a little above the kerma.", lvl="Moderate", mode="match", cap=1),
    SORT("Match each quantity to its SI unit.", ["m<sup>−2</sup>", "J/m²", "Gy (J/kg)", "C/kg", "Sv"],
         [("Fluence", 0), ("Energy fluence", 1), ("Kerma", 2), ("Absorbed dose", 2), ("Exposure", 3), ("Equivalent dose", 4)],
         "Fluence counts particles per area, and energy fluence adds the energy they carry per area. Kerma and absorbed dose are both energy per mass, which is the gray. Exposure is charge per mass of air. Equivalent dose is energy per mass weighted by radiation type, and it is given its own name, the sievert, so it is not confused with the gray.", lvl="Easy", mode="match"),
    SORT("Match each radiation to its radiation weighting factor w<sub>R</sub> (ICRP 103).", ["1", "2", "20"],
         [("Photons", 0), ("Electrons", 0), ("Protons", 1), ("α particles", 2)],
         "Photons and electrons have w<sub>R</sub> = 1. Protons are 2. α particles, which deposit their energy densely, are 20. Equivalent dose is the absorbed dose multiplied by w<sub>R</sub>.", lvl="Easy", mode="match"),
    TYPED(STEM("A free-air chamber records an exposure.", ["X = 120 R"], "What is the exposure in [[C/kg]]?"), q_cpk, 0.01, "C/kg",
          "1 R = 2.58 × 10<sup>−4</sup> C/kg, so 120 R = 120 × 2.58 × 10<sup>−4</sup> = 3.10 × 10<sup>−2</sup> C/kg.", lvl="Easy"),
]
INLINE = {0: [1, 2], 1: [3, 4], 2: [7, 8, _n0 + 1], 3: [11, 12, _n0 + 4], 4: [10, 13, _n0 + 2, _n0 + 3]}


# ---------------------------------------------------------------- dose in a medium from exposure
_nk = len(PROBLEMS)
_men_air, _men_mus = 0.0267, 0.0296                                                  # cm^2/g at 1.25 MeV
d_air30 = 30 * 0.876
d_mus30 = d_air30 * _men_mus / _men_air
PROBLEMS += [
    PRN(STEM("A free-air chamber records an exposure of 30 R at a point in a Co-60 beam. At 1.25 MeV, μ<sub>en</sub>/ρ is 0.0267 cm²/g for air and 0.0296 cm²/g for muscle. Take 1 R = 0.876 cGy in air.", [], "What is the [[dose to muscle]] at that point, under charged-particle equilibrium?"), d_mus30, [d_air30, d_air30 * _men_air / _men_mus, 30 * _men_mus / _men_air], "{:.1f} cGy",
        f"The dose to air is 30 × 0.876 = {d_air30:.1f} cGy. Under charged-particle equilibrium the dose in muscle is that value times the ratio of the mass energy-absorption coefficients: 0.0296 / 0.0267 = {_men_mus / _men_air:.3f}, which gives {d_mus30:.1f} cGy. Stopping at air gives {d_air30:.1f}, inverting the ratio gives {d_air30 * _men_air / _men_mus:.1f}, and applying the ratio to the exposure alone gives {30 * _men_mus / _men_air:.1f}.", lvl="Challenging"),
    PR("In the quantity W/e = 33.97 J/C, W is:", "the mean energy that a charged particle spends in air for each ion pair it forms", ["the energy needed to remove the least bound electron of an air molecule", "the work function of the wall of the chamber", "the energy of the photon that enters the chamber"],
       "Each ion pair costs an average energy W of about 33.97 eV, which includes the energy that goes to excitation and not only to ionization. Multiplying the charge per unit mass, in C/kg, by W/e gives the dose to air in J/kg.", lvl="Moderate"),
]
INLINE.setdefault(3, []).extend([_nk + 1, _nk + 2])
