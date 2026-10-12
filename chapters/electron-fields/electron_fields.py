from blocks import *
import math, calc

w8 = lambda z: 5 + 1.0 * z                          # schematic penumbra widths (mm) against depth (cm)
w18 = lambda z: 2.5 + 2.0 * z
z_cross = 2.5                                       # depth where the two schematic curves meet
hot_ep = 200 * 1.30                                 # photon-electron junction with no gap, 30% hot spot
hot_ee = 150 * 1.10                                 # electron-electron junction, 10% hot spot

TOPIC = dict(
    id="electron-fields", domain=3, sub="III.B", title="Electron fields, obliquity, and heterogeneities",
    ref=dict(aapm="TG-25", khan="14", ford="15"),
    guide=[
        H("Penumbra and collimation"),
        P("The penumbra of an electron beam depends on energy and depth. Near the surface, the penumbra of an 18 MeV beam is smaller than that of an 8 MeV beam, because electron scattering is more forward-directed at higher energy. As the depth increases, the penumbra widens, especially at higher energy: the high isodose lines constrict toward the center of the field while the low isodose lines bulge outward."),
        P("An electron field is defined by an applicator, or cone, and a cutout. Typical applicators are 6, 10, 15, 20, and 25 cm square, and the cutout is a shaped piece of Cerrobend at the end of the applicator. In the usual setup the patient is at SSD 100 cm, the end of the cone is 95 cm from the source, and a 5 cm air gap remains between the cone and the skin. The cutout is drawn about 1 cm wider on each side than the intended treatment area, to allow for the penumbra. The margin needed depends on the energy and the depth of the target."),
        PHOTO("electron-fields-cutout-insert"),
        P("A patient can be treated at an extended SSD of 105 or 110 cm, for example to keep the cone clear of the shoulder. Three things change. The penumbra is larger, with the high-dose lines pinching in more and the low-dose lines bulging out. The output falls, and an inverse-square correction from a virtual source is needed. The light field no longer follows the edge of the radiation field."),
        EX("Cutout size", STEM("A target.", ["width of the treatment area = 6 cm", "margin for the penumbra = 1 cm on each side"], "Find the [[cutout width]]."), ["Width = 6 + 1 + 1"], "8 cm."),

        H("Field matching"),
        P("Two fields that abut produce hot and low-dose regions. When an electron field meets a photon field edge to edge, there is a hot spot on the photon side, near the depth of maximum dose of the electron beam. In one example of a 6 MeV electron field and a 6 MV photon field the hot spot was about 30%. A gap between the fields reduces the hot spot, but a larger gap leaves a low-dose region at the surface. Feathering, which means moving the junction by a small amount each day, spreads the hot or low-dose region over a larger volume."),
        P("Two electron fields matched together also have a hot spot where they abut, about 10% for two 6 MeV fields."),
        EX("Hot spot at a junction", STEM("A photon field and an electron field abut with no gap.", ["prescription = 200 cGy", "hot spot = 30%"], "Find the [[dose in the hot spot]]."), ["Dose = 200 cGy × 1.30"], f"{hot_ep:.0f} cGy."),

        H("Obliquity, surfaces, and inhomogeneities"),
        P("When an electron beam meets the skin at an angle, the isodose lines are no longer symmetric. The dose is higher on the side where the angle is sharper, and the depth of maximum dose moves closer to the surface. A curved or sloping surface does the same near the field edge, and the effect is larger at higher energy. A tissue-equivalent bolus evens out an irregular surface. It shortens the range in the patient by its thickness and raises the skin dose."),
        P("Inhomogeneities have a strong effect on electron beams. Under a tissue prominence, such as the nose, the dose is shifted toward the source, and the regions on either side receive more dose because electrons scatter out of the prominence. The hot spot is larger at higher energy. Under a tissue defect, the isodose lines move away from the source, and electrons scattered from the sides create hot spots immediately inside the edges of the defect."),
        P("Internal shields, such as an eye shield, are made of a high-Z metal. A common design is a 3 mm tungsten shield covered by a 1 mm aluminium cap, which is adequate up to 8 MeV. The low-Z material on the beam side absorbs electrons backscattered from the tungsten, which protects the tissue in front of it."),

        H("Bolus for electron beams"),
        P("Bolus, a tissue-equivalent material laid on the skin, has three uses in electron therapy. It raises the dose at the surface, because the build-up of the beam then takes place in the bolus and the region of high dose moves toward the skin. It smooths an irregular surface, so that the dose under it is more uniform. And it shortens the range in the patient, because the electrons lose energy in the bolus first. The bolus acts as extra tissue, so the depth of any dose level below the skin is its depth in a bare beam minus the thickness of the bolus. The SSD is usually set to the upper surface of the bolus, which is treated as part of the patient."),
        EX("Range with bolus", STEM("A 9 MeV electron beam treats a lesion whose deep edge is 2.4 cm below the skin. A 1.0 cm sheet of tissue-equivalent bolus lies on the skin. Take R<sub>90</sub> = E / 3.3 cm for a bare beam.", [], "Find the [[depth of the 90% line below the skin]], and say whether it covers the lesion."),
           [f"Bare beam: R<sub>90</sub> = 9 / 3.3 = {9 / 3.3:.2f} cm", "The bolus uses 1.0 cm of that range"], f"{9 / 3.3 - 1.0:.2f} cm below the skin, so the deep edge at 2.4 cm is not covered. A 12 MeV beam gives 12 / 3.3 − 1.0 = {12 / 3.3 - 1.0:.2f} cm and covers it."),
    ],
    cards=[
        F("Electron penumbra and energy", "Near the surface the penumbra is smaller at higher energy, because scattering is more forward-directed. At depth it widens, more so at higher energy."),
        F("Isodose lines at depth in an electron beam", "The high isodose lines constrict toward the center of the field and the low isodose lines bulge outward, more so at higher energy."),
        F("Cutout margin", "Drawn about 1 cm wider on each side than the treatment area, to allow for the penumbra."),
        F("Extended SSD in electron therapy", "Larger penumbra, lower output (inverse square from a virtual source), and a light field that no longer follows the radiation field edge."),
        F("Electron–photon junction with no gap", "A hot spot on the photon side near the electron d<sub>max</sub>, about 30% in one example (6 MeV with 6 MV)."),
        F("Gap at an electron–photon junction", "A gap reduces the hot spot, but a larger gap leaves a low-dose region at the surface."),
        F("Feathering", "Moving the junction a small amount each day, to spread the hot or low-dose region."),
        F("Electron–electron junction", "A hot spot of about 10% where two 6 MeV fields abut."),
        F("Oblique electron incidence", "The isodose lines become asymmetric, with higher dose where the angle is sharper, and the dose maximum moves closer to the surface."),
        F("Tissue prominence and tissue defect", "Under a prominence, the dose shifts toward the source, with hot spots beside it. Under a defect, the dose shifts away from the source, with hot spots immediately inside its edges."),
        F("Internal eye shield", "Tungsten (3 mm) with a 1 mm aluminium cap, adequate up to 8 MeV. The low-Z cap on the beam side absorbs backscattered electrons."),
    ],
)

PROBLEMS = [
    PR("At a shallow depth, the penumbra of an 18 MeV electron beam compared with an 8 MeV beam is:", "smaller, because the scattering is more forward-directed", ["larger, because the electrons scatter more", "the same", "larger, because the range is longer"],
       "At higher energy the electrons are scattered less sideways near the surface. At greater depth the order reverses and the 18 MeV penumbra is wider.", lvl="Easy"),
    PR("Which statement about treating electron fields at an extended SSD is correct?", "The penumbra becomes larger and the output falls", ["The penumbra becomes smaller and the output rises", "The light field follows the radiation field more closely", "The output does not depend on the SSD"],
       "The inverse-square correction from a virtual source lowers the output, and the larger distance widens the penumbra.", lvl="Easy"),
    PRN(STEM("An electron field.", ["width of the treatment area = 7 cm", "margin = 1 cm on each side"], "What [[cutout width]] is drawn?"), 9.0, [7.0, 8.0, 10.0], "{:.0f} cm",
        "Width = 7 + 1 + 1 = 9 cm. The margin is added on both sides.", lvl="Moderate"),
    PR("An electron beam meets the skin at an oblique angle. Compared with perpendicular incidence, the depth of maximum dose is:", "closer to the surface", ["deeper", "unchanged", "at the exit surface"],
       "The isodose lines become asymmetric and the dose maximum moves toward the surface, with higher dose where the angle is sharper.", lvl="Moderate"),
    PR("An electron field abuts a photon field with no gap. The hot spot appears:", "on the photon side, near the depth of maximum dose of the electron beam", ["on the electron side, at the surface", "at the exit surface of the photon beam", "only at the surface of the photon side"],
       "Electrons scatter into the photon side near their dose maximum, where the photon beam is also delivering dose.", lvl="Moderate"),
    PR("Increasing the gap between an abutting electron field and photon field:", "reduces the hot spot but eventually leaves a low-dose region at the surface", ["removes both the hot spot and any low-dose region", "increases the hot spot", "does not change the dose at the junction"],
       "A small gap helps, and a large gap leaves the junction underdosed. Feathering spreads the problem over a larger volume.", lvl="Moderate"),
    PRM("Which occur in an electron beam under a tissue prominence, such as the nose?", ["The dose under the prominence is shifted toward the source", "The regions on either side receive more dose from scattered electrons"], ["The isodose lines under it move away from the source", "The hot spots are smaller at higher energy"],
        "The prominence shortens the path to the tissue under it, so the dose shifts toward the source. Electrons scattered out of the prominence add dose beside it, more at higher energy.", lvl="Moderate"),
    PR("An internal eye shield of tungsten has an aluminium cap on the side facing the beam. The cap is there to:", "absorb electrons backscattered from the tungsten, protecting the tissue in front of it", ["increase the attenuation of the beam", "raise the dose behind the shield", "make the shield lighter"],
       "A high-Z metal backscatters electrons strongly. A low-Z layer in front of it absorbs them, so the tissue in front of the shield is not overdosed.", lvl="Challenging"),
    PR("Under a tissue defect in an electron beam, the isodose lines are:", "shifted away from the source, with hot spots immediately inside the edges of the defect", ["shifted toward the source, with a line of low dose at the edges", "unchanged", "shifted toward the source, with hot spots at the center"],
       "The path to the tissue under the defect is longer, so the dose is shifted away from the source. Electrons scattered from the sides add dose immediately inside the edges.", lvl="Challenging"),
    PR("Two 6 MeV electron fields are matched with no gap. Compared with the dose elsewhere in the fields, the dose at the junction is:", "about 10% higher", ["about 30% higher", "about 10% lower", "the same"],
       "Electron–electron junctions have a smaller hot spot than electron–photon junctions, about 10% for two 6 MeV fields.", lvl="Challenging"),
]

INLINE = {0: [1, 3], 1: [5, 6], 2: [4, 7]}

TERMS = ['cutout', 'feathering', 'virtual source']

TAKE = [
    [('At shallow depth a higher energy gives a smaller penumbra, but at depth it becomes much wider and the high isodose lines constrict toward the center. Extended SSD widens the penumbra and lowers the output.', 'electron-penumbra')],
    [('An electron–photon junction with no gap has a hot spot of about 30% on the photon side. A gap lowers it but leaves a low-dose region at the surface, and feathering spreads the effect.', 'electron-matching')],
    [('Oblique incidence moves the dose maximum toward the surface. A prominence shifts the dose toward the source, with hot spots beside it, and a defect shifts it away.', 'electron-obliquity')],
    ['Bolus acts as extra tissue. It raises the surface dose, smooths an irregular surface, and shortens the range, so the 90% line lies at R<sub>90</sub> minus the bolus thickness below the skin.',
     'The SSD is usually set to the upper surface of the bolus.'],
]


# ---------------------------------------------------------------- matching, typed, and tap-the-figure questions
PROBLEMS += [
]


# ---------------------------------------------------------------- bolus
r90_b = 12 / 3.3 - 1.5
miss = 100 * (1 - 0.80) / 20                                                        # one fraction of 20 without bolus, the surface dose being 80% of the dose with it
PROBLEMS += [
    PRN(STEM("A 12 MeV electron beam is used with 1.5 cm of tissue-equivalent bolus on the skin. Take R<sub>90</sub> = E / 3.3 cm for a bare beam.", [], "How deep below the skin is the [[90% line]]?"), r90_b, [12 / 3.3, 12 / 3.3 - 2 * 1.5, 12 / 3.3 + 1.5], "{:.1f} cm",
        f"Bare beam: R<sub>90</sub> = 12 / 3.3 = {12 / 3.3:.2f} cm. The bolus uses 1.5 cm of the range, so the 90% line is at {r90_b:.2f} cm below the skin. Ignoring the bolus gives {12 / 3.3:.1f} cm, subtracting it twice gives {12 / 3.3 - 3.0:.1f} cm, and adding it gives {12 / 3.3 + 1.5:.1f} cm.", lvl="Moderate"),
    PRN(STEM("A skin cancer is treated in 20 fractions with an electron beam and bolus. On one fraction the bolus is left out. Without bolus the dose at the skin surface is 80% of the dose with it (illustrative).", [], "By what [[percentage]] is the total dose at the skin surface below the plan?"), miss, [20.0, 4.0, 100 * (1 - 0.80) / 19], "{:.2f}%",
        f"On that fraction the surface dose is short by 20%. Spread over 20 fractions the total is short by 20% / 20 = {miss:.2f}%. The shortfall on the single fraction is 20%, and using the 80% in place of the 20% gives 4.0%.", lvl="Moderate"),
    PR("A direct electron field is treated with a sheet of bolus on the skin. The SSD is usually measured to:", "the upper surface of the bolus", ["the skin under the bolus", "the depth of the dose maximum in the patient", "the distal edge of the target"],
       "The bolus is treated as part of the patient, so the beam is set up with the nominal SSD to its upper surface. The output and the PDD are then those of the beam entering a tissue-equivalent surface at that distance.", lvl="Easy"),
]
