# Radiation oncology physics

Study site for radiation oncology residents preparing for the ABR Medical Physics for Radiation Oncology exam. Each topic is a short guide followed by flashcards. The site is one self-contained HTML file.

## Build and run

```
python build.py                    # writes dist/ro-physics.html (standard library only)
python serve.py --port 8765        # serves dist/ at / ; health check at /healthz
```

`dist/` is committed, so serving needs no build. Learner progress lives in each browser's `localStorage`; the server stores nothing. Open the HTML file directly, or host it as a static file.

## Test

```
python tests/numbers.py            # re-derives every worked-example number independently
pip install -r requirements-dev.txt && playwright install chromium
python tests/smoke.py              # pages, decks, keys, progress, dial, dark mode, 390 px width, console errors
python tests/realdata.py           # real images: licences, attribution, no identifiers, measured numbers
python tests/realimg.py            # real images in the page: panels, views, decoding, phone width, the Reference sources
```

Set `CHROME_PATH` to use an existing Chromium. Run both tests after any change to content or the page.

## Layout

- `src/blueprint.py`: the seven ABR domains and their 20 subsections, with the ABR weights.
- `src/topics/`: one file per topic (guide blocks and cards). `__init__.py` lists them; the order is the study order inside each domain.
- `src/figs.py`: original figures as inline SVG that follow light and dark.
- `src/calc.py`: the formulas behind the worked examples. Topic files import them, so no example number is typed by hand.
- `src/blocks.py`: guide block constructors and the renderer.
- `src/style.css`, `src/app.js`: the page. `build.py` inlines both.
- `src/real_*.json`, `src/real.py`: real clinical images from open TCIA collections, with their attribution. `tools/tcia.py` and `tools/make_real_*.py` rebuild them (see RESTORE.md).
- `skills/house-style/`: the visual and writing style guide.
- `assets/linac/`: the linac illustration layers for the dial.

## Add a topic

1. Copy a file in `src/topics/`. Set `id`, `domain` (1 to 7), and `sub` (an ABR subsection code such as `III.A`).
2. Write the guide with the block constructors and the cards with `C(...)`. Compute every number in `calc.py`.
3. Register the module in `src/topics/__init__.py`.
4. Add the number to `tests/numbers.py` if it is a worked example. Build and run both tests.

Card ids are `topic-id:number`, so add cards at the end of a topic. Reordering or deleting cards shifts the ids and breaks saved progress.
