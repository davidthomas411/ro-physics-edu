"""The simulated CT effects on the real slice: each effect is measured from the stored image pixels, and agrees with its physical cause. The galleries work in the page."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]      # tests/numbers.py would shadow the standard module that numpy imports
import os, io, json, base64
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT = Path(__file__).resolve().parent.parent
G = json.load(open(ROOT / "src" / "gal_ct.json")); S = G["stats"]; N = G["n"]; I = {i["id"]: i for i in G["items"]}; bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
dec = lambda s: np.array(Image.open(io.BytesIO(base64.b64decode(s.split(",")[1]))).convert("L")).astype(float)
check(sorted(I) == sorted(["noise-high", "noise-mid", "noise-low", "filter-sharp", "filter-smooth", "beam-hardening", "metal", "ring", "motion", "scatter"]), f"the ten simulated views: {sorted(I)}")
check(all(dec(i["img"]).shape == (N, N) and dec(i["ref"]).shape == (N, N) for i in G["items"]), f"every image and reference is {N} x {N}")
check(all(len(i["cap"]) > 60 and len(i["facts"]) > 15 for i in G["items"]), "every view has an explanation and a measured fact")
# the statistics of the simulation, against the physics
r = S["noise_low"] / S["noise_high"]
check(S["noise_high"] < S["noise_mid"] < S["noise_low"] and 3.5 <= r <= 4.6, f"noise rises as the exposure falls: {S['noise_high']:.1f}, {S['noise_mid']:.1f}, {S['noise_low']:.1f} HU, a factor of {r:.2f} for a 16-fold fall in exposure (1/sqrt predicts 4)")
check(1.5 <= S["noise_mid"] / S["noise_high"] <= 2.6 and 1.5 <= S["noise_low"] / S["noise_mid"] <= 2.6, "each 4-fold fall in exposure roughly doubles the noise")
check(S["sd_sharp"] / S["sd_smooth"] >= 1.8, f"the sharp filter is noisier than the smooth filter by a factor of {S['sd_sharp'] / S['sd_smooth']:.1f}")
check(S["bh_rim"] - S["bh_core"] >= 15 and S["sc_rim"] - S["sc_core"] >= 40, f"beam hardening and scatter both give cupping (centre below periphery by {S['bh_rim'] - S['bh_core']:.0f} and {S['sc_rim'] - S['sc_core']:.0f} HU)")
check(S["ring_peak"] <= -30 and 15 <= S["ring_r"] <= 30, f"a faulty detector channel gives a ring of {S['ring_peak']:.0f} HU at {S['ring_r']} pixels")
check(S["metal_sd"] >= 3 * S["metal_ref_sd"] and S["motion_sd"] >= 5 * S["motion_ref_sd"], f"metal and motion raise the spread of soft-tissue values ({S['metal_ref_sd']:.0f} to {S['metal_sd']:.0f} HU, and {S['motion_ref_sd']:.0f} to {S['motion_sd']:.0f} HU)")
# the images themselves
ref_d = dec(I["noise-high"]["ref"]); check(all(np.array_equal(dec(I[k]["ref"]), ref_d) for k in ("noise-mid", "noise-low", "filter-sharp", "filter-smooth")), "the views that share a window share one reference image")
body = ndi.binary_fill_holes(ref_d > 8); core = ndi.binary_erosion(body, iterations=22) & (ref_d > 60) & (ref_d < 160); rim = body & ~ndi.binary_erosion(body, iterations=14) & (ref_d > 60) & (ref_d < 160)
soft = dec(I["scatter"]["ref"]); softbody = ndi.binary_fill_holes(soft > 8); core2 = ndi.binary_erosion(softbody, iterations=22); rim2 = softbody & ~ndi.binary_erosion(softbody, iterations=14)
for k in ("beam-hardening", "scatter"):
    d = dec(I[k]["img"]) - dec(I[k]["ref"]); check(d[core2].mean() < d[rim2].mean() - 10, f"{k}: in the stored image the centre is darker than the rim by {d[rim2].mean() - d[core2].mean():.0f} grey levels")
d = {k: dec(I[k]["img"]) - ref_d for k in ("noise-high", "noise-mid", "noise-low")}; roi = ndi.binary_erosion(body, iterations=22) & (ref_d > 60) & (ref_d < 160)
sds = {k: float(np.std(v[roi])) for k, v in d.items()}; check(sds["noise-high"] < sds["noise-mid"] < sds["noise-low"] and 2.8 <= sds["noise-low"] / sds["noise-high"] <= 5.5, f"noise measured in the stored images: {sds['noise-high']:.1f}, {sds['noise-mid']:.1f}, {sds['noise-low']:.1f} grey levels")
rg = dec(I["ring"]["img"]) - dec(I["ring"]["ref"]); yy, xx = np.mgrid[:N, :N]; rad = np.hypot(yy - N / 2, xx - N / 2).astype(int); rb = ndi.binary_fill_holes(dec(I["ring"]["ref"]) > 8)
prof = np.array([rg[(rad == k) & rb].mean() if ((rad == k) & rb).sum() > 10 else 0 for k in range(0, 80)]); r0 = S["ring_r"]
check(prof[r0 - 1:r0 + 2].mean() < 0.5 * (prof[r0 - 6:r0 - 3].mean() + prof[r0 + 4:r0 + 7].mean()) - 10, f"ring: the stored image has a dip of {0.5 * (prof[r0 - 6:r0 - 3].mean() + prof[r0 + 4:r0 + 7].mean()) - prof[r0 - 1:r0 + 2].mean():.0f} grey levels at radius {r0} pixels")
mo = dec(I["motion"]["img"]) - dec(I["motion"]["ref"]); check(np.abs(mo[core2]).mean() > 4 * np.abs(rg[core2]).mean() * 0.4 and np.abs(mo[body]).mean() > 6, "motion changes the stored image throughout the body")
mt = dec(I["metal"]["img"]) - dec(I["metal"]["ref"]); check(np.abs(mt[body]).mean() > 10, f"metal: the stored image differs from the reference by {np.abs(mt[body]).mean():.0f} grey levels on average (the window is 800 HU wide, so a level is about 3 HU)")
# in the page
from playwright.sync_api import sync_playwright
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri(); errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None); pg = b.new_page(viewport={'width': 440, 'height': 900}, color_scheme='light')
    pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(U + "#ref"); pg.goto(U + "#t/ct-quality"); pg.wait_for_timeout(500)
    for fid, ids in (("ct-gallery-noise", ["noise-high", "noise-mid", "noise-low", "filter-sharp", "filter-smooth"]), ("ct-gallery-artifacts", ["beam-hardening", "metal", "ring", "motion", "scatter"])):
        sel = f'figure.av[data-av="{fid}"]'; btns = pg.locator(sel + " button"); check(btns.count() == len(ids), f"{fid}: {len(ids)} effects to choose from")
        hrefs = set()
        for k, i in enumerate(ids):
            btns.nth(k).click(); pg.wait_for_timeout(60); imgs = pg.locator(sel + " image"); a, bb = imgs.nth(0).get_attribute("href"), imgs.nth(1).get_attribute("href"); out = pg.locator(sel + " output.avo").inner_text()
            check(a == I[i]["ref"] and bb == I[i]["img"] and I[i]["facts"] in out and btns.nth(k).get_attribute("aria-pressed") == "true", f"{fid}: {i} shows its reference, its image, and its measured fact"); hrefs.add(bb)
        check(len(hrefs) == len(ids), f"{fid}: each effect shows a different image")
    b.close()
check(not errors, f"no console or page errors {errors[:2]}")
print(f"ctart: {n} checks"); print("ctart: PASS" if not bad else f"ctart: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
