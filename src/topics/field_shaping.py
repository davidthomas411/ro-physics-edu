from blocks import *
import math, calc

t5 = 1.2 * math.log2(20)                                      # thickness for 5% transmission, HVL 1.2 cm
t2 = 1.5 * math.log2(50)                                      # thickness for 2% transmission, HVL 1.5 cm
tr5 = 100 * 0.5 ** 5                                          # transmission through 5 HVL, percent
leaf, inter = 1.25, 2.5                                       # leaf transmission and interleaf leakage, percent (1% to 1.5%, and about double)

TOPIC = dict(
    id="field-shaping", domain=3, sub="III.A", title="Blocks and MLC field shaping",
    ref=dict(aapm="", khan="", ford="9"),
    guide=[
        H("Jaws and blocks"),
        P("The jaws of a linac make straight field edges, and each jaw moves independently. The field size is defined at the isocenter unless stated otherwise, so 10 × 10 cm means 10 × 10 cm at the isocenter. Many fields need shapes that are not rectangles, for example to keep the eyes out of a lateral whole-brain field."),
        P("A traditional way to shape a field is a poured block of Wood's metal, sold as Cerrobend, with a density of 9.7 g/cm³ and a melting point of 70 °C. The shape is cut from a Styrofoam block with a heated wire that diverges like the beam. The metal is poured around the shape and the block is mounted on a plastic tray in the head. Making blocks is labour-intensive and uses toxic metals, and a different block is needed for each beam. Poured blocks have largely been replaced by multileaf collimators."),
        P("A block attenuates exponentially, so each half-value layer halves the beam. Five half-value layers transmit about 3% of the beam, a common design target for shielding blocks. The tray that holds the block also attenuates the beam slightly, which is the tray factor of the monitor-unit calculation."),
        EX("Block thickness", STEM("A shielding block.", ["half-value layer = 1.2 cm (illustrative)", "transmission wanted = 5%"], "Find the [[thickness]] needed."), ["Number of HVLs = log<sub>2</sub>(1 / 0.05) = 4.32", "Thickness = 4.32 × 1.2 cm"], f"{t5:.1f} cm."),
        EX("Transmission through five HVLs", STEM("A block.", ["thickness = 5 half-value layers"], "Find the [[transmission]]."), ["Transmission = (½)<sup>5</sup>"], f"{tr5:.1f}%."),

        H("Multileaf collimators"),
        P("A multileaf collimator is a bank of thin tungsten leaves stacked side by side. Each leaf is moved by its own motor. A leaf is 5.5 to 7.5 cm thick in the direction of the beam to attenuate it, and its width projected to the isocenter is 0.5 to 1 cm. The leaf width sets how closely the edge can follow a curved shape, because the edge is stepped."),
        P("The leaves slide past each other, so there is a small air gap between them, and many leaves have a tongue and groove along their sides. Transmission through the full thickness of a leaf is 1% to 1.5%. The leakage between leaves is about twice that. The interlocking edges also smear the dose fall-off at the sides of a leaf, which is the tongue-and-groove effect. Some planning systems model it and many do not."),
        TABLE(["Feature", "Typical value"], [["Leaf thickness along the beam", "5.5 to 7.5 cm of tungsten"], ["Leaf width at the isocenter", "0.5 to 1 cm"], ["Transmission through a leaf", "1% to 1.5%"], ["Interleaf leakage", "About twice the leaf transmission"]]),
        EX("Leakage behind the leaves", STEM("An open field gives 200 cGy.", ["leaf transmission = 1.25%", "interleaf leakage = 2.5%"], "Find the [[dose behind a leaf and between two leaves]]."), ["Behind a leaf: 0.0125 × 200 cGy", "Between leaves: 0.025 × 200 cGy"], f"{200 * leaf / 100:.1f} cGy behind a leaf and {200 * inter / 100:.1f} cGy between leaves."),

        H("Edges and penumbra"),
        P("The edge of a collimator determines the penumbra. An ideal edge diverges exactly with the beam and gives a small penumbra, but an edge that is straight stops diverging with the beam as it moves away from the central axis. Some machines mount the leaves on a circular track so that the edge always matches the divergence. Most MLCs use rounded leaf ends instead. A rounded end does not give an ideal penumbra, but the penumbra is nearly independent of where the leaf is in the field."),
        P("The distance from the source to the collimator also matters, because the geometric penumbra is w = s [ (f + d) / SCD − 1 ]. If a collimator could be placed on the skin, the penumbra at the skin would be zero. The edge of a shaped field is placed outside the target by a margin that accounts for the penumbra."),
    ],
    cards=[
        F("Field size", "Defined at the isocenter unless stated otherwise: 10 × 10 cm means 10 × 10 cm at the isocenter."),
        F("Poured block", "Wood's metal (Cerrobend), density 9.7 g/cm³, melting point 70 °C. Shape cut from Styrofoam with a heated wire that diverges like the beam, then poured and mounted on a plastic tray."),
        F("Disadvantages of poured blocks", "Labour-intensive to make, toxic metals, and a different block for each beam, exchanged between beams. Largely replaced by MLCs."),
        F("Block transmission", "(½)<sup>n</sup> for n half-value layers. Five HVLs transmit about 3.1%."),
        F("MLC leaves", "Thin tungsten blades, 5.5 to 7.5 cm thick along the beam, 0.5 to 1 cm wide at the isocenter, each moved by its own motor."),
        F("Leaf width and the edge", "The leaf width sets how closely the edge can follow a curved shape. The edge is stepped."),
        F("Leaf transmission", "1% to 1.5% through the full thickness of a leaf."),
        F("Interleaf leakage", "Leakage through the small gaps between leaves, about twice the leaf transmission."),
        F("Tongue-and-groove effect", "The interlocking leaf edges smear the dose fall-off at the sides of a leaf. Some planning systems model it and many do not."),
        F("Rounded leaf ends", "They give a penumbra that is nearly independent of leaf position, although it is not ideal."),
        F("Penumbra with the collimator on the skin", "Zero: the geometric penumbra w = s [ (f + d) / SCD − 1 ] vanishes when SCD equals the source-to-skin distance."),
    ],
)

PROBLEMS = [
    PR("A field size of 10 × 10 cm refers to the dimensions:", "at the isocenter", ["at the surface of the collimator", "at the surface of the patient in every case", "at the level of the jaws"],
       "Field size is defined at the isocenter unless it is stated otherwise.", lvl="Easy"),
    PR("Poured blocks for field shaping are made from:", "a low-melting-point alloy such as Wood's metal (Cerrobend)", ["tungsten sheets", "lead-free plastic", "aluminium"],
       "Cerrobend has a density of 9.7 g/cm³ and melts at 70 °C, so it can be poured around a shape cut from Styrofoam.", lvl="Easy"),
    PR("Why have MLCs largely replaced poured blocks?", "They shape the field without making and exchanging a block for each beam", ["They transmit more of the beam", "They give a larger penumbra", "They are made of lighter metals"],
       "Blocks are labour-intensive, use toxic metals, and must be replaced between beams. An MLC reshapes the field under motor control.", lvl="Easy"),
    PRN(STEM("A shielding block.", ["thickness = 5 half-value layers"], "What [[percentage of the beam]] is transmitted?"), tr5, [5.0, 100 * 0.5 ** 6, 20.0], "{:.1f}%",
        f"Each HVL halves the beam: (½)<sup>5</sup> = 1/32 = {tr5:.1f}%.", lvl="Moderate"),
    PRN(STEM("A shielding block.", ["half-value layer = 1.2 cm (illustrative)", "transmission wanted = 5%"], "What [[thickness]] is needed?"), t5, [4.32, 6.0, 1.2 * math.log10(20)], "{:.2f} cm",
        f"The number of HVLs is log<sub>2</sub>(1/0.05) = 4.32, so the thickness is 4.32 × 1.2 = {t5:.2f} cm. Five HVLs would be 6.0 cm.", lvl="Moderate"),
    PR("The transmission through the full thickness of a tungsten MLC leaf is typically:", "1% to 1.5%", ["10% to 15%", "0.01% to 0.015%", "5% to 6%"],
       "Interleaf leakage is higher, about twice the leaf transmission.", lvl="Moderate"),
    PR("Compared with the transmission through a leaf, the leakage between two leaves is:", "about twice as large", ["about half as large", "the same", "ten times as large"],
       "The air gap between leaves lets more radiation through than the leaf itself.", lvl="Moderate"),
    PR("The main reason most MLCs use rounded leaf ends is that:", "the penumbra is nearly independent of the leaf position", ["the penumbra is zero", "they transmit less than flat ends", "they are easier to model with a planning system"],
       "Flat ends that do not diverge with the beam give a penumbra that depends on how far the leaf is from the axis. A rounded end keeps it nearly constant.", lvl="Moderate"),
    PRM("Which are disadvantages of poured blocks?", ["They are labour-intensive to make", "They contain toxic metals", "A different block must be made and exchanged for each beam"], ["They transmit most of the beam", "They cannot be mounted on a tray"],
        "Poured blocks shield well and are mounted on a plastic tray. Their problems are in making, handling, and exchanging them.", lvl="Moderate"),
    PRN(STEM("An open field gives 200 cGy.", ["interleaf leakage = 2.5%"], "What [[dose]] is delivered between two closed leaves?"), 200 * inter / 100, [200 * leaf / 100, 50.0, 0.5], "{:.1f} cGy",
        "Dose = 0.025 × 200 = 5.0 cGy. The leaf transmission of 1.25% would give 2.5 cGy behind a leaf.", lvl="Challenging"),
    PR("The tongue-and-groove effect refers to:", "a smearing of the dose fall-off at leaf edges caused by the interlocking sides of the leaves", ["the penumbra at the leaf tips", "the rounded shape of the leaf ends", "the thickness of the tungsten"],
       "It is separate from the leaf-end penumbra. Some planning systems model it and many do not.", lvl="Challenging"),
    PR("If a collimator could be placed on the skin, the geometric penumbra at the skin would be:", "zero", ["maximal", "equal to the source size", "equal to the field size"],
       "In w = s [ (f + d) / SCD − 1 ], the distance from the source to the plane equals SCD, so the bracket is zero.", lvl="Challenging"),
]

INLINE = {0: [1, 4], 1: [6, 7], 2: [8]}

TERMS = ['Cerrobend', 'multileaf collimator', 'tongue-and-groove effect']

TAKE = [
    [('A block transmits (½)<sup>n</sup> for n half-value layers: five HVLs transmit 3.1%. MLCs have largely replaced poured Cerrobend blocks.', 'hvl-blocks')],
    [('MLC leaf transmission is about 1%–1.5% and interleaf leakage about twice that. The interlocking edges smear the dose fall-off at leaf sides.', 'mlc-leakage')],
    [('A rounded leaf end gives a penumbra that is nearly independent of leaf position. A flat edge is sharp only where it matches the beam divergence.', 'mlc-penumbra')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Does each statement describe a poured block or an MLC?", ["Poured block", "MLC"],
         [("Made from Wood's metal", 0), ("Tungsten leaves moved by motors", 1), ("One is needed for each beam shape", 0), ("The shape can change during treatment", 1), ("Mounted on a plastic tray", 0), ("Has interleaf leakage and a tongue-and-groove effect", 1), ("Cut from Styrofoam with a heated wire", 0), ("Leaf width limits how closely the edge follows a curve", 1)],
         "Poured blocks are cast from a low-melting alloy and made for each beam. An MLC is a motorized bank of tungsten leaves, so its limits are leaf width, leakage between leaves, and the tongue-and-groove effect.", lvl="Moderate"),
    TYPED(STEM("A shielding block.", ["half-value layer = 1.5 cm (illustrative)", "transmission wanted = 2%"], "What [[thickness]] is needed?"), t2, 0.015, "cm",
          f"The number of HVLs is log<sub>2</sub>(1/0.02) = {math.log2(50):.2f}, so the thickness is {math.log2(50):.2f} × 1.5 = {t2:.2f} cm.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the fraction of the beam transmitted by a block against its thickness.", [], "Tap the [[thickness of five half-value layers]]."),
         FS(x=dict(min=0, max=8, ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8], label="Block thickness (cm)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Transmitted (%)", fmt="pct"), series=[dict(pts=PTS(lambda x: 100 * 0.5 ** (x / 1.2), 0, 8), color="plot-1")], xunit=" cm", xdec=1, xname="Thickness", label="Transmission through a block against thickness"),
         [(5.5, 6.5)], "The half-value layer is the thickness that halves the beam. The curve reaches 50% at 1.2 cm, so five half-value layers are 5 × 1.2 = 6.0 cm, where the transmission is 3.1%. The curve lies almost on the axis there and cannot be read, so the thickness is worked out from the half-value layer.", lvl="Challenging", note="6.0 cm"),
]
INLINE = {0: [1, 4, _n0 + 3], 1: [6, 7, _n0 + 1], 2: [8]}
