"""Nuclear imaging chapters 4.8 and 4.9: every worked number and tap target re-derived by another route."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
import nistdata as N
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
import spect as SP, pet_imaging as PI
# ---- 4.8: half-lives and the activity remaining, by the exponential form
lam = lambda th: math.log(2) / th
close(SP.tc12, math.exp(-lam(6.0) * 12), 1e-12, "99mTc after 12 h"); close(SP.tc12, 0.25, 1e-12, "it is one quarter"); close(SP.f18_220, math.exp(-lam(109.8) * 220), 1e-12, "18F after 220 min"); close(SP.f18_220, 0.2490, 1e-3, "0.249"); close(SP.tc3, math.exp(-lam(6.0) * 3), 1e-12, "99mTc after 3 h"); close(SP.tc3, 0.7071, 1e-4, "70.7%")
for k, th in (("F-18", 109.8), ("Ga-68", 67.6), ("C-11", 20.4), ("N-13", 9.97)): close(SP.r45[k], math.exp(-lam(th) * 45), 1e-12, f"{k} after 45 min")
close(1 if SP.r45["F-18"] > SP.r45["Ga-68"] > SP.r45["C-11"] > SP.r45["N-13"] else 0, 1, 0, "the longest half-life leaves the most activity")
close(SP.t30, math.log(1 / 0.3) / lam(6.0), 1e-12, "time to 30%"); close(SP.t30, 10.42, 1e-3, "10.4 h"); close(SP.HL["F-18"], 1.83, 1e-3, "F-18 half-life in hours"); close(SP.HL["I-131"], 8.01 * 24, 1e-12, "I-131 half-life in hours")
close(100 * SP.rem(6, SP.HL["F-18"]), 10.3, 0.01, "10% of F-18 remains after 6 h"); close(100 * SP.rem(6, SP.HL["I-123"]), 72.96, 1e-3, "73% of I-123"); close(100 * SP.rem(6, SP.HL["Ga-68"]), 2.4, 0.05, "2% of Ga-68")
# ---- 4.9: mu at 511 keV from the NIST water table, the correction factor, and SUV
w = N.WATER; mu_lin = w[0.5][0] + (w[0.6][0] - w[0.5][0]) * 0.11                       # a plain linear interpolation at 511 keV, as a rough check of the log-log value
close(PI.mu511, mu_lin, 2e-3, "mu at 511 keV agrees with a linear interpolation"); close(PI.mu511, 0.0960, 2e-3, "about 0.096 per cm")
close(PI.surv(20) * PI.acf(20), 1.0, 1e-12, "the escape probability and the correction factor are inverses"); close(PI.acf(20), math.exp(0.0960 * 20), 2e-3, "correction factor for 20 cm"); close(PI.acf(20), 6.82, 5e-3, "6.8"); close(100 * PI.surv(20), 14.66, 5e-3, "14.7%")
close(PI.surv(10) ** 2, PI.surv(20), 1e-12, "two 10 cm paths multiply to one 20 cm path"); close(PI.acf(PI.L_4), 4.0, 1e-9, "the correction factor is 4 at L_4"); close(PI.L_4, math.log(4) / PI.mu511, 1e-12, "L_4 = ln 4 / mu"); close(PI.L_4, 14.44, 5e-3, "14.4 cm")
close(PI.suv_a, 20 / (370000 / 74000), 1e-12, "SUV of the tumour"); close(PI.suv_a, 4.0, 1e-12, "it is 4.0"); close(PI.suv_t, 18 / (296000 / 80000), 1e-12, "typed SUV"); close(PI.suv_t, 4.8649, 1e-4, "4.86")
for b in bad: print("FAIL", b)
print(f"numbers15: {n} numbers re-derived"); print("numbers15: PASS" if not bad else f"numbers15: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
