"""Brings the questions with several correct answers into line with the ABR item-writing guide: at least twice as many options as correct answers.
Each entry adds one plausible, false option to a question that had three correct answers among five options. Matched by the start of the plain stem."""
import re, blocks
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
EXTRA = {
    ("waves-photons", "Which of these are units of energy?"): "newton",
    ("decay-modes", "Which statements about internal conversion are correct?"): "The ejected electron has a continuous energy spectrum",
    ("photon-interactions", "Which of the following are true of Compton scattering?"): "The incident photon is absorbed completely",
    ("profiles", "Which of these contribute to the penumbra of a photon beam in a patient?"): "The pulse repetition rate of the beam",
    ("dose-algorithms", "Which parameters of a beam model are fitted to measured data?"): "The number of fields in each patient's plan",
}
def apply(topics):
    used = set()
    for t in topics:
        for i, p in enumerate(t["problems"]):
            if not p.get("multi") or len(p["opts"]) >= 2 * len(p["key"]): continue
            hit = [(k, v) for k, v in EXTRA.items() if k[0] == t["id"] and plain(p["stem0"]).startswith(k[1])]
            assert len(hit) == 1, (t["id"], plain(p["stem0"])[:60], len(hit)); (k, extra), = hit; used.add(k)
            correct = [p["opts"][blocks.LETTERS.index(c)] for c in p["key"]]; wrong = [o for o in p["opts"] if o not in correct] + [extra]
            t["problems"][i] = blocks.PRM(p["stem0"], correct, wrong, p["a"][1], w=p["w"], lvl=p["lvl"], fig=p["fig"])
    assert used == set(EXTRA), set(EXTRA) - used
