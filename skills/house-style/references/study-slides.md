# Study slides

Use for flashcards, quizzes, practice questions, and oral-exam preparation. Components: `.slide`, `.key`, `.bar` in `assets/base.css`.

## Slide

- One slide per screen: a topic line, the prompt, numbered questions, an optional figure. All questions are visible together, as on an oral-exam slide.
- The answer (key points) is hidden until Show answer. Space also reveals it.
- Two controls only: Show answer, then Next question. Keys: Space, right arrow (next), left arrow (previous).
- No grading ("knew it / didn't know"), no scores, no revealing one question at a time, no hints.
- Each slide has its own URL hash (1-based), so the browser Back button returns to the previous slide.
- When the answer is below the fold on a phone, scroll just enough to show it. Do not scroll when it is already visible.

## Decks

- Opening a session or category goes straight to slide 1. Do not build a list page that shows prompts with answers. Lists exist only on overview pages (title and seen count).
- Header: "Slide n of N", the deck name, a link to the overview, a 6 px progress bar. The bar shows slides completed over N, so it is empty on slide 1 and full on the end screen.
- End screen: Restart, the overview link, and Next deck if there is one. No score.
- Progress is "seen" per card, stored locally with try/catch. Export and import buttons go on the reference page. Treat stored state as untrusted: an empty or stale list must never break a page.

## Card content

Each card has: topic, subtopic, prompt, numbered questions, optional figure, key points. Key points are facts with units and a source where it matters. Check every number. Do not show deck or file names in the interface.

## ABR Part 3 oral (therapeutic medical physics) structure

- Five categories (ABR TMP oral content guide, 2025): 1 reference and relative dosimetry; 2 treatment machines; 3 external-beam treatment planning, uncertainty management, and treatment planning system QA; 4 brachytherapy, radiation protection, and radiation biology; 5 patient safety, data transfer and integrity, professionalism, and ethics.
- The exam asks one question from each category, so categories have equal weight: draw them as equal-size sections.
- A weekly session is five slides, one per category. Year 1 sessions only use material covered by that month of the first-year rotation calendar; year 2 sessions use everything.
- The examiner bank is a separate question set, encrypted in the page (AES-GCM key from PBKDF2), with expected points shown only to the examiner. A mock oral is one random question per category with a timer.
- Routes: `#y1`, `#y1/s13` (week 13, slide 1), `#y1/s13/3` (slide 3), `#y1/c3` (category 3); `#exam`, `#exam/mock/0`, `#exam/cat/2/1`.
- The ABR Physics Help question bank is copyrighted and is not used; the user's own decks and review notes are.

## Basis

Practice testing and distributed practice are rated high-utility; rereading and highlighting low (Dunlosky et al., 2013). Weekly spaced sessions that mix all five categories follow the same evidence.
