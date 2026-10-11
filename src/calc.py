"""Numbers used in worked examples. Content modules import these so every value is computed, not typed."""
import math

LN2 = math.log(2)

# ---------------------------------------------------------------- decay
def lam(t_half):            return LN2 / t_half
def frac_remaining(t, t_half): return 2 ** (-t / t_half)
def time_to_fraction(f, t_half): return t_half * math.log2(1 / f)
def mean_life(t_half):      return t_half / LN2

def pct_per_unit_to_lambda(x):  # "x% per unit time" = fraction lost per unit time
    return -math.log(1 - x)

def daughter_over_parent0(t, tp, td):
    """Activity of daughter / initial parent activity, no daughter at t=0, all parent decays feed the daughter."""
    lp, ld = lam(tp), lam(td)
    return ld / (ld - lp) * (math.exp(-lp * t) - math.exp(-ld * t))

def transient_ratio(tp, td):   return tp / (tp - td)
def t_max(tp, td):
    lp, ld = lam(tp), lam(td)
    return math.log(ld / lp) / (ld - lp)

# ---------------------------------------------------------------- photon dose
def ivsl(f, d, dmax):
    """Inverse-square factor between dmax and depth d at SSD f."""
    return ((f + dmax) / (f + d)) ** 2

def mayneord_F(f1, f2, d, dmax):
    return ivsl(f2, d, dmax) / ivsl(f1, d, dmax)

def equiv_square(a, b):    return 2 * a * b / (a + b)

def tmr_from_pdd(pdd_pct, f, d, dmax, sp_ratio=1.0):
    """TMR(d, A_d) = PDD/100 x ((f+d)/(f+dmax))^2 x Sp(A_dmax)/Sp(A_d)  (sp_ratio = Sp(A_dmax)/Sp(A_d))."""
    return pdd_pct / 100 * ((f + d) / (f + dmax)) ** 2 * sp_ratio

# ---------------------------------------------------------------- attenuation and Compton
def hvl_count(frac):          return math.log2(1 / frac)
def compton_scattered(e_mev, theta_deg):
    a = e_mev / 0.511
    return e_mev / (1 + a * (1 - math.cos(math.radians(theta_deg))))


# ---------------------------------------------------------------- constants, waves, relativity, atoms
C_LIGHT = 2.99792458e8          # m/s
H_EVS = 4.135667696e-15         # eV s
HC_EV_NM = 1239.84198           # eV nm
E_CHG = 1.602176634e-19         # C (and J per eV)
ME, MP, MN, MALPHA = 0.51099895, 938.27209, 939.56542, 3727.3794   # rest energies, MeV
U_MEV = 931.49410               # 1 u in MeV
K_COUL = 8.9875517923e9         # N m^2 / C^2
NA = 6.02214076e23              # 1/mol
RY_EV = 13.605693               # hydrogen ground-state binding energy, eV

def nm_from_ev(e_ev):  return HC_EV_NM / e_ev
def ev_from_nm(l_nm):  return HC_EV_NM / l_nm
def ev_from_hz(f_hz):  return H_EVS * f_hz
def hz_from_ev(e_ev):  return e_ev / H_EVS
def wavelength_m(f_hz): return C_LIGHT / f_hz
def gamma_ke(ke, rest): return 1 + ke / rest
def beta_ke(ke, rest):
    g = gamma_ke(ke, rest); return math.sqrt(1 - 1 / g ** 2)
def pc_ke(ke, rest):   return math.sqrt(ke * ke + 2 * ke * rest)          # momentum x c, MeV
def debroglie_pm(ke, rest): return 1.23984198 / pc_ke(ke, rest)           # hc = 1.23984 MeV pm
def bend_radius_m(pc_mev, b_t): return pc_mev / (299.792458 * b_t)       # r = p/(eB)
def coulomb_n(q1, q2, r_m): return K_COUL * q1 * q2 / r_m ** 2
def h_level(n):        return -RY_EV / n ** 2
def h_photon_ev(hi, lo): return RY_EV * (1 / lo ** 2 - 1 / hi ** 2)

# ---------------------------------------------------------------- nuclear structure (atomic masses in u)
M_H1, M_N, M_H2, M_HE4, M_C12, M_O16 = 1.00782503, 1.00866492, 2.01410178, 4.00260325, 12.0, 15.99491462
def binding_mev(z, a, atomic_mass_u): return (z * M_H1 + (a - z) * M_N - atomic_mass_u) * U_MEV

# ---------------------------------------------------------------- specific activity
YEAR_S, DAY_S, CI_BQ = 365.25 * 86400, 86400.0, 3.7e10
def spec_act_bq_g(t_half_s, molar_mass): return LN2 * NA / (t_half_s * molar_mass)


# ---------------------------------------------------------------- brachytherapy: TG-43 line-source geometry and dose rate
def tg43_gl(r, theta_deg, length):
    """Line-source geometry function G_L(r, theta) in cm^-2 (r and length in cm): beta / (L r sin theta) off the axis, 1 / (r^2 - L^2/4) on it."""
    th = math.radians(theta_deg); rho, z = r * math.sin(th), r * math.cos(th)
    if rho < 1e-9: return 1 / (r * r - length * length / 4)
    beta = math.atan2(z + length / 2, rho) - math.atan2(z - length / 2, rho)
    return beta / (length * rho)

def tg43_rate(sk, lam, r, theta_deg, length, g, f, r0=1.0, theta0_deg=90.0):
    """D = S_K * Lambda * [G(r, theta) / G(r0, theta0)] * g(r) * F(r, theta), in cGy/h for S_K in U and Lambda in cGy/h/U."""
    return sk * lam * tg43_gl(r, theta_deg, length) / tg43_gl(r0, theta0_deg, length) * g * f

def implant_total_dose(rate0, t_half):
    """Total dose from a permanent implant: initial dose rate x mean life (1.44 T1/2). Rate and half-life in compatible units."""
    return rate0 * t_half / LN2

def implant_dose_to(rate0, t_half, t):
    return rate0 * t_half / LN2 * (1 - math.exp(-LN2 * t / t_half))
