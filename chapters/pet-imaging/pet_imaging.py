from blocks import *
import math, calc, real
import nistdata as N

RS = real.STATS["pet"]["suv"]                                                    # measured on a real FDG PET/CT: tools/make_real_pet.py

_w = N.WATER                                                     # NIST water: mu/rho at 0.5 and 0.6 MeV, interpolated log-log to 511 keV
mu511 = math.exp(math.log(_w[0.5][0]) + math.log(0.511 / 0.5) / math.log(0.6 / 0.5) * (math.log(_w[0.6][0]) - math.log(_w[0.5][0])))
surv = lambda L: math.exp(-mu511 * L)                            # both photons escape: exp(-mu x (path to one detector + path to the other)) = exp(-mu L) for a line of response with total path length L
acf = lambda L: math.exp(mu511 * L)
suv = lambda c, dose_kbq, wt_g: c / (dose_kbq / wt_g)            # activity concentration (kBq/mL) over the injected activity per gram of body weight
suv_a = suv(20, 370000, 74000)
suv_t = suv(18, 296000, 80000)
L_4 = math.log(4) / mu511
suv_dc = lambda c, a_mbq, wt_kg, t, th: c / (a_mbq * 1000 * 2 ** (-t / th) / (wt_kg * 1000))     # SUV with the injected activity decayed to the scan time t (same unit as the half-life th)
suv_d = suv_dc(12, 370, 75, 60, 109.8)
suv_nd = suv_dc(12, 370, 75, 0, 109.8)                                                           # the activity at injection, with no decay
suv_up = suv_dc(12, 370, 75, -60, 109.8)                                                         # the decay applied in the wrong direction

TOPIC = dict(
    id="pet-imaging", domain=4, sub="IV.A", title="PET imaging",
    ref=dict(aapm="TG-126", khan="", ford="20"),
    guide=[
        H("Annihilation and coincidence"),
        P("In positron emission tomography (PET) the tracer, for example <sup>18</sup>F-fluorodeoxyglucose (FDG), accumulates in the tumour. A typical FDG protocol has the patient fast for at least 6 hours to lower the glucose level, then injects the tracer intravenously and waits about 1 hour for uptake, with minimal physical activity to reduce uptake in the muscles. The isotope decays and releases a positron, which has some energy and travels a short distance in the tissue: for F-18 the mean range in water is about 0.6 mm and the maximum is 2.4 mm, and emitters with a higher positron energy travel farther. When it slows it annihilates with an electron. [[1|The annihilation produces two photons, each of 511 keV.]] The energy is the rest-mass energy of the electron and the positron, because energy is conserved. [[1|The two photons emerge in opposite directions, because the momentum must also be conserved.]]"),
        P("The photons are registered in the crystals of a detector ring as events that are approximately coincident in time. The energy of the photons is known, so the detector can accept only photons in a small energy window around 511 keV, which rejects background and scattered photons of lower energy. [[1|Each coincident event defines a line of response (LOR).]] The annihilation occurred somewhere along the line, but the position along it is not known. As more events accumulate at different angles, tomographic reconstruction gives the distribution of the isotope. Since the early 2000s most PET scanners have a CT unit attached (PET-CT). The CT is acquired immediately before or after the PET scan, for co-localization and for attenuation correction."),

        H("Resolution and SUV"),
        P("[[1|The typical spatial resolution of PET is 4 to 5 mm.]] Four factors affect it. The two photons are not exactly anti-parallel, because the positron and the electron carry a small net momentum when they annihilate, which makes the photons non-collinear, so the line of response does not pass exactly through the annihilation point. The size of the crystals in the detector ring limits it. The energy of the positron sets how far it travels before annihilating, which blurs the response. The reconstruction algorithm and filters also play a part. The resolution of PET is substantially worse than that of CT."),
        PHOTO("pet-imaging-crystal-arrays"),
        P("The values in a PET image are often reported as the standardized uptake value (SUV), [[1|defined voxel by voxel as the measured activity concentration divided by the injected activity per unit body weight]]. [[1|Many factors affect it, so it is a semi-quantitative measure.]]"),
        EQ("[[1|SUV = activity concentration / (injected activity / body weight)]]"),
        EX("A standardized uptake value", STEM("A tumour has an activity concentration of 20 kBq/mL. The injected activity was 370 MBq in a patient of 74 kg.", [], "Find the [[SUV]]."), ["Injected activity per gram = 370,000 kBq / 74,000 g = 5.0 kBq/g", "SUV = 20 kBq/mL / 5.0 kBq/g"], f"SUV = {suv_a:.1f}. The tumour concentrates the tracer four times more than if it were spread evenly through the body."),

        P(f"In a real FDG PET/CT, the patient weighed {RS['weight_kg']:.0f} kg and was injected with {RS['dose_MBq']:.0f} MBq, and the scan started {RS['uptake_min']:.0f} min later. With a half-life of {RS['half_life_min']:.1f} min, {RS['act_scan_MBq']:.0f} MBq of the injected activity remained, and that decayed activity goes in the formula. A concentration of {RS['tumour_kbq_ml']:.0f} kBq/mL in the tumour is then an SUV of {RS['tumour_suvmax']:.1f}. The PET pixels are {RS['pet_mm']:.1f} mm and the CT pixels {RS['ct_mm']:.2f} mm, so the PET is resampled onto the CT grid for the fusion and is far coarser than the CT."),
        AVF("real-pet-suv"),

        H("Attenuation correction"),
        P("The annihilation photons are attenuated as they leave the patient, and the attenuation is not uniform. It depends on the tissue and on where the annihilation occurred. Lung, for example, attenuates less than other soft tissue. If the attenuation is not corrected, more counts emerge from the lung, and the lung appears to have activity, although it has none. A PET image without attenuation correction also shows a hot ring around the skin and a bright signal at the lateral edge of the liver. The correction uses the CT in the reconstruction, which is another reason to have a CT in the unit, and it gives a far more realistic image of the activity."),
        P("For a coincidence the two photons travel along the same line, one to each detector. [[1|The probability that both escape is e<sup>−μ(x₁ + x₂)</sup> = e<sup>−μL</sup>, where L is the total path through the patient along the line. It does not depend on where along the line the annihilation occurred, so the correction factor for a line is e<sup>μL</sup>]], found from the CT."),
        EX("An attenuation correction factor", STEM("A line of response passes through 20 cm of water-equivalent tissue. μ = " + f"{mu511:.4f}" + " cm<sup>−1</sup> at 511 keV.", [], "Find the [[probability that both photons escape]] and the [[correction factor]]."), ["Escape probability = e<sup>−μL</sup> = e<sup>−" + f"{mu511:.4f}" + " × 20</sup>", "Correction factor = e<sup>μL</sup>"], f"{100 * surv(20):.1f}% of the pairs are detected, so the counts along the line must be multiplied by {acf(20):.1f}."),

        P("In one real FDG scan reconstructed twice from the same data, without and with attenuation correction, the uncorrected image shows a hot body surface and hot arms, the liver almost disappears, and streaks run through the tumour. The DICOM header of the corrected series lists attenuation (ATTN) and scatter (SCAT) among its corrections, and the header of the uncorrected series lists neither."),
        AVF("real-pet-ac"),

        H("PET tracers"),
        P("<sup>18</sup>F-FDG is the most widely used PET radiopharmaceutical, but other compounds probe other processes. <sup>11</sup>C-flumazenil binds the benzodiazepine receptor and is used in epilepsy, and <sup>11</sup>C-raclopride binds the D2 receptor in movement disorders. [[1|<sup>13</sup>N-ammonia measures blood perfusion in the myocardium, and <sup>15</sup>O-water and <sup>15</sup>O-carbon dioxide measure blood perfusion in brain activation studies.]] [[1|FDG follows glucose metabolism in oncology, neurology, and cardiology.]] [[1|<sup>18</sup>F-fluoride follows bone metabolism in oncology, and <sup>18</sup>F-fluoromisonidazole (FMISO) shows hypoxia]], which matters for the response to radiotherapy."),
        P("The isotopes differ in half-life and positron energy. Those with short half-lives, about 20 min for <sup>11</sup>C, 10 min for <sup>13</sup>N, and 2 min for <sup>15</sup>O, are hard to work with. The half-life of <sup>18</sup>F, 109.8 min, is a large part of its convenience, and it also has the lowest positron energy of the group, so its positron has the shortest range."),
        P("Other tracers bind specific targets. Ligands of the prostate-specific membrane antigen (PSMA) are labelled with <sup>68</sup>Ga, as in <sup>68</sup>Ga-PSMA-11, or with <sup>18</sup>F and are used in prostate cancer. <sup>68</sup>Ga-DOTATATE binds somatostatin receptors and is used for neuroendocrine tumours. In three real F-18 scans the distribution follows the process each tracer probes: FDG follows glucose use, sodium fluoride follows bone formation, and the PSMA ligand follows the antigen."),
        AVF("real-pet-tracers"),
    ],
    cards=[
        F("PET annihilation photons", "A positron travels a short distance (for F-18, 0.6 mm on average and at most 2.4 mm), annihilates with an electron, and gives two 511 keV photons."),
        F("Energy of the annihilation photons", "Energy is conserved: the rest-mass energy of the electron and of the positron, 511 keV each, goes to the two photons."),
        F("Direction of the annihilation photons", "They travel in opposite directions, about 180° apart, because there was no net momentum before the annihilation."),
        F("Coincidence detection", "The two photons are registered in the detector ring as events that are approximately coincident in time."),
        F("Line of response", "Each coincident event defines a line. The annihilation was somewhere along it, which tomographic reconstruction resolves."),
        F("PET energy window", "Only photons near 511 keV are accepted, which rejects scattered and background photons."),
        F("PET resolution", "About 4 to 5 mm, worse than CT."),
        F("Factors in PET resolution", "Photon non-collinearity, the crystal size, the positron energy (range), and the reconstruction algorithm and filters."),
        F("Non-collinearity", "The positron and the electron carry a small net momentum when they annihilate, so the photons are not exactly anti-parallel (a spread of about 0.5°)."),
        F("Standardized uptake value", "SUV = activity concentration / (injected activity / body weight). It is semi-quantitative, because many factors affect it."),
        F("Attenuation in PET", "Lung attenuates less than other soft tissue, so without correction it appears to have activity."),
        F("Attenuation correction in PET", "Uses the attached CT in the reconstruction. The pair of photons on a line escapes with e<sup>−μL</sup>, whatever the position of the annihilation."),
        F("PET-CT", "Standard since the early 2000s. The CT gives co-localization and the attenuation correction."),
        F("FDG protocol", "Fast at least 6 hours, inject intravenously, wait about 1 hour for uptake with minimal physical activity."),
        F("FMISO", "<sup>18</sup>F-fluoromisonidazole: a PET tracer of hypoxia, used to follow the response to radiotherapy."),
    ],
)

PROBLEMS = [
    PR("What is measured in a PET scanner to create the image?", "The two 511 keV photons from an annihilation", ["The 140 keV photon of an isomeric transition", "The positron itself", "The electron emitted in beta decay"],
       "The positron annihilates within a few mm of its origin, and the two photons escape and reach the detector ring.", lvl="Easy"),
    PR("The two annihilation photons emerge in opposite directions because:", "momentum is conserved", ["the positron is charged", "the detector ring attracts them", "they have different energies"],
       "There was no net momentum before the annihilation, so there is none after it.", lvl="Easy"),
    PR("Each annihilation photon has an energy of 511 keV because:", "the rest-mass energy of the electron or the positron is 511 keV", ["the isotope has a half-life of 511 min", "the detector sets it", "the positron has a kinetic energy of 511 keV"],
       "Energy is conserved: the total rest-mass energy of the pair is 2 × 511 keV, shared between two photons.", lvl="Easy"),
    PR("A line of response is defined by:", "two photons registered approximately at the same time in the detector ring", ["one photon registered in a collimator", "the path of the positron", "the CT scan"],
       "The annihilation occurred somewhere along the line joining the two detectors.", lvl="Easy"),
    PR("An energy window around 511 keV in a PET detector:", "rejects scattered photons, because they have lower energy", ["rejects the true coincidences", "raises the positron range", "removes the need for a CT"],
       "Scattered photons lose energy, so the window rejects them and keeps the true events.", lvl="Moderate"),
    PR("The typical spatial resolution of a clinical PET image is about:", "4 to 5 mm", ["0.4 to 0.5 mm", "4 to 5 cm", "40 to 50 mm"],
       "It is worse than CT, because of the non-collinearity, the crystal size, the positron range, and the reconstruction.", lvl="Moderate"),
    PRN(STEM("A tumour has an activity concentration of 20 kBq/mL. The injected activity was 370 MBq in a patient of 74 kg.", [], "What is the [[SUV]]?"), suv_a, [20 / 370, 20 * 5.0, 20 / 74], "{:.1f}",
        f"The injected activity per gram is 370,000 kBq / 74,000 g = 5.0 kBq/g, and SUV = 20 / 5.0 = {suv_a:.1f}. Dividing by the dose alone gives {20 / 370:.2f}.", lvl="Moderate"),
    PRN(STEM("A line of response passes through 20 cm of water-equivalent tissue. μ = " + f"{mu511:.4f}" + " cm<sup>−1</sup> at 511 keV.", [], "What is the [[attenuation correction factor]]?"), acf(20), [surv(20), 1 + mu511 * 20, math.exp(mu511 * 10)], "{:.1f}",
        f"The factor is e<sup>μL</sup> = e<sup>{mu511 * 20:.2f}</sup> = {acf(20):.1f}. The inverse, {surv(20):.3f}, is the probability that both photons escape.", lvl="Moderate"),
    PR("Without attenuation correction, a PET image shows:", "apparent activity in the lungs, because they attenuate the photons less", ["low activity in the lungs", "a loss of the 511 keV photons", "a higher resolution"],
       "More counts emerge from the lung, but not because it has more tracer. There is also a hot ring at the skin and a bright signal at the edge of the liver.", lvl="Moderate"),
    PR("Why is a CT unit attached to a PET scanner?", "To co-localize the activity with the anatomy and to give the attenuation correction", ["To raise the PET resolution", "To raise the positron energy", "To avoid the energy window"],
       "The CT does not improve the intrinsic resolution of the PET.", lvl="Moderate"),
    PR("<sup>18</sup>F-fluoromisonidazole (FMISO) is a PET tracer of:", "hypoxia, which is relevant to the response to radiotherapy", ["glucose metabolism", "bone metabolism", "myocardial perfusion"],
       "FDG follows glucose metabolism, fluoride follows bone, and <sup>13</sup>N-ammonia follows myocardial perfusion.", lvl="Challenging"),
    PR("Before an FDG scan the patient fasts for at least 6 hours in order to:", "lower the glucose level", ["raise the positron energy", "lower the half-life of <sup>18</sup>F", "raise the attenuation"],
       "Glucose competes with FDG for uptake, so a low glucose level increases the tumour uptake.", lvl="Moderate"),
]

INLINE = {0: [1, 2, 3, 5], 1: [6, 7, 13, 15], 2: [8, 9, 10], 3: [11, 12, 14]}

TERMS = ['line of response', 'coincidence', 'standardized uptake value', 'attenuation correction']

TAKE = [
    [('The positron annihilates and gives two 511 keV photons in opposite directions. Coincident detection defines a line of response.', 'lor-events')],
    [('PET resolution is about 4 to 5 mm. SUV is the concentration divided by the injected activity per unit weight, and it is semi-quantitative.', 'suv-calc')],
    [('Both photons of a pair escape with e<sup>−μL</sup>, whatever the position of the annihilation along the line. The correction factor is e<sup>μL</sup>.', 'pet-attenuation')],
    [('FDG follows glucose metabolism, fluoride follows bone, FMISO shows hypoxia, and ammonia and water follow perfusion.', 'tracer-map')],
]


# ---------------------------------------------------------------- select-several, sorting, typed, and tap-the-figure questions
PROBLEMS += [
    PRM("Which of the following limit the spatial resolution of PET?", ["The non-collinearity of the annihilation photons", "The size of the crystals in the detector ring", "The range of the positron in the tissue"], ["The photon energy of 511 keV", "The half-life of the isotope", "The weight of the patient"],
        "The two photons are not exactly anti-parallel, the crystals have a size, and the positron travels before it annihilates. The photon energy is the same for every isotope and the half-life does not blur the image.", lvl="Moderate"),
    SORT("Which process does each PET tracer follow?", ["Glucose metabolism", "Hypoxia", "Perfusion", "Bone metabolism"],
         [("<sup>18</sup>F-FDG", 0), ("<sup>18</sup>F-FMISO", 1), ("<sup>13</sup>N-ammonia", 2), ("<sup>15</sup>O-water", 2), ("<sup>18</sup>F-fluoride", 3), ("FDG in a tumour", 0)],
         "FDG follows glucose metabolism, FMISO shows hypoxia, ammonia and water follow blood perfusion, and fluoride follows bone metabolism.", lvl="Moderate"),
]


# ---------------------------------------------------------------- SUV with decay, and tracers by target
PROBLEMS += [
    PRN(STEM("A patient of 75 kg is injected with 370 MBq of <sup>18</sup>F-FDG (half-life 109.8 min). The scan starts 60 min after the injection, and the image is decay-corrected to the start of the scan. A tumour has an activity concentration of 12 kBq/mL.", [], "What is the [[SUV]]?"), suv_d, [suv_nd, suv_up, suv_d * 2], "{:.2f}",
        f"The activity left at the scan is 370 × 2<sup>−60/109.8</sup> = {370 * 2 ** (-60 / 109.8):.0f} MBq, which is {1000 * 370 * 2 ** (-60 / 109.8) / 75000:.2f} kBq/g. SUV = 12 / {1000 * 370 * 2 ** (-60 / 109.8) / 75000:.2f} = {suv_d:.2f}. Leaving out the decay gives {suv_nd:.2f}, and applying it in the wrong direction gives {suv_up:.2f}.", lvl="Challenging"),
]
