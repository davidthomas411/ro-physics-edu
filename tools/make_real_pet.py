"""Real PET images from open TCIA collections, for the PET chapter. Writes src/real_pet.json (see tools/tcia.py for the data route and the licences).
  real-pet-ac       one FDG scan of a patient with a lung tumour, reconstructed without and with attenuation correction: a coronal MIP and an axial slice
  real-pet-suv      the CT, the PET in SUV, and the fusion of the same slice, with the SUV worked out from the DICOM header
  real-pet-tracers  coronal MIPs of three F-18 tracers: FDG, sodium fluoride (bone), and PSMA
Usage: python tools/make_real_pet.py [preview-folder]      Downloads about 350 MB the first time (cached; see TCIA_CACHE)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as ndi
import tcia
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "real_pet.json")
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
IDX, COL = tcia.index()
FIGS, SOURCES, STATS = {}, {}, {}

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

inv = lambda a, hi: 255 - tcia.gray8(a, 0, hi)                                                      # PET is shown dark on light, as a MIP usually is

def mip(Vs, sps, px):
    """Coronal MIP of a standardized volume (head at the top, patient's right on the left) on square pixels of px mm."""
    return ndi.zoom(Vs.max(axis=1)[::-1], (sps[0] / px, sps[2] / px), order=1)

def mip_box(m, px, width_mm, length_mm):
    """A crop that starts at the top of the body and is centred on it: (z0, z1, x0, x1) in pixels."""
    on = m > 0.02 * np.percentile(m, 99.5); rows = np.where(on.any(axis=1))[0]; cols = np.where(on.sum(axis=0) > 3)[0]
    cx = int(np.median(cols)); w = int(width_mm / px); z0 = int(rows.min()); return z0, min(m.shape[0], z0 + int(length_mm / px)), max(0, cx - w // 2), cx + w // 2

# ---------------------------------------------------------------- FDG, one patient of NSCLC Radiogenomics: GE Discovery STE, a lung tumour; the same scan reconstructed without (NAC) and with (AC) attenuation correction
NS, NP = "nsclc_radiogenomics", "R01-054"
rac = tcia.one(IDX, collection_id=NS, PatientID=NP, SeriesDescription="TORSO_3D_AC", Modality="PT"); rnac = tcia.one(IDX, collection_id=NS, PatientID=NP, SeriesDescription="TORSO_3D_NAC", Modality="PT")
rct = tcia.one(IDX, collection_id=NS, PatientID=NP, SeriesDescription="CT_SLICES", Modality="CT")
Vac, spa, ma = tcia.load_volume(rac); Vnac, spn, mn = tcia.load_volume(rnac)
fac, info = tcia.suv_factor(ma["dss"]); S = Vac * fac
ca, cn = list(ma["dss"][0].CorrectedImage), list(mn["dss"][0].CorrectedImage); assert "ATTN" in ca and "SCAT" in ca and "ATTN" not in cn and "SCAT" not in cn
assert str(ma["dss"][0].Units) == "BQML" and str(mn["dss"][0].Units) != "BQML"
Sa, sps = tcia.standardize(S, spa, ma["dirs"]); Sn, _ = tcia.standardize(Vnac, spn, mn["dirs"])
PX = 3.27
mA_, mN_ = mip(Sa, sps, PX), mip(Sn, sps, PX); box = mip_box(mA_, PX, 480, 840); z0, z1, x0, x1 = box
cropm = lambda m: m[z0:z1, x0:x1]
HI_A = 8.0                                                                                          # SUV window of the corrected MIP; the NAC image has no unit, so its window is set from its own distribution in the same way
hi_n = HI_A / np.percentile(cropm(mA_), 99.5) * np.percentile(cropm(mN_), 99.5)
ma_img, mn_img = inv(cropm(mA_), HI_A), inv(cropm(mN_), hi_n); preview("fdg_mip_ac", ma_img); preview("fdg_mip_nac", mn_img)

# the axial slice through the tumour: the standardized slice index of the strongest voxel in the chest
nz = Sa.shape[0]; kz = int(np.unravel_index(np.argmax(Sa[int(nz * 0.62):int(nz * 0.85)]), Sa[int(nz * 0.62):int(nz * 0.85)].shape)[0]) + int(nz * 0.62)
tmax = float(Sa[kz].max()); ty, tx = np.unravel_index(np.argmax(Sa[kz]), Sa[kz].shape)
source(NS, rac, "real-pet-ac", rac.SeriesDescription); source(NS, rnac, "real-pet-ac", rnac.SeriesDescription); source(NS, rct, "real-pet-suv", rct.SeriesDescription); source(NS, rac, "real-pet-suv", rac.SeriesDescription); source(NS, rac, "real-pet-tracers", rac.SeriesDescription)
pet_mm = float(spa[1])
# ---------------------------------------------------------------- the CT and the fusion at the same slice
dss_ct = None
rk = [k for k, _ in tcia.list_series(rct)]; hs = tcia.headers(rct, rk); order, zc = tcia.order_by_position(hs)
org_a, M_a = tcia.geometry(ma, spa)
# patient z of the standardized slice kz: the PET volume is sorted along its own slice normal; find it from the geometry
dk = ma["dirs"]["k"]; flipped = dk[np.argmax(np.abs(dk))] < 0; kn = (nz - 1 - kz) if flipped else kz; zt = float(ma["z"][kn])
ic = order[int(np.argmin(np.abs(zc[order] - zt)))]; ct = tcia.dcm(tcia.fetch(rct, rk[ic])); H = tcia.physical(ct, ct.pixel_array)
pts = tcia.slice_points(ct); P = tcia.sample(S, org_a, M_a, pts); Pn = tcia.sample(Vnac, *tcia.geometry(mn, spn), pts)
lab, n = ndi.label(H > -300); keep = 1 + int(np.argmax(ndi.sum(np.ones_like(H), lab, range(1, n + 1)))); bm = ndi.binary_fill_holes(lab == keep); yy, xx = np.where(bm)
cs = (slice(max(0, yy.min() - 8), yy.max() + 8), slice(max(0, xx.min() - 8), xx.max() + 8))
ct_img = tcia.gray8(H[cs], -160, 240); pet_img = inv(P[cs], 10.0)
t = np.clip(P[cs] / 10.0, 0, 1); a = np.clip(t * 1.6, 0, 0.85)[..., None]; fused = np.round(255 * ((1 - a) * np.dstack([ct_img / 255.0] * 3) + a * tcia.hot(t))).astype(np.uint8)
cols = np.arange(H.shape[1])[None, :] * np.ones_like(H); xm = float(np.where(bm)[1].mean()); tumour_col = float(np.where(P > 0.5 * P.max())[1].mean())
far = cols > xm if tumour_col < xm else cols < xm                                                      # the half of the body that does not hold the tumour
lung = (H < -700) & bm & far; lung_suv = float(P[lung].mean()); tum = float(P.max())
conc_kbq = tmax / fac / 1000.0; act_scan = info["dose_MBq"] * 2 ** (-info["uptake_min"] / info["half_life_min"])
for nm, im in (("ct", ct_img), ("pet", pet_img), ("fused", fused)): preview(f"fdg_fuse_{nm}", im)
STATS["suv"] = dict(weight_kg=info["weight_kg"], dose_MBq=info["dose_MBq"], uptake_min=info["uptake_min"], half_life_min=info["half_life_min"], act_scan_MBq=act_scan, factor=fac, tumour_suvmax=tmax, tumour_kbq_ml=conc_kbq, lung_suv=lung_suv,
                    pet_mm=pet_mm, pet_matrix=int(ma["dss"][0].Rows), ct_mm=float(ct.PixelSpacing[0]), ct_matrix=int(ct.Rows), tumour_xyz_idx=[int(kz), int(ty), int(tx)])
FIGS["real-pet-suv"] = dict(
    label="The CT, the PET in standardized uptake value, and the PET/CT fusion of one axial slice through a lung tumour",
    cap="One axial slice of a real FDG PET/CT of a patient with a lung tumour (GE Discovery STE): the CT, the PET (dark is high uptake, scale 0 to SUV 10), and the PET in colour over the CT. The PET is resampled onto the CT grid. Data: TCIA NSCLC Radiogenomics (CC BY 3.0).",
    views=[dict(label="PET/CT", cols=3, facts=f"Header values: {info['weight_kg']:.0f} kg, {info['dose_MBq']:.0f} MBq injected, scanned {info['uptake_min']:.0f} min later, half-life {info['half_life_min']:.1f} min, so {act_scan:.0f} MBq remain at the scan. A concentration of {conc_kbq:.0f} kBq/mL "
                                                f"in the tumour is <span class=\"f\">SUV {tmax:.1f}</span> (SUV = concentration × weight / remaining activity). The lung on the other side averages SUV {lung_suv:.1f}. The PET pixels are {pet_mm:.1f} mm and the CT pixels {float(ct.PixelSpacing[0]):.2f} mm.",
                panels=[panel(ct_img, "CT", f"{float(ct.PixelSpacing[0]):.2f} mm pixels"), panel(pet_img, "PET", f"{pet_mm:.1f} mm pixels"), panel(fused, "PET/CT")])])

HI_AX = 8.0; hi_nx = HI_AX / np.percentile(P[cs], 99.5) * np.percentile(Pn[cs], 99.5)                 # the same grey for the tumour in both; the uncorrected image has no unit
ax_a_img, ax_n_img = inv(P[cs], HI_AX), inv(Pn[cs], hi_nx); preview("fdg_ax_ac", ax_a_img); preview("fdg_ax_nac", ax_n_img)
FIGS["real-pet-ac"] = dict(
    label="Real FDG PET of a patient with a lung tumour reconstructed without and with attenuation correction, as a coronal maximum-intensity projection and as an axial slice",
    cap="One real FDG PET scan of a patient with a lung tumour (GE Discovery STE), reconstructed twice from the same data: without attenuation correction (left) and with CT-based attenuation correction (right). Dark is high uptake. Data: TCIA NSCLC Radiogenomics (CC BY 3.0).",
    head="View", views=[
        dict(label="Coronal MIP", cols=2, facts=f"The corrected series lists attenuation (ATTN) and scatter (SCAT) correction in its DICOM header, and the uncorrected one lists neither. Without correction the liver almost disappears, and the surface of the body and the arms look hot.",
             panels=[panel(mn_img, "No correction"), panel(ma_img, "Corrected")]),
        dict(label="Axial slice", cols=2, facts="At the level of the tumour, without correction the skin is outlined by a bright rim, the interior is noisy, and streaks distort the tumour. Photons from deep sites are attenuated more, so fewer of them are counted, and the deep tissue is under-represented.",
             panels=[panel(ax_n_img, "No correction"), panel(ax_a_img, "Corrected")])])


# ---------------------------------------------------------------- three F-18 tracers on the same footing (4 mm pixels, the same length of body, a window in SUV for each)
def tracer(row, hi, width=480, length=900):
    V, sp, meta = tcia.load_volume(row); f, inf = tcia.suv_factor(meta["dss"]); Vs, sps = tcia.standardize(V * f, sp, meta["dirs"]); m = mip(Vs, sps, 4.0)
    b = mip_box(m, 4.0, width, length); img = inv(m[b[0]:b[1], b[2]:b[3]], hi); return img, inf, meta
NF, NFP = "naf_prostate", "NaF-PROSTATE-01-0004"
rn = IDX[(IDX.collection_id == NF) & (IDX.PatientID == NFP) & IDX.SeriesDescription.str.contains(r"WB_CTAC.*Total Body *$", regex=True)].sort_values(["StudyDate", "instanceCount"], ascending=[True, False]).iloc[0]
PS, PSP = "psma_pet_ct_lesions", "PSMA_0198cdca94fbb95f"
rp = IDX[(IDX.collection_id == PS) & (IDX.PatientID == PSP) & (IDX.Modality == "PT")].sort_values("StudyDate").iloc[0]
m4 = mip(Sa, sps, 4.0); b4 = mip_box(m4, 4.0, 480, 900); fdg_img = inv(m4[b4[0]:b4[1], b4[2]:b4[3]], 8.0)
naf_img, inf_n, mn_ = tracer(rn, 25.0); psma_img, inf_p, mp_ = tracer(rp, 20.0)
for nm, im in (("fdg", fdg_img), ("naf", naf_img), ("psma", psma_img)): preview("tracer_" + nm, im)
source(NF, rn, "real-pet-tracers", rn.SeriesDescription); source(PS, rp, "real-pet-tracers", rp.SeriesDescription)
STATS["tracers"] = dict(nuclide_half_life_min=info["half_life_min"], windows_suv=dict(fdg=8.0, naf=25.0, psma=20.0))
FIGS["real-pet-tracers"] = dict(
    label="Coronal maximum-intensity projections of real PET scans with three F-18 tracers: FDG, sodium fluoride, and PSMA",
    cap="Real coronal MIPs of three patients, each scanned with an F-18 tracer: FDG (a patient with a lung tumour), sodium fluoride (a patient from a prostate cancer study), and a PSMA ligand (a patient from a prostate cancer study; the head is blank in these images as released). Dark is high uptake. Data: TCIA NSCLC Radiogenomics (CC BY 3.0), NaF PROSTATE (CC BY 3.0), and PSMA-PET-CT-Lesions (CC BY 4.0).",
    views=[dict(label="Tracers", cols=3, facts=f"All three tracers carry F-18, with a half-life of {info['half_life_min']:.0f} min, but they follow different processes, so the pictures differ. FDG (glucose use) shows the brain, the kidneys, the bladder, and the tumour. Sodium fluoride (bone formation) shows the skeleton, with excretion through the kidneys and bladder. "
                                  f"The PSMA ligand shows the kidneys, the liver, the spleen, the bowel, the bladder, and the lesions.", panels=[panel(fdg_img, "FDG", "glucose use"), panel(naf_img, "NaF", "bone formation"), panel(psma_img, "PSMA", "PSMA binding")])])

STATS["hdr"] = [dict(label="PET slice, FDG", modality="PT", rows=int(ma["dss"][0].Rows), cols=int(ma["dss"][0].Columns), pixel_mm=float(ma["dss"][0].PixelSpacing[0]), stored=int(ma["dss"][0].BitsStored), allocated=int(ma["dss"][0].BitsAllocated)), dict(label="PET slice, PSMA", modality="PT", rows=int(mp_["dss"][0].Rows), cols=int(mp_["dss"][0].Columns), pixel_mm=float(mp_["dss"][0].PixelSpacing[0]), stored=int(mp_["dss"][0].BitsStored), allocated=int(mp_["dss"][0].BitsAllocated))]
json.dump(dict(source="Real PET images from TCIA collections (see sources); tools/make_real_pet.py", idc_index_data=tcia.index_version(), figs=FIGS, sources=list(SOURCES.values()), stats=STATS), open(OUT, "w"), separators=(",", ":"))
print("wrote", os.path.abspath(OUT), round(os.path.getsize(OUT) / 1e3), "KB;", {k: sum(len(p['img']) for v in f['views'] for p in v['panels']) // 1000 for k, f in FIGS.items()}, "KB of images")
print(json.dumps(STATS, indent=1, default=float))
