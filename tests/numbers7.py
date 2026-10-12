"""Brachytherapy chapters: every worked number and typed answer re-derived by a different route (numerical integration where the text uses a closed form)."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import calc
plain = lambda s: re.sub(r"<[^>]+>", "", s).replace("&lt;", "<").strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def simpson(f, a, b, k=4000):
    h = (b - a) / k; return h / 3 * (f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, k)))
# ---- line-source geometry function: the average of the inverse-square law over the source length
def gl_numeric(r, theta, L):
    th = math.radians(theta); rho, z = r * math.sin(th), r * math.cos(th)
    return simpson(lambda l: 1 / (rho * rho + (z - l) ** 2), -L / 2, L / 2) / L
for r, th, L in ((1, 90, 0.3), (1, 0, 0.3), (2, 90, 0.423), (1, 90, 0.423), (0.7, 35, 0.3), (3, 60, 1.0), (1.5, 0, 0.5)): close(calc.tg43_gl(r, th, L), gl_numeric(r, th, L), 1e-7, f"G_L({r},{th},{L})")
# ---- TG-43 worked doses, with published seed data
D = lambda sk, lam, r, th, L, g, f: sk * lam * gl_numeric(r, th, L) / gl_numeric(1, 90, L) * g * f
d1, d2, d3, d4 = D(1, 0.965, 1, 90, 0.3, 1, 1), D(1, 0.965, 1, 0, 0.3, 1, 0.370), D(1, 0.686, 2, 90, 0.423, 0.555, 1), D(1, 0.965, 2, 90, 0.3, 0.814, 1)
tg = T["tg43"]; ex = {b[1]: b[4] for b in tg["guide"] if b[0] == "ex"}
for key, v in (("Transverse axis at the reference point", d1), ("On the long axis", d2), ("A low-energy seed at 2 cm", d3)):
    got = float(re.search(r"(\d\.\d+) cGy/h", plain(ex[key])).group(1)); close(got, v, 6e-3, f"TG-43 example '{key}'")
print(f"TG-43 (numerical integration): reference {d1:.4f}, long axis {d2:.4f}, Pd-103 at 2 cm {d3:.4f}, I-125 at 2 cm {d4:.4f} cGy/h per U")
close(d2 / d1, 0.370 * calc.tg43_gl(1, 0, 0.3) / calc.tg43_gl(1, 90, 0.3), 1e-9, "on-axis ratio")
r1 = next(i / 1000 for i in range(300, 5000) if gl_numeric(i / 1000, 0, 0.3) * (i / 1000) ** 2 < 1.01); close(r1, 1.5, 0.03, "within 1% of 1/r^2 beyond ~5L (1.5 cm for 3 mm)")
# ---- permanent implants: integrate the decaying dose rate
lam = math.log(2) / (60 * 24)                                                    # per hour
tot = simpson(lambda t: 5.0 * math.exp(-lam * t), 0, 60 * 24 * 40, 20000) / 100   # Gy
d7 = simpson(lambda t: 5.0 * math.exp(-lam * t), 0, 7 * 24, 2000) / 100
close(tot, 103.8, 2e-3, "total dose 5 cGy/h, T1/2 60 d (integral)"); close(tot, calc.implant_total_dose(5.0, 1440) / 100, 1e-5, "closed form equals the integral")
close(d7, calc.implant_dose_to(5.0, 1440, 168) / 100, 1e-6, "dose in 7 d (integral)"); close(d7, 8.07, 3e-3, "dose in 7 d = 8.1 Gy")
lam_i = math.log(2) / (59.4 * 24); rate = 14500 / (simpson(lambda t: math.exp(-lam_i * t), 0, 59.4 * 24 * 40, 20000)); close(rate, 7.05, 3e-3, "I-125 initial dose rate for 145 Gy")
half = next(t / 10 for t in range(1, 30000) if 1 - 0.5 ** (t / 10 / 59.4) >= 0.5); nine = next(t / 10 for t in range(1, 30000) if 1 - 0.5 ** (t / 10 / 59.4) >= 0.9); close(half, 59.4, 3e-3, "half the dose by one half-life"); close(nine, 197.3, 3e-3, "90% by 3.32 half-lives")
# ---- exposure and air kerma strength
we = 33.97 * 2.58e-4 * 100; close(we, 0.876, 1e-3, "W/e x 2.58e-4 C/kg = 0.876 cGy/R"); close(1e-6 * 1e4 * 1e2, 1.0, 1e-12, "1 uGy m2 = 1 cGy cm2")   # 1 uGy m^2 = 1e-6 Gy x 1e4 cm^2 = 1e-2 Gy cm^2 = 1 cGy cm^2
close(4.69 * 10000 / 10 ** 2, 469, 1e-9, "exposure rate 10 Ci at 10 cm"); close(0.876 * 4.69 * 10000, 41084.4, 1e-6, "S_K of 10 Ci Ir-192"); close(0.876 * 1.45 * 0.5, 0.6351, 1e-6, "S_K of 0.5 mCi I-125"); close(0.60 * 0.5 ** (30 / 59.4), 0.4227, 2e-3, "S_K after 30 d")
close(4.69 / 1.45, 3.234, 1e-3, "Ir-192 to I-125 gamma ratio"); close(100 * (2 / 5) ** 2, 16.0, 1e-12, "inverse square 2 cm to 5 cm"); close(400 / 16, 25.0, 1e-12, "400 R/h at 1 cm to 4 cm")
# ---- HDR source decay
close(10 * math.exp(-math.log(2) * 90 / 73.8), 4.294, 1e-3, "10 Ci Ir-192 after 90 d"); close(73.8 * math.log(10 / 4) / math.log(2), 97.56, 1e-3, "time to 4 Ci"); close(73.8 * math.log(10 / 3) / math.log(2), 128.19, 1e-3, "time to 3 Ci"); close(0.5 ** (91.25 / 73.8), 0.4244, 2e-3, "activity left after three months")
# ---- the numbers printed in the text and the typed answers agree with these
fig = lambda t, phrase: next(p for p in t["problems"] if p.get("kind") == "fig" and phrase in plain(p["q"]))
inside = lambda p, x, y=None: any((a is None or x >= a) and (b is None or x <= b) and (y is None or ((c is None or y >= c) and (d is None or y <= d))) for a, b, c, d in p["targets"])
def at(pts, x0):
    for (a, b), (c, d) in zip(pts, pts[1:]):
        if a <= x0 <= c: return b + (d - b) * (x0 - a) / (c - a)
p = fig(tg, "75% of the total dose"); s = p["spec"]["series"][0]["pts"]; delivered = lambda t_: 100 * (1 - 0.5 ** (t_ / 59.4))
close(delivered(118.8), 75.0, 1e-9, "75% of the dose is delivered after two half-lives"); close(at(s, 118.8), 25.0, 0.01, "the plotted dose rate is 25% at 118.8 d"); close(1 if inside(p, 118.8) and not any(inside(p, x) for x in (59.4, 89.1, 197.3, 30)) else 0, 1, 0, "figure: 75% of the dose at 119 d")
for b in bad: print("FAIL", b)
print(f"numbers7: {n} brachytherapy numbers re-derived"); print("numbers7: PASS" if not bad else f"numbers7: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
