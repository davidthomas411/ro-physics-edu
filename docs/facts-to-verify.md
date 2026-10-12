# Facts to check against the primary sources

The chapters on measurements, quality assurance, radiation protection, special procedures, imaging, brachytherapy, and particle and stereotactic therapy were drafted from memory and from search summaries. The primary documents were not available while they were written. Each item below is a statement that was not confirmed against the document named. A physics reviewer settles each one, corrects the chapter if needed, and records the review date in `site_config.json`.

Values that were confirmed from several secondary sources are not listed. The numbers that the chapters compute are re-derived by `tests/numbers_*.py`; those tests check arithmetic, not whether an input matches a report. A second pass by model reviewers found wording and attribution problems in the first group of chapters (ion chambers through proton therapy); the text was corrected, and the items they could not settle are listed here. That pass does not replace a review by a physicist.

## Ion chambers and charge collection (`ion-chambers`)

- No humidity correction between 20% and 80% relative humidity: TG-51 text.
- Leakage under 0.1% of the reading and P<sub>pol</sub> within 0.4% for a reference-class chamber: TG-51 addendum (McEwen et al., 2014), Table I.
- The corrected reading in the 2014 addendum, M = M<sub>raw</sub> P<sub>TP</sub> P<sub>leak</sub> P<sub>ion</sub> P<sub>pol</sub> P<sub>elec</sub> P<sub>rp</sub>, with P<sub>leak</sub> = 1 − Bt/M<sub>raw</sub>: McEwen et al., Med Phys 41:041501, the equation that defines M. The chapter gives the original four-factor product and names the two added factors.
- The pulsed P<sub>ion</sub> expression for pulsed-swept beams (TG-51, equation 12), and what the 2014 addendum says about pulsed-scanned beams.
- Polarity effect of several percent in some parallel-plate chambers in low-energy electron beams (NPL measured about 5% at 4 MeV for two models): TG-51, electron section.
- That P<sub>ion</sub> above 1.05 calls for another chamber: TG-51 worksheet A. No text was found that bars a higher bias within the rating of the chamber.
- P<sub>ion</sub> of 1.002 to 1.02 in linac beams: Kry et al., JACMP 2012.
- Build-up cap of about 0.5 g/cm² for Co-60: TRS-398 or ADCL practice.
- Thermal settling time of several minutes: chamber manufacturer or a physics report.
- The range of the free-air chambers that serve as primary standards (10 to 300 kV): NIST.
- Reference temperature of TRS-398 (20 °C) against TG-51 (22 °C).

## TG-51 beam calibration (`tg51`)

- Farmer-type k<sub>Q</sub> of about 0.99 at 6 MV and about 0.97 at 18 MV (one chamber checked at each end): TG-51 Table I and the 2014 addendum Table I.
- The 2014 addendum: dose equation and reference conditions kept; %dd(10)<sub>x</sub> = 1.267 %dd(10) − 20.0 for flattened beams measured without the foil, valid for an open-beam %dd(10) from 75% to 89% (below 75%, %dd(10)<sub>x</sub> = %dd(10)), with at most 0.2% change in k<sub>Q</sub>; flattening-filter-free beams still need the foil (section 4.H). The range limits come from a talk and worksheet A, not from the addendum.
- P<sub>rp</sub> as the radial dose profile averaged over the sensitive volume, and P<sub>leak</sub> as an added factor: McEwen et al., 2014.
- The electron addendum (AAPM Report 385, Muir et al., 2024): 4 to 22 MeV, reference-class cylindrical chambers at every energy, no measured P<sub>gr</sub>, doses up to about 2% higher. What Report 385 says about plane-parallel chambers, cross-calibration, and the chamber position was not checked, and the chapter says nothing on them.
- Plane-parallel chambers required below R<sub>50</sub> = 2.6 cm and preferred below 4.3 cm in the original protocol; the wall-effect reason for cross-calibration; the foil 50 or 30 cm above the phantom surface: TG-51 (1999), worksheets A and B.
- Some national laboratories use graphite calorimeters (for example NPL): BIPM key-comparison reports.

## Diodes, luminescent dosimeters, and film (`dosimeters`)

- LiF reads about 1.3 times high near 30 keV (published values 1.2 to 1.4) and Al<sub>2</sub>O<sub>3</sub> three to four times: TG-191, NIST SRD 126, Scarboro and Kry.
- TLD and OSLD dose uncertainty of roughly 2% to 5% (one standard deviation), the low end only with a careful calibration and controlled use: the uncertainty budgets of TG-191.
- MOSFET lifetime of tens to a few hundred gray: vendor data sheets.
- Diode temperature coefficient of 0.1% to 0.5% per °C (typically about 0.3%) and a sensitivity that rises with dose per pulse, by an amount that varies among diodes: TG-62.
- Water-to-silicon stopping-power ratio of about 1.2, changing by about 5% from 1 to 20 MeV: NIST ESTAR.
- Fricke ε of 2,174 L mol<sup>−1</sup> cm<sup>−1</sup> (range 2,160 to 2,200), G = 15.5 per 100 eV, density 1.024 kg/L: ICRU Report 35.
- Radiochromic film: orientation difference up to about 10%, darkening fast in the first hours and slowly for days (a plateau near 24 h, about 2.5% more over days), red against green channel: TG-235.
- Silver-halide film reading up to about ten times high near 30 to 50 keV: a published energy-response table.
- IROC Houston criterion of 5% for mailed OSLD: IROC.
- TLD anneal of about 1 h at 400 °C and then about 2 h at 100 °C for LiF:Mg,Ti, and the onset of supralinearity between 1 and 10 Gy: TG-191.

## Dose limits and ALARA (`dose-limits`)

- Linacs are not byproduct material and fall under state radiation-control rules that in nearly every state carry the same numerical limits: CRCPD Suggested State Regulations, Part D, or the state code.
- Investigation levels of 10% and 30% of the limit and the actions they trigger: NUREG-1556 Volume 9 (check whether the current revision keeps the model program).
- NCRP 116 values: embryo-fetus 0.5 mSv per month, public 5 mSv in infrequent exposures, lens 150 mSv: NCRP 116, Table 19.1.
- Survey-meter calibration under 10 CFR 35.61 (before first use, annually, after a repair that affects calibration, on every scale up to 10 mSv/h with two readings per scale or decade, and the 20% criterion); the traceability to NIST directly or through an ADCL is usual practice, not part of the rule. Any NRC revision of Part 20 after 2015 was not checked.
- Geiger-Mueller dead time of the order of 100 µs: Knoll.
- The ICRP 103 neutron radiation weighting function (equation 4.3) and 13 remainder tissues per sex (Table 3 footnote).

## Shielding design for linac vaults (`shielding`)

- Patient scatter fractions at 90° per 400 cm²: 4.26 × 10<sup>−4</sup> at 6 MV and 1.89 × 10<sup>−4</sup> at 18 MV; scatter TVL of 17 cm of concrete at 6 MV: NCRP 151, Appendix B.
- Where d<sub>L</sub> is measured from: the isocenter when the gantry angles are used about equally, otherwise the closest approach of the head: NCRP 151, section on secondary barriers.
- The rule of adding one half-value layer, taken from the component that sets the larger thickness, when the scatter and leakage thicknesses differ by less than one TVL (from NCRP 49; the wording in NCRP 151 was not confirmed).
- That the IMRT factor C<sub>I</sub> multiplies only the IMRT part of a mixed workload and enters only the leakage term.
- That concrete thick enough for the photons is generally enough for the neutrons, and that lead or steel is not.
- Door figures: neutrons reaching the door mostly as epithermal and thermal neutrons, capture gamma rays of about 3.6 MeV, lead TVL of 6.1 cm (McGinley; NCRP 79).
- The Kersey tenth-value distance of 5 m along the maze, and the Wu–McGinley distance 2.06 √S m with S the maze cross-section in m²: NCRP 151, neutron section.
- Steel TVLs and the placement of metal in laminated barriers were left out because they could not be verified.

## Linac quality assurance and TG-142 (`qa-linac`)

- Every value in the TG-142 table and its frequency (the table was checked only against secondary copies): TG-142 (Klein et al., 2009). TG-198 (2021) changed some values, among them light and radiation field coincidence (±2 mm per jaw; ±1 mm for SRS/SBRT), the isocenter tolerances (absolute values), and possibly the daily imaging-treatment coincidence for SBRT (2 mm; SRS with image guidance stays at 1 mm). The chapter states the TG-142 values and says that TG-198 restates some.
- The wording of the three TG-142 action levels (inspection, scheduled, immediate), and that the tabulated tolerance is also the first action level: TG-142.
- That the SRS/SBRT column applies to a machine used for SRS/SBRT: TG-142.
- The heterogeneity test with lung slabs in MPPG 5.a; the publication years in the documents table.
- IROC mailed-dosimeter and phantom audits as described.

## Stereotactic radiosurgery and SBRT (`srs-sbrt`)

- TG-101 recommending algorithms that model lateral electron transport in lung, and a calculation grid of 2 to 3 mm or finer (the wording was not read): TG-101, Med Phys 37:4078.
- Prescription isodose ranges of 40% to 60% on Gamma Knife, 70% to 90% (often 80%) on a linac with cones or arcs, and higher for intensity-modulated plans; 60% to 90% in RTOG 0915: a trial protocol and a practice survey.
- Gamma Knife gradient index of about 2.5 to 3 for small and medium targets, and linac and robotic plans usually higher: Paddick and Lippitz, 2006.
- Synthetic diamond with a small correction (k near 1) tabulated down to about 5 mm: TRS-483, PTW 60019 rows.
- The Toulouse accident of 2006 to 2007 (145 patients, an unsuitable detector): the ASN report of 2007.
- The end-to-end limit for a static target on a robotic linac: the 0.95 mm is the manufacturer's specification; TG-135 (2011) was quoted in one secondary table as under 0.9 mm static and under 1.5 mm moving, and TG-135.B (2025) Table 1 was not read.
- ASTRO policy allowing up to five fractions for radiosurgery.
- Robotic, helical, and Gamma Knife details, including the 6 cm reference field and the mask on recent Gamma Knife models: vendor documents and TRS-483.
- The Winston–Lutz limits of 1.0 mm for SRS and 1.5 mm for SBRT in MPPG 9.a and what MPPG 9.b (2025) states; the TG-142 annual row for the coincidence of radiation and mechanical isocenters; that TG-155 is the 2021 small-field report (Med Phys 48:e886).
- The RTOG R<sub>50%</sub> and D<sub>2cm</sub> limit values were left out because they could not be verified.

## Proton and ion beam therapy (`protons`)

- PSTAR CSDA ranges in water at 70, 100, and 150 MeV, and the projected range of about 33 g/cm² at 230 MeV: NIST PSTAR.
- The figure, the spread-out peak example, and the entrance doses (26% for a single peak, 65% for a 6.6 cm modulation) come from Bortfeld's analytical model in code. Two parameters, a nuclear loss of 0.012 per cm and a local fraction of 0.6, are from memory, and the 1% energy spread (σ) is a choice: Bortfeld, Medical Physics 1997. Measured entrance doses depend on the machine and the delivery.
- Relative stopping power of cortical bone of 1.6 to 1.7: Schneider et al., 1996.
- RBE of about 1.35 at the distal edge and 1.7 in the fall-off (in-vitro averages, Paganetti 2014), and an extension of the biologic range of about 1 to 2 mm, up to about 4 mm in some models: Paganetti 2014; whether TG-256 repeats them was not checked.
- Distal range margin recipes: 3.5% plus 1 mm (Massachusetts General Hospital), 2.5% plus 1.5 mm, or up to 3 mm added; TG-202 supports the sources of uncertainty and not one recipe.
- Carbon-ion RBE from under 2 at the entrance to 3 or more at the peak (model dependent), 430 MeV/u reaching about 30 cm, 6.6 T m, a synchrotron 20 to 25 m across: HIT, CNAO, and MedAustron publications.
- That helium ions rank between protons and carbon for lateral scatter was not checked at the source.

## Risk management and TG-100 (`risk-management`)

The regulation text was checked only through search summaries and state rules that copy it.

- 10 CFR 35.3045 deadlines and disclosure: a telephone report by the next calendar day, a written report in 15 days without the patient's name, the physician and the patient told within 24 hours: 35.3045(c) to (e).
- Events caused by the patient are reported only when there is permanent functional damage: 35.3045(b).
- Permanent seed implants have separate criteria: 35.3045(a)(2).
- The contents of a written directive for HDR: 35.40(b).
- The TG-100 scale endpoints (occurrence of 1 is about 1 in 10,000; severity of 1 is no effect) and that TG-100 advises against ranking by RPN alone: TG-100 Table II and its text.
- The six-level ranking of quality-management tools, with protocols and standards above independent checks: TG-100, or the AAPM guide to it (the ranking follows the Institute for Safe Medication Practices).
- The Joint Commission sentinel event for a dose more than 25% above the planned dose: its current Sentinel Event Policy.

## Total body and total skin irradiation (`tbi-tset`)

- Dose uniformity of ±10% and a dose-rate ceiling of 20 cGy/min: the ACR-ARS practice parameter for total body irradiation.
- A usual dose rate of 5 to 15 cGy/min, a treatment distance of 3 to 5 m, and a lung dose limit of 8 to 10 Gy: AAPM Report 17 (TG-29) and published protocols.
- That AAPM Report 23 names the multiplication factor B: Report 23.
- The EORTC limit of 0.7 Gy for the photon dose and 30 to 36 Gy over 8 to 10 weeks: EORTC consensus, J Am Acad Dermatol 2002;47:364.
- Total skin electron geometry: gantry angles of about 15° to 20° (18° at Stanford), a 1 cm acrylic scatter plate, and a distance of 3 to 4 m: Report 23.
- A beam spoiler giving at least 90% of the skin dose within about 20 cm: single studies.
- Invented values, labelled as illustrative in the text: the 18 MV tissue-maximum ratios (from an exponential model), the output factor of 1.07 at 100 cm, the lung factors 1.10 and 1.12, and the dose fractions for each total skin position.

## Kilovoltage x-ray production (`xray-tube`)

- Grenz half-value layer of a few hundredths of a millimetre of aluminium and a contact-therapy half-value layer of about 0.3 to 1.5 mm Al: Khan, clinical radiation generators.
- Orthovoltage mostly 200 to 300 kV at an SSD of 30 to 50 cm: Khan; an AAPM review course.
- Stationary oil- or water-cooled anodes in kilovoltage therapy tubes: vendor data.
- Anode angles of 7° to 20°: Bushberg.
- Tungsten K<sub>α</sub> lines at 58.0 and 59.3 keV and K<sub>β</sub> lines at 67 to 69 keV: the X-ray Data Booklet.
- NIST mass attenuation coefficients for Al at 20 and 50 keV and Cu at 60 keV (Al at 30 and 40 keV and Cu at 80, 100, and 150 keV were confirmed): NIST SRD 126.
- The TG-61 in-air equation with P<sub>stem,air</sub>: TG-61, Med Phys 28:868.
- The 2.5 mm Al minimum filtration above 70 kVp: found in state codes and not traced to the federal text.

## Linac components (`linac-components`)

- Magnetron peak power of about 2 to 5 MW and klystron about 5 to 7 MW, with magnetrons in some high-energy machines: Karzmark, *Medical Electron Accelerators*; vendor specifications.
- A standing-wave gain of 12 to 20 MeV/m, and 4 to 6 MV guides pointing straight at the isocenter: a conference paper; Varian 600C specifications.
- Gun injection at tens of keV (IAEA handbook, chapter 5) and an energy-slit window of ±3% (a patent only).
- A tungsten target backed by copper: vendor or Monte Carlo target specifications.
- A mean photon energy of about one third of the maximum (a rule of thumb; Mohan 1985 spectra suggest it overestimates at 18 MV).
- TPR<sub>20,10</sub> of 0.629 against 0.665: Fogliata et al., TrueBeam.
- A thin plate replacing the filter in some flattening-filter-free designs, and less off-axis softening in those beams: vendor documents and reviews of flattening-filter-free beams.
- A pulse rate of 360 per second, labelled illustrative: Kojima et al.
- The list of interlocks: vendor manuals.
- The beam current falling in electron mode and photon mode needing about 100 times more: Leveson's account of the Therac-25.

## CT simulation, registration, and motion (`simulation-motion`)

- TG-76's list of approaches, end-exhale gating, and tracking latency: TG-76.
- Amplitude sorting leaving bins empty: Abdelnour 2007.
- A pitch of about 0.1 and the simplified rule p ≤ T<sub>rot</sub>/T<sub>breath</sub>: Keall 2004.
- A 4D-CT dose often 2 to 4 times that of a helical scan (published comparisons run from under 2 to 12.8 times).
- The valve of an active breathing control device: Wong 1999.
- TG-66 tolerances in the table (secondary sources only): TG-66, Tables II and III.
- TG-132 registration tolerance of about one voxel, 2 to 3 mm: Brock 2017.
- Contrast changing the dose by less than about 2%: a few small studies.
- Tumour motion magnitudes: Seppenwoolde 2002.

## Image guidance (`igrt`)

- TG-142 Table V: daily imaging-treatment isocenter coincidence of 2 mm (1 mm for SRS/SBRT) and the annual imaging-dose test. The couch-shift (repositioning) tolerance was left out.
- Imaging dose: an MV portal pair at 1 to 5 cGy and a kV pair well under 1 cGy: Ding and Munro 2013; TG-180.
- MR guidance: cine imaging at several images a second (vendor specifications) and adaptive plans checked by an independent dose calculation (workflow reports).
- Probe pressure displacing the prostate (TG-154) and transponder artifacts on MR (TG-147).
- A six-degree-of-freedom couch correction range of a few degrees: vendor specifications.

## Brachytherapy calibration and safety (`brachy-qa`)

- MPPG 13.a values (source strength within 3%, timer within 1% or 1 s), seen only in a search summary: MPPG 13.a, JACMP 2023.
- An independent plan check agreeing within about 5%: TG-59 or MPPG 13.a.
- Patient-release dose rates of 0.01 and 0.03 mSv/h at 1 m and an occupancy factor of 0.25: Regulatory Guide 8.39 (1997). A 2026 draft revision makes the default occupancy factor 1, so the current guide must be read.
- Ir-192 half-value layers of 3 to 6 mm lead and 3 to 5 cm concrete; the problems use 4.8 mm and 4.5 cm as illustrative values: IAEA SRS 47.
- The emergency equipment in the NRC daily checks, the yearly drills, and the survey after treatment: 10 CFR 35.643, 35.610, 35.604.
- Patient instructions (seeds passing in semen, precautions for months): IPEM Report 106.

## Brachytherapy planning and applicators (`brachy-planning`)

- Postimplant CT of an I-125 implant at about 30 days: TG-137.
- Implant-alone doses of 145, 125, and 115 Gy for I-125, Pd-103, and Cs-131; V<sub>100</sub> of at least 95%, D<sub>90</sub> of at least 100%, V<sub>150</sub> of 50% to 65%; urethra D<sub>10</sub> under 150% and D<sub>30</sub> under 130%: TG-137; ABS 2012, Davis.
- ABS cervix goals: high-risk CTV D<sub>90</sub> of 80 to 90 Gy; D<sub>2cc</sub> of 90 Gy for the bladder and 70 to 75 Gy for the rectum and sigmoid: Viswanathan 2012.
- EMBRACE II planning aims: protocol version 1.0.
- The ICRU 38 rectal-point wording and point A in the minimum report of ICRU 89: ICRU 38 and 89.
- An HDR source step of commonly 2.5 or 5 mm: vendor specifications.
- Lungs as the usual site of seed migration, and stranded seeds migrating less: not searched.
- 1.27 U/mCi for I-125: TG-43U1.
- A 50 mCi licence limit in the seed example is labelled illustrative; no regulatory limit was verified.

## Radiopharmaceutical therapy and intraoperative radiotherapy (`rpt-iort`)

- The I-131 half-life is printed as 8.02 d; the newest evaluated value, 8.0252 d, rounds to 8.03 d: NuDat.
- Mean ranges of the beta emitters: Lu-177 about 0.3 mm (EANM; published values run from 0.23 to 0.67 mm), and approximate values for Sm-153 and Sr-89: EANM and SNMMI guidelines.
- Alpha energies of about 6 to 8 MeV: ENSDF decay chains.
- The 50 Gy cumulative lung limit and the 20% resin lung shunt fraction cut-off for Y-90 microspheres: the device instructions for use.
- Patient-release levels of 33 mCi and 0.07 mSv/h at 1 m: Regulatory Guide 8.39, Revision 1. A draft Revision 2 may change them.
- Intraoperative details: applicator sizes, no structural shielding for 50 kV systems, and a shielded room for HDR: TG-72 and vendor specifications.
- That the exposure per unit activity is far higher for I-131 than for Lu-177 rests on photon yields, not on a verified exposure rate constant for Lu-177.
