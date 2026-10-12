from blocks import *
import math

# ---------------------------------------------------------------- range and energy in water (Bortfeld 1997: R = alpha E^p, fitted to the ICRU 49 ranges up to 200 MeV)
ALPHA, PW = 0.0022, 1.77                                   # cm MeV^-p, dimensionless
PSTAR = {70: 4.080, 100: 7.718, 150: 15.77}                # CSDA ranges in liquid water, g/cm^2 (NIST PSTAR)
PSTAR_230 = 33                                             # g/cm^2, quoted to two figures
def rng(e): return ALPHA * e ** PW                         # cm of water for e in MeV
def energy(r): return (r / ALPHA) ** (1 / PW)               # MeV for a range r in cm
def margin(r): return 0.035 * r + 0.1                      # cm: 3.5% of the range plus 1 mm
def wepl(layers): return sum(t * s for t, s in layers)     # layers of (thickness in cm, relative stopping power)
RBE = 1.1

# ---------------------------------------------------------------- depth dose (Bortfeld 1997): the straggling-free curve (r − z)^(1/p − 1) + k (r − z)^(1/p),
# with k from the nuclear interactions, convolved with a Gaussian for range straggling and a 1% energy spread
BN, GN = 0.012, 0.6                                        # fluence lost to nuclear interactions per cm of water; fraction of that energy absorbed locally
KN = BN + GN * BN * PW
def sigma(r):
    e = energy(r)
    return math.hypot(0.012 * r ** 0.935, 0.01 * e * ALPHA * PW * e ** (PW - 1))
def pristine(z, r, n=64):
    """Dose at depth z (cm) of a beam of range r, per incident proton in arbitrary units. Integrated over v = (r − z')^(1/p), which removes the singularity at the end of range."""
    s = sigma(r); a = r - z
    u0, u1 = max(0.0, a - 6 * s), a + 6 * s
    if u1 <= 0: return 0.0
    v0, v1 = u0 ** (1 / PW), u1 ** (1 / PW); h = (v1 - v0) / n; tot = 0.0
    for i in range(n + 1):
        u = (v0 + i * h) ** PW
        tot += (1 if i in (0, n) else 4 if i % 2 else 2) * (1 + KN * u) * math.exp(-0.5 * ((u - a) / s) ** 2)
    return PW * tot * h / 3 / (s * math.sqrt(2 * math.pi) * (1 + BN * r))
def sobp(r_max, mod, step=0.25, sweeps=200):
    """Ranges and weights of pristine peaks whose sum is flat from r_max − mod to near r_max: nonnegative least squares by coordinate descent, normalized to a plateau of 1."""
    rs = [r_max - k * step for k in range(int(round(mod / step)) + 1)]
    grid = [r_max - mod + (mod - 0.2) * i / 79 for i in range(80)]
    M = [[pristine(z, r) for r in rs] for z in grid]
    w = [0.0] * len(rs); res = [1.0] * len(grid); hh = [sum(m[k] ** 2 for m in M) for k in range(len(rs))]
    for _ in range(sweeps):
        for k in range(len(rs)):
            new = max(0.0, w[k] + sum(m[k] * q for m, q in zip(M, res)) / hh[k])
            if new != w[k]:
                res = [q - (new - w[k]) * m[k] for m, q in zip(M, res)]; w[k] = new
    mean = sum(sum(m[k] * w[k] for k in range(len(rs))) for m in M) / len(M)
    return rs, [x / mean for x in w]
def cross(f, a, b, level):
    """Depth between a and b where f crosses level, by bisection."""
    fa = f(a) - level
    for _ in range(50):
        m = (a + b) / 2; fm = f(m) - level
        if (fm > 0) == (fa > 0): a, fa = m, fm
        else: b = m
    return (a + b) / 2

R150 = rng(150)
RS, WS = sobp(R150, 6.0)
def sobp_dose(z): return sum(x * pristine(z, r) for r, x in zip(RS, WS))
P90 = cross(sobp_dose, R150 - 8.5, R150 - 5.5, 0.9)        # proximal 90% point
D90 = cross(sobp_dose, R150 - 0.6, R150 + 0.4, 0.9)        # distal 90% point
D80 = cross(sobp_dose, R150 - 0.6, R150 + 0.4, 0.8)
Z01 = cross(sobp_dose, R150, R150 + 1.5, 0.01)             # end of the distal fall-off (1%)
ENT_SOBP = sobp_dose(0.0)
_pk = max(pristine(R150 - 0.8 + 0.005 * i, R150) for i in range(161))
ENT_PRISTINE = pristine(0.0, R150) / _pk
p90r, d90r, d80r = round(P90, 1), round(D90, 1), round(D80, 1)
e_d80 = energy(d80r)

# ---------------------------------------------------------------- numbers used in the text, the examples, and the questions
TAB = [(e, rng(e), PSTAR.get(e)) for e in (70, 150, 230)]
dev = max(abs(rng(e) / r - 1) for e, r in ((70, PSTAR[70]), (150, PSTAR[150]), (230, 32.95)))      # the 230 MeV CSDA range lies between 32.9 and 33.0 g/cm^2
r100 = rng(100); d100 = 100 * (r100 / PSTAR[100] - 1)
EX3 = [(3.0, 1.04), (1.5, 1.60), (6.0, 1.04)]
w3 = wepl(EX3); m3 = margin(w3); e3 = energy(w3 + m3)
rx_tot, rx_n = 54.0, 30
phys_fx, phys_tot = rx_tot / rx_n / RBE, rx_tot / RBE
# carbon: 430 MeV per nucleon reaches about 30 cm of water (HIT); rigidity B rho = p / (Z e)
MU, ME, MPR, CL = 931.494, 0.51099895, 938.272, 299.792458
MC12 = 12 * MU - 6 * ME                                    # C-12 nucleus, MeV
def rigidity(t, m, z): return math.sqrt(t * t + 2 * t * m) / (z * CL)        # T m for kinetic energy t (MeV), rest energy m, charge z
br_c = rigidity(430 * 12, MC12, 6)
e30 = energy(30.0); br_p = rigidity(e30, MPR, 1)

TOPIC = dict(
    id="protons", domain=6, sub="VI.B", title="Proton and ion beam therapy",
    ref=dict(aapm="TG-202, TG-224, TG-256", khan="", ford="24"),
    guide=[
        H("Depth dose and range"),
        P("A proton loses energy mainly to atomic electrons. By the Bethe expression its stopping power is proportional to z²/v², where z is the charge and v the speed of the particle, times a slowly varying logarithm. Energy loss per millimetre therefore grows as the proton slows: the dose peaks near the end of range, in the Bragg peak, and falls to nearly zero within a few millimetres."),
        P("Range straggling, the statistical spread of energy loss among protons of one energy, gives their stopping depths a standard deviation of about 1% of the range. The range is quoted at the distal 80% or 90% point; the 80% point marks the mean range of the protons, close to the CSDA range. Bortfeld fitted a power law to the ICRU 49 ranges in water up to 200 MeV."),
        EQ("R = α E<sup>p</sup>,   α = 0.0022 cm MeV<sup>−p</sup>,   p = 1.77", "E = (R / α)<sup>1/p</sup>"),
        TABLE(["Energy (MeV)", "α E<sup>p</sup> (cm)", "CSDA range, NIST PSTAR (g/cm²)"],
              [[f"{e}", f"{r:.3g}", f"{ps:.3g}" if ps else f"about {PSTAR_230}"] for e, r, ps in TAB]),
        P(f"The power law agrees with PSTAR to about {100 * dev:.0f}%. Clinical energies of about 70 MeV to 230 or 250 MeV reach about 4 cm to 33 to 38 cm of water."),
        EX("Range of a 100 MeV beam", STEM("A proton beam enters water.", ["E = 100 MeV", "α = 0.0022 cm MeV<sup>−p</sup>,   p = 1.77", f"PSTAR CSDA range = {PSTAR[100]:.2f} g/cm²"], "Find the [[range]] from the power law and compare it with PSTAR."),
           ["R = α E<sup>p</sup> = 0.0022 × 100<sup>1.77</sup>", f"100<sup>1.77</sup> = 10<sup>3.54</sup> = {100 ** PW:,.0f}", f"R = 0.0022 × {100 ** PW:,.0f} = {r100:.2f} cm"],
           f"{r100:.2f} cm, {abs(d100):.1f}% short of PSTAR. Water has a density of 1 g/cm³, so {PSTAR[100]:.2f} g/cm² is {PSTAR[100]:.2f} cm."),
        P(f"Weighted pristine peaks of several energies add up to a spread-out Bragg peak (SOBP), a plateau of uniform dose over the target that ends in the fall-off of the deepest peak. The modulation width, the length of the plateau, is usually measured between the proximal and distal 90% points; some systems use 95% proximally. In Bortfeld's model, with a 1% energy spread (σ), a 150 MeV pristine peak has {100 * ENT_PRISTINE:.0f}% of its maximum dose at the surface; every shallower peak adds entrance dose, so in the same model an SOBP {d90r - p90r:.1f} cm wide has {100 * ENT_SOBP:.0f}% of its plateau dose there, and a wider SOBP more. Measured values depend on the machine and the delivery."),
        P("The lateral penumbra widens with depth as multiple Coulomb scattering accumulates, and for a deep target it can exceed that of a megavoltage photon beam."),
        EX("Width of a spread-out peak", STEM("A calculated SOBP in water.", [f"proximal 90% dose point = {p90r:.1f} cm", f"distal 90% dose point = {d90r:.1f} cm", f"distal 80% dose point = {d80r:.1f} cm"], "Find the [[modulation width]] and the [[energy of the deepest pristine peak]], taking its range as the distal 80% depth."),
           [f"Modulation width = {d90r:.1f} − {p90r:.1f} cm", f"E = ({d80r:.1f} / 0.0022)<sup>1/1.77</sup> = {e_d80:.0f} MeV"],
           f"{d90r - p90r:.1f} cm; {e_d80:.0f} MeV."),

        H("Accelerators and beam delivery"),
        P("A cyclotron gives one fixed energy, about 230 to 250 MeV; a low-Z degrader such as graphite lowers it, and an energy selection system trims the energy spread it adds, at the cost of much of the beam and of neutrons and activation. A synchrotron accelerates each group of protons to the energy requested, with no degrader."),
        P("Passive scattering uses one scatterer for small fields such as eye treatments, or two, the second contoured, for large fields. A range modulator wheel or ridge filter builds the SOBP, an aperture shapes the field edge, and a range compensator shapes the distal dose to the far surface of the target. The modulation width is fixed across the field, so the high dose spills proximally into normal tissue."),
        P("Pencil beam scanning steers a narrow beam with magnets, spot by spot and one energy layer at a time. Spots have a σ in air of a few millimetres, smallest at the highest energy, and overlap so that their sum is flat. Scanning allows intensity-modulated proton therapy (IMPT) and robust optimization against setup and range errors in place of a PTV. A shallow target needs a range shifter, which enlarges the spots. With no scatterers in the beam, the neutron dose is lower than with passive scattering."),
        P("The interplay effect, between the motion of a breathing target and the sequence of the spots, leaves hot and underdosed regions; rescanning, gating, breath hold, or limiting the motion reduce it."),

        H("Range uncertainty and planning"),
        P("A calibration curve converts the CT number of each voxel to its relative stopping power (RSP), its stopping power divided by that of water. RSP is about 1.0 for soft tissue, 1.6 to 1.7 for cortical bone, 0.2 to 0.3 for inflated lung, and near zero for air. The water-equivalent path length (WEPL) along the beam sets where the protons stop: bone pulls the end of range toward the surface, air or lung pushes it deeper, and metal adds artifacts and an uncertain RSP."),
        EQ("WEPL = Σ RSP<sub>i</sub> × t<sub>i</sub>"),
        P("The range in the patient is uncertain by a few percent, from the CT calibration and conversion to RSP (including the mean excitation energies of tissues), the beam, setup, and anatomy that changes, such as a sinus that fills or clears (TG-202). One widely used recipe (Massachusetts General Hospital) extends the distal edge by 3.5% of the range plus 1 mm; other centres use 2.5% plus 1.5 mm or add up to 3 mm."),
        EQ("distal margin = 0.035 × R + 1 mm"),
        P("Planners avoid ending a beam immediately in front of a serial organ at risk such as the brainstem, where a range error or the higher RBE at the end of range would put dose in the organ. Beam angles place the lateral penumbra against the organ, avoid metal and interfaces along the beam, and share the target among beams that end in different places."),
        EX("Path length, margin, and energy", STEM("A proton beam reaches the distal edge of a target through three layers.", [f"soft tissue: {EX3[0][0]:.1f} cm, RSP {EX3[0][1]:.2f}", f"bone: {EX3[1][0]:.1f} cm, RSP {EX3[1][1]:.2f}", f"soft tissue: {EX3[2][0]:.1f} cm, RSP {EX3[2][1]:.2f}", "range margin: 3.5% of the range + 1 mm", "R = 0.0022 E<sup>1.77</sup> (R in cm of water, E in MeV)"],
                                                    "Find the [[WEPL]] and the [[beam energy]] that covers the distal edge with the margin."),
           [f"WEPL = 3.0 × 1.04 + 1.5 × 1.60 + 6.0 × 1.04 = {w3:.2f} cm", f"Margin = 0.035 × {w3:.2f} + 0.10 = {m3:.2f} cm, so the range needed is {w3 + m3:.2f} cm", f"E = ({w3 + m3:.2f} / 0.0022)<sup>1/1.77</sup> = {e3:.1f} MeV"],
           f"WEPL {w3:.2f} cm; about {e3:.0f} MeV."),

        H("Biological effect and carbon ions"),
        P("The relative biological effectiveness (RBE) is the ratio of the photon dose to the particle dose that gives the same effect. Following ICRU 78, proton doses use a constant RBE of 1.1 and are stated in Gy(RBE), 1.1 times the physical dose (formerly CGE, cobalt gray equivalent)."),
        EQ("D<sub>RBE</sub> = 1.1 × D,   D in Gy,   D<sub>RBE</sub> in Gy(RBE)"),
        P("The linear energy transfer (LET), the energy lost per unit path length, rises as the protons slow, and the RBE rises with it: in-vitro data average about 1.35 at the distal edge of an SOBP and 1.7 in the fall-off (Paganetti 2014; TG-256). The biologically effective range is therefore about 1 to 2 mm longer than the physical range, up to about 4 mm in some models."),
        EX("Physical dose for a prescription", STEM("A proton plan.", [f"prescription = {rx_tot:.0f} Gy(RBE) in {rx_n} fractions", "RBE = 1.1"], "Find the [[physical dose]] per fraction and in total."),
           [f"Per fraction: {rx_tot:.0f} / {rx_n} = {rx_tot / rx_n:.2f} Gy(RBE)", f"Physical dose per fraction = {rx_tot / rx_n:.2f} / 1.1 = {phys_fx:.3f} Gy", f"Total = {rx_tot:.0f} / 1.1 = {phys_tot:.1f} Gy"],
           f"{phys_fx:.2f} Gy per fraction, {phys_tot:.1f} Gy in total."),
        P(f"Carbon ions (z = 6) lose energy 36 times faster than protons of the same speed. A carbon beam that reaches 30 cm of water needs a magnetic rigidity of {br_c:.1f} T·m, nearly three times that of protons with the same range, so the synchrotron is 20 to 25 m across and a gantry far larger. Carbon ions scatter less, which sharpens the penumbra; their RBE is higher and varies along the beam, from under 2 at the entrance to 3 or more at the peak (model dependent); their oxygen enhancement ratio is lower; and nuclear fragments leave a tail of dose beyond the peak."),
    ],
    cards=[
        F("Stopping power and the Bragg peak", "The stopping power is proportional to z²/v² (Bethe), so it rises as the proton slows. The dose peaks near the end of range and falls to nearly zero beyond it."),
        F("Range straggling", "The statistical spread of energy loss gives the stopping depths a standard deviation of about 1% of the range."),
        F("Range–energy power law in water", "R = α E<sup>p</sup>, with α = 0.0022 cm MeV<sup>−p</sup> and p = 1.77 (Bortfeld).",
          w=[f"150 MeV: 0.0022 × 150<sup>1.77</sup> = {rng(150):.1f} cm, against {PSTAR[150]:.2f} g/cm² from PSTAR"]),
        F("Clinical proton energies and ranges", "About 70 MeV to 230 or 250 MeV, reaching about 4 cm to 33 to 38 cm of water."),
        F("Range at the distal 80% point", "The distal 80% point of a pristine peak lies at the mean range of the protons, close to the CSDA range."),
        F("Spread-out Bragg peak", "Pristine peaks of several energies, each weighted, summed into a uniform plateau over the target. A wider SOBP has a higher entrance dose."),
        F("Modulation width", "The length of the SOBP plateau, usually between the proximal and distal 90% dose points."),
        F("Cyclotron and synchrotron", "Cyclotron: one fixed energy, with a degrader for lower energies. Synchrotron: the energy is set for each spill, with no degrader."),
        F("Passive scattering components", "Scatterers, a range modulator wheel or ridge filter, a patient-specific aperture, and a range compensator. More neutrons reach the patient than with scanning."),
        F("Pencil beam scanning", "A narrow beam steered by magnets and delivered spot by spot in energy layers. It shapes the proximal edge of the dose as well and allows IMPT."),
        F("Interplay effect", "Target motion during spot scanning leaves hot and underdosed regions. Rescanning, gating, and breath hold reduce it."),
        F("Water-equivalent path length", "WEPL = Σ RSP × thickness along the beam. A CT calibration curve gives the RSP of each voxel."),
        F("Typical proton range margin", "3.5% of the range plus 1 mm, one widely used recipe; other centres use 2.5% plus 1.5 mm or add up to 3 mm.", w=["Range 20 cm: 0.035 × 200 mm + 1 mm = 8 mm"]),
        F("Clinical proton RBE", "A constant 1.1 (ICRU 78). Dose in Gy(RBE) = 1.1 × physical dose."),
        F("RBE at the end of range", "LET and RBE rise toward the end of range, to about 1.35 at the distal edge (in-vitro average, Paganetti 2014; TG-256). The biologically effective range is about 1 to 2 mm longer."),
        F("Carbon ions compared with protons", "A higher and variable RBE, a lower OER, less lateral scatter, a fragmentation tail beyond the peak, and a much larger accelerator."),
    ],
)

# ---------------------------------------------------------------- practice questions
q_scale = 15.6 * (120 / 150) ** PW
QW = [(4.0, 1.04), (1.5, 1.60), (6.0, 0.25)]
q_wepl = wepl(QW)
q_marg = 10 * margin(24.0)                                  # mm
q_fx = 2.0 / RBE
QE = [(5.0, 1.04), (2.0, 1.60), (7.0, 1.04)]
q_w = wepl(QE); q_e = energy(q_w + margin(q_w))
q_e_nomargin = energy(q_w); q_e_phys = energy(sum(t for t, _ in QE) + margin(sum(t for t, _ in QE))); q_e_cm = energy(1.035 * q_w + 1.0)
q_typed = 1.80 * RBE
q_distal = 1.00 / RBE * 1.35

# ---------------------------------------------------------------- the tap-the-figure question: an SOBP calculated with the model
_zs = [6 + 0.25 * i for i in range(33)] + [14 + 0.025 * i for i in range(1, 121)]
_pts = [[round(z, 3), round(100 * sobp_dose(z), 2)] for z in _zs]
FIG_X0, FIG_X1 = round(D90 - 0.1, 2), round(Z01 + 0.05, 2)
_fig = FS(x=dict(min=6, max=17, ticks=[6, 8, 10, 12, 14, 16], label="Depth in water (cm)"), y=dict(min=0, max=110, ticks=[0, 20, 40, 60, 80, 100], label="Dose (% of the plateau)", fmt="pct"),
          series=[dict(pts=_pts, color="plot-1")], xunit=" cm", xdec=1, xname="Depth", label="Depth dose of a proton SOBP in water, calculated")

PROBLEMS = [
    PR("A beam of protons of one energy enters water. Why does the dose rise to a peak near the end of the range?", "The stopping power rises as the protons slow down",
       ["Secondary electrons build up to equilibrium at that depth", "The proton fluence rises toward the end of range", "Nuclear interactions become more frequent as the protons slow"],
       "The Bethe stopping power varies as z²/v², so the energy lost per millimetre grows as the protons slow and is largest near the end of range. Electron build-up explains the d<sub>max</sub> of a photon beam, not the Bragg peak, and the proton fluence falls with depth as nuclear interactions remove protons.", lvl="Easy"),
    PR("A proton plan is prescribed in Gy(RBE). Which RBE do clinical proton plans use to convert physical dose to RBE-weighted dose?", "1.1, constant over the whole field",
       ["1.0, as for megavoltage photons", "1.1 in the plateau and 1.7 in the fall-off", "3, as for carbon ions"],
       "ICRU 78 recommends a generic RBE of 1.1, applied everywhere: D<sub>RBE</sub> = 1.1 × D. The RBE rises toward the end of range, but clinical plans do not model the rise; 1.0 is the photon reference, and values near 3 belong to carbon ions.", lvl="Easy"),
    PR("A proton beam is measured in water at several depths. How does its lateral penumbra change with depth?", "It widens, because multiple Coulomb scattering accumulates",
       ["It narrows, because the protons slow down", "It stays the same, because protons travel in straight lines", "It widens only beyond the Bragg peak, where the protons stop"],
       "Each proton is deflected by many small Coulomb scatterings, and the deflections add up along the path, so the penumbra grows with depth. For a deep target it can be wider than that of a megavoltage photon beam.", lvl="Easy"),
    PR("A proton plan is calculated on a CT scan. Which quantity does the CT calibration curve of a proton planning system give?", "Relative stopping power",
       ["Electron density relative to water", "Mass energy-absorption coefficient", "Linear attenuation coefficient at 6 MV"],
       "Where the protons stop depends on the water-equivalent path length, which needs the stopping power of each voxel relative to water. Photon planning converts CT numbers to relative electron density; a proton system converts them to RSP.", lvl="Easy"),
    PR("A spread-out Bragg peak is commissioned. How is its modulation width usually measured?", "From the proximal to the distal 90% dose point",
       ["From the surface to the distal 90% dose point", "From the distal 80% to the distal 20% dose point", "From the proximal to the distal 50% dose point"],
       "The modulation width is the length of the plateau, usually taken between the proximal and distal 90% points (some systems use 95% at the proximal end). The distal 80% to 20% distance is the width of the distal fall-off, and the surface to the distal 90% point is the range of the beam.", lvl="Easy"),
    PR("A carbon-ion beam and a proton beam have the same range in water. Which pair of properties does the carbon-ion beam have, compared with the proton beam?", "A higher RBE and less lateral scatter",
       ["A higher RBE and more lateral scatter", "A lower RBE and less lateral scatter", "The same RBE and no dose beyond the peak"],
       "Carbon ions have a higher and variable RBE, from under 2 at the entrance to 3 or more at the peak, and, being heavier, scatter less, so their penumbra is sharper. They also leave a tail of dose from nuclear fragments beyond the peak.", lvl="Easy"),
    PR("Two SOBPs have the same range, one 4 cm wide and one 10 cm wide. How does the entrance dose of the wider SOBP compare, as a fraction of its plateau dose?", "It is higher, because more shallow peaks add their entrance dose",
       ["It is lower, because the dose is spread over a longer plateau", "It is the same, because the range is the same", "It is lower, because the deepest peak carries less weight"],
       f"Each pristine peak shallower than the deepest one adds its entrance dose at the surface, so the wider the SOBP, the higher the entrance dose relative to the plateau. In Bortfeld's model a single 150 MeV peak has {100 * ENT_PRISTINE:.0f}% of its maximum at the surface and an SOBP {d90r - p90r:.1f} cm wide has {100 * ENT_SOBP:.0f}% of its plateau.", lvl="Easy"),
    PRN(STEM("A 150 MeV proton beam has a range of 15.6 cm in water.", ["R ∝ E<sup>1.77</sup>"], "What is the [[range of a 120 MeV beam]]?"), q_scale,
        [15.6 * 120 / 150, 15.6 * (120 / 150) ** (1 / PW), 15.6 * (120 / 150) ** 2], "{:.1f} cm",
        f"R = 15.6 × (120/150)<sup>1.77</sup> = 15.6 × {(120 / 150) ** PW:.4f} = {q_scale:.2f} cm. Scaling linearly gives {15.6 * 120 / 150:.1f} cm, the exponent 1/1.77 gives {15.6 * (120 / 150) ** (1 / PW):.1f} cm, and the square gives {15.6 * 0.64:.1f} cm.", lvl="Moderate"),
    PRN(STEM("A proton beam crosses three layers before the target.", [f"soft tissue: {QW[0][0]:.1f} cm, RSP {QW[0][1]:.2f}", f"bone: {QW[1][0]:.1f} cm, RSP {QW[1][1]:.2f}", f"lung: {QW[2][0]:.1f} cm, RSP {QW[2][1]:.2f}"], "What is the [[water-equivalent path length]]?"), q_wepl,
        [sum(t for t, _ in QW), sum(t / s for t, s in QW), QW[0][0] * QW[0][1] + QW[1][0] * QW[1][1] + QW[2][0]], "{:.1f} cm",
        f"WEPL = 4.0 × 1.04 + 1.5 × 1.60 + 6.0 × 0.25 = {QW[0][0] * QW[0][1]:.2f} + {QW[1][0] * QW[1][1]:.2f} + {QW[2][0] * QW[2][1]:.2f} = {q_wepl:.2f} cm. The physical depth is {sum(t for t, _ in QW):.1f} cm, treating the lung as water gives {QW[0][0] * QW[0][1] + QW[1][0] * QW[1][1] + QW[2][0]:.1f} cm, and dividing by the RSP gives {sum(t / s for t, s in QW):.1f} cm.", lvl="Moderate"),
    PRN(STEM("The distal edge of a target lies at a WEPL of 24.0 cm.", ["range margin = 3.5% of the range + 1 mm"], "What [[distal margin]] does the recipe add?"), q_marg,
        [0.035 * 240, 3.5 + 1.0, 0.035 * 240 + 10.0], "{:.1f} mm",
        f"Margin = 0.035 × 240 mm + 1 mm = {q_marg:.1f} mm. Leaving out the 1 mm gives {0.035 * 240:.1f} mm, reading 3.5% as 3.5 mm gives 4.5 mm, and adding 1 cm in place of 1 mm gives {0.035 * 240 + 10:.1f} mm. The margin covers the CT calibration, the beam, the setup, and changes in anatomy.", lvl="Moderate"),
    PRN(STEM("A proton prescription.", ["RBE-weighted dose = 70 Gy(RBE) in 35 fractions", "RBE = 1.1"], "What [[physical dose per fraction]] is delivered?"), q_fx,
        [2.0 * RBE, 2.0, 2.0 / RBE ** 2], "{:.2f} Gy",
        f"Each fraction is 70 / 35 = 2.00 Gy(RBE), and the physical dose is 2.00 / 1.1 = {q_fx:.2f} Gy. Multiplying by 1.1 gives {2.0 * RBE:.2f} Gy, ignoring the RBE gives 2.00 Gy, and dividing twice gives {2.0 / RBE ** 2:.2f} Gy.", lvl="Moderate"),
    PR("A proton beam for a skull-base tumour passes through the sphenoid sinus. At simulation the sinus was full of fluid; at a later fraction it holds air. What is the effect on the dose?", "The protons stop deeper, beyond the distal edge of the target",
       ["The protons stop shallower, short of the distal edge", "The range is unchanged, because air has almost no mass", "Only the lateral penumbra widens, and the range is unchanged"],
       "Fluid has an RSP near 1 and air near 0, so the clear sinus shortens the WEPL by about its length, and the protons travel that much farther into the tissue beyond the target. Fluid or bone added to the path would do the opposite.", lvl="Moderate"),
    PR("A liver tumour that moves 15 mm with breathing is treated with pencil beam scanning and no motion management. Which effect is the main concern specific to scanning?", "Interplay between the spot sequence and the motion, leaving hot and underdosed regions",
       ["More neutron dose from the scatterers in the nozzle", "Misalignment of the range compensator with the tumour", "A modulation width that is the same across the field"],
       "Spots are delivered one after another while the tumour moves, so some parts of it receive extra spots and others miss them. Rescanning, gating, breath hold, or limiting the motion reduce this interplay effect. Scatterers, compensators, and a fixed modulation width belong to passive scattering.", lvl="Moderate"),
    PR("A clival chordoma abuts the brainstem. In the draft plan one beam's distal edge ends immediately in front of the brainstem. Which change best protects the brainstem?", "Rotate that beam so its lateral penumbra, not its distal edge, lies against the brainstem",
       ["Increase that beam's distal margin from 3.5% + 1 mm to 3.5% + 3 mm", "Keep that beam, since its dose falls to nearly zero beyond the distal edge", "Give that beam a larger share of the dose so the other beams avoid the brainstem"],
       "A range error of a few millimetres, or the higher RBE at the end of range, would put the distal fall-off and its high dose into the brainstem. The lateral penumbra does not depend on the range, so placing it against the organ is safer. A larger distal margin pushes more dose into the brainstem.", lvl="Challenging"),
    TYPED(STEM("The distal edge of an SOBP lies at the boundary of an organ at risk.", ["planned dose at a point on the boundary = 1.00 Gy(RBE) per fraction, with RBE = 1.1", "RBE at that point = 1.35 (in-vitro average at the distal edge)"], "What would the [[RBE-weighted dose]] at that point be?"), q_distal, 0.01, "Gy(RBE)",
          f"Physical dose = 1.00 / 1.1 = {1.00 / RBE:.3f} Gy, so with RBE 1.35 the RBE-weighted dose is {1.00 / RBE:.3f} × 1.35 = {q_distal:.2f} Gy(RBE), {100 * (q_distal - 1):.0f}% more than planned. Multiplying 1.00 by 1.35 treats the RBE-weighted dose as the physical dose.", lvl="Challenging"),
]

PROBLEMS += [
    SORT("Match each part of a proton therapy system to its feature.", ["Cyclotron", "Synchrotron", "Passive scattering", "Pencil beam scanning"],
         [("One fixed energy; a degrader gives lower energies", 0), ("Energy set for each spill, with no degrader", 1), ("Range modulator wheel, aperture, and range compensator", 2), ("A narrow beam steered by magnets, spot by spot", 3)],
         "A cyclotron extracts one energy, so a degrader and an energy selection system give the lower ones. A synchrotron accelerates each group of protons to the energy requested. Passive scattering spreads and shapes a broad beam with fixed hardware, and scanning paints the target with magnetically steered spots.", lvl="Moderate", mode="match", cap=1),
    PRM("Which of these are features of pencil beam scanning compared with double scattering?", ["It can shape the high dose to the proximal edge of the target", "It produces less neutron dose from the nozzle"],
        ["It needs a range compensator for every field", "It is less sensitive to target motion", "It gives the same modulation width across the field"],
        "Scanning sets the dose of every spot, so the high dose can follow the proximal surface of the target as well as the distal one, and with no scatterers in the nozzle fewer neutrons reach the patient. Scanning is more sensitive to motion (the interplay effect), and the fixed modulation width and the compensator belong to double scattering.", lvl="Moderate"),
    PRM("A lung tumour moves 20 mm with breathing and is to be treated with pencil beam scanning. Which of these reduce the interplay effect?", ["Rescanning each energy layer several times", "Gating the beam to one phase of breathing"],
        ["Using smaller spots", "Delivering the dose in fewer fractions", "Planning on one breathing phase without gating"],
        "Rescanning spreads each layer over several passes so that the errors average out, and gating delivers the dose only while the tumour is near one position. Smaller spots and fewer fractions make the interplay effect larger, and planning on one phase does nothing about motion during delivery.", lvl="Challenging"),
]

INLINE = {0: [1, 3, 5, 8], 1: [13, 16, 17], 2: [4, 9, 10, 12]}

TERMS = ["Bragg peak", "range straggling", "spread-out Bragg peak", "pencil beam scanning", "interplay effect", "relative stopping power", "water-equivalent path length", "relative biological effectiveness"]

TAKE = [
    ["Stopping power varies as z²/v²: the dose peaks near the end of range, then falls to nearly zero.",
     "R = α E<sup>p</sup> (α = 0.0022 cm MeV<sup>−p</sup>, p = 1.77): about 4 cm of water at 70 MeV and 33 cm at 230 MeV.",
     "An SOBP is a weighted sum of pristine peaks; a wider SOBP has a higher entrance dose."],
    ["Cyclotron: one fixed energy and a degrader. Synchrotron: energy set for each spill.",
     "Passive scattering uses scatterers, a modulator, an aperture, and a compensator, and makes more neutrons. Scanning steers spots in energy layers.",
     "Scanning a moving target causes the interplay effect, reduced by rescanning, gating, or breath hold."],
    ["WEPL = Σ RSP × thickness, with the RSP from a CT calibration curve.",
     "One widely used distal margin is 3.5% of the range plus 1 mm.",
     "Planners avoid ending a beam immediately in front of a serial organ at risk."],
    ["Clinical proton RBE is 1.1: Gy(RBE) = 1.1 × Gy.",
     "LET and RBE rise at the distal end, extending the effective range by about 1 to 2 mm.",
     "Carbon ions: higher RBE, lower OER, less scatter, a fragmentation tail, and a far larger accelerator."],
]
