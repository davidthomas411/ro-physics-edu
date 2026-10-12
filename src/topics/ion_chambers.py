from blocks import *

# ---------------------------------------------------------------- conventions (TG-51) and helpers
T_REF, P_REF = 22.0, 101.33                         # TG-51 reference air conditions: °C and kPa
KPA_ATM, MMHG_ATM = 101.325, 760.0                  # one standard atmosphere
MMHG = KPA_ATM / MMHG_ATM                           # kPa per mmHg
INHG = 25.4 * MMHG                                  # kPa per inHg: 25.4 mm of mercury

def p_tp(t, p):
    """TG-51 temperature-pressure correction. t: temperature of the air in the chamber (°C); p: local pressure (kPa), not reduced to sea level."""
    return (273.2 + t) / (273.2 + T_REF) * P_REF / p

def p_ion_pulsed(mh, ml, vh, vl):
    """TG-51 two-voltage P_ion at vh for a pulsed or pulsed-swept beam; mh and ml are the raw readings at vh and vl."""
    r = vh / vl
    return (1 - r) / (mh / ml - r)

def p_ion_cont(mh, ml, vh, vl):
    """TG-51 two-voltage P_ion at vh for a continuous beam (Co-60)."""
    r2 = (vh / vl) ** 2
    return (1 - r2) / (mh / ml - r2)

def p_pol(mpos, mneg, m):
    """TG-51 polarity correction from signed readings; m is the signed reading at the polarity used routinely and at calibration."""
    return abs((mpos - mneg) / (2 * m))

TIMES = {2: "two", 3: "three", 4: "four", 5: "five"}
per_degc = 100 / (273.2 + T_REF)                    # % change of P_TP per °C near the reference
per_kpa = 100 / P_REF                               # % change of P_TP per kPa near the reference
atm_inhg = KPA_ATM / INHG                           # one atmosphere in inHg

# ---------------------------------------------------------------- worked examples
EX_VH, EX_VL = 300, 150
EX_LH, EX_LL = 18.462, 18.383                       # nC, pulsed 6 MV beam
EX_CH, EX_CL = 8.214, 8.205                         # nC, Co-60 beam
ex_rl, ex_rc = EX_LH / EX_LL, EX_CH / EX_CL
ex_pion_l = p_ion_pulsed(EX_LH, EX_LL, EX_VH, EX_VL)
ex_pion_c = p_ion_cont(EX_CH, EX_CL, EX_VH, EX_VL)
ex_pion_c_wrong = p_ion_pulsed(EX_CH, EX_CL, EX_VH, EX_VL)          # the pulsed expression applied to the Co-60 readings
EX_MP, EX_MN = 18.462, -18.421                      # nC; positive polarity is the routine one
ex_ppol = p_pol(EX_MP, EX_MN, EX_MP)
EX_T, EX_MM = 23.6, 745.0                           # °C, mmHg
ex_kpa = EX_MM * MMHG
ex_ptp = p_tp(EX_T, ex_kpa)
EX_PELEC = 1.001
F_ION, F_TP, F_POL = round(ex_pion_l, 4), round(ex_ptp, 4), round(ex_ppol, 4)    # the factors as they are printed
ex_prod = F_ION * F_TP * EX_PELEC * F_POL
ex_m = EX_LH * ex_prod

TOPIC = dict(
    id="ion-chambers", domain=2, sub="II.B", title="Ion chambers and charge collection",
    ref=dict(aapm="TG-51", khan="", ford="16"),
    guide=[
        H("Chamber types and construction"),
        P("An ionization chamber holds a gas, usually air, between two electrodes. Radiation ionizes the gas, the voltage separates the ions, and an electrometer measures the charge reaching the collecting electrode. In a thimble chamber the outer electrode is the conducting inner surface of the wall and the collector is a thin rod on the axis. A guard electrode in the stem, at the collector potential, intercepts current crossing the insulator and fixes the edge of the sensitive volume."),
        TABLE(["Chamber", "Construction", "Main use"], [
            ["Farmer type", "About 0.6 cm³; graphite or plastic wall; aluminium or graphite electrode", "Reference dosimetry of megavoltage beams"],
            ["Parallel-plate", "Plates 1 to 2 mm apart, guard ring, thin window", "Low-energy electrons, build-up region, surface dose"],
            ["Well type", "Re-entrant: the source sits inside, nearly 4π geometry", "Air kerma strength of brachytherapy sources"],
            ["Small volume", "A few hundredths of a cm³ or less", "Small-field profiles and output factors"],
            ["Free-air", "Plates in open air with guard electrodes", "Primary standard of air kerma, about 10 to 300 kV"]]),
        P("Most chambers are vented: the cavity air exchanges with the room, so its mass, and the reading for a given dose, follow the temperature and pressure. A sealed chamber holds a fixed mass of gas and needs no air correction, but a slow leak changes its response between calibrations. A wall close to air in composition, such as graphite or an air-equivalent plastic, keeps the response nearly independent of photon energy. Free in air, the wall and a build-up cap must be at least as thick as the range of the secondary electrons, about 0.5 g/cm² for Co-60, so that the electrons crossing the cavity start in the wall. In water the water supplies them, and no cap is used."),

        H("Charge collection and recombination"),
        P("As the voltage rises, the collected charge rises to a plateau, the saturation region, where nearly every ion reaches an electrode. Chambers run on the plateau at a few hundred volts, often 300 V for a Farmer chamber. Far above it, accelerated electrons ionize the gas themselves, as in a proportional counter. On the plateau a small fraction of the ions still recombines, and P<sub>ion</sub> corrects the reading to full collection."),
        P("Initial recombination, between ions of the same track, does not depend on the dose rate; it is largest for densely ionizing radiation such as α particles and small for megavoltage photons and electrons. General recombination occurs between ions of different tracks, so it grows with the ion density: with the dose per pulse in a pulsed beam and the dose rate in a continuous beam. A linac delivers its dose in pulses a few microseconds long, so the ion density during a pulse far exceeds that in a Co-60 beam of the same average dose rate. The fraction lost falls as 1/V in a pulsed beam and as 1/V² in a continuous beam, hence the two TG-51 expressions."),
        EQ("Pulsed or pulsed-swept beam (a pulsed beam scanned across the field):   P<sub>ion</sub>(V<sub>H</sub>) = (1 − V<sub>H</sub>/V<sub>L</sub>) / (M<sub>H</sub>/M<sub>L</sub> − V<sub>H</sub>/V<sub>L</sub>)",
           "Continuous beam (Co-60):   P<sub>ion</sub>(V<sub>H</sub>) = [1 − (V<sub>H</sub>/V<sub>L</sub>)²] / [M<sub>H</sub>/M<sub>L</sub> − (V<sub>H</sub>/V<sub>L</sub>)²]",
           "V<sub>H</sub> = normal operating voltage,   V<sub>L</sub> ≤ V<sub>H</sub>/2,   M<sub>H</sub>, M<sub>L</sub> = raw readings for the same MU"),
        P("M<sub>L</sub> is read after the reading settles at the lower voltage. P<sub>ion</sub> is usually 1.002 to 1.02 in linac beams, highest for the large dose per pulse of flattening-filter-free beams, and nearer 1 in Co-60. Above 1.05 the correction is too uncertain and TG-51 calls for another chamber."),
        EX("Two-voltage P<sub>ion</sub>", STEM("A Farmer chamber is read at 300 V and at 150 V in two beams, with the same irradiation at both voltages.", [f"pulsed 6 MV beam: M<sub>H</sub> = {EX_LH:.3f} nC, M<sub>L</sub> = {EX_LL:.3f} nC", f"Co-60 beam: M<sub>H</sub> = {EX_CH:.3f} nC, M<sub>L</sub> = {EX_CL:.3f} nC"], "Find [[P<sub>ion</sub>]] in each beam."),
           ["V<sub>H</sub>/V<sub>L</sub> = 300/150 = 2",
            f"6 MV: M<sub>H</sub>/M<sub>L</sub> = {EX_LH:.3f}/{EX_LL:.3f} = {ex_rl:.5f}, and P<sub>ion</sub> = (1 − 2)/({ex_rl:.5f} − 2) = {ex_pion_l:.4f}",
            f"Co-60: M<sub>H</sub>/M<sub>L</sub> = {EX_CH:.3f}/{EX_CL:.3f} = {ex_rc:.5f}, and P<sub>ion</sub> = (1 − 4)/({ex_rc:.5f} − 4) = {ex_pion_c:.4f}"],
           f"{ex_pion_l:.4f} in the 6 MV beam and {ex_pion_c:.4f} in the Co-60 beam. The pulsed expression applied to the Co-60 readings would give {ex_pion_c_wrong:.4f}, {TIMES[round((ex_pion_c_wrong - 1) / (ex_pion_c - 1))]} times the correction."),

        H("Polarity, electrometer, and cable effects"),
        P("Reversing the bias collects ions of the other sign, and the two readings differ slightly in magnitude, the polarity effect. Two kinds of charge cause it: a current of fast electrons stopping in or leaving the collector, which does not reverse with the bias (the Compton current), and charge collected outside the sensitive volume, in the stem and the cable. The effect is largest where the signal is small or the electrons are far from equilibrium: in parallel-plate and small-volume chambers, in electron beams, at low energy, and at shallow depth."),
        EQ("P<sub>pol</sub> = | (M<sup>+</sup> − M<sup>−</sup>) / (2M) |",
           "M<sup>+</sup>, M<sup>−</sup> = readings collecting positive and negative charge, with their signs",
           "M = the reading at the polarity used routinely and at calibration"),
        P("The chamber is left to settle after each reversal. For a Farmer chamber in a photon beam P<sub>pol</sub> is within a few tenths of a percent of 1; the 2014 TG-51 addendum requires a reference-class chamber to stay within 0.4%. In low-energy electron beams some parallel-plate chambers show a polarity effect of several percent."),
        P("The electrometer integrates the charge on a feedback capacitor and displays it in nC. It is warmed up and zeroed, and the chamber is pre-irradiated until consecutive readings agree. Leakage is the charge collected with the bias on and the beam off over the time of a reading; the addendum limits it to 0.1% of the reading. P<sub>elec</sub> converts the display to true charge, from an ADCL calibration of each range used, and is 1.000 when chamber and electrometer are calibrated as a unit. A triaxial cable carries the signal on its central conductor inside a guard at the collector potential, so current leaking through the insulation misses the collector. Bending, twisting, or irradiating the cable, or irradiating more of the stem, adds spurious charge."),
        EX("Polarity correction", STEM("A Farmer chamber is read at both polarities in a 6 MV beam with the same monitor units. Positive polarity is used routinely and at calibration.", [f"M<sup>+</sup> = +{EX_MP:.3f} nC", f"M<sup>−</sup> = −{-EX_MN:.3f} nC"], "Find [[P<sub>pol</sub>]]."),
           [f"M<sup>+</sup> − M<sup>−</sup> = {EX_MP:.3f} − (−{-EX_MN:.3f}) = {EX_MP - EX_MN:.3f} nC",
            f"P<sub>pol</sub> = {EX_MP - EX_MN:.3f} / (2 × {EX_MP:.3f}) = {ex_ppol:.4f}"],
           f"{ex_ppol:.4f}. The routine reading is {100 * (1 / ex_ppol - 1):.2f}% above the mean of the two magnitudes, and P<sub>pol</sub> removes that excess."),

        H("Temperature, pressure, and the corrected reading"),
        P("The mass of air in a vented chamber is proportional to P/T, so the reading for a given dose falls when the air is warmer or the pressure lower. P<sub>TP</sub> scales the reading to the air density of the calibration, 22 °C and 101.33 kPa in TG-51."),
        EQ("P<sub>TP</sub> = [(273.2 + T) / 295.2] × (101.33 / P)",
           "T = temperature of the air in the chamber in °C,   P = local air pressure in kPa",
           f"1 atm = 101.325 kPa = 760 mmHg = 1013.25 hPa (mbar) = {atm_inhg:.2f} inHg"),
        P(f"T is read in the water beside the chamber once the chamber has reached the water temperature: several minutes for a Farmer chamber, longer for a parallel-plate chamber. P is the actual room pressure; weather services report pressure reduced to sea level, too high at altitude. With P in mmHg, 760 replaces 101.33. No humidity correction is needed between 20% and 80% relative humidity. Near the reference conditions P<sub>TP</sub> changes by {per_degc:.2f}% per °C and {per_kpa:.2f}% per kPa. IAEA TRS-398 uses 20 °C, so the reference temperature must match the chamber's calibration certificate."),
        EX("Temperature and pressure", STEM("A Farmer chamber has reached the temperature of the water around it.", [f"water temperature = {EX_T:.1f} °C", f"barometer = {EX_MM:.0f} mmHg"], "Find [[P<sub>TP</sub>]]."),
           [f"P = {EX_MM:.0f} × 101.325/760 = {ex_kpa:.3f} kPa",
            f"Temperature term = (273.2 + {EX_T:.1f})/295.2 = {(273.2 + EX_T) / 295.2:.4f}",
            f"Pressure term = 101.33/{ex_kpa:.3f} = {P_REF / ex_kpa:.4f}"],
           f"P<sub>TP</sub> = {ex_ptp:.4f}. The warm water and the low pressure both lower the mass of air in the cavity, so the reading is raised by {100 * (ex_ptp - 1):.1f}%."),
        EQ("M = P<sub>ion</sub> P<sub>TP</sub> P<sub>elec</sub> P<sub>pol</sub> M<sub>raw</sub>", "original TG-51; the 2014 addendum adds P<sub>leak</sub>, a leakage correction, and P<sub>rp</sub>, a radial-profile correction"),
        P("M is the reading of a calibrated electrometer at the reference air density, with full collection and no polarity effect. TG-51 multiplies it by the beam-quality conversion factor k<sub>Q</sub> and the Co-60 calibration coefficient N<sub>D,w</sub> to give the absorbed dose to water."),
        EX("Fully corrected reading", STEM("A 6 MV reference reading is corrected with the factors measured for it.", [f"M<sub>raw</sub> = {EX_LH:.3f} nC", f"P<sub>ion</sub> = {F_ION:.4f}", f"P<sub>TP</sub> = {F_TP:.4f}", f"P<sub>elec</sub> = {EX_PELEC:.3f}", f"P<sub>pol</sub> = {F_POL:.4f}"], "Find the [[corrected reading M]]."),
           [f"Product of the factors = {F_ION:.4f} × {F_TP:.4f} × {EX_PELEC:.3f} × {F_POL:.4f} = {ex_prod:.5f}",
            f"M = {EX_LH:.3f} × {ex_prod:.5f}"],
           f"{ex_m:.3f} nC, {100 * (ex_prod - 1):.1f}% above the raw reading, most of it from P<sub>TP</sub>."),
    ],
    cards=[
        F("Farmer-type chamber", "A cylindrical chamber of about 0.6 cm³ with a graphite or plastic wall and an aluminium or graphite central electrode, used for reference dosimetry of megavoltage beams."),
        F("Parallel-plate chamber", "Plates 1 to 2 mm apart, a guard ring, and a thin entrance window. Used for low-energy electron beams, the build-up region, and surface dose."),
        F("Well-type chamber", "A re-entrant chamber that nearly surrounds the source, used to measure the air kerma strength of brachytherapy sources."),
        F("Free-air chamber", "Collecting plates in open air, with guard electrodes and a diaphragm that defines the beam. The primary standard of air kerma for x-rays of about 10 to 300 kV."),
        F("Vented and sealed chambers", "A vented chamber needs P<sub>TP</sub>, because the mass of air in it follows the temperature and pressure. A sealed chamber needs none."),
        F("Saturation region", "The plateau of collected charge against voltage, where nearly every ion is collected. Chambers run there, at a few hundred volts."),
        F("Initial and general recombination", ["Initial: ions of one track. Independent of dose rate, larger at high LET.", "General: ions of different tracks. Rises with the dose per pulse or the dose rate."]),
        F("Two-voltage P<sub>ion</sub>", ["Pulsed: (1 − V<sub>H</sub>/V<sub>L</sub>) / (M<sub>H</sub>/M<sub>L</sub> − V<sub>H</sub>/V<sub>L</sub>).", "Continuous: [1 − (V<sub>H</sub>/V<sub>L</sub>)²] / [M<sub>H</sub>/M<sub>L</sub> − (V<sub>H</sub>/V<sub>L</sub>)²].", "V<sub>L</sub> at least a factor of 2 below the operating voltage V<sub>H</sub>."]),
        F("Size of P<sub>ion</sub>", "Usually 1.002 to 1.02 in linac beams, highest for a high dose per pulse, and nearer 1 in Co-60. Above 1.05 another chamber is needed."),
        F("Polarity correction", ["P<sub>pol</sub> = |(M<sup>+</sup> − M<sup>−</sup>) / (2M)|, with signed readings and M at the routine polarity, the one used at calibration.", "Largest for parallel-plate and small-volume chambers, electron beams, and shallow depths."]),
        F("Leakage limit", "Below 0.1% of the reading for a reference-class chamber (2014 TG-51 addendum), measured with the bias on and the beam off."),
        F("Triaxial cable", "The signal runs on the central conductor inside a guard at the collector potential, so current leaking through the insulation misses the collector."),
        F("Electrometer correction", "P<sub>elec</sub> comes from an ADCL calibration of the electrometer. It is 1.000 when chamber and electrometer are calibrated together."),
        F("Temperature and pressure correction", "P<sub>TP</sub> = [(273.2 + T)/295.2] × (101.33/P), with T in °C and P the local pressure in kPa, not reduced to sea level."),
        F("Pressure units", f"1 atm = 101.325 kPa = 760 mmHg = 1013.25 hPa (mbar) = {atm_inhg:.2f} inHg."),
        F("Corrected reading", "M = P<sub>ion</sub> P<sub>TP</sub> P<sub>elec</sub> P<sub>pol</sub> M<sub>raw</sub> in the original TG-51 (the 2014 addendum adds P<sub>leak</sub> and P<sub>rp</sub>), the charge that TG-51 multiplies by k<sub>Q</sub> and N<sub>D,w</sub>."),
    ],
)

# ---------------------------------------------------------------- numbers behind the questions
q_vh, q_vl, q_mh, q_ml = 300, 150, 20.115, 20.008                    # pulsed 6 MV beam
q_pion = p_ion_pulsed(q_mh, q_ml, q_vh, q_vl)
q_pion_cont = p_ion_cont(q_mh, q_ml, q_vh, q_vl)                      # the continuous expression used by mistake
q_pion_inv = p_ion_pulsed(q_mh, q_ml, q_vl, q_vh)                     # the voltage ratio inverted
q_pion_low = 1 + (q_vh / q_vl) * (q_pion - 1)                         # the correction that applies at the lower voltage
c_vh, c_vl, c_mh, c_ml = 300, 100, 12.060, 12.002                    # Co-60 beam
c_ratio = c_mh / c_ml
c_pion = p_ion_cont(c_mh, c_ml, c_vh, c_vl)
c_pion_pulsed = p_ion_pulsed(c_mh, c_ml, c_vh, c_vl)
c_pion_low = 1 + (c_vh / c_vl) ** 2 * (c_pion - 1)
pp_pos, pp_neg = 15.244, -15.307                                       # negative polarity is the routine one
pp = p_pol(pp_pos, pp_neg, pp_neg)
pp_wrongden = p_pol(pp_pos, pp_neg, pp_pos)
pp_ratio, pp_ratio_inv = abs(pp_pos / pp_neg), abs(pp_neg / pp_pos)
lk_q, lk_sig = 0.050, 18.40                                            # nC with the beam off; nC for the exposure
lk_frac = lk_q / lk_sig
t_mm = 742.0
t_kpa = t_mm * MMHG
h_t, h_in = 21.4, 29.65
h_kpa = h_in * INHG
h_ptp = p_tp(h_t, h_kpa)
h_not = P_REF / h_kpa                                                  # the temperature term left out
h_celsius = h_t / T_REF * P_REF / h_kpa                                # Celsius temperatures used without 273.2
h_inv = 1 / h_ptp
y_t, y_hpa = 25.0, 1002.0
y_ptp = p_tp(y_t, y_hpa / 10)
READ = [18.21, 18.33, 18.40, 18.44, 18.45, 18.45]                     # nC, consecutive readings after connection
rise = (READ[-1] - READ[0]) / READ[0]
w_true, w_used = 18.0, 22.0                                            # °C: the water, and the value entered
w_err = (273.2 + w_used) / (273.2 + w_true) - 1
w_celsius = w_used / w_true - 1
alt_local, alt_report = 83.5, 101.9                                    # kPa at 1600 m, and the sea-level value reported
alt_low = alt_local / alt_report                                       # the measured dose is low by this factor
alt_over = alt_report / alt_local - 1                                  # the output is then set high by this fraction
m_raw, m_ion, m_pol, m_elec, m_t, m_mm = 20.115, 1.0054, 0.9992, 1.0006, 20.5, 763.0
m_kpa = m_mm * MMHG
m_ptp = p_tp(m_t, m_kpa)
m_corr = m_raw * m_ion * m_ptp * m_elec * m_pol
m_notp = m_raw * m_ion * m_elec * m_pol
m_divtp = m_notp / m_ptp
m_noion = m_raw * m_ptp * m_elec * m_pol

PROBLEMS = [
    # chamber types and construction
    PR(STEM("A vented chamber and a sealed chamber are read in the same room on a day when the air pressure falls.", [], "Why does the reading of the vented chamber change while the reading of the sealed chamber does not?"),
       "The mass of air in the vented cavity changes",
       ["The vented chamber has a larger collecting volume", "The vented chamber has a larger polarity effect", "The sealed chamber collects its ions more completely"],
       "Air flows in and out of a vented cavity, so the mass of air in it, and the charge per unit dose, follows P/T, which P<sub>TP</sub> corrects. The sealed chamber keeps a fixed mass of gas. Volume, polarity effect, and collection efficiency do not change with the weather.", lvl="Easy"),
    PR(STEM("A Farmer chamber with a thin wall is placed free in air in a Co-60 beam, with a build-up cap over it.", [], "Why is the build-up cap needed?"),
       "It gives charged-particle equilibrium in the cavity",
       ["It shields the cavity from photons scattered in the head", "It keeps moisture out of the vented cavity", "It raises the ion collection efficiency of the chamber"],
       "The secondary electrons of Co-60 travel up to about 0.5 g/cm², more than a thin wall. With the cap, the electrons crossing the cavity start in the wall and the cap, so charged-particle equilibrium holds in the cavity. The cap attenuates scattered photons only slightly and does not change recombination.", lvl="Moderate"),
    SORT(STEM("Five measurements each call for a different type of ionization chamber.", [], "Which chamber suits each measurement?"),
         ["Farmer-type cylindrical", "Parallel-plate", "Well type", "Small volume", "Free-air"],
         [("Reference dosimetry of a 10 MV photon beam", 0), ("Dose in the build-up region of a 6 MV beam", 1), ("Air kerma strength of an HDR Ir-192 source", 2), ("Output factor of a 2 × 2 cm field", 3), ("Primary standard of air kerma for 100 kV x-rays", 4)],
         "The Farmer chamber is the reference chamber for megavoltage beams. A parallel-plate chamber samples a thin layer at a known depth, which suits the build-up region. A well chamber surrounds the source. A small-volume chamber limits averaging across a narrow field. The free-air chamber measures air kerma from first principles at a standards laboratory.", lvl="Easy", mode="match", cap=1),

    # charge collection and recombination
    PR(STEM("The charge that a chamber collects at a fixed dose is plotted against the voltage across it.", [], "Why is the chamber operated in the saturation region of this curve?"),
       "Nearly every ion is collected there, whatever the exact voltage",
       ["Gas multiplication amplifies the signal in that region", "The polarity effect vanishes in that region", "Recombination is largest there and easiest to correct"],
       "On the plateau almost all ions reach an electrode, and P<sub>ion</sub> corrects the small loss that remains. Gas multiplication happens far above the plateau, where the chamber would act as a proportional counter.", lvl="Easy"),
    PR(STEM("Some ions recombine within the track in which they were formed, before the field separates them.", [], "Which property of the radiation increases this initial recombination?"),
       "A higher linear energy transfer, as for α particles",
       ["A higher dose per pulse at the same energy", "A higher average dose rate at the same energy", "A longer interval between the pulses"],
       "Initial recombination occurs within one track, so it depends on how densely the track is ionized, that is on the LET, and not on the number of tracks. The dose per pulse and the dose rate change general recombination, between ions of different tracks.", lvl="Moderate"),
    PRM(STEM("Ions from different tracks can meet and recombine before they reach an electrode.", [], "Which of these statements about this general recombination are correct?"),
        ["It rises with the dose per pulse in a pulsed beam", "The fraction lost falls as the voltage is raised"],
        ["It is the same in any beams of equal average dose rate", "It is the main loss for α particles at a low dose rate"],
        "General recombination grows with the density of ions, so with the dose per pulse, and a higher voltage clears the ions faster. Beams with the same average dose rate can have different doses per pulse, and the loss along dense α tracks is initial recombination.", lvl="Moderate"),
    PRN(STEM("A Farmer chamber is read in a 6 MV beam at two voltages, with the same monitor units.", [f"M<sub>H</sub> = {q_mh:.3f} nC at {q_vh} V", f"M<sub>L</sub> = {q_ml:.3f} nC at {q_vl} V"], f"What is [[P<sub>ion</sub>]] at {q_vh} V?"), q_pion, [q_pion_inv, q_pion_cont, q_pion_low], "{:.4f}",
        f"For a pulsed beam P<sub>ion</sub> = (1 − 2)/({q_mh / q_ml:.5f} − 2) = {q_pion:.4f}. The continuous-beam expression gives {q_pion_cont:.4f} and applies to Co-60 only, inverting the voltage ratio gives {q_pion_inv:.4f}, below 1, and {q_pion_low:.4f} is the correction at {q_vl} V.", lvl="Moderate"),
    PRN(STEM("A Farmer chamber is read in a Co-60 beam at two voltages, with the same exposure time.", [f"M<sub>H</sub> = {c_mh:.3f} nC at {c_vh} V", f"M<sub>L</sub> = {c_ml:.3f} nC at {c_vl} V"], f"What is [[P<sub>ion</sub>]] at {c_vh} V?"), c_pion, [c_pion_pulsed, c_ratio, c_pion_low], "{:.4f}",
        f"Co-60 is a continuous beam, so the voltage ratio is squared: P<sub>ion</sub> = (1 − 9)/({c_ratio:.5f} − 9) = {c_pion:.4f}. The pulsed expression gives {c_pion_pulsed:.4f}, the ratio of the readings is {c_ratio:.4f}, and {c_pion_low:.4f} is the correction at {c_vl} V.", lvl="Moderate"),

    # polarity, electrometer, and cables
    PR(STEM("A thimble chamber is connected to its electrometer by a triaxial cable. The middle conductor of the cable is held at the potential of the collector.", [], "What does this guard conductor do?"),
       "It intercepts leakage current through the insulation",
       ["It carries the collected charge to the electrometer", "It shields the signal conductor from scattered photons", "It discharges the chamber between two readings"],
       "No current flows between two conductors at the same potential, so current through the insulation ends on the guard and not on the signal conductor. The central conductor carries the signal.", lvl="Easy"),
    PR(STEM("Readings are taken at both polarities in four set-ups.", [], "In which set-up is the polarity effect expected to be largest?"),
       "A parallel-plate chamber at 0.5 cm depth in a 6 MeV electron beam",
       ["A Farmer chamber at 10 cm depth in a 10 MV photon beam", "A Farmer chamber with a build-up cap in a Co-60 beam", "A well chamber holding an HDR Ir-192 source"],
       "Electrons stopping in a thin collector carry a current that does not reverse with the bias, and with the charge from the stem and cable it is largest relative to the signal of a small chamber at shallow depth in a low-energy electron beam. A Farmer chamber in a photon beam near equilibrium shows a few tenths of a percent at most.", lvl="Moderate"),
    PRN(STEM("A parallel-plate chamber is read at both polarities in an electron beam, with the same monitor units. Negative polarity is used routinely and at calibration.", [f"M<sup>+</sup> = +{pp_pos:.3f} nC", f"M<sup>−</sup> = −{-pp_neg:.3f} nC"], "What is [[P<sub>pol</sub>]]?"), pp, [pp_wrongden, pp_ratio, pp_ratio_inv], "{:.4f}",
        f"P<sub>pol</sub> = |(M<sup>+</sup> − M<sup>−</sup>)/(2M<sup>−</sup>)| = ({pp_pos:.3f} + {-pp_neg:.3f})/(2 × {-pp_neg:.3f}) = {pp:.4f}, with the routine (negative) reading in the denominator. The positive reading there gives {pp_wrongden:.4f}, and the ratios of the two readings, {pp_ratio:.4f} and {pp_ratio_inv:.4f}, make the correction twice as large.", lvl="Moderate"),
    PR(STEM("Before a calibration, the leakage of a chamber and electrometer is read with the bias on and the beam off, over the time that one reading takes.", [f"charge collected with the beam off = {lk_q:.3f} nC", f"reading for the calibration exposure = {lk_sig:.2f} nC"], "What does this leakage mean?"),
       f"It is {100 * lk_frac:.2f}% of the reading, above the 0.1% limit, so the cause must be found first",
       ["It is below the 1% limit for reference dosimetry, so calibration can go ahead", "It is an electrometer offset that P<sub>elec</sub> removes", "It is the polarity effect, which P<sub>pol</sub> corrects"],
       f"The leakage is {lk_q:.3f}/{lk_sig:.2f} = {100 * lk_frac:.2f}% of the reading: below 1%, but above the 0.1% that the 2014 TG-51 addendum allows for a reference-class chamber. A damp or dirty connector or a damaged cable is the usual cause. A 1% limit is ten times too loose, P<sub>elec</sub> converts the display to true charge and does not remove leakage, and P<sub>pol</sub> corrects the polarity effect.", lvl="Challenging"),
    PRM(STEM("A physicist sets up a Farmer chamber in a water phantom for a calibration.", [], "Which of these would make the readings unreliable?"),
        ["Bending the cable between readings", "Leaving a loop of cable in the radiation field", "Reading the electrometer a minute after switching it on"],
        ["Using the polarity that was used at calibration", "Using the normal operating voltage", "Reading the thermometer in the water beside the chamber"],
        "Bending a cable frees charge in its insulation, a cable in the beam adds charge from outside the sensitive volume, and an electrometer that has not warmed up drifts. The calibration polarity, the normal bias, and a thermometer in the water are correct practice.", lvl="Moderate"),

    # temperature, pressure, and the corrected reading
    TYPED(STEM(f"A barometer in the treatment room reads {t_mm:.0f} mmHg.", [], "What is the pressure in [[kPa]]?"), t_kpa, 0.003, "kPa",
          f"760 mmHg = 101.325 kPa, so 1 mmHg = {MMHG:.4f} kPa and {t_mm:.0f} mmHg = {t_kpa:.2f} kPa.", lvl="Easy"),
    PRN(STEM("A Farmer chamber has reached the temperature of the water around it. The barometer in the room reads in inches of mercury.", [f"water temperature = {h_t:.1f} °C", f"pressure = {h_in:.2f} inHg"], "What is [[P<sub>TP</sub>]]?"), h_ptp, [h_not, h_celsius, h_inv], "{:.4f}",
        f"1 inHg = 25.4 mmHg = {INHG:.4f} kPa, so P = {h_kpa:.2f} kPa. P<sub>TP</sub> = ({273.2 + h_t:.1f}/295.2) × (101.33/{h_kpa:.2f}) = {h_ptp:.4f}. Leaving out the temperature term gives {h_not:.4f}, the Celsius temperatures without 273.2 give {h_celsius:.4f}, and the inverted factor is {h_inv:.4f}.", lvl="Moderate"),
    TYPED(STEM("A chamber is read in a water phantom.", [f"water temperature = {y_t:.1f} °C", f"pressure = {y_hpa:.0f} hPa"], "What is [[P<sub>TP</sub>]]?"), y_ptp, 0.002, "(ratio)",
          f"{y_hpa:.0f} hPa = {y_hpa / 10:.1f} kPa. P<sub>TP</sub> = ({273.2 + y_t:.1f}/295.2) × (101.33/{y_hpa / 10:.1f}) = {y_ptp:.4f}. Leaving out the temperature term gives {P_REF / (y_hpa / 10):.4f}.", lvl="Moderate"),
    SORT(STEM("Four factors convert the raw reading of a chamber to the corrected reading M.", [], "What does each factor correct?"),
         ["P<sub>ion</sub>", "P<sub>TP</sub>", "P<sub>pol</sub>", "P<sub>elec</sub>"],
         [("Ions that recombine before they reach an electrode", 0), ("A mass of air in the cavity that differs from the calibration", 1), ("Readings that differ when the bias is reversed", 2), ("A display that differs from the true charge", 3)],
         "P<sub>ion</sub> restores full collection, P<sub>TP</sub> scales the air in the cavity to 22 °C and 101.33 kPa, P<sub>pol</sub> corrects the reading to the mean of the two polarities, and P<sub>elec</sub> is the calibration of the electrometer.", lvl="Easy", mode="match", cap=1),

    # scenarios and the full correction (practice set)
    PR(STEM("At the start of a morning output check, a chamber is connected and six consecutive readings of 100 MU are taken in a water phantom.", ["readings (nC) = " + ", ".join(f"{x:.2f}" for x in READ)], "What is the most likely cause of the low early readings?"),
       "The chamber was not pre-irradiated, and its response was still settling",
       [f"The air pressure rose by about {100 * rise:.1f}% during the readings", "General recombination fell as the chamber warmed up", "Leakage added charge to the later readings"],
       f"The readings rise by {100 * rise:.1f}% and then level off, the pattern of a chamber and cable settling after connection; pre-irradiation until consecutive readings agree removes it. A pressure rise of {100 * rise:.1f}%, about {rise * 101.3:.1f} kPa, within minutes would be far faster than any change in the weather, recombination does not depend on warming, and the leakage of a working system is far below 1%.", lvl="Challenging"),
    PR(STEM(f"A water phantom is filled from a tap and used at once. The chamber and the water are at {w_true:.1f} °C, but the temperature entered in P<sub>TP</sub> is that of the room air, {w_used:.1f} °C.", [], "How does the corrected reading compare with its true value?"),
       f"About {100 * w_err:.1f}% too high",
       [f"About {100 * w_err:.1f}% too low", f"About {100 * w_celsius:.0f}% too high", "Correct, because 22 °C is the reference temperature"],
       f"The true temperature term is (273.2 + {w_true:.1f})/295.2 = {(273.2 + w_true) / 295.2:.4f}, but 1.0000 was used, so the corrected reading is {1 + w_err:.4f} times its true value, {100 * w_err:.1f}% too high. The Celsius ratio {w_used:.0f}/{w_true:.0f} gives the {100 * w_celsius:.0f}% option, and the temperature that matters is that of the air in the chamber, not the reference value.", lvl="Challenging"),
    PR(STEM("A clinic at an altitude of 1600 m calibrates a linac with TG-51, using the pressure from an airport weather report, which is reduced to sea level. The output is then adjusted to the measured dose.", [f"actual pressure in the room = {alt_local:.1f} kPa", f"reported pressure = {alt_report:.1f} kPa"], "How does the dose delivered after the adjustment compare with the intended dose?"),
       f"About {100 * alt_over:.0f}% more than intended",
       [f"About {100 * (1 - alt_low):.0f}% more than intended", f"About {100 * (1 - alt_low):.0f}% less than intended", f"About {100 * alt_over:.0f}% less than intended"],
       f"With the reported pressure, P<sub>TP</sub> is too small by the factor {alt_local:.1f}/{alt_report:.1f} = {alt_low:.3f}, so the measured dose is {100 * (1 - alt_low):.0f}% low. Raising the output until the measurement reads correctly raises the true dose by {alt_report:.1f}/{alt_local:.1f} = {1 + alt_over:.3f}, {100 * alt_over:.0f}% too much. The {100 * (1 - alt_low):.0f}% options take the error of the measurement as the error of the delivered dose.", lvl="Challenging"),
    PRN(STEM("A reference reading is corrected with its measured factors. The temperature and pressure are read at the time of the measurement.", [f"M<sub>raw</sub> = {m_raw:.3f} nC", f"P<sub>ion</sub> = {m_ion:.4f}", f"P<sub>pol</sub> = {m_pol:.4f}", f"P<sub>elec</sub> = {m_elec:.4f}", f"water temperature = {m_t:.1f} °C", f"pressure = {m_mm:.0f} mmHg"], "What is the [[corrected reading M]]?"),
        m_corr, [m_notp, m_divtp, m_noion], "{:.2f} nC",
        f"P = {m_mm:.0f} × 101.325/760 = {m_kpa:.2f} kPa, and P<sub>TP</sub> = ({273.2 + m_t:.1f}/295.2) × (101.33/{m_kpa:.2f}) = {m_ptp:.4f}. M = {m_raw:.3f} × {m_ion:.4f} × {m_ptp:.4f} × {m_elec:.4f} × {m_pol:.4f} = {m_corr:.2f} nC. Leaving out P<sub>TP</sub> gives {m_notp:.2f}, dividing by it gives {m_divtp:.2f}, and leaving out P<sub>ion</sub> gives {m_noion:.2f} nC.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4, 5, 6, 7, 8], 2: [9, 10, 11, 12, 13], 3: [14, 15, 16, 17]}

TERMS = ["guard electrode", "vented", "saturation region", "initial recombination", "general recombination", "polarity effect", "leakage", "triaxial cable"]

TAKE = [
    ["Farmer chamber (about 0.6 cm³) for reference dosimetry, parallel-plate for low-energy electrons and the build-up region, well chamber for brachytherapy sources, free-air chamber as the kilovoltage primary standard.",
     "A vented chamber needs P<sub>TP</sub>; a sealed chamber does not."],
    ["Chambers run on the saturation plateau. Initial recombination does not depend on dose rate; general recombination rises with the dose per pulse or the dose rate.",
     "Pulsed: P<sub>ion</sub> = (1 − V<sub>H</sub>/V<sub>L</sub>)/(M<sub>H</sub>/M<sub>L</sub> − V<sub>H</sub>/V<sub>L</sub>); continuous: both voltage ratios squared. Above 1.05 another chamber is needed."],
    ["P<sub>pol</sub> = |(M<sup>+</sup> − M<sup>−</sup>)/(2M)|, with M at the routine polarity. Largest for parallel-plate chambers, electron beams, and shallow depths.",
     "Leakage below 0.1% of the reading. P<sub>elec</sub> = 1 when chamber and electrometer are calibrated together."],
    ["P<sub>TP</sub> = [(273.2 + T)/295.2] × (101.33/P), with T in °C and P the local pressure in kPa, not reduced to sea level.",
     "M = P<sub>ion</sub> P<sub>TP</sub> P<sub>elec</sub> P<sub>pol</sub> M<sub>raw</sub> in the original TG-51; the 2014 addendum adds P<sub>leak</sub> and P<sub>rp</sub>."],
]
