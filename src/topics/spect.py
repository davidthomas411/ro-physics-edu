from blocks import *
import math, calc, real

RB = real.STATS["nm"]["bone"]                                                    # measured on a real bone scan: tools/make_real_nm.py

HL = {"Ga-68": 67.6 / 60, "F-18": 109.8 / 60, "Tc-99m": 6.0, "I-123": 13.2, "In-111": 2.81 * 24, "Xe-133": 5.24 * 24, "I-131": 8.01 * 24}      # half-lives in hours, from the book's table
rem = lambda t, th: 0.5 ** (t / th)                                                                                    # fraction of the activity remaining after time t
tc12, f18_220, tc3 = rem(12, 6.0), rem(220, 109.8), rem(3, 6.0)
r45 = {k: rem(45, m) for k, m in {"F-18": 109.8, "Ga-68": 67.6, "C-11": 20.4, "N-13": 9.97}.items()}                # fractions after 45 minutes
t30 = 6.0 * math.log2(1 / 0.3)                                                                                          # hours for Tc-99m to fall to 30%

TOPIC = dict(
    id="spect", domain=4, sub="IV.A", title="Radioisotopes and SPECT",
    ref=dict(aapm="TG-126", khan="", ford="20"),
    guide=[
        H("Radioisotopes for imaging"),
        P("In nuclear medicine imaging the patient is injected with a small amount of a radiopharmaceutical: a radioactive isotope joined chemically to a compound that probes a biological process. The isotopes decay by different modes and have a wide range of half-lives. The photons that emerge are often the product of a secondary process, such as the annihilation of the positron from <sup>18</sup>F, or the de-excitation of a daughter nucleus."),
        TABLE(["Isotope", "Decay", "Half-life", "Main photon energy", "Production"], [["<sup>99m</sup>Tc", "IT", "6.0 h", "140 keV", "Generator"], ["<sup>123</sup>I", "EC", "13.2 h", "159 keV", "Cyclotron"], ["<sup>131</sup>I", "β<sup>−</sup>", "8.01 d", "364 keV", "Reactor"], ["<sup>111</sup>In", "EC", "2.81 d", "171 and 245 keV", "Cyclotron"], ["<sup>133</sup>Xe", "β<sup>−</sup>", "5.24 d", "81 keV", "Reactor"], ["<sup>18</sup>F", "β<sup>+</sup>", "109.8 min", "511 keV, from annihilation", "Cyclotron"], ["<sup>68</sup>Ga", "β<sup>+</sup>", "67.6 min", "511 keV, from annihilation", "Cyclotron"]]),
        P("The decay modes of Section 2.2 apply here: beta-plus, beta-minus, electron capture, isomeric transition, and internal conversion. For beta decay, neutron-rich isotopes undergo beta-minus decay, have relatively long half-lives, and are made in reactors. Proton-rich isotopes undergo beta-plus decay, have relatively short half-lives, and are made in cyclotrons. <sup>99m</sup>Tc is the daughter of <sup>99</sup>Mo and is supplied by a generator."),

        H("Gamma camera and SPECT"),
        P("Single photon emission computed tomography (SPECT) images the distribution of a radiopharmaceutical that emits single photons. A common clinical use is the perfusion of the myocardium, to evaluate coronary artery disease. <sup>99m</sup>Tc joined to sestamibi is taken up by the healthy heart muscle. <sup>99m</sup>Tc is an excited, metastable state of Tc, and it decays to its ground state with a 140 keV photon that is used for imaging. SPECT is also used in oncology, for example <sup>123</sup>I for the thyroid and <sup>99m</sup>Tc-MDP for bone metastases, although oncologic SPECT competes with PET, which has higher sensitivity, can quantify uptake, and often has higher spatial resolution."),
        P("In a gamma camera the photons interact with a scintillator in the head, which converts them to optical photons that position-sensitive photomultiplier tubes register. A collimator in front of the scintillator provides the spatial localization: a photon entering at an angle is not transmitted to the scintillator. The assembly rotates around the patient and the images are used to reconstruct the distribution of the isotope, as in CT, but this is emission tomography and not transmission tomography. Many scanners have two heads and are coupled to a CT scanner, which gives a CT immediately before or after the SPECT scan for co-localization."),

        P(f"The simplest gamma-camera image is a planar one, a projection of the activity onto a plane. The whole-body bone scan below was made with a <sup>99m</sup>Tc bone agent. Two heads, one in front and one behind the patient, scan as the patient moves through. The matrix is {RB['matrix'][0]} × {RB['matrix'][1]} pixels of {RB['pixel_mm']:.2f} mm, but the resolution is set mainly by the collimator and is much coarser than the pixel. Each pixel holds few counts, at most {RB['peak_counts']:.0f}, so the statistical noise is visible. Structures at different depths overlap in a projection, and SPECT removes the overlap by collecting projections from many angles and reconstructing them."),
        AVF("real-nm-bone"),

        H("Half-life and remaining activity"),
        P("The half-life matters for the choice of isotope and for the signal. After a time t the fraction of the activity remaining is 2<sup>−t/T½</sup>. A short half-life gives a high count rate for the activity injected, but the activity is lost quickly during preparation, transport, and the wait for uptake. The long half-life of <sup>131</sup>I is useful for therapy and imaging over days, whereas the 110-minute half-life of <sup>18</sup>F is long enough to ship from a cyclotron."),
        EX("Activity remaining", STEM("A <sup>99m</sup>Tc agent (half-life 6.0 h) and an <sup>18</sup>F agent (half-life 109.8 min).", ["12 h after the <sup>99m</sup>Tc preparation", "220 min after the <sup>18</sup>F preparation"], "Find the [[fraction remaining]] of each."), ["Fraction = 2<sup>−t/T½</sup>", "<sup>99m</sup>Tc: 12 h is 2 half-lives", "<sup>18</sup>F: 220 min is about 2 half-lives"], f"{100 * tc12:.0f}% of the <sup>99m</sup>Tc and {100 * f18_220:.0f}% of the <sup>18</sup>F remain, because each is about two half-lives old."),
    ],
    cards=[
        F("Radiopharmaceutical", "A radioactive isotope conjugated to a compound that probes a biological process of interest."),
        F("Technetium-99m", "Isomeric transition, half-life 6.0 h, 140 keV photon. An excited state of Tc, the daughter of <sup>99</sup>Mo, supplied by a generator."),
        F("Iodine-123 and iodine-131", "<sup>123</sup>I: electron capture, 13.2 h, 159 keV, cyclotron. <sup>131</sup>I: beta-minus, 8.01 d, 364 keV, reactor."),
        F("Indium-111 and xenon-133", "<sup>111</sup>In: electron capture, 2.81 d, 171 and 245 keV. <sup>133</sup>Xe: beta-minus, 5.24 d, 81 keV."),
        F("Fluorine-18 and gallium-68", "Beta-plus emitters with half-lives of 109.8 min and 67.6 min. The 511 keV photons come from annihilation."),
        F("Neutron-rich and proton-rich isotopes", "Neutron-rich isotopes decay by beta-minus, have long half-lives, and are made in reactors. Proton-rich isotopes decay by beta-plus, have short half-lives, and are made in cyclotrons."),
        F("SPECT", "Single photon emission computed tomography: emission tomography of an isotope that emits single photons, with a rotating gamma camera."),
        F("SPECT cardiac use", "<sup>99m</sup>Tc-sestamibi is taken up by healthy heart muscle, to evaluate perfusion and coronary artery disease."),
        F("Gamma camera", "A collimator, a scintillator that gives light, and position-sensitive photomultiplier tubes. The head rotates around the patient."),
        F("Collimator", "A photon entering the camera at an angle is not transmitted to the scintillator, which gives spatial localization."),
        F("SPECT-CT", "A CT scan immediately before or after the SPECT scan gives co-localization of the activity with the anatomy."),
        F("SPECT against PET in oncology", "PET has higher sensitivity, can quantify uptake, and often has higher spatial resolution."),
    ],
)

PROBLEMS = [
    PR("A radiopharmaceutical is:", "a radioactive isotope joined to a compound that probes a biological process", ["a contrast agent for CT", "a sealed source for brachytherapy", "a detector material"],
       "The compound takes the isotope to the tissue of interest, and the photons from the decay form the image.", lvl="Easy"),
    PR("<sup>99m</sup>Tc emits the photon used for imaging when it:", "decays from an excited state to its ground state, with a 140 keV photon", ["undergoes positron annihilation", "captures an orbital electron", "decays by beta-minus emission to <sup>99</sup>Mo"],
       "<sup>99m</sup>Tc is a metastable excited state of Tc and decays by isomeric transition.", lvl="Easy"),
    PR("Neutron-rich isotopes used in nuclear medicine are typically:", "beta-minus emitters with long half-lives that are made in reactors", ["beta-plus emitters made in cyclotrons", "alpha emitters", "isotopes with very short half-lives"],
       "Proton-rich isotopes are made in cyclotrons, decay by beta-plus, and have short half-lives.", lvl="Easy"),
    PR("The collimator of a gamma camera:", "gives spatial localization, because a photon entering at an angle is not transmitted", ["converts photons into light", "rotates the patient", "amplifies the signal"],
       "The scintillator converts the photons to light and the photomultiplier tubes register it. The collimator selects the direction.", lvl="Easy"),
    PRN(STEM("A <sup>99m</sup>Tc preparation has a half-life of 6.0 h.", [], "What fraction of the activity remains after [[12 h]]?"), tc12, [0.5, 0.125, 1 / 12], "{:.3f}",
        f"12 h is two half-lives, so the fraction is (1/2)² = {tc12:.2f}. One half-life would leave 0.5, and three would leave 0.125.", lvl="Moderate"),
    PRN(STEM("An <sup>18</sup>F preparation has a half-life of 109.8 min.", [], "What fraction of the activity remains after [[220 min]]?"), f18_220, [0.5, 0.125, 1 - 0.25], "{:.3f}",
        f"220 / 109.8 = 2.00 half-lives, so the fraction is (1/2)<sup>2.00</sup> = {f18_220:.3f}.", lvl="Moderate"),
    PR("Which isotope gives the highest PET signal 45 minutes after injection, for the same injected activity and the same uptake?", "<sup>18</sup>F, half-life 109.8 min", ["<sup>68</sup>Ga, half-life 67.6 min", "<sup>11</sup>C, half-life 20.4 min", "<sup>13</sup>N, half-life 10.0 min"],
       f"The fractions remaining after 45 min are {100 * r45['F-18']:.0f}% for <sup>18</sup>F, {100 * r45['Ga-68']:.0f}% for <sup>68</sup>Ga, {100 * r45['C-11']:.0f}% for <sup>11</sup>C, and {100 * r45['N-13']:.0f}% for <sup>13</sup>N. The longest half-life leaves the most activity.", lvl="Moderate"),
    PR("Compared with SPECT in oncology, PET has:", "higher sensitivity, the ability to quantify uptake, and often higher spatial resolution", ["lower sensitivity and a lower resolution", "no need for a CT scan", "photons of lower energy"],
       "These are the reasons oncologic SPECT competes with PET.", lvl="Moderate"),
    PR("A CT scan is acquired with a SPECT scan mainly to:", "co-localize the activity with the anatomy", ["increase the half-life of the isotope", "convert the 140 keV photons to 511 keV", "replace the collimator"],
       "Many scanners combine the two so that the activity can be placed on the anatomy.", lvl="Moderate"),
    PR("SPECT image reconstruction is similar to CT reconstruction, but SPECT is:", "emission tomography, with the source inside the patient", ["transmission tomography with a source outside the patient", "done with a fixed head", "limited to a single projection"],
       "The camera rotates around the patient and the projections are reconstructed to give the distribution of the isotope.", lvl="Challenging"),
    PRN(STEM("A <sup>99m</sup>Tc preparation has a half-life of 6.0 h.", [], "After how many hours does [[30% of the activity]] remain?"), t30, [6.0 * 0.3, 6.0 * 0.5, 6.0 * 2.5], "{:.1f} h",
        f"2<sup>−t/6</sup> = 0.3 gives t = 6 × log<sub>2</sub>(1/0.3) = 6 × 1.737 = {t30:.1f} h. Multiplying 6 by 0.3 gives 1.8 h, which is incorrect.", lvl="Challenging"),
    PR("Why is <sup>18</sup>F more convenient than <sup>15</sup>O for a PET centre that has no cyclotron on site?", "Its half-life of 109.8 min is long enough to ship it, but that of <sup>15</sup>O, about 2 min, is not", ["It emits no positrons", "It has a higher photon energy", "It decays by isomeric transition"],
       "The shortest half-lives are hard to work with, and the 110-minute half-life of <sup>18</sup>F allows time for transport.", lvl="Challenging"),
]

TERMS = ['radiopharmaceutical', 'SPECT', 'collimator', 'generator']

TAKE = [
    [('Neutron-rich isotopes made in reactors decay by beta-minus with long half-lives. Proton-rich isotopes made in cyclotrons decay by beta-plus or electron capture. <sup>99m</sup>Tc comes from a generator.', 'production-route')],
    [('In a gamma camera the collimator gives the direction, the scintillator gives light, and the photomultiplier tubes give the position. The head rotates to reconstruct the distribution.', 'gamma-camera')],
    [('The fraction remaining is 2<sup>−t/T½</sup>. After one half-life half remains, and a short-lived isotope is lost quickly.', 'activity-remaining')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("How is each isotope produced?", ["Reactor", "Cyclotron", "Generator"],
         [("<sup>131</sup>I", 0), ("<sup>133</sup>Xe", 0), ("<sup>18</sup>F", 1), ("<sup>123</sup>I", 1), ("<sup>111</sup>In", 1), ("<sup>99m</sup>Tc", 2)],
         "Neutron-rich beta-minus emitters such as <sup>131</sup>I and <sup>133</sup>Xe come from reactors. Proton-rich isotopes such as <sup>18</sup>F, <sup>123</sup>I, and <sup>111</sup>In come from cyclotrons. <sup>99m</sup>Tc is the daughter of <sup>99</sup>Mo in a generator.", lvl="Moderate"),
    TYPED(STEM("A <sup>99m</sup>Tc preparation has a half-life of 6.0 h.", [], "What [[percentage of the activity]] remains after 3 h?"), 100 * tc3, 0.02, "%",
          f"3 h is half a half-life, so the fraction is 2<sup>−0.5</sup> = {tc3:.3f}, which is {100 * tc3:.1f}%.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the percentage of the <sup>99m</sup>Tc activity remaining against time.", [], "Tap the [[time at which 30% of the activity remains]]."),
         FS(x=dict(min=0, max=24, ticks=[0, 6, 12, 18, 24], label="Time (h)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Activity remaining (%)"), series=[dict(pts=PTS(lambda t: 100 * 0.5 ** (t / 6), 0, 24), color="plot-1")], xunit=" h", xdec=1, xname="Time", label="Activity remaining against time"),
         [(t30 - 2.0, t30 + 2.0)], f"2<sup>−t/6</sup> = 0.3 gives t = {t30:.1f} h. The level 30% is not marked on the axis.", lvl="Challenging", note=f"about {t30:.0f} h"),
]
INLINE = {0: [1, 2, 3, _n0 + 1], 1: [4, 8, 9], 2: [5, 7, _n0 + 2]}
