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
d_f, d_v, d_th = 5.0, 0.40, 30.0
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
        P(f"Ultrasound is a longitudinal pressure wave above 20 kHz; imaging uses about 2 to 15 MHz. Its speed c is set by the stiffness and density of the medium, not by the frequency. Scanners assume 1540 m/s, the soft-tissue average, so the wavelength λ = c/f is {lam5:.2f} mm at 5 MHz."),
        EQ("c = f λ,   period = 1/f",
           "Z = ρ c,   1 MRayl = 10<sup>6</sup> kg m<sup>−2</sup> s<sup>−1</sup>",
           "R = [(Z<sub>2</sub> − Z<sub>1</sub>) / (Z<sub>2</sub> + Z<sub>1</sub>)]<sup>2</sup>,   transmitted fraction = 1 − R   (intensity, normal incidence)",
           "sin θ<sub>t</sub> / sin θ<sub>i</sub> = c<sub>2</sub> / c<sub>1</sub>   (refraction)"),
        P(f"Where the acoustic impedance Z = ρc changes, part of the intensity is reflected: about {SOFT_MAX}% or less between soft tissues, so most of the sound goes deeper, about {bone_lo5} to {bone_hi5}% at bone, and {100 * r_air:.1f}% at air. Coupling gel therefore replaces the air between probe and skin, and bone and gas hide what lies behind them."),
        TABLE(["Medium", "Speed of sound (m/s)", "Impedance (MRayl)"], MEDIA),
        P("A smooth interface returns a strong echo only when the beam meets it nearly perpendicularly; at an angle the transmitted beam bends where the speed changes (refraction). Structures smaller than the wavelength scatter weak echoes that form the texture of organs."),
        EX("Echo from a fat–muscle interface", STEM("A pulse crosses from fat into muscle at normal incidence (illustrative values).",
           [f"impedance of fat, Z<sub>1</sub> = {x1_zf:.3f} MRayl", f"impedance of muscle, Z<sub>2</sub> = {x1_zm:.3f} MRayl"], "Find the [[intensity reflection coefficient]] and the [[echo level]] relative to the incident pulse."),
           [f"Amplitude coefficient = ({x1_zm:.3f} − {x1_zf:.3f}) / ({x1_zm:.3f} + {x1_zf:.3f}) = {x1_a:.4f}",
            f"R = {x1_a:.4f}<sup>2</sup> = {x1_r:.4f}",
            f"Echo level = 10 log<sub>10</sub> {x1_r:.4f} = −{x1_db:.1f} dB"],
           f"R = {100 * x1_r:.2f}%, an echo {x1_db:.1f} dB below the incident pulse; {100 * (1 - x1_r):.1f}% of the intensity goes on."),

        H("Attenuation and pulse-echo imaging"),
        P(f"Intensity falls with depth by absorption into heat, scattering, and reflection. Soft tissue attenuates about {ALPHA} dB/cm/MHz (roughly 0.3 to 1, by tissue), about in proportion to frequency; water and urine attenuate little. Higher frequencies resolve finer detail but reach less depth: about 2 to 5 MHz for the deep pelvis, more for transrectal imaging."),
        P(f"The echo time t gives the depth, d = ct/2 for the round trip: {us_cm:.0f} µs per centimetre. Each pulse waits for the deepest echoes, so the pulse repetition frequency (PRF) is at most c/(2 × depth); an echo arriving after the next pulse is placed too shallow. Time gain compensation (TGC) amplifies later echoes more, offsetting attenuation."),
        EQ("loss (dB) = α × f × path length,   α ≈ 0.5 dB cm<sup>−1</sup> MHz<sup>−1</sup> in soft tissue",
           "a loss of x dB leaves 10<sup>−x/10</sup> of the intensity: 3 dB halves it, 10 dB leaves a tenth",
           "d = c t / 2,   maximum depth = c / (2 PRF)"),
        P("A-mode plots echo amplitude against depth on one line. B-mode shows each echo as a dot of matching brightness, line after line, forming a cross-section. M-mode plots one B-mode line against time, for moving structures such as heart valves."),
        EX("Depth and attenuation of an echo", STEM("A 5 MHz pulse is sent into soft tissue.", [f"echo time = {x2_t:.0f} µs", "c = 1540 m/s", "α = 0.5 dB cm<sup>−1</sup> MHz<sup>−1</sup>"],
           "Find the [[depth of the reflector]] and the [[round-trip attenuation]]."),
           [f"d = c t / 2 = 1540 m/s × {x2_t:.0f} × 10<sup>−6</sup> s / 2 = {x2_d / 100:.4f} m = {x2_d:.1f} cm",
            f"Loss = 0.5 × 5 × (2 × {x2_d:.1f} cm) = {x2_loss:.0f} dB, so 10<sup>−{x2_loss / 10:.0f}</sup> of the intensity returns, before the loss at the reflector"],
           f"{x2_d:.1f} cm and {x2_loss:.0f} dB. At 10 MHz the loss would be {x2_loss10:.0f} dB."),

        H("Transducers, beams, and resolution"),
        P("A piezoelectric crystal, usually lead zirconate titanate (PZT), converts a voltage pulse to vibration and an echo to a voltage. A quarter-wavelength matching layer passes more sound into the patient, and a backing layer damps the ringing to two or three cycles per pulse, giving finer detail along the beam at some loss of sensitivity."),
        P("Linear arrays give a rectangular image, curvilinear arrays a fan for the abdomen and pelvis, and phased arrays a beam steered by small firing delays from a footprint that fits between ribs. Delays also focus the beam in the image plane; a lens focuses it across the plane."),
        P("Axial resolution, along the beam, is half the spatial pulse length nλ. Lateral resolution, in the image plane, is the beam width, smallest at the focus. Elevational resolution, across the plane, is the slice thickness, usually the coarsest. The beam of an unfocused disc of diameter D narrows over the near field, of length D<sup>2</sup>/(4λ), and diverges beyond it."),
        EQ("λ = c / f,   spatial pulse length = n λ   (n cycles)", "axial resolution = n λ / 2",
           "near field N = D<sup>2</sup> / (4λ),   beyond it sin θ = 1.22 λ / D"),
        EX("Wavelength and axial resolution", STEM("A transducer sends short pulses into soft tissue.", [f"frequency = {x3_f:.1f} MHz", f"cycles per pulse = {x3_n}", "c = 1540 m/s"],
           "Find the [[wavelength]] and the [[axial resolution]]."),
           [f"λ = 1540 / ({x3_f:.1f} × 10<sup>6</sup>) m = {x3_lam:.3f} mm",
            f"Spatial pulse length = {x3_n} × {x3_lam:.3f} = {x3_spl:.3f} mm, so the axial resolution = {x3_spl:.3f} / 2 = {x3_ax:.3f} mm"],
           f"{x3_lam:.2f} mm and {x3_ax:.2f} mm. At 10 MHz the axial resolution halves to {x3_ax10:.2f} mm."),

        H("Doppler, artifacts, and safety"),
        P("Moving blood shifts the echo frequency in proportion to the velocity component along the beam: no shift at 90°, and angle errors matter most at large angles, so velocities are measured at 60° or less. Continuous-wave Doppler gives no depth. Pulsed-wave Doppler samples one depth, and a shift above PRF/2, the Nyquist limit, aliases to the wrong direction. Colour Doppler maps the mean shift; power Doppler maps signal strength, sensitive to slow flow but without direction."),
        EQ("f<sub>D</sub> = 2 f<sub>0</sub> v cos θ / c", "no aliasing while f<sub>D</sub> < PRF / 2"),
        EX("Blood velocity from a Doppler shift", STEM("Pulsed-wave Doppler of an artery.", [f"transmitted frequency = {x4_f:.1f} MHz", f"Doppler shift = {x4_fd / 1000:.1f} kHz", f"angle between beam and flow = {x4_th:.0f}°", "c = 1540 m/s"],
           "Find the [[blood velocity]] and the [[lowest PRF]] that avoids aliasing."),
           [f"v = f<sub>D</sub> c / (2 f<sub>0</sub> cos θ) = {x4_fd:,.0f} × 1540 / (2 × {x4_f:.1f} × 10<sup>6</sup> × 0.5) = {x4_v:.3f} m/s",
            f"PRF/2 must exceed {x4_fd / 1000:.1f} kHz"],
           f"{x4_v:.2f} m/s, and a PRF above {x4_prf / 1000:.1f} kHz."),
        TABLE(["Artifact", "Cause", "Appearance"], ARTIFACTS),
        P("Heating is tracked by the thermal index and cavitation by the mechanical index; output follows ALARA."),

        H("Ultrasound in radiotherapy"),
        P("Transrectal ultrasound (TRUS) guides prostate seed and HDR implants: a biplane probe on a stepper records transverse images in fixed steps, often 5 mm, and a grid on the screen stands for the template holes (QA in AAPM TG-128)."),
        P("For external beam, a transabdominal probe tracked in room coordinates images the prostate through a full bladder and matches it to the planning contours, or to a reference scan from simulation, for a couch shift."),
        P(f"Probe pressure can push the prostate posteriorly by a few millimetres; behind fat, at about 1450 m/s, structures appear deeper by about {fat_pct:.0f}% of the fat thickness; and CT and ultrasound outline the gland differently. AAPM TG-154 (2011) sets QA of spatial accuracy and image quality for these systems."),
    ],
    cards=[
        F("Wavelength in soft tissue", f"λ = c/f, with c = 1540 m/s, the soft-tissue average that scanners assume: {lam5:.2f} mm at 5 MHz.",
          w=[f"λ = 1540 m/s ÷ (5 × 10<sup>6</sup> s<sup>−1</sup>) = {lam5:.3f} mm"]),
        F("Reflection at an interface", f"R = [(Z<sub>2</sub> − Z<sub>1</sub>)/(Z<sub>2</sub> + Z<sub>1</sub>)]<sup>2</sup>, with Z = ρc: about {SOFT_MAX}% or less between soft tissues, about {bone_lo5}–{bone_hi5}% at bone, {100 * r_air:.1f}% at air, hence coupling gel."),
        F("Attenuation in soft tissue", f"About {ALPHA} dB/cm/MHz (roughly 0.3 to 1 by tissue), about proportional to frequency, and counted over the round trip.",
          w=[f"10 cm deep at 5 MHz: 0.5 × 5 × 20 cm = {card_loss:.0f} dB"]),
        F("Echo depth and time", f"d = ct/2: {us_cm:.0f} µs per centimetre of depth at 1540 m/s.", w=[f"t = 2 × 0.01 m ÷ 1540 m/s = {us_cm:.2f} µs"]),
        F("Axial resolution", "Half the spatial pulse length, nλ/2: finer at higher frequency and with fewer cycles per pulse.", w=[f"5 MHz, 3 cycles: 3 × {lam5:.3f} ÷ 2 = {card_ax:.2f} mm"]),
    ],
)

PROBLEMS = [
    # ---- 1-3: sound waves and interfaces
    PR(STEM("Gel is spread on the skin before the transducer is placed.", ask="Why is the gel needed?"), "It displaces air, which would reflect nearly all the sound",
       ["It cools the skin under the face of the transducer", "It raises the frequency of the transmitted pulse", "It focuses the beam at the depth of the organ"],
       f"Soft tissue and air differ in impedance by a factor of about {round(z_ratio_air, -3):,.0f}, so a layer of air reflects {100 * r_air:.1f}% of the intensity and almost nothing enters the patient. The gel, close to tissue in impedance, removes that layer. It does not cool the skin or change the frequency, and the array and its lens do the focusing.", lvl="Easy"),
    PRN(STEM("A pulse meets the surface of a bone at normal incidence (illustrative impedances).", [f"impedance of soft tissue, Z<sub>1</sub> = {q_z1:.2f} MRayl", f"impedance of bone, Z<sub>2</sub> = {q_z2:.2f} MRayl"],
             "What [[fraction of the incident intensity]] is reflected?"), 100 * q_r, [100 * q_a, 100 * (1 - q_r), 100 * q_z1 / q_z2], "{:.1f}%",
        f"The amplitude coefficient is ({q_z2:.2f} − {q_z1:.2f}) / ({q_z2:.2f} + {q_z1:.2f}) = {q_a:.3f}, and the intensity coefficient is its square, {q_r:.3f}: {100 * q_r:.1f}% is reflected and {100 * (1 - q_r):.1f}% transmitted. Leaving the ratio unsquared gives {100 * q_a:.1f}%, the transmitted share is {100 * (1 - q_r):.1f}%, and Z<sub>1</sub>/Z<sub>2</sub> gives {100 * q_z1 / q_z2:.1f}%.", lvl="Moderate"),
    SORT("Rank these media by the speed of sound in them, from the slowest to the fastest.", ["1st (slowest)", "2nd", "3rd", "4th (fastest)"],
         [("Air", 0), ("Fat", 1), ("Muscle", 2), ("Cortical bone", 3)],
         "Air carries sound at about 330–350 m/s, fat at about 1,430–1,480, muscle at about 1,550–1,630, and cortical bone at about 3,000–4,100 m/s. Bone is far stiffer than soft tissue, so sound is fastest there despite its higher density.", lvl="Easy", mode="rank", cap=1),
    # ---- 4-6: attenuation and pulse-echo imaging
    PR(STEM(ask="What does time gain compensation (TGC) do?"), "It amplifies later echoes more, to offset attenuation with depth",
       ["It lowers the transmit power for deep structures, to limit heating", "It shortens the pulses sent to deep structures, to sharpen them", "It delays the next pulse until the deepest echo has returned"],
       "Echoes from deeper reflectors travel farther, return weaker, and return later, so the receiver gain rises with echo time and equal reflectors look equally bright at every depth. TGC does not change the transmitted pulse, and waiting for the deepest echo sets the PRF.", lvl="Easy"),
    PR(STEM(f"A transabdominal scan at {f_hi:.0f} MHz does not show the prostate of a large patient, and the probe is changed to one of {f_lo:.1f} MHz.", ask="What is the effect of the change?"),
       "The deeper gland is seen, with coarser resolution", ["The deeper gland is seen, with finer resolution", "The depth reached falls, with finer resolution", "The depth is unchanged, with coarser resolution"],
       f"Attenuation is about proportional to frequency: at 0.5 dB/cm/MHz an echo from {f_depth:.0f} cm loses {f_loss_hi:.0f} dB over the round trip at {f_hi:.0f} MHz and {f_loss_lo:.1f} dB at {f_lo:.1f} MHz. The wavelength doubles to {f_lam_lo:.2f} mm, so the axial resolution and the beam width at the focus are coarser.", lvl="Moderate"),
    # ---- 7: transducers and resolution
    PRN(STEM("A transrectal probe transmits short pulses into soft tissue.", [f"frequency = {a_f:.1f} MHz", f"cycles per pulse = {a_n}", "c = 1540 m/s"], "What is the [[axial resolution]]?"),
        a_ax, [a_spl, a_lam, a_lam / 2], "{:.2f} mm",
        f"λ = 1540 / ({a_f:.1f} × 10<sup>6</sup>) m = {a_lam:.3f} mm, the spatial pulse length is {a_n}λ = {a_spl:.3f} mm, and the axial resolution is half of it, {a_ax:.2f} mm: reflectors closer than that along the beam return overlapping echoes. The whole pulse length gives {a_spl:.2f} mm, one wavelength {a_lam:.2f} mm, and half a wavelength {a_lam / 2:.2f} mm.", lvl="Moderate"),
    # ---- 8-11: Doppler and artifacts
    # ---- 12: ultrasound in radiotherapy
]

INLINE = {0: [1, 2], 1: [4], 2: [6]}

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
     f"Transabdominal localization: probe pressure, slower sound in fat (about {fat_pct:.0f}% deeper), CT and ultrasound outlines; QA in TG-154."],
]
