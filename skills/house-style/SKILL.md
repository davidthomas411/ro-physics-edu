---
name: house-style
description: "Default visual and writing style for anything built for this user (web pages, apps, dashboards, slides, docs, study material). Plain dark-on-white, system sans, no filler. Apply unless told otherwise."
---

# House style

Default style for anything built for this user: web pages, apps, dashboards, study material, slides, documents. Apply it unless the user asks for something else (a brand template, a poster). It is a set of constraints, not a theme.

Files: `assets/base.css` holds the tokens and components (paste inline). `assets/example.html` renders every component and is the visual reference. Read the three files in `references/` only when the task matches (see the last section).

## Content rules

- Include only text the reader needs. No taglines, intro paragraphs, slogans, or clever phrasing.
- Titles are nouns or labels ("Year 1", "Reference"). Button labels are literal ("Show answer", "Next question").
- Add no feature, control, badge, panel, animation, or decoration that was not requested. If one seems necessary, say so in one line and ask.
- Keep internal details out of the interface: file names, source decks, build notes.
- Check every fact before writing it. Give a range where a value varies by vendor or edition. Put sources on a reference page.
- Never render an empty control. Hide a dropdown, tab, or button that has nothing to choose or do.

Why these exist: the user removed taglines, intro text, clever phrasing, and file names from earlier builds, and asked for nothing that is not needed. Unrequested text and features were corrected repeatedly, so ask first.

## Tokens

| Token | Role | Light | Dark | Contrast on paper (light / dark) |
|---|---|---|---|---|
| `--paper` | Page background | `#FFFFFF` | `#121212` | non-text |
| `--paper-2` | Equation blocks, hover fill, progress track | `#F6F6F6` | `#1C1C1C` | non-text |
| `--ink` | Headings, button fill, active tab | `#111111` | `#F2F2F2` | 18.9 / 16.7 |
| `--text` | Body text | `#1F1F1F` | `#E6E6E6` | 16.5 / 15.0 |
| `--muted` | Metadata and captions, 13 px and up | `#5C5C5C` | `#A8A8A8` | 6.7 / 7.9 |
| `--accent` | Links, disclosure labels, focus ring | `#0B5FD1` | `#7FB3FF` | 5.9 / 8.7 |
| `--danger` | Overtime, missing items, errors | `#B3261E` | `#FF8A7A` | 6.5 / 8.2 |
| `--rule` | Hairlines between rows and sections | `#E3E3E3` | `#303030` | non-text |
| `--line` | Input borders, inactive strokes | `#C9C9C9` | `#4A4A4A` | non-text |

Plot palette (data only): `--plot-1` #1F4E79 / #8FBCE6, `--plot-2` #C0561F / #E9A271, `--plot-3` #2E7D5B / #7FC8A4, `--plot-4` #6B4C9A / #B79BE0 (light / dark).

Body and heading text exceed 15:1 against the paper in both modes. `--muted`, `--accent`, and `--danger` meet WCAG AA (4.5:1) but not AAA (7:1) on white, so use them for metadata, links, and warnings, not for body text.

## Type

System stack only: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.

- Body: 17 px / 1.55, weight 400 (System sans)
- Metadata, captions: 13–14 px, weight 400 (--muted)
- h1: 30 px / 1.2 (25 px on phones), weight 700 (letter-spacing −0.01em)
- h2: 22 px, weight 700 (40 px above, 10 px below)
- h3: 18 px, weight 700
- Slide prompt: 21 px (clamp up to 32 px when presenting), weight 600
- Slide questions: 19 px, weight 600 (numbered list)
- Button: 15 px (14 small, 16 large), weight 600

Keep lines to about 75 characters. Left-align text. Use sentence case.

## Components

- Link: `--accent`, underlined. Tabs and row links are not underlined; the active tab is `--ink`, 600, with a 2 px `--ink` underline.
- Button: 1 px `--ink` border, 4 px radius, 15 px / 600, padding 7 × 14. Primary is `--ink` fill with `--paper` text. Disabled is 35% opacity. Focus is a 2 px `--accent` outline, offset 2 px.
- Table: hairline row rules, header 13 px / 600 `--muted` with a 1 px `--ink` rule below, no fills.
- Figure: 1 px `--rule` border, 3 px radius, 8 px padding, caption below in 13 px `--muted`. Label things beside the figure, not in a legend far away.
- Key points: a bold 13 px label, then a plain bulleted list at 16 px. No tinted panel.
- Disclosure (`details`): 14 px / 600 `--accent` with a small triangle.
- Progress: 6 px bar, `--paper-2` track, `--ink` fill.
- Fields: 4 px radius, 1 px `--line` border, padding 7 × 10.
- Equations: `--paper-2` block, 3 px radius.
- Sidebar items: 15 px; the current item is 600 with a 6 px `--ink` dot to its left.

## Layout and phones

- Header: name on the left, tabs on the right, 1 px rule below. The active tab is bold with a 2 px underline.
- Content column is at most 760 px (about 75 characters per line). From 900 px, a 230 px sidebar is added; below that, one column.
- On phones (390 px wide) nothing scrolls sideways, navigation becomes a dropdown that lists real destinations, and primary buttons use the .lg size.
- Everything shown on desktop needs a phone version, or an explicit decision to drop it. Do not hide a feature on phones by accident.
- Emphasis comes from weight (600/700), not color. Color carries meaning only: accent = interactive, danger = a problem.
- No shadows, gradients, icons, emoji, pills or badges, tinted callout panels, or web fonts.

## Motion and dark mode

- No motion by default. UI transitions are at most 0.3 s. Honor `prefers-reduced-motion`.
- Dark mode uses the dark column of the token table. It follows the system setting; default is light.

## Other formats

Slides, documents, and spreadsheets: the same palette and hierarchy, Arial, white background, one accent, hairline rules, no decorative backgrounds or clip art. This extends the web rules; the user has not specified it, so say what you chose if it matters.

## Build and check (web)

- Single self-contained HTML file. Inline images as data URIs. System fonts only. Wrap storage calls in try/catch.
- Paste assets/base.css inline and delete the components that are not used.
- Light by default; follow the system dark setting; a manual toggle goes on the reference or settings page, not in the header.
- Before delivering, take screenshots at 1280 × 900 and 390 × 844 in light and dark, and confirm document.documentElement.scrollWidth equals the viewport width at 390.
- Before delivering, open every route and control, use each keyboard shortcut, and load the page with stale localStorage from an earlier version. Zero console errors.
- Test hover on SVG elements by dispatching events, not by coordinates.

## When to read the references

- `references/study-slides.md`: flashcards, quizzes, practice questions, oral-exam preparation.
- `references/linac-dial.md`: navigation built around the rotating linac illustration, for radiation oncology projects.
- `references/jefferson-brand.md`: only when the user asks for Jefferson / TJU branding. Otherwise use this style.

## Basis

- Contrast follows WCAG 2.x (AA 4.5:1, AAA 7:1 for normal text).
- Dark text on a light background is read faster and more accurately than the reverse in most studies.
- For study material, practice testing and distributed practice are rated high-utility and highlighting and rereading low (Dunlosky et al., 2013, Psychological Science in the Public Interest). Mayer's coherence, signaling, and contiguity principles support removing extra elements and keeping labels next to figures.
- Decorative or deliberately hard-to-read fonts have not improved learning in replications.

## Project exception: text roles and question structure (set by the user for this project)

- Three text roles carry meaning in questions and reading text, in addition to the colour rules above: given values are blue (`--given`), the quantity to find is orange and bold (`--find`), a key term at its first definition is green and bold (`--term`). Each meets 4.5:1 on the paper colour in both modes. They are explained on the Reference page under "Text conventions".
- A question is written as a setup sentence, a bulleted list of givens, and a bold question line. Line breaks, bullets, and bold are allowed wherever they make the question easier to read.
- Chapters are numbered (1.4) with numbered sections (1.4.1) and open with an "On this page" list. A chapter heading carries no status line or progress bar; progress is shown in the contents list.
- Each section ends with a "Take away" box: at most three short lines, the minimum a resident must recall cold. Sections that only hold worked examples have none. There is no chapter-level key points list; the take-aways replace it.
- A take-away line may carry a simple animated line drawing. Lines and the palette tokens only (`--fg`, `--mu`, `--gr`, `--c1`/`--c2`), with at most one pale fill. Motion only where it shows the fact. It plays once when the figure scrolls into view and stops within a few seconds, with a Replay button. Under `prefers-reduced-motion` the finished state shows and nothing moves. Controls are at least 36 px tall and labels at least 14 px in the drawing's own units.
- Front page: Home is the default page. It offers Start or Continue, three doors (Contents, Flash cards, Reference) with a counted summary each, and the domain dial under an Exam domains heading. The dial only picks a domain; selecting one lands on Contents at that domain. Contents is the plain list, with no dial.
- Navigation: the header has three sections, Contents, Flash cards, and Reference; Home has no tab and the brand links to it. Each kind of content lives in one place. Reading and practice questions are on topic pages; recall cards are in Flash cards; coverage, sources, and progress are in Reference. A topic page links to its flash cards at the top and the bottom, and a deck links back to its topic. There are no domain pages.
- Data tables: some practice questions print a table (DT) and ask for a lookup, an interpolation, or a chain of looked-up factors. The tables come from one illustrative 6 MV data set (src/beamdata.py) whose PDD and TMR agree through the conversion formula. Answers are worked from the rounded values printed in the table. The full set is on the Reference page and is labelled illustrative.
