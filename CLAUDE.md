# Radiation oncology physics study site

Single-file study guide for radiation oncology residents preparing for the ABR Medical Physics for Radiation Oncology exam (seven domains, 20 subsections; weights in `src/blueprint.py`). Each topic is a guide page followed by flashcards. There is no calendar: no months, years, or weekly sessions.

Follow `skills/house-style/SKILL.md` for every visual and written change: plain dark-on-white, system sans, no filler text, no features or controls that were not asked for (ask first), no web fonts. Check at 1280 × 900 and 390 × 844, light and dark.

## Commands

- Build: `python build.py` (writes `dist/ro-physics.html`; standard library only).
- Tests: `python tests/numbers.py`, then `python tests/smoke.py` (needs `pip install -r requirements-dev.txt && playwright install chromium`, or `CHROME_PATH`).
- Run both after any change to content or the page.

## How it fits together

- `build.py` renders every topic's guide blocks to HTML, embeds data, figures, CSS, and JS in one page.
- Routes: `#study`, `#d3` (domain), `#d3/c` and `#d3/c/5` (domain deck), `#t/pdd` (topic guide), `#t/pdd/c` and `#t/pdd/c/5` (topic deck), `#mix` and `#mix/5` (mixed deck, topics interleaved), `#ref`.
- The dial draws one equal section per ABR domain. A domain with no topics is drawn but not linked.
- A card shows one question, then Show answer reveals the answer and optional working. No grading, no scores. Keys: Space, right arrow, left arrow. A card counts as seen when its answer is shown.
- The Reference page holds the coverage table by ABR subsection (rows in red have no cards), the reading table, progress export and import, and the theme toggle.
- Progress is stored in `localStorage` (`ro.cards`, `ro.theme`). Treat stored values as untrusted.
- Real images (`src/real_*.json`, drawn by `realFig` in `src/app.js`) are figures of views of one to four panels, each one SVG with its caption. They are rebuilt by `tools/make_real_*.py` from DICOM that the NCI Imaging Data Commons republishes from TCIA. The Reference page lists every source.

## Rules

- Write in your own words. Nothing from the textbooks, the lecture decks, the problem sets, the video quizzes, or ABR items (sample or recalled). Figures are redrawn.
- Every number in a worked example is computed in `src/calc.py` and re-derived in `tests/numbers.py`. Give ranges where a value varies by machine, vendor, or edition. Factors in worked examples are illustrative, and the Reference page says so.
- State conventions that change a formula (for example SSD versus SAD calibration) in the text.
- Card ids are `topic-id:number`. Add cards at the end of a topic.
- One idea per card, one short answer. Put calculations in the card's working steps.
- Real images: only CC BY 3.0 or CC BY 4.0 collections, every caption names the collection and its licence, nothing that identifies a patient is stored (no IDs, dates, or UIDs), and an image is called real only if no part of it is simulated. State what was done to it (resampled, cropped, windowed, aligned by the dataset's authors). Quote numbers from the stored measurements (`real.STATS`), never by hand, and read acquisition values from the DICOM header, but not tags the collection leaves unreliable (the NaF PROSTATE headers name the tracer FDG).
- Sources: the ABR study guide, the AAPM/ASTRO 2023 core curriculum, standard references, and the group's own lectures as a topic inventory only.

## Open work

- Domains 2, 4, 5, 6, 7 and most of 1 and 3 have no topics yet. The Reference page lists the gaps.
- Ford chapter numbers in each topic's `ref` come from chapter titles and need checking against the book.
