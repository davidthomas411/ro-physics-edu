"""The real-plan viewers in the page: slice scrolling, structure toggles, isodose areas, and DVH readings agree with independent calculations from the stored data."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or '.').resolve() != Path(__file__).resolve().parent]      # tests/numbers.py would shadow the standard module that numpy imports
import os, io, json, base64, re
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
C = json.load(open(ROOT / "src" / "case_hn1.json")); bad = []; n = 0; errors = []
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
dec = lambda s: np.array(Image.open(io.BytesIO(base64.b64decode(s.split(",")[1]))))
DOSE = dec(C["dose"]).astype(float) * C["level"]; w, h, cols, step = C["w"], C["h"], C["cols"], C["dvhStep"]
tile = lambda k: DOSE[(k // cols) * h:(k // cols + 1) * h, (k % cols) * w:(k % cols + 1) * w]
area = lambda k, L: float((tile(k) >= L).sum()) * C["dx"] ** 2 / 100
S = {s["name"]: s for s in C["structures"]}; ks = sorted(int(x) for x in S["PTV70"]["contours"]); kmid = round((ks[0] + ks[-1]) / 2)
here = lambda k: [s["name"] for s in C["structures"] if str(k) in s["contours"]]
def Vat(d, x):
    f = x / step; i = min(len(d) - 2, int(f)); return d[i] + (d[i + 1] - d[i]) * (f - i)
def Dat(d, v):
    if v >= d[0]: return 0.0
    for i in range(1, len(d)):
        if d[i] <= v: return ((i - 1) + (d[i - 1] - v) / (d[i - 1] - d[i])) * step
    return 80.0
def setv(pg, sel, v): pg.evaluate("([s,v])=>{const e=document.querySelector(s); e.value=v; e.dispatchEvent(new Event('input',{bubbles:true}));}", [sel, str(v)])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None); pg = b.new_page(viewport={'width': 440, 'height': 900}, color_scheme='light')
    pg.on("pageerror", lambda e: errors.append(str(e))); pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    def open_fig(tid, fid):
        pg.goto(U + "#ref"); pg.goto(U + f"#t/{tid}"); sel = f'figure.av[data-av="{fid}"]'; pg.wait_for_selector(sel + " output.avo", timeout=8000)
        pg.wait_for_function("(s)=>document.querySelector(s+' output.avo').textContent.length>5", arg=sel, timeout=8000); return sel
    # ---- contours on a real CT slice
    sel = open_fig("icru-volumes", "case-volumes"); out = lambda: pg.locator(sel + " output.avo").inner_text()
    check(pg.locator(sel + " input[type=range]").get_attribute("max") == str(C["nz"] - 1) and int(pg.locator(sel + " input[type=range]").input_value()) == kmid, f"the slice slider spans the {C['nz']} slices and starts at the middle of PTV70 (slice {kmid})")
    check(out().startswith(f"slice {kmid} (0 mm from the middle of PTV70).") and out().endswith(", ".join(here(kmid))), f"the readout lists the structures contoured on slice {kmid}: {here(kmid)} ({out()})")
    check(pg.locator(sel + " image").first.get_attribute("href").startswith("data:image/png;base64,"), "the CT slice is drawn from the embedded image")
    npaths = lambda: pg.locator(sel + " g path").count(); expect = lambda k: sum(len(s["contours"][str(k)]) for s in C["structures"] if str(k) in s["contours"])
    check(npaths() == expect(kmid), f"one outline per contour polygon on the slice ({npaths()} against {expect(kmid)})")
    pg.locator(sel + " button", has_text="PTV70").click(); check(pg.locator(sel + " button", has_text="PTV70").get_attribute("aria-pressed") == "false" and npaths() == expect(kmid) - len(S["PTV70"]["contours"][str(kmid)]), "switching a structure off removes its outlines")
    pg.locator(sel + " button", has_text="PTV70").click(); setv(pg, sel + " input[type=range]", 3); pg.wait_for_timeout(200)
    check(out().startswith("slice 3 (") and out().endswith(", ".join(here(3)) if here(3) else "none") and npaths() == expect(3), f"scrolling to slice 3 updates the structures: {here(3)}")
    # ---- isodose lines and areas
    sel = open_fig("imrt-delivery", "case-dose"); out = lambda: pg.locator(sel + " output.avo").inner_text()
    txt = out(); want = [(66.5, "66.5 Gy"), (56, "56 Gy"), (35, "35 Gy")]
    check(all(re.search(rf"{nm}: ([\d.]+) cm²", txt) and abs(float(re.search(rf"{nm}: ([\d.]+) cm²", txt).group(1)) - area(kmid, L)) < 0.06 for L, nm in want), f"the isodose areas on slice {kmid} agree with the dose grid: {[(nm, round(area(kmid, L), 1)) for L, nm in want]} ({txt[:110]})")
    check(area(kmid, 35) > area(kmid, 56) > area(kmid, 66.5) > 0, "a lower isodose level encloses a larger area")
    pg.locator(sel + " button", has_text="70 Gy").first.click(); txt = out(); a70 = re.search(r"70 Gy: ([\d.]+) cm²", txt)
    check(a70 is not None and abs(float(a70.group(1)) - area(kmid, 70)) < 0.06, f"adding the 70 Gy line adds its area ({a70.group(1) if a70 else None} against {area(kmid, 70):.1f})")
    for nm in ("70 Gy", "66.5 Gy", "56 Gy", "35 Gy"): pg.locator(sel + " button", has_text=nm).first.click()
    check("no isodose line selected" in out(), "with every line switched off the readout says so")
    pg.locator(sel + " button", has_text="Colour wash").click(); pg.wait_for_timeout(200)
    check(pg.locator(sel + " image").nth(1).get_attribute("opacity") == "1" and pg.locator(sel + " image").nth(1).get_attribute("href").startswith("data:image/png"), "the colour wash is drawn when switched on")
    # ---- the DVH
    sel = open_fig("dvh-metrics", "case-dvh"); out = lambda: pg.locator(sel + " output.avo").inner_text(); d = S["PTV70"]["dvh"]
    txt = out(); mV = re.search(r"V66\.5 Gy = ([\d.]+)%", txt); mD = re.search(r"D95% = ([\d.]+) Gy", txt); m50 = re.search(r"D50% = ([\d.]+) Gy", txt); m2 = re.search(r"D2% = ([\d.]+) Gy", txt)
    check(txt.startswith("PTV70 (213 cm³)") and mV and abs(float(mV.group(1)) - Vat(d, 66.5)) < 0.06 and mD and abs(float(mD.group(1)) - Dat(d, 95)) < 0.06 and m50 and abs(float(m50.group(1)) - Dat(d, 50)) < 0.06 and m2 and abs(float(m2.group(1)) - Dat(d, 2)) < 0.06, f"PTV70: V66.5 Gy = {Vat(d, 66.5):.1f}%, D95% = {Dat(d, 95):.1f} Gy, D50% = {Dat(d, 50):.1f} Gy, D2% = {Dat(d, 2):.1f} Gy ({txt[:150]})")
    check(abs(Dat(d, 95) - S["PTV70"]["stats"]["D95"]) < 0.35 and f"mean dose {S['PTV70']['stats']['mean']:.1f} Gy" in txt and f"maximum {S['PTV70']['stats']['max']:.1f} Gy" in txt, "the mean and maximum doses read from the plan")
    check(pg.locator(sel + " input[type=range]").count() == 0, "the DVH viewer has no slider that only moves a point along a curve")
    pg.locator(sel + " button", has_text="LeftParotid").click(); pg.wait_for_timeout(150); txt = out(); dl = S["LeftParotid"]["dvh"]
    mV = re.search(r"V66\.5 Gy = ([\d.]+)%", txt); mD = re.search(r"D50% = ([\d.]+) Gy", txt)
    check(txt.startswith("LeftParotid") and mV and abs(float(mV.group(1)) - Vat(dl, 66.5)) < 0.06 and mD and abs(float(mD.group(1)) - Dat(dl, 50)) < 0.06, f"LeftParotid: V66.5 Gy = {Vat(dl, 66.5):.1f}% and D50% = {Dat(dl, 50):.1f} Gy ({txt[:130]})")
    check(S["LeftParotid"]["stats"]["mean"] < 20 and S["RightParotid"]["stats"]["mean"] < 25, "the parotid glands are spared in this plan (mean doses below 20 and 25 Gy)")
    b.close()
check(not errors, f"no console or page errors {errors[:2]}")
print(f"case: {n} checks"); print("case: PASS" if not bad else f"case: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
