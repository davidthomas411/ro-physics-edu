# Radiation oncology physics

Study site for radiation oncology residents preparing for the ABR Medical Physics for Radiation Oncology exam. Each topic is a short guide followed by flashcards. The site is one self-contained HTML file.

## Release and citation

The owner's values (authors, contact, physics reviewers, IRB number, usage-count settings, and the rest) are in `site_config.json`, and the code reads them from there. `python build.py --release` stops with a list of what is missing. `RELEASING.md` gives the steps for a release on GitHub Pages. After editing `site_config.json`, `CHANGELOG.md`, or `src/analytics_schema.py`, run `python tools/sync_release_files.py`, which rewrites `CITATION.cff`, `.zenodo.json`, the citation block below, and `docs/irb-data-description.md`.

<!-- cite:start -->
## How to cite

DOI badge: to be added after the first Zenodo release.

Cite the version of the site that you used. `CITATION.cff` holds the same information, and GitHub shows it under "Cite this repository".

APA

> [authors missing] (2026). Radiation oncology physics study site (Version 1.0.0) [Computer software]. GitHub Pages. [URL missing]

AMA

> [authors missing]. Radiation oncology physics study site. Version 1.0.0. GitHub Pages; 2026. [URL missing]

BibTeX

```bibtex
@software{author2026radiation,
  author    = {[authors missing]},
  title     = {Radiation oncology physics study site},
  year      = {2026},
  version   = {1.0.0},
  publisher = {GitHub Pages},
  url       = {[URL missing]}
}
```
<!-- cite:end -->

## License

Code: MIT (`LICENSE`). Text, questions, flash cards, and diagrams: CC BY 4.0 (`LICENSE-CONTENT.md`). Third-party material keeps its own terms (`THIRD_PARTY_NOTICES.md`).

## Build and run

```
python build.py                    # writes dist/ro-physics.html (standard library only)
python serve.py --port 8765        # serves dist/ at / ; health check at /healthz
```

`dist/` is committed, so serving needs no build. Learner progress lives in each browser's `localStorage`; the server stores nothing. Open the HTML file directly, or host it as a static file.

## Test

```
python tests/numbers.py            # re-derives every worked-example number independently
python tests/numbers_tg51.py       # one such file per later chapter (tests/numbers*.py): its printed and keyed numbers, re-derived by another route
pip install -r requirements-dev.txt && playwright install chromium
python tests/smoke.py              # pages, decks, keys, progress, dial, dark mode, 390 px width, console errors
python tests/realdata.py           # real images: licences, attribution, no identifiers, measured numbers
python tests/realimg.py            # real images in the page: panels, views, decoding, phone width, the Reference sources
python tests/style.py              # house-style patterns in all text, including the flash-card titles
python tests/mlcfigs.py            # the MLC figures: leaf-end bands and the equal-area opening re-derived from the stated geometry
python tests/license.py            # licenses, citation files, third-party notices, and the release gate
python tests/about.py              # the About page: sections, counts, citation text, copy buttons, links
python tests/analytics.py          # usage events: off by default, the schema, no cookies, no new storage keys
```

Set `CHROME_PATH` to use an existing Chromium. Run both tests after any change to content or the page.

## Layout

- `src/blueprint.py`: the seven ABR domains and their 20 subsections, with the ABR weights.
- `src/siteinfo.py`: the About page, the citation texts, and the release checks. `src/analytics_schema.py`: the usage events the page can send; the privacy text, the IRB description, and the tests all read it.
- `chapters/<id>/`: one folder per topic (the chapter module with guide blocks and cards, and its Explain further module where one exists). `src/topics/__init__.py` lists them; the order is the study order inside each domain.
- `src/figs.py`: original figures as inline SVG that follow light and dark.
- `src/facts.py`: the title of every flash card. A flash card shows its title and its answer, not the question written in the topic file, so both must stand alone.
- `src/calc.py`: the formulas behind the worked examples. Topic files import them, so no example number is typed by hand.
- `src/blocks.py`: guide block constructors and the renderer.
- `src/style.css`, `src/app.js`: the page. `build.py` inlines both.
- `src/photos/manifest.json`, `src/photolib.py`: real equipment photographs (public domain, CC0, or CC BY only) with their credits; a chapter places one with `PHOTO(id)`.
- `src/real_*.json`, `src/real.py`: real clinical images from open TCIA collections, with their attribution. `tools/tcia.py` and `tools/make_real_*.py` rebuild them (see RESTORE.md).
- `docs/`: the audit of the questions against the ROECSG physics study guide (coverage, level, gaps, and the list of questions still to write). The guide is used to find gaps only; every question is written in its own words.
- `docs/facts-to-verify.md`: the statements in the later chapters that were not confirmed against the primary document, for a physics reviewer to settle.
- `skills/house-style/`: the visual and writing style guide.
- `assets/linac/`: the linac illustration layers for the dial.

## Add a topic

1. Copy a folder in `chapters/`. Set `id`, `domain` (1 to 7), and `sub` (an ABR subsection code such as `III.A`).
2. Write the guide with the block constructors and the cards with `C(...)`. Compute every number in `calc.py`.
3. Register the module in `src/topics/__init__.py`.
4. Write `tests/numbers_<module>.py`, which re-derives by another route every number the chapter prints or keys (model: `tests/numbers_tg51.py`). For a Basic physics (domain 1) chapter, also write the Explain further text of each question in `src/more_<module>.py` (model: `src/more_xray_tube.py`) and import it in `src/topics/__init__.py`; `tests/more.py` requires it.
5. Build and run the tests.

Card ids are `topic-id:number`, so add cards at the end of a topic. Reordering or deleting cards shifts the ids and breaks saved progress.
