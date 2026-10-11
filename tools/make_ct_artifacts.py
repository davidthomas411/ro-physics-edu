"""Simulated CT artifacts on a real anatomical slice. The anatomy is one axial CT slice of OpenKBP patient pt_14 (Babier et al., Med Phys 2021).
The artifacts come from a physical simulation: a polychromatic 120 kVp spectrum, attenuation of water and bone from the NIST tables, Poisson noise, and filtered backprojection (scikit-image).
Usage: python tools/make_ct_artifacts.py /path/to/pt_14   (writes src/gal_ct.json)"""
import sys, os, io, json, base64, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from PIL import Image
from scipy import ndimage as ndi
from skimage.transform import radon, iradon, resize
import nistdata as N

PT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/okbp/provided-data/train-pats/pt_14"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "gal_ct.json")
NPIX, PX = 192, 0.0977                                                  # image size and pixel size in cm (the original voxels are 3.9 mm; they are interpolated to 0.98 mm)
ENERGIES = np.array([35, 45, 55, 65, 75, 85, 95, 105, 115], float); W = np.array([0.03, 0.09, 0.14, 0.17, 0.18, 0.15, 0.12, 0.08, 0.04]); W /= W.sum()      # illustrative 120 kVp spectrum
def mu_rho(tab, e_kev):
    ks = sorted(tab); x = np.log([k * 1000 for k in ks]); y = np.log([tab[k][0] for k in ks]); return float(np.exp(np.interp(np.log(e_kev), x, y)))
MW = np.array([mu_rho(N.WATER, e) for e in ENERGIES]); MB = np.array([mu_rho(N.BONE, e) for e in ENERGIES]); ML = np.array([mu_rho(N.LEAD, e) if e >= 50 else mu_rho(N.LEAD, 50) for e in ENERGIES])
ENERGIES2 = np.array([25, 32, 40, 48, 56, 64], float); W2 = np.array([0.10, 0.22, 0.26, 0.22, 0.14, 0.06]); W2 /= W2.sum()      # a softer, low-kVp spectrum, which hardens more
MW2 = np.array([mu_rho(N.WATER, e) for e in ENERGIES2]); MB2 = np.array([mu_rho(N.BONE, e) for e in ENERGIES2])
E_EFF = 70.0; MW70, MB70 = mu_rho(N.WATER, E_EFF), mu_rho(N.BONE, E_EFF)
# ---- the real slice
def arr(f, mask=False):
    d = pd.read_csv(os.path.join(PT, f + ".csv"), index_col=0); a = np.zeros(128 ** 3, np.float32); a[d.index.values] = 1 if mask else d.iloc[:, 0].values; return a.reshape(128, 128, 128)
ct = arr("ct") - 1024; ptv = arr("PTV70", True); zs = np.where(ptv.sum((0, 1)) > 0)[0]; z = int(zs.mean()) - 2
sl = np.clip(ct[:, :, z], -1000, 2500); body0 = ndi.binary_fill_holes(sl > -300); rr, cc = np.where(body0); sl = sl[rr.min() - 2:rr.max() + 3, cc.min() - 2:cc.max() + 3]
sl = np.where(sl < -900, -1000, sl); up = np.clip(resize(sl, (sl.shape[0] * 4, sl.shape[1] * 4), order=3, mode="edge", anti_aliasing=False), -1000, 2500)
HU = np.full((NPIX, NPIX), -1000.0); r0, c0 = (NPIX - up.shape[0]) // 2, (NPIX - up.shape[1]) // 2; HU[r0:r0 + up.shape[0], c0:c0 + up.shape[1]] = up
BODY = ndi.binary_fill_holes(HU > -300)
def maps(hu):                                                           # water-equivalent and bone-equivalent densities (g/cm3) that reproduce the HU at 70 keV
    aw = np.clip(1 + hu / 1000.0, 0, 1.0); ab = np.maximum(hu, 0) / 1000.0 * MW70 / MB70; return aw, ab
AW, AB = maps(HU)
THETA = np.linspace(0, 180, 360, endpoint=False)
def line(img): return radon(img, theta=THETA, circle=True) * PX            # line integrals in cm
def sino_poly(aw, ab, extra=None):                                      # transmitted fraction for each ray, summed over the spectrum
    Lw, Lb = line(aw), line(ab); I = np.zeros_like(Lw)
    for k in range(len(ENERGIES)):
        t = MW[k] * Lw + MB[k] * Lb
        if extra is not None: t = t + extra[k]
        I += W[k] * np.exp(-t)
    return I
def sino_soft(aw, ab):
    Lw, Lb = line(aw), line(ab); I = np.zeros_like(Lw)
    for k in range(len(ENERGIES2)): I += W2[k] * np.exp(-(MW2[k] * Lw + MB2[k] * Lb))
    return I
def sino_mono(aw, ab): return np.exp(-(MW70 * line(aw) + MB70 * line(ab)))
def recon(I, n0, flt="ramp", rng=None, gain=None, scatter=0.0, I_ref=None):
    rng = rng or np.random.default_rng(1); Ie = I.copy()
    if scatter: Ie = Ie + scatter * ndi.gaussian_filter1d(I, 100, axis=0, mode="nearest")
    if n0: Ie = np.maximum(rng.poisson(n0 * Ie), 1) / n0
    if gain is not None: Ie = Ie * gain[:, None]
    P = -np.log(Ie); return iradon(P / PX, theta=THETA, filter_name=flt, circle=True, output_size=NPIX)
def calib(flt="ramp", scatter=0.0, soft=False):                                                  # water calibration: a uniform water cylinder under the same physics gives the scale for 0 HU
    yy, xx = np.mgrid[:NPIX, :NPIX]; cyl = ((yy - NPIX / 2) ** 2 + (xx - NPIX / 2) ** 2 < (NPIX * 0.32) ** 2).astype(float); I = (sino_soft if soft else sino_poly)(cyl, 0 * cyl); I = I + scatter * ndi.gaussian_filter1d(I, 100, axis=0, mode="nearest")
    r = iradon(-np.log(I) / PX, theta=THETA, filter_name=flt, circle=True, output_size=NPIX); return float(r[cyl > 0.5].mean())
def tohu(r, mu_w): return 1000.0 * (r - mu_w) / mu_w
MU_W_MONO, MU_W_POLY, MU_W_SCAT, MU_W_SOFT = MW70, calib(), calib("ramp", 0.12), calib("ramp", 0.0, True)
ref = tohu(recon(sino_mono(AW, AB), 0), MU_W_MONO)                      # the artifact-free reference: monoenergetic, no noise
def win(img, lo=-160, hi=240): return np.round(np.clip((img - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
def png(a):
    b = io.BytesIO(); Image.fromarray(a, "L").save(b, "PNG", optimize=True); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
roi_c = np.zeros((NPIX, NPIX), bool); roi_c[NPIX // 2 - 14:NPIX // 2 + 14, NPIX // 2 - 14:NPIX // 2 + 14] = True; roi_c &= BODY & (HU > -50) & (HU < 120)
def sd(img, roi): return float(np.std((img - ref)[roi]))
items = []
def add(id_, label, cap, img, facts, wl=(-160, 240), refimg=None):
    items.append(dict(id=id_, label=label, cap=cap, facts=facts, img=png(win(img, *wl)), ref=png(win(refimg if refimg is not None else ref, *wl))))
STATS = {}
# ---- noise at three exposures
rng = np.random.default_rng(7); I0 = sino_poly(AW, AB); CLEAN = {f: tohu(recon(I0, 0, f), MU_W_POLY) for f in ('ramp', 'hann')}
sdn = lambda im, f: float(np.std((im - CLEAN[f])[roi_c]))
for name, n0 in (("high", 120000), ("mid", 30000), ("low", 7500)):
    im = tohu(recon(I0, n0, rng=rng), MU_W_POLY); STATS["noise_" + name] = sdn(im, "ramp"); STATS["n0_" + name] = n0; STATS["img_noise_" + name] = im
for name, rel in (("high", "1"), ("mid", "1/4"), ("low", "1/16")):
    add("noise-" + name, f"Noise, exposure {rel}", "Poisson noise: the standard deviation of a uniform region rises as the exposure falls, as 1 / √(mAs).", STATS["img_noise_" + name], f"relative exposure {rel}: noise (SD in a soft-tissue region) = {STATS['noise_' + name]:.0f} HU")
# ---- reconstruction filter: sharp against smooth, at the same noise level
shp = tohu(recon(I0, 30000, "ramp", rng=np.random.default_rng(3)), MU_W_POLY); smo = tohu(recon(I0, 30000, "hann", rng=np.random.default_rng(3)), MU_W_POLY); STATS["sd_sharp"], STATS["sd_smooth"] = sdn(shp, "ramp"), sdn(smo, "hann")
add("filter-sharp", "Sharp filter", "The ramp filter keeps the fine detail and the noise. The bone edges are crisp and the soft tissue is grainy.", shp, f"sharp filter: noise = {STATS['sd_sharp']:.0f} HU")
add("filter-smooth", "Smooth filter", "A smoother filter averages neighbouring pixels. The noise falls and the fine detail softens.", smo, f"smooth filter: noise = {STATS['sd_smooth']:.0f} HU")
# ---- beam hardening and cupping: polychromatic physics, no correction
bh = tohu(recon(sino_soft(AW, AB), 0), MU_W_SOFT); d = bh - ref; rim = BODY & ~ndi.binary_erosion(BODY, iterations=14); core = ndi.binary_erosion(BODY, iterations=22) & (HU > -50) & (HU < 120)
STATS["bh_core"], STATS["bh_rim"] = float(d[core].mean()), float(d[rim & (HU > -50) & (HU < 120)].mean())
W_SOFT = (-100, 140)
add("beam-hardening", "Beam hardening", "The beam is polychromatic. The low-energy photons are removed first, so the beam hardens along thick paths and the centre reads lower than the periphery (cupping). Dark bands can also appear between dense objects. A softer beam, as here, hardens more.", bh, wl=W_SOFT, facts=f"soft tissue: the centre reads {STATS['bh_core'] - STATS['bh_rim']:+.0f} HU relative to the periphery (cupping)")
# ---- metal: a high-atomic-number object near the mandible
anterior = np.where(BODY & (np.arange(NPIX)[:, None] < NPIX * 0.5)); cand = np.argmax(np.where(HU[anterior] > 600, np.abs(anterior[1] - NPIX / 2) * -1.0 + 1000, -1e9)); my, mx = int(anterior[0][cand]), int(anterior[1][cand])
yy, xx = np.mgrid[:NPIX, :NPIX]; disc = ((yy - my) ** 2 + (xx - mx) ** 2 <= 3.0 ** 2).astype(float)
dist = ndi.distance_transform_edt(disc == 0)
metal = [0.3 * ML[k] * 7.9 * line(disc) for k in range(len(ENERGIES))]; mt = tohu(recon(sino_poly(AW, AB, extra=metal), 120000, rng=np.random.default_rng(5)), MU_W_POLY)
add("metal", "Metal streaks", "A dense metal object (steel-like, 6 mm, illustrative) absorbs most of the beam along some rays. Those rays carry too few photons and are strongly hardened, so bright and dark streaks run between the object and other dense structures.", mt, f"streaks: the soft tissue away from the metal varies by {np.std((mt - ref)[BODY & (HU > -50) & (HU < 120) & (dist > 12)]):.0f} HU (SD) around the reference", wl=(-300, 500))
STATS["metal_sd"] = float(np.std((mt - ref)[BODY & (HU > -50) & (HU < 120) & (dist > 12)])); STATS["metal_ref_sd"] = float(np.std((bh - ref)[BODY & (HU > -50) & (HU < 120) & (dist > 12)]))
# ---- ring: one detector channel with a gain error
gain = np.ones(NPIX); k_bad = NPIX // 2 + 22; gain[k_bad - 1:k_bad + 2] = 1.05                                            # the circle=True sinogram has NPIX detector channels
rg = tohu(recon(sino_poly(AW, AB), 0, gain=gain), MU_W_POLY)
add("ring", "Ring", "A group of three detector channels reads 5% high at every angle. The error is at the same distance from the centre of rotation in every projection, so it reconstructs as a ring.", rg, "faulty or miscalibrated detector channels: a ring centred on the rotation axis", wl=W_SOFT)
STATS["ring_gain"] = 1.05; STATS["ring_k"] = int(k_bad); rad = np.hypot(yy - NPIX / 2, xx - NPIX / 2).astype(int); dd = (rg - ref); prof = np.array([dd[(rad == r_) & BODY].mean() if ((rad == r_) & BODY).any() else 0 for r_ in range(0, 70)]); STATS["ring_r"] = int(abs(k_bad - NPIX // 2)); STATS["ring_peak"] = float(prof[STATS["ring_r"]] - 0.5 * (prof[STATS["ring_r"] - 4] + prof[STATS["ring_r"] + 4]))
# ---- motion: the patient moves by 6 mm half way through the scan
mv_img = np.roll(AW, 6, axis=1), np.roll(AB, 6, axis=1); I_static = sino_poly(AW, AB); I_moved = sino_poly(*mv_img); Imix = I_static.copy(); Imix[:, 180:] = I_moved[:, 180:]
mo = tohu(recon(Imix, 0), MU_W_POLY)
STATS["motion_sd"] = float(np.std((mo - ref)[BODY & (HU > -50) & (HU < 120)])); STATS["motion_ref_sd"] = float(np.std((rg - ref)[BODY & (HU > -50) & (HU < 120)]))
add("motion", "Motion", "The patient moves 6 mm during the scan, so the projections from the second half of the rotation no longer agree with those from the first half. Edges are doubled and streaks appear.", mo, "the patient moves 6 mm half way through the rotation", wl=W_SOFT)
# ---- scatter (cone-beam geometry): a smooth additive background in the projections
sc = tohu(recon(sino_poly(AW, AB), 0, scatter=0.12), MU_W_SCAT); d2 = sc - ref
STATS["sc_core"], STATS["sc_rim"] = float(d2[core].mean()), float(d2[rim & (HU > -50) & (HU < 120)].mean())
add("scatter", "Scatter (CBCT)", "Scattered photons add a smooth background to every projection. It is larger behind thick parts of the patient, so the attenuation is underestimated there. The centre looks less dense, and the HU are no longer accurate.", sc, wl=W_SOFT, facts=f"soft tissue: the centre reads {STATS['sc_core'] - STATS['sc_rim']:+.0f} HU relative to the periphery (cupping)")
# ---- the real slice itself, for the explorer: HU values as 16-bit integers, and one typical pixel for air, fat, muscle, and bone
def pick(lo, hi, erode=1):
    m = ndi.binary_erosion((HU >= lo) & (HU <= hi) & BODY, iterations=erode)
    if not m.any(): m = (HU >= lo) & (HU <= hi) & BODY
    lab, nl = ndi.label(m); big = 1 + int(np.argmax(ndi.sum(m, lab, range(1, nl + 1)))); cy, cx = ndi.center_of_mass(lab == big); ys, xs = np.where(lab == big); k = int(np.argmin((ys - cy) ** 2 + (xs - cx) ** 2))
    y, x = int(ys[k]), int(xs[k]); return dict(x=x, y=y, hu=int(round(float(HU[max(0, y - 1):y + 2, max(0, x - 1):x + 2].mean()))))
PICKS = dict(air=pick(-1000, -950, 2), fat=pick(-120, -70, 1), muscle=pick(30, 70, 2), bone=pick(900, 2500, 2))
HU16 = np.clip(np.round(HU), -1024, 3071).astype("<i2")
json.dump(dict(hu=base64.b64encode(HU16.tobytes()).decode(), picks=PICKS, fov_mm=NPIX * PX * 10, hu_min=-1024, hu_max=3071, source="Anatomy: OpenKBP patient pt_14 (Babier et al., Med Phys 2021). The artifacts are simulated: polychromatic 120 kVp spectrum, NIST attenuation, Poisson noise, filtered backprojection.", n=NPIX, px_cm=PX, items=items, stats={k: v for k, v in STATS.items() if not k.startswith("img_")}), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e6, 2), "MB;", len(items), "images")
for k, v in STATS.items():
    if not k.startswith("img_"): print(f"  {k:12} {v:.2f}" if isinstance(v, float) else f"  {k:12} {v}")
np.save("/tmp/ctart_ref.npy", ref); np.save("/tmp/ctart_bh.npy", bh); np.save("/tmp/ctart_mt.npy", mt); np.save("/tmp/ctart_rg.npy", rg); np.save("/tmp/ctart_mo.npy", mo); np.save("/tmp/ctart_sc.npy", sc); np.save("/tmp/ctart_low.npy", STATS["img_noise_low"])
