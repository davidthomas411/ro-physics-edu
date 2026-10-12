from blocks import *
import math

# ---------------------------------------------------------------- this chapter's formulas
def g_min(d_in, d_out):
    """Minification gain of an image intensifier: (input phosphor diameter / output phosphor diameter)²."""
    return (d_in / d_out) ** 2

def g_bright(d_in, d_out, flux):
    """Brightness gain: minification gain × flux gain."""
    return g_min(d_in, d_out) * flux

def mag_rate(rate, fov_large, fov_small):
    """Input (and entrance) air-kerma rate of an intensifier after its field of view shrinks, with the output brightness held: × (FOV_large / FOV_small)²."""
    return rate * (fov_large / fov_small) ** 2

def kap(k_gy, area_cm2):
    """Kerma-area product (Gy cm²) from the air kerma and the beam area in one plane."""
    return k_gy * area_cm2

def moved(k, area, d0, d):
    """Air kerma and beam area at a distance d from the focal spot, from their values at d0 (in air)."""
    return k * (d0 / d) ** 2, area * (d / d0) ** 2

# ---------------------------------------------------------------- values quoted in the text (about, where they vary)
FLUX, D_OUT = 50, 2.5                         # flux gain of an intensifier, about 50; output phosphor diameter, about 2.5 cm
KV_LO, KV_HI = 25, 35                         # accelerating voltage of an intensifier, about 25 to 35 kV
MA_LO, MA_HI = 1, 5                           # tube current in continuous fluoroscopy, about 1 to 5 mA
WE = 0.876                                    # cGy of air kerma per R in dry air, as in the exposure chapter
LIM_N, LIM_H = 88, 176                        # 21 CFR 1020.32: mGy/min at the measurement point, normal mode with automatic control and high-level mode
R_N, R_H = 10, 20                             # the same limits in R/min, as the rule also gives them
T_ALARM = 5                                   # min of cumulative beam-on time before the audible signal
SSD_FIX, SSD_MOB = 38, 30                     # minimum source-to-skin distance (cm): fixed and mobile units
TH_ERY, TH_EPI = 2, 3                         # Gy: transient erythema, temporary epilation (about)

ARTIFACTS = [
    ["Pincushion distortion", "The curved input surface is mapped onto a flat output", "Magnification rises toward the edge, and straight lines bow inward"],
    ["S-distortion", "Magnetic fields, even the Earth's, bend the electron paths", "Straight lines bend into an S that changes as the C-arm turns"],
    ["Vignetting", "Less minification and light collection at the edge", "The edge is darker than the center"],
    ["Veiling glare", "Light, electrons, and x-rays scattered inside the tube and its output window", "A haze from bright regions lowers the contrast of dark ones"],
    ["Lag", "Signal that persists from earlier frames, mainly in older camera tubes", "Moving objects leave a trail"],
]
RULES = [
    ["Air-kerma rate, normal mode with automatic control", f"At most {LIM_N} mGy/min (about {R_N} R/min)"],
    ["Air-kerma rate, high-level mode", f"At most {LIM_H} mGy/min (about {R_H} R/min), with continuous activation and an audible signal"],
    ["Recording of images", "Exempt from these limits"],
    ["Timer", f"An audible signal after at most {T_ALARM} min of cumulative beam-on time, until reset"],
    ["Source-to-skin distance", f"At least {SSD_FIX} cm on fixed units and {SSD_MOB} cm on mobile units"],
]

# ---------------------------------------------------------------- worked examples
d1 = 30.0
gm1, gb1 = g_min(d1, D_OUT), g_bright(d1, D_OUT, FLUX)                                    # 144 and 7,200
f2a, f2b, r2 = 30.0, 20.0, 12.0                                                           # fields (cm) and entrance rate (mGy/min) in the 30 cm field
g2a, g2b = g_min(f2a, D_OUT), g_min(f2b, D_OUT); r2b = mag_rate(r2, f2a, f2b)
k3, a3, d3s, d3c = 0.40, 100.0, 60.0, 30.0                                                # Gy at the skin, cm² at the skin, cm to the skin, cm to the chamber
p3 = kap(k3, a3); k3c, a3c = moved(k3, a3, d3s, d3c); p3c = kap(k3c, a3c)
mag_card = (30 / 15) ** 2

# ---------------------------------------------------------------- numbers in the questions
q_d, q_f = 23.0, 60                                                                       # brightness gain
q_gm = g_min(q_d, D_OUT); q_gb = q_gm * q_f; q_nosq = q_d / D_OUT * q_f; q_add = q_gm + q_f
m_a, m_b, m_r = 40.0, 25.0, 10.0                                                          # magnification: fields (cm), entrance rate (mGy/min)
m_new = mag_rate(m_r, m_a, m_b); m_lin = m_r * m_a / m_b; m_inv = m_r * (m_b / m_a) ** 2
c_p, c_dc, c_ds = 24.0, 25.0, 65.0                                                        # KAP reading (Gy cm²), chamber and skin distances (cm)
c_isq = c_p * (c_dc / c_ds) ** 2; c_area = c_p * (c_ds / c_dc) ** 2; c_lin = c_p * c_dc / c_ds
t_w, t_h, t_k = 10.0, 12.0, 0.30                                                          # typed KAP: field at the skin (cm) and air kerma there (Gy)
t_kap = kap(t_k, t_w * t_h)
v_a, v_b = 30.0, 15.0                                                                     # magnification: skin dose rate against KAP rate
v_rate, v_area = (v_a / v_b) ** 2, (v_b / v_a) ** 2; v_kap = v_rate * v_area

TOPIC = dict(
    id="fluoroscopy", domain=4, sub="IV.A", title="Fluoroscopy and image intensifiers",
    ref=dict(aapm="", khan="", ford="19"),
    guide=[
        H("Fluoroscopic imaging chain"),
        P(f"Fluoroscopy forms x-ray images in real time. The chain runs from the generator and tube, through the patient, to an image receptor (an image intensifier with a video camera, or a flat-panel detector) and a monitor. Fluoroscopy runs for minutes, so, unlike the hundreds of milliamperes of a radiograph, the tube current is about {MA_LO} to {MA_HI} mA in continuous mode, or the beam is pulsed. Each frame is noisier than a radiograph, and the eye averages several frames. In radiotherapy, fluoroscopy served the conventional simulator, guides brachytherapy and intraoperative work on mobile C-arms, and runs on the kilovoltage imager of a linac during gating."),

        H("Image intensifier"),
        P(f"In an image intensifier, an evacuated tube, the x-rays are absorbed in the input phosphor, sodium-doped caesium iodide, whose needle-shaped crystals channel the light, so a thick layer absorbs most x-rays without much blur. A photocathode on the phosphor emits electrons in proportion to the light. Focusing electrodes and an anode at about {KV_LO} to {KV_HI} kV accelerate the electrons and focus the image, inverted, onto an output phosphor about {D_OUT:g} cm across, viewed by the camera."),
        P(f"Each accelerated electron yields many light photons at the output, about {FLUX} per light photon at the input: the flux gain. Compressing the image onto the small output phosphor adds the minification gain."),
        EQ("G<sub>B</sub> = G<sub>min</sub> × G<sub>flux</sub>,   G<sub>min</sub> = (d<sub>in</sub> / d<sub>out</sub>)²", "d<sub>in</sub>, d<sub>out</sub> = diameters of the input and output phosphors"),
        EX("Brightness gain", STEM("An image intensifier in its largest field.", [f"input phosphor diameter = {d1:.0f} cm", f"output phosphor diameter = {D_OUT:g} cm", f"flux gain = {FLUX}"], "Find the [[minification gain]] and the [[brightness gain]]."),
           [f"G<sub>min</sub> = ({d1:.0f} / {D_OUT:g})² = {d1 / D_OUT:.0f}² = {gm1:.0f}", f"G<sub>B</sub> = {gm1:.0f} × {FLUX} = {gb1:,.0f}"],
           f"G<sub>min</sub> = {gm1:.0f} and G<sub>B</sub> = {gb1:,.0f}."),
        TABLE(["Artifact", "Cause", "Effect on the image"], ARTIFACTS),

        H("Flat-panel detectors"),
        P("Flat panels have replaced the intensifier in most fixed fluoroscopes and linac kilovoltage imagers. In an indirect panel, thallium-doped caesium iodide turns the x-rays into light, and an amorphous-silicon photodiode in each pixel, switched by a thin-film transistor, turns the light into charge. In a direct panel, amorphous selenium under a high voltage turns the x-rays straight into charge. With no electron optics, a panel has no pincushion or S-distortion and ignores magnetic fields; after gain calibration its response is uniform, and it is linear over a wider range of air kerma. Lag remains."),

        H("Brightness control and magnification"),
        P("Automatic brightness control holds the receptor signal constant: a sensor reads a central region of the image, and the generator adjusts the kV and mA, on many units also the pulse width and copper filtration. A thicker patient, or a metal applicator in the sensed region, drives the output up. A lower kV with a higher mA gives more contrast at a higher skin dose; a higher kV with copper does the reverse."),
        P("A smaller field of view on an intensifier maps a smaller central part of the input onto the whole output, and the collimators close to match. The image is larger and sharper, but the minification gain falls with the square of the field-of-view ratio, so the automatic control raises the air-kerma rate at the input and the skin by about that square."),
        EQ("K̇<sub>small</sub> / K̇<sub>large</sub> ≈ (FOV<sub>large</sub> / FOV<sub>small</sub>)²   (image intensifier)"),
        EX("Dose rate in magnification mode", STEM(f"An image intensifier is switched from its {f2a:.0f} cm field to its {f2b:.0f} cm field. The automatic brightness control holds the output brightness.", [f"entrance air-kerma rate in the {f2a:.0f} cm field = {r2:.0f} mGy/min", f"output phosphor diameter = {D_OUT:g} cm"], f"Find the [[entrance air-kerma rate]] in the {f2b:.0f} cm field."),
           [f"G<sub>min</sub> falls from ({f2a:.0f} / {D_OUT:g})² = {g2a:.0f} to ({f2b:.0f} / {D_OUT:g})² = {g2b:.0f}", f"The input must rise by {g2a:.0f} / {g2b:.0f} = ({f2a:.0f} / {f2b:.0f})² = {g2a / g2b:.2f}", f"K̇ = {r2:.0f} mGy/min × {g2a / g2b:.2f}"],
           f"{r2b:.0f} mGy/min, {r2b / r2:.2f} times the rate in the {f2a:.0f} cm field."),
        P("Pulsed fluoroscopy delivers pulses a few milliseconds long at a selected rate, such as 30, 15, or 7.5 per second, which freezes motion; at a fixed dose per pulse the dose rate is proportional to the pulse rate. Last-image hold keeps the final frame on the monitor after the beam stops."),

        H("Patient and staff dose"),
        P("The air-kerma rate where the beam enters the patient sets the skin dose rate. The US performance standard for fluoroscopes, 21 CFR 1020.32, limits it."),
        TABLE(["Requirement (21 CFR 1020.32)", "Value"], RULES),
        P("The kerma-area product (KAP), or dose-area product, is the air kerma times the beam area, in Gy cm², read by a transmission chamber at the collimator. In air it is the same at every distance, since the kerma falls as 1/d² while the area grows as d², and at a fixed kerma it rises in proportion to the field area. It follows the energy delivered to the patient, and so the stochastic risk."),
        EQ("P<sub>KA</sub> = K<sub>a</sub> × A", "K<sub>a</sub> ∝ 1/d²,   A ∝ d²,   so P<sub>KA</sub> is the same at every distance"),
        EX("Kerma-area product at two distances", STEM("A C-arm exposure. Ignore attenuation in air.", [f"air kerma at the skin, free in air = {k3:.2f} Gy", "field at the skin = 10 cm × 10 cm", f"skin = {d3s:.0f} cm from the focal spot", f"transmission chamber = {d3c:.0f} cm from the focal spot"], "Find the [[kerma-area product]] at the skin and at the chamber."),
           [f"At the skin: {k3:.2f} Gy × {a3:.0f} cm² = {p3:.0f} Gy cm²", f"At the chamber: area = {a3:.0f} cm² × ({d3c:.0f} / {d3s:.0f})² = {a3c:.0f} cm², air kerma = {k3:.2f} Gy × ({d3s:.0f} / {d3c:.0f})² = {k3c:.2f} Gy", f"Product = {k3c:.2f} Gy × {a3c:.0f} cm² = {p3c:.0f} Gy cm²"],
           f"{p3:.0f} Gy cm² in both planes."),
        P(f"Skin injury follows the peak skin dose, the cumulative dose to the most-irradiated area of skin. Thresholds are about {TH_ERY} Gy for transient erythema and {TH_EPI} Gy for temporary epilation; higher doses cause desquamation, ulceration, and necrosis. Changing the beam angle spreads the dose."),
        P("Staff dose comes mostly from scatter off the patient, strongest on the side where the beam enters. With the tube under the table that scatter goes toward the floor, and in a lateral view the operator stands on the receptor side. Collimation, a low pulse rate, last-image hold, distance, and shields lower it; a receptor close to the patient lowers the skin dose."),
    ],
    cards=[
        F("Tube current in fluoroscopy", f"About {MA_LO} to {MA_HI} mA in continuous mode, against hundreds for a radiograph, because the beam runs for minutes."),
        F("Brightness gain of an image intensifier", f"Minification gain × flux gain. The minification gain is (d<sub>in</sub>/d<sub>out</sub>)², and the flux gain is about {FLUX}.",
          w=[f"{d1:.0f} cm input, {D_OUT:g} cm output: ({d1:.0f} / {D_OUT:g})² × {FLUX} = {gm1:.0f} × {FLUX} = {gb1:,.0f}"]),
        F("Geometric distortion of an intensifier", "Pincushion: magnification rising toward the edge, from the curved input. S-distortion: magnetic fields bending the electron paths."),
        F("Indirect and direct flat panels", "Indirect: thallium-doped CsI turns x-rays into light, read by a-Si photodiodes switched by thin-film transistors. Direct: a-Se under a high voltage turns x-rays into charge."),
        F("Automatic brightness control", "Holds the receptor signal constant by adjusting kV and mA. A thicker patient or metal in the sensed region raises the output."),
        F("Magnification mode of an intensifier", "The air-kerma rate at the skin rises about as (FOV<sub>large</sub>/FOV<sub>small</sub>)².",
          w=[f"30 cm to 15 cm: (30 / 15)² = {mag_card:.0f}"]),
        F("US limits on fluoroscopic air-kerma rate", f"{LIM_N} mGy/min (about {R_N} R/min) in normal mode; {LIM_H} mGy/min (about {R_H} R/min) in high-level mode; recording exempt (21 CFR 1020.32)."),
        F("Kerma-area product", "Air kerma × beam area, in Gy cm². The same at every distance from the source; proportional to the field area at a fixed kerma."),
        F("Skin reaction thresholds", f"About {TH_ERY} Gy for transient erythema and {TH_EPI} Gy for temporary epilation."),
        F("Scatter and staff position", "Scatter is strongest where the beam enters the patient: tube under the table, and the operator on the receptor side in a lateral view."),
    ],
)

PROBLEMS = [
    PR(STEM(ask="Why does continuous fluoroscopy run the x-ray tube at a few milliamperes, while a radiograph uses hundreds?"),
       "The beam runs for minutes, so the patient dose and tube heating must stay low",
       ["A lower tube current raises the contrast between bone and soft tissue", "A lower tube current lowers the noise in each frame", "A lower tube current raises the mean energy of the beam"],
       "A radiograph gathers its photons in one short exposure, while fluoroscopy makes images for minutes, so a radiographic current would give a large dose and overheat the anode. Each frame then holds fewer photons and more noise. The current scales the number of photons without changing their energies, so it changes neither the contrast nor the mean energy.", lvl="Easy"),
    SORT("Match each part of an image-intensifier chain to its role.", ["Input phosphor", "Photocathode", "Focusing electrodes and anode", "Output phosphor", "Video camera"],
         [("Absorbs the x-rays and emits light", 0), ("Emits electrons where light strikes it", 1), ("Accelerates and focuses the electron image", 2), ("Turns the electrons into a small, bright light image", 3), ("Turns the light image into a signal for the monitor", 4)],
         "The caesium iodide input phosphor turns x-rays into light, the photocathode turns the light into electrons, the electrodes and anode accelerate and focus them onto the output phosphor, which turns them back into light, and the camera turns that light into the video signal.", lvl="Easy", mode="match", cap=1),
    PRN(STEM("An image intensifier.", [f"input phosphor diameter = {q_d:g} cm", f"output phosphor diameter = {D_OUT:g} cm", f"flux gain = {q_f}"], "What is the [[brightness gain]]?"), q_gb, [q_nosq, q_gm, q_add], "{:,.0f}",
        f"G<sub>min</sub> = ({q_d:g} / {D_OUT:g})² = {q_gm:.2f}, and G<sub>B</sub> = {q_gm:.2f} × {q_f} = {q_gb:,.0f}. Leaving out the square gives {q_nosq:,.0f}, leaving out the flux gain gives {q_gm:.0f}, and adding the two gains gives {q_add:.0f}.", lvl="Moderate"),
    PR(STEM("An indirect flat-panel detector.", [], "Which layer turns the x-rays into light?"),
       "Thallium-doped caesium iodide", ["Amorphous selenium", "Amorphous-silicon photodiodes", "Thin-film transistors"],
       "In an indirect panel the caesium iodide scintillator turns x-rays into light, the amorphous-silicon photodiodes turn the light into charge, and the thin-film transistors switch each pixel's charge out for reading. Amorphous selenium is the layer of a direct panel, which turns x-rays into charge with no light stage.", lvl="Easy"),
    PRN(STEM(f"An image intensifier is switched from its {m_a:.0f} cm field to its {m_b:.0f} cm field. The automatic brightness control holds the output brightness, and the collimators close to the new field.", [f"entrance air-kerma rate in the {m_a:.0f} cm field = {m_r:.1f} mGy/min"], f"What is the [[entrance air-kerma rate]] in the {m_b:.0f} cm field?"),
        m_new, [m_lin, m_inv, m_r], "{:.1f} mGy/min",
        f"The minification gain falls by ({m_b:.0f} / {m_a:.0f})², so the input air-kerma rate rises by ({m_a:.0f} / {m_b:.0f})² = {(m_a / m_b) ** 2:.2f}: {m_r:.1f} × {(m_a / m_b) ** 2:.2f} = {m_new:.1f} mGy/min. The ratio without the square gives {m_lin:.1f}, the inverted square gives {m_inv:.1f}, and an unchanged {m_r:.1f} mGy/min ignores the control.", lvl="Moderate"),
    PR(STEM("A C-arm under automatic brightness control images a gynecologic applicator. The metal tandem moves into the central region that the control samples.", [], "How does the control respond?"),
       "It raises the kV and mA, raising the dose rate and overexposing the tissue around the tandem",
       ["It lowers the kV and mA, because the metal raises the signal in the sensed region", "It keeps the output unchanged, because it samples the whole field equally", "It switches to high-level mode to penetrate the metal"],
       "The metal transmits few photons, so the sensed signal falls and the control drives the output up until that region reaches its set level, overexposing the tissue around it at a higher dose rate; moving the metal away from the center of the field avoids it. Metal lowers the signal, the control samples a central region, and high-level mode needs a deliberate, continuous activation.", lvl="Challenging"),
    PR(STEM("A fluoroscope made after May 1995 runs in normal mode with automatic exposure-rate control.", [], "What is the maximum air-kerma rate at the measurement point under 21 CFR 1020.32?"),
       f"{LIM_N} mGy/min (about {R_N} R/min)", [f"{LIM_H} mGy/min (about {R_H} R/min)", f"{LIM_N / 10:g} mGy/min (about {R_N / 10:g} R/min)", f"{LIM_N * 10} mGy/min (about {R_N * 10} R/min)"],
       f"Normal mode is limited to {LIM_N} mGy/min, the air kerma of {R_N} R/min ({R_N} R × {10 * WE:.2f} mGy/R = {R_N * 10 * WE:.1f} mGy). {LIM_H} mGy/min applies only in high-level mode, which needs continuous activation and sounds a signal, and the other two values are ten times too low or too high.", lvl="Easy"),
    PRN(STEM("A transmission chamber at the collimator of a C-arm reads the kerma-area product. Ignore attenuation in air and in the table.", [f"chamber = {c_dc:.0f} cm from the focal spot", f"reading = {c_p:.0f} Gy cm²", f"entrance skin = {c_ds:.0f} cm from the focal spot"], "What is the [[kerma-area product]] at the entrance skin?"),
        c_p, [c_isq, c_area, c_lin], "{:.1f} Gy cm²",
        f"Between the chamber and the skin the air kerma falls by ({c_dc:.0f} / {c_ds:.0f})² = {(c_dc / c_ds) ** 2:.3f} and the area grows by ({c_ds:.0f} / {c_dc:.0f})² = {(c_ds / c_dc) ** 2:.2f}, so the product is unchanged at {c_p:.1f} Gy cm². The inverse square alone gives {c_isq:.1f}, the area alone {c_area:.1f}, and a linear distance factor {c_lin:.1f} Gy cm².", lvl="Moderate"),
    PRM(STEM("A C-arm with automatic brightness control images the same anatomy of one patient.", [], "Which of these lower the patient's entrance skin dose?"),
        ["Moving the image receptor closer to the patient", "Adding copper filtration to the beam", "Lowering the pulse rate at the same dose per pulse"],
        ["Selecting a smaller field of view on the intensifier", "Lowering the kV and raising the mA", "Moving the x-ray tube closer to the patient"],
        "The control holds the air kerma at the receptor, so the entrance air kerma is that value divided by the patient's transmission and multiplied by the square of the ratio of the source-to-receptor and source-to-skin distances. A receptor closer to the patient lowers that ratio, copper removes low-energy photons that the patient would absorb, and fewer pulses deliver less dose. A smaller intensifier field raises the rate by the square of the field ratio, a lower kV lowers the transmission, and a tube closer to the patient raises the distance ratio.", lvl="Challenging"),
    PR(STEM("A C-arm is turned to a lateral projection during an applicator insertion.", [], "On which side of the patient is the scattered radiation strongest?"),
       "The side where the beam enters, next to the x-ray tube",
       ["The side where the beam exits, next to the image receptor", "Both sides equally, because scatter leaves the patient evenly", "Toward the floor, below the table"],
       "Backscatter from the entrance surface is stronger than the scatter that leaves through the far side, which the patient attenuates, so the operator stands on the receptor side. Scatter is not even in all directions, and the strongest scatter goes toward the floor only in a frontal view with the tube under the table.", lvl="Moderate"),
    PR(STEM(f"An image intensifier is switched from its {v_a:.0f} cm field to its {v_b:.0f} cm field. The collimators close to the new field, and the automatic brightness control raises the input air-kerma rate by the square of the field ratio.", [], "How do the skin dose rate inside the field and the kerma-area product rate change?"),
       "The skin dose rate rises about fourfold, and the KAP rate stays about the same",
       ["Both rise about fourfold", "Both stay about the same, because the control holds the dose", "The skin dose rate doubles, and the KAP rate halves"],
       f"The air-kerma rate rises by ({v_a:.0f} / {v_b:.0f})² = {v_rate:.0f}, while the irradiated area shrinks by ({v_b:.0f} / {v_a:.0f})² = {v_area:.2f}, so the KAP rate changes by a factor of {v_kap:.1f}: about the same energy goes into a smaller area of skin. Forgetting the smaller area gives fourfold for both, the control holds the brightness and not the dose, and a linear field ratio gives the twofold changes.", lvl="Challenging"),
    TYPED(STEM("A C-arm exposure ends with the values below.", [f"field at the skin = {t_w:.0f} cm × {t_h:.0f} cm", f"air kerma at the skin, free in air = {t_k:.2f} Gy"], "What is the [[kerma-area product]]?"), t_kap, 0.02, "Gy cm²",
          f"KAP = {t_k:.2f} Gy × {t_w:.0f} cm × {t_h:.0f} cm = {t_k:.2f} × {t_w * t_h:.0f} = {t_kap:.0f} Gy cm². Adding the sides in place of multiplying them gives {t_k * (t_w + t_h):.1f} Gy cm².", lvl="Moderate"),
]

INLINE = {0: [1], 1: [2, 3], 2: [4], 3: [5, 6]}          # questions on the last section, and the rest, form the practice set

TERMS = ["flux gain", "minification gain", "automatic brightness control", "pulsed fluoroscopy", "last-image hold", "kerma-area product", "peak skin dose"]

TAKE = [
    [f"Fluoroscopy runs for minutes at about {MA_LO} to {MA_HI} mA, continuous or pulsed, so each frame is noisier than a radiograph."],
    [f"CsI(Na) needles, a photocathode, electrons accelerated by about {KV_LO} to {KV_HI} kV, and an output phosphor about {D_OUT:g} cm across.",
     f"Brightness gain = (d<sub>in</sub>/d<sub>out</sub>)² × flux gain (about {FLUX}).",
     "Artifacts: pincushion and S-distortion, vignetting, veiling glare, and lag."],
    ["Indirect panel: CsI(Tl) on a-Si photodiodes. Direct panel: a-Se. No geometric distortion or magnetic sensitivity; lag remains."],
    ["Automatic brightness control holds the receptor signal: a thicker patient or metal in the sensed region raises the dose rate.",
     "Intensifier magnification raises the skin dose rate by about (FOV<sub>large</sub>/FOV<sub>small</sub>)².",
     "Dose rate ∝ pulse rate at a fixed dose per pulse; last-image hold adds no dose."],
    [f"US limits: {LIM_N} mGy/min (about {R_N} R/min); {LIM_H} mGy/min in high-level mode; recording exempt.",
     f"KAP = air kerma × area, the same at every distance. Skin: about {TH_ERY} Gy transient erythema, {TH_EPI} Gy epilation.",
     "Scatter is strongest on the tube side: tube under the table, operator on the receptor side."],
]
