# Explanation format for calculation questions

A reader who does not know the topic must be able to follow the explanation line by line. The format is implemented; this file is the rule for applying it chapter by chapter.

## Which questions need steps

Any question whose keyed answer is computed: PRN, TYPED, and any PR or PRM whose correct option comes from a calculation. Concept questions (PR, PRM, SORT, FIGQ with no arithmetic) stay a single line in `why`.

## How to write them

- Pass the steps as the existing `w` argument, as a list of `STEP(label, sym, vals, result, where="")` from `src/blocks.py`.
- `label`: two to four plain words naming what is found ("Electron momentum"), not a sentence.
- `sym`: the relation in symbols, with real symbols and `<sub>`/`<sup>` (λ, √, ², T<sub>1/2</sub>). No numbers.
- `where`: what the terms are, one short clause, only for terms the stem does not define. Optional.
- `vals`: the same relation with the values put in, units on every value that has one. Do not repeat the result here.
- `result`: the number with its unit, shown bold after "=". Compute every number in code (an f-string over a `calc.py` value or a variable at the top of the topic file), never by hand; tests/numbers*.py re-derive it by another route.
- One relation per step; a step feeds the next. Typically two to four steps. Split a conversion into its own step only if the reader could miss it.
- The numbered steps show first under "Explanation". `why` follows as one or two sentences: why the keyed answer is right, which mistake each distractor catches. It must not repeat the arithmetic and must not name option letters (letters are shuffled).
- Plain-string `w` items still work and show after `why`; convert them when you touch the question.

## Example (src/topics/tmr.py, TMR from a PDD)

```python
w=[STEP("Distance factor", "F = [(f + d) / (f + d<sub>max</sub>)]²", "F = (115 / 101.5)²",
        f"{F:.3f}", "f is the SSD, d the depth, and d<sub>max</sub> the depth of maximum dose, all in cm"),
   STEP("TMR", "TMR = (PDD / 100) × F × S<sub>p</sub> ratio", f"TMR = 0.580 × {F:.3f} × 1", f"{tmr:.3f}")]
```

with `why` = "Using the PDD unchanged gives 0.580, leaving out the square gives 0.657, and inverting the ratio gives 0.452."

Check each converted chapter at 1280 × 900 and 390 × 844, light and dark, with no sideways scroll.
