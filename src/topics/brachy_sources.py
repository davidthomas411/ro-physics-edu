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
        C("Why is HDR brachytherapy delivered by a remote afterloader?", "The source holds about 10 Ci, too active to handle. The afterloader drives it through catheters from a shielded room."),
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
    PR("Cs-137 and Ra-226 sources have mostly been replaced because:", "their long half-lives complicate storage, leak testing, and disposal", ["their photon energies are too low to treat", "they decay too quickly to be useful", "they cannot be encapsulated"],
       "Half-lives of 30 y and 1600 y make a source reusable but hard to retire, and radium releases radon if the capsule leaks. Both emit high-energy photons, which is not a disadvantage.", lvl="Challenging"),
]

INLINE = {0: [1, 3], 1: [2, 5, 7, 9], 2: [4]}

TERMS = ['seed', 'remote afterloader', 'anisotropy']

TAKE = [
    [('LDR is below 2 Gy/h and HDR is above 12 Gy/h. Permanent implants are LDR, and afterloaded implants are HDR.', 'dose-rate-classes')],
    [('LDR seeds (Cs-131, Pd-103, I-125) have low photon energy and short half-lives. Ir-192 is the HDR source: 380 keV mean energy and a 73.8 d half-life.', 'isotope-map')],
    [('The seed capsule contains the source and absorbs electrons and low-energy x-rays. The marker and welds make the dose slightly anisotropic.', 'seed-cutaway'),
     ('An HDR source is a 10 Ci Ir-192 pellet on a cable, driven to dwell positions by a remote afterloader.', 'hdr-afterloader')],
]


# ---------------------------------------------------------------- sorting, ranking, typed, and tap-the-figure questions
t3 = calc.time_to_fraction(0.3, IR_T)
_iso = [("Cs-131", 9.69, 30, "plot-1"), ("Pd-103", 16.99, 21, "plot-1"), ("I-125", 59.4, 28, "plot-1"), ("Ir-192", 73.8, 380, "plot-2"), ("Co-60", 5.27 * 365.25, 1250, "plot-4"), ("Cs-137", 30.1 * 365.25, 662, "plot-4"), ("Ra-226", 1600 * 365.25, 830, "plot-4")]
_fig_iso = FS(x=dict(min=5, max=1e6, log=True, ticks=[10, 100, 1000, 1e4, 1e5, 1e6], fmt="pow", label="Half-life (days), log scale"), y=dict(min=10, max=2000, log=True, ticks=[10, 100, 1000], label="Mean photon energy (keV)"),
              dots=[dict(x=x, y=y, color="plot-1", r=6) for _, x, y, c in _iso], xunit=" d", xname="Half-life", label="Half-life and mean photon energy of seven brachytherapy isotopes; the points are not labelled", h=300)
PROBLEMS += [
    SORT("Rank these isotopes by half-life, shortest first.", ["1st (shortest)", "2nd", "3rd", "4th (longest)"],
         [("Cs-131", 0), ("Pd-103", 1), ("I-125", 2), ("Ir-192", 3)],
         "Cs-131 is 9.7 d, Pd-103 is 17.0 d, I-125 is 59.4 d, and Ir-192 is 73.8 d. The three seed isotopes are all shorter than Ir-192, and the shortest-lived deliver their dose fastest.", lvl="Moderate", mode="rank", cap=1),
]
