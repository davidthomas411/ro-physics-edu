"""The real-CT explorer: the HU values, the tissue picks, the window and level mapping, tapping the image, the bit depth, and the matrix agree with independent calculations."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]      # tests/numbers.py would shadow the standard module that numpy imports
import os, io, json, base64, re
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
G = json.load(open(ROOT / "src" / "gal_ct.json")); n = G["n"]; A = np.frombuffer(base64.b64decode(G["hu"]), dtype="<i2").reshape(n, n).astype(float); P = G["picks"]; bad = []; nc = 0; errors = []
def check(c, m):
    global nc; nc += 1
    if not c: bad.append(m); print("FAIL", m)
check(A.shape == (192, 192) and A.min() >= -1024 and A.max() <= 3071 and abs(G["fov_mm"] - 192 * 0.977) < 1, f"the slice is 192 x 192 with HU between {A.min():.0f} and {A.max():.0f} over a field of view of {G['fov_mm']:.0f} mm")
rng = {"air": (-1024, -900), "fat": (-150, -60), "muscle": (20, 80), "bone": (500, 3071)}
for k, (lo, hi) in rng.items():
    p = P[k]; mean3 = A[max(0, p["y"] - 1):p["y"] + 2, max(0, p["x"] - 1):p["x"] + 2].mean()
    check(lo <= p["hu"] <= hi and abs(round(mean3) - p["hu"]) <= 1, f"{k}: the pick at ({p['x']}, {p['y']}) is {p['hu']} HU, in the {k} range, and equals the mean of its 3 x 3 neighbourhood ({mean3:.1f})")
gray = lambda href: np.array(Image.open(io.BytesIO(base64.b64decode(href.split(",")[1]))).convert("L")).astype(int)
win = lambda hu, w, l: int(np.clip(round((hu - (l - w / 2)) / w * 255), 0, 255))
def setv(pg, sel, v): pg.evaluate("([s,v])=>{const e=document.querySelector(s); e.value=v; e.dispatchEvent(new Event('input',{bubbles:true}));}", [sel, str(v)])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None); pg = b.new_page(viewport={'width': 440, 'height': 900}, color_scheme='light')
    pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(U + "#ref"); pg.goto(U + "#t/ct-reconstruction"); pg.wait_for_timeout(500); sel = 'figure.av[data-av="ct-hu-explorer"]'; fig = pg.locator(sel); fig.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    out = lambda: pg.locator(sel + " output.avo").inner_text(); img = lambda: gray(pg.locator(sel + " image").get_attribute("href")); btn = lambda i: pg.locator(sel + " button").nth(i)
    check(out() == "Window 400, level 40: HU below -160 appear black and above 240 white.", f"the default window readout ({out()})")
    im = img(); check(all(im[P[k]["y"], P[k]["x"]] == win(A[P[k]["y"], P[k]["x"]], 400, 40) for k in P), f"soft-tissue window: the displayed grey at each pick matches (HU - (L - W/2)) / W x 255: {[(k, int(im[P[k]['y'], P[k]['x']])) for k in P]}")
    for i, k in enumerate(("air", "fat", "muscle", "bone")):
        btn(3 + i).click(); t = out(); m = re.search(r"HU at the marker: (-?\d+)", t)
        check(m is not None and int(m.group(1)) == int(A[P[k]["y"], P[k]["x"]]), f"the {k} button reads {m.group(1) if m else None} HU (the pixel is {int(A[P[k]['y'], P[k]['x']])})")
    check("the air range" in (btn(3).click() or out()) and "the bone range" in (btn(6).click() or out()), "the readout names the tissue range")
    btn(1).click(); im = img(); y, x = P["muscle"]["y"], P["muscle"]["x"]; check(im[y, x] == win(A[y, x], 2000, 500) and out().startswith("HU at the marker") and "Window 2000, level 500: HU below -500 appear black and above 1500 white." in out(), f"the bone window changes the grey of the muscle pixel from {win(A[y, x], 400, 40)} to {win(A[y, x], 2000, 500)}")
    setv(pg, sel + " label:nth-of-type(1) input", 200); setv(pg, sel + " label:nth-of-type(2) input", 100); pg.wait_for_timeout(100)
    check("Window 200, level 100: HU below 0 appear black and above 200 white." in out() and img()[y, x] == win(A[y, x], 200, 100), "the window and level sliders set the mapping")
    box = fig.locator("svg").bounding_box(); px, py = 72, 95; cx = box["x"] + (10 + (px + 0.5) / n * 400) / 420 * box["width"]; cy = box["y"] + (6 + (py + 0.5) / n * 400) / 412 * box["height"]; pg.mouse.click(cx, cy); m = re.search(r"HU at the marker: (-?\d+)", out())
    check(m is not None and int(m.group(1)) == int(A[py, px]), f"tapping the image at pixel ({px}, {py}) reads {m.group(1) if m else None} HU (the pixel is {int(A[py, px])})")
    # ---- bit depth and matrix
    pg.goto(U + "#ref"); pg.goto(U + "#t/image-data"); pg.wait_for_timeout(500); sel = 'figure.av[data-av="ct-bits"]'; pg.locator(sel).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    setv(pg, sel + " label:nth-of-type(1) input", 4); pg.wait_for_timeout(100); t = out(); im = img()
    check("4 bits: 16 levels, each 256 HU wide" in t and "holds 1.6 levels" in t, f"4 bits: {t[:110]}")
    check(len(np.unique(im)) <= 6, f"with 4 bits the soft-tissue window shows only {len(np.unique(im))} grey levels")
    setv(pg, sel + " label:nth-of-type(1) input", 12); pg.wait_for_timeout(100); check(len(np.unique(img())) >= 40, f"with 12 bits the image shows {len(np.unique(img()))} grey levels")
    setv(pg, sel + " label:nth-of-type(2) input", 2); pg.wait_for_timeout(100); im = img(); t = out(); blocks = all(np.ptp(im[r:r + 6, c:c + 6]) == 0 for r in range(0, n, 6) for c in range(0, n, 6))
    check(blocks and "Matrix 32 × 32: pixels of 5.9 mm" in t, f"a 32 x 32 matrix gives constant 6 x 6 blocks and 5.9 mm pixels ({t[-40:]})")
    setv(pg, sel + " label:nth-of-type(1) input", 4); setv(pg, sel + " label:nth-of-type(2) input", 6); pg.locator(sel + " button").nth(1).click(); pg.wait_for_timeout(100)
    qd = np.unique(np.minimum(15, np.floor((A + 1024) / 4096 * 16)).astype(int)); check("holds 16 levels" in out() and len(np.unique(img())) == len(qd), f"with the full-range window the 4-bit image shows one grey for each of the {len(qd)} levels that the slice occupies ({len(np.unique(img()))} distinct greys)")
    b.close()
check(not errors, f"no console or page errors {errors[:2]}")
print(f"huex: {nc} checks"); print("huex: PASS" if not bad else f"huex: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
