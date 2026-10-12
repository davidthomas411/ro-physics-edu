from blocks import *
import math, calc

MU_EFF = 0.045                                              # per cm, slope of the depth dose used to turn a wedge angle into a dose tilt (schematic)
hinge = lambda phi: 90 - phi / 2                            # wedge angle for two beams separated by the hinge angle phi
tilt = lambda deg, w=10: math.exp(-MU_EFF * w * math.tan(math.radians(deg)))    # heel dose relative to toe dose across a field of width w (cm), schematic
mu_w = 150 / 0.55
mu_both = 180 / (0.66 * 0.97)

TOPIC = dict(
    id="wedges", domain=3, sub="III.A", title="Wedges and compensation",
    ref=dict(aapm="", khan="12", ford="12"),
    guide=[
        H("Wedge physics"),
        P("A wedge attenuates a beam more on one side than on the other. The thick end is the heel and the thin end is the toe. The wedge angle is not the angle of the metal. It is the angle that an isodose line makes with the line perpendicular to the beam axis, measured at a reference depth, usually 10 cm."),
        P("Wedges come in several forms. Physical wedges of fixed angles, such as 15°, 30°, 45°, and 60°, are mounted on a holder in the head of the linac. A motorized wedge is a single 60° wedge inside the head, and smaller angles are made from combinations of open and wedged beams. In a dynamic wedge there is no metal in the beam: a jaw moves across the field while the beam is on, and the side covered longer by the jaw receives less dose and plays the role of the heel."),
        P("A wedge removes part of the beam, so the monitor units must rise. The wedge factor WF is the dose per MU with the wedge divided by the dose per MU without it, at a reference point, and the MU scale as 1/WF."),
        EX("MU with a wedge", STEM("A wedged field.", ["MU without the wedge = 150", "wedge factor = 0.55"], "Find the [[MU with the wedge]]."), ["MU = 150 / 0.55"], f"{mu_w:.1f} MU."),

        H("Planning with wedges"),
        P("Wedges correct the gradient of a pair of beams that meet at an angle. The angle between the central axes of the two beams is the hinge angle φ. The wedge angle that gives a uniform dose in the overlap is approximately 90° − φ/2. For parallel-opposed beams φ = 180° and no wedge is needed. For perpendicular beams φ = 90° and the wedges are 45°."),
        EQ("wedge angle ≈ 90° − φ / 2", "φ = hinge angle between the beams"),
        TABLE(["Hinge angle φ", "Wedge angle"], [[f"{p}°", f"{hinge(p):.0f}°"] for p in (60, 90, 100, 120, 150, 180)]),
        P("The wedges are oriented heels together, toes apart. The heels sit at the corner where the two beams overlap near the surface, where the dose would otherwise be highest. A machine with only a motorized 60° wedge reaches intermediate angles, such as 50°, by weighting the open and wedged beams."),
        EX("Wedge angle for a hinge angle", STEM("Two oblique beams.", ["hinge angle φ = 100°"], "Find the [[wedge angle]]."), ["Wedge angle = 90° − φ / 2 = 90° − 50°"], "40°."),

        H("Compensation for thickness"),
        P("Wedges also compensate for a patient whose thickness changes across the field. In a breast treated with tangent fields, the tissue is thicker toward the medial side and thinner at the outer edge. A wedge with the heel toward the thinner side attenuates the beam where the tissue is thin and evens out the dose. A shaped metal compensator, thicker where more attenuation is needed, can do the same in two dimensions."),
        EX("Wedge and tray together", STEM("A field with both a wedge and a blocking tray.", ["MU without accessories = 180", "wedge factor = 0.66", "tray factor = 0.97"], "How many [[MU with both]]?"), ["MU = 180 / (0.66 × 0.97)"], f"{mu_both:.1f} MU."),
    ],
    cards=[
        F("Heel and toe of a wedge", "The thick end of the wedge is the heel, which attenuates more. The thin end is the toe."),
        F("Wedge angle", "The angle that an isodose line makes with the line perpendicular to the beam axis, at a reference depth, usually 10 cm. It is not the physical angle of the metal."),
        F("Physical, motorized, and dynamic wedges", "Physical: fixed angles (15°, 30°, 45°, 60°) mounted on a holder. Motorized: one 60° wedge in the head, other angles from combinations with an open beam. Dynamic: a jaw moves during irradiation, with no metal in the beam."),
        F("Wedge factor", "The dose per MU with the wedge divided by the dose per MU without it, at a reference point. The MU scale as 1/WF."),
        F("Hinge angle", "The angle between the central axes of two beams."),
        F("Wedge angle for a pair of beams", "About 90° − φ/2, where φ is the hinge angle. A 120° pair needs 30° wedges, and a 90° pair needs 45°."),
        F("Wedge orientation for a pair", "Heels together, toes apart."),
        F("Wedges for parallel-opposed beams", "None are needed: the hinge angle is 180° and the formula gives 0°."),
        F("Wedges in tangent breast fields", "The tissue is thinner at the outer edge, so a wedge with the heel toward the thinner side evens out the dose."),
    ],
)

PROBLEMS = [
    PR("The wedge angle of a wedged field is defined as:", "the angle between an isodose line and the line perpendicular to the beam axis", ["the angle of the sloping face of the metal", "the angle of the beam from the vertical", "the angle between the two beams of a pair"],
       "The physical shape does not define it. The dose distribution does, so the angle is read from the isodose tilt at a reference depth.", lvl="Easy"),
    PR("Which end of a wedge attenuates the beam more?", "The heel, the thick end", ["The toe, the thin end", "Both ends equally", "The middle"],
       "More metal means more attenuation. The dose is lower under the heel and higher under the toe.", lvl="Easy"),
    PRN(STEM("Two oblique beams.", ["hinge angle φ = 100°"], "What [[wedge angle]] gives a uniform dose?"), hinge(100), [50.0, 100.0, 80.0], "{:.0f}°",
        "Wedge angle ≈ 90° − φ/2 = 90° − 50° = 40°.", lvl="Moderate"),
    PR("For a pair of wedged beams, the wedges are normally oriented:", "heels together and toes apart", ["toes together and heels apart", "both heels toward the posterior", "with one wedge and one open field"],
       "The heels attenuate the beams where they overlap near the surface, which would otherwise be the hottest region.", lvl="Moderate"),
    PR("Which pair of beams needs no wedge to produce a uniform dose in the overlap?", "A parallel-opposed pair", ["A perpendicular pair", "A pair at 120°", "A pair at 60°"],
       "The hinge angle is 180°, so the formula gives a wedge angle of 0°.", lvl="Moderate"),
    PR("In a breast treated with tangent fields, the tissue is thicker medially. To even out the dose with a wedge, the heel should be placed:", "toward the thinner, outer side", ["toward the thicker, medial side", "at the chest wall only", "on the anterior surface only"],
       "The heel attenuates the beam where the tissue is thinner, so the dose in the thin and thick regions is brought closer together.", lvl="Challenging"),
]

INLINE = {0: [1, 2], 1: [3, 4]}

TERMS = ['wedge angle', 'wedge factor', 'hinge angle']

TAKE = [
    [('The wedge angle is the isodose tilt at a reference depth, not the angle of the metal. The MU scale as 1/WF.', 'wedge-profile')],
    [('For two beams with hinge angle φ the wedge angle is about 90° − φ/2, with the heels together.', 'wedge-hinge')],
    [('A wedge with the heel toward the thinner tissue evens out the dose in a tilted or tapering patient, as in a tangent breast field.', 'wedge-breast')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_prof = lambda x: 100 * math.exp(-MU_EFF * x * math.tan(math.radians(45)))
PROBLEMS += [
]
