"""No figure has a slider that only moves a marker along a fixed curve. A chart slider must change the plotted series (a slope, a shape, or a position of the curve itself). Any other slider must be on the reviewed list of figures that build a concept."""
import sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
s = open(ROOT / "src" / "app.js", encoding="utf-8").read(); bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
ALLOW = {"wave-energy": "the slider changes the wavelength that is drawn", "magnetic-circle": "the field changes the radius of the circle", "decay-atoms": "a population of atoms decaying at random", "carrier-atoms": "the radioactive fraction changes the atoms drawn",
         "fluence-box": "the sliders change the photons and their energies", "kerma-split": "g changes how the kerma splits", "equivalent-square": "the sides change the rectangle", "backprojection": "more angles build the image", "lor-events": "more events build up the lines", "matter-wave": "the energy changes both wavelengths", "mr-contrast": "TR, TE, and TI change the signal of each tissue, so the picture itself changes"}
starts = [(m.start(), m.group(1)) for m in re.finditer(r"^AV\['([\w-]+)'\]=", s, re.M)]
def trim(b):                                                                  # a figure ends at the first line that starts a new top-level statement; a closing brace at the start of a line still belongs to it
    m = re.search(r"\n(?![\s}\)])", b); return b[:m.start()] if m else b
blocks = {name: trim(s[p:(starts[i + 1][0] if i + 1 < len(starts) else s.index("let avIO=null", p))]) for i, (p, name) in enumerate(starts)}
changing, fixed, custom = [], [], []
for name, b in blocks.items():
    if "avChart(" in b and "slider:" in b and "dyn:" in b:
        ok = "series:" in b[b.index("dyn:"):]; (changing if ok else []).append(name)
        check(ok, f"{name}: the slider only moves a marker along a fixed curve; make it change the curve or draw the points statically")
    elif "avChart(" in b and "fixed:" in b: fixed.append(name)
    elif re.search(r'type=\\?"range\\?"', b):
        custom.append(name); check(name in ALLOW, f"{name}: a slider outside the reviewed list ({name})")
check(not any(re.search(r"\bslider\b", re.sub(r"<[^>]*>", "", c)) for t in [open(f, encoding='utf-8').read() for f in ROOT.glob("chapters/*/*.py")] for c in re.findall(r'P\((?:f)?"([^"]*)"', t)), "no chapter paragraph refers to a slider")
print(f"noslider: {len(changing)} chart sliders change the curve, {len(fixed)} charts are drawn statically with labelled points, {len(custom)} reviewed concept sliders; {n} checks"); print("noslider: PASS" if not bad else f"noslider: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
