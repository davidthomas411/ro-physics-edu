from blocks import *
import math

# ---------------------------------------------------------------- MIRD, Y-90 microspheres, patient release, and IORT relations behind every worked number
LN2 = math.log(2.0)
MEAN = 1.0 / LN2                                    # 1.443: the mean life in half-lives
MEV_J = 1.602176634e-13                             # J per MeV
MBQ_PER_MCI = 37.0
NBSP = chr(160)                                     # keeps a half-life and its unit on one line

def t_eff(tp, tb):
    """Effective half-life: 1/T_eff = 1/T_p + 1/T_b (any time unit, the same in and out)."""
    return tp * tb / (tp + tb)

def cum_act(a0, te):
    """Cumulated activity for instantaneous uptake and single-exponential clearance: Ã = 1.443 A0 T_eff."""
    return MEAN * a0 * te

def dose_per_gbq_kg(e_mev, t_h):
    """Gy per (GBq/kg) for a pure β emitter left to decay in place, all its energy absorbed locally: decays per GBq times E_mean."""
    return 1e9 * MEAN * t_h * 3600.0 * e_mev * MEV_J

def y90_activity(d, m, lsf, k=50.0):
    """GBq of Y-90 for a mean dose d (Gy) to a perfused mass m (kg) when a fraction lsf of the activity shunts to the lungs."""
    return d * m / (k * (1.0 - lsf))

def lung_dose(a, lsf, k=50.0, m_lung=1.0):
    """Gy to the lungs, taken as 1 kg, from a GBq with lung shunt fraction lsf."""
    return k * a * lsf / m_lung

def release_rem(gamma, q_mci, tp_d, occ, r_cm):
    """NRC Regulatory Guide 8.39: D(∞) = 34.6 Γ Q0 Tp E / r², in rem with 1 R taken as 1 rem (Γ in R cm² mCi⁻¹ h⁻¹, Q0 in mCi, Tp in d, r in cm)."""
    return 34.6 * gamma * q_mci * tp_d * occ / r_cm ** 2

def bed(D, d, ab): return D * (1 + d / ab)
def eqd2(D, d, ab): return D * (d + ab) / (2 + ab)

def sphere_dose(ds, a, r, mu):
    """Dose at r (cm) from the centre of a spherical applicator of radius a (cm) with surface dose ds: inverse square from the centre and exp(−µ(r − a))."""
    return ds * (a / r) ** 2 * math.exp(-mu * (r - a))

# ---------------------------------------------------------------- radionuclides: half-life (3 significant digits), emissions, mean and maximum range in soft tissue (published values, about), use
NUC = [("I-131", 8.02, "d", "β⁻ (E<sub>max</sub> 0.61 MeV); γ 364 keV", "0.4 / 2 mm", "Hyperthyroidism, thyroid ablation and cancer"),
       ("Lu-177", 6.65, "d", "β⁻ (E<sub>max</sub> 0.50 MeV); γ 113 and 208 keV", "0.3 / 1.8 mm", "Ligands for PSMA and somatostatin receptors"),
       ("Sm-153", 46.3, "h", "β⁻ (E<sub>max</sub> 0.81 MeV); γ 103 keV", "0.6 / 3 mm", "Painful bone metastases (as a phosphonate)"),
       ("Sr-89", 50.6, "d", "β⁻ (E<sub>max</sub> 1.5 MeV)", "2.4 / 7 mm", "Painful bone metastases (behaves as calcium)"),
       ("Y-90", 64.1, "h", "β⁻ (E<sub>max</sub> 2.28 MeV); no γ ray", "2.5 / 11 mm", "Microspheres for liver tumours"),
       ("Ra-223", 11.4, "d", "Four α particles with its daughters, about 6 to 8 MeV each", "40 to 100 µm", "Bone metastases of prostate cancer (behaves as calcium)"),
       ("Ac-225", 9.92, "d", "Four α particles with its daughters", "40 to 100 µm", "PSMA and peptide ligands")]
EMAX = {"Lu-177": 0.498, "I-131": 0.606, "Sm-153": 0.81, "Sr-89": 1.495, "Y-90": 2.28}          # MeV, maximum β energies behind the range ranking
EMAX_TXT = {"Lu-177": "0.50", "I-131": "0.61", "Sm-153": "0.81", "Sr-89": "1.5", "Y-90": "2.28"}   # the maximum β energies as the table prints them
assert all(f"E<sub>max</sub> {EMAX_TXT[r[0]]} MeV" in r[3] for r in NUC if r[0] in EMAX_TXT)
RMAX = {"Lu-177": 1.8, "I-131": 2.0, "Sm-153": 3.0, "Sr-89": 7.0, "Y-90": 11.0}                  # mm, the maximum ranges printed in the table
RANGE_ORDER = ["Ra-223"] + sorted(EMAX, key=EMAX.get)                                             # α first, then β by maximum energy
assert [k for k in RANGE_ORDER[1:]] == sorted(RMAX, key=RMAX.get)

# ---------------------------------------------------------------- worked examples
A0_1, TP_LU, TB_1, S_1 = 50.0, 6.65, 10.0, 3.4      # MBq, d, d, mGy MBq⁻¹ h⁻¹ (illustrative)
TE_1 = t_eff(TP_LU, TB_1); TE_1H = 24 * TE_1; CA_1 = cum_act(A0_1, TE_1H); D_1 = CA_1 * S_1 / 1000.0
T_Y90, E_Y90 = 64.1, 0.93                           # h; MeV, mean β energy
NDEC = 1e9 * MEAN * T_Y90 * 3600.0                  # decays per GBq left to decay in place
K_Y90 = dose_per_gbq_kg(E_Y90, T_Y90)
D_2, M_2, LSF_2 = 120.0, 0.80, 0.08
A_2 = y90_activity(D_2, M_2, LSF_2); DL_2 = lung_dose(A_2, LSF_2)
G131, TP131, OCC, R1M, Q_HIST = 2.2, 8.02, 0.25, 100.0, 33.0
D_3 = release_rem(G131, Q_HIST, TP131, OCC, R1M)     # rem
Q_5 = 0.5 / release_rem(G131, 1.0, TP131, OCC, R1M)  # mCi that gives exactly 0.5 rem
RATE_33 = G131 * Q_HIST / R1M ** 2 * 10.0            # mSv/h at 1 m for 33 mCi (R/h × 10 mSv/R)
DS, A_APP, DEPTH, MU_X = 20.0, 1.5, 1.0, 0.3         # Gy, cm, cm, cm⁻¹ (illustrative)
D_X = sphere_dose(DS, A_APP, A_APP + DEPTH, MU_X); D_X_IS = DS * (A_APP / (A_APP + DEPTH)) ** 2
B10, E10, B3, E3 = bed(10, 10, 10), eqd2(10, 10, 10), bed(10, 10, 3), eqd2(10, 10, 3)
B10F, B3F = bed(10, 2, 10), bed(10, 2, 3)            # the same 10 Gy in five 2 Gy fractions

TOPIC = dict(
    id="rpt-iort", domain=6, sub="VI.A", title="Radiopharmaceutical therapy and intraoperative radiotherapy",
    ref=dict(aapm="TG-72", khan="", ford="27"),
    guide=[
        H("Radionuclides for therapy"),
        P("A radiopharmaceutical carries a radionuclide to its target, bound to a molecule or particle or, as iodide in thyroid cells, taken up directly. The range of its particles sets how far the dose spreads, and so the use."),
        TABLE(["Nuclide", "Half-life", "Emissions", "Range in tissue, mean / maximum (about)", "Use"], [[n, f"{t:g}{NBSP}{u}", f"[[2|{e}]]" if n in ("Ra-223", "Ac-225") else e, f"[[1|{r}]]" if n in ("Y-90", "Lu-177", "I-131", "Ra-223", "Ac-225") else r, use] for n, t, u, e, r, use in NUC]),
        P("Mean ranges vary by source and definition. [[1|A long β range irradiates cells holding no activity from their neighbours' decays (crossfire), evening out the dose in a large tumour with patchy uptake; a short range suits small tumours.]] [[2|An α particle crosses a few cells with a LET of 50 to 230 keV/µm, against under 1 keV/µm for β particles,]] and suits micrometastases and single cells."),
        P("[[3|The γ rays of I-131 (364 keV), Lu-177 (208 and 113 keV), and Sm-153 (103 keV) give post-therapy images; they also leave the patient and set the dose rate nearby,]] far higher per unit activity for I-131 than for Lu-177. [[3|Y-90 has no γ ray]] and is imaged by its bremsstrahlung or, with PET, its rare positrons."),

        H("Absorbed dose from a radiopharmaceutical"),
        P("The MIRD formalism (Medical Internal Radiation Dose committee) sums, over the source regions, the decays in each source times the dose per decay to the target."),
        EQ("[[1|D(target) = Σ Ã(source) × S(target ← source)]]", "Ã = ∫ A(t) dt   (MBq h)", "S = Σ<sub>i</sub> Δ<sub>i</sub> φ<sub>i</sub> / m<sub>target</sub>   (mGy MBq<sup>−1</sup> h<sup>−1</sup>)"),
        P("The cumulated activity Ã, also called the time-integrated activity, is the area under the activity–time curve of the source. [[1|The S value, the mean dose to the target per decay in the source,]] holds the energy per decay of each emission (Δ<sub>i</sub>), the fraction absorbed in the target (φ<sub>i</sub>), and the target mass; it depends on the nuclide and the geometry, not on the activity or the timing."),
        P("For instantaneous uptake and single-exponential clearance, physical decay and biological removal add their rates, so the effective half-life is shorter than either:"),
        EQ("[[2|1/T<sub>eff</sub> = 1/T<sub>p</sub> + 1/T<sub>b</sub>,   T<sub>eff</sub> = T<sub>p</sub> T<sub>b</sub> / (T<sub>p</sub> + T<sub>b</sub>)]]", "[[2|Ã = A<sub>0</sub> / λ<sub>eff</sub> = 1.443 A<sub>0</sub> T<sub>eff</sub>]]"),
        P("β particles stop within millimetres, so a pure β emitter in a region much larger than that range deposits its energy where it decays. [[3|This local deposition approximation gives S = E<sub>mean</sub>/m for the self-dose and about 0 for other regions.]] For Y-90 decaying in place, with E<sub>mean</sub> about 0.93 MeV (quoted from 0.927 to 0.937 MeV):"),
        EQ(f"D / (A<sub>0</sub>/m) = 1.443 × {T_Y90:g} h × 3600 s/h × 10<sup>9</sup> Bq/GBq × {E_Y90:g} MeV × 1.602 × 10<sup>−13</sup> J/MeV",
           f"[[3|= {K_Y90:.1f} J per GBq, so {K_Y90:.1f} Gy per GBq per kg]]"),
        P("Published constants run from about 49.4 to 50 Gy kg GBq<sup>−1</sup>, usually rounded to 50."),
        EX("Dose to a tumour", STEM("A Lu-177 agent is taken up by a tumour at once and cleared by a single exponential (illustrative values).",
                                    [f"A<sub>0</sub> = {A0_1:g} MBq in the tumour", f"T<sub>p</sub> = {TP_LU:g} d", f"T<sub>b</sub> = {TB_1:.1f} d", f"S(tumour ← tumour) = {S_1:g} mGy MBq<sup>−1</sup> h<sup>−1</sup>"],
                                    "Find the [[effective half-life]], the [[cumulated activity]], and the [[dose]]."),
           [f"T<sub>eff</sub> = {TP_LU:g} × {TB_1:.1f} / ({TP_LU:g} + {TB_1:.1f}) = {TE_1:.2f} d = {TE_1H:.2f} h",
            f"Ã = A<sub>0</sub> T<sub>eff</sub> / ln 2 = {A0_1:g} × {TE_1H:.2f} / 0.6931 = {CA_1:,.0f} MBq h",
            f"D = Ã S = {CA_1:,.0f} × {S_1:g} mGy = {D_1:.1f} Gy"],
           f"T<sub>eff</sub> = {TE_1:.2f} d, Ã = {CA_1:,.0f} MBq h, and D = {D_1:.1f} Gy."),

        H("Yttrium-90 microspheres"),
        P("Y-90 microspheres injected into a hepatic artery lodge in tumour arterioles, since liver tumours draw their blood mainly from that artery. [[3|Glass spheres (20 to 30 µm) carry about 2500 Bq each and resin spheres (20 to 60 µm) about 50 Bq, so resin needs tens of millions of spheres and slows the flow more.]]"),
        P("Spheres that pass through shunts reach the lungs. Tc-99m macroaggregated albumin (MAA), injected where the spheres will go, [[1|gives the lung shunt fraction (LSF) from planar images]], using geometric means of anterior and posterior counts. [[2|With the lungs taken as 1 kg, the lung dose is held to about 30 Gy per treatment and 50 Gy in total for glass spheres;]] for resin spheres an LSF above 20% excludes treatment."),
        EQ("[[1|LSF = lung counts / (lung counts + liver counts)]]", "[[2|D<sub>liver</sub> = 50 A (1 − LSF) / m,   D<sub>lung</sub> = 50 A × LSF / 1 kg]]", "A in GBq, m = perfused mass in kg, D in Gy, uptake taken as uniform"),
        P("The partition model divides the activity among tumour, normal liver, and lung by the tumour-to-normal uptake ratio on the MAA images, so the activity can give a chosen tumour dose within the liver and lung limits."),
        EX("Activity for a planned dose", STEM("Glass Y-90 microspheres are planned for one lobe of the liver, with uniform uptake assumed.",
                                               [f"intended mean dose = {D_2:.0f} Gy", f"perfused mass = {M_2:.2f} kg", f"lung shunt fraction = {100 * LSF_2:.0f}%", "dose constant = 50 Gy kg GBq<sup>−1</sup>, lungs taken as 1 kg"],
                                               "Find the [[activity]] and the [[lung dose]]."),
           [f"A = D m / [50 (1 − LSF)] = {D_2:.0f} × {M_2:.2f} / (50 × {1 - LSF_2:.2f}) = {A_2:.3f} GBq", f"D<sub>lung</sub> = 50 × {A_2:.3f} × {LSF_2:.2f} = {DL_2:.1f} Gy"],
           f"{A_2:.2f} GBq; the lungs receive {DL_2:.1f} Gy, below the 30 Gy limit."),

        H("Radiation safety and patient release"),
        P("[[3|A written directive, signed beforehand by an authorized user, is required for any therapeutic dosage of unsealed byproduct material and for I-131 sodium iodide above 1.11 MBq (30 µCi) (10 CFR 35.40).]] A patient who cannot be released stays in a private room with its own toilet and a Radioactive Materials sign, with visitors' places and times noted (10 CFR 35.315); staff keep contacts short and use bedside shields, and items leaving the room are monitored."),
        P("[[1|Release is allowed when the total effective dose equivalent to any other individual is not likely to exceed 5 mSv (0.5 rem); written instructions on limiting it are required above 1 mSv (0.1 rem),]] with advice on breast-feeding (10 CFR 35.75). NRC Regulatory Guide 8.39 estimates the dose to the most exposed person over complete decay:"),
        EQ("[[2|D(∞) = 34.6 Γ Q<sub>0</sub> T<sub>p</sub> E / r²]]", "Γ = exposure rate constant (R cm² mCi<sup>−1</sup> h<sup>−1</sup>),   Q<sub>0</sub> = activity (mCi),   T<sub>p</sub> = physical half-life (d),   r in cm",
           "E = occupancy factor, 0.25 at r = 100 cm;   34.6 = 24 h/d × 1.443;   D in rem, with 1 R taken as 1 rem"),
        P(f"With Γ = {G131:g} for I-131, [[2|Revision 1 of the guide lists 1.22 GBq (33 mCi), or 0.07 mSv/h at 1 m, as default release levels]]; a patient-specific estimate with effective half-lives can allow more, with a record of its basis."),
        P("Instructions cover distance from others, especially children and pregnant women, sleeping alone, travel, and hygiene, each for stated days. I-131 leaves in urine, saliva, sweat, and vomit: floors and the toilet are covered with absorbent sheets, and a spill is covered, kept clear, cleaned by staff in gloves, checked with a survey meter and wipe tests, and held as waste to decay."),
        EX("Release estimate for I-131", STEM("A patient is treated with I-131, and the dose to the most exposed other person is estimated with physical decay only.",
                                              [f"Q<sub>0</sub> = {Q_HIST:.0f} mCi (1.22 GBq)", f"Γ = {G131:g} R cm² mCi<sup>−1</sup> h<sup>−1</sup>", f"T<sub>p</sub> = {TP131:g} d", f"E = {OCC:g}", f"r = {R1M:.0f} cm"],
                                              "Find the [[dose]] and the [[activity that gives exactly 5 mSv]]."),
           [f"D(∞) = 34.6 × {G131:g} × {Q_HIST:.0f} × {TP131:g} × {OCC:g} / {R1M:.0f}² = {D_3:.3f} rem = {10 * D_3:.2f} mSv",
            f"Activity for 0.5 rem: {Q_HIST:.0f} mCi × 0.5 / {D_3:.3f} = {Q_5:.1f} mCi = {Q_5 * MBQ_PER_MCI / 1000:.2f} GBq"],
           f"{D_3:.2f} rem ({10 * D_3:.1f} mSv), at the release limit; {Q_5:.1f} mCi gives exactly 5 mSv, and the guide rounds it to 33 mCi."),

        H("Intraoperative radiotherapy"),
        P("Intraoperative radiotherapy (IORT) gives [[1|one fraction, typically 10 to 20 Gy]], to the exposed tumour bed during surgery, with normal tissue moved aside or shielded."),
        TABLE(["Technique", "Beam and applicator", "Dose with depth", "Room"], [
            ["Mobile electron linac", "[[1|Electrons up to about 12 MeV; circular applicators about 3 to 10 cm across, flat or bevelled]]", "[[1|Prescribed at the 90% isodose; energy chosen from the depth of the tumour bed]]", "Little added shielding: low leakage, a beam stopper, a limit on cases per week"],
            ["Low-energy x-rays", "[[1|50 kV source at the centre of a spherical applicator, 1.5 to 5 cm across]]", "[[2|20 Gy at the surface, about 5 to 7 Gy at 1 cm (TARGIT)]]", "No structural shielding; mobile shields"],
            ["HDR brachytherapy", "[[1|Ir-192 source stepping through a flexible applicator laid on the bed]]", "Prescribed at 0.5 to 1 cm depth", "A shielded operating room"]]),
        P("A linac applicator is fixed to the head (hard docking) or clamped to the table with the head aligned to it without contact (soft docking); each applicator, bevel, and energy is commissioned for output, depth dose, and profiles (AAPM TG-72). The 50 kV dose falls by inverse square from the applicator centre and by attenuation; with an illustrative effective attenuation coefficient of 0.3 cm<sup>−1</sup>:"),
        PHOTO("rpt-iort-ham-applicator"),
        EQ("D(r) = D<sub>s</sub> (a/r)² e<sup>−µ(r − a)</sup>   (a = applicator radius, r measured from its centre)",
           f"3 cm applicator, 1 cm deep: {DS:.0f} Gy × ({A_APP:g}/{A_APP + DEPTH:g})² × e<sup>−{MU_X:g} × {DEPTH:.1f}</sup> = {D_X:.1f} Gy   (inverse square alone: {D_X_IS:.1f} Gy)"),
        P(f"A single large fraction is biologically potent, so normal tissue is kept out of the beam; the linear-quadratic model is less certain above about 10 Gy. [[3|A single 10 Gy fraction has an EQD2 of {E10:.1f} Gy for α/β = 10 Gy and {E3:.1f} Gy for α/β = 3 Gy.]] Surveys at the highest energy set the weekly case limit, and a checklist before the beam confirms applicator, bevel, docking, energy, dose, depth, monitor units (independently checked), beam stopper, tissue shields, and that staff are clear."),
        EX("BED of a single IORT dose", STEM("An IORT boost of 10 Gy is given in one fraction.", ["tumour: α/β = 10 Gy", "late-responding tissue in the field: α/β = 3 Gy"],
                                              "Find the [[BED]] and the [[EQD2]] for each, and compare them with 10 Gy in five 2 Gy fractions."),
           [f"Tumour: BED = 10 × (1 + 10/10) = {B10:.0f} Gy; EQD2 = 10 × (10 + 10) / (2 + 10) = {E10:.1f} Gy",
            f"Late-responding tissue: BED = 10 × (1 + 10/3) = {B3:.1f} Gy; EQD2 = 10 × (10 + 3) / (2 + 3) = {E3:.1f} Gy",
            f"Five 2 Gy fractions: BED = {B10F:.0f} Gy (α/β = 10) and {B3F:.1f} Gy (α/β = 3), and EQD2 = 10 Gy for both"],
           f"One 10 Gy fraction equals {E10:.1f} Gy in 2 Gy fractions for the tumour and {E3:.1f} Gy for late-responding tissue, against 10 Gy for the fractionated course."),
    ],
    cards=[
        F("Range of therapy emissions", "Y-90 β particles reach about 11 mm and suit large tumours with patchy uptake; Lu-177 and I-131 β particles reach about 2 mm and suit small tumours; α particles stop within 0.1 mm and suit micrometastases."),
        F("α emitters in therapy", "Ra-223 (11.4 d) and Ac-225 (9.92 d) each release four α particles per decay with their daughters, with a LET of 50 to 230 keV/µm and a range under 0.1 mm."),
        F("Imaging photons of therapy nuclides", "I-131 364 keV, Lu-177 208 and 113 keV, Sm-153 103 keV: post-therapy images, and the dose rate near the patient. Y-90 has none and is imaged by bremsstrahlung or PET."),
        F("MIRD dose equation", "D(target) = Σ Ã(source) × S(target ← source), summed over the source regions."),
        F("S value", "The mean absorbed dose to the target per decay in the source, Σ Δ<sub>i</sub> φ<sub>i</sub> / m. It depends on the nuclide and the geometry, not on the activity or the timing."),
        F("Effective half-life", "1/T<sub>eff</sub> = 1/T<sub>p</sub> + 1/T<sub>b</sub>, so T<sub>eff</sub> = T<sub>p</sub> T<sub>b</sub> / (T<sub>p</sub> + T<sub>b</sub>), shorter than either."),
        F("Cumulated activity", "The area under the activity–time curve: Ã = 1.443 A<sub>0</sub> T<sub>eff</sub> for instantaneous uptake and single-exponential clearance."),
        F("Local deposition approximation", "A pure β emitter in a region much larger than its β range deposits all its energy there, so S = E<sub>mean</sub>/m for the self-dose."),
        F("Written directive for unsealed sources", "Required for any therapeutic dosage of unsealed byproduct material and for I-131 sodium iodide above 1.11 MBq (30 µCi) (10 CFR 35.40)."),
        F("Release of patients", "Allowed when no other individual is likely to receive more than 5 mSv (0.5 rem); written instructions are needed above 1 mSv (10 CFR 35.75)."),
        F("Release estimate for I-131", f"D(∞) = 34.6 Γ Q<sub>0</sub> T<sub>p</sub> E / r². With Γ = {G131:g}, E = {OCC:g}, and r = 100 cm, 33 mCi gives about 0.5 rem.",
          w=[f"34.6 × {G131:g} × {Q_HIST:.0f} × {TP131:g} × {OCC:g} / {R1M:.0f}² = {D_3:.3f} rem"]),
        F("IORT techniques", "One fraction of 10 to 20 Gy by a mobile electron linac (up to about 12 MeV, prescribed at the 90% isodose), 50 kV x-rays in a spherical applicator, or HDR brachytherapy in a flexible applicator."),
        F("One 10 Gy IORT fraction", f"EQD2 {E10:.1f} Gy for α/β = 10 Gy and {E3:.1f} Gy for α/β = 3 Gy.",
          w=[f"BED = 10 × (1 + 10/10) = {B10:.0f} Gy, and EQD2 = {B10:.0f} / (1 + 2/10) = {E10:.1f} Gy", f"BED = 10 × (1 + 10/3) = {B3:.1f} Gy, and EQD2 = {B3:.1f} / (1 + 2/3) = {E3:.1f} Gy"]),
    ],
)

# ---------------------------------------------------------------- practice questions
q_te = t_eff(8.02, 6.0)
te_a, te_b = t_eff(TP_LU, 3.0), t_eff(TP_LU, 6.0); r_ca = te_b / te_a; r_sum = (TP_LU + 6.0) / (TP_LU + 3.0)
q_ca = cum_act(40.0, 60.0); q_d = q_ca * 2.5 / 1000.0
q_d_no143, q_d_ln2, q_d_note = 40.0 * 60.0 * 2.5 / 1000.0, 40.0 * 60.0 * LN2 * 2.5 / 1000.0, MEAN * 40.0 * 2.5 / 1000.0
q_a = y90_activity(120.0, 1.2, 0.10); q_a_nolsf, q_a_times, q_a_nom = 120.0 * 1.2 / 50.0, 120.0 * 1.2 * 0.90 / 50.0, 120.0 / (50.0 * 0.90)
q_amax = 30.0 / (50.0 * 0.18); q_amax_wrong = 30.0 / (50.0 * 0.82)
q_rel = 10 * release_rem(G131, 100.0, TP131, OCC, R1M)                                     # mSv
q_rel_e1, q_rel_24, q_rel_gbq = 10 * release_rem(G131, 100.0, TP131, 1.0, R1M), q_rel * 24 / 34.6, 10 * release_rem(G131, 3.7, TP131, OCC, R1M)
q_eq = eqd2(12, 12, 10); q_eq_bed, q_eq_late = bed(12, 12, 10), eqd2(12, 12, 3)
q_x = sphere_dose(20.0, 2.0, 3.0, MU_X); q_x_is, q_x_lin, q_x_att = 20.0 * (2.0 / 3.0) ** 2, 20.0 * (2.0 / 3.0) * math.exp(-MU_X), 20.0 * math.exp(-MU_X)
RANK_BINS = ["1st (shortest)", "2nd", "3rd", "4th", "5th", "6th (longest)"]

PROBLEMS = [
    PR(STEM("A man with castration-resistant prostate cancer has painful bone metastases and no visceral disease. The team wants a bone-seeking agent whose particles deposit their energy within a few cell diameters.", [], "Which [[agent]] fits?"),
       "Ra-223 dichloride, an α emitter that behaves as calcium", ["Sr-89 chloride, a β emitter with a range of several millimetres", "Sm-153 lexidronam, a β emitter with a range of a few millimetres", "Y-90 microspheres, β emitters carried by the hepatic artery"],
       "Ra-223 collects where bone forms around metastases, and its four α particles per decay with its daughters stop within 0.1 mm. Sr-89 and Sm-153 also seek bone, but their β particles travel millimetres, and Y-90 microspheres treat the liver.", lvl="Easy"),
    PR(STEM("A 5 cm liver tumour takes up a targeting agent unevenly, and many of its cells hold no activity.", [], "Which emission gives the most [[uniform dose]] across these cells?"),
       "Long-range β particles, such as those of Y-90, by crossfire", ["α particles, because of their high LET", "Auger electrons, because they act next to the DNA", "Short-range β particles, such as those of Lu-177"],
       "Y-90 β particles travel up to 11 mm, so cells without activity are irradiated from their neighbours, which evens out the dose. α particles reach only a few cell diameters and Auger electrons far less, so cells away from the activity are missed, and the 2 mm range of Lu-177 bridges fewer gaps.", lvl="Moderate"),
    PR(STEM("A patient given 5.5 GBq of I-131 is kept in hospital under radiation precautions, while a patient given 3 GBq of Y-90 microspheres goes home the same day.", [], "What [[physical difference]] explains this?"),
       "I-131 emits a 364 keV γ ray that leaves the body; Y-90 β particles stay in it", ["I-131 emits β particles with a longer range in tissue than Y-90", "Y-90 has the longer half-life, so its dose rate per GBq is lower", "I-131 emits α particles that pass through the skin to others"],
       f"The 364 keV γ rays of I-131 escape the body and set the dose to others, so a large activity fails the release estimate. Y-90 β particles stop within 11 mm, and only weak bremsstrahlung leaves the patient. The β range of I-131 is the shorter one, and Y-90 has the shorter half-life ({T_Y90:g} h against {TP131:g} d).", lvl="Moderate"),
    SORT("Match each radionuclide to its emissions and use.", ["Ra-223", "Y-90", "I-131", "Lu-177", "Sm-153"],
         [("α particles; bone metastases of prostate cancer", 0), ("Pure β, range up to 11 mm; liver microspheres", 1), ("β and a 364 keV γ ray; thyroid disease", 2),
          ("β with 113 and 208 keV γ rays; PSMA ligands", 3), ("β and a 103 keV γ ray; bone pain, as a phosphonate", 4)],
         "Ra-223 is the α emitter that behaves as calcium. Y-90 has no γ ray and the longest β range. I-131 is known by its 364 keV line, Lu-177 by its 113 and 208 keV lines, and Sm-153 by its 103 keV line; Sm-153 lexidronam binds to bone.", lvl="Easy", mode="match", cap=1),
    PRN(STEM("Radioiodine is retained in thyroid tissue (illustrative values).", ["T<sub>p</sub> = 8.02 d", "T<sub>b</sub> = 6.0 d"], "What is the [[effective half-life]]?"), q_te, [8.02 + 6.0, (8.02 + 6.0) / 2, 8.02 * 6.0 / (8.02 - 6.0)], "{:.2f} d",
        f"T<sub>eff</sub> = T<sub>p</sub> T<sub>b</sub> / (T<sub>p</sub> + T<sub>b</sub>) = 8.02 × 6.0 / 14.02 = {q_te:.2f} d, shorter than either. Adding the half-lives gives 14.02 d and averaging them gives 7.01 d, both longer than the shorter half-life.", lvl="Easy"),
    PR(STEM("A Lu-177 agent clears from a tumour with a biological half-life of 3.0 d. A new ligand raises the biological half-life to 6.0 d, and the activity taken up is unchanged.", [f"T<sub>p</sub> = {TP_LU:g} d"], "By what factor does the [[cumulated activity]] in the tumour change?"),
       f"It rises by a factor of {r_ca:.2f}", [f"It rises by a factor of {r_sum:.2f}", "It doubles, as the biological half-life does", "It is unchanged, as the physical half-life is"],
       f"Ã = 1.443 A<sub>0</sub> T<sub>eff</sub>, and T<sub>eff</sub> rises from {te_a:.2f} d to {te_b:.2f} d, a factor of {r_ca:.2f}. Physical decay still removes activity, so doubling T<sub>b</sub> raises Ã by less than 2; adding the half-lives in place of their rates gives {r_sum:.2f}.", lvl="Moderate"),
    PRN(STEM("A tumour takes up a β-emitting agent at once, which then clears by a single exponential.", ["A<sub>0</sub> = 40 MBq", "T<sub>eff</sub> = 60 h", "S(tumour ← tumour) = 2.5 mGy MBq<sup>−1</sup> h<sup>−1</sup>"], "What [[absorbed dose]] does the tumour receive?"),
        q_d, [q_d_no143, q_d_ln2, q_d_note], "{:.2f} Gy",
        f"Ã = 1.443 × 40 MBq × 60 h = {q_ca:,.0f} MBq h, and D = Ã S = {q_ca:,.0f} × 2.5 mGy = {q_d:.2f} Gy. Leaving out the 1.443 gives {q_d_no143:.2f} Gy, multiplying by ln 2 in place of dividing gives {q_d_ln2:.2f} Gy, and leaving out T<sub>eff</sub> gives {q_d_note:.2f} Gy.", lvl="Moderate"),
    PRM(STEM("The S value for the dose that a tumour receives from its own activity is looked up for a treatment.", [], "Which of these change the [[S value]]?"),
        ["The mass of the tumour", "The radionuclide attached to the agent"], ["The activity administered", "The biological half-life in the tumour", "The time over which the dose is summed"],
        "S is the mean dose to the target per decay in the source: it holds the energy per decay of the nuclide, the fraction absorbed, and the target mass. The activity, the clearance, and the time enter through the cumulated activity, not through S.", lvl="Moderate"),
    PR(STEM("A patient is to go home after treatment with an unsealed radionuclide, and 10 CFR 35.75 sets the condition for release.", [], "Which [[dose to any other individual]] must not be likely to be exceeded?"),
       "5 mSv (0.5 rem)", ["1 mSv (0.1 rem)", "50 mSv (5 rem)", "0.5 mSv (0.05 rem)"],
       "Release is allowed when the total effective dose equivalent to any other individual is not likely to exceed 5 mSv. 1 mSv is the level above which written instructions are required, not the release limit.", lvl="Easy"),
    PR(STEM("After I-131 therapy, a patient-specific calculation estimates the dose to the most exposed member of the household.", ["estimated dose = 3 mSv"], "What does 10 CFR 35.75 [[allow]]?"),
       "Release, with written instructions on keeping the dose to others low", ["Release without instructions, because 3 mSv is below 5 mSv", "Admission until the estimate falls below 1 mSv", "Admission until the estimate falls below 0.5 mSv"],
       "3 mSv is below the 5 mSv release limit, so the patient may go home, but it is above 1 mSv, the level that requires written instructions. Holding the patient until 1 mSv treats the instruction level as the release limit.", lvl="Moderate"),
    PRN(STEM("A release estimate for a patient treated with I-131 uses the NRC equation with physical decay only.", ["Q<sub>0</sub> = 100 mCi (3.7 GBq)", f"Γ = {G131:g} R cm² mCi<sup>−1</sup> h<sup>−1</sup>", f"T<sub>p</sub> = {TP131:g} d", f"E = {OCC:g} at r = 100 cm"], "What [[dose]] does the most exposed person receive?"),
        q_rel, [q_rel_e1, q_rel_24, q_rel_gbq], "{:.1f} mSv",
        f"D = 34.6 × {G131:g} × 100 × {TP131:g} × {OCC:g} / 100² = {q_rel / 10:.2f} rem = {q_rel:.1f} mSv, above 5 mSv, so this estimate does not allow release; one with effective half-lives may. Leaving out the occupancy factor gives {q_rel_e1:.1f} mSv, 24 in place of 34.6 drops the 1.443 and gives {q_rel_24:.1f} mSv, and the activity entered in GBq gives {q_rel_gbq:.1f} mSv.", lvl="Challenging"),
    PRM(STEM("A patient given 5.5 GBq of I-131 cannot be released and is admitted.", [], "Which of these precautions does 10 CFR 35.315 [[require]]?"),
        ["A private room with its own toilet", "A Radioactive Materials sign posted on the room"], ["A bed in a bay shared with patients who had no therapy", "Visits from children only, as they are less sensitive", "Trays and linen sent to general use without monitoring"],
        "The rule requires a private room with its own sanitary facility, or one shared only with another such patient, a posted Radioactive Materials sign, a note of where and how long visitors may stay, and items from the room monitored or handled as radioactive waste. Children are more sensitive, not less, and are kept away.", lvl="Moderate"),
    PR(STEM("An hour after an oral therapy dose of I-131, an inpatient vomits on the floor of the room.", [], "Which [[first action]] fits?"),
       "Keep others out, cover the vomit with absorbent pads, and call radiation safety", ["Mop the floor with water at once and send the mop to the laundry", "Lock the room for ten half-lives, about 80 days, before anyone enters", "Give a second dose at once to replace the activity that was lost"],
       "Containing the spill stops the activity from spreading; trained staff in gloves then clean it, survey with a meter, and take wipe tests, and the waste is held for decay. Mopping spreads the contamination, a room cannot stand empty for months, and any further dose waits until the retained activity is known.", lvl="Challenging"),
    PR(STEM("In intraoperative electron therapy, the energy is chosen from the measured depth of the tumour bed.", [], "Which [[isodose]] is usually placed at the deep edge of the target?"),
       "The 90% isodose", ["The 50% isodose", "The 100% isodose", "The 30% isodose"],
       "IORT electron doses are usually prescribed at the 90% isodose, so the energy is chosen to bring that depth to the deep edge of the bed. The 100% level lies at the depth of maximum dose, shallower than the deep edge, and the 50% level leaves the deep part underdosed.", lvl="Easy"),
    PRN(STEM("An IORT boost is given in one fraction to a tumour bed.", ["dose = 12 Gy", "tumour α/β = 10 Gy"], "What is the [[EQD2]] for the tumour?"),
        q_eq, [12.0, q_eq_bed, q_eq_late], "{:.1f} Gy",
        f"EQD2 = D (d + α/β) / (2 + α/β) = 12 × 22 / 12 = {q_eq:.1f} Gy. The BED is {q_eq_bed:.1f} Gy and the physical dose 12 Gy; α/β = 3 Gy gives {q_eq_late:.1f} Gy, the value for late-responding tissue in the field.", lvl="Moderate"),
    PR(STEM("A hospital plans IORT with a mobile electron linac of up to 12 MeV in an existing operating room with ordinary walls.", [], "Which [[radiation protection plan]] fits?"),
       "A beam stopper under the patient, a survey at the highest energy, and a weekly case limit", ["A maze and a borated polyethylene door, as for an 18 MV photon vault", "No added measures, because the electrons stop within the patient's tissue", "Lead aprons for the surgical team, who stay at the table during the beam"],
       "Mobile IORT linacs have low leakage and a beam stopper that intercepts the primary beam, and a survey at the highest energy sets how many cases a week keep nearby areas within their limits (AAPM TG-72). Neutron shielding belongs to high-energy photon vaults, bremsstrahlung and leakage still leave the patient, and staff leave the room during the beam.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3, 4], 1: [5, 6, 7], 3: [9, 10, 11, 13], 4: [14, 15, 16]}

TERMS = ['crossfire', 'cumulated activity', 'S value', 'effective half-life', 'local deposition approximation', 'lung shunt fraction', 'partition model', 'written directive']

TAKE = [
    ["Y-90 β up to 11 mm for large tumours (crossfire); Lu-177 and I-131 β about 2 mm for small ones; α under 0.1 mm for micrometastases.",
     "α particles: LET 50 to 230 keV/µm; Ra-223 and Ac-225 give four per decay with their daughters.",
     "γ rays of I-131 (364 keV) and Lu-177 (208 and 113 keV) give images and dose to others; Y-90 has none."],
    ["D = Σ Ã × S, with S the dose to the target per decay in the source.",
     "1/T<sub>eff</sub> = 1/T<sub>p</sub> + 1/T<sub>b</sub>, and Ã = 1.443 A<sub>0</sub> T<sub>eff</sub>.",
     "Local deposition: S = E<sub>mean</sub>/m; Y-90 gives about 50 Gy per GBq per kg."],
    ["LSF = lung / (lung + liver) counts on the Tc-99m MAA scan.",
     "D = 50 A (1 − LSF) / m; lung dose = 50 A × LSF per 1 kg, at most about 30 Gy per treatment and 50 Gy in total.",
     "Glass: about 2500 Bq per sphere; resin: about 50 Bq, so more spheres and more embolic."],
    ["Release if no other person is likely to exceed 5 mSv; written instructions above 1 mSv (10 CFR 35.75).",
     "D(∞) = 34.6 Γ Q<sub>0</sub> T<sub>p</sub> E / r²: 33 mCi of I-131 gives about 0.5 rem.",
     "Written directive for any therapeutic dosage, and for I-131 above 1.11 MBq (30 µCi)."],
    ["IORT: one fraction of 10 to 20 Gy by electrons (up to about 12 MeV, 90% isodose), 50 kV x-rays, or HDR.",
     "50 kV: 20 Gy at the applicator surface, about 5 to 7 Gy at 1 cm.",
     f"10 Gy in one fraction: EQD2 {E10:.1f} Gy for α/β = 10 Gy and {E3:.1f} Gy for α/β = 3 Gy."],
]
