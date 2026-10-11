from blocks import *
import math, calc
import beamdata as bd

pd = lambda d, s=10: bd.pdd_model(d, s)
hs = lambda S, s=10: (100 + pd(S - bd.DMAX, s)) / (2 * pd(S / 2, s))                 # hot spot ratio of an equally weighted parallel-opposed pair, separation S (cm)
p20a, p20b = round(pd(18.5), 1), round(pd(10), 1)                                     # separation 20 cm
p30a, p30b = round(pd(28.5), 1), round(pd(15), 1)                                     # separation 30 cm
p40a, p40b = round(pd(38.5), 1), round(pd(20), 1)                                     # separation 40 cm
h20, h30, h40 = (100 + p20a) / (2 * p20b), (100 + p30a) / (2 * p30b), (100 + p40a) / (2 * p40b)

TOPIC = dict(
    id="multifield", domain=3, sub="III.A", title="Multi-field plans and hot spots",
    ref=dict(aapm="", khan="12", ford="12"),
    guide=[
        H("Parallel-opposed fields"),
        P("Real treatments rarely use a single beam. Two parallel-opposed beams enter from opposite sides of the patient, and the dose along the central axis is the sum of the two PDDs, one counted from each surface. Near each entrance surface the beam entering there is at its maximum dose, and the beam leaving there adds its exit dose, so the superficial dose is higher than the dose at the midplane. These superficial regions are hot spots."),
        EQ("hot spot ratio = [ PDD(d<sub>max</sub>) + PDD(S − d<sub>max</sub>) ] / [ 2 PDD(S / 2) ]", "equal weights and equal SSD,   S = separation of the entrance surfaces,   dose at the midplane = 2 PDD(S / 2)"),
        P("The ratio grows with the separation of the entrance surfaces, because the midplane dose falls while the superficial dose does not (illustrative 6 MV values for a 10 × 10 cm field)."),
        TABLE(["Separation (cm)", "Hot spot ratio"], [[str(S), f"{hs(S):.2f}"] for S in (10, 20, 30, 40, 50)]),
        EX("Hot spot of a pair", STEM("A parallel-opposed pair of 6 MV beams, equal weights.", ["separation S = 20 cm", f"PDD(1.5 cm) = 100%,   PDD(18.5 cm) = {p20a}%", f"PDD(10 cm) = {p20b}%"], "Find the [[hot spot ratio]]."),
           [f"Dose near one surface = 100 + {p20a} = {100 + p20a:.1f} (own beam plus the exit dose of the other)", f"Dose at the midplane = 2 × {p20b} = {2 * p20b:.1f}", f"Ratio = {100 + p20a:.1f} / {2 * p20b:.1f}"], f"{h20:.3f}, about {100 * (h20 - 1):.0f}% above the midplane dose."),

        H("Reducing hot spots"),
        P("Anything that makes the PDD fall off more slowly lowers the hot spot, because the midplane dose is then closer to the maximum. A higher energy does this, and so does a larger field. A thinner patient has a smaller separation, so low energies are acceptable for the brain and for head and neck, while the pelvis and abdomen need higher energies. Opposed lateral beams cross more tissue than AP/PA beams and give larger hot spots."),
        P("The number of fields matters as much. As more beams are used, the entrance dose is spread over more surfaces, and the superficial hot spot falls. Stereotactic systems that use hundreds of beams push this to the limit."),
        TABLE(["Change", "Hot spot"], [["Larger separation", "Higher"], ["Higher energy", "Lower"], ["Larger field", "Lower"], ["More fields", "Lower"], ["Lateral beams instead of AP/PA", "Higher"]]),

        H("Field arrangements"),
        P("Two perpendicular beams give a much lower superficial dose than a parallel-opposed pair, but the dose is not uniform: there is a hot region where the beams cross near the surface and a low-dose region in the opposite corner. Wedges fix this. A four-field box, AP/PA plus two laterals, gives a uniform dose where the beams overlap and spreads the entrance dose over four surfaces."),
        P("The weight of each beam is its share of the dose at the isocenter. With equal weights, four fields deliver a quarter of the prescription each."),
        EX("Beam weights", STEM("A four-field box prescribed to the isocenter.", ["dose at the isocenter = 240 cGy", "AP and PA weights = 30% each", "lateral weights = 20% each"], "Find the [[dose to the isocenter from each lateral field]]."),
           ["Lateral field = 0.20 × 240 cGy"], "48 cGy from each lateral and 72 cGy from each of the AP and PA fields."),
    ],
    cards=[
        F("Parallel-opposed fields", "Two beams entering from opposite sides. The dose on the central axis is the sum of the two PDDs."),
        F("Superficial hot spot of a parallel-opposed pair", "Each entrance surface receives the maximum dose of its own beam plus the exit dose of the other, so the superficial dose exceeds the midplane dose."),
        F("Hot spot ratio", "[ PDD(d<sub>max</sub>) + PDD(S − d<sub>max</sub>) ] / [ 2 PDD(S / 2) ], for equal weights and equal SSD, with S the separation."),
        F("Hot spot and separation", "It grows with the separation: larger for lateral than for AP/PA fields, and for the pelvis than for the neck."),
        F("Hot spot and energy", "Lower at higher energy, because the PDD falls off less steeply and the midplane dose is closer to the maximum."),
        F("Hot spot and field size", "Lower for larger fields, because the PDD falls off less steeply."),
        F("Hot spot and number of fields", "It falls as more fields are used, because the entrance dose is spread over more surfaces. SRS and SBRT may use hundreds of beams."),
        F("Perpendicular pair of beams", "Lower superficial dose than a parallel-opposed pair, but a hot region where the beams cross near the surface and a low-dose region opposite. Wedges correct it."),
        F("Four-field box", "AP/PA plus two laterals. The dose is uniform where the beams overlap and the entrance dose is shared among four surfaces."),
        F("Beam weights", "The share of the isocenter dose that each beam delivers. Four equal fields deliver a quarter of the prescription each."),
        F("Energy for thin and thick sites", "Thin sites (brain, head and neck) allow a low energy. Thick sites (pelvis, abdomen) need a higher energy to limit hot spots."),
    ],
)

PROBLEMS = [
    PR("For a parallel-opposed pair of beams, the dose along the central axis is highest near:", "the entrance surfaces", ["the midplane", "the center of the target only", "the exit skin only"],
       "Each surface receives the maximum dose of its own beam plus the exit dose of the other, so the superficial dose exceeds the midplane dose.", lvl="Easy"),
    PR("Which change lowers the superficial hot spot of a parallel-opposed pair?", "A higher beam energy", ["A larger patient separation", "A lower beam energy", "A smaller field size"],
       "A higher energy makes the PDD fall off more slowly, so the midplane dose is closer to the maximum.", lvl="Easy"),
    PR("Compared with AP/PA beams across a thin neck, opposed lateral beams across a wide pelvis give:", "larger superficial hot spots", ["smaller superficial hot spots", "the same hot spots", "no hot spots"],
       "The separation is larger, so the midplane dose is lower relative to the entrance dose.", lvl="Easy"),
    PRN(STEM("A parallel-opposed pair of 6 MV beams, equal weights.", ["separation = 20 cm", f"PDD(1.5 cm) = 100%,   PDD(18.5 cm) = {p20a}%", f"PDD(10 cm) = {p20b}%"], "What is the [[hot spot ratio]]?"), h20, [(100 + p20b) / (2 * p20a), (100 + p20a) / p20b, 1.0], "{:.3f}",
        f"Ratio = (100 + {p20a}) / (2 × {p20b}) = {h20:.3f}. The midplane dose is the sum of two equal contributions, so the denominator has a factor of 2.", lvl="Moderate"),
    PRN(STEM("A four-field box prescribed to the isocenter.", ["dose at the isocenter = 240 cGy", "AP and PA weights = 30% each", "lateral weights = 20% each"], "What dose does each [[lateral field]] deliver to the isocenter?"), 48.0, [60.0, 72.0, 120.0], "{:.0f} cGy",
        "Each lateral field delivers 0.20 × 240 = 48 cGy. The AP and PA fields deliver 72 cGy each, and the four add to 240 cGy.", lvl="Moderate"),
    PR("Two perpendicular beams are used instead of a parallel-opposed pair. Compared with the pair, the plan has:", "a lower superficial dose, but a hot region where the beams cross and a low-dose region opposite", ["a higher superficial dose and a uniform target dose", "the same dose distribution", "a low-dose region where the beams cross and a hot region opposite"],
       "The beams cross near the surface on one side, where their doses add, and are far apart on the other. Wedges, heels together, correct the gradient.", lvl="Moderate"),
    PRM("Which changes lower the hot spot of a parallel-opposed pair?", ["A higher beam energy", "A larger field size", "Adding more fields"], ["A larger patient separation", "A lower beam energy"],
        "Anything that makes the PDD fall off more slowly lowers the ratio, and spreading the entrance dose over more surfaces lowers the superficial dose. A larger separation and a lower energy raise it.", lvl="Moderate"),
    PR("Why does a higher beam energy lower the hot spot of a parallel-opposed pair?", "The PDD falls off less steeply, so the midplane dose is closer to the maximum dose", ["The entrance dose increases", "The beams scatter less in the patient", "The exit dose is removed"],
       "The hot spot ratio compares the superficial dose with the midplane dose. A flatter PDD raises the midplane dose and leaves the superficial dose almost unchanged.", lvl="Moderate"),
    PRN(STEM("A parallel-opposed pair of 6 MV beams, equal weights.", ["separation = 40 cm", f"PDD(1.5 cm) = 100%,   PDD(38.5 cm) = {p40a}%", f"PDD(20 cm) = {p40b}%"], "What is the [[hot spot ratio]]?"), h40, [h20, (100 + p40a) / p40b, 1 / h40], "{:.2f}",
        f"Ratio = (100 + {p40a}) / (2 × {p40b}) = {h40:.2f}. The midplane dose is low at this depth, so the superficial dose is about {100 * (h40 - 1):.0f}% higher.", lvl="Challenging"),
    PR("A parallel-opposed pair is replaced by a four-field box that delivers the same dose at the isocenter. The superficial dose at each entrance surface:", "falls, because the entrance dose is shared among four surfaces", ["rises, because more beams enter", "stays the same", "becomes uniform and zero"],
       "Each beam delivers a smaller share of the isocenter dose, so each entrance surface receives less.", lvl="Challenging"),
    PR("The hot spot ratio of a parallel-opposed pair is 1.0 when:", "the PDD at the midplane equals the dose at the entrance, which only happens for a patient of negligible thickness", ["the field is larger than 20 × 20 cm", "the beam energy is 6 MV", "the beams are unweighted"],
       "The ratio is [ PDD(d<sub>max</sub>) + PDD(S − d<sub>max</sub>) ] / [ 2 PDD(S / 2) ]. It approaches 1 as S falls toward 2 d<sub>max</sub>, where the two entrance maxima meet in the middle.", lvl="Challenging"),
]

INLINE = {0: [1, 4], 1: [2, 7], 2: [5, 6]}

TERMS = ['parallel-opposed', 'hot spots']

TAKE = [
    [('For a parallel-opposed pair the axial dose is the sum of two PDDs. Each entrance surface is a hot spot: the ratio is [ PDD(d<sub>max</sub>) + PDD(S − d<sub>max</sub>) ] / [ 2 PDD(S / 2) ].', 'parallel-opposed')],
    [('The hot spot grows with separation and falls with higher energy, larger fields, and more fields.', 'hotspot-separation')],
    [('Perpendicular beams spare the surface but leave a hot corner and a low-dose corner. A four-field box shares the entrance dose among four surfaces.', 'beam-count')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Does each change raise or lower the superficial hot spot of a parallel-opposed pair?", ["Raises it", "Lowers it"],
         [("Thicker patient", 0), ("Higher beam energy", 1), ("Larger field size", 1), ("Lateral beams instead of AP/PA on the same patient", 0), ("Adding two more fields", 1), ("Lower beam energy", 0), ("Thinner patient", 1), ("Smaller field size", 0)],
         "The ratio rises when the midplane dose falls relative to the entrance dose: thicker patients, lower energies, smaller fields, and fewer beams. It falls with the opposite changes.", lvl="Moderate"),
    TYPED(STEM("A parallel-opposed pair of 6 MV beams, equal weights.", ["separation = 30 cm", f"PDD(1.5 cm) = 100%,   PDD(28.5 cm) = {p30a}%", f"PDD(15 cm) = {p30b}%"], "What is the [[hot spot ratio]]?"), h30, 0.01, "(ratio)",
          f"Ratio = (100 + {p30a}) / (2 × {p30b}) = {h30:.3f}.", lvl="Moderate"),
    FIGQ(STEM("Two parallel-opposed 6 MV beams, A and B, have equal weights and a separation of 24 cm. The graph shows the PDD of one beam.", [], "Tap the [[depth on this curve whose value is the dose that beam B adds]] at the depth of d<sub>max</sub> of beam A."),
         FS(x=dict(min=0, max=30, ticks=[0, 5, 10, 15, 20, 25, 30], label="Depth (cm)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Percent depth dose", fmt="pct"), series=[dict(pts=PTS(pd, 1.5, 30), color="plot-1")], xunit=" cm", xdec=1, xname="Depth", label="PDD of one 6 MV beam"),
         [(21.5, 23.5)], "The d<sub>max</sub> of beam A is 1.5 cm from A's surface, so the point is 24 − 1.5 = 22.5 cm from B's surface. Beam B contributes its PDD at 22.5 cm, which is read from this curve at that depth. This is the term PDD(S − d<sub>max</sub>) in the hot spot ratio.", lvl="Challenging", note="22.5 cm"),
]
INLINE = {0: [1, 4, _n0 + 3], 1: [2, 7, _n0 + 1], 2: [5, 6]}
