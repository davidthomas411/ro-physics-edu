"""A real planar nuclear medicine image for the SPECT chapter: a whole-body Tc-99m bone scan (anterior and posterior views), from TCIA's CMB-PCA collection. Writes src/real_nm.json.
  real-nm-bone  the two views of one whole-body acquisition on a dual-head gamma camera
Usage: python tools/make_real_nm.py [preview-folder]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import tcia
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "real_nm.json")
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
IDX, COL = tcia.index()
FIGS, STATS = {}, {}
row = tcia.one(IDX, collection_id="cmb_pca", PatientID="MSB-03973", SeriesDescription="WHOLE BODY", Modality="NM")
key = tcia.list_series(row)[0][0]; ds = tcia.dcm(tcia.fetch(row, key)); a = ds.pixel_array.astype(np.float32)                         # frames: anterior, posterior
assert a.ndim == 3 and a.shape[0] == 2 and str(ds.Modality) == "NM"
nuc = ds.RadiopharmaceuticalInformationSequence[0].RadionuclideCodeSequence[0].CodeMeaning if "RadiopharmaceuticalInformationSequence" in ds else ""
win = ds.EnergyWindowInformationSequence[0].EnergyWindowRangeSequence[0]; e_lo, e_hi = float(win.EnergyWindowLowerLimit), float(win.EnergyWindowUpperLimit)
assert "99m" in nuc, nuc
ant, post = a[0], a[1]                                                                              # each view as its own detector sees it, which is the clinical display: the posterior view is the mirror image of the anterior one (checked on the focal uptake in the ankle)
pix = float(ds.PixelSpacing[0])
def img(x):                                                                                         # dark on light as bone scans are usually read, scaled to the 99.7th percentile of the counts
    t = np.clip(x / np.percentile(x, 99.7), 0, 1) ** 0.6; return np.round(255 * (1 - t)).astype(np.uint8)
rows = np.where(np.maximum(ant, post).max(axis=1) > 0.05 * np.percentile(np.maximum(ant, post), 99.7))[0]; r0, r1 = max(0, rows.min() - 14), min(a.shape[1], rows.max() + 14)       # crop the empty rows above the head and below the feet
ia, ip = img(ant[r0:r1]), img(post[r0:r1])
if PREVIEW:
    from PIL import Image
    os.makedirs(PREVIEW, exist_ok=True); Image.fromarray(np.hstack([ia, ip])).save(os.path.join(PREVIEW, "bone_scan.png"))
counts = float(a.sum()); STATS["hdr"] = [dict(label="Planar bone scan", modality="NM", rows=int(ds.Rows), cols=int(ds.Columns), pixel_mm=float(ds.PixelSpacing[0]), stored=int(ds.BitsStored), allocated=int(ds.BitsAllocated))]
STATS["bone"] = dict(matrix=[int(a.shape[2]), int(a.shape[1])], shown_rows=[int(r0), int(r1)], pixel_mm=pix, energy_window_keV=[e_lo, e_hi], counts=counts, nuclide=str(nuc), peak_counts=float(a.max()))
panel = lambda x, label: dict(label=label, sub=None, w=int(x.shape[1]), h=int(x.shape[0]), img=tcia.uri(x, quality=88))
FIGS["real-nm-bone"] = dict(
    label="Anterior and posterior views of a real whole-body Tc-99m bone scan from a dual-head gamma camera",
    cap="A real whole-body bone scan (Tc-99m, GE Millennium MG gamma camera): the anterior and posterior views are acquired together by two detector heads as the patient moves through, and each is a projection of the whole body onto one plane. Dark is high uptake. Data: TCIA CMB-PCA (CC BY 4.0).",
    views=[dict(label="Bone scan", cols=2, facts=f"The matrix is {a.shape[2]} × {a.shape[1]} pixels of {pix:.2f} mm and the window of the Tc-99m photopeak is {e_lo:.0f} to {e_hi:.0f} keV. Each pixel holds a count of photons, at most {a.max():.0f} here, so the statistical noise is large, and structures at different depths overlap in a projection. The posterior view is seen from behind, so it is the mirror image of the anterior view.",
                panels=[panel(ia, "Anterior"), panel(ip, "Posterior")])])
src = dict(tcia.provenance(COL, "cmb_pca", row), figs=["real-nm-bone"], series=[row.SeriesDescription])
json.dump(dict(source="Real nuclear medicine image from a TCIA collection; tools/make_real_nm.py", idc_index_data=tcia.index_version(), figs=FIGS, sources=[src], stats=STATS), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e3), "KB"); print(json.dumps(STATS, indent=1))
