from blocks import *
import math

# ---------------------------------------------------------------- this chapter's formulas
C0 = 1540.0                                         # m/s, the soft-tissue average that every scanner assumes
ALPHA = 0.5                                         # dB cm⁻¹ MHz⁻¹, soft-tissue average (about 0.3 to 1 by tissue)

def wavelength_mm(f_mhz, c=C0):
    """λ = c/f, in mm, for f in MHz and c in m/s."""
    return c / (f_mhz * 1e6) * 1000

def impedance(rho, c):
    """Acoustic impedance Z = ρc in MRayl (10⁶ kg m⁻² s⁻¹), for ρ in kg/m³ and c in m/s."""
    return rho * c / 1e6

def amp_refl(z1, z2):
    """Pressure amplitude reflection coefficient at normal incidence, from medium 1 into medium 2."""
    return (z2 - z1) / (z2 + z1)

def refl(z1, z2):
    """Intensity reflection coefficient at normal incidence: the square of the amplitude coefficient."""
    return amp_refl(z1, z2) ** 2

def db_below(ratio):
    """How many decibels an intensity ratio below 1 lies under the reference."""
    return -10 * math.log10(ratio)

def depth_cm(t_us, c=C0):
    """Depth of a reflector from the round-trip echo time: d = ct/2."""
    return c * t_us * 1e-6 / 2 * 100

def max_depth_cm(prf_hz, c=C0):
    """Greatest depth whose echo returns before the next pulse: c/(2 PRF)."""
    return c / (2 * prf_hz) * 100

def max_prf_hz(d_cm, c=C0):
    """Highest pulse repetition frequency for echoes from d_cm: c/(2d)."""
    return c / (2 * d_cm / 100)

def loss_db(f_mhz, path_cm, alpha=ALPHA):
    """Attenuation in dB over a path, with α in dB cm⁻¹ MHz⁻¹."""
    return alpha * f_mhz * path_cm

def axial_mm(f_mhz, cycles, c=C0):
    """Axial resolution: half the spatial pulse length nλ."""
    return cycles * wavelength_mm(f_mhz, c) / 2

def near_field_mm(d_mm, f_mhz, c=C0):
    """Near-field length D²/(4λ) of an unfocused disc of diameter D."""
    return d_mm ** 2 / (4 * wavelength_mm(f_mhz, c))

def divergence_deg(d_mm, f_mhz, c=C0):
    """Far-field half-angle of an unfocused disc: sin θ = 1.22 λ/D."""
    return math.degrees(math.asin(1.22 * wavelength_mm(f_mhz, c) / d_mm))

def doppler_hz(f_mhz, v, deg, c=C0):
    """Doppler shift f_D = 2 f₀ v cos θ / c, with v in m/s."""
    return 2 * f_mhz * 1e6 * v * math.cos(math.radians(deg)) / c

def doppler_v(fd_hz, f_mhz, deg, c=C0):
    """Velocity (m/s) from a Doppler shift: v = f_D c / (2 f₀ cos θ)."""
    return fd_hz * c / (2 * f_mhz * 1e6 * math.cos(math.radians(deg)))

def refract_deg(theta_i, c1, c2):
    """Angle of the transmitted beam by Snell's law, sin θt / sin θi = c₂/c₁."""
    return math.degrees(math.asin(c2 / c1 * math.sin(math.radians(theta_i))))

def depth_error_mm(thick_cm, c_layer, c=C0):
    """How much deeper (mm) a structure appears behind a layer whose speed is c_layer, when the scanner assumes c."""
    return 10 * thick_cm * (c / c_layer - 1)

# ---------------------------------------------------------------- values quoted in the text (ranges where they vary)
C_FAT = 1450.0                                      # m/s, a representative value for fat (about 1,430 to 1,480)
C_WATER = 1480.0                                    # m/s, water at room temperature
Z_SOFT = 1.63                                       # MRayl, soft tissue
Z_AIR = 0.0004                                      # MRayl, air
Z_SOFT_LO, Z_SOFT_HI = 1.6, 1.7                     # MRayl, soft tissues other than fat
Z_FAT_LO = 1.3                                      # MRayl, the lowest fat value
Z_BONE_LO, Z_BONE_HI = 6.0, 8.0                     # MRayl, cortical bone
MEDIA = [
    ["Air", "about 330–350", "about 0.0004"],
    ["Fat", "about 1,430–1,480", "about 1.3–1.4"],
    ["Water, 20–37 °C", "about 1,480–1,525", "about 1.5"],
    ["Soft tissue, average", "1,540 (assumed by scanners)", "about 1.6–1.7"],
    ["Muscle", "about 1,550–1,630", "about 1.7"],
    ["Cortical bone", "about 3,000–4,100", "about 6–8"],
    ["PZT (transducer crystal)", "about 4,000–4,600", "about 30–35"],
]
ARTIFACTS = [
    ["Reverberation", "Sound bouncing between two strong reflectors, or between one and the probe", "Equally spaced copies of the echo, deeper"],
    ["Acoustic shadowing", "Strong attenuation or reflection by bone, calcification, gas, or metal", "A dark band behind the object"],
    ["Acoustic enhancement", "Weak attenuation in fluid, with the TGC set for tissue", "A bright band behind a cyst or the bladder"],
    ["Speckle", "Interference of echoes from scatterers smaller than the resolution", "A granular texture that does not map the tissue"],
    ["Refraction", "Bending of the beam at an oblique boundary where the speed changes", "An object shifted sideways, or seen twice"],
    ["Speed of sound", "A speed other than the 1540 m/s assumed", "A wrong depth: too deep behind fat"],
    ["Mirror image", "A strong, smooth reflector such as the diaphragm", "A copy of an object beyond the reflector"],
]
lam5 = wavelength_mm(5.0)                                                    # 0.31 mm at 5 MHz
r_air = refl(Z_SOFT, Z_AIR)                                                  # soft tissue against air
z_ratio_air = Z_SOFT / Z_AIR
r_soft_max = refl(Z_FAT_LO, Z_SOFT_HI)                                       # the largest step between soft tissues: fat against muscle
r_bone_lo, r_bone_hi = refl(Z_SOFT_HI, Z_BONE_LO), refl(Z_SOFT_LO, Z_BONE_HI)
bone_lo5, bone_hi5 = 5 * math.floor(20 * r_bone_lo), 5 * math.ceil(20 * r_bone_hi)     # rounded out to 5%
SOFT_MAX = math.ceil(100 * r_soft_max)                                       # "about 2% or less"
us_cm = 2 * 0.01 / C0 * 1e6                                                  # µs of echo time per cm of depth
fat_pct = 100 * (C0 / C_FAT - 1)                                             # depth error behind fat, % of its thickness
water_pct = 100 * (C0 / C_WATER - 1)                                         # distances in a water bath at room temperature
card_loss = loss_db(5.0, 20.0)                                               # 10 cm deep at 5 MHz, round trip
card_depth = max_depth_cm(5000)
card_ax = axial_mm(5.0, 3)
card_nf = near_field_mm(10.0, 5.0)
card_fd = doppler_hz(5.0, 0.40, 60)

# ---------------------------------------------------------------- worked examples
x1_rf, x1_cf, x1_rm, x1_cm = 920.0, 1450.0, 1070.0, 1580.0                   # fat and muscle (illustrative)
x1_zf, x1_zm = impedance(x1_rf, x1_cf), impedance(x1_rm, x1_cm)
x1_a = amp_refl(x1_zf, x1_zm); x1_r = refl(x1_zf, x1_zm); x1_db = db_below(x1_r)
x2_t, x2_f = 130.0, 5.0                                                      # echo time (µs), frequency (MHz)
x2_d = depth_cm(x2_t); x2_loss = loss_db(x2_f, 2 * x2_d); x2_prf = max_prf_hz(x2_d); x2_loss10 = loss_db(10.0, 2 * x2_d)
x3_f, x3_n, x3_d = 5.0, 3, 10.0                                              # MHz, cycles per pulse, disc diameter (mm)
x3_lam = wavelength_mm(x3_f); x3_spl = x3_n * x3_lam; x3_ax = axial_mm(x3_f, x3_n); x3_nf = near_field_mm(x3_d, x3_f); x3_div = divergence_deg(x3_d, x3_f)
x3_ax10, x3_nf10 = axial_mm(10.0, x3_n), near_field_mm(x3_d, 10.0)
x4_f, x4_fd, x4_th = 4.0, 2600.0, 60.0                                       # MHz, Hz, degrees
x4_v = doppler_v(x4_fd, x4_f, x4_th); x4_prf = 2 * x4_fd

# ---------------------------------------------------------------- numbers in the questions
q_z1, q_z2 = 1.63, 7.80                                                      # soft tissue and bone (MRayl)
q_a = amp_refl(q_z1, q_z2); q_r = refl(q_z1, q_z2)
t_z1, t_z2 = 1.34, 1.65                                                      # fat and liver (MRayl)
t_r = refl(t_z1, t_z2); t_db = db_below(t_r); t_db_amp = db_below(amp_refl(t_z1, t_z2))
s_ci, s_c1, s_c2 = 30.0, 1450.0, 1580.0                                      # refraction from fat into muscle
s_t = refract_deg(s_ci, s_c1, s_c2); s_inv = refract_deg(s_ci, s_c2, s_c1); s_crit = math.degrees(math.asin(s_c1 / s_c2))
p_prf = 5000.0
p_d = max_depth_cm(p_prf)
f_lo, f_hi, f_depth = 2.5, 5.0, 15.0                                         # probe change for a deep prostate
f_loss_hi, f_loss_lo, f_lam_lo = loss_db(f_hi, 2 * f_depth), loss_db(f_lo, 2 * f_depth), wavelength_mm(f_lo)
a_f, a_n = 7.5, 3
a_lam = wavelength_mm(a_f); a_spl = a_n * a_lam; a_ax = axial_mm(a_f, a_n)
d_f, d_v, d_th = 5.0, 0.40, 60.0
d_fd = doppler_hz(d_f, d_v, d_th); d_half = d_fd / 2; d_nocos = 2 * d_f * 1e6 * d_v / C0; d_sin = 2 * d_f * 1e6 * d_v * math.sin(math.radians(d_th)) / C0
v_f, v_fd, v_th = 3.0, 2000.0, 45.0
v_v = doppler_v(v_fd, v_f, v_th); v_nocos = v_fd * C0 / (2 * v_f * 1e6)
e_thick = 4.0                                                                # cm of fat in front of the prostate
e_err = depth_error_mm(e_thick, C_FAT); e_inv = 10 * e_thick * (1 - C_FAT / C0)
k_thick = 3.0                                                                # cm of fat in the probe-pressure question
k_err = depth_error_mm(k_thick, C_FAT)

TOPIC = dict(
    id="ultrasound", domain=4, sub="IV.A", title="Ultrasound physics and imaging",
    ref=dict(aapm="TG-154", khan="", ford="20"),
    guide=[
        H("Sound waves and interfaces"),
        P(f"Ultrasound is sound above 20 kHz; imaging uses about 2 to 15 MHz. The longitudinal pressure wave travels at a speed c set by the stiffness and density of the medium, not by the frequency. Scanners assume 1540 m/s, the soft-tissue average, so the wavelength λ = c/f is {lam5:.2f} mm at 5 MHz."),
        EQ("c = f λ,   period = 1/f",
           "Z = ρ c,   1 MRayl = 10<sup>6</sup> kg m<sup>−2</sup> s<sup>−1</sup>",
           "R = [(Z<sub>2</sub> − Z<sub>1</sub>) / (Z<sub>2</sub> + Z<sub>1</sub>)]<sup>2</sup>,   transmitted fraction = 1 − R   (intensity, normal incidence)",
           "sin θ<sub>t</sub> / sin θ<sub>i</sub> = c<sub>2</sub> / c<sub>1</sub>   (refraction)"),
        P(f"Where the acoustic impedance Z = ρc changes, part of the intensity is reflected. Between soft tissues the echo carries about {SOFT_MAX}% or less, so most of the sound goes deeper; soft tissue reflects about {bone_lo5} to {bone_hi5}% against bone and {100 * r_air:.1f}% against air. Coupling gel therefore replaces the air between probe and skin, and bone and gas hide what lies behind them."),
        TABLE(["Medium", "Speed of sound (m/s)", "Impedance (MRayl)"], MEDIA),
        P("A smooth interface reflects like a mirror and returns a strong echo only when the beam meets it nearly perpendicularly. At oblique incidence the transmitted beam bends where the speed changes (refraction). Structures smaller than the wavelength scatter weak echoes in all directions, which form the texture of organs."),
        EX("Echo from a fat–muscle interface", STEM("A pulse crosses from fat into muscle at normal incidence (illustrative values).",
           [f"fat: ρ = {x1_rf:.0f} kg/m³,   c = {x1_cf:.0f} m/s", f"muscle: ρ = {x1_rm:,.0f} kg/m³,   c = {x1_cm:.0f} m/s"], "Find the [[intensity reflection coefficient]] and the [[echo level]] relative to the incident pulse."),
           [f"Z<sub>fat</sub> = {x1_rf:.0f} × {x1_cf:.0f} = {x1_zf:.3f} MRayl;   Z<sub>muscle</sub> = {x1_rm:,.0f} × {x1_cm:.0f} = {x1_zm:.3f} MRayl",
            f"Amplitude coefficient = ({x1_zm:.3f} − {x1_zf:.3f}) / ({x1_zm:.3f} + {x1_zf:.3f}) = {x1_a:.4f}",
            f"R = {x1_a:.4f}<sup>2</sup> = {x1_r:.4f}",
            f"Echo level = 10 log<sub>10</sub> {x1_r:.4f} = −{x1_db:.1f} dB"],
           f"R = {100 * x1_r:.2f}%, an echo {x1_db:.1f} dB below the incident pulse; {100 * (1 - x1_r):.1f}% of the intensity goes on."),

        H("Attenuation and pulse-echo imaging"),
        P(f"Intensity falls with depth by absorption into heat, scattering, and reflection. A loss of x dB leaves 10<sup>−x/10</sup> of the intensity, so 3 dB halves it. Soft tissue attenuates about {ALPHA} dB/cm/MHz (roughly 0.3 to 1, by tissue), about in proportion to frequency; water and urine attenuate little. Higher frequencies resolve finer detail but reach less depth: about 2 to 5 MHz for the deep pelvis, more for transrectal imaging."),
        P(f"The echo time t gives the depth, d = ct/2, the 2 for the round trip: {us_cm:.0f} µs per centimetre. The next pulse waits for the deepest echoes, so the pulse repetition frequency (PRF) is at most c/(2 × depth), and an echo arriving after the next pulse is placed too shallow. Time gain compensation (TGC) amplifies later echoes more, offsetting attenuation. The image is built line by line, so the frame rate falls as the depth, the number of lines, or the number of focal zones grows."),
        EQ("loss (dB) = α × f × path length,   α ≈ 0.5 dB cm<sup>−1</sup> MHz<sup>−1</sup> in soft tissue",
           "d = c t / 2,   maximum depth = c / (2 PRF)"),
        P("A-mode plots echo amplitude against depth along one line. B-mode shows each echo as a dot whose brightness follows its amplitude, line after line, to form a cross-section. M-mode plots one B-mode line against time, for moving structures such as heart valves."),
        EX("Depth and attenuation of an echo", STEM("A 5 MHz pulse is sent into soft tissue.", [f"echo time = {x2_t:.0f} µs", "c = 1540 m/s", "α = 0.5 dB cm<sup>−1</sup> MHz<sup>−1</sup>"],
           "Find the [[depth of the reflector]], the [[round-trip attenuation]], and the [[highest PRF]] that reaches this depth."),
           [f"d = c t / 2 = 1540 m/s × {x2_t:.0f} × 10<sup>−6</sup> s / 2 = {x2_d / 100:.4f} m = {x2_d:.1f} cm",
            f"Loss = 0.5 × 5 × (2 × {x2_d:.1f} cm) = {x2_loss:.0f} dB, so 10<sup>−{x2_loss / 10:.0f}</sup> of the intensity returns, before the loss at the reflector",
            f"PRF = c / (2d) = 1540 / (2 × {x2_d / 100:.3f} m) = {x2_prf:,.0f} Hz"],
           f"{x2_d:.1f} cm, {x2_loss:.0f} dB, and {x2_prf / 1000:.1f} kHz. At 10 MHz the loss would be {x2_loss10:.0f} dB."),

        H("Transducers, beams, and resolution"),
        P("A piezoelectric crystal, usually the ceramic lead zirconate titanate (PZT), turns a voltage pulse into vibration and a returning echo into a voltage; it resonates at the frequency for which its thickness is half a wavelength. A matching layer a quarter wavelength thick, of impedance between the crystal's and tissue's, passes more sound into the patient. A backing layer damps the ringing to a pulse of two or three cycles: lower sensitivity and a broader bandwidth, but finer detail along the beam."),
        P("A linear array fires groups of elements in sequence for a rectangular image of superficial structures. A curvilinear array, its elements on an arc, gives a fan that widens with depth, for the abdomen and pelvis. A phased array steers the beam through a sector by firing every element with small delays, from a footprint small enough to fit between ribs. Delays also focus the beam in the image plane; a lens focuses it across the plane."),
        P("Axial resolution, along the beam, is half the spatial pulse length nλ. Lateral resolution, in the image plane, is the beam width, smallest at the focus. Elevational resolution, across the plane, is the slice thickness, usually the coarsest. The beam of an unfocused disc of diameter D narrows over the near field, of length D<sup>2</sup>/(4λ), and diverges beyond it."),
        EQ("λ = c / f,   spatial pulse length = n λ   (n cycles)", "axial resolution = n λ / 2",
           "near field N = D<sup>2</sup> / (4λ),   beyond it sin θ = 1.22 λ / D"),
        EX("Wavelength, axial resolution, and near field", STEM("An unfocused disc transducer.", [f"frequency = {x3_f:.1f} MHz", f"cycles per pulse = {x3_n}", "c = 1540 m/s", f"diameter D = {x3_d:.0f} mm"],
           "Find the [[wavelength]], the [[axial resolution]], and the [[near-field length]]."),
           [f"λ = 1540 / ({x3_f:.1f} × 10<sup>6</sup>) m = {x3_lam:.3f} mm",
            f"Spatial pulse length = {x3_n} × {x3_lam:.3f} = {x3_spl:.3f} mm, so the axial resolution = {x3_spl:.3f} / 2 = {x3_ax:.3f} mm",
            f"N = {x3_d:.0f}<sup>2</sup> / (4 × {x3_lam:.3f}) = {x3_nf:.1f} mm",
            f"Beyond it, sin θ = 1.22 × {x3_lam:.3f} / {x3_d:.0f} = {math.sin(math.radians(x3_div)):.4f}, θ = {x3_div:.1f}°"],
           f"{x3_lam:.2f} mm, {x3_ax:.2f} mm, and {x3_nf:.0f} mm. At 10 MHz the axial resolution halves to {x3_ax10:.2f} mm and the near field doubles to {x3_nf10:.0f} mm."),

        H("Doppler, artifacts, and safety"),
        P("Moving blood shifts the frequency of the echo in proportion to the velocity component along the beam. There is no shift at 90°, and an angle error matters most at large angles, so velocities are measured at 60° or less. Continuous-wave Doppler gives no depth. Pulsed-wave Doppler samples one depth, and a shift above PRF/2, the Nyquist limit, aliases to the wrong direction. Colour Doppler maps the mean shift; power Doppler maps the strength of the signal, sensitive to slow flow but without direction."),
        EQ("f<sub>D</sub> = 2 f<sub>0</sub> v cos θ / c", "no aliasing while f<sub>D</sub> < PRF / 2"),
        EX("Blood velocity from a Doppler shift", STEM("Pulsed-wave Doppler of an artery.", [f"transmitted frequency = {x4_f:.1f} MHz", f"Doppler shift = {x4_fd / 1000:.1f} kHz", f"angle between beam and flow = {x4_th:.0f}°", "c = 1540 m/s"],
           "Find the [[blood velocity]] and the [[lowest PRF]] that avoids aliasing."),
           [f"v = f<sub>D</sub> c / (2 f<sub>0</sub> cos θ) = {x4_fd:,.0f} × 1540 / (2 × {x4_f:.1f} × 10<sup>6</sup> × 0.5)",
            f"PRF/2 must exceed {x4_fd / 1000:.1f} kHz"],
           f"{x4_v:.2f} m/s, and a PRF above {x4_prf / 1000:.1f} kHz."),
        P("Artifacts arise where the assumptions of the scanner fail: a straight beam, one reflection per echo, even attenuation, and 1540 m/s."),
        TABLE(["Artifact", "Cause", "Appearance"], ARTIFACTS),
        P("The possible biological effects are heating, tracked by the thermal index (TI), and cavitation, tracked by the mechanical index (MI): the derated peak rarefactional pressure in MPa over √f in MHz, limited by the FDA to 1.9 except for the eye. Output follows ALARA."),

        H("Ultrasound in radiotherapy"),
        P(f"Transrectal ultrasound (TRUS) guides prostate seed and HDR implants. A biplane probe gives transverse images from a curvilinear array and sagittal images from a linear array. A stepper moves it in fixed steps, often 5 mm, for the volume study and to follow each needle to its depth, and a grid on the screen stands for the template holes. AAPM TG-128 gives phantom tests of these systems, including the alignment of the grid with the template and the accuracy of distances, areas, and volumes. Test phantoms carry sound at 1540 m/s; in water at room temperature, about 1480 m/s, distances appear about {water_pct:.0f}% too long."),
        P("For external beam, a transabdominal probe images the prostate through a full bladder. The probe is tracked in room coordinates by infrared cameras or an arm, and the gland is matched to the planning contours, or to a reference scan from simulation, for a couch shift. A transperineal probe, outside the beam paths, can monitor the prostate during treatment."),
        P(f"Probe pressure can push the prostate posteriorly by a few millimetres. Behind fat, at about 1450 m/s, structures appear deeper by about {fat_pct:.0f}% of the fat thickness, and the outlines of the gland on CT and ultrasound differ, as do operators. AAPM TG-154 (2011) sets QA of these systems at stated frequencies: spatial accuracy, tested with a phantom against the room lasers and isocenter, and image quality against a baseline."),
    ],
    cards=[
        F("Wavelength in soft tissue", f"λ = c/f, with c = 1540 m/s, the soft-tissue average that scanners assume: {lam5:.2f} mm at 5 MHz.",
          w=[f"λ = 1540 m/s ÷ (5 × 10<sup>6</sup> s<sup>−1</sup>) = {lam5:.3f} mm"]),
        F("Speed of sound in other media", ["Air: about 330–350 m/s", "Fat: about 1,430–1,480 m/s", "Cortical bone: about 3,000–4,100 m/s"]),
        F("Reflection at an interface", f"R = [(Z<sub>2</sub> − Z<sub>1</sub>)/(Z<sub>2</sub> + Z<sub>1</sub>)]<sup>2</sup>, with Z = ρc: about {SOFT_MAX}% or less between soft tissues, about {bone_lo5}–{bone_hi5}% at bone, {100 * r_air:.1f}% at air, hence coupling gel."),
        F("Attenuation in soft tissue", f"About {ALPHA} dB/cm/MHz (roughly 0.3 to 1 by tissue), about proportional to frequency, and counted over the round trip.",
          w=[f"10 cm deep at 5 MHz: 0.5 × 5 × 20 cm = {card_loss:.0f} dB"]),
        F("Echo depth and time", f"d = ct/2: {us_cm:.0f} µs per centimetre of depth at 1540 m/s.", w=[f"t = 2 × 0.01 m ÷ 1540 m/s = {us_cm:.2f} µs"]),
        F("Pulse repetition frequency and depth", "The maximum depth is c/(2 PRF). An echo arriving after the next pulse is placed too shallow.",
          w=[f"PRF = 5 kHz: 1540 ÷ (2 × 5000) m = {card_depth:.1f} cm"]),
        F("Time gain compensation", "The gain rises with echo time, to offset the attenuation of deeper echoes."),
        F("Axial resolution", "Half the spatial pulse length, nλ/2: finer at higher frequency and with fewer cycles per pulse.", w=[f"5 MHz, 3 cycles: 3 × {lam5:.3f} ÷ 2 = {card_ax:.2f} mm"]),
        F("Lateral and elevational resolution", "Lateral: the beam width in the image plane, smallest at the focus. Elevational: the slice thickness across the plane, usually the coarsest."),
        F("Near field of a disc transducer", "Length D<sup>2</sup>/(4λ) for an unfocused disc of diameter D; beyond it the beam diverges, with sin θ = 1.22 λ/D.",
          w=[f"D = 10 mm at 5 MHz: 100 ÷ (4 × {lam5:.3f}) = {card_nf:.0f} mm"]),
        F("Doppler shift", "f<sub>D</sub> = 2 f<sub>0</sub> v cos θ / c: no shift at 90°, and velocities are measured at 60° or less.",
          w=[f"5 MHz, 0.40 m/s, 60°: 2 × 5 × 10<sup>6</sup> × 0.40 × 0.5 ÷ 1540 = {card_fd / 1000:.2f} kHz"]),
        F("Aliasing in pulsed Doppler", "A shift above PRF/2, the Nyquist limit, wraps around to the opposite direction. A higher PRF, a lower frequency, or continuous-wave Doppler avoids it."),
        F("Shadowing and enhancement", "Shadowing: a dark band behind bone, calcification, gas, or metal. Enhancement: a bright band behind fluid, which attenuates less than the TGC assumes."),
        F("Mechanical and thermal indices", "MI, the derated peak rarefactional pressure (MPa) over √f (MHz), tracks the chance of cavitation; TI tracks heating. Output follows ALARA."),
        F("Transrectal ultrasound for prostate implants", "A biplane probe on a stepper, moved in fixed steps (often 5 mm), with a grid on the screen for the template holes. QA in AAPM TG-128."),
        F("Errors of transabdominal prostate localization", f"Probe pressure moving the prostate, slower sound in fat (a deeper image, about {fat_pct:.0f}% of the fat thickness), CT and ultrasound outlines that differ, and differences between operators. QA in AAPM TG-154."),
    ],
)

PROBLEMS = [
    # ---- 1-5: sound waves and interfaces
    PR(STEM("Gel is spread on the skin before the transducer is placed.", ask="Why is the gel needed?"), "It displaces air, which would reflect nearly all the sound",
       ["It cools the skin under the face of the transducer", "It raises the frequency of the transmitted pulse", "It focuses the beam at the depth of the organ"],
       f"Soft tissue and air differ in impedance by a factor of about {round(z_ratio_air, -3):,.0f}, so a layer of air reflects {100 * r_air:.1f}% of the intensity and almost nothing enters the patient. The gel, close to tissue in impedance, removes that layer. It does not cool the skin or change the frequency, and the array and its lens do the focusing.", lvl="Easy"),
    PRN(STEM("A pulse meets the surface of a bone at normal incidence (illustrative impedances).", [f"impedance of soft tissue, Z<sub>1</sub> = {q_z1:.2f} MRayl", f"impedance of bone, Z<sub>2</sub> = {q_z2:.2f} MRayl"],
             "What [[fraction of the incident intensity]] is reflected?"), 100 * q_r, [100 * q_a, 100 * (1 - q_r), 100 * q_z1 / q_z2], "{:.1f}%",
        f"The amplitude coefficient is ({q_z2:.2f} − {q_z1:.2f}) / ({q_z2:.2f} + {q_z1:.2f}) = {q_a:.3f}, and the intensity coefficient is its square, {q_r:.3f}: {100 * q_r:.1f}% is reflected and {100 * (1 - q_r):.1f}% transmitted. Leaving the ratio unsquared gives {100 * q_a:.1f}%, the transmitted share is {100 * (1 - q_r):.1f}%, and Z<sub>1</sub>/Z<sub>2</sub> gives {100 * q_z1 / q_z2:.1f}%.", lvl="Moderate"),
    TYPED(STEM("A pulse crosses from fat into liver at normal incidence (illustrative impedances).", [f"impedance of fat, Z<sub>1</sub> = {t_z1:.2f} MRayl", f"impedance of liver, Z<sub>2</sub> = {t_z2:.2f} MRayl"],
               "By how many [[decibels]] is the reflected echo weaker than the incident pulse?"), t_db, 0.02, "dB",
          f"R = [({t_z2:.2f} − {t_z1:.2f}) / ({t_z2:.2f} + {t_z1:.2f})]<sup>2</sup> = ({amp_refl(t_z1, t_z2):.4f})<sup>2</sup> = {t_r:.5f}, and 10 log<sub>10</sub> {t_r:.5f} = −{t_db:.1f} dB, so the echo is {t_db:.1f} dB below the incident pulse. The unsquared amplitude ratio gives {t_db_amp:.1f} dB.", lvl="Moderate"),
    PR(STEM("A beam crosses an oblique boundary from fat into muscle.", [f"speed of sound in fat = {s_c1:.0f} m/s", f"speed of sound in muscle = {s_c2:.0f} m/s", f"angle of incidence = {s_ci:.0f}°"], "How is the transmitted beam deflected?"),
       f"Away from the normal, to about {s_t:.0f}°", [f"Toward the normal, to about {s_inv:.0f}°", "Not at all, since refraction needs a change of density", "Back into the fat, by total reflection"],
       f"Snell's law gives sin θ<sub>t</sub> = ({s_c2:.0f} / {s_c1:.0f}) × sin {s_ci:.0f}° = {math.sin(math.radians(s_t)):.3f}, so θ<sub>t</sub> = {s_t:.1f}°: entering the faster medium, the beam bends away from the normal. Inverting the ratio gives {s_inv:.1f}°. Refraction follows the change of speed, not of density, and total reflection would need an incidence beyond {s_crit:.0f}°.", lvl="Moderate"),
    SORT("Rank these media by the speed of sound in them, from the slowest to the fastest.", ["1st (slowest)", "2nd", "3rd", "4th (fastest)"],
         [("Air", 0), ("Fat", 1), ("Muscle", 2), ("Cortical bone", 3)],
         "Air carries sound at about 330–350 m/s, fat at about 1,430–1,480, muscle at about 1,550–1,630, and cortical bone at about 3,000–4,100 m/s. Bone is far stiffer than soft tissue, so sound is fastest there despite its higher density.", lvl="Easy", mode="rank", cap=1),
    # ---- 6-9: attenuation and pulse-echo imaging
    PR(STEM(ask="What does time gain compensation (TGC) do?"), "It amplifies later echoes more, to offset attenuation with depth",
       ["It lowers the transmit power for deep structures, to limit heating", "It shortens the pulses sent to deep structures, to sharpen them", "It delays the next pulse until the deepest echo has returned"],
       "Echoes from deeper reflectors travel farther, return weaker, and return later, so the receiver gain rises with echo time and equal reflectors look equally bright at every depth. TGC does not change the transmitted pulse, and waiting for the deepest echo sets the PRF.", lvl="Easy"),
    PRN(STEM("A scanner transmits pulses at a fixed rate into soft tissue.", [f"pulse repetition frequency = {p_prf / 1000:.1f} kHz", "c = 1540 m/s"], "What is the [[greatest depth]] whose echo returns before the next pulse?"),
        p_d, [2 * p_d, p_d / 2, p_d / 10], "{:.1f} cm",
        f"The pulse repetition period is 1/{p_prf:,.0f} s = {1e6 / p_prf:.0f} µs, and it must cover the round trip: d = c/(2 PRF) = 1540 / (2 × {p_prf:,.0f}) m = {p_d:.1f} cm, or {1e6 / p_prf:.0f} µs at {us_cm:.0f} µs per cm. Forgetting the round trip gives {2 * p_d:.1f} cm. An echo from deeper arrives after the next pulse and is placed too shallow.", lvl="Moderate"),
    PR(STEM(ask="Which display mode plots the depth of the echoes along one beam line against time?"), "M-mode", ["A-mode", "B-mode", "Power Doppler"],
       "M-mode (motion) shows one B-mode line against time, so a moving structure such as a heart valve traces a curve. A-mode plots echo amplitude against depth, B-mode builds a cross-section from many lines, and power Doppler maps the strength of the Doppler signal.", lvl="Easy"),
    PR(STEM(f"A transabdominal scan at {f_hi:.0f} MHz does not show the prostate of a large patient, and the probe is changed to one of {f_lo:.1f} MHz.", ask="What does the change bring?"),
       "The deeper gland is seen, with coarser resolution", ["The deeper gland is seen, with finer resolution", "The depth reached falls, with finer resolution", "The depth is unchanged, with coarser resolution"],
       f"Attenuation is about proportional to frequency: at 0.5 dB/cm/MHz an echo from {f_depth:.0f} cm loses {f_loss_hi:.0f} dB over the round trip at {f_hi:.0f} MHz and {f_loss_lo:.1f} dB at {f_lo:.1f} MHz. The wavelength doubles to {f_lam_lo:.2f} mm, so the axial resolution and the beam width at the focus are coarser.", lvl="Moderate"),
    # ---- 10-12: transducers, beams, and resolution
    PRN(STEM("A transrectal probe transmits short pulses into soft tissue.", [f"frequency = {a_f:.1f} MHz", f"cycles per pulse = {a_n}", "c = 1540 m/s"], "What is the [[axial resolution]]?"),
        a_ax, [a_spl, a_lam, a_lam / 2], "{:.2f} mm",
        f"λ = 1540 / ({a_f:.1f} × 10<sup>6</sup>) m = {a_lam:.3f} mm, the spatial pulse length is {a_n}λ = {a_spl:.3f} mm, and the axial resolution is half of it, {a_ax:.2f} mm: reflectors closer than that along the beam return overlapping echoes. The whole pulse length gives {a_spl:.2f} mm, one wavelength {a_lam:.2f} mm, and half a wavelength {a_lam / 2:.2f} mm.", lvl="Moderate"),
    PR(STEM("A transducer is rebuilt with a heavier backing layer behind its crystal.", ask="Which change follows?"), "Shorter pulses and finer axial resolution, at lower sensitivity",
       ["Longer pulses and finer lateral resolution, at higher sensitivity", "Shorter pulses and a narrower bandwidth, at higher sensitivity", "A longer near field and less divergence beyond it"],
       "The backing absorbs the vibration that keeps the crystal ringing, so each pulse lasts fewer cycles, the axial resolution (half the pulse length) is finer, and the short pulse has a broad bandwidth. Energy lost in the backing lowers the sensitivity. The near field and the divergence depend on the aperture and the wavelength, not on the backing.", lvl="Moderate"),
    PRM(STEM("A curvilinear array images a target 8 cm deep, with its transmit focus at 8 cm. The penetration is adequate at every frequency considered.", ask="Which of these improve the lateral resolution at the target?"),
        ["Raising the transducer frequency", "Widening the active aperture"],
        ["Raising the pulse repetition frequency", "Raising the overall receiver gain", "Adding cycles to each pulse", "Moving the transmit focus to 12 cm"],
        "At the focus the beam width is proportional to λ times the focal depth over the aperture width, so a shorter wavelength or a wider aperture narrows it. The PRF and the gain do not change the beam, extra cycles lengthen the pulse and coarsen the axial resolution, and a focus at 12 cm leaves a wider beam at 8 cm.", lvl="Challenging"),
    # ---- 13-17: Doppler, artifacts, and safety
    PRN(STEM("Blood flows past the sample volume of a pulsed Doppler system.", [f"transmitted frequency = {d_f:.1f} MHz", f"blood velocity = {d_v:.2f} m/s", f"angle between beam and flow = {d_th:.0f}°", "c = 1540 m/s"], "What is the [[Doppler shift]]?"),
        d_fd / 1000, [d_half / 1000, d_nocos / 1000, d_sin / 1000], "{:.2f} kHz",
        f"f<sub>D</sub> = 2 f<sub>0</sub> v cos θ / c = 2 × {d_f:.1f} × 10<sup>6</sup> × {d_v:.2f} × 0.5 / 1540 = {d_fd:,.0f} Hz. Leaving out the 2, which counts the shift on the way in and on the way back, gives {d_half / 1000:.2f} kHz; leaving out cos θ gives {d_nocos / 1000:.2f} kHz, and sin θ in place of cos θ gives {d_sin / 1000:.2f} kHz.", lvl="Moderate"),
    SORT("Match each ultrasound artifact to its cause.", ["Reverberation", "Acoustic shadowing", "Acoustic enhancement", "Speckle", "Refraction"],
         [("Sound bouncing between two strong reflectors", 0), ("Strong attenuation by bone, calcification, or gas", 1), ("Weak attenuation in fluid, with the gain set for tissue", 2),
          ("Interference of echoes from scatterers smaller than the resolution", 3), ("Bending of the beam where the speed changes at an oblique boundary", 4)],
         "Reverberation repeats an echo at equal spacing deeper; shadowing darkens the region behind a strong attenuator or reflector; enhancement brightens the region behind fluid, because the TGC assumes tissue attenuation; speckle is the interference pattern of scatterers too small to resolve; refraction shifts or doubles an object.", lvl="Moderate", mode="match", cap=1),
    PR(STEM(ask="What does the mechanical index (MI) displayed by a scanner indicate?"), "The chance of cavitation, from the peak rarefactional pressure",
       ["The expected temperature rise in the tissue", "The total acoustic power leaving the probe", "The mechanical wear of the transducer elements"],
       "MI is the derated peak rarefactional pressure in MPa divided by the square root of the frequency in MHz, a measure of the chance of cavitation; the FDA limit is 1.9 outside the eye. The temperature rise is described by the thermal index, and neither index measures the total power or the wear of the probe.", lvl="Easy"),
    PRM(STEM("Pulsed-wave Doppler of a fast jet shows aliasing. The PRF is below its limit for this depth.", ask="Which of these reduce the aliasing?"),
        ["Raising the pulse repetition frequency", "Lowering the transmitted frequency", "Switching to continuous-wave Doppler"],
        ["Raising the transmitted frequency", "Aligning the beam more closely with the flow", "Narrowing the sample volume"],
        "Aliasing appears when f<sub>D</sub> exceeds PRF/2. A higher PRF raises that limit, a lower transmitted frequency lowers f<sub>D</sub> in proportion, and continuous-wave Doppler does not sample, so it cannot alias. A higher frequency or a smaller angle between beam and flow raises f<sub>D</sub>, and the size of the sample volume does not change it.", lvl="Challenging"),
    TYPED(STEM("Spectral Doppler measures the peak shift in an artery.", [f"transmitted frequency = {v_f:.1f} MHz", f"peak Doppler shift = {v_fd / 1000:.1f} kHz", f"angle between beam and flow = {v_th:.0f}°", "c = 1540 m/s"],
               "What is the peak [[blood velocity]]?"), 100 * v_v, 0.02, "cm/s",
          f"v = f<sub>D</sub> c / (2 f<sub>0</sub> cos θ) = {v_fd:,.0f} × 1540 / (2 × {v_f:.1f} × 10<sup>6</sup> × {math.cos(math.radians(v_th)):.4f}) = {v_v:.3f} m/s = {100 * v_v:.1f} cm/s. Leaving out cos θ gives {100 * v_nocos:.1f} cm/s.", lvl="Challenging"),
    # ---- 18-21: ultrasound in radiotherapy
    PR(STEM("A prostate seed implant is guided by transrectal ultrasound, with the needles passed through a perineal template.", ask="What does the grid of points shown on the transverse image represent?"),
       "The holes of the template, at the same spacing", ["The planned seed positions in that plane", "The points where the dose is calculated", "The elements of the transducer array"],
       "The grid is the template drawn on the image, so a needle through a given hole should appear at the matching point; TG-128 tests that alignment with a phantom. The plan places seeds at only some of these positions, the dose points belong to the planning system, and the array elements are not drawn.", lvl="Easy"),
    PR(STEM("A patient drinks water before each transabdominal ultrasound localization of the prostate.", ask="Why does the scan need a full bladder?"),
       "Urine attenuates little and pushes gas-filled bowel aside", ["Urine reflects strongly and so outlines the gland", "A full bladder moves the prostate closer to the probe", "Urine absorbs reverberations from the abdominal wall"],
       "The full bladder is an acoustic window: urine attenuates far less than soft tissue and holds the gas-filled bowel, which would shadow the gland, out of the way. Urine is free of scatterers and shows dark, it does not bring the prostate closer to the probe, and it does not absorb reverberations.", lvl="Moderate"),
    PRN(STEM("A transabdominal scan reaches the prostate through a layer of abdominal fat. The scanner assumes 1540 m/s everywhere.", [f"fat thickness = {e_thick:.1f} cm", f"speed of sound in fat = {C_FAT:.0f} m/s", "rest of the path = 1540 m/s"],
             "How much [[deeper than its true position]] does the prostate appear?"), e_err, [e_inv, 2 * e_err, e_err / 2], "{:.1f} mm",
        f"The sound spends {C0 / C_FAT:.4f} times as long in the fat as the scanner assumes, so the fat is drawn {e_thick:.1f} × {C0 / C_FAT:.4f} = {e_thick * C0 / C_FAT:.3f} cm thick and everything behind it {e_err:.1f} mm too deep, {fat_pct:.1f}% of the fat thickness. The ratio inverted gives {e_inv:.1f} mm, and doubling for the round trip, already in the echo time, gives {2 * e_err:.1f} mm.", lvl="Challenging"),
    PR(STEM("A prostate patient is localized with transabdominal ultrasound before each fraction, and implanted gold markers are imaged with kV right after the scan, with the probe removed. Today the therapist pressed hard to see the gland through a thick abdominal wall.",
            ["ultrasound: prostate 7 mm posterior to its planned position", "markers, within a minute of the scan: within 1 mm of their planned position", f"abdominal fat = {k_thick:.1f} cm, speed of sound about {C_FAT:.0f} m/s", "daily phantom check of the ultrasound system: within tolerance"],
            "What most likely explains the difference?"),
       "The probe pushed the prostate posteriorly during the scan", ["Slower sound in the abdominal fat displaced its image", "The calibration of the system to the room had drifted", "The prostate drifted between the two sets of images"],
       f"Hard pressure on the abdomen pushes the prostate posteriorly, and the markers, imaged with the probe removed, show where it lies during treatment. Slower sound in {k_thick:.1f} cm of fat places the image only {k_err:.1f} mm deeper, the phantom check rules out a calibration error, and a drift of 6 mm or more within a minute is far less likely than the displacement the pressure explains.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 4], 1: [6, 7, 8], 2: [10, 11], 3: [13, 14, 15]}          # questions on the last section, and the rest, form the practice set

TERMS = ["acoustic impedance", "pulse repetition frequency", "time gain compensation", "axial resolution", "lateral resolution", "near field", "Nyquist limit", "mechanical index"]

TAKE = [
    [f"c = fλ, with 1540 m/s assumed: λ = {lam5:.2f} mm at 5 MHz. Z = ρc.",
     f"R = [(Z<sub>2</sub> − Z<sub>1</sub>)/(Z<sub>2</sub> + Z<sub>1</sub>)]<sup>2</sup>: about {SOFT_MAX}% or less between soft tissues, {bone_lo5}–{bone_hi5}% at bone, {100 * r_air:.1f}% at air, hence coupling gel."],
    [f"About {ALPHA} dB/cm/MHz in soft tissue, over the round trip: a higher frequency resolves finer detail and reaches less depth.",
     f"Depth = ct/2, {us_cm:.0f} µs per cm; maximum depth = c/(2 PRF); TGC raises the gain of later echoes.",
     "A-mode: amplitude against depth. B-mode: brightness, a cross-section. M-mode: one line against time."],
    ["Backing shortens the pulse; axial resolution = nλ/2. Lateral resolution = beam width, smallest at the focus; elevational is usually the coarsest.",
     "Linear array: rectangle. Curvilinear: fan. Phased: steered sector from a small footprint. Near field D<sup>2</sup>/(4λ)."],
    ["f<sub>D</sub> = 2f<sub>0</sub>v cos θ/c, measured at 60° or less; pulsed Doppler aliases above PRF/2.",
     "Shadowing behind bone, calcification, and gas; enhancement behind fluid; reverberation between strong reflectors.",
     "MI tracks cavitation and TI heating; output follows ALARA."],
    ["TRUS: biplane probe on a stepper, template grid on the screen; QA in TG-128.",
     f"Transabdominal localization: probe pressure, slower sound in fat (about {fat_pct:.0f}% deeper), CT and ultrasound outlines, operators; QA in TG-154."],
]
