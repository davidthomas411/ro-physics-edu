from blocks import *
import math, calc

IR_T, I_T, PD_T, CS131_T = 73.8, 59.4, 16.99, 9.69
a90 = 10 * calc.frac_remaining(90, IR_T)                 # Ci left from 10 Ci after 90 d
t4 = calc.time_to_fraction(0.4, IR_T)                    # days for 10 Ci to fall to 4 Ci
f3 = calc.frac_remaining(91.25, IR_T)                    # fraction left after about three months
a90_mean = 10 * math.exp(-90 / IR_T)                     # trap: half-life used as a mean life
tau = lambda th: th / calc.LN2

TOPIC = dict(
    id="brachy-sources", domain=5, sub="V", title="Brachytherapy sources and isotopes",
    ref=dict(aapm="", khan="15", ford="4"),
    guide=[
        H("Dose-rate classes"),
        P("Brachytherapy treats with sealed radioactive sources placed in or next to the tumour. ICRU Report 38 sorts treatments by the dose rate at the reference point."),
        TABLE(["Class", "Dose rate", "Delivery", "Typical sources"],
              [["Low (LDR)", "below 2 Gy/h", "Permanent seeds, or temporary implants left for days", "I-125, Pd-103, Cs-131; Cs-137 and Ra-226 in the past"],
               ["Medium (MDR)", "2 to 12 Gy/h", "Rarely used", "—"],
               ["High (HDR)", "above 12 Gy/h", "Temporary: minutes per fraction, by remote afterloader", "Ir-192; Co-60 in some units"]]),
        P("A permanent seed implant delivers its dose at a low rate, a few cGy per hour at first, and the dose accumulates over months as the activity decays. An HDR treatment delivers its prescription in minutes and is repeated in fractions. Cells repair sublethal damage during a long, low-rate exposure, so LDR and HDR schedules are not interchangeable at the same total dose."),

        H("Isotopes"),
        P("LDR isotopes decay by electron capture and emit low-energy photons. The photons are absorbed within a few centimetres, so the dose stays in the target and shielding needs are modest. Their half-lives are days to weeks, which suits a permanent implant: most of the dose is delivered while the seeds are in place, and they remain as inert metal."),
        TABLE(["Isotope", "Half-life", "Decay", "Mean photon energy", "Use"],
              [["Cs-131", "9.7 d", "EC", "about 30 keV", "Permanent seeds"],
               ["Pd-103", "17.0 d", "EC", "21 keV", "Permanent seeds"],
               ["I-125", "59.4 d", "EC", "28 keV", "Permanent seeds, eye plaques"],
               ["Ir-192", "73.8 d", "β⁻ (95%), EC (5%)", "380 keV", "HDR; temporary LDR wires"],
               ["Cs-137", "30.1 y", "β⁻", "662 keV", "Gynecologic LDR, now rare"],
               ["Co-60", "5.27 y", "β⁻", "1.25 MeV", "Some HDR units"],
               ["Ra-226", "1600 y", "α chain", "about 0.8 MeV", "Historical"]]),
        P("Ir-192 decays by β⁻ to excited levels of Pt-192 and, about 5% of the time, by electron capture to Os-192. Many levels lead to many photon lines, and the mean photon energy is about 380 keV. A half-life of 73.8 d lets one source treat patients for about three months before it is replaced."),
        P("Cs-137 and Ra-226 have half-lives of 30 y and 1600 y. A long half-life makes a source reusable, but storage, leak testing, and disposal become burdens, and a leaking radium capsule releases radon gas. Both have been replaced by shorter-lived sources."),
        EX("Activity of an HDR source", STEM("An Ir-192 HDR source.", ["initial activity = 10 Ci", "T<sub>1/2</sub> = 73.8 d", "time in use = 90 d"], "Find the [[activity]] after 90 d."),
           [f"Fraction remaining = ½<sup>90/73.8</sup> = ½<sup>{90 / IR_T:.2f}</sup> = {a90 / 10:.3f}", f"A = 10 Ci × {a90 / 10:.3f}"], f"{a90:.1f} Ci."),
        EX("When to replace the source", STEM("An Ir-192 HDR source.", ["initial activity = 10 Ci", "replacement activity = 4 Ci"], "After how many [[days]] does the source fall to 4 Ci?"),
           ["Fraction = 4 / 10 = 0.40", f"t = T<sub>1/2</sub> × log<sub>2</sub>(1 / 0.40) = 73.8 × {math.log2(2.5):.3f}"], f"{t4:.1f} d, about three months."),

        H("Source construction"),
        P("Most seeds are a sealed titanium capsule about 4.5 mm long and 0.8 mm across, small enough to pass through a 17- or 18-gauge needle. The capsule contains the radionuclide. Its thin wall, 0.05 mm of titanium in the I-125 Model 6711, absorbs electrons and the lowest-energy x-rays that would add dose at the seed surface without reaching the target. A dense marker, a silver rod in the 6711 or a lead marker in the Pd-103 Model 200, makes the seed visible on radiographs and CT."),
        P("The marker, the end welds, and the capsule wall absorb photons travelling along the seed axis, so the dose there is lower than at the same distance on the transverse axis. This anisotropy is part of the TG-43 dose calculation."),
        P("An HDR source is a pellet of Ir-192, about 3.6 mm long, in a stainless steel capsule laser-welded to the end of a flexible cable. A new source holds about 10 Ci (370 GBq), far too active to handle. A remote afterloader stores it in a shield, drives the cable through catheters or applicators to programmed dwell positions, and retracts it, all from outside a shielded room."),
        P("Other forms of internal radiation therapy exist. Electronic brachytherapy uses a miniature x-ray tube or an electron source inside an applicator, so no radionuclide is involved. Radiopharmaceutical therapy places unsealed sources in the body, for example I-131 for thyroid cancer or Y-90 microspheres for liver tumours."),
    ],
    cards=[
        C("State the ICRU 38 dose-rate limits for LDR and HDR brachytherapy.", "LDR: below 2 Gy/h. HDR: above 12 Gy/h. Medium dose rate (MDR) lies between them."),
        C("Which delivery is usually permanent, LDR or HDR?", "LDR: the seeds stay in the patient. HDR is temporary: a source is sent into catheters and withdrawn."),
        C("Name three LDR seed isotopes.", "I-125, Pd-103, and Cs-131. All decay by electron capture and emit low-energy photons."),
        C("How does Ir-192 decay, and what is its mean photon energy?", "About 95% β⁻ to Pt-192 and 5% electron capture to Os-192. Many photon lines, with a mean energy of about 380 keV."),
        C("What is the half-life of Ir-192, and what does it imply?", "73.8 d. An HDR source is replaced about every three months, close to 1.2 half-lives."),
        C("What are the half-lives and mean photon energies of I-125 and Pd-103?", "I-125: 59.4 d, 28 keV. Pd-103: 17.0 d, 21 keV."),
        C("Why were Cs-137 and Ra-226 phased out?", "Their half-lives (30 y and 1600 y) make storage, leak testing, and disposal difficult. Radium also releases radon gas."),
        C("What does the seed capsule do?", "Contains the radionuclide, absorbs unwanted electrons and low-energy x-rays, and holds a radiographic marker."),
        C("Why is the dose around a seed not spherically symmetric?", "The marker, end welds, and capsule absorb photons along the seed axis, so the dose there is lower (anisotropy)."),
        C("Why is HDR brachytherapy delivered by a remote afterloader?", "The source holds about 10 Ci, too active to handle. The afterloader drives it through catheters from a shielded room."),
        C("What is the approximate activity of a new HDR Ir-192 source?", "About 10 Ci (370 GBq)."),
        C("Why do LDR seeds use low-energy photons?", "They are absorbed within a few centimetres, so the dose stays in the target and shielding and radiation protection are easier."),
        C("Name two forms of brachytherapy that do not use seeds.", "HDR afterloading with a single Ir-192 source on a cable, and electronic brachytherapy with a miniature x-ray tube."),
    ],
)

PROBLEMS = [
    PR("ICRU Report 38 defines high-dose-rate brachytherapy as a dose rate at the reference point above:", "12 Gy/h", ["2 Gy/h", "0.4 Gy/h", "50 Gy/h"],
       "LDR is below 2 Gy/h, MDR is 2 to 12 Gy/h, and HDR is above 12 Gy/h.", lvl="Easy"),
    PR("Which radionuclide is used in most HDR afterloaders?", "Ir-192", ["I-125", "Pd-103", "Cs-131"],
       "Ir-192 has a mean photon energy of about 380 keV and a half-life of 73.8 d, and it can be made at the high specific activity that HDR needs. I-125, Pd-103, and Cs-131 are low-energy LDR seed isotopes.", lvl="Easy"),
    PR("Which implant is normally left in the patient permanently?", "LDR seeds such as I-125", ["HDR Ir-192 delivered by an afterloader", "A Co-60 teletherapy source", "An electronic brachytherapy x-ray tube"],
       "LDR seeds are low-energy, short-lived sources that deliver their dose over weeks to months, so they are implanted and left in place. HDR sources are withdrawn after each fraction.", lvl="Easy"),
    PR("What is the main purpose of the 0.05 mm titanium wall of an I-125 seed?", "To seal the source and absorb electrons and the lowest-energy x-rays", ["To raise the photon energy", "To make the dose distribution more anisotropic", "To lengthen the half-life of the source"],
       "The wall contains the radionuclide and filters radiation that would add dose at the seed surface without reaching the target. It does not change the half-life or the photon energy. Anisotropy is an unwanted side effect of the marker and welds.", lvl="Moderate"),
    PRN(STEM("An Ir-192 HDR source.", ["initial activity = 10 Ci", "T<sub>1/2</sub> = 73.8 d", "time in use = 90 d"], "What [[activity]] remains?"), a90, [a90_mean, 5.0, 10 * 0.5 ** (IR_T / 90)], "{:.2f} Ci",
        f"The fraction remaining is ½<sup>90/73.8</sup> = {a90 / 10:.3f}, so A = {a90:.2f} Ci. One half-life would leave 5.0 Ci. Using e<sup>−t/T</sup> gives {a90_mean:.2f} Ci because it treats the half-life as a mean life.", lvl="Moderate"),
    PR("Why is an Ir-192 HDR source replaced about every three months?", "Its activity has fallen below half of its initial value, so treatment times grow", ["Its photon energy rises as it decays", "Its half-life increases with use", "The capsule absorbs more of the radiation"],
       f"Three months is about 1.2 half-lives of 73.8 d, so the activity is down to {f3:.0%}. Treatment times scale inversely with activity, so the same dose takes more than twice as long.", lvl="Moderate"),
    PR("Pd-103 has a half-life of 17 d and I-125 has 59.4 d. For the same total dose from a permanent implant, which statement is correct?", "Pd-103 starts at a higher dose rate", ["Pd-103 starts at a lower dose rate", "Both start at the same dose rate", "Pd-103 delivers more total dose"],
       f"Total dose is the initial dose rate times the mean life, and the mean life is 1.44 T<sub>1/2</sub>: {tau(PD_T):.1f} d for Pd-103 and {tau(I_T):.1f} d for I-125. A shorter-lived isotope needs a higher starting rate to reach the same total.", lvl="Moderate"),
    PRM("Which statements about HDR brachytherapy with Ir-192 are correct?", ["The source is delivered by a remote afterloader", "The source is temporary", "A new source has an activity of about 10 Ci"], ["The source is left in the patient permanently", "The dose rate is below 2 Gy/h"],
        "HDR means above 12 Gy/h. The source is a 10 Ci pellet on a cable, driven into catheters by an afterloader and withdrawn after each fraction.", lvl="Moderate"),
    PR("Cs-137 and Ra-226 sources have mostly been replaced because:", "their long half-lives complicate storage, leak testing, and disposal", ["their photon energies are too low to treat", "they decay too quickly to be useful", "they cannot be encapsulated"],
       "Half-lives of 30 y and 1600 y make a source reusable but hard to retire, and radium releases radon if the capsule leaks. Both emit high-energy photons, which is not a disadvantage.", lvl="Challenging"),
    PRN(STEM("Compare two sources.", ["new HDR Ir-192 source: 10 Ci", "I-125 seed: 0.50 mCi"], "By what [[factor]] does the HDR activity exceed the seed activity?"), 10000 / 0.5, [2000.0, 200000.0, 20.0], "{:,.0f}",
        "10 Ci = 10,000 mCi, and 10,000 / 0.50 = 20,000. The HDR source is so active that it cannot be handled and must be loaded remotely.", lvl="Challenging"),
]

INLINE = {0: [1, 3], 1: [2, 5, 7], 2: [4, 8]}

TERMS = ['seed', 'remote afterloader', 'anisotropy']

TAKE = [
    [('LDR is below 2 Gy/h and HDR is above 12 Gy/h. Permanent implants are LDR, and afterloaded implants are HDR.', 'dose-rate-classes')],
    [('LDR seeds (Cs-131, Pd-103, I-125) have low photon energy and short half-lives. Ir-192 is the HDR source: 380 keV mean energy and a 73.8 d half-life.', 'isotope-map')],
    [('The seed capsule contains the source and absorbs electrons and low-energy x-rays. The marker and welds make the dose slightly anisotropic.', 'seed-cutaway'),
     ('An HDR source is a 10 Ci Ir-192 pellet on a cable, driven to dwell positions by a remote afterloader.', 'hdr-afterloader')],
]


# ---------------------------------------------------------------- sorting, ranking, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
t3 = calc.time_to_fraction(0.3, IR_T)
_iso = [("Cs-131", 9.69, 30, "plot-1"), ("Pd-103", 16.99, 21, "plot-1"), ("I-125", 59.4, 28, "plot-1"), ("Ir-192", 73.8, 380, "plot-2"), ("Co-60", 5.27 * 365.25, 1250, "plot-4"), ("Cs-137", 30.1 * 365.25, 662, "plot-4"), ("Ra-226", 1600 * 365.25, 830, "plot-4")]
_fig_iso = FS(x=dict(min=5, max=1e6, log=True, ticks=[10, 100, 1000, 1e4, 1e5, 1e6], fmt="pow", label="Half-life (days), log scale"), y=dict(min=10, max=2000, log=True, ticks=[10, 100, 1000], label="Mean photon energy (keV)"),
              dots=[dict(x=x, y=y, color="plot-1", r=6) for _, x, y, c in _iso], xunit=" d", xname="Half-life", label="Half-life and mean photon energy of seven brachytherapy isotopes; the points are not labelled", h=300)
PROBLEMS += [
    SORT("Does each statement describe LDR or HDR brachytherapy?", ["LDR", "HDR"],
         [("Below 2 Gy/h", 0), ("Above 12 Gy/h", 1), ("Usually a permanent implant", 0), ("Delivered by a remote afterloader", 1), ("I-125, Pd-103, or Cs-131", 0), ("Ir-192 pellet on a cable", 1), ("Seeds of about 0.5 mCi", 0), ("Source of about 10 Ci", 1)],
         "LDR is below 2 Gy/h and uses small, low-energy seeds that are usually left in place. HDR is above 12 Gy/h and uses a 10 Ci Ir-192 source that a remote afterloader sends into catheters and withdraws.", lvl="Easy"),
    SORT("Rank these isotopes by half-life, shortest first.", ["1st (shortest)", "2nd", "3rd", "4th (longest)"],
         [("Cs-131", 0), ("Pd-103", 1), ("I-125", 2), ("Ir-192", 3)],
         "Cs-131 is 9.7 d, Pd-103 is 17.0 d, I-125 is 59.4 d, and Ir-192 is 73.8 d. The three seed isotopes are all shorter than Ir-192, and the shortest-lived deliver their dose fastest.", lvl="Moderate", mode="rank", cap=1),
    TYPED(STEM("An Ir-192 HDR source.", ["initial activity = 10 Ci", "T<sub>1/2</sub> = 73.8 d", "replacement activity = 3 Ci"], "After how many [[days]] does the activity reach 3 Ci?"), t3, 0.015, "d",
          f"The fraction is 3 / 10 = 0.30, and t = T<sub>1/2</sub> log<sub>2</sub>(1 / 0.30) = 73.8 × {math.log2(1 / 0.3):.3f} = {t3:.1f} d. Using the natural logarithm in place of log<sub>2</sub> gives {IR_T * math.log(1 / 0.3):.1f} d.", lvl="Challenging"),
    FIGQ(STEM("Each point is a brachytherapy isotope, plotted by half-life and mean photon energy. The points are not labelled.", [], "Tap the isotope used in most [[HDR afterloaders]]."), _fig_iso, [(50, 110, 250, 570)],
         "Ir-192 has a half-life of 73.8 d and a mean photon energy of about 380 keV. The three seed isotopes (Cs-131, Pd-103, I-125) are at 21 to 30 keV, and the sources at similar or higher energy (Cs-137 at 662 keV, Ra-226, Co-60 at 1250 keV) have half-lives of years or centuries.", lvl="Moderate", note="Ir-192 (73.8 d, 380 keV)"),
    FIGQ(STEM("Each point is a brachytherapy isotope, plotted by half-life and mean photon energy. The points are not labelled.", [], "Tap the isotope whose source emits a [[662 keV photon]], which comes from its daughter Ba-137m."), _fig_iso, [(6000, 20000, 520, 850)],
         "Cs-137 has a half-life of 30.1 y, about 11,000 d, and decays to Ba-137m, which emits the 662 keV photon. Co-60 emits two photons that average 1250 keV, and Ra-226 averages about 830 keV.", lvl="Moderate", note="Cs-137 (30.1 y, 662 keV)"),
    FIGQ(STEM("Each point is a brachytherapy isotope, plotted by half-life and mean photon energy. The points are not labelled. A permanent implant of one of these isotopes delivers 90% of its total dose in about two months, or 60 days.", [], "Tap the [[isotope]]."), _fig_iso, [(12.5, 24, 14, 32)],
         "90% of the total dose is delivered after 3.32 half-lives, so a half-life of about 60 / 3.32 = 18 d is needed. The point near 17 d is Pd-103 (17.0 d, 21 keV), which delivers 90% in 3.32 × 17.0 = 56 d. Cs-131 (9.7 d) would take 32 d, I-125 (59.4 d) 197 d, and Ir-192 (73.8 d) 245 d.", lvl="Challenging", note="Pd-103 (17.0 d)"),
]
INLINE = {0: [1, 3, _n0 + 1], 1: [2, 5, 7, _n0 + 2, _n0 + 4, _n0 + 5, _n0 + 6], 2: [4, 8]}
