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
        P("The penumbra of an electron beam depends on energy and depth. Near the surface, the penumbra of an 18 MeV beam is smaller than that of an 8 MeV beam, because electron scattering is more forward-directed at higher energy. As the depth increases, the penumbra becomes very wide, especially at higher energy: the high isodose lines tuck in toward the center of the field while the low isodose lines bulge out."),
        P("An electron field is defined by an applicator, or cone, and a cutout. Typical applicators are 6, 10, 15, 20, and 25 cm square, and the cutout is a shaped piece of Cerrobend at the end of the applicator. In the usual setup the patient is at SSD 100 cm, the end of the cone is 95 cm from the source, and a 5 cm air gap remains between the cone and the skin. The cutout is drawn about 1 cm wider on each side than the intended treatment area, to allow for the penumbra. This is only a rough rule."),
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
    ],
    cards=[
        F("Electron penumbra and energy", "Near the surface the penumbra is smaller at higher energy, because scattering is more forward-directed. At depth it becomes very wide, especially at higher energy."),
        F("Isodose lines at depth in an electron beam", "The high isodose lines tuck in toward the center of the field and the low isodose lines bulge out, more so at higher energy."),
        F("Electron applicators", "Typically 6, 10, 15, 20, and 25 cm square, with a Cerrobend cutout at the end."),
        F("Standard electron setup", "SSD 100 cm. The end of the cone is 95 cm from the source, so a 5 cm air gap remains to the skin."),
        F("Cutout margin", "Drawn about 1 cm wider on each side than the treatment area, to allow for the penumbra. A rough rule."),
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
       "At higher energy the electrons are scattered less sideways near the surface. At greater depth the situation reverses and the penumbra becomes very wide.", lvl="Easy"),
    PR("In the usual electron setup with the patient at SSD 100 cm, the end of the applicator is about how far from the skin?", "5 cm", ["0 cm", "10 cm", "20 cm"],
       "The end of the cone is 95 cm from the source, so a 5 cm air gap remains.", lvl="Easy"),
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
    PRN(STEM("A photon field and an electron field abut with no gap.", ["prescription = 200 cGy", "hot spot = 30%"], "What [[dose]] is received in the hot spot?"), hot_ep, [200.0, 230.0, 170.0], "{:.0f} cGy",
        f"Dose = 200 × 1.30 = {hot_ep:.0f} cGy. A 30% hot spot raises the dose by 30% of the prescription.", lvl="Moderate"),
    PRM("Which occur in an electron beam under a tissue prominence, such as the nose?", ["The dose under the prominence is shifted toward the source", "The regions on either side receive more dose from scattered electrons"], ["The isodose lines under it move away from the source", "The hot spots are smaller at higher energy"],
        "The prominence shortens the path to the tissue under it, so the dose shifts toward the source. Electrons scattered out of the prominence add dose beside it, more at higher energy.", lvl="Moderate"),
    PR("An internal eye shield of tungsten has an aluminium cap on the side facing the beam. The cap is there to:", "absorb electrons backscattered from the tungsten, protecting the tissue in front of it", ["increase the attenuation of the beam", "raise the dose behind the shield", "make the shield lighter"],
       "A high-Z metal backscatters electrons strongly. A low-Z layer in front of it absorbs them, so the tissue in front of the shield is not overdosed.", lvl="Challenging"),
    PR("Under a tissue defect in an electron beam, the isodose lines are:", "shifted away from the source, with hot spots immediately inside the edges of the defect", ["shifted toward the source, with a cold line at the edges", "unchanged", "shifted toward the source, with hot spots at the center"],
       "The path to the tissue under the defect is longer, so the dose is shifted away from the source. Electrons scattered from the sides add dose immediately inside the edges.", lvl="Challenging"),
    PR("Two 6 MeV electron fields are matched with no gap. Compared with the dose elsewhere in the fields, the dose at the junction is:", "about 10% higher", ["about 30% higher", "about 10% lower", "the same"],
       "Electron–electron junctions have a smaller hot spot than electron–photon junctions, about 10% for two 6 MeV fields.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 4], 1: [6, 7], 2: [5, 9]}

TERMS = ['cutout', 'feathering', 'virtual source']

TAKE = [
    [('At shallow depth a higher energy gives a smaller penumbra, but at depth it becomes much wider and the high isodose lines tuck in. Extended SSD widens the penumbra and lowers the output.', 'electron-penumbra')],
    [('An electron–photon junction with no gap has a hot spot of about 30% on the photon side. A gap lowers it but leaves a low-dose region at the surface, and feathering spreads the effect.', 'electron-matching')],
    [('Oblique incidence moves the dose maximum toward the surface. A prominence shifts the dose toward the source, with hot spots beside it, and a defect shifts it away.', 'electron-obliquity')],
]


# ---------------------------------------------------------------- matching, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Match each junction to its main finding.", ["Electron–photon, no gap", "Electron–photon, large gap", "Electron–electron, no gap", "Feathering"],
         [("A hot spot of about 30% on the photon side near the electron d<sub>max</sub>", 0), ("A low-dose region at the surface", 1), ("A hot spot of about 10% where the fields abut", 2), ("The junction is moved by a small amount each day", 3)],
         "A junction with no gap gives a hot spot, which is larger for an electron–photon pair than for two electron fields. A large gap leaves the surface underdosed, and feathering spreads whichever problem is present.", lvl="Moderate", mode="match", cap=1),
    TYPED(STEM("An electron field.", ["width of the treatment area = 6 cm", "margin = 1 cm on each side"], "What [[cutout width]] is drawn?"), 8.0, 0.01, "cm",
          "Width = 6 + 1 + 1 = 8 cm.", lvl="Moderate"),
    FIGQ(STEM("The graph shows schematic penumbra widths against depth for 8 MeV and 18 MeV electron beams.", [], "Tap the [[depth at which the 18 MeV penumbra becomes wider than the 8 MeV penumbra]]."),
         FS(x=dict(min=0, max=8, ticks=[0, 2, 4, 6, 8], label="Depth (cm)"), y=dict(min=0, max=20, ticks=[0, 5, 10, 15, 20], label="Penumbra width (mm)"), series=[dict(pts=PTS(w8, 0, 8), color="plot-1"), dict(pts=PTS(w18, 0, 8), color="plot-2")],
            texts=[dict(x=6.2, y=7.5, t="8 MeV", color="plot-1", b=True), dict(x=5.4, y=15.5, t="18 MeV", color="plot-2", b=True)], xunit=" cm", xdec=1, xname="Depth", label="Electron penumbra against depth (schematic)"),
         [(z_cross - 0.5, z_cross + 0.5)], f"The curves cross at {z_cross:.1f} cm. Shallower than that the 18 MeV penumbra is smaller, because scattering is more forward-directed. Deeper, it is wider. The widths are schematic.", lvl="Challenging", note=f"about {z_cross:.1f} cm"),
]
INLINE = {0: [1, 2, 4, _n0 + 3], 1: [6, 7, _n0 + 1], 2: [5, 9]}
