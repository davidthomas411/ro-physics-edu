# Audit of the site's question bank against the ROECSG Physics Study Guide

Site audited: the working tree at commit f0e32c8 (42 topics, 505 cards, 659 problems), which is the source archive before the real-image work and before the questions described under 'Status after the follow-up commits'. Reference: the ROECSG Physics Study Guide (the PDF in the repository root), 277 parsed questions plus 23 further items found only in the raw text (Appendix B). Date of the audit: 2026-10-11. The audit changed no site file. It is a gap and level analysis: no wording from the guide is used in the site, and the guide's own keys are treated as claims to verify, not as answers.

## Summary

- **Coverage.** Of 277 parsed guide questions, 79 (29%) are covered, 68 (25%) partial and 130 (47%) not covered.
- **Planned against unexpected.** 155 of the 198 gaps (78%) sit on topics on the PLAN that are not yet built. 43 are unplanned gaps in built topics (35 partial, 8 not covered). Of the 122 guide questions that belong to built topics, 79 (65%) are covered.
- **Blueprint weight.** Domains VI and VII (26% to 30% of the ABR blueprint) and II.B have no built topic. The guide is not a weighting yardstick: 30% of its questions are in domain I (blueprint 11% to 13%) and 9% are in imaging (16% to 18%).
- **Imaging, guide chapters 12-13.** 24 questions: 3 covered, 6 partial, 15 not covered. At the snapshot the site had nothing on ultrasound, MR safety, MR simulation or synthetic CT, 4D-CT or motion management. kV against MV cone-beam CT is compared only in part. PET against SPECT, PET and SPECT agents by name, optical density and CT patient size are thin (section d).
- **Level.** Where both exist, the site's problems are more calculation-heavy than the guide (36% one-step or multi-step against 14%) and less conceptual (19% against 32%). The excess is arithmetic and derivation, not breadth: relativistic physics, MU with tables, TG-43 and IMRT-delivery algebra go deeper than anything in the guide. Recall items are easier than the guide in electron beams and brachytherapy radiobiology. Clinical-scenario items are 7% of the guide (33% in imaging) and almost absent from the site. Conclusions by area are in section c3.
- **Internal level labels** are a weak signal: each area splits about 25/50/25 into Easy, Moderate and Challenging, and 39% of the Challenging problems are recall or one-step.
- **Style.** The site passes its own ABR-style test (2,898 checks). The guide breaks those rules often (55 negative stems, 14 all-or-none options, about 20 combination items), so it is a content reference, not a format template.
- **Disagreements to verify.** Nine guide-against-site differences (section f1, plus a group of minor ones) and 28 further doubtful guide statements (f2); 43 guide questions carry a `verify` note in roecsg-audit-mapping.json. The strongest: the guide's key for the dominant kV interaction (Q162, Q174), the IMRT energy ordering against its own cited source (Q144), the electron range rule (Q137).
- **Top gaps in built topics (section e).** MR safety, PET and SPECT agents, PET against SPECT, FFF beams, protracted-dose BED, two-source equal activity, electron bolus and surface dose, broad-beam attenuation, lung edge effects, optical density, CT patient size, the exposure-to-dose f-factor, interaction frequency against contrast, electromagnetism vocabulary. One proposed question for each is in section g.
- **Since the snapshot.** See 'Status after the follow-up commits' below.
- **Independence from the guide.** No wording is shared (highest TF-IDF cosine between any site item and any guide question is 0.29). Two site scenarios share their givens with one guide item each (Appendix E).

## Status after the follow-up commits

The tables below describe the question bank at commit f0e32c8: 42 topics, 505 cards, 659 problems. Later commits on this branch added real clinical images to the imaging chapters and wrote new questions for the gaps found here. The site now has the same 505 cards and 714 problems. The 55 new problems were appended at the end of each topic, so no card or problem id changed. The numbers in the new worked examples and numeric problems are re-derived by another route in `tests/numbers16.py`, and every new Basic physics question has its "Explain further" text.

Closed, with the question ids on the site:

| Gap (guide questions) | What was added | Question ids |
|---|---|---|
| MR safety, field units (Q169, Q10) | A section "MRI safety" with a worked SAR example and a take-away; hazards by field, SAR, MR Safe, Conditional and Unsafe, pacemaker and ICD risks; a pacemaker scenario | `mri-physics:27` to `:33` |
| PET and SPECT agents by name (Q166) | A table of agents with scanner and target; a sort by scanner; a match of tracer to target | `spect:28`, `pet-imaging:34` |
| PET against SPECT (Q167) | Dual-isotope imaging; collimator against coincidence as the reason for the sensitivity | `spect:29`, `spect:30` |
| Interaction frequency against contrast (Q162, Q174) | A sort and a select-two question; a fourth bullet in the photon chapter | `radiographic-quality:31`, `photon-interactions:35` |
| Optical density and mAs (Q163) | Film density, distance scaling, digital overexposure, kVp against mAs | `radiographic-quality:32` to `:35` |
| CT image quality: patient size, metal (Q165) | Patient size and automatic exposure control; the real phantom noise as a question; streaks and a prosthesis scenario | `ct-quality:29` to `:32` |
| kV against MV cone-beam CT (Q174) | A paragraph on MV CBCT and a question | `ct-quality:33` |
| SUV with decay | The decay-corrected dose in the SUV formula | `pet-imaging:33` |
| Flattening-filter-free beams (Q121) | A section with a worked example and three questions | `profiles:30` to `:32` |
| BED with repair (Q190) | A section on continuous low dose rate irradiation with a worked example and two questions | `bed-tcp:27`, `:28` |
| Equal activity, chance of decay (Q189, Q29) | Two questions | `decay-law:32`, `:33` |
| Electron bolus, surface dose (Q62, Q137, Q139, Q141) | A section on bolus with a worked example; the surface-dose trend; three bolus questions | `electron-fields:29` to `:31`, `electron-pdd:28` |
| Broad beam, build-up (Q88) | The build-up formula and two questions | `photon-interactions:36`, `:37` |
| Lung edge effect (Q251) | One question on the edge of a lung tumour | `dose-algorithms:32` |
| Exposure to dose in a medium (Q93, Q97) | W and the f-factor in the text; two questions | `kerma-dose:30`, `:31` |
| 4D-CT and the ITV (Q151, Q182) | A real 4D-CT figure (two breathing phases, with the lung volume and the movement of the lung base measured on the volumes), a paragraph, and three questions | `icru-volumes:30` to `:32` |
| Electromagnetism and wave vocabulary (Q2, Q4, Q5, Q7, Q8, Q10, Q24) | A section "Electric field, potential, and current"; transverse and longitudinal waves; characteristic-line threshold | `charges-atom:23` to `:29`, `waves-photons:23` |
| Photon mass equivalent, elastic collisions (Q16, Q17) | One paragraph and three questions | `particles-energy:23` to `:25` |
| Forces, magic numbers (Q22, Q36) | One paragraph and two questions | `nuclear-structure:27`, `:28` |

Not changed: the unbuilt chapters (kV beams, linac, calibration, ultrasound, simulation, 4D-CT and motion management, CBCT workflow, MR simulation, special procedures, particles, SRS and SBRT, QA, protection, safety), which are all on the plan; the internal Easy, Moderate and Challenging labels; and the observation in section c2 about the position of the key in sorted numeric choices. Open items from the lists below: interface effects at lung (Q133), internal shield thickness (Q138, the guide's rule is approximate), IMRT energy against whole-body dose (Q143, Q144, settle the source first), ICRU objectives and ICRU 62 injury classes (Q148, Q158), dose in free space and TAR (Q94), the penumbra, output and off-axis items (Q119, Q122, Q126), nuclear reaction types (Q39), equal-effect prescription for I-125 and Pd-103 (Q191), and pulsed-dose-rate brachytherapy (Q195).

## Later review of wording and facts

After the questions above were written, all text on the site was read again against the house style and its facts were checked a second time. The review changed the wording of about 150 cards, problems and worked examples, removed purpose statements and filler from the chapters, and made every question and example stand on its own. It added, removed, or moved no card or problem, so every id in this document is still correct (505 cards, 714 problems).

Statements that were wrong, with the items that now carry the corrected text:

| Earlier statement | Corrected statement | Ids |
|---|---|---|
| A gradient larger than the system assumes compresses the MR image | It stretches it, because a point at x is placed at x G / G₀. The 5% example gives 210 mm, and the brain-slice simulation stretches the image | `mri-artifacts:7`, `:11`, `:16` |
| The chemical shift artifact is a shift at an interface | Fat protons precess about 3.5 ppm more slowly than water protons, so the fat signal is displaced along the frequency-encoding direction | `mri-artifacts:8` |
| Non-collinearity of the annihilation photons comes from momentum given to the nucleus | It comes from the net momentum of the positron and electron when they annihilate | `pet-imaging:9` |
| A positron travels 1 to 2 mm | For F-18 the mean range in water is about 0.6 mm and the maximum 2.4 mm; emitters with a higher positron energy travel farther | `pet-imaging:1` |
| The practical range of an electron beam is where the extended fall-off reaches zero | It is where the extended fall-off meets the bremsstrahlung tail | `electron-pdd:5`, `:25` |
| ICRU Report 38 recommends 0.07 mm as the skin depth | The ICRU recommends 0.07 mm; Report 38 covers gynecologic brachytherapy | `skin-bolus:1`, `:16` |
| Exposure at the skin is proportional to mA·kVp² | It is proportional to mAs·kVp² | `radiographic-quality:12` |
| The Paddick index is always below 1 | It lies between 0 and 1 and equals 1 for an ideal plan | `dvh-metrics:8` |
| Helium has zero spin | Helium-4 has zero spin; helium-3 has spin ½ | `mri-physics:5`, `:14` |
| Proton-rich isotopes decay by β⁺ | By β⁺ or electron capture, which needs only a positive decay energy | `spect:6`, `:15`, `decay-modes:17` |
| Specific activity with the half-life left in days is 86,400 times too small | It is 86,400 times too large | `specific-activity:13` |
| Cs-137 gives 850 photons of 662 keV per 1000 decays | 851, with 90.2% of Ba-137m transitions emitting a photon | `decay-schemes:17` |
| The FLAIR example nulled CSF at a T1 of 20 s | 4.23 s, from a corrected search for the null | the FLAIR paragraph of `mri-sequences` |

To confirm against a reference: the direction of the gradient scaling (first row). It follows from the system converting frequency to position with the gradient it assumes.

`tests/style.py` now also rejects the intensifiers "very" and "highly", colloquial words, purpose statements, references to another question, example, or chapter, a stem that starts with "The same", and exponent notation in answer options. A flash card shows its title and its fact, not the question written in the topic file, so the test scans the titles in `src/facts.py` as well.

## a. Method and limits

**What was compared.** I read every guide question with its explanation and every site topic: guide text, 505 cards (255 of them fact cards) and 659 problems (507 single-answer, 23 select-several, 47 sorting, 44 figure, 38 typed number), in 143 guide sections. A TF-IDF pass (unigram and bigram, scikit-learn) proposed candidate matches only. Of the 369 matches I cited (one site item can be cited for several questions), 238 (64%) were in the TF-IDF candidate lists, and 131 of the 161 matched questions had at least one cited item there: reading found matches that word overlap misses, and I rejected topical neighbours that did not test the concept.

**Definitions.**
- covered: the site's guide text teaches the point and at least one card or problem practises it, so a learner could answer the guide question from the site.
- partial: a text-only mention, or only part of what the guide question needs is practised.
- not covered: nothing on the point.
- planned: the concept belongs to a topic on the PLAN (src/syllabus.py, 67 unbuilt topics) or to a domain the site has not built. A gap on a built topic is unexpected.

**How level was judged.**
1. Each guide question and site item was typed: recall (R), conceptual (C), one-step calculation (1), multi-step calculation (M), figure (F), clinical scenario (SC), sorting (S) or typed number (T). Guide types come from reading all 277 questions. Site types come from a rule-based classifier run on all 1,164 items and checked against 45 hand-typed items: 80% agreement on the five classes and 96% on calculation against non-calculation. Site shares are therefore good to about 10 points.
2. For each covered or partial question a rank rule compared the guide item with the hardest matched site item (R 1, F 2, C 3, 1-step 3, SC 4, M 5; a gap of two or more gives harder or easier). I overrode the rule in 21 of the 128 cases that have a level verdict, after reading both items (level_why in roecsg-audit-mapping.json gives the reason).
3. The 70 matched pairs in section c3 were chosen and typed by hand. A pair verdict compares one guide item with one or two site items; the mapping's level_note compares the guide item with the hardest site item that tests the same concept.

**Limits.**
- No ABR item was available. Statements about the ABR exam rest on the blueprint (src/blueprint.py, transcribed from the ABR 2023 study guide), the item-writing rules in tests/abrstyle.py and the guide's own depth. The guide is a community source with 43 questions that I flagged, so it is a content reference, not an answer key.
- The guide parse is imperfect (Appendix A). Figures are not in the extracted text, so figure-based guide items (for example Q23, Q95, Q133, Q149) were judged from stem and explanation.
- The site's interactive viewers and MU calculator were not run; figure problems were read as text.
- The snapshot is not the current repository (see the status section).

## b. Coverage

### b1. By guide chapter

| Ch | Chapter | ABR | n | covered | partial | not covered | gap on a planned topic | gap on a built topic |
|---|---|---|---|---|---|---|---|---|
| 1 | Fundamental physics | I.A | 18 | 8 | 6 | 4 | 1 | 9 |
| 2 | Atomic and nuclear structure | I.B | 19 | 14 | 5 | 0 | 0 | 5 |
| 3 | Kilovoltage x-ray beams | I.C | 16 | 0 | 5 | 11 | 16 | 0 |
| 4 | Megavoltage beams (linac) | I.D | 18 | 2 | 4 | 12 | 15 | 1 |
| 5 | Radiation interactions | I.E | 13 | 6 | 3 | 4 | 5 | 2 |
| 6 | Radiation quantities and units | II.A | 9 | 6 | 3 | 0 | 1 | 2 |
| 7 | Measurement and calibration | II.B | 18 | 0 | 2 | 16 | 18 | 0 |
| 8 | Photon beam dosimetry | III.A | 16 | 11 | 5 | 0 | 0 | 5 |
| 9 | Electron beam dosimetry | III.B | 8 | 3 | 3 | 2 | 0 | 5 |
| 10 | IMRT | III.D | 5 | 3 | 2 | 0 | 1 | 1 |
| 11 | Prescribing, reporting, evaluating | III.C | 13 | 11 | 1 | 1 | 0 | 2 |
| 12 | Imaging fundamentals | IV.A | 10 | 2 | 5 | 3 | 2 | 6 |
| 13 | Simulation, motion, verification | IV.B | 14 | 1 | 1 | 12 | 13 | 0 |
| 14 | Clinical brachytherapy | V | 16 | 7 | 6 | 3 | 5 | 4 |
| 15 | Brachytherapy QA | V | 5 | 0 | 0 | 5 | 5 | 0 |
| 16 | Special procedures (TBI, TSET, IORT, RPT, ART, AI) | VI.A | 22 | 1 | 3 | 18 | 21 | 0 |
| 17 | Particle therapy | VI.B | 7 | 0 | 1 | 6 | 7 | 0 |
| 18 | SRS and SBRT | VI.C | 16 | 1 | 7 | 8 | 14 | 1 |
| 19 | Quality assurance | VII.A | 4 | 0 | 0 | 4 | 4 | 0 |
| 20 | Radiation protection and shielding | VII.B | 21 | 3 | 5 | 13 | 18 | 0 |
| 21 | Safety and incidents | VII.C | 9 | 0 | 1 | 8 | 9 | 0 |
|  | **All parsed questions** |  | 277 | 79 | 68 | 130 | 155 | 43 |

Chapters 3, 4, 7 and 16-21 have no built topic of their own (the few covered questions there are served by topics from other chapters, for example field-shaping for Q73), so almost every question there is a planned gap. Within built chapters the unexpected gaps cluster in chapter 1 (9 of 18), chapter 12 (6 of 10), chapter 2 (5 of 19), chapter 8 (5 of 16) and chapter 9 (5 of 8).

### b2. By ABR domain

| Domain | ABR weight | topics built | topics on PLAN | guide Qs | share of guide | covered | partial | not covered |
|---|---|---|---|---|---|---|---|---|
| I Basic physics | 11% to 13% | 10 | 13 | 84 | 30% | 30 | 23 | 31 |
| II Measurements | 9% to 11% | 1 | 11 | 27 | 10% | 6 | 5 | 16 |
| III Treatment planning | 19% to 21% | 19 | 0 | 42 | 15% | 28 | 11 | 3 |
| IV Imaging | 16% to 18% | 9 | 10 | 24 | 9% | 3 | 6 | 15 |
| V Brachytherapy | 12% to 14% | 3 | 6 | 21 | 8% | 7 | 6 | 8 |
| VI Special procedures | 15% to 17% | 0 | 13 | 45 | 16% | 2 | 11 | 32 |
| VII Safety and QA | 11% to 13% | 0 | 14 | 34 | 12% | 3 | 6 | 25 |

The guide puts 30% of its questions in domain I against a blueprint weight of 11% to 13%, and 9% in imaging against 16% to 18%. Gap counts per domain should not be read as exam weights.

### b3. Built topics that are thin relative to the guide

All 42 built topics are similar in size (8 to 17 cards, 13 to 27 problems), so thinness here means that the guide asks things the topic does not teach or practise. Full per-topic counts are in Appendix C. This table is the snapshot: since then mri-physics (Q169), radiographic-quality (Q162, Q163), ct-quality (Q165), spect and pet-imaging (Q166, Q167) have been extended (see the status section).

| Topic | guide Qs homed here | not fully covered | What is missing |
|---|---|---|---|
| `charges-atom` | 9 | 5: Q4, Q5, Q7, Q10, Q24 | units and properties of E and B fields, current and AC/DC; threshold logic for characteristic lines |
| `particles-energy` | 4 | 3: Q15, Q16, Q17 | relativistic-mass wording, mass equivalent of a photon's energy, elastic against inelastic collisions |
| `nuclear-structure` | 5 | 3: Q22, Q36, Q39 | ranking of forces, magic numbers, which processes are nuclear reactions |
| `electron-fields` | 5 | 4: Q62, Q138, Q140, Q141 | SSD to the bolus surface, shield thickness, oblique R90, omitting bolus |
| `electron-pdd` | 3 | 2: Q137, Q139 | range minus bolus; surface-dose trend with energy |
| `dose-algorithms` | 5 | 3: Q86, Q133, Q251 | heterogeneity coefficients, interface effects, lung SBRT correction |
| `radiographic-quality` | 2 | 2: Q162, Q163 | optical density and mAs; interaction share |
| `waves-photons` | 6 | 2: Q2, Q8 | transverse against longitudinal waves; W = qV |
| `decay-law` | 7 | 2: Q29, Q189 | 50% per half-life; two-source equality |
| `profiles` | 4 | 2: Q119, Q126 | penumbra across beam types; off-axis ratio |
| `mri-physics` | 1 | 1: Q169 | the whole MR safety topic |
| `pet-imaging`, `spect` | 1 each | Q166, Q167 | agents by name; PET against SPECT mechanism |
| `ct-quality` | 1 | Q165 | patient size and dose |
| `bed-tcp` | 1 | Q190 | repair and time term for protracted irradiation |
| ten other topics | 1 to 9 | one each: Q121, Q122, Q94, Q93, Q88, Q148, Q158, Q144, Q195, Q191 | single concepts (see section e) |

### b4. Built topics that go beyond the guide

`wedges`, `image-data` and `mri-artifacts` have no guide question. `decay-schemes`, `specific-activity`, `equilibrium`, `multifield`, `field-shaping`, `electron-mu`, `inverse-planning`, `imrt-delivery`, `ct-reconstruction`, `mri-sequences` and `bed-tcp` have one each, and `mu-calc` and `pdd` have two. For these the guide cannot show whether the site is complete, only that the site is deeper than the guide. Sixteen PLAN topics also have no guide question (Appendix D).

## c. Level analysis

### c1. Question types: guide against site

Shares in percent of items in each area. Guide: all parsed questions in chapters that have a built topic. Site problems: practice questions only. Site all items: cards plus problems. 1-step and multi are calculation items; fig/scen is figure plus clinical scenario for the guide, figure plus sorting for the site. Site types are heuristic (about 10 points).

| Area | guide n | R | C | 1-step | multi | fig/scen | site problems n | R | C | 1-step | multi | fig/sort | site all items n | R | C | calc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A basic physics and radioactivity | 37 | 57 | 19 | 16 | 5 | 3 | 134 | 34 | 14 | 30 | 12 | 10 | 224 | 40 | 22 | 31 |
| B interactions and quantities | 22 | 41 | 50 | 5 | 0 | 5 | 38 | 24 | 8 | 21 | 24 | 24 | 63 | 33 | 19 | 33 |
| C photon beam dosimetry and MU | 16 | 19 | 38 | 19 | 19 | 6 | 168 | 26 | 23 | 21 | 18 | 12 | 295 | 41 | 25 | 26 |
| D electron beams | 8 | 0 | 38 | 12 | 38 | 12 | 44 | 25 | 30 | 27 | 5 | 14 | 80 | 59 | 16 | 18 |
| E plan evaluation and IMRT | 18 | 56 | 33 | 0 | 0 | 11 | 89 | 34 | 19 | 27 | 7 | 13 | 164 | 63 | 11 | 18 |
| F imaging | 24 | 33 | 33 | 0 | 0 | 33 | 137 | 40 | 20 | 23 | 4 | 13 | 248 | 66 | 12 | 15 |
| G brachytherapy | 21 | 67 | 24 | 5 | 5 | 0 | 49 | 29 | 16 | 20 | 12 | 22 | 90 | 46 | 24 | 18 |
| **All built areas** | 146 | 45 | 32 | 8 | 6 | 10 | 659 | 31 | 19 | 24 | 12 | 14 | 1164 | 50 | 19 | 23 |
| unbuilt guide chapters (3, 4, 7, 16-21) | 131 | 62 | 22 | 2 | 2 | 12 | - | - | - | - | - | - | - | - | - | - |

Reading the table:
- The guide in built areas is 45% recall, 32% conceptual, 14% calculation (8% one-step, 6% multi-step), 3% figure and 6% scenario. Over all 277 questions it is 53% recall, 27% conceptual, 9% calculation, 7% scenario.
- The site's problems are 31% recall, 19% conceptual, 36% calculation (24% one-step, 12% multi-step), 7% figure and 7% sorting. The cards are 75% recall, 19% conceptual and 6% one-step calculation, so counting cards pulls the site toward recall (all items: 50% recall, 16% one-step and 7% multi-step).
- By area, the site's problems are most calculation-heavy in B (45%), A (42%) and C (39%) and least in F (27%), D and G (32% each). The guide is most calculation-heavy in D (50%) and C (38%), where half or more of its calculation items are multi-step; in D the guide asks more of each item than the site does.
- The guide has 20 clinical-scenario items (7%): 8 of 24 in imaging, 8 of 22 in chapter 16 and a few elsewhere. At most a handful of the site's problems are written as a clinical situation (for example wedges:21, tg43:24); I counted none as a scenario item for the shares above.

### c2. Format and the ABR select-several rules

Rules enforced by tests/abrstyle.py (status at the snapshot: PASS, 2,898 checks):
- A select-several stem names the number it wants ("Which three of these ...") and ends with "(Please select N options.)".
- At least twice as many options as correct answers (the site uses six options for three correct answers, or four or five for two).
- No repeated options.
- No negative stem: NOT, EXCEPT, FALSE, INCORRECT or LEAST in capitals, or "not true", "not correct", "which of the following is false".
- No "all of the above" or "none of the above" option.
- At least 20 select-several problems overall; the site has 23 (19 with six options and three answers, 3 with four options and two answers, 1 with five options and two answers), 3.5% of its problems.

The guide does not follow these rules: 55 of 277 stems (20%) ask for the false, not, except or least option (counted by regular expression, then 5 false positives removed by hand); 6 offer "all of the above" and 8 offer "none" among combination options (14 items, 5%); about 20 items (7%) use numbered statements with combination or ordering options. In four-option items the key is A in 33% of cases, and in five-option items it is E in 38%. So the guide is usable for what to test, not for how to word it.

Side finding on the site: in the 199 single-answer problems whose numeric options are sorted ascending, the correct option is B or C in 76% (A 10%, D 14%); in the other 308 single-answer problems the key is spread evenly (A 25%, B 26%, C 27%, D 22%). A test-wise learner can discard the extreme values. src/blocks.py places the correct value by a hash of the stem "whenever the kept traps allow it"; the kept traps appear to force the middle. Allowing the correct value at either end more often would remove the cue.

### c3. Matched pairs and conclusions by area

70 pairs, 8 to 12 per area. Types: R recall, C conceptual, 1 one-step calculation, M multi-step calculation, F figure, S sorting, SC clinical scenario, T typed number. Levels are the site's internal labels (E Easy, Mo Moderate, Ch Challenging; card = flashcard). Item ids refer to the snapshot; problems added later are listed in the status section. Guide items are described in my words and without their numbers. Pair verdicts below compare items; at concept level, for the 128 guide questions that have a level verdict in roecsg-audit-mapping.json, the site is harder for 26, similar for 84 and easier for 18.

| Area | pairs | site harder | similar | site easier |
|---|---|---|---|---|
| A. Basic physics and radioactivity | 11 | 4 | 4 | 3 |
| B. Interactions and quantities | 9 | 1 | 8 | 0 |
| C. Photon beam dosimetry and monitor units | 12 | 2 | 7 | 3 |
| D. Electron beams | 8 | 1 | 5 | 2 |
| E. Plan evaluation and IMRT | 11 | 1 | 8 | 2 |
| F. Imaging | 9 | 2 | 6 | 1 |
| G. Brachytherapy | 10 | 1 | 7 | 2 |
| **All** | 70 | 12 | 45 | 13 |

#### A. Basic physics and radioactivity (guide ch1-2; site topics waves-photons, particles-energy, charges-atom, nuclear-structure, decay-modes, decay-schemes, decay-law, specific-activity, equilibrium)

| Guide Q (type) | Site item (type, level) | Verdict | What differs |
|---|---|---|---|
| Q3 (C) | waves-photons:16 (1, Mo); waves-photons:19 (C, Mo) | site harder | Guide: pick the true direction of change of photon energy with wavelength. Site: halving the wavelength doubles E, and doubling intensity changes photon number, not photon energy. |
| Q6 (C, negative stem) | charges-atom:10 (R, E); charges-atom:14 (1, Mo) | site harder | Same law. Guide: which stated property is false. Site: distance doubled gives one quarter (:10, same depth) and the force between two protons at 2.0 fm, 57.7 N (:14). |
| Q11 (C) | charges-atom:11 (R, E); charges-atom:20 (M, Ch) | site harder | Same fact (circular path, no energy change). :20 asks the radius for a 6 MeV electron with relativistic momentum, 10.8 cm against 4.1 cm classical. |
| Q16 (1) | particles-energy:14 (1, Mo) | similar | Both convert between mass and energy. The guide item concerns the mass equivalent of a photon's energy and is itself doubtful (section f). |
| Q22 (R) | nuclear-structure:13 (R, E) | site easier | Guide: rank all four fundamental forces. Site: which force binds protons against Coulomb repulsion; no ranking that includes gravity and the weak force. |
| Q24 (M) | charges-atom:17 (1, Mo) | site easier | Guide: decide which characteristic lines an electron of a stated energy can excite from three binding energies (K threshold first, then each transition). Site: one L to K difference, 59.3 keV. |
| Q29 (C) | decay-law:1 (card); decay-law:16 (R, E) | site easier | The statement that a nucleus has a 50% chance of decaying in one half-life is implied by the card on lambda but never posed. Site asks the fraction left after 5 half-lives. |
| Q30 (1) | decay-law:27 (1, Ch) | similar | Mean life and half-life, opposite direction. The site's Challenging label overstates a one-step item. |
| Q32 (1) | decay-law:18 (M, Mo); decay-law:21 (1, Mo) | site harder | Guide: choose the correct exponential expression. Site: evaluate it (Tc-99m 925 MBq after 6.5 h gives 437 MBq) or find T1/2 from two activities. |
| Q34 (M) | specific-activity:24 (T, Mo); specific-activity:16 (R, Mo) | similar | Same chain: lambda from T1/2, atoms per gram, conversion to Ci. The site uses a hypothetical nuclide, so the result cannot be recalled. |
| Q38 (C) | equilibrium:21 (C, Ch); equilibrium:15 and :22 (1, Mo and Ch) | similar | Same concept. The site states the transient ratio Tp/(Tp - Td) correctly (the guide's wording does not, section f) and adds the time of peak daughter activity, which the guide does not ask. |

**Conclusion for A.** Appropriate for decay and activity (decay-law:16-19, :21, :22 against Q30-Q33; charges-atom:10-11 against Q6 and Q11; equilibrium:21 against Q38; specific-activity:24 against Q34). Heavier than the guide on relativistic and atomic-mass arithmetic, lighter on vocabulary.
- Too easy: nuclear-structure:12 (neutron count from A and Z), decay-law:15 (mCi and GBq conversion), specific-activity:9 and :10 (definition and unit), decay-law:27 (one step, labelled Challenging).
- Too hard, or beyond anything in the guide: charges-atom:20 (relativistic path radius), particles-energy:20 and :22 (proton speed from kinetic energy; pair production with kinetic energies), waves-photons:22 (matter-wave comparison), nuclear-structure:22 (binding energy per nucleon from six-decimal masses), equilibrium:15 and :22 (time of peak daughter activity). They are valid physics. I cannot say from the guide whether the ABR asks them; keep a few as stretch items.
- Missing recall the guide tests: units and properties of electric and magnetic fields, current and AC/DC (Q4, Q5, Q7, Q10), transverse against longitudinal waves (Q2), ranking of forces (Q22), the 50% statement (Q29).

#### B. Interactions and quantities (guide ch5-6; site topics photon-interactions, kerma-dose)

| Guide Q (type) | Site item (type, level) | Verdict | What differs |
|---|---|---|---|
| Q76 (C, patient wrapper) | photon-interactions:8 (card); photon-interactions:24 (C select-three, Ch) | similar | Same concept: Compton scattering per electron does not depend on Z. The site's select-three adds angle and threshold properties. |
| Q77 (C, patient wrapper) | photon-interactions:13 (card); mlc-imrt:3 (card) | similar | Photoneutron production at 10 MV and above. The site has cards only, no problem. |
| Q83 (R) | photon-interactions:15 (R, E) | similar | Choose the attenuation equation. |
| Q84 (1) | photon-interactions:5 (card); photon-interactions:32 (F, Mo) | similar | Fraction left after n half-value layers. The site's figure item reads the 12.5% level off a curve. |
| Q85 (C) | photon-interactions:6 (card) | similar | HVL grows with depth in a polyenergetic beam; card only, no problem. |
| Q90 (R) | kerma-dose:1 (card); kerma-dose:14 (M, Mo) | site harder | Guide: definition of energy fluence. Site: compute it from fluence and photon energy with the MeV to joule conversion (0.601 J/m2). |
| Q91 (R) | kerma-dose:7 (card); kerma-dose:27 (S, E) | similar | SI unit of exposure. The site adds the 3 MeV limit (kerma-dose:24). |
| Q92 (C, negative stem) | kerma-dose:19 (C, E); kerma-dose:5 (card) | similar | Dose against collision kerma in build-up. The site never asks how the radiative fraction makes total kerma exceed dose as energy rises. |
| Q93 and Q97 (R, C) | kerma-dose:9 (card); kerma-dose:23 (M, Mo) | similar | The site computes dose to air from exposure (0.876 cGy/R) but never defines W as energy per ion pair and stops before the f-factor for a medium. |

**Conclusion for B.** Appropriate, with a calculation emphasis (24% of the area's problems are multi-step, mostly table look-ups). Fine: photon-interactions:15, :20, :24, :25 and kerma-dose:13, :19, :27 against Q76-Q85 and Q89-Q96.
- Too easy: kerma-dose:22 (1 Gy = 100 cGy), kerma-dose:13.
- Too hard: none. The NIST-table items (photon-interactions:18, :19, :26, :29) take two to three minutes and use data printed with the question.
- Gaps: narrow against broad beam (Q88), tissue heterogeneity coefficients (Q86), W and the f-factor (Q93, Q97).

#### C. Photon beam dosimetry and monitor units (guide ch8; site topics pdd, tmr, scatter, mu-calc, profiles, skin-bolus, dose-algorithms, multifield, wedges, field-shaping)

| Guide Q (type) | Site item (type, level) | Verdict | What differs |
|---|---|---|---|
| Q117 (1) | brachy-exposure:22 (R, Mo); brachy-exposure:26 (1, Ch) | similar | Both are one inverse-square ratio. The guide sets it in a kV skin set-up error; the site has no kV example. :26 is labelled Challenging but is one step. |
| Q118 (R) | profiles:4 (card); profiles:15 (C, E) | similar | Geometric penumbra comes from source size. The site adds the formula and its dependences (profiles:5, :26). |
| Q119 (C) | profiles:7 (card); profiles:18 (C, Mo) | similar | The site compares 6 and 18 MV and lung; it has no kV or electron comparison. See section f for the guide's reasoning. |
| Q123 (R) | pdd:8 (card); pdd:22 (M, Mo); pdd:23 (M, Ch) | site harder | Guide: what the Mayneord factor does. Site: compute F and the new PDD (70.0% at SSD 140 cm; a reduced-SSD case in :23). |
| Q124 (C) | tmr:7 (card); tmr:14 (R, E) | site easier | Guide: choose the backscatter factor for scatter at the surface of a kV skin field from four ratios. Site: define TAR and BSF and state TMR at dmax; no kV scenario. |
| Q125 (M) | tmr:9 (card); tmr:19 (M, Mo); tmr:23 (M, Ch) | similar | Same PDD to TMR conversion with the inverse-square factor. The site adds a check that SSD-120 data give the same TMR (tmr:23). The givens coincide with tmr:9 (Appendix E). |
| Q126 (C, negative stem) | profiles:23 (R, Ch); wedges:25 (F, Mo) | similar | Off-axis ratio appears as a table row in mu-calc and in profile items; no item defines it or states that a wedge changes it. |
| Q128 (1) | scatter:6 (card); scatter:22 (1, Mo); scatter:29 (T, Mo) | similar | Equivalent square by 2ab/(a + b). The site uses more elongated fields (6 x 18, 8 x 20, 12 x 30). |
| Q129 (M) | mu-calc:7 (card); mu-calc:34 (M, Ch) | site harder | Guide: extended-SSD MU with an inverse-square factor and a unit output. Site: adds Sc at the collimator opening, Sp, a Mayneord-corrected PDD and the calibration convention. |
| Q130 (M) | multifield:15 (1, Mo) | site easier | Guide: surface, maximum and midplane dose of a parallel-opposed pair from PDD data. Site: the hot-spot ratio from three PDD values. |
| Q132 (1) | dose-algorithms:20 (1, Mo); dose-algorithms:30 (T, Mo) | similar | Radiological depth is the sum of density times thickness. The site uses three layers and then compares TMR at radiological and physical depth (:24, Ch). |
| Q133 (F) | dose-algorithms:26 (C, Mo) | site easier | Guide: dose change at four points around a lung slab, both interfaces. Site: the dose beyond the slab only; build-down and re-build-up at the interfaces are not taught. |

**Conclusion for C.** Appropriate to slightly hard, and the best-covered area. Fine: pdd:8-9 and :22 against Q123; tmr:9 and :19 against Q125; scatter:6 and :22 against Q128; dose-algorithms:20 against Q132.
- Too easy: tmr:14 (TMR at dmax is 1) and pdd:14 (dmax of 6 MV) are single-number recalls.
- Too hard, or beyond the guide: mu-calc:28, :33, :38 (four to six factors from two tables), scatter:24 and :25 (interpolation in a table), dose-algorithms:24 (ratio of TMRs along radiological and physical path). They are realistic physicist tasks; the guide's MU items need one factor. Keep a few as capstones.
- Gaps: flattening-filter-free beams (Q121), interface effects at lung (Q133, Q251), penumbra across beam types (Q119), off-axis ratio (Q126).

#### D. Electron beams (guide ch9; site topics electron-pdd, electron-fields, electron-mu)

| Guide Q (type) | Site item (type, level) | Verdict | What differs |
|---|---|---|---|
| Q134.2 (R, unparsed item) | electron-pdd:5 (card); electron-pdd:14 (1, E) | similar | Practical range; Rp = E/2 gives 6 cm for 12 MeV. |
| Q135 (F) | electron-pdd:3 (card); electron-pdd:15 (R, E); electron-pdd:21 (C select-three, Mo) | similar | Dose beyond the electron range is bremsstrahlung. The site adds size, origin and energy dependence. |
| Q136 (1) | electron-mu:16 (1, Mo); electron-mu:24 (T, Mo) | site harder | Guide: prescription at the normalisation point, so MU equals the dose. Site: divide by the PDD at the prescription depth and by the output factor. |
| Q137 (M) | electron-pdd:6 (card); electron-pdd:16 (1, Mo) | site easier | Guide: apply a range rule, then subtract the bolus thickness. Site: R90 of a bare beam. The two sources also use different rules (section f). |
| Q138 (M) | electron-fields:13 (card) | site easier | Guide: choose a shield thickness from the energy left at the shield. Site: one card (3 mm tungsten with 1 mm aluminium, adequate to 8 MeV). |
| Q140 (C) | electron-fields:11 (card); electron-fields:18 (C, Mo) | similar | Oblique incidence moves dmax toward the surface. The guide also asks about the change in R90. |
| Q142 (C) | electron-fields:13 (card); electron-fields:23 (R, Ch) | similar | A low-Z layer absorbs backscatter from a high-Z shield. The site's :23 is labelled Challenging but is a recall of that fact. |
| Q62 (R) | electron-fields:4 (card) | similar | Standard cone set-up (SSD 100 cm, cone end 95 cm). The convention that SSD is measured to the bolus surface is not stated. |

**Conclusion for D.** Easier than the guide where the guide is hardest, and the least varied area. All 36 electron cards are recall, and the problems are one-step arithmetic (electron-pdd:14, :16; electron-mu:16, :24). Three of the guide's eight electron questions are multi-step (Q137, Q138, Q141, all rule-of-thumb arithmetic with bolus or shields); two of the site's 44 electron problems are.
- Fine: electron-mu:16 and :24 against Q136 (the site is harder: PDD and output factor).
- Too easy: electron-fields:23 (labelled Challenging, one recalled fact), electron-pdd:14.
- Missing: bolus and range (Q62, Q137, Q141), surface-dose trend with energy (Q139), shield thickness (Q138).

#### E. Plan evaluation and IMRT (guide ch10-11; site topics icru-volumes, dvh-metrics, bed-tcp, inverse-planning, imrt-delivery, mlc-imrt)

| Guide Q (type) | Site item (type, level) | Verdict | What differs |
|---|---|---|---|
| Q143 (C) | mlc-imrt:15 (C, E); mlc-imrt:2 and :3 (cards) | similar | Why IMRT uses 6 to 10 MV: neutrons and leakage grow with MU. The guide's keyed option bundles extra claims (section f). |
| Q144 (C, ordering) | mlc-imrt:2 and :3 (cards) | site easier | The principle is on cards, but the comparison of techniques by low-dose volume or whole-body dose is never posed. The guide's source for the ordering is disputed (section f). |
| Q146 (R) | inverse-planning:2 (card); inverse-planning:14 (C, E) | similar | Definition. The site goes further with cost-function arithmetic (inverse-planning:20, :22, :25), which the guide does not ask. |
| Q150 (SC) | icru-volumes:2 (card); icru-volumes:27 (S, Mo) | site easier | Guide: which volume is contoured after a complete response (lymphoma scenario). Site: define each volume. |
| Q151 (C) | icru-volumes:3 (card); icru-volumes:27 (S, Mo) | similar | ITV from CTVs drawn on several breathing phases. The site defines the ITV but never mentions 4D-CT. |
| Q152 to Q154 (R) | icru-volumes:4 to :6 (cards); icru-volumes:15 and :16 (R, E) | similar | PTV, treated volume and irradiated volume. The guide asks them from a figure or a scenario, the site in words. |
| Q155 (R) | dvh-metrics:5 (card) | similar | D2% as the near-maximum dose (ICRU 83). |
| Q157 (R) | dvh-metrics:6 (card); dvh-metrics:18 (1, Mo); dvh-metrics:20 (M, Ch) | site harder | Guide: definition of the conformity index. Site: calculate CI (1.50) and the Paddick index (0.581). |
| Q158 (C, combination) | dvh-metrics:10 (card); dvh-metrics:23 (S, Mo) | similar | Serial and parallel organs. ICRU 62 injury classes are not taught. |
| Q159 (R) | dvh-metrics:4 (card); dvh-metrics:16 (R, Mo) | similar | Meaning of Vx Gy on a cumulative DVH. |
| Q160 (C) | dvh-metrics:12 (card); dvh-metrics:21 (C, Ch) | similar | A DVH carries no spatial information. The guide adds anatomy change and biology. |

**Conclusion for E.** Fine on volumes and DVH metrics (icru-volumes:15, :16, :27; dvh-metrics:4, :16, :23 against Q152-Q154, Q158, Q159). IMRT-delivery arithmetic goes beyond the guide, and scenario items are absent.
- Too easy: icru-volumes:15 and :16 (Easy definitions; the guide asks the same volumes from a figure or a scenario).
- Too hard, or beyond the guide: inverse-planning:20, :22, :25 (cost-function arithmetic), mlc-imrt:21, :22, :26, :27 (sliding-window MU algebra), imrt-delivery:24 (largest MU of a VMAT arc), dvh-metrics:20 (Paddick index). Useful for understanding, doubtful as exam-depth.
- Gaps: technique comparison by whole-body dose (Q144, source disputed), ICRU 62 injury classes (Q158), ICRU objectives (Q148).

#### F. Imaging (guide ch12-13; site topics radiographic-quality, image-data, ct-reconstruction, ct-quality, mri-physics, mri-sequences, mri-artifacts, spect, pet-imaging)

| Guide Q (type) | Site item (type, level) | Verdict | What differs |
|---|---|---|---|
| Q162 (C) | photon-interactions:20 (R, E); radiographic-quality:15 (C, E) | similar | Both concern which interaction matters in the kV range. The site separates frequency (Compton above about 30 keV) from contrast (photoelectric, Z cubed); the guide's key does not (section f). |
| Q163 (R) | radiographic-quality:12 (card); radiographic-quality:23 (C, Mo); radiographic-quality:25 (R, Ch) | site harder | Guide: mAs sets optical density. Site: never mentions density; it scales exposure with mA and kVp squared and SNR with mAs. |
| Q164 (C, negative stem) | ct-reconstruction:6, :7, :10 (cards); :15 and :16 (1, Mo); :21 (1, Ch); :26 (T, Mo) | site harder | Guide: statements about HU (air, water, affine definition). Site: compute HU from mu and mu from HU. |
| Q165 (C, negative stem) | ct-quality:5, :6, :12 (cards); ct-quality:16 (R, E) | site easier | Guide: what determines CT image quality (focal spot, dose, metal, patient size). Site: single facts (mA changes noise, not resolution); no patient-size or dose-noise item. |
| Q166 (R) | pet-imaging:30 (S, Mo); spect:2 and :5 (cards) | similar | Guide: recognise agents by name. Site: sorts five PET tracers by process; no Ga-68 agent and no SPECT agent in any problem. |
| Q167 (C) | spect:20 (C, Mo); spect:12 and pet-imaging:6 (cards) | similar | PET against SPECT. The site states sensitivity, quantification and resolution but not the collimator-versus-coincidence reason, SPECT resolution or dual-isotope imaging. |
| Q168 (R) | mri-sequences:2 and :7 (cards); mri-sequences:21 (R, Mo) | similar | Guide: T1, T2, TE, TR vocabulary. Site: the cards define TR and TE and :21 takes the next step (which TR and TE pair gives T2 weighting); both are recall-level. |
| Q174 (C, negative stem) | ct-quality:23 (C, Ch) | similar | Guide: kV against MV CBCT. Site: why CBCT is worse than diagnostic CT (scatter). No kV-MV comparison. |
| Q185 (C) | icru-volumes:3 (card); icru-volumes:18 (C, Mo) | similar | Guide: widen margins when motion cannot be controlled. Site: ITV definition and the margin recipe (2.5 Sigma + 0.7 sigma) with systematic against random error. |

**Conclusion for F.** Right depth for CT, MR and PET physics; the clinical-workflow half is missing. Fine: ct-reconstruction:15-16, :21, :26 against Q164; mri-sequences:21 against Q168; pet-imaging:22-24 and :31 (SUV, attenuation correction) go beyond the guide's PET item. Eight of the guide's 24 imaging questions are clinical scenarios (technique selection for a patient); the site has none in this area.
- Too easy: image-data:16-19 (bit, byte, DICOM, grey levels), mri-physics:14 (helium-4 has zero spin), spect:13 (definition of a radiopharmaceutical).
- Too hard: none clearly; mri-artifacts:17 (field uniformity in ppm for a 0.1 mm shift) and mri-physics:21 are specialised.
- Missing: see section d.

#### G. Brachytherapy (guide ch14-15; site topics brachy-sources, brachy-exposure, tg43, with bed-tcp and decay-law)

| Guide Q (type) | Site item (type, level) | Verdict | What differs |
|---|---|---|---|
| Q186 (R) | brachy-sources:5 (card); brachy-sources:15 (R, E) | similar | Ir-192 half-life. The site also uses it in calculations (decay-law:19). |
| Q187 (1) | decay-law:28 (T, Mo); decay-law:19 (M, Mo) | similar | Same decay calculation; decay-law:28 uses the same isotope and elapsed time as the guide item and reports percent remaining (Appendix E). |
| Q188 (R) | brachy-exposure:8 (card); tg43:15 (R, E); brachy-exposure:24 (C, Ch) | site harder | Guide: air kerma strength is the recommended quantity. Site: also asks why seeds are ordered by SK rather than by activity. |
| Q189 (M) | decay-law:8 (card); decay-law:22 (1, Mo) | site easier | Guide: time at which two decaying sources have equal activity (two exponentials). Site: time for one source to reach a stated activity. |
| Q190 (C, combination) | bed-tcp:3 and :4 (cards); bed-tcp:18 (1, Mo) | site easier | Guide: determinants of BED for LDR and HDR, including repair and time. Site: the acute formula and EQD2; no repair or dose-rate term for continuous irradiation. |
| Q191 (C) | brachy-sources:20 (C, Mo); tg43:14 (card) | similar | I-125 against Pd-103. Site: starting dose rate for an equal total dose; guide: prescription dose for equal biological effect. |
| Q192 (R) | tg43:1 and :3 (cards) | similar | TG-43 as the formalism; the site goes on to the full dose-rate equation. |
| Q193 (C) | tg43:9 (card); tg43:19 (R, Mo) | similar | g(r) falls faster for low-energy sources. |
| Q194 (C) | tg43:10 (card); tg43:21 (M, Mo) | similar | Guide: where the anisotropy function is lowest. Site: the card states it, and tg43:21 also uses F in a dose-rate calculation (0.368 cGy/h), an extension. |
| Q196 (R) | brachy-sources:10 (card); brachy-sources:21 (C select-three, Mo) | similar | Purpose of a remote afterloader; the site adds other HDR facts in a select-three item. |

**Conclusion for G.** Appropriate. Fine: brachy-sources:18, :20; tg43:9, :10, :15, :19; brachy-exposure:8, :18 against Q186-Q194. Brachytherapy radiobiology is the thin spot, and clinical brachytherapy (guide 14.5-14.7) and brachytherapy QA (ch15) are unbuilt.
- Too easy: brachy-sources:14-16 (HDR threshold, Ir-192 in afterloaders, permanent implants), tg43:15.
- Too hard, or beyond the guide: tg43:25 and :29 (full TG-43 dose rate with a line-source geometry ratio), tg43:21.
- Gaps: BED with repair (Q190), equal-effect prescription (Q191), pulsed-dose-rate (Q195), two-source equal activity (Q189).


**Overall.** Where the site is harder than the guide it is mostly through added arithmetic: tables, unit conversions, extra factors. A handful of problems need derivations the guide never asks for: relativistic momentum (charges-atom:20), binding energy per nucleon from atomic masses (nuclear-structure:22), the time of peak daughter activity (equilibrium:15, :22) and a gradient tolerance in ppm (mri-artifacts:17). The site is easier than the guide where the guide combines rules of thumb (electrons, brachytherapy radiobiology) and where it sets physics inside a clinical situation (imaging, ICRU volumes). Whether the site's arithmetic-heavy items match the ABR depth cannot be settled from the guide; the safest reading is that they are above the guide's depth and should not take the place of the missing recall and scenario items.

### c4. The internal level labels

The 659 problems are 24% Easy, 51% Moderate and 25% Challenging, and every area lies within 20% to 34% Easy and 16% to 30% Challenging. Among the Challenging problems, 39% are recall or one-step (for example decay-law:27, electron-fields:23, profiles:23). The labels look assigned to fit a distribution, not measured. Use them for ordering, not as evidence of difficulty.

## d. The imaging domain in detail

### d1. Every guide concept in chapters 12 and 13

Chapter 12 has 10 questions (2 covered, 5 partial, 3 not covered) and chapter 13 has 14 (1 covered, 1 partial, 12 not covered). Of the 21 gaps, 15 are on PLAN topics and 6 are unplanned (Q162, Q163, Q165, Q166, Q167, Q169).

| Guide Q | Concept | Site at snapshot | Nearest site items | Home (built topic, or PLAN title) | At 19:35 |
|---|---|---|---|---|---|
| Q162 | dominant photon interaction in diagnostic radiography (photoelectric versus Compton) | partial | `photon-interactions:7`; `photon-interactions:20`; `radiographic-quality:15` | `radiographic-quality` | covered (new items) |
| Q163 | which acquisition parameter sets radiograph density | partial | `radiographic-quality:12`; `radiographic-quality:23`; `radiographic-quality:25` | `radiographic-quality` | covered (new items) |
| Q164 | Hounsfield-unit definition, reference values and use in dose calculation | covered | `ct-reconstruction:6`; `ct-reconstruction:7`; `ct-reconstruction:10` | `ct-reconstruction` | unchanged |
| Q165 | determinants of CT image quality | partial | `ct-quality:5`; `ct-quality:6`; `ct-quality:12` | `ct-quality` | covered (new items) |
| Q166 | recognising PET and SPECT radiopharmaceuticals by name (includes Ga-68 agents) | partial | `pet-imaging:30`; `spect:2`; `spect:5` | `pet-imaging` | covered (new items) |
| Q167 | PET versus SPECT comparison | partial | `spect:20`; `spect:12`; `pet-imaging:6` | `spect` | covered (new items) |
| Q168 | MRI vocabulary: relaxation times and sequence timings | covered | `mri-sequences:2`; `mri-sequences:7`; `mri-sequences:21` | `mri-sequences` | unchanged |
| Q169 | MRI hazards for cardiac implantable devices | not covered | `mri-artifacts:10` | `mri-physics` | covered (new items) |
| Q170 | physical basis of ultrasound imaging | not covered (planned) | none | Ultrasound physics | unchanged |
| Q171 | transducer material in diagnostic ultrasound | not covered (planned) | none | Ultrasound physics | unchanged |
| Q172 | what happens at simulation versus on the treatment unit | not covered (planned) | none | CT simulation and image registration | unchanged |
| Q173 | properties of MR simulation | not covered (planned) | none | PET and MRI in treatment planning | unchanged |
| Q174 | kV versus MV cone-beam CT: contrast, dose, metal artifacts, dominant interaction | partial (planned) | `ct-quality:23`; `radiographic-quality:15`; `photon-interactions:25` | CBCT and image-guided shifts | covered (new items) |
| Q175 | strategies when the CBCT does not match the planning CT | not covered (planned) | none | CBCT and image-guided shifts | unchanged |
| Q176 | purpose of motion management | not covered (planned) | none | 4DCT and motion management | unchanged |
| Q177 | abdominal compression for motion management | not covered (planned) | none | 4DCT and motion management | unchanged |
| Q178 | technique choice to protect the heart in left-sided breast treatment | not covered (planned) | none | 4DCT and motion management | unchanged |
| Q179 | method choice for irregular breathing | not covered (planned) | none | 4DCT and motion management | unchanged |
| Q180 | main limitation of voluntary breath-hold | not covered (planned) | none | 4DCT and motion management | unchanged |
| Q181 | technique choice for a patient anxious about gating | not covered (planned) | none | 4DCT and motion management | unchanged |
| Q182 | purpose of 4D-CT | not covered (planned) | `icru-volumes:3` | 4DCT and motion management | unchanged |
| Q183 | strategy for intrafraction prostate motion | not covered (planned) | none | Surface guidance and tracking | unchanged |
| Q184 | gating versus tracking: when each is preferred | not covered (planned) | none | 4DCT and motion management | unchanged |
| Q185 | expanding margins to cover motion when no motion-control tool is available | covered | `icru-volumes:3`; `icru-volumes:11`; `icru-volumes:18` | `icru-volumes` | unchanged |

### d2. Weak or missing site items, by focus area

**PET against SPECT.**
- Site has: spect:12 (card) and spect:20 (problem) state that PET has higher sensitivity, quantification and often higher resolution; pet-imaging:6 (511 keV window), pet-imaging:7 (resolution 4 to 5 mm); spect:7-11 (gamma camera, collimator, SPECT-CT); spect:19 (isotope choice by half-life).
- Weak or missing: the reason for the sensitivity difference (electronic coincidence against an absorbing collimator); a SPECT resolution figure, so 'often higher' cannot be quantified; dual-isotope SPECT against PET's inability to separate two positron emitters; attenuation and scatter correction in SPECT; time of flight. One problem and one card only. The site has the resolution comparison the right way round (PET finer).
- Live update (19:35): spect:29 and new guide text cover dual-isotope imaging (SPECT separates two isotopes by energy window, PET cannot) and spect:28 sorts agents by scanner. The collimator-against-coincidence reason and a SPECT resolution figure are still missing.

**PET and SPECT radiopharmaceuticals.**
- Site has: PET FDG, fluoride, FMISO, 13N-ammonia, 15O-water (pet-imaging:14, :15, :30) and 11C-flumazenil and 11C-raclopride in text; SPECT 99mTc (sestamibi, MDP), 123I, 131I, 111In, 133Xe in the isotope table and spect:2-5; Lu-177, Ra-223 and Y-90 as therapy nuclides in decay-modes. At the snapshot Ga-68 appeared only as an isotope (spect:5; the 68Ge generator row in decay-schemes). The later commit adds one pet-imaging paragraph that names 68Ga-PSMA-11 and 68Ga-DOTATATE.
- Missing: any card or problem on the Ga-68 agents, F-18 PSMA agents or choline; the pairing of 111In-pentetreotide (SPECT) with 68Ga-DOTATATE (PET); theranostic pairs such as 68Ga and 177Lu (guide Q223, planned); a problem that sorts agents by modality.
- Live update (19:35): spect:28 sorts 18F-FDG, 68Ga-DOTATATE, 68Ga-PSMA-11, 18F-fluoride, 99mTc-MDP, 99mTc-sestamibi, 111In-pentetreotide and 99mTc-MAA by scanner, and pet-imaging:34 matches tracers to targets. Open: F-18 PSMA agents, theranostic pairs.

**MRI safety.**
- Site has: metal only as a susceptibility artifact (mri-artifacts:6, :10); B0 in tesla and the Earth's field (mri-physics:2).
- Missing: everything else: static-field force and torque (the projectile effect), RF heating and SAR, gradient noise and nerve stimulation, MR-conditional devices and the cardiac-device hazards of guide Q169, safety zones, the 5 gauss line and the tesla-gauss conversion (guide Q10). Not on the PLAN under IV.A; the planned IV.B topic 'MR-guided radiotherapy' could host a short section, but the basics belong in `mri-physics`.
- Live update (19:35): mri-physics now has an 'MRI safety' section (static-field force, gradient stimulation, RF heating and SAR, MR Safe, Conditional and Unsafe labels, pacemaker risks) and problems mri-physics:27 to :32. The tesla-gauss conversion and safety zones are still absent.

**Ultrasound.**
- Site has: nothing (no hit for ultrasound, transducer or piezoelectric in any topic).
- Missing: sound waves, piezoelectric transducers (Q170, Q171), acoustic impedance and reflection, frequency against depth and resolution, Doppler, and the use of ultrasound for prostate brachytherapy (Q201) and localisation. The PLAN has 'Ultrasound physics' under IV.A; the two guide questions would be trivial for that topic, so build it to the blueprint, not to the guide.

**CBCT, kV against MV.**
- Site has: ct-quality guide section on CBCT (single rotation, about 700 images, about one minute, scatter, HU inaccuracy) and cards ct-quality:8-10; ct-quality:23 (why CBCT contrast and HU are worse than diagnostic CT); EPID cards radiographic-quality:7-9; photon-interactions:25 (little bone contrast at MV); radiographic-quality:2, :3 (contrast at kV against MV). The later commit adds a paragraph comparing a real CBCT with a planning CT (noise, contrast, field of view).
- Missing: a kV against MV CBCT comparison (soft-tissue contrast, imaging dose, metal artifacts, field of view, geometry), imaging dose values, registration and couch-shift workflow, and the strategies when the CBCT does not match the plan (Q175). All of IV.B is on the PLAN.
- Live update (19:35): ct-quality:33 compares MV and kV CBCT (streaks, soft-tissue contrast, dose) and a new paragraph explains it. Registration, couch shifts and imaging-dose values are still open.

**4D-CT.**
- Site has: the ITV definition (icru-volumes:3, :27, guide text 'expansion for physiological motion').
- Missing: 4D-CT itself (Q182), respiratory phases, binning artifacts, MIP and average images, surrogate signals, and how an ITV is built from phases (Q151 is in the site's coverage only as a definition).

**Motion management.**
- Site has: nothing beyond the ITV and margin recipe (icru-volumes:18).
- Missing: breath-hold, gating, tracking, abdominal compression, fiducials, the choice between them (Q176 to Q184), and TG-76. The guide's 10 items here are technique-selection scenarios, a style the site does not use. Planned: '4DCT and motion management', 'Surface guidance and tracking'.

**MR simulation and synthetic CT.**
- Site has: distortion matters in radiation oncology (mri-artifacts:1, :18), distortion phantom (mri-artifacts:4, :13); TG-284 is cited in the topic metadata but not discussed.
- Missing: MR-only against MR-plus-CT workflows, synthetic CT for density (Q173), coils and immobilisation, registration. Planned: 'PET and MRI in treatment planning', 'MR-guided radiotherapy'.

**Optical density and mAs.**
- Site has: radiographic-quality:12 (exposure scales with mA and kVp squared), :23 (SNR with mAs), :25 (skin exposure), :28 (what a higher mA changes). The later commit adds the kVp, mAs and time of a real radiograph in text.
- Missing: film, the characteristic curve, optical density, the exposure index of digital detectors, and the link from mAs and SID to detector exposure (Q163).
- Live update (19:35): radiographic-quality:32 (darkness set by mAs; the explanation defines optical density), :33 (digital image, four times the mAs, exposure index) and :34 (kVp against mAs). The film characteristic curve is still absent.

## e. Gaps

### e1. Top 15 gaps in built topics, in priority order

Priority combines how likely the point is to be examined (blueprint domain and the guide's emphasis), how much of the point the site lacks (nothing, text only, or a fragment) and how cheaply it can be closed. Each row cites what the site had at the snapshot; the last column gives the state of the working tree at 19:35.

| # | Concept | Guide Q | Topic file | Question type | Why it matters and what the site had at the snapshot | State at the first re-check (19:35) |
|---|---|---|---|---|---|---|
| 1 | MR safety: projectile force and torque, RF heating of leads, MR-conditional labelling, static-field units | Q169, Q10 | `mri-physics` (new guide section and cards) | PRM select-two, PR | Patient and staff safety is a standing imaging topic and MR simulation is routine. The site has no safety content; its only metal item is the susceptibility artifact (mri-artifacts:6, :10). Not on PLAN under IV.A. | Closed: mri-physics has an MRI safety section and problems :27 to :32. |
| 2 | PET and SPECT radiopharmaceuticals by name and modality (Ga-68 PSMA-11, Ga-68 DOTATATE, Tc-99m, In-111, I-123 agents) | Q166, Q222.1, Q223 | `pet-imaging`, `spect` | PRM select-two, SORT | Ga-68 and F-18 PSMA agents are in routine use for prostate disease. At the snapshot Ga-68 appeared only as an isotope (spect:5); one guide paragraph now names the two agents (text only). The tracer sort pet-imaging:30 holds five agents, none Ga-68 and none SPECT. | Mostly closed: spect:28 and pet-imaging:34 sort agents by modality and target, including 68Ga-PSMA-11, 68Ga-DOTATATE and the SPECT agents. Open: F-18 PSMA agents, theranostic pairs. |
| 3 | PET against SPECT: coincidence detection against collimators, sensitivity and resolution, dual-isotope SPECT | Q167 | `spect` (link from `pet-imaging`) | PR conceptual, PRM | The comparison is a standard framing. The site has one card (spect:12) and one problem (spect:20) that state the result without the mechanism, no SPECT resolution figure and no dual-isotope imaging. | Mostly closed: spect:29 and new guide text cover dual-isotope imaging. Open: the collimator-against-coincidence reason, a SPECT resolution figure. |
| 4 | Flattening-filter-free beams: dose rate, spectrum, head scatter and output factors, profile shape, surface and out-of-field dose | Q121 (Q43, Q69) | `profiles`, `skin-bolus`, `scatter` | PRM select-two | FFF is the default mode for SRS and SBRT on many machines. The site names it once, in passing (imrt-delivery guide text), with no card or problem; Q43 and Q69 sit on a planned linac topic, but Q121 sits here. | Open, no change |
| 5 | Protracted irradiation: BED with a repair term; equal-effect prescription for I-125 and Pd-103 | Q190, Q191 | `bed-tcp` (guide text and two problems); cross-link `brachy-sources` | PRN multi-step | Links brachytherapy and fractionation. The site gives only the acute formula and one sentence on repair (brachy-sources guide text). | Open, no change |
| 6 | Time at which two decaying sources reach equal activity; the 50% chance per half-life | Q189, Q29 | `decay-law` | PRN multi-step; PR | Standard two-exponential calculation. The site has single-source decay and equilibrium but never the equality; the 50% statement is only implied. | Open, no change |
| 7 | Electron bolus: SSD to the bolus surface, range lost to bolus thickness, effect of leaving it out | Q62, Q137, Q141 | `electron-fields`, with the rules from `electron-pdd` | PRN, PR | All 36 electron cards are recall. The guide combines range rules with bolus; the site teaches bolus only for photons (skin-bolus). | Open, no change |
| 8 | Electron surface-dose trend with energy (opposite to photons); internal shield thickness | Q139, Q138 | `electron-pdd` (trend), `electron-fields` (shield) | PR | A classic discriminator between photons and electrons; the site has the photon trend (pdd:3) and no electron trend. | Open, no change |
| 9 | Narrow-beam against broad-beam geometry and the build-up factor | Q88 | `photon-interactions` | PRN | Underlies HVL measurement against shielding design. The site states the definitions in one guide passage; every attenuation problem is narrow-beam. | Open, no change |
| 10 | Lung: small-field loss of lateral electron equilibrium, interface effects, effect of the heterogeneity correction in lung SBRT | Q251, Q133, Q86 | `dose-algorithms` | PR conceptual, PRM | The site covers dose beyond a slab and the TMR-like overestimate (dose-algorithms:25, :26), not the edge effect or the interfaces. | Open, no change |
| 11 | Optical density and mAs, with SID scaling; film characteristic curve and exposure index | Q163 | `radiographic-quality` | PRN, PR | The site never mentions optical density, the characteristic curve or an exposure index; it teaches skin exposure and SNR scaling instead. | Closed: radiographic-quality:32 to :34 (density, mAs, kVp against mAs). The guide text still lacks optical density. |
| 12 | CT noise and patient size: mAs needed to hold noise; tube-current modulation | Q165 | `ct-quality` | PRN | Patient-size effects on noise and dose are absent; ct-quality teaches SNR with mAs and slice thickness only. | Closed: ct-quality:29 asks the same calculation as proposal P12. |
| 13 | Dose to a medium from exposure with the f-factor; W/e as energy per ion pair | Q93, Q97 | `kerma-dose` | PRN | The site reaches dose to air (0.876 cGy/R) and stops. The f-factor underlies kV dosimetry and the exposure to dose step. | Open, no change |
| 14 | Interaction frequency against contrast in the kV range (Compton against photoelectric) | Q162, Q174 | `photon-interactions`, `radiographic-quality` | PRM select-two | The guide's keys conflate the two (section f). The site's text is right, but no item separates frequency from contrast, so a learner who meets the guide's version has no counter-example. | Closed: radiographic-quality:31 separates interaction frequency from contrast. |
| 15 | Electromagnetism and wave vocabulary: E-field units, current and AC/DC, transverse against longitudinal waves, field units | Q2, Q4, Q5, Q7, Q10, Q1.1 | `charges-atom`, `waves-photons` | Cards, PRN | The main block of recall gaps in domain I.A. The site's basic-physics problems are calculation-heavy and omit the vocabulary the guide tests. | Open, no change |

Next tier (smaller, or better settled first): Q24 threshold logic for characteristic lines (the site has the worked example, no item); Q143 and Q144 whole-body dose against IMRT energy (settle the source first); Q158 ICRU 62 injury classes; Q94 dose in free space and TAR; Q119, Q122, Q126 flattened-beam output, penumbra comparison and off-axis ratio; Q15 to Q17 relativistic mass and elastic collisions; Q22, Q36, Q39 forces, magic numbers, nuclear reactions; Q148 ICRU objectives; Q195 pulsed-dose-rate.

### e2. Unbuilt chapters (planned gaps, not unexpected ones)

| Guide ch | Chapter | guide Qs that are planned gaps | What the guide asks (one line) |
|---|---|---|---|
| 3 | Kilovoltage x-ray beams | 16 | Spectrum and the Duane-Hunt limit, tube parts, heel effect, filtration, efficiency; I.C, 3 PLAN topics |
| 4 | Megavoltage beams (linac) | 15 | Waveguide, klystron and magnetron, thyratron, bending magnet, target and flattening filter, FFF, interlocks, gantry and couch conventions; I.D, 5 PLAN topics |
| 5 (part) | Charged-particle interactions | 5 | LET, CSDA range, heavy-particle and electron collisions; I.E, PLAN topics on stopping power, electrons, Bragg peak, neutrons |
| 7 | Measurement and calibration | 18 | Chamber design, recombination, cavity theory, TG-51, detectors (TLD, OSLD, film, diodes, Fricke, GM), traceability and uncertainty; II.B, 10 PLAN topics, plus cavity theory in II.A |
| 12.5 | Ultrasound | 2 | Sound waves and piezoelectric transducers; IV.A |
| 13 | Simulation, motion, verification | 13 | CT and MR simulation, 4D-CT, breath-hold, gating, tracking, compression, kV and MV CBCT, correction strategies; IV.B, 7 PLAN topics |
| 14 (part), 15 | Clinical brachytherapy and brachytherapy QA | 10 | APBI applicators, plaques, TRUS prostate planning, Y-90, well chambers, tolerances, autoradiographs, QA categories; V, 6 PLAN topics |
| 16 | Special procedures | 21 | TBI and total marrow irradiation, TSET, IORT, cardiac devices and fetal dose, radiopharmaceutical therapy, adaptive RT, AI; VI.A, 5 PLAN topics |
| 17 | Particle therapy | 7 | Bragg peak, RBE and OER against LET, cyclotron and synchrotron, passive scattering and scanning, OTV; VI.B, 4 PLAN topics |
| 18 | SRS and SBRT | 14 | RTOG constraints and regimens, Gamma Knife, CyberKnife, cones against MLC, TG-155 small fields, Winston-Lutz, motion tools; VI.C, 4 PLAN topics |
| 19 | Quality assurance | 4 | Daily QA, isocenter tests, accuracy goals, patient-specific QA; VII.A, 5 PLAN topics |
| 20 | Radiation protection and shielding | 18 | ALARA, ICRP principles, dose limits, barrier design, transport, NCRP 160, survey meters, posting; VII.B, 6 PLAN topics |
| 21 | Safety and incidents | 9 | FMEA, fault trees, incident learning, root-cause analysis, Therac-25, HDR and IMRT accidents; VII.C, 3 PLAN topics |

Sixteen PLAN topics have no guide question: collimation, attenuation coefficients and mixtures, neutron interactions, electrometers, TG-51 for electrons, film dosimetry, MTF/NPS/DQE, fluoroscopy, portal imaging, MR-guided radiotherapy, gynecologic applicators and ICRU points (only the figure item Q200, which the parser dropped), unsealed sources and patient release, imaging system QA, TPS QA, commissioning and acceptance, and shielding design for linac vaults. The guide cannot test the site's completeness on these.

## f. Disagreements to verify

Where the guide and the site differ I do not say the site is wrong. Each row gives what each says, my reasoning and what would settle it.

### f1. Guide against site

| Guide Q | Guide says | Site says | My view and the physics | Settle with |
|---|---|---|---|---|
| Q162, Q174 | Keys the photoelectric effect as the main interaction in diagnostic radiography (Q162) and calls Compton dominance in kV CBCT false (Q174). | photon-interactions:7, :20: photoelectric below about 30 keV in water, Compton from about 30 keV to 24 MeV. radiographic-quality:15: bone contrast at kV comes from the photoelectric Z-cubed dependence. Added after the snapshot: radiographic-quality:31 assigns most soft-tissue interactions above about 30 keV to Compton scattering and the bone contrast to the photoelectric effect. | Both can hold if frequency and contrast are separated. Free-electron Klein-Nishina estimates on the site's NIST tables give Compton shares of the total attenuation of water of 72% at 40 keV, 83% at 50, 89% at 60 and 94% at 80 keV (cortical bone: 41% at 50, 54% at 60, 72% at 80 and 82% at 100 keV). Binding and coherent scatter move these by a few points. The photoelectric effect makes the bone-to-water ratio per gram 1.9 at 50 keV against 1.1 at 100 keV, so it forms most of the contrast. 'Primary interaction' is ambiguous: for frequency in soft tissue the site is right; for contrast, the guide is defensible. | NIST XCOM; Khan ch. 5; Bushberg ch. 3. |
| Q121 | Surface dose rises as energy falls and is highest for 6 MV FFF in small fields. | skin-bolus:5: higher energy lowers the dose in the first centimetre, but the dose at the skin itself changes little. pdd:3: 6 MV has more surface dose than 15 MV. FFF is named once in passing (imrt-delivery). | The direction agrees. 'Changes little' understates a monotonic fall with energy, small next to the effect of field size or devices. The FFF claim cannot be judged from the site, which does not teach FFF. Surface dose in FFF beams depends on field size, so a blanket statement for small fields needs the measurements. | Khan ch. 9; Georg, Knoos and McClean, Med Phys 2011 (FFF review); Kragl 2009; AAPM TG-176 for devices. |
| Q137 | Uses R90 = E/4 and dmax = E/5 (a '5-4-3-2' mnemonic). | electron-pdd:6 and table: R90 = E/3.3, R80 = E/3, R50 = E/2.33, Rp = E/2 (6 MeV: R90 1.8 cm). | For 6 MeV the rules give 1.5 and 1.8 cm. Measured R90 for a 6 MeV beam is about 1.7 to 1.8 cm, so E/4 is conservative. After the bolus thickness is subtracted both rules lead to the same keyed option, so the guide's answer survives. Rules of thumb should be tied to a named source in the question. | Khan ch. 14; AAPM TG-25; the clinic's own beam data. |
| Q261 | Table of quality factors: thermal neutrons 5, fast neutrons 20, alpha 20. | kerma-dose:11, :25: ICRP 103 radiation weighting factors (photons 1, protons 2, alpha 20). | The two agree for photons, electrons and alpha. They differ for neutrons and protons: ICRP 103 uses a continuous function of neutron energy (about 2.5 to 20) and 2 for protons; 10 CFR 20.1004 has its own quality-factor table. The answer to the guide item is unaffected, but a question must name the document. | ICRP 103 (wR); 10 CFR 20.1004. |
| Q143, Q144 | Photons above 10 MV give more leakage, scatter and neutrons (Q143). Orders 3D-CRT, 6 MV VMAT and 15 MV IMRT by low-dose volume, then explains it by whole-body dose (Q144). | mlc-imrt:2, :3 and guide text: more MU gives proportionally more leakage; photons above about 10 MV make neutrons, so IMRT is delivered at 6 or 10 MV. | The site's statements are standard. The guide's ordering is not supported by the paper it cites, which concludes that whole-body dose equivalent, neutrons included, is similar for 6 and 15 MV across IMRT, VMAT and 3D-CRT. The stem also asks for V5 Gy volume while the explanation discusses whole-body dose. One keyed reason in Q143 (more patient scatter above 10 MV) is doubtful because the scatter fraction in the patient falls with energy. | Hauri and Schneider 2019 (cited by the guide); AAPM TG-158; NCRP 151. |
| Q122 | Output rising with field size is attributed to electron contamination. | scatter:1, :10: output rises through head scatter (Sc) and phantom scatter (Sp). | Sc and Sp account for the output factor. Electron contamination changes the build-up dose and surface dose (skin-bolus:19), not the output rise. | Khan ch. 10. |
| Q119 | Orthovoltage has the smallest penumbra because photoelectric absorption dominates. | profiles:7: radiological penumbra grows with the range of the secondary electrons, so with energy and in low-density tissue. | The conclusion is plausible. The reason is the short secondary-electron range plus a short SSD and a small focal spot; at about 80 keV effective energy Compton, not photoelectric, dominates in soft tissue. | The penumbra sections of Khan. |
| Q38 | Defines parent-daughter equilibrium as equal activities with a constant ratio, and describes transient equilibrium in garbled terms. | equilibrium:1, :2, :21: transient ratio Ad/Ap = Tp/(Tp - Td) above 1; secular gives nearly equal activities. | Equal activities hold only for secular equilibrium. The site is correct; the guide's wording is not. | Khan ch. 2; Cherry, Sorenson and Phelps, Physics in Nuclear Medicine. |
| Q16 | Calls E/c2 the rest mass of a photon. | particles-energy: the photon's rest energy is listed as 0. | A photon has zero invariant (rest) mass; E/c2 is the old relativistic mass. The site follows the standard statement. | Khan ch. 2; a modern relativity text. |
| Q265, Q91, Q187, Q130 | Cs-137 exposure rate constant 3.26 (Q265); roentgen called the metric unit (Q91); explanation arithmetic about 1% high (Q187); stem and worked PDD differ by one point (Q130). | brachy-exposure table: 3.28 R cm2/(mCi h) for Cs-137; kerma-dose:7: C/kg is the SI unit, 1 R = 2.58e-4 C/kg. | Minor. The keyed options are unchanged in all four. | AAPM TG-43U1 or NIST for the constant; ICRU 85 for units. |

### f2. Other doubtful guide statements

These do not involve site content; they matter because a learner who uses the guide as a key could learn them. The full notes are in the `verify` field of roecsg-audit-mapping.json (43 questions).

| Guide Q | What looks doubtful (own words) | Settle with |
|---|---|---|
| Q19 | No incident energy is given, so the electron energy after 180-degree scatter is undetermined. The keyed 0.256 MeV is the limiting scattered-photon energy (m_e c2/2) at infinite incident energy; it equals the electron energy only at an incident energy of 0.414 MeV. | Khan ch. 5 (Compton equations). |
| Q23 | Explanation mixes electron-impact ionisation (tube) with photoelectric absorption; the figure is not in the parsed text. | Khan ch. 3. |
| Q41 | Minimum wavelength is said to vary as 1/V squared; Duane-Hunt gives 1/V, and the maximum photon energy equals eV. One option mixes the two relations. | Khan ch. 3. |
| Q42 | The explanation's 6 MV lead HVL (a few millimetres) and an 'effective energy' close to the nominal peak look wrong: an NCRP 151 TVL of about 5.7 cm of lead implies an HVL of about 1.5 to 1.7 cm, and the mean photon energy is about one third of the peak. | Khan ch. 3; NCRP 151 Appendix B. |
| Q56 | Hooded anode attributed to imaging tubes; Khan associates it with therapy (orthovoltage) tubes. The keyed answer is unaffected. | Khan ch. 3. |
| Q65 | Vendor-to-structure assignment (travelling wave against standing wave) depends on model and era. | Khan ch. 4; vendor documentation. |
| Q76 | Electron densities given for lung and soft tissue: the lung value implies about 0.7 g/cm3, far above inflated lung. The conclusion (Compton follows electron density) holds. | NIST ICRU-44 compositions. |
| Q92 | Explanation does not separate total from collision kerma; under CPE dose equals collision kerma and total kerma exceeds dose by the radiative fraction. The keyed false option is right. | Khan ch. 6. |
| Q100 | Lack of CPE is excluded from chamber corrections, yet the cited source treats it as a small-field correction. Protocol dependent. | TG-155; TRS-483. |
| Q102 | 'Fricke calorimetry' is chemical dosimetry, not calorimetry. | Khan ch. 8. |
| Q106 | One option describes a Geiger-Mueller tube as measuring current; it registers pulses of fixed size. | Khan ch. 6; Knoll or Attix. |
| Q138 | States 2 MeV lost per mm of lead; ESTAR gives about 1.4 to 1.7 MeV per mm at 1 to 2 MeV. A rule of thumb, approximate. | NIST ESTAR; Khan ch. 14. |
| Q140 | Explanation lists both a shift of R80 toward the surface and a larger practical range under oblique incidence; wording is loose. | Khan ch. 14. |
| Q164 | The key (HU is affine in mu, not proportional) is right but pedantic for a learner who knows the definition. | Bushberg ch. 10. |
| Q165 | Patient size does change CT noise, so the keyed 'no effect' is ambiguous. | Bushberg ch. 10; AAPM Report 204. |
| Q169 | One option denying any pull on the device is keyed true. Force and torque are real MR hazards and depend on the device's MR-conditional labelling. | ACR MR safety manual; device labelling. |
| Q173 | The keyed option makes synthetic CT crucial for dose calculation; that holds only in MR-only workflows. With an MR registered to a CT, the CT supplies density. | AAPM TG-284 (the site cites it for MRI). |
| Q184 | The keyed rule (gating for regular, tracking for irregular breathing) is a simplification; both rely on surrogate or marker correlation. | AAPM TG-76. |
| Q191 | The explanation's SBRT analogy is backwards. The key (I-125 needs the higher prescription) is right. | ABS consensus doses. |
| Q204, Q206 | HDR source-strength and position or timer tolerances differ between TG-40, TG-56, TG-59 and ESTRO. | TG-56, TG-59; licence conditions. |
| Q231 | Neutrons are listed with protons and carbon ions as sharing a Bragg peak; they have none. | Khan or Podgorsak (particle-therapy sections). |
| Q234 | A cyclotron is said to be unable to start particles from rest; it has an internal ion source. A synchrotron needs an injector. | Khan or Podgorsak (accelerator sections). |
| Q235 | Lateral spreading in passive scattering is by scatterers; range modulators and compensators do other jobs. | Khan (proton and heavy-ion chapter). |
| Q249 | The frame localiser does not 'guarantee' MR accuracy; gradient non-linearity and susceptibility shifts remain. | AAPM TG-284. |
| Q254 | TG-142 daily tests include more than output constancy; the keyed option is still the only dosimetry test listed. | TG-142; the AAPM MPPG on linac QA. |
| Q264 | NRC has no five-year averaging (that is ICRP style); the lens limit is stated both as 500 and 150 mSv. | 10 CFR 20.1201; ICRP 103 and 118. |
| Q269 | Transport index is dimensionless (dose rate at 1 m in mSv/h times 100); the keyed option is imprecise. | IAEA SSR-6. |
| Q278 | Lead is called best because of high Z. At MV energies Compton scattering is Z-independent per electron, so lead wins per centimetre through density; concrete is the standard barrier. | NCRP 151. |

## g. Proposed questions

**These are proposals, not site content.** Wording and numbers are mine; none is taken from an ABR item, textbook or the guide. They follow the site's ABR style (single best answer, or select-two with five options; no negative stems; no all or none of the above). Numeric options are in ascending order and each wrong value matches a specific slip. Check each against the site's conventions and constants before adding it. Calculations were checked in Python. At the 19:35 re-check, P1, P2, P3, P11, P12 and P14 overlap with items already added to the working tree (mri-physics:27 to :32; spect:28, :29 and pet-imaging:34; radiographic-quality:31 to :34; ct-quality:29, which repeats the design of P12), so compare before adding. P4 to P10, P13 and P15 address gaps that are still open.


**P1. MR safety (Q169)** (proposed for `mri-physics`; PRM select-two, 5 options)

Stem: A patient with a cardiac device labelled MR conditional is to have an MR simulation. Which two of these hazards do the MR-conditional limits (static field strength, spatial field gradient, specific absorption rate) exist to control? (Please select two options.)

- A. Heating of the lead tips by the radiofrequency field
- B. Force and torque on ferromagnetic parts in the static field
- C. A rise in the absorbed ionizing dose to the device
- D. Neutron activation of the device casing
- E. Loss of image contrast near the device

Answer: A and B. Explanation: The field-strength and gradient limits control force and torque. The SAR limit controls RF heating of the leads. MR uses no ionizing radiation, so there is no absorbed dose and no activation, and lost contrast is an image problem, not a hazard.

**P2. PET and SPECT agents (Q166)** (proposed for `pet-imaging`; PRM select-two, 5 options)

Stem: Which two of these agents are labelled with a positron emitter and imaged by PET? (Please select two options.)

- A. 99mTc-sestamibi
- B. 68Ga-DOTATATE
- C. 111In-pentetreotide
- D. 18F-FDG
- E. 123I-MIBG

Answer: B and D. Explanation: 68Ga (half-life 67.6 min) and 18F (109.8 min) decay by positron emission and are detected in coincidence. The 99mTc, 111In and 123I agents emit single photons and are imaged with a gamma camera. 111In-pentetreotide and 68Ga-DOTATATE bind the same receptor class, one for SPECT and one for PET.

**P3. PET against SPECT (Q167)** (proposed for `spect`; PR conceptual, 4 options)

Stem: Why does PET reach a higher sensitivity than SPECT for the same injected activity?

- A. Coincidence detection replaces the absorbing collimator, so far more of the emitted photons are used
- B. PET tracers are injected at about ten times the activity
- C. PET isotopes have longer half-lives, so more decays occur during the scan
- D. SPECT images cannot be corrected for attenuation

Answer: A. Explanation: A SPECT collimator defines direction by absorbing most photons (it passes of the order of 0.01% to 0.1%). PET defines the line of response electronically from two coincident 511 keV photons, and detects a fraction of the order of 1%. Injected activities are not higher for PET, most PET isotopes are shorter-lived, and SPECT-CT corrects attenuation.

**P4. Flattening-filter-free beams (Q121)** (proposed for `profiles`; PRM select-two, 5 options)

Stem: Compared with a flattened beam of the same nominal energy and field size, which two properties are expected of a flattening-filter-free beam? (Please select two options.)

- A. A higher dose rate on the central axis
- B. A harder mean photon energy
- C. Less variation of output with field size, because there is less head scatter
- D. A flat profile at 10 cm depth
- E. A wider penumbra

Answer: A and C. Explanation: Without the filter the central-axis dose rate rises by a factor of about 2 to 4. The filter hardens the beam, so the spectrum is softer without it, and the profile is bell-shaped. Head scatter falls, so output varies less with field size. The penumbra is similar or slightly smaller.

**P5. Protracted irradiation (Q190)** (proposed for `bed-tcp`; PRN multi-step, 4 options)

Stem: A low-dose-rate implant delivers 0.50 Gy/h for 72 h, a total of 36 Gy. Sublethal damage repairs with a half-time of 1.5 h, and the tumour has an α/β of 10 Gy. Use BED = D [1 + (2R / (μ α/β)) (1 − (1 − e^(−μT)) / (μT))], with R the dose rate, T the time and μ the repair rate. What is the BED?

- A. 36.0 Gy
- B. 39.8 Gy
- C. 43.6 Gy
- D. 165.6 Gy

Answer: C. Explanation: μ = ln 2 / 1.5 h = 0.462 per hour, and μT = 33.3. The bracket is 1 + (2 × 0.50 / (0.462 × 10)) × (1 − 0.030) = 1.210, so BED = 36 × 1.210 = 43.6 Gy. Dropping the repair term gives 36.0, omitting the factor 2 gives 39.8, and treating 36 Gy as one acute dose gives 165.6.

**P6. Equal activity (Q189, Q29)** (proposed for `decay-law`; PRN multi-step, 4 options)

Stem: Source X has 9.0 mCi and a half-life of 12 d. Source Y has 2.5 mCi and a half-life of 40 d. After how many days do the two sources have the same activity?

- A. 22.2 d
- B. 31.7 d
- C. 52.0 d
- D. 73.9 d

Answer: B. Explanation: 9.0 e^(−λX t) = 2.5 e^(−λY t) gives t = ln(3.6) / (λX − λY) = 1.281 / (0.05776 − 0.01733) = 31.7 d. Letting X fall to 2.5 mCi while ignoring the decay of Y gives 22.2 d, and adding the half-lives gives 52.0 d.

**P7. Electron bolus (Q62, Q137, Q141)** (proposed for `electron-fields`; PRN, 4 options)

Stem: A 9 MeV electron beam treats a lesion whose deep edge is 2.4 cm below the skin. A 1.0 cm sheet of tissue-equivalent bolus lies on the skin. Take R90 = E/3.3 cm for a bare beam. How deep below the skin is the 90% line?

- A. 0.7 cm
- B. 1.7 cm
- C. 2.7 cm
- D. 3.7 cm

Answer: B. Explanation: Bolus acts as extra tissue, so it uses up part of the range: 9 / 3.3 − 1.0 = 1.7 cm. The deep edge at 2.4 cm is not covered, and 12 MeV (3.6 − 1.0 = 2.6 cm) would cover it. Ignoring the bolus gives 2.7 cm, subtracting it twice gives 0.7 cm, and adding it gives 3.7 cm.

**P8. Electron surface dose (Q139)** (proposed for `electron-pdd`; PR conceptual, 4 options)

Stem: An open photon beam and an open electron beam are each used without bolus. Which statement about the dose at the surface as the beam energy rises is correct?

- A. The photon surface dose falls and the electron surface dose rises
- B. Both surface doses fall
- C. Both surface doses rise
- D. The photon surface dose rises and the electron surface dose falls

Answer: A. Explanation: Higher-energy photons set electrons moving more forward, so dmax is deeper and the surface dose lower. Higher-energy electrons scatter less, so the fluence builds up less with depth and the surface dose is a larger fraction of the maximum, roughly 75% to 80% at 6 MeV and above 90% at 20 MeV.

**P9. Broad beam (Q88)** (proposed for `photon-interactions`; PRN, 4 options)

Stem: A lead barrier must reduce a beam to 1.0% of the unshielded intensity. Narrow-beam data give an HVL of 0.80 cm of lead. Scatter in the barrier gives a build-up factor of 2.0, taken as constant. What thickness is needed?

- A. 4.5 cm
- B. 5.3 cm
- C. 6.1 cm
- D. 6.9 cm

Answer: C. Explanation: Transmission is B e^(−μx), so the beam must be attenuated to 0.010 / 2.0, and x = HVL × log2(B / T) = 0.80 × log2(200) = 6.1 cm. The narrow-beam value is 5.3 cm, putting B on the wrong side gives 4.5 cm, and adding B × HVL gives 6.9 cm.

**P10. Lung SBRT edge effect (Q251, Q133)** (proposed for `dose-algorithms`; PR conceptual, 4 options)

Stem: A 2 cm lung tumour is treated with 6 MV through small fields. The plan, calculated with a radiological-path-length correction, is recalculated with Monte Carlo at the same monitor units. Which change at the tumour edge is most likely?

- A. Lower dose and a wider penumbra, because lateral electron equilibrium is lost in low-density lung
- B. Higher dose, because lung attenuates the beam less than water
- C. No change, because both calculations use the same CT densities
- D. Higher dose and a sharper penumbra, because scatter in lung is lower

Answer: A. Explanation: Secondary electrons have long ranges in lung and leave a small field sideways. A path-length correction scales only the primary attenuation, so it overestimates the edge dose and underestimates the penumbra width. Option B is the effect the correction does model.

**P11. Optical density and mAs (Q163)** (proposed for `radiographic-quality`; PRN, 4 options)

Stem: A film-screen radiograph made at 100 cm SID with 20 mAs gives the right optical density. The SID is increased to 140 cm with the same kVp and film. What mAs keeps the optical density?

- A. 10.2 mAs
- B. 20.0 mAs
- C. 28.0 mAs
- D. 39.2 mAs

Answer: D. Explanation: Optical density follows the exposure at the film. That exposure falls as the inverse square of the distance, so the mAs must rise by (140/100)^2 = 1.96, giving 39.2 mAs. Leaving it unchanged gives 20.0, scaling linearly gives 28.0, and inverting the ratio gives 10.2.

**P12. CT patient size (Q165)** (proposed for `ct-quality`; PRN, 4 options)

Stem: A CT protocol uses 200 mAs for a patient whose water-equivalent thickness is 28 cm. The kVp, slice thickness and kernel are kept, and μ = 0.19 per cm for the beam. What mAs holds the same noise in a patient 36 cm thick? Ignore beam hardening.

- A. 200 mAs
- B. 257 mAs
- C. 428 mAs
- D. 914 mAs

Answer: D. Explanation: Noise depends on the number of detected photons, which is proportional to mAs × e^(−μd). Holding it fixed needs mAs to rise by e^(0.19 × 8) = 4.57, so 914 mAs. Scaling with thickness gives 257, taking the square root of the factor gives 428, and no change gives 200.

**P13. Exposure to dose in a medium (Q93, Q97)** (proposed for `kerma-dose`; PRN, 4 options)

Stem: A free-air chamber records an exposure of 30 R at a point in a Co-60 beam. At 1.25 MeV, μ_en/ρ is 0.0267 cm^2/g for air and 0.0296 cm^2/g for muscle. With 1 R = 0.876 cGy in air, what is the dose to muscle at that point under charged-particle equilibrium?

- A. 23.7 cGy
- B. 26.3 cGy
- C. 29.1 cGy
- D. 33.3 cGy

Answer: C. Explanation: Dose to air is 30 × 0.876 = 26.3 cGy. Under CPE the dose in muscle is that value times the ratio of mass energy-absorption coefficients, 0.0296 / 0.0267 = 1.109, giving 29.1 cGy. Stopping at air gives 26.3, inverting the ratio gives 23.7, and applying the ratio to the exposure alone gives 33.3.

**P14. Interaction frequency against contrast (Q162, Q174)** (proposed for `photon-interactions`; PRM select-two, 5 options)

Stem: A 100 kVp radiograph has an effective photon energy of about 50 keV. Which two statements about soft tissue and bone are correct? (Please select two options.)

- A. Most interactions in soft tissue are Compton scattering
- B. Most interactions in soft tissue are photoelectric absorption
- C. The photoelectric effect, which varies roughly as Z^3, produces most of the bone-to-soft-tissue contrast
- D. Compton scattering produces most of the contrast, because bone has more electrons per gram
- E. Pair production accounts for a few percent of the interactions in bone

Answer: A and C. Explanation: In water Compton scattering is roughly 80% of the attenuation at 50 keV. The photoelectric effect rises steeply with Z, so per gram bone attenuates about 1.9 times as much as water at 50 keV, while electrons per gram differ little. Pair production needs more than 1.022 MeV.

**P15. Electromagnetism vocabulary (Q5, Q8, Q9)** (proposed for `charges-atom`; PRN, 4 options)

Stem: A proton crosses a 2.0 cm gap in which the electric field is uniform at 1.5 MV/m. What kinetic energy does it gain?

- A. 3.0 keV
- B. 30 keV
- C. 300 keV
- D. 3.0 MeV

Answer: B. Explanation: The potential difference is E d = 1.5 × 10^6 V/m × 0.020 m = 30 kV, and the energy gained is qΔV = 30 keV (4.8 × 10^(−15) J). Electric field is measured in V/m, which equals N/C. Reading 2.0 cm as 0.20 cm gives 3.0 keV, reading it as 20 cm gives 300 keV, and using the field in MV as volts gives 3.0 MeV.


## Appendix A. Parse problems in the guide data

- Section labels in the parsed JSON are wrong for Q35-Q39 (labelled by a stray 0.975 Ci/g, really 2.2), Q80-Q88 and Q89-Q94 (labelled by a stray 2.5 MeV alpha, really 5.3, 5.4 and 6.1), Q168-Q169 (labelled 12.3, really 12.4 MRI), Q203-Q207 (labelled 14.6, really 15.1) and Q279-Q287 (labelled 20.7, really chapter 21). I corrected them from the table of contents in roecsg-audit-mapping.json.
- Answer missing: Q38, Q59, Q74, Q100, Q146 (read from the raw text); Q251 holds six sub-questions folded into one record.
- Fewer than two options: Q10 (options inline, A to E) and Q29 (options inline, a to d). Q49 options mis-split. Q16 option text garbled by the extraction (fractions). Answer letters were checked against the raw text.
- 23 items present in the raw text were not parsed (headers such as "Questions 21" or "Question 200." and numbered sub-questions); they are in the 23 unparsed items in Appendix B and Appendix B.
- Figures are not in the extracted text; figure-based items were judged from stem and explanation.

## Appendix B. Items found in the raw text but not parsed

23 items: 16 covered, 3 partial, 4 not covered. They are not included in the 277-question counts above.

| Item | Concept | Site | Nearest site items |
|---|---|---|---|
| Q1.1 | SI unit of electric current (ampere) | not covered | none |
| Q1.2 | SI unit of absorbed dose (gray) | covered | `kerma-dose:27`; `kerma-dose:22` |
| Q1.3 | SI unit of exposure (C/kg) | covered | `kerma-dose:7`; `kerma-dose:27` |
| Q1.4 | SI unit of activity (becquerel) | covered | `decay-law:3`; `decay-law:15` |
| Q1.5 | SI unit of equivalent dose (sievert) and the weighting factor | covered | `kerma-dose:11`; `kerma-dose:25` |
| Q1.6 | SI unit of effective dose (sievert) and tissue weighting | covered | `kerma-dose:11` |
| Q21 | isotopes, isotones, isobars, isomers | covered | `nuclear-structure:2`; `nuclear-structure:24`; `nuclear-structure:15` |
| Q44.1 | characteristic x-rays come from shell transitions | covered | `charges-atom:7`; `charges-atom:21` |
| Q44.2 | bremsstrahlung comes from electron-nucleus Coulomb interaction | partial (planned) | `decay-schemes:2` |
| Q44.3 | gamma rays come from nuclear transitions | covered | `waves-photons:5`; `decay-modes:7` |
| Q44.4 | annihilation quanta come from positron-electron collision | covered | `particles-energy:6`; `pet-imaging:1` |
| Q75.2 | neutrons are indirectly ionizing | covered | `photon-interactions:1`; `photon-interactions:27` |
| Q75.3 | protons are directly ionizing | covered | `photon-interactions:27`; `photon-interactions:14` |
| Q103.1 | thermoluminescent dosimeter reads dose from light emitted on heating | not covered (planned) | none |
| Q120 | dmax grows with MV energy; photoneutrons only above 10 MV | covered | `pdd:14`; `pdd:2`; `photon-interactions:13` |
| Q134.1 | CSDA range definition | not covered (planned) | none |
| Q134.2 | practical range of an electron beam | covered | `electron-pdd:5`; `electron-pdd:14` |
| Q134.3 | maximum range of an electron beam | partial | `electron-pdd:5` |
| Q161 | serial organs are judged by the maximum dose to a small volume | covered | `dvh-metrics:10`; `dvh-metrics:15` |
| Q200 | figure: ring and tandem HDR applicator | not covered (planned) | none |
| Q222.1 | Lu-177 PSMA therapy uses a beta emitter | partial (planned) | `decay-modes` |
| Q222.2 | decay type of Ra-223 for radiopharmaceutical therapy | covered | `decay-modes:24`; `decay-modes:25` |
| Q222.3 | F-18 FDG is a positron emitter | covered | `decay-modes:14`; `pet-imaging:1` |

## Appendix C. Coverage by built topic

Guide questions are assigned to the topic that should hold them. 'partial or missing' lists the questions that are not fully covered.

| Topic | ABR | cards | problems | guide Qs homed here | covered | partial | not covered | partial or missing |
|---|---|---|---|---|---|---|---|---|
| `waves-photons` | I.A | 9 | 13 | 6 | 4 | 1 | 1 | Q2, Q8 |
| `particles-energy` | I.A | 9 | 13 | 4 | 1 | 2 | 1 | Q15, Q16, Q17 |
| `charges-atom` | I.A | 9 | 13 | 9 | 4 | 3 | 2 | Q4, Q5, Q7, Q10, Q24 |
| `nuclear-structure` | I.B | 10 | 16 | 5 | 2 | 3 | 0 | Q22, Q36, Q39 |
| `decay-modes` | I.B | 12 | 15 | 3 | 3 | 0 | 0 | - |
| `decay-schemes` | I.B | 10 | 17 | 1 | 1 | 0 | 0 | - |
| `decay-law` | I.B | 13 | 18 | 7 | 5 | 2 | 0 | Q29, Q189 |
| `specific-activity` | I.B | 8 | 16 | 1 | 1 | 0 | 0 | - |
| `equilibrium` | I.B | 10 | 13 | 1 | 1 | 0 | 0 | - |
| `photon-interactions` | I.E | 13 | 21 | 7 | 6 | 1 | 0 | Q88 |
| `kerma-dose` | II.A | 12 | 17 | 9 | 8 | 1 | 0 | Q93 |
| `pdd` | III.A | 12 | 19 | 2 | 2 | 0 | 0 | - |
| `tmr` | III.A | 11 | 15 | 3 | 2 | 1 | 0 | Q94 |
| `scatter` | III.A | 11 | 18 | 2 | 1 | 1 | 0 | Q122 |
| `mu-calc` | III.A | 17 | 27 | 2 | 2 | 0 | 0 | - |
| `profiles` | III.A | 13 | 16 | 4 | 2 | 2 | 0 | Q119, Q126 |
| `skin-bolus` | III.A | 15 | 14 | 1 | 0 | 1 | 0 | Q121 |
| `dose-algorithms` | III.A | 15 | 16 | 5 | 2 | 3 | 0 | Q86, Q133, Q251 |
| `multifield` | III.A | 11 | 14 | 1 | 1 | 0 | 0 | - |
| `wedges` | III.A | 11 | 14 | 0 | 0 | 0 | 0 | - |
| `field-shaping` | III.A | 11 | 15 | 1 | 1 | 0 | 0 | - |
| `electron-pdd` | III.B | 12 | 15 | 3 | 1 | 1 | 1 | Q137, Q139 |
| `electron-fields` | III.B | 13 | 15 | 5 | 1 | 3 | 1 | Q62, Q138, Q140, Q141 |
| `electron-mu` | III.B | 11 | 14 | 1 | 1 | 0 | 0 | - |
| `icru-volumes` | III.C | 14 | 15 | 9 | 8 | 0 | 1 | Q148 |
| `dvh-metrics` | III.C | 12 | 15 | 6 | 5 | 1 | 0 | Q158 |
| `bed-tcp` | III.C | 11 | 15 | 1 | 0 | 1 | 0 | Q190 |
| `inverse-planning` | III.D | 12 | 14 | 1 | 1 | 0 | 0 | - |
| `imrt-delivery` | III.D | 14 | 15 | 1 | 1 | 0 | 0 | - |
| `mlc-imrt` | III.D | 12 | 15 | 2 | 1 | 1 | 0 | Q144 |
| `radiographic-quality` | IV.A | 14 | 16 | 2 | 0 | 2 | 0 | Q162, Q163 |
| `image-data` | IV.A | 15 | 15 | 0 | 0 | 0 | 0 | - |
| `ct-reconstruction` | IV.A | 11 | 16 | 1 | 1 | 0 | 0 | - |
| `ct-quality` | IV.A | 13 | 15 | 1 | 0 | 1 | 0 | Q165 |
| `mri-physics` | IV.A | 11 | 15 | 1 | 0 | 0 | 1 | Q169 |
| `mri-sequences` | IV.A | 12 | 15 | 1 | 1 | 0 | 0 | - |
| `mri-artifacts` | IV.A | 8 | 13 | 0 | 0 | 0 | 0 | - |
| `spect` | IV.A | 12 | 15 | 1 | 0 | 1 | 0 | Q167 |
| `pet-imaging` | IV.A | 15 | 17 | 1 | 0 | 1 | 0 | Q166 |
| `brachy-sources` | V | 13 | 16 | 4 | 3 | 1 | 0 | Q195 |
| `brachy-exposure` | V | 14 | 16 | 3 | 3 | 0 | 0 | - |
| `tg43` | V | 14 | 17 | 4 | 3 | 1 | 0 | Q191 |

## Appendix D. Coverage by PLAN topic

| ABR | Planned topic | guide Qs | which |
|---|---|---|---|
| I.C | Bremsstrahlung and characteristic x-rays | 3 | Q40, Q45, Q46 |
| I.C | X-ray tube components and the heel effect | 6 | Q47, Q51, Q52, Q53, Q54, Q56 |
| I.C | Filtration, kV spectra, and beam quality | 5 | Q41, Q48, Q49, Q50, Q55 |
| I.D | Linac components and the waveguide | 7 | Q57, Q58, Q59, Q60, Q65, Q71, Q72 |
| I.D | RF power: klystron, magnetron, and electron gun | 3 | Q66, Q67, Q68 |
| I.D | Bending magnet, target, and flattening filter | 5 | Q42, Q43, Q64, Q69, Q70 |
| I.D | Collimation: jaws, MLC, and field definition | 0 | none |
| I.D | Linac dosimetry system and beam steering | 1 | Q74 |
| I.E | Attenuation coefficients and mixtures | 0 | none |
| I.E | Stopping power and range of charged particles | 5 | Q18, Q63, Q78, Q79, Q80 |
| I.E | Electron interactions and bremsstrahlung yield | 1 | Q82 |
| I.E | Heavy charged particles and the Bragg peak | 1 | Q81 |
| I.E | Neutron interactions | 0 | none |
| II.A | Cavity theory and stopping power ratios | 1 | Q110 |
| II.B | Ion chamber design and charge collection | 2 | Q99, Q115 |
| II.B | Ion recombination and polarity effects | 1 | Q100 |
| II.B | Electrometers, cables, and leakage | 0 | none |
| II.B | TG-51 photon beam calibration | 5 | Q98, Q108, Q109, Q113, Q114 |
| II.B | TG-51 electron beam calibration | 0 | none |
| II.B | Diodes, MOSFETs, and scintillators | 1 | Q105 |
| II.B | TLD and OSLD dosimetry | 1 | Q104 |
| II.B | Film dosimetry and radiochromic film | 0 | none |
| II.B | Arrays, gels, and 3D dosimetry | 1 | Q102 |
| II.B | Calibration traceability and kV dosimetry | 5 | Q97, Q101, Q111, Q112, Q116 |
| IV.A | MTF, NPS, and DQE | 0 | none |
| IV.A | Fluoroscopy and image intensifiers | 0 | none |
| IV.A | Ultrasound physics | 2 | Q170, Q171 |
| IV.B | CT simulation and image registration | 1 | Q172 |
| IV.B | PET and MRI in treatment planning | 1 | Q173 |
| IV.B | 4DCT and motion management | 8 | Q176, Q177, Q178, Q179, Q180, Q181, Q182, Q184 |
| IV.B | Portal imaging and EPID | 0 | none |
| IV.B | CBCT and image-guided shifts | 2 | Q174, Q175 |
| IV.B | Surface guidance and tracking | 1 | Q183 |
| IV.B | MR-guided radiotherapy | 0 | none |
| V | Permanent seed implant dosimetry | 1 | Q201 |
| V | HDR planning and dwell times | 2 | Q197, Q199 |
| V | Gynecologic applicators and ICRU points | 0 | none |
| V | Source calibration and well chambers | 4 | Q203, Q204, Q205, Q206 |
| V | Eye plaques and skin brachytherapy | 1 | Q198 |
| V | Brachytherapy radiation safety | 1 | Q207 |
| VI.A | Total body irradiation | 4 | Q208, Q209, Q210, Q211 |
| VI.A | Total skin electron therapy | 6 | Q212, Q213, Q214, Q215, Q216, Q217 |
| VI.A | Intraoperative radiotherapy | 1 | Q218 |
| VI.A | Radiopharmaceutical therapy dosimetry | 3 | Q202, Q223, Q225 |
| VI.A | Unsealed sources and patient release | 0 | none |
| VI.B | Proton Bragg peak and spread-out peak | 2 | Q231, Q234 |
| VI.B | Passive scattering and pencil beam scanning | 2 | Q235, Q236 |
| VI.B | Proton range uncertainty and planning | 1 | Q237 |
| VI.B | Carbon ions, LET, and RBE | 2 | Q232, Q233 |
| VI.C | Stereotactic radiosurgery systems | 6 | Q239, Q244, Q246, Q247, Q248, Q249 |
| VI.C | Small-field dosimetry | 1 | Q252 |
| VI.C | SBRT planning and motion | 6 | Q238, Q240, Q241, Q242, Q245, Q250 |
| VI.C | Stereotactic QA and end-to-end tests | 1 | Q253 |
| VII.A | QA program and TG-142 tests | 3 | Q254, Q255, Q256 |
| VII.A | Imaging system QA | 0 | none |
| VII.A | MLC and IMRT QA | 2 | Q147, Q257 |
| VII.A | Treatment planning system QA | 0 | none |
| VII.A | Commissioning and acceptance testing | 0 | none |
| VII.B | Dose limits and ALARA | 7 | Q258, Q259, Q263, Q264, Q270, Q271, Q272 |
| VII.B | Shielding design for linac vaults | 0 | none |
| VII.B | Primary and secondary barriers | 4 | Q260, Q275, Q277, Q278 |
| VII.B | Neutron shielding above 10 MV | 1 | Q276 |
| VII.B | Brachytherapy and unsealed-source protection | 1 | Q266 |
| VII.B | Survey instruments and regulations | 7 | Q106, Q107, Q267, Q268, Q269, Q273, Q274 |
| VII.C | Quality management and TG-100 | 4 | Q279, Q280, Q281, Q287 |
| VII.C | Incident reporting and root cause analysis | 3 | Q282, Q283, Q284 |
| VII.C | Medical events and communication | 2 | Q285, Q286 |

## Appendix E. Independence check (own words)

- Wording: I compared every site card and problem (stem plus options or answer, 1 to 3-grams, TF-IDF cosine) with every guide question. The highest cosine is 0.29 (Q243 against dvh-metrics:6, both defining a conformity index); no pair is close to a copy.
- Shared givens: tmr:9 (6 MV, PDD 67.0% at 10 cm, dmax 1.5 cm, Sp ratio 1) has the same energy, depth, dmax and PDD value as Q125, and the same data run through tmr:19, tmr:20, tmr:23, pdd:9 and pdd:22. decay-law:28 (Co-60, half-life 5.27 y, 10 y in use) has the same isotope and elapsed time as Q187. The values are standard textbook data and the wording differs, but the owner may prefer different numbers for the site's items.
- Shared source values: both use the tungsten K binding energy of 69.5 keV (a constant).
## Appendix F. Reproduction

The audit read every guide question with its explanation and every site topic. The mapping in `roecsg-audit-mapping.json` holds one entry per parsed guide question: the concept in the audit's words, the coverage verdict, the matching site items, the level verdict and its reason, a `verify` note where the guide looks doubtful, and for questions closed since the snapshot the fields `live_status`, `live_note` and `live_checked`. Site item ids are `topic:number`, where the number counts the cards first and then the problems, as on the site; ids at the snapshot are unchanged because new items were appended. The scripts that built the tables (a TF-IDF candidate search, a rule-based item typer, and the hand decisions) are not part of the repository.
