# Radiation oncology physics study site: source archive

Built with Python; the output is one self-contained HTML file (dist/ro-physics.html).

## Rebuild and test
    python3 build.py                      # writes dist/ro-physics.html
    python3 tests/<name>.py               # static tests: style, structure, takeaway, facts, problems, plan, abrstyle, numbers*, tapquality, mudata, figq, casedata, noslider
                                          # browser tests (Playwright): av_all, activities, more, questions, textbook, huex, drr, case, ctart, mrex, nav, sidebar, swipe, dialsync, mu, calc, av, smoke
    Run browser tests a few at a time: each command must finish within 300 s.
    Tests that import numpy remove tests/ from sys.path first, because tests/numbers.py would shadow the standard module.

## Layout
- src/app.js          routing, question player, diagram engine, figures (AV['id']), real-data viewers
- src/topics/*.py     one file per chapter: guide blocks, cards, problems, take-aways
- src/*.json          processed real data: case_hn1 (OpenKBP plan), gal_ct (CT effects), gal_drr (radiographs), mr_case and gal_mr (MR brain)
- tools/*.py          scripts that regenerate those JSON files from the open sources (see below)
- tests/*.py          the test suite
- tools_plan.py       removes a finished chapter from the plan (src/syllabus.py)

## Data provenance (check the terms before sharing the site publicly)
- OpenKBP (Babier et al., Med Phys 2021; github.com/ababier/open-kbp): CT, structures, and dose of clinical head-and-neck plans. tools/make_case.py, make_ct_artifacts.py, make_drr_gallery.py read patient pt_14 from a sparse checkout.
- ICBM152 (MNI152 2009) average brain and tissue maps, shipped with the nilearn package (pip install nilearn): tools/make_mr.py.
- NIST attenuation tables in src/nistdata.py. Text is written in our own words; Ford (2nd ed.) is the ground truth for content.

## Rules locked in
- No chart slider that only moves a marker along a fixed curve (tests/noslider.py enforces it).
- No difficulty labels shown to learners. Select-several questions follow the ABR wording (tests/abrstyle.py).
- Simulated images are labelled as simulations; real images carry their attribution in the caption.
