from blocks import *
import calc

tmr10 = calc.tmr_from_pdd(67.0, 100, 10, 1.5)
k = ((100 + 10) / (100 + 1.5)) ** 2

TOPIC = dict(
    id="tmr", domain=3, sub="III.A", title="TMR and the SAD technique",
    ref=dict(aapm="8.1", khan="9, 10", ford="11"),
    guide=[
        H("Limits of PDD"),
        P("PDD depends on the SSD. In an isocentric treatment the SSD changes with every beam angle and patient contour, while the distance from the source to the point of interest stays fixed. A quantity that does not depend on the SSD makes dose calculation at the isocenter simpler."),

        H("TAR, TMR, and TPR"),
        TABLE(["Quantity", "Definition", "Notes"], [
            ["TAR", "Dose at depth d in the phantom ÷ dose that the same beam gives at that point in free space", "Independent of SSD. Used for kilovoltage and Co-60. The backscatter factor (BSF, peak scatter factor at megavoltage energies) is TAR at d<sub>max</sub>."],
            ["TMR", "Dose at depth d ÷ dose at d<sub>max</sub>, at the same point", "1 at d<sub>max</sub>. Depends on depth, energy, and the field size at depth. Independent of SSD."],
            ["TPR", "Dose at depth d ÷ dose at a reference depth, at the same point", "TMR is the TPR whose reference depth is d<sub>max</sub>. TPR<sub>20,10</sub> uses 20 and 10 cm."]]),
        EQ("TMR(d, A<sub>d</sub>) = D<sub>P</sub>(depth d) / D<sub>P</sub>(depth d<sub>max</sub>)"),
        P("TMR assumes the scatter at a point depends on the field size at that point and the thickness above it, not on the divergence of the beam, so it can be independent of SSD."),
        FIG("pdd_vs_tmr", "PDD compares two points at different distances from the source. TMR compares the same point with different thicknesses of phantom above it."),

        H("PDD compared with TMR"),
        TABLE(["", "PDD", "TMR"], [
            ["How it is measured", "Surface fixed; detector moves in depth", "Point fixed; phantom thickness above it changes"],
            ["Source-to-point distance", "Changes with depth", "Constant"],
            ["Includes inverse square", "Yes", "No"],
            ["Depends on SSD", "Yes", "No"],
            ["Field size", "At the surface", "At the point's depth"],
            ["Used for", "SSD technique, extended SSD, electrons", "SAD (isocentric) technique"]]),

        H("Converting PDD to TMR"),
        EQ("TMR(d, A<sub>d</sub>) = PDD(d, A, f)/100 × [(f + d)/(f + d<sub>max</sub>)]<sup>2</sup> × S<sub>p</sub>(A<sub>dmax</sub>)/S<sub>p</sub>(A<sub>d</sub>)"),
        P("A is the field at the surface, A<sub>d</sub> = A(f + d)/f is the field at depth d, and A<sub>dmax</sub> = A(f + d<sub>max</sub>)/f is the field at d<sub>max</sub>. The squared factor corrects for the two points being at different distances from the source. The S<sub>p</sub> ratio corrects for the different field sizes at the two planes, and is close to 1 for modest depths."),
        EX("PDD to TMR", STEM("A 6 MV beam.", ["d<sub>max</sub> = 1.5 cm", "PDD = 67.0% at 10 cm depth, SSD 100 cm", "S<sub>p</sub> ratio = 1"], "Estimate the [[TMR]] at 10 cm."),
           [f"[(100 + 10)/(100 + 1.5)]² = (110/101.5)² = {k:.3f}.", f"TMR = 0.670 × {k:.3f}."], f"About {tmr10:.3f}."),

    ],
    cards=[
        C("Why was TMR introduced?", "PDD depends on SSD, which changes with each beam in an isocentric treatment. TMR does not depend on SSD, so dose at the isocenter is simpler to calculate."),
        C("Define TMR.", "The dose at depth d divided by the dose at d<sub>max</sub> at the same point in space, with the same field size at that point. The phantom thickness above the point is what changes.", fig="pdd_vs_tmr"),
        C("What is TMR at d<sub>max</sub>, and why?", "1.0. The numerator and denominator are the same measurement."),
        C("What does TMR depend on, and what does it not depend on?", "It depends on depth, energy, and the field size at depth. To a good approximation it does not depend on SSD."),
        C("Which calculation technique uses PDD, and which uses TMR?", "PDD: SSD technique (including extended SSD) and electrons. TMR: SAD (isocentric) technique."),
        C("How is a TMR measured?", "The detector stays at a fixed distance from the source (the isocenter) while the water thickness above it is varied. Each reading is divided by the reading with d<sub>max</sub> of water above the point."),
        C("Define TAR and the backscatter factor.", "TAR is the dose at depth in the phantom divided by the dose that the same beam gives at that point in free space. The backscatter factor (peak scatter factor at megavoltage energies) is the TAR at d<sub>max</sub>."),
        C("How do TMR and TPR differ?", "TMR uses d<sub>max</sub> as the reference depth. TPR may use any reference depth; TPR<sub>20,10</sub> compares 20 cm with 10 cm."),
        C("A 6 MV beam (d<sub>max</sub> = 1.5 cm) has PDD = 67.0% at 10 cm and SSD 100 cm. Estimate TMR at 10 cm, taking the S<sub>p</sub> ratio as 1.", f"About {tmr10:.3f}.", w=[f"TMR = PDD/100 × [(f + d)/(f + d<sub>max</sub>)]² = 0.670 × (110/101.5)² = 0.670 × {k:.3f}."]),
        C("Why does the PDD-to-TMR conversion contain [(f + d)/(f + d<sub>max</sub>)]²?", "PDD compares points at distances f + d and f + d<sub>max</sub> from the source. TMR compares the same point, so the inverse-square difference between those distances must be removed."),
        C("Which field size defines a PDD, and which defines a TMR?", "PDD: the field at the surface, A. TMR: the field at the point's depth, A<sub>d</sub> = A(f + d)/f."),
    ],
)

TERMS = ['isocentric']

TAKE = [
    [('PDD depends on SSD, and the SSD changes with every beam angle in isocentric treatments, so PDD is the wrong quantity there.', 'isocentric-ssd')],
    [('TMR = D(depth d) / D(depth d<sub>max</sub>) at the same point. It is 1 at d<sub>max</sub> and independent of SSD. TMR is the TPR whose reference depth is d<sub>max</sub>.', 'tmr-setup')],
    [('PDD goes with the SSD technique, TMR with the SAD (isocentric) technique. TMR depends on depth, energy, and the field size at depth.', 'pdd-vs-tmr')],
    [('TMR = PDD/100 × [(f + d)/(f + d<sub>max</sub>)]² × S<sub>p</sub> ratio.', 'pdd-to-tmr')],
]


# ---------------------------------------------------------------- practice questions
q_tmr15 = calc.tmr_from_pdd(58.0, 100, 15, 1.5)
q_wk = tmr10 / 0.670 - 1                          # PDD used where TMR belongs: fractional error in delivered dose
q_tmr80 = calc.tmr_from_pdd(71.0, 80, 12, 2.5, 0.99)
q_pdd120 = 67.0 * calc.mayneord_F(100, 120, 10, 1.5); q_tmr120 = calc.tmr_from_pdd(q_pdd120, 120, 10, 1.5)
_dir = lambda v: ("too high by " if v > 0 else ("too low by " if v < 0 else "no error: ")) + (f"{abs(v) * 100:.1f}%" if v else "0%")

PROBLEMS = [
    PR("Why is TMR used for isocentric treatments?", "It does not depend on SSD, which changes with every beam angle and patient contour", ["It does not depend on the beam energy", "It does not depend on the field size", "It already includes the inverse-square fall-off"],
       "In an isocentric treatment the point of interest stays at the same distance from the source while the SSD changes with the gantry angle and the patient's contour. TMR does not depend on SSD, so it fits. It still depends on energy, depth, and field size.", lvl="Easy"),
    PR("TMR is the ratio of the dose at depth d to the dose at d<sub>max</sub>, both measured:", "at the same point in space, with the thickness of phantom above the point changed", ["at the same SSD, with the detector moved in depth", "at the same point in free space, with no phantom", "at the surface, for a 10 × 10 cm field"],
       "For TMR the detector stays put and the phantom above it is made thicker or thinner, so the source-to-point distance is constant. Moving the detector in depth at a fixed SSD gives PDD, and the free-space reference gives TAR.", lvl="Easy"),
    PR("What is the TMR at d<sub>max</sub>?", "1.000", ["the backscatter factor, about 1.05", "0.500", "It depends on the SSD"],
       "TMR is the dose at depth d divided by the dose at d<sub>max</sub>, so at d<sub>max</sub> it is 1 by definition. The backscatter or peak scatter factor is the TAR at d<sub>max</sub>.", lvl="Easy"),
    PR("TMR is a special case of the tissue phantom ratio (TPR). Its reference depth is:", "d<sub>max</sub>", ["10 cm", "5 cm", "the surface"],
       "TPR compares the dose at depth d with the dose at any fixed reference depth. TMR is the TPR whose reference depth is d<sub>max</sub>.", lvl="Easy"),
    PRM("Which of the following does the TMR depend on?", ["Beam energy", "Field size at the point", "Depth"], ["SSD", "Prescribed dose"],
        "TMR depends on the energy, the depth, and the field size at the point. It does not depend on the SSD, and the amount of dose cancels in the ratio.", lvl="Moderate"),
    PR("For a 6 MV beam at SSD 100 cm, how do PDD and TMR compare at a depth of 10 cm?", "TMR is larger, because PDD also includes the inverse-square fall-off from d<sub>max</sub> to 10 cm", ["PDD is larger, because it includes scatter from the surface", "They are equal at 10 cm", "They differ only when the field sizes differ"],
       "PDD compares two points at different distances from the source, so it contains the inverse-square fall-off. TMR compares the same point, so it does not. For 6 MV at 10 cm depth and SSD 100 cm, PDD is 0.670 and TMR is 0.787.", lvl="Moderate"),
    PR("In the PDD-to-TMR conversion, what does the factor S<sub>p</sub>(A<sub>dmax</sub>) / S<sub>p</sub>(A<sub>d</sub>) correct for?", "The different field sizes in the d<sub>max</sub> plane and in the plane at depth d, because the beam diverges", ["The attenuation of the beam between d<sub>max</sub> and d", "The different SSDs of the two measurements", "Scatter from the collimators"],
       "The two planes are at different distances from the source, so the same beam covers a different field size in each. S<sub>p</sub> depends on that field size. The ratio is close to 1 at modest depths.", lvl="Moderate"),
    PRN(STEM("A 6 MV beam.", ["d<sub>max</sub> = 1.5 cm", "PDD = 58.0% at 15 cm depth, SSD 100 cm", "S<sub>p</sub> ratio = 1"], "Estimate the [[TMR]] at 15 cm depth."), q_tmr15, [0.58, 0.58 * (115 / 101.5), 0.58 * (101.5 / 115) ** 2], "{:.3f}",
        f"Using the PDD unchanged gives 0.580, leaving out the square gives {0.58 * (115 / 101.5):.3f}, and inverting the ratio gives {0.58 * (101.5 / 115) ** 2:.3f}.",
        w=[STEP("Distance factor", "F = [(f + d) / (f + d<sub>max</sub>)]²", f"F = (115 / 101.5)²", f"{((100 + 15) / (100 + 1.5)) ** 2:.3f}", "f is the SSD, d the depth, and d<sub>max</sub> the depth of maximum dose, all in cm"),
           STEP("TMR", "TMR = (PDD / 100) × F × S<sub>p</sub> ratio", f"TMR = 0.580 × {((100 + 15) / (100 + 1.5)) ** 2:.3f} × 1", f"{q_tmr15:.3f}", "S<sub>p</sub> ratio = S<sub>p</sub>(A<sub>dmax</sub>) / S<sub>p</sub>(A<sub>d</sub>), given as 1")], lvl="Moderate",
        calc=CALC("", [TILE("PDD", 0.58, "", disp="0.580"), TILE("f", 100, "cm"), TILE("d", 15, "cm"), TILE("dmax", 1.5, "cm", id="dm")], ops=("+", "×", "÷", "(", ")", "²"), solution=["PDD", "×", "(", "(", "f", "+", "d", ")", "÷", "(", "f", "+", "dm", ")", ")", "²"])),
    PRN(STEM("An isocentric 6 MV treatment at 10 cm depth is calculated with the SSD-100 PDD in place of the TMR.", ["PDD at 10 cm = 0.670", "TMR at 10 cm = 0.787 (d<sub>max</sub> = 1.5 cm)"], "How is the [[dose delivered at the isocenter]] wrong?"), q_wk, [1 / (tmr10 / 0.670) - 1, (tmr10 / 0.670) ** 2 - 1, 0.0], _dir,
        f"The MU come from dose ÷ (dose per MU), and the PDD (0.670) is smaller than the TMR (0.787), so too many MU are set. The error is {tmr10:.3f}/0.670 − 1 = {q_wk * 100:.1f}% too high. The opposite sign is the factor inverted; squaring the factor gives {((tmr10 / 0.670) ** 2 - 1) * 100:.1f}%.", lvl="Moderate"),
    PRN(STEM("A 10 MV beam.", ["d<sub>max</sub> = 2.5 cm", "PDD = 71.0% at 12 cm depth, SSD 80 cm", "S<sub>p</sub>(A<sub>dmax</sub>) / S<sub>p</sub>(A<sub>d</sub>) = 0.99"], "Estimate the [[TMR]] at 12 cm depth."), q_tmr80, [0.71, calc.tmr_from_pdd(71.0, 80, 12, 2.5), calc.tmr_from_pdd(71.0, 80, 12, 2.5, 1 / 0.99)], "{:.3f}",
        f"TMR = 0.710 × (92/82.5)² × 0.99 = 0.710 × {(92/82.5)**2:.3f} × 0.99 = {q_tmr80:.3f}. Leaving out the S<sub>p</sub> ratio gives {calc.tmr_from_pdd(71.0, 80, 12, 2.5):.3f}, applying it upside down gives {calc.tmr_from_pdd(71.0, 80, 12, 2.5, 1 / 0.99):.3f}, and skipping the conversion gives 0.710.", lvl="Challenging",
        calc=CALC("", [TILE("PDD", 0.71, "", disp="0.710"), TILE("f", 80, "cm"), TILE("d", 12, "cm"), TILE("dmax", 2.5, "cm", id="dm"), TILE("Sp ratio", 0.99, "", id="r")], ops=("+", "×", "÷", "(", ")", "²"), solution=["PDD", "×", "(", "(", "f", "+", "d", ")", "÷", "(", "f", "+", "dm", ")", ")", "²", "×", "r"])),
    PR("Two setups irradiate a point at 10 cm depth with a 10 × 10 cm field at the point. In setup A the point is 100 cm from the source. In setup B it is 120 cm from the source. How do the TMR values compare?", "They are equal, because TMR does not depend on the distance from the source", ["Setup A is larger, because of the inverse-square fall-off", "Setup B is larger, because the inverse-square fall-off is smaller", "They differ by the ratio (120/100)²"],
       "TMR compares the same point with two thicknesses of phantom above it, so the source-to-point distance cancels. For the same depth, energy, and field size at the point, TMR is the same. PDD would differ between the two setups.", lvl="Challenging"),
    PRN(STEM("A 6 MV beam with PDD data from SSD 120 cm.", ["d<sub>max</sub> = 1.5 cm", "PDD = 68.7% at 10 cm depth, SSD 120 cm", "S<sub>p</sub> ratio = 1"], "Find the [[TMR]] at 10 cm depth."), q_tmr120, [q_pdd120 / 100, q_pdd120 / 100 * (130 / 121.5), q_pdd120 / 100 * (130 / 121.5) ** -2], "{:.3f}",
        f"TMR = 0.687 × (130/121.5)² = 0.687 × {(130/121.5)**2:.3f} = {q_tmr120:.3f}, the same as from the SSD-100 data ({tmr10:.3f}). Converting PDD to TMR removes the SSD dependence. Skipping the conversion gives {q_pdd120 / 100:.3f}, and leaving out the square gives {q_pdd120 / 100 * (130 / 121.5):.3f}.", lvl="Challenging",
        calc=CALC("", [TILE("PDD", q_pdd120 / 100, "", disp="0.687"), TILE("f", 120, "cm"), TILE("d", 10, "cm"), TILE("dmax", 1.5, "cm", id="dm")], ops=("+", "×", "÷", "(", ")", "²"), solution=["PDD", "×", "(", "(", "f", "+", "d", ")", "÷", "(", "f", "+", "dm", ")", ")", "²"])),
]

INLINE = {0: [0], 1: [1, 2], 2: [5], 3: [7, 8]}


# ---------------------------------------------------------------- practice questions that use a data table
import beamdata as bd
q_tm_ratio = bd.TMR[(20, 10)] / bd.TMR[(10, 10)] - 1
_f60 = (bd.TMR[(16, 10)] - 0.600) / (bd.TMR[(16, 10)] - bd.TMR[(18, 10)])                  # 0.600 lies between the 16 and 18 cm rows
q_tm_d60 = 16 + _f60 * 2
_sgn = lambda v: f"{v * 100:+.1f}%".replace("-", "−")

PROBLEMS += [
    PRN(STEM("An isocentric 6 MV treatment with a 10 × 10 cm field at the isocenter, delivered with the same MU in two setups. The isocenter is at 10 cm depth in one and 20 cm in the other. Use the table.", [],
             "By how much does the [[dose at the isocenter]] change from the 10 cm setup to the 20 cm setup?", tables=[bd.table_tmr([5, 10, 14, 20, 25], [10])]),
        q_tm_ratio, [bd.TMR[(10, 10)] / bd.TMR[(20, 10)] - 1, bd.TMR[(20, 10)] - bd.TMR[(10, 10)], bd.TMR[(25, 10)] / bd.TMR[(10, 10)] - 1], _sgn,
        f"The dose at the isocenter is proportional to the TMR, so the change is TMR(20)/TMR(10) − 1 = {bd.TMR[(20, 10)]:.3f}/{bd.TMR[(10, 10)]:.3f} − 1 = {_sgn(q_tm_ratio)}. Inverting the ratio gives {_sgn(bd.TMR[(10, 10)] / bd.TMR[(20, 10)] - 1)}, subtracting the TMRs gives {_sgn(bd.TMR[(20, 10)] - bd.TMR[(10, 10)])}, and reading the 25 cm row gives {_sgn(bd.TMR[(25, 10)] / bd.TMR[(10, 10)] - 1)}.", lvl="Moderate",
        calc=CALC("", [TILE("T20", bd.TMR[(20, 10)], "", disp=f"{bd.TMR[(20, 10)]:.3f}"), TILE("T10", bd.TMR[(10, 10)], "", disp=f"{bd.TMR[(10, 10)]:.3f}"), TILE("1", 1)], ops=("−", "÷"), solution=["T20", "÷", "T10", "−", "1"])),
    PRN(STEM("A 6 MV beam with a 10 × 10 cm field at the point. Use the table.", [], "At what [[depth]] is the TMR equal to 0.600? Interpolate linearly.", tables=[bd.table_tmr([14, 16, 18, 20, 25], [10])]),
        q_tm_d60, [16.0, 18.0, 17.0], "{:.1f} cm",
        f"0.600 lies between {bd.TMR[(16, 10)]:.3f} at 16 cm and {bd.TMR[(18, 10)]:.3f} at 18 cm. The fraction of the way is ({bd.TMR[(16, 10)]:.3f} − 0.600) / ({bd.TMR[(16, 10)]:.3f} − {bd.TMR[(18, 10)]:.3f}) = {_f60:.2f}, so d = 16 + {_f60:.2f} × 2 = {q_tm_d60:.1f} cm. The midpoint, 17.0 cm, ignores where 0.600 sits between the two values.", lvl="Moderate"),
]
INLINE = {0: [0], 1: [1, 2], 2: [5, 12], 3: [7, 8]}


# ---------------------------------------------------------------- sorting question
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Does each statement describe the PDD or the TMR?", ["PDD", "TMR"],
         [("Includes the inverse-square fall-off", 0), ("Does not depend on SSD", 1), ("Field size is defined at the surface", 0), ("Field size is defined at the depth of the point", 1),
          ("Used to calculate SAD treatments", 1), ("Used to calculate SSD treatments", 0), ("Source-to-point distance changes with depth", 0), ("Source-to-point distance stays the same", 1)],
         "The PDD compares doses along one ray at a fixed SSD, so the distance from the source changes with depth and the inverse-square fall-off is built in. The TMR compares doses at the same distance from the source, with the field size defined at the depth of the point, so it has no SSD dependence and suits isocentric (SAD) setups.", lvl="Moderate"),
]
INLINE = {0: [1], 1: [2, 3, 5], 2: [6, 9, _n0 + 1], 3: [7, 8]}
