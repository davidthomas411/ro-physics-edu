from blocks import *
import math


# ---------------------------------------------------------------- formulas quoted in the text
def eqd2(D, d, ab):
    """Equivalent dose in 2 Gy fractions of a total dose D given in fractions of d, for the ratio ab (all in Gy): D (d + ab) / (2 + ab)."""
    return D * (d + ab) / (2 + ab)

def hdr_rate(sk, lam, r):
    """Dose rate (cGy/h) at r cm on the transverse axis of a source of air kerma strength sk (U) and dose rate constant lam (cGy/h/U),
    in the TG-43 point-source form with g(r) and the anisotropy taken as 1: S_K Lambda (r0 / r)^2 with r0 = 1 cm."""
    return sk * lam / r ** 2

def left(t, t_half):
    """Fraction of the source strength left after a time t (same unit as the half-life)."""
    return 2 ** (-t / t_half)

def max_per_fraction(budget, n, ab):
    """Largest dose per fraction d that keeps n equal fractions within an EQD2 budget: n d (d + ab) / (2 + ab) = budget, the positive root."""
    c = budget * (2 + ab) / n
    return (-ab + math.sqrt(ab * ab + 4 * c)) / 2

def implant_time(D, rate0, t_half):
    """Time for a decaying source that starts at rate0 to deliver D: D = rate0 tau (1 - exp(-t / tau)), with the mean life tau = T1/2 / ln 2."""
    tau = t_half / math.log(2)
    return -tau * math.log(1 - D / (rate0 * tau))


# ---------------------------------------------------------------- constants quoted in the text
IR_T, I_T = 73.8, 59.4                    # half-lives in days, as in the sources chapter
U_MCI = 0.876 * 1.45                      # U per mCi of apparent activity for I-125: W/e in cGy/R times the exposure rate constant
AB_T, AB_O = 10.0, 3.0                    # alpha/beta in Gy: tumour, organs at risk
APEX, TG129_I = 85.0, 75.0                # COMS apex prescription; TG-129 value at 5 mm with the plaque materials (I-125)

# ---------------------------------------------------------------- worked examples
EB, EB_N, HDR_D, HDR_N, R_D = 45.0, 25, 7.0, 4, 4.0                    # external beam, HDR to the HR-CTV, rectum D2cc per HDR fraction
D_EB = EB / EB_N
eb_t, hdr_t = eqd2(EB, D_EB, AB_T), eqd2(HDR_D * HDR_N, HDR_D, AB_T)
eb_o, hdr_o = eqd2(EB, D_EB, AB_O), eqd2(R_D * HDR_N, R_D, AB_O)
tot_t, tot_o = eb_t + hdr_t, eb_o + hdr_o

SK0, LAM, R2, DOSE = 40000.0, 1.11, 2.0, 500.0                         # U, cGy/h/U, cm, cGy
rate2 = hdr_rate(SK0, LAM, R2)                                          # cGy/h
t0 = DOSE / rate2 * 3600                                                # s
f45 = left(45, IR_T); t45 = t0 / f45
trak0, trak45 = SK0 * t0 / 3600, SK0 * f45 * t45 / 3600                 # µGy at 1 m

NS, SKS, LIMIT = 80, 0.50, 50.0                                         # seeds, U per seed, mCi (illustrative licence limit)
sk_tot = NS * SKS; a_tot = sk_tot / U_MCI

skin10, skin5 = (10 / (10 + 3)) ** 2, (5 / (5 + 3)) ** 2                 # dose at 3 mm depth over the surface dose, source 10 mm and 5 mm above the skin

RATE_A = 0.75                                                           # Gy/h at the apex
tau_h = I_T * 24 / math.log(2)
tp_simple, tp_decay = APEX / RATE_A, implant_time(APEX, RATE_A, I_T * 24)

# ---------------------------------------------------------------- numbers of the questions
q_hdr, q_hdr_bed, q_hdr3 = eqd2(28, 7, AB_T), 28 * (1 + 7 / AB_T), eqd2(28, 7, AB_O)
RQ_D = 4.2                                                              # rectum D2cc per HDR fraction
r_eb = eqd2(EB, D_EB, AB_O); r_hdr = eqd2(RQ_D * HDR_N, RQ_D, AB_O)
r_tot, r_phys = r_eb + r_hdr, EB + RQ_D * HDR_N
r_ab10 = eqd2(EB, D_EB, AB_T) + eqd2(RQ_D * HDR_N, RQ_D, AB_T)
r_bed = EB * (1 + D_EB / AB_O) + RQ_D * HDR_N * (1 + RQ_D / AB_O)
RLIM = 75.0
r_left = RLIM - r_eb
d_max = max_per_fraction(r_left, HDR_N, AB_O)
SKQ, RQ, DQ = 36000.0, 1.5, 600.0                                       # U, cm, cGy
rate_q = hdr_rate(SKQ, LAM, RQ)
tq = DQ / rate_q * 3600
tq_noinv, tq_lin, tq_mul = DQ / (SKQ * LAM) * 3600, DQ / (SKQ * LAM / RQ) * 3600, DQ / (SKQ * LAM * RQ ** 2) * 3600
DWELLS = [(2.0, 100.0), (2.5, 150.0)]                                  # hand check: (distance in cm, dwell time in s)
pd_each = [hdr_rate(SK0, LAM, r) * t / 3600 for r, t in DWELLS]         # cGy from each dwell
pd_sum = sum(pd_each)
pd_noinv = sum(SK0 * LAM * t / 3600 for r, t in DWELLS)
pd_lin = sum(SK0 * LAM / r * t / 3600 for r, t in DWELLS)
NQ, SKQ_SEED = 90, 0.45
skq_tot = NQ * SKQ_SEED; a_q = skq_tot / U_MCI
RATE_Q = 0.65
tq_plaque, tq_plaque0 = implant_time(APEX, RATE_Q, I_T * 24), APEX / RATE_Q

TOPIC = dict(
    id="brachy-planning", domain=5, sub="V", title="Brachytherapy planning and applicators",
    ref=dict(aapm="TG-137, TG-129", khan="", ford="26"),
    guide=[
        H("Gynecologic brachytherapy and reference points"),
        P("Intracavitary applicators pair a tandem in the uterine canal with ovoids in the lateral fornices, a ring around the cervix, or a cylinder when the vagina is narrow or the disease extends down its wall. Needles, through a perineal template or a hybrid applicator, reach tumour beyond these sources, as in the parametrium."),
        P("The Manchester system specified the dose at point A, 2 cm superior to the vaginal fornix along the tandem and 2 cm lateral to it; definitions differ in how the fornix level is marked. It lay where the uterine vessels cross the ureter, whose tolerance limited the dose. Point B, at the same level 5 cm from the midline, marks the pelvic sidewall."),
        P("ICRU Report 38 added organ points on orthogonal radiographs. On the lateral film the bladder point is the posterior surface of a Foley balloon holding 7 cm³ of contrast, pulled down to the urethra, and the rectal point is 5 mm behind the posterior vaginal wall, level with the lower end of the tandem sources. It also defines the total reference air kerma (TRAK): air kerma strength × time, summed over all sources or dwell positions, as air kerma at 1 m."),
        P("These points are fixed to the applicator, not the tumour: point A can lie inside a large tumour or outside a small one, in a steep gradient, and an organ point can miss the hottest part of the wall. Image-based planning (GEC-ESTRO, ICRU Report 89) contours on MR or CT. The high-risk CTV, the cervix with any tumour left at brachytherapy, is reported as D<sub>90</sub>, the dose received by at least 90% of it, and each organ as D<sub>2cc</sub>, the minimum dose in its most exposed 2 cm³. ICRU 89 keeps point A and TRAK in the minimum report."),
        EQ("EQD2 = D (d + α/β) / (2 + α/β),   α/β = 10 Gy for the tumour and 3 Gy for the organs"),
        P("Summing D<sub>2cc</sub> over fractions assumes the same 2 cm³ is the hottest each time, which overestimates the organ dose."),
        TABLE(["Total EQD2", "ABS", "EMBRACE II planning aim"], [
            ["High-risk CTV D<sub>90</sub>", "80 to 90 Gy (at least 85 Gy for a tumour over 4 cm or a poor response)", "90 to 95 Gy"],
            ["Bladder D<sub>2cc</sub>", "At most about 90 Gy", "Below 80 Gy"],
            ["Rectum D<sub>2cc</sub>", "At most 70 to 75 Gy", "Below 65 Gy"],
            ["Sigmoid D<sub>2cc</sub>", "At most 70 to 75 Gy", "Below 70 Gy"]]),
        EX("EQD2 of external beam and HDR", STEM("A cervical cancer receives external beam therapy and then HDR brachytherapy. The rectum is taken to receive the full external beam dose.",
                                                 ["external beam = 45 Gy in 25 fractions of 1.8 Gy", "HDR = 7 Gy × 4 to the high-risk CTV D<sub>90</sub>", "rectum D<sub>2cc</sub> per HDR fraction = 4.0 Gy",
                                                  "α/β = 10 Gy for the tumour, 3 Gy for the rectum"], "Find the [[total EQD2]] of the high-risk CTV and of the rectum."),
           [f"Tumour, external beam: 45 × (1.8 + 10) / (2 + 10) = {eb_t:.2f} Gy", f"Tumour, HDR: 28 × (7 + 10) / (2 + 10) = {hdr_t:.2f} Gy",
            f"Rectum, external beam: 45 × (1.8 + 3) / (2 + 3) = {eb_o:.2f} Gy", f"Rectum, HDR: 16 × (4.0 + 3) / (2 + 3) = {hdr_o:.2f} Gy"],
           f"{tot_t:.1f} Gy for the high-risk CTV, inside 80 to 90 Gy, and {tot_o:.1f} Gy for the rectum, below the ABS limit of 70 to 75 Gy."),

        H("HDR dwell times and optimization"),
        P("An HDR afterloader drives one Ir-192 source along each applicator channel and stops it at dwell positions a set step apart, commonly 2.5 or 5 mm. The dwell time at each position sets the dose distribution: the dose at a point is the sum of dose rate × time over the positions."),
        EQ("D = Σ<sub>i</sub> Ḋ<sub>i</sub> t<sub>i</sub>", "Ḋ<sub>i</sub> ≈ S<sub>K</sub> Λ (r₀ / r<sub>i</sub>)²,   r₀ = 1 cm,   r<sub>i</sub> = distance from dwell position i",
           "TG-43 point-source form with g(r) and the anisotropy set to 1: close on the transverse axis beyond about 1 cm"),
        P("Geometric optimization sets each dwell time from the positions alone, longer where neighbours add less dose, as at catheter ends. Graphical optimization moves isodose lines by hand, and inverse planning finds the times that best meet dose–volume objectives for the target and organs. The prescription goes to a point (point A, or 5 mm from the surface of a vaginal cylinder) or to an isodose around the target, and the plan is normalized to it."),
        P("A second calculation checks each plan: the time and TRAK against earlier plans with the same applicator, and a reference point dose. As the source decays (T<sub>1/2</sub> = 73.8 d) the times for the same dose grow as 2<sup>t/T<sub>1/2</sub></sup>, and the TRAK, strength times time, stays the same."),
        EX("Dwell time and source decay", STEM("One dwell position of an Ir-192 HDR source treats a point on its transverse axis. Use the point-source form with g(r) and the anisotropy taken as 1.",
                                               ["S<sub>K</sub> = 40,000 U", "Λ = 1.11 cGy h<sup>−1</sup> U<sup>−1</sup>", "distance = 2.0 cm", "dose at the point = 5.0 Gy", "T<sub>1/2</sub> = 73.8 d"],
                                               "Find the [[dwell time]] now and for the same dose 45 days later."),
           [f"Ḋ = S<sub>K</sub> Λ (1 cm / r)² = 40,000 × 1.11 × 0.25 = {rate2:,.0f} cGy/h = {rate2 / 3600:.3f} cGy/s",
            f"t = 500 cGy / {rate2 / 3600:.3f} cGy/s = {t0:.1f} s",
            f"After 45 d the strength is ½<sup>45/73.8</sup> = {f45:.4f} of its value, so t = {t0:.1f} / {f45:.4f} = {t45:.1f} s",
            f"TRAK = S<sub>K</sub> t = 40,000 U × {t0 / 3600:.5f} h = {trak0:,.0f} µGy at 1 m, and the same after the decay"],
           f"{t0:.1f} s now and {t45:.1f} s after 45 days, with the same TRAK."),

        H("Permanent seed implants"),
        P("Permanent prostate implants place I-125, Pd-103, or Cs-131 seeds through needles guided by ultrasound and a template. Common prescriptions for an implant alone, to full decay, are 145 Gy (I-125), 125 Gy (Pd-103), and 115 Gy (Cs-131), and a boost after external beam uses less. The dose is the sum of the point-source doses of all seeds, with the anisotropy factor, since their orientations are unknown."),
        P("The plan is made before the implant from an ultrasound volume study, or in the operating room. Peripheral loading puts most seeds near the edge of the gland and few at the centre, sparing the urethra, which runs through the centre. The total strength needed grows with the gland volume, and weaker seeds mean more seeds and needles. TG-137 names D<sub>90</sub>, V<sub>100</sub>, and V<sub>150</sub> as primary parameters for the prostate, D<sub>10</sub> for the urethra, and D<sub>2cc</sub> for the rectum."),
        TABLE(["Quantity", "Meaning", "Usual goal"], [
            ["Prostate D<sub>90</sub>", "Dose received by at least 90% of the prostate", "At least the prescription in the plan; at least 90% of it after the implant"],
            ["Prostate V<sub>100</sub>", "Fraction of the prostate receiving the prescription", "At least 95% in the plan; at least 90% after the implant"],
            ["Prostate V<sub>150</sub>", "Fraction receiving 1.5 times the prescription", "At most about 50 to 65%"],
            ["Urethra D<sub>10</sub>, D<sub>30</sub>", "Dose to its most exposed 10% and 30%", "Below 150% and 130% of the prescription"]]),
        P("The postimplant CT is taken about 30 days after an I-125 implant, sooner after the shorter-lived Pd-103 or Cs-131, because needle trauma causes edema that resolves over weeks (a half-time of about 9 days in one serial CT study). A scan on the day of the implant shows the seeds spread apart and underestimates D<sub>90</sub>. Loose seeds can migrate, mostly to the lungs, and their dose is lost to the prostate; stranded seeds migrate less."),
        EX("Total strength of a seed implant", STEM("An I-125 prostate implant. The licence of the department allows it to hold at most 50 mCi of I-125 at one time (an illustrative limit).",
                                                    ["seeds = 80", "S<sub>K</sub> per seed on the implant date = 0.50 U", "1 mCi of apparent activity = 0.876 × 1.45 = 1.27 U for I-125"],
                                                    "Find the [[total air kerma strength]] and the apparent activity, and compare them with the limit."),
           [f"Total S<sub>K</sub> = 80 × 0.50 U = {sk_tot:.1f} U", f"Apparent activity = {sk_tot:.1f} U / {U_MCI:.3f} U per mCi = {a_tot:.1f} mCi"],
           f"{sk_tot:.0f} U, or {a_tot:.1f} mCi, below the 50 mCi limit. Seeds for a second implant of the same size, held at the same time, would raise the total to {2 * a_tot:.1f} mCi, above it."),

        H("Eye plaques and skin applicators"),
        P("An episcleral plaque treats a choroidal melanoma from outside the eye: seeds, usually I-125, in a Silastic carrier inside a gold-alloy shell sutured to the sclera. The shell and its lip collimate the dose and shield the orbit, and a notch fits the plaque around the optic nerve. The Collaborative Ocular Melanoma Study (COMS) prescribed 85 Gy to the tumour apex, or to 5 mm for a thinner tumour, and the ABS suggests 0.60 to 1.05 Gy/h at the apex, so 3 to 7 days. With the gold and Silastic included, 85 Gy calculated in water at 5 mm is about 75 Gy (TG-129)."),
        P("Skin brachytherapy uses an Ir-192 HDR source in a Leipzig-type applicator, a shielded cup a few centimetres across holding the source above the skin, or in a flap or mould for larger or curved surfaces; a flap holds catheters about 5 mm from the skin. The dose falls steeply with depth, so the surface receives more than the prescription depth. The ABS working group gives 3 mm for a thin lesion, with 40 Gy in 8 fractions or 42 Gy in 6 for surface applicators."),
        EQ("D(z) / D(0) ≈ [h / (h + z)]²   (one dwell position, inverse square alone; h = source height above the skin, z = depth)",
           f"at z = 3 mm: {100 * skin10:.0f}% of the surface dose for h = 10 mm, {100 * skin5:.0f}% for h = 5 mm"),
        EX("Treatment time of an eye plaque", STEM("An I-125 COMS plaque treats a choroidal melanoma.",
                                                   ["prescription = 85 Gy to the tumour apex", "initial dose rate at the apex = 0.75 Gy/h", "T<sub>1/2</sub> = 59.4 d"],
                                                   "Find the [[treatment time]], first at a constant dose rate and then with the decay during the implant."),
           [f"Constant rate: t = 85 / 0.75 = {tp_simple:.1f} h = {tp_simple / 24:.2f} d",
            f"Mean life τ = 59.4 × 24 / ln 2 = {tau_h:,.0f} h, and the dose by time t is Ḋ₀ τ (1 − e<sup>−t/τ</sup>)",
            f"t = −τ ln(1 − 85 / (0.75 × {tau_h:,.0f})) = {tp_decay:.1f} h"],
           f"{tp_simple:.0f} h ({tp_simple / 24:.1f} d) at a constant rate, and {tp_decay:.0f} h ({tp_decay / 24:.1f} d) with the decay, {100 * (tp_decay / tp_simple - 1):.0f}% longer and inside 3 to 7 days."),
    ],
    cards=[
        F("Point A", "2 cm superior to the vaginal fornix along the tandem and 2 cm lateral to it, where the uterine vessels cross the ureter."),
        F("Point B", "At the level of point A, 5 cm from the midline of the pelvis, at the pelvic sidewall."),
        F("Limits of point A", "Fixed to the applicator, not the tumour: it can lie inside a large tumour or outside a small one, in a steep dose gradient."),
        F("ICRU 38 bladder point", "On the lateral radiograph, the posterior surface of a Foley balloon holding 7 cm³ of contrast, pulled down against the urethra."),
        F("ICRU 38 rectal point", "5 mm behind the posterior vaginal wall, level with the lower end of the tandem sources or the middle of the vaginal sources."),
        F("Total reference air kerma (TRAK)", "Air kerma strength × time, summed over all sources or dwell positions, as air kerma at 1 m: 1 U for 1 h gives 1 µGy at 1 m."),
        F("High-risk CTV", "The whole cervix with any tumour remaining at brachytherapy, contoured on MR or CT and reported as D<sub>90</sub>."),
        F("D<sub>2cc</sub> of an organ at risk", "The minimum dose in the most exposed 2 cm³ of the organ."),
        F("Cervix EQD2 goals of the ABS", "High-risk CTV D<sub>90</sub> 80 to 90 Gy in total. D<sub>2cc</sub> at most about 90 Gy for the bladder and 70 to 75 Gy for the rectum and sigmoid."),
        F("Geometric optimization", "Dwell times set from the positions alone: longer where neighbouring positions add less dose, as at the ends of a catheter."),
        F("TRAK as the source decays", "The times of the same plan grow as 1/S<sub>K</sub>, so the TRAK stays the same.",
          w=[f"40,000 U for {t0:.1f} s and {SK0 * f45:,.0f} U for {t45:.1f} s both give {trak0:,.0f} µGy at 1 m."]),
        F("Prostate seed prescriptions", "Implant alone, to full decay: 145 Gy for I-125, 125 Gy for Pd-103, 115 Gy for Cs-131."),
        F("Timing of the postimplant CT", "About 30 days after an I-125 implant, sooner after Pd-103 or Cs-131, once the edema has largely resolved."),
        F("Peripheral loading", "Most seeds near the edge of the gland and few at the centre, to keep the urethral dose down."),
        F("COMS eye plaque prescription", "85 Gy to the tumour apex, or to 5 mm for a thinner tumour, at 0.60 to 1.05 Gy/h over 3 to 7 days. It was 100 Gy before the COMS adopted TG-43 dosimetry in 1996."),
        F("Skin surface applicators", "Prescribed at 3 mm depth: 40 Gy in 8 fractions or 42 Gy in 6."),
    ],
)

PROBLEMS = [
    PR("The Manchester system specifies the dose of an intracavitary cervix treatment at point A. Where is point A?",
       "2 cm superior to the vaginal fornix along the tandem and 2 cm lateral to the tandem",
       ["2 cm superior to the vaginal fornix and 5 cm lateral to the midline of the pelvis",
        "5 mm posterior to the posterior vaginal wall, level with the lower end of the tandem sources",
        "The posterior surface of a Foley balloon filled with 7 cm³ of contrast"],
       "Point A lies 2 cm up the tandem from the fornix level and 2 cm lateral to the tandem, where the uterine vessels cross the ureter; definitions mark the fornix level by the fornix itself, the tandem flange, or the top of the ovoids or ring. The point 5 cm from the midline is point B, and the other two are the ICRU 38 rectal and bladder points.", lvl="Easy"),
    PR("At brachytherapy, a cervical cancer has spread as a thin layer 3 cm down the vaginal wall. Which applicator treats the cervix and the involved vagina in one insertion?",
       "A tandem and cylinder", ["A tandem and ovoids", "A tandem and ring", "A vaginal cylinder without a tandem"],
       "A cylinder carries sources along the vaginal wall, and the tandem treats the cervix and uterus. Ovoids and a ring treat the fornices and the cervix but not the lower vaginal wall, and a cylinder without a tandem leaves the cervix and uterus untreated.", lvl="Easy"),
    PR("MR at the first fraction shows residual cervical tumour extending 3.5 cm lateral to the tandem on one side. The plan delivers the prescription to point A. Which statement best describes the dose at the lateral edge of the tumour?",
       "It is below the prescription, because point A lies inside the tumour",
       ["It equals the prescription, because point A follows the tumour edge", "It is above the prescription, because the edge lies nearer the sources", "It is unknown, because point A is defined on radiographs only"],
       "Point A is 2 cm from the tandem, so a tumour reaching 3.5 cm extends beyond it, where the dose has fallen further with distance from the sources. Point A is fixed to the applicator and does not follow the tumour, which is why image-based planning prescribes to the high-risk CTV D<sub>90</sub> instead.", lvl="Moderate"),
    PR("At brachytherapy, residual cervical tumour extends into the left parametrium, beyond the reach of the dose from a tandem and ring. Which change covers it best?",
       "Add interstitial needles through a template or a hybrid applicator",
       ["Raise the prescription to point A on both sides", "Prescribe the plan to point B in place of point A", "Lengthen every dwell time in the ring by the same factor"],
       "Needles place sources inside the parametrial disease, so the dose reaches it without raising the dose everywhere else. Raising the point A dose, prescribing to point B, or scaling every time all increase the dose to the bladder, rectum, and sigmoid along with the tumour.", lvl="Moderate"),
    PRN(STEM("An HDR course for a cervical cancer, evaluated for the tumour.", ["HDR = 7 Gy × 4 fractions", "α/β = 10 Gy"], "What is the [[EQD2]] of the HDR course?"), q_hdr, [28.0, q_hdr_bed, q_hdr3], "{:.1f} Gy",
        f"EQD2 = 28 × (7 + 10) / (2 + 10) = {q_hdr:.1f} Gy. The physical dose is 28.0 Gy, the BED is {q_hdr_bed:.1f} Gy, and α/β = 3 Gy gives {q_hdr3:.1f} Gy, the value for an organ that received the full 7 Gy.", lvl="Moderate"),
    PRM("Image-based cervix brachytherapy reports each organ at risk as D<sub>2cc</sub> rather than as the dose at an ICRU 38 point. Which of these are reasons?",
        ["A single point can miss the most exposed part of the organ wall", "CT or MR shows the organ itself, so the dose to a volume can be calculated"],
        ["The ICRU 38 points cannot be located on radiographs", "The ICRU 38 points are defined relative to the tumour", "D<sub>2cc</sub> does not change when the applicator moves"],
        "Radiographs show the applicator and the contrast but not the organ walls, and a single point need not lie where the organ is hottest. With CT or MR the wall is contoured and the dose to its most exposed 2 cm³ is calculated. The ICRU 38 points are found on radiographs relative to the applicator, not the tumour, and D<sub>2cc</sub> changes when the applicator moves.", lvl="Challenging"),
    PRN(STEM("A cervical cancer is treated with external beam therapy and HDR. The rectum is taken to receive the full external beam dose.",
             ["external beam = 45 Gy in 25 fractions", "rectum D<sub>2cc</sub> per HDR fraction = 4.2 Gy, in 4 fractions", "α/β = 3 Gy for the rectum"],
             "What is the [[total EQD2]] of the rectum D<sub>2cc</sub>?"), r_tot, [r_phys, r_ab10, r_bed], "{:.1f} Gy",
        f"External beam: 45 × (1.8 + 3) / (2 + 3) = {r_eb:.1f} Gy. HDR: {RQ_D * HDR_N:.1f} × (4.2 + 3) / (2 + 3) = {r_hdr:.1f} Gy. Total = {r_tot:.1f} Gy, below the ABS limit of 70 to 75 Gy. The physical sum is {r_phys:.1f} Gy, α/β = 10 Gy gives {r_ab10:.1f} Gy, and adding the BEDs gives {r_bed:.1f} Gy.", lvl="Challenging"),
    TYPED(STEM("An HDR course for a cervical cancer must keep the rectum within a stated limit. The rectum is taken to receive the full external beam dose.",
               ["external beam = 45 Gy in 25 fractions", "HDR = 4 fractions", "limit for the rectum D<sub>2cc</sub> = 75 Gy EQD2", "α/β = 3 Gy"],
               "What is the [[largest rectal D<sub>2cc</sub> per HDR fraction]] that stays within the limit?"), d_max, 0.02, "Gy",
          f"The external beam uses 45 × 4.8 / 5 = {r_eb:.1f} Gy, leaving {r_left:.1f} Gy. Four fractions of d give 4 d (d + 3) / 5, so d² + 3d − {r_left * 5 / 4:.2f} = 0 and d = {d_max:.2f} Gy. Dividing the remaining {r_left:.1f} Gy by four, as if it were physical dose, gives {r_left / 4:.2f} Gy per fraction, far too much.", lvl="Challenging"),
    PRN(STEM("One dwell position of an Ir-192 HDR source treats a point on its transverse axis. Use the point-source form with g(r) and the anisotropy taken as 1.",
             ["S<sub>K</sub> = 36,000 U", "Λ = 1.11 cGy h<sup>−1</sup> U<sup>−1</sup>", "distance = 1.5 cm", "dose at the point = 6.0 Gy"], "What [[dwell time]] delivers this dose?"), tq, [tq_noinv, tq_lin, tq_mul], "{:.0f} s",
        f"Ḋ = 36,000 × 1.11 / 1.5² = {rate_q:,.0f} cGy/h = {rate_q / 3600:.3f} cGy/s, so t = 600 / {rate_q / 3600:.3f} = {tq:.0f} s. Leaving out the inverse square gives {tq_noinv:.0f} s, dividing by r in place of r² gives {tq_lin:.0f} s, and multiplying by r² gives {tq_mul:.0f} s.", lvl="Challenging"),
    PRN(STEM("A hand check of an HDR plan recalculates the dose at a reference point from two dwell positions. Use the point-source form with g(r) and the anisotropy taken as 1.",
             ["S<sub>K</sub> = 40,000 U", "Λ = 1.11 cGy h<sup>−1</sup> U<sup>−1</sup>", "dwell 1: 2.0 cm from the point, 100 s", "dwell 2: 2.5 cm from the point, 150 s"],
             "What [[dose]] do the two dwells give at the point?"), pd_sum / 100, [pd_noinv / 100, pd_lin / 100, pd_each[0] / 100], "{:.2f} Gy",
        f"Each dwell gives S<sub>K</sub> Λ t / r²: 40,000 × 1.11 × (100 / 3600 h) / 2.0² = {pd_each[0]:.1f} cGy and 40,000 × 1.11 × (150 / 3600 h) / 2.5² = {pd_each[1]:.1f} cGy, so D = {pd_sum:.1f} cGy = {pd_sum / 100:.2f} Gy. Leaving out the inverse square gives {pd_noinv / 100:.2f} Gy, dividing by r in place of r² gives {pd_lin / 100:.2f} Gy, and the first dwell alone gives {pd_each[0] / 100:.2f} Gy.", lvl="Moderate"),
    PR("An HDR plan is recalculated 30 days later to deliver the same dose distribution with the decayed source. How does the total reference air kerma of the plan change?",
       "It stays the same, because the times grow as the strength falls",
       ["It falls in proportion to the source strength", "It rises in proportion to the treatment time", "It changes by the square of the decay factor"],
       "TRAK is the air kerma strength times the total time. For the same dose the times scale as 1/S<sub>K</sub>, so the product is unchanged, and a TRAK that differs from earlier fractions of the same plan points to an error. Scaling it with the strength or with the time alone forgets that the other factor changes in the opposite direction.", lvl="Moderate"),
    SORT("Put the steps of an image-guided HDR fraction in order.", ["1st", "2nd", "3rd", "4th", "5th"],
         [("Insert the applicator", 0), ("Image the applicator in place with CT or MR", 1), ("Contour the targets and organs and reconstruct the source paths", 2),
          ("Optimize the dwell times and normalize the plan", 3), ("Check the plan independently, then treat", 4)],
         "Contours and source paths need images taken with the applicator in place, the dwell times can be optimized only once the targets and paths exist, and the independent check of the final plan comes before the source leaves the afterloader.", lvl="Easy", mode="rank", cap=1),
    PR("In a permanent prostate implant, most seeds are placed near the edge of the gland and few near its centre. What is the main reason?",
       "To keep the urethra, which runs through the centre, from a high dose",
       ["To raise the dose at the centre of the gland", "To keep the seeds away from the rectal wall", "To reduce the chance that seeds migrate"],
       "Seeds spaced evenly through the gland add up their doses at the centre, where the urethra runs. Peripheral loading keeps the coverage at the edge while the centre stays cooler; it does not move seeds away from the rectum, which lies along the posterior edge, and it does not change migration.", lvl="Easy"),
    PR("The postimplant CT of an I-125 prostate implant is taken about 30 days after the implant rather than on the day of the implant. What is the main reason?",
       "The swelling from the needles has largely resolved by then",
       ["The seeds have reached their full strength by then", "Half of the total dose has been delivered by then", "The metal artifacts of the seeds have faded by then"],
       f"Edema swells the gland and spreads the seeds apart, so a scan on the day of the implant gives a lower D<sub>90</sub> than the gland receives as it shrinks; in one serial CT study the swelling resolved with a half-time of about 9 days. The seeds are strongest at the implant and decay from then on, and half of the I-125 dose takes one half-life, {I_T:.0f} days.", lvl="Moderate"),
    PRM("A permanent I-125 prostate implant is evaluated on CT after the implant. Which of these does TG-137 name as primary dose parameters for the prostate?",
        ["D<sub>90</sub>", "V<sub>100</sub>", "V<sub>150</sub>"], ["V<sub>200</sub>", "D<sub>100</sub>", "V<sub>90</sub>"],
        "TG-137 keeps D<sub>90</sub>, V<sub>100</sub>, and V<sub>150</sub> as the primary prostate parameters, with D<sub>10</sub> of the urethra and D<sub>2cc</sub> of the rectum for the organs. V<sub>200</sub>, D<sub>100</sub>, and V<sub>90</sub> are secondary.", lvl="Moderate"),
    PRN(STEM("An I-125 prostate implant. Licences count activity, so the strength is converted with the exposure rate constant.", ["seeds = 90", "S<sub>K</sub> per seed = 0.45 U", "1 mCi of apparent activity = 1.27 U for I-125"],
             "What is the [[total apparent activity]] implanted?"), a_q, [skq_tot, skq_tot * U_MCI, SKQ_SEED / U_MCI], "{:.3g} mCi",
        f"Total S<sub>K</sub> = 90 × 0.45 = {skq_tot:.2f} U, and {skq_tot:.2f} / {U_MCI:.3f} = {a_q:.1f} mCi. Reading the strength in U as mCi gives {skq_tot:.1f}, multiplying by the factor gives {skq_tot * U_MCI:.1f}, and one seed alone is {SKQ_SEED / U_MCI:.3f} mCi.", lvl="Moderate"),
    PR("A choroidal melanoma lies against the optic disc. Which plaque design lets the plaque cover the tumour base with a margin?",
       "A notched plaque, cut away to fit around the optic nerve",
       ["A plaque with a thicker gold-alloy backing", "A smaller plaque loaded with stronger seeds", "A plaque loaded with Pd-103 in place of I-125"],
       "The notch lets the plaque sit against the nerve, so its seeds still reach the tumour edge at the disc. A thicker backing, stronger seeds, or another isotope does not change where the plaque can sit.", lvl="Easy"),
    PRM("An I-125 episcleral plaque is sutured over a choroidal melanoma. Which of these limit the dose to the tissue behind and beside the plaque?",
        ["The gold-alloy shell behind the seeds", "The lip of the shell around the seeds"],
        ["The Silastic carrier that holds the seeds", "The notch cut for the optic nerve", "A lower apex dose rate with a longer implant"],
        "The low-energy I-125 photons are absorbed in a fraction of a millimetre of gold, so the shell shields the orbit behind the plaque and its lip collimates the dose at the sides. The Silastic carrier sits between the seeds and the eye, the notch only shapes the plaque, and a lower dose rate delivers the same total dose.", lvl="Moderate"),
    PR("A COMS plaque plan for an I-125 plaque is calculated in water with the TG-43 formalism, ignoring the gold-alloy shell and the Silastic carrier. How does the dose delivered at 5 mm depth compare with this calculation?",
       f"Lower: about {TG129_I:.0f} Gy where the water calculation gives {APEX:.0f} Gy",
       [f"Higher: about {2 * APEX - TG129_I:.0f} Gy, from backscatter off the gold", "The same, because the plaque materials lie behind the seeds", f"Lower: about {APEX / 2:.1f} Gy, because the gold absorbs half"],
       f"TG-129 found that the plaque materials lower the dose: the Silastic carrier attenuates the photons, and the gold scatters back less than the water it replaces, so {APEX:.0f} Gy calculated in water at 5 mm is about {TG129_I:.0f} Gy for I-125. The gold adds no backscatter at these energies, and it lies behind the seeds, not between them and the tumour.", lvl="Challenging"),
    TYPED(STEM("An I-125 plaque treats a choroidal melanoma. Include the decay of I-125 during the implant.", ["prescription = 85 Gy to the tumour apex", "initial dose rate at the apex = 0.65 Gy/h", "T<sub>1/2</sub> = 59.4 d"],
               "What [[treatment time]] delivers the prescription?"), tq_plaque, 0.015, "h",
          f"Mean life τ = 59.4 × 24 / ln 2 = {tau_h:,.0f} h. The dose by time t is Ḋ₀ τ (1 − e<sup>−t/τ</sup>), so t = −τ ln(1 − 85 / (0.65 × {tau_h:,.0f})) = {tq_plaque:.1f} h, about {tq_plaque / 24:.1f} days. Ignoring the decay gives 85 / 0.65 = {tq_plaque0:.1f} h, {100 * (1 - tq_plaque0 / tq_plaque):.1f}% short.", lvl="Challenging"),
    PR("A thin basal cell carcinoma is treated with an HDR surface applicator. To what depth is the dose usually prescribed?",
       "3 mm below the skin surface", ["The skin surface itself", "5 mm below the skin surface", "10 mm below the skin surface"],
       "The ABS working group gives 3 mm as the standard depth for a skin cancer without significant thickness, and a thicker lesion needs a deeper prescription. 5 mm is the usual depth for a vaginal cylinder, and with the steep fall of dose with depth a prescription at the surface would leave the base of the lesion short.", lvl="Easy"),
    SORT("Match each quantity to its definition.", ["D<sub>90</sub>", "D<sub>2cc</sub>", "V<sub>100</sub>", "V<sub>150</sub>", "TRAK"],
         [("Dose received by at least 90% of the target", 0), ("Minimum dose in the most exposed 2 cm³ of an organ", 1), ("Fraction of the target receiving at least the prescription", 2),
          ("Fraction of the target receiving at least 1.5 times the prescription", 3), ("Air kerma strength times the total dwell time, at 1 m", 4)],
         "D quantities are doses read from the dose–volume histogram at a stated volume, and V quantities are volumes read at a stated dose. TRAK uses no patient data: it is the source strength times the time, expressed at 1 m.", lvl="Moderate", mode="match", cap=1),
]

INLINE = {0: [1, 2, 3, 5], 1: [9, 10, 11, 12], 2: [13, 14, 15, 16], 3: [17, 18, 21]}

TERMS = ["point A", "point B", "total reference air kerma", "high-risk CTV", "dwell time", "geometric optimization", "peripheral loading", "episcleral plaque"]

TAKE = [
    ["Point A: 2 cm above the vaginal fornix along the tandem and 2 cm lateral. Point B: the same level, 5 cm from the midline.",
     "Image-based plans report the high-risk CTV D<sub>90</sub> and the organ D<sub>2cc</sub> as total EQD2 (α/β 10 and 3 Gy). ABS: D<sub>90</sub> 80 to 90 Gy; D<sub>2cc</sub> about 90 Gy bladder, 70 to 75 Gy rectum and sigmoid.",
     "TRAK = S<sub>K</sub> × total dwell time, as air kerma at 1 m."],
    ["Dose at a point = the sum over dwell positions of dose rate × dwell time; the times shape the distribution.",
     "As the source decays the times grow as 2<sup>t/T<sub>1/2</sub></sup>, and the TRAK of the plan stays the same."],
    ["Implant alone: 145 Gy (I-125), 125 Gy (Pd-103), 115 Gy (Cs-131). Report D<sub>90</sub>, V<sub>100</sub>, V<sub>150</sub>; urethra D<sub>10</sub> below 150%.",
     "Peripheral loading spares the central urethra. The postimplant CT waits about 30 days for I-125, until the edema resolves."],
    ["COMS: 85 Gy to the tumour apex (or 5 mm) at 0.60 to 1.05 Gy/h, over 3 to 7 days. The gold shell and lip collimate; a notch clears the optic nerve.",
     "Skin HDR: prescribed at 3 mm, 40 Gy in 8 or 42 Gy in 6 fractions, with a steep fall of dose with depth."],
]
