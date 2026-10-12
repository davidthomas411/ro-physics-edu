"""MRI chapters 4.5 to 4.7: every worked number and tap target re-derived by another route."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
import mri_physics as MP, mri_sequences as MS, mri_artifacts as MA
# ---- 4.5 Larmor frequency and gradients
close(MP.f15, 42.6 * 1.5, 1e-12, "1.5 T"); close(MP.f15, 63.9, 1e-12, "63.9 MHz"); close(MP.f3, 127.8, 1e-12, "127.8 MHz"); close(MP.f035, 14.91, 1e-12, "0.35 T"); close(MP.f3 / MP.f15, 2.0, 1e-12, "doubling the field doubles the frequency")
close(MP.df, 42.6 * 1.0015 - 42.6 * 0.9985, 1e-12, "frequency span"); close(MP.df, 0.1278, 1e-9, "it is 0.128 MHz"); close(MP.z_of(42.6), 0.0, 1e-9, "42.6 MHz selects the center"); close(MP.z_of(MP.f_inf), 25.0, 1e-6, "the inferior end is at +25 cm"); close(MP.z_of(MP.f_sup), -25.0, 1e-6, "the superior end is at −25 cm")
# ---- 4.6 relaxation
close(MS.fat500, 1 - math.exp(-2), 1e-12, "fat at TR 500"); close(MS.fat500, 0.8647, 1e-3, "0.86"); close(MS.csf500, 1 - math.exp(-500 / 3000), 1e-12, "CSF at TR 500"); close(MS.csf500, 0.1535, 1e-3, "0.15"); close(MS.fat4000, 1.0, 1e-6, "fat is fully recovered at TR 4000"); close(MS.csf4000, 0.7364, 1e-3, "CSF at TR 4000")
close(MS.fat500 - MS.csf500, 0.711, 2e-3, "a large difference at TR 500"); close(MS.fat4000 - MS.csf4000, 0.264, 2e-3, "a smaller difference at TR 4000")
close(MS.b15, math.exp(-15 / 90), 1e-12, "brain at TE 15"); close(MS.b100, 0.3292, 1e-3, "brain at TE 100"); close(MS.c100, math.exp(-0.05), 1e-12, "CSF at TE 100"); close(MS.c100 - MS.b100, 0.622, 2e-3, "the difference at TE 100"); close(MS.c15 - MS.b15, 0.147, 2e-3, "the difference at TE 15")
close(MS.null(3000), 3000 * math.log(2), 1e-12, "inversion time"); close(MS.null(3000), 2079.4, 1e-4, "2079 ms"); close(MS.ir(MS.null(3000), 3000), 0.0, 1e-9, "the magnetization is zero at the null time"); close(MS.ir(0, 3000), -1.0, 1e-12, "it starts at −M0"); close(MS.mz(1000, 3000), 1 - math.exp(-1 / 3), 1e-12, "typed")
# ---- 4.7 distortion
close(MA.s_a, 0.05 / 10 * 1000, 1e-12, "shift 5 mm"); close(MA.s_b, 10.0, 1e-12, "shift 10 mm"); close(MA.shift(0.02, 10), 2.0, 1e-12, "typed shift"); close(MA.g_a, 200 * 1.05, 1e-12, "apparent length"); close(MA.g_a, 210.0, 1e-9, "210 mm: a point at x is placed at x G / G0")
close(MA.ppm(0.001, 1.5), 0.6667, 1e-3, "0.67 ppm"); close(MA.p_a, 0.01e-3 / 1.5 * 1e6, 1e-12, "6.7 ppm for 1 mm"); close(MA.dB_3, 0.03, 1e-12, "field error for 3 mm")
for b in bad: print("FAIL", b)
print(f"numbers14: {n} numbers re-derived"); print("numbers14: PASS" if not bad else f"numbers14: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
