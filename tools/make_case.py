"""Builds src/case_hn1.json from one real clinical plan in the OpenKBP dataset (patient pt_14 of the training set).
Source: A. Babier, B. Zhang, R. Mahmood, K.L. Moore, T.G. Purdie, A.L. McNiven, T.C.Y. Chan, "OpenKBP: The open-access knowledge-based planning grand challenge and dataset", Med Phys 48:5549-5561, 2021 (https://github.com/ababier/open-kbp).
The data are 128 x 128 x 128 arrays: CT (HU + 1024), delivered dose (Gy), and structure masks. Usage: python tools/make_case.py /path/to/open-kbp/provided-data/train-pats/pt_14"""
import sys, os, json, io, base64
import numpy as np, pandas as pd
from PIL import Image
from skimage import measure

PT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/okbp/provided-data/train-pats/pt_14"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "case_hn1.json")
def arr(f, mask=False):
    d = pd.read_csv(os.path.join(PT, f + ".csv"), index_col=0); a = np.zeros(128 ** 3, np.float32); a[d.index.values] = 1 if mask else d.iloc[:, 0].values; return a.reshape(128, 128, 128)
vox = [float(x) for x in open(os.path.join(PT, "voxel_dimensions.csv")).read().split()]; dx, dz = vox[0], vox[2]
ct = arr("ct") - 1024; dose = arr("dose")
STRUCT = [("PTV70", "#ff3b8d"), ("PTV63", "#ff9f1c"), ("PTV56", "#ffd60a"), ("Brainstem", "#2ec4b6"), ("SpinalCord", "#7bd957"), ("LeftParotid", "#4da3ff"), ("RightParotid", "#b388ff"), ("Esophagus", "#c9a66b"), ("Mandible", "#d9d9d9")]
masks = {n: arr(n, True) > 0 for n, _ in STRUCT if os.path.exists(os.path.join(PT, n + ".csv"))}
pz = np.where(masks["PTV70"].sum((0, 1)) > 0)[0]; z0, z1 = max(0, pz.min() - 6), min(127, pz.max() + 6); zs = list(range(z0, z1 + 1))
union = np.zeros((128, 128, 128), bool)
for m in masks.values(): union |= m
nz = np.argwhere(union[:, :, z0:z1 + 1]); (r0, c0, _), (r1, c1, _) = nz.min(0), nz.max(0)                              # crop to the structures plus a margin, so the anatomy fills the picture
r0, c0, r1, c1 = max(0, int(r0) - 12), max(0, int(c0) - 12), min(127, int(r1) + 12), min(127, int(c1) + 12); H, W = r1 - r0 + 1, c1 - c0 + 1
cols = 10; rows = -(-len(zs) // cols)
ctS = np.zeros((rows * H, cols * W), np.uint8); doS = np.zeros((rows * H, cols * W), np.uint8)
LEVEL = 80.0 / 255.0                                                           # Gy per grey level in the dose sprite
for k, z in enumerate(zs):
    r, c = divmod(k, cols)
    ctS[r * H:(r + 1) * H, c * W:(c + 1) * W] = np.round((np.clip(ct[r0:r1 + 1, c0:c1 + 1, z], -160, 240) + 160) / 400 * 255).astype(np.uint8)
    doS[r * H:(r + 1) * H, c * W:(c + 1) * W] = np.clip(np.round(dose[r0:r1 + 1, c0:c1 + 1, z] / LEVEL), 0, 255).astype(np.uint8)
def png(a):
    b = io.BytesIO(); Image.fromarray(a, "L").save(b, "PNG", optimize=True); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
vv = dx * dx * dz / 1000.0                                                      # voxel volume in cm3
edges = np.arange(0, 80.5, 0.5); out = []
for n, col in STRUCT:
    if n not in masks: continue
    m = masks[n]; d = dose[m]; N = d.size
    dvh = [round(float(100.0 * (d >= e).sum() / N), 2) for e in edges]
    stats = dict(volume=round(N * vv, 1), mean=round(float(d.mean()), 2), max=round(float(d.max()), 2), min=round(float(d.min()), 2), D98=round(float(np.percentile(d, 2)), 2), D95=round(float(np.percentile(d, 5)), 2), D50=round(float(np.percentile(d, 50)), 2), D2=round(float(np.percentile(d, 98)), 2))
    cont = {}
    for k, z in enumerate(zs):
        mk = m[r0:r1 + 1, c0:c1 + 1, z]
        if not mk.any(): continue
        polys = []
        for cn in measure.find_contours(np.pad(mk.astype(float), 1), 0.5):
            cn = measure.approximate_polygon(cn, 0.3) - 1
            if len(cn) >= 4: polys.append([round(float(v), 1) for p in cn for v in (p[1], p[0])])
        if polys: cont[str(k)] = polys
    out.append(dict(name=n, color=col, dvh=dvh, stats=stats, contours=cont))
CASE = dict(source="OpenKBP training patient pt_14 (Babier et al., Med Phys 2021)", w=W, h=H, nz=len(zs), cols=cols, z0=int(z0), dx=dx, dz=dz, level=LEVEL, rx=70.0, ct=png(ctS), dose=png(doS), dvhStep=0.5, structures=out, doseMax=round(float(dose.max()), 1))
json.dump(CASE, open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e6, 2), "MB | image", W, "x", H, "| slices", len(zs), "| voxel", dx, "x", dx, "x", dz, "mm")
for s in out: print(f"{s['name']:13} {s['stats']}")
