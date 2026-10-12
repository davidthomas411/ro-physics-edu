from blocks import *
import math, calc

# ---------------------------------------------------------------- this chapter's formulas
IR_T, I_T = 73.8, 59.4                              # half-lives of Ir-192 and I-125 (d)
GAMMA_IR, WE = 4.69, 0.876                          # Γ of Ir-192 (R cm² mCi⁻¹ h⁻¹) and W/e of dry air (cGy/R), as in the exposure chapter

def p_tp(t_c, p_kpa):
    """Air-density correction of a vented chamber to 22 °C and 101.33 kPa (T in °C, P in kPa)."""
    return (273.2 + t_c) / 295.2 * 101.33 / p_kpa

def s_k(m_amp, n_sk, ptp, pion, pelec):
    """Air kerma strength (U) from a well-chamber current (A): S_K = M N_SK P_TP P_ion P_elec."""
    return m_amp * n_sk * ptp * pion * pelec

def decayed(s0, days, th=IR_T):
    """Strength left after a number of days."""
    return s0 * calc.frac_remaining(days, th)

def pct(meas, ref):
    """Percent difference of a measured value from a reference value."""
    return 100 * (meas / ref - 1)

def kerma_rate(sk, d_m):
    """Air kerma rate in free air (µGy/h) at d metres from a source of S_K units (1 U = 1 µGy m² h⁻¹)."""
    return sk / d_m ** 2

def exposure_rate(gamma, a_mci, r_cm):
    """Exposure rate (R/h) at r cm from a point source of A mCi."""
    return gamma * a_mci / r_cm ** 2

def n_hvl(reduction):
    """Half-value layers needed for a stated reduction of the rate."""
    return math.log2(reduction)

def assay_n(n_seeds):
    """Seeds assayed from one order: 10% of the seeds or 10 seeds, whichever is greater (AAPM working group, 2008)."""
    return max(math.ceil(0.10 * n_seeds), 10)

def release_dose(rate_1m, th_days, e):
    """Dose (mSv) to a person who spends the fraction e of the time at 1 m until the implant has decayed: rate × 1.44 T1/2 × e."""
    return rate_1m * calc.mean_life(th_days * 24) * e

sgn = lambda v, d=1: f"{v:+.{d}f}".replace("-", "−")

# ---------------------------------------------------------------- values quoted in the text
AIM, NRC_OUT, POS = 3.0, 5.0, 1.0                   # % agreement aimed for (MPPG 13.a, GEC-ESTRO); NRC output tolerance (%); source position (mm)
SEED_PCT, SEED_MIN, SEED_MEAN = 10, 10, 3.0         # seed sample and its mean (AAPM working group, 2008)
LEAK_BQ, LEAK_UCI, LEAK_MO = 185, 0.005, 6          # NRC leak test: limit for removable activity and interval (months)
REL, INSTR = 5.0, 1.0                               # NRC release: mSv to any other individual; instructions above this
RATE_I, RATE_PD, E_NRC = 0.01, 0.03, 0.25           # NRC Regulatory Guide 8.39 (1997): mSv/h at 1 m for I-125 and Pd-103 implants; occupancy factor at 1 m
HVL_PB, HVL_CON = 4.8, 4.5                          # illustrative half-value layers for Ir-192: lead (mm) and concrete (cm)
f90, f120 = calc.frac_remaining(90, IR_T), calc.frac_remaining(120, IR_T)

QA_ROWS = [
    ["Door interlock, warning lights, room monitor", "Daily, before the first treatment", "The source retracts when the door opens, and its state is shown"],
    ["Viewing and intercom", "Daily", "The patient can be seen and heard"],
    ["Emergency kit and survey meter", "Daily", "The response to a stuck source is ready"],
    ["Clock and decayed S<sub>K</sub> in the console", "Daily", "Dwell times are computed for the current strength"],
    ["Timer", "Daily, and at each new source", "Dwell times run as programmed, within 1% or 1 s, whichever is greater (MPPG 13.a)"],
    ["Source position", "Daily, and at each new source", f"Each dwell position within {POS:g} mm"],
    ["Source strength in a well chamber", "Each new source", f"Within {AIM:g}% of the certificate; NRC limit {NRC_OUT:g}%"],
    ["Transfer tube and applicator lengths", "Each new source, and each new applicator", "The source reaches the planned positions"],
    ["Retraction on the backup battery", "Each new source", "The source returns to its safe if the power fails"],
]

# ---------------------------------------------------------------- worked examples
m1, n1, t1, p1, ion1, el1 = 87.62e-9, 4.690e11, 23.5, 99.80, 1.003, 0.998          # a new HDR source in the well chamber
cert1, days1 = 43350.0, 5.0                                                         # certificate value and its age at the measurement
ptp1 = p_tp(t1, p1); raw1 = m1 * n1; sk1 = s_k(m1, n1, ptp1, ion1, el1)
cert1_now = decayed(cert1, days1); pct1 = pct(sk1, cert1_now)
s2, t2, days2 = 41000.0, 300.0, 60.0                                                # dwell time after decay
s2_now = decayed(s2, days2); t2_now = t2 * s2 / s2_now
a3, r3, min3 = 10000.0, 100.0, 2.0                                                  # stuck 10 Ci source, physicist at 1.0 m for 2.0 min
xr3 = exposure_rate(GAMMA_IR, a3, r3); x3 = xr3 * min3 / 60; k3 = WE * x3            # R/h, R, cGy
red4 = 1000.0                                                                       # lead shield for a factor of 1000
n4 = n_hvl(red4); t4 = n4 * HVL_PB

# ---------------------------------------------------------------- numbers in the questions
m_q, n_q, t_q, p_q, ion_q, el_q = 79.40e-9, 4.712e11, 20.0, 102.80, 1.002, 1.000     # typed well-chamber reading
ptp_q = p_tp(t_q, p_q); sk_q = s_k(m_q, n_q, ptp_q, ion_q, el_q); sk_q_notp = s_k(m_q, n_q, 1.0, ion_q, el_q)
c5, days5, m5 = 44000.0, 7.0, 42300.0                                               # certificate against measurement
c5_now = decayed(c5, days5); pct5 = pct(m5, c5_now)
w5_nodecay, w5_exp, w5_grow = pct(m5, c5), pct(m5, c5 * math.exp(-days5 / IR_T)), pct(m5, c5 / calc.frac_remaining(days5, IR_T))
c6 = 41400.0; m6 = round(c6 * 0.94); pct6 = pct(m6, c6)                             # a source 6% below its certificate
n7 = 80; seeds7 = assay_n(n7)                                                       # seeds to assay from an order of 80
s8, t8, days8 = 40800.0, 280.0, 50.0                                                # dwell time after 50 d
f8 = calc.frac_remaining(days8, IR_T); t8_now = t8 / f8
w8_lin, w8_inv, w8_exp = t8 * (1 + days8 / IR_T), t8 * f8, t8 * math.exp(days8 / IR_T)
a15, r15, min15 = 10000.0, 200.0, 3.0                                               # exposure at 2.0 m for 3.0 min
xr15 = exposure_rate(GAMMA_IR, a15, r15); x15 = 1000 * xr15 * min15 / 60            # mR
w15_1m, w15_hours, w15_ci = 1000 * exposure_rate(GAMMA_IR, a15, 100.0) * min15 / 60, 1000 * xr15 * min15, 1000 * exposure_rate(GAMMA_IR, 10.0, r15) * min15 / 60
sk16, d16, goal16 = 40000.0, 3.0, 20.0                                              # wall of an HDR room
k16 = kerma_rate(sk16, d16); r16 = k16 / goal16; n16 = n_hvl(r16); t16 = n16 * HVL_CON
w16_log10, w16_ln, w16_nod = math.log10(r16) * HVL_CON, math.log(r16) * HVL_CON, n_hvl(sk16 / goal16) * HVL_CON
r20 = 0.006                                                                          # mSv/h at 1 m after an I-125 implant
tau20 = calc.mean_life(I_T * 24); d20 = release_dose(r20, I_T, E_NRC); w20 = r20 * I_T * 24 * E_NRC

TOPIC = dict(
    id="brachy-qa", domain=5, sub="V", title="Source calibration and brachytherapy safety",
    ref=dict(aapm="TG-40, TG-56, TG-59, TG-64", khan="", ford="26"),
    guide=[
        H("Source calibration"),
        P("Each new source is measured in a well chamber before its first treatment. The reading is converted with a calibration coefficient, N<sub>SK</sub>: the air kerma strength per unit reading for one source model in one insert, set by an Accredited Dosimetry Calibration Laboratory (ADCL) with a source traceable to NIST. The NRC requires a calibration within the previous 2 years, or 4 years with an intercomparison between."),
        EQ("S<sub>K</sub> = M · N<sub>SK</sub> · P<sub>TP</sub> · P<sub>ion</sub> · P<sub>elec</sub>", "M = reading (A),   N<sub>SK</sub> in U/A,   P factors as for any vented chamber"),
        P("M is the mean current with the source at the sweet spot, the position along the axis of the well with the largest response, found by stepping the source through the insert. The coefficient applies there, and a small position error changes the reading least. A coefficient does not transfer to another model, even of the same nuclide, because the response depends on the construction and spectrum of the source."),
        P(f"The measured value is compared with the vendor's certificate, both decayed to the same time. A difference above {AIM:g}% (AAPM MPPG 13.a, GEC-ESTRO) is investigated. Above {NRC_OUT:g}%, the NRC requirement for HDR output, the source is held from clinical use until the measurement is rechecked and the cause found with the vendor."),
        P(f"For seeds, a sample of each order is assayed: at least {SEED_PCT}% (TG-40, TG-56, TG-64), or {SEED_PCT}% or {SEED_MIN} seeds, whichever is greater, with the mean within {SEED_MEAN:g}% of the vendor's value or the difference resolved (AAPM working group on low-energy sources, 2008)."),
        P(f"Dwell times scale as 1/S<sub>K</sub>: after 90 d an Ir-192 source is at {100 * f90:.0f}% of its strength and a fraction takes {1 / f90:.1f} times as long, so HDR sources are replaced about every 3 to 4 months."),
        EX("Air kerma strength of a new HDR source", STEM("A new Ir-192 HDR source is measured at the sweet spot of a vented well chamber.",
           ["mean reading M = 87.62 nA", "N<sub>SK</sub> = 4.690 × 10<sup>11</sup> U/A for this source model", "temperature = 23.5 °C,   pressure = 99.80 kPa", "P<sub>ion</sub> = 1.003,   P<sub>elec</sub> = 0.998",
            "certificate = 43,350 U, dated 5.0 d before the measurement", "T<sub>1/2</sub> = 73.8 d"], "Find the [[air kerma strength]] and its difference from the certificate."),
           [f"P<sub>TP</sub> = [(273.2 + 23.5) / 295.2] × (101.33 / 99.80) = {ptp1:.4f}",
            f"M N<sub>SK</sub> = 87.62 × 10<sup>−9</sup> A × 4.690 × 10<sup>11</sup> U/A = {raw1:,.0f} U",
            f"S<sub>K</sub> = {raw1:,.0f} × {ptp1:.4f} × 1.003 × 0.998 = {sk1:,.0f} U",
            f"Certificate at the time of the measurement = 43,350 × ½<sup>5.0/73.8</sup> = {cert1_now:,.0f} U",
            f"Difference = {sk1:,.0f} / {cert1_now:,.0f} − 1 = {sgn(pct1)}%"],
           f"{sk1:,.0f} U, {sgn(pct1)}% from the certificate, within {AIM:g}%, so the source is accepted."),
        EX("Treatment time after decay", STEM("An HDR plan is delivered again, later in the life of its Ir-192 source.",
           ["S<sub>K</sub> when the plan was made = 41,000 U", "total dwell time then = 300.0 s", "time since then = 60 d", "T<sub>1/2</sub> = 73.8 d"], "Find the [[total dwell time]] now."),
           [f"S<sub>K</sub> now = 41,000 × ½<sup>60/73.8</sup> = {s2_now:,.0f} U", f"The time scales as 1/S<sub>K</sub>: 300.0 s × 41,000 / {s2_now:,.0f}"],
           f"{t2_now:.0f} s, {t2_now / t2:.2f} times as long."),

        H("Afterloader and applicator QA"),
        P("The NRC sets the minimum checks of a remote afterloader: spot checks before the first treatment of each day and a full calibration at each new source. The AAPM practice guideline MPPG 13.a adds tolerances."),
        TABLE(["Check", "When", "Confirms"], QA_ROWS),
        P("Source position is checked with a ruler viewed by a camera, with film, or with an autoradiograph: film taped to a catheter holding radiopaque markers, exposed with the source at set dwell positions, shows each dwell against the markers. The source is driven a programmed distance from the afterloader, so a transfer tube or applicator longer than the length in the plan leaves every dwell position short by the difference, with no alarm. Tubes and applicators are measured when new and inspected for kinks, cracks, and worn connectors."),
        P("Before each fraction, the channel connections and the dwell positions and times at the console are checked against the approved plan. An independent check of each new plan, a second calculation of a point dose or of the total dwell time, is expected to agree within about 5%."),

        H("Radiation safety and emergencies"),
        P(f"Time, distance, and shielding limit the exposure of staff. In free air the air kerma rate at d metres from a source is S<sub>K</sub>/d² in µGy/h, because 1 U is 1 µGy m² h<sup>−1</sup>: {kerma_rate(40000, 1) / 1000:.0f} mGy/h at 1 m from a 40,000 U source. For Ir-192 one half-value layer is about 3 to 6 mm of lead or 3 to 5 cm of concrete, depending on the geometry."),
        EQ("K̇(d) = S<sub>K</sub> / d²   (µGy/h, S<sub>K</sub> in U, d in m)", "n = log<sub>2</sub>(rate without the barrier / rate wanted),   thickness = n × HVL"),
        P("An HDR room has a door interlock, warning lights, a radiation monitor that shows when the source is out, and a camera and intercom. Beside the unit are long-handled forceps, a portable survey meter, and the emergency container, a shielded container large enough for an applicator with the source inside."),
        P("If the source fails to return, the console emergency stop is pressed first. If the room monitor still shows the source out, the physicist enters with a survey meter and turns the manual crank. If the source stays out, the applicator is removed from the patient with the source inside and placed in the emergency container, and the patient is taken out and surveyed. The room is locked, each step and time recorded, and the radiation safety officer informed. The procedure is posted at the console and drilled at least once a year."),
        P(f"A written directive signed by the authorized user precedes treatment, and after an HDR treatment the patient and afterloader are surveyed to confirm the source is in its safe. A leak test, a wipe of the source or of nearby surfaces counted for removable activity, is done at least every {LEAK_MO} months; {LEAK_BQ} Bq ({LEAK_UCI:g} µCi) or more withdraws the source, with a report within 5 days, and sources with a half-life under 30 days are exempt. Sources are inventoried every 6 months, stored locked and shielded, and shipped in labelled transport packages."),
        EX("Exposure near a stuck source", STEM("An Ir-192 HDR source fails to retract, and a physicist works 1.0 m from it.",
           ["activity = 10 Ci = 10,000 mCi", "Γ = 4.69 R cm² mCi<sup>−1</sup> h<sup>−1</sup>", "time at 1.0 m = 2.0 min"], "Find the [[exposure]] to the physicist."),
           [f"Ẋ = Γ A / r² = 4.69 × 10,000 / 100² = {xr3:.2f} R/h", f"X = {xr3:.2f} R/h × 2.0/60 h = {x3:.3f} R", f"Air kerma = 0.876 cGy/R × {x3:.3f} R = {k3:.3f} cGy"],
           f"{1000 * x3:.0f} mR, an air kerma of {10 * k3:.2f} mGy. The same time at 2.0 m gives a quarter, {250 * x3:.0f} mR."),
        EX("Lead for a factor of 1000", STEM("A lead shield must lower the air kerma rate from an Ir-192 source by a factor of 1000.", [f"HVL of lead for Ir-192 = {HVL_PB:g} mm (illustrative)"], "Find the [[thickness of lead]]."),
           [f"n = log<sub>2</sub>(1000) = {n4:.2f} half-value layers", f"Thickness = {n4:.2f} × {HVL_PB:g} mm"],
           f"{t4:.0f} mm, about 10 half-value layers."),

        H("Permanent implants and release"),
        P(f"The NRC allows release of a patient with permanent seeds when the total effective dose equivalent to any other person is not likely to exceed {REL:g} mSv, and requires instructions, including written ones, above {INSTR:g} mSv. The dose is estimated from the dose rate measured at 1 m from the patient, the mean life, and an occupancy factor E, the fraction of the time a person spends at 1 m ({E_NRC:g} in the NRC guide of 1997)."),
        EQ("D = Ḋ(1 m) × 1.44 T<sub>1/2</sub> × E", "Ḋ(1 m) in mSv/h,   T<sub>1/2</sub> in h"),
        P(f"On that basis, Regulatory Guide 8.39 (1997) allows release at up to {RATE_I:g} mSv/h at 1 m for an I-125 implant and {RATE_PD:g} mSv/h for Pd-103. Tissue absorbs most of the low-energy photons, so measured rates are usually far lower, and a release based on a measurement is recorded."),
        P("Instructions vary between clinics. Pregnant women and young children avoid long close contact, such as a child on the lap, for the first months, longer for I-125 than for Pd-103 or Cs-131. Seeds can pass in the urine or semen in the first weeks; a seed found in the bed, on the floor, or in a stool is lifted with tweezers or a spoon, never by hand, into the shielded container provided, and the physicist is informed."),
    ],
    cards=[
        F("Well-chamber equation", "S<sub>K</sub> = M N<sub>SK</sub> P<sub>TP</sub> P<sub>ion</sub> P<sub>elec</sub>: the current at the sweet spot times the coefficient for the source model, with the corrections of a vented chamber."),
        F("Sweet spot of a well chamber", "The position along the axis of the well with the largest response, found by stepping the source through the insert. The coefficient applies there, and small position errors change the reading least."),
        F("Well-chamber calibration coefficient", "Specific to the source model and the insert, set by an ADCL with a source traceable to NIST. The NRC requires a calibration within the previous 2 years."),
        F("Source strength against the certificate", f"Both are decayed to the same time. Above {AIM:g}% (MPPG 13.a, GEC-ESTRO) the difference is investigated; above {NRC_OUT:g}%, the NRC requirement for HDR output, the source is held from use."),
        F("Dwell time and source decay", f"Dwell times scale as 1/S<sub>K</sub>. Ir-192 is at {100 * f90:.0f}% of its strength after 90 d and {100 * f120:.0f}% after 120 d, so HDR sources are replaced every 3 to 4 months."),
        F("Daily checks of an HDR unit", "Door interlock, warning lights, room monitor, viewing and intercom, emergency kit, timer, clock, and the decayed source strength in the console (NRC)."),
        F("Checks at each new HDR source", ["Output, and source position within 1 mm", "Retraction on the backup battery", "Transfer tube and applicator lengths", "Timer accuracy and linearity", "Function of tubes, applicators, and connections (NRC)"]),
        F("Autoradiograph of dwell positions", "Film on a catheter holding radiopaque markers, exposed with the source at set dwell positions. Each dwell image is compared with the markers."),
        F("Transfer tube too long", "The source is driven a programmed distance, so every dwell position falls short of the plan, toward the afterloader, by the extra length, with no alarm."),
        F("Door interlock of an HDR room", "Opening the door retracts the source at once. It stays in the safe until the door is closed and the interlock is reset at the console."),
        F("Order of actions for a stuck source", "Console emergency stop, enter with a survey meter, manual crank, applicator into the emergency container, then survey the patient and the room."),
        F("Leak test of sealed sources", f"At least every {LEAK_MO} months. A source with {LEAK_BQ} Bq ({LEAK_UCI:g} µCi) or more of removable activity is withdrawn and reported within 5 days (NRC)."),
        F("Release after a permanent implant", f"Allowed when the dose to any other person is not likely to exceed {REL:g} mSv. Instructions, including written ones, are needed above {INSTR:g} mSv (NRC)."),
        F("Dose to others from an implant patient", f"D = Ḋ(1 m) × 1.44 T<sub>1/2</sub> × E, with E the fraction of the time spent at 1 m ({E_NRC:g} in the NRC guide of 1997).",
          w=[f"I-125 at {RATE_I:g} mSv/h: {RATE_I:g} × 1.44 × 59.4 d × 24 h/d × {E_NRC:g} = {release_dose(RATE_I, I_T, E_NRC):.1f} mSv"]),
        F("Seed found after an implant", "Lifted with tweezers or a spoon, never by hand, into a shielded container, and the physicist informed."),
    ],
)

PROBLEMS = [
    # ---- 1-8: source calibration
    PR(STEM(ask="Under NRC rules, how recent must the calibration of the well chamber used for an HDR source be?"), "Within the previous 2 years", ["Within the previous year", "Within the previous 5 years", "Once, when the chamber is bought"],
       "The NRC asks for a dosimetry system calibrated within the previous 2 years, traceable to NIST, or within 4 years with an intercomparison in between. A yearly calibration is more than the rule requires, and a calibration at purchase alone does not meet it.", lvl="Easy"),
    PR(STEM("Before measuring a new HDR source, the physicist steps it through the insert of the well chamber and records the reading at each position.", ask="Why is the source then measured at the position of maximum reading?"),
       "The coefficient applies there, and position errors matter least", ["No temperature and pressure correction is needed there", "Ion recombination is smallest at that position", "The reading there equals S<sub>K</sub> with no coefficient"],
       "The ADCL determines the coefficient with the source at the maximum of the response, so the clinic measures at the same place, and near a maximum a small position error changes the reading least. The corrections apply at every position, and recombination, if anything, is largest where the current is largest.", lvl="Moderate"),
    PR(STEM("A clinic replaces its HDR afterloader with one from another vendor, whose Ir-192 source has a different capsule and cable. The well chamber and its insert are kept.", ask="Which calibration coefficient applies to the new source?"),
       "A coefficient measured by an ADCL for the new source model", ["The old coefficient, because both sources are Ir-192", "The old coefficient scaled by the ratio of the activities", "The old coefficient scaled by the ratio of the source lengths"],
       "The response of a well chamber depends on the construction and spectrum of the source, so a coefficient belongs to one model in one insert, and the new model needs its own. The nuclide alone does not fix the coefficient, and neither the activity nor the length scales it.", lvl="Moderate"),
    TYPED(STEM("A new HDR source is measured at the sweet spot of a vented well chamber.", ["M = 79.40 nA", "N<sub>SK</sub> = 4.712 × 10<sup>11</sup> U/A", "temperature = 20.0 °C,   pressure = 102.80 kPa", "P<sub>ion</sub> = 1.002,   P<sub>elec</sub> = 1.000"], "What is the [[air kerma strength]]?"), sk_q, 0.01, "U",
          f"P<sub>TP</sub> = [(273.2 + 20.0) / 295.2] × (101.33 / 102.80) = {ptp_q:.4f}, and S<sub>K</sub> = 79.40 × 10<sup>−9</sup> A × 4.712 × 10<sup>11</sup> U/A × {ptp_q:.4f} × 1.002 = {sk_q:,.0f} U. Cool, dense air gives a correction below 1; leaving it out gives {sk_q_notp:,.0f} U, {pct(sk_q_notp, sk_q):.1f}% high.", lvl="Moderate"),
    PRN(STEM("A new HDR source is measured in the well chamber and compared with its certificate.", ["certificate = 44,000 U, dated 7.0 d before the measurement", "measured S<sub>K</sub> = 42,300 U", "T<sub>1/2</sub> = 73.8 d"], "What is the [[percent difference]] of the measured value from the certificate?"),
        pct5, [w5_nodecay, w5_exp, w5_grow], lambda v: sgn(v) + "%",
        f"The certificate decays by ½<sup>7.0/73.8</sup> = {calc.frac_remaining(days5, IR_T):.4f} to {c5_now:,.0f} U, so the difference is 42,300 / {c5_now:,.0f} − 1 = {sgn(pct5)}%, within {AIM:g}%. The undecayed certificate gives {sgn(w5_nodecay)}%, decaying with e<sup>−t/T</sup> gives {sgn(w5_exp)}%, and growing the certificate instead of decaying it gives {sgn(w5_grow)}%.", lvl="Challenging"),
    PR(STEM("A new HDR source is measured at the sweet spot, and the certificate is decayed to the time of the measurement.", [f"measured S<sub>K</sub> = {m6:,.0f} U", f"certificate, decayed = {c6:,.0f} U", "repeat readings = within 0.2% of each other"], "What is the next step?"),
       "Hold the source from clinical use until the cause is found", ["Treat with the certificate value, because it is traceable", "Treat with the measured value and report the difference later", "Treat with the mean of the two values until the next source"],
       f"The difference is {sgn(pct6)}%, beyond both the {AIM:g}% level for investigation and the {NRC_OUT:g}% NRC requirement, and the repeat readings rule out noise. Until the setup, insert, corrections, decay, coefficient, or certificate is found to be at fault, neither value can be trusted, and treating with either one or their mean risks a dose error of up to 6%.", lvl="Challenging"),
    PRN(STEM("An HDR plan was made with a new Ir-192 source and is repeated later.", [f"S<sub>K</sub> when the plan was made = {s8:,.0f} U", f"total dwell time then = {t8:.0f} s", f"time since then = {days8:.0f} d", "T<sub>1/2</sub> = 73.8 d"], "What [[total dwell time]] delivers the same plan now?"),
        t8_now, [w8_lin, w8_inv, w8_exp], "{:.0f} s",
        f"S<sub>K</sub> falls to ½<sup>{days8:.0f}/73.8</sup> = {f8:.4f} of its value, and the time scales as 1/S<sub>K</sub>: {t8:.0f} / {f8:.4f} = {t8_now:.0f} s. A straight-line decay gives {w8_lin:.0f} s, multiplying by the fraction instead of dividing gives {w8_inv:.0f} s, and e<sup>t/T</sup> treats the half-life as a mean life ({w8_exp:.0f} s).", lvl="Moderate"),
    # ---- 9-12: afterloader QA
    SORT("Match each QA test of an HDR unit to what it confirms.", ["Autoradiograph of a catheter", "Well chamber reading", "Door opened with the source out", "Stopwatch against a set dwell", "Leak test wipe"],
         [("Dwell positions match the plan", 0), ("Source strength agrees with the certificate", 1), ("The interlock retracts the source", 2), ("Dwell times run as programmed", 3), ("No radioactive material escapes the capsule", 4)],
         "The autoradiograph shows where the source dwelt, the well chamber gives its strength, the open door must retract it, a stopwatch tests the timer, and a wipe counted for removable activity is the leak test.", lvl="Easy", mode="match", cap=1),
    PR(STEM("During the daily check of an HDR unit, the room door is opened while the source is at a dwell position in a test catheter.", ask="What is the correct result?"),
       "The source retracts and stays in the safe until the interlock is reset", ["The source retracts and returns when the door is closed again", "An alarm sounds, and the source stays at its dwell position", "The console shows a warning, and the delivery continues"],
       "The interlock returns the source to its safe as soon as the door opens, and delivery cannot resume until the door is closed and the interlock is reset at the console. An alarm or a warning alone leaves the person at the door exposed, and an automatic return of the source would expose anyone still in the room.", lvl="Easy"),
    PR(STEM("An afterloader drives the source to positions measured from its own reference point. A transfer tube 10 mm longer than the length used in the plan is connected by mistake.", ask="What happens to the dwell positions?"),
       "All are 10 mm short of the plan, toward the afterloader", ["All are 10 mm beyond the plan, toward the tip", "Only the most distal one moves, by 10 mm", "None move, because the check cable corrects them"],
       "The source travels the programmed distance, so an extra 10 mm of tube leaves every dwell position 10 mm short. The check cable detects an obstruction, not a longer path, so no alarm sounds. A tube 10 mm too short would put every position 10 mm beyond the plan.", lvl="Challenging"),
    PRM(STEM("An HDR fraction is about to start.", ask="Which of these are checked before this fraction is delivered?"),
        ["Each applicator channel is connected to the transfer tube named in the plan", "The dwell positions and times at the console match the approved plan"], ["The source strength is measured again in the well chamber", "The source is leak tested with a wipe"],
        "Each fraction checks that the right applicator is connected to the right channel and that the console holds the approved plan. The source strength is measured at each new source, and the leak test is done at least every 6 months, not before each fraction.", lvl="Moderate"),
    # ---- 13-17: radiation safety and emergencies
    SORT("Rank the actions for an HDR source that fails to retract, in the order they are taken.", ["1st", "2nd", "3rd", "4th", "5th"],
         [("Press the emergency stop at the console", 0), ("Enter the room with a survey meter", 1), ("Turn the manual crank on the afterloader", 2), ("Move the applicator into the emergency container", 3), ("Take the patient out and survey the patient", 4)],
         "The console stop is the quickest attempt and exposes no one. If the monitor still shows the source out, the physicist enters with a survey meter and tries the manual crank. If the source still does not retract, the applicator, with the source inside, goes into the emergency container, and the patient is taken out and surveyed to confirm that no source remains.", lvl="Moderate", mode="rank", cap=1),
    PR(STEM(ask="Under NRC rules, how often are sealed brachytherapy sources leak tested, and at what removable activity is a source withdrawn?"), "Every 6 months; 185 Bq (0.005 µCi)", ["Every 12 months; 185 Bq (0.005 µCi)", "Every 6 months; 1850 Bq (0.05 µCi)", "Every 3 months; 18.5 Bq (0.0005 µCi)"],
       "The NRC requires a leak test at intervals of at most 6 months, able to detect 185 Bq (0.005 µCi), and a source with that much removable activity or more is withdrawn and reported within 5 days. The other options change the interval or the limit by a factor of 2 or 10.", lvl="Easy"),
    PRN(STEM("An Ir-192 HDR source is stuck outside its safe, and a therapist stands near the door of the room.", ["activity = 10 Ci = 10,000 mCi", "Γ = 4.69 R cm² mCi<sup>−1</sup> h<sup>−1</sup>", "distance = 2.0 m", "time = 3.0 min"], "What [[exposure]] does the therapist receive?"),
        x15, [w15_1m, w15_hours, w15_ci], lambda v: f"{v:,.1f} mR" if v >= 1 else f"{v:.4f} mR",
        f"Ẋ = 4.69 × 10,000 / 200² = {xr15:.3f} R/h, and 3.0 min is 0.050 h, so X = {x15:.1f} mR. The rate at 1 m gives {w15_1m:.1f} mR, treating 3.0 min as 3.0 h gives {w15_hours:,.1f} mR, and entering 10 Ci as 10 mCi gives {w15_ci:.4f} mR.", lvl="Moderate"),
    PRN(STEM("The wall of an HDR room is designed for a source left out of its safe, ignoring workload and occupancy.", [f"S<sub>K</sub> = {sk16:,.0f} U", f"distance from the source to the outside of the wall = {d16:.1f} m", f"air kerma rate wanted outside = {goal16:.0f} µGy/h (illustrative)", f"HVL of concrete for Ir-192 = {HVL_CON:g} cm (illustrative)"], "What [[concrete thickness]] is needed?"),
        t16, [w16_log10, w16_ln, w16_nod], "{:.1f} cm",
        f"Without the wall the rate is {sk16:,.0f} / {d16:.1f}² = {k16:,.0f} µGy/h, so the reduction is {k16:,.0f} / {goal16:.0f} = {r16:.1f}, n = log<sub>2</sub>({r16:.1f}) = {n16:.2f}, and t = {n16:.2f} × {HVL_CON:g} cm = {t16:.1f} cm. Using log<sub>10</sub> or ln in place of log<sub>2</sub> gives {w16_log10:.1f} or {w16_ln:.1f} cm, and leaving out the inverse square gives {w16_nod:.1f} cm.", lvl="Challenging"),
    PRM(STEM("An HDR unit is prepared for the first patient of the day.", ask="Which of these belong beside the unit for a source that fails to retract?"),
        ["Long-handled forceps", "A shielded emergency container", "A portable survey meter"], ["A well chamber with its electrometer", "Film for an autoradiograph", "A spare source on its cable"],
        "Forceps let the applicator be handled at a distance, the container shields the source once it is out of the patient, and the survey meter shows where the source is and when the room is safe. The well chamber and film are QA equipment, and a spare source has no part in an emergency.", lvl="Moderate"),
    # ---- 18-20: permanent implants and release
    PR(STEM("A patient is ready to go home after a permanent I-125 prostate implant.", ask="Under NRC rules, what dose to any other person must release not be likely to exceed?"), f"{REL:g} mSv", ["0.5 mSv", f"{INSTR:g} mSv", "50 mSv"],
       f"The NRC allows release when the total effective dose equivalent to any other individual is not likely to exceed {REL:g} mSv. {INSTR:g} mSv is the level above which instructions are required, 50 mSv is the annual occupational limit, and 0.5 mSv misreads 0.5 rem, which equals 5 mSv.", lvl="Easy"),
    PR(STEM("A week after a permanent seed implant, a family member finds a seed in the patient's bed.", ask="What is the correct action?"),
       "Lift it with tweezers into the shielded container and call the physicist", ["Pick it up by hand and put it in the household trash", "Leave it in place until it has decayed, then discard it", "Wrap it in tissue and bring it in a pocket to the clinic"],
       "A loose seed is picked up with tweezers or a spoon, never by hand, put in the shielded container the clinic provided, and reported, so that the physicist can account for it and dispose of it. Leaving it, carrying it in a pocket, or throwing it away exposes people and loses track of radioactive material.", lvl="Moderate"),
    TYPED(STEM("A patient is ready to leave after a permanent I-125 prostate implant. The dose to a family member is estimated by the NRC method.", [f"dose rate at 1 m from the patient = {r20:g} mSv/h", "T<sub>1/2</sub> = 59.4 d", f"occupancy factor at 1 m = {E_NRC:g}"], "What [[total dose]] could the family member receive?"), d20, 0.02, "mSv",
          f"The mean life is 1.44 × 59.4 d × 24 h/d = {tau20:,.0f} h, so D = {r20:g} × {tau20:,.0f} × {E_NRC:g} = {d20:.2f} mSv: below {REL:g} mSv, so the patient can be released, and above {INSTR:g} mSv, so instructions are required. Using the half-life in place of the mean life gives {w20:.2f} mSv.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 4], 1: [8, 9, 10], 2: [12, 13, 14]}

TERMS = ["calibration coefficient", "sweet spot", "autoradiograph", "emergency container", "leak test"]

TAKE = [
    ["S<sub>K</sub> = M N<sub>SK</sub> P<sub>TP</sub> P<sub>ion</sub> P<sub>elec</sub>, read at the sweet spot with a coefficient for that source model, calibrated within 2 years.",
     f"The certificate is decayed to the time of the measurement. Above {AIM:g}% the difference is investigated; above {NRC_OUT:g}% (NRC) the source is held from use.",
     f"Seeds: {SEED_PCT}% of the order or {SEED_MIN} seeds, whichever is greater. Dwell times scale as 1/S<sub>K</sub>."],
    ["Daily: door interlock, lights, room monitor, viewing and intercom, emergency kit, timer, clock and decayed S<sub>K</sub>.",
     f"Dwell positions within {POS:g} mm. A transfer tube or applicator of the wrong length shifts every dwell position."],
    ["Air kerma rate = S<sub>K</sub>/d² in µGy/h, with d in m; n half-value layers transmit 2<sup>−n</sup>.",
     "Stuck source: console stop, enter with a survey meter, manual crank, applicator into the emergency container, survey the patient.",
     f"Leak test every {LEAK_MO} months; {LEAK_BQ} Bq ({LEAK_UCI:g} µCi) of removable activity withdraws the source."],
    [f"Release when the dose to any other person is not likely to exceed {REL:g} mSv; instructions when it may exceed {INSTR:g} mSv.",
     "D = Ḋ(1 m) × 1.44 T<sub>1/2</sub> × E. A loose seed is lifted with tweezers into a shielded container."],
]
