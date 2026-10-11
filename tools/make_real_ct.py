"""Real CT images from open TCIA collections, for the CT chapters. Writes src/real_ct.json (see tools/tcia.py for the data route and the licences).
  real-ct-noise   one uniform block of a test phantom scanned at four tube currents, with the measured noise
  real-ct-kernel  a textured block of the same phantom, one scan reconstructed with four kernels, with the measured noise
  real-ct-cbct    a planning CT and a cone-beam CT of one patient, on the same grid
  real-ct-metal   one chest CT reconstructed without and with iterative metal artifact reduction (iMAR)
Usage: python tools/make_real_ct.py [preview-folder]      Downloads about 700 MB the first time (cached; see TCIA_CACHE)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import tcia
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "real_ct.json")
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
IDX, COL = tcia.index()
FIGS, SOURCES = {}, {}

def source(coll, row, fig, series):
    s = SOURCES.setdefault(coll, dict(tcia.provenance(COL, coll, row), figs=[], series=[])); assert s["license"] == row.license_short_name, (coll, s["license"], row.license_short_name)
    if fig not in s["figs"]: s["figs"].append(fig)
    s["series"].append(series)

def preview(name, a):
    if PREVIEW:
        from PIL import Image
        os.makedirs(PREVIEW, exist_ok=True); Image.fromarray(a).save(os.path.join(PREVIEW, name + ".png"))

def panel(a, label, sub=None, **kw):
    return dict(label=label, sub=sub, w=int(a.shape[1]), h=int(a.shape[0]), img=tcia.uri(a, **kw))

# ---------------------------------------------------------------- the phantom: Credence Cartridge Radiomics, CC-Radiomics-Phantom-2 (GE Discovery STE)
PH = "cc_radiomics_phantom_2"

def phantom_slice(desc, z):
    r = tcia.one(IDX, collection_id=PH, SeriesDescription=desc); ds, zz, _ = tcia.slice_at(r, z_mm=z); return r, ds, tcia.physical(ds, ds.pixel_array)

def block_box(a):                                                                                  # the box that holds the cartridge: the largest connected piece above -300 HU (not the couch)
    lab, n = ndi.label(a > -300); k = 1 + int(np.argmax(ndi.sum(np.ones_like(a), lab, range(1, n + 1)))); ys, xs = np.where(lab == k); return ys.min(), ys.max(), xs.min(), xs.max()

# real-ct-noise: 120 kVp, 1.25 mm slices, 180 mm field of view, only the tube current changes; the uniform block is at z = -318 mm
MA, ZU = (50, 100, 200, 400), -318.0
tiles, sds, mean = [], [], None
for ma in MA:
    r, ds, a = phantom_slice(f"GE_DiscoverySTE_120_1.25_{ma}", ZU); assert int(float(ds.XRayTubeCurrent)) == ma and float(ds.KVP) == 120
    y0, y1, x0, x1 = block_box(a); cy, cx = (y0 + y1) // 2, (x0 + x1) // 2; h = int(0.22 * min(y1 - y0, x1 - x0))
    roi = a[cy - h:cy + h, cx - h:cx + h]; sds.append(float(roi.std())); mean = float(roi.mean()); px = float(ds.PixelSpacing[0]); mm = 2 * h * px
    tiles.append(panel(tcia.gray8(a[cy - 48:cy + 48, cx - 48:cx + 48], mean - 40, mean + 40), f"{ma} mA", f"SD {sds[-1]:.1f} HU", lossless=True)); preview(f"noise_{ma}", tcia.gray8(a[cy - 48:cy + 48, cx - 48:cx + 48], mean - 40, mean + 40))
    source(PH, r, "real-ct-noise", r.SeriesDescription)
exp = [sds[0] * (MA[0] / m) ** 0.5 for m in MA]                                                    # what 1 / sqrt(mA) predicts from the first point
FIGS["real-ct-noise"] = dict(
    label="Four real CT scans of a uniform block of a test phantom at tube currents of 50, 100, 200, and 400 mA, each with its measured noise",
    cap="Real scans of a uniform plastic block in a test phantom, on one scanner (GE Discovery STE, 120 kVp, 1.25 mm slices, standard kernel). Only the tube current changes. Each tile is a 34 mm square at a window of ±40 HU around the block's mean. Data: TCIA CC-Radiomics-Phantom-2 (CC BY 3.0).",
    views=[dict(label="Tube current", cols=4, facts=f"Noise is the standard deviation of the HU in a {mm:.0f} mm square of the block (mean {mean:.0f} HU): <span class=\"f\">{', '.join(f'{s:.1f}' for s in sds[:-1])}, and {sds[-1]:.1f} HU</span> at {', '.join(str(m) for m in MA[:-1])}, and {MA[-1]} mA. "
               f"Noise ∝ 1 / √(tube current) predicts {', '.join(f'{e:.1f}' for e in exp[:-1])}, and {exp[-1]:.1f} HU from the 50 mA value: the measurements agree within {100 * max(abs(s / e - 1) for s, e in zip(sds, exp)):.0f}%.", panels=tiles)])
STATS_NOISE = dict(mA=list(MA), sd=sds, mean=mean, roi_mm=mm)

# real-ct-kernel: one acquisition (120 kVp, 65 mA, 1.25 mm) reconstructed four ways; the uniform block is at z = -272 mm and the textured block at z = -209 mm
KN = (("Soft", "SOFT"), ("Standard", "STANDARD"), ("Lung", "LUNG"), ("Edge", "EDGE")); ZA, ZT = -272.0, -209.0
tiles, ksd, BOX = [], [], None
for nm, kern in KN:
    r, ds, a = phantom_slice(f"GE_DiscoverySTE_120_65_1.25_{nm}", ZA); assert str(ds.ConvolutionKernel) == kern
    BOX = BOX or block_box(a); y0, y1, x0, x1 = BOX; cy, cx = (y0 + y1) // 2, (x0 + x1) // 2; h = int(0.22 * min(y1 - y0, x1 - x0)); ksd.append(float(a[cy - h:cy + h, cx - h:cx + h].std()))
    _, _, b = phantom_slice(f"GE_DiscoverySTE_120_65_1.25_{nm}", ZT); t = tcia.gray8(b[cy - 48:cy + 48, cx - 48:cx + 48], -200, 500)
    tiles.append(panel(t, nm, f"SD {ksd[-1]:.0f} HU", lossless=True)); preview(f"kernel_{nm}", t); source(PH, r, "real-ct-kernel", r.SeriesDescription)
FIGS["real-ct-kernel"] = dict(
    label="A real textured block of a test phantom reconstructed with a soft, a standard, a lung, and an edge kernel from the same scan",
    cap="One scan of a textured block in a test phantom (GE Discovery STE, 120 kVp, 65 mA, 1.25 mm slices), reconstructed with four kernels. Each tile is a 47 mm square. The noise under each tile is the standard deviation of the HU in a uniform block scanned at the same time and reconstructed with the same kernel. Data: TCIA CC-Radiomics-Phantom-2 (CC BY 3.0).",
    views=[dict(label="Kernel", cols=4, facts=f"Same raw data, four kernels: the noise in the uniform block is <span class=\"f\">{', '.join(f'{s:.0f}' for s in ksd[:-1])}, and {ksd[-1]:.0f} HU</span>. The soft kernel smooths the texture and the noise, and the edge kernel keeps the finest detail and the most noise.", panels=tiles)])
STATS_KERNEL = dict(kernels=[k for _, k in KN], sd=ksd)

# ---------------------------------------------------------------- planning CT and cone-beam CT of one patient: Pancreatic-CT-CBCT-SEG, patient 002 (the CBCT was aligned and resampled onto the CT grid by the dataset authors)
PC, PID = "pancreatic_ct_cbct_seg", "Pancreas-CT-CB_002"
rc = tcia.one(IDX, collection_id=PC, PatientID=PID, SeriesDescription="DIBH, iDose (3)"); rb = tcia.one(IDX, collection_id=PC, PatientID=PID, SeriesDescription="Aligned CBCT01")
views, roi_info = [], None
for nm, z in (("Upper abdomen", -915.5), ("Lower chest", -847.5)):
    a, za, _ = tcia.slice_at(rc, z_mm=z); b, zb, _ = tcia.slice_at(rb, z_mm=z); assert abs(za - zb) < 0.01
    A, B = tcia.physical(a, a.pixel_array), tcia.physical(b, b.pixel_array)
    sl = (slice(138, 412), slice(72, 440))
    pa, pb = tcia.gray8(A[sl], -160, 240), tcia.gray8(B[sl], -160, 240); preview(f"cbct_{nm[:5]}_ct", pa); preview(f"cbct_{nm[:5]}_cbct", pb)
    facts = ""
    if nm == "Upper abdomen":                                                                       # noise in the liver (the quietest 24 pixel square there in the planning CT) and the mean HU of the same square
        _, y, x = min(((A[y:y + 24, x:x + 24].std(), y, x) for y in range(236, 310, 4) for x in range(106, 190, 4)))
        sdc, sdb = float(A[y:y + 24, x:x + 24].std()), float(B[y:y + 24, x:x + 24].std()); mc, mb = float(A[y:y + 24, x:x + 24].mean()), float(B[y:y + 24, x:x + 24].mean())
        roi_info = dict(liver_xy=[int(x), int(y)], sd_ct=sdc, sd_cbct=sdb, liver_ct=mc, liver_cbct=mb, pix_mm=float(a.PixelSpacing[0]))
        facts = (f"Noise in the liver (SD of a {24 * roi_info['pix_mm']:.0f} mm square): <span class=\"f\">{sdc:.0f} HU</span> on the planning CT and <span class=\"f\">{sdb:.0f} HU</span> on the cone-beam CT. The same square reads {mc:.0f} HU on the planning CT, "
                 f"where the vessels are enhanced, and {mb:.0f} HU on the cone-beam CT, where they are not.")
    else: facts = "At this level the cone-beam field of view cuts off the patient's right side (the left of the image): anatomy outside the reconstruction diameter is missing."
    views.append(dict(label=nm, cols=2, facts=facts, panels=[panel(pa, "Planning CT", f"{float(a.KVP):.0f} kVp, {float(a.SliceThickness):.0f} mm"), panel(pb, "Cone-beam CT", f"{float(b.KVP):.0f} kVp, {float(b.SliceThickness):.0f} mm")]))
source(PC, rc, "real-ct-cbct", rc.SeriesDescription); source(PC, rb, "real-ct-cbct", rb.SeriesDescription)
FIGS["real-ct-cbct"] = dict(
    label="A real planning CT and cone-beam CT of the same patient at the same level, in the upper abdomen and the lower chest",
    cap="Real images of one patient treated for pancreatic cancer: the planning CT (Philips Brilliance Big Bore, iterative reconstruction) and a cone-beam CT from the linac (Varian, reconstructed with the Ram-Lak filter), which the dataset's authors aligned to the planning CT. Both are shown at the same window. Data: TCIA Pancreatic-CT-CBCT-SEG (CC BY 4.0).",
    head="Level", views=views)
HDR_CBCT = dict(ct=dict(kvp=str(a.KVP), kernel=str(a.ConvolutionKernel), thick=str(a.SliceThickness)), cbct=dict(kvp=str(b.KVP), kernel=str(b.ConvolutionKernel), fov=float(b.ReconstructionDiameter)))

# ---------------------------------------------------------------- one chest CT, reconstructed twice from the same data: cmb_lca MSB-05332, series 'AX ST' and 'AX ST iMAR' (Siemens SOMATOM go.Top)
LC, LP, LS = "cmb_lca", "MSB-05332", "28320555"
s = IDX[(IDX.collection_id == LC) & (IDX.PatientID == LP) & IDX.StudyInstanceUID.str.endswith(LS)]
r0, r1 = tcia.one(s, SeriesDescription="AX ST"), tcia.one(s, SeriesDescription="AX ST iMAR")
V0, sp0, m0 = tcia.load_volume(r0); V1, sp1, m1 = tcia.load_volume(r1); assert V0.shape == V1.shape and np.allclose(m0["z"], m1["z"], atol=0.01)
d0, d1 = m0["dss"][0], m1["dss"][0]; assert str(d0.KVP) == str(d1.KVP) and str(d0.SliceThickness) == str(d1.SliceThickness)
views = []; msd = []
for nm, k in (("Spine", 104), ("Shoulders", 96)):
    A, B = V0[k], V1[k]; w = np.abs(A - B) * (A > -300); cy, cx = ndi.center_of_mass(w); ch, cw = 300, 400
    y0 = int(np.clip(cy - ch / 2, 0, A.shape[0] - ch)); x0 = int(np.clip(cx - cw / 2, 0, A.shape[1] - cw)); sl = (slice(y0, y0 + ch), slice(x0, x0 + cw))
    pa, pb = tcia.gray8(A[sl], -160, 240), tcia.gray8(B[sl], -160, 240); preview(f"metal_{nm}_std", pa); preview(f"metal_{nm}_imar", pb)
    views.append(dict(label=nm, cols=2, panels=[panel(pa, "Standard", None), panel(pb, "With iMAR", None)]))
    msd.append(dict(k=k, z=float(m0["z"][k]), box=[y0, x0, ch, cw]))
source(LC, r0, "real-ct-metal", r0.SeriesDescription); source(LC, r1, "real-ct-metal", r1.SeriesDescription)
FIGS["real-ct-metal"] = dict(
    label="A real chest CT with metal implants, reconstructed from the same data without and with iterative metal artifact reduction, at the level of the spine and the shoulders",
    cap="One real chest CT (Siemens SOMATOM go.Top, 100 kVp, 3 mm slices) with metal implants, reconstructed from the same raw data in two ways: the standard reconstruction (left) and Siemens iMAR, an iterative metal artifact reduction (right). Both are shown at the window 40 ± 200 HU. Data: TCIA CMB-LCA (CC BY 4.0).",
    head="Level", views=views)
STATS_METAL = msd

json.dump(dict(source="Real CT images from TCIA collections (see sources); tools/make_real_ct.py", idc_index_data=tcia.index_version(), figs=FIGS, sources=list(SOURCES.values()),
               stats=dict(noise=STATS_NOISE, kernel=STATS_KERNEL, cbct=roi_info, cbct_hdr=HDR_CBCT, metal=STATS_METAL, hdr=[dict(label="CT slice", modality="CT", rows=int(a.Rows), cols=int(a.Columns), pixel_mm=float(a.PixelSpacing[0]), stored=int(a.BitsStored), allocated=int(a.BitsAllocated))])), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e3), "KB;", {k: sum(len(p['img']) for v in f['views'] for p in v['panels']) // 1000 for k, f in FIGS.items()}, "KB of images")
print(json.dumps(dict(noise=STATS_NOISE, kernel=STATS_KERNEL, cbct=roi_info, metal=STATS_METAL), indent=1))
