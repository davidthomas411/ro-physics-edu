"""Kilovoltage x-ray production: every worked number and keyed answer re-derived by another route.
Wavelengths come from the SI values of h, c, and e; x-ray power from k Z I V² instead of efficiency × power; the focal spot from projecting the
strip's end points; the heat-unit factors from the rms voltage of each waveform; the ripple from a numerical scan of the rectified envelope;
HVLs by bisection on the exponential through the readings; and effective energies by bisection on the log–log line through the NIST values,
checked by putting the energy back into the attenuation of one HVL."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import xray_tube as X
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T_ = {t["id"]: t for t in TOPICS}; bad = []; n = 0
assert "xray-tube" in T_, "xray-tube is not registered in src/topics/__init__.py"
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in T_["xray-tube"]["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def block_text(b):
    if b[0] in ("h2", "p"): return plain(b[1])
    if b[0] in ("ul", "ol", "eq"): return " ".join(plain(x) for x in b[1])
    if b[0] == "ex": return " ".join(plain(x) for x in [b[1], b[2], b[4], *b[3]])
    if b[0] == "table": return " ".join(plain(c) for r in b[2] for c in r)
    return ""
GUIDE = " ".join(block_text(b) for b in T_["xray-tube"]["guide"])
CARDS = " ".join(plain(x) for c in T_["xray-tube"]["cards"] for x in [*c["a"], *c["w"]])
def shown(s, what, where=None):                                                # a re-derived number, formatted, appears on the page
    global n; n += 1
    if s not in (GUIDE if where is None else where): bad.append((what, "not found", s))
H_SI, C_SI, E_SI = 6.62607015e-34, 299792458.0, 1.602176634e-19
lam_si = lambda kv: H_SI * C_SI / (E_SI * kv * 1e3) * 1e9                     # nm, from E = eV and λ = hc/E in SI units
LN2 = math.log(2.0)

# ---- the Duane–Hunt limit
close(X.HC, H_SI * C_SI / E_SI * 1e9 / 1e3, 1e-4, "hc = 1.2398 keV nm against the SI constants")
close(X.lam1, lam_si(250), 1e-4, "minimum wavelength at 250 kV"); shown(f"{lam_si(250):.5f} nm", "250 kV wavelength printed"); shown(f"{lam_si(250) * 1000:.2f} pm", "in pm")
close(value(prob("runs at 80 kVp")), lam_si(80), 1e-4, "keyed minimum wavelength at 80 kVp"); shown(f"{lam_si(80):.4f} nm", "80 kVp wavelength on the card", CARDS)
vals = sorted(prob("runs at 80 kVp")["vals"]); check(any(abs(v / lam_si(80) - 3) < 1e-3 for v in vals) and any(abs(v - 1.2398 * 80) < 1e-6 for v in vals), "distractors: one third of the peak energy, and multiplying by the kVp")

# ---- efficiency: the x-ray power as k Z I V², with the beam power left out
px = lambda Z, V, I: 9e-10 * Z * I * V ** 2
close(X.Px1, px(74, 250e3, 15e-3), 1e-12, "x-ray power at 250 kV and 15 mA"); shown(f"{px(74, 250e3, 15e-3):.0f} W of x-rays", "x-ray power printed")
close(X.P1 - X.Px1, 250e3 * 15e-3 - px(74, 250e3, 15e-3), 1e-9, "heat in the anode"); shown(f"{250e3 * 15e-3 - px(74, 250e3, 15e-3):,.0f} W", "heat printed")
shown(f"{100 * px(74, 250e3, 15e-3) / (250e3 * 15e-3):.1f}% at 250 kV", "efficiency at 250 kV in the text"); shown(f"{100 * px(74, 100e3, 1.0) / 100e3:.1f}% at 100 kV", "efficiency at 100 kV in the text")
shown(f"{100 * px(74, 100e3, 1.0) / 100e3:.2f}%", "efficiency at 100 kV on the card", CARDS)
close(value(prob("leaves the anode as x-rays")), px(74, 200e3, 20e-3), 1e-12, "typed x-ray power at 200 kV and 20 mA"); close(px(74, 200e3, 20e-3), 53.28, 1e-9, "53.3 W")
close(px(74, 200e3, 2e5) / px(74, 100e3, 2e5), 4.0, 1e-12, "at a fixed current the x-ray power rises as V²")

# ---- the thick-target triangle: thin layers, each flat up to the energy of the electrons reaching it, summed
E0, steps = 100.0, 20000
layers = [E0 * (1 - (k + 0.5) / steps) for k in range(steps)]                    # equal energy loss in each layer
spec = lambda e: sum(1.0 for el in layers if el >= e) / steps                     # flat thin-target spectrum of unit height per layer
for e in (10.0, 30.0, 60.0, 90.0): close(spec(e), (E0 - e) / E0, 2e-4, f"sum of flat layers at {e:.0f} keV lies on the straight line to zero at E_max")

# ---- line focus: project the end points of the strip on the plane normal to the central ray
def projected(L, deg):
    t = math.radians(deg); u = (0.0, -1.0)                                      # central ray points down
    a, b = (0.0, 0.0), (L * math.sin(t), -L * math.cos(t))                      # strip on the anode face, at θ to the central ray
    d = (b[0] - a[0], b[1] - a[1]); along = d[0] * u[0] + d[1] * u[1]
    return math.hypot(d[0] - along * u[0], d[1] - along * u[1])
close(X.s2, projected(5.0, 12.0), 1e-12, "effective spot of a 5.0 mm strip at 12°"); shown(f"{projected(5.0, 12.0):.2f} mm, about one fifth", "effective spot printed")
close(value(prob("small anode angle")), projected(6.0, 10.0), 1e-12, "keyed effective spot at 10°")

# ---- heat units: the waveform factors are the rms voltage relative to a single-phase supply
def rms(p, k=200000):                                                          # rms of an ideal p-pulse rectified waveform of unit peak
    return math.sqrt(sum(max(math.cos(2 * math.pi * j / k - 2 * math.pi * q / p) for q in range(p)) ** 2 for j in range(k)) / k)
r2, r6 = rms(2, 20000), rms(6, 20000)
close(r2, 1 / math.sqrt(2), 1e-4, "single-phase rms 0.71"); close(r6 / r2, X.F_6P, 4e-3, "six-pulse factor 1.35 is the rms ratio"); close(1.0 / r2, X.F_12P, 4e-3, "constant potential: factor √2 = 1.41")
close(X.hu3, (120 * 250 * 15) * 1.41, 1e-12, "CT scan heat units"); shown(f"{120 * 250 * 15 * 1.41:,.0f} HU", "heat units printed")
energy = sum(120e3 * 0.250 * 0.001 for _ in range(15000))                       # 15 s in 1 ms steps at constant power
close(X.J3, energy, 1e-9, "electrical energy of the scan"); shown(f"{energy / 1000:.0f} kJ of electrical energy", "energy printed"); shown(f"{energy * (1 - 9e-10 * 74 * 120e3) / 1000:.0f} kJ stays", "heat printed")
shown(f"{1 / 1.41:.2f} J", "1 HU in joules")

# ---- ripple: the lowest point of the rectified envelope, found by scanning the phase
def dip(p, k=36000):
    return min(max(math.cos(2 * math.pi * j / k - 2 * math.pi * q / p) for q in range(p)) for j in range(k))
for p_, txt in ((2, "100% ripple"), (6, "13% ripple"), (12, "3% ripple")):
    close(X.ripple(p_), 1 - dip(p_), 1e-6, f"ripple of {p_} pulses"); shown(f"{100 * (1 - dip(p_)):.0f}% ripple", txt)
shown(f"{100 * dip(6):.0f}% for three-phase", "six-pulse dip printed"); shown(f"{100 * dip(12):.0f}% for twelve-pulse", "twelve-pulse dip printed")

# ---- homogeneity coefficient
close(X.hc4, 2.0 / (4.4 - 2.0), 1e-12, "worked example HC"); shown(f"HC = {2.0 / 2.4:.2f}", "HC printed")
p = prob("air kerma falls to 50% behind 2.5 mm Al"); close(value(p), 2.5 / 3.5, 1e-12, "keyed HC")
check(sorted(round(v, 4) for v in p["vals"]) == sorted(round(v, 4) for v in (2.5 / 6.0, 2.5 / 3.5, 3.5 / 2.5, 6.0 / 2.5)), "HC distractors: total thickness, inverted, ratio of thicknesses")

# ---- effective energy: bisection on the log–log line through the NIST values, then one HVL of that energy must transmit half
def mu_rho_at(E, tab):
    es = sorted(tab); a = max(e for e in es if e <= E); b = min(e for e in es if e >= E)
    if a == b: return tab[a]
    return math.exp(math.log(tab[a]) + (math.log(tab[b]) - math.log(tab[a])) * (math.log(E) - math.log(a)) / (math.log(b) - math.log(a)))
def e_eff(hvl_mm, rho, tab, k=LN2):
    target = k / (hvl_mm / 10) / rho; es = sorted(tab)
    return bisect(lambda E: mu_rho_at(E, tab) - target, es[0], es[-1])
for tab in (X.AL, X.CU):
    es = sorted(tab); check(all(tab[a] > tab[b] for a, b in zip(es, es[1:])), "μ/ρ falls with energy in each table")
E4 = e_eff(2.0, 8.96, X.CU); close(X.E4, E4, 1e-9, "orthovoltage effective energy"); shown(f"about {E4:.0f} keV, {E4 / 250:.2f} of the peak", "effective energy printed")
close(math.exp(-mu_rho_at(E4, X.CU) * 8.96 * 0.20), 0.5, 1e-9, "one HVL at the effective energy transmits half")
check(1 / 3 <= E4 / 250 <= 1 / 2, "the worked effective energy lies between one third and one half of the peak")
p = prob("first HVL of 3.0 mm Al"); Eal = e_eff(3.0, 2.699, X.AL); close(value(p), Eal, 1e-9, "keyed superficial effective energy"); close(Eal, 33.7, 2e-3, "about 34 keV")
close(math.exp(-mu_rho_at(Eal, X.AL) * 2.699 * 0.30), 0.5, 1e-9, "3.0 mm Al halves a beam of that energy")
for got, want in zip(sorted(p["vals"]), sorted([Eal, e_eff(3.0, 1.0, X.AL), e_eff(3.0, 2.699, X.AL, math.log10(2.0)), 100.0])): close(got, want, 1e-9, "effective energy distractors: no density, log10 2, the peak")
check(1 / 3 - 0.01 <= Eal / 100 <= 1 / 2, "the superficial beam's effective energy is about one third of the peak")

# ---- the rank question: effective energies of four first HVLs
r = [e_eff(2.0, 2.699, X.AL), e_eff(4.0, 2.699, X.AL), e_eff(1.0, 8.96, X.CU), e_eff(3.0, 8.96, X.CU)]
for (txt, v), w in zip(X.RANK, r): close(v, w, 1e-9, f"rank energy: {txt}")
check(r == sorted(r), "lowest to highest effective energy"); check([c["b"] for c in prob("Rank the beams")["chips"]] == [0, 1, 2, 3], "each item is keyed to its rank")
check(1.0 < 4.0 and r[2] > r[1], "ranking by the number alone puts 1 mm Cu below 4 mm Al, but its effective energy is higher")

# ---- first HVL by interpolation between two readings: bisection on the exponential through them
x50 = bisect(lambda x: 54.5 * (45.2 / 54.5) ** ((x - 2.0) / 1.0) - 50.0, 2.0, 3.0)
close(x50, 2.46, 1e-3, "2.46 mm Al")

# ---- other numbers in explanations
shown(f"{42 / 74:.2f} of the tungsten value", "molybdenum yield ratio", plain(prob("replaced by a molybdenum anode")["a"][1]))
shown(f"{(100 / 80) ** 2:.2f} or more", "kVp squared ratio", plain(prob("changed from 80 kVp to 100 kVp")["a"][1]))
for c in ("0.0155", "1.04 mm"): shown(c, f"card working {c}", CARDS)

for b in bad: print("FAIL", b)
print(f"numbers_xray_tube: {n} numbers re-derived"); print("numbers_xray_tube: PASS" if not bad else f"numbers_xray_tube: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
