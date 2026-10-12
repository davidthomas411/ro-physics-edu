from blocks import *
import math, calc
import nistdata as nd

# ---------------------------------------------------------------- constants and data
NA = 6.02214076e23                                   # Avogadro constant, 1/mol
RE = 2.8179403262e-13                                # classical electron radius, cm
MEC2 = 0.51099895                                    # electron rest energy, MeV
BARN = 1e-24                                         # cm²
M_EXP = 2.94                                         # power-law exponent of the effective atomic number
A = dict(H=1.008, Li=6.94, C=12.011, N=14.007, O=15.999, F=18.998, Na=22.990, Mg=24.305, P=30.974, S=32.06, Cl=35.45, Ar=39.948, K=39.098, Ca=40.078, Pb=207.2)   # standard atomic weights, g/mol
Z = dict(H=1, Li=3, C=6, N=7, O=8, F=9, Na=11, Mg=12, P=15, S=16, Cl=17, Ar=18, K=19, Ca=20, Pb=82)
EL125 = dict(H=(0.1129, 0.05311), O=(0.05697, 0.02669))                # NIST (XCOM-based) μ/ρ and μen/ρ of the elements of water at 1.25 MeV, cm²/g
M_W = 2 * A["H"] + A["O"]                                              # molar mass of water, g/mol
COMP = {                                                               # composition by mass
    "water": dict(H=2 * A["H"] / M_W, O=A["O"] / M_W),
    "air": dict(C=0.000124, N=0.755268, O=0.231781, Ar=0.012827),                                          # dry air near sea level (NIST)
    "adipose": dict(H=0.114, C=0.598, N=0.007, O=0.278, Na=0.001, S=0.001, Cl=0.001),                     # adipose tissue, ICRU Report 44
    "muscle": dict(H=0.102, C=0.143, N=0.034, O=0.710, Na=0.001, P=0.002, S=0.003, Cl=0.001, K=0.004),     # skeletal muscle, ICRU Report 44
    "bone": dict(H=0.034, C=0.155, N=0.042, O=0.435, Na=0.001, Mg=0.002, P=0.103, S=0.003, Ca=0.225),      # cortical bone, ICRU Report 44
    "lead": dict(Pb=1.0),
}
RHO = dict(water=1.00, air=0.001205, adipose=0.95, muscle=1.05, bone=1.92, lead=11.35)                    # g/cm³
NAMES = dict(water="Water", air="Air, dry", adipose="Adipose tissue", muscle="Skeletal muscle", bone="Cortical bone", lead="Lead")
WAT, BON, LEA = nd.WATER, nd.BONE, nd.LEAD

# ---------------------------------------------------------------- formulas
def zoa(c):
    """Mean Z/A of a composition given by mass fractions."""
    return sum(w * Z[e] / A[e] for e, w in c.items())
def e_per_g(c): return NA * zoa(c)
def zeff(c, m=M_EXP):
    """Power-law effective atomic number, weighting Z^m by the share of the electrons on each element."""
    t = zoa(c)
    return sum(w * Z[e] / A[e] / t * Z[e] ** m for e, w in c.items()) ** (1 / m)
def zeff_units(units, m=M_EXP):
    """The same from a formula: units maps each element to its atoms per formula unit."""
    ne = sum(n * Z[e] for e, n in units.items())
    return sum(n * Z[e] / ne * Z[e] ** m for e, n in units.items()) ** (1 / m)
def mix(fracs, values): return sum(w * values[k] for k, w in fracs.items())
def kn(e):
    """Klein–Nishina cross-section per electron (cm²) for a photon of e MeV."""
    a = e / MEC2; L = math.log(1 + 2 * a)
    return 2 * math.pi * RE ** 2 * ((1 + a) / a ** 2 * (2 * (1 + a) / (1 + 2 * a) - L / a) + L / (2 * a) - (1 + 3 * a) / (1 + 2 * a) ** 2)
def trans(*pairs): return math.exp(-sum(mu * x for mu, x in pairs))   # narrow beam, one energy: (μ, x) for each layer
en_mu = lambda tab, e: tab[e][1] / tab[e][0]                          # fraction of hν absorbed locally per interaction
bw = lambda e: BON[e][1] / WAT[e][1]                                  # (μen/ρ) bone / water

# ---------------------------------------------------------------- numbers in the text
EG = {k: e_per_g(c) for k, c in COMP.items()}; ZE = {k: zeff(c) for k, c in COMP.items()}
zoa_el = {e: Z[e] / A[e] for e in ("H", "C", "N", "O", "Ca", "Pb")}
r10, r125, r10m = en_mu(WAT, 0.01), en_mu(WAT, 1.25), en_mu(WAT, 10.0)
r_lo, r_hi = min(en_mu(WAT, e) for e in (0.06, 0.08, 0.1)), max(en_mu(WAT, e) for e in (0.06, 0.08, 0.1))
tmax100 = 1000 * (0.1 - calc.compton_scattered(0.1, 180))           # keV, largest energy a Compton electron takes from a 100 keV photon
PB_MIN = min((e for e in LEA if e >= 1.0), key=lambda e: LEA[e][0]); _pe = sorted(LEA)
PB_LO, PB_HI = _pe[_pe.index(PB_MIN) - 1], _pe[_pe.index(PB_MIN) + 1]
pct_b, pct_air = 100 * (1 - EG["bone"] / EG["water"]), 100 * (1 - EG["air"] / EG["water"])
R_TAB = [0.03, 0.06, 0.1, 0.2, 1.25, 6.0, 20.0]
R_WHY = {0.03: "Photoelectric, about Z³ per gram", 0.06: "Photoelectric, about Z³ per gram", 0.1: "Photoelectric, falling with energy", 0.2: "Photoelectric, falling with energy",
         1.25: "Compton: electrons per gram", 6.0: "Compton and pair production", 20.0: "Pair production, about Z per gram"}
r_mv = [bw(e) for e in (0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0)]; r_mv_lo, r_mv_hi = min(r_mv), max(r_mv)
re_bw = EG["bone"] / EG["water"]
MV_R = f"{re_bw:.2f}"; assert MV_R == f"{r_mv_lo:.2f}" == f"{r_mv_hi:.2f}"                  # the 0.5 to 2 MeV ratios all round to the electron ratio
G_AIR = 0.003                                                         # ḡ for Co-60 γ rays in air: 0.0032 in the BIPM and NIST air-kerma standards
PB_AZ = A["Pb"] / Z["Pb"]
_up = next(e for e in sorted(BON) if e > 1 and bw(e) > 1); _dn = max(e for e in sorted(BON) if e < _up)
E_CROSS = _dn * (_up / _dn) ** (math.log(1 / bw(_dn)) / math.log(bw(_up) / bw(_dn)))   # ratio = 1, interpolating ln(ratio) against ln(E)
fmt_e = lambda e: f"{1000 * e:g} keV" if e < 1 else f"{e:g} MeV"
sig4 = lambda v: f"{v:#.4g}"                                         # a tabulated value with its four significant figures (1.070, not 1.07)

# ---- worked example: water at 1.25 MeV
mr1 = WAT[1.25][0]; mu1 = RHO["water"] * mr1
mol_g = NA / M_W                                                      # molecules per gram
s_mol = mr1 / mol_g / BARN; s_el = s_mol / 10                          # barns per molecule and per electron
kn125 = kn(1.25) / BARN
# ---- worked example: water from hydrogen and oxygen
wH, wO = COMP["water"]["H"], COMP["water"]["O"]
mu_mix = wH * EL125["H"][0] + wO * EL125["O"][0]; en_mix = wH * EL125["H"][1] + wO * EL125["O"][1]
share_H = wH * EL125["H"][0] / mu_mix
# ---- worked example: electrons per gram and Z_eff of water
ne_w = EG["water"]; zw = zeff_units(dict(H=2, O=1)); sum_w = 0.2 * 1 ** M_EXP + 0.8 * 8 ** M_EXP
# ---- worked example: bone dose at two energies
D_W = 2.0
q30, q125 = bw(0.03), bw(1.25)

TOPIC = dict(
    id="attenuation", domain=1, sub="I.E", title="Attenuation coefficients and mixtures",
    ref=dict(aapm="", khan="", ford="5"),
    guide=[
        H("Linear, mass, atomic, and electronic coefficients"),
        P("The linear coefficient μ (cm<sup>−1</sup>) scales with density, so ice, water, and steam differ in μ but share one mass coefficient μ/ρ (cm²/g); their attenuation is set by the mass thickness ρx (g/cm²). The atomic attenuation coefficient <sub>a</sub>μ and the electronic attenuation coefficient <sub>e</sub>μ are cross-sections, in cm² per atom and per electron, often given in barns (1 b = 10<sup>−24</sup> cm²)."),
        EQ("μ = ρ (μ/ρ),   I = I<sub>0</sub> e<sup>−(μ/ρ) ρx</sup>",
           "μ/ρ = (N<sub>A</sub> / A) <sub>a</sub>μ = (N<sub>A</sub> Z / A) <sub>e</sub>μ,   <sub>a</sub>μ = Z <sub>e</sub>μ",
           "N<sub>A</sub> = 6.022 × 10<sup>23</sup> mol<sup>−1</sup>; for a compound the molar mass M replaces A and gives a cross-section per molecule"),
        P(f"A is about 2Z ({PB_AZ:.1f}Z for lead), so a power of Z drops by about one from atom to gram: Compton scattering, about Z per atom, is nearly constant per gram. Per electron it follows the Klein–Nishina cross-section, whatever the atom."),
        EX("Water at 1.25 MeV", STEM("Water in a Co-60 beam, with the photon energy taken as 1.25 MeV.", [f"μ/ρ = {mr1} cm²/g (NIST)", f"ρ = {RHO['water']:.2f} g/cm³", f"M = {M_W:.3f} g/mol, with 10 electrons per molecule"],
                                     "Find [[μ]], the [[cross-section per molecule]], and the [[cross-section per electron]]."),
           [f"μ = {RHO['water']:.2f} g/cm³ × {mr1} cm²/g = {mu1:.5f} cm<sup>−1</sup>",
            f"Molecules per gram = N<sub>A</sub> / M = 6.022 × 10<sup>23</sup> / {M_W:.3f} = {sci(mol_g, 4)}",
            f"Per molecule: {mr1} / ({sci(mol_g, 4)}) = {sci(s_mol * BARN, 4)} cm² = {s_mol:.3f} b",
            f"Per electron: {s_mol:.3f} b / 10 = {s_el:.4f} b"],
           f"μ = {mu1:.4f} cm<sup>−1</sup>, {s_mol:.2f} b per molecule, and {s_el:.3f} b per electron. The Klein–Nishina cross-section at 1.25 MeV is {kn125:.4f} b, so Compton scattering accounts for nearly all of the attenuation."),

        H("Energy transfer and energy absorption"),
        P("μ counts interactions of every kind. In an interaction, part of the photon energy hν becomes kinetic energy of electrons or positrons, and the rest leaves as scattered photons, fluorescence x-rays, or annihilation photons. The energy-transfer coefficient keeps only the transferred part. The energy-absorption coefficient also removes the fraction ḡ of that kinetic energy which the charged particles radiate as they slow down, mainly as bremsstrahlung."),
        EQ("μ<sub>tr</sub> = μ Ē<sub>tr</sub> / hν   (Ē<sub>tr</sub>: mean energy transferred per interaction)", "μ<sub>en</sub> = μ<sub>tr</sub> (1 − ḡ),   so μ ≥ μ<sub>tr</sub> ≥ μ<sub>en</sub>", "mean energy absorbed per interaction = hν μ<sub>en</sub> / μ"),
        UL("Narrow-beam transmission and the HVL follow μ: any interaction, coherent scattering included, removes the photon from the beam.",
           "Kerma follows μ<sub>tr</sub>/ρ, and collision kerma, equal to the dose under charged-particle equilibrium, follows μ<sub>en</sub>/ρ. Coherent scattering adds to μ only."),
        P(f"In water μ<sub>en</sub>/μ is {r125:.2f} at 1.25 MeV but only {r_lo:.2f} to {r_hi:.2f} between 60 and 100 keV, where a Compton electron takes at most {tmax100:.0f} keV of a 100 keV photon. ḡ grows with photon energy and atomic number; for Co-60 γ rays in air it is about {G_AIR}."),

        H("Beam geometry and beam hardening"),
        P("Tabulated coefficients are narrow-beam values: the beam is collimated and a small detector sits far behind the absorber, so only photons that cross it without interacting are counted. For several layers the exponents add, in any order."),
        EQ("T = e<sup>−(μ<sub>1</sub>x<sub>1</sub> + μ<sub>2</sub>x<sub>2</sub> + …)</sup>   (narrow beam, one energy)"),
        P("With a wide field or a detector close behind the absorber, scattered photons are counted too: the build-up factor raises the transmission above e<sup>−μx</sup>, so a fitted exponential has a coefficient smaller than μ, and a barrier designed from narrow-beam μ alone transmits more than calculated. The build-up factor grows with thickness, field size, and closeness of the detector."),
        P(f"A beam with a spectrum loses its softer photons first, so it hardens with depth. In water μ/ρ falls with energy throughout the therapy range; in lead it is lowest between {PB_LO:g} and {PB_HI:g} MeV and rises above that through pair production, so lead removes both ends of an 18 MV spectrum."),

        H("Compounds and mixtures"),
        P("The mass coefficients of a compound or mixture are the weight-fraction averages of those of its elements: the mixture rule. It holds for μ/ρ and μ<sub>tr</sub>/ρ, neglecting chemical binding, which matters mainly near absorption edges, and closely for μ<sub>en</sub>/ρ, because the radiative losses of the electrons depend on the mixture as a whole."),
        EQ("(μ/ρ)<sub>mix</sub> = Σ w<sub>i</sub> (μ/ρ)<sub>i</sub>,   w<sub>i</sub> = n<sub>i</sub> A<sub>i</sub> / M   (n<sub>i</sub> atoms of element i per molecule)",
           "electrons per gram N<sub>e</sub> = N<sub>A</sub> Σ w<sub>i</sub> Z<sub>i</sub> / A<sub>i</sub>,   electrons per cm³ = ρ N<sub>e</sub>",
           f"Z<sub>eff</sub> = (Σ a<sub>i</sub> Z<sub>i</sub><sup>m</sup>)<sup>1/m</sup>,   a<sub>i</sub> = share of the electrons on element i,   m = {M_EXP}"),
        P(f"Z/A is {zoa_el['H']:.2f} for hydrogen, {zoa_el['O']:.2f} for carbon, nitrogen, oxygen, and calcium, and {zoa_el['Pb']:.2f} for lead, so electrons per gram depend mainly on the hydrogen content. In the Compton region μ/ρ is proportional to N<sub>e</sub>, and μ to the electron density, ρN<sub>e</sub>, which planning systems derive from CT numbers."),
        P(f"The effective atomic number describes photoelectric absorption, about Z<sup>3</sup> per electron; values vary with m and with the composition assumed."),
        TABLE(["Material", "ρ (g/cm³)", "Electrons per gram (10<sup>23</sup>)", f"Z<sub>eff</sub> (m = {M_EXP})"],
              [[NAMES[k], (f"{RHO[k]:.4f}" if RHO[k] < 0.1 else f"{RHO[k]:.2f}"), f"{EG[k] / 1e23:.2f}", (f"{ZE[k]:.0f}" if k == "lead" else f"{ZE[k]:.1f}")] for k in COMP]),
        P("Tissue compositions by mass from ICRU Report 44; air dry, near sea level."),
        P(f"Fat has about the electrons per gram of water but a lower Z<sub>eff</sub>, so it absorbs less per gram at low energies. Calcium and phosphorus raise the Z<sub>eff</sub> of bone to about {ZE['bone']:.0f}, while its lower hydrogen content leaves {pct_b:.0f}% fewer electrons per gram than water; air has {pct_air:.0f}% fewer."),
        EX("Water from hydrogen and oxygen", STEM("Water, H<sub>2</sub>O, at 1.25 MeV.", [f"hydrogen: A = {A['H']}, μ/ρ = {EL125['H'][0]} cm²/g, μ<sub>en</sub>/ρ = {EL125['H'][1]} cm²/g", f"oxygen: A = {A['O']}, μ/ρ = {EL125['O'][0]} cm²/g, μ<sub>en</sub>/ρ = {EL125['O'][1]} cm²/g"],
                                                 "Find [[μ/ρ]] and [[μ<sub>en</sub>/ρ]] of water by the mixture rule."),
           [f"M = 2 × {A['H']} + {A['O']} = {M_W:.3f} g/mol",
            f"w<sub>H</sub> = {2 * A['H']:.3f} / {M_W:.3f} = {wH:.4f},   w<sub>O</sub> = {A['O']} / {M_W:.3f} = {wO:.4f}",
            f"μ/ρ = {wH:.4f} × {EL125['H'][0]} + {wO:.4f} × {EL125['O'][0]} = {wH * EL125['H'][0]:.5f} + {wO * EL125['O'][0]:.5f} = {mu_mix:.5f} cm²/g",
            f"μ<sub>en</sub>/ρ = {wH:.4f} × {EL125['H'][1]} + {wO:.4f} × {EL125['O'][1]} = {en_mix:.5f} cm²/g"],
           f"{mu_mix:.5f} and {en_mix:.5f} cm²/g, the NIST values for water. Hydrogen is {100 * wH:.0f}% of the mass but gives {100 * share_H:.0f}% of μ/ρ, because its Z/A is twice that of oxygen."),
        EX("Electrons per gram and Z<sub>eff</sub> of water", STEM("Water, H<sub>2</sub>O.", [f"hydrogen: Z = 1, A = {A['H']}", f"oxygen: Z = 8, A = {A['O']}", f"m = {M_EXP}"], "Find the [[electrons per gram]] and the [[effective atomic number]]."),
           [f"Electrons per molecule = 2 × 1 + 8 = 10;   M = {M_W:.3f} g/mol",
            f"N<sub>e</sub> = 6.022 × 10<sup>23</sup> × 10 / {M_W:.3f} = {sci(ne_w, 4)} g<sup>−1</sup>",
            "Shares of the electrons: a<sub>H</sub> = 2/10 = 0.2,   a<sub>O</sub> = 8/10 = 0.8",
            f"Z<sub>eff</sub> = (0.2 × 1<sup>{M_EXP}</sup> + 0.8 × 8<sup>{M_EXP}</sup>)<sup>1/{M_EXP}</sup> = ({sum_w:.1f})<sup>1/{M_EXP}</sup> = {zw:.3f}"],
           f"{sci(ne_w, 3)} electrons per gram and Z<sub>eff</sub> = {zw:.2f}."),

        H("Dose ratios between materials"),
        P("Two small masses in the same photon energy fluence, each in charged-particle equilibrium, receive doses in the ratio of their μ<sub>en</sub>/ρ. For cortical bone and water that ratio follows the dominant interaction:"),
        TABLE(["Photon energy", "(μ<sub>en</sub>/ρ)<sub>bone</sub> / (μ<sub>en</sub>/ρ)<sub>water</sub>", "Main cause"], [[fmt_e(e), f"{bw(e):.2f}" if bw(e) > 1.5 else f"{bw(e):.3f}", R_WHY[e]] for e in R_TAB]),
        P(f"From 0.5 to 2 MeV the ratio is {r_mv_lo:.3f} to {r_mv_hi:.3f}, the ratio of electrons per gram ({re_bw:.3f}). At kilovoltage energies bone absorbed about {bw(0.1):.0f} to {bw(0.03):.0f} times the energy per gram of soft tissue, a cause of bone necrosis; megavoltage beams avoid that excess. Above about {E_CROSS:.0f} MeV pair production lifts the ratio above 1. For a spectrum the ratio is averaged over the energy fluence."),
        EX("Bone dose at two energies", STEM(f"A small piece of cortical bone lies in soft tissue, taken as water, under charged-particle equilibrium. The soft tissue receives {D_W:.1f} Gy.",
                                            [f"30 keV: μ<sub>en</sub>/ρ = {sig4(BON[0.03][1])} cm²/g (bone), {sig4(WAT[0.03][1])} cm²/g (water)", f"1.25 MeV: μ<sub>en</sub>/ρ = {BON[1.25][1]} cm²/g (bone), {WAT[1.25][1]} cm²/g (water)"],
                                            "Find the [[dose to the bone]] at each energy."),
           [f"30 keV: ratio = {sig4(BON[0.03][1])} / {sig4(WAT[0.03][1])} = {q30:.2f};   dose = {D_W:.1f} × {q30:.2f} = {D_W * q30:.1f} Gy",
            f"1.25 MeV: ratio = {BON[1.25][1]} / {WAT[1.25][1]} = {q125:.3f};   dose = {D_W:.1f} × {q125:.3f} = {D_W * q125:.2f} Gy",
            f"Electrons per gram, bone / water = {EG['bone'] / 1e23:.3f} / {EG['water'] / 1e23:.3f} = {re_bw:.3f}, close to the ratio at 1.25 MeV"],
           f"{D_W * q30:.1f} Gy at 30 keV and {D_W * q125:.2f} Gy at 1.25 MeV."),
    ],
    cards=[
        F("Linear and mass attenuation coefficients", "μ (cm<sup>−1</sup>) = ρ × μ/ρ (cm²/g). Ice, water, and steam share μ/ρ but differ in μ."),
        F("Atomic and electronic coefficients", "Cross-sections per atom (<sub>a</sub>μ) and per electron (<sub>e</sub>μ), in cm² or barns (1 b = 10<sup>−24</sup> cm²). μ/ρ = (N<sub>A</sub>/A) <sub>a</sub>μ = (N<sub>A</sub>Z/A) <sub>e</sub>μ."),
        F("Energy-transfer coefficient", "μ<sub>tr</sub> = μ Ē<sub>tr</sub>/hν, with Ē<sub>tr</sub> the mean energy given to electrons and positrons as kinetic energy per interaction."),
        F("Coefficient for transmission and for dose", "μ ≥ μ<sub>tr</sub> ≥ μ<sub>en</sub>. Narrow-beam transmission and HVL follow μ, kerma μ<sub>tr</sub>/ρ, and dose under charged-particle equilibrium μ<sub>en</sub>/ρ."),
        F("Radiative fraction ḡ", f"About {G_AIR} for Co-60 γ rays in air. It grows with the photon energy and with the atomic number of the medium."),
        F("Broad-beam measurement", "Scatter reaches the detector, so the transmission exceeds e<sup>−μx</sup> and a fitted coefficient is below μ. The build-up grows with thickness, field size, and closeness of the detector."),
        F("Mixture rule", "(μ/ρ)<sub>mix</sub> = Σ w<sub>i</sub>(μ/ρ)<sub>i</sub> with weight fractions w<sub>i</sub>. It holds for μ/ρ and μ<sub>tr</sub>/ρ, and closely for μ<sub>en</sub>/ρ.",
          w=[f"Water: w<sub>H</sub> = {wH:.4f}, w<sub>O</sub> = {wO:.4f}", f"μ/ρ at 1.25 MeV = {wH:.4f} × {EL125['H'][0]} + {wO:.4f} × {EL125['O'][0]} = {mu_mix:.5f} cm²/g"]),
        F("Electrons per gram", f"N<sub>A</sub> Σ w<sub>i</sub>Z<sub>i</sub>/A<sub>i</sub>. Z/A is {zoa_el['H']:.2f} for hydrogen and about 0.5 for C, N, O. Water {EG['water'] / 1e23:.2f}, air {EG['air'] / 1e23:.2f}, cortical bone {EG['bone'] / 1e23:.2f}, lead {EG['lead'] / 1e23:.2f} × 10<sup>23</sup>."),
        F("Effective atomic number", f"(Σ a<sub>i</sub>Z<sub>i</sub><sup>{M_EXP}</sup>)<sup>1/{M_EXP}</sup>, with a<sub>i</sub> the shares of the electrons. Water {zw:.2f}, air {ZE['air']:.1f}, fat about {ZE['adipose']:.1f}, cortical bone about {ZE['bone']:.0f}.",
          w=[f"Water: (0.2 × 1 + 0.8 × 8<sup>{M_EXP}</sup>)<sup>1/{M_EXP}</sup> = ({sum_w:.1f})<sup>1/{M_EXP}</sup> = {zw:.2f}"]),
        F("Bone-to-water ratio of μ<sub>en</sub>/ρ", f"About {q30:.1f} at 30 keV, {MV_R} from 0.5 to 2 MeV (the ratio of electrons per gram), and above 1 beyond about {E_CROSS:.0f} MeV (pair production)."),
    ],
)

# ---------------------------------------------------------------- practice questions
# lead at 1.25 MeV: atomic cross-section
p_at = LEA[1.25][0] * A["Pb"] / NA / BARN
p_el, p_zfa, p_lin = p_at / Z["Pb"], LEA[1.25][0] * Z["Pb"] / NA / BARN, LEA[1.25][0] * RHO["lead"] * A["Pb"] / NA / BARN
p_kn = e_per_g(COMP["lead"]) * kn(1.25) / LEA[1.25][0]                # share of μ/ρ that is Compton scattering (Klein–Nishina)
# spongy bone modelled as cortical bone and water by mass, 30 keV
FB = 0.40
q_mix = FB * BON[0.03][1] + (1 - FB) * WAT[0.03][1]
q_mix_mean, q_mix_swap, q_mix_mu = (BON[0.03][1] + WAT[0.03][1]) / 2, (1 - FB) * BON[0.03][1] + FB * WAT[0.03][1], FB * BON[0.03][0] + (1 - FB) * WAT[0.03][0]
# relative electron density of cortical bone
ZA_B, ZA_W = round(zoa(COMP["bone"]), 4), round(zoa(COMP["water"]), 4)
q_red = RHO["bone"] * ZA_B / ZA_W
q_red_rho, q_red_za, q_red_div = RHO["bone"], ZA_B / ZA_W, RHO["bone"] / (ZA_B / ZA_W)
E_HI = 10.0                                                            # an energy above which the bone-to-water ratio exceeds 1 (checked in the tests)

PROBLEMS = [
    # ---- coefficients
    PR(STEM("Ice, liquid water, and steam are each irradiated by photons of one energy.", [], "Which [[coefficient]] has the same value in all three?"),
       "The mass attenuation coefficient, μ/ρ", ["The linear attenuation coefficient, μ", "The half-value layer, in cm", "The mean free path, in cm"],
       "μ/ρ depends only on the composition and the photon energy, and all three are H<sub>2</sub>O. μ, the HVL in cm, and the mean free path all scale with density, which is far lower in steam than in ice or liquid water.", lvl="Easy"),
    PRN(STEM("Lead in a Co-60 beam, with the photon energy taken as 1.25 MeV.", [f"μ/ρ = {LEA[1.25][0]} cm²/g (NIST)", f"ρ = {RHO['lead']} g/cm³", f"A = {A['Pb']} g/mol,   Z = {Z['Pb']}", "N<sub>A</sub> = 6.022 × 10<sup>23</sup> mol<sup>−1</sup>"], "What is the [[atomic cross-section]] of lead?"),
        p_at, [p_el, p_zfa, p_lin], lambda v: f"{v:.3f} b" if v < 1 else f"{v:.1f} b",
        f"<sub>a</sub>μ = (μ/ρ) A / N<sub>A</sub> = {LEA[1.25][0]} × {A['Pb']} / (6.022 × 10<sup>23</sup>) = {sci(p_at * BARN, 3)} cm² = {p_at:.1f} b. Dividing by Z gives the cross-section per electron ({p_el:.3f} b), using Z in place of A gives {p_zfa:.1f} b, and leaving the density in gives {p_lin:.1f} b. Per electron, lead exceeds the Klein–Nishina {kn125:.3f} b: at this energy about {100 * (1 - p_kn):.0f}% of its attenuation comes from processes other than Compton scattering.", lvl="Moderate"),

    # ---- energy transfer and absorption
    SORT(STEM("Photons of one energy cross a material.", [], "Which [[coefficient]] sets each quantity?"), ["μ", "μ/ρ", "μ<sub>tr</sub>/ρ", "μ<sub>en</sub>/ρ"],
         [("Fraction of a narrow beam transmitted through 1 cm", 0), ("Fraction of a narrow beam transmitted through 1 g/cm²", 1), ("Kerma per unit energy fluence", 2), ("Dose per unit energy fluence under charged-particle equilibrium", 3)],
         "Transmission through a thickness in centimetres follows μ, and through a mass thickness in g/cm² follows μ/ρ. Kerma counts the energy transferred to charged particles, μ<sub>tr</sub>/ρ, and under charged-particle equilibrium the dose equals the collision kerma, which follows μ<sub>en</sub>/ρ.", lvl="Easy", mode="match", cap=1),
    # ---- beam geometry and hardening
    PR(STEM("The transmission of Cs-137 γ rays (662 keV) through concrete slabs is measured with a wide field and a detector close behind the slabs. An exponential is fitted to the readings.", [], "How does the fitted [[coefficient]] compare with the tabulated narrow-beam μ?"),
       "Smaller, because scattered photons add to the readings", ["Larger, because scattered photons are removed from the beam", "Equal, because μ depends only on the material and the energy", "Smaller, because the primary photons harden in the concrete"],
       "In a wide field, photons scattered in the slab reach a close detector, so each reading exceeds e<sup>−μx</sup> by a build-up factor that grows with thickness, and the fitted slope is less steep than μ. Removal of every scattered photon describes narrow-beam geometry, and the 662 keV photons are monoenergetic, so the primary beam cannot harden.", lvl="Moderate"),
    PR(STEM("A thick lead absorber is placed in a narrow 18 MV x-ray beam.", [], "How does the lead change the [[photon spectrum]]?"),
       f"It removes the lowest and the highest energies faster than those of {PB_LO:g} to {PB_HI:g} MeV", ["It removes the lowest energies only, as a filter does in a kilovoltage beam", "It removes all energies alike, because Compton scattering dominates in lead", "It removes the highest energies only, because pair production dominates in lead"],
       f"In lead μ/ρ falls with energy to its lowest value near {PB_MIN:g} MeV ({LEA[PB_MIN][0]} cm²/g) and then rises through pair production, to {LEA[10.0][0]} cm²/g at 10 MeV, while below 1 MeV photoelectric absorption raises it steeply. Photons at both ends of the spectrum are therefore removed faster than those in between. In water μ/ρ keeps falling with energy, so water only hardens the beam.", lvl="Challenging"),

    # ---- compounds and mixtures
    PR(STEM("Materials rich in hydrogen have more electrons per gram than other low-Z materials.", [], "What is the [[reason]]?"),
       "Hydrogen has no neutrons, so its Z/A is about 1 against about 0.5 for C, N, and O", ["A hydrogen atom carries more electrons than a carbon or oxygen atom", "Materials rich in hydrogen have a higher density than other materials", "Hydrogen has the highest effective atomic number of the light elements"],
       f"Electrons per gram are N<sub>A</sub> Z/A. Hydrogen's nucleus is a single proton, so Z/A = {zoa_el['H']:.2f}, while carbon, nitrogen, and oxygen carry about as many neutrons as protons, giving Z/A ≈ 0.50. Each hydrogen atom has fewer electrons than a carbon atom, but far less mass per electron; density does not enter a quantity per gram.", lvl="Easy"),
    PRN(STEM("Spongy bone is modelled, for illustration, as a mixture of cortical bone and water by mass. Use the table.", [f"cortical bone = {100 * FB:.0f}% by mass", f"water = {100 * (1 - FB):.0f}% by mass", "photon energy = 30 keV"], "What is the [[mass energy-absorption coefficient]] of the mixture?",
             tables=[nd.table_two(["bone", "water"], [0.02, 0.03, 0.04])]),
        q_mix, [q_mix_mean, q_mix_swap, q_mix_mu], "{:.3f} cm²/g",
        f"By the mixture rule μ<sub>en</sub>/ρ = {FB:.2f} × {sig4(BON[0.03][1])} + {1 - FB:.2f} × {sig4(WAT[0.03][1])} = {FB * BON[0.03][1]:.4f} + {(1 - FB) * WAT[0.03][1]:.4f} = {q_mix:.3f} cm²/g, {q_mix / WAT[0.03][1]:.2f} times that of water. The plain mean of the two gives {q_mix_mean:.3f}, swapping the fractions gives {q_mix_swap:.3f}, and the attenuation columns give {q_mix_mu:.3f}.", lvl="Moderate"),
    PR(STEM("At 40 keV, adipose tissue attenuates less per gram than water.", [], "What is the main [[reason]]?"),
       "Its effective atomic number is lower, so photoelectric absorption per gram is lower", [f"Its density is lower, {RHO['adipose']:.2f} g/cm³ against {RHO['water']:.2f} g/cm³", "It has fewer electrons per gram than water", "Pair production is weaker in its carbon atoms"],
       f"Adipose tissue holds more carbon and less oxygen than water, so its Z<sub>eff</sub> is about {ZE['adipose']:.1f} against {ZE['water']:.1f}, and photoelectric absorption, about Z<sup>3</sup> per gram, is lower. Its electrons per gram ({EG['adipose'] / 1e23:.2f} × 10<sup>23</sup>) match water's ({EG['water'] / 1e23:.2f} × 10<sup>23</sup>), so Compton scattering per gram is the same. Density changes μ, not μ/ρ, and pair production needs more than 1.022 MeV.", lvl="Moderate"),
    PRM(STEM("A physicist calculates μ/ρ of a new tissue-substitute plastic at 1.25 MeV from tabulated element data.", [], "Which of these are needed?"),
        ["The mass fraction of each element in the plastic", "The μ/ρ of each element at 1.25 MeV"],
        ["The density of the plastic", "The effective atomic number of the plastic", "The half-value layer of the plastic"],
        "The mixture rule needs only the weight fractions and the element values at that energy. Density turns μ/ρ into μ but does not enter μ/ρ, Z<sub>eff</sub> summarizes photoelectric absorption and is not an input, and the HVL is a result of the calculation, not an input.", lvl="Moderate"),
    PRN(STEM("A treatment planning system needs the electron density of cortical bone relative to water.", [f"density of cortical bone = {RHO['bone']} g/cm³", f"Z/A of cortical bone = {ZA_B}", f"Z/A of water = {ZA_W}"], "What is the [[relative electron density]] of cortical bone?"),
        q_red, [q_red_rho, q_red_za, q_red_div], "{:.2f}",
        f"Electrons per cm³ are ρ N<sub>A</sub> Z/A, so relative to water: {RHO['bone']} × {ZA_B} / {ZA_W} = {q_red:.2f}. The density alone ({q_red_rho:.2f}) ignores the lower Z/A of bone, the Z/A ratio alone ({q_red_za:.2f}) is the ratio per gram, and dividing by it ({q_red_div:.2f}) applies the correction the wrong way. In the Compton region μ of cortical bone is about {q_red:.2f} times that of water.", lvl="Challenging"),

    # ---- dose ratios between materials
    PR(STEM("Orthovoltage therapy carried a risk of bone necrosis that megavoltage beams largely removed.", [], "Which [[property of bone]] explains the difference?"),
       "Its calcium and phosphorus raise photoelectric absorption at low energies", ["Its density raises the energy absorbed per gram at all energies", "Its electrons per gram exceed those of soft tissue", "Its pair production is large at orthovoltage energies"],
       f"Calcium (Z = 20) and phosphorus (Z = 15) give bone a Z<sub>eff</sub> of about {ZE['bone']:.0f}, and photoelectric absorption per gram rises about as Z<sup>3</sup>, so at kilovoltage energies bone absorbs {bw(0.1):.0f} to {bw(0.03):.0f} times as much energy per gram as soft tissue. At megavoltage energies Compton scattering dominates and bone absorbs slightly less per gram. Density does not change the energy per gram, bone has fewer electrons per gram than soft tissue, and pair production needs more than 1.022 MeV.", lvl="Easy"),
    PRM(STEM("Cortical bone and water receive the same photon energy fluence, under charged-particle equilibrium.", [], "Which of these statements about the [[energy absorbed per gram]] are correct?"),
        [f"At 30 keV bone absorbs about {round(bw(0.03))} times as much as water", f"From 0.5 to 2 MeV bone absorbs about {100 * (1 - re_bw):.0f}% less than water", f"Above about {E_HI:g} MeV bone absorbs more than water"],
        [f"At 1.25 MeV bone absorbs about {RHO['bone'] / RHO['water']:.1f} times as much, the ratio of the densities", f"At 60 keV bone absorbs about {100 * (1 - re_bw):.0f}% less, as its electrons per gram suggest", f"Near 200 keV bone absorbs about {round(bw(0.03))} times as much as water"],
        f"The ratio of μ<sub>en</sub>/ρ, bone to water, is {bw(0.03):.2f} at 30 keV, {bw(0.06):.2f} at 60 keV, {bw(0.2):.2f} at 200 keV, {r_mv_lo:.3f} to {r_mv_hi:.3f} from 0.5 to 2 MeV, and {bw(10.0):.2f} at 10 MeV. Photoelectric absorption by calcium and phosphorus raises it at low energies, Compton scattering holds it near the ratio of electrons per gram ({re_bw:.3f}) at megavoltage energies, and pair production, about Z per gram, lifts it above 1 at high energies. Density changes the energy per cm³, not per gram.", lvl="Challenging"),
]

INLINE = {0: [1, 2], 1: [3], 2: [4, 5], 3: [6, 7, 8]}      # questions on the last section, and the rest, form the practice set

TERMS = ["mass thickness", "atomic attenuation coefficient", "electronic attenuation coefficient", "energy-transfer coefficient", "energy-absorption coefficient", "mixture rule", "electron density", "effective atomic number"]

TAKE = [
    ["μ (cm<sup>−1</sup>) = ρ × μ/ρ (cm²/g); μ/ρ = (N<sub>A</sub>/A) <sub>a</sub>μ = (N<sub>A</sub>Z/A) <sub>e</sub>μ; 1 b = 10<sup>−24</sup> cm².",
     "μ/ρ does not depend on density or physical state.",
     f"Per electron, water at 1.25 MeV attenuates as the Klein–Nishina cross-section, {kn125:.3f} b."],
    ["μ ≥ μ<sub>tr</sub> ≥ μ<sub>en</sub>: μ sets transmission and the HVL, μ<sub>tr</sub>/ρ kerma, and μ<sub>en</sub>/ρ the dose under charged-particle equilibrium.",
     f"Energy absorbed per interaction = hν μ<sub>en</sub>/μ: in water {r125:.2f} hν at 1.25 MeV and about {en_mu(WAT, 0.1):.2f} hν at 100 keV.",
     f"ḡ is about {G_AIR} for Co-60 in air and grows with energy and with Z."],
    ["Narrow beam: T = e<sup>−Σμ<sub>i</sub>x<sub>i</sub></sup>, in any order of layers. A broad beam transmits more, so its fitted coefficient is below μ.",
     f"A spectrum hardens with depth. Lead's μ/ρ is lowest between {PB_LO:g} and {PB_HI:g} MeV, so lead removes both ends of a high-energy spectrum."],
    ["(μ/ρ)<sub>mix</sub> = Σ w<sub>i</sub>(μ/ρ)<sub>i</sub>, by weight fraction.",
     f"Electrons per gram = N<sub>A</sub> Σ w<sub>i</sub>Z<sub>i</sub>/A<sub>i</sub>: water {EG['water'] / 1e23:.2f}, air {EG['air'] / 1e23:.2f}, cortical bone {EG['bone'] / 1e23:.2f}, lead {EG['lead'] / 1e23:.2f} × 10<sup>23</sup>.",
     f"Z<sub>eff</sub> = (Σ a<sub>i</sub>Z<sub>i</sub><sup>{M_EXP}</sup>)<sup>1/{M_EXP}</sup>: water {zw:.2f}, fat about {ZE['adipose']:.1f}, cortical bone about {ZE['bone']:.0f}."],
    ["Same energy fluence and charged-particle equilibrium: the dose ratio is the ratio of μ<sub>en</sub>/ρ.",
     f"Bone to water: about {q30:.1f} at 30 keV, {MV_R} from 0.5 to 2 MeV (electrons per gram), and above 1 beyond about {E_CROSS:.0f} MeV."],
]
