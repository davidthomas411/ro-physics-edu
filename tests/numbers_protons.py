"""Proton and ion beam therapy: every number the chapter prints or keys, re-derived by another route.
Ranges by integrating the stopping power that the power law implies, energies by bisection, the PSTAR comparison by integrating the Bethe stopping power,
the depth-dose model by Bortfeld's closed form (parabolic cylinder functions from Kummer series) in place of the chapter's numerical convolution,
the magnetic rigidity from gamma and beta, and the SOBP weights by a second solver."""
import sys, re, math
from pathlib import Path
sys.path = [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent]
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
import protons as M
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; TP = T["protons"]; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
def true(c, what):
    global n; n += 1
    if not c: bad.append((what, False, True))
def prob(phrase):
    hits = [p for p in TP["problems"] if phrase in plain(p.get("stem0", p["q"]))]; assert len(hits) == 1, (phrase, len(hits)); return hits[0]
def value(p): return p["ans"] if p.get("kind") == "num" else p["vals"]["ABCDEFG".index(p["key"][0])]
def bisect(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2; fm = f(m)
        if (fm > 0) == (fa > 0): a, fa = m, fm
        else: b = m
    return (a + b) / 2
def simpson(f, a, b, k=2000):
    h = (b - a) / k
    return h / 3 * sum((1 if i in (0, k) else 4 if i % 2 else 2) * f(a + i * h) for i in range(k + 1))
text = " ".join(plain(b[1]) for b in TP["guide"] if b[0] == "p")
def says(s, what): true(s in text, f"the text says '{s}' ({what})")
A, PW = 0.0022, 1.77

# ---- the power law, by integrating dR/dE = alpha p E^(p-1), the inverse of the stopping power it implies
R_int = lambda e: simpson(lambda x: A * PW * x ** (PW - 1), 0.0, e)
for e, r, _ in M.TAB: close(r, R_int(e), 1e-7, f"range at {e} MeV")
rows = next(b for b in TP["guide"] if b[0] == "table")[2]
close(float(rows[0][1]), 4.06, 0, "table: 70 MeV gives 4.06 cm"); close(float(rows[1][1]), 15.6, 0, "table: 150 MeV gives 15.6 cm"); close(float(rows[2][1]), 33.3, 0, "table: 230 MeV gives 33.3 cm")
true(rows[0][2] == "4.08" and rows[1][2] == "15.8" and rows[2][2] == "about 33", f"table: PSTAR values {[r[2] for r in rows]}")
close(M.r100, R_int(100), 1e-7, "worked example: 100 MeV"); close(100 ** 1.77, 10 ** 3.54, 1e-12, "100^1.77 is 10^3.54")
close(round(M.r100, 2), 7.63, 0, "7.63 cm"); close(round(abs(M.d100), 1), round(100 * (1 - R_int(100) / 7.718), 1), 0, "1.2% short of PSTAR")

# ---- the PSTAR comparison: Bethe stopping power of water (I = 75 eV, as in PSTAR), integrated from the verified 150 MeV CSDA range
K, ZA, ME, MP, I = 0.307075, 10 / 18.01528, 0.51099895, 938.27209, 75e-6
def S_bethe(t):
    g = 1 + t / MP; b2 = 1 - 1 / g ** 2; bg2 = b2 * g * g; wmax = 2 * ME * bg2 / (1 + 2 * g * ME / MP + (ME / MP) ** 2)
    return K * ZA / b2 * (0.5 * math.log(2 * ME * bg2 * wmax / I ** 2) - b2)
dR = lambda a, b: simpson(lambda t: 1 / S_bethe(t), a, b, 1000)
close(dR(70, 100), 7.718 - 4.080, 2e-3, "Bethe range difference 70 to 100 MeV against PSTAR"); close(dR(100, 150), 15.77 - 7.718, 2e-3, "Bethe range difference 100 to 150 MeV against PSTAR")
c230, c250 = 15.77 + dR(150, 230), 15.77 + dR(150, 250)
true(32.91 <= c230 < 33.0 and round(c230) == 33, f"CSDA range at 230 MeV is about 33 g/cm2 ({c230:.3f}; the projected range is 32.91)")
true(round(c250) == 38, f"250 MeV reaches about 38 cm ({c250:.2f})")
dev = max(abs(R_int(e) / r - 1) for e, r in ((70, 4.080), (150, 15.77), (230, c230)))
close(round(100 * dev), 1, 0, f"the power law agrees with PSTAR to about 1% ({100 * dev:.2f}%)"); close(round(100 * M.dev), round(100 * dev), 0, "the chapter's figure")
says("agrees with PSTAR to about 1%", "power law against PSTAR"); says("about 4 cm to 33 to 38 cm", "clinical ranges")
close(round(4.080), 4, 0, "70 MeV reaches about 4 cm")

# ---- the depth-dose model by Bortfeld's closed form: D = s^(1/p) Gamma(1/p) e^(-zeta^2/4) / (sqrt(2 pi)(1 + beta R)) [D_(-1/p)(-zeta)/s + (k/p) D_(-1/p-1)(-zeta)]
def kummer(a, b, x):
    term, tot, k = 1.0, 1.0, 0
    while True:
        term *= (a + k) / (b + k) * x / (k + 1); tot += term; k += 1
        if abs(term) < 1e-17 * abs(tot) and k > 5: return tot
def pcf(nu, x):                                                                          # parabolic cylinder function D_nu(x) for nu < 0
    y = x * x / 2
    return 2 ** (nu / 2) * math.exp(-x * x / 4) * (math.sqrt(math.pi) / math.gamma((1 - nu) / 2) * kummer(-nu / 2, 0.5, y) - math.sqrt(2 * math.pi) * x / math.gamma(-nu / 2) * kummer((1 - nu) / 2, 1.5, y))
BN, GN = 0.012, 0.6; KN = BN + GN * BN * PW; q = 1 / PW
def sig(r):
    e = (r / A) ** q; return math.sqrt((0.012 * r ** 0.935) ** 2 + (0.01 * e * A * PW * e ** (PW - 1)) ** 2)
def unstraggled(a, r, s):                                                                # far before the end of range: f(a) + (s^2/2) f''(a)
    f = a ** (q - 1) + KN * a ** q; f2 = (q - 1) * (q - 2) * a ** (q - 3) + KN * q * (q - 1) * a ** (q - 2)
    return (f + s * s / 2 * f2) / (1 + BN * r)
def bortfeld(z, r):
    s = sig(r); zeta = (r - z) / s
    if zeta > 20: return unstraggled(r - z, r, s)
    if zeta < -6: return 0.0
    return s ** q * math.gamma(q) * math.exp(-zeta * zeta / 4) / (math.sqrt(2 * math.pi) * (1 + BN * r)) * (pcf(-q, -zeta) / s + KN / PW * pcf(-q - 1, -zeta))
for z in (0.0, 8.0, 14.0, 15.3, 15.6, 15.9, 16.2):
    close(M.pristine(z, M.R150), bortfeld(z, M.R150), 2e-4, f"numerical and closed-form pristine dose at {z} cm")
r0 = M.R150; gr = (math.sqrt(5) - 1) / 2; lo, hi = r0 - 0.8, r0
for _ in range(80):
    c, d = hi - gr * (hi - lo), lo + gr * (hi - lo)
    if bortfeld(c, r0) > bortfeld(d, r0): hi = d
    else: lo = c
ent_p = unstraggled(r0, r0, sig(r0)) / bortfeld((lo + hi) / 2, r0)
close(M.ENT_PRISTINE, ent_p, 2e-3, "entrance of the 150 MeV pristine peak against its maximum"); says(f"has {round(100 * ent_p)}% of its maximum dose", "pristine entrance")
sob = lambda z: sum(w * bortfeld(z, r) for r, w in zip(M.RS, M.WS))
ent_s = sum(w * unstraggled(r, r, sig(r)) for r, w in zip(M.RS, M.WS))
close(M.ENT_SOBP, ent_s, 2e-3, "entrance of the SOBP against its plateau"); says(f"has {round(100 * ent_s)}% of its plateau dose", "SOBP entrance")
p90 = bisect(lambda z: sob(z) - 0.9, r0 - 8.5, r0 - 5.5); d90 = bisect(lambda z: sob(z) - 0.9, r0 - 0.6, r0 + 0.4)
d80 = bisect(lambda z: sob(z) - 0.8, r0 - 0.6, r0 + 0.4); z01 = bisect(lambda z: sob(z) - 0.01, r0, r0 + 1.5)
for got, want, what in ((M.P90, p90, "proximal 90%"), (M.D90, d90, "distal 90%"), (M.D80, d80, "distal 80%"), (M.Z01, z01, "1% point")): close(got, want, 0.002 / max(1.0, want), f"{what} depth")
close(round(d90, 1) - round(p90, 1), 6.6, 1e-9, "modulation width 15.5 - 8.9 = 6.6 cm"); says(f"an SOBP {round(d90, 1) - round(p90, 1):.1f} cm wide", "SOBP width")
plat = [sob(z) for z in [r0 - 5.6 + 0.1 * i for i in range(53)]]
true(0.97 < min(plat) and max(plat) < 1.03, f"the plateau is flat within 3% ({min(plat):.3f} to {max(plat):.3f})")
e_d80 = bisect(lambda e: A * e ** PW - round(d80, 1), 50, 300); close(M.e_d80, e_d80, 1e-9, "energy of the deepest peak from the 80% depth"); close(round(e_d80), 150, 0, "150 MeV")
# a second solver: multiplicative updates on the same peaks give the same entrance dose
grid = [r0 - 6.0 + 5.8 * i / 59 for i in range(60)]; Mx = [[M.pristine(z, r) for r in M.RS] for z in grid]; w = [1.0] * len(M.RS)
for _ in range(1500):
    tot = [sum(m[k] * w[k] for k in range(len(w))) for m in Mx]
    w = [w[k] * sum(m[k] for m in Mx) / sum(m[k] * t for m, t in zip(Mx, tot)) for k in range(len(w))]
mean = sum(sum(m[k] * w[k] for k in range(len(w))) for m in Mx) / len(Mx)
ent2 = sum(wk * M.pristine(0.0, r) for r, wk in zip(M.RS, w)) / mean
true(abs(ent2 - M.ENT_SOBP) < 0.015, f"a second solver gives the same SOBP entrance dose ({ent2:.3f} against {M.ENT_SOBP:.3f})")

# ---- range uncertainty and planning
w3 = math.fsum(t * s for t, s in [(3.0, 1.04), (1.5, 1.60), (6.0, 1.04)]); close(M.w3, w3, 1e-12, "worked example: WEPL"); close(w3, 11.76, 1e-12, "11.76 cm")
need = 1.035 * w3 + 0.1; close(M.w3 + M.m3, need, 1e-12, "range with the margin")
e3 = bisect(lambda e: A * e ** PW - need, 50, 300); close(M.e3, e3, 1e-9, "worked example: energy"); close(round(e3), 131, 0, "about 131 MeV")
close(value(prob("crosses three layers before the target")), math.fsum([4.0 * 1.04, 1.5 * 1.60, 6.0 * 0.25]), 1e-12, "WEPL with lung")
close(value(prob("WEPL of 24.0 cm")), (24.0 * 1.035 + 0.1 - 24.0) * 10, 1e-9, "distal margin at 24 cm"); close(value(prob("WEPL of 24.0 cm")), 9.4, 1e-9, "9.4 mm")
close(value(prob("has a range of 15.6 cm")), math.exp(math.log(15.6) + 1.77 * math.log(0.8)), 1e-12, "scaling 150 MeV to 120 MeV"); close(round(value(prob("has a range of 15.6 cm")), 1), 10.5, 0, "10.5 cm")
true(prob("has a range of 15.6 cm")["opts"] == ["10.0 cm", "10.5 cm", "12.5 cm", "13.8 cm"], "scaling options")
close(R_int(150), 15.635, 1e-4, "card and take-away: 150 MeV reaches 15.6 cm"); close(0.035 * 200 + 1, 8.0, 1e-12, "card: 20 cm range gives an 8 mm margin")

# ---- biological effect
close(M.phys_fx * 30, 54 / 1.1, 1e-12, "worked example: 30 fractions of the physical dose"); close(round(M.phys_fx, 2), 1.64, 0, "1.64 Gy per fraction"); close(round(M.phys_tot, 1), 49.1, 0, "49.1 Gy in total")
close(value(prob("70 Gy(RBE) in 35 fractions")) * 35 * 1.1, 70.0, 1e-12, "physical dose per fraction for 70 Gy(RBE) in 35")
close(value(prob("RBE at that point = 1.35")), 1.35 / 1.1, 1e-12, "dose with the distal RBE"); close(round(100 * (1.35 / 1.1 - 1)), 23, 0, "23% more than planned")

# ---- carbon ions: rigidity from gamma and beta, and the range of 430 MeV per nucleon by velocity scaling of the Bethe range
def brho(t, m, z):
    g = 1 + t / m; b = math.sqrt(1 - 1 / g ** 2); return g * b * m / (z * 299.792458)
mc = 12 * 931.494 - 6 * 0.51099895
close(M.br_c, brho(430 * 12, mc, 6), 1e-9, "carbon rigidity"); close(round(M.br_c, 1), 6.6, 0, "6.6 T m (the HIT synchrotron's maximum)")
ep30 = bisect(lambda e: A * e ** PW - 30.0, 50, 400); close(M.e30, ep30, 1e-9, "proton energy for 30 cm"); ratio = brho(430 * 12, mc, 6) / brho(ep30, 938.272, 1)
true(2.8 < ratio < 3.0, f"nearly three times the proton rigidity ({ratio:.2f})"); says("nearly three times that of protons", "rigidity ratio")
tp = 430 * MP / 931.494; rc = (15.77 + dR(150, tp)) * (mc / MP) / 36
true(29.0 < rc < 32.0, f"430 MeV per nucleon carbon reaches about 30 cm of water ({rc:.1f} cm by z-squared scaling)")

for b in bad: print("FAIL", b)
print(f"numbers_protons: {n} numbers re-derived"); print("numbers_protons: PASS" if not bad else f"numbers_protons: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
