from blocks import *
import math
import beamdata as bd

# ---------------------------------------------------------------- TG-51 relations used in this chapter
def m_corr(m_raw, p_ion, p_tp, p_elec, p_pol):
    """Fully corrected reading M = P_ion P_TP P_elec P_pol M_raw."""
    return m_raw * p_ion * p_tp * p_elec * p_pol
def dw_cgy_per_mu(m_nc, kq, ndw_gy_per_c, mu=100):
    """D_w = M k_Q N_D,w. M in nC for `mu` monitor units, N in Gy/C; returns cGy per MU."""
    return m_nc * 1e-9 * kq * ndw_gy_per_c * 100 / mu
def r50_of(i50):
    """R50 (cm) from the depth of 50% ionization I50 (cm), TG-51."""
    return 1.029 * i50 - 0.06 if i50 <= 10 else 1.059 * i50 - 0.37
def dref_of(r50): return 0.6 * r50 - 0.1
def kr50_cyl(r50):
    """k'_R50 for Farmer-like cylindrical chambers, 2 <= R50 <= 9 cm (TG-51)."""
    return 0.9905 + 0.0710 * math.exp(-r50 / 3.67)
def ddx_from_pb(pb, foil_cm=50):
    """%dd(10)_x from %dd(10)_Pb measured with 1 mm of lead 50 cm or 30 cm above the phantom surface (TG-51)."""
    a, b, cut = (0.8905, 0.00150, 73.0) if foil_cm == 50 else (0.8116, 0.00264, 71.0)
    return (a + b * pb) * pb if pb >= cut else pb
def ddx_open(dd10):
    """%dd(10)_x of a flattened beam measured without the foil (2014 addendum): open-beam %dd(10) from 75% to 89%; below 75%, %dd(10)_x = %dd(10)."""
    return 1.267 * dd10 - 20.0 if dd10 >= 75 else dd10
def pct_diff(measured, expected): return 100 * (measured - expected) / expected

PDD10, TMR10 = bd.PDD[(10, 10)], bd.TMR[(10, 10)]       # illustrative 6 MV beam: 10 x 10 cm, SSD 100 cm and SAD

# ---- worked example: 6 MV photon beam, SSD setup
NDW = 5.40e7                                             # Gy/C, illustrative ADCL coefficient of a Farmer-type chamber
NDW_NC = NDW * 1e-9                                      # Gy/nC
MRAW1, PION1, PTP1, PELEC1, PPOL1, KQ1 = 12.40, 1.003, 1.012, 1.000, 1.001, 0.992
M1 = m_corr(MRAW1, PION1, PTP1, PELEC1, PPOL1)
D1 = dw_cgy_per_mu(M1, KQ1, NDW)                         # cGy/MU at 10 cm
D1r = round(D1, 4)
DMAX1 = D1r / (PDD10 / 100)                              # cGy/MU at d_max
PD1 = pct_diff(DMAX1, 1.000)

# ---- worked example: electron beam quality and reference depth
RCAV = 0.30
I50C = 6.65                                              # depth of 50% ionization read at the chamber's center
I50E = I50C - 0.5 * RCAV
R50E = r50_of(I50E); DREFE = dref_of(R50E)

# ---- worked example: electron dose at d_ref
ME, PGRE, KECAL = 20.10, 0.995, 0.903
KRE = round(kr50_cyl(R50E), 3)
KQE = PGRE * KRE * KECAL
DE = dw_cgy_per_mu(ME, KQE, NDW)

TOPIC = dict(
    id="tg51", domain=2, sub="II.B", title="TG-51 beam calibration",
    ref=dict(aapm="TG-51", khan="", ford="16"),
    guide=[
        H("Traceability and the dose equation"),
        P("The AAPM TG-51 protocol for megavoltage photon and electron beams starts from a chamber calibrated in absorbed dose to water. An Accredited Dosimetry Calibration Laboratory (ADCL) irradiates the chamber in Co-60 under reference conditions and issues its calibration coefficient N<sub>D,w</sub><sup>60Co</sup>: the dose to water per unit corrected reading, in Gy/C, or in Gy per reading unit when chamber and electrometer are calibrated as a pair."),
        P("The ADCL's instruments are calibrated against the national primary standard. In the United States that is a water calorimeter at NIST, which derives dose from the temperature rise of irradiated water; some other national laboratories use graphite calorimeters."),
        EQ("D<sub>w</sub><sup>Q</sup> = M k<sub>Q</sub> N<sub>D,w</sub><sup>60Co</sup>", "M = P<sub>ion</sub> P<sub>TP</sub> P<sub>elec</sub> P<sub>pol</sub> M<sub>raw</sub>   (original TG-51; the 2014 addendum adds P<sub>leak</sub> and P<sub>rp</sub>)"),
        P("D<sub>w</sub><sup>Q</sup> is the dose to water at the chamber's point of measurement in a beam of quality Q, with the chamber removed; M is the fully corrected reading. The quality conversion factor k<sub>Q</sub> converts the Co-60 coefficient to quality Q (k<sub>Q</sub> = 1 in Co-60). It depends on the beam and the chamber model: the water-to-air stopping-power ratio changes with the beam, and each design's wall, central electrode, and cavity perturb the fluence differently."),

        H("Photon beam calibration"),
        P("Only cylindrical chambers are used. The cavity center, the point of measurement, is placed at 10 cm depth in water, with the 10 × 10 cm field defined at the phantom surface (SSD setup) or at the chamber's depth (SAD setup). The gradient across the cavity is the same in every beam of one quality, so k<sub>Q</sub> includes it and the chamber is not shifted."),
        P("Beam quality is %dd(10)<sub>x</sub>, the percent depth dose at 10 cm for a 10 × 10 cm field at SSD 100 cm from photons alone, read from a depth-ionization curve shifted upstream by 0.6 r<sub>cav</sub> (r<sub>cav</sub> = cavity radius). The shift moves each reading to the chamber's effective point of measurement, the depth whose dose it represents. Below 10 MV, %dd(10)<sub>x</sub> is the measured %dd(10). From 10 MV up, electrons from the linac head add dose at d<sub>max</sub> that varies between machines, so a 1 mm lead foil is placed about 50 cm (or 30 cm) above the phantom surface; it absorbs them and adds a smaller, known contamination that the TG-51 equations remove:"),
        EQ("foil 50 cm above the surface: %dd(10)<sub>x</sub> = (0.8905 + 0.00150 %dd(10)<sub>Pb</sub>) %dd(10)<sub>Pb</sub>,   for %dd(10)<sub>Pb</sub> ≥ 73%",
           "foil 30 cm above the surface: %dd(10)<sub>x</sub> = (0.8116 + 0.00264 %dd(10)<sub>Pb</sub>) %dd(10)<sub>Pb</sub>,   for %dd(10)<sub>Pb</sub> ≥ 71%",
           "below those values %dd(10)<sub>x</sub> = %dd(10)<sub>Pb</sub>; the foil is removed for the dose measurement"),
        P("k<sub>Q</sub> is read for that %dd(10)<sub>x</sub> from the table or fit for the exact chamber model; for Farmer-type chambers it falls from about 0.99 at 6 MV to about 0.97 at 18 MV. Models differ, so another model's value biases every calibration made with it."),
        P("The 2014 addendum for photon beams kept the dose equation and reference conditions. It gave Monte Carlo k<sub>Q</sub> values for more chamber models, fitted against %dd(10)<sub>x</sub> from 63% to 86%; set specifications for a reference-class chamber; and added P<sub>rp</sub>, which corrects for the radial dose profile averaged over the chamber's sensitive volume in a beam that is not flat, such as a flattening-filter-free beam, and P<sub>leak</sub>, a correction for leakage. Flattened beams may skip the foil (k<sub>Q</sub> changes by at most 0.2%); flattening-filter-free beams still use it."),
        EQ("%dd(10)<sub>x</sub> = 1.267 %dd(10) − 20.0   (flattened beam measured without the foil; open-beam %dd(10) from 75% to 89%)", "below 75%, %dd(10)<sub>x</sub> = %dd(10)"),
        EX("Dose at 10 cm in a 6 MV beam",
           STEM("A Farmer-type chamber in a 6 MV beam, TG-51 SSD setup: SSD 100 cm, 10 × 10 cm field at the surface, cavity center at 10 cm depth. The k<sub>Q</sub> value is an illustrative table entry for this chamber model.",
                [f"N<sub>D,w</sub><sup>60Co</sup> = {sci(NDW, 3)} Gy/C", f"M<sub>raw</sub> = {MRAW1:.2f} nC for 100 MU", f"P<sub>ion</sub> = {PION1:.3f},   P<sub>TP</sub> = {PTP1:.3f},   P<sub>elec</sub> = {PELEC1:.3f},   P<sub>pol</sub> = {PPOL1:.3f}", f"%dd(10)<sub>x</sub> = {PDD10:.1f}%, so k<sub>Q</sub> = {KQ1:.3f}"],
                "Find the [[dose to water per MU at 10 cm]]."),
           [f"M = {MRAW1:.2f} × {PION1:.3f} × {PTP1:.3f} × {PELEC1:.3f} × {PPOL1:.3f} = {M1:.3f} nC",
            f"N<sub>D,w</sub><sup>60Co</sup> = {sci(NDW, 3)} Gy/C = {NDW_NC:.4f} Gy/nC",
            f"D<sub>w</sub> = {M1:.3f} × {KQ1:.3f} × {NDW_NC:.4f} = {D1:.4f} Gy for 100 MU",
            f"{D1:.4f} Gy / 100 MU = {D1:.4f} cGy/MU"],
           f"{D1:.4f} cGy/MU at 10 cm depth."),

        H("Electron beam calibration"),
        P("Electron beam quality is specified by R<sub>50</sub>, the depth at which the dose falls to 50% of its maximum, measured at SSD 100 cm. A chamber gives the depth of 50% ionization, I<sub>50</sub>, read on a curve shifted upstream by 0.5 r<sub>cav</sub> for a cylindrical chamber, and TG-51 converts it:"),
        EQ("R<sub>50</sub> = 1.029 I<sub>50</sub> − 0.06 cm   (2 ≤ I<sub>50</sub> ≤ 10 cm)", "R<sub>50</sub> = 1.059 I<sub>50</sub> − 0.37 cm   (I<sub>50</sub> > 10 cm)", "d<sub>ref</sub> = 0.6 R<sub>50</sub> − 0.1 cm"),
        P("A cylindrical chamber has its cavity center at d<sub>ref</sub>, and its k<sub>Q</sub> has three factors:"),
        EQ("D<sub>w</sub><sup>Q</sup> = M P<sub>gr</sub><sup>Q</sup> k′<sub>R50</sub> k<sub>ecal</sub> N<sub>D,w</sub><sup>60Co</sup>",
           "P<sub>gr</sub><sup>Q</sup> = M<sub>raw</sub>(center at d<sub>ref</sub> + 0.5 r<sub>cav</sub>) / M<sub>raw</sub>(center at d<sub>ref</sub>)",
           "k′<sub>R50</sub> = 0.9905 + 0.0710 e<sup>−R<sub>50</sub>/3.67</sup>   (Farmer-like chambers, 2 ≤ R<sub>50</sub> ≤ 9 cm)"),
        UL("k<sub>ecal</sub>, the photon-electron conversion factor, is fixed for each chamber model and converts the Co-60 coefficient to an electron beam with R<sub>50</sub> = 7.5 cm; k′<sub>R50</sub> then converts to the beam's own R<sub>50</sub>.",
           "P<sub>gr</sub>, the gradient correction, applies to cylindrical chambers only. Their effective point of measurement in an electron beam lies 0.5 r<sub>cav</sub> upstream of the center, so the reading with the center 0.5 r<sub>cav</sub> deeper stands for the dose at d<sub>ref</sub>. The gradient differs between beams of one R<sub>50</sub>, so P<sub>gr</sub> is measured in each beam."),
        P("In the original TG-51 (1999), plane-parallel chambers are required below R<sub>50</sub> = 2.6 cm (about 6 MeV), and for them P<sub>gr</sub> = 1. Their Co-60 coefficients carry wall effects that differ between chambers of one model, so TG-51 prefers cross-calibration: in a high-energy electron beam a calibrated cylindrical chamber gives the dose at d<sub>ref</sub>, and the plane-parallel chamber at the same depth is assigned the product k<sub>ecal</sub> N<sub>D,w</sub><sup>60Co</sup> that reproduces it."),
        P("A 2024 AAPM addendum for electron beams (Report 385, Muir et al.) allows a reference-class cylindrical chamber at every energy from 4 to 22 MeV, with no measured P<sub>gr</sub>: its Monte Carlo k<sub>Q</sub> values include the gradient. Doses per MU come out up to about 2% higher than with the original protocol."),
        TABLE(["Reference conditions", "Photon beams", "Electron beams"], [
            ["Beam quality", "%dd(10)<sub>x</sub>, SSD 100 cm", "R<sub>50</sub>, SSD 100 cm"],
            ["Depth", "10 cm", "0.6 R<sub>50</sub> − 0.1 cm"],
            ["Field", "10 × 10 cm at the surface (SSD) or chamber (SAD)", "10 × 10 cm or more; 20 × 20 cm if R<sub>50</sub> &gt; 8.5 cm"],
            ["Distance", "SSD or SAD setup", "SSD 90 to 110 cm"]]),
        TABLE(["Chamber", "Photon beams", "Electron beams, original TG-51"], [
            ["Type", "Cylindrical only", "Either; plane-parallel required if R<sub>50</sub> &lt; 2.6 cm, preferred if &lt; 4.3 cm"],
            ["Point of measurement", "Cavity center", "Cavity center; inner face of the front window if plane-parallel"],
            ["Depth-curve shift", "0.6 r<sub>cav</sub> upstream", "0.5 r<sub>cav</sub> upstream"],
            ["Gradient", "Inside k<sub>Q</sub>", "P<sub>gr</sub>, measured"]]),
        EX("Electron beam quality and reference depth",
           STEM("A Farmer-type chamber measures a depth-ionization curve in an electron beam at SSD 100 cm with a 10 × 10 cm field.", [f"r<sub>cav</sub> = {RCAV:.2f} cm", f"50% ionization with the chamber's center at {I50C:.2f} cm depth"], "Find [[R<sub>50</sub> and d<sub>ref</sub>]]."),
           [f"Shift upstream by 0.5 × {RCAV:.2f} = {0.5 * RCAV:.2f} cm: I<sub>50</sub> = {I50C:.2f} − {0.5 * RCAV:.2f} = {I50E:.2f} cm",
            f"I<sub>50</sub> lies between 2 and 10 cm: R<sub>50</sub> = 1.029 × {I50E:.2f} − 0.06 = {R50E:.2f} cm",
            f"d<sub>ref</sub> = 0.6 × {R50E:.2f} − 0.1 = {DREFE:.2f} cm"],
           f"R<sub>50</sub> = {R50E:.2f} cm and d<sub>ref</sub> = {DREFE:.2f} cm. R<sub>50</sub> is below 8.5 cm, so the 10 × 10 cm field is large enough."),
        EX("Electron dose at the reference depth",
           STEM(f"A Farmer-type chamber with its cavity center at d<sub>ref</sub> = {DREFE:.2f} cm in an electron beam with R<sub>50</sub> = {R50E:.2f} cm. The k<sub>ecal</sub> value is illustrative for this chamber model.",
                [f"M = {ME:.2f} nC for 100 MU (fully corrected)", f"P<sub>gr</sub> = {PGRE:.3f}", f"k′<sub>R50</sub> = {KRE:.3f} (TG-51 expression at R<sub>50</sub> = {R50E:.2f} cm)", f"k<sub>ecal</sub> = {KECAL:.3f}", f"N<sub>D,w</sub><sup>60Co</sup> = {sci(NDW, 3)} Gy/C"],
                "Find [[k<sub>Q</sub>]] and the [[dose to water per MU at d<sub>ref</sub>]]."),
           [f"k<sub>Q</sub> = P<sub>gr</sub> k′<sub>R50</sub> k<sub>ecal</sub> = {PGRE:.3f} × {KRE:.3f} × {KECAL:.3f} = {KQE:.4f}",
            f"D<sub>w</sub> = {ME:.2f} × {KQE:.4f} × {NDW_NC:.4f} = {DE:.4f} Gy for 100 MU, or {DE:.4f} cGy/MU"],
           f"k<sub>Q</sub> = {KQE:.4f}, and {DE:.4f} cGy/MU at d<sub>ref</sub>."),

        H("Dose per monitor unit"),
        P("TG-51 ends with the dose at the reference depth. This clinic's convention is 1 cGy/MU at d<sub>max</sub> for a 10 × 10 cm field at SSD 100 cm, the geometry of the TG-51 SSD setup, so the clinical percent depth dose at 10 cm carries the result to d<sub>max</sub>:"),
        EQ("D(d<sub>max</sub>)/MU = [D<sub>w</sub>(10 cm)/MU] ÷ [%dd(10)/100]   (SSD setup, SSD calibration: this clinic)",
           "D(d<sub>max</sub>)/MU = [D<sub>w</sub>(10 cm)/MU] ÷ TMR(10 cm, 10 × 10)   (SAD setup, SAD calibration)",
           "percent difference = 100 × (measured − expected) / expected"),
        P("The clinical %dd(10) includes the electron contamination at d<sub>max</sub>; %dd(10)<sub>x</sub> only selects k<sub>Q</sub>. Under the SAD convention, 1 cGy/MU at d<sub>max</sub> with the point at the isocenter, the chamber sits at the isocenter at 10 cm depth with the field defined there, and TMR(10 cm) replaces %dd(10)/100. Electron beams use the clinical PDD at d<sub>ref</sub> the same way. The result is compared with the expected output as a percent difference; beyond the clinic's action level, the setup and factors are checked, the dose monitor is adjusted, and the measurement is repeated."),
        EX("Output against the clinic convention",
           STEM("A 6 MV beam measured in the TG-51 SSD setup, at a clinic calibrated to 1 cGy/MU at d<sub>max</sub> for a 10 × 10 cm field at SSD 100 cm.", [f"D<sub>w</sub>(10 cm) = {D1r:.4f} cGy/MU", f"clinical %dd(10) = {PDD10:.1f}%"],
                "Find the [[dose per MU at d<sub>max</sub>]] and its [[percent difference]] from the expected output."),
           [f"D(d<sub>max</sub>)/MU = {D1r:.4f} / {PDD10 / 100:.3f} = {DMAX1:.4f} cGy/MU",
            f"Percent difference = 100 × ({DMAX1:.4f} − 1.000) / 1.000 = +{PD1:.2f}%"],
           f"{DMAX1:.3f} cGy/MU, {PD1:.2f}% above the expected output. The difference is compared with the clinic's action levels; beyond them, the setup and the factors are checked, the output is adjusted, and the measurement is repeated."),
    ],
    cards=[
        F("TG-51 dose equation", "D<sub>w</sub><sup>Q</sup> = M k<sub>Q</sub> N<sub>D,w</sub><sup>60Co</sup>, with M = P<sub>ion</sub> P<sub>TP</sub> P<sub>elec</sub> P<sub>pol</sub> M<sub>raw</sub>."),
        F("Calibration coefficient N<sub>D,w</sub><sup>60Co</sup>", "Absorbed dose to water per unit corrected reading in Co-60 under reference conditions, issued by an ADCL. Unit: Gy/C, or Gy per reading unit."),
        F("Traceability in the United States", "Clinic chamber, then ADCL, then NIST, whose primary standard of absorbed dose to water in Co-60 is a water calorimeter."),
        F("Quality conversion factor k<sub>Q</sub>", "Converts the Co-60 coefficient to the user's beam. It is 1 in Co-60 and depends on the chamber model; for Farmer-type chambers it is about 0.99 at 6 MV and 0.97 at 18 MV."),
        F("Photon reference conditions", "Cylindrical chamber with its cavity center at 10 cm depth in water; 10 × 10 cm field at the surface (SSD setup) or at the chamber's depth (SAD setup)."),
        F("Photon beam quality %dd(10)<sub>x</sub>", "Percent depth dose at 10 cm for a 10 × 10 cm field at SSD 100 cm, from photons alone. Below 10 MV it equals the measured %dd(10)."),
        F("Lead foil for photon beam quality", "From 10 MV up: 1 mm of lead about 50 cm (or 30 cm) above the phantom surface while %dd(10)<sub>Pb</sub> is measured, then converted to %dd(10)<sub>x</sub>. The foil is removed for the dose measurement."),
        F("2014 photon addendum", "Monte Carlo k<sub>Q</sub> for more chambers, reference-class chamber specifications, and P<sub>rp</sub> for beams that are not flat. Flattened beams may skip the foil and use %dd(10)<sub>x</sub> = 1.267 %dd(10) − 20.0 for an open-beam %dd(10) from 75% to 89%."),
        F("Electron beam quality R<sub>50</sub>", "R<sub>50</sub> = 1.029 I<sub>50</sub> − 0.06 cm for 2 ≤ I<sub>50</sub> ≤ 10 cm, and 1.059 I<sub>50</sub> − 0.37 cm for I<sub>50</sub> above 10 cm."),
        F("Electron reference conditions", "d<sub>ref</sub> = 0.6 R<sub>50</sub> − 0.1 cm; field at least 10 × 10 cm (20 × 20 cm if R<sub>50</sub> > 8.5 cm); SSD 90 to 110 cm."),
        F("Electron k<sub>Q</sub> for a cylindrical chamber", "k<sub>Q</sub> = P<sub>gr</sub> k′<sub>R50</sub> k<sub>ecal</sub>. k<sub>ecal</sub> is fixed by the chamber model and refers to R<sub>50</sub> = 7.5 cm; k′<sub>R50</sub> converts to the beam's R<sub>50</sub>."),
        F("Gradient correction P<sub>gr</sub>", "Original TG-51: M<sub>raw</sub>(center at d<sub>ref</sub> + 0.5 r<sub>cav</sub>) / M<sub>raw</sub>(center at d<sub>ref</sub>), measured in each electron beam. It is 1 for a plane-parallel chamber."),
        F("Effective point of measurement, cylindrical chamber", "Upstream of the center by 0.6 r<sub>cav</sub> in photon beams and 0.5 r<sub>cav</sub> in electron beams. Depth-ionization curves are shifted by these amounts."),
        F("Plane-parallel chambers in electron beams", "Original TG-51: required for R<sub>50</sub> below 2.6 cm, preferred below 4.3 cm. Cross-calibrated against a cylindrical chamber in a high-energy electron beam, because their Co-60 wall effects vary between chambers."),
        F("Transfer of the calibration to d<sub>max</sub>", "Dose per MU at d<sub>max</sub> = dose per MU at 10 cm ÷ (clinical %dd(10)/100) for the SSD convention, or ÷ TMR(10 cm) for the SAD convention. %dd(10)<sub>x</sub> is not used."),
        F("2024 electron addendum", "Reference-class cylindrical chambers at every electron energy from 4 to 22 MeV, no measured P<sub>gr</sub>, and doses per MU up to about 2% higher than with the original TG-51."),
    ],
)

# ---------------------------------------------------------------- practice questions
# 10 MV photon dose at 10 cm
KQ_N1, NDW_N1, M_N1, DDX_N1 = 0.984, 5.36e7, 13.85, 73.5
d_n1 = dw_cgy_per_mu(M_N1, KQ_N1, NDW_N1)
d_n1_nokq, d_n1_divkq = dw_cgy_per_mu(M_N1, 1.0, NDW_N1), dw_cgy_per_mu(M_N1, 1 / KQ_N1, NDW_N1)
d_n1_xpdd = d_n1 * DDX_N1 / 100
# chamber placed 0.6 r_cav too deep for the photon reference reading (illustrative 6 MV data)
SHIFT = 0.6 * RCAV
pdd_a, pdd_b = bd.pdd_model(10, 10), bd.pdd_model(10 + SHIFT, 10)
read_ratio = round(pdd_b, 1) / round(pdd_a, 1)
over_shift = 100 * (1 / read_ratio - 1)
grad_mm = 100 * (1 - read_ratio) / (10 * SHIFT)
# d_ref from I50 (typed)
I50_T1 = 4.75
R50_T1 = r50_of(I50_T1); DREF_T1 = dref_of(R50_T1)
# %dd(10)_x from a lead-foil measurement (typed)
PB_T2 = 79.0
DDX_T2 = ddx_from_pb(PB_T2, 50)
# electron dose at d_ref
R50_N5, M_N5, PGR_N5 = 5.40, 20.25, 0.996
KR_N5 = round(kr50_cyl(R50_N5), 3)
KQ_N5 = PGR_N5 * KR_N5 * KECAL
d_n5 = dw_cgy_per_mu(M_N5, KQ_N5, NDW)
d_n5_nopgr, d_n5_nokr, d_n5_noke = dw_cgy_per_mu(M_N5, KR_N5 * KECAL, NDW), dw_cgy_per_mu(M_N5, PGR_N5 * KECAL, NDW), dw_cgy_per_mu(M_N5, PGR_N5 * KR_N5, NDW)
# 6 MV transfer to d_max
D10_N2 = 0.6655
dmax_n2 = D10_N2 / (PDD10 / 100)
dmax_n2_mult, dmax_n2_tmr, dmax_n2_isq = D10_N2 * PDD10 / 100, D10_N2 / TMR10, dmax_n2 * (101.5 / 100) ** 2
sad_over = 100 * (TMR10 / (PDD10 / 100) - 1)
# 18 MV transfer to d_max: clinical %dd(10) against %dd(10)_x
D10_N3, DD_N3 = 0.7860, 78.8
DDX_N3 = round(ddx_open(DD_N3), 1)
dmax_n3 = D10_N3 / (DD_N3 / 100)
dmax_n3_x, dmax_n3_mult = D10_N3 / (DDX_N3 / 100), D10_N3 * DD_N3 / 100
low_n3 = 100 * (1 - dmax_n3_x / dmax_n3)
# polarity correction left out
PPOL_P5 = 1.004
deliv_p5, low_p5, dbl_p5 = 1.000 * PPOL_P5, 1.000 / PPOL_P5, 1.000 * PPOL_P5 ** 2
# k_Q from the wrong chamber model
KQ_A, KQ_B = 0.997, 0.992
deliv_n4, inv_n4, dbl_n4 = KQ_A / KQ_B, KQ_B / KQ_A, (KQ_A / KQ_B) ** 2

PROBLEMS = [
    PR(STEM("Before a TG-51 calibration, an ion chamber returns from an ADCL with its coefficient N<sub>D,w</sub><sup>60Co</sup>.", [], "What does [[N<sub>D,w</sub><sup>60Co</sup>]] convert?"),
       "A corrected reading into absorbed dose to water in a Co-60 beam",
       ["A corrected reading into air kerma in a Co-60 beam", "A corrected reading into absorbed dose to water in the user's beam", "An exposure into absorbed dose to water in a Co-60 beam"],
       "N<sub>D,w</sub><sup>60Co</sup> is the dose to water per unit corrected reading for that chamber in Co-60 under reference conditions, in Gy/C. An air-kerma coefficient gives air kerma, not dose to water, and the step to the user's beam needs k<sub>Q</sub> as well.", lvl="Easy"),
    PR(STEM("A clinic in the United States sends its chamber to an ADCL for an absorbed-dose-to-water calibration.", [], "To which [[primary standard]] is that calibration traceable?"),
       "A water calorimeter at NIST",
       ["A free-air chamber at the ADCL", "The manufacturer's factory calibration", "A Co-60 unit at the clinic"],
       "The ADCL's instruments are calibrated at NIST, where absorbed dose to water in Co-60 is realized with a water calorimeter. A free-air chamber is a standard of air kerma for kilovoltage x-rays, not of dose to water.", lvl="Easy"),
    PR(STEM("A 6 MV beam is calibrated with TG-51 using a cylindrical chamber.", [], "Where is the [[center of the chamber's cavity]] placed?"),
       "At 10 cm depth in water", ["At the depth of maximum dose", "At 5 cm depth in water", "At the depth of 50% dose"],
       "The photon reference depth is 10 cm, and the point of measurement of a cylindrical chamber lies at its cavity center. The gradient across the cavity is included in k<sub>Q</sub>, so no shift is added. d<sub>max</sub> is where the clinic states its calibration, not where TG-51 measures.", lvl="Easy"),
    PR(STEM("The quality of an 18 MV beam is measured with a 1 mm lead foil in the beam, about 50 cm above the water surface.", [], "What is the [[purpose of the foil]]?"),
       "To absorb the electron contamination from the linac head",
       ["To harden the beam for the dose measurement", "To lower the dose rate at the chamber", "To flatten the beam profile at depth"],
       "Electrons from the head add dose near d<sub>max</sub> that varies between linacs and would change %dd(10). The foil absorbs them, and the TG-51 equations remove its own smaller, known contamination. The foil is taken out for the dose measurement, so it does not harden the beam that is calibrated.", lvl="Easy"),
    PRM(STEM("A physicist sets up a TG-51 reference measurement in a 6 MV photon beam.", [], "Which of these belong to the [[reference conditions]]?"),
        ["A cylindrical chamber with its cavity center at 10 cm depth in water", "A 10 × 10 cm field at the surface (SSD setup) or at the chamber's depth (SAD setup)"],
        ["A plane-parallel chamber with its front window at 10 cm depth", "A cylindrical chamber with its cavity center at d<sub>max</sub>", "A 20 × 20 cm field at the phantom surface"],
        "Photon reference dosimetry uses a cylindrical chamber with the cavity center at 10 cm and a 10 × 10 cm field, defined at the surface for an SSD setup or at the chamber for an SAD setup. Plane-parallel chambers are not used for photon reference dosimetry, and d<sub>max</sub> is where the clinic states its calibration, not where TG-51 measures.", lvl="Easy"),
    TYPED(STEM("The quality of an 18 MV beam is measured with a 1 mm lead foil 50 cm above the water surface, at SSD 100 cm with a 10 × 10 cm field.", [f"%dd(10)<sub>Pb</sub> = {PB_T2:.1f}%"], "What is [[%dd(10)<sub>x</sub>]]?"), DDX_T2, 0.003, "%",
          f"%dd(10)<sub>Pb</sub> is above 73%, so the 50 cm equation applies: %dd(10)<sub>x</sub> = (0.8905 + 0.00150 × {PB_T2:.1f}) × {PB_T2:.1f} = {DDX_T2:.2f}%. Reporting the foil value unchanged gives {PB_T2:.1f}%, outside the tolerance.",
          w=[f"0.8905 + 0.00150 × {PB_T2:.1f} = {0.8905 + 0.00150 * PB_T2:.4f}", f"{0.8905 + 0.00150 * PB_T2:.4f} × {PB_T2:.1f} = {DDX_T2:.2f}%"], lvl="Moderate"),
    PRN(STEM("A 10 MV beam is calibrated with TG-51 in the SSD setup. The k<sub>Q</sub> value is an illustrative table entry for the chamber model.",
             [f"%dd(10)<sub>x</sub> = {DDX_N1:.1f}% (lead-foil method)", f"k<sub>Q</sub> = {KQ_N1:.3f}", f"N<sub>D,w</sub><sup>60Co</sup> = {sci(NDW_N1, 3)} Gy/C", f"M = {M_N1:.2f} nC for 100 MU (fully corrected)"],
             "What is the [[dose to water per MU at 10 cm]]?"),
        d_n1, [d_n1_nokq, d_n1_divkq, d_n1_xpdd], "{:.4f} cGy/MU",
        f"D<sub>w</sub> = M k<sub>Q</sub> N<sub>D,w</sub><sup>60Co</sup> = {M_N1:.2f} nC × {KQ_N1:.3f} × {NDW_N1 * 1e-9:.4f} Gy/nC = {d_n1:.4f} Gy for 100 MU, which is {d_n1:.4f} cGy/MU. Leaving out k<sub>Q</sub> gives {d_n1_nokq:.4f} and dividing by it gives {d_n1_divkq:.4f}. Multiplying by %dd(10)<sub>x</sub>/100 gives {d_n1_xpdd:.4f}, but the reading was taken at 10 cm, so no depth-dose factor belongs in it; %dd(10)<sub>x</sub> only selects k<sub>Q</sub>.", lvl="Moderate"),
    PR(STEM("Two 18 MV linacs share a photon spectrum but have different heads, and their open-beam %dd(10) values differ.", [], "Why does TG-51 specify [[photon beam quality]] by %dd(10)<sub>x</sub> rather than by %dd(10)?"),
       "Electrons from the head change the open-beam %dd(10) without changing k<sub>Q</sub>",
       ["The open-beam %dd(10) cannot be measured with an ion chamber", "%dd(10)<sub>x</sub> includes the electron contamination that %dd(10) leaves out", "%dd(10)<sub>x</sub> is measured at d<sub>max</sub>, where the dose is highest"],
       "%dd(10) is normalized at d<sub>max</sub>, where electrons from the head add dose that varies between machines, while k<sub>Q</sub> follows the photon spectrum that %dd(10)<sub>x</sub> describes. The option saying %dd(10)<sub>x</sub> includes the contamination has the two definitions swapped.", lvl="Moderate"),
    PRM(STEM("A physicist moves a photon calibration procedure from the original TG-51 to its 2014 addendum.", [], "Which of these did the [[addendum]] introduce?"),
        ["New k<sub>Q</sub> values from Monte Carlo calculations for more chamber models", "Specifications for a reference-class chamber", "A correction, P<sub>rp</sub>, for a beam profile that is not flat across the chamber"],
        ["A photon reference depth of 5 cm in place of 10 cm", "Plane-parallel chambers for photon reference dosimetry", "An air-kerma calibration coefficient in place of N<sub>D,w</sub><sup>60Co</sup>"],
        "The addendum kept the dose equation, the 10 cm reference depth, and cylindrical chambers. It replaced k<sub>Q</sub> with Monte Carlo values fitted against %dd(10)<sub>x</sub>, defined what a reference-class chamber must meet, and added P<sub>rp</sub>, mainly for flattening-filter-free beams.", lvl="Moderate"),
    PR(STEM(f"A physicist calibrates a 6 MV beam with a Farmer-type chamber (r<sub>cav</sub> = {RCAV:.2f} cm) and places the center of its cavity {SHIFT:.2f} cm deeper than 10 cm, so that the effective point of measurement sits at 10 cm. All other steps follow TG-51, and the output is then adjusted to the clinic's convention.",
            [f"PDD(10 cm) = {pdd_a:.1f}%", f"PDD({10 + SHIFT:.2f} cm) = {pdd_b:.1f}% (illustrative 6 MV data)"], "How does the [[dose per MU]] the linac then delivers compare with the intended dose?"),
       f"Higher by about {over_shift:.1f}%, because k<sub>Q</sub> already includes the gradient",
       [f"Lower by about {over_shift:.1f}%, because the deeper reading overstates the dose", "The same, because the shift puts the effective point of measurement at 10 cm", "The same, because P<sub>gr</sub> removes any shift of the chamber"],
       f"TG-51 places the cavity center at 10 cm and accounts for the gradient inside k<sub>Q</sub>. The deeper chamber reads {pdd_b:.1f}/{pdd_a:.1f} = {read_ratio:.4f} of the correct value, about {grad_mm:.2f}% per mm, so the calculated dose is low and raising the output to match leaves the linac {over_shift:.1f}% high. P<sub>gr</sub> belongs to electron beams.", lvl="Challenging"),
    TYPED(STEM("A depth-ionization curve is measured in an electron beam with a cylindrical chamber and shifted upstream by 0.5 r<sub>cav</sub>.", [f"I<sub>50</sub> on the shifted curve = {I50_T1:.2f} cm"], "What is the [[reference depth d<sub>ref</sub>]]?"), DREF_T1, 0.01, "cm",
          f"R<sub>50</sub> = 1.029 × {I50_T1:.2f} − 0.06 = {R50_T1:.3f} cm, so d<sub>ref</sub> = 0.6 × {R50_T1:.3f} − 0.1 = {DREF_T1:.2f} cm. Using I<sub>50</sub> in place of R<sub>50</sub> gives {dref_of(I50_T1):.2f} cm, outside the tolerance.",
          w=[f"R<sub>50</sub> = 1.029 × {I50_T1:.2f} − 0.06 = {R50_T1:.3f} cm", f"d<sub>ref</sub> = 0.6 × {R50_T1:.3f} − 0.1 = {DREF_T1:.3f} cm"], lvl="Moderate"),
    PR(STEM("A plane-parallel chamber will be used to calibrate a 6 MeV electron beam.", [], "Why does the original TG-51 prefer to [[cross-calibrate]] it against a cylindrical chamber in a high-energy electron beam rather than use its Co-60 coefficient?"),
       "Its Co-60 coefficient carries wall effects that vary between chambers",
       ["Plane-parallel chambers cannot be calibrated in a Co-60 beam", "Plane-parallel chambers have no polarity effect in electron beams", "Cylindrical chambers need no corrections in an electron beam"],
       "In Co-60 the wall of a plane-parallel chamber changes the reading by amounts that differ from chamber to chamber, which makes k<sub>ecal</sub> N<sub>D,w</sub><sup>60Co</sup> uncertain. In a high-energy electron beam a calibrated cylindrical chamber gives the dose at d<sub>ref</sub>, and the plane-parallel chamber read at the same depth is assigned that product directly. Plane-parallel chambers can be calibrated in Co-60; the issue is how reliable that coefficient is.", lvl="Moderate"),
    PRN(STEM("An electron beam is calibrated with TG-51 using a Farmer-type chamber with its cavity center at d<sub>ref</sub>. The k<sub>ecal</sub> value is illustrative for the chamber model.",
             [f"R<sub>50</sub> = {R50_N5:.2f} cm", f"M = {M_N5:.2f} nC for 100 MU (fully corrected)", f"P<sub>gr</sub> = {PGR_N5:.3f}", f"k′<sub>R50</sub> = {KR_N5:.3f}", f"k<sub>ecal</sub> = {KECAL:.3f}", f"N<sub>D,w</sub><sup>60Co</sup> = {sci(NDW, 3)} Gy/C"],
             "What is the [[dose to water per MU at d<sub>ref</sub>]]?"),
        d_n5, [d_n5_nopgr, d_n5_nokr, d_n5_noke], "{:.4f} cGy/MU",
        f"For a cylindrical chamber k<sub>Q</sub> = P<sub>gr</sub> k′<sub>R50</sub> k<sub>ecal</sub> = {PGR_N5:.3f} × {KR_N5:.3f} × {KECAL:.3f} = {KQ_N5:.4f}, so D<sub>w</sub> = {M_N5:.2f} × {KQ_N5:.4f} × {NDW_NC:.4f} = {d_n5:.4f} cGy/MU. Leaving out P<sub>gr</sub> gives {d_n5_nopgr:.4f}, leaving out k′<sub>R50</sub> gives {d_n5_nokr:.4f}, and leaving out k<sub>ecal</sub> gives {d_n5_noke:.4f}, about {100 * (d_n5_noke / d_n5 - 1):.0f}% high.", lvl="Challenging"),
    PRN(STEM("A 6 MV beam is measured in the TG-51 SSD setup at a clinic calibrated to 1 cGy/MU at d<sub>max</sub> for a 10 × 10 cm field at SSD 100 cm. The beam data are illustrative.",
             [f"D<sub>w</sub>(10 cm) = {D10_N2:.4f} cGy/MU", f"clinical %dd(10) = {PDD10:.1f}%", f"TMR(10 cm, 10 × 10) = {TMR10:.3f}"], "What is the [[dose per MU at d<sub>max</sub>]]?"),
        dmax_n2, [dmax_n2_mult, dmax_n2_tmr, dmax_n2_isq], "{:.3f} cGy/MU",
        f"The SSD setup shares the surface distance and the field with the clinic's convention, so D(d<sub>max</sub>)/MU = {D10_N2:.4f} / {PDD10 / 100:.3f} = {dmax_n2:.3f} cGy/MU. Dividing by the TMR gives {dmax_n2_tmr:.3f}, the SAD convention applied to an SSD measurement; multiplying by the PDD gives {dmax_n2_mult:.3f}; and the factor (101.5/100)², which belongs to isocentric treatments on an SSD-calibrated linac, gives {dmax_n2_isq:.3f}.", lvl="Moderate"),
    PR(STEM("A clinic defines its calibration by the SAD convention: 1 cGy/MU at d<sub>max</sub> with the point at the isocenter, for a 10 × 10 cm field there. The TG-51 dose is measured with the chamber at the isocenter at 10 cm depth and a 10 × 10 cm field at that depth.", [], "Which [[factor]] converts the measured dose per MU into the dose per MU at the calibration point?"),
       "Division by TMR(10 cm, 10 × 10)",
       ["Division by the clinical %dd(10)/100 at SSD 100 cm", "Division by %dd(10)<sub>x</sub>/100", "Multiplication by (101.5/100)²"],
       f"Both points are at the isocenter on the central axis, so the ratio of the dose at 10 cm to the dose at d<sub>max</sub> at a fixed distance is the TMR ({TMR10:.3f} in the illustrative 6 MV data). The PDD belongs to the SSD setup, where the distance to the point grows with depth; dividing by it ({PDD10:.1f}%) would overstate the dose at d<sub>max</sub> by {sad_over:.0f}%.", lvl="Moderate"),
    PRN(STEM("An 18 MV beam is measured in the TG-51 SSD setup at a clinic calibrated to 1 cGy/MU at d<sub>max</sub> for a 10 × 10 cm field at SSD 100 cm.",
             [f"D<sub>w</sub>(10 cm) = {D10_N3:.4f} cGy/MU", f"clinical %dd(10) = {DD_N3:.1f}%", f"%dd(10)<sub>x</sub> = {DDX_N3:.1f}% (photon component)"], "What is the [[dose per MU at d<sub>max</sub>]]?"),
        dmax_n3, [dmax_n3_x, D10_N3, dmax_n3_mult], "{:.3f} cGy/MU",
        f"The clinical %dd(10) includes the dose that electrons from the head add at d<sub>max</sub>, so it links the two depths: {D10_N3:.4f} / {DD_N3 / 100:.3f} = {dmax_n3:.3f} cGy/MU. %dd(10)<sub>x</sub> leaves that dose out and only selects k<sub>Q</sub>; using it gives {dmax_n3_x:.3f}, {low_n3:.1f}% low, and an output raised to match would overdose by about as much. Reporting the 10 cm value gives {D10_N3:.3f}.", lvl="Challenging"),
    PR(STEM("During a TG-51 photon calibration the polarity correction is measured but left out of M. The physicist then adjusts the linac until the calculated dose at d<sub>max</sub> is 1.000 cGy/MU.", [f"P<sub>pol</sub> = {PPOL_P5:.3f}"], "What [[dose per MU at d<sub>max</sub>]] does the linac then deliver?"),
       f"{deliv_p5:.3f} cGy/MU, {100 * (deliv_p5 - 1):.1f}% more than intended",
       [f"{low_p5:.3f} cGy/MU, {100 * (1 - low_p5):.1f}% less than intended", "1.000 cGy/MU, because P<sub>pol</sub> cancels in the transfer", f"{dbl_p5:.3f} cGy/MU, {100 * (dbl_p5 - 1):.1f}% more than intended"],
       f"Without P<sub>pol</sub> the corrected reading, and so the calculated dose, is low by the factor 1/{PPOL_P5:.3f}. Raising the output until the calculation shows 1.000 cGy/MU leaves the linac at {deliv_p5:.3f} cGy/MU. A fall to {low_p5:.3f} would need the omitted factor to be below 1.", lvl="Challenging"),
    PRN(STEM("A physicist calibrates a 6 MV beam with chamber model A but reads k<sub>Q</sub> from the row for model B, then adjusts the output until the calculated dose at d<sub>max</sub> is 1.000 cGy/MU. Both k<sub>Q</sub> values are illustrative.",
             [f"k<sub>Q</sub>, model A = {KQ_A:.3f}", f"k<sub>Q</sub>, model B = {KQ_B:.3f}"], "What [[dose per MU at d<sub>max</sub>]] does the linac deliver?"),
        deliv_n4, [inv_n4, 1.0, dbl_n4], "{:.3f} cGy/MU",
        f"Model B's value makes the calculated dose low by the factor {KQ_B:.3f}/{KQ_A:.3f} = {inv_n4:.4f}, so the output is raised until the calculation shows 1.000; the true dose is then {KQ_A:.3f}/{KQ_B:.3f} = {deliv_n4:.3f} cGy/MU, {100 * (deliv_n4 - 1):.1f}% high. {inv_n4:.3f} has the ratio inverted, and 1.000 ignores the error.", lvl="Challenging"),
    SORT(STEM("A TG-51 calibration applies several factors.", [], "What does each [[factor]] correct for?"),
         ["P<sub>TP</sub>", "P<sub>ion</sub>", "P<sub>pol</sub>", "k<sub>Q</sub>, photon beam", "P<sub>gr</sub>", "k<sub>ecal</sub>"],
         [("Air in the cavity at a temperature and pressure other than the reference values", 0), ("Charge lost to recombination before collection", 1), ("A reading that changes when the collecting voltage is reversed", 2),
          ("A photon beam whose quality differs from Co-60", 3), ("The ionization gradient across a cylindrical cavity in an electron beam", 4), ("The change from Co-60 to an electron beam with R<sub>50</sub> = 7.5 cm", 5)],
         "P<sub>TP</sub>, P<sub>ion</sub>, and P<sub>pol</sub> correct the reading itself. k<sub>Q</sub> moves the Co-60 coefficient to the photon beam's quality. In electron beams k<sub>ecal</sub> moves it to R<sub>50</sub> = 7.5 cm, k′<sub>R50</sub> to the beam's own R<sub>50</sub>, and P<sub>gr</sub> corrects a cylindrical chamber for the gradient across its cavity.", lvl="Moderate", mode="match", cap=1),
    SORT(STEM("A photon beam is calibrated with TG-51 at a clinic whose convention is 1 cGy/MU at d<sub>max</sub>.", [], "In what order, first to last, are these [[steps]] done?"), ["1st", "2nd", "3rd", "4th", "5th"],
         [("Calibrate the chamber in Co-60 at an ADCL to obtain N<sub>D,w</sub><sup>60Co</sup>", 0), ("Measure and correct the reading M at 10 cm depth", 1), ("Compute D<sub>w</sub> = M k<sub>Q</sub> N<sub>D,w</sub><sup>60Co</sup> at 10 cm", 2),
          ("Divide by the clinical %dd(10)/100 to reach d<sub>max</sub>", 3), ("Compare with 1 cGy/MU and adjust the output if needed", 4)],
         "Each step uses the result of the one before: the coefficient from the ADCL, the corrected reading, the dose at 10 cm, the transfer to d<sub>max</sub>, and the comparison with the convention.", lvl="Easy", mode="rank", cap=1),
]

INLINE = {0: [1, 2], 1: [3, 4, 6], 2: [11, 12], 3: [14, 15]}

TERMS = ["Accredited Dosimetry Calibration Laboratory", "calibration coefficient", "quality conversion factor", "effective point of measurement", "lead foil", "photon-electron conversion factor", "gradient correction", "cross-calibration"]

TAKE = [
    ["D<sub>w</sub> = M k<sub>Q</sub> N<sub>D,w</sub><sup>60Co</sup>, with M the fully corrected reading.",
     "N<sub>D,w</sub><sup>60Co</sup> comes from an ADCL in Co-60 and is traceable, in the United States, to the NIST water calorimeter.",
     "k<sub>Q</sub> depends on the beam quality and on the chamber model."],
    ["Photons: cylindrical chamber, cavity center at 10 cm depth, 10 × 10 cm field; the gradient is inside k<sub>Q</sub>.",
     "Beam quality is %dd(10)<sub>x</sub>, from photons alone, with a 1 mm lead foil from 10 MV up or, for flattened beams, the no-foil relation of the 2014 addendum.",
     "Farmer-type chambers: k<sub>Q</sub> about 0.99 at 6 MV and 0.97 at 18 MV."],
    ["R<sub>50</sub> = 1.029 I<sub>50</sub> − 0.06 cm for I<sub>50</sub> up to 10 cm; d<sub>ref</sub> = 0.6 R<sub>50</sub> − 0.1 cm.",
     "Original TG-51, cylindrical chamber: k<sub>Q</sub> = P<sub>gr</sub> k′<sub>R50</sub> k<sub>ecal</sub>, with P<sub>gr</sub> measured in each beam.",
     "Original TG-51: plane-parallel chambers below R<sub>50</sub> = 2.6 cm, cross-calibrated in a high-energy electron beam."],
    ["Dose per MU at d<sub>max</sub> = dose per MU at 10 cm ÷ (clinical %dd(10)/100) for SSD calibration, or ÷ TMR(10 cm) for SAD calibration.",
     "%dd(10)<sub>x</sub> selects k<sub>Q</sub> and is not used to transfer dose.",
     "Percent difference = 100 × (measured − expected) / expected."],
]
