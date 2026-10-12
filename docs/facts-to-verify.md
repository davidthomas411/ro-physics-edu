# Facts to check against the primary sources

The chapters on measurements, quality assurance, radiation protection, special procedures, and particle and stereotactic therapy were drafted from memory and from search summaries. The primary documents were not available while they were written. Each item below is a statement that was not confirmed against the document named. A physics reviewer settles each one, corrects the chapter if needed, and records the review date in `site_config.json`.

Values that were confirmed from several secondary sources are not listed. The numbers that the chapters compute are re-derived by `tests/numbers_*.py`; those tests check arithmetic, not whether an input matches a report.

## Ion chambers and charge collection (`ion-chambers`)

- No humidity correction between 20% and 80% relative humidity: TG-51 text.
- Leakage under 0.1% of the reading and P<sub>pol</sub> within 0.4% for a reference-class chamber: TG-51 addendum (McEwen et al., 2014), Table I.
- The pulsed P<sub>ion</sub> expression for pulsed-swept beams (TG-51, equation 12); what the 2014 addendum says about pulsed-scanned beams.
- P<sub>pol</sub> of about 2% in low-energy electron beams: TG-51, electron section.
- P<sub>ion</sub> of 1.002 to 1.02 in linac beams: Kry et al., JACMP 2012.
- Build-up cap of about 0.5 g/cm² for Co-60: TRS-398 or ADCL practice.
- Thermal settling time of several minutes: chamber manufacturer or a physics report.
- The range of the free-air chambers that serve as primary standards (10 to 300 kV): NIST.
- Reference temperature of TRS-398 (20 °C) against TG-51 (22 °C).

## TG-51 beam calibration (`tg51`)

- Farmer-type k<sub>Q</sub> of about 0.99 at 6 MV and about 0.97 at 18 MV (one chamber checked at each end): TG-51 Table I and the 2014 addendum Table I.
- The 2014 addendum: dose equation and reference conditions kept; %dd(10)<sub>x</sub> = 1.267 %dd(10) − 20.0 for flattened beams without the lead foil, with at most 0.2% change in k<sub>Q</sub>; flattening-filter-free beams still need the foil (section 4.H).
- The electron addendum (AAPM Report 385, Muir et al., 2024): 4 to 22 MeV, reference-class cylindrical chambers at every energy, no measured P<sub>gr</sub>, doses up to about 2% higher.
- Plane-parallel chambers preferred below R<sub>50</sub> = 4.3 cm; the wall-effect reason for cross-calibration; the foil 50 or 30 cm above the phantom surface: TG-51.
- Some national laboratories use graphite calorimeters (for example NPL): BIPM key-comparison reports.

## Diodes, luminescent dosimeters, and film (`dosimeters`)

- LiF reads about 1.3 to 1.4 times high near 30 keV and Al<sub>2</sub>O<sub>3</sub> three to four times: TG-191, NIST SRD 126.
- TLD and OSLD dose uncertainty of 2% to 5% (one standard deviation): TG-191.
- MOSFET lifetime of tens to a few hundred gray: vendor data sheets.
- Diode temperature coefficient of 0.1% to 0.5% per °C and a sensitivity that rises with dose per pulse: TG-62.
- Fricke ε of 2,174 L mol<sup>−1</sup> cm<sup>−1</sup> (range 2,160 to 2,200), G = 15.5 per 100 eV, density 1.024 kg/L: ICRU Report 35.
- Radiochromic film: orientation difference up to about 10%, darkening for about a day, red against green channel: TG-235.
- Water-to-silicon stopping-power ratio nearly constant for electrons: TG-70.
- IROC Houston criterion of 5% for mailed OSLD: IROC.
- TLD anneal of 400 °C for 1 h, then a low-temperature step: TG-191.

## Dose limits and ALARA (`dose-limits`)

- Linacs fall under state rules that follow the same limits: CRCPD Suggested State Regulations, Part D, or the state code.
- Investigation levels of 10% and 30% of the limit and the actions they trigger: NUREG-1556 Volume 9 (check whether the current revision keeps the model program).
- NCRP 116 values: embryo-fetus 0.5 mSv per month, public 5 mSv in infrequent exposures, lens 150 mSv: NCRP 116, Table 19.1.
- Calibration of a survey meter traceable to NIST directly or through an ADCL: practice and some state rules; 10 CFR 35.61 says only "a radiation source".
- Geiger-Mueller dead time of the order of 100 µs: Knoll.
- The ICRP 103 neutron radiation weighting function (equation 4.3) and 13 remainder tissues per sex (Table 3 footnote).

## Shielding design for linac vaults (`shielding`)

- Patient scatter fractions at 90° per 400 cm²: 4.26 × 10<sup>−4</sup> at 6 MV and 1.89 × 10<sup>−4</sup> at 18 MV; scatter TVL of 17 cm of concrete at 6 MV: NCRP 151, Appendix B.
- Whether d<sub>sec</sub> and d<sub>L</sub> are measured from the isocenter or from the target: NCRP 151, section on secondary barriers.
- The rule of adding one half-value layer when the scatter and leakage thicknesses differ by less than one TVL (from NCRP 49; the wording in NCRP 151 was not confirmed).
- That the IMRT factor C<sub>I</sub> multiplies only the IMRT part of a mixed workload and enters only the leakage term.
- That concrete thick enough for the photons is generally enough for the neutrons.
- Door figures: neutrons of about 100 keV at the door, capture gamma rays of about 3.6 MeV, lead TVL of 6.1 cm (McGinley; NCRP 79).
- A neutron dose falling about tenfold for each 5 m of maze (the Kersey method): the tenth-value distance and how it is defined.
- Steel TVLs and the placement of metal in laminated barriers were left out because they could not be verified.

## Linac quality assurance and TG-142 (`qa-linac`)

- Every value in the TG-142 table and its frequency (the table was checked only against secondary copies): TG-142 (Klein et al., 2009). TG-198 (2021) changed some values, among them light and radiation field coincidence (±2 mm per jaw) and the isocenter tolerances, which are absolute values; the chapter quotes TG-142.
- The wording of the three TG-142 action levels (inspection, scheduled, immediate): TG-142.
- The heterogeneity test with lung slabs in MPPG 5.a; the publication years in the documents table.
- IROC mailed-dosimeter and phantom audits as described.

## Stereotactic radiosurgery and SBRT (`srs-sbrt`)

- TG-101 advising against pencil-beam algorithms that scale only the path length.
- Prescription isodose ranges of 40% to 60% on Gamma Knife and 80% to 95% on linacs: a practice survey.
- Gamma Knife gradient index of about 2.5 to 3: Paddick and Lippitz, 2006.
- Synthetic diamond within about 2% down to 5 mm: TRS-483 tables.
- The Toulouse accident of 2006 to 2007 (145 patients, an unsuitable detector): the ASN report of 2007.
- The static end-to-end limit of 0.95 mm: TG-135 (seen only in the TG-135.B update).
- ASTRO policy allowing up to five fractions for radiosurgery.
- Robotic, helical, and Gamma Knife details, including the 6 cm reference field and the mask on recent Gamma Knife models: vendor documents and TRS-483.
- Whether MPPG 9.b keeps the 1.0 and 1.5 mm limits of MPPG 9.a; that TG-155 is the 2021 small-field report (title not verified).
- The RTOG R<sub>50%</sub> and D<sub>2cm</sub> limit values were left out because they could not be verified.

## Proton and ion beam therapy (`protons`)

- PSTAR CSDA ranges in water at 70, 100, and 150 MeV, and the projected range of about 33 g/cm² at 230 MeV: NIST PSTAR.
- The figure, the spread-out peak example, and the entrance doses (26% for a single peak, 65% for a 6.6 cm modulation) come from Bortfeld's analytical model in code. Two parameters, a nuclear loss of 0.012 per cm and a local fraction of 0.6, are from memory, and the 1% energy spread is a choice: Bortfeld, Medical Physics 1997.
- Relative stopping power of cortical bone of 1.6 to 1.7: Schneider et al., 1996.
- Spot σ of 2 to 6 mm: vendor commissioning papers.
- RBE of about 1.35 at the distal edge and 1.7 in the fall-off, and a range extension of a few millimetres: TG-256.
- Carbon-ion RBE of 2 to 4, 430 MeV/u reaching about 30 cm, 6.6 T m, a synchrotron about 20 m across: HIT publications.
- That helium ions rank between protons and carbon for lateral scatter was not checked.

## Risk management and TG-100 (`risk-management`)

The regulation text was checked only through search summaries and state rules that copy it.

- 10 CFR 35.3045 deadlines and disclosure: a telephone report by the next calendar day, a written report in 15 days without the patient's name, the physician and the patient told within 24 hours: 35.3045(c) to (e).
- Events caused by the patient are reported only when there is permanent functional damage: 35.3045(b).
- Permanent seed implants have separate criteria: 35.3045(a)(2).
- The contents of a written directive for HDR: 35.40(b).
- The TG-100 scale endpoints (occurrence of 1 is about 1 in 10,000; severity of 1 is no effect) and that TG-100 advises against ranking by RPN alone: TG-100 Table II and its text.
- The six-level ranking of quality-management tools, with protocols and standards above independent checks: TG-100, or the AAPM guide to it (the ranking follows the Institute for Safe Medication Practices).
- The Joint Commission sentinel event for a dose more than 25% above the planned dose: its current Sentinel Event Policy.
