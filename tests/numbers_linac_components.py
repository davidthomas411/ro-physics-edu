"""Linac components: every number the chapter prints or keys, re-derived by another route
(SI units for momentum and field, the wave period for the wavelength, bisection for lengths, pulses per minute for the dose per pulse)."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import linac_components as L
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}["linac-components"]; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in T["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
text = " ".join(plain(x) for b in T["guide"] for x in (b[1:] if b[0] != "ex" else [b[1], b[2], *b[3], b[4]]) if isinstance(x, str))
shown = lambda s: s in text                                                   # a value as printed in the guide

# SI constants (CODATA 2018), independent of calc.py
C, H, E, ME_KG = 299792458.0, 6.62607015e-34, 1.602176634e-19, 9.1093837015e-31
MEC2 = ME_KG * C ** 2 / E / 1e6                                               # electron rest energy in MeV, from its mass in kg

# ---- wavelength from the period (λ = c × 1/f) and from the photon energy (λ = hc / hf)
for f_mhz, got in ((2998, L.LAM), (2856, L.LAM_T)):
    close(got, 100 * C * (1 / (f_mhz * 1e6)), 1e-12, f"wavelength at {f_mhz} MHz from the period")
    close(got, 100 * (H * C / E) / (H * f_mhz * 1e6 / E), 1e-9, f"wavelength at {f_mhz} MHz from hc / E")
close(value(prob("f = 2856 MHz")), L.LAM_T, 1e-12, "typed key: wavelength at 2856 MHz"); close(round(L.LAM_T, 1), 10.5, 1e-12, "10.5 cm")
check(shown(f"{L.LAM:.1f} cm") and round(L.LAM, 1) == 10.0, "worked example prints 10.0 cm")

# ---- speeds: β = pc / total energy, against calc's √(1 − 1/γ²)
beta = lambda t: math.sqrt(t * t + 2 * t * MEC2) / (t + MEC2)
close(L.B30, beta(0.030), 1e-9, "β at 30 keV"); close(L.B2, beta(2.0), 1e-9, "β at 2 MeV")
check(shown(f"{beta(0.030):.2f}c at 30 keV") and shown(f"{beta(2.0):.2f}c by 2 MeV"), "the text prints 0.33c and 0.98c")

# ---- energy gain per metre and guide length, the length found by bisection on gain × length = energy
close(L.G1, 6 / 0.40, 1e-12, "gain: 6 MeV over 0.40 m"); close(L.L18, bisect(lambda x: L.G1 * x - 18, 0, 10), 1e-9, "length for 18 MeV")
check(shown("15 MeV/m, and 1.2 m for 18 MeV"), "worked example prints 15 MeV/m and 1.2 m")
q8 = prob("over 30 cm"); g2 = 6 / 0.30
close(value(q8), bisect(lambda x: g2 * x - 15, 0, 10), 1e-9, "question: length for 15 MeV at 20 MeV/m"); close(value(q8), 0.30 * 15 / 6, 1e-12, "proportional to the energy")
close(L.L15_inv, 0.30 / (15 / 6), 1e-12, "decoy: the inverted ratio"); check(L.L15_inv in q8["vals"] and L.L15_ratio in q8["vals"], "both fixed decoys are offered")

# ---- bending magnet: p = γ m β c in SI and B = p / (e r)
def b_si(t_mev, r_m):
    g = 1 + t_mev / MEC2; b = math.sqrt(1 - 1 / g ** 2)
    return g * ME_KG * b * C / (E * r_m)
close(L.BF18, b_si(18, 0.10), 1e-7, "field for 18 MeV on 10 cm"); close(L.BF6, b_si(6, 0.10), 1e-7, "field for 6 MeV on 10 cm")
close(L.RAT18, b_si(18, 0.10) / b_si(6, 0.10), 1e-7, "momentum ratio 18 to 6 MeV")
check(shown(f"{b_si(18, 0.10):.3f} T at 18 MeV and {b_si(6, 0.10):.3f} T at 6 MeV") and shown(f"{L.RAT18:.2f} times larger"), "worked example prints 0.617 T, 0.217 T, and 2.85")
q9 = prob("radius of the path r = 8.0 cm")
close(value(q9), b_si(12, 0.080), 1e-7, "question: field for 12 MeV on 8.0 cm")
close(L.BNR12, math.sqrt(2 * ME_KG * 12e6 * E) / (E * 0.080), 1e-7, "decoy: the non-relativistic momentum in SI"); check(L.BNR12 in q9["vals"], "the non-relativistic decoy is offered")
q10 = prob("from a 6 MeV to a 20 MeV")
close(value(q10), b_si(20, 1.0) / b_si(6, 1.0), 1e-7, "question: field ratio 20 to 6 MeV")
check(all(any(abs(v - w) < 1e-12 for v in q10["vals"]) for w in (20 / 6, math.sqrt(20 / 6))), "the kinetic-energy and non-relativistic ratios are offered")
check(round(b_si(20, 1) / b_si(6, 1), 2) != round(20 / 6, 2) and round(L.RAT18, 2) == 2.85, "the momentum ratios differ from the energy ratios")

# ---- photon energies: the mean is a third of the maximum, which is the electron kinetic energy
close(3 * L.M6, 6.0, 1e-12, "three means make the maximum"); close(value(prob("Electrons of 6 MeV strike")), 2.0, 1e-12, "question key: 2.0 MeV")
check(shown("about 2 MeV for 6 MeV electrons"), "the text prints about 2 MeV")

# ---- dose per pulse: dose per minute over pulses per minute
ppm = 360 * 60
close(L.DP600, 600 / ppm, 1e-12, "600 MU/min at 360 per second"); close(L.DP1400, 1400 / ppm, 1e-12, "1400 MU/min at 360 per second")
check(shown(f"{10 * 600 / ppm:.2f} mGy per pulse flattened and {10 * 1400 / ppm:.2f} mGy FFF, {1400 / 600:.1f} times more"), "worked example prints 0.28 mGy, 0.65 mGy, and 2.3")
q20 = prob("2400 MU/min")
close(value(q20), 10 * 2400 / ppm, 1e-12, "question: 2400 MU/min at 360 per second, in mGy"); close(round(value(q20), 2), 1.11, 1e-12, "1.11 mGy")
check(any(abs(v - 10 * 2400 / 360) < 1e-9 for v in q20["vals"]) and any(abs(v - 10 * 2400 / 60) < 1e-9 for v in q20["vals"]), "the decoys without the 60 s and without the pulse rate are offered")

# ---- average RF power: energy per pulse times pulses per second
q5 = prob("peak power = 3.0 MW")
close(value(q5), 3.0e6 * 4.0e-6 * 250 / 1e3, 1e-12, "typed key: 12 J per pulse × 250 per second = 3.0 kW"); close(L.DUTY, 1e-3, 1e-12, "duty cycle 0.1%")

for b in bad: print("FAIL", b)
print(f"numbers_linac_components: {n} numbers re-derived"); print("numbers_linac_components: PASS" if not bad else f"numbers_linac_components: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
