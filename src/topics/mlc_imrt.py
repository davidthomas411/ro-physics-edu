from blocks import *
import math, calc

TL = 0.015                                                         # leaf transmission, 1.5%
MU_C, RATIO = 250, 3.5
MU_I = MU_C * RATIO
leak_c, leak_i = MU_C * TL, MU_I * TL                              # dose to a point under the leaves, in cGy for 1 cGy/MU
dlg_ratio = lambda g, dlg: (g + dlg) / g                           # output relative to the nominal gap, for gaps g and DLG in mm
dlg_err = lambda g, dlg, d: d / (g + dlg)                          # fractional dose error from an error d in the DLG
sw_mu = lambda rate, g, v: rate * g / v                            # MU through a sliding gap g (cm) at leaf speed v (cm/s), dose rate in MU/s
sw_rate = lambda mu, g, v: mu * v / g                              # the highest dose rate (MU/s) that still delivers mu at speed v
rate_s = 600 / 60
r2 = lambda v: f"{math.floor(v * 100 + 0.5 + 1e-9) / 100:.2f}"      # round half up: 13.125 is written 13.13

TOPIC = dict(
    id="mlc-imrt", domain=3, sub="III.D", title="MLC effects in IMRT",
    ref=dict(aapm="TG-119, TG-218", khan="20", ford="9, 14"),
    guide=[
        H("Monitor units and leakage"),
        P("In an IMRT delivery most of each field is blocked by the leaves at any moment. To deliver a given dose to the target, many more monitor units are needed than in a conventional plan, commonly several times as many. The leaves transmit 1% to 1.5% of the beam through their thickness, and about twice that leaks between them. Every extra monitor unit sends that fraction to the whole shielded area, so the dose from leakage rises in proportion to the MU."),
        EX("Leakage with more MU", STEM("A conventional plan uses 250 MU. An IMRT plan for the same dose uses 3.5 times as many.", ["leaf transmission 1.5%", "output 1 cGy/MU in the reference geometry"], "Find the [[leakage dose]] to a point under the leaves in each plan."), ["Conventional: 250 × 0.015", "IMRT: 875 × 0.015"], f"{leak_c:.2f} cGy and {leak_i:.2f} cGy. The leakage dose is {leak_i / leak_c:.1f} times larger, in step with the MU."),
        P("The larger leakage raises the dose to the whole body, which is a concern for the risk of second cancers. Photons above about 10 MV also produce neutrons in the head of the linac, and with more MU per gray the neutron dose rises too, so IMRT is usually delivered at 6 MV or 10 MV."),
        H("Rounded leaf ends"),
        P("The ends of a leaf are rounded so that the penumbra is nearly the same wherever the leaf is. The rounded end transmits some radiation through its thin edge, even when two opposing leaves are nominally touching or are separated by a small gap. The radiation through the gap therefore behaves as if the gap were wider than its nominal size by an amount called the dosimetric leaf gap, DLG, typically 1 to 2 mm. The planning system uses a measured DLG when it models the leaves."),
        EQ("output through a gap g  ∝  g + DLG", "g = nominal gap,   DLG = dosimetric leaf gap, both in mm"),
        FIG("mlc_dlg", "Schematic with exaggerated proportions. Two opposing leaves with rounded ends, closed and with a gap g, and the relative fluence below them. The thin edges of the rounded ends transmit, so the fluence has the same area as an opening of width g + DLG (dashed). For closed leaves the equivalent opening has width DLG."),
        P("The DLG matters most for small gaps, which IMRT uses throughout. The same error in the DLG gives a much larger fractional error in the dose when the gap is small."),
        EX("An error in the leaf gap", STEM("The DLG used by the planning system is wrong by 0.5 mm. The true DLG is 1.5 mm.", ["a sliding gap of 5 mm", "a sliding gap of 20 mm"], "Find the [[fractional dose error]] for each gap."), ["Error = 0.5 / (g + DLG)", "g = 5 mm: 0.5 / 6.5", "g = 20 mm: 0.5 / 21.5"], f"{100 * dlg_err(5, 1.5, 0.5):.1f}% for the 5 mm gap and {100 * dlg_err(20, 1.5, 0.5):.1f}% for the 20 mm gap. Small gaps are about {dlg_err(5, 1.5, 0.5) / dlg_err(20, 1.5, 0.5):.1f} times more sensitive."),
        H("Tongue and groove"),
        P("Neighbouring leaves interlock along their sides with a tongue and a groove, so that radiation does not pass straight between them. The interlocking edge is thinner than the full leaf. When adjacent leaves are at different positions in a segment, a narrow strip along their boundary is shielded by part of the neighbouring leaf, and the strip can receive less dose than it should. Over a whole IMRT delivery this tongue-and-groove effect can leave lines of underdose along leaf boundaries. For a single field the underdose can be a few percent, and several fields from different angles, or leaf sequences that avoid it, average it out. Some planning systems model the effect, and many do not."),
        FIG("mlc_tg", "Schematic. End view of three neighbouring leaves: the tongue of one leaf fits the groove of the next, so the beam has no straight path through the joint. Beam's-eye view of two neighbouring leaves at different positions: the tongue of the extended leaf shields a narrow strip of the open field along the boundary."),
        H("Leaf speed and dose rate"),
        P("In sliding-window delivery, a point receives dose while it lies in the gap between two leaves that move together at speed v. A gap of width g crosses the point in a time g / v, so the monitor units delivered at that point are the dose rate times that time."),
        EQ("MU = R × g / v", "R = dose rate (MU/s),   g = gap width (cm),   v = leaf speed (cm/s)"),
        P("The leaves have a maximum speed, about 2.5 cm/s for many machines. When a part of the plan needs few MU at the point, the leaves would have to cross it faster than the limit allows. The dose rate is then lowered, which lengthens the delivery. Faster leaves, or a plan with a smoother fluence, remove the limit. VMAT has the same constraint, with the gantry speed as a further limit."),
        EX("Leaf speed against dose rate", STEM("A sliding gap of 1 cm. The maximum leaf speed is 2.5 cm/s.", ["dose rate = 600 MU/min = 10 MU/s", "the plan needs 2 MU at one point"], "Find the [[MU delivered]] at 2 cm/s, and the [[highest dose rate]] that can deliver 2 MU."), ["MU = 10 × 1 / 2", "Rate = MU × v / g = 2 × 2.5 / 1"], f"{sw_mu(rate_s, 1, 2):.0f} MU at 2 cm/s. Delivering only 2 MU at 10 MU/s would need a leaf speed of 10 × 1 / 2 = {rate_s * 1 / 2:.0f} cm/s, beyond the limit. The highest dose rate that works is {sw_rate(2, 1, 2.5):.0f} MU/s = {60 * sw_rate(2, 1, 2.5):.0f} MU/min."),
        P("The width of a leaf, projected to the isocenter, sets how closely the field edge follows a curved target. Narrow leaves of 2.5 to 5 mm suit small targets, and wider ones are acceptable for large targets, where the edge matters less."),
    ],
    cards=[
        F("MU in IMRT", "Most of each field is blocked at any moment, so IMRT commonly needs several times the MU of a conventional plan for the same dose."),
        F("Leakage in IMRT", "The leaves transmit 1% to 1.5% and about twice that leaks between them. More MU means proportionally more leakage dose to the whole body."),
        F("Neutrons in high-energy IMRT", "Photons above about 10 MV produce neutrons in the head, and more MU per gray raises the neutron dose, so IMRT is usually at 6 MV or 10 MV."),
        F("Rounded leaf ends", "They keep the penumbra nearly the same wherever the leaf is, and they transmit some radiation through the thin edge."),
        F("Dosimetric leaf gap", "DLG: the amount, typically 1 to 2 mm, by which the radiation through a small gap behaves as if the gap were wider than its nominal size."),
        F("Output through a small gap", "Proportional to g + DLG, with g the nominal gap."),
        F("DLG error", "A given DLG error produces a larger fractional dose error for a smaller gap: error = δ / (g + DLG)."),
        F("Tongue and groove", "The interlocking sides of neighbouring leaves. When adjacent leaves are at different positions, a strip along their boundary can be underdosed."),
        F("Reducing the tongue-and-groove effect", "Several fields from different angles, or leaf sequences that avoid it, average it out. Some planning systems model it and many do not."),
        F("Sliding-window MU", "MU = R × g / v: the dose rate times the time g / v that a gap of width g takes to pass a point at leaf speed v."),
        F("Maximum leaf speed", "About 2.5 cm/s for many machines. If a plan needs the leaves to go faster, the dose rate is lowered and the delivery takes longer."),
        F("Leaf width", "Narrow leaves of 2.5 to 5 mm let the edge follow a small curved target more closely. Wider leaves suit large targets."),
    ],
)

PROBLEMS = [
    PR("Compared with a conventional plan for the same dose, an IMRT plan usually needs:", "more monitor units", ["fewer monitor units", "the same monitor units", "no monitor units for the leaves"],
       "Most of each field is blocked by the leaves at any moment, so more MU are needed to deliver the dose.", lvl="Easy"),
    PR("Because IMRT uses more MU, the dose to the whole body from leakage through the leaves:", "increases", ["decreases", "does not change", "becomes zero"],
       "The leakage dose is proportional to the MU delivered.", lvl="Easy"),
    PR("Why is IMRT usually delivered at 6 MV or 10 MV rather than at higher energies?", "Higher energies produce neutrons, and the larger MU raise the neutron dose", ["Higher energies cannot be used with an MLC", "Higher energies have a higher surface dose", "Higher energies have a larger penumbra from the jaws"],
       "Photons above about 10 MV produce neutrons in the head of the linac, and more MU per gray raises the neutron dose.", lvl="Easy"),
    PRN(STEM("A conventional plan uses 250 MU, and an IMRT plan for the same dose uses 875 MU.", ["leaf transmission = 1.5%", "output = 1 cGy/MU"], "What is the [[leakage dose]] to a point under the leaves in the IMRT plan?"), leak_i, [leak_c, 875.0, 875 * TL * 2], lambda v: r2(v) + " cGy",
        f"Dose = 875 × 0.015 = {r2(leak_i)} cGy. The conventional plan would give {r2(leak_c)} cGy, and a transmission of 3% would give {r2(875 * TL * 2)} cGy.", lvl="Moderate"),
    PR("The dosimetric leaf gap exists because the:", "rounded leaf ends transmit radiation, so a small gap acts wider than its nominal size", ["leaves are too thick", "jaws are open behind the leaves", "beam energy changes with the gap"],
       "The radiation through the gap behaves as if the gap were larger by the DLG, typically 1 to 2 mm.", lvl="Moderate"),
    PRN(STEM("The output through a gap is proportional to g + DLG.", ["DLG = 1.5 mm", "nominal gap g = 5 mm"], "What is the [[output relative to the nominal gap]], (g + DLG) / g?"), dlg_ratio(5, 1.5), [1.5 / 5, 5 / 6.5, 1.0], "{:.2f}",
        f"(5 + 1.5) / 5 = {dlg_ratio(5, 1.5):.2f}. The gap acts 30% wider than its nominal size. The same DLG with a 20 mm gap gives only {dlg_ratio(20, 1.5):.3f}.", lvl="Moderate"),
    PR("A 0.5 mm error in the DLG used by the planning system gives:", "a larger fractional dose error for a small sliding gap than for a large one", ["the same fractional error for every gap", "no error, because the DLG cancels", "an error only at the field edge"],
       "The error is δ / (g + DLG), which is larger when the gap g is small.", lvl="Moderate"),
    PR("The tongue-and-groove effect in IMRT can cause:", "narrow lines of underdose along leaf boundaries", ["a uniform overdose of the whole field", "a change of the beam energy", "a rotation of the collimator"],
       "When adjacent leaves are at different positions, a strip along their boundary is partly shielded.", lvl="Moderate"),
    PRN(STEM("A sliding gap of 1 cm crosses a point at a leaf speed of 2 cm/s, at a dose rate of 600 MU/min.", [], "How many [[MU]] are delivered at the point?"), sw_mu(rate_s, 1, 2), [600 * 1 / 2, rate_s * 2 / 1, 600 / 60], "{:.0f} MU",
        f"The dose rate is 600 / 60 = 10 MU/s and the gap takes 1/2 = 0.5 s to pass, so MU = 10 × 0.5 = {sw_mu(rate_s, 1, 2):.0f}. Leaving the minutes unconverted gives {600 * 1 / 2:.0f}, and inverting the ratio gives {rate_s * 2 / 1:.0f}.", lvl="Challenging"),
    PRN(STEM("A sliding gap of 1 cm. The maximum leaf speed is 2.5 cm/s. A point needs 2 MU.", [], "What is the [[highest dose rate]] that can deliver 2 MU?"), 60 * sw_rate(2, 1, 2.5), [2 * 60.0, 60 * 2 / 2.5, 600.0], "{:.0f} MU/min",
        f"MU = R × g / v, so R = MU × v / g = 2 × 2.5 / 1 = {sw_rate(2, 1, 2.5):.0f} MU/s = {60 * sw_rate(2, 1, 2.5):.0f} MU/min. A higher dose rate would need the leaves to move faster than the limit.", lvl="Challenging"),
    PR("A part of an IMRT plan needs the leaves to move faster than their maximum speed. The usual consequence is that the:", "dose rate is lowered and the delivery takes longer", ["beam energy is increased", "MU are reduced to zero", "gantry is stopped permanently"],
       "Slowing the dose rate gives the leaves more time per MU, at the price of a longer delivery.", lvl="Challenging"),
    PR("Which statement about leaf width is correct?", "Narrow leaves let the field edge follow a small curved target more closely", ["Wide leaves give a smaller penumbra than narrow ones in every direction", "Leaf width does not affect the shape of the field edge", "Narrow leaves are needed for every large target"],
       "The width of a leaf projected to the isocenter sets how closely the stepped edge can follow a curve.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]}

TERMS = ['dosimetric leaf gap', 'tongue-and-groove', 'sliding-window', 'leakage']

TAKE = [
    [('IMRT needs several times the MU of a conventional plan, so the leakage through and between the leaves is several times larger too.', 'leakage-mu')],
    [('A small gap acts wider than its nominal size by the dosimetric leaf gap, so an error in the DLG matters most for the small gaps that IMRT uses.', 'dlg-error')],
    [('Adjacent leaves at different positions can leave a narrow strip of underdose. Delivering from several angles averages it out.', 'tongue-groove')],
    [('In sliding-window delivery MU = R × g / v. A maximum leaf speed limits the dose rate when a point needs few MU.', 'sliding-window-mu')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Is each effect a result of the rounded leaf end, the tongue-and-groove, or leakage?", ["Rounded leaf end", "Tongue and groove", "Leakage"],
         [("A small gap acts wider than its nominal size", 0), ("A narrow strip of underdose between leaves at different positions", 1), ("Dose under closed leaves that rises with the MU", 2), ("A penumbra that changes little with leaf position", 0), ("Interlocking leaf sides", 1), ("Transmission through the full leaf thickness", 2)],
         "The rounded end gives the dosimetric leaf gap and a nearly constant penumbra, the tongue and groove gives lines of underdose between leaves, and leakage is the radiation through and between the leaves.", lvl="Moderate"),
    TYPED(STEM("A sliding gap of 1 cm crosses a point at a leaf speed of 1.5 cm/s, at a dose rate of 600 MU/min.", [], "How many [[MU]] are delivered at the point?"), sw_mu(rate_s, 1, 1.5), 0.01, "MU",
          f"MU = 10 × 1 / 1.5 = {sw_mu(rate_s, 1, 1.5):.1f}.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the MU delivered at a point by a 1 cm sliding gap at 10 MU/s, against the leaf speed.", [], "Tap the [[leaf speed at which the point receives 4 MU]]."),
         FS(x=dict(min=0.5, max=5, ticks=[0.5, 1, 2, 3, 4, 5], label="Leaf speed (cm/s)"), y=dict(min=0, max=20, ticks=[0, 5, 10, 15, 20], label="MU delivered at the point"), series=[dict(pts=PTS(lambda v: sw_mu(10, 1, v), 0.5, 5), color="plot-1")], xunit=" cm/s", xdec=2, xname="Leaf speed", label="MU delivered against leaf speed"),
         [(2.5 - 0.35, 2.5 + 0.35)], "MU = R g / v, so v = R g / MU = 10 × 1 / 4 = 2.5 cm/s. The level 4 MU is not marked on the axis. 2.5 cm/s is about the maximum speed of many machines.", lvl="Challenging", note="2.5 cm/s"),
]
INLINE = {0: [1, 2, 3, 4], 1: [5, 6, 7], 2: [8, _n0 + 1], 3: [9, 10, _n0 + 2, _n0 + 3]}
