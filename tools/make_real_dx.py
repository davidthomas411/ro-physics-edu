"""A real digital chest radiograph for the radiography chapter, with the exposure factors that its DICOM header records: a portable AP chest on a flat-panel detector, from TCIA's COVID-19-AR collection.
Writes src/real_dx.json.   Usage: python tools/make_real_dx.py [preview-folder]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import tcia
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "real_dx.json")
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
IDX, COL = tcia.index()
row = tcia.one(IDX, collection_id="covid_19_ar", PatientID="COVID-19-AR-16406496", Modality="DX", SeriesDescription="AP")
ds = tcia.dcm(tcia.fetch(row, tcia.list_series(row)[0][0])); a = ds.pixel_array.astype(np.float32)
assert str(ds.PhotometricInterpretation) == "MONOCHROME2" and str(ds.BurnedInAnnotation) == "NO" and str(ds.Modality) == "DX"
lo, hi = np.percentile(a, 0.5), np.percentile(a, 99.5); g = tcia.gray8(a, lo, hi)
W = 640; small = np.asarray(Image.fromarray(g).resize((W, int(round(W * g.shape[0] / g.shape[1]))), Image.LANCZOS))
if PREVIEW:
    os.makedirs(PREVIEW, exist_ok=True); Image.fromarray(small).save(os.path.join(PREVIEW, "dx_chest.png"))
H = dict(kvp=float(ds.KVP), mas=float(ds.ExposureInuAs) / 1000.0, ms=float(ds.ExposureTime), grid=str(ds.Grid).title(), detector=str(ds.DetectorType).title(), model=str(ds.ManufacturerModelName), rows=int(ds.Rows), cols=int(ds.Columns),
         pixel_mm=float(ds.ImagerPixelSpacing[0]), stored=int(ds.BitsStored), allocated=int(ds.BitsAllocated), view=str(ds.ViewPosition))
assert H["grid"] == "None" and H["detector"] == "Scintillator"
FIGS = {"real-dx-chest": dict(
    label="A real portable anteroposterior chest radiograph made on a digital flat-panel detector, with the exposure factors from its DICOM header",
    cap=f"A real portable anteroposterior chest radiograph ({H['model']}, a flat-panel detector with a scintillator). The image is reduced from {H['cols']} × {H['rows']} pixels. Data: TCIA COVID-19-AR (CC BY 4.0).",
    views=[dict(label="Chest radiograph", cols=1, facts=f"Technique from the DICOM header: <span class=\"f\">{H['kvp']:g} kVp, {H['mas']:.1f} mAs</span> in {H['ms']:g} ms, no anti-scatter grid. The matrix is {H['cols']} × {H['rows']} pixels of {H['pixel_mm']:.3f} mm, stored with {H['stored']} bits in {H['allocated']}-bit words.",
                panels=[dict(label=None, sub=None, w=int(small.shape[1]), h=int(small.shape[0]), img=tcia.uri(small, quality=86))])])}
src = dict(tcia.provenance(COL, "covid_19_ar", row), figs=["real-dx-chest"], series=[f"{row.Modality} {row.SeriesDescription}"])
hdr = [dict(label="Chest radiograph", modality="DX", rows=H["rows"], cols=H["cols"], pixel_mm=H["pixel_mm"], stored=H["stored"], allocated=H["allocated"])]
json.dump(dict(source="Real radiograph from a TCIA collection; tools/make_real_dx.py", idc_index_data=tcia.index_version(), figs=FIGS, sources=[src], stats=dict(dx=H, hdr=hdr)), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e3), "KB"); print(json.dumps(H, indent=1))
