"""Simulated planar radiographs of a real patient: an AP projection (a digitally reconstructed radiograph) of the CT volume of OpenKBP patient pt_14 (Babier et al., Med Phys 2021).
The imaging physics is simulated: polychromatic kV and megavoltage spectra, NIST attenuation of water and bone, Poisson noise, a scatter background, and an anti-scatter grid.
Usage: python tools/make_drr_gallery.py /path/to/pt_14   (writes src/gal_drr.json)"""
import sys, os, io, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from PIL import Image
from scipy import ndimage as ndi
import nistdata as N
PT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/okbp/provided-data/train-pats/pt_14"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "gal_drr.json")
vox = [float(x) for x in open(os.path.join(PT, "voxel_dimensions.csv")).read().split()]; DX, DZ = vox[0] / 10, vox[2] / 10       # cm
def mu_rho(tab, e_kev):
    ks = sorted(tab); return float(np.exp(np.interp(np.log(e_kev), np.log([k * 1000 for k in ks]), np.log([tab[k][0] for k in ks]))))
KV_E = np.array([30, 40, 50, 60, 70, 80.]); KV_W = np.array([0.08, 0.22, 0.28, 0.24, 0.13, 0.05]); KV_W /= KV_W.sum()                    # an illustrative 80 kVp diagnostic spectrum
MV_E = np.array([1000, 1500, 2000, 3000, 4000.]); MV_W = np.array([0.25, 0.30, 0.25, 0.15, 0.05]); MV_W /= MV_W.sum()                    # an illustrative 6 MV spectrum (keV)
MWk, MBk = np.array([mu_rho(N.WATER, e) for e in KV_E]), np.array([mu_rho(N.BONE, e) for e in KV_E]); MWm, MBm = np.array([mu_rho(N.WATER, e) for e in MV_E]), np.array([mu_rho(N.BONE, e) for e in MV_E])
MW70, MB70 = mu_rho(N.WATER, 70), mu_rho(N.BONE, 70); RHOB = 1.92
d = pd.read_csv(os.path.join(PT, "ct.csv"), index_col=0); ct = np.zeros(128 ** 3, np.float32); ct[d.index.values] = d.iloc[:, 0].values; ct = np.clip(ct.reshape(128, 128, 128) - 1024, -1000, 3000)
aw = np.clip(1 + ct / 1000.0, 0, 1.0); ab = np.maximum(ct, 0) / 1000.0 * MW70 / MB70                                                    # water-equivalent and bone-equivalent densities that reproduce the HU at 70 keV
Lw, Lb = aw.sum(axis=0) * DX, ab.sum(axis=0) * DX                                                                                     # AP line integrals in cm, indexed (left-right, slice)
thick = aw.sum(axis=0) * DX; cols = np.where((thick > 6).any(axis=1))[0]; c0, c1 = max(0, cols.min() - 3), min(127, cols.max() + 3); zs = np.where((thick > 6).any(axis=0))[0]; z0, z1 = zs.min(), zs.max()      # the part of the volume with at least 6 g/cm2 of tissue: the couch is left out
Lw, Lb = Lw[c0:c1 + 1, z0:z1 + 1], Lb[c0:c1 + 1, z0:z1 + 1]
width = (Lw > 2).sum(axis=0); inferior_low = width[:max(3, len(width) // 5)].mean() > width[-max(3, len(width) // 5):].mean()          # which end of the slice axis is the shoulders
def orient(a): a = a.T; return a[::-1] if inferior_low else a                                                                          # superior at the top
Lw, Lb = orient(Lw), orient(Lb)
PIX = 0.2                                                                                                                              # output pixel in cm
zoom = (DZ / PIX, DX / PIX); Lw = np.maximum(ndi.zoom(Lw, zoom, order=3), 0); Lb = np.maximum(ndi.zoom(Lb, zoom, order=3), 0); H, W = Lw.shape
bodyp = Lw > 1.0
def primary(MW, MB, Wt): return sum(w * np.exp(-(mw * Lw + mb * Lb)) for w, mw, mb in zip(Wt, MW, MB))                                   # transmitted fraction: mass attenuation coefficient times the mass thickness of water and of bone
Ik, Im = primary(MWk, MBk, KV_W), primary(MWm, MBm, MV_W); P = lambda I: -np.log(I)
def win_of(img, m): return np.percentile(img[m], 1), np.percentile(img[m], 99)
def gray(img, lo, hi): return np.round(np.clip((img - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
def png(a):
    b = io.BytesIO(); Image.fromarray(a, "L").save(b, "PNG", optimize=True); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
# ---- ROIs: a bone region and a soft-tissue region at the same height
mid = slice(int(H * 0.45), int(H * 0.75)); sub = Lb[mid, W // 4:3 * W // 4]; r_, c_ = np.unravel_index(np.argmax(sub), sub.shape); br, bc = r_ + mid.start, c_ + W // 4
# a soft-tissue region with the same water thickness as the bone region, so that the difference between them is the bone and not the thickness
lwb = Lw[br - 3:br + 4, bc - 3:bc + 4].mean(); yy, xx = np.mgrid[:H, :W]; ok = bodyp & (Lb < 0.15) & (np.abs(Lw - lwb) < 0.4) & (yy > 8) & (yy < H - 8) & (xx > 8) & (xx < W - 8) & (np.abs(yy - br) < 40) & (np.abs(xx - bc) < 60)
cand = np.argwhere(ok); k_ = int(np.argmin(((cand - np.array([br, bc])) ** 2).sum(1))); sr, sc = int(cand[k_][0]), int(cand[k_][1])
def roi(r, c, k=3): m = np.zeros((H, W), bool); m[r - k:r + k + 1, c - k:c + k + 1] = True; return m
RB, RS = roi(br, bc), roi(sr, sc)
STATS = dict(H=int(H), W=int(W), pix_cm=PIX, roi_bone=[int(br), int(bc)], roi_soft=[int(sr), int(sc)], bone_Lb=float(Lb[RB].mean()), soft_Lb=float(Lb[RS].mean()), bone_Lw=float(Lw[RB].mean()), soft_Lw=float(Lw[RS].mean()))
# ---- the contrast of 2 cm of bone against 2 cm of water, for each beam: the change in -ln(I)
def c2(MW, MB, Wt): base = sum(w * np.exp(-mw * 10.0) for w, mw in zip(Wt, MW)); with_b = sum(w * np.exp(-(mw * 8.0 + mb * 2.0 * 0 + (mb * 2.0 * RHOB))) for w, mw, mb in zip(Wt, MW, MB)); return float(np.log(base / with_b))
STATS["c_kv"], STATS["c_mv"] = c2(MWk, MBk, KV_W), c2(MWm, MBm, MV_W)
items = []
def add(id_, label, cap, facts, img, ref): items.append(dict(id=id_, label=label, cap=cap, facts=facts, img=png(img), ref=png(ref)))
lo, hi = win_of(P(Ik), bodyp); REF = gray(P(Ik), lo, hi); REFA = np.where(bodyp, REF, 0).astype(np.uint8)
def mueff(MW, Wt, tt=10.0): return float(-np.log(sum(w * np.exp(-mw * tt) for w, mw in zip(Wt, MW))) / tt)
mk_, mm_ = mueff(MWk, KV_W), mueff(MWm, MV_W); base_mv = float(np.percentile(P(Im)[bodyp], 1)); lom, him = base_mv, base_mv + (hi - lo) * mm_ / mk_; MVG = gray(P(Im), lom, him)      # the same window in water thickness: a soft-tissue difference gives the same grey change in both images
# the in-body contrast between the two ROIs, from the displayed images
cd = lambda img: float(img[RB].mean() - img[RS].mean())
STATS["gray_kv"], STATS["gray_mv"] = cd(REF.astype(float)), cd(MVG.astype(float))
STATS["gray_kv"], STATS["gray_mv"] = cd(REF.astype(float)), cd(MVG.astype(float))
add("mv", "Megavoltage beam", "A 6 MV beam gives images with little Z-dependence, so bone is distinguished from soft tissue only by its density. The bone contrast is far smaller than at kilovoltage energy, where the photoelectric effect adds a strong Z-dependence. Both images use the same window in water thickness, so the soft tissue looks the same and only the bone differs.",
    f"replacing 2 cm of water by 2 cm of bone changes −ln(I) by {STATS['c_kv']:.2f} at kV and {STATS['c_mv']:.3f} at MV, a factor of {STATS['c_kv'] / STATS['c_mv']:.0f}. With the same soft-tissue window, the bone region differs from the soft-tissue region by {100 * STATS['gray_kv'] / 255:.0f}% of the display range at kV and {100 * STATS['gray_mv'] / 255:.0f}% at MV", MVG, REF)
# ---- noise at three exposures: counts per pixel before the patient
for name, rel, n0 in (("high", "1", 12000.0), ("mid", "1/4", 3000.0), ("low", "1/16", 750.0)):
    rng = np.random.default_rng(11 + len(name)); Ic = np.maximum(rng.poisson(n0 * Ik), 1) / n0; Pn = P(Ic); sd = float(np.std((Pn - P(Ik))[roi(sr, sc, 7)]))
    STATS["noise_" + name] = sd; STATS["n0_" + name] = n0; add("noise-" + name, f"Exposure {rel}", "Photon counting noise. The standard deviation of the signal in a uniform region rises as the exposure falls, as 1 / √(exposure), and the grain hides the weak contrast.", f"relative exposure {rel}: noise = {sd:.3f} in −ln(I)", gray(Pn, lo, hi), REF)
# ---- scatter and the grid
SPR = 2.0; S0 = ndi.gaussian_filter(Ik * bodyp, 25); Is = S0 * (SPR * Ik[bodyp].mean() / S0[bodyp].mean()); I_ns = Ik + Is;                      # scatter is made in the patient: a smooth background that sums to SPR times the primary over the body
TP, TS = 0.70, 0.15; I_g = TP * Ik + TS * Is
con = lambda I: float(P(I)[RB].mean() - P(I)[RS].mean())
STATS["con_primary"], STATS["con_scatter"], STATS["con_grid"] = con(Ik), con(I_ns), con(TP * Ik + 0 * Is)
STATS["spr_in"] = float((Is[bodyp].sum()) / Ik[bodyp].sum()); STATS["spr_grid"] = float((TS * Is[bodyp].sum()) / (TP * Ik[bodyp].sum())); STATS["bucky"] = float(I_ns[bodyp].mean() / I_g[bodyp].mean()); STATS["con_with_grid"] = con(I_g)
STATS["TP"], STATS["TS"], STATS["SPR"] = TP, TS, SPR
add("scatter", "Scatter, no grid", "Photons that scatter in the patient reach the detector along the wrong path. They add a smooth background that carries no information, so the contrast falls and the image looks flat.",
    f"the contrast between the bone and soft-tissue regions falls to {STATS['con_scatter'] / STATS['con_primary']:.2f} of its primary-only value (scatter-to-primary ratio {STATS['spr_in']:.1f})", gray(P(I_ns), lo, hi), REF)
add("grid", "Scatter, with grid", "The fins of the grid stop most of the scattered photons and pass most of the primary photons. The contrast recovers, at the cost of a higher exposure to make up for the primary photons that the grid also absorbs.",
    f"the contrast recovers to {STATS['con_with_grid'] / STATS['con_primary']:.2f} of its primary-only value (scatter-to-primary ratio {STATS['spr_grid']:.2f}), and the exposure must rise {STATS['bucky']:.1f} times (the Bucky factor)", gray(P(I_g), lo, hi), REF)
json.dump(dict(source="Anatomy: OpenKBP patient pt_14 (Babier et al., Med Phys 2021), AP projection of the CT volume. The radiographic effects are simulated.", items=items, stats=STATS), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e6, 2), "MB;", len(items), "images; image", H, "x", W, "; inferior_low =", inferior_low)
for k, v in STATS.items(): print(f"  {k:14} {v}")
Image.fromarray(np.hstack([REFA, MVG])).save("/tmp/shots/drr_kv_mv.png")
