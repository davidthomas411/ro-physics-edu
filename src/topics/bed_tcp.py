from blocks import *
import math, calc

bed = lambda D, d, ab: D * (1 + d / ab)
eqd2 = lambda D, d, ab: D * (d + ab) / (2 + ab)
ALPHA, NCELL = 0.3, 1e7
tcp = lambda B: math.exp(-NCELL * math.exp(-ALPHA * B))
sf = lambda D, a, b: math.exp(-a * D - b * D * D)
b_a, b_b = bed(30, 3, 10), bed(32, 8, 10)
e_a, e_b = eqd2(32, 8, 10), eqd2(32, 8, 3)
e_p1, e_p2 = eqd2(30, 3, 3), eqd2(8, 8, 3)
ldr_mu = math.log(2) / 1.5                                                          # repair rate, per hour, for a repair half-time of 1.5 h
ldr_bed = lambda R, T, ab: R * T * (1 + 2 * R / (ldr_mu * ab) * (1 - (1 - math.exp(-ldr_mu * T)) / (ldr_mu * T)))     # BED in Gy for a dose rate R (Gy/h) over T hours
B90 = (math.log(NCELL) - math.log(-math.log(0.9))) / ALPHA          # BED at which the tumour control probability is 90%

TOPIC = dict(
    id="bed-tcp", domain=3, sub="III.C", title="Fractionation, BED, TCP, and NTCP",
    ref=dict(aapm="", khan="", ford="13"),
    guide=[
        H("The linear-quadratic model"),
        P("Two plans can have similar total doses and different effects, for example 300 cGy × 10 = 30 Gy and 8 Gy × 4 = 32 Gy. The dose per fraction changes the biological effect, so total doses cannot be compared or added directly. A biological model is needed."),
        P("After a single dose d, the fraction of cells that survive is described by the linear-quadratic model, SF = e<sup>−αd − βd²</sup>. It has a term linear in dose and a term quadratic in dose, and on a logarithmic axis the curve has a shoulder. The ratio α/β sets the shape. For fractionated treatment the surviving fractions of the fractions multiply, so the exponents add. For n fractions of dose d, SF = e<sup>−n d (α + βd)</sup> = e<sup>−α BED</sup>."),
        EQ("BED = D (1 + d / (α/β))", "D = total dose = n d,   d = dose per fraction"),
        P("Tumours and early-responding tissues usually have a high α/β, about 10 Gy, and late-responding tissues a low one, about 3 Gy. Some tumours, such as prostate cancer, are thought to have a low α/β. A regimen with a larger dose per fraction gains more BED in a tissue with a low α/β than in one with a high α/β."),
        EX("BED of two regimens", STEM("Two regimens for a tumour with α/β = 10 Gy.", ["30 Gy in 10 fractions (3 Gy each)", "32 Gy in 4 fractions (8 Gy each)"], "Find the [[BED]] of each."), ["BED = 30 × (1 + 3 / 10)", "BED = 32 × (1 + 8 / 10)"], f"{b_a:.1f} Gy and {b_b:.1f} Gy. The second regimen has the higher BED for the tumour, although its total dose is only 2 Gy larger."),

        H("Equivalent dose in 2 Gy fractions"),
        P("The equivalent dose in 2 Gy fractions, EQD2, is the total dose that would give the same effect if it were delivered in 2 Gy fractions. Setting the BED of the regimen equal to the BED of D<sub>2</sub> in 2 Gy fractions gives the formula. EQD2 puts regimens with different fractionation on one scale, so they can be compared and their doses added."),
        EQ("EQD2 = D (d + α/β) / (2 + α/β)"),
        EX("EQD2 depends on α/β", STEM("A regimen of 32 Gy in 4 fractions of 8 Gy.", [], "Find the [[EQD2]] for α/β = 10 Gy and for α/β = 3 Gy."), ["α/β = 10: 32 × (8 + 10) / (2 + 10)", "α/β = 3: 32 × (8 + 3) / (2 + 3)"], f"{e_a:.1f} Gy for a tumour (α/β = 10) and {e_b:.1f} Gy for a late-responding tissue (α/β = 3). The same plan is biologically much stronger in the late-responding tissue."),
        EX("Adding two courses", STEM("A patient with a late-responding tissue (α/β = 3 Gy) receives two courses to the same region.", ["30 Gy in 10 fractions of 3 Gy", "later, 8 Gy in 1 fraction"], "Find the [[total EQD2]]."), ["First course: 30 × (3 + 3) / (2 + 3)", "Second course: 8 × (8 + 3) / (2 + 3)"], f"{e_p1:.1f} + {e_p2:.1f} = {e_p1 + e_p2:.1f} Gy. Adding the physical doses, 38 Gy, would underestimate the effect."),

        H("Tumour control and normal tissue complications"),
        P("The model can be extended to a whole tumour. If a tumour starts with N cells, the mean number that survive is N × SF. The tumour control probability is the probability that none survives, which Poisson statistics gives as e<sup>−N × SF</sup>. It is a sigmoid function of dose: close to zero at low dose and close to one at high dose."),
        EQ("TCP = exp( − N e<sup>−α BED</sup> )"),
        P("Normal tissue complication probability models are built from clinical data and not from this statistical argument. The QUANTEC papers summarize them. The difference between the TCP and NTCP curves is the therapeutic window, the range of doses with high tumour control and low complications, and a plan aims to make it as large as possible. The TCP formula is a considerable simplification, with no host response and no oxygenation effects."),
        EX("TCP at two doses", STEM("A tumour.", ["N = 10<sup>7</sup> clonogenic cells", "α = 0.3 per Gy"], "Find the [[TCP]] for BED = 50 Gy and for BED = 60 Gy."), ["BED = 50: N × SF = 10<sup>7</sup> × e<sup>−15</sup> = 3.06, so TCP = e<sup>−3.06</sup>", "BED = 60: N × SF = 10<sup>7</sup> × e<sup>−18</sup> = 0.152, so TCP = e<sup>−0.152</sup>"], f"{tcp(50):.3f} and {tcp(60):.3f}. Ten gray of BED moves the TCP from about 5% to about 86%."),

        H("Continuous low dose rate irradiation"),
        P("In low-dose-rate brachytherapy the dose is delivered continuously over hours or days, and sublethal damage is repaired while the dose is being delivered. The repair has the rate μ = ln 2 / T<sub>rep</sub>, with T<sub>rep</sub> the repair half-time, about 1.5 h for many tissues. For a constant dose rate R delivered for a time T, the total dose is D = R T and the BED is"),
        EQ("BED = D [1 + (2R / (μ α/β)) (1 − (1 − e<sup>−μT</sup>) / (μT))]", "R = dose rate,   T = time,   μ = ln 2 / T<sub>rep</sub>"),
        P("The second term in the bracket falls as the dose rate falls, because more of the damage is repaired during the treatment, and the BED approaches the physical dose. The fall is larger for a low α/β, so a lower dose rate spares late-responding tissue more than the tumour. For a long treatment μT is large, and the bracket approaches 1 + 2R / (μ α/β)."),
        EX("BED of a low-dose-rate implant", STEM("An implant delivers 0.50 Gy/h for 72 h, a total of 36 Gy. Sublethal damage repairs with a half-time of 1.5 h, and the tumour has α/β = 10 Gy.", [], "Find the [[BED]]."),
           [f"μ = ln 2 / 1.5 = {ldr_mu:.3f} per hour, and μT = {ldr_mu * 72:.1f}", f"1 − (1 − e<sup>−μT</sup>) / (μT) = {1 - (1 - math.exp(-ldr_mu * 72)) / (ldr_mu * 72):.3f}", f"Bracket = 1 + (2 × 0.50 / ({ldr_mu:.3f} × 10)) × {1 - (1 - math.exp(-ldr_mu * 72)) / (ldr_mu * 72):.3f} = {ldr_bed(0.50, 72, 10) / 36:.3f}"],
           f"BED = 36 × {ldr_bed(0.50, 72, 10) / 36:.3f} = {ldr_bed(0.50, 72, 10):.1f} Gy, only {ldr_bed(0.50, 72, 10) - 36:.1f} Gy above the physical dose, because most of the damage is repaired during the 72 h."),
    ],
    cards=[
        F("Linear-quadratic model", "SF = e<sup>−αd − βd²</sup> for a single dose d: a linear term and a quadratic term, with a shoulder on a logarithmic plot."),
        F("Fractionated surviving fraction", "The surviving fractions multiply, so the exponents add: SF = e<sup>−n d (α + βd)</sup> = e<sup>−α BED</sup>."),
        F("BED", "BED = D (1 + d/(α/β)): the biologically effective dose, with D = n d the total dose and d the dose per fraction."),
        F("α/β values", "About 10 Gy for tumours and early-responding tissues, and about 3 Gy for late-responding tissues. Some tumours, such as prostate, are thought to have a low α/β."),
        F("Dose per fraction and α/β", "A larger dose per fraction gains more BED in a tissue with a low α/β than in one with a high α/β."),
        F("EQD2", "The total dose in 2 Gy fractions that gives the same effect: EQD2 = D (d + α/β) / (2 + α/β)."),
        F("Adding courses with different fractionation", "Convert each to EQD2 with the same α/β and add. Adding the physical doses is wrong."),
        F("TCP", "The probability that no clonogenic cell survives: TCP = exp(−N e<sup>−α BED</sup>). A sigmoid function of dose."),
        F("TCP model assumptions", "A simplification: no host response, no oxygenation effects."),
        F("NTCP", "Models built from clinical data, for example the QUANTEC papers, and not from statistical arguments."),
        F("Therapeutic window", "The range of doses between the TCP and NTCP curves with high tumour control and low complications."),
    ],
)

PROBLEMS = [
    PR("In the linear-quadratic model, the fraction of cells surviving a single dose d is:", "e<sup>−αd − βd²</sup>", ["e<sup>−αd</sup>", "1 − αd − βd²", "αd + βd²"],
       "There is a linear term and a quadratic term in the exponent. The quadratic term gives the shoulder of the curve.", lvl="Easy"),
    PR("For n fractions of equal dose, the total surviving fraction is the product of the surviving fractions, so in the exponent the terms:", "add, giving SF = e<sup>−n d (α + βd)</sup>", ["multiply, giving SF = e<sup>−(nd)²</sup>", "average, giving the SF of one fraction", "cancel"],
       "Multiplying exponentials adds their exponents.", lvl="Easy"),
    PR("EQD2 is:", "the total dose in 2 Gy fractions that gives the same effect", ["the dose per fraction that gives the same total dose", "the biologically effective dose of one fraction", "the dose to 2% of the volume"],
       "It puts regimens with different fractionation on one scale, so that they can be compared and added.", lvl="Easy"),
    PRN(STEM("A regimen for a tumour with α/β = 10 Gy.", ["30 Gy in 10 fractions of 3 Gy"], "What is the [[BED]]?"), b_a, [30.0, 30 * (1 + 10 / 3), 30 * 3 / 10], "{:.1f} Gy",
        f"BED = 30 × (1 + 3/10) = {b_a:.1f} Gy. The physical dose is 30 Gy, and inverting the ratio gives {30 * (1 + 10 / 3):.1f}.", lvl="Moderate"),
    PRN(STEM("A regimen for a tumour with α/β = 10 Gy.", ["32 Gy in 4 fractions of 8 Gy"], "What is the [[BED]]?"), b_b, [32.0, 32 * (1 + 10 / 8), e_a], "{:.1f} Gy",
        f"BED = 32 × (1 + 8/10) = {b_b:.1f} Gy. The EQD2 is {e_a:.1f} Gy, and inverting the ratio gives {32 * (1 + 10 / 8):.1f}.", lvl="Moderate"),
    PRN(STEM("A regimen of 32 Gy in 4 fractions of 8 Gy, for a tumour with α/β = 10 Gy.", [], "What is the [[EQD2]]?"), e_a, [32.0, b_b, e_b], "{:.1f} Gy",
        f"EQD2 = 32 × (8 + 10) / (2 + 10) = {e_a:.1f} Gy. The BED is {b_b:.1f} Gy, and with α/β = 3 the EQD2 would be {e_b:.1f} Gy.", lvl="Moderate"),
    PRN(STEM("A regimen of 32 Gy in 4 fractions of 8 Gy, for a late-responding tissue with α/β = 3 Gy.", [], "What is the [[EQD2]]?"), e_b, [32.0, e_a, bed(32, 8, 3)], "{:.1f} Gy",
        f"EQD2 = 32 × (8 + 3) / (2 + 3) = {e_b:.1f} Gy, much more than the tumour value of {e_a:.1f} Gy.", lvl="Moderate"),
    PR("The tumour BED (α/β = 10) is kept constant while the dose per fraction is raised and the number of fractions lowered. The BED to a late-responding tissue (α/β = 3 Gy) will:", "rise, because it depends more strongly on the dose per fraction", ["fall, because there are fewer fractions", "stay the same, because the tumour BED is constant", "become zero"],
       "A low α/β means the BED grows faster with dose per fraction, so late-responding tissues are the concern with large fractions.", lvl="Moderate"),
    PR("The tumour control probability is the probability that:", "no clonogenic cells survive", ["half of the cells survive", "the tumour shrinks by half", "the normal tissue is spared"],
       "Poisson statistics gives the probability of zero survivors from the mean number of survivors, N × SF.", lvl="Moderate"),
    PRN(STEM("A patient with a late-responding tissue (α/β = 3 Gy) receives two courses to the same region.", ["30 Gy in 10 fractions of 3 Gy", "8 Gy in 1 fraction"], "What is the [[total EQD2]]?"), e_p1 + e_p2, [38.0, e_p1 + 8, bed(30, 3, 3) + bed(8, 8, 3)], "{:.1f} Gy",
        f"EQD2 of the first course: 30 × (3 + 3)/5 = {e_p1:.1f} Gy. Second course: 8 × (8 + 3)/5 = {e_p2:.1f} Gy. Total {e_p1 + e_p2:.1f} Gy. The physical total is 38 Gy.", lvl="Challenging"),
    PRN(STEM("A tumour.", ["TCP = exp(−N e<sup>−α BED</sup>)", "N = 10<sup>7</sup> cells, α = 0.3 per Gy"], "What is the [[TCP]] at a BED of 60 Gy?"), tcp(60), [tcp(50), math.exp(-math.exp(-18)), 0.5], "{:.3f}",
        f"N × SF = 10<sup>7</sup> × e<sup>−18</sup> = {NCELL * math.exp(-18):.3f}, so TCP = e<sup>−{NCELL * math.exp(-18):.3f}</sup> = {tcp(60):.3f}. At a BED of 50 Gy the TCP is only {tcp(50):.3f}.", lvl="Challenging"),
    PR("Two courses with different fractionation cannot be combined by adding their physical doses because:", "the biological effect of a dose depends on the dose per fraction, so each course must first be converted to EQD2", ["the second course always has a different energy", "physical doses cannot be added in any case", "the dose rate differs"],
       "EQD2 puts both courses on the same footing, for a chosen α/β, so that they can be summed.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 4, 5], 1: [3, 6, 7], 2: [8, 9]}

TERMS = ['linear-quadratic model', 'EQD2', 'tumour control probability', 'therapeutic window']

TAKE = [
    [('SF = e<sup>−αd − βd²</sup> for one dose. For n fractions the exponents add, so SF = e<sup>−α BED</sup> with BED = D (1 + d/(α/β)).', 'lq-survival')],
    [('EQD2 = D (d + α/β) / (2 + α/β). A large dose per fraction raises the BED far more in a late-responding tissue (α/β about 3 Gy) than in a tumour (about 10 Gy).', 'bed-compare')],
    [('TCP = exp(−N e<sup>−α BED</sup>) is sigmoid in dose. The gap between the TCP and NTCP curves is the therapeutic window.', 'tcp-ntcp')],
    ['In continuous low-dose-rate irradiation repair acts during the treatment, so the BED is below the value for acute doses and approaches the physical dose as the dose rate falls, more so for a low α/β.'],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Does each tissue usually have a high or a low α/β?", ["High α/β, about 10 Gy", "Low α/β, about 3 Gy"],
         [("Most tumours", 0), ("Early-responding tissue such as mucosa", 0), ("Spinal cord, a late-responding tissue", 1), ("Lung fibrosis, a late effect", 1), ("Skin reaction in the first weeks", 0), ("Late bowel damage", 1)],
         "Tumours and early-responding tissues usually have a high α/β. Late-responding tissues have a low α/β, so they are more sensitive to the dose per fraction.", lvl="Moderate"),
    TYPED(STEM("A late-responding tissue with α/β = 3 Gy.", ["45 Gy in 15 fractions of 3 Gy"], "What is the [[BED]]?"), bed(45, 3, 3), 0.01, "Gy",
          f"BED = 45 × (1 + 3/3) = {bed(45, 3, 3):.1f} Gy.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the tumour control probability against BED for N = 10<sup>7</sup> cells and α = 0.3 per Gy.", [], "Tap the [[BED at which the TCP is 90%]]."),
         FS(x=dict(min=30, max=90, ticks=[30, 45, 60, 75, 90], label="BED (Gy)"), y=dict(min=0, max=1, ticks=[0, 0.25, 0.5, 0.75, 1], label="Tumour control probability"), series=[dict(pts=PTS(tcp, 30, 90), color="plot-1")], xunit=" Gy", xdec=1, xname="BED", label="Tumour control probability against BED"),
         [(B90 - 3.5, B90 + 3.5)], f"TCP = 0.9 means N e<sup>−α BED</sup> = −ln 0.9 = 0.105, so BED = (ln 10<sup>7</sup> − ln 0.105) / 0.3 = {B90:.1f} Gy. The level 0.9 is not marked on the axis.", lvl="Challenging", note=f"about {B90:.0f} Gy"),
]
INLINE = {0: [1, 2, 4, 5, _n0 + 2], 1: [3, 6, 7, _n0 + 1], 2: [8, 9, _n0 + 3]}


# ---------------------------------------------------------------- continuous low dose rate irradiation
_nl = len(PROBLEMS)
ldr_late, ldr_tum = ldr_bed(0.60, 60, 3), ldr_bed(0.60, 60, 10)
PROBLEMS += [
    PRN(STEM("A low-dose-rate implant delivers 0.60 Gy/h for 60 h, a total of 36 Gy. Sublethal damage repairs with a half-time of 1.5 h.", ["late-responding tissue with α/β = 3 Gy"], "What is the [[BED]] of the late-responding tissue?"), ldr_late, [36.0, ldr_tum, 36 * (1 + 1 * 0.6 / (ldr_mu * 3) * (1 - (1 - math.exp(-ldr_mu * 60)) / (ldr_mu * 60)))], "{:.1f} Gy",
        f"μ = ln 2 / 1.5 = {ldr_mu:.3f} per hour and μT = {ldr_mu * 60:.1f}. The bracket is 1 + (2 × 0.60 / ({ldr_mu:.3f} × 3)) × {1 - (1 - math.exp(-ldr_mu * 60)) / (ldr_mu * 60):.3f} = {ldr_late / 36:.3f}, so BED = 36 × {ldr_late / 36:.3f} = {ldr_late:.1f} Gy. Leaving out the repair term gives 36.0 Gy, using α/β = 10 Gy gives {ldr_tum:.1f} Gy, and leaving out the factor 2 gives {36 * (1 + 1 * 0.6 / (ldr_mu * 3) * (1 - (1 - math.exp(-ldr_mu * 60)) / (ldr_mu * 60))):.1f} Gy.", lvl="Challenging"),
    PR("The dose rate of a continuous irradiation is lowered, with the total dose unchanged. The BED:", "falls toward the physical dose, more in a late-responding tissue than in the tumour", ["rises, because the treatment takes longer", "stays the same, because the total dose is unchanged", "falls, more in the tumour than in a late-responding tissue"],
       "More of the sublethal damage is repaired during a longer treatment, so the BED falls toward the physical dose. The repair term is larger for a low α/β, so the fall is larger in late-responding tissue, which is why a low dose rate spares it.", lvl="Moderate"),
]
INLINE.setdefault(2, []).append(_nl + 2)
