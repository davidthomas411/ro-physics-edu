"""One coherent, illustrative 6 MV photon beam for the data-table practice questions.

Not measured data. Sc and Sp are smooth hand-set curves. TMR comes from a three-parameter model that fits typical clinical 6 MV data: the beam
attenuates at a constant rate, and a scatter term that grows with depth and field size offsets part of that attenuation. The parameters are chosen
so that PDD(10 cm) = 67.0%, TPR20,10 = 0.667, and d_max = 1.5 cm for a 10 x 10 cm field. PDD at SSD 100 cm is generated from the TMR and Sp with the
same conversion formula the TMR chapter teaches, so the tables agree with each other.
The tables printed in the questions are rounded (factors to 3 decimals, PDD to 0.1%), and every answer is worked from the printed values."""
import math
from blocks import DT

DMAX = 1.5
SC = {4: 0.952, 5: 0.965, 6: 0.975, 8: 0.988, 10: 1.000, 12: 1.009, 15: 1.020, 20: 1.034, 25: 1.043, 30: 1.049, 40: 1.056}
SP = {4: 0.982, 5: 0.987, 6: 0.991, 8: 0.996, 10: 1.000, 12: 1.004, 15: 1.010, 20: 1.019, 25: 1.027, 30: 1.034, 40: 1.044}
MUINF, DELTA, BETA, LAM = 0.04482, 0.19161, 0.38, 7.0      # attenuation per cm, scatter term for 10 x 10 cm, its growth with field size, and its build-up length (cm)

def interp(x, xs, ys):
    """Linear interpolation in x (clamped to the ends of the table)."""
    if x <= xs[0]: return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]: return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return ys[-1]
def _sp_ln(s):                                   # smooth model value of Sp at any size: linear in ln(size) between the tabulated points
    ks = sorted(SP); return interp(math.log(s), [math.log(k) for k in ks], [SP[k] for k in ks])
def tmr_model(d, s):
    x = max(0.0, d - DMAX); return math.exp(-MUINF * x + DELTA * (1 + BETA * math.log(s / 10)) * (1 - math.exp(-x / LAM)))
def pdd_model(d, s, f=100.0):
    ad, am = s * (f + d) / f, s * (f + DMAX) / f
    return 100 * tmr_model(d, ad) * ((f + DMAX) / (f + d)) ** 2 * _sp_ln(ad) / _sp_ln(am)

TMR_DEPTHS = [1.5, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 25]
PDD_DEPTHS = [1.5, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20]
SIZES = [4, 6, 8, 10, 12, 15, 20, 25, 30]
TMR = {(d, s): round(tmr_model(d, s), 3) for d in TMR_DEPTHS for s in SIZES}
PDD = {(d, s): round(pdd_model(d, s), 1) for d in PDD_DEPTHS for s in SIZES}

def tmr_at(d, s):
    """Read TMR from the printed table, interpolating linearly in field size, then depth, as one would by hand."""
    ds = TMR_DEPTHS; row = lambda dd: interp(s, SIZES, [TMR[(dd, k)] for k in SIZES])
    return interp(d, ds, [row(x) for x in ds])
def pdd_at(d, s):
    ds = PDD_DEPTHS; row = lambda dd: interp(s, SIZES, [PDD[(dd, k)] for k in SIZES])
    return interp(d, ds, [row(x) for x in ds])
def sc_at(s): ks = sorted(SC); return interp(s, ks, [SC[k] for k in ks])
def sp_at(s): ks = sorted(SP); return interp(s, ks, [SP[k] for k in ks])

def _fmt(d): return f"{d:g}"
def table_scatter(sizes=None):
    ks = sizes or sorted(SC)
    return DT("6 MV scatter factors (illustrative data)", ["Field size (cm)", "S<sub>c</sub>", "S<sub>p</sub>"], [[f"{k} × {k}", f"{SC[k]:.3f}", f"{SP[k]:.3f}"] for k in ks])
def table_tmr(depths, sizes):
    return DT("6 MV TMR (illustrative data)", ["Depth (cm)"] + [f"{k} × {k}" for k in sizes], [[_fmt(d)] + [f"{TMR[(d, k)]:.3f}" for k in sizes] for d in depths], "Columns are equivalent-square field sizes at the depth of the point (cm).")
def table_pdd(depths, sizes):
    return DT("6 MV percent depth dose, SSD 100 cm (illustrative data)", ["Depth (cm)"] + [f"{k} × {k}" for k in sizes], [[_fmt(d)] + [f"{PDD[(d, k)]:.1f}" for k in sizes] for d in depths], "Columns are field sizes at the surface (cm). d<sub>max</sub> = 1.5 cm.")

def reference_html():
    """The full illustrative data set, for the Reference page."""
    return table_scatter() + table_tmr(TMR_DEPTHS, SIZES) + table_pdd(PDD_DEPTHS, SIZES)
