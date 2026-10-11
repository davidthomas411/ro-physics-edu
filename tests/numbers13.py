"""Imaging chapters 4.1 to 4.4: every worked number and tap target re-derived by another route."""
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
def fig(t, phrase): return next(p for p in t["problems"] if p.get("kind") == "fig" and phrase in plain(p["q"]))
inside = lambda p, x: any((a is None or x >= a) and (b is None or x <= b) for a, b, _, _ in p["targets"])
import radiographic_quality as RQ, image_data as ID, ct_reconstruction as CR, ct_quality as CQ
# ---- 4.1 radiographic quality: contrast from the NIST tables, magnification, blur, SNR
for E, tab in ((0.03, None), (0.05, None), (0.1, None), (1.25, None)):
    mu_b, mu_w = N.BONE[E][0] * 1.92, N.WATER[E][0]; I_w = math.exp(-mu_w * 10); I_b = math.exp(-mu_w * 8 - mu_b * 2)
    close(RQ.ratio_bone(E), I_w / I_b, 1e-12, f"contrast ratio at {E} MeV, from the two transmissions")
close(RQ.r30, 78.3, 0.005, "30 keV contrast is 78"); close(RQ.r50, 3.24, 0.005, "50 keV contrast is 3.2"); close(RQ.r125, 1.10, 0.005, "1.25 MeV contrast is 1.10"); close(1 if RQ.r30 > RQ.r50 > RQ.r100 > RQ.r125 > 1 else 0, 1, 0, "the contrast falls with energy")
close(RQ.m_a, 100 / 90, 1e-12, "magnification 1.11"); close(RQ.b_a, 1.0 * 10 / 90, 1e-12, "blur 0.11 mm"); close(RQ.m_b, 100 / 70, 1e-12, "magnification 1.43"); close(RQ.b_b, 30 / 70, 1e-12, "blur 0.43 mm")
close(1 if RQ.m_b > RQ.m_a and RQ.b_b > RQ.b_a else 0, 1, 0, "moving the object away raises both the magnification and the blur")
close(RQ.snr(10000), 100.0, 1e-12, "SNR 100"); close(RQ.snr(40000) / RQ.snr(10000), 2.0, 1e-12, "four times the photons doubles the SNR"); close(RQ.npix(5), 10000, 0, "10,000 photons at 5 mAs")
close(RQ.skin(60, 16), 57600, 0, "skin exposure of the 60 kVp technique"); close(1 if RQ.skin(60, 16) < min(RQ.skin(80, 10), RQ.skin(100, 8), RQ.skin(120, 5)) else 0, 1, 0, "it is the lowest")
p = fig(T["radiographic-quality"], "magnification is 1.25"); s = p["spec"]["series"][0]["pts"]; xb = min(s, key=lambda q: abs(q[1] - 1.25))[0]
close(xb, 20.0, 0.02, "the magnification is 1.25 at 20 cm"); close(1 if inside(p, 20) and not inside(p, 10) and not inside(p, 30) else 0, 1, 0, "the magnification target holds 20 cm and rejects 10 and 30")
# ---- 4.2 digital images
close(ID.levels(4), 16, 0, "4 bits"); close(ID.levels(8), 256, 0, "8 bits"); close(ID.levels(16), 65536, 0, "16 bits")
close(ID.s_ct, 1024 * 1024 * 2, 0, "a 1024 x 1024 image at 16 bits"); close(ID.mb(ID.s_ct), 2.097152, 1e-9, "2.1 MB"); close(ID.s_512, 524288, 0, "512 x 512 x 2"); close(ID.mb(ID.study(200)), 104.8576, 1e-9, "a 200-slice study")
close(ID.px(50, 512), 500 / 512, 1e-12, "pixel size 0.98 mm"); close(ID.px(25, 128), 1.953125, 1e-9, "25 cm over 128 pixels"); close(ID.px(80, 1024), 0.78125, 1e-9, "80 cm over 1024 pixels"); close(min(ID.px(25, 128), ID.px(50, 512), ID.px(50, 256), ID.px(80, 1024)), ID.px(80, 1024), 1e-12, "the smallest pixel is the 80 cm field on 1024 pixels")
close(ID.mb(ID.s_rad), 10.0, 1e-12, "a 2000 x 2500 radiograph at 16 bits is 10 MB"); close(2 ** 10, 1024, 0, "10 bits give 1024 levels")
p = fig(T["image-data"], "1024 grayscale levels"); s = p["spec"]["series"][0]["pts"]; xn = min(s, key=lambda q: abs(q[1] - 1024))[0]
close(xn, 10.0, 0.02, "the curve reaches 1024 at 10 bits"); close(1 if inside(p, 10) and not inside(p, 8) and not inside(p, 11.5) else 0, 1, 0, "the bit-depth target holds 10 and rejects 8 and 11.5")
# ---- 4.3 Hounsfield units
close(CR.hu_a, 1000 * (1.1 * 0.19 - 0.19) / 0.19, 1e-9, "HU of a 10% larger μ"); close(CR.hu_a, 100.0, 1e-6, "it is +100"); close(CR.hu_b, -250.0, 1e-6, "HU of a 25% smaller μ"); close(CR.mu_of(1000, 0.19), 0.38, 1e-12, "μ at +1000 HU"); close(CR.mu_of(-500, 0.19), 0.095, 1e-12, "μ at −500 HU"); close(CR.hu_t, 140.0, 1e-9, "typed HU 140")
close(CR.hu(0.19, 0.19), 0.0, 1e-12, "water is 0 HU"); close(CR.hu(0.0, 0.19), -1000.0, 1e-12, "air is −1000 HU"); close(CR.mu_of(CR.hu(0.3, 0.19), 0.19), 0.3, 1e-12, "HU and μ convert back and forth")
p = fig(T["ct-reconstruction"], "HU is +250"); s = p["spec"]["series"][0]["pts"]; xr = min(s, key=lambda q: abs(q[1] - 250))[0]
close(xr, 1.25, 0.01, "the HU is +250 at a relative attenuation of 1.25"); close(1 if inside(p, 1.25) and not inside(p, 1.0) and not inside(p, 1.5) else 0, 1, 0, "the HU target holds 1.25 and rejects 1.0 and 1.5")
# ---- 4.4 CT acquisition and quality
close(CQ.pitch(15, 10), 1.5, 1e-12, "pitch 1.5"); close(CQ.pitch(12, 8), 1.5, 1e-12, "typed pitch"); close(CQ.t_p1, 200 / 5 * 0.5, 1e-12, "scan time at pitch 1.0 is 20 s"); close(CQ.t_p15, 200 / 7.5 * 0.5, 1e-12, "scan time at pitch 1.5 is 13.3 s"); close(CQ.t_p15, 13.3333, 1e-4, "it is 13.3 s")
close(CQ.noise(100, 5), math.sqrt(2), 1e-12, "relative noise 1.41"); close(CQ.noise(100, 2.5), 2.0, 1e-12, "relative noise 2.0 for 2.5 mm"); close(CQ.noise(100, 10), 1.0, 1e-12, "relative noise 1.0 for 10 mm"); close(CQ.noise(400, 5) / CQ.noise(100, 5), 0.5, 1e-12, "four times the mAs halves the noise")
p = fig(T["ct-quality"], "scan takes 10 s"); s = p["spec"]["series"][0]["pts"]; xp = min(s, key=lambda q: abs(q[1] - 10))[0]
close(xp, 2.0, 0.02, "the scan takes 10 s at pitch 2.0"); close(1 if inside(p, 2.0) and not inside(p, 1.5) and not inside(p, 2.5) else 0, 1, 0, "the pitch target holds 2.0 and rejects 1.5 and 2.5")
for b in bad: print("FAIL", b)
print(f"numbers13: {n} numbers re-derived"); print("numbers13: PASS" if not bad else f"numbers13: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
