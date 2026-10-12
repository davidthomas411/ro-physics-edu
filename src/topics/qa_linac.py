from blocks import *
import math

# ---------------------------------------------------------------- this chapter's formulas
def dev(m, b):
    """Percent change of a reading m from its baseline b."""
    return 100 * (m - b) / b

def big_gamma(r, d, dta, dd):
    """Γ for one measured-calculated pair: distance r (mm) and dose difference d (%), scaled by the criteria dta (mm) and dd (%)."""
    return math.sqrt((r / dta) ** 2 + (d / dd) ** 2)

def gamma(pairs, dta, dd):
    """γ at a measured point: the smallest Γ over the calculated points, each given as (distance mm, dose difference %)."""
    return min(big_gamma(r, d, dta, dd) for r, d in pairs)

def rate(n_eval, n_fail):
    """Percent of evaluated points with γ ≤ 1."""
    return 100 * (n_eval - n_fail) / n_eval

def gap_dose(err, g):
    """Percent change of the dose through a sliding gap of effective width g (mm) when one bank opens it by err (mm): the dose goes as the width."""
    return 100 * err / g

sgn = lambda v, d=1: f"{v:+.{d}f}".replace("-", "−")

# ---------------------------------------------------------------- tolerances quoted in the text
OUT_D, OUT_M, OUT_A = 3.0, 2.0, 1.0                 # TG-142 photon output: daily constancy, monthly constancy, annual TG-51 calibration (%)
BACKUP, PROFILE = 2.0, 1.0                          # TG-142 monthly: backup monitor chamber constancy, photon profile constancy (%)
LAS = (2.0, 1.5, 1.0)                               # TG-142 daily lasers (mm): conventional, IMRT, SRS/SBRT
ANG, MLC = 1.0, 1.0                                 # TG-142 monthly: angle indicators (degrees), IMRT leaf position (mm)
IMG, ISO = (2.0, 1.0), (2.0, 1.0)                   # TG-142 (mm): imaging-treatment isocenter coincidence (daily), radiation-mechanical isocenter coincidence (annual); conventional, SRS/SBRT
DD, DTA, THR, TL, AL = 3.0, 2.0, 10.0, 95.0, 90.0   # TG-218 universal limits: criteria, low-dose threshold, tolerance limit, action limit (%)
mm = lambda v: f"{v:g} mm"
TG142 = [
    ["Photon output", "Daily; monthly; annual", f"{OUT_D:g}%; {OUT_M:g}%; {OUT_A:g}%"],
    ["Backup monitor chamber constancy", "Monthly", f"{BACKUP:g}%"],
    ["Photon beam profile constancy", "Monthly", f"{PROFILE:g}%"],
    ["Lasers", "Daily", f"{mm(LAS[0])}; IMRT {mm(LAS[1])}; SRS/SBRT {mm(LAS[2])}"],
    ["Light and radiation field coincidence", "Monthly", "2 mm or 1% per side"],
    ["Gantry and collimator angle indicators", "Monthly", f"{ANG:g}°"],
    ["MLC leaf position (IMRT)", "Monthly", f"{mm(MLC)}; weekly picket fence"],
    ["Imaging and treatment isocenters", "Daily", f"{mm(IMG[0])}; SRS/SBRT {mm(IMG[1])}"],
    ["Radiation and mechanical isocenters", "Annual", f"{mm(ISO[0])}; SRS/SBRT {mm(ISO[1])}"],
]
DOCS = [
    ["TG-142 (2009)", "Linac QA tests, frequencies, and tolerances"],
    ["TG-198 (2021)", "Implementation guide for TG-142"],
    ["MPPG 8.a (2017), revised as 8.b (2023)", "Critical linac performance tests"],
    ["TG-106 (2008)", "Equipment and methods for beam data commissioning"],
    ["TG-53 (1998); MPPG 5.a (2015), revised as 5.b (2022)", "Commissioning and QA of the planning system"],
    ["TG-218 (2018)", "Tolerance and action limits for IMRT measurement QA"],
    ["TG-100 (2016)", "Risk analysis of the treatment process"],
]

# ---------------------------------------------------------------- worked examples
ex_b, ex_6, ex_10 = 1.000, 1.013, 0.977                             # monthly chamber check, cGy/MU
ex_d6, ex_d10 = dev(ex_6, ex_b), dev(ex_10, ex_b)
ex_g, ex_e = 5.0, 1.0                                               # effective gap and one-bank error (mm)
ex_gap = gap_dose(ex_e, ex_g)
gA, gB = big_gamma(0.0, 4.2, DTA, DD), big_gamma(1.2, 1.5, DTA, DD)  # two calculated points near one measured point
g_ex = gamma([(0.0, 4.2), (1.2, 1.5)], DTA, DD)
pr_all, pr_eval, pr_fail = 1386, 1240, 75                           # diode array: all diodes, above the threshold, γ > 1
pr_ex = rate(pr_eval, pr_fail)

# ---------------------------------------------------------------- numbers in the questions
q_base = 60.0                                                       # daily device baseline reading
q_hi = q_base * (1 + OUT_D / 100)
q_r, q_d = 1.0, 2.4                                                 # γ question, 3%/2 mm
q_gam = big_gamma(q_r, q_d, DTA, DD)
t_r, t_d, t_dd = 1.0, 1.5, 2.0                                      # γ question, 2%/2 mm
t_gam, t_gam3 = big_gamma(t_r, t_d, DTA, t_dd), big_gamma(t_r, t_d, DTA, DD)
n_all, n_eval, n_fail = 1386, 1108, 50                              # passing-rate question
n_rate = rate(n_eval, n_fail)
n_all_den = 100 * (n_eval - n_fail) / n_all                         # every diode in the denominator
n_low_pass = 100 * (n_all - n_fail) / n_all                         # low-dose diodes counted as passing
n_failpct = 100 * n_fail / n_eval
s_nom, s_dlg, s_err = 8.5, 1.5, 0.5                                 # sliding-gap question, mm
s_gap = gap_dose(s_err, s_nom + s_dlg)
s_nodlg, s_both = gap_dose(s_err, s_nom), gap_dose(2 * s_err, s_nom + s_dlg)
b_g, b_e = 5.0, 0.5                                                 # both banks shifted together
b_one, b_two = gap_dose(b_e, b_g), gap_dose(2 * b_e, b_g)
acc_g, acc_lim = 5.0, 2.0                                           # gap accuracy for a 2% dose error
acc = acc_lim / 100 * acc_g
loc_p, loc_d = 0.15, 1.0                                            # local against global: point at 15% of the maximum, difference 1% of the maximum
loc_pct = loc_d / loc_p
loc_gg, loc_gl = loc_d / DD, loc_pct / DD

TOPIC = dict(
    id="qa-linac", domain=7, sub="VII.A", title="Linac quality assurance and TG-142",
    ref=dict(aapm="TG-142", khan="", ford="18"),
    guide=[
        H("Structure of a QA program"),
        P("Acceptance testing confirms that an installed linac meets the specifications agreed in the purchase. Commissioning measures the beam data, enters them into the planning system, and validates the calculation before clinical use. Periodic QA repeats set tests daily, monthly, and annually, and event-driven QA repeats the relevant ones after a repair, an upgrade, or a move."),
        P("The values measured at acceptance and commissioning form the baseline. Later results are judged by their change from it and trended, so that a slow drift shows before it reaches a limit. A tolerance is the range of normal operation. In TG-142 the tabulated tolerance is also the first action level, and the response is graded: inspection for a sudden change within tolerance, scheduled action for results at or slightly beyond tolerance, and immediate action, which stops treatment, for a failed interlock or a large dose error."),
        P("A qualified medical physicist (QMP) designs the program, sets its limits, performs or supervises the monthly and annual tests, and reviews the daily results recorded by therapists. TG-100 departs from fixed lists of tests: it analyses how each step of the process can fail and directs QA at the failures of highest risk."),
        TABLE(["AAPM document", "Subject"], DOCS),

        H("TG-142 tests and tolerances"),
        P("TG-142 updated the linac tests of TG-40 and added asymmetric jaws, the MLC, dynamic wedges, and imaging on the linac. Its tests are dosimetric (output, profiles, energy), mechanical (lasers, distance indicator, field size, angles, couch, isocenter), and safety (interlocks, audiovisual monitors). Faults that could affect the next patient's dose or position are checked daily, slower drifts monthly, and the calibration and the isocenter annually. A machine used for SRS or SBRT has tighter geometric tolerances, mostly 1 mm; the output constancy tolerances are the same for every use."),
        TABLE(["Test", "Frequency", "Tolerance"], TG142),
        P("The table gives TG-142 (2009). TG-198 (2021) restates some values, among them light and radiation field coincidence as ±2 mm per jaw, and gives the isocenter tolerances as absolute values; the document in force governs."),
        P("Imaging QA checks the coincidence of the imaging and treatment isocenters daily, image quality (resolution, contrast, noise, and CT number constancy for CBCT) monthly against baseline, and imaging dose annually."),
        EX("Monthly output check", STEM("A calibrated ion chamber in water measures the output under the reference conditions of the calibration.", [f"baseline = {ex_b:.3f} cGy/MU", f"6 MV reading = {ex_6:.3f} cGy/MU", f"10 MV reading = {ex_10:.3f} cGy/MU", f"TG-142 monthly tolerance = {OUT_M:g}%"], "Find the [[percent deviation]] of each beam and whether it passes."),
           [f"6 MV: ({ex_6:.3f} − {ex_b:.3f}) / {ex_b:.3f} × 100 = {sgn(ex_d6)}%", f"10 MV: ({ex_10:.3f} − {ex_b:.3f}) / {ex_b:.3f} × 100 = {sgn(ex_d10)}%", f"Compare each magnitude with {OUT_M:g}%"],
           f"6 MV is within tolerance at {sgn(ex_d6)}%. 10 MV is outside it at {sgn(ex_d10)}%: the reading is repeated and checked, then the output is adjusted to the baseline and the change recorded."),
        P("A picket fence delivers narrow strips at regular intervals, each formed by every leaf pair at one position; a leaf out of position breaks the line of its strip. A starshot exposes one film to a narrow field at several gantry, collimator, or couch angles, and the smallest circle crossed by every line measures the size of that rotation isocenter. A Winston–Lutz test images a small field around a ball bearing at the isocenter from several angles and measures the offset between the radiation isocenter and the bearing."),
        P("A calibration error in one leaf bank changes the width of every sliding gap by the same amount, whereas a shift of both banks together moves the dose pattern without changing it."),
        EX("Leaf bank error", STEM("A sliding-window field. The dose at a point goes as the effective width of the gap, the nominal gap plus the dosimetric leaf gap.", [f"effective gap = {ex_g:g} mm", f"error = one bank opens every gap by {ex_e:g} mm"], "Find the [[change in dose]], and the change if both banks are shifted 1 mm the same way."),
           [f"One bank: the gap becomes {ex_g:g} + {ex_e:g} = {ex_g + ex_e:g} mm", f"Dose ratio = {ex_g + ex_e:g} / {ex_g:g} = {(ex_g + ex_e) / ex_g:.2f}", f"Both banks: the gap stays {ex_g:g} mm and moves 1 mm"],
           f"{sgn(ex_gap, 0)}% with the error in one bank. With both banks shifted, the dose is unchanged and the pattern is displaced by 1 mm."),

        H("Patient-specific IMRT QA"),
        P("Before the first treatment, an IMRT or VMAT plan is delivered to a phantom holding a detector array, film, or an ion chamber, and the measured dose is compared with the dose calculated for that phantom. TG-218 recommends delivering all beams at their planned angles (true composite) and comparing absolute dose."),
        P("A dose difference alone fails good plans in steep gradients, where a 1 mm shift changes the dose by several percent, and a distance to agreement alone is too lenient in flat regions. The gamma index combines the two criteria."),
        EQ("Γ(r<sub>m</sub>, r<sub>c</sub>) = √[ (|r<sub>c</sub> − r<sub>m</sub>| / Δd)² + ((D<sub>c</sub> − D<sub>m</sub>) / ΔD)² ]",
           "γ(r<sub>m</sub>) = the smallest Γ over all calculated points r<sub>c</sub>;   the point passes when γ ≤ 1",
           "Δd = distance criterion (mm),   ΔD = dose criterion (% of the normalization dose)"),
        P(f"γ ≤ 1 means that a calculated point lies inside the ellipse set by the two criteria, commonly {DD:g}% and {DTA:g} mm. Global normalization expresses the dose difference as a percentage of one reference dose, usually the maximum; local normalization uses the dose at the point, which is stricter in low-dose regions. Points below a threshold, commonly {THR:g}% of the maximum, are excluded."),
        EX("Gamma at one point", STEM(f"A planar comparison at {DD:g}%/{DTA:g} mm with global normalization. Near one measured point, two calculated points give the smallest Γ; every other point gives a larger one.", ["point A: distance 0 mm, dose difference 4.2% of the maximum", "point B: distance 1.2 mm, dose difference 1.5% of the maximum"], "Find [[γ]] at the measured point."),
           [f"Γ<sub>A</sub> = √[0² + (4.2/3)²] = {gA:.2f}", f"Γ<sub>B</sub> = √[(1.2/2)² + (1.5/3)²] = √({(1.2 / 2) ** 2:.2f} + {(1.5 / 3) ** 2:.2f}) = {gB:.2f}", "γ is the smaller value"],
           f"γ = {g_ex:.2f}, so the point passes, although the dose difference at the same position (4.2%) exceeds {DD:g}%. The point lies in a gradient, where a small shift accounts for the difference."),
        P(f"For {DD:g}%/{DTA:g} mm, global normalization, and a {THR:g}% threshold, TG-218 sets a universal tolerance limit of {TL:g}% of points passing and an action limit of {AL:g}%. A result between the two is investigated; below the action limit the plan is not treated until the cause is found and corrected. A clinic may also derive its own limits from the statistics of its past results."),
        EX("Passing rate and limits", STEM(f"A VMAT plan is measured with a diode array and compared at {DD:g}%/{DTA:g} mm with global normalization and a {THR:g}% threshold.", [f"diodes in the array = {pr_all:,}", f"diodes above {THR:g}% of the maximum = {pr_eval:,}", f"evaluated diodes with γ > 1 = {pr_fail}"], "Find the [[passing rate]] and the action."),
           [f"Evaluated points = {pr_eval:,}; the {pr_all - pr_eval} below the threshold are excluded", f"Passing = {pr_eval:,} − {pr_fail} = {pr_eval - pr_fail:,}", f"Rate = {pr_eval - pr_fail:,} / {pr_eval:,} = {pr_ex:.1f}%"],
           f"{pr_ex:.1f}%: below the {TL:g}% tolerance limit and above the {AL:g}% action limit, so the result is investigated before the plan is accepted."),
        P("A failing result shows that delivery and calculation disagree, not why: the measurement, the machine, the beam model, or a plan too complex to deliver. A pass shows that the plan is delivered as calculated in a phantom, not that the patient's anatomy, contours, prescription, or setup are right, and passing rates correlate poorly with errors in organ doses. In audits with an anthropomorphic phantom, the institutions' own QA had flagged few of the plans that failed."),

        H("Commissioning and planning-system QA"),
        P("Commissioning measures the data the planning system needs: depth doses and profiles over a range of field sizes, output factors, wedge factors, MLC transmission and the dosimetric leaf gap, and electron depth doses and applicator factors. The detector must suit the field (TG-106): a large chamber averages over a steep gradient, so it widens the measured penumbra and lowers the measured small-field output."),
        P("The beam model is validated against measurement for open, wedged, and MLC-shaped fields in water, in a heterogeneous phantom with lung-like slabs, and for IMRT and VMAT test plans (TG-53, MPPG 5.a). An end-to-end test takes a phantom through CT, contouring, planning, data transfer, image guidance, and delivery, and measures the dose in it. A second physicist or an external audit (an IROC phantom or mailed dosimeters) reviews the commissioning, because its errors affect every patient planned with that model."),
        P("Afterwards, stored reference plans are recalculated after every software upgrade and compared with their earlier results, and non-dosimetric checks cover the CT-number-to-density table, image import, contours, and plan transfer to the linac."),
    ],
    cards=[
        F("Acceptance testing", "Confirms that the installed machine meets the specifications agreed in the purchase, before clinical use."),
        F("Commissioning", "Measures the beam data, builds and validates the planning-system model, and records the baseline for periodic QA."),
        F("Baseline", "The value measured at acceptance and commissioning. Each later result is judged by its change from it, and results are trended."),
        F("Tolerance and action level", "TG-142 grades the response: inspection for a sudden change within tolerance, scheduled correction at or slightly beyond it, and immediate action (stop treatment) when a safety interlock fails or the result is far beyond it."),
        F("TG-142 photon output tolerances", f"{OUT_D:g}% daily, {OUT_M:g}% monthly, and {OUT_A:g}% for the annual TG-51 calibration."),
        F("TG-142 daily laser tolerance", f"{mm(LAS[0])} for a conventional machine, {mm(LAS[1])} for IMRT, and {mm(LAS[2])} for SRS/SBRT."),
        F("MLC leaf position in TG-142", f"For an IMRT machine: a visual picket fence weekly and a measurement monthly, with a tolerance of {mm(MLC)}."),
        F("Picket fence", "Narrow strips at regular intervals, each formed by every leaf pair at one position. A leaf out of position breaks the line of its strip."),
        F("Winston–Lutz test", "A small field imaged around a ball bearing at the isocenter from several gantry, collimator, and couch angles. It measures the offset between the radiation isocenter and the ball bearing."),
        F("Leaf bank error in a sliding window", "An error Δx in one bank changes the dose through a gap of effective width g by Δx/g. A shift of both banks the same way only displaces the pattern."),
        F("Gamma index", "Γ = √[(Δr/Δd)² + (δ/ΔD)²] for the distance Δr and dose difference δ to each calculated point, with criteria Δd and ΔD. γ is the smallest Γ, and the point passes when γ ≤ 1."),
        F("TG-218 universal limits", f"At {DD:g}%/{DTA:g} mm, global normalization, and a {THR:g}% threshold: tolerance limit {TL:g}% of points passing, action limit {AL:g}%."),
        F("Global and local normalization", "Global: the dose difference as a percentage of one reference dose, usually the maximum. Local: a percentage of the dose at the point, stricter in low-dose regions."),
        F("Limits of patient-specific QA", "It tests the delivery of the plan in a phantom. It does not test the patient's anatomy, contours, prescription, or setup."),
        F("End-to-end test", "A phantom taken through CT, planning, data transfer, image guidance, and delivery, with the dose measured in it."),
    ],
)

PROBLEMS = [
    # ---- 1-2: structure of the program
    SORT("Match each stage of linac testing to what it establishes.", ["Acceptance testing", "Commissioning", "Periodic QA", "End-to-end test"],
         [("The machine meets the specification agreed in the purchase", 0), ("Beam data are measured and the planning model is built", 1), ("The machine has not drifted from its baseline", 2), ("The whole chain from CT to delivery gives the planned dose", 3)],
         "Acceptance testing checks the machine against the purchase specification, commissioning gathers the beam data and builds the planning model, periodic QA checks for drift from the baseline, and an end-to-end test checks the whole chain at once.", lvl="Easy", mode="match", cap=1),
    # ---- 3-13: TG-142
    PRN(STEM(ask="What is the TG-142 [[tolerance]] for the daily photon output constancy check?"), OUT_D, [OUT_M, OUT_A, 5.0], "{:.0f}%",
        f"TG-142 sets {OUT_D:g}% for the daily constancy check. {OUT_M:g}% is the monthly tolerance for a calibrated chamber, and {OUT_A:g}% applies to the annual calibration.", lvl="Easy"),
    PRM(STEM("A clinic sets up the QA schedule for a linac that delivers conventional and IMRT treatments.", ask="Which of these are daily tests in TG-142?"),
        ["Photon output constancy", "Laser localization"], ["MLC transmission", "Radiation and mechanical isocenter coincidence", "Gantry angle indicators"],
        "Output constancy and the lasers are checked daily, because a fault in either affects the next patient's dose or position. MLC transmission and the radiation and mechanical isocenter coincidence are annual tests, and the angle indicators are checked monthly.", lvl="Easy"),
    SORT("Rank these TG-142 tests from the most frequent to the least frequent.", ["1st (most frequent)", "2nd", "3rd", "4th (least frequent)"],
         [("Door interlock", 0), ("Visual picket fence on an IMRT machine", 1), ("Light and radiation field coincidence", 2), ("Output calibration by TG-51", 3)],
         "The door interlock is checked daily, the picket fence weekly, the light and radiation field coincidence monthly, and the TG-51 calibration annually.", lvl="Easy", mode="rank", cap=1),
    PRN(STEM("A daily QA device measures the photon output of a linac.", [f"baseline reading = {q_base:.1f}"], "What is the [[highest reading]] that is within the TG-142 daily tolerance?"), q_hi, [q_base + OUT_D, q_base * (1 + OUT_M / 100), q_base * (1 + OUT_A / 100)], "{:.1f}",
        f"The daily tolerance is {OUT_D:g}% of the baseline: {q_base:.1f} × {1 + OUT_D / 100:.2f} = {q_hi:.1f}. Adding 3 reading units gives {q_base + OUT_D:.1f}, and the monthly and annual tolerances give {q_base * (1 + OUT_M / 100):.1f} and {q_base * (1 + OUT_A / 100):.1f}.", lvl="Moderate"),
    PR(STEM("The monthly ion-chamber check of a 10 MV beam, under the reference conditions of the calibration, reads 2.6% above the baseline. The setup, the chamber, and the temperature and pressure correction have been checked, and a repeat reading agrees.", ask="What is the appropriate action?"),
       "Adjust the output to the baseline and record the change", ["Continue, because the 3% daily tolerance is not exceeded", "Lower each patient's monitor units by 2.6% until the annual calibration", "Leave the output and repeat the check at next month's QA"],
       f"The monthly tolerance is {OUT_M:g}%, and a confirmed reading of +2.6% exceeds it, so the output is brought back to the baseline. The {OUT_D:g}% daily tolerance belongs to the daily device, not to the monthly chamber measurement, and changing each patient's monitor units hides the fault without correcting it.", lvl="Moderate"),
    PR(STEM("A linac is used for SRS/SBRT as well as for conventional and IMRT treatments.", ask="Which daily laser tolerance applies to it?"), f"{mm(LAS[2])}, the stereotactic value", [f"{mm(LAS[1])}, the IMRT value", f"{mm(LAS[0])}, the conventional value", "None, because image guidance corrects the setup"],
       f"A machine used for SRS/SBRT is held to the SRS/SBRT column. TG-142 gives {mm(LAS[0])} for a conventional machine, {mm(LAS[1])} for IMRT, and {mm(LAS[2])} for SRS/SBRT. Image guidance does not remove the need, because the lasers place the patient and the phantoms that check the imaging isocenter.", lvl="Moderate"),
    PR(STEM("The weekly picket fence on an IMRT linac shows straight lines, except at one leaf pair, where the line is offset by about 1.5 mm in every strip.", ask="What is the most likely cause?"),
       "A single leaf out of position", ["A collimator angle off by about 1°", "A drift in the beam output", "A sag of the gantry at the test angle"],
       f"A step at one leaf pair in every strip points to that leaf, through its calibration or its drive. A collimator rotation tilts every line, a gantry sag shifts every leaf, and an output drift changes the darkness of the strips, not their position. The offset also exceeds the {mm(MLC)} IMRT tolerance, so the leaf is repaired before further IMRT.", lvl="Moderate"),
    SORT("Match each test to the fault it finds.", ["Picket fence", "Starshot", "Winston–Lutz test", "Daily output check", "Light and radiation field check"],
         [("A leaf that stops short of its planned position", 0), ("A gantry rotation axis that moves by more than 1 mm", 1), ("A radiation isocenter offset from a ball bearing at the isocenter", 2), ("A change in the response of the monitor chamber", 3), ("A light field shifted from the radiation field", 4)],
         "A picket fence shows a leaf out of position, a starshot measures the size of a rotation isocenter, and a Winston–Lutz test measures the offset between the radiation isocenter and a ball bearing. The output check finds a change in the monitor chamber, and the light and radiation field check finds a misaligned light field.", lvl="Moderate", mode="match", cap=1),
    PRN(STEM("A sliding-window field. The dose at a point goes as the effective width of the gap, the nominal gap plus the dosimetric leaf gap.", [f"nominal gap = {s_nom:g} mm", f"dosimetric leaf gap = {s_dlg:g} mm", f"error = one bank opens every gap by {s_err:g} mm"], "By what [[percentage]] does the dose through the gap change?"),
        s_gap, [s_nodlg, s_both, 0.0], "{:.1f}%",
        f"The effective gap is {s_nom:g} + {s_dlg:g} = {s_nom + s_dlg:g} mm, and one bank opens it by {s_err:g} mm, so the dose rises by {s_err:g} / {s_nom + s_dlg:g} = {s_gap:.1f}%. Leaving out the leaf gap gives {s_nodlg:.1f}%, counting the error on both banks gives {s_both:.1f}%, and treating it as a shift gives 0.", lvl="Moderate"),
    PR(STEM(f"A sliding-window field has an effective gap of {b_g:g} mm. QA finds both leaf banks displaced by {b_e:g} mm in the same direction.", ask="What is the effect on the dose that the gap delivers?"),
       f"The same dose, displaced by {b_e:g} mm", [f"A dose {b_one:.0f}% higher, in the same place", f"A dose {b_two:.0f}% higher, in the same place", f"A dose {b_one:.0f}% lower, in the same place"],
       f"The gap keeps its {b_g:g} mm width, so every point receives the same dose, displaced by {b_e:g} mm. An error in one bank alone would change the gap by {b_e:g} mm and the dose by {b_e:g} / {b_g:g} = {b_one:.0f}%, and adding the two shifts as if they widened the gap gives {b_two:.0f}%.", lvl="Challenging"),
    # ---- 14-20: patient-specific QA
    PR(STEM(ask=f"In a gamma analysis at {DD:g}%/{DTA:g} mm, what does γ ≤ 1 at a measured point mean?"), f"A calculated point lies inside the {DD:g}%, {DTA:g} mm ellipse", [f"The dose difference at the same position is below {DD:g}%", "The measured and calculated doses differ by less than 1%", "The nearest calculated point is less than 1 mm away"],
       f"γ is the smallest combined distance, in units of the two criteria, from the measured point to any calculated point. A dose difference below {DD:g}% at the same position is only one way to pass, and γ is a ratio to the criteria, not a percentage or a distance.", lvl="Easy"),
    PRN(STEM(f"A planar comparison at {DD:g}%/{DTA:g} mm with global normalization. For one measured point, the calculated point with the smallest Γ is described below.", [f"distance from the measured point = {q_r:.1f} mm", f"dose difference = {q_d:.1f}% of the maximum dose"], "What is [[γ]] at the measured point?"),
        q_gam, [q_d / DD, q_r / DTA, q_d / DD + q_r / DTA, (q_r / DTA) ** 2 + (q_d / DD) ** 2], "{:.2f}",
        f"Γ = √[({q_r:.1f}/{DTA:g})² + ({q_d:.1f}/{DD:g})²] = √({(q_r / DTA) ** 2:.2f} + {(q_d / DD) ** 2:.2f}) = {q_gam:.2f}, so the point passes. The dose term alone gives {q_d / DD:.2f} and the distance term alone {q_r / DTA:.2f}; adding the two ratios gives {q_d / DD + q_r / DTA:.2f}, and leaving out the square root gives {(q_r / DTA) ** 2 + (q_d / DD) ** 2:.2f}.", lvl="Moderate"),
    PR(STEM(f"A planar comparison at {DD:g}%/{DTA:g} mm with a {THR:g}% threshold. At one measured point in a low-dose region, the calculated point at the same position gives the smallest Γ.", [f"dose at the point = {100 * loc_p:g}% of the maximum dose", f"calculated minus measured = {loc_d:g}% of the maximum dose"], "How does the point fare under global and under local normalization?"),
       "It passes with global normalization and fails with local", ["It fails with global normalization and passes with local", "It passes with both normalizations", "It fails with both normalizations"],
       f"Globally the difference is {loc_d:g}% of the maximum, a third of the {DD:g}% criterion, so γ = {loc_gg:.2f}. Locally it is {loc_d:g} / {loc_p:.2f} = {loc_pct:.1f}% of the dose at the point, so γ = {loc_gl:.2f} and the point fails. At {100 * loc_p:g}% of the maximum the point lies above the {THR:g}% threshold and is evaluated.", lvl="Moderate"),
    PRN(STEM(f"A VMAT plan is measured with a diode array and compared at {DD:g}%/{DTA:g} mm, global normalization, and a {THR:g}% low-dose threshold.", [f"diodes in the array = {n_all:,}", f"diodes above {THR:g}% of the maximum dose = {n_eval:,}", f"evaluated diodes with γ > 1 = {n_fail}"], "What is the [[passing rate]]?"),
        n_rate, [n_all_den, n_low_pass, n_failpct], "{:.1f}%",
        f"Passing = {n_eval:,} − {n_fail} = {n_eval - n_fail:,} of {n_eval:,} evaluated points, {n_rate:.1f}%, above the {TL:g}% tolerance limit. Dividing by all {n_all:,} diodes gives {n_all_den:.1f}%, counting the low-dose diodes as passing gives {n_low_pass:.1f}%, and {n_failpct:.1f}% is the fraction that fails.", lvl="Challenging"),
    PR(STEM(f"A VMAT plan for a lung tumour passes patient-specific QA with 99% of points at γ ≤ 1 ({DD:g}%/{DTA:g} mm), measured in a homogeneous cylindrical phantom.", ask="Which conclusion does this result support?"),
       "The machine delivers the plan as calculated in the phantom", [f"The calculated dose in the patient's lung is accurate to {DD:g}%", "The target contour and the prescription are correct", f"The patient will be set up within {DTA:g} mm"],
       "Patient-specific QA compares delivery with calculation in the phantom. A homogeneous phantom does not test the calculation in lung, and the contours, the prescription, and the patient's setup are not part of the measurement.", lvl="Challenging"),
    PRM(STEM("A VMAT plan fails its patient-specific QA measurement.", ask="Which of these could cause the failure?"),
        ["A leaf-bank calibration error on the linac", "An error in the leaf gap modelled by the planning system", "A misplaced phantom or a miscalibrated detector"],
        ["A prescription dose entered wrongly in the plan", "A target contour drawn too small", "A patient setup error on the first day"],
        "QA compares the measured dose with the dose calculated for that plan, so a fault in the delivery, the beam model, or the measurement shows up. A wrong prescription or contour is part of both the plan and its calculation, so the two still agree, and the patient's setup is not part of the test.", lvl="Moderate"),
    # ---- 21-22: commissioning and the planning system
    PR(STEM("The planning system receives a software upgrade.", ask="Which check confirms that its dose calculations have not changed?"),
       "Recalculating stored reference plans", ["Running each linac's daily output check", "Measuring QA for the next plan only", "Repeating each linac's acceptance tests"],
       "Recalculating stored reference plans with the new version shows whether the calculation changed. Linac checks test the machine, not the planning software, and one patient's QA covers only one plan.", lvl="Easy"),
]

INLINE = {0: [1], 1: [2, 3, 6, 8, 10], 2: [12, 13, 14, 15]}

TERMS = ["acceptance testing", "commissioning", "baseline", "tolerance", "action level", "picket fence", "gamma index", "end-to-end test"]

TAKE = [
    ["Acceptance testing checks the purchase specification, commissioning measures the beam data and sets the baseline, and periodic QA checks for drift from the baseline.",
     "TG-142 grades the response: inspection within tolerance, scheduled action at or slightly beyond it, immediate action (stop treatment) for a failed interlock or a large error."],
    [f"TG-142 output constancy: {OUT_D:g}% daily and {OUT_M:g}% monthly; annual calibration {OUT_A:g}%.",
     f"Lasers {mm(LAS[0])} daily ({mm(LAS[2])} for SRS/SBRT); MLC leaf position {mm(MLC)} monthly, with a weekly picket fence.",
     "An error Δx in one leaf bank changes the dose through a gap of effective width g by Δx/g."],
    ["γ is the smallest Γ = √[(Δr/Δd)² + (δ/ΔD)²] over the calculated points; a point passes when γ ≤ 1.",
     f"TG-218: {DD:g}%/{DTA:g} mm, global normalization, {THR:g}% threshold; tolerance limit {TL:g}%, action limit {AL:g}%.",
     "A pass shows that the plan is delivered as calculated in a phantom, not that the patient's dose is right."],
    ["A large chamber widens the measured penumbra and lowers small-field output, and the error enters every plan.",
     "End-to-end tests check the whole chain; recalculated reference plans check the planning system after upgrades."],
]
