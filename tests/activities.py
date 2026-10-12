"""Sorting, matching, ranking, and typed-number questions: fact checks on every item, then tap, mouse drag, real touch drag, keyboard, persistence, and typed-answer parsing."""
import sys, re, math, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
from playwright.sync_api import sync_playwright
plain = lambda s: re.sub(r"<[^>]+>", "", s).replace("&lt;", "<").strip()
SORTS = [(t["id"], p) for t in TOPICS for p in t["problems"] if p.get("kind") == "sort"]
bad = []; n = 0
def check(c, msg):
    global n; n += 1
    if not c: bad.append(msg); print("FAIL", msg)
    else: print("ok  ", msg)
def sort_of(phrase):
    h = [(i, p) for i, p in SORTS if phrase in plain(p["q"])]; assert len(h) == 1, (phrase, len(h)); return h[0]
def mapping(p): return {plain(c["t"]): plain(p["bins"][c["b"]]) for c in p["chips"]}
# ---------------------------------------------------------------- facts, entered a second time here and compared with the question data
Zn = {"C-12": 6, "C-14": 6, "N-14": 7, "N-15": 7, "I-125": 53, "I-131": 53, "Xe-132": 54, "Mo-99": 42, "Tc-99": 43, "Tc-99m": 43, "Co-60": 27, "Co-60m": 27}
def fam(a, b):
    A = lambda s: int(re.search(r"-(\d+)", s).group(1)); za, zb, aa, ab = Zn[a], Zn[b], A(a), A(b)
    if za == zb and aa == ab: return "Isomers"
    if za == zb: return "Isotopes"
    if aa == ab: return "Isobars"
    if aa - za == ab - zb: return "Isotones"
    return "none"
_, p = sort_of("isotopes, isotones, isobars, or isomers")
got = {k: v for k, v in mapping(p).items()}
check(all(fam(*k.split(" and ")) == v for k, v in got.items()) and len(got) == 8, "nuclide families re-derived from Z and A for all 8 pairs")
FACTS = {
 "Sort each radionuclide": {"Y-90": "β⁻ emitter", "Lu-177": "β⁻ emitter", "I-131": "β⁻ emitter", "Ir-192": "β⁻ emitter", "F-18": "β⁺ emitter", "I-125": "Electron capture", "Pd-103": "Electron capture", "Ra-223": "α emitter"},
 "Match each decay": {"β⁻": "Z + 1, A unchanged", "β⁺": "Z − 1, A unchanged", "Electron capture": "Z − 1, A unchanged", "α": "Z − 2, A − 4"},
 "leave a vacancy": {"Electron capture": "Leaves a shell vacancy", "Internal conversion": "Leaves a shell vacancy", "β⁻ decay": "Does not", "α decay": "Does not", "γ emission": "Does not"},
 "Match each process to its arrow": {"β⁻": "Down and to the right", "β⁺ or electron capture": "Short, down and to the left", "α": "Steep, down and to the left", "γ or internal conversion": "Straight down"},
 "continuous energy spectrum": {"β⁻ particles": "Continuous spectrum", "β⁺ particles": "Continuous spectrum", "α particles": "Discrete lines", "γ rays": "Discrete lines", "Conversion electrons": "Discrete lines", "Characteristic x-rays": "Discrete lines", "Auger electrons": "Discrete lines"},
 "How is each nuclide produced": {"Co-60": "Neutron capture in a reactor", "Ir-192": "Neutron capture in a reactor", "Cs-137": "Fission product", "Mo-99": "Fission product", "F-18": "Cyclotron"},
 "directly or indirectly": {"Electrons": "Directly ionizing", "Protons": "Directly ionizing", "α particles": "Directly ionizing", "Photons": "Indirectly ionizing", "Neutrons": "Indirectly ionizing"},
 "Which interaction does each": {"Coefficient proportional to Z3/E3": "Photoelectric effect", "Per electron, independent of Z": "Compton scattering", "Needs a photon of at least 1.022 MeV": "Pair production", "Followed by a characteristic x-ray or Auger electron": "Photoelectric effect",
     "Dominates in water from about 30 keV to 24 MeV": "Compton scattering", "Ends with two 511 keV photons": "Pair production", "The electron gets the most energy when the photon backscatters": "Compton scattering", "Gives bone–soft-tissue contrast at kilovoltage energies": "Photoelectric effect"},
 "Match each quantity to its SI unit": {"Fluence": "m−2", "Energy fluence": "J/m²", "Kerma": "Gy (J/kg)", "Absorbed dose": "Gy (J/kg)", "Exposure": "C/kg", "Equivalent dose": "Sv"},
 "radiation weighting factor": {"Photons": "1", "Electrons": "1", "Protons": "2", "α particles": "20"},
 "PDD beyond": {"Beam energy": "PDD rises", "Field size": "PDD rises", "SSD": "PDD rises", "Depth": "PDD falls", "Prescribed dose": "PDD does not change", "Monitor-unit setting": "PDD does not change"},
 "PDD or the TMR": {"Includes the inverse-square fall-off": "PDD", "Does not depend on SSD": "TMR", "Field size is defined at the surface": "PDD", "Field size is defined at the depth of the point": "TMR",
     "Used to calculate SAD treatments": "TMR", "Used to calculate SSD treatments": "PDD", "Source-to-point distance changes with depth": "PDD", "Source-to-point distance stays the same": "TMR"},
 "Rank these isotopes by half-life": {"Cs-131": "1st (shortest)", "Pd-103": "2nd", "I-125": "3rd", "Ir-192": "4th (longest)"},
 "Match each TG-43 factor": {"Inverse-square fall-off for the shape of the source": "G, geometry function", "Scatter and attenuation in water": "g, radial dose function", "Absorption in the capsule and marker along the seed axis": "F, anisotropy function",
     "Dose rate at 1 cm per unit source strength, for the seed model": "Λ, dose rate constant", "The strength of the source, which decays with time": "SK, air kerma strength"},
 "Does each change widen or narrow the penumbra": {"Larger source size": "Widens it", "Smaller focal spot": "Narrows it", "Larger SSD": "Widens it", "Greater depth": "Widens it", "Larger source-to-collimator distance": "Narrows it", "Lower photon energy": "Narrows it", "Lung instead of muscle": "Widens it", "Collimator closer to the source": "Widens it"},
 "raise or lower the skin dose": {"Larger field size": "Raises it", "Couch in the beam path": "Raises it", "Vacuum immobilization bag": "Raises it", "Mask stretched thinner": "Lowers it", "Block tray moved closer to the patient": "Raises it", "Block tray moved farther from the patient": "Lowers it", "Bolus on the skin": "Raises it", "Smaller field size": "Lowers it"},
 "Match each algorithm": {"Tabulated factors with empirical corrections for shape and density": "Correction-based (Clarkson, TAR)", "A sum of narrow beams, each with a depth kernel": "Pencil beam", "TERMA convolved with a density-scaled kernel": "Convolution / superposition", "The Boltzmann transport equation solved on a grid": "Acuros XB", "Individual particle histories sampled at random": "Monte Carlo"},
 "raise or lower the superficial hot spot": {"Thicker patient": "Raises it", "Higher beam energy": "Lowers it", "Larger field size": "Lowers it", "Lateral beams instead of AP/PA on the same patient": "Raises it", "Adding two more fields": "Lowers it", "Lower beam energy": "Raises it", "Thinner patient": "Lowers it", "Smaller field size": "Raises it"},
 "Rank these depths for one electron beam": {"R90": "1st (most superficial)", "R80": "2nd", "R50": "3rd", "Rp": "4th (deepest)"},
 "Is each organ serial or parallel": {"Spinal cord": "Serial: maximum dose", "Lung": "Parallel: mean dose or Vx", "Liver": "Parallel: mean dose or Vx", "Optic nerve": "Serial: maximum dose", "Brainstem": "Serial: maximum dose", "Kidney": "Parallel: mean dose or Vx"},
 "Does each tissue usually have a high or a low": {"Most tumours": "High α/β, about 10 Gy", "Early-responding tissue such as mucosa": "High α/β, about 10 Gy", "Spinal cord, a late-responding tissue": "Low α/β, about 3 Gy", "Lung fibrosis, a late effect": "Low α/β, about 3 Gy", "Skin reaction in the first weeks": "High α/β, about 10 Gy", "Late bowel damage": "Low α/β, about 3 Gy"},
 "Does each change improve, worsen, or leave unchanged the sharpness": {"The object is moved closer to the detector": "Improves sharpness", "A larger focal spot": "Worsens sharpness", "Smaller detector pixels": "Improves sharpness", "A thicker scintillator": "Worsens sharpness", "A higher mA": "No change", "The object is moved closer to the source": "Worsens sharpness"},
 "Which Hounsfield-unit range does each material fall in?": {"Air": "About −1000 HU", "A gas bubble in the bowel": "About −1000 HU", "Water": "About 0 HU", "Distilled water in a phantom": "About 0 HU", "Cortical bone": "About +500 to +1000 HU", "Dense bone": "About +500 to +1000 HU"},
 "Which part of the MRI system does each role belong to?": {"Sets the Larmor frequency and aligns the nuclei, 1 to 3 T": "Main field B0", "Flips the spins at the Larmor frequency": "RF pulse", "Makes the Larmor frequency depend on position": "Gradient", "Detects the changing flux as a current": "Readout coil", "Selects the slice by frequency": "Gradient", "Supplies energy for resonance": "RF pulse"},
 "Is the tissue bright or dark on each type of image?": {"CSF on a T2-weighted image": "Bright", "Fat on a T1-weighted image": "Bright", "CSF on a T1-weighted image": "Dark", "Brain on a T2-weighted image, relative to CSF": "Dark", "CSF on a FLAIR image": "Dark", "A tumour enhanced by gadolinium on a T1-weighted image": "Bright"},
 "Match each MRI artifact to its cause.": {"A metallic object distorts the local field": "Susceptibility", "The gradient is larger than expected": "Gradient distortion", "Protons in different environments precess at different frequencies": "Chemical shift", "The main field bows out at the edge of the bore": "B0 inhomogeneity"},
 "Which process does each PET tracer follow?": {"18F-FDG": "Glucose metabolism", "18F-FMISO": "Hypoxia", "13N-ammonia": "Perfusion", "15O-water": "Perfusion", "18F-fluoride": "Bone metabolism", "FDG in a tumour": "Glucose metabolism"},
 "Put the steps of a monitor-unit": {"Confirm the calibration convention and the technique": "1st", "Find the equivalent square and read Sc, Sp, and the PDD or TMR": "2nd", "Apply the inverse-square term and any wedge or tray factor": "3rd",
     "Multiply the factors to get the dose per monitor unit": "4th", "Divide the prescribed dose by the dose per monitor unit": "5th"},
}
for ph, exp in FACTS.items():
    _, p = sort_of(ph); got = mapping(p); check(got == exp, f"facts match for '{ph}' ({len(exp)} items)" + ("" if got == exp else f": {set(got.items()) ^ set(exp.items())}"))
# specific activity rank and the inverse-square terms are computed, not typed
T = {"Pd-103": (16.99, 102.91), "I-125": (59.4, 124.90), "Ir-192": (73.8, 191.96), "Co-60": (5.27 * 365.25, 59.93), "Cs-137": (30.1 * 365.25, 136.91), "Ra-226": (1600 * 365.25, 226.03)}
S = {k: math.log(2) / (t * 86400) * 6.02214076e23 / m for k, (t, m) in T.items()}; order = sorted(S, key=S.get, reverse=True); _, p = sort_of("Rank these nuclides by specific activity")
check(mapping(p) == {k: ["1st (highest)", "2nd", "3rd", "4th", "5th", "6th (lowest)"][i] for i, k in enumerate(order)}, f"specific-activity ranking computed from half-life and molar mass: {' > '.join(order)}")
for tid, p in SORTS:                                                                          # structure
    m, cap, nb, nc = p["mode"], p.get("cap"), len(p["bins"]), len(p["chips"]); occ = [sum(1 for c in p["chips"] if c["b"] == b) for b in range(nb)]; txt = [plain(c["t"]) for c in p["chips"]]
    ok = 3 <= nc <= 8 and len(set(txt)) == nc and len({plain(b) for b in p["bins"]}) == nb and (not cap or max(occ) <= cap) and (m == "rank" and sorted(c["b"] for c in p["chips"]) == list(range(nb)) or m != "rank") and (m in ("match", "rank") or min(occ) >= 1)
    if not ok: bad.append((tid, "sort structure", plain(p["q"])[:50], occ))
check(not [b for b in bad if b[1:2] == ("sort structure",)], f"all {len(SORTS)} sorting questions: 3 to 8 unique items, unique bins, capacity respected, no empty bin")
# ---------------------------------------------------------------- browser
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
def cid(pg, phrase): return pg.evaluate("ph=>{const c=DATA.cards.find(c=>c.opts&&(c.q||'').replace(/<[^>]+>/g,'').includes(ph)); return c&&c.id}", phrase)
def open_q(pg, phrase):
    pg.goto(U + "#ref"); c = cid(pg, phrase); assert c, phrase; pg.goto(U + "#home"); pg.goto(U + "#t/" + c.split(":")[0]); pg.wait_for_timeout(250)
    q = pg.locator(f'.pq[data-id="{c}"]'); pg.evaluate("el=>window.scrollTo(0,el.getBoundingClientRect().top+scrollY-130)", q.element_handle()); pg.wait_for_timeout(80); return c, q
def tap_all(q, p, skip=()):
    for c in p["chips"]:
        t = plain(c["t"])
        if t in skip: continue
        q.locator(".chip", has_text=t).first.click(); q.locator(f'.bin[data-b="{c["b"]}"] .bh').click()
def where(q, text):                                                                           # which bin holds this chip (-1 = tray)
    return q.evaluate("(el,t)=>{const c=[...el.querySelectorAll('.chip')].find(c=>c.firstChild&&c.textContent.startsWith(t)); const b=c&&c.closest('.bin'); return b?+b.dataset.b:-1}", text)
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    ctx = b.new_context(viewport={"width": 1100, "height": 900}, color_scheme="light"); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    _, P = sort_of("Sort each radionuclide")
    c, q = open_q(pg, "Sort each radionuclide")
    check(q.locator(".chk").is_disabled() and q.locator(".chip").count() == 8, "sorting question: 8 items in the tray and Check is disabled at the start")
    tap_all(q, P, skip=("Ra-223",)); check(q.locator(".chk").is_disabled(), "Check stays disabled with one item unplaced")
    q.locator(".chip", has_text="Ra-223").first.click(); q.locator('.bin[data-b="3"] .bh').click(); check(q.locator(".chk").is_enabled(), "Check enables once every item is placed")
    q.locator(".chk").click(); res = q.locator(".res").inner_text()
    check(res == "All correct." and q.locator(".chip.right").count() == 8 and q.evaluate("el=>el.classList.contains('done')"), f"tap to place, all 8 correct: '{res}'")
    pg.reload(); pg.wait_for_timeout(250); q = pg.locator(f'.pq[data-id="{c}"]')
    check(q.evaluate("el=>el.classList.contains('done')") and q.locator(".chip.right").count() == 8 and pg.evaluate("id=>!!qSel(id)", c), "the placements are saved and restored after a reload")
    q.locator(".again").click(); check(q.locator(".tray .chip").count() == 8 and q.locator(".chk").is_disabled() and pg.evaluate("id=>!qSel(id)", c), "Try again puts all items back and clears the saved answer")
    tap_all(q, P, skip=("Ir-192",)); q.locator(".chip", has_text="Ir-192").first.click(); q.locator('.bin[data-b="1"] .bh').click(); q.locator(".chk").click()
    wrong = q.locator(".chip.wrong"); check(q.locator(".res").inner_text() == "7 of 8 in the right place." and wrong.count() == 1 and "β⁻ emitter" in wrong.first.inner_text(), f"one wrong item is marked and names its bin: '{q.locator('.res').inner_text()}'")
    q.locator(".again").click()
    # mouse drag, tray to bin and back
    f18 = q.locator(".chip", has_text="F-18").first; bb, tb = f18.bounding_box(), q.locator('.bin[data-b="1"]').bounding_box()
    pg.mouse.move(bb["x"] + 10, bb["y"] + 10); pg.mouse.down(); pg.mouse.move(tb["x"] + 40, tb["y"] + 40, steps=10); pg.mouse.up(); pg.wait_for_timeout(100)
    check(where(q, "F-18") == 1 and not q.evaluate("el=>!!document.querySelector('.chip.drag')"), "mouse drag drops an item into the bin under the pointer")
    f18 = q.locator(".chip", has_text="F-18").first; bb = f18.bounding_box(); tr = q.locator(".tray").bounding_box()
    pg.mouse.move(bb["x"] + 10, bb["y"] + 10); pg.mouse.down(); pg.mouse.move(tr["x"] + 20, tr["y"] + 20, steps=10); pg.mouse.up(); pg.wait_for_timeout(100)
    check(where(q, "F-18") == -1, "mouse drag back onto the tray returns the item")
    # keyboard: select with Enter, place with the Place here button, Escape cancels
    q.locator(".chip", has_text="Y-90").first.focus(); pg.keyboard.press("Enter"); pr = q.locator('.bin[data-b="0"] .place')
    check(pr.is_visible() and q.locator('.chip[aria-pressed="true"]').count() == 1, "keyboard: Enter selects an item and reveals the Place here buttons")
    pg.keyboard.press("Escape"); check(q.locator('.chip[aria-pressed="true"]').count() == 0, "Escape cancels the selection")
    q.locator(".chip", has_text="Y-90").first.focus(); pg.keyboard.press("Enter"); pr.focus(); pg.keyboard.press("Enter"); check(where(q, "Y-90") == 0, "keyboard: the Place here button puts the selected item in that bin")
    q.locator(".reset").click(); check(q.locator(".tray .chip").count() == 8, "Start over empties the bins before checking")
    # capacity 1: a second item replaces the first, and a move into an occupied slot swaps
    _, P2 = sort_of("Match each process to its arrow"); c2, q2 = open_q(pg, "Match each process to its arrow")
    q2.locator(".chip", has_text="β⁻").first.click(); q2.locator('.bin[data-b="0"] .bh').click(); q2.locator(".chip", has_text="α").first.click(); q2.locator('.bin[data-b="0"] .bh').click()
    check(where(q2, "α") == 0 and where(q2, "β⁻") == -1, "capacity 1: placing a second item in an occupied slot sends the first back to the tray")
    q2.locator(".chip", has_text="β⁻").first.click(); q2.locator('.bin[data-b="1"] .bh').click(); q2.locator(".chip", has_text="β⁻").first.click(); q2.locator('.bin[data-b="0"] .bh').click()
    check(where(q2, "β⁻") == 0 and where(q2, "α") == 1, "capacity 1: moving an item into an occupied slot swaps the two")
    # ranking by tap
    _, P3 = sort_of("Put the steps of a monitor-unit"); c3, q3 = open_q(pg, "Put the steps of a monitor-unit"); tap_all(q3, P3); q3.locator(".chk").click()
    check(q3.locator(".res").inner_text() == "All correct." and "Rank" in q3.locator(".meta").inner_text(), "ranking question: the five steps in order are marked correct, and the card says Rank")
    # typed answers
    c4, q4 = open_q(pg, "A field with both a wedge and a blocking tray"); inp = q4.locator(".numin"); chk = q4.locator(".chk")
    check(chk.is_disabled() and "Type the answer" in q4.locator(".meta").inner_text(), "typed question: Check is disabled until something is typed")
    def tryit(txt):
        inp.fill(txt); chk.click() if chk.is_enabled() else None
        r = (q4.locator(".res").inner_text() if q4.locator(".fb").is_visible() else "", q4.locator(".msg").is_visible()); return r
    def again(): q4.locator(".again").click()
    for txt in ("281.2", "2.812e2", "2.812 × 10^2", "281", "280", "2.812x10^2"):
        r = tryit(txt); check(r[0] == "Correct.", f"typed '{txt}' is accepted ({r[0]})"); again()
    r = tryit("272.7"); check(r[0].startswith("Not quite. The answer is 281.2 MU"), f"typed '272.7' (the tray factor left out) is rejected and the answer is shown ({r[0]})"); again()
    inp.fill("abc"); chk.click(); check(q4.locator(".msg").is_visible() and not q4.locator(".fb").is_visible(), "text that is not a number gets a message and is not scored")
    inp.fill("281.2"); pg.keyboard.press("Enter"); check(q4.locator(".res").inner_text() == "Correct.", "Enter submits a typed answer")
    pg.reload(); pg.wait_for_timeout(250); q4 = pg.locator(f'.pq[data-id="{c4}"]'); check(q4.locator(".numin").input_value() == "281.2" and q4.locator(".res").inner_text() == "Correct.", "a typed answer is saved and restored after a reload")
    # layout and progress
    for tid in ("decay-modes", "photon-interactions", "kerma-dose", "mu-calc"):
        pg.goto(U + "#ref"); pg.goto(U + "#t/" + tid); pg.wait_for_timeout(200)
    nq = pg.evaluate("DATA.cards.filter(c=>c.opts).length"); per = pg.evaluate("DATA.topics.map(t=>quizOf(t.id).length).reduce((a,b)=>a+b,0)")
    check(nq == per, f"the new item types count as questions in their topics' sets ({nq} in all, {per} in the sets)")
    check(not errs, f"no console or page errors on desktop {errs[:2]}")
    # phone: touch drag, tap, layout
    mc = b.new_context(viewport={"width": 390, "height": 844}, color_scheme="light", has_touch=True, is_mobile=True); mp = mc.new_page(); merrs = []
    mp.on("pageerror", lambda e: merrs.append(str(e))); cdp = mc.new_cdp_session(mp)
    c, q = open_q(mp, "Sort each radionuclide"); sy0 = mp.evaluate("scrollY")
    for bn in range(4): q.locator(f'.bin[data-b="{bn}"]').scroll_into_view_if_needed()
    q.locator(".tray").scroll_into_view_if_needed(); mp.evaluate("window.scrollBy(0,-60)"); mp.wait_for_timeout(100)
    def drag_touch(chip_text, bin_i):
        ch = q.locator(".chip", has_text=chip_text).first; cb = ch.bounding_box(); bx = q.locator(f'.bin[data-b="{bin_i}"] .bh').bounding_box(); y0 = mp.evaluate("scrollY")
        x0, y0c, x1, y1 = cb["x"] + cb["width"] / 2, cb["y"] + cb["height"] / 2, bx["x"] + 30, bx["y"] + bx["height"] / 2
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0c}]})
        for k in range(1, 13): cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * k / 12, "y": y0c + (y1 - y0c) * k / 12}]})
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); mp.wait_for_timeout(120); return mp.evaluate("scrollY") - y0
    tb = q.locator(".tray").bounding_box(); bb = q.locator('.bin[data-b="1"]').bounding_box(); both = tb["y"] >= 0 and bb["y"] + bb["height"] <= 844
    moved = drag_touch("F-18", 1); check(where(q, "F-18") == 1 and abs(moved) < 2, f"touch drag on a phone drops an item into a bin and the page does not scroll (scroll change {moved:.0f}px, both in view: {both})")
    q.locator(".chip", has_text="Y-90").first.tap(); q.locator('.bin[data-b="0"] .bh').tap(); check(where(q, "Y-90") == 0, "tap an item, then tap a bin, on a phone")
    h = q.evaluate("el=>Math.min(...[...el.querySelectorAll('.chip')].map(c=>c.getBoundingClientRect().height))"); check(h >= 36, f"items are at least 36 px tall for touch (min {h:.0f}px)")
    for tid in ("decay-modes", "decay-schemes", "photon-interactions", "kerma-dose", "mu-calc", "scatter"):
        mp.goto(U + "#ref"); mp.goto(U + "#t/" + tid); mp.wait_for_timeout(200)
        w = mp.evaluate("[document.documentElement.scrollWidth, innerWidth, Math.max(0,...[...document.querySelectorAll('.pq.sortq, .pq.numq')].map(e=>e.scrollWidth-e.clientWidth))]"); check(w[0] <= w[1] and w[2] <= 0, f"{tid}: no sideways scroll at 390 px, sorting and typed cards fit {w}")
    check(not merrs, f"no page errors on the phone {merrs[:2]}")
    b.close()
print(f"activities: {n} checks"); print("activities: PASS" if not bad else f"activities: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
