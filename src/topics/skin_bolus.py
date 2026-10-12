from blocks import *
import math, calc
import beamdata as bd

p3, p4 = round(bd.pdd_model(3, 10), 1), round(bd.pdd_model(4, 10), 1)       # illustrative 6 MV, 10 x 10 cm, SSD 100 cm
dose_b = 200 * p4 / p3                                                       # dose at the target with 1 cm bolus and unchanged MU
mu_up = (p3 / p4 - 1) * 100                                                  # percent more MU to restore the dose
skin10, skin40 = 0.30 * 200, 0.60 * 200                                      # skin dose, cGy, for a 200 cGy d_max dose
couch = 200 * 0.98
# schematic build-up curve with a 30% dose at the skin and its maximum at d_max = 1.5 cm
def _curve(s=0.30, dmax=bd.DMAX, p10=67.0):
    mu = math.log(100 / p10) / (10 - dmax); lo, hi = 0.3, 30.0
    for _ in range(60):
        k = (lo + hi) / 2
        if math.log((1 - s) * (k + mu) / mu) / k > dmax: lo = k
        else: hi = k
    N = 1 - (1 - s) * math.exp(-k * dmax); return lambda d: 100 * math.exp(-mu * (d - dmax)) * (1 - (1 - s) * math.exp(-k * d)) / N
buildup = _curve()

TOPIC = dict(
    id="skin-bolus", domain=3, sub="III.A", title="Skin dose, devices, and bolus",
    ref=dict(aapm="", khan="9, 13", ford="10"),
    guide=[
        H("Skin dose"),
        P("The skin cells most at risk lie in the basal layer, 0.05 to 0.4 mm below the surface. Physicists commonly use 0.1 mm as the reference depth, and the ICRU recommends 0.07 mm for the skin dose. For a 6 MV beam the dose at these depths is about 20% to 40% of the d<sub>max</sub> dose. This is skin sparing: the build-up of secondary electrons keeps the surface dose low. It is not zero, because electrons produced in the head of the linac, in the flattening filter and the collimators, and in the air reach the skin."),
        P("The skin dose depends on field size, energy, devices in the beam, and the angle of the beam. A larger field sends more electrons from the head to the patient, and the skin dose of a 40 × 40 cm field is about twice that of a 10 × 10 cm field. A higher energy lowers the dose in the first centimetre; the dose at the skin falls only slightly. A beam that meets the skin at a glancing angle gives a higher skin dose than one perpendicular to it."),
        TABLE(["Factor", "Effect on the skin dose"], [["Larger field", "Higher: about double from 10 × 10 to 40 × 40 cm"], ["Higher energy", "Lower in the first centimetre; small change at the skin itself"], ["Device in the beam", "Higher"], ["Beam at a glancing angle", "Higher"]]),
        EX("Skin dose and field size", STEM("A 6 MV beam.", ["dose at d<sub>max</sub> = 200 cGy", "skin dose = 30% of the d<sub>max</sub> dose for a 10 × 10 cm field", "a 40 × 40 cm field doubles the skin dose"], "Find the [[skin dose]] for each field."),
           ["10 × 10 cm: 0.30 × 200 cGy = 60 cGy", "40 × 40 cm: 2 × 60 cGy = 120 cGy"], f"{skin10:.0f} cGy for 10 × 10 cm and {skin40:.0f} cGy for 40 × 40 cm."),

        H("Devices in the beam"),
        P("Anything between the source and the skin can add electrons that reach it. When a beam passes through the treatment couch, two things happen: the beam is attenuated, typically by about 2% at depth, and the skin dose rises, in some 6 MV measurements from about 10% to about 60% of the d<sub>max</sub> dose. The size of the effect depends on the couch and the field, and it is smaller at 18 MV. AAPM Task Group 176 reports the effects of couches and immobilization devices."),
        P("A vacuum-formed bag raises the skin dose by about 10% to 50% for 6 MV, depending on field size and bag thickness. A thermoplastic mask raises the skin dose even though it has holes, and a mask stretched thinner raises it less. A plastic block tray raises it more the closer the tray is to the patient. These increases are usually unwanted, so a plan that treats through such a device has to include it in the calculation."),
        EX("Couch attenuation", STEM("A posterior field.", ["dose at depth without the couch = 200 cGy", "attenuation by the couch = 2%"], "Find the [[dose at depth]] with the couch in the beam."),
           ["Dose = 200 cGy × (1 − 0.02)"], f"{couch:.0f} cGy. A calculation that ignores the couch overestimates the dose at depth by about 2%."),

        H("Bolus"),
        P("Bolus is material placed on the skin to raise the skin or superficial dose, for example when the target includes a scar or the skin itself. Common materials are gel sheets such as Superflab, beeswax, and paraffin, and 3D-printed pieces shaped to the patient. Most bolus is tissue-equivalent, and metal mesh is sometimes used."),
        P("A bolus of thickness t moves the build-up region toward the skin. For a tissue-equivalent bolus in full contact, the dose at depth d below the skin is the dose at depth t + d in the beam. A bolus equal to d<sub>max</sub>, about 1.5 cm for 6 MV, puts the maximum dose at the skin. Bolus also attenuates the beam, so a plan whose monitor units were set without it delivers less dose at the target. An air gap between the bolus and the skin reduces its effect."),
        EQ("Dose at depth d below the skin with bolus of thickness t = PDD(t + d)"),
        EX("Dose at the target with bolus", STEM("A 6 MV, 10 × 10 cm field at SSD 100 cm.", ["prescription = 200 cGy at 3 cm below the skin, MU set without bolus", f"PDD(3 cm) = {p3}%,   PDD(4 cm) = {p4}%", "1.0 cm bolus is added and the MU are unchanged"], "Find the [[dose at the target]]."),
           ["The target is now at depth 1.0 + 3.0 = 4.0 cm in the beam", f"Dose = 200 cGy × PDD(4 cm) / PDD(3 cm) = 200 × {p4} / {p3}"], f"{dose_b:.1f} cGy, about {100 * (1 - dose_b / 200):.1f}% low."),
        EX("Restoring the dose", STEM("A 6 MV, 10 × 10 cm field at SSD 100 cm, with 1.0 cm of bolus added to a plan that prescribes 200 cGy at 3 cm below the skin.", [f"PDD(3 cm) = {p3}%,   PDD(4 cm) = {p4}%"], "By what [[percentage]] must the MU increase to restore 200 cGy at the target?"),
           [f"MU factor = PDD(3) / PDD(4) = {p3} / {p4}"], f"{mu_up:.1f}% more MU."),
    ],
    cards=[
        C("Which skin layer matters most in radiotherapy, and how deep is it?", "The basal layer, 0.05 to 0.4 mm below the surface. The reference depth is 0.1 mm, and the ICRU recommends 0.07 mm for the skin dose."),
        C("What is the dose at the skin for a 6 MV beam, as a fraction of the d<sub>max</sub> dose?", "About 20% to 40%. This is skin sparing."),
        C("Why is the skin dose not zero in a megavoltage beam?", "Electrons produced in the head of the linac (flattening filter, collimators) and in the air reach the skin."),
        C("How does the skin dose change with field size?", "It rises. A 40 × 40 cm field gives about twice the skin dose of a 10 × 10 cm field, because more electrons from the head reach the patient."),
        C("How does beam energy affect the skin dose?", "A higher energy lowers the dose in the first centimetre; the dose at the skin falls only slightly."),
        C("How does the beam angle affect the skin dose?", "A glancing angle of incidence gives a higher skin dose than perpendicular incidence."),
        C("What are the two effects of the couch on a beam passing through it?", "About 2% attenuation at depth, and a higher skin dose."),
        C("Name devices in the beam that raise the skin dose.", "The couch, vacuum immobilization bags, thermoplastic masks, and plastic block trays."),
        C("How does the position of a block tray affect the skin dose?", "The closer the tray is to the patient, the higher the skin dose."),
        C("What is bolus, and when is it used?", "Material placed on the skin to raise the skin dose, used when the target includes the skin or a scar."),
        C("What dose does a bolus of thickness t give at depth d below the skin?", "The dose at depth t + d in the beam without bolus."),
        C("What bolus thickness puts d<sub>max</sub> at the skin for 6 MV?", "About 1.5 cm, equal to d<sub>max</sub>."),
        C("What happens to the MU needed when bolus is added over a deep target?", "They increase, because bolus attenuates the beam. The dose at the target falls if the MU are not changed."),
        C("What does an air gap under bolus do?", "It reduces the bolus effect: the skin dose is lower than for full contact."),
    ],
)

PROBLEMS = [
    PR("The depth that the ICRU recommends for the skin dose is:", "0.07 mm", ["0.7 mm", "7 mm", "1.5 cm"],
       "The basal layer lies 0.05 to 0.4 mm deep. Physicists commonly use 0.1 mm, and the ICRU recommends 0.07 mm.", lvl="Easy"),
    PR("Compared with a 10 × 10 cm field, the skin dose from a 40 × 40 cm field in a 6 MV beam is about:", "twice as large", ["half as large", "the same", "ten times as large"],
       "More electrons from the head of the linac reach the skin as the field grows.", lvl="Easy"),
    PR("In a megavoltage photon beam, the dose at the skin is delivered mainly by:", "electrons produced in the head of the linac, in the air, and in the patient", ["photons absorbed directly at the surface", "neutrons from the target", "characteristic x-rays from the skin"],
       "Photons set electrons in motion. The surface dose is low because of build-up, and what is present comes from electrons produced upstream.", lvl="Easy"),
    PR("A posterior field passes through the treatment couch. Compared with a calculation that ignores the couch, the real dose is:", "about 2% lower at depth and higher at the skin", ["higher at depth and lower at the skin", "about 2% higher at depth and at the skin", "unchanged at depth and at the skin"],
       "The couch attenuates the beam by about 2% and adds electrons that increase the skin dose.", lvl="Moderate"),
    PRN(STEM("A 6 MV, 10 × 10 cm field at SSD 100 cm.", ["prescription = 200 cGy at 3 cm below the skin, MU set without bolus", f"PDD(3 cm) = {p3}%,   PDD(4 cm) = {p4}%", "1.0 cm bolus is added and the MU are unchanged"], "What [[dose]] does the target receive?"), dose_b, [200.0, 200 * p3 / p4, 200 * p4 / 100], "{:.1f} cGy",
        f"With 1.0 cm of bolus the target is at depth 4.0 cm in the beam. Dose = 200 × {p4} / {p3} = {dose_b:.1f} cGy. Leaving the MU unchanged does not keep the dose at 200 cGy.", lvl="Moderate"),
    PR("What bolus thickness places d<sub>max</sub> of a 6 MV beam at the skin surface?", "About 1.5 cm", ["About 0.5 mm", "About 5 mm", "About 3 cm"],
       "The maximum dose is at depth d<sub>max</sub> = 1.5 cm in the beam. A tissue-equivalent bolus of that thickness moves it to the skin.", lvl="Moderate"),
    PR("Bolus is placed on a patient, but a thin air gap remains between the bolus and the skin. Compared with full contact, the skin dose is:", "lower, because the gap reduces the bolus effect", ["higher, because of added scatter", "the same", "zero"],
       "The build-up region is moved only partly toward the skin when the bolus is not in contact.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 8], 1: [4], 2: [6]}

TERMS = ['basal layer', 'skin sparing', 'bolus']

TAKE = [
    [('The dose at the skin is about 20%–40% of the d<sub>max</sub> dose for 6 MV. It rises with field size (about double from 10 × 10 to 40 × 40 cm) and falls only slightly with energy.', 'skin-dose')],
    [('The couch, immobilization devices, and trays add electrons and raise the skin dose. The couch also attenuates the beam by about 2%.', 'device-skin')],
    [('Bolus of thickness t shifts the build-up curve toward the skin. The dose at depth d below the skin is the PDD at depth t + d.', 'bolus-shift')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
PROBLEMS += [
    SORT("Does each change raise or lower the skin dose of a 6 MV beam?", ["Raises it", "Lowers it"],
         [("Larger field size", 0), ("Couch in the beam path", 0), ("Vacuum immobilization bag", 0), ("Mask stretched thinner", 1), ("Block tray moved closer to the patient", 0), ("Block tray moved farther from the patient", 1), ("Bolus on the skin", 0), ("Smaller field size", 1)],
         "Anything that adds electrons or removes build-up raises the skin dose: larger fields, devices in the beam, trays close to the patient, and bolus. A thinner mask, a tray farther away, and a smaller field lower it.", lvl="Moderate"),
]
