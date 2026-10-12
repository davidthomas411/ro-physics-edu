"""Independent re-derivation of the numbers in the Chapter 1-3 topics, by routes that share no code with calc.py or the topic files."""
import sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import calc, charges_atom, particles_energy, nuclear_structure, specific_activity, problems_decay, waves_photons, figs

fails = []; n = 0
def check(name, got, want, tol=2e-3):
    global n; n += 1
    if abs(got - want) > tol * abs(want): fails.append(f"{name}: got {got!r}, independent {want!r}")
H, C, E, EPS0, NA = 6.62607015e-34, 299792458.0, 1.602176634e-19, 8.8541878128e-12, 6.02214076e23
me_mev, u_mev = 0.51099895, 931.49410

check("hc in eV nm", calc.HC_EV_NM, H * C / E * 1e9)
check("linac wavelength (cm)", waves_photons.lam_lin_cm, C / 2.998e9 * 100)
check("100 keV photon wavelength (pm)", waves_photons.lam_100k_pm, H * C / (1e5 * E) * 1e12)
check("511 keV photon wavelength (pm)", waves_photons.lam_511_pm, H * C / (511e3 * E) * 1e12)
check("Tc-99m 140 keV frequency", waves_photons.f_tc, 140e3 * E / H)
E_tot = 6.0 + me_mev; pc = math.sqrt(E_tot ** 2 - me_mev ** 2)
check("6 MeV electron beta = pc/E", particles_energy.b6, pc / E_tot)
check("6 MeV electron gamma", particles_energy.g6, E_tot / me_mev)
check("100 MeV proton beta", particles_energy.bp100, math.sqrt(1 - (938.27209 / (100 + 938.27209)) ** 2))
check("100 MeV electron de Broglie (pm)", waves_photons.lam_e100_pm, H / (math.sqrt((0.1 + me_mev) ** 2 - me_mev ** 2) * 1e6 * E / C) * 1e12, 3e-3)
check("Coulomb force 2 fm (N)", charges_atom.F2, E ** 2 / (4 * math.pi * EPS0 * (2e-15) ** 2))
pc6 = math.sqrt((6.0 + me_mev) ** 2 - me_mev ** 2); p_si = pc6 * 1e6 * E / C
check("bend radius 6 MeV, 0.20 T (cm)", charges_atom.r6, p_si / (E * 0.20) * 100)
alpha = 7.2973525693e-3
check("hydrogen ground state (eV)", calc.RY_EV, 0.5 * alpha ** 2 * me_mev * 1e6, 3e-4)
check("H n=3 to 2 photon (eV)", charges_atom.E32, 13.6057 * (1 / 4 - 1 / 9), 2e-3)
# binding energies from nuclear masses (atomic mass minus electron masses): a different route from the atomic-mass formula
mp, mn, mel = 1.007276467, 1.008664916, 0.000548580
check("deuteron BE (MeV)", nuclear_structure.be_h2, (mp + mn - (2.01410178 - mel)) * u_mev, 2e-3)
check("He-4 BE (MeV)", nuclear_structure.be_he4, (2 * mp + 2 * mn - (4.00260325 - 2 * mel)) * u_mev, 2e-3)
check("O-16 BE (MeV)", nuclear_structure.be_o16, (8 * mp + 8 * mn - (15.99491462 - 8 * mel)) * u_mev, 2e-3)
check("C-12 BE (MeV)", nuclear_structure.be_c12, (6 * mp + 6 * mn - (12.0 - 6 * mel)) * u_mev, 2e-3)
# specific activity: activity = decay constant x atoms in one gram, with half-lives in other units
YR, D = 365.25 * 24 * 3600, 86400.0
for name, th_s, M in (("Co-60", 5.27 * YR, 59.93), ("Cs-137", 30.1 * YR, 136.91), ("Ir-192", 73.8 * D, 191.96), ("I-125", 59.4 * D, 124.90), ("Pd-103", 16.99 * D, 102.91), ("Ra-226", 1600 * YR, 226.03)):
    N = NA / M; A = (1 / (th_s / math.log(2))) * N          # lambda = 1/mean life
    check(f"specific activity {name} (Bq/g)", specific_activity.S[name], A)
check("Ra-226 is about 1 Ci/g", specific_activity.S["Ra-226"] / 3.7e10, 1.0, 0.03)
check("Lu-177 theoretical specific activity", specific_activity.lu, math.log(2) * NA / (6.647 * D * 176.94), 1e-6)
# I-125 permanent implant total dose by numerical integration of the dose rate
lam_h = math.log(2) / (59.4 * 24); dose = 0.0; t = 0.0
while t < 60 * 59.4 * 24: dose += 7.5 * math.exp(-lam_h * (t + 0.5)) * 1.0; t += 1.0
check("I-125 total dose (Gy), numerical integral", problems_decay.d_inf, dose / 100, 3e-3)
# daughter peak time and transient ratio by brute force
lp, ld = math.log(2) / 36.0, math.log(2) / 4.0
best_t = max((k * 0.001 for k in range(1, 100000)), key=lambda x: math.exp(-lp * x) - math.exp(-ld * x))
check("t_max for 36 h / 4 h (h)", problems_decay.tmax, best_t, 1e-3)
lp2, ld2 = math.log(2) / 65.94, math.log(2) / 6.0067; Np, Nd, dt = 1.0, 0.0, 0.001
for _ in range(int(400 / dt)): dNp = -lp2 * Np; dNd = lp2 * Np - ld2 * Nd; Np += dNp * dt; Nd += dNd * dt
check("Mo/Tc activity ratio by ODE", problems_decay.mo_tc, ld2 * Nd / (lp2 * Np), 2e-3)
check("Tc-99m 925 MBq at 6.5 h", problems_decay.a_tc, 925 * math.exp(-math.log(2) * 6.5 / 6.0))
check("Ir-192 370 GBq after 120 d", problems_decay.a_ir, 370 * math.exp(-120 * math.log(2) / 73.8))
check("72 I-125 seeds after 45 d (mCi)", problems_decay.a_seeds, 72 * 0.32 * math.exp(-45 * math.log(2) / 59.4))
check("Lu-177 150 to 25 MBq (d)", problems_decay.t_lu, math.log(150 / 25) / (math.log(2) / 6.65))
check("6% per day half-life (d)", problems_decay.th6, math.log(2) / -math.log(0.94))
check("99% of secular equilibrium (half-lives)", problems_decay.n_hl, math.log(100) / math.log(2))
check("Cs-137 photons per 1000 decays", sum([0.944 * 0.9015 * 1000]), 851.0, 2e-3)
bad_svg = [k for k, v in figs.build().items() if "nan" in v.lower().replace("nuclide", "").replace("scan", "").replace("ranan", "")]
if bad_svg: fails.append(f"figures contain NaN: {bad_svg}")
print(f"{n} numbers re-derived independently")
for f in fails: print("FAIL", f)
print("numbers2: PASS" if not fails else f"numbers2: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
