from blocks import *
import math, calc

NUC = [("Co-60", 5.27 * calc.YEAR_S, 59.93, "5.27 y", "Teletherapy sources"),
       ("Cs-137", 30.1 * calc.YEAR_S, 136.91, "30.1 y", "Older brachytherapy, calibration"),
       ("Ir-192", 73.8 * calc.DAY_S, 191.96, "73.8 d", "HDR brachytherapy"),
       ("I-125", 59.4 * calc.DAY_S, 124.90, "59.4 d", "Permanent seed implants"),
       ("Pd-103", 16.99 * calc.DAY_S, 102.91, "17.0 d", "Permanent seed implants"),
       ("Ra-226", 1600 * calc.YEAR_S, 226.03, "1600 y", "Historical brachytherapy")]
S = {n: calc.spec_act_bq_g(th, m) for n, th, m, _, _ in NUC}
ci = lambda n: S[n] / calc.CI_BQ
lam_i = calc.LN2 / (59.4 * calc.DAY_S); atoms_i = calc.NA / 124.90
m_seed_ng = 0.50e-3 * calc.CI_BQ / S["I-125"] * 1e9
m_ir_mg = 370e9 / S["Ir-192"] * 1e3
m_ir_given_mg = 370e9 / 3.4e14 * 1e3                               # from the rounded S printed in the question
m_seed_given_ng = 0.50e-3 * calc.CI_BQ / 6.5e14 * 1e9
m_cs_mg = 370e9 / S["Cs-137"] * 1e3
m_co_g = 185e12 / S["Co-60"]
lu = calc.spec_act_bq_g(6.647 * calc.DAY_S, 176.94)
hyp = calc.spec_act_bq_g(100 * calc.DAY_S, 100.0)
pd_over_i = S["Pd-103"] / S["I-125"]

TOPIC = dict(
    id="specific-activity", domain=1, sub="I.B", title="Specific activity",
    ref=dict(aapm="2.2", khan="2", ford="3"),
    guide=[
        H("Activity per gram"),
        P("Specific activity is the activity per unit mass of the radioactive material. For a pure sample of one radionuclide it follows from the decay constant and the number of atoms in a gram."),
        EQ("S = A / m = λ N<sub>A</sub> / M = ln 2 · N<sub>A</sub> / (T<sub>1/2</sub> · M)", "N<sub>A</sub> = 6.022 × 10<sup>23</sup> mol<sup>−1</sup>,   M = molar mass in g/mol"),
        P("A short half-life and a light atom both raise S: more decays per atom, and more atoms per gram. Units are Bq/g or Ci/g."),
        TABLE(["Nuclide", "T<sub>1/2</sub>", "S (Bq/g)", "S (Ci/g)", "Use"],
              [[n, t, sci(S[n]), (f"{ci(n):,.0f}" if ci(n) >= 10 else f"{ci(n):.2f}"), u] for n, _, _, t, u in NUC]),
        P("These are theoretical maxima for pure, carrier-free material. Real sources are lower. Ir-192 is made by neutron capture on stable Ir-191, so most of the atoms in an iridium source are still stable iridium."),

        H("Source size and carrier"),
        P(f"In brachytherapy, specific activity sets how small a source can be. 370 GBq (10 Ci) of Ir-192 is about {m_ir_mg:.1f} mg of iridium, small enough for near-point geometry. The same activity of Cs-137 is {m_cs_mg:.0f} mg, {m_cs_mg / m_ir_mg:.0f} times the mass and too bulky for an HDR catheter."),
        P(f"In radiopharmaceutical therapy, specific activity sets how much non-radioactive carrier is given with the activity, and carrier can compete for receptor sites. Lu-177 made by neutron capture on Lu-176 keeps stable Lu-176 in the product. Irradiating Yb-176 gives Yb-177, which decays to Lu-177 that can be separated chemically and approaches the theoretical {sci(lu)} Bq/g."),

        EX("Specific activity of I-125", STEM("", ["T<sub>1/2</sub> = 59.4 d", "molar mass M = 124.9 g/mol"], "Find the [[specific activity]] S of I-125."),
           [f"λ = 0.693 / (59.4 × 86,400 s) = {sci(lam_i, 4)} s<sup>−1</sup>", f"Atoms per gram = 6.022 × 10<sup>23</sup> / 124.9 = {sci(atoms_i, 4)}", f"S = λ × atoms per gram = {sci(S['I-125'], 3)} Bq/g"],
           f"{sci(S['I-125'])} Bq/g, or {ci('I-125'):,.0f} Ci/g."),
        EX("Mass of a seed", STEM("", ["seed activity = 0.50 mCi", f"S (I-125) = {sci(S['I-125'])} Bq/g"], "Find the [[mass of I-125]] in the seed."),
           ["0.50 mCi × 3.7 × 10<sup>7</sup> Bq/mCi = 1.85 × 10<sup>7</sup> Bq", f"m = A / S = 1.85 × 10<sup>7</sup> / {sci(S['I-125'])}"], f"{m_seed_given_ng:.1f} ng."),
        EX("Mass of a teletherapy source", STEM("A Co-60 teletherapy source.", ["activity = 185 TBq (5000 Ci)", "S (Co-60) = 4.19 × 10<sup>13</sup> Bq/g"], "Find the [[mass of Co-60]]."),
           ["m = A / S = 1.85 × 10<sup>14</sup> / 4.19 × 10<sup>13</sup>"], f"{m_co_g:.1f} g of pure Co-60."),
    ],
    cards=[
        C("Define specific activity and give its units.", "Activity per unit mass of the radioactive material: Bq/g or Ci/g."),
        C("Write the formula for specific activity.", "S = λN<sub>A</sub>/M = ln 2 · N<sub>A</sub> / (T<sub>1/2</sub> · M), with M the molar mass in g/mol."),
        C("What raises specific activity?", "A shorter half-life and a smaller molar mass."),
        C("Rank Pd-103, I-125, Ir-192, Co-60, Cs-137, and Ra-226 by specific activity.", f"Pd-103 ({sci(S['Pd-103'])} Bq/g) > I-125 ({sci(S['I-125'])}) > Ir-192 ({sci(S['Ir-192'])}) > Co-60 ({sci(S['Co-60'])}) > Cs-137 ({sci(S['Cs-137'])}) > Ra-226 ({sci(S['Ra-226'])})."),
        C("What is the specific activity of Ra-226?", f"About {sci(S['Ra-226'])} Bq/g, close to 1 Ci per gram. That is how the curie was originally defined."),
        C("Why do real sources have lower specific activity than the theoretical value?", "Neutron-capture products still contain the stable target atoms (carrier). Ir-192 sources are mostly stable Ir-191."),
        C("Why is high specific activity needed for HDR brachytherapy?", f"A high activity fits in a small, near-point source: 370 GBq of Ir-192 is about {m_ir_mg:.1f} mg of iridium, against about {m_cs_mg:.0f} mg for Cs-137."),
        C("How does specific activity affect radiopharmaceutical therapy?", "Low specific activity means more non-radioactive carrier is given with the activity, and carrier can compete for and saturate receptor sites."),
    ],
)

PROBLEMS = [
    PR("Specific activity is defined as:", "the activity per unit mass of the radioactive material", ["the activity per unit volume of tissue", "the activity divided by the half-life", "the number of photons emitted per decay"],
       "It is A/m, in Bq/g or Ci/g.", lvl="Easy"),
    PR("Which unit is used for specific activity?", "Bq/g", ["Gy/s", "Bq·s", "Ci·h"], "Becquerels (or curies) per gram of radioactive material.", lvl="Easy"),
    PR("Two radionuclides have the same atomic mass. Which has the higher specific activity?", "The one with the shorter half-life", ["The one with the longer half-life", "They are equal", "The one that emits higher-energy photons"],
       "S ∝ 1/(T<sub>1/2</sub> · M). With M equal, a shorter half-life means more decays per atom per second.", lvl="Easy"),
    PR("Why is a high specific activity valuable for an HDR brachytherapy source?", "A high activity fits in a small, nearly point-like source", ["It lengthens the half-life", "It raises the photon energy", "It lowers the exposure rate constant"],
       "A small source passes through narrow catheters and approximates a point, which simplifies dose calculation.", lvl="Easy"),
    PRN(STEM("A hypothetical nuclide.", ["T<sub>1/2</sub> = 100 d", "molar mass = 100 g/mol"], "What is its [[specific activity]]?"), hyp, [hyp / calc.LN2, hyp * 86400, hyp * 100], lambda v: sci(v) + " Bq/g",
        f"λ = 0.693 / (100 × 86,400 s) = 8.02 × 10<sup>−8</sup> s<sup>−1</sup>. Atoms per gram = 6.022 × 10<sup>23</sup> / 100 = 6.02 × 10<sup>21</sup>. S = {sci(hyp)} Bq/g. Leaving out the ln 2 gives {sci(hyp / calc.LN2)}; leaving the half-life in days gives {sci(hyp * 86400)}; forgetting to divide by the molar mass gives {sci(hyp * 100)}.", lvl="Moderate"),
    PRN(STEM("", ["S (Ir-192) = 3.4 × 10<sup>14</sup> Bq/g", "activity = 370 GBq (10 Ci)"], "About what [[mass of Ir-192]] gives this activity?"), m_ir_given_mg, [m_ir_given_mg / 10, m_ir_given_mg * 10, m_ir_given_mg * 100], "{:.3g} mg",
        f"m = A/S = 3.7 × 10<sup>11</sup> Bq / 3.4 × 10<sup>14</sup> Bq/g = {sci(m_ir_given_mg / 1e3, 3)} g = {m_ir_given_mg:.2f} mg.", lvl="Moderate",
        calc=CALC("mg", [TILE("A", 370, "GBq"), TILE("S", 3.4e14, "Bq/g", disp="3.4 × 10¹⁴"), CONV("GBq", "Bq", 1e9), CONV("g", "mg", 1e3), TILE("T½", 73.8, "d", id="T")], solution=["A", "×", "GBq→Bq", "÷", "S", "×", "g→mg"])),
    PR("The activity of 1 g of Ra-226 is closest to:", "1 Ci (3.7 × 10<sup>10</sup> Bq)", ["1 mCi", "1 GBq", "1 kCi"],
       f"S = {sci(S['Ra-226'], 3)} Bq/g = {ci('Ra-226'):.2f} Ci/g. The curie was defined from this.", lvl="Moderate"),
    PRN(STEM("Compare two seed isotopes.", ["Pd-103: T<sub>1/2</sub> = 17.0 d, M = 102.9 g/mol", "I-125: T<sub>1/2</sub> = 59.4 d, M = 124.9 g/mol"], "The specific activity of Pd-103 is how many [[times that of I-125]]?"), pd_over_i, [1.0, 0.24, 12.0], "{:.2g}",
        f"S ∝ 1/(T<sub>1/2</sub> · M). Ratio = (59.4 / 17.0) × (124.9 / 102.9) = {59.4 / 16.99:.2f} × {124.9 / 102.9:.2f} = {pd_over_i:.1f}.", lvl="Moderate"),
    PR("If the half-life and the molar mass of a nuclide were both doubled, its specific activity would:", "fall to one quarter", ["fall to one half", "stay the same", "double"],
       "S ∝ 1/(T<sub>1/2</sub> · M). Doubling both divides S by 4.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3, 10]}

TERMS = ['specific activity', 'carrier']

TAKE = [
    [('S = ln 2 · N<sub>A</sub> / (T<sub>1/2</sub> · M): a shorter half-life and a lighter atom raise it.', 'sa-formula'), ('Order: Pd-103 > I-125 > Ir-192 > Co-60 > Cs-137 > Ra-226. 1 g of Ra-226 is about 1 Ci.', 'sa-order')],
    [('High specific activity gives a small source: 10 Ci of Ir-192 is about 1 mg.', 'source-size'), ('Practical sources contain stable carrier atoms, so they fall short of the theoretical value.', 'carrier-atoms')],
]


# ---------------------------------------------------------------- ranking and typed-number questions
PROBLEMS += [
    SORT("Rank these nuclides by specific activity, highest first.", ["1st (highest)", "2nd", "3rd", "4th", "5th", "6th (lowest)"],
         [("Pd-103", 0), ("I-125", 1), ("Ir-192", 2), ("Co-60", 3), ("Cs-137", 4), ("Ra-226", 5)],
         f"S = ln 2 · N<sub>A</sub> / (T<sub>1/2</sub> · M), so a short half-life and a light atom raise it. In Bq/g: Pd-103 {sci(S['Pd-103'])}, I-125 {sci(S['I-125'])}, Ir-192 {sci(S['Ir-192'])}, Co-60 {sci(S['Co-60'])}, Cs-137 {sci(S['Cs-137'])}, and Ra-226 {sci(S['Ra-226'])}, which is about 1 Ci/g.", lvl="Moderate", mode="rank", cap=1),
]
