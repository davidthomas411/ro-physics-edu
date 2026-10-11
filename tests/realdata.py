"""The real clinical images (src/real_*.json, built by tools/make_real_*.py from open TCIA collections): licences and attribution, the images decode to the stored size, no patient identifiers,
the figures are used and registered, and the measured numbers agree with the physics and with each other."""
import base64, io, json, math, re, sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]            # tests/numbers.py would shadow the standard module that numpy imports
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
import real
from topics import TOPICS
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
files = sorted((ROOT / "src").glob("real_*.json")); J = {f.stem[5:]: json.loads(f.read_text()) for f in files}
check(set(J) == {"ct", "pet", "mr", "nm", "dx"}, f"data files for the five modalities: {sorted(J)}")
FIGS, SRC = real.FIGS, real.SOURCES
decl = {b[1] for t in TOPICS for b in t["guide"] if b[0] == "avf" and b[1].startswith("real-")}
check(decl == set(FIGS), f"every real figure is placed in a chapter and every placed one has data (placed {len(decl)}, data {len(FIGS)}; difference {decl ^ set(FIGS)})")
app = (ROOT / "src" / "app.js").read_text()
check(all(f"AV['{i}']=root=>realFig(root,'{i}');" in app for i in FIGS), "every real figure is registered in app.js")
# ---- attribution
OK = {"CC BY 3.0", "CC BY 4.0"}
for s in SRC:
    check(s["license"] in OK, f"{s['collection']}: licence {s['license']} is an attribution-only licence")
    check(re.fullmatch(r"10\.\d{4,}/\S+", s["doi"]) is not None and len(s["citation"]) > 60 and s["figs"], f"{s['collection']}: DOI, citation, and the figures it is used in")
    check(all(f in FIGS for f in s["figs"]), f"{s['collection']}: its figures exist")
for fid, f in FIGS.items():
    srcs = [s for s in SRC if fid in s["figs"]]
    check(srcs != [], f"{fid}: has at least one source")
    for s in srcs: check(f"{s['collection']} ({s['license']})" in f["cap"], f"{fid}: the caption names {s['collection']} and its licence {s['license']}")
    check(re.search(r"\breal\b", f["cap"] + f["label"], re.I) is not None and "Data:" in f["cap"], f"{fid}: the caption says it is real and has a Data: credit")
    check(len(f["cap"]) > 120 and len(f["label"]) > 40, f"{fid}: caption and label are written out")
# ---- images
tot = 0; dims = []
for fid, f in FIGS.items():
    check(1 <= len(f["views"]) <= 3 and (len(f["views"]) == 1 or f.get("head")), f"{fid}: one to three views, with a heading for the buttons when there are several")
    for v in f["views"]:
        check(1 <= v["cols"] <= 4 and 1 <= len(v["panels"]) <= 4 and v["cols"] <= len(v["panels"]) or v["cols"] == 1, f"{fid}/{v['label']}: {len(v['panels'])} panels in {v['cols']} columns")
        for p in v["panels"]:
            m = re.fullmatch(r"data:image/(webp|png);base64,(.+)", p["img"]); check(m is not None, f"{fid}: a data URI image")
            im = Image.open(io.BytesIO(base64.b64decode(m.group(2)))); im.load(); tot += len(p["img"]); dims.append(len(p["img"]))
            check(im.size == (p["w"], p["h"]) and 60 <= p["w"] <= 1000 and 60 <= p["h"] <= 1000, f"{fid}/{p.get('label')}: the image is {im.size}, stored as {p['w']} x {p['h']}")
            a = np.asarray(im.convert("L")); check(a.std() > 5 and a.max() > 100, f"{fid}/{p.get('label')}: the image has content (SD {a.std():.0f})")
        if "facts" in v and v["facts"]: check("<script" not in v["facts"].lower() and v["facts"].count("<span") == v["facts"].count("</span>"), f"{fid}/{v['label']}: the facts text is balanced HTML")
check(max(dims) < 160000 and tot < 1_000_000, f"size: the largest image is {max(dims) // 1000} KB and all images together {tot // 1000} KB")
# ---- no patient identifiers, dates, or file names in anything that is shipped
blob = json.dumps(real.REAL)
for pat in (r"MSB-\d", r"UPENN-GBM-\d", r"R01-\d", r"NaF-PROSTATE-\d", r"Pancreas-CT-CB", r"PSMA_[0-9a-f]{6}", r"COVID-19-AR-\d", r"1\.3\.6\.1\.4\.1\.", r"\b(19|20)\d\d-\d\d-\d\d\b", r"\.dcm"):
    check(re.search(pat, blob) is None, f"nothing shipped matches the identifier pattern {pat}")
# ---- the measured numbers
St = {k: v["stats"] for k, v in J.items()}
nz = St["ct"]["noise"]; sd, ma = nz["sd"], nz["mA"]
check(all(sd[i] > sd[i + 1] for i in range(len(sd) - 1)), f"noise falls with the tube current: {[round(x, 1) for x in sd]}")
check(all(abs(sd[i] / (sd[0] * math.sqrt(ma[0] / ma[i])) - 1) < 0.05 for i in range(len(sd))), "noise follows 1 / sqrt(mA) within 5% of the 50 mA value")
kn = St["ct"]["kernel"]; check(kn["kernels"] == ["SOFT", "STANDARD", "LUNG", "EDGE"] and all(kn["sd"][i] < kn["sd"][i + 1] for i in range(3)), f"noise rises from the soft to the edge kernel: {[round(x) for x in kn['sd']]}")
cb = St["ct"]["cbct"]; check(cb["sd_cbct"] > cb["sd_ct"] and cb["liver_ct"] > cb["liver_cbct"], f"the CBCT is noisier ({cb['sd_cbct']:.0f} against {cb['sd_ct']:.0f} HU) and the contrast-enhanced liver reads higher on the planning CT")
su = St["pet"]["suv"]
fac = su["weight_kg"] * 1000 / (su["dose_MBq"] * 1e6 * 2 ** (-su["uptake_min"] / su["half_life_min"]))
check(abs(fac / su["factor"] - 1) < 1e-6, f"the SUV factor {su['factor']:.3e} follows from the header values ({fac:.3e})")
check(abs(su["tumour_kbq_ml"] * 1000 * su["factor"] / su["tumour_suvmax"] - 1) < 1e-6 and abs(su["act_scan_MBq"] / (su["dose_MBq"] * 2 ** (-su["uptake_min"] / su["half_life_min"])) - 1) < 1e-9, "the tumour SUV, its concentration, and the activity at the scan agree")
check(10 < su["tumour_suvmax"] < 80 and 0.1 < su["lung_suv"] < 1.2 and 100 < su["half_life_min"] / 1.0 < 120 and 40 < su["uptake_min"] < 120, f"plausible values: tumour SUV {su['tumour_suvmax']:.1f}, lung SUV {su['lung_suv']:.2f}, half-life {su['half_life_min']:.1f} min, uptake {su['uptake_min']:.0f} min")
check(su["pet_mm"] > 4 and su["ct_mm"] < 1.2 and su["ct_matrix"] == 512, "the PET pixels are coarse and the CT matrix is 512")
pr = St["mr"]["params"]
check(pr["t1"]["ti"] == pr["t1gd"]["ti"] and pr["flair"]["ti"] > 2000 and pr["t2"]["tr"] < pr["flair"]["tr"] and all(p["field"] == 3.0 for p in pr.values()), "MR parameters from the headers: the T1 pair shares its timing, FLAIR has the longest TR and an inversion time")
bone = St["nm"]["bone"]; check(bone["matrix"] == [256, 1024] and bone["peak_counts"] < 5000 and bone["nuclide"].replace("^", "").lower().startswith("99m"), "the bone scan is a 256 x 1024 Tc-99m acquisition with low counts per pixel")
dx = St["dx"]["dx"]; check(dx["kvp"] == 90 and abs(dx["mas"] - 1.9) < 1e-9 and dx["grid"] == "None" and dx["stored"] == 12 and 0.1 < dx["pixel_mm"] < 0.2, f"the radiograph technique is read from its header: {dx['kvp']:g} kVp, {dx['mas']} mAs")
check(len(real.HDR) == 6 and all(h["stored"] <= h["allocated"] for h in real.HDR) and max(h["rows"] * h["cols"] * h["allocated"] for h in real.HDR) > 100 * min(h["rows"] * h["cols"] * h["allocated"] for h in real.HDR), "header table: six images, and sizes spanning more than two orders of magnitude")
print(f"realdata: {n} checks"); print("realdata: PASS" if not bad else f"realdata: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
