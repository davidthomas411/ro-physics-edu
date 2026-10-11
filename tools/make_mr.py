"""Real-anatomy MR examples from the ICBM152 (MNI152 2009) average brain that ships with the nilearn package: one axial slice at 12 mm above the anterior commissure plane,
its gray-matter and white-matter probability maps, and a CSF map (brain mask minus gray and white matter). The contrast weighting and the artifacts are simulated.
Writes src/mr_case.json (tissue fractions, for the contrast explorer) and src/gal_mr.json (artifact gallery)."""
import os, io, json, base64, warnings
warnings.filterwarnings("ignore")
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from nilearn import datasets
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, "..", "src")
T, G, Wm, M = (datasets.load_mni152_template(resolution=1), datasets.load_mni152_gm_template(), datasets.load_mni152_wm_template(), datasets.load_mni152_brain_mask())
oz = int(round(np.linalg.inv(T.affine)[2, 3])); K = oz + 12
orient = lambda a: np.fliplr(np.rot90(np.asarray(a.get_fdata())[:, :, K]))                       # anterior at the top, patient right on the left (radiological)
t, g, w, m = orient(T), orient(G), orient(Wm), orient(M)
m = (m > 0.5).astype(float); gm = np.clip(g, 0, 1) * m; wm = np.clip(w, 0, 1) * m; csf = np.clip(m - gm - wm, 0, 1)
s = gm + wm + csf; over = s > 1; gm[over] /= s[over]; wm[over] /= s[over]; csf[over] /= s[over]
rr, cc = np.where(m > 0.5); r0, r1, c0, c1 = max(0, rr.min() - 8), rr.max() + 9, max(0, cc.min() - 8), cc.max() + 9
crop = lambda a: a[r0:r1, c0:c1]; t, m, gm, wm, csf = map(crop, (t, m, gm, wm, csf)); H, W = t.shape
def png(a, mode="L"):
    b = io.BytesIO(); Image.fromarray(a, mode).save(b, "PNG", optimize=True); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
q = lambda a: np.round(np.clip(a, 0, 1) * 255).astype(np.uint8)
frac = np.dstack([q(csf), q(gm), q(wm), np.full((H, W), 255, np.uint8)])
TISSUE = dict(WM=dict(T1=600, T2=80, PD=0.70), GM=dict(T1=950, T2=100, PD=0.80), CSF=dict(T1=4000, T2=2000, PD=1.00))                         # illustrative values at 1.5 T
mr = dict(w=int(W), h=int(H), z_mm=12, frac=png(frac, "RGBA"), tissue=TISSUE, source="ICBM152 (MNI152 2009) average T1 brain and tissue probability maps, shipped with the nilearn package; axial slice 12 mm above the anterior commissure plane. The contrast weighting is simulated.")
json.dump(mr, open(os.path.join(SRC, "mr_case.json"), "w"), separators=(",", ":"))
# ---- the artifact gallery, from the real T1 slice
t1 = np.clip(t / np.percentile(t[m > 0.5], 99.5), 0, 1); yy, xx = np.mgrid[:H, :W].astype(float); xc, yc = np.where(m > 0.5)[1].mean(), np.where(m > 0.5)[0].mean()
def grid(sp=20, thick=1):
    g_ = np.zeros((H, W)); g_[::sp, :] = 1; g_[:, ::sp] = 1; return ndi.binary_dilation(g_ > 0, iterations=thick - 1) * 1.0 if thick > 1 else g_
GRID = grid(20)
def warp_x(img, dx, jac=False):                                                                                                                  # the signal that belongs at x - dx appears at x; where pixels are squeezed together the intensity piles up
    out = ndi.map_coordinates(img, [yy, xx - dx], order=1, mode="constant", cval=0.0)
    return out / np.clip(1 - np.gradient(dx, axis=1), 0.35, 3.0) if jac else out
def overlay(a, gr): return np.maximum(a, 0.0) * (1 - 0.0) + gr * 0.75 * (a >= 0)
REF = np.maximum(t1, GRID * 0.85)
items = []; STATS = dict(H=int(H), W=int(W), grid_mm=20, pix_mm=1.0)
def add(id_, label, cap, facts, img): items.append(dict(id=id_, label=label, cap=cap, facts=facts, img=png(q(img)), ref=png(q(REF))))
# B0 inhomogeneity: a smooth bowl of field error, zero at the centre, 0.06 mT at the edge; with a gradient of 10 mT/m a field error of dB moves a pixel by dB / G
Gx, dBe = 10.0, 0.06; R = max(W, H) / 2.0; dB = dBe * (((xx - xc) ** 2 + (yy - yc) ** 2) / (R * R)); dx = dB / Gx * 1000.0                          # mm = pixels
d_img = np.maximum(warp_x(t1, dx, True), warp_x(GRID * 0.85, dx)); STATS["dx_max"] = float(dx[m > 0.5].max()); STATS["dx_mean"] = float(dx[m > 0.5].mean()); STATS["G"], STATS["dBe"], STATS["R"] = Gx, dBe, float(R); STATS["xc"], STATS["yc"] = float(xc), float(yc)
add("distortion", "B0 inhomogeneity", "A change of the local field is equivalent to moving the pixel: the apparent shift is the field error divided by the gradient. Here the field error grows from zero at the centre to 0.06 mT at the edge, with a gradient of 10 mT/m, so the pixels shift sideways by up to 6 mm and the grid lines bend. The 20 mm grid plays the part of the distortion phantom.",
    f"shift = ΔB / G: up to {STATS['dx_max']:.1f} mm at the edge of the brain, {STATS['dx_mean']:.1f} mm on average over the brain", d_img)
# gradient scaling: a gradient 5% larger than assumed compresses the image
sc = 1.05; g_img = np.maximum(ndi.map_coordinates(t1, [yy, xc + (xx - xc) * sc], order=1, mode="constant"), ndi.map_coordinates(GRID * 0.85, [yy, xc + (xx - xc) * sc], order=1, mode="constant"))
wm0 = (m > 0.5).sum(axis=0) > 0; w_true = float(wm0.sum()); STATS["scale"] = sc; STATS["w_true"] = w_true; mm_ = ndi.map_coordinates(m, [yy, xc + (xx - xc) * sc], order=1, mode="constant") > 0.5; STATS["w_comp"] = float((mm_.sum(axis=0) > 0).sum())
add("gradient", "Gradient 5% too strong", "The gradient sets the position of each pixel. If it is 5% larger than the system assumes, features are placed closer together, and the image is compressed in that direction.", f"the brain is {STATS['w_true']:.0f} mm wide in the reference and {STATS['w_comp']:.0f} mm wide in this image", g_img)
# susceptibility: a metal object gives a signal void, and the field around it shifts pixels sideways, which piles the signal up on one side
x0, y0, rm = xc - 12.0, yc - 52.0, 5.0; r = np.hypot(xx - x0, yy - y0) + 1e-6; Dm = 30.0; dxs = Dm * (rm / r) ** 3 * (xx - x0) / r
s_img = np.clip(warp_x(t1, np.where(r > rm, dxs, 0), True), 0, 1.6); void = r <= 1.6 * rm; s_img = np.where(void, 0.0, s_img); s_img = np.maximum(s_img, warp_x(GRID * 0.85, 0 * dxs)); STATS["sus_void_mm"] = float(2 * 1.6 * rm); STATS["sus_x0"], STATS["sus_y0"], STATS["sus_r"] = float(x0), float(y0), float(rm)
add("susceptibility", "Metal (susceptibility)", "A metal object distorts the local field, so no usable signal comes from the region around it, a signal void, and the field around the void shifts pixels sideways, which piles the signal up on one side and stretches it on the other. Illustrative size and field.", f"a metal object of {2 * rm:.0f} mm gives a signal void about {STATS['sus_void_mm']:.0f} mm across", s_img)
json.dump(dict(source=mr["source"], items=items, stats=STATS), open(os.path.join(SRC, "gal_mr.json"), "w"), separators=(",", ":"))
print("mr_case.json", round(os.path.getsize(os.path.join(SRC, "mr_case.json")) / 1e3), "KB; gal_mr.json", round(os.path.getsize(os.path.join(SRC, "gal_mr.json")) / 1e3), "KB; image", H, "x", W, "; k =", K)
for k_, v in STATS.items(): print(f"  {k_:10} {v}")
Image.fromarray(np.hstack([q(REF), q(d_img), q(g_img), q(s_img)]), "L").save("/tmp/shots/mr_art.png")
