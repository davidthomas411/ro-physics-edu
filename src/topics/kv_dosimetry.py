from blocks import *
import math

# ---------------------------------------------------------------- this chapter's formulas (TG-61 notation)
def k_air(m_nc, nk):
    """Air kerma (Gy) free in air: a corrected reading M in nC times N_K in Gy/C."""
    return m_nc * 1e-9 * nk

def d_in_air(m_nc, nk, bw, pstem, ratio):
    """TG-61 in-air method: D_w,z=0 = M N_K B_w P_stem,air [(mu_en/rho) water to air, free in air]."""
    return k_air(m_nc, nk) * bw * pstem * ratio

def d_in_water(m_nc, nk, pq, psh, ratio):
    """TG-61 in-water method: D_w,z=2cm = M N_K P_Q,cham P_sheath [(mu_en/rho) water to air, at 2 cm in water]."""
    return k_air(m_nc, nk) * pq * psh * ratio

def nk_at(h, h1, n1, h2, n2):
    """N_K at HVL h, taken as linear in HVL between two calibration beams (h1, n1) and (h2, n2)."""
    return n1 + (h - h1) / (h2 - h1) * (n2 - n1)

def combined(*u):
    """Combined standard uncertainty of independent components, in the same units: the root of the sum of squares."""
    return math.sqrt(sum(x * x for x in u))

def isq(d_from, d_to):
    """Factor that carries a reading at distance d_from from a point source to distance d_to."""
    return (d_from / d_to) ** 2

def end_effect_line(t1, r1, t2, r2):
    """End effect from readings at two set times, with R = rate × (t + delta); returns delta in the unit of t."""
    rate = (r2 - r1) / (t2 - t1)
    return r1 / rate - t1

def end_effect_split(t, r1, rn, n):
    """End effect from one exposure of time t (reading r1) and n exposures of t/n each (total reading rn)."""
    return t * (rn - r1) / (n * r1 - rn)

def set_time(dose, rate, delta):
    """Timer setting that delivers `dose` when the dose is rate × (t + delta)."""
    return dose / rate - delta

RATIO_AIR = "[(μ̄<sub>en</sub>/ρ)<sup>w</sup><sub>air</sub>]<sub>air</sub>"
RATIO_WATER = "[(μ̄<sub>en</sub>/ρ)<sup>w</sup><sub>air</sub>]<sub>water</sub>"

# ---------------------------------------------------------------- worked examples
U_EX = (0.4, 0.6, 0.5, 2.0)                                       # %, illustrative: primary standard, ADCL transfer, clinic reading, B_w and the ratio
uc_ex, uc_ex_nof, uc_ex_lin = combined(*U_EX), combined(*U_EX[:3]), sum(U_EX)

H1, N1, H2, N2, HU = 1.80, 4.735e7, 2.80, 4.689e7, 2.40          # mm Al and Gy/C: two illustrative ADCL beams and the clinical HVL
fr_ex = (HU - H1) / (H2 - H1)
NK_EX = nk_at(HU, H1, N1, H2, N2)
NK_USE = round(NK_EX, -4)                                         # 4.707 × 10^7 Gy/C, as printed
near_ex = 100 * (1 - N2 / NK_EX)                                  # % low if the nearer beam's coefficient is taken

M_EX, BW_EX, PST_EX, RAT_EX = 13.06, 1.16, 1.000, 1.023          # nC/min and illustrative TG-61 factors: 100 kV, HVL 2.40 mm Al, 5 cm applicator, SSD 15 cm
ka_ex = k_air(M_EX, NK_USE)
kw_ex = ka_ex * RAT_EX
d_ex = d_in_air(M_EX, NK_USE, BW_EX, PST_EX, RAT_EX)
rise_ex = 100 * (d_ex / ka_ex - 1)

T1E, R1E, T2E, R2E = 0.50, 6.21, 2.00, 24.06                      # min and nC: readings at two set times
DR_E, DOSE_E = 0.730, 3.00                                        # Gy/min and Gy
rate_e = (R2E - R1E) / (T2E - T1E)
delta_e = end_effect_line(T1E, R1E, T2E, R2E)                     # min
t_plain_e = DOSE_E / DR_E
t_set_e = set_time(DOSE_E, DR_E, delta_e)
over_e = 100 * delta_e / t_plain_e                                # % too much dose if the end effect is ignored
mm_e, ss_e = divmod(60 * t_set_e, 60)

# ---------------------------------------------------------------- numbers in the questions
U_Q = (0.3, 0.7, 1.2, 0.9)                                        # %, illustrative
uc_q, uc_q_lin, uc_q_max = combined(*U_Q), sum(U_Q), max(U_Q)
uc_q_root = math.sqrt(sum(U_Q))                                   # the root of the plain sum, without squaring

HA, NA, HB, NB, HC = 3.00, 4.668e7, 5.00, 4.616e7, 3.70          # typed N_K interpolation
fr_q = (HC - HA) / (HB - HA)
nk_q = nk_at(HC, HA, NA, HB, NB)
near_q = 100 * (NA / nk_q - 1)

M_C, NK_C, BW_C, PST_C, RAT_C = 1.538, 1.426e9, 1.06, 1.000, 1.025   # 50 kV contact beam, parallel-plate chamber
DOSE_C = 4.00                                                     # Gy prescribed at the surface
ka_c = k_air(M_C, NK_C)
d_c = d_in_air(M_C, NK_C, BW_C, PST_C, RAT_C)
d_c_nobw, d_c_norat, d_c_divbw = d_in_air(M_C, NK_C, 1.0, PST_C, RAT_C), d_in_air(M_C, NK_C, BW_C, PST_C, 1.0), d_in_air(M_C, NK_C, 1 / BW_C, PST_C, RAT_C)
t_c, t_c_nobw, t_c_norat, t_c_divbw = (DOSE_C / x for x in (d_c, d_c_nobw, d_c_norat, d_c_divbw))

SSD_I, OFF_I = 20.0, 0.4                                          # cm: closed applicator, chamber center beyond its end
M_I, NK_I, BW_I, PST_I, RAT_I = 11.42, 4.652e7, 1.24, 1.000, 1.031
ka_i = k_air(M_I, NK_I)
f_i = isq(SSD_I + OFF_I, SSD_I)
d_i_noisq = d_in_air(M_I, NK_I, BW_I, PST_I, RAT_I)
d_i = d_i_noisq * f_i
d_i_inv, d_i_lin = d_i_noisq / f_i, d_i_noisq * (SSD_I + OFF_I) / SSD_I
low_i = 100 * (1 - d_i_noisq / d_i)

M_W, NK_W, PQ_W, PSH_W, RAT_W = 9.42, 4.810e7, 1.010, 0.997, 1.082   # 250 kV beam, in-water method
ka_w = k_air(M_W, NK_W)
d_w = d_in_water(M_W, NK_W, PQ_W, PSH_W, RAT_W)
d_w_nopq, d_w_norat, d_w_inv = d_in_water(M_W, NK_W, 1.0, PSH_W, RAT_W), d_in_water(M_W, NK_W, PQ_W, PSH_W, 1.0), d_in_water(M_W, NK_W, PQ_W, PSH_W, 1 / RAT_W)

hand = 100 * (isq(15.3, 15.0) - 1)                                # % change for a chamber 3 mm farther away at SSD 15 cm

T_S, R1_S, R4_S, N_S = 2.00, 23.84, 24.54, 4                      # min, nC, nC: one exposure against four
delta_s = end_effect_split(T_S, R1_S, R4_S, N_S)                  # min
delta_s_sec = 60 * delta_s
wrong_s_one = 60 * (R4_S - R1_S) / (R1_S / T_S)                   # s: the whole difference taken as one end effect
wrong_s_den = 60 * T_S * (R4_S - R1_S) / (N_S * R1_S)             # s: n R1 in the denominator

DOSE_N, DR_N, CROSS_N = 2.50, 0.850, 0.90                         # Gy, Gy/min, s where the line of readings crosses the time axis
delta_n = -CROSS_N / 60                                           # min
t_n = set_time(DOSE_N, DR_N, delta_n)
t_n_plain, t_n_sign, t_n_unit = DOSE_N / DR_N, set_time(DOSE_N, DR_N, -delta_n), DOSE_N / DR_N + CROSS_N

TOPIC = dict(
    id="kv-dosimetry", domain=2, sub="II.B", title="Kilovoltage dosimetry and calibration traceability",
    ref=dict(aapm="TG-61", khan="", ford="16–17"),
    guide=[
        H("Primary standards"),
        P("A primary standard realizes a quantity from its definition, from measured charge, mass, volume, or temperature and physical constants, without calibration against another instrument of that quantity. National laboratories hold them, NIST in the United States, including these three."),
        TABLE(["Standard", "Quantity", "Beams", "Principle"], [
            ["Free-air ionization chamber", "Air kerma", "Kilovoltage x-rays, up to about 300 kV", "Charge from a beam-defined volume of air, with the plates beyond the range of the secondary electrons"],
            ["Graphite-walled cavity chamber", "Air kerma", "Co-60", "Charge in an air cavity of known volume; cavity theory, with wall corrections, gives the air kerma"],
            ["Water calorimeter", "Absorbed dose to water", "Co-60", "Temperature rise of irradiated water"]]),
        EQ("K<sub>air</sub> = (Q / m<sub>air</sub>) (W<sub>air</sub>/e) / (1 − g) × corrections   (free-air chamber; m<sub>air</sub> = mass of air in the defined volume)"),
        P("The secondary electrons set in motion in the measured air must spend nearly all their energy before they reach the plates, so the plate separation grows with photon energy. For Co-60 they travel metres in air, so air kerma is realized instead with a graphite-walled cavity chamber, whose wall supplies the electrons that cross the cavity. A water calorimeter is corrected for the heat defect, the share of the absorbed energy that drives chemical change instead of heating the water."),

        H("Traceability chain and calibration coefficients"),
        P("NIST calibrates the secondary standard chambers of each Accredited Dosimetry Calibration Laboratory (ADCL), and the ADCL calibrates a clinic's reference chamber by substitution: it determines the quantity at a point in a reference beam with its own standard, places the clinic's chamber at that point, and divides by that chamber's corrected reading. The result is a calibration coefficient, valid only for its quantity and the beam quality of the calibration."),
        UL("N<sub>K</sub>: air kerma free in air at the chamber's reference point, with the chamber absent, per unit corrected reading (Gy/C), for a stated x-ray beam quality; the basis of TG-61.",
           "N<sub>D,w</sub><sup>60Co</sup>: absorbed dose to water at that point in water per unit corrected reading in Co-60, traced to the water calorimeter; the basis of TG-51."),
        P("In the clinic, field chambers are cross-calibrated against the reference chamber, which is compared between ADCL calibrations with a second chamber or a check source, a redundancy check. After a failed check, damage, or repair, it returns to an ADCL. Each step adds uncertainty; independent components add in quadrature, so the largest dominates. A primary standard carries a few tenths of a percent, a megavoltage reference dose in the clinic about 1 to 2%, and a kilovoltage dose a few percent."),
        EQ("u<sub>c</sub> = √(u<sub>1</sub>² + u<sub>2</sub>² + …)   (independent relative standard uncertainties)"),
        EX("Combined uncertainty of a kilovoltage calibration",
           STEM("A surface dose rate is set with the TG-61 in-air method. The relative standard uncertainties of the steps are illustrative.",
                [f"primary standard: {U_EX[0]:.1f}%", f"transfer at the ADCL: {U_EX[1]:.1f}%", f"clinic reading and its corrections: {U_EX[2]:.1f}%", f"B<sub>w</sub> and the coefficient ratio: {U_EX[3]:.1f}%"],
                "Find the [[combined standard uncertainty]]."),
           [f"Sum of squares = {U_EX[0]:.1f}² + {U_EX[1]:.1f}² + {U_EX[2]:.1f}² + {U_EX[3]:.1f}² = {sum(x * x for x in U_EX):.2f}",
            f"u<sub>c</sub> = √{sum(x * x for x in U_EX):.2f} = {uc_ex:.2f}%"],
           f"{uc_ex:.2f}%. The {U_EX[3]:.1f}% term dominates: without it the chain gives {uc_ex_nof:.2f}%, and a linear sum would overstate the total as {uc_ex_lin:.1f}%."),

        H("Kilovoltage beam quality"),
        P("A kilovoltage beam is specified by its first HVL, in mm Al or mm Cu, with the kVp. The kVp fixes only the end point of the spectrum; the filtration and the generator waveform shape the rest, so two 100 kV beams can differ in HVL by a factor of two or more. The chamber response, the backscatter, and the averaged energy-absorption coefficients all follow the spectrum."),
        P("N<sub>K</sub> varies with beam quality because the wall, central electrode, or window is not air. The photoelectric effect, important at these energies, rises steeply with atomic number and falls steeply with photon energy, so the ionization in the cavity per unit air kerma changes with the spectrum; the wall also absorbs the softest photons. An ADCL therefore calibrates the chamber in several standard beams, and N<sub>K</sub> is taken at the clinical beam's HVL, between calibration beams of similar kVp that bracket it."),
        EX("N<sub>K</sub> at the beam's HVL",
           STEM("An ADCL calibrates a Farmer-type chamber in two x-ray beams of similar kVp that bracket a 100 kV superficial beam. The coefficients are illustrative, and N<sub>K</sub> is taken as linear in HVL between them.",
                [f"calibration beam 1: HVL = {H1:.2f} mm Al, N<sub>K</sub> = {sci(N1, 4)} Gy/C", f"calibration beam 2: HVL = {H2:.2f} mm Al, N<sub>K</sub> = {sci(N2, 4)} Gy/C", f"clinical beam: HVL = {HU:.2f} mm Al"],
                "Find [[N<sub>K</sub>]] for the clinical beam."),
           [f"Fraction of the interval = ({HU:.2f} − {H1:.2f}) / ({H2:.2f} − {H1:.2f}) = {fr_ex:.3f}",
            f"N<sub>K</sub> = {N1 / 1e7:.3f} + {fr_ex:.3f} × ({N2 / 1e7:.3f} − {N1 / 1e7:.3f}) = {NK_EX / 1e7:.4f} × 10<sup>7</sup> Gy/C"],
           f"{sci(NK_USE, 4)} Gy/C. The nearer calibration beam's coefficient alone would be {near_ex:.1f}% low."),

        H("TG-61 in-air and in-water methods"),
        EQ(f"D<sub>w,z=0</sub> = M N<sub>K</sub> B<sub>w</sub> P<sub>stem,air</sub> {RATIO_AIR}   (in-air method)",
           f"D<sub>w,z=2 cm</sub> = M N<sub>K</sub> P<sub>Q,cham</sub> P<sub>sheath</sub> {RATIO_WATER}   (in-water method)",
           "M = P<sub>TP</sub> P<sub>ion</sub> P<sub>pol</sub> P<sub>elec</sub> M<sub>raw</sub>, as for any chamber"),
        P("In the in-air method the chamber is read free in air with its reference point where the skin will be, at the end of an open applicator, so M N<sub>K</sub> is the air kerma there. The ratio of mass energy-absorption coefficients, water to air, averaged over the spectrum, converts it to water kerma, taken as the dose because the secondary electrons travel a millimetre or less. The backscatter factor B<sub>w</sub>, the water kerma at the surface of a full-scatter water phantom divided by the water kerma at that point free in air, adds the photons scattered back. TG-61 tabulates it: it rises with field size and, through the superficial range, with HVL, and changes less with SSD. Thin anatomy such as the ear or nose returns less backscatter, so its surface dose falls below the calibrated value. The stem correction P<sub>stem,air</sub> accounts for the change in scatter from the chamber stem when the field differs from the calibration field."),
        P("In the in-water method the chamber's center sits at 2 cm depth. P<sub>Q,cham</sub> accounts for the change in the chamber's response from calibration free in air to measurement in water: the displaced water, the stem, and the changed spectrum and direction of the photons. P<sub>sheath</sub> corrects for the waterproofing sleeve. Below 100 kV only the in-air method applies; from 100 to 300 kV the in-air method serves skin lesions and the in-water method lesions at depth."),
        TABLE(["Condition", "In-air method", "In-water method"], [
            ["Tube potential", "40 to 300 kV", "100 to 300 kV"],
            ["Reference point", "Surface of a water phantom, on the axis", "Chamber center at 2 cm depth in water"],
            ["Chamber", "Parallel-plate below about 70 kV; cylindrical, usually Farmer-type, above", "Cylindrical, in a waterproof sleeve"],
            ["Factors after N<sub>K</sub>", "B<sub>w</sub>, P<sub>stem,air</sub>, and the ratio averaged free in air", "P<sub>Q,cham</sub>, P<sub>sheath</sub>, and the ratio averaged at 2 cm in water"],
            ["Use", "Contact, superficial, and orthovoltage beams; dose at the skin", "Beams of 100 kV and above; dose at depth"]]),
        EX("Surface dose rate from an in-air reading",
           STEM(f"A 100 kV superficial beam (HVL {HU:.2f} mm Al) with a 5 cm diameter open applicator at SSD 15 cm is calibrated with the TG-61 in-air method, the chamber's center at the end of the applicator. B<sub>w</sub> and the coefficient ratio are illustrative table entries.",
                [f"M = {M_EX:.2f} nC per minute (fully corrected)", f"N<sub>K</sub> = {sci(NK_USE, 4)} Gy/C", f"B<sub>w</sub> = {BW_EX:.2f}", f"P<sub>stem,air</sub> = {PST_EX:.3f}", f"{RATIO_AIR} = {RAT_EX:.3f}"],
                "Find the [[dose rate to water at the surface]]."),
           [f"N<sub>K</sub> = {sci(NK_USE, 4)} Gy/C = {NK_USE * 1e-9:.5f} Gy/nC",
            f"Air kerma rate = {M_EX:.2f} × {NK_USE * 1e-9:.5f} = {ka_ex:.4f} Gy/min",
            f"Water kerma free in air = {ka_ex:.4f} × {RAT_EX:.3f} = {kw_ex:.4f} Gy/min",
            f"D = {kw_ex:.4f} × {BW_EX:.2f} × {PST_EX:.3f} = {d_ex:.4f} Gy/min"],
           f"{d_ex:.4f} Gy/min at the surface, {rise_ex:.0f}% above the air kerma rate, mostly from the backscatter."),

        H("Output checks and timer end effect"),
        P("Between full calibrations, each beam's output is checked for constancy with the same chamber, electrometer, and holder at the applicator, corrected for temperature and pressure, against a baseline taken immediately after the calibration. Each combination of kV, filter, and applicator has its own output. A wrong filter changes both the output and the HVL, so the filter in place is confirmed before each treatment, by an interlock where the unit has one."),
        P("In a unit that ends each exposure on a timer, the dose rate is below its full value while the tube voltage and current rise and fall, and the timer need not start and stop with the beam. The dose then equals the full rate times t + δ, where t is the set time and δ, the end effect, is a fixed time, positive or negative. Readings at several set times lie on a line that crosses the time axis at −δ; alternatively, one exposure of time t is compared with n exposures of t/n. A fixed δ matters most in short exposures."),
        EQ("D = Ḋ (t + δ),   so the timer setting for a dose D is t = D/Ḋ − δ",
           "δ = t (R<sub>n</sub> − R<sub>1</sub>) / (n R<sub>1</sub> − R<sub>n</sub>)   (R<sub>1</sub>: one exposure of t; R<sub>n</sub>: total of n exposures of t/n)"),
        EX("Timer end effect",
           STEM("A timer-controlled superficial unit is checked with a chamber in a fixed holder, and a fraction is then planned.",
                [f"set time {T1E:.2f} min: reading = {R1E:.2f} nC", f"set time {T2E:.2f} min: reading = {R2E:.2f} nC", f"surface dose rate = {DR_E:.3f} Gy/min", f"prescribed dose = {DOSE_E:.2f} Gy"],
                "Find the [[end effect δ]] and the [[timer setting]]."),
           [f"Slope = ({R2E:.2f} − {R1E:.2f}) / ({T2E:.2f} − {T1E:.2f}) = {rate_e:.2f} nC/min",
            f"δ = {R1E:.2f} / {rate_e:.2f} − {T1E:.2f} = {delta_e:+.4f} min = {60 * delta_e:+.2f} s",
            f"D/Ḋ = {DOSE_E:.2f} / {DR_E:.3f} = {t_plain_e:.3f} min",
            f"t = {t_plain_e:.3f} − {delta_e:.4f} = {t_set_e:.3f} min"],
           f"δ = {60 * delta_e:+.1f} s, and the timer is set to {t_set_e:.3f} min ({mm_e:.0f} min {ss_e:.0f} s). Ignoring δ would give {over_e:.1f}% too much dose."),
    ],
    cards=[
        F("Primary standard", "An instrument that realizes a quantity from its definition, from measured charge, mass, volume, or temperature, without calibration against another instrument of that quantity."),
        F("Primary standards for external beams", ["Free-air ionization chamber: air kerma, kilovoltage x-rays", "Graphite-walled cavity chamber: air kerma, Co-60", "Water calorimeter: absorbed dose to water, Co-60"]),
        F("Upper energy limit of a free-air chamber", "About 300 kV. The plates must lie beyond the range of the secondary electrons in air, which reaches metres for Co-60."),
        F("Traceability chain", "NIST primary standard, then the ADCL's secondary standard, then the clinic's reference chamber, then field chambers cross-calibrated against it."),
        F("Calibration by substitution", "The ADCL measures the quantity at a point with its standard, places the clinic's chamber at that point, and divides the quantity by that chamber's corrected reading."),
        F("Air-kerma calibration coefficient N<sub>K</sub>", "Air kerma free in air at the chamber's reference point, with the chamber absent, per unit corrected reading (Gy/C), for a stated x-ray beam quality."),
        F("Redundancy check", "Comparison of the reference chamber with a second chamber or a check source between ADCL calibrations. A failed check, damage, or repair sends it back to an ADCL."),
        F("Uncertainty along the chain", "A few tenths of a percent at the primary standard, about 1 to 2% for a megavoltage reference dose, a few percent for a kilovoltage dose. Independent components add in quadrature.",
          w=[f"{U_EX[0]:.1f}%, {U_EX[1]:.1f}%, {U_EX[2]:.1f}%, and {U_EX[3]:.1f}%: √{sum(x * x for x in U_EX):.2f} = {uc_ex:.2f}%"]),
        F("Kilovoltage beam quality", "The first HVL, in mm Al or mm Cu, with the kVp. The kVp alone does not fix the spectrum, which filtration and waveform change."),
        F("Energy dependence of N<sub>K</sub>", "Wall, electrode, and window are not air, and their photoelectric absorption changes steeply with energy. N<sub>K</sub> is taken at the beam's HVL, between bracketing calibration beams of similar kVp."),
        F("TG-61 in-air method", f"D<sub>w,z=0</sub> = M N<sub>K</sub> B<sub>w</sub> P<sub>stem,air</sub> {RATIO_AIR}: dose to water at the surface from a reading free in air, 40 to 300 kV."),
        F("Backscatter factor B<sub>w</sub>", "Water kerma at the surface of a full-scatter water phantom divided by water kerma at that point free in air. Rises with field size and, through the superficial range, with HVL; changes less with SSD."),
        F("Surface dose on thin anatomy", "The ear or nose returns less backscatter than a full-scatter phantom, so the surface dose falls below the value calibrated with B<sub>w</sub>."),
        F("TG-61 in-water method", f"D<sub>w,z=2 cm</sub> = M N<sub>K</sub> P<sub>Q,cham</sub> P<sub>sheath</sub> {RATIO_WATER}, with a cylindrical chamber's center at 2 cm depth, 100 to 300 kV."),
        F("Chambers for kilovoltage calibration", "Parallel-plate below about 70 kV (TG-61); cylindrical, usually Farmer-type, above that and for the in-water method."),
        F("Timer end effect", "D = Ḋ (t + δ), with δ fixed for every exposure. Found from readings at several set times; the timer setting for a dose D is D/Ḋ − δ.",
          w=[f"Readings {R1E:.2f} nC at {T1E:.2f} min and {R2E:.2f} nC at {T2E:.2f} min: slope {rate_e:.2f} nC/min, δ = {R1E:.2f}/{rate_e:.2f} − {T1E:.2f} = {delta_e:+.4f} min"]),
    ],
)

PROBLEMS = [
    # ---- 1-2: primary standards
    PR(STEM("A national laboratory realizes air kerma for a 100 kV x-ray beam from first principles.", [], "Which [[instrument]] serves as this primary standard?"),
       "A free-air ionization chamber", ["A graphite-walled cavity chamber", "A water calorimeter", "A Farmer-type chamber calibrated at an ADCL"],
       "A free-air chamber measures the charge from a beam-defined volume of air, with its plates beyond the range of the secondary electrons, which kilovoltage photons allow. The graphite cavity chamber is the air-kerma standard for Co-60, the water calorimeter realizes absorbed dose to water, and a chamber calibrated at an ADCL is a secondary instrument.", lvl="Easy"),
    PR(STEM("NIST realizes air kerma for Co-60 γ rays with a graphite-walled cavity chamber, not with a free-air chamber.", [], "What is the [[reason]]?"),
       "The secondary electrons travel metres in air, so a free-air chamber would be impractically large",
       ["Co-60 photons produce too few ions in air for a free-air chamber to measure", "A free-air chamber cannot collect the charge of a continuous beam", "Graphite has the atomic number of air, so the cavity needs no correction"],
       "The plates of a free-air chamber must lie beyond the range of the secondary electrons in air, metres for the electrons that Co-60 photons set in motion. A graphite wall thick enough for charged-particle equilibrium supplies the electrons instead, and cavity theory gives the air kerma. Graphite (Z = 6) is not air, so the cavity theory carries material ratios and wall corrections; and free-air chambers measure continuous kilovoltage beams routinely.", lvl="Moderate"),

    # ---- 3-6: traceability chain and coefficients
    SORT(STEM("A kilovoltage beam is calibrated at a clinic in the United States.", [], "Rank the [[instruments]] from the primary standard to the clinic's working instrument."), ["1st", "2nd", "3rd", "4th"],
         [("Free-air chamber at NIST", 0), ("Secondary standard chamber at an ADCL", 1), ("Clinic's reference chamber with its N<sub>K</sub>", 2), ("Field chamber cross-calibrated in the clinic", 3)],
         "NIST calibrates the ADCL's secondary standards against its free-air chamber, the ADCL calibrates the clinic's reference chamber by substitution, and the clinic cross-calibrates its field chambers against the reference chamber. Each step adds uncertainty.", lvl="Easy", mode="rank", cap=1),
    PR(STEM("An ADCL returns a chamber with an air-kerma calibration coefficient N<sub>K</sub> for a 100 kV beam of stated HVL.", [], "What does [[N<sub>K</sub>]] give?"),
       "Air kerma at the chamber's position, chamber absent, per unit corrected reading, in that beam",
       ["Dose to water at 2 cm depth per unit corrected reading, in that beam", "Air kerma per unit corrected reading, in any kilovoltage beam", "Dose to the air in the cavity per unit uncorrected reading, in that beam"],
       "N<sub>K</sub> converts a corrected reading into the air kerma that would exist at the chamber's reference point without the chamber, and it holds for the beam quality of the calibration. Dose to water needs the TG-61 factors as well, and the chamber's response changes with beam quality, so a coefficient for one beam does not hold in every beam.", lvl="Easy"),
    PRN(STEM("The uncertainty of a kilovoltage calibration is estimated from independent components. The relative standard uncertainties are illustrative.",
             [f"primary standard: {U_Q[0]:.1f}%", f"transfer at the ADCL: {U_Q[1]:.1f}%", f"conversion factors: {U_Q[2]:.1f}%", f"clinic measurement: {U_Q[3]:.1f}%"], "What is the [[combined standard uncertainty]]?"),
        uc_q, [uc_q_lin, uc_q_max, uc_q_root], "{:.2f}%",
        f"Independent components add in quadrature: √({U_Q[0]:.1f}² + {U_Q[1]:.1f}² + {U_Q[2]:.1f}² + {U_Q[3]:.1f}²) = √{sum(x * x for x in U_Q):.2f} = {uc_q:.2f}%. The linear sum, {uc_q_lin:.2f}%, treats them as fully correlated; the largest component alone, {uc_q_max:.2f}%, ignores the rest; and the root of the plain sum, {uc_q_root:.2f}%, leaves out the squares.", lvl="Moderate"),
    PR(STEM("A clinic's reference chamber is dropped. Its next redundancy check, against a Sr-90 check source, reads 1.2% below the baseline after the decay and air-density corrections.", [], "What is the [[appropriate action]]?"),
       "Withdraw it from reference use until an ADCL recalibrates it",
       ["Scale its coefficient by the 1.2% change and keep using it", "Keep using it until its next scheduled ADCL calibration", "Keep using it for kilovoltage beams, whose uncertainty is larger"],
       "A fall can change the volume, the wall, or the electrode, and with them the response by a different amount at each beam quality, so one factor from the check source does not restore traceability; the chamber is repaired if needed and recalibrated. A scheduled date does not keep a coefficient valid once a check shows a change, and the larger uncertainty of kilovoltage dosimetry does not absorb a known error.", lvl="Challenging"),

    # ---- 7-10: beam quality
    PR(STEM("A physicist will calibrate a 120 kV superficial beam with AAPM TG-61.", [], "Which [[calibration coefficient]] does the chamber need?"),
       "N<sub>K</sub> from an ADCL in beams matching the user's kVp and HVL",
       ["N<sub>D,w</sub><sup>60Co</sup> from an ADCL, with k<sub>Q</sub> from the TG-51 tables", "N<sub>K</sub> from an ADCL in a Co-60 beam", "N<sub>SK</sub> from an ADCL for a well chamber"],
       "TG-61 is an air-kerma protocol: its chamber needs N<sub>K</sub> measured in x-ray beams close to the user's in kVp and HVL. N<sub>D,w</sub><sup>60Co</sup> and k<sub>Q</sub> serve megavoltage beams under TG-51, an N<sub>K</sub> from Co-60 misses the chamber's energy dependence at kilovoltage energies, and N<sub>SK</sub> belongs to brachytherapy well chambers.", lvl="Easy"),
    PR(STEM("Two superficial units both run at 100 kV. Their added filters differ, and their first HVLs are 2.1 mm Al and 4.8 mm Al.", [], "Why are N<sub>K</sub> and B<sub>w</sub> taken at each beam's [[HVL]] rather than at its kVp?"),
       "Filtration changes the spectrum, and the chamber response and backscatter follow the spectrum",
       ["The kVp of a superficial unit cannot be measured accurately enough", "The HVL sets the maximum photon energy, which the kVp does not", "N<sub>K</sub> and B<sub>w</sub> depend on the tube current, which the HVL reflects"],
       "The kVp fixes only the end point of the spectrum; the filter removes low-energy photons and raises the HVL. The chamber's response per unit air kerma and the backscatter from the phantom both depend on the photon energies present, which the HVL tracks. The maximum energy is set by the kVp, and the tube current changes the output, not the spectrum.", lvl="Moderate"),
    PR(STEM("An ADCL calibrates a Farmer-type chamber, with a graphite wall and an aluminium central electrode, in several x-ray beams, and N<sub>K</sub> differs from beam to beam.", [], "What mainly causes [[N<sub>K</sub> to vary with beam quality]]?"),
       "The wall and electrode are not air, and their photoelectric absorption changes steeply with energy",
       ["W/e of air changes with the photon energy across the kilovoltage range", "Ion recombination in the cavity depends on the HVL of the beam", "The temperature-pressure correction depends on the photon energy"],
       "The photoelectric effect rises steeply with atomic number and falls steeply with photon energy, so an aluminium electrode and a graphite wall change the ionization per unit air kerma differently in soft and hard beams, and the wall absorbs the softest photons. W/e of air is constant for the electrons these beams set in motion, general recombination follows the dose rate, and P<sub>TP</sub> depends only on the air density.", lvl="Moderate"),
    TYPED(STEM("An ADCL calibrates a chamber in two superficial beams of similar kVp that bracket a clinical beam. The coefficients are illustrative, and N<sub>K</sub> is taken as linear in HVL.",
               [f"HVL {HA:.2f} mm Al: N<sub>K</sub> = {sci(NA, 4)} Gy/C", f"HVL {HB:.2f} mm Al: N<sub>K</sub> = {sci(NB, 4)} Gy/C", f"clinical beam: HVL = {HC:.2f} mm Al"],
               "What is [[N<sub>K</sub>]] for the clinical beam, in units of 10<sup>7</sup> Gy/C?"), nk_q / 1e7, 0.001, "× 10⁷ Gy/C",
          f"The clinical HVL lies {HC - HA:.2f}/{HB - HA:.2f} = {fr_q:.2f} of the way from {HA:.2f} to {HB:.2f} mm Al, so N<sub>K</sub> = {NA / 1e7:.3f} + {fr_q:.2f} × ({NB / 1e7:.3f} − {NA / 1e7:.3f}) = {nk_q / 1e7:.4f} × 10<sup>7</sup> Gy/C. Taking the nearer beam's {NA / 1e7:.3f} is {near_q:.2f}% high, outside the tolerance.",
          w=[f"Fraction = ({HC:.2f} − {HA:.2f}) / ({HB:.2f} − {HA:.2f}) = {fr_q:.2f}", f"N<sub>K</sub> = {NA / 1e7:.3f} − {fr_q:.2f} × {(NA - NB) / 1e7:.3f} = {nk_q / 1e7:.4f} × 10<sup>7</sup> Gy/C"], lvl="Moderate"),

    # ---- 11-18: the TG-61 methods
    PR(STEM("A 50 kV contact beam is calibrated with the TG-61 in-air method.", [], "Which [[chamber]] does TG-61 call for?"),
       "A parallel-plate chamber calibrated in air kerma at a matching quality",
       ["A Farmer-type chamber, with its TG-51 k<sub>Q</sub> for the beam", "A well chamber calibrated for brachytherapy sources", "A free-air chamber kept at the clinic as its standard"],
       "Below about 70 kV TG-61 calls for a parallel-plate chamber, calibrated in air kerma in beams that match the user's kVp and HVL; cylindrical chambers serve higher energies. TG-51 factors belong to megavoltage beams, a well chamber measures sources placed inside it, and free-air chambers serve as primary standards at national laboratories.", lvl="Easy"),
    PRN(STEM("A 50 kV contact beam is calibrated with the TG-61 in-air method, a parallel-plate chamber at the end of the applicator. B<sub>w</sub> and the coefficient ratio are illustrative table entries, and the end effect of the timer is negligible.",
             [f"M = {M_C:.3f} nC per minute (fully corrected)", f"N<sub>K</sub> = {sci(NK_C, 4)} Gy/C", f"B<sub>w</sub> = {BW_C:.2f}", f"P<sub>stem,air</sub> = {PST_C:.3f}", f"{RATIO_AIR} = {RAT_C:.3f}", f"prescribed surface dose = {DOSE_C:.2f} Gy"],
             "What [[treatment time]] delivers the prescribed surface dose?"),
        t_c, [t_c_nobw, t_c_norat, t_c_divbw], "{:.2f} min",
        f"The surface dose rate is M N<sub>K</sub> B<sub>w</sub> P<sub>stem,air</sub> × ratio = {M_C:.3f} × 10<sup>−9</sup> C/min × {sci(NK_C, 4)} Gy/C × {BW_C:.2f} × {PST_C:.3f} × {RAT_C:.3f} = {d_c:.3f} Gy/min, so the time is {DOSE_C:.2f} / {d_c:.3f} = {t_c:.2f} min. Leaving out B<sub>w</sub> gives {t_c_nobw:.2f} min, leaving out the ratio {t_c_norat:.2f} min, and dividing by B<sub>w</sub> {t_c_divbw:.2f} min, each an overdose.", lvl="Moderate"),
    PRM(STEM("A superficial beam is calibrated with the TG-61 in-air method.", [], "Which of these changes raise the [[backscatter factor B<sub>w</sub>]]?"),
        ["A larger applicator, at the same HVL and SSD", "A harder filter that raises the HVL from 1 to 3 mm Al"],
        ["A higher tube current, at the same kVp and filter", "A longer treatment time, at the same kVp and filter", "A smaller applicator, at the same HVL and SSD"],
        "A larger field irradiates more water that can scatter photons back to the surface. In the superficial range a harder beam loses fewer photons to photoelectric absorption, so more are scattered back. The tube current and the time change the output, not the spectrum or the field, and a smaller applicator lowers B<sub>w</sub>.", lvl="Moderate"),
    SORT(STEM("TG-61 converts a corrected reading into dose to water with several factors.", [], "Match each [[factor]] to what it accounts for."),
         ["B<sub>w</sub>", "P<sub>stem,air</sub>", "P<sub>Q,cham</sub>", "P<sub>sheath</sub>", "(μ̄<sub>en</sub>/ρ)<sup>w</sup><sub>air</sub>"],
         [("Photons scattered back from the phantom to the surface", 0), ("Scatter from the chamber stem in a field unlike the calibration field", 1), ("The change in chamber response from free air to water", 2),
          ("The waterproofing sleeve around the chamber", 3), ("The step from air kerma to water kerma", 4)],
         "B<sub>w</sub> and P<sub>stem,air</sub> belong to the in-air method, P<sub>Q,cham</sub> and P<sub>sheath</sub> to the in-water method, and the ratio of mass energy-absorption coefficients to both, averaged over the spectrum free in air or at 2 cm in water.", lvl="Moderate", mode="match", cap=1),
    PR(STEM("A lesion on the rim of the ear is treated with a superficial beam. The treatment time comes from the surface dose rate measured with the TG-61 in-air method, with B<sub>w</sub> for a full-scatter water phantom. The ear is about 1 cm thick, with air behind it.", [], "How does the [[surface dose delivered]] compare with the planned dose?"),
       "Lower, because the thin ear scatters fewer photons back than the phantom",
       ["The same, because B<sub>w</sub> depends only on the HVL and the field", "Higher, because the beam is attenuated less in the thin ear", "Higher, because the air behind the ear scatters photons back"],
       "B<sub>w</sub> assumes water deep and wide enough to give full backscatter. An ear about 1 cm thick has little tissue behind its surface, so fewer photons return and the surface dose falls short of the calibrated value. B<sub>w</sub> depends on the scattering volume as well as on the HVL and field, attenuation below the surface does not raise the dose at the surface, and air scatters far less than tissue.", lvl="Challenging"),
    PRN(STEM(f"A superficial beam with a closed-ended applicator at SSD {SSD_I:.1f} cm is calibrated with the TG-61 in-air method. The closed end keeps the Farmer chamber's center {OFF_I:.1f} cm beyond the applicator end. Inverse square from the focal spot is assumed, and the factors are illustrative.",
             [f"M = {M_I:.2f} nC per minute (fully corrected)", f"N<sub>K</sub> = {sci(NK_I, 4)} Gy/C", f"B<sub>w</sub> = {BW_I:.2f}", f"P<sub>stem,air</sub> = {PST_I:.3f}", f"{RATIO_AIR} = {RAT_I:.3f}"],
             "What is the [[dose rate to water at the skin surface]], at the end of the applicator?"),
        d_i, [d_i_noisq, d_i_inv, d_i_lin], "{:.3f} Gy/min",
        f"The air kerma rate at the chamber is {M_I:.2f} × {NK_I * 1e-9:.5f} = {ka_i:.4f} Gy/min. Carrying it {OFF_I:.1f} cm closer to the source multiplies it by ({SSD_I + OFF_I:.1f}/{SSD_I:.1f})² = {f_i:.4f}, giving {ka_i * f_i:.4f} Gy/min at the skin, and D = {ka_i * f_i:.4f} × {BW_I:.2f} × {PST_I:.3f} × {RAT_I:.3f} = {d_i:.3f} Gy/min. Without the distance correction the result is {d_i_noisq:.3f}, {low_i:.1f}% low; the inverted factor gives {d_i_inv:.3f} and the plain ratio of distances {d_i_lin:.3f}.", lvl="Challenging"),
    PRM(STEM("A 250 kV orthovoltage beam (HVL 2.0 mm Cu) is calibrated with the TG-61 in-water method, the chamber's center at 2 cm depth.", [], "Which of these factors enter the [[dose at 2 cm]]?"),
        ["P<sub>Q,cham</sub>", "P<sub>sheath</sub>", RATIO_WATER], ["B<sub>w</sub>", "P<sub>stem,air</sub>", "k<sub>Q</sub> from the TG-51 tables"],
        f"In water, D = M N<sub>K</sub> P<sub>Q,cham</sub> P<sub>sheath</sub> {RATIO_WATER}. The phantom's scatter reaches the chamber directly, so no backscatter factor enters, and P<sub>Q,cham</sub> covers the stem in water. k<sub>Q</sub> converts a Co-60 dose-to-water coefficient for megavoltage beams and has no place in this air-kerma protocol.", lvl="Challenging"),
    PRN(STEM("A 250 kV orthovoltage beam is calibrated with the TG-61 in-water method, a Farmer-type chamber in its sleeve with the center at 2 cm depth. The factors are illustrative table entries.",
             [f"M = {M_W:.2f} nC per minute (fully corrected)", f"N<sub>K</sub> = {sci(NK_W, 4)} Gy/C", f"P<sub>Q,cham</sub> = {PQ_W:.3f}", f"P<sub>sheath</sub> = {PSH_W:.3f}", f"{RATIO_WATER} = {RAT_W:.3f}"],
             "What is the [[dose rate to water at 2 cm]]?"),
        d_w, [d_w_nopq, d_w_norat, d_w_inv], "{:.3f} Gy/min",
        f"D = M N<sub>K</sub> P<sub>Q,cham</sub> P<sub>sheath</sub> × ratio = {M_W:.2f} × {NK_W * 1e-9:.5f} × {PQ_W:.3f} × {PSH_W:.3f} × {RAT_W:.3f} = {d_w:.4f} Gy/min. Leaving out P<sub>Q,cham</sub> gives {d_w_nopq:.3f}, leaving out the ratio gives {d_w_norat:.3f}, and dividing by it gives {d_w_inv:.3f} Gy/min.", lvl="Moderate"),

    # ---- 19-21: output checks and the end effect
    PR(STEM("The output of a superficial unit is checked for constancy between full calibrations.", [], "Which [[setup]] gives a reading that can be compared with the baseline?"),
       "The baseline's chamber, electrometer, and holder, with P<sub>TP</sub> applied",
       ["Any calibrated chamber at the applicator end, without P<sub>TP</sub>", "The baseline's chamber, held by hand at the applicator end, with P<sub>TP</sub>", "The baseline's chamber and holder, with the baseline's P<sub>TP</sub> reused"],
       f"A constancy check compares like with like: the same chamber and electrometer in the same holder and geometry, with the air-density correction of the day. A hand-held chamber changes the distance, and at SSD 15 cm a 3 mm shift changes the reading by about {hand:.0f}%; the baseline's P<sub>TP</sub> ignores the day's temperature and pressure; and another chamber has its own response.", lvl="Easy"),
    PRN(STEM(f"Readings of a timer-controlled superficial unit against set time lie on a line that crosses the time axis at t = +{CROSS_N:.2f} s.",
             [f"prescribed dose = {DOSE_N:.2f} Gy", f"surface dose rate = {DR_N:.3f} Gy/min"], "What [[timer setting]] delivers the prescribed dose?"),
        t_n, [t_n_plain, t_n_sign, t_n_unit], "{:.3f} min",
        f"D = Ḋ (t + δ) is zero at t = −δ, so δ = −{CROSS_N:.2f} s = {delta_n:.3f} min: the unit delivers less than the set time implies. t = D/Ḋ − δ = {t_n_plain:.3f} + {-delta_n:.3f} = {t_n:.3f} min. Ignoring δ gives {t_n_plain:.3f}, the wrong sign gives {t_n_sign:.3f}, and adding {CROSS_N:.2f} min in place of {CROSS_N:.2f} s gives {t_n_unit:.3f} min.", lvl="Moderate"),
    TYPED(STEM("The end effect of a timer-controlled superficial unit is measured with a chamber in a fixed holder.",
               [f"one exposure of {T_S:.2f} min: reading = {R1_S:.2f} nC", f"{N_S} exposures of {T_S / N_S:.2f} min each: total reading = {R4_S:.2f} nC"], "What is the [[end effect δ]], in seconds?"), delta_s_sec, 0.02, "s",
          f"Each exposure carries one δ, so R<sub>1</sub> = Ṙ (t + δ) and R<sub>4</sub> = Ṙ (t + 4δ). Solving, δ = t (R<sub>4</sub> − R<sub>1</sub>) / (4R<sub>1</sub> − R<sub>4</sub>) = {T_S:.2f} × {R4_S - R1_S:.2f} / {N_S * R1_S - R4_S:.2f} = {delta_s:.4f} min = {delta_s_sec:.2f} s. Taking the {R4_S - R1_S:.2f} nC difference as one δ gives {wrong_s_one:.2f} s, three times too much, because four exposures carry three more ends than one.",
          w=[f"R<sub>4</sub> − R<sub>1</sub> = {R4_S:.2f} − {R1_S:.2f} = {R4_S - R1_S:.2f} nC", f"4R<sub>1</sub> − R<sub>4</sub> = {N_S * R1_S:.2f} − {R4_S:.2f} = {N_S * R1_S - R4_S:.2f} nC",
             f"δ = {T_S:.2f} min × {R4_S - R1_S:.2f} / {N_S * R1_S - R4_S:.2f} = {delta_s:.4f} min = {delta_s_sec:.2f} s"], lvl="Challenging"),
]

INLINE = {0: [1, 2], 1: [3, 4, 5], 2: [7, 8, 9], 3: [11, 12, 13, 14]}      # questions on the last section, and the rest, form the practice set

TERMS = ["primary standard", "heat defect", "secondary standard", "substitution", "redundancy check", "backscatter factor", "stem correction", "end effect"]

TAKE = [
    ["Free-air chamber: air kerma for kilovoltage x-rays. Graphite-walled cavity chamber: air kerma in Co-60. Water calorimeter: dose to water in Co-60.",
     "The free-air chamber stops at about 300 kV, because the electron range in air outgrows any practical plate separation."],
    ["NIST primary standard, ADCL secondary standard by substitution, clinic reference chamber, field chambers.",
     "N<sub>K</sub> (air kerma) or N<sub>D,w</sub> (dose to water) holds only for its own beam quality.",
     "Independent uncertainties add in quadrature: a few tenths of a percent at NIST, a few percent for a kilovoltage dose."],
    ["Kilovoltage quality: first HVL with the kVp; the kVp alone does not fix the spectrum.",
     "N<sub>K</sub> varies with HVL and is taken at the beam's HVL between bracketing calibration beams of similar kVp."],
    [f"In air, 40 to 300 kV: D<sub>w,z=0</sub> = M N<sub>K</sub> B<sub>w</sub> P<sub>stem,air</sub> × ratio. B<sub>w</sub> rises with field size and, in superficial beams, with HVL.",
     "In water, 100 to 300 kV: D<sub>w,z=2 cm</sub> = M N<sub>K</sub> P<sub>Q,cham</sub> P<sub>sheath</sub> × ratio.",
     "Parallel-plate chamber below about 70 kV; cylindrical above and in water."],
    ["Constancy: the baseline's chamber, electrometer, and holder, with P<sub>TP</sub>; each kV, filter, and applicator has its own output.",
     "Timer units: D = Ḋ (t + δ), so the setting is D/Ḋ − δ; δ matters most in short exposures."],
]
