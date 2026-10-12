"""Spatial resolution, noise power, and DQE: every worked number and keyed answer re-derived by another route.
MTFs come from a numerical Fourier integral of the sampled LSF (Simpson's rule), with the frequencies at 0.5 and 0.1 found by bisection;
the Gaussian width from a bisection on the half maximum; the Nyquist frequency as the point about which sampled cosines fold;
aliases from the sampled values themselves and from a DFT peak search; the aperture MTF from integrating the rectangle;
the cascade through logarithms; the DQE in exact fractions and by a bisection for the fluence an ideal detector needs; and the
exposure relations by bisection on the square-root laws."""
import sys, re, math, cmath
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]   # before any other import: tests/numbers.py would shadow the standard module
from fractions import Fraction as Fr
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import image_metrics as M
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T_ = {t["id"]: t for t in TOPICS}; bad = []; n = 0
assert "image-metrics" in T_, "image-metrics is not registered in src/topics/__init__.py"
TOP = T_["image-metrics"]
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def check(c, what):
    global n; n += 1
    if not c: bad.append((what, "", ""))
def prob(phrase):
    hits = [p for p in TOP["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def keyed_text(p): return plain(p["opts"]["ABCDEFG".index(p["key"][0])])
def opts(p): return [plain(o) for o in p["opts"]]
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
GUIDE = " ".join(block_text(b) for b in TOP["guide"])
CARDS = " ".join(plain(x) for c in TOP["cards"] for x in [*c["a"], *c["w"]])
TAKE = " ".join(plain(x) for items in M.TAKE for x in items)
def shown(s, what, where=None):                                                # a re-derived number, formatted, appears on the page
    global n; n += 1
    if s not in (GUIDE if where is None else where): bad.append((what, "not found", s))

# ---------------------------------------------------------------- numerical tools
def simpson(g, a, b, k=4000):
    h = (b - a) / k
    return h / 3 * (g(a) + g(b) + sum((4 if i % 2 else 2) * g(a + i * h) for i in range(1, k)))
def mtf_num(lsf, f, half):                                                     # |∫ LSF e^(−2πifx) dx| / ∫ LSF dx for an even LSF, so the sine part vanishes
    return abs(simpson(lambda x: lsf(x) * math.cos(2 * math.pi * f * x), -half, half)) / simpson(lsf, -half, half)
def gauss(sigma): return lambda x: math.exp(-x * x / (2 * sigma * sigma))
def f_level(sigma, level):                                                     # bisection on the numerical MTF
    return bisect(lambda f: mtf_num(gauss(sigma), f, 10 * sigma) - level, 0.0, 3.0 / sigma)
def ln_series(x):                                                              # ln x = 2 artanh((x − 1)/(x + 1)), summed
    y = (x - 1) / (x + 1); return 2 * sum(y ** (2 * k + 1) / (2 * k + 1) for k in range(400))
def sqrt_newton(x):
    r = x if x > 1 else 1.0
    for _ in range(80): r = (r + x / r) / 2
    return r
def prod_log(*xs): return math.exp(sum(math.log(x) for x in xs))

# ---- FWHM of a Gaussian: bisection on the half maximum
half_x = bisect(lambda x: math.exp(-x * x / 2) - 0.5, 0.0, 5.0)
close(M.FWHM_K, 2 * half_x, 1e-12, "FWHM = 2.355 σ from the half maximum"); shown(f"FWHM = {2 * half_x:.3f} σ", "FWHM factor in the equation")

# ---- worked example: f50 and f10 of a Gaussian LSF with σ = 0.10 mm, from the numerical MTF
f50n, f10n = f_level(M.SIG1, 0.5), f_level(M.SIG1, 0.1)
close(M.f50_1, f50n, 1e-7, "f50 at σ = 0.10 mm, numerical MTF"); close(M.f10_1, f10n, 1e-7, "f10 at σ = 0.10 mm, numerical MTF")
shown(f"f50 = {f50n:.2f} lp/mm and f10 = {f10n:.2f} lp/mm", "answer of the Gaussian example")
shown(f"πσ = {math.pi * M.SIG1:.4f} mm", "πσ printed"); shown(f"√({ln_series(2):.4f} / 2)", "ln 2 from its series"); shown(f"√({ln_series(10):.4f} / 2)", "ln 10 from its series")
shown(f"{sqrt_newton(ln_series(2) / 2):.4f} / {math.pi * M.SIG1:.4f} = {f50n:.2f} lp/mm", "f50 step"); shown(f"{sqrt_newton(ln_series(10) / 2):.4f} / {math.pi * M.SIG1:.4f} = {f10n:.2f} lp/mm", "f10 step")
close(f_level(2 * M.SIG1, 0.5), f50n / 2, 1e-6, "a blur twice as wide halves f50 (as the answer says)")
close(mtf_num(gauss(M.SIG1), 0.0, 1.0), 1.0, 1e-12, "MTF(0) = 1 after normalization")

# ---- card: f50 = 0.187/σ and f10 = 0.342/σ, from the numerical MTF at σ = 1
c50, c10 = f_level(1.0, 0.5), f_level(1.0, 0.1)
shown(f"f50 = {c50:.3f}/σ and f10 = {c10:.3f}/σ", "card constants", CARDS)
shown(f"√(ln 2 / 2) / π = {c50:.3f}", "card working, 0.5", CARDS); shown(f"√(ln 10 / 2) / π = {c10:.3f}", "card working, 0.1", CARDS)

# ---- question: f50 from a FWHM of 0.30 mm
p = prob("full width at half maximum = 0.30 mm")
sig_q = bisect(lambda s: math.exp(-(0.15 ** 2) / (2 * s * s)) - 0.5, 0.01, 1.0)          # σ for which the LSF is at half maximum 0.15 mm from the centre
close(M.s_q, sig_q, 1e-9, "σ from FWHM 0.30 mm by bisection"); close(value(p), f_level(sig_q, 0.5), 1e-7, "keyed f50 from the numerical MTF")
check("1.47 lp/mm" == keyed_text(p), "keyed option reads 1.47 lp/mm")
close(M.f50_q_fwhm, f_level(0.30, 0.5), 1e-7, "trap: FWHM used as σ"); close(M.f10_q, f_level(sig_q, 0.1), 1e-7, "trap: the 0.10 level")
close(M.f50_q_no2, bisect(lambda f: math.exp(-(math.pi * sig_q * f) ** 2) - 0.5, 0.0, 20.0), 1e-9, "trap: e^(−π²σ²f²), the 2 left out")
check(sorted(opts(p)) == sorted(["0.62 lp/mm", "1.47 lp/mm", "2.08 lp/mm", "2.68 lp/mm"]), f"Gaussian FWHM options {opts(p)}")

# ---- Nyquist frequency: the point about which sampled cosines fold
def folds_at(pitch, fn, eps=(0.013, 0.21, 0.37)):
    return all(abs(math.cos(2 * math.pi * (fn + e) * k * pitch) - math.cos(2 * math.pi * (fn - e) * k * pitch)) < 1e-9 for e in eps for k in range(400))
fold2 = bisect(lambda f: (1 / M.P2 - f) - f, 0.0, 1 / M.P2)                     # the frequency equal to its own fold partner f_s − f
close(M.fn2, fold2, 1e-12, "Nyquist frequency of a 0.20 mm pitch as the fixed point of folding"); check(folds_at(M.P2, fold2), "sampled cosines at f_N ± ε coincide for a 0.20 mm pitch")
check(not folds_at(M.P2, 1 / M.P2 / 4), "they do not coincide about a quarter of the sampling frequency")
shown(f"fN = 1 / (2 × 0.20 mm) = {fold2:.2f} lp/mm", "Nyquist step"); shown(f"1/Δ = {1 / M.P2:.1f} lp/mm", "sampling frequency")

# ---- aliases: the sampled values themselves, and a DFT peak search over 0 to f_N
def samples(f, pitch, k=200): return [math.cos(2 * math.pi * f * i * pitch) for i in range(k)]
def dft_peak(f, pitch, k=200, step=0.0025):
    s = samples(f, pitch, k); fn = 1 / (2 * pitch); best = (0.0, -1.0)
    for j in range(int(round(fn / step)) + 1):
        g = j * step; mag = abs(sum(v * cmath.exp(-2j * math.pi * g * i * pitch) for i, v in enumerate(s)))
        if mag > best[1]: best = (g, mag)
    return best[0]
a2 = dft_peak(M.F2, M.P2)
close(M.al2, a2, 1e-9, "3.5 lp/mm at a 0.20 mm pitch peaks at 1.5 lp/mm"); check(max(abs(x - y) for x, y in zip(samples(M.F2, M.P2), samples(a2, M.P2))) < 1e-9, "the samples of 3.5 and 1.5 lp/mm are identical")
shown(f"2fN − f = {1 / M.P2:.1f} − 3.5 = {a2:.1f} lp/mm", "alias step"); shown(f"appears at {a2:.1f} lp/mm, with a period of {1 / a2:.2f} mm in place of {1 / M.F2:.2f} mm", "alias answer")
p = prob("pattern frequency = 1.75 lp/mm")
a5 = dft_peak(1.75, 0.40)
close(value(p), a5, 1e-9, "keyed alias of 1.75 lp/mm at a 0.40 mm pitch"); check(keyed_text(p) == "0.75 lp/mm", "keyed option 0.75 lp/mm")
check(max(abs(x - y) for x, y in zip(samples(1.75, 0.40), samples(0.50, 0.40))) > 0.5, "trap 0.50 lp/mm (f − f_N) gives different samples")
check(max(abs(x - y) for x, y in zip(samples(1.75, 0.40), samples(1.25, 0.40))) > 0.5, "trap 1.25 lp/mm (f_N) gives different samples")
check(sorted(opts(p)) == sorted(["0.50 lp/mm", "0.75 lp/mm", "1.25 lp/mm", "1.75 lp/mm"]), f"alias options {opts(p)}")
p = prob("pixel pitch = 0.125 mm")
fn4 = bisect(lambda f: (1 / 0.125 - f) - f, 0.0, 8.0)
close(value(p), fn4, 1e-12, "Nyquist frequency of a 0.125 mm pitch"); check(folds_at(0.125, fn4), "folding about 4 lp/mm at a 0.125 mm pitch")
check(opts(p) == ["0.4 lp/mm", "2 lp/mm", "4 lp/mm", "8 lp/mm"] and keyed_text(p) == "4 lp/mm", f"Nyquist options include the sampling frequency 1/Δ = 8 lp/mm {opts(p)}")

# ---- aperture MTF: integrate the rectangle
ap_num = lambda f, a: abs(simpson(lambda x: math.cos(2 * math.pi * f * x), -a / 2, a / 2)) / a
close(M.ap2, ap_num(M.F2, M.P2), 1e-9, "aperture MTF of 0.20 mm at 3.5 lp/mm"); shown(f"= {ap_num(M.F2, M.P2):.2f} of the modulation", "aperture step")
close(ap_num(1 / (2 * 0.3), 0.3), 2 / math.pi, 1e-9, "aperture MTF at f_N with a = Δ is 2/π"); shown(f"{ap_num(0.5, 1.0):.2f} at fN when a = Δ", "0.64 in the equation")

# ---- cascade: the product through logarithms
p = prob("Three stages blur a radiograph")
close(value(p), prod_log(0.90, 0.55, 0.80), 1e-12, "system MTF 0.90 × 0.55 × 0.80"); check(keyed_text(p) == "0.40", "keyed system MTF reads 0.40")
check(sorted(opts(p)) == ["0.25", "0.40", "0.55", "0.75"], f"cascade options {opts(p)}"); check(prod_log(0.90, 0.55, 0.80) < min(0.90, 0.55, 0.80), "below the weakest stage")
shown(f"= {prod_log(0.90, 0.55, 0.80):.3f}", "product in the explanation", plain(p["a"][1]))
g1, g2 = 0.08, 0.06                                                              # two Gaussian blurs (mm): the product of their numerical MTFs is the MTF of their convolution
conv = gauss(math.hypot(g1, g2))
close(mtf_num(gauss(g1), 2.0, 1.0) * mtf_num(gauss(g2), 2.0, 1.0), mtf_num(conv, 2.0, 1.0), 1e-9, "MTFs of convolved blurs multiply")

# ---- CNR in exact fractions
p = prob("mean in the object = 520")
close(value(p), float(Fr(520 - 480, 16)), 1e-12, "CNR = 40/16"); shown(f"gives {float(Fr(40, 256)):.2f}", "variance trap", plain(p["a"][1])); shown(f"the contrast, {float(Fr(40, 480)):.3f}", "contrast trap", plain(p["a"][1]))
check(abs(float(Fr(40, 256)) / value(p) - 1) > p["tol"], "the variance trap lies outside the tolerance")

# ---- DQE worked example: exact fractions, and a bisection for the fluence an ideal detector needs (its NNPS is 1/q)
q3 = Fr(25, 10) * 30000; neq3 = Fr(62, 100) ** 2 / Fr(114, 10 ** 7)
close(M.q3, float(q3), 1e-12, "q = 2.5 µGy × 30,000"); close(M.neq3, float(neq3), 1e-12, "NEQ = MTF²/NNPS in fractions")
q_ideal = bisect(lambda q: 1 / q - 1.14e-5 / 0.62 ** 2, 1.0, 1e7)               # an ideal detector with NNPS = 1/q matches MTF²/NNPS at this fluence
close(M.dqe3, q_ideal / float(q3), 1e-9, "DQE as the fraction of the photons an ideal detector would need")
shown(f"= {float(q3):,.0f} photons/mm²", "q printed"); shown(f"= {float(neq3):,.0f} photons/mm²", "NEQ printed in the step"); shown(f"NEQ ≈ {round(float(neq3), -2):,.0f} photons/mm² and DQE = {q_ideal / float(q3):.2f}", "answer")
shown(f"with {100 * q_ideal / float(q3):.0f}% of the photons", "share of the photons"); shown(f"{0.62 ** 2:.4f} / (1.14 × 10−5 mm²)", "MTF² step")

# ---- DQE typed question
p = prob("NNPS(2.0 lp/mm) = 4.5")
q14 = Fr(4) * 30000; d14 = Fr(40, 100) ** 2 / (q14 * Fr(45, 10 ** 7))
close(value(p), float(d14), 1e-12, "typed DQE in fractions"); close(value(p), bisect(lambda q: 1 / q - 4.5e-6 / 0.16, 1.0, 1e7) / float(q14), 1e-9, "typed DQE by the ideal-detector bisection")
check(abs(float(Fr(40, 100) / (q14 * Fr(45, 10 ** 7))) / value(p) - 1) > p["tol"], "the unsquared MTF lies outside the tolerance")
shown(f"= {float(q14):,.0f} photons/mm²", "q in the explanation", plain(p["a"][1])); shown(f"{0.16:.2f} / {float(q14 * Fr(45, 10 ** 7)):.2f} = {float(d14):.2f}", "DQE step", plain(p["a"][1]))
shown(f"gives {float(Fr(40, 100) / (q14 * Fr(45, 10 ** 7))):.2f}", "unsquared trap", plain(p["a"][1]))

# ---- DQE of 0.50: the SNR ratio
p = prob("A detector has a DQE of 0.50")
check(keyed_text(p).startswith(f"Its SNR is {sqrt_newton(0.5):.2f} of the ideal; twice the exposure"), "keyed DQE meaning: SNR 0.71, twice the exposure")
close(bisect(lambda x: x * 0.5 - 1.0, 0.1, 10.0), 2.0, 1e-12, "twice the exposure restores SNR² by a factor of 2")
shown(f"√0.5 = {sqrt_newton(0.5):.2f} of the ideal", "0.71 in the text")

# ---- edge enhancement: H = 2 scales MTF² and NPS by 4
mtf2, nps2 = 0.20, 3.0e-6
close((2 * mtf2) ** 2 / (4 * nps2), mtf2 ** 2 / nps2, 1e-12, "NEQ unchanged by a gain of 2")
check(keyed_text(prob("doubles the MTF")).startswith("It is unchanged"), "keyed: unchanged")

# ---- exposure for 20% less relative noise: bisection on 1/√x
p = prob("must fall by 20%")
close(value(p), bisect(lambda x: 1 / sqrt_newton(x) - 0.80, 1.0, 4.0), 1e-9, "exposure factor for 20% less noise"); check(keyed_text(p) == "1.56", "keyed 1.56")
check(sorted(opts(p)) == ["0.64", "1.12", "1.25", "1.56"], f"noise options {opts(p)}")

# ---- equal SNR with a lower DQE: bisection on √(K × DQE)
p = prob("Detector A gives the required SNR at 2.5")
kb = bisect(lambda k: sqrt_newton(k * 0.25) - sqrt_newton(2.5 * 0.60), 0.1, 50.0)
close(value(p), kb, 1e-9, "air kerma for B"); check(keyed_text(p) == "6.0 µGy", "keyed 6.0 µGy")
check(sorted(opts(p), key=lambda s: float(s.split()[0])) == ["1.0 µGy", "3.9 µGy", "6.0 µGy", "14.4 µGy"], f"equal-SNR options {opts(p)}")
kb4 = bisect(lambda k: sqrt_newton(k * 0.30) - sqrt_newton(2.0 * 0.65), 0.1, 50.0)
close(M.kb4, kb4, 1e-9, "worked example: air kerma for B"); shown(f"= {kb4:.2f} µGy", "4.33 µGy step"); shown(f"{kb4:.1f} µGy for B, {kb4 / 2.0:.2f} times", "answer")
r4 = sqrt_newton(1.0 * 0.65) / sqrt_newton(2.0 * 0.65)
shown(f"= {r4:.3f}", "SNR ratio after halving"); shown(f"lowers its SNR by {100 * (1 - r4):.0f}%", "29% lower")

# ---- Rose: SNR = C√(qA); half the diameter
area = lambda d: math.pi * d * d / 4
k_rose = bisect(lambda k: 0.02 * sqrt_newton(k * 1e4 * area(0.5)) - 0.02 * sqrt_newton(1e4 * area(1.0)), 0.5, 50.0)
close(k_rose, 4.0, 1e-9, "four times the fluence for half the diameter"); check(keyed_text(prob("at the limit of detection")).startswith("Four times the fluence"), "keyed four times")

# ---- half the pixel width: photons per pixel and SNR
n_px = lambda w, q: q * w * w
close(sqrt_newton(n_px(0.05, 1e5)) / sqrt_newton(n_px(0.10, 1e5)), 0.5, 1e-12, "SNR per pixel halves with half the width")
close(bisect(lambda k: sqrt_newton(n_px(0.05, k * 1e5)) - sqrt_newton(n_px(0.10, 1e5)), 0.5, 50.0), 4.0, 1e-9, "four times the exposure restores it")
check(keyed_text(prob("half the pixel width")).startswith("It halves; four times"), "keyed: halves, four times")

# ---- take-away and card values that repeat the text
shown("0.6 to 0.8", "kV panel DQE(0) range in the text"); shown("about 0.01", "MV portal imager DQE(0) in the text")
shown("0.6 to 0.8", "kV panel range in the take-away", TAKE); shown("about 0.01", "MV imager in the take-away", TAKE)

# ---- every numeric question has distinct options
for q in TOP["problems"]:
    if q.get("vals"): check(len(set(round(v, 9) for v in q["vals"])) == len(q["vals"]) and len(set(opts(q))) == len(q["vals"]), f"distinct options: {plain(q['q'])[:40]}")

for b in bad: print("FAIL", b)
print(f"numbers_image_metrics: {n} numbers re-derived"); print("numbers_image_metrics: PASS" if not bad else f"numbers_image_metrics: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
