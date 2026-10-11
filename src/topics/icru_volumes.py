from blocks import *
import math, calc, cases, real
CS = cases.ST
RM = real.STATS["4d"]["motion"]                                                                  # measured on a real 4D-CT: tools/make_real_4d.py

margin = lambda sys, rnd: 2.5 * sys + 0.7 * rnd                 # van Herk recipe: 2.5 x systematic + 0.7 x random, all in the same unit
m_a, m_b, m_c, m_d = margin(2, 3), margin(1, 3), margin(2, 2), margin(3, 2)

TOPIC = dict(
    id="icru-volumes", domain=3, sub="III.C", title="ICRU volumes, margins, and prescriptions",
    ref=dict(aapm="TG-263", khan="", ford="13"),
    guide=[
        H("Target and normal tissue volumes"),
        P("Treatment planning works with regions of interest drawn on CT or MRI. ICRU Reports 50, 62, and 83 define them. The gross tumour volume is the disease that can be seen. The clinical target volume adds an expansion for the extension of disease that cannot be seen. The internal target volume adds an expansion for physiological motion of the target. The planning target volume adds an expansion for variability in patient setup, so that the intended target is treated."),
        P("Two volumes describe the dose. The treated volume is enclosed by the isodose surface that the radiation oncologist has chosen as necessary for the purpose of treatment. The irradiated volume receives a dose that is significant relative to normal tissue tolerance, typically taken to be the volume inside the 50% isodose line. For normal tissue, an organ at risk is a structure to be avoided, and the planning risk volume is its expansion for setup variability. It is used mainly for serial organs such as the spinal cord. For a tubular organ such as the rectum, the ICRU recommends using the wall and not the contents."),
        TABLE(["Volume", "What it accounts for"], [["GTV, gross tumour volume", "Disease visible on imaging"], ["CTV, clinical target volume", "Occult disease around the GTV"], ["ITV, internal target volume", "Motion of the target"], ["PTV, planning target volume", "Variability of patient setup"],
                                                    ["TV, treated volume", "The volume enclosed by the prescription isodose"], ["IV, irradiated volume", "A significant dose to normal tissue, typically the 50% isodose"], ["OAR, organ at risk", "A structure to be avoided"], ["PRV, planning risk volume", "Setup variability of an OAR"]]),
        P("AAPM Task Group 263 gives standard names for structures and dose metrics, so that clinics, trials, and automation can agree. Examples are Lung_L for the left lung, Lungs for both lungs, and Lungs-PTV for the lungs minus the PTV."),

        P(f"In a head-and-neck plan from the open OpenKBP dataset, the planning target volumes are contoured at three dose levels, 70, 63, and 56 Gy. The PTV70 is {CS['PTV70']['volume']:.0f} cm³ and the PTV56, which covers the neck, is {CS['PTV56']['volume']:.0f} cm³. The organs at risk are the brainstem, the spinal cord, both parotid glands, and the esophagus."),
        AVF("case-volumes"),
        P("The ITV exists because a target in the chest does not stay in one place. Breathing moves the diaphragm, and a lung tumour near it, up and down in every breath. A four-dimensional CT sorts the images into phases of the breathing cycle, so that the target can be contoured in each phase, and the ITV is the union of those contours."),
        AVF("real-ct-motion"),
        H("Margins"),
        P("The expansion from CTV or ITV to PTV covers the variability of aiming the beam at the patient. Two kinds of setup error contribute. Random errors, with standard deviation σ, are day-to-day variations around the mean position. A systematic error, with standard deviation Σ, is an offset of the mean position from the ideal that affects every fraction in the same direction. A systematic error therefore has the larger effect."),
        EQ("PTV margin = 2.5 Σ + 0.7 σ", "the van Herk recipe: Σ = systematic error,   σ = random error,   both in the same unit"),
        P("The van Herk recipe gives a margin for which a stated percentage of patients receive the full dose to the CTV, and it rests on assumptions about the population, the coverage wanted, and the dose distribution, so it is used with caution. Because the systematic error is multiplied by the larger coefficient, reducing it with better image guidance shrinks the margin more than reducing the random error by the same amount."),
        EX("A margin from the recipe", STEM("Setup errors for a site.", ["systematic error Σ = 2 mm", "random error σ = 3 mm"], "Find the [[PTV margin]]."), ["Margin = 2.5 × 2 + 0.7 × 3 = 5.0 + 2.1"], f"{m_a:.1f} mm."),
        EX("Which error to reduce", STEM("Setup errors for a site, after image guidance halves the systematic error from 2 mm to 1 mm.", ["systematic error Σ = 1 mm", "random error σ = 3 mm"], "Find the new [[margin]]."), ["Margin = 2.5 × 1 + 0.7 × 3 = 2.5 + 2.1"], f"{m_b:.1f} mm, a reduction of {m_a - m_b:.1f} mm from {m_a:.1f} mm. Halving the random error instead gives {margin(2, 1.5):.2f} mm, a reduction of only {m_a - margin(2, 1.5):.2f} mm."),

        H("Prescriptions"),
        P("The ASTRO white paper on prescriptions asks for five items in every prescription: the treatment site, the delivery method, the dose per fraction, the number of fractions, and the total dose. It also asks for doses in cGy, which avoids misplaced decimal points. An example is L_Lung, Photons, 200 cGy × 32 to 6400 cGy. Writing it this way, in this order, avoids confusion between the dose per fraction and the number of fractions: 54 Gy in 3 could mean 1800 cGy × 3 or 300 cGy × 18."),
        P("A dose can be prescribed to a point or to a volume. For three-dimensional conformal plans the dose is fairly uniform in and around the tumour, so a point prescription is reasonable. ICRU Report 83 asks that the point be where the dose can be calculated accurately, not in the build-up region, near a steep gradient, or at an interface, and in a central part of the PTV, usually the isocenter. For IMRT the dose is less uniform. A point in a hot region would lower the dose of the whole plan, and a point in a low-dose region would raise it. ICRU 83 therefore recommends a volume prescription, and recommends reporting the dose to 50% of the PTV, D<sub>50%</sub>, because it is reproducible across systems and plans."),
        EX("Reading a prescription", STEM("A prescription written as 1800 cGy × 3.", [], "What is the [[total dose]]?"), ["Total = 1800 cGy × 3"], "5400 cGy, or 54 Gy. Written as 3 Gy × 18 it is the same total but a different plan."),
    ],
    cards=[
        F("GTV", "The gross tumour volume: the disease that can be seen on imaging."),
        F("CTV", "The clinical target volume: the GTV plus an expansion for occult disease that cannot be seen."),
        F("ITV", "The internal target volume: an expansion for physiological motion of the target."),
        F("PTV", "The planning target volume: an expansion for variability in patient setup, so that the intended target is treated."),
        F("Treated volume", "The volume enclosed by the isodose surface that the radiation oncologist has chosen as necessary for the purpose of treatment."),
        F("Irradiated volume", "The volume receiving a significant dose relative to normal tissue tolerance, typically inside the 50% isodose line."),
        F("OAR and PRV", "An organ at risk is a structure to be avoided. The planning risk volume expands it for setup variability, especially for serial organs such as the cord."),
        F("Tubular organs", "The ICRU recommends the wall and not the contents. Many planners optimize on the whole organ and evaluate on the wall."),
        F("TG-263", "AAPM Task Group 263: standard names for structures and dose metrics, for example Lung_L, Lungs, and Lungs-PTV."),
        F("Random and systematic setup errors", "Random errors (σ) vary day to day around the mean. A systematic error (Σ) is an offset of the mean that affects every fraction, so it has the larger effect."),
        F("van Herk margin recipe", "PTV margin = 2.5 Σ + 0.7 σ. It rests on assumptions about the population and coverage, so it is used with caution."),
        F("ASTRO prescription", "Treatment site, delivery method, dose per fraction, number of fractions, and total dose, in cGy. Example: L_Lung, Photons, 200 cGy × 32 to 6400 cGy."),
        F("Point prescription", "Reasonable for 3D conformal plans. ICRU 83: a point where dose is calculated accurately (not in build-up, a steep gradient, or an interface) in a central part of the PTV."),
        F("Volume prescription for IMRT", "ICRU 83 recommends a dose-volume prescription and reporting the dose to 50% of the PTV, D<sub>50%</sub>, which is reproducible across systems and plans."),
    ],
)

PROBLEMS = [
    PR("The planning target volume accounts for:", "variability in patient setup", ["microscopic extension of disease", "motion of the target within the patient", "a dose that is significant to normal tissue"],
       "The CTV covers occult disease, the ITV covers motion, and the PTV covers setup variability so that the intended target is treated.", lvl="Easy"),
    PR("The volume enclosed by the isodose surface that the radiation oncologist has chosen for the purpose of treatment is the:", "treated volume", ["irradiated volume", "gross tumour volume", "planning risk volume"],
       "The treated volume follows the prescription isodose. The irradiated volume is larger and is typically taken to be inside the 50% isodose.", lvl="Easy"),
    PR("A planning risk volume is an expansion of:", "an organ at risk, for setup variability", ["the CTV, for motion", "the PTV, for dose gradients", "the GTV, for occult disease"],
       "It is the normal-tissue counterpart of the PTV, and is used mainly for serial organs such as the cord.", lvl="Easy"),
    PR("Which setup error has the larger effect on the PTV margin?", "The systematic error, because it affects every fraction in the same direction", ["The random error, because it varies every day", "They are equal", "Neither, because margins depend only on the target size"],
       "In the recipe 2.5 Σ + 0.7 σ, the systematic error is multiplied by the larger coefficient.", lvl="Moderate"),
    PRN(STEM("Setup errors for a treatment site.", ["systematic error Σ = 2 mm", "random error σ = 3 mm"], "What [[PTV margin]] does the van Herk recipe give?"), m_a, [2 + 3, 2.5 * 3 + 0.7 * 2, 0.7 * 2 + 2.5 * 2], "{:.1f} mm",
        f"Margin = 2.5 × 2 + 0.7 × 3 = {m_a:.1f} mm. Adding the errors gives 5.0, and swapping the coefficients gives {2.5 * 3 + 0.7 * 2:.1f}.", lvl="Moderate"),
    PRN(STEM("A site has a systematic error Σ = 3 mm and a random error σ = 2 mm.", [], "What [[margin]] does the recipe give?"), m_d, [2.5 * 2 + 0.7 * 3, 3 + 2, 2.5 * 3], "{:.1f} mm",
        f"Margin = 2.5 × 3 + 0.7 × 2 = {m_d:.1f} mm.", lvl="Moderate"),
    PR("The ICRU recommends that the rectum be contoured as:", "the wall, and not the contents", ["the contents, and not the wall", "the wall plus a 1 cm margin", "the whole pelvis"],
       "For tubular organs the dose to the wall matters. Planners may optimize on the whole structure but evaluate the wall.", lvl="Moderate"),
    PR("Which prescription is complete under the ASTRO recommendation?", "L_Lung, Photons, 200 cGy × 32 to 6400 cGy", ["64 Gy to the lung", "6400 cGy to L_Lung in 32 fractions", "Lung, 2 Gy, 32"],
       "It gives the site, the delivery method, the dose per fraction, the number of fractions, and the total dose, in cGy and in that order.", lvl="Moderate"),
    PR("An IMRT plan is prescribed to a point that lies in a hot region of the dose distribution. The dose in the rest of the plan is:", "lower than intended", ["higher than intended", "unchanged", "uniform"],
       "Normalizing the dose at a hot point to the prescription scales the whole distribution down.", lvl="Challenging"),
    PR("Why does ICRU 83 recommend reporting D<sub>50%</sub> of the PTV for IMRT plans?", "It is reproducible across systems and plans", ["It is always equal to the maximum dose", "It is the dose at the isocenter", "It ignores hot spots entirely"],
       "A volume-based value is less sensitive than a point value to local high-dose and low-dose regions.", lvl="Challenging"),
    PRN(STEM("Image guidance reduces the systematic error from 2 mm to 1 mm, and the random error stays at 3 mm.", [], "By how many millimetres does the [[PTV margin]] fall?"), m_a - m_b, [m_a - margin(2, 1.5), 1.0, m_a], "{:.2f} mm",
        f"Before: {m_a:.1f} mm. After: {m_b:.1f} mm. The fall is {m_a - m_b:.2f} mm. Halving the random error instead would save only {m_a - margin(2, 1.5):.2f} mm.", lvl="Challenging"),
    PR("54 Gy in 3 written without units for each part is ambiguous because it could mean:", "1800 cGy × 3 fractions or 300 cGy × 18 fractions", ["a single dose of 54 Gy", "5400 cGy × 1 fraction", "a dose to a point or to a volume"],
       "The ASTRO format writes the dose per fraction first, in cGy, then the number of fractions, so that the two numbers cannot be exchanged.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4, 5, 9], 2: [7, 8]}

TERMS = ['planning target volume', 'treated volume', 'organ at risk', 'systematic error', 'van Herk']

TAKE = [
    [('The GTV is the visible disease. The CTV adds occult disease, the ITV adds motion, and the PTV adds setup variability. The treated volume follows the prescription isodose.', 'icru-volumes')],
    [('PTV margin = 2.5 Σ + 0.7 σ. The systematic error Σ has the larger coefficient, so reducing it shrinks the margin most.', 'margin-recipe')],
    [('An ASTRO prescription names the site, the delivery method, the dose per fraction, the number of fractions, and the total, in cGy. For IMRT, prescribe to a volume and report D<sub>50%</sub>.', 'prescription-elements')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Match each volume to what it accounts for.", ["GTV", "CTV", "ITV", "PTV"],
         [("Disease that can be seen on imaging", 0), ("Occult disease that cannot be seen", 1), ("Physiological motion of the target", 2), ("Variability of patient setup", 3)],
         "Each volume is built from the one inside it: the GTV, then the CTV with an expansion for occult disease, the ITV with an expansion for motion, and the PTV with an expansion for setup.", lvl="Moderate", mode="match", cap=1),
    TYPED(STEM("Setup errors for a treatment site.", ["systematic error Σ = 1.5 mm", "random error σ = 2.5 mm"], "What [[PTV margin]] does the recipe give?"), margin(1.5, 2.5), 0.015, "mm",
          f"Margin = 2.5 × 1.5 + 0.7 × 2.5 = 3.75 + 1.75 = {margin(1.5, 2.5):.2f} mm.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the PTV margin from the van Herk recipe against the systematic error, for a random error of 3 mm.", [], "Tap the [[systematic error at which the margin is 10 mm]]."),
         FS(x=dict(min=0, max=5, ticks=[0, 1, 2, 3, 4, 5], label="Systematic error Σ (mm)"), y=dict(min=0, max=16, ticks=[0, 4, 8, 12, 16], label="PTV margin (mm)"), series=[dict(pts=PTS(lambda s: margin(s, 3), 0, 5), color="plot-1")], xunit=" mm", xdec=2, xname="Systematic error", label="PTV margin against systematic error"),
         [((10 - 0.7 * 3) / 2.5 - 0.3, (10 - 0.7 * 3) / 2.5 + 0.3)], f"Solve 2.5 Σ + 0.7 × 3 = 10: Σ = (10 − 2.1) / 2.5 = {(10 - 2.1) / 2.5:.2f} mm. The margin of 10 mm is not a marked level.", lvl="Challenging", note=f"about {(10 - 2.1) / 2.5:.1f} mm"),
]
INLINE = {0: [1, 2, 3, _n0 + 1], 1: [4, 5, 9, _n0 + 3], 2: [7, 8]}


# ---------------------------------------------------------------- motion and the ITV
_n2 = len(PROBLEMS)
itv_len = 30 + 14                                                                   # the target length plus the distance between its two extreme positions
PROBLEMS += [
    PR("How is the internal target volume obtained from a four-dimensional CT of a lung tumour?", "The target is contoured in every phase of the breathing cycle, or on an image built from all of them, and the ITV is the union of these contours", ["The target is contoured on one phase, and the ITV is that contour with the setup margin added", "The target is contoured on the planning CT with the patient breathing freely, and the ITV is the PTV minus the setup margin", "The ITV is the average of the contours in all the phases, which has the volume of the mean target"],
       "The ITV has to contain the target wherever it is during the breathing cycle, so it is the union of its positions. One phase shows only one position, and an average would be smaller than the volume that the target sweeps.", lvl="Moderate"),
    PR("A four-dimensional CT is used for a lung tumour because it:", "shows the position of the target in each phase of the breathing cycle", ["raises the resolution of the planning CT", "gives the electron density without a calibration", "removes the need for any margin for setup error"],
       "The images are sorted by the phase of the breathing cycle, so the motion of the target and of the organs at risk can be seen and measured. The resolution, the calibration, and the setup margin are not changed by the sorting.", lvl="Easy"),
    PRN(STEM("A lung tumour is 30 mm long from superior to inferior, and its position moves 14 mm between the two extreme phases of the breathing cycle.", [], "What [[length]] does the ITV have from superior to inferior?"), itv_len, [30.0, 30 + 14 / 2, 30 + 2 * 14], "{:.0f} mm",
        f"The ITV is the union of the positions, so it is the tumour length plus the distance between the extremes: 30 + 14 = {itv_len} mm. The tumour length alone gives 30 mm, adding half of the motion gives {30 + 14 / 2:.0f} mm, and adding it on both sides gives {30 + 2 * 14} mm.", lvl="Moderate"),
]
INLINE[0].append(_n2 + 1)
