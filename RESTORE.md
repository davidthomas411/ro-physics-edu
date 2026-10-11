# Radiation oncology physics study site: source archive

Built with Python; the output is one self-contained HTML file (dist/ro-physics.html).

## Rebuild and test
    python3 build.py                      # writes dist/ro-physics.html
    python3 tests/<name>.py               # static tests: style, structure, takeaway, facts, problems, plan, abrstyle, numbers*, tapquality, mudata, figq, casedata, noslider, realdata
                                          # browser tests (Playwright): av_all, activities, more, questions, textbook, huex, drr, case, ctart, mrex, nav, sidebar, swipe, dialsync, mu, calc, av, smoke, realimg
    Run browser tests a few at a time: each command must finish within 300 s.
    Tests that import numpy remove tests/ from sys.path first, because tests/numbers.py would shadow the standard module.

## Layout
- src/app.js          routing, question player, diagram engine, figures (AV['id']), real-data viewers
- src/topics/*.py     one file per chapter: guide blocks, cards, problems, take-aways
- src/*.json          processed real data: case_hn1 (OpenKBP plan), gal_ct (CT effects), gal_drr (radiographs), mr_case and gal_mr (MR brain), real_ct/real_pet/real_mr/real_nm/real_dx (TCIA clinical images)
- tools/*.py          scripts that regenerate those JSON files from the open sources (see below)
- tests/*.py          the test suite
- tools_plan.py       removes a finished chapter from the plan (src/syllabus.py)

## Data provenance (check the terms before sharing the site publicly)
- OpenKBP (Babier et al., Med Phys 2021; github.com/ababier/open-kbp): CT, structures, and dose of clinical head-and-neck plans. tools/make_case.py, make_ct_artifacts.py, make_drr_gallery.py read patient pt_14 from a sparse checkout.
- ICBM152 (MNI152 2009) average brain and tissue maps, shipped with the nilearn package (pip install nilearn): tools/make_mr.py.
- TCIA collections (all CC BY 3.0 or CC BY 4.0), read as DICOM from the public buckets of the NCI Imaging Data Commons by tools/tcia.py (pip install -r requirements-tools.txt; the first run downloads about 1 GB, cached in TCIA_CACHE):
    tools/make_real_ct.py: CC-Radiomics-Phantom-2 (noise against tube current, kernels), Pancreatic-CT-CBCT-SEG (planning CT and CBCT), CMB-LCA (iMAR).
    tools/make_real_pet.py: NSCLC Radiogenomics (FDG without and with attenuation correction, fusion, SUV), NaF PROSTATE, PSMA-PET-CT-Lesions.
    tools/make_real_nm.py: CMB-PCA (planar bone scan).  tools/make_real_mr.py: UPENN-GBM (T1, T1 with gadolinium, T2, FLAIR).  tools/make_real_dx.py: COVID-19-AR (chest radiograph).
  `bash tools/make_real_all.sh` runs all five.
  Each JSON file carries the collection name, DOI, licence, and citation text, which the Reference page lists. The scripts pick fixed patients and series, so a rebuild gives the same files. TCIA's own hosts were not reachable from the build environment; the IDC buckets hold the same collections.
- NIST attenuation tables in src/nistdata.py. Text is written in our own words; Ford (2nd ed.) is the ground truth for content.

## Rules locked in
- No chart slider that only moves a marker along a fixed curve (tests/noslider.py enforces it).
- No difficulty labels shown to learners. Select-several questions follow the ABR wording (tests/abrstyle.py).
- Simulated images are labelled as simulations; real images carry their attribution in the caption.
- Real TCIA images: attribution-only licences, no patient identifiers in the data, only values the DICOM header gives reliably (tests/realdata.py and tests/realimg.py enforce this).
