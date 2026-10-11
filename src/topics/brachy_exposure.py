from blocks import *
import math, calc

GAMMA = {"Ra-226 (0.5 mm Pt)": 8.25, "Co-60": 13.2, "Cs-137": 3.28, "Ir-192": 4.69, "I-125": 1.45}       # R cm^2 / (mCi h), typical values; they vary slightly with source and filtration
WE = 0.876                                                                                          # cGy/R in dry air: W/e = 33.97 J/C times 2.58e-4 C/kg per R
x10 = GAMMA["Ir-192"] * 10000 / 10 ** 2                      # exposure rate, 10 Ci Ir-192 at 10 cm
sk_ir = WE * GAMMA["Ir-192"] * 10000                         # air kerma strength of 10 Ci of Ir-192, in U
sk_i125 = WE * GAMMA["I-125"] * 0.50                         # 0.50 mCi of I-125
sk30 = 0.60 * calc.frac_remaining(30, 59.4)                  # 0.60 U I-125 seed after 30 d
ratio_ir_i = GAMMA["Ir-192"] / GAMMA["I-125"]

TOPIC = dict(
    id="brachy-exposure", domain=5, sub="V", title="Exposure rate and air kerma strength",
    ref=dict(aapm="", khan="15", ford="4"),
    guide=[
        H("From activity to dose"),
        P("Activity counts decays per second but does not give dose, because radionuclides differ in how many photons they emit per decay and in how energetic those photons are. Brachytherapy therefore links activity to dose in steps: activity to exposure rate, exposure rate to air kerma rate, and air kerma rate to dose in tissue."),
        P("Exposure X is the charge dQ released by photons in a mass dm of air, X = dQ/dm, measured in coulombs per kilogram. The older unit, the roentgen (R), is 2.58 × 10<sup>−4</sup> C/kg. Sources emit continuously, so the working quantity is the exposure rate, in R/h."),

        H("Exposure rate constant"),
        P("For a point source in air with no attenuation, the exposure rate is proportional to the activity and falls with the square of the distance."),
        EQ("Ẋ = Γ A / r²", "Γ = exposure rate constant (R cm² mCi<sup>−1</sup> h<sup>−1</sup>),   A = activity (mCi),   r = distance (cm)"),
        P("Γ, the exposure rate constant, is a property of the radionuclide. It grows with the number of photons per decay and with their energy, because higher-energy photons ionize more air per photon. Equal activities of different sources therefore give different exposure rates."),
        TABLE(["Source", "Γ (R cm² mCi<sup>−1</sup> h<sup>−1</sup>)"], [[n, f"{g:g}"] for n, g in GAMMA.items()]),
        P(f"Typical values are shown. They differ slightly between references and with source filtration. At equal activity, Ir-192 gives {ratio_ir_i:.1f} times the exposure rate of I-125. The milligram radium equivalent, an older way to specify strength, is the mass of radium filtered by 0.5 mm of platinum that gives the same exposure rate as the source. Air kerma strength has replaced it."),
        EX("Exposure rate in air", STEM("An Ir-192 HDR source.", ["activity = 10 Ci = 10,000 mCi", "Γ = 4.69 R cm² mCi<sup>−1</sup> h<sup>−1</sup>", "distance = 10 cm"], "Find the [[exposure rate]] in air."),
           ["Ẋ = Γ A / r²", f"Ẋ = 4.69 × 10,000 / 10<sup>2</sup>"], f"{x10:.0f} R/h."),

        H("Inverse-square fall-off"),
        P("Photons leave a point source equally in all directions. At distance r they are spread over a sphere of area 4πr², so the number crossing each square centimetre falls as 1/r²."),
        EQ("Ẋ(r₂) = Ẋ(r₁) × (r₁ / r₂)²"),
        P("Doubling the distance cuts the exposure rate to a quarter, and tripling it cuts it to a ninth. Near a brachytherapy source the gradient is steep: the rate at 1 cm is four times the rate at 2 cm, so a small error in source position changes the dose considerably. In tissue, attenuation and scatter modify this simple law, and the radial dose function g(r) in the TG-43 formalism accounts for the net effect."),
        EX("Scaling with distance", STEM("A brachytherapy source in air.", ["exposure rate at 2 cm = 100 R/h"], "Find the [[exposure rate at 5 cm]]."),
           ["Ẋ(5) = Ẋ(2) × (2 / 5)²", "Ẋ(5) = 100 × 0.16"], "16 R/h."),

        H("Air kerma strength"),
        P("The TG-43 formalism specifies a source by its air kerma strength S<sub>K</sub>: the air kerma rate K̇ at a distance d in free space along the transverse axis, multiplied by d². By convention d is 1 m, and the unit is the U."),
        EQ("S<sub>K</sub> = K̇(d) × d²", "1 U = 1 μGy m² h<sup>−1</sup> = 1 cGy cm² h<sup>−1</sup>"),
        P("In air the kerma rate is the exposure rate times W/e, the mean energy spent per unit charge of ions produced. For dry air W/e = 33.97 J/C, which is 0.876 cGy/R."),
        EQ("S<sub>K</sub> = 0.876 Ẋ r² = 0.876 Γ A", "S<sub>K</sub> in U, with Γ in R cm² mCi<sup>−1</sup> h<sup>−1</sup> and A in mCi"),
        P("S<sub>K</sub> decays with the half-life of the source. Seeds are ordered by air kerma strength, which the manufacturer measures against a traceable standard, not by activity. The dose rate constant Λ then converts S<sub>K</sub> to dose rate in water. Λ is fixed by the seed model and cannot be adjusted by the user."),
        EQ("S<sub>K</sub>(t) = S<sub>K</sub>(0) e<sup>−λt</sup>"),
        EX("Air kerma strength of an HDR source", STEM("An Ir-192 HDR source.", ["activity = 10 Ci = 10,000 mCi", "Γ = 4.69 R cm² mCi<sup>−1</sup> h<sup>−1</sup>"], "Find the [[air kerma strength]]."),
           ["S<sub>K</sub> = 0.876 × Γ × A", "S<sub>K</sub> = 0.876 × 4.69 × 10,000"], f"{sk_ir:,.0f} U, about 4.1 × 10<sup>4</sup> U."),
        EX("Decay of seed strength", STEM("An I-125 seed.", ["S<sub>K</sub> at calibration = 0.60 U", "T<sub>1/2</sub> = 59.4 d", "time = 30 d"], "Find the [[air kerma strength]] after 30 d."),
           [f"Fraction remaining = ½<sup>30/59.4</sup> = {calc.frac_remaining(30, 59.4):.3f}", f"S<sub>K</sub> = 0.60 × {calc.frac_remaining(30, 59.4):.3f}"], f"{sk30:.2f} U."),
    ],
    cards=[
        C("Define exposure and give its units.", "The charge released by photons per unit mass of air, X = dQ/dm, in C/kg. The roentgen is 2.58 × 10<sup>−4</sup> C/kg."),
        C("What is a roentgen?", "2.58 × 10<sup>−4</sup> C/kg of air. It was originally defined as 1 esu per cm³ of air."),
        C("Write the exposure rate from a point source in air.", "Ẋ = Γ A / r², with Γ the exposure rate constant (R cm² mCi<sup>−1</sup> h<sup>−1</sup>), A the activity (mCi), and r the distance (cm)."),
        C("What does the exposure rate constant Γ depend on?", "The number of photons emitted per decay and their energies. It is specific to each radionuclide."),
        C("Why do equal activities of Ir-192 and I-125 give different exposure rates?", f"Ir-192 photons are far more energetic and ionize more air. Γ is {GAMMA['Ir-192']} for Ir-192 and {GAMMA['I-125']} for I-125, a ratio of {ratio_ir_i:.1f}."),
        C("State the inverse-square law.", "The intensity from a point source falls as 1/r², because the photons spread over a sphere of area 4πr²."),
        C("How does the exposure rate change from 1 cm to 2 cm?", "It falls to one quarter. Moving from 2 cm to 1 cm raises it fourfold."),
        C("Define air kerma strength.", "The air kerma rate at a distance d in free space, multiplied by d², with d taken as 1 m. Symbol S<sub>K</sub>."),
        C("Give the unit of air kerma strength and its equivalents.", "The U: 1 U = 1 μGy m² h<sup>−1</sup> = 1 cGy cm² h<sup>−1</sup>."),
        C("Relate air kerma strength to Γ and activity.", "S<sub>K</sub> = 0.876 Γ A, with Γ in R cm² mCi<sup>−1</sup> h<sup>−1</sup> and A in mCi."),
        C("What is the value of W/e for dry air, and what does it convert?", "33.97 J/C, which is 0.876 cGy/R. It converts exposure to air kerma."),
        C("Why are seeds ordered by air kerma strength rather than activity?", "S<sub>K</sub> is measured against a traceable standard and, with the seed model's dose rate constant, gives the dose rate directly. Activity depends on how it is defined and measured."),
        C("How does the air kerma strength of a seed change with time?", "It decays exponentially with the half-life of the radionuclide: S<sub>K</sub>(t) = S<sub>K</sub>(0) e<sup>−λt</sup>."),
        C("What was the milligram radium equivalent?", "The mass of radium, filtered by 0.5 mm of platinum, that gives the same exposure rate as the source. An older way of stating source strength."),
    ],
)

PROBLEMS = [
    PR("Exposure is measured in:", "coulombs per kilogram of air (the roentgen is 2.58 × 10<sup>−4</sup> C/kg)", ["grays (joules per kilogram of tissue)", "curies", "sieverts"],
       "Exposure is the charge released in air per unit mass of air. Gray is the unit of absorbed dose and kerma, the curie is a unit of activity, and the sievert is a unit of equivalent dose.", lvl="Easy"),
    PR("The exposure rate from a point source in air falls with the distance r as:", "1/r²", ["1/r", "1/r³", "e<sup>−r</sup>"],
       "The photons spread over a sphere of area 4πr², so the number crossing each unit area falls as 1/r².", lvl="Easy"),
    PR("Two sources have the same activity. Source A emits higher-energy photons than source B. Source A has:", "a larger exposure rate constant", ["a smaller exposure rate constant", "the same exposure rate constant", "a shorter half-life"],
       "Γ grows with photon energy and with the number of photons per decay, so equal activities of different sources do not give equal exposure rates.", lvl="Easy"),
    PRN(STEM("An Ir-192 HDR source.", ["activity = 10 Ci = 10,000 mCi", "Γ = 4.69 R cm² mCi<sup>−1</sup> h<sup>−1</sup>", "distance = 10 cm"], "What is the [[exposure rate]] in air?"), x10, [0.469, 4690.0, WE * x10], "{:.3g} R/h",
        f"Ẋ = Γ A / r² = 4.69 × 10,000 / 100 = {x10:.0f} R/h. Entering the activity as 10 instead of 10,000 mCi gives 0.469; leaving r unsquared gives 4690; multiplying by 0.876 gives the kerma rate in cGy/h, not the exposure rate.", lvl="Moderate"),
    PRN(STEM("An Ir-192 HDR source.", ["activity = 10 Ci = 10,000 mCi", "Γ = 4.69 R cm² mCi<sup>−1</sup> h<sup>−1</sup>"], "What is its [[air kerma strength]]?"), sk_ir, [GAMMA["Ir-192"] * 10000, WE * GAMMA["Ir-192"] * 10, sk_ir * 10], lambda v: f"{v:,.1f} U" if v < 100 else f"{v:,.0f} U",
        f"S<sub>K</sub> = 0.876 Γ A = 0.876 × 4.69 × 10,000 = {sk_ir:,.0f} U. Leaving out W/e gives 46,900; using 10 for the activity gives 41.1.", lvl="Moderate"),
    PR("The air kerma strength of a source is the air kerma rate at a distance d in free space multiplied by:", "d², with d taken as 1 m", ["d, with d taken as 1 cm", "1/d², with d taken as 1 m", "the activity"],
       "Multiplying by d² makes S<sub>K</sub> independent of the distance at which it was measured. The unit is μGy m² h<sup>−1</sup>, called the U.", lvl="Moderate"),
    PR("Which quantity is equal to 1 U?", "1 cGy cm² h<sup>−1</sup>", ["1 cGy h<sup>−1</sup>", "1 R cm² h<sup>−1</sup>", "1 Gy m²"],
       "1 μGy m² h<sup>−1</sup> = 10<sup>−6</sup> Gy × 10<sup>4</sup> cm² h<sup>−1</sup> = 10<sup>−2</sup> Gy cm² h<sup>−1</sup> = 1 cGy cm² h<sup>−1</sup>.", lvl="Moderate"),
    PR("The distance from a point source in air is tripled. The exposure rate becomes:", "one ninth", ["one third", "one sixth", "one half"],
       "The rate scales as 1/r², and (1/3)² = 1/9.", lvl="Moderate"),
    PRN(STEM("An I-125 seed.", ["S<sub>K</sub> at calibration = 0.60 U", "T<sub>1/2</sub> = 59.4 d", "time = 30 d"], "What is its [[air kerma strength]] after 30 d?"), sk30, [0.30, 0.60 * math.exp(-30 / 59.4), 0.60 * (1 - 30 / 59.4)], "{:.3f} U",
        f"The fraction left is ½<sup>30/59.4</sup> = {calc.frac_remaining(30, 59.4):.3f}, so S<sub>K</sub> = {sk30:.3f} U. One half-life would give 0.30; e<sup>−t/T</sup> treats the half-life as a mean life; a straight-line fall is not exponential.", lvl="Challenging"),
    PR("Why are brachytherapy seeds ordered by air kerma strength rather than by activity?", "S<sub>K</sub> is measured against a traceable standard and, with the seed model's dose rate constant, gives the dose rate", ["Activity cannot be measured for a sealed source", "S<sub>K</sub> does not decay with time", "The dose rate constant depends on the activity ordered"],
       "Activity can be defined in several ways for an encapsulated source, while S<sub>K</sub> is the quantity the dose calculation uses. S<sub>K</sub> decays like the activity, and Λ is a fixed property of the seed model.", lvl="Challenging"),
    PRM("Which factors determine the exposure rate constant Γ?", ["The number of photons emitted per decay", "The photon energies", "The filtration of the source"], ["The distance from the source", "The activity of the source"],
        "Γ is the exposure rate at unit distance per unit activity. It depends on the emission spectrum, which includes the photons that survive the encapsulation, and not on distance or activity.", lvl="Challenging"),
    PRN(STEM("A brachytherapy source in air.", ["exposure rate at 1 cm = 400 R/h"], "What is the [[exposure rate at 4 cm]]?"), 25.0, [100.0, 50.0, 6.25], "{:.3g} R/h",
        "Ẋ(4) = 400 × (1/4)² = 400 / 16 = 25 R/h. A 1/r law would give 100 R/h.", lvl="Challenging"),
]

INLINE = {0: [1], 1: [3, 4], 2: [2, 8], 3: [5, 7]}

TERMS = ['exposure', 'exposure rate constant', 'air kerma strength']

TAKE = [
    [('Activity does not give dose. The exposure rate from a point source is Ẋ = Γ A / r², and Γ depends on how many photons are emitted and their energies.', 'dose-chain')],
    [('At equal activity, Ir-192 gives 3.2 times the exposure rate of I-125, at every distance, because Γ is larger.', 'gamma-compare')],
    [('The exposure rate falls as 1/r²: doubling the distance cuts it to a quarter.', 'sphere-shells')],
    [('S<sub>K</sub> = 0.876 Γ A, in U (cGy cm² h<sup>−1</sup>). 10 Ci of Ir-192 is about 4.1 × 10<sup>4</sup> U.', 'sk-per-mci'),
     ('Seeds are ordered by S<sub>K</sub>, which decays with the half-life. The dose rate constant Λ is fixed by the seed model.', 'sk-decay')],
]


# ---------------------------------------------------------------- matching, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
_fig_inv = FS(x=dict(min=1, max=12, ticks=[1, 2, 4, 6, 8, 10, 12], label="Distance from the source (cm)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Exposure rate (% of the rate at 1 cm)", fmt="pct"),
              series=[dict(pts=PTS(lambda r: 100 / r ** 2, 1, 12), color="plot-1")], xunit=" cm", xdec=2, xname="Distance", label="Exposure rate against distance from a point source")
PROBLEMS += [
    SORT("Match each quantity to its unit.", ["R", "R cm² mCi<sup>−1</sup> h<sup>−1</sup>", "U (cGy cm² h<sup>−1</sup>)", "mCi"],
         [("Exposure", 0), ("Exposure rate constant", 1), ("Air kerma strength", 2), ("Activity", 3)],
         "Exposure is in roentgens. The exposure rate constant is the exposure rate at unit distance per unit activity. Air kerma strength is in U. Activity is in curies or becquerels, and the millicurie is the usual unit for a seed.", lvl="Easy", mode="match", cap=1),
    TYPED(STEM("An I-125 seed.", ["apparent activity = 0.50 mCi", "Γ = 1.45 R cm² mCi<sup>−1</sup> h<sup>−1</sup>"], "What is its [[air kerma strength]]?"), sk_i125, 0.015, "U",
          f"S<sub>K</sub> = 0.876 Γ A = 0.876 × 1.45 × 0.50 = {sk_i125:.3f} U. A typical I-125 seed is a little over half a unit.", lvl="Moderate"),
    FIGQ(STEM("The exposure rate in air from a point source is plotted as a percentage of its value at 1 cm.", [], "Tap the [[distance at which the rate has fallen to one ninth]] of its value at 1 cm."),
         _fig_inv, [(2.6, 3.4)], "The rate scales as 1/r², so one ninth means r² = 9 and r = 3 cm. The curve is at 11% there, which is not a marked level, so the distance has to be worked out.", lvl="Moderate", note="3 cm"),
    FIGQ(STEM("The exposure rate in air from a point source is plotted as a percentage of its value at 1 cm.", [], "Tap the [[distance at which the rate is 1%]] of its value at 1 cm."),
         _fig_inv, [(9.3, 10.7)], "1% means 1/r² = 1/100, so r = 10 cm. At that distance the curve lies almost on the axis and cannot be read, so the inverse-square law has to be applied.", lvl="Challenging", note="10 cm"),
]
INLINE = {0: [1], 1: [3, 4], 2: [2, 8, _n0 + 3, _n0 + 4], 3: [5, 7, _n0 + 1, _n0 + 2]}
