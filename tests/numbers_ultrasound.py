"""Ultrasound physics and imaging: every worked number and keyed answer re-derived by another route
(exact fractions for wavelengths and echo times, the pressure boundary conditions solved as a linear system for the reflection,
bisection for depths, PRFs, and velocities, attenuation as a product of thin slabs, Fermat's principle for refraction,
the exact moving-reflector Doppler formula, the on-axis field of a piston for the near field, a Bessel zero for the divergence,
and the echo time traced through each layer for the speed-of-sound errors)."""
import sys
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard module
import re, math
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import ultrasound as U
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-9, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in T["ultrasound"]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed_text(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def example(title):
    hits = [b for b in U.TOPIC["guide"] if b[0] == "ex" and b[1] == title]; assert len(hits) == 1, title; return hits[0]
def bisect(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2; fm = f(m)
        if fa * fm <= 0: b = m
        else: a, fa = m, fm
    return (a + b) / 2
def golden_min(f, a, b, it=200):
    g = (math.sqrt(5) - 1) / 2; c, d = b - g * (b - a), a + g * (b - a)
    for _ in range(it):
        if f(c) < f(d): b, d = d, c; c = b - g * (b - a)
        else: a, c = c, d; d = a + g * (b - a)
    return (a + b) / 2
text = " ".join(plain(b[1]) for b in U.TOPIC["guide"] if b[0] == "p")
C = 1540.0

# ---- reflection: pressure continuity and velocity continuity at the boundary, solved as a 2 x 2 linear system
def boundary(z1, z2):
    """Incident pressure 1. Unknowns p_r, p_t:  p_r - p_t = -1  and  -p_r/z1 - p_t/z2 = -1/z1.  Returns (R, T) as intensity fractions."""
    a11, a12, b1 = 1.0, -1.0, -1.0
    a21, a22, b2 = -1.0 / z1, -1.0 / z2, -1.0 / z1
    det = a11 * a22 - a12 * a21
    pr = (b1 * a22 - a12 * b2) / det; pt = (a11 * b2 - b1 * a21) / det
    return pr * pr, (pt * pt / z2) / (1.0 / z1)
for z1, z2 in ((1.63, 0.0004), (1.63, 7.8), (1.334, 1.6906), (1.34, 1.65)):
    R_, T_ = boundary(z1, z2)
    close(R_ + T_, 1.0, 1e-12, f"energy is conserved at {z1} / {z2} MRayl"); close(U.refl(z1, z2), R_, 1e-12, f"R at {z1} / {z2} MRayl from the boundary conditions")
R_air = boundary(U.Z_SOFT, U.Z_AIR)[0]
check(f"{100 * R_air:.1f}%" == "99.9%" and "99.9% at air" in text, "soft tissue against air reflects 99.9%, as printed")
grid = [(lo + (hi - lo) * i / 20) for lo, hi in ((1.6, 1.7),) for i in range(21)]
bone = [boundary(zs, 6.0 + 2.0 * j / 40)[0] for zs in grid for j in range(41)]
check(0.30 <= min(bone) and max(bone) <= 0.45 and U.bone_lo5 == 30 and U.bone_hi5 == 45, f"every soft tissue (1.6-1.7) against cortical bone (6-8 MRayl) reflects 30-45% ({100 * min(bone):.1f}-{100 * max(bone):.1f}%)")
soft = [boundary(1.3 + 0.1 * i / 10, zs)[0] for i in range(11) for zs in grid]
check(max(soft) <= 0.02 and U.SOFT_MAX == 2, f"fat (1.3-1.4) against other soft tissue (1.6-1.7 MRayl) reflects at most 2% ({100 * max(soft):.2f}%)")
check("about 2% or less between soft tissues" in text and "about 30 to 45% at bone" in text, "the text prints the soft-tissue and bone ranges")

# ---- wavelength and echo time per centimetre, in exact fractions
lam5 = Fr(1540) / Fr(5_000_000) * 1000                                       # mm
close(U.lam5, float(lam5), 1e-12, "wavelength at 5 MHz"); check("0.31 mm at 5 MHz" in text, "the text prints 0.31 mm")
t_cm = Fr(2, 100) / Fr(1540) * 10 ** 6                                       # µs for 1 cm of depth, there and back
close(U.us_cm, float(t_cm), 1e-12, "echo time per cm"); check(round(float(t_cm)) == 13 and "13 µs per centimetre" in text, "13 µs per cm, as printed")

# ---- worked example: fat-muscle interface
zf, zm = Fr(920) * Fr(1450) / 10 ** 6, Fr(1070) * Fr(1580) / 10 ** 6
check(f"{float(zf):.3f}" in plain(example("Echo from a fat–muscle interface")[2]) and f"{float(zm):.3f}" in plain(example("Echo from a fat–muscle interface")[2]), "the printed impedances are ρc of fat and muscle"); close(U.x1_zf, float(zf), 1e-12, "Z of fat"); close(U.x1_zm, float(zm), 1e-12, "Z of muscle")
R1 = boundary(float(zf), float(zm))[0]
close(U.x1_r, R1, 1e-12, "R fat-muscle"); db1 = -10 * math.log10(2) * math.log2(R1)                 # decibels through a base-2 logarithm
close(U.x1_db, db1, 1e-12, "echo level in dB")
check(plain(example("Echo from a fat–muscle interface")[4]).startswith(f"R = {100 * R1:.2f}%, an echo {db1:.1f} dB below") and f"{100 * (1 - R1):.1f}%" == "98.6%", "the printed answer: 1.39%, 18.6 dB, 98.6% on")

# ---- attenuation as a product of thin slabs, each passing 10^(-α f dx / 10) of the intensity
def slab_loss(f_mhz, path_cm, alpha=0.5, steps=4000):
    frac = 1.0; dx = path_cm / steps
    for _ in range(steps): frac *= 10 ** (-alpha * f_mhz * dx / 10)
    return -10 * math.log10(frac)

# ---- worked example: depth, loss, and PRF from an echo at 130 µs
d2 = bisect(lambda d: 2 * d / C - 130e-6, 0.0, 1.0) * 100                    # cm, the depth whose round trip takes 130 µs
close(U.x2_d, d2, 1e-9, "depth from echo time"); close(U.x2_loss, slab_loss(5.0, 2 * d2), 1e-6, "round-trip loss at 5 MHz")
prf2 = bisect(lambda f: 1 / f - 2 * (d2 / 100) / C, 100.0, 1e6)
close(U.x2_prf, prf2, 1e-7, "highest PRF for that depth"); close(U.x2_loss10, slab_loss(10.0, 2 * d2), 1e-6, "loss at 10 MHz")
check(plain(example("Depth and attenuation of an echo")[4]).startswith(f"{d2:.1f} cm and {slab_loss(5.0, 2 * d2):.0f} dB") and f"{slab_loss(10.0, 2 * d2):.0f} dB" == "100 dB", "printed: 10.0 cm and 50 dB; 100 dB at 10 MHz")
check(round(U.x2_loss / 10) == 5, "the intensity left is 10^-5, as printed")

# ---- worked example: wavelength, axial resolution, near field and divergence of a 10 mm disc at 5 MHz
lam = float(Fr(1540) / Fr(5_000_000) * 1000); a = 5.0                          # mm
dur = Fr(3, 5_000_000)                                                        # pulse duration n/f, s
close(U.x3_ax, float(Fr(1540) * dur * 1000 / 2), 1e-12, "axial resolution as half of c times the pulse duration")
z_last = bisect(lambda z: math.sqrt(z * z + a * a) - z - lam / 2, 1.0, 1000.0)   # last on-axis maximum of a piston: path difference λ/2
close(U.x3_nf, z_last, 2e-3, f"near field D²/(4λ) against the last on-axis maximum ({z_last:.2f} mm)")
def j1(x, terms=40): return sum((-1) ** m / (math.factorial(m) * math.factorial(m + 1)) * (x / 2) ** (2 * m + 1) for m in range(terms))
x0 = bisect(j1, 3.0, 4.5)                                                     # first zero of J1, 3.8317
close(U.x3_div, math.degrees(math.asin(x0 * lam / (math.pi * 2 * a))), 2e-3, f"divergence from the first zero of J1 ({x0:.4f})")
ans3 = plain(example("Wavelength and axial resolution")[4])
check(ans3.startswith(f"{lam:.2f} mm and {U.x3_ax:.2f} mm") and f"{U.x3_ax10:.2f} mm" == "0.23 mm" and "0.23 mm" in ans3, "printed: 0.31 mm and 0.46 mm; 0.23 mm at 10 MHz")
close(U.x3_nf10 / U.x3_nf, 2.0, 1e-12, "the near field doubles with the frequency"); close(U.x3_ax / U.x3_ax10, 2.0, 1e-12, "the axial resolution halves")

# ---- Doppler: the exact shift of a moving reflector, f0 (c + u)/(c - u) - f0 with u = v cos θ
def exact_shift(f0, v, deg): u = v * math.cos(math.radians(deg)); return f0 * ((C + u) / (C - u) - 1)
v4 = bisect(lambda v: exact_shift(4.0e6, v, 60) - 2600, 0.0, 10.0)
close(U.x4_v, v4, 1e-3, f"example velocity against the exact formula ({v4:.5f} m/s)"); check(plain(example("Blood velocity from a Doppler shift")[4]).startswith(f"{v4:.2f} m/s, and a PRF above 5.2 kHz"), "printed: 1.00 m/s and 5.2 kHz")
close(U.x4_prf, 2 * 2600, 0, "lowest PRF = twice the shift")

# ---- questions: sound waves and interfaces
p = prob("Why is the gel needed"); check(f"about {round(U.Z_SOFT / U.Z_AIR, -3):,.0f}" in plain(p["a"][1]) and "99.9%" in plain(p["a"][1]), "gel: impedance ratio about 4,000 and 99.9% reflected")
p = prob("fraction of the incident intensity"); Rb, Tb = boundary(1.63, 7.80)
close(value(p), 100 * Rb, 1e-12, "bone reflection"); check(f"{100 * Rb:.1f}%" == "42.8%", "42.8%")
check(sorted(round(v, 9) for v in p["vals"]) == sorted(round(v, 9) for v in (100 * Rb, 100 * math.sqrt(Rb), 100 * Tb, 100 * 1.63 / 7.80)), "decoys: unsquared, transmitted, Z1/Z2")
p = prob("Rank these media")
rng = {r[0]: [float(x.replace(",", "")) for x in re.findall(r"[\d,.]+", r[1])] for r in U.MEDIA}
order = ["Air", "Fat", "Muscle", "Cortical bone"]
check(all(max(rng[order[i]]) < min(rng[order[i + 1]]) for i in range(3)) and [c["b"] for c in p["chips"]] == [0, 1, 2, 3], "the ranges in the media table do not overlap, so the ranking is unique")

# ---- questions: attenuation and pulse-echo imaging
p = prob("greatest depth"); dmax = bisect(lambda d: 2 * d / C - 1 / 5000, 0.0, 1.0) * 100
close(value(p), dmax, 1e-9, "greatest depth at 5 kHz"); close(dmax, 200 / float(t_cm), 1e-12, "200 µs at 13 µs per cm"); check(f"{dmax:.1f}" == "15.4", "15.4 cm")
p = prob("probe is changed"); ex = plain(p["a"][1])
check(f"{slab_loss(5.0, 30.0):.0f} dB" == "75 dB" and f"{slab_loss(2.5, 30.0):.1f} dB" == "37.5 dB" and "75 dB" in ex and "37.5 dB" in ex and "0.62 mm" in ex, "trade-off: 75 dB at 5 MHz, 37.5 dB at 2.5 MHz, λ 0.62 mm")

# ---- questions: transducers and resolution
p = prob("A transrectal probe transmits"); ax = float(Fr(1540) * Fr(3, 7_500_000) * 1000 / 2)
close(value(p), ax, 1e-12, "axial resolution at 7.5 MHz, 3 cycles"); check(sorted(p["vals"]) == sorted([ax, 2 * ax, ax * 2 / 3, ax / 3]), "decoys: the whole pulse, one wavelength, half a wavelength")


# ---- questions: Doppler
p = prob("What is the Doppler shift"); fd = exact_shift(5.0e6, 0.40, 30.0)
close(value(p) * 1000, fd, 1e-3, f"Doppler shift at 30° against the exact formula ({fd:.1f} Hz)"); check(f"{value(p):.2f}" == "2.25", "2.25 kHz")
check({round(v, 6) for v in (U.d_half / 1000, U.d_nocos / 1000, U.d_sin / 1000)} == {round(x, 6) for x in (U.d_fd / 2000, 2 * 5.0e6 * 0.40 / C / 1000, 2 * 5.0e6 * 0.40 * 0.5 / C / 1000)}, "traps: no factor 2, no cos θ, sin θ")
check(all(round(v, 6) in {round(x, 6) for x in p["vals"]} for v in (U.d_nocos / 1000, U.d_sin / 1000)), "the no-cos θ and sin θ traps are both shown")
p = prob("peak blood velocity"); v17 = bisect(lambda v: exact_shift(3.0e6, v, 45.0) - 2000, 0.0, 10.0)
close(value(p), 100 * v17, 1e-3, f"typed velocity against the exact formula ({100 * v17:.2f} cm/s)"); check(abs(100 * U.v_nocos / value(p) - 1) > p["tol"], "leaving out cos θ lies outside the tolerance")

# ---- questions and text: speed-of-sound errors, by tracing the echo time through each layer
def displayed_shift(fat_cm, c_fat, rest_cm=7.0):
    t = 2 * (fat_cm / 100 / c_fat + rest_cm / 100 / C)                       # true echo time
    return (C * t / 2 * 100 - (fat_cm + rest_cm)) * 10                        # mm the scanner adds
close(displayed_shift(4.0, 1450.0, rest_cm=2.0), displayed_shift(4.0, 1450.0), 1e-9, "the error does not depend on what lies behind the fat")
close(U.k_err, displayed_shift(3.0, 1450.0), 1e-9, "3 cm of fat in the probe-pressure question"); check(f"{U.k_err:.1f} mm" in plain(prob("pressed hard")["a"][1]) and U.k_err < 6, "printed 1.9 mm, far below the 6 mm difference")
check(keyed_text(prob("pressed hard")) == "The probe pushed the prostate posteriorly during the scan", "keyed: probe pressure")
close(U.fat_pct, 100 * displayed_shift(1.0, 1450.0) / 10, 1e-9, "fat error as a share of its thickness"); check(f"about {round(U.fat_pct)}% of the fat thickness" in text, "about 6% in the text")

# ---- cards and take-aways print the same numbers
cards = {c["q"]: plain(" ".join(c["a"] + c["w"])) for c in U.TOPIC["cards"]}
check("0.31 mm at 5 MHz" in cards["Wavelength in soft tissue"] and "0.308 mm" in cards["Wavelength in soft tissue"], "card: wavelength")
check(f"= {slab_loss(5.0, 20.0):.0f} dB" in cards["Attenuation in soft tissue"], "card: 50 dB for 10 cm at 5 MHz")
check(f"{float(t_cm):.2f} µs" in cards["Echo depth and time"], "card: 12.99 µs")
check(f"{bisect(lambda d: 2 * d / C - 1 / 5000, 0.0, 1.0) * 100:.1f} cm" in cards["Pulse repetition frequency and depth"], "card: 15.4 cm at 5 kHz")
check(f"{float(Fr(1540) * dur * 1000 / 2):.2f} mm" in cards["Axial resolution"], "card: 0.46 mm")
check(f"{exact_shift(5.0e6, 0.40, 60.0) / 1000:.2f} kHz" in cards["Doppler shift"], "card: 1.30 kHz at 60°")
check(f"about {round(U.fat_pct)}%" in cards["Errors of transabdominal prostate localization"], "card: about 6% behind fat")
take = plain(" ".join(x for t in U.TAKE for x in t))
check("λ = 0.31 mm at 5 MHz" in take and "30–45% at bone" in take and "99.9% at air" in take and "13 µs per cm" in take and "about 6% deeper" in take, "take-aways print the same values")

# ---- every numeric question has distinct options
for q in T["ultrasound"]["problems"]:
    if q.get("vals"): check(len(set(round(v, 6) for v in q["vals"])) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_ultrasound: {n} numbers re-derived"); print("numbers_ultrasound: PASS" if not bad else f"numbers_ultrasound: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
