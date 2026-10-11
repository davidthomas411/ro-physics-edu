from blocks import *
import math, calc

gp = lambda s, dist, scd: s * (dist / scd - 1)             # geometric penumbra: s [ (f + d) / SCD - 1 ], all lengths in the same unit
w_a, w_b, w_c = gp(3, 100, 50), gp(3, 110, 50), gp(3, 100, 40)
r_scd = gp(1, 100, 40) / gp(1, 100, 50)                      # SCD 40 against 50 cm at the same plane
r_dep = gp(1, 120, 50) / gp(1, 105, 50)                      # depth 20 against 5 cm at SSD 100 cm, SCD 50 cm
w_typed = gp(2, 105, 45)
sig = lambda x: 0.5 * math.erfc(x / math.sqrt(2))            # dose fraction at x standard deviations beyond the 50% point

TOPIC = dict(
    id="profiles", domain=3, sub="III.A", title="Beam profiles, flatness, and penumbra",
    ref=dict(aapm="", khan="9, 13", ford="10"),
    guide=[
        H("Profiles and penumbra"),
        P("A beam profile is the dose across the beam at a fixed depth. The edge of the field is the position where the dose has fallen to 50% of the central-axis value. The dose does not drop to zero at the edge: it falls over a distance called the penumbra. The usual measure is the 80%–20% penumbra, the distance between the 80% and the 20% dose points on the profile."),
        P("Three effects widen the penumbra. Geometric penumbra comes from the finite size of the source, because points on the source see the collimator edge from different angles. Transmission through the edge of the collimator, a jaw or an MLC leaf, adds a second contribution. Radiological penumbra comes from the patient: Compton electrons set in motion near the edge can travel out of the field, so the dose immediately inside the edge falls and the dose immediately outside rises."),
        EQ("w = s [ (f + d) / SCD − 1 ]", "w = geometric penumbra,   s = source size,   f + d = distance from the source to the plane,   SCD = source-to-collimator distance"),
        P("The geometric penumbra grows with source size, with SSD, and with depth, and it shrinks as the collimator is moved farther from the source. The radiological penumbra grows with electron range. It is therefore larger at higher energy and larger in low-density tissue such as lung."),
        EX("Geometric penumbra at the isocenter", STEM("A linac with a finite source.", ["source size s = 3 mm", "source-to-collimator distance SCD = 50 cm", "plane at 100 cm from the source"], "Find the [[geometric penumbra]]."),
           ["w = s [ (f + d) / SCD − 1 ]", "w = 3 mm × (100 / 50 − 1)"], f"{w_a:.1f} mm."),
        EX("Penumbra at depth", STEM("A linac with a finite source.", ["source size = 3 mm", "SCD = 50 cm", "point at 10 cm depth, SSD 100 cm"], "Find the [[geometric penumbra]] at 10 cm depth."),
           ["The distance from the source is 100 + 10 = 110 cm", "w = 3 mm × (110 / 50 − 1)"], f"{w_b:.1f} mm, wider than at the surface."),
        EX("Moving the collimator", STEM("A linac with a finite source.", ["source size = 3 mm", "SCD = 40 cm", "plane at 100 cm from the source"], "Find the [[geometric penumbra]]."),
           ["w = 3 mm × (100 / 40 − 1)"], f"{w_c:.1f} mm. A collimator 10 cm closer to the source widens the penumbra by 50%."),

        H("Flatness and horns"),
        P("A profile is flat when the dose is nearly uniform across the central part of the field. A linac makes the beam flat with a flattening filter, thicker on the axis than at the edges, and the beam is flat at one reference depth, usually 10 cm. Flatness and symmetry are specified there."),
        P("At shallower depths the dose near the edges is higher than at the center. These bumps are the horns, and they are largest at d<sub>max</sub> and larger at higher energy. At greater depths the profile becomes higher at the center. Scatter builds up toward the axis with depth, and the beam on the axis has crossed the thickest part of the filter, so its spectrum is harder and its dose falls off more slowly with depth."),
        TABLE(["Depth", "Profile shape"], [["Shallower than the reference depth", "Horns: edges higher than the center"], ["Reference depth (10 cm)", "Flat"], ["Deeper than the reference depth", "Center higher than the edges"]]),

        H("Out-of-field dose"),
        P("The dose outside the field edge is not zero. Close to the edge it comes mostly from photons scattered out of the field, in the patient and in the head of the machine. Farther away it comes mostly from leakage through the collimators and the shielding of the head. The planning system predicts dose far outside the field poorly, and it should not be used to estimate it. AAPM Task Group 158 covers the measurement and calculation of out-of-field dose, which matters for shielding and for organs and devices outside the treated volume."),

        H("Flattening-filter-free beams"),
        P("The flattening filter is a cone of metal in the beam, thickest on the axis, that evens out the profile of the beam from the target. A flattening-filter-free (FFF) beam leaves it out, and the profile keeps the peaked shape of the beam from the target: highest on the axis and falling toward the edges. Stereotactic and other small-field treatments are often delivered with FFF beams, because the peak matters little over a small field."),
        P("Without the filter the beam has four differences from a flattened beam of the same nominal energy. The dose rate on the axis is higher, typically two to four times, so a high-dose fraction takes less time and the patient has less time to move. The spectrum is softer, because the filter hardens the beam, so the depth dose falls slightly faster. Less of the head scatter comes from the filter, so the output changes less with the field size. And the profile is not flat, so the planning system needs a beam model that is commissioned for it, and the two modes are not interchangeable."),
        EX("Beam-on time", STEM("A stereotactic fraction needs 2000 MU. A flattened beam delivers 600 MU/min and an FFF beam of the same nominal energy 1400 MU/min (illustrative).", [], "Find the [[beam-on time]] in each mode."), ["Time = MU / dose rate", "Flattened: 2000 / 600", "FFF: 2000 / 1400"], f"{2000 / 600:.1f} min with the flattened beam and {2000 / 1400:.1f} min with the FFF beam, a saving of {2000 / 600 - 2000 / 1400:.1f} min."),
    ],
    cards=[
        C("What is a beam profile?", "The dose across the beam at a fixed depth."),
        C("Where is the field edge on a profile?", "At the 50% dose point, relative to the central-axis dose."),
        C("Define the 80%–20% penumbra.", "The distance between the 80% and the 20% dose points on the profile, across the field edge."),
        C("Name three contributions to the penumbra.", "Geometric (finite source size), transmission through the collimator edge, and radiological (electron transport in the patient)."),
        C("Write the geometric penumbra.", "w = s [ (f + d) / SCD − 1 ], with s the source size, f + d the distance from the source to the plane, and SCD the source-to-collimator distance."),
        C("How does the geometric penumbra change with source size, SSD, depth, and SCD?", "It grows with source size, SSD, and depth, and it shrinks as the SCD increases."),
        C("How does the radiological penumbra depend on energy and density?", "It grows with the range of the secondary electrons, so it is larger at higher energy and in low-density tissue such as lung."),
        C("At what depth is a linac profile made flat?", "A reference depth, usually 10 cm."),
        C("What are horns?", "Higher dose near the field edges than at the center, seen at shallow depths such as d<sub>max</sub> in a beam that is flat at 10 cm."),
        C("How does the profile change with depth for a beam flat at 10 cm?", "Shallower, there are horns. Deeper, the center is higher, because scatter builds up on the axis and the central spectrum is harder."),
        C("Why is the central spectrum of a flattened beam harder?", "The central rays cross the thickest part of the flattening filter, which removes more low-energy photons."),
        C("What produces the dose immediately outside the field edge, and what far from it?", "Near the edge: photons scattered out of the field. Far from the field: leakage through the head and collimators."),
        C("Can the planning system be trusted for out-of-field dose?", "No. It predicts dose far from the field poorly. AAPM TG-158 covers out-of-field dose."),
    ],
)

PROBLEMS = [
    PR("The 80%–20% penumbra of a photon beam is:", "the distance between the 80% and the 20% dose points on the profile", ["the distance between the 100% and the 0% dose points", "the width of the 50% isodose", "the depth between the 80% and 20% PDD values"],
       "The penumbra describes the fall-off at the field edge on a profile, so it is a distance along the profile.", lvl="Easy"),
    PR("Which change increases the geometric penumbra?", "A larger source size", ["A larger source-to-collimator distance", "A smaller SSD", "A shallower point of interest"],
       "w = s [ (f + d) / SCD − 1 ] grows with s, with f and d, and shrinks with SCD.", lvl="Easy"),
    PR("A photon beam profile is normally made flat at a depth of about:", "10 cm", ["d<sub>max</sub>", "1 cm", "30 cm"],
       "The flattening filter is designed for a reference depth, usually 10 cm, which is typical of the depth of treatment.", lvl="Easy"),
    PR("A linac beam is flat at 10 cm depth. At d<sub>max</sub> the dose near the edges of the field is:", "higher than at the center, forming horns", ["lower than at the center", "equal to the dose at the center", "zero"],
       "To be flat at depth, the beam is over-corrected at shallow depths, so the edges are higher than the center at d<sub>max</sub>.", lvl="Moderate"),
    PR("Compared with a 6 MV beam, the radiological penumbra of an 18 MV beam is:", "larger, because the secondary electrons have a longer range", ["smaller, because the electrons have a longer range", "the same, because it depends only on source size", "smaller, because there is less scatter"],
       "Compton electrons from a higher-energy beam travel farther, so more of them leave the field edge and the fall-off is smeared out.", lvl="Moderate"),
    PRN(STEM("A linac with a finite source.", ["source size = 3 mm", "SCD = 50 cm", "point at 10 cm depth, SSD 100 cm"], "What is the [[geometric penumbra]] at that point?"), w_b, [w_a, 3 * 110 / 50, 1.5], "{:.1f} mm",
        f"w = s [ (f + d) / SCD − 1 ] = 3 × (110 / 50 − 1) = {w_b:.1f} mm. Using 100 cm for the distance gives 3.0 mm; leaving out the −1 gives {3 * 110 / 50:.1f} mm.", lvl="Moderate"),
    PRM("Which of these contribute to the penumbra of a photon beam in a patient?", ["The size of the radiation source", "Transmission through the edge of the collimator", "Scatter of secondary electrons out of the field edge"], ["The monitor unit calibration", "The prescribed dose"],
        "Geometric, transmission, and radiological effects shape the penumbra. The calibration and the prescription scale the dose but do not change its fall-off.", lvl="Moderate"),
    PR("Close to the edge of a treatment field, the out-of-field dose comes mainly from:", "photons scattered out of the field", ["leakage through the collimators", "activation of the linac head", "back-scatter from the couch"],
       "Scatter dominates near the edge. Leakage through the head becomes the main source farther from the field.", lvl="Moderate"),
    PRN(STEM("Two collimator positions for the same linac.", ["source size = 3 mm", "SCD = 40 cm in case A, 50 cm in case B", "plane at 100 cm from the source"], "The geometric penumbra in case A is how many [[times that in case B]]?"), r_scd, [1.25, 0.8, 1.56], "{:.2f}",
        f"Case A: 3 × (100 / 40 − 1) = {w_c:.1f} mm. Case B: 3 × (100 / 50 − 1) = {w_a:.1f} mm. The ratio is {r_scd:.2f}. The ratio of the distances (1.25) is not the ratio of the penumbras, because of the −1.", lvl="Challenging"),
    PR("A beam is flat at 10 cm depth. At 20 cm the profile is:", "higher at the center than at the edges", ["flat", "higher at the edges than at the center", "asymmetric"],
       "Scatter increases on the axis with depth, and the harder central spectrum falls off more slowly, so the center rises relative to the edges.", lvl="Challenging"),
    PRN(STEM("A linac with a finite source.", ["source size = 3 mm", "SCD = 50 cm", "SSD = 100 cm"], "The geometric penumbra at 20 cm depth is how many [[times that at 5 cm depth]]?"), r_dep, [120 / 105, 4.0, 1.40], "{:.2f}",
        f"w ∝ (f + d) / SCD − 1. At 20 cm: 120 / 50 − 1 = 1.40. At 5 cm: 105 / 50 − 1 = 1.10. The ratio is {r_dep:.2f}. The ratio of the distances (1.14) is smaller because of the −1.", lvl="Challenging"),
    PR("Which statement about out-of-field dose is correct?", "Planning systems predict it poorly far from the field, where leakage dominates", ["Planning systems are most accurate far from the field", "It is caused only by scatter in the patient", "It does not depend on the energy of the beam"],
       "Scatter dominates near the edge and head leakage far away. The model parameters of a planning system are fitted to the beam inside the field, so far-out doses are unreliable.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 5, 6], 1: [3, 4], 2: [8]}

TERMS = ['penumbra', 'geometric penumbra', 'horns', 'flattening filter']

TAKE = [
    [('The penumbra is the fall-off at the field edge, measured as the 80%–20% width. The geometric part is w = s [ (f + d) / SCD − 1 ]: it grows with source size, SSD, and depth.', 'penumbra-geometry'),
     ('Electron transport widens the penumbra: more at higher energy and in low-density tissue such as lung.', 'penumbra-energy')],
    [('A linac profile is flat at a reference depth, usually 10 cm. Shallower there are horns, and deeper the center is higher.', 'profile-depth')],
    [('Out-of-field dose is scatter near the field edge and head leakage far from it. The planning system does not predict it well.', 'out-of-field')],
    ['An FFF beam has a peaked profile, a dose rate two to four times higher, a softer spectrum, and less head scatter, so its output changes less with field size.'],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
_edge = lambda x: 100 * sig(x / 0.35)
_k = lambda d: calc_k(d)
def calc_k(d):                                                # profile curvature: +0.04 at d_max, 0 at 10 cm, -0.05 at 20 cm (schematic)
    return 0.04 * (10 - d) / 8.5 if d <= 10 else -0.05 * (d - 10) / 10
_ratio = lambda d: (1 + 0.8 * calc_k(d)) / (1 - 0.2 * calc_k(d))     # edge-to-axis dose for the profile 1 + k (u^4 - 0.2)
PROBLEMS += [
    SORT("Does each change widen or narrow the penumbra?", ["Widens it", "Narrows it"],
         [("Larger source size", 0), ("Smaller focal spot", 1), ("Larger SSD", 0), ("Greater depth", 0), ("Larger source-to-collimator distance", 1), ("Lower photon energy", 1), ("Lung instead of muscle", 0), ("Collimator closer to the source", 0)],
         "Geometric penumbra grows with source size, SSD, and depth, and falls with source-to-collimator distance. Radiological penumbra grows with electron range, which is larger at higher energy and in lung.", lvl="Moderate"),
    TYPED(STEM("A linac with a finite source.", ["source size = 2 mm", "SCD = 45 cm", "plane at 105 cm from the source"], "What is the [[geometric penumbra]]?"), w_typed, 0.01, "mm",
          f"w = s [ (f + d) / SCD − 1 ] = 2 × (105 / 45 − 1) = {w_typed:.2f} mm.", lvl="Moderate"),
    FIGQ(STEM("The graph shows a beam profile across the edge of a field. The position is measured from the 50% point.", [], "Tap the [[field edge]]."),
         FS(x=dict(min=-2, max=2, ticks=[-2, -1, 0, 1, 2], label="Position (cm)"), y=dict(min=0, max=100, ticks=[0, 20, 50, 80, 100], label="Dose (% of the central axis)", fmt="pct"), series=[dict(pts=PTS(_edge, -2, 2), color="plot-1")], xunit=" cm", xdec=2, xname="Position", label="Dose profile across a field edge"),
         [(-0.15, 0.15)], "The field edge is defined at the 50% dose point. The 80% and 20% points lie on either side of it, about 0.3 cm away for this edge, and the distance between them is the penumbra.", lvl="Easy", note="the 50% point"),
    FIGQ(STEM("A linac beam is flat at a reference depth of 10 cm. The graph shows the ratio of the dose near the field edge to the dose on the axis.", [], "Tap the depth at which the [[horns are largest]]."),
         FS(x=dict(min=1.5, max=20, ticks=[2, 5, 10, 15, 20], label="Depth (cm)"), y=dict(min=0.9, max=1.1, ticks=[0.9, 0.95, 1, 1.05, 1.1], label="Edge ÷ axis dose"), series=[dict(pts=PTS(_ratio, 1.5, 20), color="plot-1")], xunit=" cm", xdec=1, xname="Depth", label="Edge-to-axis dose ratio against depth (schematic)"),
         [(1.5, 3.5)], "Horns are higher dose near the field edges than on the axis, so they appear where the ratio is above 1. That is at depths shallower than the reference depth, and the ratio is largest at the shallowest depth, d<sub>max</sub>, where the beam is most over-corrected at the edges. At 10 cm the ratio is 1 (flat), and deeper it falls below 1, which means the center is higher. The curve is schematic.", lvl="Easy", note="at d<sub>max</sub>, about 1.5 cm"),
]
INLINE = {0: [1, 2, 5, 6, _n0 + 1, _n0 + 3], 1: [3, 4, _n0 + 4], 2: [8]}


# ---------------------------------------------------------------- flattening-filter-free beams
_nf = len(PROBLEMS)
t_flat, t_fff = 2400 / 600, 2400 / 1400
PROBLEMS += [
    PR("The profile of a flattening-filter-free beam, measured across the field, is:", "peaked on the axis and falling toward the edges", ["flat to within a few percent at 10 cm depth", "higher at the edges than on the axis, with horns", "the same as that of a flattened beam, with a different energy"],
       "Without the filter nothing evens out the profile of the beam from the target, which is forward-peaked. The flattening filter produces the flat profile, and horns appear when the filter overcorrects at shallow depth.", lvl="Easy"),
    PRM("Which of the following are expected of a flattening-filter-free beam, compared with a flattened beam of the same nominal energy and field size?", ["A higher dose rate on the central axis", "Less variation of the output with the field size, because there is less head scatter"],
        ["A harder mean photon energy", "A flat profile at 10 cm depth", "A much wider penumbra"],
        "Without the filter the dose rate on the axis rises by a factor of about 2 to 4. The filter hardens the beam, so the spectrum is softer without it, and the profile is peaked. Head scatter falls, so the output varies less with field size. The penumbra is similar.", lvl="Moderate"),
    PRN(STEM("A stereotactic fraction needs 2400 MU. A flattened beam delivers 600 MU/min and an FFF beam 1400 MU/min (illustrative).", [], "By how many [[minutes]] does the FFF beam shorten the beam-on time?"), t_flat - t_fff, [t_fff, t_flat, 2400 / (1400 - 600)], "{:.1f} min",
        f"The flattened beam needs 2400 / 600 = {t_flat:.1f} min and the FFF beam 2400 / 1400 = {t_fff:.2f} min, so the saving is {t_flat - t_fff:.1f} min. The time with the FFF beam alone is {t_fff:.1f} min, the time with the flattened beam alone is {t_flat:.1f} min, and dividing by the difference of the dose rates gives {2400 / (1400 - 600):.1f} min.", lvl="Moderate"),
]
INLINE.setdefault(1, []).append(_nf + 1)
