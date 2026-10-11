from blocks import *
import math, calc, cases
CS = cases.ST
hi_real = (CS['PTV70']['D2'] - CS['PTV70']['D98']) / CS['PTV70']['D50']
d95_pct = 100 * CS['PTV70']['D95'] / 70.0

DOSE = [40, 45, 48, 50, 52, 54, 56]                              # a cumulative PTV DVH: dose (Gy) and the percentage of the volume receiving at least that dose
VOL = [100, 99, 97, 90, 50, 5, 0]
d_at = lambda v: next(DOSE[i] + (VOL[i] - v) / (VOL[i] - VOL[i + 1]) * (DOSE[i + 1] - DOSE[i]) for i in range(len(DOSE) - 1) if VOL[i] >= v >= VOL[i + 1])
v_at = lambda d: next(VOL[i] + (d - DOSE[i]) / (DOSE[i + 1] - DOSE[i]) * (VOL[i + 1] - VOL[i]) for i in range(len(DOSE) - 1) if DOSE[i] <= d <= DOSE[i + 1])
d95, d50, d2, d98 = d_at(95), d_at(50), d_at(2), d_at(98)
hi = lambda a, b, c: (a - b) / c
VT, VP, VTP = 30.0, 45.0, 28.0                                  # target volume, volume at the prescription dose, and the part of the target that gets it (cc)
ci = VP / VT; cov = VTP / VT; sel = VTP / VP; pad = cov * sel
dvh_ptv = lambda D: 100 * 0.5 * math.erfc((D - 50) / (math.sqrt(2) * 1.4))                # a smooth PTV DVH, 50% of the volume at 50 Gy
dvh_oar = lambda D: 100 * math.exp(-(D / 18.0) ** 1.5)                                    # a smooth DVH of a parallel organ

TOPIC = dict(
    id="dvh-metrics", domain=3, sub="III.C", title="Dose-volume histograms and plan metrics",
    ref=dict(aapm="TG-263", khan="", ford="13"),
    guide=[
        H("The dose-volume histogram"),
        P("A dose-volume histogram summarizes a three-dimensional dose distribution for one structure. In the cumulative form, each point is the percentage of the volume that receives at least a given dose, so the curve starts at 100% at zero dose and falls to zero at the highest dose. A uniform dose to the PTV gives a curve that stays high and then drops sharply. Hot spots give a tail at high dose, and low-dose regions pull the curve down at lower dose."),
        P("Two kinds of value are read from a DVH. D<sub>x%</sub> is the dose that at least x% of the volume receives, for example D<sub>95%</sub> of the PTV for coverage. V<sub>x Gy</sub> is the volume that receives at least x Gy, for example V<sub>30 Gy</sub> of an organ at risk. The mean dose and the maximum dose are also reported. ICRU Report 83 prefers D<sub>2%</sub> as the near-maximum and D<sub>98%</sub> as the near-minimum, because the exact extremes depend on single voxels."),
        EX("Reading a DVH", STEM("A cumulative PTV DVH.", ["50 Gy: 90% of the volume", "48 Gy: 97% of the volume", "52 Gy: 50% of the volume"], "Find [[D<sub>95%</sub>]] by linear interpolation, and V<sub>50 Gy</sub>."), ["95% lies between 97% at 48 Gy and 90% at 50 Gy", "D<sub>95%</sub> = 48 + (97 − 95) / (97 − 90) × 2"], f"D<sub>95%</sub> = {d95:.2f} Gy, and V<sub>50 Gy</sub> = 90%."),

        P(f"In the cumulative DVHs of a real head-and-neck IMRT plan from the OpenKBP dataset, the curve of the PTV70 stays near 100% and then falls steeply close to the prescription: its D<sub>95%</sub> is {CS['PTV70']['D95']:.1f} Gy, which is {d95_pct:.1f}% of 70 Gy, and its mean dose is {CS['PTV70']['mean']:.1f} Gy. The curves of the parotid glands fall from 100% almost at once, which shows sparing. Their mean doses are {CS['LeftParotid']['mean']:.1f} Gy and {CS['RightParotid']['mean']:.1f} Gy, although a part of each gland lies close to the target and receives a high dose."),
        AVF("case-dvh"),
        H("Conformity and homogeneity"),
        P("The conformity index quantifies how closely the dose distribution wraps around the PTV, which matters most for the high doses per fraction of SRS and SBRT. One definition is CI = V<sub>P</sub> / V<sub>T</sub>, where V<sub>P</sub> is the volume receiving the prescription dose and V<sub>T</sub> is the target volume. The ideal value is 1. It is usually larger than 1, and it can be below 1 when the target is not covered. It ignores where the dose volume is, so a prescription isodose displaced from the target can still give a CI of 1."),
        P("The Paddick index fixes this by combining coverage and selectivity. Coverage is the fraction of the target that receives the prescription dose, V<sub>TP</sub> / V<sub>T</sub>, where V<sub>TP</sub> is the part of the target inside the prescription isodose. Selectivity is the fraction of the prescription isodose volume that lies in the target, V<sub>TP</sub> / V<sub>P</sub>. Their product is always below 1 and approaches 1 for an ideal plan."),
        EQ("CI<sub>Paddick</sub> = (V<sub>TP</sub> / V<sub>T</sub>) × (V<sub>TP</sub> / V<sub>P</sub>)"),
        P("For homogeneity, ICRU Report 83 defines HI = (D<sub>2%</sub> − D<sub>98%</sub>) / D<sub>50%</sub>. A value of 0 is a uniform dose, and larger values mean a wider spread."),
        EX("Conformity", STEM("A stereotactic plan.", ["target volume V<sub>T</sub> = 30 cc", "prescription isodose volume V<sub>P</sub> = 45 cc", "part of the target inside the prescription isodose V<sub>TP</sub> = 28 cc"], "Find CI and the [[Paddick index]]."), ["CI = 45 / 30", "Coverage = 28 / 30,   selectivity = 28 / 45", "Paddick = (28 / 30) × (28 / 45)"], f"CI = {ci:.2f}. Paddick = {cov:.3f} × {sel:.3f} = {pad:.3f}."),
        EX("Homogeneity", STEM("A PTV.", ["D<sub>2%</sub> = 105%", "D<sub>98%</sub> = 95%", "D<sub>50%</sub> = 100%"], "Find the [[homogeneity index]]."), ["HI = (105 − 95) / 100"], f"{hi(105, 95, 100):.2f}."),

        H("Reading a plan"),
        P("The limit that matters for an organ at risk depends on how the organ is built. A serial organ, such as the spinal cord, fails if any part is damaged, so the limit is on the maximum dose to a small volume. A parallel organ, such as the lung or the liver, has many independent units and tolerates damage to part of it, so the limits are on the mean dose and on the volume above a threshold, such as V<sub>20 Gy</sub> of the lung."),
        P("A DVH has no spatial information. Two plans with the same DVH can place the high dose in different places, so the DVH is read together with the dose distribution on the images."),
    ],
    cards=[
        F("Cumulative DVH", "Each point is the percentage of a structure's volume that receives at least that dose. The curve starts at 100% and falls to zero."),
        F("DVH of a uniform PTV dose", "The curve stays high and then drops sharply. Hot spots give a tail at high dose."),
        F("D<sub>x%</sub>", "The dose that at least x% of the volume receives, for example D<sub>95%</sub> of the PTV for coverage."),
        F("V<sub>x Gy</sub>", "The volume that receives at least x Gy, for example V<sub>30 Gy</sub> of an organ at risk."),
        F("Near-maximum and near-minimum dose", "ICRU 83 prefers D<sub>2%</sub> and D<sub>98%</sub>, because the exact maximum and minimum depend on single voxels."),
        F("Conformity index", "CI = V<sub>P</sub> / V<sub>T</sub>: the volume receiving the prescription dose over the target volume. Ideal 1, usually above 1, below 1 if the target is not covered."),
        F("Limit of the conformity index", "It ignores where the dose volume is. A displaced prescription isodose can still give a CI of 1."),
        F("Paddick index", "Coverage × selectivity, with coverage V<sub>TP</sub>/V<sub>T</sub> and selectivity V<sub>TP</sub>/V<sub>P</sub>. Between 0 and 1, and equal to 1 for an ideal plan."),
        F("Homogeneity index", "HI = (D<sub>2%</sub> − D<sub>98%</sub>) / D<sub>50%</sub> (ICRU 83). Zero is a uniform dose."),
        F("Serial organ", "Fails if any part is damaged, such as the spinal cord. The limit is on the maximum dose to a small volume."),
        F("Parallel organ", "Many independent units, such as lung or liver. The limits are on the mean dose and on the volume above a threshold, such as V<sub>20 Gy</sub>."),
        F("Information missing from a DVH", "Spatial information. Two plans with the same DVH can place the high dose in different places."),
    ],
)

PROBLEMS = [
    PR("In a cumulative DVH, the value of the curve at a dose D is:", "the percentage of the volume that receives at least D", ["the percentage of the volume that receives exactly D", "the average dose to the structure", "the maximum dose to the structure"],
       "The curve starts at 100% at zero dose, because all of the volume receives at least zero.", lvl="Easy"),
    PR("A PTV DVH that drops sharply near the prescription dose indicates:", "a uniform dose to the PTV", ["a large hot spot", "an under-dosed target", "a large target"],
       "A steep fall means most of the volume receives nearly the same dose.", lvl="Easy"),
    PR("The spinal cord is a serial organ, so its main limit is on:", "the maximum dose to a small volume", ["the mean dose", "the V<sub>20 Gy</sub>", "the total volume"],
       "Damage to any part can cause loss of function, so the highest dose matters most.", lvl="Easy"),
    PR("V<sub>30 Gy</sub> of the heart is:", "the volume of the heart that receives at least 30 Gy", ["the dose to 30% of the heart", "the mean dose to the heart over 30 fractions", "the volume of the heart that receives exactly 30 Gy"],
       "V<sub>x Gy</sub> is a volume, read from the DVH at the dose x.", lvl="Moderate"),
    PRN(STEM("A cumulative PTV DVH.", ["48 Gy: 97% of the volume", "50 Gy: 90% of the volume"], "What is [[D<sub>95%</sub>]], by linear interpolation?"), d95, [48.0, 50.0, 49.0], "{:.2f} Gy",
        f"95% lies between 97% at 48 Gy and 90% at 50 Gy: 48 + (97 − 95) / (97 − 90) × 2 = {d95:.2f} Gy. The midpoint, 49.0, ignores where 95% sits.", lvl="Moderate"),
    PRN(STEM("A stereotactic plan.", ["V<sub>T</sub> = 30 cc", "V<sub>P</sub> = 45 cc"], "What is the [[conformity index]] CI = V<sub>P</sub> / V<sub>T</sub>?"), ci, [30 / 45, 1.0, 15.0], "{:.2f}",
        f"CI = 45 / 30 = {ci:.2f}. The inverse, {30 / 45:.2f}, is the ratio the wrong way round.", lvl="Moderate"),
    PR("A conformity index CI = V<sub>P</sub> / V<sub>T</sub> that is below 1 means that:", "the prescription isodose volume is smaller than the target, so the target is not fully covered", ["the plan is ideal", "the plan is perfectly selective", "the dose is homogeneous"],
       "V<sub>P</sub> smaller than V<sub>T</sub> means that part of the target is outside the prescription isodose.", lvl="Moderate"),
    PRN(STEM("A stereotactic plan.", ["V<sub>T</sub> = 30 cc, V<sub>P</sub> = 45 cc", "V<sub>TP</sub> = 28 cc, the part of the target inside the prescription isodose"], "What is the [[Paddick index]]?"), pad, [ci, cov, sel], "{:.3f}",
        f"Coverage = 28 / 30 = {cov:.3f}, selectivity = 28 / 45 = {sel:.3f}, and their product is {pad:.3f}. The CI is {ci:.2f}, and each factor alone is {cov:.3f} or {sel:.3f}.", lvl="Challenging"),
    PR("Two plans give the same DVH for the PTV and the cord. The plans:", "can still place the high dose in different places, because a DVH has no spatial information", ["must be identical in every voxel", "must have the same conformity index and location", "must give identical doses to every organ"],
       "A DVH is a histogram of doses, so rearranging the dose in space leaves it unchanged.", lvl="Challenging"),
    PRN(STEM("A PTV.", ["D<sub>2%</sub> = 108%", "D<sub>98%</sub> = 93%", "D<sub>50%</sub> = 100%"], "What is the [[homogeneity index]] (D<sub>2%</sub> − D<sub>98%</sub>) / D<sub>50%</sub>?"), hi(108, 93, 100), [108 - 93, hi(93, 108, 100), 15 / 108], "{:.2f}",
        f"HI = (108 − 93) / 100 = {hi(108, 93, 100):.2f}. A larger HI means a wider spread of dose.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 4], 1: [5, 6, 7], 2: [3, 8]}

TERMS = ['dose-volume histogram', 'conformity index', 'Paddick index', 'serial organ', 'parallel organ']

TAKE = [
    [('A cumulative DVH gives the percentage of the volume that receives at least each dose. D<sub>x%</sub> is a dose and V<sub>x Gy</sub> is a volume, both read from the curve.', 'dvh-curve')],
    [('CI = V<sub>P</sub>/V<sub>T</sub> is ideally 1 and ignores location. The Paddick index, coverage × selectivity, is always below 1 and approaches 1 for an ideal plan.', 'conformity-index')],
    [('Serial organs are limited by the maximum dose to a small volume. Parallel organs are limited by the mean dose and by the volume above a threshold.', 'serial-parallel')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Is each organ serial or parallel, and so which limit applies?", ["Serial: maximum dose", "Parallel: mean dose or V<sub>x</sub>"],
         [("Spinal cord", 0), ("Lung", 1), ("Liver", 1), ("Optic nerve", 0), ("Brainstem", 0), ("Kidney", 1)],
         "Serial organs fail if any part is damaged, so the maximum dose to a small volume is limited. Parallel organs have many independent units, so the mean dose and the volume above a threshold are limited.", lvl="Moderate"),
    TYPED(STEM("A PTV.", ["D<sub>2%</sub> = 106%", "D<sub>98%</sub> = 94%", "D<sub>50%</sub> = 100%"], "What is the [[homogeneity index]]?"), hi(106, 94, 100), 0.02, "(ratio)",
          f"HI = (106 − 94) / 100 = {hi(106, 94, 100):.2f}.", lvl="Moderate"),
    FIGQ(STEM("The graph shows a smooth cumulative DVH of a PTV.", [], "Tap [[D<sub>95%</sub>]], the dose that at least 95% of the volume receives."),
         FS(x=dict(min=40, max=60, ticks=[40, 45, 50, 55, 60], label="Dose (Gy)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Volume receiving at least the dose (%)", fmt="pct"), series=[dict(pts=PTS(dvh_ptv, 40, 60), color="plot-1")], xunit=" Gy", xdec=1, xname="Dose", label="Cumulative DVH of a PTV"),
         [(50 - 1.4 * 1.645 - 1.0, 50 - 1.4 * 1.645 + 1.0)], f"D<sub>95%</sub> is the dose at which the curve is at 95%. For this curve it is {50 - 1.4 * 1.645:.1f} Gy. The 95% level is not marked on the axis, and it lies on the upper part of the fall.", lvl="Moderate", note=f"about {50 - 1.4 * 1.645:.1f} Gy"),
]
INLINE = {0: [1, 2, 4, _n0 + 3], 1: [5, 6, 7], 2: [3, 8, _n0 + 1]}


# ---------------------------------------------------------------- questions that use the numbers of the real plan
PROBLEMS += [
    PRN(STEM("In a real head-and-neck IMRT plan the PTV70 has D<sub>95%</sub> = " + f"{CS['PTV70']['D95']:.2f}" + " Gy. The prescription is 70 Gy.", [], "What [[percentage of the prescription]] is D<sub>95%</sub>?"), d95_pct, [100 * (70 - CS['PTV70']['D95']) / 70, 100 * 70 / CS['PTV70']['D95'], 95.0], "{:.1f}%",
        f"{CS['PTV70']['D95']:.2f} / 70 = {d95_pct / 100:.4f}, which is {d95_pct:.1f}%. At least 95% of the volume receives this dose or more.", lvl="Moderate"),
    PRN(STEM("In a real head-and-neck IMRT plan the PTV70 has D<sub>2%</sub> = " + f"{CS['PTV70']['D2']:.2f}" + " Gy, D<sub>98%</sub> = " + f"{CS['PTV70']['D98']:.2f}" + " Gy, and D<sub>50%</sub> = " + f"{CS['PTV70']['D50']:.2f}" + " Gy.", [], "What is the [[homogeneity index]], HI = (D<sub>2%</sub> − D<sub>98%</sub>) / D<sub>50%</sub>?"), hi_real, [(CS['PTV70']['D2'] - CS['PTV70']['D98']), CS['PTV70']['D98'] / CS['PTV70']['D2'], (CS['PTV70']['D2'] - CS['PTV70']['D98']) / 70 * 100], "{:.3f}",
        f"HI = ({CS['PTV70']['D2']:.2f} − {CS['PTV70']['D98']:.2f}) / {CS['PTV70']['D50']:.2f} = {hi_real:.3f}. A value near zero means a uniform dose in the target.", lvl="Challenging"),
]
