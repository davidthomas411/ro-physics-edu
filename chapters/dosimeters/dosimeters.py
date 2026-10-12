from blocks import *
import math

# ---------------------------------------------------------------- constants quoted in the text
W_AIR = 33.97                       # eV per ion pair in dry air
W_SI = 3.6                          # eV per electron-hole pair in silicon
RHO_SI, RHO_AIR = 2.33, 0.001205    # g/cm³; air at 20 °C and 101.3 kPa
EPS_FE = 2174.0                     # L mol⁻¹ cm⁻¹, ferric ion at 304 nm and 25 °C (one published value; others run from 2,160 to 2,200)
RHO_FRICKE = 1.024                  # kg/L
G_100EV = 15.5                      # Fe³⁺ ions per 100 eV in megavoltage beams
E_CHARGE, N_A = 1.602176634e-19, 6.02214076e23
C_WATER = 4186.0                    # J kg⁻¹ K⁻¹


def per_volume(rho, w):
    """Charge freed per unit volume per unit absorbed dose, in relative units: density over the energy per charge pair."""
    return rho / w


def in_vivo(r, n, *cf):
    """Entrance dose at d_max: reading times calibration factor times every correction factor."""
    return r * n * math.prod(cf)


def cf_temp(alpha, dt):
    """Temperature correction of a diode whose sensitivity rises by alpha per °C, warmer by dt than at calibration."""
    return 1 / (1 + alpha * dt)


def tld_dose(m, ecf, d_cal, m_cal):
    """Dose from a chip reading, its element correction factor, and calibration chips given d_cal that read m_cal (mean, corrected)."""
    return m * ecf * d_cal / m_cal


def od(i0, i):
    return math.log10(i0 / i)


def g_mol_per_j(g100):
    """A G value in ions per 100 eV, converted to mol/J."""
    return g100 / (100 * E_CHARGE * N_A)


def fricke_dose(da, eps, l, rho, g):
    """Gy from the change in absorbance: eps in L mol⁻¹ cm⁻¹, l in cm, rho in kg/L, g in mol/J."""
    return da / (eps * l * rho * g)


def pm(x, d=1):
    return f"{x:+.{d}f}".replace("-", "−")


def sig2(v):
    """Two significant figures with thousands separators: 18,246 is written 18,000."""
    return f"{float(f'{v:.2g}'):,g}"


# ---------------------------------------------------------------- numbers in the text and the worked examples
dens = RHO_SI / RHO_AIR
e_ratio = W_AIR / W_SI
sens = per_volume(RHO_SI, W_SI) / per_volume(RHO_AIR, W_AIR)
dens_r, sens_r = int(round(dens, -2)), int(round(sens, -3))

ex_r, ex_n, ex_fs, ex_w, ex_alpha, ex_dt, ex_plan = 184.0, 1.065, 0.993, 1.024, 0.0030, 31 - 22, 198.0
ex_cft = cf_temp(ex_alpha, ex_dt)
ex_d = in_vivo(ex_r, ex_n, ex_fs, ex_w, ex_cft)
ex_diff = 100 * (ex_d - ex_plan) / ex_plan

tl_m, tl_ecf, tl_dcal, tl_mcal = 26.4, 1.037, 1.00, 25.1
tl_n = tl_dcal / tl_mcal
tl_d = tld_dose(tl_m, tl_ecf, tl_dcal, tl_mcal)

od_u, od_e = od(1000, 800), od(1000, 160)
od_net = od_e - od_u
od_t = 160 / 1000

fr_da, fr_l, fr_g = 0.150, 1.00, 1.61e-6
fr_c = fr_da / (EPS_FE * fr_l)
fr_d = fricke_dose(fr_da, EPS_FE, fr_l, RHO_FRICKE, fr_g)

cal_mk = 1000 / C_WATER                                     # mK per Gy in water

TOPIC = dict(
    id="dosimeters", domain=2, sub="II.B", title="Diodes, luminescent dosimeters, and film",
    ref=dict(aapm="TG-62, TG-191, TG-235", khan="", ford="17"),
    guide=[
        H("Semiconductor detectors"),
        P(f"[[1|A silicon diode is a p–n junction whose built-in field collects the electron–hole pairs that radiation frees, with no bias voltage.]] A pair costs about {W_SI:g} eV, against {W_AIR} eV per ion pair in air, and silicon is about {dens_r:,} times denser, [[1|so the same dose frees about {sens_r:,} times more charge per unit volume than air]]."),
        P("[[1|Radiation damage lowers the sensitivity as dose accumulates, less in p-type silicon, the usual choice.]] The sensitivity also rises with temperature, by 0.1% to 0.5% per °C (TG-62; typically about 0.3%), rises with the dose per pulse (so it falls as the SSD grows) by an amount that varies among diodes, and changes with the beam angle."),
        P("[[2|Silicon (Z = 14) absorbs low-energy photons far more strongly than water, so an unshielded diode reads high in large megavoltage fields and at depth, where low-energy scatter is greatest; shielded diodes, with a high-Z filter, serve there.]] [[2|Unshielded diodes suit small fields, where their small size matters and little low-energy scatter reaches them, and electron beams]], where the water-to-silicon stopping-power ratio (about 1.2) changes by only about 5% from 1 to 20 MeV."),
        P("In vivo, the diode sits on the skin under a build-up cap. The entrance dose at d<sub>max</sub> is the reading times a calibration factor from a 10 × 10 cm field at SSD 100 cm, times a correction factor for each condition that differs (TG-62)."),
        EQ("[[3|D = R × N × CF<sub>SSD</sub> × CF<sub>field</sub> × CF<sub>wedge</sub> × CF<sub>angle</sub> × CF<sub>T</sub>]]",
           "N = dose at d<sub>max</sub> per unit reading in the reference field,   CF<sub>T</sub> = 1 / (1 + α ΔT),   α = fractional rise of sensitivity per °C"),
        EX("Entrance dose from a diode",
           STEM("A diode measures one fraction on the skin of a patient.",
                [f"reading R = {ex_r:.1f} nC", f"calibration factor N = {ex_n:.3f} cGy/nC (22 °C)", f"CF<sub>field</sub> = {ex_fs:.3f},   CF<sub>wedge</sub> = {ex_w:.3f}",
                 f"skin temperature = 31 °C,   sensitivity rise α = {100 * ex_alpha:.2f}% per °C", f"planned entrance dose = {ex_plan:.1f} cGy"],
                "Find the [[entrance dose]] and its difference from the plan."),
           [f"ΔT = 31 − 22 = {ex_dt} °C, so CF<sub>T</sub> = 1 / (1 + {ex_alpha:.4f} × {ex_dt}) = {ex_cft:.4f}",
            f"D = {ex_r:.1f} × {ex_n:.3f} × {ex_fs:.3f} × {ex_w:.3f} × {ex_cft:.4f} = {ex_d:.1f} cGy",
            f"Difference = ({ex_d:.1f} − {ex_plan:.1f}) / {ex_plan:.1f} = {pm(ex_diff)}%"],
           f"{ex_d:.1f} cGy, {abs(ex_diff):.1f}% below the plan."),
        P("A MOSFET (metal–oxide–semiconductor field-effect transistor) [[3|records dose as a shift of its threshold voltage]], caused by holes trapped in the gate oxide and proportional to the dose. The shift is permanent and cumulative, and the device is spent after tens to a few hundred gray. Small and read at once, it serves for in vivo checks."),

        H("Luminescent dosimeters"),
        P("A plastic scintillator emits light as it absorbs energy, carried by an optical fibre to a photodetector. The plastic is close to water, so its response barely depends on energy in megavoltage beams, and an element about 1 mm across suits small fields. [[3|Electrons crossing the fibre also produce Cerenkov light, the stem effect, which grows with the irradiated fibre length; a blank second fibre or its distinct spectrum removes it.]]"),
        P("A thermoluminescent dosimeter (TLD) stores dose as electrons held in traps. [[1|A reader heats it steadily and records the light released against temperature, the glow curve; for LiF:Mg,Ti (TLD-100) the main peak lies near 200 °C.]] The light is proportional to dose up to about 1 Gy or more, with [[1|supralinearity setting in somewhere between 1 and 10 Gy]], and fades slowly. [[1|For LiF:Mg,Ti an anneal of about 1 h at 400 °C and then about 2 h at 100 °C empties the traps before reuse.]]"),
        P("Chips differ in sensitivity, so each has [[2|an element correction factor: the batch mean reading divided by its own reading for the same dose]]. Calibration chips given a known dose, read in the same session, convert corrected readings to dose."),
        EQ("[[2|D = M × ECF × D<sub>cal</sub> / M<sub>cal</sub>]]",
           "M = chip reading,   ECF = batch mean / chip reading,   M<sub>cal</sub> = mean corrected reading of the calibration chips"),
        EX("Dose from a TLD chip",
           STEM("A LiF chip is read after an in vivo measurement.",
                [f"chip reading M = {tl_m:.1f} nC", f"ECF of the chip = {tl_ecf:.3f}", f"calibration chips: {tl_dcal:.2f} Gy gives a mean corrected reading of {tl_mcal:.1f} nC"],
                "Find the [[dose]] to the chip."),
           [f"D<sub>cal</sub> / M<sub>cal</sub> = {tl_dcal:.2f} Gy / {tl_mcal:.1f} nC = {tl_n:.5f} Gy/nC",
            f"D = {tl_m:.1f} × {tl_ecf:.3f} × {tl_n:.5f} = {tl_d:.3f} Gy"],
           f"{tl_d:.2f} Gy."),
        P("An optically stimulated luminescent dosimeter (OSLD) of Al<sub>2</sub>O<sub>3</sub>:C [[3|is read with green light, which releases the trapped charge as blue light near 420 nm. Each reading uses a small fraction of the signal and can be repeated; optical bleaching under bright light empties the traps for reuse.]] Mailed OSLDs check beam outputs in remote audits (IROC Houston, 5% criterion)."),
        P("[[3|Calibrated in a megavoltage beam, LiF (effective atomic number 8.2, water 7.4) reads about 1.3 times high near 30 keV (published values run from about 1.2 to 1.4), and Al<sub>2</sub>O<sub>3</sub> (about 11) three to four times.]] A dose from either carries an uncertainty of roughly 2% to 5% (one standard deviation, TG-191), the low end only with a careful calibration and controlled conditions of use."),
        PHOTO("dosimeters-osld-phantom"),

        H("Radiographic and radiochromic film"),
        P("Film records dose across a plane at a resolution set by the reader. Its darkening is the optical density, from the light falling on the film and the light passing through it; the net optical density subtracts the OD of unexposed film from the same batch."),
        EQ("[[1|OD = log<sub>10</sub>(I<sub>0</sub> / I),   T = I / I<sub>0</sub> = 10<sup>−OD</sup>]]",
           "[[1|net OD = OD<sub>exposed</sub> − OD<sub>unexposed</sub> = log<sub>10</sub>(I<sub>unexposed</sub> / I<sub>exposed</sub>)]]"),
        EX("Net optical density",
           STEM("A densitometer reads the light through a film.", ["no film: I<sub>0</sub> = 1,000", "unexposed part of the same film: 800", "irradiated part: 160"],
                "Find the [[net optical density]] and the [[fraction of light]] that the irradiated part transmits."),
           [f"OD<sub>unexposed</sub> = log<sub>10</sub>(1,000 / 800) = {od_u:.3f}",
            f"OD<sub>exposed</sub> = log<sub>10</sub>(1,000 / 160) = {od_e:.3f}",
            f"Net OD = {od_e:.3f} − {od_u:.3f} = {od_net:.3f}, equal to log<sub>10</sub>(800 / 160) = log<sub>10</sub> 5",
            f"T = 160 / 1,000 = 10<sup>−{od_e:.3f}</sup> = {od_t:.2f}"],
           f"Net OD = {od_net:.3f}; the irradiated part transmits {100 * od_t:.0f}% of the light."),
        P("[[2|Silver (Z = 47) in radiographic film makes it over-respond strongly below about 150 keV]], so it reads high at depth and outside large fields, where low-energy scatter builds up. [[2|Radiochromic film is close to tissue and needs no processing.]]"),
        TABLE(["Property", "Radiographic", "Radiochromic"], [
            ["Sensitive layer", "Silver halide in gelatin", "Monomer that polymerizes"],
            ["Development", "[[2|Chemical, varies by processor]]", "None"],
            ["Below 150 keV", "Strong over-response", "Close to tissue"],
            ["Light", "Kept dark until processed", "Kept from ultraviolet"],
            ["After exposure", "Stable once processed", "Darkens fast at first, then slowly for days"],
            ["Read with", "Densitometer", "Flatbed scanner"]]),
        P("Radiochromic films given known doses give a nonlinear calibration curve of net OD against dose. [[3|Calibration and measurement films are scanned at the same delay after exposure, near the centre of the flatbed, where its reading is most uniform, and in one orientation]], since portrait and landscape scans differ by up to about 10%. The red channel serves most clinical doses, the green extends the range, and multichannel methods remove thickness variations."),

        H("Arrays, gels, and chemical dosimeters"),
        P("Arrays of ion chambers or diodes, a few millimetres to 1 cm apart, measure a plane for patient-specific QA; cylindrical and biplanar arrays cover rotational deliveries. [[1|An array samples dose only at its detectors, so an error narrower than the spacing can fall between them.]] Each detector is calibrated relative to the others, and the array against an ion chamber."),
        P("Gels record dose in three dimensions, read by MRI or optical CT. [[2|Ferric ions in a Fricke gel diffuse and blur the distribution within hours; polymerization in a polymer gel is inhibited by oxygen]] and can depend on dose rate."),
        P(f"In the Fricke dosimeter, an acidic ferrous sulfate solution, radiation oxidizes Fe<sup>2+</sup> to Fe<sup>3+</sup>, [[2|which absorbs ultraviolet light at 304 nm]]. [[2|The G value, the yield per unit energy, is about {G_100EV:g} ions per 100 eV ({1e6 * g_mol_per_j(G_100EV):.2f} μmol/J) in megavoltage beams.]]"),
        EQ("[[2|D = ΔA / (ε l ρ G)]]",
           "ε ≈ 2,160 to 2,200 L mol<sup>−1</sup> cm<sup>−1</sup> at 304 nm and 25 °C, by source,   l = path length,   ρ = 1.024 kg/L"),
        EX("Dose from a Fricke solution",
           STEM("A Fricke solution is read in a 1.00 cm cell at 304 nm.",
                [f"ΔA = {fr_da:.3f}", f"ε = {EPS_FE:,.0f} L mol<sup>−1</sup> cm<sup>−1</sup>", f"ρ = {RHO_FRICKE:.3f} kg/L", f"G = {1e6 * fr_g:.2f} μmol/J"],
                "Find the [[dose]]."),
           [f"Ferric ions: ΔA / (ε l) = {fr_da:.3f} / ({EPS_FE:,.0f} × {fr_l:.2f}) = {sci(fr_c, 3)} mol/L",
            f"Per kilogram: {sci(fr_c, 3)} / {RHO_FRICKE:.3f} = {sci(fr_c / RHO_FRICKE, 3)} mol/kg",
            f"D = {sci(fr_c / RHO_FRICKE, 3)} / ({1e6 * fr_g:.2f} × 10<sup>−6</sup> mol/J) = {fr_d:.1f} Gy"],
           f"{fr_d:.1f} Gy."),
        P(f"[[3|Calorimetry, which measures the temperature rise from the absorbed energy ({cal_mk:.2f} mK per gray in water), is a primary method behind national absorbed-dose standards.]]"),

        H("Detector choice by task"),
        P("Volume averaging limits a detector in small fields; the response to low-energy scatter, in large photon fields; readout delay, in vivo; and spatial resolution, in planar QA. [[1|For mailed remote audits, an OSLD is the usual choice.]]"),
        TABLE(["Task", "Usual detectors"], [
            ["[[1|In vivo, at once]]", "[[1|Diode, MOSFET]]"],
            ["[[1|In vivo, later]]", "[[1|TLD, OSLD]]"],
            ["[[1|Small fields]]", "[[1|Plastic scintillator, unshielded diode, radiochromic film]]"],
            ["Large photon fields", "Ion chamber, shielded diode"],
            ["Electron PDD", "Ion chamber, unshielded diode"],
            ["[[1|IMRT, VMAT QA]]", "[[1|Diode or chamber array, radiochromic film]]"],
            ["Stereotactic end-to-end", "Radiochromic film, small chamber"]]),
    ],
    cards=[
        F("Sensitivity of a silicon diode", f"About {sens_r:,} times more charge per unit volume than air for the same dose: about {W_SI:g} eV per charge pair against {W_AIR} eV, and about {dens_r:,} times the density.",
          w=[f"{W_AIR} / {W_SI:g} = {e_ratio:.2f}", f"{RHO_SI} / {RHO_AIR} = {dens:,.0f}", f"{e_ratio:.2f} × {dens:,.0f} = {sens:,.0f}"]),
        F("Influences on diode sensitivity", ["Accumulated dose: radiation damage lowers it, less in p-type silicon.", "Temperature: a rise of about 0.1% to 0.5% per °C (TG-62).", "Dose per pulse: a rise with it, so a fall as SSD grows, by an amount that varies among diodes.", "Beam angle."]),
        F("Shielded and unshielded diodes", "A shielded diode carries a high-Z filter against low-energy scatter, for large photon fields. Unshielded diodes suit small fields and electron beams."),
        F("In vivo diode dose", "D = R × N × CF<sub>SSD</sub> × CF<sub>field</sub> × CF<sub>wedge</sub> × CF<sub>angle</sub> × CF<sub>T</sub>: the entrance dose at d<sub>max</sub> (TG-62)."),
        F("MOSFET dosimeter", "Holes trapped in the gate oxide shift the threshold voltage in proportion to the dose. The record is permanent and cumulative until the device is spent."),
        F("Stem effect in plastic scintillators", "Cerenkov light from electrons crossing the optical fibre, which grows with the length of fibre in the field. It is removed with a blank fibre or by its spectrum."),
        F("TLD glow curve", "The light emitted against temperature as the chip is heated at a steady rate. The main LiF:Mg,Ti peak lies near 200 °C."),
        F("TLD annealing", "LiF:Mg,Ti: about 1 h at 400 °C, then about 2 h at 100 °C, empties the traps and restores the sensitivity before reuse."),
        F("Element correction factor", "The batch mean reading divided by the chip's own reading after the same dose. D = M × ECF × D<sub>cal</sub> / M<sub>cal</sub>."),
        F("OSLD readout and reuse", "Green light releases the charge stored in Al<sub>2</sub>O<sub>3</sub>:C as blue light near 420 nm. A reading uses a small fraction of the signal, and optical bleaching resets the dosimeter."),
        F("Radiochromic film", "Close to tissue and self-developing. It darkens fast in the first hours and slowly for days after exposure, so films are scanned at a fixed delay, and its reading depends on the scan orientation and the position on the scanner bed."),
        F("Optical density", "OD = log<sub>10</sub>(I<sub>0</sub>/I), so OD 1 transmits 10% and OD 2 transmits 1%. Net OD subtracts the OD of unexposed film."),
    ],
)

# ---------------------------------------------------------------- numbers behind the questions
q_dens, q_e = dens, e_ratio
q_ivr, q_ivn, q_ivfs, q_iva, q_ivdt = 191.5, 1.048, 0.991, 0.0040, 31 - 23
q_ivcft = cf_temp(q_iva, q_ivdt)
q_iv = in_vivo(q_ivr, q_ivn, q_ivfs, q_ivcft)
q_iv_mult = in_vivo(q_ivr, q_ivn, q_ivfs) * (1 + q_iva * q_ivdt)
q_iv_none = in_vivo(q_ivr, q_ivn, q_ivfs)

q_ecf = 20.0 / 19.2
q_tm, q_tecf, q_tdcal, q_tmcal = 18.6, 0.955, 2.00, 42.0
q_tld = tld_dose(q_tm, q_tecf, q_tdcal, q_tmcal)
q_tld_div = q_tm / q_tecf * q_tdcal / q_tmcal
q_tld_no = q_tm * q_tdcal / q_tmcal
q_tld_nocal = q_tm * q_tecf / q_tmcal

q_t = 10 ** -1.3
q_net = od(850, 120)
q_od_e, q_od_u = od(1000, 120), od(1000, 850)

q_g = g_mol_per_j(G_100EV)
q_fr = fricke_dose(0.090, EPS_FE, 1.00, RHO_FRICKE, q_g)
q_fr_norho = fricke_dose(0.090, EPS_FE, 1.00, 1.0, q_g)
q_fr_xrho = 0.090 * RHO_FRICKE / (EPS_FE * 1.00 * q_g)
q_fr_g = fricke_dose(0.090, EPS_FE, 1.00, RHO_FRICKE, G_100EV * 1e-6)

PROBLEMS = [
    # ---- semiconductor detectors
    PR(STEM("A silicon diode and an air ion chamber of the same volume receive the same absorbed dose.", [], "Why does the diode give the far larger signal?"),
       "Silicon is denser and needs less energy per charge pair", ["The junction multiplies each charge pair in an avalanche", "Silicon has a lower atomic number than air", "A high bias voltage collects charge from outside the junction"],
       f"The charge per unit volume is the density divided by the energy per pair. Silicon is about {dens_r:,} times denser than air and needs {W_SI:g} eV per pair against {W_AIR} eV, about {sens_r:,} times more charge in all. A therapy diode runs with no bias and no gain, so nothing is multiplied.", lvl="Easy"),
    PR(STEM("Profiles of a 30 × 30 cm 6 MV field at 20 cm depth are scanned with an unshielded silicon diode and with an ion chamber. Outside the field edge the diode reads several percent higher.", [], "What causes the difference?"),
       "Silicon absorbs low-energy scattered photons more strongly than water", ["The diode's sensitivity rises with the dose per pulse", "Radiation damage has lowered the diode's sensitivity", "The diode is warmer than the ion chamber"],
       "Outside a large field at depth much of the dose comes from low-energy scatter, which silicon (Z = 14) absorbs far more strongly per gram than water. A sensitivity that rises with the dose per pulse would make the diode read lower outside the field, where the dose per pulse is lower, and damage or warmth would change every reading by the same fraction.", lvl="Moderate"),
    PRM(STEM("An in vivo diode reading is converted to the entrance dose under conditions that differ from its calibration.", [], "Which of these correction factors apply?"),
        ["SSD", "Field size", "Temperature of the diode"], ["Air density (temperature and pressure)", "Polarity of the collecting voltage", "Stopping-power ratio of water to air"],
        "A diode has no air cavity and no bias, so the ion-chamber corrections for air density, polarity, and the water-to-air stopping-power ratio play no part. Its sensitivity changes with the dose per pulse (SSD), the scatter in the field (field size), and its temperature; TG-62 also lists wedge and beam-angle factors.", lvl="Moderate"),
    TYPED(STEM("A diode calibrated at 23 °C measures the entrance dose on a patient whose skin warms it to 31 °C.",
               [f"reading R = {q_ivr:.1f} nC", f"calibration factor N = {q_ivn:.3f} cGy/nC", f"CF<sub>field</sub> = {q_ivfs:.3f}", f"rise of sensitivity α = {100 * q_iva:.2f}% per °C"],
               "What is the [[entrance dose]]?"), q_iv, 0.01, "cGy",
          f"The warm diode reads high, so CF<sub>T</sub> = 1 / (1 + {q_iva:.4f} × {q_ivdt}) = {q_ivcft:.4f}. D = {q_ivr:.1f} × {q_ivn:.3f} × {q_ivfs:.3f} × {q_ivcft:.4f} = {q_iv:.1f} cGy. Multiplying by {1 + q_iva * q_ivdt:.3f} in place of dividing gives {q_iv_mult:.1f} cGy, and leaving out the temperature gives {q_iv_none:.1f} cGy.",
          lvl="Challenging", w=[f"ΔT = 31 − 23 = {q_ivdt} °C", f"CF<sub>T</sub> = 1 / {1 + q_iva * q_ivdt:.3f} = {q_ivcft:.4f}", f"D = {q_ivr:.1f} × {q_ivn:.3f} × {q_ivfs:.3f} × {q_ivcft:.4f} = {q_iv:.1f} cGy"]),

    # ---- luminescent dosimeters
    PR(STEM("A TLD chip is placed in a reader after irradiation.", [], "What does the glow curve record?"),
       "Light emitted against the temperature of the heated chip", ["Light emitted against the wavelength of the stimulating light", "Charge collected against the applied bias voltage", "Optical density against the absorbed dose"],
       "Heating at a steady rate releases the trapped charge, and the light emitted as it recombines is recorded against temperature; the main LiF:Mg,Ti peak lies near 200 °C. Stimulation by light is how an OSLD is read.", lvl="Easy"),
    PR(STEM("A plastic scintillation detector, with its fibre running across the field, measures output factors in a 6 MV beam. Without correction its readings exceed those of an ion chamber by more and more as the field grows.", [], "What causes the excess?"),
       "Cerenkov light produced in the irradiated length of fibre", ["Over-response of the plastic to low-energy scatter", "Temperature dependence of the scintillator", "Ionization quenching in the scintillator"],
       "Electrons crossing the fibre faster than light travels in it emit Cerenkov light, and the length of fibre in the beam grows with the field. The plastic is close to water, so it does not over-respond to low-energy scatter, and quenching matters only at high LET, as near a proton Bragg peak.", lvl="Moderate"),
    PRN(STEM("Every chip of a TLD batch receives the same dose.", ["batch mean reading = 20.0 nC", "reading of one chip = 19.2 nC"], "What is the [[element correction factor]] of that chip?"),
        q_ecf, [19.2 / 20.0, 0.8 / 19.2, 0.8], "{:.3f}",
        f"ECF = batch mean / chip reading = 20.0 / 19.2 = {q_ecf:.3f}, so a reading from this chip is multiplied by {q_ecf:.3f}. The inverse ratio, {19.2 / 20.0:.3f}, would make a chip that reads low read lower still.", lvl="Easy"),
    PR(STEM("LiF TLDs and Al<sub>2</sub>O<sub>3</sub>:C OSLDs, both calibrated in a 6 MV beam, are placed side by side in a 50 kV x-ray beam, and no energy correction is applied.", [], "How do their readings compare with the true dose to water?"),
       "Both read high, the OSLDs far more than the TLDs", ["Both read high, the TLDs far more than the OSLDs", "Both read low, by about the same fraction", "Both read correctly, because each was calibrated"],
       "Photoelectric absorption per gram rises steeply with atomic number. LiF (effective atomic number 8.2) is close to water (7.4) and reads about 1.2 to 1.4 times high near 30 keV, while Al<sub>2</sub>O<sub>3</sub> (about 11) reads three to four times high. A calibration at 6 MV does not carry over to a low-energy beam.", lvl="Challenging"),

    # ---- film
    PRN(STEM("A region of a film has an optical density of 1.3.", [], "What [[fraction of the light]] does it transmit?"),
        100 * q_t, [100 * math.exp(-1.3), 100 * (1 - q_t), 10 / 1.3], "{:.1f}%",
        f"T = 10<sup>−OD</sup> = 10<sup>−1.3</sup> = {q_t:.4f}, or {100 * q_t:.1f}%. Using e<sup>−OD</sup> gives {100 * math.exp(-1.3):.1f}%, and {100 * (1 - q_t):.1f}% is the fraction absorbed.", lvl="Easy"),
    TYPED(STEM("A densitometer reads the light through a film.", ["no film: 1,000", "unexposed part of the same film: 850", "irradiated part: 120"], "What is the [[net optical density]] of the irradiated part?"),
          q_net, 0.01, "",
          f"Net OD = log<sub>10</sub>(850 / 120) = {q_net:.3f}, the same as OD<sub>exposed</sub> − OD<sub>unexposed</sub> = {q_od_e:.3f} − {q_od_u:.3f}. Leaving out the unexposed film gives {q_od_e:.3f}.", lvl="Moderate"),
    PR(STEM("Radiochromic calibration films were scanned 48 h after irradiation. A measurement film from a plan check is scanned 1 h after its irradiation and read with that calibration.", [], "How does the dose read compare with the dose delivered?"),
       "Too low, because the film has not finished darkening", ["Too high, because the film fades after exposure", "Correct, because radiochromic film develops at once", "Correct, because only the net optical density is used"],
       "Radiochromic film keeps darkening after exposure, quickly in the first hours and slowly for days. Scanned at 1 h, the film is lighter than the calibration films were at 48 h for the same dose, so the dose read is too low. The net optical density removes the unexposed film, not the delay.", lvl="Moderate"),
    PRM(STEM("Radiochromic film is chosen for a plan check.", [], "Which of these describe radiochromic film?"),
        ["It forms its image without chemical processing", "It keeps darkening after exposure, fast at first and then slowly"], ["It over-responds strongly below about 150 keV", "It is read by heating it in a reader", "Its reading is the same in any scanner orientation"],
        "Radiochromic film polymerizes and darkens by itself, most of it in the first hours. The strong low-energy over-response belongs to silver-halide film, heating reads a TLD, and portrait and landscape scans can differ by up to about 10%.", lvl="Easy"),

    # ---- arrays, gels, and chemical dosimeters
    PR(STEM("A VMAT plan is checked with a diode array whose detectors are 10 mm apart, and it passes. Film in the same phantom shows a strip of low dose 3 mm wide where one MLC leaf lagged.", [], "Why did the array miss the strip?"),
       "The strip fell between detectors, which sample the dose only at their positions", ["Diodes over-respond to low-energy scatter in the strip", "The array was calibrated against an ion chamber", "The film over-responds in regions of low dose"],
       "An array measures the dose only at its detectors, so a feature narrower than the 10 mm spacing can lie between two of them. The over-response of silicon would not hide a 3 mm strip, and a calibration against an ion chamber sets the dose scale of every detector, not where it samples.", lvl="Moderate"),

    # ---- detector choice by task
    PR(STEM("The output factor of a 5 mm diameter stereotactic cone is measured in a 6 MV beam.", [], "Which detector suits the measurement best?"),
       "A plastic scintillation detector", ["A Farmer chamber of 0.6 cm³", "A shielded silicon diode", "An OSLD with a 5 mm sensitive disc"],
       "A plastic scintillator about 1 mm across is close to water, so it neither averages over the field nor perturbs it. The Farmer chamber and the 5 mm disc average the dose over a region as wide as the field, and the high-Z filter of a shielded diode perturbs a field this small.", lvl="Challenging"),
    PR(STEM("A dosimetry audit group checks the beam outputs of distant clinics by mail.", [], "Which dosimeters are usually sent?"),
       "Optically stimulated luminescent dosimeters", ["A Farmer chamber and an electrometer", "Sheets of radiographic film", "A silicon diode array"],
       "OSLDs are small, robust, and cheap to send in numbers; the clinic irradiates them under set conditions and the audit group reads them centrally, and IROC Houston flags outputs that differ by more than 5%. An ion chamber and electrometer suit an on-site visit rather than the mail, and film depends on processing.", lvl="Easy"),
    SORT("Match each detector to the signal it reads.", ["Silicon diode", "MOSFET", "Plastic scintillator", "TLD", "OSLD", "Radiochromic film"],
         [("Current from charge pairs swept out by a built-in field", 0), ("A shift in threshold voltage", 1), ("Light emitted during irradiation, carried by a fibre", 2),
          ("Light emitted as the crystal is heated", 3), ("Blue light emitted under green light", 4), ("Lower light transmission after polymerization", 5)],
         "A diode collects charge pairs in its junction, a MOSFET keeps the dose as trapped charge that shifts its threshold voltage, and a scintillator emits light at once. A TLD releases its stored charge as light when heated and an OSLD when stimulated with light. Radiochromic film darkens as its monomer polymerizes.", lvl="Moderate", mode="match", cap=1),
]

INLINE = {0: [1, 2, 3], 1: [5, 6, 7], 2: [9, 10, 11, 12], 3: [13], 4: [14, 15]}

TERMS = ["threshold voltage", "stem effect", "glow curve", "supralinearity", "element correction factor", "optical bleaching", "net optical density", "G value"]

TAKE = [
    [f"A diode collects charge with no bias and frees about {sens_r:,} times more charge per unit volume than air; p-type silicon degrades least.",
     "Silicon over-responds to low-energy scatter: shielded diodes for large photon fields, unshielded ones for small fields and electrons.",
     "In vivo: D = R × N × CF for SSD, field, wedge, angle, and temperature. A MOSFET records dose as a threshold-voltage shift."],
    ["TLD: heated, light against temperature is the glow curve, LiF:Mg,Ti peak near 200 °C, supralinear from somewhere between 1 and 10 Gy, annealed before reuse.",
     "D = M × ECF × D<sub>cal</sub> / M<sub>cal</sub>, with ECF = batch mean / chip reading.",
     "OSLD (Al<sub>2</sub>O<sub>3</sub>:C, Z<sub>eff</sub> about 11): read by light, read again, bleached for reuse, three to four times high near 30 keV. Scintillators need the Cerenkov stem signal removed."],
    ["OD = log<sub>10</sub>(I<sub>0</sub>/I) and T = 10<sup>−OD</sup>; net OD = log<sub>10</sub>(I<sub>unexposed</sub>/I<sub>exposed</sub>).",
     "Radiographic film over-responds below about 150 keV and depends on processing; radiochromic film is close to tissue and self-developing.",
     "Radiochromic calibration and measurement films are scanned at the same delay, in one orientation, near the centre of the scanner."],
    ["Arrays sample the dose only at their detectors, so an error narrower than the spacing can be missed.",
     f"Fricke: D = ΔA / (ε l ρ G), G ≈ {1e6 * g_mol_per_j(G_100EV):.2f} μmol/J, read at 304 nm. Fricke gels blur by diffusion; polymer gels are inhibited by oxygen.",
     "Calorimetry is a primary standard of absorbed dose."],
    ["Small fields: plastic scintillator, unshielded diode, or radiochromic film. In vivo: diode, MOSFET, TLD, or OSLD. Mailed audits: OSLD. Planar QA: array or radiochromic film."],
]
