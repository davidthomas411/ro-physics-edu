from blocks import *
import calc

# Example 1: SSD technique at SSD 100 cm
sc1, sp1, pdd1 = 1.012, 1.008, 74.8
dpm1 = sc1 * sp1 * pdd1 / 100; mu1 = 200 / dpm1
# Example 2: extended SSD 120 cm, same prescription
ac2 = 12 * 100 / 120; sc2, sp2, pdd2 = 1.000, 1.008, 76.2
iv2 = ((100 + 1.5) / (120 + 1.5)) ** 2
dpm2 = sc2 * sp2 * pdd2 / 100 * iv2; mu2 = 200 / dpm2
# Example 3: SAD technique, parallel-opposed pair
es3 = calc.equiv_square(14, 16); sc3, sp3, tmr3 = 1.021, 1.013, 0.776
cal = ((100 + 1.5) / 100) ** 2             # SSD calibration, SAD technique: the calibration point is at 101.5 cm, the isocenter at 100 cm
cal_inv = (100 / (100 + 1.5)) ** 2         # SAD calibration, SSD technique at SSD 100 cm
iv120_sad = (100 / (120 + 1.5)) ** 2
dpm3_sad = sc3 * sp3 * tmr3; mu3_sad = 100 / dpm3_sad      # the pair under SAD calibration
dpm3 = dpm3_sad * cal; mu3 = 100 / dpm3                    # the pair under SSD calibration (this clinic)
# Example 4: the patient of Example 1 under SAD calibration
dpm4 = dpm1 * cal_inv; mu4 = 200 / dpm4

TOPIC = dict(
    id="mu-calc", domain=3, sub="III.A", title="Monitor unit calculations",
    ref=dict(aapm="8.2", khan="10", ford="11"),
    guide=[
        H("Monitor unit calculation"),
        P("A monitor-unit calculation starts from a known point dose, the calibration, and applies correction factors to reach the dose per MU in the treatment geometry."),
        EQ("MU = prescribed dose at the point / dose per MU at the point"),

        H("Reference conditions"),
        P("Linacs are commonly calibrated to give 1 cGy per MU at d<sub>max</sub> in water for a 10 × 10 cm field. The two conventions differ in where that d<sub>max</sub> point sits, which sets the calibration distance d<sub>cal</sub> from the source. SSD calibration is the convention used at this clinic. SAD calibration is common elsewhere and on exam problems, so both are worked here. Every question says which one it uses."),
        TABLE(["", "SSD calibration (this clinic)", "SAD calibration"], [
            ["Where 1 cGy/MU is delivered", "d<sub>max</sub>, with the surface at 100 cm", "d<sub>max</sub>, with the point at 100 cm"],
            ["Calibration distance d<sub>cal</sub>", "100 + d<sub>max</sub> (101.5 cm for 6 MV)", "100 cm"]]),
        EQ("inverse-square term = (d<sub>cal</sub> / d)²", "d = source-to-point distance in the treatment: f + d<sub>max</sub> for the SSD technique, 100 cm for the SAD technique"),
        P("The dose per MU at the treatment point differs from the calibration by the inverse square of the two distances. This one rule gives every inverse-square term in the chapter:"),
        TABLE(["Inverse-square term (d<sub>max</sub> = 1.5 cm)", "SSD technique, SSD f", "SAD technique"], [
            ["SSD calibration", f"[(100 + d<sub>max</sub>)/(f + d<sub>max</sub>)]²: 1.000 at f = 100, {(101.5 / 121.5) ** 2:.3f} at f = 120", f"[(100 + d<sub>max</sub>)/100]² = {cal:.3f}"],
            ["SAD calibration", f"[100/(f + d<sub>max</sub>)]²: {cal_inv:.3f} at f = 100, {iv120_sad:.3f} at f = 120", "1 (none)"]]),
        P(f"The two calibrations are different machine settings, about {100 * (cal - 1):.0f}% apart. A machine calibrated at SSD 100 cm delivers {cal:.3f} cGy/MU at the isocenter, because the isocenter is nearer the source than the calibration point. Confirm which convention applies before using any inverse-square term."),

        H("SSD technique"),
        EQ("Dose/MU = Ḋ<sub>0</sub> · S<sub>c</sub>(A<sub>c</sub>) · S<sub>p</sub>(A) · PDD(d, A, f)/100 · [d<sub>cal</sub>/(f + d<sub>max</sub>)]² · WF · TF"),
        UL("Ḋ<sub>0</sub> = 1 cGy/MU at d<sub>max</sub>, 10 × 10 cm, at distance d<sub>cal</sub>.",
           "A is the field at the surface. A<sub>c</sub> is the collimator opening projected to 100 cm, A × 100/f.",
           f"With SSD calibration d<sub>cal</sub> = 100 + d<sub>max</sub>, so the term is 1 at f = 100 cm and below 1 at an extended SSD, which raises the MU. With SAD calibration d<sub>cal</sub> = 100 cm, so the term is already {cal_inv:.3f} at f = 100 cm."),

        H("SAD technique"),
        EQ("Dose/MU = Ḋ<sub>0</sub> · S<sub>c</sub>(A<sub>c</sub>) · S<sub>p</sub>(A<sub>d</sub>) · TMR(d, A<sub>d</sub>) · (d<sub>cal</sub>/100)² · WF · TF"),
        UL("A<sub>d</sub> is the field at the isocenter plane, and d is the depth of the isocenter.",
           "The point stays at 100 cm, so the only inverse-square term comes from the calibration distance.",
           f"With SSD calibration it is [(100 + d<sub>max</sub>)/100]² = {cal:.3f}, a 3% gain in dose per MU. With SAD calibration it is 1."),

        H("Beam modifiers"),
        TABLE(["Factor", "Meaning", "Effect on MU"], [
            ["WF (wedge factor)", "Dose with the wedge ÷ dose without, at the same point and field size", "MU × 1/WF"],
            ["TF (tray factor)", "Transmission through the blocking tray", "MU × 1/TF"],
            ["OAR (off-axis ratio)", "Dose at an off-axis point ÷ dose on the axis at the same depth", "Applies when the point is off the central axis"]]),

        H("Worked examples"),
        EX("SSD technique, SSD 100 cm",
           STEM("A 6 MV beam with an SSD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm.", ["prescription = 200 cGy at d = 8 cm", "field = 12 × 12 cm at the surface, SSD 100 cm", "S<sub>c</sub>(12 × 12) = 1.012", "S<sub>p</sub>(12 × 12) = 1.008", "PDD(8 cm, 12 × 12, SSD 100) = 74.8%"], "Find the [[monitor units]]."),
           [f"Dose/MU = 1 × 1.012 × 1.008 × 0.748 = {dpm1:.4f} cGy/MU.", f"MU = 200 / {dpm1:.4f} = {mu1:.1f}."], f"{mu1:.0f} MU."),
        EX("Extended SSD, 120 cm",
           STEM("Same prescription and field as the previous example, now at an extended SSD.", ["SSD = 120 cm", "field = 12 × 12 cm at the surface", "PDD(8 cm, 12 × 12, SSD 120) = 76.2%"], "Find the [[monitor units]]."),
           [f"Collimator opening = 12 × 100/120 = {ac2:.0f} cm, so S<sub>c</sub>(10 × 10) = 1.000. S<sub>p</sub> still uses the 12 × 12 cm field at the surface: 1.008.",
            f"Inverse square: (101.5/121.5)² = {iv2:.4f}.", f"Dose/MU = 1.000 × 1.008 × 0.762 × {iv2:.4f} = {dpm2:.4f} cGy/MU.", f"MU = 200 / {dpm2:.4f} = {mu2:.1f}."],
           f"{mu2:.0f} MU, {100*(mu2/mu1-1):.0f}% more than at SSD 100 cm. The inverse square outweighs the small gain in PDD."),
        EX("SAD technique, parallel-opposed pair, SSD calibration",
           STEM("A 6 MV AP/PA pair with equal weights and a patient separation of 22 cm, with an SSD calibration.", ["prescription = 200 cGy at mid-plane, so 100 cGy per field at depth 11 cm", "field at the isocenter = 14 × 16 cm", "S<sub>c</sub> = 1.021", "S<sub>p</sub> = 1.013", "TMR(11 cm, equivalent square) = 0.776"], "Find the [[monitor units per field]]."),
           [f"Equivalent square = 2 × 14 × 16 / 30 = {es3:.1f} cm (use it to read the tables).", f"Inverse square = (101.5/100)² = {cal:.3f}, because the calibration point is farther from the source than the isocenter.", f"Dose/MU = 1.021 × 1.013 × 0.776 × {cal:.3f} = {dpm3:.4f} cGy/MU.", f"MU per field = 100 / {dpm3:.4f} = {mu3:.1f}."],
           f"{mu3:.0f} MU per field. With a SAD calibration there is no {cal:.3f} factor and the result is {mu3_sad:.0f} MU."),
        EX("Example 1 with a SAD calibration",
           STEM("The patient, field, and factors of Example 1, now on a machine with a SAD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm with the point at 100 cm.", ["prescription = 200 cGy at d = 8 cm", "field = 12 × 12 cm at the surface, SSD 100 cm", "S<sub>c</sub> = 1.012, S<sub>p</sub> = 1.008, PDD = 74.8%"], "Find the [[monitor units]]."),
           [f"Inverse square = [100/(100 + 1.5)]² = {cal_inv:.4f}, because the point at d<sub>max</sub> is now 101.5 cm from the source and the calibration point is at 100 cm.", f"Dose/MU = 1.012 × 1.008 × 0.748 × {cal_inv:.4f} = {dpm4:.4f} cGy/MU.", f"MU = 200 / {dpm4:.4f} = {mu4:.1f}."],
           f"{mu4:.0f} MU, {100 * (mu4 / mu1 - 1):.0f}% more than the {mu1:.0f} MU with SSD calibration."),
        P('To practise whole calculations, with full tables for 6, 10, 15, and 18 MV and a check on every factor, open <a href="#mu">MU calc</a>.'),
    ],
    cards=[
        C("What does a hand MU calculation do?", "It starts from the calibration (1 cGy/MU at a reference point) and applies correction factors for field size, depth, distance, and beam modifiers to give the dose per MU in the treatment geometry. MU = prescribed dose ÷ dose per MU."),
        C("Write the dose-per-MU equation for the SSD technique.", "Ḋ<sub>0</sub> · S<sub>c</sub>(A<sub>c</sub>) · S<sub>p</sub>(A) · PDD/100 · [d<sub>cal</sub>/(f + d<sub>max</sub>)]² · WF · TF. With SSD calibration d<sub>cal</sub> = 100 + d<sub>max</sub>, so the inverse-square term is 1 at SSD 100 cm."),
        C("Write the dose-per-MU equation for the SAD technique.", f"Ḋ<sub>0</sub> · S<sub>c</sub>(A<sub>c</sub>) · S<sub>p</sub>(A<sub>d</sub>) · TMR(d, A<sub>d</sub>) · (d<sub>cal</sub>/100)² · WF · TF. The inverse-square term is {cal:.3f} with SSD calibration and 1 with SAD calibration."),
        C("Which scatter factor uses the collimator opening, and which uses the field at the phantom?", "S<sub>c</sub> uses the collimator opening (projected to 100 cm). S<sub>p</sub> uses the field that irradiates the phantom: at the surface for the SSD technique, at the isocenter plane for the SAD technique."),
        C("At SSD 120 cm, what collimator setting gives a 12 × 12 cm field at the surface?", "10 × 10 cm.", w=["A<sub>c</sub> = A × 100/f = 12 × 100/120 = 10."]),
        C("6 MV, calibrated 1 cGy/MU at d<sub>max</sub> = 1.5 cm, SSD 100. Deliver 200 cGy at 8 cm depth, 12 × 12 cm at the surface, SSD 100. S<sub>c</sub> = 1.012, S<sub>p</sub> = 1.008, PDD = 74.8%. How many MU?", f"{mu1:.0f} MU.", w=[f"Dose/MU = 1.012 × 1.008 × 0.748 = {dpm1:.4f}.", f"MU = 200 / {dpm1:.4f} = {mu1:.1f}."]),
        C("Repeat that calculation at SSD 120 cm, 12 × 12 cm at the surface. PDD at SSD 120 = 76.2%.", f"{mu2:.0f} MU.", w=[f"A<sub>c</sub> = 10, so S<sub>c</sub> = 1.000. S<sub>p</sub>(12 × 12) = 1.008.", f"Inverse square = (101.5/121.5)² = {iv2:.4f}.", f"Dose/MU = 1.008 × 0.762 × {iv2:.4f} = {dpm2:.4f}.", f"MU = 200 / {dpm2:.4f} = {mu2:.1f}."]),
        C("6 MV AP/PA pair, separation 22 cm, equal weights, SSD calibration. 100 cGy per field at the 11 cm mid-plane isocenter. S<sub>c</sub> = 1.021, S<sub>p</sub> = 1.013, TMR = 0.776. MU per field?", f"{mu3:.0f} MU.", w=[f"Dose/MU = 1.021 × 1.013 × 0.776 × {cal:.3f} = {dpm3:.4f}.", f"MU = 100 / {dpm3:.4f} = {mu3:.1f}. With a SAD calibration (no {cal:.3f} factor) it would be {mu3_sad:.0f} MU."]),
        C("Why does the MU increase at extended SSD even though PDD rises?", f"The inverse-square factor ({iv2:.2f} for SSD 120 versus 100) outweighs the roughly 2% gain in PDD."),
        C("A wedge has WF = 0.60. By what factor do the MU change?", "MU increase by 1/0.60 = 1.67, a 67% increase."),
        C("A blocking tray transmits 97% of the beam. What is TF, and how do the MU change?", "TF = 0.97, so MU increase by 1/0.97 = 1.031, about 3%."),
        C("A machine has an SSD calibration and is used isocentrically. What extra factor applies (d<sub>max</sub> = 1.5 cm)?", f"[(100 + 1.5)/100]² = {cal:.3f}, about 3%. The calibration point is farther from the source than the isocenter, so the dose per MU at the isocenter is higher.", w=["With a SAD calibration the factor is 1."]),
        C("Why is TMR rather than PDD used for isocentric calculations?", "TMR does not depend on SSD, and the point of calculation stays at the SAD, so the only inverse-square term comes from the calibration distance."),
        C("What distinguishes SSD calibration from SAD calibration?", "Where the 1 cGy/MU point at d<sub>max</sub> sits. SSD calibration puts the surface at 100 cm, so the point is at 100 + d<sub>max</sub> from the source (the convention at this clinic). SAD calibration puts the point at 100 cm."),
        C("State the rule for the inverse-square term in an MU calculation.", "(d<sub>cal</sub> / d)², where d<sub>cal</sub> is the source-to-point distance at calibration (100 + d<sub>max</sub> or 100 cm) and d is the source-to-point distance in the treatment (f + d<sub>max</sub> for the SSD technique, 100 cm for the SAD technique)."),
        C("Give the inverse-square term for each calibration and technique at SSD 100 cm and the SAD (d<sub>max</sub> = 1.5 cm).", f"SSD calibration: SSD technique 1.000, SAD technique {cal:.3f}. SAD calibration: SSD technique {cal_inv:.3f}, SAD technique 1.000."),
        C("Repeat Example 1 on a machine with a SAD calibration. How many MU?", f"{mu4:.0f} MU, about 3% more than the {mu1:.0f} MU with SSD calibration.", w=[f"Inverse square = [100/(100 + 1.5)]² = {cal_inv:.4f}.", f"Dose/MU = {dpm1:.4f} × {cal_inv:.4f} = {dpm4:.4f}.", f"MU = 200 / {dpm4:.4f} = {mu4:.1f}."]),
    ],
)

TERMS = ['monitor-unit calculation', 'SSD calibration', 'SAD calibration']

TAKE = [
    [('MU = dose ÷ (dose per MU). Dose per MU = calibration × the factors converting the reference geometry to the treatment geometry.', 'mu-chain')],
    [('Calibration is 1 cGy/MU at d<sub>max</sub> for 10 × 10 cm. The inverse-square term is (d<sub>cal</sub>/d)²: d<sub>cal</sub> = 100 + d<sub>max</sub> for SSD calibration (this clinic) and 100 cm for SAD calibration.', 'calibration-points')],
    [('SSD technique: dose per MU = calibration × S<sub>c</sub> · S<sub>p</sub> · PDD/100 × (d<sub>cal</sub>/(f + d<sub>max</sub>))². With SSD calibration the term is 1 at SSD 100 cm.', 'ssd-formula'), ('At an extended SSD the term is below 1 and raises the MU.', 'ssd-term')],
    [('SAD technique: dose per MU = calibration × S<sub>c</sub> · S<sub>p</sub> · TMR × (d<sub>cal</sub>/100)²: 1.030 for SSD calibration and 1 for SAD calibration.', 'sad-formula')],
    [('WF and TF multiply the dose per MU, so MU scale as 1/WF and 1/TF.', 'accessory-factors')],
    None,
]


# ---------------------------------------------------------------- practice questions
_a = 1.017 * 1.014 * 0.680; q_mua = 250 / _a
_b = 1.021 * 1.013 * 0.738; q_mub = 100 / (_b * (101.5 / 100) ** 2)
_c_iv = (101.5 / 121.5) ** 2; _c = 1.009 * 1.014 * 0.714 * _c_iv; q_muc = 200 / _c
_d = 1.011 * 1.010 * 0.742; q_mud = 100 / _d
q_cal = (101.5 / 100) ** 2; q_mue = 100 / _b
q_muw = 120 / 0.62; q_mut = 200 / 0.97; q_ac = 15 * 100 / 125

PROBLEMS = [
    PR("What is a monitor unit (MU)?", "A reading of the linac's monitor ionization chamber, calibrated so that a known number of MU gives a known dose at the reference point", ["A unit of absorbed dose to the patient at d<sub>max</sub>", "The dose delivered at 10 cm depth", "One cGy delivered to the target"],
       "The monitor chamber measures the beam as it leaves the machine, and the machine is calibrated so that, for example, 1 MU gives 1 cGy at d<sub>max</sub> in the reference geometry. The dose to a patient also depends on field size, depth, and distance.", lvl="Easy"),
    PR("The monitor-unit equation is:", "MU = prescribed dose at the point ÷ dose per MU at the point", ["MU = dose per MU ÷ prescribed dose", "MU = prescribed dose × dose per MU", "MU = prescribed dose ÷ dose rate"],
       "The dose per MU in the treatment geometry comes from the calibration and the correction factors. The prescription divided by it gives the number of MU.", lvl="Easy"),
    PR("A common linac calibration is 1 cGy per MU at:", "d<sub>max</sub> in water, for a 10 × 10 cm field", ["the surface, for a 10 × 10 cm field", "10 cm depth, for a 20 × 20 cm field", "d<sub>max</sub>, for the largest field"],
       "The reference is d<sub>max</sub> in water for the 10 × 10 cm field. Correction factors then account for any other field, depth, or distance.", lvl="Easy"),
    PRN(STEM("An isocentric field is calculated with the SSD-calibration inverse-square term and needs 127 MU. A second machine is calibrated by the SAD convention: 1 cGy/MU at d<sub>max</sub> = 1.5 cm with the point at 100 cm. Everything else about the field is the same.", [], "How many [[MU]] does the SAD-calibrated machine need?"), q_mue, [q_mub, q_mub / q_cal, q_mub * q_cal ** 2], "{:.0f} MU",
        f"Under SSD calibration the isocenter gains (101.5/100)² = {q_cal:.3f} in dose per MU, because the calibration point is farther from the source. A SAD calibration has no such gain, so more MU are needed: {q_mub:.1f} × {q_cal:.3f} = {q_mue:.0f}. Ignoring the convention gives {q_mub:.0f}, applying the factor the wrong way gives {q_mub / q_cal:.0f}, and applying it twice gives {q_mub * q_cal ** 2:.0f}.", lvl="Challenging"),
    PRN(STEM("A 6 MV beam with an SSD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm.", ["prescription = 250 cGy at 10 cm depth", "field = 15 × 15 cm at the surface, SSD 100 cm", "S<sub>c</sub> = 1.017, S<sub>p</sub> = 1.014", "PDD(10 cm, 15 × 15) = 68.0%"], "Find the [[monitor units]]."), q_mua, [250 / 0.680, 250 / (1.017 * 1.014), 250 * 0.680], "{:.0f} MU",
        f"Dose/MU = 1 × 1.017 × 1.014 × 0.680 = {_a:.4f} cGy/MU. MU = 250 / {_a:.4f} = {q_mua:.0f}. Leaving out the scatter factors gives {250 / 0.680:.0f}, leaving out the PDD gives {250 / (1.017 * 1.014):.0f}, and multiplying by the PDD gives {250 * 0.680:.0f}.", lvl="Moderate",
        calc=CALC("MU", [TILE("D", 250, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", 1.017, "", disp="1.017"), TILE("Sp", 1.014, "", disp="1.014"), TILE("PDD", 0.680, "", disp="0.680")], ops=("×", "÷", "(", ")"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "PDD", ")"])),
    PR("The same prescription at depth is treated at SSD 120 cm instead of SSD 100 cm, with the same field at the surface. The MU required:", "increase, because the inverse-square factor falls by more than the PDD rises", ["decrease, because the PDD rises with SSD", "stay the same, because TMR replaces PDD", "decrease, because the field at depth is larger"],
       f"A larger SSD raises the PDD a little, but the inverse-square factor [(100 + d<sub>max</sub>)/(f + d<sub>max</sub>)]² drops by more. Net dose per MU falls, so more MU are needed. The chapter's example goes from {mu1:.0f} MU at SSD 100 cm to {mu2:.0f} MU at SSD 120 cm, {100 * (mu2 / mu1 - 1):.0f}% more.", lvl="Moderate"),
    PRN(STEM("An extended-SSD treatment.", ["field at the surface = 15 × 15 cm", "SSD = 125 cm", "reference distance = 100 cm"], "What [[collimator opening]] is needed, projected to 100 cm?"), q_ac, [15 * 125 / 100, 15.0, 10.0], "{:.1f} cm",
        f"The collimator setting is the field projected to 100 cm: A<sub>c</sub> = A × 100 / f = 15 × 100 / 125 = {q_ac:.1f} cm. S<sub>c</sub> is read for this opening, while S<sub>p</sub> uses the 15 × 15 cm field at the surface. Projecting the wrong way gives {15 * 125 / 100:.1f} cm.", lvl="Moderate",
        calc=CALC("cm", [TILE("A", 15, "cm"), TILE("f0", 100, "cm"), TILE("f", 125, "cm")], solution=["A", "×", "f0", "÷", "f"])),
    PRN(STEM("A 6 MV beam with an SSD calibration (1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm), treated at SSD 120 cm.", ["prescription = 200 cGy at 10 cm depth", "field = 15 × 15 cm at the surface", "S<sub>c</sub>(12.5 × 12.5, the collimator opening) = 1.009", "S<sub>p</sub>(15 × 15) = 1.014", "PDD(10 cm, 15 × 15, SSD 120) = 71.4%"], "Find the [[monitor units]]."), q_muc, [200 / (1.009 * 1.014 * 0.714), 200 / (1.009 * 1.014 * 0.714 / _c_iv), 200 / (1.009 * 1.014 * _c_iv)], "{:.0f} MU",
        f"Inverse square = (101.5/121.5)² = {_c_iv:.4f}. Dose/MU = 1.009 × 1.014 × 0.714 × {_c_iv:.4f} = {_c:.4f} cGy/MU. MU = 200 / {_c:.4f} = {q_muc:.0f}. Leaving out the inverse square gives {200 / (1.009 * 1.014 * 0.714):.0f}, inverting it gives {200 / (1.009 * 1.014 * 0.714 / _c_iv):.0f}, and leaving out the PDD gives {200 / (1.009 * 1.014 * _c_iv):.0f}.", lvl="Challenging",
        calc=CALC("MU", [TILE("D", 200, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", 1.009, "", disp="1.009"), TILE("Sp", 1.014, "", disp="1.014"), TILE("PDD", 0.714, "", disp="0.714"), TILE("f0", 100, "cm"), TILE("dmax", 1.5, "cm", id="dm"), TILE("f", 120, "cm")],
                    ops=("+", "×", "÷", "(", ")", "²"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "PDD", "×", "(", "(", "f0", "+", "dm", ")", "÷", "(", "f", "+", "dm", ")", ")", "²", ")"])),
    PR("Which technique uses the TMR in its monitor-unit equation?", "The SAD (isocentric) technique", ["The SSD technique", "The extended-SSD technique", "Electron beam treatments"],
       "TMR does not depend on SSD, so it suits isocentric treatments. The SSD and extended-SSD techniques use PDD, which includes the inverse-square fall-off.", lvl="Easy"),
    PRN(STEM("A 6 MV beam in the SAD technique, with an SSD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm.", ["dose per field = 100 cGy at 12 cm depth", "S<sub>c</sub> = 1.021, S<sub>p</sub> = 1.013", "TMR(12 cm) = 0.738"], "Find the [[monitor units]] for the field."), q_mub, [100 / _b, 100 / (_b / q_cal), 200 / (_b * q_cal)], "{:.0f} MU",
        f"The calibration point is at 101.5 cm and the isocenter at 100 cm, so the dose per MU at the isocenter is higher by (101.5/100)² = {q_cal:.3f}. Dose/MU = 1.021 × 1.013 × 0.738 × {q_cal:.3f} = {_b * q_cal:.4f} cGy/MU, and MU = 100 / {_b * q_cal:.4f} = {q_mub:.0f}. Leaving out the factor gives {100 / _b:.0f}, applying it the wrong way gives {100 / (_b / q_cal):.0f}, and using the 200 cGy total instead of 100 cGy gives {200 / (_b * q_cal):.0f}.", lvl="Moderate",
        calc=CALC("MU", [TILE("D", 100, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", 1.021, "", disp="1.021"), TILE("Sp", 1.013, "", disp="1.013"), TILE("TMR", 0.738, "", disp="0.738"), TILE("c", 101.5, "cm", disp="101.5"), TILE("f", 100, "cm")], ops=("×", "÷", "(", ")", "²"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "TMR", "×", "(", "c", "÷", "f", ")", "²", ")"])),
    PRN(STEM("A 6 MV AP/PA pair in the SAD technique with a SAD calibration (1 cGy/MU at d<sub>max</sub> with the point at 100 cm), equally weighted, 200 cGy at mid-plane, patient separation 24 cm. The field at the isocenter is 12 × 20 cm. Factors are tabulated for squares:", ["10 × 10: S<sub>c</sub> 1.000, S<sub>p</sub> 1.000, TMR(12 cm) 0.723", "15 × 15: S<sub>c</sub> 1.011, S<sub>p</sub> 1.010, TMR(12 cm) 0.742", "20 × 20: S<sub>c</sub> 1.019, S<sub>p</sub> 1.017, TMR(12 cm) 0.757"], "Find the [[monitor units per field]]."), q_mud, [100 / (1.019 * 1.017 * 0.757), 100 / 0.723, 200 / _d], "{:.0f} MU",
        f"The equivalent square of 12 × 20 cm is 2 × 12 × 20 / 32 = {calc.equiv_square(12, 20):.1f} cm, so use the 15 × 15 row. Dose/MU = 1.011 × 1.010 × 0.742 = {_d:.4f}. MU per field = 100 / {_d:.4f} = {q_mud:.0f}. The 20 × 20 row (the long side) gives {100 / (1.019 * 1.017 * 0.757):.0f}, the 10 × 10 row (the short side) gives {100 / 0.723:.0f}, and using the full 200 cGy gives {200 / _d:.0f}.", lvl="Challenging",
        calc=CALC("MU", [TILE("D", 100, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", 1.011, "", disp="1.011"), TILE("Sp", 1.010, "", disp="1.010"), TILE("TMR", 0.742, "", disp="0.742")], ops=("×", "÷", "(", ")"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "TMR", ")"])),
    PRN(STEM("A wedged field.", ["MU without the wedge = 120", "wedge factor = 0.62"], "How many [[MU with the wedge]] give the same dose?"), q_muw, [120 * 0.62, 120 / (1 - 0.62), 120.0], "{:.0f} MU",
        f"The wedge factor is the dose with the wedge divided by the dose without, at the same point, so the wedge lowers the dose per MU and the MU rise: 120 / 0.62 = {q_muw:.0f}. Multiplying gives {120 * 0.62:.0f}, and using 1 − WF gives {120 / 0.38:.0f}.", lvl="Moderate",
        calc=CALC("MU", [TILE("MU0", 120, "MU", id="M"), TILE("WF", 0.62, "", disp="0.62")], solution=["M", "÷", "WF"])),
    PRN(STEM("A field treated through a blocking tray.", ["MU without the tray = 200", "tray factor = 0.97"], "How many [[MU with the tray]] give the same dose?"), q_mut, [200 * 0.97, 200.0, 200 / 0.97 ** 2], "{:.0f} MU",
        f"The tray transmits 97% of the beam, so the dose per MU falls and the MU rise: 200 / 0.97 = {q_mut:.0f}. Multiplying gives {200 * 0.97:.0f}, ignoring the tray gives 200, and applying the factor twice gives {200 / 0.97 ** 2:.0f}.", lvl="Moderate",
        calc=CALC("MU", [TILE("MU0", 200, "MU", id="M"), TILE("TF", 0.97, "", disp="0.97")], solution=["M", "÷", "TF"])),
    PR("The lower quarter of a field is blocked and the jaws are left unchanged. To deliver the same prescription dose, the MU:", "increase, because S<sub>p</sub> falls while S<sub>c</sub> is unchanged", ["decrease, because less tissue is irradiated", "stay the same, because the jaws are unchanged", "increase, because S<sub>c</sub> falls"],
       "S<sub>c</sub> follows the jaw opening and does not change. S<sub>p</sub> follows the irradiated field, which is smaller, so S<sub>p</sub> and the dose per MU fall. More MU are needed for the same dose.", lvl="Moderate"),
]

INLINE = {0: [0, 1], 1: [2], 2: [4, 5], 3: [8, 9], 4: [11]}


# ---------------------------------------------------------------- practice questions that use data tables
import beamdata as bd
_m1 = bd.SC[20] * bd.SP[20] * bd.PDD[(8, 20)] / 100; q_tm1 = 250 / _m1
_m2 = bd.SC[15] * bd.SP[15] * bd.TMR[(14, 15)]; q_tm2 = 100 / (_m2 * q_cal)
_F = ((121.5 / 130) ** 2) / ((101.5 / 110) ** 2); _p120 = bd.PDD[(10, 15)] * _F; _sc125 = bd.sc_at(12.5); _iv = (101.5 / 121.5) ** 2
_m3 = _sc125 * bd.SP[15] * _p120 / 100 * _iv; q_tm3 = 200 / _m3
_m4 = bd.SC[15] * bd.SP[15] * bd.TMR[(10, 15)] * 0.71 * 0.97; q_tm4 = 120 / _m4

PROBLEMS += [
    PRN(STEM("A 6 MV beam with an SSD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm. Use the tables.", ["prescription = 250 cGy at 8 cm depth", "field = 20 × 20 cm at the surface, SSD 100 cm"], "Find the [[monitor units]].", tables=[bd.table_scatter([10, 12, 15, 20, 25]), bd.table_pdd([6, 8, 10], [10, 15, 20])]),
        q_tm1, [250 / (bd.PDD[(8, 20)] / 100), 250 / (bd.SC[20] * bd.SP[20] * bd.PDD[(10, 20)] / 100), 250 * _m1], "{:.0f} MU",
        f"Read S<sub>c</sub> = {bd.SC[20]:.3f} and S<sub>p</sub> = {bd.SP[20]:.3f} for 20 × 20 cm, and PDD = {bd.PDD[(8, 20)]:.1f}% at 8 cm for the 20 × 20 column. Dose/MU = {bd.SC[20]:.3f} × {bd.SP[20]:.3f} × {bd.PDD[(8, 20)] / 100:.3f} = {_m1:.4f} cGy/MU. MU = 250 / {_m1:.4f} = {q_tm1:.0f}. Leaving out the scatter factors gives {250 / (bd.PDD[(8, 20)] / 100):.0f}, reading the 10 cm row gives {250 / (bd.SC[20] * bd.SP[20] * bd.PDD[(10, 20)] / 100):.0f}, and multiplying instead of dividing gives {250 * _m1:.0f}.", lvl="Moderate",
        calc=CALC("MU", [TILE("D", 250, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", bd.SC[20], "", disp=f"{bd.SC[20]:.3f}"), TILE("Sp", bd.SP[20], "", disp=f"{bd.SP[20]:.3f}"), TILE("PDD", bd.PDD[(8, 20)] / 100, "", disp=f"{bd.PDD[(8, 20)] / 100:.3f}")], ops=("×", "÷", "(", ")"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "PDD", ")"])),
    PRN(STEM("A 6 MV AP/PA pair in the SAD technique, equally weighted, with an SSD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm. Use the tables.", ["prescription = 200 cGy at mid-plane", "patient separation = 28 cm", "field at the isocenter = 12 × 20 cm"], "Find the [[monitor units per field]].", tables=[bd.table_scatter([10, 12, 15, 20]), bd.table_tmr([12, 14, 16], [10, 12, 15, 20])]),
        q_tm2, [100 / _m2, 100 / (bd.SC[20] * bd.SP[20] * bd.TMR[(14, 20)] * q_cal), 200 / (_m2 * q_cal)], "{:.0f} MU",
        f"Each field gives 100 cGy at the mid-plane, 14 cm deep. The equivalent square of 12 × 20 cm is 2 × 12 × 20 / 32 = 15.0 cm, so read the 15 × 15 column: S<sub>c</sub> = {bd.SC[15]:.3f}, S<sub>p</sub> = {bd.SP[15]:.3f}, TMR(14 cm) = {bd.TMR[(14, 15)]:.3f}. With an SSD calibration the isocenter gains (101.5/100)² = {q_cal:.3f}. Dose/MU = {_m2:.4f} × {q_cal:.3f} = {_m2 * q_cal:.4f} and MU = 100 / {_m2 * q_cal:.4f} = {q_tm2:.0f}. Leaving out the calibration factor gives {100 / _m2:.0f}, the 20 × 20 column (the long side) gives {100 / (bd.SC[20] * bd.SP[20] * bd.TMR[(14, 20)] * q_cal):.0f}, and using 200 cGy per field gives {200 / (_m2 * q_cal):.0f}.", lvl="Challenging",
        calc=CALC("MU", [TILE("D", 100, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", bd.SC[15], "", disp=f"{bd.SC[15]:.3f}"), TILE("Sp", bd.SP[15], "", disp=f"{bd.SP[15]:.3f}"), TILE("TMR", bd.TMR[(14, 15)], "", disp=f"{bd.TMR[(14, 15)]:.3f}"), TILE("c", 101.5, "cm", disp="101.5"), TILE("f", 100, "cm")],
                    ops=("×", "÷", "(", ")", "²"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "TMR", "×", "(", "c", "÷", "f", ")", "²", ")"])),
    PRN(STEM("A 6 MV beam with an SSD calibration (1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm), treated at SSD 120 cm. Only the SSD 100 PDD is tabulated, so correct it with the Mayneord F factor. Use the tables.", ["prescription = 200 cGy at 10 cm depth", "field = 15 × 15 cm at the surface"], "Find the [[monitor units]].", tables=[bd.table_scatter([10, 12, 15, 20]), bd.table_pdd([8, 10, 12], [10, 15, 20])]),
        q_tm3, [200 / (_sc125 * bd.SP[15] * _p120 / 100), 200 / (_sc125 * bd.SP[15] * bd.PDD[(10, 15)] / 100 * _iv), 200 / (_sc125 * bd.SP[15] * _p120 / 100 / _iv)], "{:.0f} MU",
        f"PDD at SSD 100 = {bd.PDD[(10, 15)]:.1f}%. F = [(121.5/130)²]/[(101.5/110)²] = {_F:.3f}, so PDD at SSD 120 = {_p120:.1f}%. The collimator opening is 15 × 100/120 = 12.5 cm, so S<sub>c</sub> is read between 12 and 15 cm: {_sc125:.3f}. S<sub>p</sub> uses the 15 × 15 field at the surface: {bd.SP[15]:.3f}. Inverse square = (101.5/121.5)² = {_iv:.4f}. Dose/MU = {_m3:.4f} and MU = 200 / {_m3:.4f} = {q_tm3:.0f}. Leaving out the inverse square gives {200 / (_sc125 * bd.SP[15] * _p120 / 100):.0f}, leaving out F gives {200 / (_sc125 * bd.SP[15] * bd.PDD[(10, 15)] / 100 * _iv):.0f}, and inverting the inverse square gives {200 / (_sc125 * bd.SP[15] * _p120 / 100 / _iv):.0f}.", lvl="Challenging",
        calc=CALC("MU", [TILE("D", 200, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", _sc125, "", disp=f"{_sc125:.3f}"), TILE("Sp", bd.SP[15], "", disp=f"{bd.SP[15]:.3f}"), TILE("PDD", bd.PDD[(10, 15)] / 100, "", disp=f"{bd.PDD[(10, 15)] / 100:.3f}"), TILE("F", _F, "", disp=f"{_F:.3f}"), TILE("f0", 100, "cm"), TILE("dmax", 1.5, "cm", id="dm"), TILE("f", 120, "cm")],
                    ops=("×", "÷", "+", "(", ")", "²"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "PDD", "×", "F", "×", "(", "(", "f0", "+", "dm", ")", "÷", "(", "f", "+", "dm", ")", ")", "²", ")"])),
    PRN(STEM("A wedged 6 MV field in the SAD technique with a SAD calibration: 1 cGy/MU at d<sub>max</sub> with the point at 100 cm. Use the tables.", ["prescription = 120 cGy at 10 cm depth", "field at the isocenter = 15 × 15 cm", "wedge factor = 0.71", "tray factor = 0.97"], "Find the [[monitor units]].", tables=[bd.table_scatter([10, 12, 15, 20]), bd.table_tmr([8, 10, 12], [10, 12, 15, 20])]),
        q_tm4, [120 / (bd.SC[15] * bd.SP[15] * bd.TMR[(10, 15)] * 0.71), 120 / (bd.SC[15] * bd.SP[15] * bd.TMR[(10, 15)] * 0.97), 120 / (bd.SC[15] * bd.SP[15] * bd.TMR[(10, 15)] / 0.71 * 0.97)], "{:.0f} MU",
        f"S<sub>c</sub> = {bd.SC[15]:.3f}, S<sub>p</sub> = {bd.SP[15]:.3f}, TMR(10 cm) = {bd.TMR[(10, 15)]:.3f} for 15 × 15 cm. Dose/MU = {bd.SC[15]:.3f} × {bd.SP[15]:.3f} × {bd.TMR[(10, 15)]:.3f} × 0.71 × 0.97 = {_m4:.4f} cGy/MU, and MU = 120 / {_m4:.4f} = {q_tm4:.0f}. Leaving out the tray factor gives {120 / (bd.SC[15] * bd.SP[15] * bd.TMR[(10, 15)] * 0.71):.0f}, leaving out the wedge factor gives {120 / (bd.SC[15] * bd.SP[15] * bd.TMR[(10, 15)] * 0.97):.0f}, and multiplying by the wedge factor gives {120 / (bd.SC[15] * bd.SP[15] * bd.TMR[(10, 15)] / 0.71 * 0.97):.0f}.", lvl="Moderate",
        calc=CALC("MU", [TILE("D", 120, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", bd.SC[15], "", disp=f"{bd.SC[15]:.3f}"), TILE("Sp", bd.SP[15], "", disp=f"{bd.SP[15]:.3f}"), TILE("TMR", bd.TMR[(10, 15)], "", disp=f"{bd.TMR[(10, 15)]:.3f}"), TILE("WF", 0.71, "", disp="0.71"), TILE("TF", 0.97, "", disp="0.97")], ops=("×", "÷", "(", ")"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "TMR", "×", "WF", "×", "TF", ")"])),
]
INLINE = {0: [0, 1], 1: [2], 2: [4, 5, 14], 3: [8, 9, 15], 4: [11]}


# ---------------------------------------------------------------- practice questions on the two calibration conventions
q_ssdc = (100 / 101.5) ** 2
q_mun2 = 250 / (_a * q_ssdc)
_n3 = bd.SC[15] * bd.SP[15] * bd.PDD[(12, 15)] / 100 * q_ssdc; q_mun3 = 200 / _n3

PROBLEMS += [
    PR("In an SSD calibration, the machine delivers 1 cGy/MU at d<sub>max</sub>:", "with the surface at 100 cm, so the point is at 100 + d<sub>max</sub> from the source", ["with the point at 100 cm from the source", "at the surface, with the surface at 100 cm", "at 100 cm depth in water"],
       "SSD calibration puts the surface at 100 cm, so the d<sub>max</sub> point is at 101.5 cm for 6 MV. SAD calibration puts the d<sub>max</sub> point itself at 100 cm. SSD calibration is the convention at this clinic.", lvl="Easy"),
    PRN(STEM("A 6 MV beam with a SAD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, point at 100 cm.", ["prescription = 250 cGy at 10 cm depth", "field = 15 × 15 cm at the surface, SSD 100 cm", "S<sub>c</sub> = 1.017, S<sub>p</sub> = 1.014", "PDD(10 cm, 15 × 15) = 68.0%"], "Find the [[monitor units]] for this SSD treatment."),
        q_mun2, [q_mua, 250 / (_a * q_cal), 250 / (_a * q_ssdc ** 2)], "{:.0f} MU",
        f"The d<sub>max</sub> point of an SSD 100 cm treatment is 101.5 cm from the source, but the calibration point is at 100 cm, so the dose per MU is lower by (100/101.5)² = {q_ssdc:.4f}. Dose/MU = 1.017 × 1.014 × 0.680 × {q_ssdc:.4f} = {_a * q_ssdc:.4f} cGy/MU, and MU = 250 / {_a * q_ssdc:.4f} = {q_mun2:.0f}. An SSD calibration would give {q_mua:.0f}, applying the factor the wrong way gives {250 / (_a * q_cal):.0f}, and applying it twice gives {250 / (_a * q_ssdc ** 2):.0f}.", lvl="Moderate",
        calc=CALC("MU", [TILE("D", 250, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", 1.017, "", disp="1.017"), TILE("Sp", 1.014, "", disp="1.014"), TILE("PDD", 0.680, "", disp="0.680"), TILE("c", 100, "cm"), TILE("f", 100, "cm"), TILE("dmax", 1.5, "cm", id="dm")],
                  ops=("×", "÷", "+", "(", ")", "²"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "PDD", "×", "(", "c", "÷", "(", "f", "+", "dm", ")", ")", "²", ")"])),
    PRN(STEM("A 6 MV beam with a SAD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, point at 100 cm. Use the tables.", ["prescription = 200 cGy at 12 cm depth", "field = 15 × 15 cm at the surface, SSD 100 cm"], "Find the [[monitor units]] for this SSD treatment.", tables=[bd.table_scatter([10, 12, 15, 20]), bd.table_pdd([10, 12, 14], [12, 15, 20])]),
        q_mun3, [200 / (bd.SC[15] * bd.SP[15] * bd.PDD[(12, 15)] / 100), 200 / (bd.SC[15] * bd.SP[15] * bd.PDD[(12, 15)] / 100 * q_cal), 200 / (bd.SC[15] * bd.SP[15] * bd.PDD[(10, 15)] / 100 * q_ssdc)], "{:.0f} MU",
        f"Read S<sub>c</sub> = {bd.SC[15]:.3f}, S<sub>p</sub> = {bd.SP[15]:.3f}, and PDD(12 cm) = {bd.PDD[(12, 15)]:.1f}% for 15 × 15 cm. With a SAD calibration the inverse-square term is (100/101.5)² = {q_ssdc:.4f}. Dose/MU = {bd.SC[15]:.3f} × {bd.SP[15]:.3f} × {bd.PDD[(12, 15)] / 100:.3f} × {q_ssdc:.4f} = {_n3:.4f} and MU = 200 / {_n3:.4f} = {q_mun3:.0f}. Ignoring the convention gives {200 / (bd.SC[15] * bd.SP[15] * bd.PDD[(12, 15)] / 100):.0f}, applying the factor the wrong way gives {200 / (bd.SC[15] * bd.SP[15] * bd.PDD[(12, 15)] / 100 * q_cal):.0f}, and reading the 10 cm row gives {200 / (bd.SC[15] * bd.SP[15] * bd.PDD[(10, 15)] / 100 * q_ssdc):.0f}.", lvl="Challenging",
        calc=CALC("MU", [TILE("D", 200, "cGy"), TILE("D0", 1, "cGy/MU", disp="1"), TILE("Sc", bd.SC[15], "", disp=f"{bd.SC[15]:.3f}"), TILE("Sp", bd.SP[15], "", disp=f"{bd.SP[15]:.3f}"), TILE("PDD", bd.PDD[(12, 15)] / 100, "", disp=f"{bd.PDD[(12, 15)] / 100:.3f}"), TILE("c", 100, "cm"), TILE("f", 100, "cm"), TILE("dmax", 1.5, "cm", id="dm")],
                  ops=("×", "÷", "+", "(", ")", "²"), solution=["D", "÷", "(", "D0", "×", "Sc", "×", "Sp", "×", "PDD", "×", "(", "c", "÷", "(", "f", "+", "dm", ")", ")", "²", ")"])),
    PRM("Which statements about the two calibration conventions are correct?", ["They differ in the distance from the source to the 1 cGy/MU point", "For d<sub>max</sub> = 1.5 cm, an isocentric field needs about 3% fewer MU on an SSD-calibrated machine than on a SAD-calibrated one", "The SAD technique on an SSD-calibrated machine has an inverse-square term of [(100 + d<sub>max</sub>)/100]²"],
        ["They differ in the beam energy used for calibration", "The SSD technique at SSD 100 cm on an SSD-calibrated machine has an inverse-square term below 1"],
        "The conventions differ only in where the d<sub>max</sub> point sits: 100 + d<sub>max</sub> or 100 cm from the source. On an SSD-calibrated machine the isocenter is nearer the source than the calibration point, so the dose per MU there is 3.0% higher and the MU are about 3% fewer. At SSD 100 cm the SSD technique has d = 100 + d<sub>max</sub> = d<sub>cal</sub>, so its term is exactly 1.", lvl="Moderate"),
]
INLINE = {0: [0, 1], 1: [2, 18], 2: [4, 5, 19], 3: [8, 9, 15], 4: [11]}


# ---------------------------------------------------------------- matching, ranking, and typed-number questions
_n0 = len(PROBLEMS)
q_t1 = 300 / (1.017 * 1.014 * 0.680)
q_t2 = 120 / (1.021 * 1.013 * 0.738 * (101.5 / 100) ** 2)
q_t3 = 180 / (0.66 * 0.97)
PROBLEMS += [
    SORT("A beam has d<sub>max</sub> = 1.5 cm. Match each calibration and technique to its inverse-square term (d<sub>cal</sub>/d)².", ["× 1.000", "× 1.030", "× 0.971"],
         [("SSD calibration, SSD technique at SSD 100 cm", 0), ("SAD calibration, SAD technique", 0), ("SSD calibration, SAD technique", 1), ("SAD calibration, SSD technique at SSD 100 cm", 2)],
         "The term is (d<sub>cal</sub>/d)², where d<sub>cal</sub> is where the machine was calibrated and d is where the dose is calculated. When both are the same, it is 1. With an SSD calibration (101.5 cm) and the isocenter at 100 cm, it is (101.5/100)² = 1.030. With a SAD calibration (100 cm) and d<sub>max</sub> at 101.5 cm, it is (100/101.5)² = 0.971.", lvl="Challenging", mode="match"),
    SORT("Put the steps of a monitor-unit calculation in order.", ["1st", "2nd", "3rd", "4th", "5th"],
         [("Confirm the calibration convention and the technique", 0), ("Find the equivalent square and read S<sub>c</sub>, S<sub>p</sub>, and the PDD or TMR", 1), ("Apply the inverse-square term and any wedge or tray factor", 2),
          ("Multiply the factors to get the dose per monitor unit", 3), ("Divide the prescribed dose by the dose per monitor unit", 4)],
         "The convention decides which inverse-square term applies, so it comes first. Then look up the field-dependent factors, add the geometry and accessory factors, and multiply them to get the dose delivered per MU. The prescription divided by that number gives the monitor units.", lvl="Moderate", mode="rank", cap=1),
    TYPED(STEM("A 6 MV beam with an SSD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm.", ["SSD technique, SSD = 100 cm", "prescription = 300 cGy at 10 cm depth", "field = 15 × 15 cm at the surface", "S<sub>c</sub> = 1.017, S<sub>p</sub> = 1.014", "PDD(10 cm, 15 × 15) = 68.0%"], "Find the [[monitor units]]."), q_t1, 0.012, "MU",
          "With an SSD calibration and the surface at 100 cm, the inverse-square term is 1.000.", w=["Dose per MU = 1.017 × 1.014 × 0.680 = 0.7012 cGy/MU.", f"MU = 300 / 0.7012 = {q_t1:.1f}."], lvl="Moderate"),
    TYPED(STEM("A 6 MV beam in the SAD technique, with an SSD calibration: 1 cGy/MU at d<sub>max</sub> = 1.5 cm, surface at 100 cm.", ["dose = 120 cGy at 12 cm depth, isocenter at 100 cm", "field = 10 × 10 cm at the isocenter", "S<sub>c</sub> = 1.021, S<sub>p</sub> = 1.013", "TMR(12 cm, 10 × 10) = 0.738"], "Find the [[monitor units]]."), q_t2, 0.01, "MU",
          "The calibration point is at 101.5 cm and the isocenter at 100 cm, so the inverse-square term is (101.5/100)² = 1.030.", w=["Dose per MU = 1.021 × 1.013 × 0.738 × 1.030 = 0.7863 cGy/MU.", f"MU = 120 / 0.7863 = {q_t2:.1f}."], lvl="Challenging"),
    TYPED(STEM("A field with both a wedge and a blocking tray.", ["MU without accessories = 180", "wedge factor = 0.66", "tray factor = 0.97"], "How many [[MU with the accessories]]?"), q_t3, 0.01, "MU",
          "Each accessory attenuates the beam, so the monitor units go up by dividing by both factors: 180 / (0.66 × 0.97). Using the wedge factor alone gives 272.7, which is too low.", w=["Combined factor = 0.66 × 0.97 = 0.6402.", f"MU = 180 / 0.6402 = {q_t3:.1f}."], lvl="Moderate"),
]
INLINE = {0: [1, 2], 1: [3, 19], 2: [5, 6, _n0 + 3], 3: [9, 10, _n0 + 1, _n0 + 4], 4: [12, 13, _n0 + 5], 5: [_n0 + 2]}
