from blocks import *
import calc

F = calc.mayneord_F(100, 120, 10, 1.5); p2 = 67.0 * F
a1 = (101.5 / 110); a2 = (121.5 / 130)

TOPIC = dict(
    id="pdd", domain=3, sub="III.A", title="Percent depth dose",
    ref=dict(aapm="8.1", khan="9", ford="10"),
    guide=[
        H("Build-up, d<sub>max</sub>, and skin sparing"),
        P("A photon beam transfers energy to electrons, and those electrons deposit it downstream. Kerma is highest at the surface and falls with depth as the beam is attenuated. Absorbed dose rises over the first centimetres because electrons set in motion upstream travel forward, until charged-particle equilibrium is reached at about one electron range. That depth is d<sub>max</sub>. Beyond it the dose falls with the beam."),
        P("Higher energy sends the electrons farther forward, so d<sub>max</sub> is deeper and the dose in the first centimetre is lower, which means more skin sparing. The reduction at the skin itself is modest: field size and devices in the beam matter more. The surface dose is not zero: electrons scattered from the head and the air, and backscattered electrons, reach the skin."),
        TABLE(["Beam", "d<sub>max</sub> (10 × 10 cm field)"], [["Co-60", "0.5 cm"], ["4 MV", "1.0 cm"], ["6 MV", "1.5 cm"], ["10 MV", "2.5 cm"], ["15 MV", "3.0 cm"], ["18 MV", "3.0–3.5 cm"]]),
        P("d<sub>max</sub> also shifts a little with field size and machine."),

        H("Percent depth dose"),
        EQ("PDD(d, A, f, E) = 100 × D(d) / D(d<sub>max</sub>)"),
        P("PDD is the dose at depth d on the central axis as a percentage of the dose at d<sub>max</sub>. The field size A is defined at the surface, and f is the SSD. PDD depends on depth, energy, field size, and SSD."),
        FIG("pdd_curves", "Schematic PDD for three photon energies. Higher energy gives a deeper d<sub>max</sub>, a lower surface dose, and a higher PDD at depth."),
        TABLE(["Increase in", "PDD beyond d<sub>max</sub>", "Why"], [
            ["Depth", "Falls", "Attenuation and inverse square"],
            ["Energy", "Rises", "More penetrating beam"],
            ["Field size", "Rises", "More scatter reaches the point, and scatter is a larger share of the dose at depth than at d<sub>max</sub>"],
            ["SSD", "Rises", "The inverse-square fall-off between d<sub>max</sub> and d is smaller"]]),

        H("Inverse square and SSD"),
        P("Photon fluence from the source falls as 1/r². Between d<sub>max</sub> and depth d at SSD f, the inverse-square factor is [(f + d<sub>max</sub>)/(f + d)]². If only the SSD changes and the scatter is assumed unchanged, PDD changes by the ratio of these factors. This is the Mayneord F factor."),
        EQ("PDD(d, f<sub>2</sub>) = PDD(d, f<sub>1</sub>) × F", "F = [(f<sub>2</sub> + d<sub>max</sub>)/(f<sub>2</sub> + d)]<sup>2</sup> / [(f<sub>1</sub> + d<sub>max</sub>)/(f<sub>1</sub> + d)]<sup>2</sup>"),
        P("A larger SSD raises PDD but cuts the dose rate, so 100 cm, the usual SAD, is the common compromise. F ignores any change in scatter, so it suits modest SSD changes. Measured PDD data are preferred."),
        EX("Mayneord F factor", STEM("A 6 MV beam.", ["d<sub>max</sub> = 1.5 cm", "PDD = 67.0% at d = 10 cm, SSD 100 cm", "new SSD = 120 cm"], "Estimate the [[PDD]] at SSD 120 cm."),
           [f"SSD 100: (101.5/110)² = {a1:.4f}² = {a1**2:.4f}.", f"SSD 120: (121.5/130)² = {a2:.4f}² = {a2**2:.4f}.", f"F = {a2**2:.4f} / {a1**2:.4f} = {F:.3f}.", f"PDD = 67.0 × {F:.3f} = {p2:.1f}%."], f"About {p2:.1f}%."),
        EX("Field size at depth", STEM("", ["field at the surface = 10 × 10 cm", "SSD = 100 cm"], "Find the [[field size]] at a depth of 10 cm."),
           ["The beam diverges: 10 × (100 + 10)/100."], "11 × 11 cm."),

    ],
    cards=[
        C("Why does dose build up below the surface of a megavoltage photon beam?", "Photons set electrons in motion, and those electrons deposit their energy downstream. Dose rises until electron equilibrium at about one electron range (d<sub>max</sub>), then falls with the attenuated beam."),
        C("What is d<sub>max</sub>, and how does it change with energy?", "The depth of maximum dose on the central axis, at about one electron range. It deepens with energy: about 0.5 cm for Co-60, 1.5 cm for 6 MV, 2.5 cm for 10 MV, and 3–3.5 cm for 15–18 MV."),
        C("Which has the greater surface dose, 6 MV or 15 MV, for the same field? Why?", "6 MV. Higher-energy secondary electrons are more forward-directed, so d<sub>max</sub> is deeper and the surface dose lower (more skin sparing)."),
        C("Define percent depth dose.", "PDD = 100 × D(d)/D(d<sub>max</sub>) along the central axis, at fixed SSD and a field size defined at the surface."),
        C("Name what PDD depends on, and the direction of each effect beyond d<sub>max</sub>.", "Depth: falls. Energy: rises. Field size: rises. SSD: rises."),
        C("Why does PDD increase with field size?", "A larger field puts more scattering material around the point, and the scattered dose is a larger fraction of the dose at depth than at d<sub>max</sub>."),
        C("Why does PDD at a given depth increase with SSD?", "With the source farther away, the inverse-square fall-off between d<sub>max</sub> and the point is weaker."),
        C("State the Mayneord F factor and its assumption.", "F = [(f<sub>2</sub> + d<sub>max</sub>)/(f<sub>2</sub> + d)]² / [(f<sub>1</sub> + d<sub>max</sub>)/(f<sub>1</sub> + d)]², and PDD<sub>2</sub> = PDD<sub>1</sub> × F. It assumes the scatter is unchanged when only the SSD changes."),
        C("A 6 MV beam (d<sub>max</sub> = 1.5 cm) has PDD = 67.0% at 10 cm depth and SSD 100 cm. Estimate the PDD at SSD 120 cm.", f"About {p2:.1f}%.", w=[f"F = (121.5/130)² / (101.5/110)² = {a2**2:.4f} / {a1**2:.4f} = {F:.3f}.", f"67.0 × {F:.3f} = {p2:.1f}%."]),
        C("A field is 10 × 10 cm at the surface at SSD 100 cm. How large is it at 10 cm depth?", "11 × 11 cm.", w=["10 × (100 + 10)/100 = 11."]),
        C("Beyond d<sub>max</sub> at fixed SSD, which two effects make PDD fall with depth?", "Exponential attenuation of the primary beam and the inverse-square fall-off. Scatter partly offsets them."),
    ],
)

TERMS = ['charged-particle equilibrium', 'skin sparing', 'PDD', 'Mayneord F factor']

TAKE = [
    [('Dose builds up to d<sub>max</sub> because electrons travel downstream. Higher energy gives a deeper d<sub>max</sub> and a lower dose in the first centimetre (skin sparing). The skin dose itself depends more on field size and devices.', 'pdd-buildup')],
    [('PDD = 100 × D(d)/D(d<sub>max</sub>) on the central axis at fixed SSD. It rises with energy, field size, and SSD, and falls with depth.', 'pdd-factors')],
    [('Mayneord F is the ratio of the inverse-square factors at the two SSDs; it ignores scatter changes.', 'mayneord'), ('Field size is defined at the surface; at depth d it is A(f + d)/f.', 'field-divergence')],
]


# ---------------------------------------------------------------- practice questions
q_dose10 = 150 * 0.670
q_dmaxdose = 200 / 0.670
q_fld15 = 10 * (100 + 15) / 100
q_F140 = calc.mayneord_F(100, 140, 10, 1.5); q_p140 = 67.0 * q_F140
q_F80 = calc.mayneord_F(100, 80, 12, 2.5); q_p80 = 71.0 * q_F80
q_F80_nodmax = ((80 / 92) ** 2) / ((100 / 112) ** 2)
q_ratio = 70.0 / 67.0

PROBLEMS = [
    PR("Dose builds up over the first centimetres of a megavoltage photon beam because:", "electrons set in motion upstream travel forward and deposit their energy deeper, until charged-particle equilibrium is reached",
       ["the photon fluence increases with depth", "the inverse-square law raises the dose immediately below the surface", "low-energy photons are absorbed in the first centimetres"],
       "Photons transfer energy to electrons, and those electrons travel downstream before depositing it. The dose rises until the electrons entering a small volume balance those leaving it, at about one electron range. That depth is d<sub>max</sub>.", lvl="Easy"),
    PR("For a 6 MV photon beam and a 10 × 10 cm field, d<sub>max</sub> is about:", "1.5 cm", ["0.5 cm", "3.0 cm", "5.0 cm"],
       "About 1.5 cm for 6 MV. Co-60 is about 0.5 cm and 15 to 18 MV is about 3 cm, because higher energy sends the electrons farther forward.", lvl="Easy"),
    PR("Percent depth dose at depth d is the central-axis dose at d divided by:", "the central-axis dose at d<sub>max</sub>, times 100", ["the dose at the surface, times 100", "the free-space dose at that point, times 100", "the dose at the isocenter, times 100"],
       "PDD = 100 × D(d) / D(d<sub>max</sub>), at a fixed SSD with the field size defined at the surface. The dose in free space is the reference for TAR, not for PDD.", lvl="Easy"),
    PRN(STEM("A single 6 MV field.", ["dose at d<sub>max</sub> = 150 cGy", "PDD at 10 cm = 67.0%"], "What is the [[dose at 10 cm depth]]?"), q_dose10, [150 / 0.670, 150 * (1 - 0.670), 67.0], "{:.1f} cGy",
        f"D(10 cm) = PDD × D(d<sub>max</sub>) = 0.670 × 150 = {q_dose10:.1f} cGy. Dividing by the PDD gives {150 / 0.670:.1f} cGy, and using 1 − PDD gives {150 * 0.33:.1f} cGy.", lvl="Moderate",
        calc=CALC("cGy", [TILE("D", 150, "cGy", id="D"), TILE("PDD", 0.670, "", disp="0.670")], solution=["D", "×", "PDD"])),
    PRN(STEM("A single 6 MV field.", ["prescription = 200 cGy at 10 cm depth", "PDD at 10 cm = 67.0%"], "What is the [[dose at d<sub>max</sub>]]?"), q_dmaxdose, [200 * 0.670, 200.0, 200 / (1 - 0.670)], "{:.1f} cGy",
        f"D(10 cm) = PDD × D(d<sub>max</sub>), so D(d<sub>max</sub>) = 200 / 0.670 = {q_dmaxdose:.1f} cGy. Multiplying instead of dividing gives {200 * 0.670:.1f} cGy.", lvl="Moderate",
        calc=CALC("cGy", [TILE("D", 200, "cGy", id="D"), TILE("PDD", 0.670, "", disp="0.670")], solution=["D", "÷", "PDD"])),
    PR("Increasing the field size raises the PDD at depth mainly because:", "more scattered photons reach the point, and scatter is a larger share of the dose at depth than at d<sub>max</sub>",
       ["the inverse-square fall-off between d<sub>max</sub> and the point is smaller", "the beam is attenuated less in a larger field", "the primary beam has a higher energy"],
       "A larger field puts more tissue around the point to scatter photons into it. Scatter is a bigger part of the dose at depth than at d<sub>max</sub>, so the ratio rises. Attenuation of the primary beam and the inverse square do not change with field size.", lvl="Moderate"),
    PR("Why does the PDD at a given depth rise when the SSD is increased?", "The inverse-square fall-off between d<sub>max</sub> and the point of interest is smaller", ["The beam is attenuated less in tissue at a larger SSD", "The beam becomes harder as the distance from the source grows", "Scatter from the patient increases with distance"],
       "The distance from the source changes by a smaller fraction between d<sub>max</sub> and depth d when the SSD is larger, so less of the fall-off is due to the inverse square. Attenuation in tissue and scatter are about the same.", lvl="Moderate"),
    PRN(STEM("A point source gives a diverging beam.", ["field at the surface = 10 × 10 cm", "SSD = 100 cm"], "What is the side of the square [[field at 15 cm depth]]?"), q_fld15, [10 * 100 / 115, 10.0, 10 * 115 / 101.5], "{:.1f} cm",
        f"The field grows in proportion to the distance from the source: 10 × (100 + 15)/100 = {q_fld15:.1f} cm. Ignoring divergence gives 10.0 cm, inverting the ratio gives {10 * 100 / 115:.1f} cm, and measuring from d<sub>max</sub> instead of the surface gives {10 * 115 / 101.5:.1f} cm.", lvl="Easy",
        calc=CALC("cm", [TILE("A", 10, "cm"), TILE("f", 100, "cm"), TILE("d", 15, "cm")], ops=("+", "×", "÷", "(", ")"), solution=["A", "×", "(", "f", "+", "d", ")", "÷", "f"])),
    PRN(STEM("A 6 MV beam.", ["d<sub>max</sub> = 1.5 cm", "PDD = 67.0% at 10 cm depth, SSD 100 cm", "new SSD = 140 cm"], "Estimate the [[PDD]] at 10 cm depth for SSD 140 cm."), q_p140, [67.0 / q_F140, 67.0, 67.0 * q_F140 ** 2], "{:.1f}%",
        f"F = [(141.5/150)²] / [(101.5/110)²] = {(141.5/150)**2:.4f} / {(101.5/110)**2:.4f} = {q_F140:.3f}. PDD = 67.0 × {q_F140:.3f} = {q_p140:.1f}%. Dividing by F gives {67.0 / q_F140:.1f}%, leaving PDD unchanged gives 67.0%, and applying F twice gives {67.0 * q_F140 ** 2:.1f}%.", lvl="Moderate"),
    PR("A single beam must deliver 200 cGy at 10 cm depth at SSD 100 cm. Which beam gives the largest dose at d<sub>max</sub>?", "6 MV, 10 × 10 cm", ["6 MV, 30 × 30 cm", "18 MV, 10 × 10 cm", "18 MV, 30 × 30 cm"],
       "Dose at d<sub>max</sub> = prescription / PDD, so the beam with the lowest PDD at 10 cm needs the most dose at d<sub>max</sub>. PDD rises with both energy and field size, so the lowest is the lower energy with the smaller field.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 13], 1: [3, 4, 11, 12], 2: [7, 8, 9]}


# ---------------------------------------------------------------- practice questions that use a data table
import beamdata as bd
q_tpd9 = (bd.PDD[(8, 10)] + bd.PDD[(10, 10)]) / 2
q_trx12 = 180 / (bd.PDD[(12, 15)] / 100)
_f50 = (bd.PDD[(14, 10)] - 50) / (bd.PDD[(14, 10)] - bd.PDD[(16, 10)])                  # 50% lies between the 14 and 16 cm rows
q_td50 = 14 + _f50 * 2

PROBLEMS += [
    PRN(STEM("A 6 MV beam with a 10 × 10 cm field at the surface, SSD 100 cm. Use the table.", [], "Estimate the [[PDD at 9 cm depth]] by linear interpolation.", tables=[bd.table_pdd([5, 6, 8, 10, 12], [10])]),
        q_tpd9, [bd.PDD[(8, 10)], bd.PDD[(10, 10)], bd.PDD[(12, 10)]], "{:.1f}%",
        f"9 cm lies halfway between 8 and 10 cm, so PDD = ({bd.PDD[(8, 10)]:.1f} + {bd.PDD[(10, 10)]:.1f}) / 2 = {q_tpd9:.1f}%. Reading the 8 cm row gives {bd.PDD[(8, 10)]:.1f}%, the 10 cm row gives {bd.PDD[(10, 10)]:.1f}%, and the 12 cm row gives {bd.PDD[(12, 10)]:.1f}%.", lvl="Moderate",
        calc=CALC("", [TILE("P8", bd.PDD[(8, 10)], "", disp=f"{bd.PDD[(8, 10)]:.1f}"), TILE("P10", bd.PDD[(10, 10)], "", disp=f"{bd.PDD[(10, 10)]:.1f}"), TILE("2", 2)], ops=("+", "÷", "(", ")"), solution=["(", "P8", "+", "P10", ")", "÷", "2"])),
]


# ---------------------------------------------------------------- sorting question
PROBLEMS += [
    SORT("How does the PDD beyond d<sub>max</sub> respond when each of these increases?", ["PDD rises", "PDD falls", "PDD does not change"],
         [("Beam energy", 0), ("Field size", 0), ("SSD", 0), ("Depth", 1), ("Prescribed dose", 2), ("Monitor-unit setting", 2)],
         "A more energetic beam penetrates further, a larger field adds scatter, and a larger SSD weakens the inverse-square fall-off with depth, so all three raise the PDD. Going deeper lowers it. The PDD is a ratio of two doses in the same beam, so the prescribed dose and the number of monitor units cancel.", lvl="Moderate"),
]


# ---------------------------------------------------------------- tap-the-figure questions
_ext = lambda d: bd.pdd_model(d, 10) / 100
def _argmax(k): f = lambda d: _ext(d) * (1 - 0.9 * math.exp(-k * d)); return max((i * 0.003 for i in range(1, 1000)), key=f)
_lo, _hi = 0.8, 8.0
for _ in range(50):
    _k = (_lo + _hi) / 2
    if _argmax(_k) > bd.DMAX: _lo = _k
    else: _hi = _k
_g = lambda d: 1 - 0.9 * math.exp(-_k * d)
_pdd_curve = lambda d: 100 * _ext(d) * _g(d) / (_ext(bd.DMAX) * _g(bd.DMAX))
_d50 = next(i * 0.001 for i in range(1500, 30000) if _pdd_curve(i * 0.001) <= 50)
PROBLEMS += [
    FIGQ(STEM("A 6 MV beam, 10 × 10 cm field, SSD 100 cm. The graph shows the percent depth dose (illustrative).", [], "Tap the [[depth of d<sub>max</sub>]]."),
         FS(x=dict(min=0, max=6, ticks=[0, 1, 2, 3, 4, 5, 6], label="Depth (cm)"), y=dict(min=0, max=100, ticks=[0, 20, 40, 60, 80, 100], label="Percent depth dose", fmt="pct"), series=[dict(pts=PTS(_pdd_curve, 0, 6), color="plot-1")], xunit=" cm", xdec=1, xname="Depth", label="Percent depth dose against depth near the surface"),
         [(1.0, 2.0)], "d<sub>max</sub> is the depth of the maximum dose, where the curve peaks. For a 6 MV beam it is about 1.5 cm. Dose rises over the first 1.5 cm as the secondary electrons build up, and then falls slowly as the beam is attenuated.", lvl="Easy", note="about 1.5 cm"),
]
