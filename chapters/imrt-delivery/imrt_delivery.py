from blocks import *
import math, calc, cases
CS = cases.ST

SEG = [(5.0, 40), (4.0, 30), (3.0, 20), (1.5, 10)]                    # step-and-shoot segments: half-width in cm and MU
flu = lambda x, k=4: sum(w for h, w in SEG[:k] if abs(x) <= h)
t_on = lambda mu, rate: mu / rate * 60                                # beam-on time in seconds for a dose rate in MU/min
arc_t = lambda deg, speed: deg / speed                                # arc time in seconds for a gantry speed in degrees per second
arc_mu = lambda rate, t: rate / 60 * t                                # the most MU an arc can deliver at a dose rate in MU/min

TOPIC = dict(
    id="imrt-delivery", domain=3, sub="III.D", title="IMRT and VMAT delivery",
    ref=dict(aapm="TG-119, TG-218", khan="20", ford="14"),
    guide=[
        H("Rationale for IMRT"),
        P("In three-dimensional conformal therapy each beam has a uniform fluence across it, shaped to the target as seen from that angle. The high-dose region may then not conform well to the target, and an organ at risk may not be spared. A concave target with an organ inside the concavity is a hard case. [[1|In intensity-modulated radiation therapy the fluence of each beam is varied across the field, with higher or lower intensity where it is needed.]] The posterior beam of a prostate or pelvic plan, for example, can have high intensity at its edges and low intensity where the beam passes through the organ."),
        TABLE(["Reason for IMRT", "Example"], [["[[1|Conforms the high-dose region to the target]]", "[[1|A concave target]]"], ["[[1|Spares normal tissue]]", "Cord, salivary glands, rectum, bladder"], ["Introduces an inhomogeneous dose when it is needed", "Different dose levels to different parts of the target"]]),
        P("In a head-and-neck case the goals may be 68.6 Gy to the gross disease, 60 Gy to an intermediate region, and 50 Gy to the nodes. With 3D conformal fields, the posterior photon fields have to stop at about 45 Gy to spare the spinal cord, so the goals are not met even with an electron boost. IMRT controls the dose much more finely, treats each region to its dose, and can also spare a parotid gland. There is Level I evidence of lower toxicity with IMRT than with 3D conformal therapy in prostate cancer, and guidelines for hypofractionated prostate treatment recommend IMRT. Sites that benefit include the central nervous system, head and neck, lung, and prostate."),
        P(f"In the delivered dose of a real head-and-neck IMRT plan from the OpenKBP dataset, the 66.5 Gy isodose line, which is 95% of the 70 Gy prescription, wraps around the PTV70 and follows its concave shape on the side of the spinal cord. The dose then falls steeply, so that the maximum dose to the spinal cord is {CS['SpinalCord']['max']:.1f} Gy. A parallel-opposed or a three-dimensional conformal arrangement of open fields cannot make such a concave distribution with this steep fall-off. The lines are the contours of the dose grid that the planning system produced."),
        AVF("case-dose"),
        H("Fluence maps and delivery methods"),
        P("The beam's-eye view is the view of the beam from the source. The fluence map of an IMRT field shows the intensity at each point across the beam, with high gradients in places. [[1|The map can be delivered on a linac with the MLC]], and the delivered fluence can be checked with film or an electronic portal imaging device."),
        TABLE(["Method", "How the fluence is made"], [["[[1|Step-and-shoot]]", "[[1|The MLC forms a shape, the beam is on for a set time, the beam is off, and the MLC moves to the next shape. The shapes add up to the fluence map.]]"],
                                                       ["[[1|Dynamic MLC (sliding window)]]", "[[1|The beam stays on while the leaves move.]] Where a leaf moves slowly, more fluence accumulates, so leaf speed sets the intensity."],
                                                       ["[[2|VMAT]]", "[[2|As dynamic MLC, but the gantry also rotates during the delivery.]] The dose rate and the gantry speed can change as well."],
                                                       ["[[2|Helical tomotherapy]]", "A bank of binary MLC leaves opens and closes quickly while the gantry rotates and the couch slides through the ring. One slice is irradiated at a time."],
                                                       ["[[2|Physical compensator]]", "A machined metal block, often brass, thickest where the least fluence is needed. Its thickness is the inverse of the fluence map."]]),
        EX("Building a fluence profile", STEM("Four step-and-shoot segments are delivered in one dimension.", ["segment 1: |x| ≤ 5 cm, 40 MU", "segment 2: |x| ≤ 4 cm, 30 MU", "segment 3: |x| ≤ 3 cm, 20 MU", "segment 4: |x| ≤ 1.5 cm, 10 MU"], "Find the [[fluence]] at x = 3.5 cm and at x = 0."), ["At 3.5 cm only segments 1 and 2 are open: 40 + 30", "At 0 all four are open: 40 + 30 + 20 + 10"], f"{flu(3.5):.0f} MU at 3.5 cm and {flu(0):.0f} MU at the center. The stepped profile has a high dose in the middle and less toward the edges, built from open fields."),
        P("A control point is a state of the machine in the plan: the gantry angle, the leaf and jaw positions, and the cumulative MU at one moment of the delivery. The machine moves from one control point to the next. For step-and-shoot the control points give the leaf positions of each segment, and for dynamic MLC and VMAT they give a series of leaf positions, with the gantry angles and the MU between them."),
        H("Practical points"),
        P("The usual arrangement for fixed-gantry IMRT is five to nine beams spread evenly around the patient, and VMAT uses one or more arcs. During a VMAT delivery the gantry angle, the leaf positions, and the dose rate can all change. [[1|A dose rate above 1000 MU/min, as in flattening-filter-free beams, shortens the beam-on time.]] [[1|The beam-on time is the MU divided by the dose rate, and for VMAT it cannot be shorter than the time the gantry needs to turn through the arc.]]"),
        EX("Beam-on time", STEM("An IMRT plan of 540 MU.", ["dose rate = 600 MU/min"], "Find the [[beam-on time]]."), ["Time = 540 MU / 600 MU per minute × 60 s"], f"{t_on(540, 600):.0f} s. The time for the leaves to move between segments is added in step-and-shoot delivery."),
        EX("A VMAT arc", STEM("A 360° arc.", ["gantry speed = 4°/s", "dose rate = 600 MU/min"], "Find the [[arc time]] and the most MU the arc can deliver."), ["Time = 360° / 4°/s", "MU = 600 / 60 × 90"], f"{arc_t(360, 4):.0f} s, and at most {arc_mu(600, 90):.0f} MU. A plan with more MU would need a slower gantry or a higher dose rate."),
        P("A hand calculation is a practical secondary check for a simple open-field plan. For IMRT and VMAT, the fluence is modulated across each field and a hand calculation of the point dose is not practical, so the check is a measurement or an independent calculation of the plan."),
        PHOTO("imrt-delivery-diode-array-setup"),
    ],
    cards=[
        F("3D conformal therapy", "Each beam has a uniform fluence, shaped to the target as seen from that angle."),
        F("IMRT", "The fluence of each beam is varied across the field, with higher or lower intensity where it is needed."),
        F("Rationale for IMRT", "It conforms the high-dose region to the target, spares normal tissue, and introduces an inhomogeneous dose when that is wanted."),
        F("IMRT for a head-and-neck case", "3D conformal posterior fields have to stop at about 45 Gy to spare the cord. IMRT can treat each region to its dose and also spare a parotid."),
        F("Fluence map", "The distribution of intensities across a beam. It can be checked with film or an electronic portal imaging device."),
        F("Step-and-shoot", "The MLC forms a shape, the beam is on for a set time, then off while the MLC moves to the next shape."),
        F("Dynamic MLC", "The beam stays on while the leaves move. Slower leaf motion gives more fluence, so leaf speed sets the intensity. Also called sliding window."),
        F("VMAT", "Dynamic MLC with a rotating gantry. The gantry angle, the leaf positions, and the dose rate can all change during delivery."),
        F("Helical tomotherapy", "A bank of binary MLC leaves opens and closes quickly as the gantry rotates and the couch slides through. One slice is irradiated at a time."),
        F("Physical compensator", "A machined metal block, often brass, thickest where the least fluence is wanted: its thickness is the inverse of the fluence map. It uses dose efficiently, but a block is needed for each field."),
        F("Control point", "The state of the machine at one moment of the delivery: gantry angle, leaf and jaw positions, and cumulative MU."),
        F("Hand calculation for IMRT", "Not practical, because the fluence is modulated across each field. A measurement or an independent calculation is used."),
    ],
)

PROBLEMS = [
    PR("In IMRT, compared with 3D conformal therapy, the fluence across a beam is:", "varied across the field", ["uniform across the field", "always zero at the edges", "set by the jaws only"],
       "A 3D conformal beam has a uniform fluence shaped to the target. In IMRT the intensity is modulated.", lvl="Easy"),
    PR("Which is a rationale for IMRT?", "Sparing normal tissue near a concave target", ["Making the dose distribution as uniform as possible in all cases", "Reducing the number of monitor units", "Avoiding the use of an MLC"],
       "IMRT conforms the high dose to the target and spares nearby organs, and it can introduce an inhomogeneous dose on purpose.", lvl="Easy"),
    PR("In step-and-shoot IMRT, the beam is:", "off while the MLC moves between segments", ["on while the leaves move", "on only at one gantry angle", "always at a different energy"],
       "The MLC forms a shape, the beam is on for a set time, and then the beam turns off for the next shape.", lvl="Easy"),
    PR("In dynamic MLC (sliding-window) IMRT, the intensity at a point is controlled mainly by:", "the speed of the leaves", ["the beam energy", "the size of the jaws", "the patient's thickness"],
       "A point is irradiated while it lies in the gap, so slower leaves give more fluence.", lvl="Moderate"),
    PR("Which parameters can change during a VMAT delivery?", "Gantry angle, leaf positions, and dose rate", ["Only the leaf positions", "Only the gantry angle", "The beam energy and the patient position"],
       "VMAT is dynamic MLC with a rotating gantry, and the dose rate and gantry speed can also vary.", lvl="Moderate"),
    PRN(STEM("Four step-and-shoot segments are delivered.", ["segment 1: |x| ≤ 5 cm, 40 MU", "segment 2: |x| ≤ 4 cm, 30 MU", "segment 3: |x| ≤ 3 cm, 20 MU", "segment 4: |x| ≤ 1.5 cm, 10 MU"], "What is the [[fluence]] at x = 3.5 cm?"), flu(3.5), [flu(0), 40.0, 30.0], "{:.0f} MU",
        f"Only segments 1 and 2 are open at 3.5 cm: 40 + 30 = {flu(3.5):.0f} MU. At the center the fluence is {flu(0):.0f} MU.", lvl="Moderate"),
    PRN(STEM("An IMRT plan of 540 MU at a dose rate of 600 MU/min.", [], "What is the [[beam-on time]]?"), t_on(540, 600), [540 / 600, 540 / 600 * 100, 600 / 540 * 60], "{:.0f} s",
        f"Time = 540 / 600 min = 0.9 min = {t_on(540, 600):.0f} s. Leaving the minutes unconverted gives 0.9, and inverting the ratio gives {600 / 540 * 60:.0f}.", lvl="Moderate"),
    PR("A physical compensator for IMRT is thicker where:", "less fluence is required", ["more fluence is required", "the patient is thinner", "the field edge lies"],
       "A thicker block attenuates more, so it is thickest where the least fluence is wanted. The compensator map is the inverse of the fluence map.", lvl="Moderate"),
    PRN(STEM("A 360° VMAT arc is delivered at a gantry speed of 4°/s and a dose rate of 600 MU/min.", [], "What is the [[most MU]] that the arc can deliver?"), arc_mu(600, 90), [600.0, 600 / 60 * 4, 360 / 4], "{:.0f} MU",
        f"The arc takes 360 / 4 = {arc_t(360, 4):.0f} s. At 600 MU/min = 10 MU/s the most it can deliver is 10 × {arc_t(360, 4):.0f} = {arc_mu(600, 90):.0f} MU.", lvl="Challenging"),
    PR("Why is a hand calculation of the point dose not practical for an IMRT plan?", "The fluence is modulated across each field, so there is no simple open-field geometry", ["IMRT uses no monitor units", "The calibration of an IMRT plan is unknown", "The beam energy is not defined"],
       "A hand calculation needs a uniform field with a known size and depth. IMRT is checked by measurement or an independent calculation instead.", lvl="Challenging"),
    PR("A control point in a treatment plan specifies:", "the gantry angle, the leaf and jaw positions, and the cumulative MU at one moment of the delivery", ["only the prescription dose", "the position of the patient on the couch", "the beam energy of the next fraction"],
       "The machine moves between control points, so a series of them describes the whole delivery.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4, 5, 6, 7], 2: [9]}

TERMS = ['step-and-shoot', 'dynamic MLC', 'fluence map', 'control point', "beam's-eye view"]

TAKE = [
    ["IMRT varies the fluence across each beam, so the high-dose region can follow a concave target and spare organs at risk."],
    [('The fluence map of an IMRT field is built from MLC shapes: step-and-shoot adds segments with the beam off between them, and dynamic MLC keeps the beam on while the leaves move.', 'fluence-segments'),
     ('Step-and-shoot, dynamic MLC, VMAT, tomotherapy, and compensators deliver a fluence map in different ways. VMAT adds a rotating gantry to dynamic MLC.', 'delivery-methods')],
    [('Beam-on time is MU divided by dose rate. A higher dose rate shortens it, but a VMAT arc cannot be shorter than the gantry rotation allows.', 'beam-time')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
PROBLEMS += [
]
