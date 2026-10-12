"""Brachytherapy source calibration and safety chapter (brachy-qa): every worked number and keyed answer re-derived by another route.
P_TP from the air density of the ideal-gas law, decay by integrating dS/dt = -lambda S step by step, dwell times from a constant product of
strength and time, exposure through the air kerma strength instead of the exposure rate constant, barrier thickness by bisection on the
transmission, the seed sample by counting, and the dose to others by summing the decaying dose rate hour by hour. The quoted limits are
checked for agreement between the text, the cards, the take-aways, and the questions."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import brachy_qa as B
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}["brachy-qa"]; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def true(c, what):
    global n; n += 1
    if not c: bad.append((what, "not true", ""))
def prob(phrase):
    hits = [p for p in T["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                   # the number behind the keyed option, or the typed answer
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
def ex_text(title):
    b = next(x for x in T["guide"] if x[0] == "ex" and x[1] == title); return plain(" ".join([b[2], *b[3], b[4]]))
text = plain(" ".join(b[1] for b in T["guide"] if b[0] == "p"))
cards = {c["q"]: plain(" ".join(c["a"] + c["w"])) for c in T["cards"]}
take = plain(" ".join(x for sec in T["take"] for x in sec))

# ---- air density: P_TP is the mass of air in the chamber at 22 °C and 101.325 kPa over the mass at the measurement (ideal gas)
R_GAS, M_AIR = 8.314462618, 0.0289647
rho = lambda t_c, p_kpa: p_kpa * 1e3 * M_AIR / (R_GAS * (273.15 + t_c))
ptp_gas = lambda t_c, p_kpa: rho(22.0, 101.325) / rho(t_c, p_kpa)
close(B.ptp1, ptp_gas(23.5, 99.80), 1e-4, "worked example: P_TP at 23.5 °C and 99.80 kPa"); close(B.ptp_q, ptp_gas(20.0, 102.80), 1e-4, "question: P_TP at 20.0 °C and 102.80 kPa")
true(B.ptp1 > 1 > B.ptp_q, "warm, thin air gives P_TP above 1; cool, dense air below 1")

# ---- decay, by fourth-order Runge-Kutta steps of dS/dt = -lambda S
def decay_rk4(s0, days, th, h=0.01):
    lam = math.log(2) / th; s = s0; k = round(days / h)
    f = lambda y: -lam * y
    for _ in range(k):
        a1 = f(s); a2 = f(s + h * a1 / 2); a3 = f(s + h * a2 / 2); a4 = f(s + h * a3)
        s += h * (a1 + 2 * a2 + 2 * a3 + a4) / 6
    return s

# worked example: a new HDR source in the well chamber
raw = 87.62 * (4.690e11 / 1e9)                                                  # nA times U per nA
sk = raw * ptp_gas(23.5, 99.80) * 1.003 * 0.998; cert = decay_rk4(43350.0, 5.0, 73.8)
close(B.raw1, raw, 1e-9, "M N_SK in U"); close(B.sk1, sk, 1e-4, "S_K with all corrections"); close(B.cert1_now, cert, 1e-8, "certificate decayed by 5.0 d")
close(B.pct1, 100 * (sk - cert) / cert, 1e-2, "percent difference from the certificate")
t1 = ex_text("Air kerma strength of a new HDR source")
true(all(s in t1 for s in ("1.0205", "41,094 U", "41,977 U", "41,361 U", "+1.5%", "within 3%")), "the worked example prints P_TP 1.0205, 41,094, 41,977, and 41,361 U, and +1.5%")

# worked example: dwell time after 60 d, from a constant product of strength and time
s_now = decay_rk4(41000.0, 60.0, 73.8)
close(B.s2_now, s_now, 1e-8, "S_K after 60 d"); close(B.t2_now, bisect(lambda t: s_now * t - 41000.0 * 300.0, 1, 5000), 1e-9, "the time that delivers the same strength-time product")
true(all(s in ex_text("Treatment time after decay") for s in ("23,337 U", "527 s", "1.76 times")), "the worked example prints 23,337 U, 527 s, and 1.76 times")

# strengths and times quoted in the text and the cards
f90, f120 = decay_rk4(1.0, 90, 73.8), decay_rk4(1.0, 120, 73.8)
close(B.f90, f90, 1e-8, "fraction left after 90 d"); close(B.f120, f120, 1e-8, "after 120 d")
true(f"at {100 * f90:.0f}% of its strength" in text and f"{1 / f90:.1f} times as long" in text, f"the text quotes {100 * f90:.0f}% and {1 / f90:.1f} times after 90 d")
true(f"{100 * f90:.0f}% of its strength after 90 d and {100 * f120:.0f}% after 120 d" in cards["Dwell time and source decay"], "the card quotes 43% and 32%")

# ---- exposure near a stuck 10 Ci source, through the air kerma strength: S_K = 0.876 Γ A, K = S_K / d² (µGy/h at d metres)
sk_10ci = 0.876 * 4.69 * 10000                                                  # U
k_1m = sk_10ci / 1.0 ** 2 * (2.0 / 60)                                          # µGy in 2.0 min at 1.0 m
close(10 * B.k3, k_1m / 1000, 1e-9, "air kerma in mGy, 2.0 min at 1.0 m"); close(1000 * B.x3, k_1m / 8.76, 1e-9, "exposure in mR (1 mR is 8.76 µGy of air kerma)")
true(all(s in ex_text("Exposure near a stuck source") for s in ("4.69 R/h", "156 mR", "1.37 mGy", "39 mR")), "the worked example prints 4.69 R/h, 156 mR, 1.37 mGy, and 39 mR at 2 m")
close(B.kerma_rate(40000, 1) / 1000, 40000 / 100 ** 2 * 10, 1e-12, "40,000 U: 40 mGy/h at 1 m, by 1 U = 1 cGy cm²/h at 100 cm"); true("40 mGy/h at 1 m from a 40,000 U source" in text, "the text quotes 40 mGy/h")
p = prob("therapist stands near the door")
k_2m = sk_10ci / 2.0 ** 2 * (3.0 / 60)
close(value(p), k_2m / 8.76, 1e-9, "keyed 58.6 mR at 2.0 m for 3.0 min, from the air kerma")
close(B.w15_1m, 4 * value(p), 1e-12, "distractor: the rate at 1 m"); close(B.w15_hours, 60 * value(p), 1e-12, "distractor: minutes taken as hours"); close(B.w15_ci, value(p) / 1000, 1e-12, "distractor: 10 Ci entered as 10 mCi")
true(set(p["vals"]) == {value(p), B.w15_1m, B.w15_hours, B.w15_ci}, "the four exposure options are the keyed value and its three traps")

# ---- shielding, by bisection on the transmission 2^(-x/HVL)
x_pb = bisect(lambda x: 2 ** (-x / 4.8) - 1 / 1000, 0, 500)
close(B.t4, x_pb, 1e-9, "lead for a factor of 1000"); true("48 mm" in ex_text("Lead for a factor of 1000") and "9.97" in ex_text("Lead for a factor of 1000"), "the worked example prints 9.97 HVL and 48 mm")
p = prob("The wall of an HDR room")
x_con = bisect(lambda x: 40000 / 3.0 ** 2 * 2 ** (-x / 4.5) - 20.0, 0, 500)
close(value(p), x_con, 1e-9, "keyed concrete thickness: 35.1 cm"); close(B.w16_nod, bisect(lambda x: 40000 * 2 ** (-x / 4.5) - 20.0, 0, 500), 1e-9, "distractor: no inverse square")
close(B.w16_log10, x_con * math.log10(2), 1e-9, "distractor: log10 in place of log2"); close(B.w16_ln, x_con * math.log(2), 1e-9, "distractor: ln in place of log2")

# ---- typed well-chamber question
p = prob("M = 79.40 nA")
close(value(p), 79.40 * 471.2 * ptp_gas(20.0, 102.80) * 1.002, 1e-4, "typed S_K: 36,702 U"); close(B.sk_q_notp / value(p), 1 / ptp_gas(20.0, 102.80), 1e-4, "leaving out P_TP is 1/P_TP too high")
true("2.1% high" in plain(p["a"][1]), "the explanation says 2.1% high")
true(p["tol"] < abs(B.sk_q_notp / value(p) - 1), "a reading without P_TP is marked wrong")

# ---- certificate comparison with decay, 7.0 d
p = prob("dated 7.0 d before the measurement")
c7 = decay_rk4(44000.0, 7.0, 73.8)
close(value(p), 100 * (42300 / c7 - 1), 1e-6, "keyed +2.7%"); close(B.w5_nodecay, 100 * (42300 / 44000 - 1), 1e-12, "distractor: no decay")
close(B.w5_exp, 100 * (42300 / (44000 * math.exp(-7.0 / 73.8)) - 1), 1e-12, "distractor: e^(-t/T)"); close(B.w5_grow, 100 * (42300 * c7 / 44000 ** 2 - 1), 1e-6, "distractor: the certificate grown, not decayed")
true([plain(o) for o in p["opts"]] == ["−10.0%", "−3.9%", "+2.7%", "+5.7%"], "the options are −10.0, −3.9, +2.7, and +5.7%")
true(abs(value(p)) < B.AIM < abs(B.w5_nodecay), "the decayed comparison is within 3% and the undecayed one is not")
# a source 6% low
p = prob("repeat readings")
close(B.pct6, -6.0, 1e-9, "the stem's values differ by 6.0%"); true(abs(B.pct6) > B.NRC_OUT > B.AIM and keyed(p).startswith("Hold the source"), "6% exceeds both levels, and the key holds the source from use")

# ---- dwell time after 50 d
p = prob("What total dwell time delivers the same plan now")
s50 = decay_rk4(40800.0, 50.0, 73.8)
close(value(p), bisect(lambda t: s50 * t - 40800.0 * 280.0, 1, 5000), 1e-8, "keyed 448 s"); close(B.w8_lin, 280 * (1 + 50 / 73.8), 1e-12, "distractor: straight-line decay")
close(B.w8_inv, 280 * s50 / 40800.0, 1e-8, "distractor: times the fraction"); close(B.w8_exp, 280 * math.exp(50 / 73.8), 1e-12, "distractor: e^(t/T)")

# ---- release after an implant: the dose to others by summing the decaying dose rate hour by hour
def dose_sum(rate, th_days, e, h=1.0):
    lam = math.log(2) / (th_days * 24); total = 0.0; t = h / 2
    while t < 40 * th_days * 24: total += rate * math.exp(-lam * t) * h; t += h
    return total * e
p = prob("dose to a family member is estimated")
close(value(p), dose_sum(0.006, 59.4, 0.25), 1e-4, "typed 3.09 mSv to a family member"); true(B.INSTR < value(p) < B.REL, "release allowed, with instructions")
close(B.w20, 0.006 * 59.4 * 24 * 0.25, 1e-12, "distractor: the half-life in place of the mean life")
close(B.release_dose(B.RATE_I, 59.4, B.E_NRC), dose_sum(0.01, 59.4, 0.25), 1e-4, "I-125 at 0.01 mSv/h gives 5.1 mSv over the life of the implant")
true("5.1 mSv" in cards["Dose to others from an implant patient"], "the card's working prints 5.1 mSv")
d_pd = dose_sum(B.RATE_PD, 16.99, 0.25); true(4.0 < d_pd <= 5.0 and 4.9 < dose_sum(B.RATE_I, 59.4, 0.25) < 5.2, f"the RG 8.39 dose rates correspond to about 5 mSv with E = 0.25 (Pd-103 {d_pd:.2f} mSv)")
p = prob("ready to go home")
true(keyed(p) == "5 mSv" and [plain(o) for o in p["opts"]] == ["0.5 mSv", "1 mSv", "5 mSv", "50 mSv"], "release question: key 5 mSv, options ascending")

# ---- limits quoted in several places agree
close(B.LEAK_UCI * 37000, B.LEAK_BQ, 1e-9, "0.005 µCi is 185 Bq")
for where, s in (("text", text), ("take-aways", take), ("card", cards["Leak test of sealed sources"])):
    true("185 Bq (0.005 µCi)" in s and "6 months" in s, f"the {where} quote 185 Bq (0.005 µCi) and 6 months")
p = prob("how often are sealed brachytherapy sources leak tested"); true(keyed(p) == "Every 6 months; 185 Bq (0.005 µCi)", "leak test question keyed to 6 months and 185 Bq")
true("above 3%" in text and "Above 5%" in text and "within 1 mm" in plain(" ".join(r[2] for r in B.QA_ROWS)), "3%, 5%, and 1 mm appear in the text and the table")
true("not likely to exceed 5 mSv" in text and "above 1 mSv" in text and "0.25 in the NRC guide of 1997" in text, "release limits and the occupancy factor in the text")

for b in bad: print("FAIL", b)
print(f"numbers_brachy_qa: {n} numbers re-derived"); print("numbers_brachy_qa: PASS" if not bad else f"numbers_brachy_qa: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
