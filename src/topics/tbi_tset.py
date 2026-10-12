from blocks import *
import math

# ---------------------------------------------------------------- helpers. Distances in cm from the source, doses in cGy unless stated.
def inv_sq(o_ref, d_ref, d):
    """Dose per MU at distance d from the dose per MU at distance d_ref, by the inverse square law."""
    return o_ref * (d_ref / d) ** 2

def tmr_ill(d, mu=0.020, dmax=3.0):
    """Illustrative TMR of an 18 MV beam in the TBI geometry: exponential beyond d_max, rounded to 3 decimals as printed."""
    return round(math.exp(-mu * max(0.0, d - dmax)), 3)

def mu_field(dose, o_spd, tmr, oar=1.0):
    """Monitor units for each of two opposed fields of equal weight that together give `dose` at the midline."""
    return (dose / 2.0) / (o_spd * tmr * oar)

def lung_dose(per_fx, factor, n_fx, n_blocked, trans):
    """Total lung dose: per_fx × factor on each open fraction, and that times the block transmission on each blocked fraction."""
    return per_fx * factor * ((n_fx - n_blocked) + n_blocked * trans)

# ---------------------------------------------------------------- total body irradiation: field size, monitor units, dose rate, uniformity
DIAG = 40.0 * math.sqrt(2.0)                   # cm: diagonal of a 40 × 40 cm field at 100 cm
diag4 = DIAG * 4.0 / 100.0                     # m at 400 cm
O100 = 1.07                                    # cGy/MU at d_max, point 100 cm from the source, TBI collimator setting (illustrative)
SPD1, T1, D_FX = 400.0, 34.0, 200.0            # source to midline (cm), separation at the umbilicus (cm), dose per fraction (cGy)
o1 = inv_sq(O100, 100.0, SPD1)                 # cGy/MU at d_max with the point at 400 cm
tmr1 = tmr_ill(T1 / 2)
dpm1 = o1 * tmr1                               # cGy/MU at the midline, one field
mu1 = mu_field(D_FX, o1, tmr1)
R1 = 200.0                                     # machine rate, MU/min
rate1 = R1 * dpm1                              # cGy/min at the midline
time1 = mu1 / R1                               # min per field
SITES = [("Head", 16.0), ("Neck", 12.0), ("Chest with arms, water-equivalent", 32.0), ("Abdomen at the umbilicus", 34.0), ("Knees, legs together", 22.0)]
UROWS = [(n, s, tmr_ill(s / 2), 100.0 * tmr_ill(s / 2) / tmr1) for n, s in SITES]
U = {n: pct for n, _, _, pct in UROWS}
# lung blocks, worked example: AP/PA, 12 Gy in 6 fractions
LF1, LT1, NB1 = 1.10, 0.50, 4
lung1 = lung_dose(2.0, LF1, 6, NB1, LT1)       # Gy
lung1_open = lung_dose(2.0, LF1, 6, 0, LT1)

# ---------------------------------------------------------------- total skin electron therapy: dose per cycle from the six positions
POS = ["Anterior", "Right anterior oblique", "Left anterior oblique", "Right posterior oblique", "Left posterior oblique", "Posterior"]
CH = dict(zip(POS, [1.00, 0.90, 0.90, 0.0, 0.0, 0.0]))     # anterior chest: dose per cycle from each position / calibration-point dose of one dual field (illustrative)
B1 = sum(CH.values())
CYC = 2.0                                      # Gy at the skin per two-day cycle
dp1 = CYC / B1                                 # Gy per dual field at its calibration point
share_a = CH["Anterior"] / B1

TOPIC = dict(
    id="tbi-tset", domain=6, sub="VI.A", title="Total body and total skin irradiation",
    ref=dict(aapm="TG-29, TG-30", khan="", ford="23"),
    guide=[
        H("TBI purpose and techniques"),
        P("Total body irradiation (TBI), with chemotherapy, conditions a patient for a hematopoietic stem cell transplant. It kills malignant cells throughout the body, including sites that drugs reach poorly, and suppresses the immune system so that the donor graft is not rejected. Myeloablative regimens destroy the marrow, for example 12 Gy in 6 fractions twice a day over 3 days; nonmyeloablative regimens, for example 2 Gy in one fraction with fludarabine, give only enough to let the graft take."),
        P("The lung limits the dose: the risk of interstitial pneumonitis rises with the lung dose and with the dose rate. The midline dose rate is commonly 5 to 15 cGy/min (at most 20 cGy/min in many protocols), and the lung dose is often held to about 8 to 10 Gy. The ACR practice parameter asks for a dose within ±10% of the prescription along the body."),
        P(f"At an extended distance of about 3 to 5 m one field covers the whole patient: with the collimator open to 40 × 40 cm and turned 45°, the field diagonal spans {diag4:.2f} m at 4 m."),
        UL("<b>Anterior–posterior</b>: standing against a support frame, or lying on one side. The separation varies less along the body, and partial-transmission blocks shield the lungs.",
           "<b>Bilateral</b>: sitting or lying with the knees bent, treated from both sides. More comfortable, and the arms shield part of the lungs, but the separation varies more, so a compensator is needed at the head and neck and at the legs."),
        P("A beam spoiler, an acrylic screen about 1 cm thick within about 20 cm of the patient, adds electrons that raise the skin dose to about 90% of the maximum or more. Total marrow irradiation with helical tomotherapy or VMAT aims the dose at the marrow instead, sparing the lungs, the liver, and other organs."),

        H("TBI dosimetry and monitor units"),
        P("The output is measured with an ion chamber at d<sub>max</sub> in a large phantom at the treatment distance, behind the spoiler; the inverse square law from the output at 100 cm is a check, since scatter from the room and the spoiler can make the two differ. The dose is prescribed at a stated point, usually the midline at the level of the umbilicus."),
        P("Each of two opposed fields of equal weight gives half the dose at the midline, at a depth of half the separation t. The TMR does not depend on the source distance and applies directly; a PDD would have to be that of the treatment SSD, not one from tables at 100 cm."),
        EQ("O<sub>SPD</sub> ≈ O<sub>100</sub> × (100 / SPD)²",
           "MU per field = (D<sub>Rx</sub> / 2) / [O<sub>SPD</sub> × TMR(t/2) × OAR]",
           "O<sub>100</sub>: dose per MU at d<sub>max</sub> with that point 100 cm from the source, for the TBI collimator setting",
           "SPD: source to the prescription point (cm);   OAR = 1 on the central axis"),
        P("Points far from the axis, such as the head and the feet, take the off-axis ratio measured at the treatment distance. Each site's midline dose follows its own separation; for a bilateral technique without compensators (illustrative 18 MV TMR values, off-axis ratio 1):"),
        TABLE(["Site", "Separation t (cm)", "TMR(t/2)", "Midline dose (% of the umbilicus)"], [[n, f"{s:.0f}", f"{t:.3f}", f"{p:.0f}"] for n, s, t, p in UROWS]),
        P("A compensator in each field (a metal sheet in the beam, or bolus around the thin part) brings these sites within ±10%."),
        EX("Monitor units for a bilateral fraction", STEM("A bilateral TBI, prescribed at the midline at the umbilicus.",
                                                          [f"dose per fraction = {D_FX:.0f} cGy, two fields of equal weight", f"separation at the umbilicus = {T1:.0f} cm", f"O<sub>100</sub> = {O100:.2f} cGy/MU at d<sub>max</sub>, point 100 cm from the source", f"SPD = {SPD1:.0f} cm", f"TMR({T1 / 2:.0f} cm) = {tmr1:.3f} (illustrative 18 MV)"],
                                                          "Find the [[monitor units per field]]."),
           [f"Dose per field at the midline = {D_FX:.0f} / 2 = {D_FX / 2:.0f} cGy", f"O<sub>SPD</sub> = {O100:.2f} × (100 / {SPD1:.0f})² = {o1:.5f} cGy/MU", f"Dose per MU at the midline = {o1:.5f} × {tmr1:.3f} = {dpm1:.5f} cGy/MU", f"MU per field = {D_FX / 2:.0f} / {dpm1:.5f} = {mu1:.0f}"],
           f"{mu1:.0f} MU per field."),
        EX("Midline dose rate and beam-on time", STEM("A bilateral TBI field.", [f"dose per MU at the midline = {dpm1:.5f} cGy/MU", f"MU per field = {mu1:.0f}", f"machine rate = {R1:.0f} MU/min"], "Find the [[midline dose rate]] and the [[beam-on time]] of each field."),
           [f"Dose rate = {R1:.0f} MU/min × {dpm1:.5f} cGy/MU = {rate1:.1f} cGy/min", f"Beam-on time = {mu1:.0f} / {R1:.0f} = {time1:.1f} min"],
           f"{rate1:.1f} cGy/min, inside the usual 5 to 15 cGy/min, and {time1:.1f} min per field, about {2 * time1:.0f} min of beam for the fraction."),

        H("Total skin electron therapy"),
        P("Total skin electron therapy (TSET) treats mycosis fungoides, the most common cutaneous T-cell lymphoma, when it covers much of the skin. The aim is a uniform dose over the whole skin to a depth of a few millimetres, with little dose to the marrow. AAPM Report 23 (TG-30) describes beams of 4 to 10 MeV at the accelerator window, degraded by a scatter plate and the air to about 3 to 7 MeV at the patient."),
        P("In the Stanford six-dual-field technique the patient stands about 3 to 4 m from the source, close behind an acrylic scatter plate about 1 cm thick, in six positions 60° apart: anterior, posterior, and four obliques. Each position takes two fields, the gantry angled about 15° to 20° above and below the horizontal: their sum is uniform from head to foot, and their central axes, where the bremsstrahlung is most intense, point above the head and below the feet. The anterior and both posterior obliques are treated on one day, the other three on the next: a two-day cycle."),
        P("Each patch of skin on the trunk faces about three positions, so the skin dose of a cycle is a multiple of the dose that one dual field gives at its calibration point: the multiplication factor B of AAPM Report 23, measured for each set-up. A standard course gives 30 to 36 Gy at the skin over 8 to 10 weeks (36 Gy in 9 weeks at Stanford, 2 Gy per cycle, four days a week); a low-dose course, 12 Gy in 12 fractions over 3 weeks, is less toxic. The EORTC consensus limits the photon dose of a course, which reaches the whole body, to about 0.7 Gy."),
        EX("Skin dose from six dual fields", STEM("A point on the anterior chest in the six-dual-field technique. Each position gives a stated fraction of the calibration-point dose D<sub>p</sub> of one dual field (illustrative).",
                                                  [f"anterior = {CH['Anterior']:.2f}", f"right and left anterior obliques = {CH['Right anterior oblique']:.2f} each", "posterior and the two posterior obliques = 0", f"skin dose wanted per two-day cycle = {CYC:.1f} Gy"],
                                                  "Find the [[multiplication factor at the point]] and the [[dose D<sub>p</sub> per dual field]]."),
           [f"Sum over the six positions = {CH['Anterior']:.2f} + {CH['Right anterior oblique']:.2f} + {CH['Left anterior oblique']:.2f} = {B1:.2f}", f"D<sub>p</sub> = {CYC:.1f} / {B1:.2f} = {dp1:.3f} Gy", f"The anterior position gives {CH['Anterior']:.2f} / {B1:.2f} = {100 * share_a:.0f}% of the dose at the point"],
           f"B = {B1:.2f} at the point, and D<sub>p</sub> = {dp1:.3f} Gy per dual field per cycle."),

        H("Shielding, boosts, and in vivo dosimetry"),
        P("In TBI, partial-transmission blocks shield the lungs for some or all of the fractions, and the lung dose depends on the transmission at the lung midline, scatter from the unblocked tissue included. On the first fraction, diodes, TLD, OSLD, or MOSFETs at the entrance and the exit of several sites estimate each midline dose, and compensators are adjusted where a site falls outside ±10%."),
        EX("Lung dose under partial-transmission blocks", STEM("An anterior–posterior TBI of 12 Gy in 6 fractions, prescribed at the midline at the umbilicus.",
                                                              [f"lung midline dose without blocks = {LF1:.2f} × the prescription (illustrative)", f"effective block transmission at the lung midline = {LT1:.2f}", f"fractions with blocks = {NB1} of 6"],
                                                              "Find the [[total lung dose]]."),
           [f"Open fraction: 2.0 Gy × {LF1:.2f} = {2.0 * LF1:.2f} Gy", f"Blocked fraction: {2.0 * LF1:.2f} × {LT1:.2f} = {2.0 * LF1 * LT1:.2f} Gy", f"Total = {6 - NB1} × {2.0 * LF1:.2f} + {NB1} × {2.0 * LF1 * LT1:.2f} = {lung1:.1f} Gy"],
           f"{lung1:.1f} Gy, inside the usual 8 to 10 Gy, against {lung1_open:.1f} Gy without blocks."),
        P("In TSET, internal eye shields under the lids or external goggles protect the eyes, and lead shields the fingernails and toenails. Self-shielding and skin folds leave the soles of the feet, the perineum, the inner thighs, the top of the scalp, and the skin under the breasts and the chin under-dosed. TLD, OSLD, or radiochromic film on the skin in the first cycle measures these sites, and the under-dosed ones receive boosts with separate electron fields."),
    ],
    cards=[
        F("TBI before a stem cell transplant", "It kills malignant cells throughout the body, including sites that drugs reach poorly, and suppresses the immune system so that the graft is not rejected."),
        F("TBI regimens", "Myeloablative: 12 Gy in 6 fractions, twice a day over 3 days. Nonmyeloablative: 2 Gy in one fraction, with fludarabine."),
        F("Protecting the lung in TBI", "Interstitial pneumonitis limits the dose. The lung dose is often held to about 8 to 10 Gy and the midline dose rate to about 5 to 15 cGy/min, under 20 cGy/min in many protocols."),
        F("TBI treatment distance", f"About 3 to 5 m. With the collimator open to 40 × 40 cm and turned 45°, the field diagonal spans {diag4:.2f} m at 4 m.",
          w=[f"Diagonal at 100 cm = 40 × √2 = {DIAG:.1f} cm", f"At 400 cm: {DIAG:.1f} cm × 4 = {DIAG * 4:.0f} cm"]),
        F("Beam spoiler", "An acrylic screen about 1 cm thick close to the patient. Its electrons raise the skin dose to about 90% of the maximum or more."),
        F("Anterior–posterior and bilateral TBI", "AP/PA: standing or lying on one side, a more uniform dose, lung blocks. Bilateral: sitting or lying, more comfortable, the arms shield the lungs, compensators at the head, neck, and legs."),
        F("TBI monitor units for opposed fields", "MU per field = (D/2) / [O<sub>SPD</sub> × TMR(t/2) × OAR], prescribed at the midline at the umbilicus, with O<sub>SPD</sub> ≈ O<sub>100</sub> (100/SPD)²."),
        F("TMR in TBI calculations", "The TMR does not depend on the source distance, so it applies at 4 m. A PDD from tables at SSD 100 cm does not."),
        F("Thickness and dose uniformity in TBI", "Thinner sites (head, neck, legs) receive a higher midline dose. Compensators bring every site within ±10% of the prescription (ACR practice parameter)."),
        F("TSET indication and target", "Mycosis fungoides, a cutaneous T-cell lymphoma, over much of the skin. The target is the whole skin to a depth of a few millimetres."),
        F("TSET beam energy", "4 to 10 MeV at the accelerator window and about 3 to 7 MeV at the patient, after the scatter plate and the air (AAPM Report 23)."),
        F("Stanford six-dual-field technique", "Standing at 3 to 4 m, six positions 60° apart, two fields per position angled about 15° to 20° up and down, three positions a day in a two-day cycle."),
        F("TSET prescriptions", "30 to 36 Gy at the skin over 8 to 10 weeks (Stanford: 36 Gy in 9 weeks, 2 Gy per cycle). Low dose: 12 Gy in 12 fractions over 3 weeks."),
        F("TSET x-ray contamination", "Bremsstrahlung reaches the whole body. The EORTC consensus limits the photon dose of a course to about 0.7 Gy, and the angled dual fields point the x-ray-rich axes off the trunk."),
        F("TSET shields and boosts", "Shielded: the eyes and the nails. Boosted: the soles, perineum, inner thighs, scalp, and the skin under the breasts and the chin."),
    ],
)

# ---------------------------------------------------------------- practice questions
# inverse square to 400 cm, with the classic slips
q_is = inv_sq(O100, 100.0, 400.0); q_is_lin = O100 * 100.0 / 400.0; q_is_inv = O100 * (400.0 / 100.0) ** 2; q_is_dmax = O100 * (103.0 / 400.0) ** 2
# monitor units at SPD 420 cm, separation 30 cm
SPD2, T2 = 420.0, 30.0
o2 = inv_sq(O100, 100.0, SPD2); tmr2 = tmr_ill(T2 / 2); dpm2 = o2 * tmr2
q_mu = mu_field(D_FX, o2, tmr2); q_mu_nohalf = D_FX / dpm2; q_mu_lin = (D_FX / 2) / (O100 * 100.0 / SPD2 * tmr2); q_mu_notmr = (D_FX / 2) / o2
# dose rate at 300 MU/min
R2 = 300.0
q_rate = R2 * dpm2; q_rate_notmr = R2 * o2; q_rate_100 = R2 * O100; q_rate_half = R2 * dpm2 / 2
# lung dose, blocks for 3 of 6 fractions
LF2, LT2, NB2 = 1.12, 0.45, 3
q_lung = lung_dose(2.0, LF2, 6, NB2, LT2); q_lung_nof = lung_dose(2.0, 1.0, 6, NB2, LT2); q_lung_all = lung_dose(2.0, LF2, 6, 6, LT2); q_lung_open = lung_dose(2.0, LF2, 6, 0, LT2)
# effective transmission that gives 8 Gy with blocks in every fraction
q_T8 = 100.0 * 8.0 / (12.0 * LF1)
# compensator at the neck
r_neck = U["Neck"] / 100.0
q_comp = 1.0 / r_neck; q_comp_sub = 1.0 - (r_neck - 1.0); q_comp_sqrt = math.sqrt(1.0 / r_neck); q_comp_one = 2.0 / r_neck - 1.0
# in vivo at the neck: what lowering every MU by 22% would do to the umbilicus
q_low = 100.0 / 1.22
# TSET: photon dose of a course
XF, NCYC = 0.015, 18
q_x = NCYC * CYC * XF; q_x_one = CYC * XF; q_x_six = q_x * 6
# TSET: dose per cycle at a point on the right side of the chest, with D_p from the anterior chest
SIDE = dict(zip(POS, [0.30, 0.95, 0.0, 0.95, 0.0, 0.30]))
B_side = sum(SIDE.values()); q_side = B_side * dp1
# ranking: preparing TBI for a first patient
STEPS = ["Measure the output, TMR, and off-axis ratios at the treatment distance", "Measure the patient's separations at the umbilicus and other sites",
         "Calculate the monitor units and design the compensators", "Treat the first fraction with dosimeters at the entrance and the exit", "Compare the measured midline doses with the plan and adjust"]

PROBLEMS = [
    # ---- TBI purpose and techniques (1-5)
    PR(STEM("A patient with acute leukemia receives chemotherapy and TBI before an allogeneic stem cell transplant.", [], "Which [[role]] does the TBI have?"),
       "It kills malignant cells and suppresses the immune system so the graft takes", ["It sterilizes the donor marrow before the marrow is infused", "It stimulates the remaining marrow so that it recovers sooner", "It replaces chemotherapy in the sites that drugs reach well"],
       "TBI reaches every site, including those that drugs reach poorly, and suppresses the recipient's immune system so that the donor graft is not rejected. The donor cells are never irradiated, and radiation does not speed the recovery of the marrow.", lvl="Easy"),
    PR(STEM("TBI is delivered with the patient 3 to 5 m from the source.", [], "What is the [[main reason]] for the extended distance?"),
       "One field then covers the whole length of the patient", ["The photon energy at the patient is then lower", "The neutron dose to the patient is then removed", "The skin dose then rises without a spoiler"],
       f"The field grows in proportion to the distance: a 40 × 40 cm field turned 45° has a diagonal of {diag4:.2f} m at 4 m. The photon energy does not change with distance, and the skin dose stays in the build-up region unless a spoiler is used.", lvl="Easy"),
    PR(STEM("An acrylic screen about 1 cm thick is placed close to the patient during TBI.", [], "What does the [[screen]] achieve?"),
       "Its electrons raise the skin dose to about 90% of the maximum or more", ["It absorbs low-energy photons and so lowers the skin dose", "It flattens the beam profile at the head and the feet", "It lowers the dose rate at the midline of the patient"],
       "The beam spoiler adds secondary electrons that bring the skin out of the build-up region. It changes the dose at depth by only a small amount, so it neither flattens the profile nor lowers the midline dose rate.", lvl="Easy"),
    PR(STEM("To shorten treatment, a clinic considers raising the machine rate for TBI.", ["midline dose rate now = 10 cGy/min", "midline dose rate proposed = 30 cGy/min"], "Which [[risk]] rises most with the change?"),
       "Interstitial pneumonitis, because lung injury rises with the dose rate", ["Graft rejection, because the marrow dose falls with the dose rate", "Skin reaction, because the spoiler adds more electrons at high rates", "Underdosing of the legs, because the off-axis ratio falls"],
       "Lung injury rises with the lung dose and with the dose rate, so most protocols keep the midline dose rate near 5 to 15 cGy/min and below 20 cGy/min. The dose to the marrow and the electrons from the spoiler do not depend on the dose rate.", lvl="Moderate"),
    PRM("Which of these lower the risk of interstitial pneumonitis after TBI?",
        ["Partial-transmission lung blocks", "A lower midline dose rate"],
        ["A beam spoiler in front of the patient", "One fraction in place of six for the same total dose", "A higher machine rate in MU per minute"],
        "Lung injury rises with the lung dose and the dose rate and falls with fractionation. Blocks lower the lung dose, and a lower dose rate spares the lung. The spoiler changes only the skin dose, and one large fraction or a higher rate raises the risk.", lvl="Moderate"),

    # ---- TBI dosimetry and monitor units (6-10)
    PRN(STEM("A bilateral TBI, prescribed at the midline at the umbilicus.", [f"dose per fraction = {D_FX:.0f} cGy, two fields of equal weight", f"separation at the umbilicus = {T2:.0f} cm", f"O<sub>100</sub> = {O100:.2f} cGy/MU at d<sub>max</sub>, point 100 cm from the source", f"SPD = {SPD2:.0f} cm", f"TMR({T2 / 2:.0f} cm) = {tmr2:.3f}"], "How many [[monitor units per field]] are needed?"),
        q_mu, [q_mu_nohalf, q_mu_lin, q_mu_notmr], "{:.0f} MU",
        f"Dose per MU at the midline = {O100:.2f} × (100 / {SPD2:.0f})² × {tmr2:.3f} = {dpm2:.5f} cGy/MU, and each field gives {D_FX / 2:.0f} cGy: {D_FX / 2:.0f} / {dpm2:.5f} = {q_mu:.0f} MU. The full {D_FX:.0f} cGy from each field gives {q_mu_nohalf:.0f}, the distance ratio not squared gives {q_mu_lin:.0f}, and leaving out the TMR gives {q_mu_notmr:.0f}.", lvl="Moderate"),
    PRN(STEM("A TBI field is delivered at a set machine rate.", [f"dose per MU at the midline = {dpm2:.5f} cGy/MU", f"machine rate = {R2:.0f} MU/min"], "What is the [[dose rate at the midline]]?"),
        q_rate, [q_rate_notmr, q_rate_100, q_rate_half], "{:.1f} cGy/min",
        f"Dose rate = {R2:.0f} × {dpm2:.5f} = {q_rate:.1f} cGy/min, inside the 20 cGy/min limit of many protocols. The output at d<sub>max</sub> without the TMR gives {q_rate_notmr:.1f}, the output at 100 cm gives {q_rate_100:.0f}, and halving for the two fields gives {q_rate_half:.1f}; the fields are delivered one at a time.", lvl="Moderate"),
    PR(STEM("A TBI calculation needs the dose at the midline of a patient whose midline lies 400 cm from the source.", [], "Why is the [[TMR]] used rather than PDD tables measured at SSD 100 cm?"),
       "The TMR does not depend on the source distance, and the PDD does", ["The TMR already includes the inverse square law to the midline", "The PDD cannot be measured in a large water phantom", "The TMR already includes the effect of the beam spoiler"],
       "A TMR compares two doses at the same distance from the source, so it holds at 4 m. A PDD changes with the SSD through its inverse square term and would need a correction from 100 cm. The inverse square to the midline is applied separately, through the output.", lvl="Moderate"),
    PR(STEM("A bilateral TBI is planned without compensators.", [f"prescription point = midline at the umbilicus, separation {SITES[3][1]:.0f} cm", f"head separation = {SITES[0][1]:.0f} cm", f"knee separation, legs together = {SITES[4][1]:.0f} cm"], "How do the [[midline doses at the head and the knees]] compare with the dose at the umbilicus?"),
       "Both are higher, because the beams cross less tissue", ["Both are lower, because they lie farther off the axis", "Both are equal, because the distance is the same", "The head is higher and the knees are lower"],
       f"Each field reaches the midline through half the separation, so a thinner site has a larger TMR: about {U['Head']:.0f}% at the head and {U['Knees, legs together']:.0f}% at the knees with illustrative 18 MV values. Compensators bring them back within ±10%.", lvl="Moderate"),

    # ---- total skin electron therapy (11-14)
    PR(STEM("Total skin electron therapy gives a uniform dose to the entire skin surface.", [], "For which [[disease]] is it mainly used?"),
       "Mycosis fungoides, a cutaneous T-cell lymphoma", ["Basal cell carcinoma of the face and scalp", "Psoriasis of the trunk and the limbs", "Melanoma of the lower leg and foot"],
       "Mycosis fungoides is the most common cutaneous T-cell lymphoma, and when it covers much of the skin the whole surface is the target. Localized skin cancers are treated with local fields.", lvl="Easy"),
    PR(STEM("In the six-dual-field technique each position is treated with two fields, the gantry angled above and below the horizontal.", [], "What does the [[pair of angled fields]] achieve?"),
       "An even dose from head to foot, with the x-ray-rich axes off the trunk", ["A higher electron energy at the skin of the trunk", "Full coverage of the soles and the perineum", "A lower total dose to the eyes and the nails"],
       "One field alone is not uniform over the height of a patient, and the sum of the two is. The bremsstrahlung is most intense along each central axis, and the angled axes point above the head and below the feet. The soles and the perineum still need boosts, and the eyes and nails need shields.", lvl="Easy"),
    PRN(STEM("A TSET course is given in two-day cycles.", [f"skin dose per cycle = {CYC:.0f} Gy", f"number of cycles = {NCYC}", f"photon dose at the midline, all fields together = {100 * XF:.1f}% of the skin dose"], "What [[photon dose]] does the course give to the whole body?"),
        q_x, [q_x_one, q_x_six, q_x / 10], "{:.2f} Gy",
        f"Skin dose of the course = {NCYC} × {CYC:.0f} = {NCYC * CYC:.0f} Gy, and {100 * XF:.1f}% of it is {q_x:.2f} Gy, under the 0.7 Gy of the EORTC consensus. One cycle alone gives {q_x_one:.2f} Gy, and multiplying again by the six positions gives {q_x_six:.2f} Gy, though the percentage already covers every field.", lvl="Moderate"),

    # ---- shielding, boosts, and in vivo dosimetry (15-17)
    PRN(STEM("An anterior–posterior TBI of 12 Gy in 6 fractions, prescribed at the midline at the umbilicus.", [f"lung midline dose without blocks = {LF2:.2f} × the prescription", f"effective block transmission at the lung midline = {LT2:.2f}", f"fractions with blocks = {NB2} of 6"], "What is the [[total lung dose]]?"),
        q_lung, [q_lung_nof, q_lung_all, q_lung_open], "{:.1f} Gy",
        f"Open fractions: {6 - NB2} × 2.0 × {LF2:.2f} = {(6 - NB2) * 2.0 * LF2:.2f} Gy. Blocked fractions: {NB2} × 2.0 × {LF2:.2f} × {LT2:.2f} = {NB2 * 2.0 * LF2 * LT2:.3f} Gy. Total {q_lung:.1f} Gy. Leaving out the lung factor gives {q_lung_nof:.1f}, blocks in every fraction give {q_lung_all:.1f}, and no blocks give {q_lung_open:.1f}.", lvl="Challenging"),
    PRM("The six-dual-field technique leaves some regions of skin under-dosed. Which of these regions receive boosts?",
        ["The soles of the feet", "The perineum"],
        ["The anterior abdomen", "The upper back", "The outer thighs"],
        "The soles face the floor and the perineum lies between the thighs, so no position reaches them fully. The abdomen, the back, and the outer thighs each face at least one position squarely.", lvl="Easy"),

    # ---- practice set (18-22)
    PRN(STEM("A bilateral TBI without compensators gives the neck a midline dose above the dose at the umbilicus.", [f"neck midline dose = {U['Neck']:.1f}% of the umbilicus", "compensators = one in each lateral field, of equal transmission"], "What [[compensator transmission]] brings the neck to the dose at the umbilicus?"),
        q_comp, [q_comp_sub, q_comp_sqrt, q_comp_one], "{:.3f}",
        f"Both fields pass through a compensator, so the neck dose is multiplied by T: T = 1 / {r_neck:.3f} = {q_comp:.3f}. Subtracting the excess from 1 gives {q_comp_sub:.3f}, taking the square root as if the two compensators multiplied gives {q_comp_sqrt:.3f}, and compensating one field only would need {q_comp_one:.3f}.", lvl="Challenging"),
    PR(STEM("On the first fraction of a bilateral TBI, entrance and exit diodes give these midline estimates.", ["umbilicus = 100% of the prescription", "chest = 103%", "neck = 122%"], "What is the [[best response]]?"),
       "Increase the compensation at the neck and check the next fraction", ["Lower the monitor units of both fields until the neck reads 100%", "Remove the beam spoiler from the region of the neck", "Raise the machine rate so that the fraction ends sooner"],
       f"Only the neck is outside ±10%, so more compensation there brings it back without changing the rest. Lowering every monitor unit until the neck reads 100% would leave the umbilicus at 100 / 1.22 = {q_low:.0f}% of the prescription, and the spoiler only affects the skin.", lvl="Challenging"),
    PR(STEM("After the first TSET cycle, OSLDs on the skin read these doses as a percentage of the prescription.", ["chest = 98%", "back = 101%", "soles of the feet = 35%", "perineum = 50%"], "What is the [[best response]]?"),
       "Add boost fields for the soles and the perineum", ["Raise the monitor units of all twelve fields", "Lower the energy to raise the surface dose", "Shield the chest and the back for one cycle"],
       "The soles and the perineum are self-shielded in the standing positions, so they receive boosts with separate electron fields. Raising every field would overdose the rest of the skin, which is already near the prescription.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3, 4, 5], 1: [6, 7, 8, 9], 2: [10, 11, 12], 3: [13, 14]}

TERMS = ["myeloablative", "interstitial pneumonitis", "beam spoiler", "compensator", "total marrow irradiation", "scatter plate", "six-dual-field technique", "multiplication factor"]

TAKE = [
    ["TBI before a stem cell transplant: 12 Gy in 6 fractions twice a day (myeloablative) or 2 Gy in one fraction (nonmyeloablative).",
     "The lung limits the dose: about 8 to 10 Gy to the lung, 5 to 15 cGy/min at the midline, uniformity within ±10%.",
     "An extended distance of 3 to 5 m covers the patient; a 1 cm acrylic spoiler restores the skin dose."],
    ["Output measured at the treatment distance; the inverse square from 100 cm is the check.",
     "MU per field = (D/2) / [O<sub>SPD</sub> × TMR(t/2) × OAR], prescribed at the midline at the umbilicus.",
     "Thinner sites (head, neck, legs) receive more and need compensators."],
    ["TSET for mycosis fungoides: 4 to 10 MeV at the window, about 3 to 7 MeV at the patient, at 3 to 4 m.",
     "Six positions 60° apart, two fields each angled up and down, three positions a day in a two-day cycle.",
     "30 to 36 Gy over 8 to 10 weeks (12 Gy low dose); photon dose of the course under about 0.7 Gy."],
    ["TBI: partial-transmission lung blocks; entrance and exit dosimeters estimate the midline dose.",
     "TSET: shields for the eyes and the nails; boosts for the soles, perineum, inner thighs, scalp, and the skin under the breasts and the chin."],
]
