"""Teaching beam data for the MU calculation module: 6, 10, 15, and 18 MV photons.

Not measured data. Every table comes from one model per energy, so the tables agree with each other.
- TMR(d, s) = exp(-mu_inf x + delta (1 + beta ln(s/10)) (1 - exp(-x/7))), x = d - d_max: a constant attenuation rate offset by a scatter term that grows with depth and field size.
- PDD at SSD 100 cm is built from the TMR, the inverse-square law, and Sp, with the same conversion the TMR chapter teaches. Between the surface and d_max a build-up curve is used.
- Sc and Sp are hand-set curves for 6 MV, scaled for the other energies. Wedge and tray factors are typical values.
The parameters are fitted to typical clinical anchors for a 10 x 10 cm field: PDD(10 cm), TPR20,10, and d_max. Replace the numbers with measured beam data before any clinical use.
The tables are rounded as printed (PDD 0.1%, other factors 3 decimals), and every answer in the module is worked from the printed values.
"""
import math
import beamdata as bd

SIZES = [4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40]
DEPTHS = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 25, 26, 28, 30]
WF_ANGLES = [15, 30, 45, 60]
WF_SIZES = [4, 6, 8, 10, 12, 15, 20]
WF_SLOPE = {15: 0.010, 30: 0.015, 45: 0.020, 60: 0.025}                      # fractional change of the wedge factor per 10 cm of field size
LAM = bd.LAM

ENERGY = {
    6:  dict(dmax=1.5, muinf=0.04482, delta=0.19161, beta=0.38, ka=1.00, kb=1.00, sigma=0.22, wf=(0.930, 0.790, 0.670, 0.545), tf=0.970, pdd10=67.0, tpr=0.667),
    10: dict(dmax=2.5, muinf=0.03382, delta=0.12681, beta=0.30, ka=1.05, kb=0.80, sigma=0.18, wf=(0.950, 0.830, 0.725, 0.600), tf=0.975, pdd10=73.5, tpr=0.737),
    15: dict(dmax=3.0, muinf=0.03087, delta=0.13192, beta=0.24, ka=1.08, kb=0.65, sigma=0.16, wf=(0.960, 0.855, 0.760, 0.645), tf=0.980, pdd10=77.0, tpr=0.762),
    18: dict(dmax=3.5, muinf=0.02845, delta=0.12428, beta=0.20, ka=1.10, kb=0.55, sigma=0.15, wf=(0.965, 0.870, 0.780, 0.670), tf=0.982, pdd10=79.5, tpr=0.781),
}

def sc_table(E): return {s: round(1 + ENERGY[E]["ka"] * (bd.SC[s] - 1), 3) for s in SIZES}
def sp_table(E): return {s: round(1 + ENERGY[E]["kb"] * (bd.SP[s] - 1), 3) for s in SIZES}
def _sp_ln(E, s):
    sp = {k: 1 + ENERGY[E]["kb"] * (v - 1) for k, v in bd.SP.items()}; ks = sorted(sp)
    return bd.interp(math.log(s), [math.log(k) for k in ks], [sp[k] for k in ks])

def tmr_model(E, d, s):
    P = ENERGY[E]; x = max(0.0, d - P["dmax"])
    return math.exp(-P["muinf"] * x + P["delta"] * (1 + P["beta"] * math.log(s / 10)) * (1 - math.exp(-x / LAM)))

def _pdd_deep(E, d, s, f=100.0):
    P = ENERGY[E]; dm = P["dmax"]; ad, am = s * (f + d) / f, s * (f + dm) / f
    return 100 * tmr_model(E, d, ad) * ((f + dm) / (f + d)) ** 2 * _sp_ln(E, ad) / _sp_ln(E, am)

def _surface_fraction(E, s):
    sig = ENERGY[E]["sigma"]
    return sig * (0.75 + 0.25 * s / 10) if s <= 10 else sig * (1 + (s - 10) / 30)

def pdd_model(E, d, s):
    """Percent depth dose at SSD 100 cm for a field of side s at the surface."""
    dm = ENERGY[E]["dmax"]
    if d >= dm: return _pdd_deep(E, d, s)
    h = 1e-4; mu_e = -(math.log(_pdd_deep(E, dm + h, s)) - math.log(_pdd_deep(E, dm, s))) / h        # fall-off rate just beyond d_max
    sig = _surface_fraction(E, s); lo, hi = 0.3, 40.0
    for _ in range(80):                                   # build-up rate k so that the dose peaks at d_max
        k = (lo + hi) / 2
        if math.log((1 - sig) * (k + mu_e) / mu_e) / k > dm: lo = k
        else: hi = k
    G = lambda x: 1 - (1 - sig) * math.exp(-k * x)
    return 100 * math.exp(-mu_e * (d - dm)) * G(d) / G(dm)

def tables(E):
    P = ENERGY[E]; dm = P["dmax"]
    pdd = [[round(pdd_model(E, d, s), 1) for s in SIZES] for d in DEPTHS]
    tmr_depths = [d for d in DEPTHS if d >= dm]
    tmr = [[round(tmr_model(E, d, s), 3) for s in SIZES] for d in tmr_depths]
    wf = {a: [round(P["wf"][i] * (1 + WF_SLOPE[a] * (s - 10) / 10), 3) for s in WF_SIZES] for i, a in enumerate(WF_ANGLES)}
    return dict(energy=E, dmax=dm, sizes=SIZES, depths=DEPTHS, pdd=pdd, tmr_depths=tmr_depths, tmr=tmr, sc=[sc_table(E)[s] for s in SIZES], sp=[sp_table(E)[s] for s in SIZES],
                wf_angles=WF_ANGLES, wf_sizes=WF_SIZES, wf=wf, tf=P["tf"], pdd10=P["pdd10"], tpr=P["tpr"])

def all_tables(): return {E: tables(E) for E in ENERGY}
