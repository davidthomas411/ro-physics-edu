from blocks import *
import math


# ---------------------------------------------------------------- formulas quoted in the text
def r_lcpe(tpr):
    """Lateral charged-particle equilibrium range in cm from TPR20,10 of the 10 x 10 cm field (TRS-483)."""
    return 8.369 * tpr - 4.382

def min_fwhm(tpr, d):
    """Smallest FWHM (cm) that keeps the outer edge of a detector of outer width d (cm) at least r_LCPE inside each field edge."""
    return 2 * r_lcpe(tpr) + d

def out_of_sphere(R, d):
    """Fraction of a sphere of radius R left outside an identical sphere shifted by d (d < 2R): one minus the lens-shaped overlap, pi (4R + d)(2R - d)^2 / 12, over 4 pi R^3 / 3."""
    return 1 - (4 * R + d) * (2 * R - d) ** 2 / (16 * R ** 3)

def ci_rtog(piv, tv): return piv / tv
def ci_paddick(tv, piv, tv_piv): return tv_piv ** 2 / (tv * piv)
def gi(piv50, piv): return piv50 / piv
def bed(n, d, ab): return n * d * (1 + d / ab)
def chord(r, deg): return 2 * r * math.sin(math.radians(deg) / 2)         # displacement of a point turned by deg about an axis r away
def sphere_r(v): return (3 * v / (4 * math.pi)) ** (1 / 3)                 # radius of a sphere of volume v


# ---------------------------------------------------------------- numbers of the text and the worked examples
out10, out20 = out_of_sphere(5.0, 1.0), out_of_sphere(10.0, 1.0)            # 1 mm shift of a 10 mm and a 20 mm spherical target
r66, r68 = r_lcpe(0.66), r_lcpe(0.68)                                       # 6 MV beams
DIO, K_DIO = 0.684, 0.958                                                   # worked example: unshielded diode, ratio of readings and k (illustrative)
ICH, K_ICH = 0.622, 1.053                                                   # small ion chamber
om_dio, om_ich = DIO * K_DIO, ICH * K_ICH
TV, PIV, TVP, P50 = 2.10, 2.40, 2.02, 7.70                                  # cm3: target, prescription isodose, target inside it, half-prescription volume
ci_a, pad_a, gi_a = ci_rtog(PIV, TV), ci_paddick(TV, PIV, TVP), gi(P50, PIV)
fall_a = 10 * (sphere_r(P50) - sphere_r(PIV))                               # mm between the two surfaces, as equivalent spheres
b24, b54, b55 = bed(1, 24, 10), bed(3, 18, 10), bed(5, 11, 10)
ch_a, ch_180 = chord(1.0, 90), chord(1.0, 180)

TOPIC = dict(
    id="srs-sbrt", domain=6, sub="VI.C", title="Stereotactic radiosurgery and SBRT",
    ref=dict(aapm="TG-101, TG-135, TG-155", khan="", ford="22"),
    guide=[
        H("Stereotactic systems and localization"),
        P("Stereotactic radiosurgery (SRS) treats a small intracranial target with a high dose and a targeting accuracy of about 1 mm, classically in one fraction and, by current definitions (ACR, ASTRO), in up to five. Stereotactic body radiotherapy (SBRT, also SABR) treats targets outside the skull the same way, in one to five fractions."),
        P(f"The dose falls steeply outside the target, the margin is small or zero, and few fractions leave no averaging of errors: a 1 mm shift moves {100 * out10:.0f}% of a 10 mm spherical target out of a prescription isodose that fits it exactly, and {100 * out20:.1f}% of a 20 mm one."),
        TABLE(["System", "Beams and collimation", "Localization"], [
            ["Gamma Knife", "192 Co-60 sources (201 in older models) aimed at one point; 4, 8, and 16 mm collimators", "Frame, or a mask with cone-beam CT on recent models"],
            ["Robotic linac", "6 MV without a flattening filter on a robotic arm; non-isocentric beams", "Two kV x-ray systems; the robot follows the target"],
            ["C-arm linac", "Isocentric arcs at several couch angles, through cones or an MLC with 2.5 to 5 mm leaves", "Frame or mask; cone-beam CT, stereoscopic kV, or surface imaging"],
            ["Helical unit", "6 MV on a ring; a binary MLC shapes a fan beam as the couch moves", "Megavoltage CT"]]),
        P("A frame pinned to the skull carries a localizer whose rods give every CT and MR image point frame coordinates, and then fixes the head to the couch. A mask alone does not guarantee 1 mm, so frameless treatment relies on imaging before and during treatment, with couch corrections in six degrees of freedom."),
        PHOTO("srs-sbrt-gamma-knife-setups"),
        P("The target is contoured on MR fused to the planning CT. Registration adds error, and MR is distorted: gradient nonlinearity grows with distance from the centre of the magnet, and susceptibility differences shift tissue near air and bone. For SRS the distortion is measured with a phantom and corrected."),

        H("Small-field dosimetry"),
        P("TRS-483, the IAEA–AAPM code of practice, calls a field small when any of three conditions holds on the beam axis."),
        UL("Loss of lateral charged-particle equilibrium: the field radius is shorter than the lateral range of secondary electrons, so electrons leaving the axis are not replaced. The range grows with energy and in lung.",
           "Partial source occlusion: the collimator hides part of the focal spot from the axis, so the output falls steeply, the penumbrae overlap, and the FWHM exceeds the collimator setting.",
           "A detector comparable in size to the field, which averages over the peaked profile and disturbs the electron fluence."),
        EQ("r<sub>LCPE</sub> (cm) = 8.369 × TPR<sub>20,10</sub> − 4.382",
           "small for a detector of outer width d when the FWHM is below 2 r<sub>LCPE</sub> + d",
           "equivalent square S<sub>clin</sub> = √(A × B) for FWHMs A and B,   r √π for a circle of FWHM radius r"),
        P(f"For flattened 6 MV beams (TPR<sub>20,10</sub> 0.66 to 0.68), r<sub>LCPE</sub> is {r66:.1f} to {r68:.1f} cm, so fields narrower than about {2 * r66:.1f} to {2 * r68:.1f} cm lack lateral equilibrium on the axis, before the detector width is added. A small field is sized by the FWHM of its measured profile."),
        P("A detector reading is not the dose. The field output factor Ω, the ratio of doses to water in the clinical and reference fields, is the ratio of readings times an output correction factor k, tabulated in TRS-483 by detector and field size."),
        EQ("Ω<sub>clin,msr</sub> = (M<sub>clin</sub> / M<sub>msr</sub>) × k<sub>clin,msr</sub>", "M = detector reading,   msr = machine-specific reference field: 10 × 10 cm where the machine can set it, otherwise its own, such as the 6 cm circular field of the robotic linac"),
        P("Because an unshielded diode over-reads the low-energy scatter of large fields, it is linked to the reference field through an intermediate field of a few centimetres, measured with both the diode and an ion chamber."),
        TABLE(["Detector", "Small-field response", "Limitation"], [
            ["Small ion chamber", "Under-reads: volume averaging, low-density cavity (k above 1)", "Polarity and stem effects"],
            ["Unshielded diode", "Over-reads a few percent: dense silicon (k below 1)", "Over-reads large fields"],
            ["Synthetic diamond", "Small correction (k near 1), tabulated in TRS-483 down to about 5 mm", "Dense carbon; a disc 2 mm across"],
            ["Plastic scintillator", "Close to water (k near 1)", "Cerenkov light to remove"],
            ["Radiochromic film", "Close to water; sub-millimetre resolution", "Uncertainty of a few percent"],
            ["Alanine", "Close to water", "Pellet about 5 mm across; read by EPR"]]),
        EX("Output factor from two detectors",
           STEM("A 6 MV field with an FWHM of 8 mm is measured at 10 cm depth against the 10 × 10 cm reference field with two detectors. The values of k are illustrative.",
                ["unshielded diode: M<sub>clin</sub>/M<sub>msr</sub> = 0.684, k = 0.958", "small ion chamber (0.015 cm³): M<sub>clin</sub>/M<sub>msr</sub> = 0.622, k = 1.053"],
                "Find the [[field output factor]] from each detector."),
           [f"Diode: Ω = 0.684 × 0.958 = {om_dio:.4f}", f"Chamber: Ω = 0.622 × 1.053 = {om_ich:.4f}"],
           f"{om_dio:.3f} from both. The diode reading alone is {100 * (DIO / om_dio - 1):.1f}% high and the chamber reading {100 * (1 - ICH / om_ich):.1f}% low."),

        H("Planning and plan metrics"),
        P("SRS and SBRT plans accept a hot centre for a steep fall-off outside, so the prescription isodose (as a percentage of the maximum) is lower than in conventional plans: commonly 40% to 60% on a Gamma Knife (often 50%), 70% to 90% (often 80%) on a linac with cones or arcs, higher for intensity-modulated plans, and 60% to 90% in the RTOG 0915 lung trial. A calculation grid of 2 to 3 mm or finer is advised (TG-101)."),
        EQ("RTOG CI = PIV / TV,   Paddick CI = TV<sub>PIV</sub>² / (TV × PIV),   GI = PIV<sub>50%</sub> / PIV",
           "lung SBRT: R<sub>100%</sub> = PIV / PTV,   R<sub>50%</sub> = PIV<sub>50%</sub> / PTV,   D<sub>2cm</sub> = maximum dose 2 cm from the PTV, in % of the prescription",
           "TV = target volume,   PIV = prescription isodose volume,   TV<sub>PIV</sub> = target volume inside it,   PIV<sub>50%</sub> = volume inside half the prescription dose"),
        P("The RTOG radiosurgery guidelines accept a CI of 1.0 to 2.0, with 0.9 to 1.0 or 2.0 to 2.5 a minor deviation. The gradient index measures the fall-off to half the prescription dose: lower is steeper, and Gamma Knife plans typically reach about 2.5 to 3 for small and medium targets; linac and robotic plans are usually higher. RTOG 0915 asked for R<sub>100%</sub> below 1.2 and set limits on R<sub>50%</sub> and D<sub>2cm</sub> that depend on the PTV volume."),
        EX("Conformity and gradient",
           STEM("A single brain metastasis treated with radiosurgery.", ["target volume TV = 2.10 cm³", "prescription isodose volume PIV = 2.40 cm³", "target volume inside the prescription isodose TV<sub>PIV</sub> = 2.02 cm³", "volume inside half the prescription dose PIV<sub>50%</sub> = 7.70 cm³"],
                "Find the RTOG CI, the Paddick CI, and the [[gradient index]]."),
           [f"RTOG CI = 2.40 / 2.10 = {ci_a:.3f}", f"Paddick CI = 2.02² / (2.10 × 2.40) = {TVP ** 2:.4f} / {TV * PIV:.2f} = {pad_a:.3f}", f"GI = 7.70 / 2.40 = {gi_a:.3f}"],
           f"RTOG CI {ci_a:.2f}, within 1.0 to 2.0. Paddick CI {pad_a:.2f}. GI {gi_a:.2f}: as equivalent spheres, the prescription and half-prescription surfaces are {fall_a:.1f} mm apart."),
        P("In lung the dose is calculated with heterogeneity corrections by an algorithm that transports electrons sideways: convolution–superposition, a Boltzmann solver, or Monte Carlo. TG-101 recommends algorithms that model lateral electron transport in lung; pencil-beam algorithms that scale only the path length overestimate the dose at the edge of a lung tumour."),
        P("Regimens are compared by BED. A tumour BED of at least 100 Gy (α/β = 10 Gy) was associated with better local control of early lung cancer (Onishi and colleagues), although the linear-quadratic model is less certain at these doses per fraction."),
        EX("BED of three regimens",
           STEM("Three stereotactic regimens for a tumour with α/β = 10 Gy.", ["1 × 24 Gy", "3 × 18 Gy", "5 × 11 Gy"], "Find the [[BED]] of each."),
           ["BED = n d (1 + d / (α/β))", f"1 × 24 × (1 + 24/10) = {b24:.1f} Gy", f"3 × 18 × (1 + 18/10) = {b54:.1f} Gy", f"5 × 11 × (1 + 11/10) = {b55:.1f} Gy"],
           f"{b24:.1f}, {b54:.1f}, and {b55:.1f} Gy. Three fractions of 18 Gy give the most, and the single fraction falls below 100 Gy."),

        H("Motion, QA, and end-to-end tests"),
        P("TG-76 recommends managing respiratory motion when the target moves more than 5 mm, or when management spares normal tissue. An ITV from a 4D-CT covers the whole excursion, abdominal compression shortens it, and a breath hold fixes the target at one phase. Gating switches the beam on only in a window of the breathing cycle, so delivery takes longer. Tracking moves the beam with the target; the robotic linac links external markers to periodic x-ray images of fiducials."),
        P("The Winston-Lutz test images a small ball at the laser or imaging isocentre in a small field at many gantry, couch, and collimator angles; the shadow's offset from the field centre is the distance from the beam axis to the ball. MPPG 9.a allows at most 1.0 mm for SRS and 1.5 mm for SBRT, and MPPG 9.b (2025) revises it; TG-142 asks for radiation and mechanical isocentres to coincide within 1 mm for SRS and SBRT, against 2 mm otherwise."),
        EX("Couch axis offset",
           STEM("A Winston-Lutz test at several couch angles shows that the couch rotation axis passes 1.0 mm from the radiation isocentre. A target sits at the radiation isocentre with the couch at 0°.", [], "Find how far the [[target moves]] when the couch turns to 90°."),
           ["The target turns on a circle of radius r = 1.0 mm about the couch axis", "Displacement = chord = 2 r sin(θ/2) = 2 × 1.0 × sin 45°"],
           f"{ch_a:.2f} mm, beyond the 1 mm tolerance for SRS although the axis is only 1.0 mm off. A turn of 180° would give {ch_180:.1f} mm."),
        P("An end-to-end test takes an anthropomorphic phantom with a hidden target and film or a small detector through imaging, fusion, planning, image-guided setup, and delivery. A pass shows that the whole chain puts the dose where it was planned; a failure does not locate the faulty step. A robotic linac should reach a total targeting error of about 1 mm or less for a static target in an end-to-end test (the manufacturer's specification is 0.95 mm)."),
        P("Cone and MLC QA check field size, centring on the collimator axis, leaf positions, and the interlock that identifies the cone. Per-patient QA is stricter than for conventional IMRT: the dose per fraction is high, few fractions average errors, and small fields are where beam models and detectors are least accurate. An independent calculation checks the monitor units with small-field output factors from suitable detectors."),
    ],
    cards=[
        F("SRS and SBRT", "SRS gives a small intracranial target a high dose with about 1 mm targeting accuracy, classically in one fraction and in up to five by current definitions. SBRT (SABR) brings the same methods to targets outside the skull, in one to five fractions."),
        F("Geometric accuracy in radiosurgery", f"About 1 mm: the dose falls steeply, the margin is small, and few fractions leave no averaging. A 1 mm shift moves {100 * out10:.0f}% of a 10 mm target out of an exactly fitting prescription isodose.",
          w=["Overlap of two spheres of radius R whose centres are d apart = π (4R + d)(2R − d)² / 12", f"R = 5 mm, d = 1 mm: overlap = {math.pi * 21 * 81 / 12:.1f} mm³ of {4 / 3 * math.pi * 125:.1f} mm³, so {100 * out10:.0f}% lies outside"]),
        F("Gamma Knife", "192 Co-60 sources (201 in older models) aimed at one focal point, with 4, 8, and 16 mm collimators (helmets of 4 to 18 mm on older models). A frame, or on recent models a mask with cone-beam CT."),
        F("Small-field conditions (TRS-483)", "Loss of lateral charged-particle equilibrium on the axis, partial occlusion of the source, or a detector as large as the field. Any one makes a field small."),
        F("Size of a small field", "The FWHM of the measured profile at the measurement depth, which exceeds the collimator setting once the penumbrae overlap. The equivalent square is √(A × B)."),
        F("Field output factor", "Ω = (M<sub>clin</sub> / M<sub>msr</sub>) × k: the ratio of detector readings times the output correction factor for that detector and field size (TRS-483)."),
        F("Detector response in small fields", "Diodes over-read (k below 1) and air-filled chambers under-read (k above 1). Plastic scintillators and film are close to water."),
        F("Uncorrected chamber output factor", "The reading is too low, so the planning system assigns too many monitor units and the patient is overdosed by the factor k."),
        F("Prescription isodose in radiosurgery", "Commonly 40% to 60% (often 50%) on a Gamma Knife and 70% to 90% (often 80%) on a linac with cones or arcs, higher for intensity-modulated plans. A lower isodose gives a hotter centre and a steeper fall-off."),
        F("RTOG conformity index", "PIV / TV. From 1.0 to 2.0 meets the RTOG radiosurgery guidelines; 0.9 to 1.0 or 2.0 to 2.5 is a minor deviation."),
        F("Gradient index", "PIV<sub>50%</sub> / PIV, the volume inside half the prescription dose over the prescription isodose volume. Lower is steeper; about 2.5 to 3 on a Gamma Knife for small and medium targets, usually higher on linacs."),
        F("Tumour BED for early lung cancer", "A BED of at least 100 Gy (α/β = 10 Gy) was associated with better local control."),
        F("Respiratory motion threshold (TG-76)", "Motion management is recommended when the target moves more than 5 mm, or when it spares normal tissue."),
        F("Winston-Lutz test", "A ball at the isocentre is imaged in a small field at many gantry, couch, and collimator angles. MPPG 9.a allows at most 1.0 mm for SRS and 1.5 mm for SBRT."),
        F("End-to-end test", "A phantom taken through imaging, planning, setup, and delivery. It checks the whole chain at once but does not locate an error."),
    ],
)


# ---------------------------------------------------------------- questions
q_om = 0.742 * 0.965
q_fw = min_fwhm(0.680, 0.30)
q_sq = math.sqrt(8.4 * 11.2)
q_gi = gi(5.90, 1.85)
q_bed = bed(4, 12, 10)
q_gt = 1800 / (1400 * 0.30)
q_ch = chord(0.7, 90)
q_te = math.sqrt(0.42 ** 2 + 0.38 ** 2 + 0.55 ** 2)
REG = [(8, 7.5), (1, 25), (3, 12), (5, 9)]                                  # regimens of the BED threshold question; only the first reaches 100 Gy

PROBLEMS = [
    # 1 to 3: systems and localization
    PR(STEM("A brain metastasis is treated with frameless SRS on a C-arm linac, with the head in a thermoplastic mask.", [], "What provides the targeting accuracy of about 1 mm?"),
       "Imaging before and during treatment, with couch corrections of translation and rotation",
       ["The mask alone, once it has set around the head", "Alignment of the skin marks to the room lasers", "A planning CT taken with the head in the mask"],
       "A mask restrains the head but does not by itself guarantee 1 mm, and lasers and a planning CT only set up a starting position. Cone-beam CT, stereoscopic kV images, or surface imaging locate the target before and during treatment, and the couch corrects in six degrees of freedom.", lvl="Moderate"),
    SORT("Match each stereotactic system to its design.", ["Gamma Knife", "Robotic linac", "C-arm linac with cones", "Helical ring-gantry unit"],
         [("Many Co-60 beams aimed at one focal point", 0), ("Non-isocentric beams aimed by a robotic arm, with x-ray tracking", 1), ("Isocentric non-coplanar arcs through a circular collimator", 2), ("A fan beam shaped by a binary MLC as the couch moves through the ring", 3)],
         "The Gamma Knife focuses fixed Co-60 beams, the robotic linac moves a compact linac around the patient and follows the target with two x-ray systems, the C-arm linac rotates about one isocentre at several couch angles, and the helical unit delivers a modulated fan beam while the couch moves.", lvl="Easy", mode="match", cap=1),

    # 4 to 12: small-field dosimetry
    PR(STEM("A 6 MV field is set to 5 mm with the jaws and the MLC.", [], "How does TRS-483 specify the size of this small field?"),
       "By the FWHM of the measured profile at the measurement depth", ["By the collimator setting projected to the isocentre", "By the 80% to 20% width of the penumbra", "By the light field projected on the surface"],
       "When the penumbrae overlap and the source is partly hidden, the FWHM of the profile is larger than the collimator setting, so the setting no longer describes the field. Output factors and correction factors are tabulated against the field size from the FWHM.", lvl="Easy"),
    PRN(STEM("An unshielded diode measures a 6 MV field of 10 mm FWHM and the 10 × 10 cm reference field at the same depth. The value of k is illustrative.", ["M<sub>clin</sub>/M<sub>msr</sub> = 0.742", "output correction factor k = 0.965"], "What is the [[field output factor]]?"),
        q_om, [0.742, 0.742 / 0.965, 0.742 * 0.965 ** 2], "{:.3f}",
        f"Ω = (M<sub>clin</sub>/M<sub>msr</sub>) × k = 0.742 × 0.965 = {q_om:.3f}. The diode over-reads the small field, so k is below 1 and lowers the ratio. The ratio of readings alone gives 0.742, dividing by k gives {0.742 / 0.965:.3f}, and applying k twice gives {0.742 * 0.965 ** 2:.3f}.", lvl="Moderate"),
    PRM("A 6 MV field is narrowed from 3 cm to 5 mm across. Which of these are small-field effects that lower the dose on the axis itself, and not only the reading of a detector?",
        ["Loss of lateral charged-particle equilibrium", "Partial occlusion of the source by the collimator"],
        ["Volume averaging in the detector", "Over-response of an unshielded diode", "Perturbation of the fluence by an air cavity"],
        "Electrons leave the narrow beam and are not replaced, and the collimator hides part of the focal spot from the axis; both lower the dose to water. Volume averaging, diode over-response, and cavity perturbation change what a detector reads, which is what k corrects.", lvl="Moderate"),
    PR(STEM("Profiles of a 5 mm cone are needed to find its FWHM and penumbra.", [], "Which detector suits this measurement best?"),
       "Radiochromic film", ["A Farmer-type chamber scanned across the field", "A 0.125 cm³ scanning chamber", "Alanine pellets"],
       "Film is close to water and resolves well under 1 mm, so the steep edges are not blurred. A chamber several millimetres across averages over the penumbra and widens it, and an alanine pellet about 5 mm across is as large as the field.", lvl="Moderate"),
    PR(STEM("During commissioning of the smallest SRS cone, its output factor is measured with a 0.125 cm³ chamber, and the ratio of readings is entered in the planning system without a correction.", [], "What happens to patients treated with that cone?"),
       "They are overdosed, because the reading is too low and the system assigns too many monitor units",
       ["They are underdosed, because the reading is too low and the system assigns too few monitor units", "They are underdosed, because the chamber over-reads small fields", "They receive the planned dose, because the system corrects for detector size"],
       "The chamber averages over the peaked profile and under-reads, so the output factor entered is too low. The system believes each monitor unit gives less dose and assigns more of them, so the patient receives the planned dose times k; a low output factor raises the monitor units, never lowers them. In Toulouse in 2006 and 2007, small-field data from an unsuitable detector affected 145 radiosurgery patients.", lvl="Challenging"),
    PRM(STEM("A small air-filled ion chamber measures the output of a 6 MV field 6 mm across.", [], "Which of these make its ratio of readings lower than the true ratio of doses?"),
        ["Volume averaging over the peaked profile", "Fluence perturbation by the low-density air cavity"],
        ["Over-response of dense silicon", "Cerenkov light produced in the stem", "Partial occlusion of the source"],
        "The chamber averages the dose over a volume that reaches into the falling edge, and where lateral equilibrium is missing its air cavity changes the electron fluence relative to water; both lower the reading, so k is above 1. Silicon belongs to diodes, Cerenkov light to scintillators, and source occlusion lowers the dose itself.", lvl="Challenging"),
    TYPED(STEM("A small MLC field is measured at 10 cm depth.", ["in-plane FWHM A = 8.4 mm", "cross-plane FWHM B = 11.2 mm"], "What is the [[equivalent square field size]] S<sub>clin</sub> (TRS-483)?"), q_sq, 0.01, "mm",
          f"S<sub>clin</sub> = √(A × B) = √({8.4 * 11.2:.2f} mm²) = {q_sq:.2f} mm. The arithmetic mean, {(8.4 + 11.2) / 2:.1f} mm, is slightly larger; the two agree only for a square.", lvl="Moderate"),

    # 13 to 17: planning and plan metrics
    PR(STEM("Two radiosurgery plans give the same margin dose to a small target. One is prescribed to the 50% isodose and the other to the 80% isodose.", [], "How does the 50% plan compare with the 80% plan?"),
       "Its centre is hotter and its dose falls off more steeply outside the target",
       ["Its centre is cooler and its dose falls off more steeply outside the target", "Its centre is hotter and its dose falls off less steeply outside the target", "Its dose is more uniform and falls off less steeply outside the target"],
       f"The maximum is the margin dose divided by the prescription isodose: {1 / 0.5:.2f} times the margin dose at 50% and {1 / 0.8:.2f} times at 80%. A low isodose places the prescription surface on the steepest part of the dose profile, so the fall-off outside is steeper. The hot centre is accepted because the target holds no functioning tissue.", lvl="Moderate"),
    PRN(STEM("A radiosurgery plan.", ["target volume = 1.60 cm³", "prescription isodose volume = 1.85 cm³", "volume inside half the prescription dose = 5.90 cm³"], "What is the [[gradient index]]?"),
        q_gi, [1.85 / 5.90, 5.90 / 1.60, ci_rtog(1.85, 1.60)], "{:.2f}",
        f"GI = PIV<sub>50%</sub> / PIV = 5.90 / 1.85 = {q_gi:.2f}. Dividing by the target volume gives {5.90 / 1.60:.2f}, the inverted ratio is {1.85 / 5.90:.2f}, and {ci_rtog(1.85, 1.60):.2f} is the RTOG conformity index.", lvl="Moderate"),
    PRN(STEM("An SBRT regimen.", ["4 fractions of 12 Gy", "tumour α/β = 10 Gy"], "What is the tumour [[BED]]?"),
        q_bed, [48.0, 48 * (1 + 10 / 12), bed(4, 12, 3)], "{:.1f} Gy",
        f"BED = n d (1 + d/(α/β)) = 48 × (1 + 12/10) = {q_bed:.1f} Gy, above the 100 Gy associated with better local control of early lung cancer. The physical dose is 48 Gy, inverting the ratio gives {48 * (1 + 10 / 12):.1f} Gy, and α/β = 3 Gy gives {bed(4, 12, 3):.1f} Gy.", lvl="Moderate"),

    # 18 to 22: motion, QA, and end-to-end tests
    PRN(STEM("A lung SBRT fraction is delivered with respiratory gating.", ["monitor units = 1800", "dose rate with the beam on = 1400 MU/min", "duty cycle, the fraction of each breath with the beam on = 30%"], "How long does [[delivery]] take, leaving out setup and imaging?"),
        q_gt, [1800 / 1400, 1800 * 0.30 / 1400, 1800 / (1400 * 0.70)], "{:.1f} min",
        f"The beam is on for 30% of the time, so delivery takes 1800 / (1400 × 0.30) = {q_gt:.1f} min, against {1800 / 1400:.1f} min without gating. Multiplying by the duty cycle instead of dividing gives {1800 * 0.30 / 1400:.1f} min, and dividing by the beam-off fraction gives {1800 / (1400 * 0.70):.1f} min.", lvl="Moderate"),
    PR(STEM("An end-to-end test with an anthropomorphic head phantom passes: the dose measured in the hidden target agrees with the plan in position and value.", [], "What does the result show?"),
       "The whole chain, from imaging to delivery, places the dose where it was planned",
       ["Each component, such as MR distortion or the couch, meets its own tolerance", "Every patient plan delivered on the machine will pass its own QA", "The output factors of all the cones are correct"],
       "The phantom passes through imaging, fusion, planning, setup, and delivery together, so the test checks their combined effect. Errors can cancel and one test samples one geometry, so each component and each patient plan still needs its own check.", lvl="Moderate"),
    PRN(STEM("A Winston-Lutz test at several couch angles shows that the couch rotation axis passes 0.7 mm from the radiation isocentre. A target is placed at the radiation isocentre with the couch at 0°.", [], "How far does the [[target move]] when the couch turns to 90°?"),
        q_ch, [0.70, 1.40, 0.7 * math.pi / 2], "{:.2f} mm",
        f"The target turns on a circle of radius 0.7 mm about the couch axis, so it moves along the chord 2 r sin(θ/2) = 2 × 0.7 × sin 45° = {q_ch:.2f} mm. The arc length r θ gives {0.7 * math.pi / 2:.2f} mm, the radius alone 0.70 mm, and 1.40 mm is the shift after a turn of 180°.", lvl="Challenging"),
    TYPED(STEM("An end-to-end test of a robotic linac uses orthogonal films in a head phantom. The centre of the delivered dose is offset from the centre of the hidden target.", ["left–right = 0.42 mm", "anterior–posterior = 0.38 mm", "superior–inferior = 0.55 mm"], "What is the [[total targeting error]]?"), q_te, 0.015, "mm",
          f"The total targeting error is the length of the offset vector: √(0.42² + 0.38² + 0.55²) = {q_te:.2f} mm, within the 0.95 mm specification for a static target. Adding the components gives {0.42 + 0.38 + 0.55:.2f} mm, which overstates it.", lvl="Challenging"),
]

INLINE = {0: [1, 2], 1: [3, 4, 5], 2: [10, 11], 3: [13, 14]}

TERMS = ['stereotactic radiosurgery', 'stereotactic body radiotherapy', 'lateral charged-particle equilibrium', 'source occlusion', 'output correction factor', 'gradient index', 'Winston-Lutz test', 'end-to-end test']

TAKE = [
    ["SRS and SBRT give one to five large fractions; SRS aims for about 1 mm targeting accuracy.",
     "Frameless treatment depends on image guidance, not on the mask. MR distortion and image fusion add to the error."],
    ["A field is small when lateral equilibrium is lost, the source is partly hidden, or the detector is as large as the field.",
     "Ω = (M<sub>clin</sub> / M<sub>msr</sub>) × k. Diodes over-read and air-filled chambers under-read; an uncorrected chamber reading overdoses the patient."],
    ["RTOG CI = PIV / TV, Paddick CI = TV<sub>PIV</sub>² / (TV × PIV), GI = PIV<sub>50%</sub> / PIV.",
     "Lung SBRT dose is calculated with heterogeneity corrections by an algorithm that transports electrons sideways."],
    ["Winston-Lutz: the beam axis passes at most 1.0 mm from the ball for SRS (MPPG 9.a).",
     "An end-to-end test checks the whole chain at once but does not locate an error."],
]
