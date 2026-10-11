"""Helpers for the make_real_*.py tools: real clinical images from open-licence The Cancer Imaging Archive (TCIA) collections.

The collections are read as DICOM from the public buckets of the NCI Imaging Data Commons (IDC), which republishes TCIA collections with their licences and DOIs.
Nothing here needs credentials. Only attribution-only licences (CC BY 3.0, CC BY 4.0) are used.
Needs: pip install numpy scipy pillow pydicom pandas pyarrow idc-index-data   (the build itself needs none of these).
Environment: TCIA_CACHE = a folder for downloaded instances (default: the system temp folder). Downloads are cached and resumable."""
import base64, io, os, re, tempfile, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import numpy as np

CACHE = os.environ.get("TCIA_CACHE") or os.path.join(tempfile.gettempdir(), "tcia_cache")
OPEN = ("CC BY 3.0", "CC BY 4.0")
_NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


# ---------------------------------------------------------------- the IDC index and provenance
def index():
    """(series index, collection table) from the idc-index-data package: one row per DICOM series, with licence, bucket and series uuid."""
    import idc_index_data, pandas as pd
    d = os.path.dirname(idc_index_data.__file__)
    return pd.read_parquet(d + "/idc_index.parquet"), pd.read_parquet(d + "/collections_index.parquet")


def index_version():
    import idc_index_data
    return idc_index_data.__version__


def rows(IDX, **kw):
    """Index rows whose columns equal the given values (a list means any of them)."""
    m = np.ones(len(IDX), bool)
    for k, v in kw.items(): m &= IDX[k].isin(v if isinstance(v, (list, tuple, set)) else [v]).values
    return IDX[m]


def one(IDX, **kw):
    """The single index row for a series; raises if there is none. With several matches the one with the most instances is used."""
    r = rows(IDX, **kw)
    if not len(r): raise LookupError(f"no series for {kw}")
    return r.sort_values("instanceCount", ascending=False).iloc[0]


def provenance(COL, collection_id, row=None):
    """The attribution record of a collection: name, DOI, licence, and the citation text that IDC gives (HTML removed)."""
    c = COL[COL.collection_id == collection_id].iloc[0]; s = c["sources"][0]
    cite = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s["citation"]).replace("&amp;", "&")).strip()
    lic = row.license_short_name if row is not None else s["license"]["license_short_name"]
    assert lic in OPEN, (collection_id, lic)
    return dict(collection=c["collection_name"], id=collection_id, doi=s["source_doi"], license=lic, citation=cite)


# ---------------------------------------------------------------- download
def _get(url, headers=None, tries=5):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=120) as r: return r.read()
        except Exception:
            if k == tries - 1: raise
            time.sleep(1.5 * (k + 1))


def list_series(row):
    """[(key, size)] of the instances of one series (S3 ListObjectsV2 on the public bucket)."""
    out, token = [], None
    while True:
        u = f"https://{row.aws_bucket}.s3.amazonaws.com/?list-type=2&prefix={row.crdc_series_uuid}/" + (f"&continuation-token={urllib.parse.quote(token)}" if token else "")
        root = ET.fromstring(_get(u))
        for c in root.findall("s3:Contents", _NS):
            key, size = c.find("s3:Key", _NS).text, int(c.find("s3:Size", _NS).text)
            if not key.endswith("/") and size > 0: out.append((key, size))
        t = root.find("s3:NextContinuationToken", _NS)
        if t is None: return sorted(out)
        token = t.text


def fetch(row, key, nbytes=None):
    """The bytes of one instance, cached on disk. nbytes: only the first nbytes (enough for a header), cached separately."""
    p = os.path.join(CACHE, row.aws_bucket, key + (f".head{nbytes}" if nbytes else ""))
    if os.path.exists(p): return open(p, "rb").read()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    data = _get(f"https://{row.aws_bucket}.s3.amazonaws.com/{key}", {"Range": f"bytes=0-{nbytes - 1}"} if nbytes else None)
    with open(p + ".part", "wb") as f: f.write(data)
    os.replace(p + ".part", p); return data


def fetch_many(row, keys, nbytes=None, workers=12):
    with ThreadPoolExecutor(workers) as ex: return list(ex.map(lambda k: fetch(row, k, nbytes), keys))


# ---------------------------------------------------------------- DICOM
def dcm(data, pixels=True):
    import pydicom
    return pydicom.dcmread(io.BytesIO(data), stop_before_pixels=not pixels, force=True)


def headers(row, keys, nbytes=24576):
    """Parsed headers (no pixels) of many instances from a range read of the first bytes of each."""
    return [dcm(d, pixels=False) for d in fetch_many(row, keys, nbytes=nbytes)]


def normal(ds):
    iop = np.array([float(x) for x in ds.ImageOrientationPatient]); return np.cross(iop[:3], iop[3:])


def order_by_position(hs):
    """(order, z): the sort order of single-frame instances along the slice normal, and their positions in mm."""
    n = normal(hs[0]); z = np.array([float(np.dot(n, [float(x) for x in h.ImagePositionPatient])) for h in hs]); return np.argsort(z), z


def physical(ds, a):
    """Stored values -> HU, Bq/mL, and so on (rescale slope and intercept)."""
    return a.astype(np.float32) * float(getattr(ds, "RescaleSlope", 1) or 1) + float(getattr(ds, "RescaleIntercept", 0) or 0)


def slice_at(row, z_mm=None, frac=0.5, keys=None):
    """(dataset with pixels, z, sorted z of the series) for the instance nearest z_mm along the slice normal, or at a fraction of the series."""
    keys = keys or [k for k, _ in list_series(row)]
    hs = headers(row, keys); order, z = order_by_position(hs); zs = z[order]
    i = order[int(round(frac * (len(order) - 1)))] if z_mm is None else order[int(np.argmin(np.abs(zs - z_mm)))]
    return dcm(fetch(row, keys[i])), float(z[i]), zs


def load_volume(row, workers=12):
    """A whole single-frame series: (V[k, r, c] in physical units sorted along the slice normal, (dz, dr, dc) in mm, meta).
    meta holds the sorted datasets (no need to keep pixels), their z positions, and the direction in patient (LPS) space of the three index axes."""
    keys = [k for k, _ in list_series(row)]
    dss = [dcm(d) for d in fetch_many(row, keys, workers=workers)]
    order, z = order_by_position(dss); dss = [dss[i] for i in order]; z = z[order]
    V = np.stack([physical(d, d.pixel_array) for d in dss]).astype(np.float32)
    iop = np.array([float(x) for x in dss[0].ImageOrientationPatient]); n = np.cross(iop[:3], iop[3:]); ps = [float(x) for x in dss[0].PixelSpacing]
    dz = float(np.median(np.diff(z))) if len(z) > 1 else float(getattr(dss[0], "SliceThickness", 1) or 1)
    for d in dss: d.PixelData = b""                                                                # the pixels are in V now
    return V, (abs(dz), ps[0], ps[1]), dict(dss=dss, z=z, dirs=dict(k=n, r=iop[3:], c=iop[:3]))


def standardize(V, spacing, dirs):
    """Reorder a volume to Vs[z, y, x] with z toward the head, y toward the back and x toward the patient's left, each increasing with its index. Returns (Vs, (dz, dy, dx) in mm)."""
    ax = {"k": 0, "r": 1, "c": 2}; names = ["x", "y", "z"]; assign = {}
    for a, vec in dirs.items():
        j = int(np.argmax(np.abs(vec))); assign[names[j]] = (ax[a], 1 if vec[j] > 0 else -1)
    assert set(assign) == {"x", "y", "z"}, assign
    perm = [assign["z"][0], assign["y"][0], assign["x"][0]]; out = np.transpose(V, perm); sp = tuple(spacing[p] for p in perm)
    for i, nm in enumerate(["z", "y", "x"]):
        if assign[nm][1] < 0: out = np.flip(out, axis=i)
    return np.ascontiguousarray(out), sp


def geometry(meta, spacing):
    """(origin, M) of a volume in patient space: the position of voxel [0, 0, 0] and the matrix whose columns are the step for one index along (k, r, c)."""
    d = meta["dirs"]; return np.array([float(x) for x in meta["dss"][0].ImagePositionPatient]), np.stack([d["k"] * spacing[0], d["r"] * spacing[1], d["c"] * spacing[2]], axis=1)


def slice_points(ds):
    """Patient coordinates (rows, cols, 3) of the pixel centres of one slice."""
    iop = np.array([float(x) for x in ds.ImageOrientationPatient]); ipp = np.array([float(x) for x in ds.ImagePositionPatient]); ps = [float(x) for x in ds.PixelSpacing]
    r, c = np.mgrid[0:ds.Rows, 0:ds.Columns]
    return ipp + r[..., None] * ps[0] * iop[3:] + c[..., None] * ps[1] * iop[:3]


def sample(V, origin, M, pts, order=1, cval=0.0):
    """Trilinear samples of V[k, r, c] at patient points pts (..., 3): how a volume is resampled onto another image grid."""
    from scipy import ndimage as ndi
    idx = np.linalg.solve(M, (pts.reshape(-1, 3) - origin).T)
    return ndi.map_coordinates(V, idx, order=order, mode="constant", cval=cval).reshape(pts.shape[:-1])


def coronal_mip(Vs, sp):
    """Coronal maximum-intensity projection of a standardized volume (head at the top, patient's right on the left), on square pixels of the finer spacing. Returns (image, pixel mm)."""
    from scipy import ndimage as ndi
    px = min(sp[0], sp[2]); return ndi.zoom(Vs.max(axis=1)[::-1], (sp[0] / px, sp[2] / px), order=1), px


# ---------------------------------------------------------------- PET
def hhmmss(s):
    s = str(s).split(".")[0].zfill(6); return int(s[:2]) * 3600 + int(s[2:4]) * 60 + int(s[4:6])


def suv_factor(dss):
    """(factor, info): multiply Bq/mL by factor for the SUV by body weight. From the header: weight, injected dose, injection time, half-life,
    and the earliest acquisition time (the images are decay corrected to the start of the scan)."""
    d0 = dss[0]; r0 = d0.RadiopharmaceuticalInformationSequence[0]
    dose, half, t_inj = float(r0.RadionuclideTotalDose), float(r0.RadionuclideHalfLife), hhmmss(r0.RadiopharmaceuticalStartTime)
    t_scan = min(hhmmss(d.AcquisitionTime) for d in dss if "AcquisitionTime" in d); dt = t_scan - t_inj
    if dt < -43200: dt += 86400
    return float(d0.PatientWeight) * 1000.0 / (dose * 2 ** (-dt / half)), dict(weight_kg=float(d0.PatientWeight), dose_MBq=dose / 1e6, uptake_min=dt / 60.0, half_life_min=half / 60.0)


# ---------------------------------------------------------------- images
def gray8(a, lo, hi, gamma=1.0):
    """Linear window lo..hi -> 0..255 (uint8)."""
    t = np.clip((np.asarray(a, np.float32) - lo) / (hi - lo), 0, 1); return np.round(255 * (t ** gamma if gamma != 1.0 else t)).astype(np.uint8)


def hot(t):
    """Black -> red -> yellow -> white, for t in 0..1 (float RGB)."""
    t = np.clip(t, 0, 1); return np.dstack([np.clip(3 * t, 0, 1), np.clip(3 * t - 1, 0, 1), np.clip(3 * t - 2, 0, 1)])


def uri(a, quality=84, lossless=False, fmt="webp"):
    """A data: URI of a uint8 image (2-D grey or 3-D RGB). WebP, lossy by default; lossless where the noise itself is the content."""
    from PIL import Image
    im = Image.fromarray(a); b = io.BytesIO()
    if fmt == "webp": im.save(b, "WEBP", lossless=lossless, quality=100 if lossless else quality, method=6)
    else: im.save(b, "PNG", optimize=True)
    return f"data:image/{fmt};base64," + base64.b64encode(b.getvalue()).decode()


def crop_box(a, y0, y1, x0, x1):
    return a[max(0, y0):y1, max(0, x0):x1]
