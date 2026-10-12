"""Fluoroscopy and image intensifiers: every worked number and keyed answer re-derived by another route
(gains from phosphor areas and logarithms, magnified dose rates by holding the output brightness in a bisection, and the kerma-area
product by integrating a point source over the beam at several distances and by summing a field cell by cell;
the rate limits from roentgens)."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]     # before the imports below: tests/numbers.py would shadow the standard module
import re, math
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import fluoroscopy as G
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
tp = {t["id"]: t for t in TOPICS}["fluoroscopy"]
bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in tp["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                   # the number behind the keyed option, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def example(title):
    hits = [b for b in tp["guide"] if b[0] == "ex" and b[1] == title]; assert len(hits) == 1, title; return hits[0]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def options(p, wrong):                                                          # the option values are the key and the written distractors, none swapped by the option engine
    return sorted(round(v, 9) for v in p["vals"]) == sorted(round(v, 9) for v in [value(p), *wrong])
text = " ".join(plain(b[1]) for b in tp["guide"] if b[0] == "p")
table_text = " ".join(plain(c) for b in tp["guide"] if b[0] == "table" for r in b[2] for c in r)
cards = {plain(c["q"]): c for c in tp["cards"]}

# ---- brightness gain: the minification gain as a ratio of phosphor areas, the product through logarithms
area = lambda d: math.pi * d * d / 4
gm30 = area(30.0) / area(2.5)
close(G.gm1, gm30, 1e-12, "example: minification gain from the areas of the phosphors"); close(G.gb1, math.exp(math.log(gm30) + math.log(50)), 1e-12, "example: brightness gain through logarithms")
ex = example("Brightness gain")
check(plain(ex[4]) == f"Gmin = {gm30:.0f} and GB = {gm30 * 50:,.0f}.", "the example prints 144 and 7,200")
check(f"(30 / 2.5)² = 12² = {gm30:.0f}" in plain(ex[3][0]), "the example's first step prints (30 / 2.5)² = 12² = 144")
check(f"= {gm30:.0f} × 50 = {gm30 * 50:,.0f}" in plain(cards["Brightness gain of an image intensifier"]["w"][0]), "the card's working step prints 144 × 50 = 7,200")
p = prob("input phosphor diameter = 23 cm")
gm23 = area(23.0) / area(2.5)
close(value(p), math.exp(2 * math.log(23.0 / 2.5) + math.log(60)), 1e-12, "question: brightness gain with a 23 cm input and a flux gain of 60")
check(options(p, [23.0 / 2.5 * 60, gm23, gm23 + 60]), "decoys: no square, no flux gain, and the gains added")
check(f"{value(p):,.0f}" == "5,078" and keyed(p) == "5,078", "the keyed option reads 5,078")

# ---- magnification: hold the output brightness (input rate × minification gain) and solve for the input rate
def held(rate, fov_a, fov_b, d_out=2.5):
    target = rate * (fov_a / d_out) ** 2
    return bisect(lambda r: r * (fov_b / d_out) ** 2 - target, 0.0, 1000.0)
close(G.r2b, held(12.0, 30.0, 20.0), 1e-9, "example: 30 cm to 20 cm field"); check(plain(example("Dose rate in magnification mode")[4]).startswith(f"{held(12.0, 30.0, 20.0):.0f} mGy/min, 2.25 times"), "the example prints 27 mGy/min, 2.25 times")
close(G.g2a / G.g2b, area(30.0) / area(20.0), 1e-12, "example: the ratio of the minification gains equals the ratio of the field areas")
p = prob("switched from its 40 cm field to its 25 cm field")
close(value(p), held(10.0, 40.0, 25.0), 1e-9, "question: 40 cm to 25 cm field"); close(value(p), 25.6, 1e-9, "25.6 mGy/min")
check(options(p, [10.0 * 40 / 25, 10.0 * (25 / 40) ** 2, 10.0]), "decoys: the linear ratio, the inverted square, and no change")
close(G.mag_card, held(1.0, 30.0, 15.0), 1e-9, "card: 30 cm to 15 cm is a factor of 4"); check("(30 / 15)² = 4" in plain(cards["Magnification mode of an intensifier"]["w"][0]), "the card prints the factor 4")

# ---- kerma-area product: a point source integrated over a square pyramid of beam, at several distances
def kap_int(c, half_u, d, steps=240):
    """∫ K dA over the square field of half-width half_u × d at distance d, with K = c / r² from a point source."""
    h = 2 * half_u * d / steps; s = 0.0
    for i in range(steps):
        x = -half_u * d + (i + 0.5) * h
        for j in range(steps):
            y = -half_u * d + (j + 0.5) * h
            s += c / (d * d + x * x + y * y)
    return s * h * h
c3 = 0.40 * 60.0 ** 2; u3 = 5.0 / 60.0                                          # source constant from 0.40 Gy on the axis at 60 cm; half-field 5 cm at 60 cm
i60, i30 = kap_int(c3, u3, 60.0), kap_int(c3, u3, 30.0)
close(i60, i30, 1e-9, "the integrated kerma-area product is the same at 60 cm and 30 cm")
close(G.p3, 0.40 * 100.0, 1e-12, "example: KAP at the skin on the axis"); close(G.p3, i60, 0.01, "and within 1% of the integral over the field, which includes the off-axis fall-off")
close(G.k3c, c3 / 30.0 ** 2, 1e-12, "example: air kerma at the chamber from the source constant"); close(G.a3c, (2 * 5.0 * 30 / 60) ** 2, 1e-12, "example: area at the chamber by similar triangles")
check(plain(example("Kerma-area product at two distances")[4]) == "40 Gy cm² in both planes.", "the example prints 40 Gy cm² in both planes")
p = prob("reading = 24 Gy cm²")
c14 = 1.0; u14 = 0.1
close(value(p), 24.0 * kap_int(c14, u14, 65.0) / kap_int(c14, u14, 25.0), 1e-9, "question: KAP carried from the chamber to the skin by the integral")
check(options(p, [24.0 * (25 / 65) ** 2, 24.0 * (65 / 25) ** 2, 24.0 * 25 / 65]), "decoys: inverse square alone, area alone, and a linear distance factor")
p = prob("A C-arm exposure ends")
# a 10 cm x 12 cm field summed cell by cell on a 1 mm grid
cells = sum(0.30 * 0.01 for _ in range(100) for _ in range(120))
close(value(p), cells, 1e-9, "typed question: KAP as the kerma summed over 1 mm² cells of a 10 x 12 cm field"); close(value(p), 36.0, 1e-12, "36 Gy cm²")
check(abs(0.30 * 22 / value(p) - 1) > p["tol"], "adding the sides lies outside the tolerance")

# ---- magnification and KAP rate: the rate rises by the square, the area falls by it
p = prob("skin dose rate inside the field")
rate_ratio = held(1.0, 30.0, 15.0); area_ratio = (2 * 7.5) ** 2 / (2 * 15.0) ** 2
close(G.v_rate, rate_ratio, 1e-9, "skin dose rate rises fourfold"); close(G.v_area, area_ratio, 1e-12, "area falls to a quarter"); close(G.v_kap, rate_ratio * area_ratio, 1e-9, "KAP rate unchanged")
check(keyed(p) == "The skin dose rate rises about fourfold, and the KAP rate stays about the same", "keyed: fourfold skin dose rate, the same KAP rate")

# ---- US rate limits: the roentgen values converted with W/e
mgy_per_r = 0.876 * 10                                                          # 0.876 cGy per R of air kerma
check(round(10 * mgy_per_r) == G.LIM_N, "10 R/min is 88 mGy/min of air kerma"); check(G.LIM_H == 2 * G.LIM_N and abs(20 * mgy_per_r / G.LIM_H - 1) < 0.005, "176 mGy/min is twice 88 and within 0.5% of 20 R/min")
p = prob("normal mode with automatic exposure-rate control")
check(keyed(p) == "88 mGy/min (about 10 R/min)", "keyed: 88 mGy/min"); check(f"{10 * mgy_per_r:.1f} mGy" in plain(p["a"][1]), "the explanation prints 87.6 mGy")
check(all(x in table_text for x in ("At most 88 mGy/min (about 10 R/min)", "At most 176 mGy/min (about 20 R/min)", "At least 38 cm on fixed units and 30 cm on mobile units", "at most 5 min of cumulative beam-on time")), "the table prints the limits, the distances, the reference point, and the timer")
check("88 mGy/min (about 10 R/min)" in plain(cards["US limits on fluoroscopic air-kerma rate"]["a"][0]), "the card prints the same limit")

# ---- quoted values print the same in the text, the cards, and the take-aways
check("about 1 to 5 mA" in text and "about 1 to 5 mA" in plain(tp["take"][0][0]), "tube current about 1 to 5 mA in the text and take-away")
check("about 25 to 35 kV" in text and "about 2.5 cm across" in text and "about 50 per light photon" in text, "accelerating voltage, output phosphor, and flux gain in the text")
check(f"about {G.TH_ERY} Gy for transient erythema and {G.TH_EPI} Gy for temporary epilation" in text, "skin thresholds in the text")

# ---- every numeric question has distinct options
for q in tp["problems"]:
    if q.get("vals"): check(len(set(round(v, 6) for v in q["vals"])) == len(q["vals"]) == 4, f"four distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_fluoroscopy: {n} numbers re-derived"); print("numbers_fluoroscopy: PASS" if not bad else f"numbers_fluoroscopy: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
