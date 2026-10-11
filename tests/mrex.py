"""The MR contrast explorer and the MR artifact gallery on the real brain slice: the tissue fractions, the signal equations, the displayed grey levels, the distortion, the compression, and the susceptibility void agree with independent calculations."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]      # tests/numbers.py would shadow the standard module that numpy imports
import os, io, json, base64, math
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
M = json.load(open(ROOT / "src" / "mr_case.json")); G = json.load(open(ROOT / "src" / "gal_mr.json")); S = G["stats"]; I = {i["id"]: i for i in G["items"]}; bad = []; n = 0; errors = []
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
dec = lambda s: np.array(Image.open(io.BytesIO(base64.b64decode(s.split(",")[1]))))
F = dec(M["frac"]).astype(float) / 255; csf, gm, wm = F[:, :, 0], F[:, :, 1], F[:, :, 2]; h, w = csf.shape
check((h, w) == (M["h"], M["w"]), f"the fraction image is {w} x {h}")
check(float((csf + gm + wm).max()) <= 1.02 and float((csf + gm + wm).min()) >= 0, f"the three tissue fractions never sum to more than 1 ({float((csf + gm + wm).max()):.3f})")
pure = {k: np.argwhere(a >= 0.97) for k, a in (("CSF", csf), ("GM", gm), ("WM", wm))}; check(all(len(v) >= 20 for v in pure.values()), f"pixels of pure CSF, gray matter, and white matter exist: {[(k, len(v)) for k, v in pure.items()]}")
check(0.06 < csf.sum() / (csf + gm + wm).sum() < 0.35 and wm.sum() > gm.sum() * 0.6, f"the slice is {100 * csf.sum() / (csf + gm + wm).sum():.0f}% CSF, {100 * gm.sum() / (csf + gm + wm).sum():.0f}% gray matter, and {100 * wm.sum() / (csf + gm + wm).sum():.0f}% white matter")
T = M["tissue"]
def sig(t, TR, TE, TI):
    e1 = math.exp(-TR / t["T1"]); s = abs(1 - 2 * math.exp(-TI / t["T1"]) + e1) if TI > 0 else (1 - e1); return t["PD"] * s * math.exp(-TE / t["T2"])
def expect(TR, TE, TI):
    s = {k: sig(T[k], TR, TE, TI) for k in ("CSF", "GM", "WM")}; mx = max(s.values()); return {k: v / mx for k, v in s.items()}, mx
# the contrast statements of the chapter, from the equations
t1, _ = expect(500, 15, 0); t2, _ = expect(4000, 100, 0); pdw, _ = expect(4000, 15, 0); fl, _ = expect(9000, 100, 2370)
check(t1["WM"] > t1["GM"] > t1["CSF"], f"T1-weighted: white matter {t1['WM']:.2f} > gray matter {t1['GM']:.2f} > CSF {t1['CSF']:.2f}")
check(t2["CSF"] > t2["GM"] > t2["WM"], f"T2-weighted: CSF {t2['CSF']:.2f} > gray matter {t2['GM']:.2f} > white matter {t2['WM']:.2f}")
check(max(pdw.values()) - min(pdw.values()) < 0.25, f"PD-weighted: the three tissues are within {max(pdw.values()) - min(pdw.values()):.2f} of each other")
check(fl["CSF"] < 0.01 and fl["GM"] > fl["WM"], f"FLAIR: the CSF signal is {fl['CSF']:.4f} and the gray matter is brighter than the white matter")
TI_null = lambda TR: T["CSF"]["T1"] * math.log(2 / (1 + math.exp(-TR / T["CSF"]["T1"]))); check(abs(TI_null(9000) - 2370) < 5, f"the TI that nulls the CSF at TR 9000 ms is {TI_null(9000):.0f} ms")
# the explorer in the page
from playwright.sync_api import sync_playwright
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
gray = lambda href: np.array(Image.open(io.BytesIO(base64.b64decode(href.split(",")[1]))).convert("L")).astype(int)
def setv(pg, sel, v): pg.evaluate("([s,v])=>{const e=document.querySelector(s); e.value=v; e.dispatchEvent(new Event('input',{bubbles:true}));}", [sel, str(v)])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None); pg = b.new_page(viewport={'width': 440, 'height': 900}, color_scheme='light')
    pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(U + "#ref"); pg.goto(U + "#t/mri-sequences"); pg.wait_for_timeout(600); sel = 'figure.av[data-av="mr-contrast"]'; fig = pg.locator(sel); fig.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    out = lambda: pg.locator(sel + " output.avo").inner_text(); img = lambda: gray(pg.locator(sel + " image").get_attribute("href"))
    def verify(TR, TE, TI, label):
        pg.wait_for_timeout(120); e, mx = expect(TR, TE, TI); t = out(); im = img()
        ok = f"TR {TR} ms, TE {TE} ms" in t and all(f"{k} {e[k]:.2f}" in t for k in ("WM", "GM", "CSF"))
        g_ = {k: float(np.mean([im[y, x] for y, x in pure[k]])) for k in pure}; ok2 = all(abs(g_[k] - 255 * e[k]) <= 4.5 for k in pure)          # the 'pure' pixels are at least 97% one tissue, so allow for the last 3%
        check(ok and ok2, f"{label}: readout {t[-62:]}; mean grey of the pure tissues {[(k, round(g_[k])) for k in pure]} against {[(k, round(255 * e[k])) for k in pure]}")
    for k, (nm, (TR, TE, TI)) in enumerate((("T1-weighted", (500, 15, 0)), ("T2-weighted", (4000, 100, 0)), ("PD-weighted", (4000, 15, 0)), ("FLAIR", (9000, 100, 2370)))):
        pg.locator(sel + " button", has_text=nm).click(); verify(TR, TE, TI, nm)
        check(pg.locator(sel + " button", has_text=nm).get_attribute("aria-pressed") == "true", f"{nm} is marked as chosen")
    pg.locator(sel + " button", has_text="T1-weighted").click(); setv(pg, sel + " label:nth-of-type(2) input", 100); verify(500, 100, 0, "T1 settings with TE raised to 100 ms")       # changing a parameter changes the image
    setv(pg, sel + " label:nth-of-type(1) input", 3000); verify(3000, 100, 0, "TR raised to 3000 ms"); setv(pg, sel + " label:nth-of-type(3) input", 1000); verify(3000, 100, 1000, "an inversion time of 1000 ms")
    # the artifact gallery
    pg.goto(U + "#ref"); pg.goto(U + "#t/mri-artifacts"); pg.wait_for_timeout(500); sel = 'figure.av[data-av="mr-gallery-artifacts"]'; btns = pg.locator(sel + " button"); check(btns.count() == 3, "three artifacts to choose from"); hrefs = set()
    for k, i in enumerate(("distortion", "gradient", "susceptibility")):
        btns.nth(k).click(); pg.wait_for_timeout(60); imgs = pg.locator(sel + " image"); a_, b_ = imgs.nth(0).get_attribute("href"), imgs.nth(1).get_attribute("href")
        check(a_ == I[i]["ref"] and b_ == I[i]["img"] and I[i]["facts"] in pg.locator(sel + " output.avo").inner_text(), f"{i}: shows its reference, its image, and its measured fact"); hrefs.add(b_)
    check(len(hrefs) == 3, "each artifact shows a different image")
    b.close()
# the artifacts, measured from the stored pixels
ref = dec(I["distortion"]["ref"]).astype(float); dist = dec(I["distortion"]["img"]).astype(float); grad = dec(I["gradient"]["img"]).astype(float); sus = dec(I["susceptibility"]["img"]).astype(float)
H_, W_ = ref.shape; xc, yc, Rr, Gx, dBe = S["xc"], S["yc"], S["R"], S["G"], S["dBe"]; dxf = lambda x, y: dBe * (((x - xc) ** 2 + (y - yc) ** 2) / (Rr * Rr)) / Gx * 1000.0
def line_pos(img, row, x_guess, wdw=9): seg = img[row, int(x_guess) - wdw:int(x_guess) + wdw + 1]; return int(x_guess) - wdw + int(np.argmax(seg))
res = []
for row in (4, H_ - 5):
    for xin in (40, 100, 120):
        xo = min(np.arange(0, W_, 0.05), key=lambda x: abs(x - dxf(x, row) - xin)); res.append((row, xin, line_pos(dist, row, round(xo)), xo))
check(all(abs(m_ - xo) <= 1.0 for r_, xi, m_, xo in res), f"distortion: the grid lines are where ΔB / G puts them (measured and predicted positions {[(m_, round(xo, 1)) for r_, xi, m_, xo in res]})")
check(max(abs(m_ - xi) for r_, xi, m_, xo in res) >= 3, "distortion: at least one grid line has moved by 3 pixels or more")
gres = [(xin, line_pos(grad, 4, round(xc + (xin - xc) / S["scale"])), xc + (xin - xc) / S["scale"]) for xin in (20, 40, 120, 140)]
check(all(abs(m_ - xo) <= 1.0 for xi, m_, xo in gres), f"gradient: the grid lines are compressed by the factor {S['scale']} about the centre ({[(m_, round(xo, 1)) for xi, m_, xo in gres]})")
check(abs(S["w_true"] / S["w_comp"] - S["scale"]) < 0.02, f"gradient: the brain is {S['w_true']:.0f} mm wide, and {S['w_comp']:.0f} mm in the compressed image")
yy, xx = np.mgrid[:H_, :W_]; rr = np.hypot(xx - S["sus_x0"], yy - S["sus_y0"]); rm = S["sus_r"]
check(sus[rr < rm].mean() < 5 and ref[rr < rm].mean() > 100, f"susceptibility: the metal region is a signal void ({sus[rr < rm].mean():.0f} grey levels, against {ref[rr < rm].mean():.0f} in the reference)")
ring = (rr >= 1.6 * rm) & (rr < 2.6 * rm); check((sus - ref)[ring].max() > 25 and (sus - ref)[ring].min() < -25, f"susceptibility: pile-up and loss of signal around the void (the difference runs from {(sus - ref)[ring].min():.0f} to {(sus - ref)[ring].max():.0f} grey levels)")
vd = float((sus[rr < 14] < 10).sum()); check(0.6 * math.pi * (1.6 * rm) ** 2 <= vd <= 1.5 * math.pi * (1.6 * rm) ** 2, f"susceptibility: the void covers {vd:.0f} pixels (predicted {math.pi * (1.6 * rm) ** 2:.0f})")
check(not errors, f"no console or page errors {errors[:2]}")
print(f"mrex: {n} checks"); print("mrex: PASS" if not bad else f"mrex: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
