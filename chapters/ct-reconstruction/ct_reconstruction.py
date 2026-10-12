from blocks import *
import math, calc, gal
PK = {k: v['hu'] for k, v in gal.PICKS.items()}
sg = lambda v: f"{v}".replace("-", "−")                                   # a signed number with a true minus sign

hu = lambda mu, muw: 1000 * (mu - muw) / muw                       # Hounsfield units from linear attenuation coefficients
mu_of = lambda h, muw: muw * (1 + h / 1000)                       # the attenuation coefficient for a given HU
MUW = 0.19                                                         # illustrative effective mu of water, per cm
hu_a, hu_b = hu(1.1 * MUW, MUW), hu(0.75 * MUW, MUW)
mu_bone = mu_of(1000, MUW); mu_lung = mu_of(-500, MUW)
hu_t = hu(0.2166, MUW)

TOPIC = dict(
    id="ct-reconstruction", domain=4, sub="IV.A", title="CT reconstruction and Hounsfield units",
    ref=dict(aapm="TG-66", khan="", ford="19"),
    guide=[
        H("Filtered backprojection"),
        P("In computed tomography an x-ray source and a detector rotate around the patient. At each angle the detector records a profile of photon fluences. Reconstruction works by backprojecting each profile through the reconstruction space, which smears the signal along the path of the beam. A single backprojection shows that something dense lies along that path, but not where along it. Rotating the source and detector gives many angles, and [[1|when the backprojections from all of them are added they build up an image of the object.]]"),
        P("The algorithm is properly called filtered backprojection. [[1|A frequency filter has to be applied to the profiles before they are backprojected for the reconstruction to be mathematically exact.]] Without the filter, the sum of the backprojections is blurred."),

        H("Hounsfield units"),
        P("CT measures the transmission through the patient, I = I₀e<sup>−μx</sup>. The incident intensity, the transmitted intensity, and the path length are known, so the linear attenuation coefficient μ can be found for each pixel. A CT image shows μ in every pixel, with small values dark and large values bright. The unit is the Hounsfield unit, which expresses μ relative to water. [[1|A material whose μ is 10% above that of water reads +100 HU.]]"),
        EQ("[[1|HU = 1000 × (μ − μ<sub>water</sub>) / μ<sub>water</sub>]]", "[[1|water = 0 HU,   air = −1000 HU]],   bone = +500 to +1000 HU"),
        P("Higher-density materials have larger HU. The composition matters too, because μ depends on the atomic number through the photoelectric effect. The HU also depends on the x-ray spectrum: a softer beam has more low-energy photons, where μ is larger and the contrast between materials of different Z is greater. The HU of a material therefore depends on its density, its composition, and the spectrum of the beam."),
        EX("Hounsfield units from μ", STEM("A material is scanned with an effective water coefficient of μ<sub>water</sub> = 0.19 cm<sup>−1</sup>.", ["material 1: μ is 10% larger than water", "material 2: μ is 25% smaller than water"], "Find the [[HU]] of each."), ["HU = 1000 × (μ − μ<sub>water</sub>) / μ<sub>water</sub> = 1000 × (μ/μ<sub>water</sub> − 1)", "Material 1: 1000 × (1.10 − 1)", "Material 2: 1000 × (0.75 − 1)"], f"{hu_a:+.0f} HU and {hu_b:+.0f} HU. The HU is a fractional difference in μ in parts per thousand."),

        P(f"In a real CT slice of a head-and-neck patient the airway reads {sg(PK['air'])} HU, the fat {sg(PK['fat'])} HU, the muscle {sg(PK['muscle'])} HU, and the bone {sg(PK['bone'])} HU. The window and the level choose which range of HU is spread over the grey scale: a narrow window of 400 HU centred on 40 HU shows the soft tissue, and a wide window shows the bone but flattens the soft tissue."),
        AVF("ct-hu-explorer"),
        H("From HU to density"),
        P("For radiation therapy, the HU must be converted to a mass density, which the dose calculation needs. [[1|The relationship between HU and density is not linear, and it differs between scanners and tube voltages, so a calibration has to be established for each scanner.]] It is usually measured by scanning a phantom that has inserts of known density and building a table of HU against density. The same table is used for every patient scanned with the same technique. [[1|Any curve printed in this guide is illustrative, not a calibration to copy.]]"),
        EX("The attenuation coefficient from an HU", STEM("A pixel has a value of +1000 HU, and another has −500 HU. μ<sub>water</sub> = 0.19 cm<sup>−1</sup>.", [], "Find the [[attenuation coefficient]] of each."), ["μ = μ<sub>water</sub> × (1 + HU/1000)", "+1000 HU: 0.19 × 2", "−500 HU: 0.19 × 0.5"], f"{mu_bone:.2f} cm<sup>−1</sup> and {mu_lung:.3f} cm<sup>−1</sup>. A pixel at +1000 HU attenuates twice as strongly as water, and one at −500 HU attenuates half as strongly."),
    ],
    cards=[
        F("CT reconstruction", "A source and detector rotate around the patient. The profile of fluence at each angle is backprojected through the reconstruction space."),
        F("Backprojection from one angle", "It smears the signal along the beam path, showing that a dense object lies along it but not where."),
        F("Filtered backprojection", "A frequency filter is applied to the profiles before backprojection, which makes the reconstruction mathematically exact."),
        F("CT pixel value", "The linear attenuation coefficient μ of that pixel, from I = I₀e<sup>−μx</sup>."),
        F("Hounsfield unit", "HU = 1000 × (μ − μ<sub>water</sub>) / μ<sub>water</sub>: the attenuation coefficient relative to water."),
        F("Key HU values", "Water is 0 HU, air is −1000 HU, and bone is about +500 to +1000 HU."),
        F("Dependence of the HU", "The density, the composition (the atomic number), and the x-ray spectrum of the beam."),
        F("HU and the spectrum", "A softer beam has more low-energy photons, where μ is larger and the Z-dependence is greater, so the HU of bone changes with the tube voltage."),
        F("HU to density conversion", "Needed for dose calculation. The relationship is non-linear and scanner-specific, so a calibration is established for each scanner."),
        F("Making the calibration", "Scan a phantom with inserts of known density and tabulate the HU against the density."),
    ],
)

PROBLEMS = [
    PR("The Hounsfield unit of water is:", "0", ["+1000", "−1000", "+100"],
       "The HU is defined relative to water, so water is 0 HU. Air is −1000 HU.", lvl="Easy"),
    PR("The Hounsfield unit of air is:", "−1000", ["0", "−100", "+1000"],
       "Air has a linear attenuation coefficient of nearly zero, so HU = 1000 × (0 − μ<sub>water</sub>) / μ<sub>water</sub> = −1000.", lvl="Easy"),
    PR("The value in each pixel of a CT image represents:", "the linear attenuation coefficient of that pixel", ["the mass density of that pixel", "the number of photons in that pixel", "the atomic number of that pixel"],
       "CT derives μ from the transmission I = I₀e<sup>−μx</sup>. The HU expresses it relative to water.", lvl="Easy"),
    PRN(STEM("A material has a linear attenuation coefficient 10% larger than that of water.", [], "What is its [[Hounsfield unit]]?"), hu_a, [10.0, 1000 * 1.1, -100.0], "{:.0f} HU",
        f"HU = 1000 × (1.10 − 1) = {hu_a:.0f}. Multiplying 1000 by 1.10 gives 1100.", lvl="Moderate"),
    PRN(STEM("A pixel has −500 HU. The linear attenuation coefficient of water is 0.19 cm<sup>−1</sup>.", [], "What is the [[attenuation coefficient]] of the pixel?"), mu_lung, [0.19 * 1.5, 0.19 * 500 / 1000 * 2, 0.5], "{:.3f} cm<sup>−1</sup>",
        f"μ = μ<sub>water</sub> × (1 + HU/1000) = 0.19 × 0.5 = {mu_lung:.3f} cm<sup>−1</sup>.", lvl="Moderate"),
    PR("A single backprojection from one angle is not enough to reconstruct an object because it:", "shows that the object lies along the beam path, but not where along it", ["shows only the edge of the object", "measures the density but not the position", "measures only the atomic number"],
       "The signal is smeared along the whole path. Other angles localize the object where the smeared bands cross.", lvl="Moderate"),
    PR("The HU of dense bone is larger at 80 kVp than at 140 kVp because at 80 kVp:", "more of the photons have low energy, where the photoelectric effect raises μ of bone far more than μ of water", ["the beam has higher energy", "the detector is more sensitive", "water attenuates more than bone"],
       "A softer beam raises the ratio of μ of bone to μ of water, so the HU of bone rises. The HU depends on the spectrum.", lvl="Moderate"),
    PR("The relationship between HU and mass density used in treatment planning is:", "non-linear and scanner-specific, so a calibration is established for each scanner", ["linear, with the same slope for every scanner", "the same for every tube voltage", "not needed, because the HU is a density"],
       "The HU depends on the composition and the spectrum as well as on the density, so each scanner and technique needs its own calibration.", lvl="Moderate"),
    PR("Filtered backprojection requires a frequency filter because:", "without it the sum of the backprojections is blurred, and it is exact only with the filter", ["the filter removes the noise", "the filter changes the HU of water", "the detector measures frequencies"],
       "Backprojecting the unfiltered profiles smears each point over the whole path. The filter corrects this and makes the reconstruction mathematically exact.", lvl="Challenging"),
]

TERMS = ['filtered backprojection', 'Hounsfield unit', 'calibration', 'spectrum']

TAKE = [
    [('A CT image is built by adding the backprojections from many angles. A filter applied before backprojection makes the reconstruction exact.', 'backprojection')],
    [('HU = 1000 × (μ − μ<sub>water</sub>) / μ<sub>water</sub>. Water is 0 HU and air is −1000 HU. A material with 10% more μ than water is +100 HU.', 'hu-scale')],
    [('HU is converted to density with a non-linear calibration made for each scanner. The values in the curve here are illustrative.', 'ct-density')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
PROBLEMS += [
    PRM("Which of the following does the HU of a tissue depend on?", ["Its density", "Its composition, through the atomic number", "The x-ray spectrum of the beam"], ["The tube current", "The scan time", "The slice position on the table"],
        "The HU is the attenuation coefficient relative to water. That depends on the density, on the composition, and on the energies of the photons. The current and the time change only the noise.", lvl="Moderate"),
    SORT("Which Hounsfield-unit range does each material fall in?", ["About −1000 HU", "About 0 HU", "About +500 to +1000 HU"],
         [("Air", 0), ("A gas bubble in the bowel", 0), ("Water", 1), ("Distilled water in a phantom", 1), ("Cortical bone", 2), ("Dense bone", 2)],
         "Air is −1000 HU by definition and water is 0 HU. Bone attenuates more than water because of its density and its higher atomic number, giving about +500 to +1000 HU.", lvl="Moderate"),
]
INLINE = {0: [6, 9], 1: [1, 4, 11], 2: [8, 7]}
