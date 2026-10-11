"""Real 4D-CT for the chapter on target volumes: two phases of one breathing cycle of a lung cancer patient. Writes src/real_4d.json (see tools/tcia.py for the data route and the licences).
  real-ct-motion   the same coronal plane in the 0% and the 50% phase, with the lung volume and the movement of the lung base measured on the whole volumes
Usage: python tools/make_real_4d.py [preview-folder]      Downloads about 150 MB the first time (cached; see TCIA_CACHE)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import tcia
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "real_4d.json")
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
IDX, COL = tcia.index()
COLL, PID = "4d_lung", "100_HM10395"                                                                       # one patient, chosen for a clear lung base and a visible mass
PHASES = ("0.0", "50.0")

def phase_row(ph):
    r = IDX[(IDX.collection_id == COLL) & (IDX.PatientID == PID) & (IDX.Manufacturer == "ADAC") & IDX.SeriesDescription.str.contains(f"Gated, {ph}%A", regex=False) & (IDX.instanceCount > 100)]
    assert len(r) == 1, (ph, len(r)); return r.iloc[0]

vols = []
for ph in PHASES:
    r = phase_row(ph); V, sp, meta = tcia.load_volume(r)
    d0 = meta["dss"][0]; assert str(d0.PatientPosition) == "HFS" and len(V) == 142
    Vs, sps = tcia.standardize(V, sp, meta["dirs"]); vols.append(Vs); ROW = r
V0, V1 = vols; dz, dy, dx = sps; assert V0.shape == V1.shape == (142, 512, 512)

def lung_mask(V):                                                                                      # aerated lung: air-like voxels that do not touch the border of the volume, in the large components
    air = V < -400; lab, n = ndi.label(air)
    border = np.unique(np.concatenate([lab[:, 0, :].ravel(), lab[:, -1, :].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()]))
    m = air.copy()
    for b in border:
        if b: m[lab == b] = False
    lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); return np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 2e5])

L0, L1 = lung_mask(V0), lung_mask(V1)
litres = [float(L.sum() * dz * dy * dx / 1e6) for L in (L0, L1)]

def base(L):                                                                                           # index of the lowest lung voxel in every (y, x) column, and whether the column holds lung
    has = L.any(axis=0); return np.where(has, np.argmax(L, axis=0), -1), has
b0, h0 = base(L0); b1, h1 = base(L1)
cols = h0 & h1 & (L0.sum(axis=0) * dz > 80)                                                            # columns with at least 8 cm of lung, so the trachea and the edges are left out
shift = (b1[cols] - b0[cols]) * dz                                                                     # mm; positive = toward the head in the second phase
q1, med, q3 = (float(x) for x in np.percentile(shift, [25, 50, 75]))
assert litres[0] > litres[1] > 2.0 and 5 < med < 40, (litres, med)

# the figure: one coronal plane, cropped to the body and to the lungs, resampled to square pixels, lung window
YI = int(0.54 * V0.shape[1])
body = (V0[:, YI, :] > -300) | (V1[:, YI, :] > -300); xs = np.where(body.any(axis=0))[0]; x0, x1 = max(xs.min() - 6, 0), min(xs.max() + 6, 511)
zl = np.where((L0 | L1).any(axis=(1, 2)))[0]; z0, z1 = max(int(zl.min() - 45 / dz), 0), min(int(zl.max() + 12 / dz), V0.shape[0] - 1)
def view(V, nm):
    a = V[z0:z1 + 1, YI, x0:x1 + 1][::-1]                                                              # head at the top, the patient's left on the right of the image
    a = ndi.zoom(a, (dz / dx, 1.0), order=1); g = tcia.gray8(a, -1000, 500)
    if PREVIEW:
        from PIL import Image
        os.makedirs(PREVIEW, exist_ok=True); Image.fromarray(g).save(os.path.join(PREVIEW, f"motion_{nm}.png"))
    return g
tiles = []
for (nm, V), lit in zip((("0", V0), ("50", V1)), litres):
    g = view(V, nm); tiles.append(dict(label=f"{nm}% phase", sub=f"lung {lit:.1f} L", w=int(g.shape[1]), h=int(g.shape[0]), img=tcia.uri(g)))

src = dict(tcia.provenance(COL, COLL, ROW), figs=["real-ct-motion"], series=["planning 4D-CT, phase-sorted volumes at 0% and 50%"])
N = int(cols.sum())
FIG = dict(
    label="Two real coronal CT slices of the same plane of one lung cancer patient in the 0% and the 50% phase of the breathing cycle, with the lung volume of each phase",
    cap=f"Real coronal slices of one four-dimensional CT of a lung cancer patient: the same plane in the 0% and the 50% phase of the breathing cycle. The slices are 3 mm thick and were cropped, resampled to square pixels of {dx:.2f} mm, and windowed from −1000 to 500 HU. Data: TCIA {src['collection']} ({src['license']}).",
    views=[dict(label="Two phases", cols=2, facts=(f"The lung volume, from a threshold at −400 HU, is <span class=\"f\">{litres[0]:.1f} L</span> in the 0% phase and <span class=\"f\">{litres[1]:.1f} L</span> in the 50% phase. "
                                                 f"The lung base, the lowest lung voxel in each of {N:,} vertical columns through the lungs, lies a median of <span class=\"f\">{med:.0f} mm</span> higher in the 50% phase (middle half of the columns: {q1:.0f} to {q3:.0f} mm)."), panels=tiles)])
STATS = dict(phases=[0, 50], lung_l=litres, shift_mm=dict(median=med, q1=q1, q3=q3, columns=N), slice_mm=float(dz), pixel_mm=float(dx), plane=YI)
json.dump(dict(source="Real 4D-CT from a TCIA collection; tools/make_real_4d.py", idc_index_data=tcia.index_version(), figs={"real-ct-motion": FIG}, sources=[src], stats=dict(motion=STATS, hdr=[])), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e3), "KB"); print(json.dumps(STATS, indent=1))
