from blocks import *
import math

# ---------------------------------------------------------------- constants quoted in the text
HC = 1.2398                                   # keV nm
K_BR = 9e-10                                  # bremsstrahlung efficiency constant, per volt (sources give 0.9 to 1.1 × 10^-9)
Z_W, Z_MO = 74, 42
LN2 = math.log(2.0)
AL = {20: 3.441, 30: 1.128, 40: 0.5685, 50: 0.3681}         # aluminium μ/ρ (cm²/g) against photon energy (keV), NIST
CU = {60: 1.593, 80: 0.7630, 100: 0.4584, 150: 0.2217}      # copper μ/ρ (cm²/g) against photon energy (keV), NIST
RHO_AL, RHO_CU = 2.699, 8.96                                 # g/cm³
F_1PH, F_6P, F_12P = 1.0, 1.35, 1.41                         # heat-unit waveform factors

# ---------------------------------------------------------------- formulas
def lam_min(kvp):
    """Duane–Hunt limit in nm for a peak voltage in kV."""
    return HC / kvp

def eff(Z, volts):
    """Fraction of the electron beam energy radiated as bremsstrahlung in a thick target."""
    return K_BR * Z * volts

def spot(L, deg):
    """Effective focal spot (line-focus principle): actual length times sin of the anode angle."""
    return L * math.sin(math.radians(deg))

def heat_units(kvp, ma, s, f):
    return kvp * ma * s * f

def ripple(p):
    """Ripple of an ideal rectified supply with p pulses per cycle: it dips to cos(180°/p) of the peak."""
    return 1.0 - math.cos(math.pi / p)

def x_at(level, x1, r1, x2, r2):
    """Thickness at which the reading falls to `level`, interpolating ln(reading) linearly between two measured points."""
    return x1 + (x2 - x1) * math.log(r1 / level) / math.log(r1 / r2)

def hc_coef(x50, x25):
    """Homogeneity coefficient from the thicknesses that leave 50% and 25%."""
    return x50 / (x25 - x50)

def mu_rho(hvl_mm, rho, k=LN2):
    """Mass attenuation coefficient (cm²/g) of a monoenergetic beam with this first HVL (mm)."""
    return k / (hvl_mm / 10.0) / rho

def n_of(a, b, tab):
    """Local power-law exponent of μ/ρ ∝ E^−n between two tabulated energies."""
    return math.log(tab[a] / tab[b]) / math.log(b / a)

def e_of(mr, tab):
    """Energy (keV) whose μ/ρ equals mr, interpolating ln(μ/ρ) linearly in ln E between the bracketing table entries."""
    es = sorted(tab)
    for a, b in zip(es, es[1:]):
        if tab[b] <= mr <= tab[a]:
            return a * (tab[a] / mr) ** (1.0 / n_of(a, b, tab))
    raise ValueError(mr)

# ---------------------------------------------------------------- worked examples
V1, I1 = 250e3, 15e-3                          # V, A
E1 = V1 / 1e3; lam1 = lam_min(E1); eff1 = eff(Z_W, V1); P1 = V1 * I1; Px1 = eff1 * P1
eff100 = eff(Z_W, 100e3)
L2, TH2 = 5.0, 12.0; s2 = spot(L2, TH2)
hu3 = heat_units(120, 250, 15, F_12P); J3 = 120 * 250 * 15; eff3 = eff(Z_W, 120e3)
x50_4, x25_4 = 2.0, 4.4
hvl2_4 = x25_4 - x50_4; hc4 = hc_coef(x50_4, x25_4); mu4 = LN2 / (x50_4 / 10.0); mr4 = mu4 / RHO_CU; n4 = n_of(100, 150, CU); E4 = e_of(mr4, CU)
c30, c15 = math.cos(math.radians(30)), math.cos(math.radians(15))

TOPIC = dict(
    id="xray-tube", domain=1, sub="I.C", title="Kilovoltage x-ray production",
    ref=dict(aapm="TG-61", khan="", ford="8"),
    guide=[
        H("Bremsstrahlung and characteristic radiation"),
        P("Electrons from the heated cathode are accelerated through the tube voltage V and strike the anode with kinetic energy eV; most of it ionizes and excites target atoms and ends as heat. A small part is radiated as bremsstrahlung: an electron deflected by the field of a nucleus emits a photon of any energy up to its kinetic energy, so the spectrum ends at E<sub>max</sub> = eV, the kVp in keV (the Duane–Hunt law)."),
        EQ("E<sub>max</sub> (keV) = kVp", f"λ<sub>min</sub> = hc / E<sub>max</sub>,   λ<sub>min</sub> (nm) = {HC} / kVp   (hc = {HC} keV nm)"),
        P(f"The radiated fraction rises with the atomic number Z of the target and with the voltage, so at a fixed current the x-ray power rises as V². For tungsten (Z = 74) it is about {100 * eff100:.1f}% at 100 kV and {100 * eff(Z_W, 250e3):.1f}% at 250 kV; the rest heats the anode."),
        EQ("efficiency ≈ k Z V   (V in volts)", "k ≈ 9 × 10<sup>−10</sup> V<sup>−1</sup>   (sources give 0.9 to 1.1 × 10<sup>−9</sup>)", "x-ray power = efficiency × V I ≈ k Z I V²"),
        P("A thick target acts as a stack of thin layers, each giving an energy fluence spectrum that is flat up to the energy of the electrons reaching it, which falls with depth. Before any filtration the sum is a triangle: the energy fluence per unit energy falls in a straight line to zero at E<sub>max</sub> (Kramers' law, I(E) ∝ Z (E<sub>max</sub> − E))."),
        P("Characteristic x-rays are lines on this continuum, emitted when an inner-shell vacancy made by an incident electron is filled. Their energies are set by the anode material, not by the kVp, and K lines need eV above the K-shell binding energy: tungsten (69.5 keV) gives Kα at 58.0 and 59.3 keV and Kβ at 67 to 69 keV only above about 70 kVp. Molybdenum (Kα 17.5 keV) and rhodium (Kα 20.2 keV) anodes serve mammography."),
        EX("Energies and efficiency at 250 kV", STEM("An orthovoltage tube with a tungsten anode runs at constant potential.", ["tube voltage = 250 kV", "tube current = 15 mA", "Z = 74", "efficiency = 9 × 10<sup>−10</sup> Z V, with V in volts"],
                                                     "Find the [[maximum photon energy]], the [[minimum wavelength]], and the [[x-ray power]]."),
           [f"E<sub>max</sub> = e × 250 kV = {E1:.0f} keV", f"λ<sub>min</sub> = {HC} keV nm / {E1:.0f} keV = {lam1:.5f} nm = {1000 * lam1:.2f} pm",
            f"efficiency = 9 × 10<sup>−10</sup> × 74 × 250,000 = {eff1:.5f}", f"beam power = 250 kV × 15 mA = {P1:,.0f} W", f"x-ray power = {eff1:.5f} × {P1:,.0f} W = {Px1:.1f} W"],
           f"{E1:.0f} keV, {lam1:.5f} nm, and {Px1:.0f} W of x-rays; the other {P1 - Px1:,.0f} W, {100 * (1 - eff1):.1f}% of the power, heats the anode."),

        H("Tube, focal spot, and heel effect"),
        P("A filament current heats the cathode, a tungsten coil, until electrons escape from it (thermionic emission), so the filament temperature sets the mA. At low tube voltage the emitted electrons form a space charge around the filament that limits the current; at higher voltage all of them reach the anode and the current saturates."),
        TABLE(["Part", "Design", "Purpose"], [
            ["Focusing cup", "Metal cup around the filament at the cathode potential", "Aims the electrons at the focal spot"],
            ["Anode", "Tungsten with 5 to 10% rhenium in the focal track; molybdenum or rhodium for mammography", "High Z for bremsstrahlung yield; melting point 3,422 °C"],
            ["Rotating anode", "Disc spinning at about 3,000 to 10,000 rpm", "Spreads the heat around a circular focal track"],
            ["Stationary anode", "Tungsten target set in copper, cooled by circulating oil or water", "Long exposures at modest power, as in kV therapy"],
            ["Envelope", "Evacuated glass or metal", "Electrons reach the anode without striking gas"],
            ["Oil and housing", "Oil bath inside a lead-lined housing", "Insulation and cooling; leakage of a diagnostic tube at most 0.88 mGy air kerma in 1 h at 1 m (21 CFR 1020.30)"],
            ["Window", "Thin glass, or beryllium in low-kV tubes", "Lets the beam out with little filtration"]]),
            PHOTO("xray-tube-anode"),
        P("The anode face makes a small angle θ, typically 7° to 20°, with the central ray. Viewed along the central ray, the strip of length L that the electrons strike is foreshortened to L sin θ (the line-focus principle). A smaller angle gives a smaller effective spot for the same heat load but covers a smaller field, since rays more than θ from the central ray on the anode side run into the anode."),
        EQ("effective focal spot = actual focal spot length × sin θ"),
        EX("Effective focal spot", STEM("A diagnostic tube.", [f"actual focal spot length = {L2:.1f} mm", f"anode angle θ = {TH2:.0f}°"], "Find the [[effective focal spot size]] along the central ray."),
           [f"sin {TH2:.0f}° = {math.sin(math.radians(TH2)):.4f}", f"effective = {L2:.1f} mm × {math.sin(math.radians(TH2)):.4f} = {s2:.2f} mm"],
           f"{s2:.2f} mm, about one fifth of the actual length, while the heat spreads over the full {L2:.1f} mm strip."),
        P("Photons heading toward the anode side of the field cross more anode metal, so the intensity falls toward that side: the heel effect. It is stronger with a smaller anode angle, a larger field, and a shorter source-to-image distance, so the thicker part of the patient goes on the cathode side."),
        P("Electrons scattered back from the focal spot onto other parts of the anode make off-focus radiation, which a collimator close to the focal spot reduces. Anode heating is counted in heat units (HU), with a factor f for the generator waveform."),
        EQ("HU = kVp × mA × s × f", f"f = {F_1PH:.1f} single-phase,   {F_6P} three-phase six-pulse,   {F_12P} three-phase twelve-pulse or high-frequency (some sources: 1.45)",
           f"constant potential: energy (J) = kVp × mA × s, so 1 HU ≈ 1/{F_12P} J = {1 / F_12P:.2f} J"),
        EX("Heat units of a CT simulation scan", STEM("A CT simulator with a high-frequency generator.", ["120 kVp, 250 mA", "total beam-on time = 15 s", f"waveform factor f = {F_12P}"], "Find the [[heat units]] and the [[energy]] delivered to the anode."),
           [f"HU = 120 × 250 × 15 × {F_12P} = {hu3:,.0f} HU", f"energy = 120 kV × 250 mA × 15 s = {J3:,.0f} J",
            f"efficiency = 9 × 10<sup>−10</sup> × 74 × 120,000 = {100 * eff3:.2f}%, so {J3 * (1 - eff3) / 1000:.0f} kJ stays in the anode as heat"],
           f"{hu3:,.0f} HU, from {J3 / 1000:.0f} kJ of electrical energy, nearly all of it heat."),

        H("Filtration, technique, and waveform"),
        P("Inherent filtration, in the target, envelope, oil, and window, amounts to about 0.5 to 1 mm of aluminium. Added filtration is aluminium for diagnostic and superficial beams and copper, backed by aluminium, for orthovoltage beams; US rules require at least 2.5 mm of aluminium in total above 70 kVp. A filter absorbs low-energy photons far more than high-energy ones, so it lowers the output and raises the mean energy and the HVL (beam hardening), leaving E<sub>max</sub> unchanged. In a Thoraeus filter of tin, copper, and aluminium, in that order from the tube, each layer absorbs the characteristic x-rays of the one before."),
        P("Raising the kVp raises E<sub>max</sub>, the mean energy, and the output, which grows about as kVp² and faster in a filtered beam. Raising the mA or the time multiplies the photons at every energy without changing the shape of the spectrum."),
        P(f"Between its peaks a rectified supply with p pulses per cycle falls, in principle, to cos(180°/p) of the peak: to zero for single-phase full-wave (p = 2, {100 * ripple(2):.0f}% ripple), {100 * c30:.0f}% for three-phase six-pulse ({100 * ripple(6):.0f}% ripple), and {100 * c15:.0f}% for twelve-pulse ({100 * ripple(12):.0f}% ripple); a high-frequency generator is nearly constant. At the same kVp and mAs, less ripple gives more output and a higher mean energy."),

        H("Half-value layer and kV therapy"),
        P("Beam quality is stated as the half-value layer with the kVp, measured with an ion chamber in narrow-beam geometry: in aluminium for diagnostic and superficial beams, in copper for orthovoltage beams. Copper attenuates far more, so an HVL of 1 mm Cu marks a much more penetrating beam than one of a few millimetres of aluminium. Each layer removes the softest photons left, so the second HVL, the extra thickness from 50% to 25%, exceeds the first; their ratio, the homogeneity coefficient, is 1 for a monoenergetic beam and below 1 for a spectrum."),
        EQ("HVL<sub>1</sub> = x<sub>50%</sub>,   HVL<sub>2</sub> = x<sub>25%</sub> − x<sub>50%</sub>", "HC = HVL<sub>1</sub> / HVL<sub>2</sub>", "μ<sub>eff</sub> = ln 2 / HVL<sub>1</sub>"),
        P("The effective energy is the energy of a monoenergetic beam with the same first HVL, found by matching μ<sub>eff</sub>/ρ to tabulated narrow-beam values of μ/ρ. For a filtered beam it is about one third to one half of the peak energy."),
        EX("HVL, homogeneity, and effective energy", STEM("A 250 kVp orthovoltage beam is measured in narrow-beam geometry with copper added.",
                                                          [f"reading falls to 50% behind {x50_4:.1f} mm Cu", f"reading falls to 25% behind {x25_4:.1f} mm Cu", f"copper: ρ = {RHO_CU} g/cm³", f"μ/ρ = {CU[100]} cm²/g at 100 keV and {CU[150]} cm²/g at 150 keV (NIST)"],
                                                          "Find [[HVL<sub>1</sub>]], [[HVL<sub>2</sub>]], the [[homogeneity coefficient]], and the [[effective energy]]."),
           [f"HVL<sub>1</sub> = {x50_4:.1f} mm Cu; HVL<sub>2</sub> = {x25_4:.1f} − {x50_4:.1f} = {hvl2_4:.1f} mm Cu", f"HC = {x50_4:.1f} / {hvl2_4:.1f} = {hc4:.2f}",
            f"μ<sub>eff</sub> = ln 2 / {x50_4 / 10:.2f} cm = {mu4:.3f} cm<sup>−1</sup>; μ<sub>eff</sub>/ρ = {mu4:.3f} / {RHO_CU} = {mr4:.4f} cm²/g, between the 100 and 150 keV values",
            f"On a log–log scale μ/ρ ∝ E<sup>−n</sup>, with n = ln({CU[100]} / {CU[150]}) / ln(150 / 100) = {n4:.3f}", f"E = 100 keV × ({CU[100]} / {mr4:.4f})<sup>1/{n4:.3f}</sup> = {E4:.1f} keV"],
           f"HVL<sub>1</sub> = {x50_4:.1f} mm Cu, HVL<sub>2</sub> = {hvl2_4:.1f} mm Cu, HC = {hc4:.2f}, and an effective energy of about {E4:.0f} keV, {E4 / 250:.2f} of the peak."),
        TABLE(["Beam", "Tube voltage and SSD", "Typical HVL"], [
            ["Grenz rays", "Below 20 kV", "A few hundredths of a mm Al"],
            ["Contact therapy", "40 to 50 kV, SSD 2 cm or less", "About 0.3 to 1.5 mm Al"],
            ["Superficial therapy", "50 to 150 kV, SSD 15 to 20 cm", "1 to 8 mm Al"],
            ["Orthovoltage therapy", "150 to 500 kV (mostly 200 to 300 kV), SSD 30 to 50 cm", "About 0.5 to 4 mm Cu"]]),
        P("AAPM TG-61 calibrates 40 to 300 kV beams with an ion chamber calibrated in air kerma (N<sub>K</sub>) at a matching kVp and HVL. For points at or near the surface, the in-air method measures free in air and converts to dose to water at the surface with a backscatter factor and a water-to-air ratio of mass energy-absorption coefficients. For 100 kV and above, the in-phantom method measures at 2 cm depth in water."),
        EQ("D<sub>w,z=0</sub> = M N<sub>K</sub> B<sub>w</sub> P<sub>stem,air</sub> [(μ̄<sub>en</sub>/ρ)<sup>w</sup><sub>air</sub>]<sub>air</sub>", "M: corrected reading,   B<sub>w</sub>: backscatter factor,   P<sub>stem,air</sub>: chamber stem correction"),
    ],
    cards=[
        F("Bremsstrahlung", "Photons emitted by electrons deflected in the field of a nucleus: a continuous spectrum from zero up to the electron's kinetic energy."),
        F("Maximum energy and minimum wavelength", f"E<sub>max</sub> = eV, the kVp in keV; λ<sub>min</sub> (nm) = {HC} / kVp (Duane–Hunt law).", w=[f"80 kVp: λ<sub>min</sub> = {HC} / 80 = {lam_min(80):.4f} nm"]),
        F("Efficiency of x-ray production", "About 9 × 10<sup>−10</sup> Z V, with V in volts: under 1% for tungsten at diagnostic voltages. The rest of the beam energy becomes heat.",
          w=[f"Tungsten at 100 kV: 9 × 10<sup>−10</sup> × 74 × 10<sup>5</sup> = {100 * eff100:.2f}%"]),
        F("Unfiltered thick-target spectrum", "A triangle: the energy fluence per unit energy falls in a straight line to zero at E<sub>max</sub> (Kramers' law)."),
        F("Characteristic x-ray lines", "Energies set by the binding energies of the anode, not by the kVp. Tungsten K lines (Kα 58 to 59 keV) need more than 69.5 kV."),
        F("Filament and tube current", "The filament temperature sets the mA (thermionic emission). At low kV the space charge limits the current; at higher kV it saturates."),
        F("Rotating anode", "A tungsten–rhenium track on a disc spinning at about 3,000 to 10,000 rpm spreads the heat, so a small focal spot takes a high power."),
        F("Line-focus principle", "Effective focal spot = actual length × sin θ. A smaller anode angle gives a smaller spot but covers a smaller field.", w=[f"{L2:.1f} mm × sin {TH2:.0f}° = {s2:.2f} mm"]),
        F("Heel effect", "Lower intensity toward the anode side, from the longer path through the anode. Stronger with a smaller anode angle, a larger field, and a shorter distance; the thick body part goes toward the cathode."),
        F("Heat units", f"HU = kVp × mA × s × f, with f = {F_1PH:.1f} single-phase, {F_6P} three-phase six-pulse, {F_12P} twelve-pulse or high-frequency. 1 HU ≈ {1 / F_12P:.2f} J."),
        F("Effect of added filtration", "The output falls; the mean energy and the HVL rise (beam hardening); E<sub>max</sub> is unchanged."),
        F("kVp and mA", "kVp raises E<sub>max</sub>, the mean energy, and the output (about as kVp²). mA multiplies the photons at every energy."),
        F("Homogeneity coefficient", "HVL<sub>1</sub> / HVL<sub>2</sub>, with HVL<sub>2</sub> the extra thickness from 50% to 25%: 1 for a monoenergetic beam, below 1 for a spectrum.",
          w=[f"50% at {x50_4:.1f} mm Cu, 25% at {x25_4:.1f} mm Cu: HC = {x50_4:.1f} / {hvl2_4:.1f} = {hc4:.2f}"]),
        F("Effective energy", "The energy of a monoenergetic beam with the same first HVL: about one third to one half of the peak for a filtered beam."),
        F("Kilovoltage therapy beams", ["Grenz rays: below 20 kV", "Contact: 40 to 50 kV, SSD 2 cm or less", "Superficial: 50 to 150 kV, HVL 1 to 8 mm Al", "Orthovoltage: 150 to 500 kV, HVL about 0.5 to 4 mm Cu"]),
        F("TG-61 calibration methods", "In-air method, with a backscatter factor, for points at or near the surface; in-phantom method at 2 cm depth for 100 kV and above."),
    ],
)

# ---------------------------------------------------------------- practice questions
q_lam = lam_min(80)
q_px = eff(Z_W, 200e3) * 200e3 * 20e-3
s10, cs10 = math.sin(math.radians(10)), math.cos(math.radians(10))
q_spot = spot(6.0, 10.0)
q_shrink = math.sin(math.radians(10)) / math.sin(math.radians(16))
q_hu = heat_units(80, 300, 0.20, F_6P); q_hu0 = heat_units(80, 300, 0.20, F_1PH); q_hu12 = heat_units(80, 300, 0.20, F_12P); q_hudiv = q_hu0 / F_6P
q_hc = hc_coef(2.5, 6.0)
q_mu = LN2 / 0.30; q_mr = mu_rho(3.0, RHO_AL); q_n = n_of(30, 40, AL)
q_E = e_of(q_mr, AL); q_E_nd = e_of(mu_rho(3.0, 1.0), AL); q_E_l10 = e_of(mu_rho(3.0, RHO_AL, math.log10(2.0)), AL)
q_x50 = x_at(50.0, 2.0, 54.5, 3.0, 45.2); q_x50_lin = 2.0 + (54.5 - 50.0) / (54.5 - 45.2); q_x50_one = 2.0 * LN2 / math.log(100.0 / 54.5)
RANK = [("HVL 2 mm Al", e_of(mu_rho(2.0, RHO_AL), AL)), ("HVL 4 mm Al", e_of(mu_rho(4.0, RHO_AL), AL)),
        ("HVL 1 mm Cu", e_of(mu_rho(1.0, RHO_CU), CU)), ("HVL 3 mm Cu", e_of(mu_rho(3.0, RHO_CU), CU))]
assert [x[1] for x in RANK] == sorted(x[1] for x in RANK)
AL_TABLE = DT(f"Aluminium, ρ = {RHO_AL} g/cm³: narrow-beam μ/ρ (NIST)", ["Energy (keV)", "μ/ρ (cm²/g)"], [[f"{e}", f"{AL[e]:g}"] for e in sorted(AL)])

PROBLEMS = [
    # ---- production
    PR(STEM("An x-ray tube runs at a set kVp, mA, and filtration.", [], "What sets the [[maximum photon energy]] in its beam?"),
       "The peak tube voltage", ["The atomic number of the anode", "The tube current", "The added filtration"],
       "An electron accelerated through the tube voltage V gains eV, and one bremsstrahlung photon can carry at most all of it, so E<sub>max</sub> in keV equals the kVp. The anode's Z sets the yield and the line energies, the mA the number of photons, and the filtration the low-energy end of the spectrum.", lvl="Easy"),
    PR(STEM("Electrons strike a thick tungsten target, and no filtration is in the beam.", [], "What is the [[shape]] of the bremsstrahlung energy fluence per unit energy?"),
       "A straight line falling to zero at the peak energy", ["A straight line rising to a maximum at the peak energy", "A flat line from zero up to the peak energy", "A hump that peaks near one third of the peak energy"],
       "A thick target acts as a stack of thin layers, each giving a flat spectrum up to the energy of the electrons that reach it, and the sum is a triangle that falls to zero at E<sub>max</sub> (Kramers' law). A flat spectrum belongs to a thin target, and the hump appears only after filtration removes the low energies.", lvl="Easy"),
    PRN(STEM("A diagnostic tube runs at 80 kVp.", [f"hc = {HC} keV nm"], "What is the [[minimum wavelength]] in its spectrum?"), q_lam, [3 * q_lam, HC * 80, 10 * q_lam], lambda v: f"{v:.3g} nm",
        f"λ<sub>min</sub> = hc / E<sub>max</sub> = {HC} keV nm / 80 keV = {q_lam:.4f} nm. Using one third of the peak energy, as for the effective energy, gives {3 * q_lam:.4f} nm, and multiplying in place of dividing gives {HC * 80:.1f} nm.", lvl="Moderate"),
    PR(STEM("The tungsten anode of a tube operated at 100 kVp is replaced by a molybdenum anode. The kVp and mA are unchanged.", [f"tungsten: Z = {Z_W}", f"molybdenum: Z = {Z_MO}"], "How does the [[spectrum]] change?"),
       "The lines move to lower energies and the bremsstrahlung output falls", ["The maximum energy falls to the molybdenum K-shell energy", "The lines stay where they were and the bremsstrahlung output falls", "The lines move to lower energies and the bremsstrahlung output rises"],
       f"Line energies are set by the binding energies of the target: molybdenum Kα is 17.5 keV against 58 to 59 keV for tungsten. The bremsstrahlung efficiency is proportional to Z, so the output falls to {Z_MO}/{Z_W} = {Z_MO / Z_W:.2f} of the tungsten value. The maximum energy still equals the kVp, since it depends only on the voltage.", lvl="Moderate"),
    TYPED(STEM("An orthovoltage tube with a tungsten anode runs at constant potential.", ["tube voltage = 200 kV", "tube current = 20 mA", f"Z = {Z_W}", "efficiency = 9 × 10<sup>−10</sup> Z V, with V in volts"], "What [[power]] leaves the anode as x-rays?"), q_px, 0.02, "W",
          f"The efficiency is 9 × 10<sup>−10</sup> × 74 × 200,000 = {eff(Z_W, 200e3):.5f} and the beam power is 200 kV × 20 mA = {200e3 * 20e-3:,.0f} W, so {q_px:.1f} W leaves as x-rays and the other {200e3 * 20e-3 - q_px:,.0f} W heats the anode. Putting V in kilovolts gives a power a thousand times too small.",
          w=[f"efficiency = 9 × 10<sup>−10</sup> × 74 × 2.0 × 10<sup>5</sup> = {eff(Z_W, 200e3):.5f}", f"beam power = 200 kV × 20 mA = {200e3 * 20e-3:,.0f} W", f"x-ray power = {eff(Z_W, 200e3):.5f} × {200e3 * 20e-3:,.0f} W = {q_px:.1f} W"], lvl="Moderate"),

    # ---- the tube
    PR(STEM("Most diagnostic tubes have a rotating anode.", [], "What does the [[rotation]] achieve?"),
       "It spreads the heat around a circular track, so a small focal spot takes a high power", ["It shrinks the effective focal spot below the size set by the anode angle", "It removes the heel effect by averaging over the face of the anode", "It raises the efficiency of bremsstrahlung production in the target"],
       "The electrons strike a fixed point in space while the disc turns beneath it, so the heat is shared by a circular track many times longer than the spot. The effective focal spot is still the actual spot times sin θ, the heel effect still follows the anode angle, and the efficiency still depends on Z and V.", lvl="Easy"),
    SORT("Match each part of an x-ray tube to its purpose.", ["Filament", "Focusing cup", "Rotating anode", "Evacuated envelope", "Oil bath"],
         [("Releases electrons when heated", 0), ("Aims the electrons at the focal spot", 1), ("Spreads the heat around a circular track", 2), ("Lets the electrons reach the anode without striking gas", 3), ("Insulates the high voltage and carries heat away", 4)],
         "The filament releases electrons by thermionic emission, the focusing cup shapes them into a beam aimed at the focal spot, the rotating anode shares the heat over a ring, the vacuum lets the electrons cross the gap freely, and the oil insulates and cools.", lvl="Easy", mode="match", cap=1),
    PRN(STEM("A tube has a small anode angle.", ["actual focal spot length = 6.0 mm", "anode angle θ = 10°"], "What is the [[effective focal spot size]] along the central ray?"), q_spot, [6.0 * cs10, 6.0 / s10, 2 * q_spot], "{:.2f} mm",
        f"Effective = L sin θ = 6.0 × {s10:.4f} = {q_spot:.2f} mm. Using cos θ gives {6.0 * cs10:.2f} mm, the strip seen almost side-on, and dividing by sin θ gives {6.0 / s10:.2f} mm, the actual length that a 6.0 mm effective spot would need.", lvl="Moderate"),
    PRN(STEM("An exposure is made with a three-phase six-pulse generator.", ["80 kVp", "300 mA", "0.20 s"], "How many [[heat units]] does it produce?"), q_hu, [q_hu0, q_hu12, q_hudiv], lambda v: f"{v:,.0f} HU",
        f"HU = kVp × mA × s × f = 80 × 300 × 0.20 × {F_6P} = {q_hu:,.0f} HU. Leaving out the factor gives {q_hu0:,.0f} HU, the single-phase value; {F_12P} belongs to twelve-pulse and high-frequency generators ({q_hu12:,.0f} HU); and dividing by {F_6P} gives {q_hudiv:,.0f} HU.", lvl="Moderate"),
    PRM(STEM("A radiograph shows a heel effect across the field.", [], "Which of these make the [[heel effect]] stronger?"),
        ["A smaller anode angle", "A shorter source-to-image distance"], ["A smaller field at the image receptor", "A longer source-to-image distance", "A higher tube current"],
        "The heel effect comes from the longer path through the anode for rays leaving toward the anode side, and that path grows as the anode angle falls. A shorter distance or a larger field uses rays farther from the central ray, where the loss is larger; a smaller field or a longer distance uses only the central part of the beam. The tube current scales the whole field in proportion.", lvl="Moderate"),
    PR(STEM("A body part is radiographed with its long axis along the anode–cathode axis of the tube.", ["thickness at one end of the field = 20 cm", "thickness at the other end = 12 cm"], "Where should the [[cathode end]] of the tube be placed?"),
       "Over the 20 cm end, where the beam is more intense", ["Over the 12 cm end, where the beam is more intense", "Over the 12 cm end, so the harder anode-side photons cross the 20 cm end", "At either end, since the heel effect is symmetric about the central ray"],
       "The intensity falls toward the anode side, so the thicker end goes on the cathode side and the exposure at the receptor evens out; in mammography the cathode faces the chest wall for the same reason. The photons on the anode side are slightly harder, but their lower intensity outweighs that.", lvl="Challenging"),
    PR(STEM("A tube is replaced by one with a smaller anode angle and the same actual focal spot length.", ["old anode angle = 16°", "new anode angle = 10°"], "How do the [[effective focal spot, the field covered, and the heel effect]] change?"),
       "The spot shrinks, the field covered shrinks, and the heel effect grows", ["The spot grows, the field covered grows, and the heel effect shrinks", "The spot shrinks, the field covered grows, and the heel effect shrinks", "The spot shrinks, and the field covered and the heel effect stay the same"],
       f"The effective spot scales as sin θ: sin 10° / sin 16° = {q_shrink:.2f}, so it is {100 * (1 - q_shrink):.0f}% smaller. Rays more than θ from the central ray on the anode side run into the anode, so the field covered shrinks, and rays toward the anode side cross more anode metal, so the heel effect grows. A smaller spot does not come with a larger field.", lvl="Challenging"),

    # ---- filtration, technique, and waveform
    PR(STEM("Two generators make exposures at the same kVp and mAs, one single-phase and one high-frequency.", [], "How does the [[high-frequency beam]] compare?"),
       "More output and a higher mean energy", ["The same output and the same mean energy", "The same output and a higher maximum energy", "More output at the same mean energy"],
       f"A single-phase supply falls to zero twice in each cycle ({100 * ripple(2):.0f}% ripple), so much of the exposure is made below the peak voltage, where fewer and softer photons are made. A high-frequency generator stays near the peak, so more photons are made and their mean energy is higher. The maximum energy is the kVp in both.", lvl="Easy"),
    PRM(STEM("The first HVL of an x-ray beam is measured before and after a change.", [], "Which of these [[raise the first HVL]]?"),
        ["Raising the kVp", "Adding copper filtration"], ["Raising the tube current", "Lengthening the exposure time", "Using the larger focal spot"],
        "Raising the kVp adds higher-energy photons and filtration removes low-energy ones, so both raise the mean energy and the HVL. The tube current and the time multiply the photons at every energy without changing the shape of the spectrum, and the focal spot size changes the sharpness of the image, not the spectrum.", lvl="Easy"),
    PR(STEM("An extra 2 mm of aluminium is placed in a 100 kVp beam. The kVp and mAs are unchanged.", [], "What happens to the [[output and the HVL]]?"),
       "The output falls and the HVL rises", ["The output rises and the HVL rises", "The output falls and the HVL falls", "The output falls and the HVL stays the same"],
       "The filter absorbs low-energy photons far more than high-energy ones, so fewer photons get through, and those left have a higher mean energy and penetrate further. Treating filtration as a uniform loss leaves the HVL unchanged, which holds only for a monoenergetic beam.", lvl="Moderate"),
    PRM(STEM("A technique is changed from 80 kVp to 100 kVp with the same mA, time, and filtration.", [], "Which of these [[change]]?"),
        ["The maximum photon energy", "The output per mAs", "The first HVL"], ["The energies of the tungsten K lines", "The inherent filtration of the tube", "The ratio of effective to actual focal spot size"],
        f"The maximum energy rises from 80 to 100 keV, the output rises about as kVp², by (100/80)² = {(100 / 80) ** 2:.2f} or more, and the added high-energy photons raise the HVL. The K lines stay at 58 to 69 keV because the binding energies of tungsten do not change, the inherent filtration is part of the tube, and the effective spot is the actual spot times sin θ.", lvl="Moderate"),

    # ---- beam quality and kV therapy
    PR(STEM("A 250 kV orthovoltage beam is commissioned for treatment.", [], "How is its [[beam quality]] usually specified?"),
       "By its HVL in millimetres of copper, with the kVp", ["By its HVL in millimetres of lead, with the kVp", "By its percentage depth dose at 10 cm, %dd(10)<sub>x</sub>", "By its tube current and its exposure time"],
       "Orthovoltage beams are specified by a copper HVL together with the kVp; aluminium serves for diagnostic and superficial beams. %dd(10)<sub>x</sub> is the TG-51 specifier for megavoltage photons, lead HVLs describe shielding, and the mA and time set the quantity of radiation, not its quality.", lvl="Easy"),
    PRN(STEM("Narrow-beam transmission measurements are made for a superficial beam.", ["air kerma falls to 50% behind 2.5 mm Al", "air kerma falls to 25% behind 6.0 mm Al"], "What is the [[homogeneity coefficient]]?"), q_hc, [2.5 / 6.0, 3.5 / 2.5, 6.0 / 2.5], "{:.2f}",
        f"HVL<sub>2</sub> is the extra thickness from 50% to 25%: 6.0 − 2.5 = 3.5 mm Al, so HC = 2.5 / 3.5 = {q_hc:.2f}. Using the total 6.0 mm as HVL<sub>2</sub> gives {2.5 / 6.0:.2f}, and inverting the ratio gives {3.5 / 2.5:.2f}, above 1, which a polyenergetic beam does not reach.", lvl="Moderate"),
    SORT(STEM("Four kilovoltage beams are described by their first HVL.", [], "Rank the [[beams]] from the lowest to the highest effective energy."), ["1st (lowest)", "2nd", "3rd", "4th (highest)"], [(t, i) for i, (t, _) in enumerate(RANK)],
         f"Copper attenuates far more than aluminium, so a copper HVL of 1 mm marks a harder beam than an aluminium HVL of a few millimetres. Matching ln 2 / (HVL × ρ) to NIST μ/ρ values gives about {RANK[0][1]:.0f}, {RANK[1][1]:.0f}, {RANK[2][1]:.0f}, and {RANK[3][1]:.0f} keV. Ranking by the number alone puts 1 mm Cu below 4 mm Al.", lvl="Moderate", mode="rank", cap=1),
    PRN(STEM("A 100 kVp superficial beam has a first HVL of 3.0 mm Al.", [f"ρ(Al) = {RHO_AL} g/cm³"], "What is the [[effective energy]] of the beam?", tables=[AL_TABLE]), q_E, [q_E_nd, q_E_l10, 100.0], "{:.0f} keV",
        f"μ<sub>eff</sub> = ln 2 / 0.30 cm = {q_mu:.3f} cm<sup>−1</sup> and μ<sub>eff</sub>/ρ = {q_mu:.3f} / {RHO_AL} = {q_mr:.3f} cm²/g, between the 30 and 40 keV values; interpolating on a log–log scale gives {q_E:.0f} keV, about one third of the peak. Leaving out the density gives {q_E_nd:.0f} keV, log<sub>10</sub> 2 in place of ln 2 gives {q_E_l10:.0f} keV, and the peak itself is 100 keV.",
        w=[f"μ<sub>eff</sub> = ln 2 / 0.30 cm = {q_mu:.3f} cm<sup>−1</sup>", f"μ<sub>eff</sub>/ρ = {q_mu:.3f} / {RHO_AL} = {q_mr:.4f} cm²/g", f"E = 30 keV × ({AL[30]} / {q_mr:.4f})<sup>1/{q_n:.3f}</sup> = {q_E:.1f} keV, with n = ln({AL[30]} / {AL[40]}) / ln(40 / 30) = {q_n:.3f}"], lvl="Challenging"),
    TYPED(STEM("Narrow-beam readings are taken for a superficial beam with aluminium added. The HVL is found by interpolating ln(reading) between the two readings that bracket half the open value.", ["no added aluminium: 100.0", "2.0 mm Al: 54.5", "3.0 mm Al: 45.2"], "What is the [[first HVL]]?"), q_x50, 0.02, "mm Al",
          f"The reading falls exponentially between the two points, so x = 2.0 + 1.0 × ln(54.5 / 50) / ln(54.5 / 45.2) = {q_x50:.2f} mm Al. A straight-line interpolation of the readings gives {q_x50_lin:.2f} mm Al, close here because both points are near 50. Treating the 2.0 mm reading as one exponential from zero gives {q_x50_one:.2f} mm Al, too low, because the first millimetres remove the softest photons.",
          w=[f"ln(54.5 / 50) = {math.log(54.5 / 50):.4f}", f"ln(54.5 / 45.2) = {math.log(54.5 / 45.2):.4f}", f"x = 2.0 + {math.log(54.5 / 50):.4f} / {math.log(54.5 / 45.2):.4f} = {q_x50:.2f} mm Al"], lvl="Challenging"),
    PR(STEM("A 70 kV superficial beam treats a skin lesion, and the dose at the skin surface is calibrated with AAPM TG-61.", [], "Which [[method]] applies?"),
       "The in-air method, with a backscatter factor to reach the surface dose", ["The in-phantom method, with the chamber at 2 cm depth in water", "The TG-51 method, with a beam quality conversion factor k<sub>Q</sub>", "The in-phantom method, with the chamber at the depth of maximum dose"],
       "TG-61 uses the in-air method for points at or near the surface: the chamber, calibrated in air kerma, reads free in air, and the backscatter factor and the water-to-air ratio of mass energy-absorption coefficients give the dose to water at the surface. The in-phantom method at 2 cm is for tube potentials of 100 kV and above, and TG-51 covers megavoltage beams.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [6, 7, 8, 11], 2: [13, 15, 16], 3: [17, 18, 19, 22]}

TERMS = ['bremsstrahlung', 'thermionic emission', 'space charge', 'line-focus principle', 'heel effect', 'beam hardening', 'homogeneity coefficient', 'effective energy']

TAKE = [
    [f"E<sub>max</sub> = kVp in keV; λ<sub>min</sub> (nm) = 1.24 / kVp.",
     "Efficiency ≈ 9 × 10<sup>−10</sup> Z V (V in volts): under 1% at diagnostic voltages, and the rest is heat.",
     "Characteristic lines depend on the anode, not the kVp; tungsten K lines need more than 69.5 kV."],
    ["The filament temperature sets the mA; a rotating anode spreads the heat.",
     "Effective focal spot = actual × sin θ. A smaller angle gives a smaller spot, a smaller field, and a stronger heel effect.",
     f"Less intensity on the anode side: thick part toward the cathode. HU = kVp × mA × s × f ({F_1PH:.1f}, {F_6P}, or {F_12P})."],
    ["Filtration lowers the output and raises the mean energy and HVL; E<sub>max</sub> is unchanged.",
     "kVp raises E<sub>max</sub>, the mean energy, and the output (about as kVp²); mA scales the output only.",
     "Less ripple gives more output and a higher mean energy at the same kVp."],
    ["HVL in Al for diagnostic and superficial beams, in Cu for orthovoltage. HC = HVL<sub>1</sub> / HVL<sub>2</sub>, at most 1.",
     "Effective energy: the monoenergetic energy with the same HVL, about one third to one half of the peak.",
     "TG-61: in-air method near the surface; in-phantom at 2 cm depth for 100 kV and above."],
]
