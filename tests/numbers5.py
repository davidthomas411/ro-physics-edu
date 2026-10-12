"""Photon interaction and kerma questions: the NIST table values are checked a second way (retyped values and physical sanity), and every answer is recomputed from the table as printed in the question."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import nistdata as nd
BY = {t["id"]: t for t in TOPICS}; plain = lambda s: re.sub(r"<[^>]+>", "", s)
fails = []; n = 0
def check(name, got, want, tol=1e-6):
    global n; n += 1
    if abs(got - want) > tol * max(abs(want), 1e-12): fails.append(f"{name}: got {got!r}, independent {want!r}")
# ---- the NIST values: retyped from the NIST pages, entered separately from the module
GOLD = {"water": {0.05: (0.2269, 0.04223), 0.1: (0.1707, 0.02546), 0.5: (0.09687, 0.03299), 1.0: (0.07072, 0.03103), 1.25: (0.06323, 0.02965), 1.5: (0.05754, 0.02833), 2.0: (0.04942, 0.02608), 3.0: (0.03969, 0.02281), 6.0: (0.02770, 0.01806)},
        "bone": {0.05: (0.4242, 0.2336), 0.1: (0.1855, 0.04585), 0.5: (0.09022, 0.03073), 1.0: (0.06566, 0.02875), 6.0: (0.02734, 0.01788)},
        "lead": {0.5: (0.1614, 0.09128), 1.0: (0.07102, 0.03654), 1.25: (0.05876, 0.02988), 1.5: (0.05222, 0.02640), 2.0: (0.04606, 0.02360)}}
for m, rows in GOLD.items():
    for e, (a, b) in rows.items():
        check(f"{m} mu/rho at {e} MeV", nd.MAT[m][1][e][0], a, 1e-12); check(f"{m} mu_en/rho at {e} MeV", nd.MAT[m][1][e][1], b, 1e-12)
for m, (label, tab) in nd.MAT.items():
    es = sorted(tab)
    for e in es:
        n += 1
        if tab[e][1] > tab[e][0]: fails.append(f"{m} at {e}: mu_en/rho exceeds mu/rho")
    seq = [e for e in es if e <= 4.0 and not (m == "lead" and e < 0.1)] if m == "lead" else es
    n += 1
    if any(tab[a][0] <= tab[b][0] for a, b in zip(seq, seq[1:])): fails.append(f"{m}: mu/rho does not fall with energy over the Compton and photoelectric range")
n += 1
if not all(nd.LEAD[a][0] < nd.LEAD[b][0] for a, b in zip([4.0, 5.0, 6.0, 8.0, 10.0, 15.0], [5.0, 6.0, 8.0, 10.0, 15.0, 20.0])): fails.append("lead mu/rho should rise again above 4 MeV (pair production)")
check("water mu_en/mu at 1 MeV (energy transferred locally)", nd.WATER[1.0][1] / nd.WATER[1.0][0], 0.4388, 1e-3)
check("the kerma example's 0.0297 is NIST's 0.02965 for water at 1.25 MeV", 0.0297, nd.WATER[1.25][1], 2e-3)
# ---- parse the tables as a student sees them
def tables_in(html):
    out = []
    for m in re.finditer(r'<div class="dt"><div class="dtc">(.*?)</div><div class="tblwrap"><table><thead><tr>(.*?)</tr></thead><tbody>(.*?)</tbody>', html, re.S):
        head = [plain(x) for x in re.findall(r"<th>(.*?)</th>", m.group(2))]; rows = {}
        for lab, cells in re.findall(r'<tr><th scope="row">(.*?)</th>(.*?)</tr>', m.group(3), re.S): key = plain(lab); key = float(key) if re.fullmatch(r"[\d.]+", key) else key; rows[key] = [float(c) for c in re.findall(r"<td>(.*?)</td>", cells)]
        out.append(dict(cap=plain(m.group(1)), head=head, rows=rows))
    return out
def find(tid, phrase):
    hits = [p for p in BY[tid]["problems"] if plain(phrase) in plain(p["q"])]; assert len(hits) == 1, (tid, phrase, len(hits)); return hits[0]
def right(p): i = "ABCDEFG".index(re.search(r"<b>([A-G])\.", p["a"][0]).group(1)); return p["vals"][i]
EJ = 1.602176634e-19 * 1e6
H, C, ME = 6.62607015e-34, 299792458.0, 9.1093837015e-31
# ---- photon interactions
p = find("photon-interactions", "required transmission = 5%"); check("lead thickness for 5%", right(p), 0.80 * math.log(1 / 0.05) / math.log(2), 1e-9)
p = find("photon-interactions", "tenth-value layer"); check("TVL from HVL", right(p), 2.2 * math.log(10) / math.log(2), 1e-9)
p = find("photon-interactions", "scattering angle = 45°")                      # by the wavelength shift, a route that shares nothing with the energy formula
lam = H * C / (1.0 * EJ); lam2 = lam + H / (ME * C) * (1 - math.cos(math.radians(45))); check("Compton electron energy at 45 degrees (MeV)", right(p), 1.0 - H * C / lam2 / EJ, 2e-4)
p = find("photon-interactions", "half-value layer"); t = tables_in(p["q"])[0]; mr = t["rows"][1.25][0]; check("HVL of water at 1.25 MeV", right(p), math.log(2) / (mr * 1.00), 1e-9)
p = find("photon-interactions", "passes through lead"); t = tables_in(p["q"])[0]; mr = t["rows"][1.25][0]; check("lead transmission (%)", right(p), 100 * math.exp(-mr * 11.35 * 3.0), 1e-9)
# ---- kerma
p = find("kerma-dose", "photon energy = 1.25 MeV"); check("energy fluence", right(p), 3.0e12 * 1.25 * EJ, 1e-9)
p = find("kerma-dose", "energy fluence Ψ = 0.80 J/m²"); t = tables_in(p["q"])[0]; men = t["rows"][1.0][1]; check("collision kerma, 1 MeV (mGy)", right(p), 0.80 * men * 0.1 * 1000, 1e-9)
p = find("kerma-dose", "100 keV with the same energy fluence"); t = tables_in(p["q"])[0]; r = t["rows"][0.1]; check("bone to water energy absorption per gram at 100 keV", right(p), r[1] / r[3], 1e-9)
check("at 6 MeV the two absorb about equally per gram", t["rows"][6.0][1] / t["rows"][6.0][3], 0.99, 1e-2)
p = find("kerma-dose", "β = 1.03"); t = tables_in(p["q"])[0]; men = t["rows"][2.0][1]; check("absorbed dose beyond dmax (mGy)", right(p), 1.03 * 0.50 * men * 0.1 * 1000, 1e-9)
p = find("kerma-dose", "X = 25 R"); check("dose to air from 25 R (cGy), by C/kg and W/e", right(p), 25 * 2.58e-4 * 33.97 * 100, 2e-3)
p = find("kerma-dose", "photon dose = 0.50 Gy"); check("equivalent dose", right(p), 0.50 * 1 + 0.10 * 20, 1e-12)
# every table printed in a question is a faithful copy of the data
for t in TOPICS:
    for q in t["problems"]:
        for tb in tables_in(q["q"]):
            if "NIST" not in tb["cap"]: continue
            names = ["water" if "water" in tb["cap"].lower() else "bone" if "bone" in tb["cap"].lower() else "lead" if "lead" in tb["cap"].lower() else None]
            for e, row in tb["rows"].items():
                if len(row) == 2:
                    m = names[0]
                    for got, want in zip(row, nd.MAT[m][1][e]): 
                        n += 1
                        if abs(got - float(f"{want:.4g}")) > 1e-12: fails.append(f"{t['id']}: {m} {e} MeV prints {got}, data {want}")
                elif len(row) == 4:
                    for got, want in zip(row, list(nd.BONE[e]) + list(nd.WATER[e])):
                        n += 1
                        if abs(got - float(f"{want:.4g}")) > 1e-12: fails.append(f"{t['id']}: two-material table {e} MeV prints {got}, data {want}")
print(f"numbers5: {n} checks")
for f in fails: print("FAIL", f)
print("numbers5: PASS" if not fails else f"numbers5: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
