"""Numbers added in answer to the audit against the ROECSG study guide (mri safety, radiography, CT, PET, decay, photons, kerma, electrons, FFF, low dose rate BED):
every worked number and numeric answer re-derived by another route."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import nistdata as N, real
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def prob(tid, phrase):
    hits = [p for p in T[tid]["problems"] if phrase in plain(p["q"])]; assert len(hits) == 1, (tid, phrase, len(hits)); return hits[0]
def value(p):                                                                  # the number behind the keyed option of a numeric choice, or the answer of a typed question
    return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b):
    for _ in range(200):
        m = (a + b) / 2
        if f(a) * f(m) <= 0: b = m
        else: a = m
    return (a + b) / 2
LN2 = math.log(2)

# ---- MRI safety: SAR is power per mass; it rises with the square of the field
close(value(prob("mri-physics", "105 W of RF power")), 105 / 70, 1e-12, "SAR of 105 W in 70 kg")
import mri_physics as MP
close(MP.s_ex, 150 / 60, 1e-12, "worked example: 150 W in 60 kg is 2.5 W/kg, above the 2 W/kg limit"); close(1 if MP.s_ex > 2 > value(prob("mri-physics", "105 W of RF power")) else 0, 1, 0, "the example is above the limit and the problem is below it")
close((3.0 / 1.5) ** 2, 4.0, 1e-12, "SAR at 3 T against 1.5 T goes as the field squared")

# ---- CT: patient size, and the real phantom
mu = 0.19; extra = 8
photons = lambda mas, d: mas * math.exp(-mu * d)                              # photons at the detector for a thickness d
need = bisect(lambda m: photons(m, 24 + extra) - photons(150, 24), 1, 5000)
close(value(prob("ct-quality", "8 cm thicker")), need, 1e-6, "mAs for an 8 cm thicker patient, solved from equal photon counts"); close(need, 686, 2e-3, "about 686 mAs")
close(photons(2.0, math.log(2) / mu) / photons(1.0, 0.0) * 1.0, 1.0, 1e-12, "doubling the mAs offsets ln 2 / mu of extra thickness"); close(math.log(2) / mu, 3.65, 5e-3, "3.6 cm doubles the mAs")
RN = real.STATS["ct"]["noise"]; sd_a, sd_b = round(RN["sd"][0], 1), round(RN["sd"][2], 1)
close(value(prob("ct-quality", "uniform block in a test phantom")), RN["mA"][0] * (sd_a / sd_b) ** 2, 1e-12, "tube current for the lower noise")
close(RN["sd"][0] * math.sqrt(RN["mA"][0] / RN["mA"][2]), RN["sd"][2], 0.02, "the measured noise at 200 mA follows 1/sqrt(mA) from the 50 mA value within 2%")
close(abs(value(prob("ct-quality", "uniform block in a test phantom")) - RN["mA"][2]) / RN["mA"][2], 0.0, 0.03, "the predicted current is within 3% of the 200 mA used")

# ---- radiography: distance and the mAs
d_ratio = lambda m: m / 140 ** 2 - 20 / 100 ** 2                                # equal exposure at the film: mAs / d^2
close(value(prob("radiographic-quality", "100 cm with 20 mAs")), bisect(d_ratio, 1, 500), 1e-9, "mAs at 140 cm"); close(value(prob("radiographic-quality", "100 cm with 20 mAs")), 39.2, 1e-9, "39.2 mAs")

# ---- PET: SUV with the injected activity decayed to the scan
a_scan = 370 * math.exp(-LN2 / 109.8 * 60)                                      # MBq at the scan
close(value(prob("pet-imaging", "decay-corrected")), 12 / (a_scan * 1000 / 75000), 1e-9, "SUV with decay"); close(value(prob("pet-imaging", "decay-corrected")), 3.55, 3e-3, "3.55")
close(12 / (370 * 1000 / 75000), 2.432, 1e-3, "without the decay the SUV would be 2.43")

# ---- decay: the time at which two sources have the same activity, solved numerically
lx, ly = LN2 / 12, LN2 / 40
t_eq = bisect(lambda t: 9.0 * math.exp(-lx * t) - 2.5 * math.exp(-ly * t), 0, 500)
close(value(prob("decay-law", "same activity")), t_eq, 1e-9, "time of equal activity"); close(t_eq, 31.68, 1e-3, "31.7 d")
close(1 - math.exp(-LN2 / 10 * 10), 0.5, 1e-12, "the chance of decay in any one half-life is 50%")

# ---- photon interactions: the barrier with a build-up factor, and the contrast ratio per gram
mu_pb = LN2 / 0.80
x_b = bisect(lambda x: 2.0 * math.exp(-mu_pb * x) - 0.010, 0, 50)
close(value(prob("photon-interactions", "build-up factor of 2.0")), x_b, 1e-9, "barrier thickness with build-up"); close(x_b, 6.115, 1e-3, "6.1 cm")
close(0.80 * math.log2(100), 5.315, 1e-3, "narrow beam value")
close(N.BONE[0.05][0] / N.WATER[0.05][0], 1.87, 5e-3, "bone against water per gram at 50 keV: about 1.9"); close(N.BONE[0.1][0] / N.WATER[0.1][0], 1.09, 5e-3, "and at 100 keV: about 1.1")
def kn(E):                                                                      # Klein-Nishina cross section per electron in cm^2
    k = E / 511.0; re_ = 2.8179403e-13
    return 2 * math.pi * re_ ** 2 * ((1 + k) / k ** 2 * (2 * (1 + k) / (1 + 2 * k) - math.log(1 + 2 * k) / k) + math.log(1 + 2 * k) / (2 * k) - (1 + 3 * k) / (1 + 2 * k) ** 2)
share = kn(50) * (10 / 18.015) * 6.02214076e23 / N.WATER[0.05][0]               # Compton share of the attenuation in water at 50 keV, free electrons
close(1 if 0.75 < share < 0.90 else 0, 1, 0, f"Compton is roughly 80% of the attenuation in water at 50 keV ({share:.2f})")

# ---- kerma: dose to muscle from exposure
d_air = 30 * 2.58e-4 * 33.97 * 100                                              # cGy: exposure in C/kg times W/e in J/C
close(d_air, 30 * 0.876, 2e-3, "30 R is 26.3 cGy in air by the charge route"); close(value(prob("kerma-dose", "dose to muscle")), d_air * 0.0296 / 0.0267, 2e-3, "dose to muscle"); close(value(prob("kerma-dose", "dose to muscle")), 29.1, 2e-3, "29.1 cGy")

# ---- charges: the energy gained across a gap
e_ch = 1.602176634e-19
close(e_ch * (8.0e6 * 0.025) / e_ch / 1e3, 200.0, 1e-9, "a 2.5 cm gap at 8.0 MV/m: 200 kV"); close(value(prob("charges-atom", "2.5 cm along a uniform")), 200.0, 1e-9, "keyed value is 200 keV")

# ---- electrons: bolus and the surface dose
import electron_pdd as EP
close(value(prob("electron-fields", "1.5 cm of tissue-equivalent bolus")), EP.r90(12) - 1.5, 1e-12, "R90 under 1.5 cm of bolus"); close(EP.r90(12) - 1.5, 2.136, 1e-3, "2.1 cm")
close(EP.r90(9) - 1.0, 1.727, 1e-3, "worked example: 9 MeV with 1.0 cm of bolus"); close(1 if EP.r90(9) - 1.0 < 2.4 < EP.r90(12) - 1.0 else 0, 1, 0, "9 MeV falls short of 2.4 cm and 12 MeV reaches it")
close(value(prob("electron-fields", "bolus is left out")), 100 * sum((0.80 if k == 0 else 1.0) for k in range(20)) / 20 * -1 + 100, 1e-9, "one of 20 fractions at 80% of the surface dose: 1.0% short")

# ---- flattening-filter-free beams: beam-on times
close(value(prob("profiles", "2400 MU")), 2400 / 600 - 2400 / 1400, 1e-12, "time saved with 2400 MU"); close(value(prob("profiles", "2400 MU")), 2.286, 1e-3, "2.3 min")
close(2000 / 600 - 2000 / 1400, 1.905, 1e-3, "worked example: 2000 MU, 3.3 min against 1.4 min")

# ---- continuous low dose rate irradiation: the closed form against the Lea-Catcheside double integral
mu_r = LN2 / 1.5
def bed_numeric(R, T, ab, steps=4000):
    h = T / steps; inner = 0.0; acc = 0.0                                     # G D^2 / 2 = integral of R(t) * integral of R(s) exp(-mu (t - s)) ds dt, by a running sum
    for i in range(steps):
        inner = inner * math.exp(-mu_r * h) + R * h                           # damage left from earlier dose, with repair
        acc += R * h * inner
    D = R * T; GD2 = 2 * acc
    return D + GD2 / ab
close(bed_numeric(0.50, 72, 10), 43.56, 5e-3, "worked example by numerical integration"); close(bed_numeric(0.60, 60, 3), value(prob("bed-tcp", "0.60 Gy/h for 60 h")), 5e-3, "low dose rate BED of the late-responding tissue")
close(value(prob("bed-tcp", "0.60 Gy/h for 60 h")), 66.0, 2e-3, "66.0 Gy")
close(bed_numeric(0.60, 60, 10), 45.0, 5e-3, "the tumour value used as a decoy"); close(bed_numeric(0.60, 60, 3), 36 * (1 + 0.8658 * 0.964), 5e-3, "the bracket")
close(1 if bed_numeric(0.60, 60, 3) - 36 > bed_numeric(0.60, 60, 10) - 36 > 0 else 0, 1, 0, "the repair term is larger for the low alpha/beta")
# ---- the T1 that the FLAIR inversion time of the real images nulls, quoted in the MRI sequences chapter
import mri_sequences as MS
fl = real.STATS["mr"]["params"]["flair"]
null_f = lambda t1: 1 - 2 * math.exp(-fl["ti"] / t1) + math.exp(-fl["tr"] / t1)
close(null_f(MS.T1_FLAIR), 0.0, 1e-9, "the quoted T1 makes the signal 1 - 2 exp(-TI/T1) + exp(-TR/T1) zero")
close(1 if 3800 < MS.T1_FLAIR < 4600 else 0, 1, 0, f"the nulled T1 is a CSF-like value near 4 s ({MS.T1_FLAIR:.0f} ms)")
first = next(t for t in range(100, 20000, 10) if null_f(t) < 0)                                  # the signal changes sign once, so a scan finds the same root
close(MS.T1_FLAIR, first, 3e-3, "a scan for the sign change gives the same T1")

for b in bad: print("FAIL", b)
print(f"numbers16: {n} numbers re-derived"); print("numbers16: PASS" if not bad else f"numbers16: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
