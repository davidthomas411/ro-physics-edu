"""Photon mass attenuation (mu/rho) and mass energy-absorption (mu_en/rho) coefficients, cm^2/g, from NIST SRD 126 (Hubbell and Seltzer, XCOM-based tables)
for liquid water, cortical bone (ICRU-44), and lead (Z = 82). Densities: water 1.00, cortical bone 1.92, lead 11.35 g/cm^3. Values transcribed from the NIST tables."""
from blocks import DT

WATER = {0.01: (5.329, 4.944), 0.015: (1.673, 1.374), 0.02: (0.8096, 0.5503), 0.03: (0.3756, 0.1557), 0.04: (0.2683, 0.06947), 0.05: (0.2269, 0.04223), 0.06: (0.2059, 0.03190),
         0.08: (0.1837, 0.02597), 0.1: (0.1707, 0.02546), 0.15: (0.1505, 0.02764), 0.2: (0.1370, 0.02967), 0.3: (0.1186, 0.03192), 0.4: (0.1061, 0.03279), 0.5: (0.09687, 0.03299),
         0.6: (0.08956, 0.03284), 0.8: (0.07865, 0.03206), 1.0: (0.07072, 0.03103), 1.25: (0.06323, 0.02965), 1.5: (0.05754, 0.02833), 2.0: (0.04942, 0.02608), 3.0: (0.03969, 0.02281),
         4.0: (0.03403, 0.02066), 5.0: (0.03031, 0.01915), 6.0: (0.02770, 0.01806), 8.0: (0.02429, 0.01658), 10.0: (0.02219, 0.01566), 15.0: (0.01941, 0.01441), 20.0: (0.01813, 0.01382)}
BONE = {0.02: (4.001, 3.601), 0.03: (1.331, 1.070), 0.04: (0.6655, 0.4507), 0.05: (0.4242, 0.2336), 0.06: (0.3148, 0.1400), 0.08: (0.2229, 0.06896), 0.1: (0.1855, 0.04585), 0.15: (0.1480, 0.03183),
        0.2: (0.1309, 0.03003), 0.3: (0.1113, 0.03032), 0.4: (0.09908, 0.03069), 0.5: (0.09022, 0.03073), 0.6: (0.08332, 0.03052), 0.8: (0.07308, 0.02973), 1.0: (0.06566, 0.02875),
        1.25: (0.05871, 0.02745), 1.5: (0.05346, 0.02623), 2.0: (0.04607, 0.02421), 3.0: (0.03745, 0.02145), 4.0: (0.03257, 0.01975), 5.0: (0.02946, 0.01864), 6.0: (0.02734, 0.01788),
        8.0: (0.02467, 0.01695), 10.0: (0.02314, 0.01644), 15.0: (0.02132, 0.01587), 20.0: (0.02068, 0.01568)}
LEAD = {0.05: (8.041, 6.740), 0.06: (5.021, 4.149), 0.08: (2.419, 1.916), 0.1: (5.549, 1.976), 0.15: (2.014, 1.056), 0.2: (0.9985, 0.5870), 0.3: (0.4031, 0.2455), 0.4: (0.2323, 0.1370),
        0.5: (0.1614, 0.09128), 0.6: (0.1248, 0.06819), 0.8: (0.08870, 0.04644), 1.0: (0.07102, 0.03654), 1.25: (0.05876, 0.02988), 1.5: (0.05222, 0.02640), 2.0: (0.04606, 0.02360),
        3.0: (0.04234, 0.02322), 4.0: (0.04197, 0.02449), 5.0: (0.04272, 0.02600), 6.0: (0.04391, 0.02744), 8.0: (0.04675, 0.02989), 10.0: (0.04972, 0.03181), 15.0: (0.05658, 0.03478), 20.0: (0.06206, 0.03595)}
DENS = {"water": 1.00, "bone": 1.92, "lead": 11.35}
MAT = {"water": ("Liquid water", WATER), "bone": ("Cortical bone (ICRU-44)", BONE), "lead": ("Lead", LEAD)}
LEAD_K_EDGE = (0.0880, (1.910, 1.482), (7.683, 2.160))   # keV edge at 88.0 keV: values just below and just above

_f = lambda v: f"{v:.4g}"
_e = lambda e: f"{e:g}"
def table_one(name, energies):
    label, tab = MAT[name]
    return DT(f"{label}: mass coefficients (NIST SRD 126)", ["Energy (MeV)", "μ/ρ (cm²/g)", "μ<sub>en</sub>/ρ (cm²/g)"], [[_e(e), _f(tab[e][0]), _f(tab[e][1])] for e in energies])
def table_two(names, energies):
    head = ["Energy (MeV)"]; cols = []
    for n in names:
        label, tab = MAT[n]; short = label.split(" (")[0]; head += [f"{short} μ/ρ", f"{short} μ<sub>en</sub>/ρ"]; cols.append(tab)
    return DT("Mass coefficients in cm²/g (NIST SRD 126)", head, [[_e(e)] + [x for tab in cols for x in (_f(tab[e][0]), _f(tab[e][1]))] for e in energies])
def reference_html():
    out = []
    for n in ("water", "bone", "lead"):
        label, tab = MAT[n]; rows = [[_e(e), _f(v[0]), _f(v[1])] for e, v in sorted(tab.items())]
        if n == "lead":
            rows.insert(3, ["0.0880 (just below the K edge)", _f(LEAD_K_EDGE[1][0]), _f(LEAD_K_EDGE[1][1])]); rows.insert(4, ["0.0880 (just above the K edge)", _f(LEAD_K_EDGE[2][0]), _f(LEAD_K_EDGE[2][1])])
        out.append(DT(f"{label}, density {DENS[n]:g} g/cm³", ["Energy (MeV)", "μ/ρ (cm²/g)", "μ<sub>en</sub>/ρ (cm²/g)"], rows))
    return "".join(out)
