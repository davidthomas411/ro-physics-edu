from blocks import *
import math

# ---------------------------------------------------------------- helpers: risk numbers and the NRC medical event tests
def rpn(o, s, d):
    """Risk priority number of a failure mode: occurrence × severity × lack of detectability, each scored 1 to 10."""
    return o * s * d

def p_and(*p):
    """AND gate: the probability that every one of several independent events occurs."""
    return math.prod(p)

def p_or(*p):
    """OR gate: the probability that at least one of several independent events occurs."""
    return 1 - math.prod(1 - x for x in p)

def residual(p0, *det):
    """Error rate left after independent checks, each detecting the fraction det of the errors that reach it."""
    return p0 * math.prod(1 - d for d in det)

def dev(delivered, intended):
    """Deviation from the intended dose or dosage, in percent of the intended value."""
    return 100 * (delivered - intended) / intended

ME_TOTAL, ME_FRAC = 20, 50          # 10 CFR 35.3045: total dose or dosage 20% or more from the written directive; one fraction 50% or more
ME_SV = 0.5                         # Sv to an organ or tissue (with 0.05 Sv effective dose and 0.5 Sv shallow dose to the skin)
ME_SITE = 50                        # a site outside the treatment site: 0.5 Sv or more and 50% or more above its expected dose
TJC = 25                            # Joint Commission sentinel event: radiotherapy more than 25% above the planned dose
REPORT_DAYS, TELL_HOURS = 15, 24    # written report to the NRC; telling the referring physician and the patient

def me_course(delivered, per_fraction):
    """Medical event test for a fractionated course of photons (1 Gy = 1 Sv): the total 20% or more from the written directive,
    or one fraction 50% or more from its prescribed dose, with the dose differing by more than 0.5 Sv."""
    total, presc = sum(delivered), per_fraction * len(delivered)
    big = abs(total - presc) > ME_SV or any(abs(f - per_fraction) > ME_SV for f in delivered)
    return big and (abs(dev(total, presc)) >= ME_TOTAL or any(abs(dev(f, per_fraction)) >= ME_FRAC for f in delivered))

def me_site(received, expected):
    """Medical event test for a site outside the treatment site: 0.5 Sv or more and 50% or more above the expected dose."""
    return received - expected >= ME_SV and dev(received, expected) >= ME_SITE

# ---------------------------------------------------------------- worked examples (scores and probabilities illustrative)
FA = ("Bolus left off for one fraction", 6, 4, 5)
FB = ("Wrong source strength entered after an HDR source exchange", 2, 9, 6)
ra, rb = rpn(*FA[1:]), rpn(*FB[1:])
a1, m1, a2, m2 = 0.01, 0.2, 0.002, 0.5                      # fault tree: error and miss probabilities per plan on two branches
b1, b2 = p_and(a1, m1), p_and(a2, m2); top = p_or(b1, b2)
e0, d1, d2 = 0.005, 0.80, 0.60                              # error rate before the checks; detection probability of each check
r1, r2 = residual(e0, d1), residual(e0, d1, d2)
hp, hn, hx = 7.0, 3, 10.8                                   # HDR: Gy per fraction, fractions, dose delivered in fraction 2
h_del = [hp, hx, hp]; h_fd = dev(hx, hp); h_tot = sum(h_del); h_td = dev(h_tot, hp * hn); h_me = me_course(h_del, hp)
assert ra > rb and FB[2] > FA[2] and h_me and h_td < ME_TOTAL <= ME_FRAC <= h_fd

TOPIC = dict(
    id="risk-management", domain=7, sub="VII.C", title="Risk management and TG-100",
    ref=dict(aapm="TG-100", khan="", ford="28"),
    guide=[
        H("Risk-based quality management"),
        P("A prescriptive QA program runs a fixed list of device tests, as TG-142 does for linacs. It weighs every failure alike and ignores the clinic's own process, where many events start: a step left out, an order misread, data copied wrongly. AAPM Task Group 100 (2016) sets out a risk-based alternative. A team from every profession involved maps each step from the consultation to the last fraction, finds each failure mode (each way a step can fail), ranks the failures by risk, and puts the quality-management effort where the risk is highest."),
        P("TG-100 ranks quality-management tools by strength, following the Institute for Safe Medication Practices:"),
        OL("A forcing function or interlock makes the error impossible: the beam is held until the applicator code matches the plan.",
           "Automation: plan parameters reach the machine without retyping.",
           "Protocols and standards: one approved template per site.",
           "Independent checks and checklists.",
           "Rules and policies, such as a required time-out.",
           "Education and training."),
        P("The weaker tools rely on a person catching the problem every time, and attention fades with routine, fatigue, and time pressure; a warning that appears often is dismissed. A forcing function works whether or not anyone is paying attention."),

        H("FMEA and fault trees"),
        P("A failure mode and effects analysis (FMEA) works forward from each step of the process map, recording each failure mode with its causes and its effect on the patient and scoring it three ways from 1 to 10."),
        TABLE(["Score", "Rates", "1", "10"], [
            ["O, occurrence", "how often the failure happens", "rare, about 1 in 10,000", "frequent"],
            ["S, severity", "harm if the failure is not caught", "no effect", "catastrophic"],
            ["D, lack of detectability", "chance the failure passes undetected", "easily detected", "hard to detect"]]),
        EQ("RPN = O × S × D   (from 1 to 1000)"),
        P("The scores are a team's judgments, so the risk priority number (RPN) ranks failure modes within one analysis and is not an absolute risk; numbers from different teams or scales cannot be compared. A product can also rank a rare catastrophic failure low, since a high S with a low O gives a modest RPN. TG-100 advises against ranking by RPN alone, so a high severity is also reviewed on its own."),
        EX("Ranking two failure modes", STEM("Two failure modes from an FMEA, with scores agreed by the team.", [f"{FA[0][0].lower() + FA[0][1:]}: O = {FA[1]}, S = {FA[2]}, D = {FA[3]}", f"{FB[0][0].lower() + FB[0][1:]}: O = {FB[1]}, S = {FB[2]}, D = {FB[3]}"], "Find the [[RPN of each]] and rank the two by RPN and by severity."),
           [f"{FA[0]}: RPN = {FA[1]} × {FA[2]} × {FA[3]} = {ra}", f"{FB[0]}: RPN = {FB[1]} × {FB[2]} × {FB[3]} = {rb}", f"By RPN the bolus error ranks first ({ra} against {rb}); by severity the source-strength error ranks first ({FB[2]} against {FA[2]})"],
           f"{ra} and {rb}. The source-strength error is reviewed first despite its lower RPN: a wrong strength affects every treatment given with that source until it is found."),
        P("A fault tree works backward from one unwanted outcome, the top event, to the combinations of failures that cause it. An AND gate passes a failure upward only if all of its inputs occur; an OR gate passes it if any input occurs. For independent events:"),
        EQ("AND gate:   P = p₁ × p₂ × …", "OR gate:   P = 1 − (1 − p₁)(1 − p₂) …   ≈ p₁ + p₂ + … when every p is small"),
        P("A check enters the tree as one more AND input, the probability that it misses the error. Checks that share information or trust each other are not independent, so the product is a best case."),
        EX("Probability of a top event", STEM("A top event, a wrong dose reaching the patient, sits on an OR gate with two independent branches, each an AND gate (probabilities per plan).", [f"branch 1, a dose-calculation error: p = {a1:g}", f"branch 1, the physics plan check misses it: p = {m1:g}", f"branch 2, the wrong plan version is sent to the machine: p = {a2:g}", f"branch 2, the therapist's check misses it: p = {m2:g}"], "Find the [[probability of the top event]]."),
           [f"Branch 1: {a1:g} × {m1:g} = {b1:.3f}", f"Branch 2: {a2:g} × {m2:g} = {b2:.3f}", f"OR gate: P = 1 − (1 − {b1:.3f})(1 − {b2:.3f}) = {top:.6f}"],
           f"{top:.4f}, about {top * 1000:.0f} plans in 1000. The sum of the branches, {b1 + b2:.3f}, is almost the same because both are small."),
        EX("Error rate after two checks", STEM("Errors enter treatment plans before two independent checks.", [f"error rate before the checks = {e0 * 100:g}% of plans", f"detected by the physics plan check = {d1 * 100:.0f}% of errors", f"detected by the therapist's check at the first treatment = {d2 * 100:.0f}%"], "Find the [[error rate after one check and after both]]."),
           [f"After the physics check: {e0:g} × (1 − {d1:.2f}) = {r1:.4f}", f"After the therapist's check: {r1:.4f} × (1 − {d2:.2f}) = {r2:.4f}"],
           f"{r1:.4f} (1 in {1 / r1:,.0f} plans) after one check and {r2:.4f} (1 in {1 / r2:,.0f}) after both. Checks that are not independent leave a higher rate."),

        H("Incident learning and root cause analysis"),
        P("An error is a planned action not carried out as intended, or a wrong plan. In RO-ILS terms, a safety event that does not reach the patient is a near miss, one that does is an incident, with or without harm, and a circumstance that makes an event more likely is an unsafe condition. Near misses are analyzed like incidents, at no cost to a patient."),
        P("In a safety culture reporting is safe: no name is needed, reporters hear what changed, and honest error is not punished. A just culture keeps accountability by behavior: human error is consoled, at-risk behavior (a shortcut whose risk was not recognized) is coached, and reckless behavior (conscious disregard of a substantial risk) is sanctioned. RO-ILS, a voluntary national system launched in 2014 by ASTRO and the AAPM, keeps reports confidential and privileged through a patient safety organization."),
        P("In Reason's Swiss cheese model every layer of defense has holes, and an incident reaches the patient only when the holes line up. Recurring failures include communication and data transfer, a wrong patient or site, a plan changed after its check, and a required step not done."),
        P("A root cause analysis builds a timeline, sorts causes on a fishbone diagram (people, equipment, procedures, communication, environment), and asks why repeatedly (the five whys) until it reaches a cause in the system rather than a person. A root cause is one whose removal would have prevented the event; a contributing factor made it more likely or worse. Stronger actions change the system (a forcing function, simplification, standardization), intermediate ones add redundancy or a checklist, and weaker ones rely on people (training, a policy, a warning)."),

        H("Medical events and disclosure"),
        P("A medical event is an error in an administration of byproduct material (brachytherapy sources, Gamma Knife cobalt units, therapeutic radiopharmaceuticals) that crosses the limits of 10 CFR 35.3045. Agreement States apply rules of the same form. Linacs use no byproduct material; the states regulate them, and their reporting rules differ. Each delivery is judged against the written directive, dated and signed by an authorized user beforehand; for HDR it gives the radionuclide, site, dose per fraction, number of fractions, and total dose."),
        TABLE(["Event", "Medical event when"], [
            ["Total dose or dosage", f"it differs from the written directive by {ME_TOTAL}% or more"],
            ["One fraction", f"its dose differs from the prescribed fraction dose by {ME_FRAC}% or more"],
            ["Wrong patient, radioactive drug, radionuclide, route, or mode of treatment, or a leaking sealed source", f"the dose exceeds 0.05 Sv effective dose, {ME_SV} Sv to an organ or tissue, or {ME_SV} Sv shallow dose to the skin"],
            ["Dose to a site outside the treatment site", f"it exceeds the expected dose there by {ME_SV} Sv or more and by {ME_SITE}% or more"]]),
        P("The first two rows also need the dose to differ from the prescribed dose by more than those amounts, which a therapeutic error passes easily. An event caused by the patient's own action is reported only if a physician judges that it causes permanent functional damage. Permanent seed implants have separate criteria."),
        P(f"After discovery the licensee telephones the NRC Operations Center by the next calendar day and sends a written report within {REPORT_DAYS} days, without the patient's name. The referring physician and the patient are told within {TELL_HOURS} hours, unless the referring physician will tell the patient or judges that telling would be harmful. A report to an incident learning system is voluntary and does not replace the regulatory report. The Joint Commission counts radiotherapy to the wrong patient or body region, or more than {TJC}% above the planned dose, as a sentinel event, which calls for a root cause analysis and an action plan."),
        EX("A wrong fraction dose", STEM("An HDR vaginal-cuff course is given under a written directive.", [f"written directive = {hp:g} Gy × {hn} fractions = {hp * hn:g} Gy", f"fraction 2 delivered = {hx:g} Gy", "fractions 1 and 3 = as prescribed"], "Find the [[percentage deviation of the fraction and of the course]], and decide whether the error is a medical event under 10 CFR 35.3045."),
           [f"Fraction: ({hx:g} − {hp:g}) / {hp:g} = +{h_fd:.1f}%", f"Course: {hp:g} + {hx:g} + {hp:g} = {h_tot:g} Gy, and ({h_tot:g} − {hp * hn:g}) / {hp * hn:g} = +{h_td:.1f}%",
            f"The course is under the {ME_TOTAL}% limit, but the fraction is over {ME_FRAC}%, and its excess of {hx - hp:.1f} Gy is more than {ME_SV} Sv"],
           f"{'A medical event' if h_me else 'Not a medical event'}, under the single-fraction criterion."),
    ],
    cards=[
        F("TG-100 approach", "A team maps the treatment process, finds the failure modes of each step, ranks them by risk, and puts the quality-management effort where the risk is highest."),
        F("Quality-management tools by strength", "Strongest to weakest: forcing functions and interlocks, automation, protocols and standards, independent checks and checklists, rules and policies, training."),
        F("Forcing function", "A design that makes the error impossible, such as an interlock that holds the beam until the electron applicator code matches the plan."),
        F("FMEA scores", ["O, occurrence: how often the failure happens.", "S, severity: how harmful its effect is.", "D, lack of detectability: how likely the failure is to pass undetected.", "Each is scored from 1 to 10."]),
        F("Risk priority number", "RPN = O × S × D, from 1 to 1000. It ranks failure modes within one analysis and is not an absolute risk."),
        F("Ranking by RPN alone", "A rare catastrophic failure can have a modest RPN, so failure modes are also sorted by severity, and a high severity is reviewed on its own.",
          w=[f"{FA[0]}: {FA[1]} × {FA[2]} × {FA[3]} = {ra}, with S = {FA[2]}.", f"{FB[0]}: {FB[1]} × {FB[2]} × {FB[3]} = {rb}, with S = {FB[2]}."]),
        F("FMEA against fault-tree analysis", "FMEA works forward from each process step to its effects. A fault tree works backward from one unwanted outcome to the failures that cause it."),
        F("Fault-tree gates", ["AND: every input is needed, so P = p₁ × p₂ × …", "OR: any input is enough, so P = 1 − (1 − p₁)(1 − p₂) …, close to the sum when every p is small."]),
        F("Error rate after independent checks", "The starting rate × (1 − d₁)(1 − d₂) …, where d is the detection probability of each check. Checks that share information are not independent.",
          w=[f"{e0:g} × (1 − {d1:.2f}) = {r1:.4f} after one check.", f"{r1:.4f} × (1 − {d2:.2f}) = {r2:.4f} after two."]),
        F("Near miss, incident, and unsafe condition", "A near miss does not reach the patient. An incident does, with or without harm. An unsafe condition makes an event more likely."),
        F("Just culture", "Human error is consoled, at-risk behavior is coached, and reckless behavior is sanctioned."),
        F("Swiss cheese model", "Every layer of defense has holes. An incident reaches the patient only when the holes in every layer line up."),
        F("Root cause analysis", "A timeline, a fishbone diagram, and the five whys lead to causes in the system. Stronger actions change the system; retraining alone is a weak action."),
        F("NRC medical event criteria", [f"Total dose or dosage {ME_TOTAL}% or more from the written directive.", f"One fraction {ME_FRAC}% or more from its prescribed dose.", "Wrong patient, drug, radionuclide, route, or mode, or a leaking source.",
                                        f"A site outside the target {ME_SV} Sv and {ME_SITE}% or more above its expected dose."]),
        F("Medical event deadlines", f"The NRC by telephone by the next calendar day, a written report within {REPORT_DAYS} days, and the referring physician and the patient within {TELL_HOURS} hours."),
        F("Linac errors and the NRC", "The NRC medical event rule covers byproduct material only. The states regulate linacs, and their reporting rules differ."),
    ],
)

# ---------------------------------------------------------------- numbers behind the questions
q_o, q_s, q_d = 4, 8, 3; q_rpn = rpn(q_o, q_s, q_d)                                  # RPN, with the classic slips as distractors
EQA, EQB = (2, 10, 6), (6, 4, 5); assert rpn(*EQA) == rpn(*EQB)                      # two failure modes with the same RPN
c1, k1, c2, k2 = 0.005, 0.80, 0.0005, 0.90                                           # fault tree: rates per fraction and the detection probability of each check
ft = 100 * p_or(c1 * (1 - k1), c2 * (1 - k2)); ft_det = 100 * p_or(c1 * k1, c2 * k2); ft_none = 100 * p_or(c1, c2); ft_one = 100 * c1 * (1 - k1)
g0, g1, g2 = 0.02, 0.70, 0.60                                                        # two checks on a 2% error rate
g_res = 1000 * residual(g0, g1, g2); g_one = 1000 * residual(g0, g1); g_det = 1000 * g0 * g1 * g2; g_pair = 1000 * residual(g0, g1 * g2)
w0, w1, w2 = 0.002, 0.1, 0.05; w_ppm = 1e6 * p_and(w0, w1, w2)                       # wrong patient: three independent failures in one fraction
y_n, y0, y1, y2 = 1200, 0.01, 0.75, 0.60; y_res = y_n * residual(y0, y1, y2)          # undetected errors per year
i_rx, i_giv = 555, 740; i_dev = dev(i_giv, i_rx)                                     # I-131 dosage in MBq
s_exp = 0.6; s_thr = max(s_exp + ME_SV, s_exp * (1 + ME_SITE / 100))                 # wrong-site criterion: both conditions must hold
assert me_site(s_thr, s_exp) and not me_site(s_thr - 0.01, s_exp)
q8p, q8n, q8x = 6.0, 5, 9.6; q8_del = [q8p, q8p, q8x, q8p, q8p]                     # HDR course with one wrong fraction
q8_fd, q8_td = dev(q8x, q8p), dev(sum(q8_del), q8p * q8n); assert me_course(q8_del, q8p) and q8_td < ME_TOTAL
lin_over = 30                                                                        # a linac course 30% high: outside the NRC rule
# five errors for the select-two question: (option, is it a medical event under 10 CFR 35.3045)
_hdr_u = [7.0, 7.0, 2.4]; _hdr_o = [7.8, 6.0, 6.0, 6.0, 6.0]
ME_CASES = [
    (f"An HDR course delivers {abs(dev(sum(_hdr_u), 21.0)):.0f}% less than its written directive", me_course(_hdr_u, 7.0)),
    ("A Gamma Knife treatment is given to the wrong side of the brain", me_site(18.0, 1.0)),
    (f"A linac course delivers {lin_over}% more than its prescription", False),
    (f"One HDR fraction is {dev(7.8, 6.0):.0f}% high and the course {dev(sum(_hdr_o), 30.0):.0f}% high", me_course(_hdr_o, 6.0)),
    (f"An I-131 therapy dosage is {dev(4255, 3700):.0f}% above its written directive", abs(dev(4255, 3700)) >= ME_TOTAL),
]

PROBLEMS = [
    # risk-based quality management
    PR(STEM("After a near miss in which an electron field was nearly treated with the wrong applicator, four changes are proposed.", [], "Which change is the [[strongest]]?"),
       "An interlock that holds the beam until the applicator code matches the plan", ["A checklist item to confirm the applicator before each field", "Retraining all therapists on the electron setup procedure", "A sign at the console reminding staff to check the applicator"],
       "An interlock is a forcing function: the wrong applicator cannot be used whether or not anyone is paying attention. A checklist and a sign depend on a person reading them and acting every time, and retraining leaves the process unchanged.", lvl="Easy"),
    SORT("Rank these quality-management tools from strongest to weakest.", ["1, strongest", "2", "3", "4", "5, weakest"],
         [("An interlock that holds the beam", 0), ("Electronic transfer of the plan to the machine", 1), ("A standard template for each treatment site", 2), ("An independent second check of the plan", 3), ("A training session for the staff", 4)],
         "TG-100, following the Institute for Safe Medication Practices, ranks forcing functions first, then automation, protocols and standards, independent checks, rules and policies, and training. The weaker a tool, the more it depends on a person acting correctly every time.", lvl="Moderate", mode="rank", cap=1),
    # FMEA and fault trees
    PR(STEM("A team scores failure modes on the TG-100 scales of 1 to 10.", [], "What does a [[detectability score of 10]] mean?"),
       "The failure is among the hardest to detect", ["The failure is among the easiest to detect", "The failure has the most harmful effect", "The failure happens most often"],
       "D scores the lack of detectability, the chance that a failure passes unnoticed, so 10 is the hardest to detect. Reading it as the ease of detection inverts the scale, harm is S, and frequency is O.", lvl="Easy"),
    PR(STEM("Before a new technique starts, a team takes one unwanted outcome, a wrong dose reaching the patient, and works backward to the combinations of failures that could produce it.", [], "Which [[method]] is this?"),
       "Fault-tree analysis", ["Failure mode and effects analysis", "Root cause analysis", "Process mapping"],
       "A fault tree starts from the top event and works down through AND and OR gates. FMEA works forward from each process step to its effects, and a root cause analysis looks back at an event that has already happened.", lvl="Easy"),
    PRN(STEM("A failure mode is scored on the TG-100 scales.", [f"O = {q_o}", f"S = {q_s}", f"D = {q_d}"], "What is its [[risk priority number]]?"), q_rpn, [q_o + q_s + q_d, q_o * q_s, rpn(q_o, q_s, 11 - q_d)], "{:.0f}",
        f"RPN = O × S × D = {q_o} × {q_s} × {q_d} = {q_rpn}. Adding the scores gives {q_o + q_s + q_d}, leaving out D gives {q_o * q_s}, and inverting the detectability scale (11 − D = {11 - q_d}) gives {rpn(q_o, q_s, 11 - q_d)}.", lvl="Moderate"),
    PR(STEM("Two failure modes from one FMEA have the same RPN.", [f"failure mode 1: O = {EQA[0]}, S = {EQA[1]}, D = {EQA[2]}", f"failure mode 2: O = {EQB[0]}, S = {EQB[1]}, D = {EQB[2]}"], "Which is [[addressed first]], and why?"),
       "Failure mode 1, because its effect is catastrophic", [f"Failure mode 2, because it occurs {NUMW[EQB[0] // EQA[0]]} times as often", "Either one, because equal RPNs mean equal risk", "Failure mode 2, because its detectability score is lower"],
       f"Both give RPN = {rpn(*EQA)}, but a severity of {EQA[1]} is reviewed on its own whatever the product. The RPN only ranks, so equal products do not mean equal risk, and a lower D means the failure is easier to catch, which lowers its priority.", lvl="Moderate"),
    PRN(STEM("Errors enter treatment plans before two independent checks.", [f"error rate before the checks = {g0 * 100:g}% of plans", f"detected by the physics plan check = {g1 * 100:.0f}%", f"detected by the therapist's check = {g2 * 100:.0f}%"], "What [[error rate]] reaches the patient?"),
        g_res, [g_one, g_det, g_pair], "{:.1f} per 1000 plans",
        f"Each check passes the fraction it misses: {g0:g} × {1 - g1:.2f} × {1 - g2:.2f} = {g_res / 1000:.4f}, or {g_res:.1f} per 1000 plans. Stopping after the first check gives {g_one:.1f}, multiplying by the detection probabilities gives {g_det:.1f}, and treating the pair as one check that detects {g1:.1f} × {g2:.1f} gives {g_pair:.1f}.", lvl="Moderate"),
    TYPED(STEM("Treating the wrong patient needs three independent failures in one fraction.", [f"another patient's plan is opened: p = {w0:g}", f"the photo check misses it: p = {w1:g}", f"the time-out misses it: p = {w2:g}"], "What is the [[probability of treating the wrong patient]], per million fractions?"),
          w_ppm, 0.01, "per million fractions",
          f"An AND gate multiplies: {w0:g} × {w1:g} × {w2:g} = {w_ppm / 1e6:.5f}, or {w_ppm:.0f} per million fractions. Each independent barrier multiplies the rate by its miss probability.", lvl="Moderate"),
    # incident learning and root cause analysis
    PR(STEM("Before the first fraction, a therapist finds that the plan loaded at the machine is an earlier version than the one the physician approved. The treatment is held and the approved plan is delivered.", [], "What [[response]] fits best?"),
       "A report to the incident learning system and an analysis of how the unapproved version reached the machine", ["No report, because the error did not reach the patient", "A report to the NRC as a medical event within a day", "A disciplinary review of the planner who exported the plan"],
       "The event is a near miss: it did not reach the patient but exposed a weak point in plan transfer, so it is reported and analyzed like an incident. No wrong dose was delivered, so there is nothing for a regulator, and punishing an honest error discourages reporting.", lvl="Moderate"),
    PR(STEM("A root cause analysis uses the five whys.", [], "When does the [[questioning stop]]?"),
       "When it reaches a cause in the system that can be changed", ["When a person responsible for the error is named", "When exactly five answers have been recorded", "When the first cause that explains the event is found"],
       "The aim is a cause in the system whose removal prevents a repeat. Stopping at a person or at the first plausible cause leaves the process unchanged, and the number five is approximate.", lvl="Easy"),
    PRM(STEM("A department sets up an incident learning system.", [], "Which of these features make staff more likely to report?"),
        ["Reports can be made without giving a name", "Reporters hear what changed as a result"],
        ["Each report starts a review of the reporter's performance", "Only events that harmed a patient are accepted", "Each report is sent to the regulator as a medical event"],
        "Anonymity, no punishment for honest error, and visible feedback encourage reporting. Reviewing the reporter discourages it, accepting only harm throws away the near misses, and a learning report is separate from any regulatory report.", lvl="Moderate"),
    PR(STEM("On a busy afternoon a therapist skips the required time-out for a patient on the twentieth fraction, judging it unnecessary because the setup is familiar. Nothing goes wrong.", [], "In a model that separates human error, at-risk behavior, and reckless behavior, which [[response]] fits?"),
       "Coaching, because the shortcut is at-risk behavior whose risk was not recognized", ["Sanction, because any departure from a written procedure is reckless", "Consolation only, because the therapist made an honest error", "No response, because the treatment caused no harm"],
       "Skipping a step by choice, without seeing the risk, is at-risk behavior, and the response is coaching and a look at why the shortcut seemed reasonable. Reckless behavior is a conscious disregard of a substantial risk; an honest error is unintended, whereas this omission was a choice; and judging by the outcome ignores the risk that was taken.", lvl="Challenging"),
    # medical events and disclosure
    PR(STEM("A licensee discovers a medical event in an HDR treatment.", [], "Which set of [[deadlines]] applies?"),
       f"NRC by telephone by the next calendar day; written report within {REPORT_DAYS} days; physician and patient within {TELL_HOURS} hours",
       [f"NRC by telephone within {REPORT_DAYS} days; written report within 30 days; physician and patient within {TELL_HOURS} hours", f"NRC by telephone by the next calendar day; written report within {REPORT_DAYS} days; patient told only if harmed",
        f"NRC in writing within 30 days; no telephone report; physician and patient within {REPORT_DAYS} days"],
       f"The NRC Operations Center is called by the next calendar day and the written report follows within {REPORT_DAYS} days. The referring physician and the patient are told within {TELL_HOURS} hours, whether or not there was harm, unless the referring physician will tell the patient or judges that telling would be harmful.", lvl="Easy"),
    PR(STEM(f"A planning error on a linac delivers a total dose {lin_over}% above the prescription.", [], "Which [[rules]] govern the regulatory report?"),
       "The state's rules, because the NRC rule covers byproduct material only", [f"10 CFR 35.3045, because the total differs by {ME_TOTAL}% or more", "None, because only brachytherapy errors are reportable", "RO-ILS rules, because they replace regulatory reports for linacs"],
       f"A linac uses no byproduct material, so the NRC medical event rule does not apply; the state regulates the machine and sets the reporting rule. The {ME_TOTAL}% test belongs to the NRC rule for brachytherapy, Gamma Knife, and radiopharmaceuticals, and a learning report does not replace a regulatory one.", lvl="Moderate"),
    PRN(STEM("A radioactive iodine therapy is given.", [f"I-131 sodium iodide in the written directive = {i_rx} MBq", f"administered = {i_giv} MBq"], "By what [[percentage]] does the administered dosage differ from the prescribed dosage?"),
        i_dev, [100 * (i_giv - i_rx) / i_giv, 100 * i_giv / i_rx, 100 * i_rx / i_giv], "{:.1f}%",
        f"({i_giv} − {i_rx}) / {i_rx} = {i_dev:.1f}%, above the {ME_TOTAL}% criterion, and the extra thyroid dose is far above {ME_SV} Sv, so it is a medical event. Dividing by the administered activity gives {100 * (i_giv - i_rx) / i_giv:.1f}%, and {100 * i_giv / i_rx:.1f}% and {100 * i_rx / i_giv:.1f}% are ratios, not differences.", lvl="Moderate"),
    PRN(STEM("During an HDR treatment an organ outside the treatment site receives more dose than the written directive implies (photons, so 1 Gy = 1 Sv).", [f"expected dose to the organ = {s_exp:g} Gy"], "What is the [[lowest dose to the organ]] that meets the wrong-site criterion of 10 CFR 35.3045?"),
        s_thr, [s_exp * (1 + ME_SITE / 100), ME_SV, s_exp + ME_SV + s_exp * ME_SITE / 100], "{:.1f} Gy",
        f"Both conditions must hold: {ME_SV} Sv or more above the expected dose ({s_exp + ME_SV:.1f} Gy) and {ME_SITE}% or more above it ({s_exp * (1 + ME_SITE / 100):.1f} Gy). The larger, {s_thr:.1f} Gy, governs. The percentage alone gives {s_exp * (1 + ME_SITE / 100):.1f} Gy, reading {ME_SV} Sv as the dose itself gives {ME_SV} Gy, and adding both increments gives {s_exp + ME_SV + s_exp * ME_SITE / 100:.1f} Gy.", lvl="Challenging"),
    PR(STEM("An HDR cervix course is given under a written directive.", [f"written directive = {q8p:g} Gy × {q8n} fractions = {q8p * q8n:g} Gy", f"fraction 3 delivered = {q8x:g} Gy", "the other fractions = as prescribed"], "Is this a [[medical event]] under 10 CFR 35.3045?"),
       f"Yes: one fraction differs by {q8_fd:.0f}%, at or above the {ME_FRAC}% limit", [f"No: the course total differs by {q8_td:.0f}%, below the {ME_TOTAL}% limit", f"Yes: the course total differs by {q8_td:.0f}%, above a 10% limit", "No: HDR afterloaders are regulated by the states"],
       f"The fraction received {q8x:g} Gy against {q8p:g} Gy, {q8_fd:.0f}% high, so the single-fraction criterion is met, and the {q8x - q8p:.1f} Gy excess is more than {ME_SV} Sv. Checking only the total ({q8_td:.0f}%) misses it, there is no 10% limit, and the Ir-192 source of an HDR unit is byproduct material under the NRC.", lvl="Challenging"),
    PRM(STEM("Five errors are found in one year.", [], "Which of these are medical events under 10 CFR 35.3045?"),
        [t for t, me in ME_CASES if me], [t for t, me in ME_CASES if not me],
        f"An HDR course {ME_TOTAL}% or more short is a medical event, because underdoses count as well as overdoses, and treating the wrong side puts far more than {ME_SV} Sv and {ME_SITE}% above the expected dose on a site outside the target. The linac is outside the NRC rule, {dev(7.8, 6.0):.0f}% in one fraction is under {ME_FRAC}% and {dev(sum(_hdr_o), 30.0):.0f}% in total under {ME_TOTAL}%, and a dosage {dev(4255, 3700):.0f}% high is under the {ME_TOTAL}% limit.", lvl="Challenging"),
]

INLINE = {0: [1, 2], 1: [3, 4, 5, 7], 2: [9, 10, 12]}

TERMS = ["failure mode", "forcing function", "risk priority number", "fault tree", "near miss", "root cause", "medical event", "written directive"]

TAKE = [
    ["TG-100: a map of the process, its failure modes ranked by risk, and the quality-management effort placed where the risk is highest.",
     "Strongest to weakest: forcing functions and interlocks, automation, protocols and standards, checks and checklists, rules and policies, training."],
    ["RPN = O × S × D, each scored 1 to 10, D being the chance that a failure goes undetected. It ranks; it is not an absolute risk, and a high S is reviewed on its own.",
     "AND gates multiply probabilities and OR gates nearly add them. Each independent check multiplies the error rate by its miss probability."],
    ["Near miss: did not reach the patient. Incident: reached the patient, with or without harm.",
     "Reporting without names or punishment; honest error consoled, at-risk behavior coached, reckless behavior sanctioned.",
     "Root cause analysis: timeline, fishbone, five whys. Stronger fixes change the system; retraining is weak."],
    [f"NRC medical event (byproduct material): total dose or dosage off by {ME_TOTAL}% or more, one fraction by {ME_FRAC}% or more, or a wrong patient, drug, route, or site.",
     f"NRC by telephone by the next calendar day, written report within {REPORT_DAYS} days, referring physician and patient within {TELL_HOURS} hours. Linacs fall under state rules."],
]
