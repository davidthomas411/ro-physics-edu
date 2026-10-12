"""Ion chambers and charge collection: every number the chapter prints or keys, re-derived by another route.
Pressures come from a mercury column, P_TP from ideal-gas air densities, P_ion from a bisection on the recombination model behind each
TG-51 expression, P_pol from the true signal recovered from both polarities, the corrected reading from a sum of logarithms,
the altitude error from a simulated calibration, and the pressure at 1600 m from a hydrostatic integration."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import ion_chambers as IC
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
TID = "ion-chambers"; T = {t["id"]: t for t in TOPICS}[TID]; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def ok(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in T["problems"] if phrase in plain(p["q"])]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def has_val(p, v, tol=1e-9): return any(abs(x - v) <= tol * max(1.0, abs(v)) for x in p["vals"])
def example(title): return next(b for b in T["guide"] if b[0] == "ex" and plain(b[1]) == title)
def shows(text, s, what): ok(s in plain(text), f"{what}: '{s}' is printed")
def bisect(f, a, b):
    for _ in range(300):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2

# ---- pressure units from a mercury column: p = rho g h, with the conventional density of mercury at 0 °C and standard gravity
RHO_HG, G0 = 13595.1, 9.80665
mmhg = RHO_HG * G0 * 1e-3 / 1000                                               # kPa per mmHg
inhg = RHO_HG * G0 * 25.4e-3 / 1000                                            # kPa per inHg
close(760 * mmhg, 101.325, 1e-6, "760 mmHg of mercury is one standard atmosphere")
close(101.325 / inhg, 29.92, 2e-4, "one atmosphere is 29.92 inHg"); shows(next(c for c in T["cards"] if c["q"] == "Pressure units")["a"][0], f"{101.325 / inhg:.2f} inHg", "pressure card")
eq = next(b for b in T["guide"] if b[0] == "eq" and "inHg" in plain(b[1][-1])); shows(eq[1][-1], f"{101.325 / inhg:.2f} inHg", "pressure units under the P_TP equation")
close(1013.25 / 10, 101.325, 1e-12, "1013.25 hPa is 101.325 kPa")

# ---- P_TP as the ratio of ideal-gas air densities, with the TG-51 kelvin offset of 273.2 and the reference 22 °C and 101.33 kPa
R, M_AIR = 8.314462618, 0.0289647
rho = lambda t, p_kpa: p_kpa * 1000 * M_AIR / (R * (t + 273.2))               # kg/m3
ptp = lambda t, p_kpa: rho(22.0, 101.33) / rho(t, p_kpa)
d_t = (ptp(22.5, 101.33) - ptp(21.5, 101.33)) * 100                            # % per °C, central difference at the reference
d_p = (ptp(22.0, 100.83) - ptp(22.0, 101.83)) * 100                            # % per kPa
close(d_t, IC.per_degc, 1e-9, "P_TP changes by 0.34% per °C"); close(d_p, IC.per_kpa, 2e-4, "P_TP changes by 0.99% per kPa")
txt = next(b[1] for b in T["guide"] if b[0] == "p" and "per °C" in plain(b[1]))
shows(txt, f"{d_t:.2f}% per °C", "sensitivity to temperature"); shows(txt, f"{d_p:.2f}% per kPa", "sensitivity to pressure")

# ---- P_ion: the model behind each TG-51 expression, solved by bisection for its constant.
# Pulsed: M_sat/M(V) = 1 + a/V. Continuous: M_sat/M(V) = 1 + b/V^2. The constant reproduces the measured ratio M_H/M_L.
def pion_model(mh, ml, vh, vl, power):
    f = lambda a: (1 + a / vl ** power) / (1 + a / vh ** power) - mh / ml
    a = bisect(f, 0.0, 1e9)
    return 1 + a / vh ** power, 1 + a / vl ** power                           # the correction at V_H and at V_L
pl, _ = pion_model(IC.EX_LH, IC.EX_LL, 300, 150, 1); pc, _ = pion_model(IC.EX_CH, IC.EX_CL, 300, 150, 2); pcw, _ = pion_model(IC.EX_CH, IC.EX_CL, 300, 150, 1)
close(pl, IC.ex_pion_l, 1e-9, "worked example: P_ion of the pulsed 6 MV beam"); close(pc, IC.ex_pion_c, 1e-9, "worked example: P_ion of the Co-60 beam")
close(pcw, IC.ex_pion_c_wrong, 1e-9, "worked example: the pulsed expression applied to Co-60")
ex = example("Two-voltage Pion")
shows(ex[4], f"{pl:.4f} in the 6 MV beam", "two-voltage example"); shows(ex[4], f"{pc:.4f} in the Co-60 beam", "two-voltage example"); shows(ex[4], f"{pcw:.4f}", "two-voltage example")
close(round((pcw - 1) / (pc - 1)), 3, 0, "the pulsed expression triples the Co-60 correction (r + 1 = 3 to first order)"); shows(ex[4], "three times", "two-voltage example")
shows(ex[3][1], f"{IC.EX_LH / IC.EX_LL:.5f}", "6 MV reading ratio"); shows(ex[3][2], f"{IC.EX_CH / IC.EX_CL:.5f}", "Co-60 reading ratio")
close(round((1 - 2) / (round(IC.EX_LH / IC.EX_LL, 5) - 2), 4), round(pl, 4), 0, "the printed 6 MV ratio gives the printed P_ion")
close(round((1 - 4) / (round(IC.EX_CH / IC.EX_CL, 5) - 4), 4), round(pc, 4), 0, "the printed Co-60 ratio gives the printed P_ion")
# Boag's exact collection efficiency for short pulses, f = ln(1 + u)/u with u proportional to 1/V, against the two-voltage value
f_boag = lambda u: math.log1p(u) / u
u_h = bisect(lambda u: f_boag(u) / f_boag(2 * u) - IC.EX_LH / IC.EX_LL, 1e-9, 1.0)
close(1 / f_boag(u_h), pl, 5e-4, "Boag's exact pulsed theory agrees with the two-voltage P_ion within 0.05%")
ok(1.002 <= pl <= 1.02 and 1.0 < pc < pl, "the example values sit in the quoted ranges: 1.002 to 1.02 for a linac, nearer 1 for Co-60")

p7 = prob("in a 6 MV beam at two voltages"); a7, low7 = pion_model(IC.q_mh, IC.q_ml, 300, 150, 1)
close(value(p7), a7, 1e-9, "P_ion, pulsed 6 MV"); ok(f"{a7:.4f}" in [plain(o) for o in p7["opts"]], "keyed P_ion is an option")
close(low7, IC.q_pion_low, 1e-9, "distractor: the correction at 150 V"); ok(has_val(p7, low7), "the 150 V distractor is shown")
cw7, _ = pion_model(IC.q_mh, IC.q_ml, 300, 150, 2); ok(has_val(p7, cw7), "distractor: the continuous expression")
inv7 = (1 - 0.5) / (IC.q_mh / IC.q_ml - 0.5); ok(has_val(p7, inv7) and inv7 < 1, "distractor: the voltage ratio inverted, below 1")

# ---- P_pol: the true signal S is the mean of the magnitudes, because M+ = S + d and M- = -(S - d) for a charge d that does not reverse
def ppol_signal(mpos, mneg, routine):
    s = (abs(mpos) + abs(mneg)) / 2; d = mpos - s
    close(-(s - d), mneg, 1e-12, "the two readings are reproduced by S and d")
    return s / abs(routine)
pe = ppol_signal(IC.EX_MP, IC.EX_MN, IC.EX_MP); close(pe, IC.ex_ppol, 1e-12, "worked example: P_pol")
ex = example("Polarity correction"); shows(ex[4], f"{pe:.4f}", "polarity example"); shows(ex[3][0], f"{IC.EX_MP - IC.EX_MN:.3f} nC", "polarity example")
shows(ex[4], f"{100 * (abs(IC.EX_MP) / ((abs(IC.EX_MP) + abs(IC.EX_MN)) / 2) - 1):.2f}% above the mean", "routine reading above the mean")
p11 = prob("Negative polarity is used routinely"); a11 = ppol_signal(IC.pp_pos, IC.pp_neg, IC.pp_neg)
close(value(p11), a11, 1e-12, "P_pol with the negative polarity routine"); ok(has_val(p11, ppol_signal(IC.pp_pos, IC.pp_neg, IC.pp_pos)), "distractor: positive reading in the denominator")
ok(has_val(p11, abs(IC.pp_pos / IC.pp_neg)) and has_val(p11, abs(IC.pp_neg / IC.pp_pos)), "distractors: the ratios of the readings")
close(abs(abs(IC.pp_pos / IC.pp_neg) - 1) / abs(a11 - 1), 2.0, 0.01, "the ratio of the readings doubles the correction")

# ---- P_TP: worked example and questions by the density route
ex = example("Temperature and pressure"); kpa = 745 * mmhg; t1 = ptp(23.6, kpa)
close(t1, IC.ex_ptp, 1e-6, "worked example: P_TP at 23.6 °C and 745 mmHg"); shows(ex[4], f"{t1:.4f}", "P_TP example"); shows(ex[3][0], f"{kpa:.3f} kPa", "745 mmHg in kPa")
shows(ex[3][1], f"{(23.6 + 273.2) / (22 + 273.2):.4f}", "temperature term"); shows(ex[3][2], f"{101.33 / kpa:.4f}", "pressure term"); shows(ex[4], f"{100 * (t1 - 1):.1f}%", "P_TP example")
close(round(round((23.6 + 273.2) / 295.2, 4) * round(101.33 / round(kpa, 3), 4), 4), round(t1, 4), 0, "the printed terms multiply to the printed P_TP")
p14 = prob("742 mmHg"); close(value(p14), 742 * mmhg, 1e-6, "742 mmHg in kPa")
def typed_ok(p, x): return abs(x - p["ans"]) <= p["tol"] * abs(p["ans"]) + 1e-12      # the rule the page applies to a typed answer
ok(all(typed_ok(p14, x) for x in (98.93, 98.9, 742 / 7.50)), "742 mmHg: rounded answers and 1 kPa = 7.50 mmHg are accepted")
ok(not any(typed_ok(p14, x) for x in (74.2, 742 / 760, 742 * 1.33322)), "742 mmHg: hPa taken as kPa, atmospheres, and a power-of-ten slip are rejected")
p16 = prob("1002 hPa"); close(value(p16), ptp(25.0, 100.2), 1e-9, "P_TP from hPa")
y = ptp(25.0, 100.2)
ok(all(typed_ok(p16, x) for x in (round(y, 4), round(y, 3), (25 + 273.15) / 295.15 * 101.325 / 100.2)), "1002 hPa: rounded answers and the 273.15 and 101.325 variants are accepted")
ok(not any(typed_ok(p16, x) for x in (101.33 / 100.2, 1 / y, 25 / 22 * 101.33 / 100.2, (298.2 / 295.2) * 101.33 / 1002)), "1002 hPa: no temperature term, the inverse, Celsius ratio, and hPa as kPa are rejected")

# ---- the corrected reading by a sum of logarithms
ex = example("Fully corrected reading")
f_ion, f_tp, f_pol = round(pl, 4), round(t1, 4), round(pe, 4)
m_log = math.exp(math.log(IC.EX_LH) + sum(math.log(x) for x in (f_ion, f_tp, IC.EX_PELEC, f_pol)))
close(m_log, IC.ex_m, 1e-9, "worked example: M from the printed factors"); shows(ex[4], f"{m_log:.3f} nC", "corrected reading example")
shows(ex[4], f"{100 * (m_log / IC.EX_LH - 1):.1f}%", "corrected reading example"); shows(ex[3][0], f"{m_log / IC.EX_LH:.5f}", "product of the factors")
p21 = prob("corrected with its measured factors"); mk = 763 * mmhg; t21 = ptp(20.5, mk)
m21 = math.exp(sum(math.log(x) for x in (20.115, 1.0054, t21, 1.0006, 0.9992)))
close(value(p21), m21, 1e-6, "corrected reading with P_TP from mmHg"); ok(has_val(p21, m21 / t21, 1e-6) and has_val(p21, m21 / t21 ** 2, 1e-6) and has_val(p21, m21 / 1.0054, 1e-6), "distractors: P_TP left out, divided, P_ion left out")
close(round(m21, 2), 20.04, 1e-12, "20.04 nC")
t21p = round((20.5 + 273.2) / 295.2 * 101.33 / round(mk, 2), 4)                   # P_TP from the printed 101.72 kPa
close(t21p, round(t21, 4), 0, "the printed pressure gives the printed P_TP"); close(round(20.115 * 1.0054 * t21p * 1.0006 * 0.9992, 2), round(m21, 2), 0, "the printed P_TP gives the keyed M")

# ---- leakage as currents
i_leak, i_sig = 0.050e-9 / 60, 18.40e-9 / 60                                   # A over the 60 s of a reading
p12 = prob("leakage of a chamber and electrometer"); shows(p12["a"][1], f"{100 * i_leak / i_sig:.2f}%", "leakage fraction")
ok(0.001 < i_leak / i_sig < 0.01, "the leakage is above 0.1% and below 1% of the reading, as the keyed option and its twin require")

# ---- settling: the rise from the first to the last reading, by logarithms, and the pressure change it would need
p18 = prob("six consecutive readings"); rd = IC.READ; rise = math.exp(math.log(rd[-1]) - math.log(rd[0])) - 1
shows(p18["a"][1], f"{100 * rise:.1f}%", "rise of the readings"); shows(p18["a"][1], f"{rise * 101.3:.1f} kPa", "pressure change needed")
ok(any(f"about {100 * rise:.1f}%" in plain(o) for o in p18["opts"]), "the pressure distractor quotes the same rise")
ok(rd[-1] == rd[-2] and all(b >= a for a, b in zip(rd, rd[1:])), "the readings rise and then level off")

# ---- temperature taken from the room air: the error by the density route
p19 = prob("filled from a tap"); err = rho(18.0, 101.33) / rho(22.0, 101.33) - 1    # P_TP used / P_TP true - 1
close(err, IC.w_err, 1e-9, "1.4% too high"); ok(keyed(p19) == f"About {100 * err:.1f}% too high", "keyed option for the water temperature")
shows(p19["a"][1], f"{(18.0 + 273.2) / 295.2:.4f}", "true temperature term")

# ---- altitude: a simulated calibration with the sea-level pressure, then the output adjusted to the measurement
true_out = 1.000                                                                # cGy/MU before the adjustment
k_cal = 1 / (rho(22.0, 83.5) * ptp(22.0, 83.5))                                 # chamber constant: reading x P_TP x k = dose
measured = true_out * rho(22.0, 83.5) * ptp(22.0, 101.9) * k_cal                # the reading follows the real air density; P_TP uses the reported pressure
new_out = true_out / measured                                                   # the output is raised until the measurement reads 1.000
p20 = prob("altitude of 1600 m")
ok(keyed(p20) == f"About {100 * (new_out - 1):.0f}% more than intended", f"keyed option for the altitude error ({100 * (new_out - 1):.1f}%)")
ok(any(plain(o) == f"About {100 * (1 - measured):.0f}% more than intended" for o in p20["opts"]), "the 18% distractor is the error of the measurement")
# the pressure at 1600 m from dP/dh = -P M g / (R T(h)) with the standard lapse rate, integrated with RK4
def dpdh(h, p): return -p * M_AIR * G0 / (R * (288.15 - 0.0065 * h))
p_h, hh, step = 101.325, 0.0, 1.0
while hh < 1600 - 1e-9:
    k1 = dpdh(hh, p_h); k2 = dpdh(hh + step / 2, p_h + step / 2 * k1); k3 = dpdh(hh + step / 2, p_h + step / 2 * k2); k4 = dpdh(hh + step, p_h + step * k3)
    p_h += step / 6 * (k1 + 2 * k2 + 2 * k3 + k4); hh += step
close(IC.alt_local, p_h, 2e-3, f"83.5 kPa is the standard-atmosphere pressure at 1600 m ({p_h:.2f} kPa)")

# ---- the build-up cap: the most energetic Compton electron of Co-60 and its range (Katz and Penfold) against 'about 0.5 g/cm2'
e_ph = 1.25; a = e_ph / 0.511; e_max = e_ph * 2 * a / (1 + 2 * a)
r_kp = 0.412 * e_max ** (1.265 - 0.0954 * math.log(e_max))                     # g/cm2
ok(0.35 < r_kp < 0.55, f"the range of a {e_max:.2f} MeV electron, {r_kp:.2f} g/cm2, is about 0.5 g/cm2")

for b in bad: print("FAIL", b)
print(f"numbers_ion_chambers: {n} numbers re-derived"); print("numbers_ion_chambers: PASS" if not bad else f"numbers_ion_chambers: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
