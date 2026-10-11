"""The simulated radiographs of a real patient: the contrast, noise, scatter, and grid effects agree with independent calculations, are visible in the stored pixels, and the galleries work in the page."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]      # tests/numbers.py would shadow the standard module that numpy imports
import os, io, json, base64, math
import numpy as np
from PIL import Image
from scipy.interpolate import interp1d
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT / "src"))
import nistdata as N
D = json.load(open(ROOT / "src" / "gal_drr.json")); S = D["stats"]; I = {i["id"]: i for i in D["items"]}; H, W = S["H"], S["W"]; bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
dec = lambda s: np.array(Image.open(io.BytesIO(base64.b64decode(s.split(",")[1]))).convert("L")).astype(float)
check(sorted(I) == ["grid", "mv", "noise-high", "noise-low", "noise-mid", "scatter"], f"the six views: {sorted(I)}")
check(all(dec(i["img"]).shape == (H, W) and dec(i["ref"]).shape == (H, W) for i in D["items"]) and W / H > 1.4, f"every image and reference is {H} x {W}")
# the contrast of 2 cm of bone against 2 cm of water, worked out separately from the table
def mu(tab, e):
    ks = sorted(tab); f = interp1d(np.log([k * 1000 for k in ks]), np.log([tab[k][0] for k in ks]), kind="linear"); return float(np.exp(f(np.log(e))))
def contrast(E, Wt):
    Wt = np.array(Wt) / sum(Wt); a = sum(w * math.exp(-mu(N.WATER, e) * 10) for w, e in zip(Wt, E)); b = sum(w * math.exp(-(mu(N.WATER, e) * 8 + mu(N.BONE, e) * 2 * 1.92)) for w, e in zip(Wt, E)); return math.log(a / b)
ckv = contrast([30, 40, 50, 60, 70, 80], [0.08, 0.22, 0.28, 0.24, 0.13, 0.05]); cmv = contrast([1000, 1500, 2000, 3000, 4000], [0.25, 0.30, 0.25, 0.15, 0.05])
check(abs(ckv - S["c_kv"]) < 0.01 * ckv and abs(cmv - S["c_mv"]) < 0.01 * cmv, f"the contrast of 2 cm of bone: {ckv:.3f} at kV and {cmv:.4f} at MV, as stored ({S['c_kv']:.3f}, {S['c_mv']:.4f})")
check(8 <= ckv / cmv <= 16, f"the subject contrast of bone is {ckv / cmv:.1f} times smaller at megavoltage energy")
check(S["gray_kv"] > S["gray_mv"] > 5, f"in the displayed images the bone region is {S['gray_kv']:.0f} grey levels from the soft tissue at kV and {S['gray_mv']:.0f} at MV")
r = S["noise_low"] / S["noise_high"]; check(S["noise_high"] < S["noise_mid"] < S["noise_low"] and 3.4 <= r <= 4.8, f"noise rises as the exposure falls: {S['noise_high']:.3f}, {S['noise_mid']:.3f}, {S['noise_low']:.3f}; a factor of {r:.2f} for a 16-fold fall (1/sqrt predicts 4)")
spr, tp, ts = S["SPR"], S["TP"], S["TS"]
check(abs(S["spr_in"] - spr) < 0.01 and abs(S["spr_grid"] - spr * ts / tp) < 0.01 * spr, f"the scatter-to-primary ratio is {S['spr_in']:.2f} without the grid and {S['spr_grid']:.2f} with it (analytic {spr * ts / tp:.2f})")
check(abs(S["bucky"] - (1 + spr) / (tp + ts * spr)) < 0.01 * S["bucky"], f"the Bucky factor is {S['bucky']:.2f} (analytic {(1 + spr) / (tp + ts * spr):.2f})")
check(S["con_scatter"] < 0.5 * S["con_primary"] and S["con_with_grid"] > 1.5 * S["con_scatter"] and S["con_with_grid"] < S["con_primary"], f"scatter lowers the contrast to {S['con_scatter'] / S['con_primary']:.2f} and the grid restores it to {S['con_with_grid'] / S['con_primary']:.2f}")
# measured from the stored pixels
br, bc = S["roi_bone"]; sr, sc = S["roi_soft"]
def roi(a, r_, c_, k=3): return a[r_ - k:r_ + k + 1, c_ - k:c_ + k + 1]
gd = lambda a: float(roi(a, br, bc).mean() - roi(a, sr, sc).mean())
ref = dec(I["noise-high"]["ref"]); g_ref, g_sc, g_gr = gd(ref), gd(dec(I["scatter"]["img"])), gd(dec(I["grid"]["img"]))
check(g_ref > g_gr > g_sc > 0, f"in the stored images the bone region is {g_ref:.0f} grey levels from the soft tissue in the reference, {g_sc:.0f} with scatter, and {g_gr:.0f} with the grid")
sds = {k: float(np.std((dec(I[k]["img"]) - ref)[sr - 7:sr + 8, sc - 7:sc + 8])) for k in ("noise-high", "noise-mid", "noise-low")}
check(sds["noise-high"] < sds["noise-mid"] < sds["noise-low"] and 3.0 <= sds["noise-low"] / sds["noise-high"] <= 5.5 and sds["noise-low"] >= 3, f"noise measured in the stored images: {sds['noise-high']:.1f}, {sds['noise-mid']:.1f}, {sds['noise-low']:.1f} grey levels")
mvg = dec(I["mv"]["img"]); body = ref > 20; check(abs(np.corrcoef(mvg[body], ref[body])[0, 1]) > 0.8 and not np.array_equal(mvg, ref), "the megavoltage image shows the same anatomy as the kilovoltage image")
# in the page
from playwright.sync_api import sync_playwright
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri(); errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None); pg = b.new_page(viewport={'width': 440, 'height': 900}, color_scheme='light')
    pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(U + "#ref"); pg.goto(U + "#t/radiographic-quality"); pg.wait_for_timeout(500)
    for fid, ids in (("drr-gallery-contrast", ["mv"]), ("drr-gallery-noise", ["noise-high", "noise-mid", "noise-low"]), ("drr-gallery-scatter", ["scatter", "grid"])):
        sel = f'figure.av[data-av="{fid}"]'; btns = pg.locator(sel + " button"); check(btns.count() == len(ids), f"{fid}: {len(ids)} effects")
        vb = pg.locator(sel + " svg").get_attribute("viewBox").split(); check(float(vb[3]) > 0.8 * float(vb[2]) * H / W, f"{fid}: the reference and the effect are stacked for the wide image")
        for k, i in enumerate(ids):
            btns.nth(k).click(); pg.wait_for_timeout(60); imgs = pg.locator(sel + " image"); a_, b_ = imgs.nth(0).get_attribute("href"), imgs.nth(1).get_attribute("href"); out = pg.locator(sel + " output.avo").inner_text()
            check(a_ == I[i]["ref"] and b_ == I[i]["img"] and I[i]["facts"] in out, f"{fid}: {i} shows its reference, its image, and its measured fact")
    b.close()
check(not errors, f"no console or page errors {errors[:2]}")
print(f"drr: {n} checks"); print("drr: PASS" if not bad else f"drr: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
