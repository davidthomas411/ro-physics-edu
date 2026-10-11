"""Real MR images for the MRI chapters: one patient with a glioblastoma on a 3 T scanner, in one axial plane in four sequences, from TCIA's UPENN-GBM collection. Writes src/real_mr.json.
  real-mr-seq  T1, T1 after gadolinium, T2, and FLAIR, with the TR, TE, and TI that the DICOM headers give
Usage: python tools/make_real_mr.py [preview-folder]      Downloads about 80 MB the first time (cached; see TCIA_CACHE)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import tcia
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "real_mr.json")
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
IDX, COL = tcia.index()
COLL, PID, DATE, K_FLAIR = "upenn_gbm", "UPENN-GBM-00005", "2002-03-24", 33
def kind(d):
    x = d.lower()
    if "flair" in x: return "flair"
    if "t1" in x and re.search(r"post|stealth|gad|gd|\+c", x): return "t1gd"
    if "t1" in x: return "t1"
    if "t2" in x: return "t2"
s = IDX[(IDX.collection_id == COLL) & (IDX.PatientID == PID) & (IDX.StudyDate == DATE) & IDX.SeriesDescription.str.contains("Processed_CaPTk", na=False)].copy(); s["kind"] = s.SeriesDescription.map(kind)
rows = {k: s[s.kind == k].sort_values("instanceCount", ascending=False).iloc[0] for k in ("t1", "t1gd", "t2", "flair")}
vols = {k: tcia.load_volume(r) for k, r in rows.items()}
Vf, spf, mf = vols["flair"]; zt = float(mf["z"][K_FLAIR]); V1, sp1, m1 = vols["t1"]; k1 = int(np.argmin(np.abs(m1["z"] - zt))); pts = tcia.slice_points(m1["dss"][k1])
imgs = {}
for k, (V, sp, meta) in vols.items():
    org, M = tcia.geometry(meta, sp); imgs[k] = tcia.sample(V, org, M, pts, order=1)
mask = ndi.binary_fill_holes(ndi.binary_opening(imgs["t1"] > 0.08 * np.percentile(imgs["t1"], 99.5), iterations=2)); ys, xs = np.where(mask); pad = 6
sl = (slice(max(0, ys.min() - pad), ys.max() + pad), slice(max(0, xs.min() - pad), xs.max() + pad))
def img(a):
    nz = a[a > 0]; hi = np.percentile(nz, 99.5); return tcia.gray8(a[sl], 0, hi, gamma=0.9)
panels = {k: img(a) for k, a in imgs.items()}
if PREVIEW:
    from PIL import Image
    os.makedirs(PREVIEW, exist_ok=True); Image.fromarray(np.hstack([panels[k] for k in ("t1", "t1gd", "t2", "flair")])).save(os.path.join(PREVIEW, "mr_seq.png"))
hd = {k: m["dss"][0] for k, (V, sp, m) in vols.items()}
f = lambda v: f"{float(v):g}"
par = {k: dict(tr=float(d.RepetitionTime), te=float(d.EchoTime), ti=float(d.InversionTime) if "InversionTime" in d else None, flip=float(d.FlipAngle), etl=int(d.EchoTrainLength), seq=str(d.SequenceName), field=float(d.MagneticFieldStrength)) for k, d in hd.items()}
assert all(p["field"] == 3.0 for p in par.values()) and "ContrastBolusAgent" in hd["t1gd"] and "ContrastBolusAgent" not in hd["t1"]
sub = lambda p: f"TR {p['tr']:g}, TE {p['te']:g}" + (f", TI {p['ti']:g}" if p["ti"] else "")
model = str(hd["t1"].ManufacturerModelName); agent = str(hd["t1gd"].ContrastBolusAgent)
PANELS = [("t1", "T1"), ("t1gd", "T1 with gadolinium"), ("t2", "T2"), ("flair", "FLAIR")]
panel = lambda k, label: dict(label=label, sub=sub(par[k]), w=int(panels[k].shape[1]), h=int(panels[k].shape[0]), img=tcia.uri(panels[k], quality=88))
FIGS = {"real-mr-seq": dict(
    label="Four real MR images of the same axial plane of a patient with a glioblastoma: T1, T1 after gadolinium, T2, and FLAIR, each with its repetition, echo, and inversion times",
    cap=f"Real images of a patient with a glioblastoma on a 3 T scanner ({model}), in one axial plane, resampled onto the same grid from four sequences of one session. Times are in ms. Each image is scaled to the 99.5th percentile of its own signal. Data: TCIA UPENN-GBM (CC BY 4.0).",
    views=[dict(label="Sequences", cols=2, facts=f"The T1 images are inversion-prepared gradient-echo images, and the second one follows an injection of gadolinium ({agent.split()[0].title()}). CSF is dark on T1 and FLAIR and bright on T2. "
                                                  f"The tumour rim enhances after gadolinium, and the surrounding oedema is bright on T2 and FLAIR. The T2 images are 3D fast spin-echo, so their TE is an effective value.", panels=[panel(k, label) for k, label in PANELS])])}
src = dict(tcia.provenance(COL, COLL, rows["t1"]), figs=["real-mr-seq"], series=[r.SeriesDescription for r in rows.values()])
json.dump(dict(source="Real MR images from a TCIA collection; tools/make_real_mr.py", idc_index_data=tcia.index_version(), figs=FIGS, sources=[src], stats=dict(params=par, plane=dict(z_mm=zt, t1_slice=int(k1), flair_slice=K_FLAIR))), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e3), "KB"); print(json.dumps(par, indent=1))
