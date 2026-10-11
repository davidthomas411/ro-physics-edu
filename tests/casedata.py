"""The real clinical case: the stored CT, dose, contours, and DVHs are consistent with each other, and (when the OpenKBP files are present) with the original data."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]      # tests/numbers.py would shadow the standard module that numpy imports
import os, io, json, base64, math
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
C = json.load(open(ROOT / "src" / "case_hn1.json")); bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
dec = lambda s: np.array(Image.open(io.BytesIO(base64.b64decode(s.split(",")[1]))))
ct, do = dec(C["ct"]), dec(C["dose"]); w, h, cols, nz = C["w"], C["h"], C["cols"], C["nz"]; rows = -(-nz // cols)
check(ct.shape == (rows * h, cols * w) and do.shape == ct.shape, f"the sprites are {rows * h} x {cols * w}: one {w} x {h} tile per slice ({ct.shape}, {do.shape})")
check(C["dx"] > 3 and C["dz"] >= 2.5 and C["rx"] == 70.0, "voxel size and prescription are stored")
check(int(do.max()) * C["level"] <= 80.01 and abs(int(do.max()) * C["level"] - C["doseMax"]) < 0.5, f"the dose sprite maximum is {int(do.max()) * C['level']:.1f} Gy, matching the stored maximum {C['doseMax']}")
names = [s["name"] for s in C["structures"]]; check(names[:3] == ["PTV70", "PTV63", "PTV56"] and "SpinalCord" in names and "LeftParotid" in names, f"structures: {names}")
step = C["dvhStep"]
def Dat(d, v):
    for i in range(1, len(d)):
        if d[i] <= v: return ((i - 1) + (d[i - 1] - v) / (d[i - 1] - d[i])) * step
    return 80.0
def sarea(poly): return sum(poly[i] * poly[(i + 3) % len(poly)] - poly[(i + 2) % len(poly)] * poly[(i + 1) % len(poly)] for i in range(0, len(poly), 2)) / 2      # signed: a hole is traced the other way round and subtracts
def slice_area(polys): return abs(sum(sarea(p) for p in polys))
for s in C["structures"]:
    d, st = s["dvh"], s["stats"]
    check(abs(d[0] - 100) < 0.01 and d[-1] < 0.5 and all(d[i] >= d[i + 1] for i in range(len(d) - 1)), f"{s['name']}: the DVH starts at 100%, falls monotonically, and ends near 0")
    check(abs(Dat(d, 95) - st["D95"]) < 0.35, f"{s['name']}: D95% from the DVH ({Dat(d, 95):.2f}) agrees with the stored value ({st['D95']})")
    check(abs(Dat(d, 50) - st["D50"]) < 0.35, f"{s['name']}: D50% from the DVH ({Dat(d, 50):.2f}) agrees with the stored value ({st['D50']})")
    check(st["min"] <= st["D98"] <= st["D95"] <= st["D50"] <= st["D2"] <= st["max"], f"{s['name']}: min <= D98 <= D95 <= D50 <= D2 <= max")
p70 = next(s for s in C["structures"] if s["name"] == "PTV70")
vol70 = sum(slice_area(polys) for polys in p70["contours"].values()) * C["dx"] ** 2 * C["dz"] / 1000; check(0.97 * p70["stats"]["volume"] <= vol70 <= 1.03 * p70["stats"]["volume"], f"PTV70 lies wholly inside the displayed slices: its contour polygons enclose {vol70:.0f} cm3 against a stored volume of {p70['stats']['volume']} cm3")
check(0.97 * 70 <= p70["stats"]["D95"] <= 1.02 * 70 and p70["stats"]["max"] < 80, "PTV70 is covered: D95 within 3% of the prescription")
cord = next(s for s in C["structures"] if s["name"] == "SpinalCord"); check(cord["stats"]["max"] < 45, f"the cord maximum is {cord['stats']['max']} Gy, below 45 Gy")
# the original files, when present
O = Path("/tmp/okbp/provided-data/train-pats/pt_14")
if O.exists():
    import pandas as pd
    def arr(f, mask=False):
        d = pd.read_csv(O / f"{f}.csv", index_col=0); a = np.zeros(128 ** 3, np.float32); a[d.index.values] = 1 if mask else d.iloc[:, 0].values; return a.reshape(128, 128, 128)
    dose = arr("dose")
    for s in C["structures"]:
        m = arr(s["name"], True) > 0; d = dose[m]; check(abs(float(np.percentile(d, 5)) - s["stats"]["D95"]) < 0.01 and abs(float(d.mean()) - s["stats"]["mean"]) < 0.01, f"{s['name']}: the stored D95 and mean agree with the original data")
        check(all(abs(100.0 * (d >= e).sum() / d.size - s["dvh"][i]) < 0.011 for i, e in enumerate(np.arange(0, 80.5, 0.5))), f"{s['name']}: the stored DVH agrees with the original dose")
        ok = True
        for k in range(nz):
            vox = int(m[:, :, C["z0"] + k].sum()); polys = s["contours"].get(str(k), []); pa = slice_area(polys)
            if abs(pa - vox) > 0.04 * vox + 0.5 * len(polys) + 1.0: ok = False          # a lone voxel traced at the half level loses half its area
        check(ok, f"{s['name']}: on every displayed slice the contour area equals the number of mask voxels, within the loss at isolated voxels")
    print("compared with the original OpenKBP files")
else: print("(original OpenKBP files not present: comparison skipped)")
print(f"casedata: {n} checks"); print("casedata: PASS" if not bad else f"casedata: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
