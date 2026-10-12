from blocks import *
import math


# ---------------------------------------------------------------- formulas used in the text, the worked examples, and the questions
def quad(*xs):
    """Independent errors add in quadrature: the square root of the sum of their squares."""
    return math.sqrt(sum(x * x for x in xs))

def margin(S, s):
    """CTV-to-PTV margin of the van Herk recipe from the total systematic error S and the total random error s, in the same unit."""
    return 2.5 * S + 0.7 * s

def rot_shift(r, deg):
    """Displacement of a point at distance r from the axis of a small rotation error of deg degrees: r sin(theta)."""
    return r * math.sin(math.radians(deg))

def swept(r, d):
    """Volume swept by a sphere of radius r that moves a distance d along a straight line: a cylinder of length d with a hemisphere at each end."""
    return 4 / 3 * math.pi * r ** 3 + math.pi * r ** 2 * d

def delivery(t_on, duty):
    """Delivery time of a gated field: the beam-on time divided by the duty cycle (a fraction)."""
    return t_on / duty

def max_pitch(t_rot, t_breath):
    """Highest helical pitch that keeps every point in the beam for one breathing period: a point stays in the beam for t_rot / p."""
    return t_rot / t_breath

def sine_duty(f):
    """Duty cycle of an amplitude gate that is open while a sinusoidal breathing signal is in the lowest fraction f of its range, next to end-exhale."""
    return math.acos(1 - 2 * f) / math.pi

def hold_delivery(t_on, hold, rest):
    """Seconds needed to give t_on seconds of beam in breath holds of `hold` seconds, with `rest` seconds of free breathing between holds; and the number of holds."""
    n = math.ceil(t_on / hold - 1e-9)
    return t_on + (n - 1) * rest, n


# ---------------------------------------------------------------- worked examples
TH_EX, RA, RB = 2.0, 30, 90                                         # rotation error (degrees) and two distances from the axis (mm)
dA, dB = rot_shift(RA, TH_EX), rot_shift(RB, TH_EX)
R1, SI1, AP1 = 15, 12, 5                                            # a 30 mm sphere moving 12 mm superior-inferior and 5 mm anterior-posterior
path1 = math.hypot(SI1, AP1)
v_sph1, v_itv1 = swept(R1, 0), swept(R1, path1)                     # mm^3
MU_G, RATE_G, T_B, GATE = 600, 400, 4.0, 1.2                        # MU, MU/min, breathing period (s), gate open per breath (s)
ton_g, duty_g = MU_G / RATE_G, GATE / T_B
tdel_g = delivery(ton_g, duty_g)
SYS_EX, RND_EX = (1.2, 2.1, 1.6), (1.8, 2.4)                        # systematic: setup, delineation, target position; random: setup, breathing (mm)
S_ex, s_ex = quad(*SYS_EX), quad(*RND_EX)
m_ex, m_lin = margin(S_ex, s_ex), margin(sum(SYS_EX), sum(RND_EX))

# ---------------------------------------------------------------- numbers behind the questions
q_th = math.degrees(math.asin(2 / 80))                              # largest rotation error (degrees) that keeps a point 80 mm from the axis within 2 mm
q_th_rad, q_th_turn = 2 / 80, 360 * 2 / 80                          # the angle left in radians; r θ / 360 = δ, without the 2π
q_th_radial = math.degrees(math.acos(1 - 2 / 80))                   # the radial change r (1 − cos θ) set equal to δ
q_p = max_pitch(0.5, 4.0)
v_table = lambda p: p * 24 / 0.5                                    # table speed (mm/s) for 24 mm of detector coverage and a 0.5 s rotation
t_scan, t_scan1 = 300 / v_table(q_p), 300 / v_table(1.0)            # seconds to cover 300 mm
R2, SI2, AP2 = 10, 16, 6
path2 = math.hypot(SI2, AP2)
q_itv, q_itv_sph = swept(R2, path2) / 1000, swept(R2, 0) / 1000     # cm^3
q_itv_lin, q_itv_box = swept(R2, SI2 + AP2) / 1000, (2 * R2 + SI2) * (2 * R2 + AP2) * 2 * R2 / 1000
q_duty = 100 * sine_duty(0.25)                                      # percent
T_ON = 90                                                           # seconds of beam-on time for the ranking question
t_hold, n_hold = hold_delivery(T_ON, 20, 40)
DELIVERIES = [("Free breathing with an ITV, beam on throughout", T_ON), ("Gating with a duty cycle of 50%", delivery(T_ON, 0.5)),
              ("Breath holds of 20 s, with 40 s of free breathing between holds", t_hold), ("Gating with a duty cycle of 30%", delivery(T_ON, 0.3))]
_order = sorted(range(len(DELIVERIES)), key=lambda i: DELIVERIES[i][1])
q_S = quad(1.0, 2.0, 2.0)
S_q, s_q = quad(1.5, 2.0), quad(2.4, 3.2)
q_m = margin(S_q, s_q)


TOPIC = dict(
    id="simulation-motion", domain=4, sub="IV.B", title="Simulation and motion management",
    ref=dict(aapm="TG-66, TG-76, TG-132", khan="", ford="21"),
    guide=[
        H("CT simulation"),
        P("A CT simulator is a CT scanner equipped for planning: [[1|a bore of about 80 to 90 cm (65 to 70 cm in diagnostic CT) that takes the patient with the immobilization, a flat couch top indexed like the treatment couch, and moveable external lasers.]] [[1|Its scanned field of view, typically 50 to 70 cm, is smaller than the bore, and tissue cut off outside it is missing from the dose calculation.]]"),
        P("Radio-opaque markers at the laser crossings show a reference point on the images, kept as tattoos; the isocentre is planned as a shift from it or marked with the moveable lasers."),
        P("[[2|Each kVp used needs its own HU-to-electron-density curve, because the HU of bone changes with the tube voltage.]] Contrast, absent at treatment, usually changes the calculated dose by less than about 2%, more for dense contrast in a beam, so it is overridden to soft tissue or the dose is calculated on a scan without contrast."),
        TABLE(["Check (TG-66, 2003)", "Frequency", "Tolerance"],
              [["[[2|Gantry lasers aligned with the centre of the imaging plane]]", "[[2|Daily]]", "[[2|±2 mm]]"], ["[[2|CT number of water]]", "[[2|Daily]]", "[[2|0 ± 5 HU]]"],
               ["In-plane spatial integrity, along one axis", "Daily", "±1 mm"], ["Table vertical and longitudinal motion", "Monthly", "±1 mm"],
               ["[[2|CT number to electron density conversion]]", "[[2|Annually and after a scanner calibration]]", "Consistent with commissioning"]]),

        H("Registration and multimodality planning"),
        P("Registration maps each point of one image onto the same anatomy in another. [[1|A rigid transformation has six parameters, three translations and three rotations]]; a deformable registration gives each voxel its own displacement and can follow organs that change shape."),
        P("Landmarks, surfaces, or voxel intensities drive a registration. The sum of squared intensity differences suits two CT scans, whose HU agree; [[1|mutual information measures how well the intensity in one image predicts that in the other, without requiring them to be equal, so it works between modalities.]]"),
        P("[[2|TG-132 asks for commissioning with phantoms of known transformation and a check of each clinical result, including the distance between matched landmarks, expected within about one voxel, 2 to 3 mm.]] A deformable result can look plausible yet be wrong where the image is uniform, and dose accumulated through it inherits the error."),
        EQ("δ = r sin θ", "δ = displacement of a point at distance r from the axis of a small rotation error θ"),
        EX("Rotation error across a target", STEM("A rigid registration of an MR to the planning CT leaves a rotation error about an axis through the centre of the brain.", [f"rotation error θ = {TH_EX:.1f}°", f"point A: r = {RA} mm from the axis", f"point B: r = {RB} mm from the axis"], "Find the [[displacement]] of each point."),
           [f"δ = r sin θ, with sin {TH_EX:.1f}° = {math.sin(math.radians(TH_EX)):.4f}", f"A: {RA} × {math.sin(math.radians(TH_EX)):.4f}", f"B: {RB} × {math.sin(math.radians(TH_EX)):.4f}"],
           f"{dA:.2f} mm at A and {dB:.2f} mm at B. The match looks exact near the axis and is off by more than 2 to 3 mm at B."),
        P("[[3|MR holds no electron density and is distorted most far from the centre of the magnet, so it is registered to the planning CT, or an MR-only plan uses bulk densities or a synthetic CT.]] A PET contour at a fixed SUV, such as 2.5, or at 40% to 50% of the maximum depends on lesion size, contrast, and reconstruction. PET averages many breaths, smearing a lesion near the diaphragm, while the CT of a PET-CT freezes one moment."),

        H("Respiratory motion and 4D-CT"),
        P("Breathing moves tumours mostly superior–inferior: upper-lobe lung tumours often under 5 mm, lower-lobe tumours near the diaphragm most, sometimes 2 cm or more, and liver and pancreatic tumours about 1 to 2 cm. TG-76 recommends managing motion beyond 5 mm in any direction, or when it spares substantial normal tissue."),
        P("[[1|A fast helical CT in free breathing catches each slice at a different moment, so a moving tumour can look stretched, shortened, or split.]] A 4D-CT records a breathing signal, from an external marker, a surface camera, or an abdominal belt, while every couch position is imaged for at least one breath, and [[1|sorts the images into usually 10 bins, by phase (time within each breath) or by amplitude (height of the signal)]]. Phase sorting suffers when the depth of breathing varies; amplitude sorting copes better but leaves a bin empty when a breath falls short of it. The dose is often 2 to 4 times that of a helical scan."),
        EQ("time a point stays in the beam = T<sub>rot</sub> / p", "one full breath:   p ≤ T<sub>rot</sub> / T<sub>breath</sub>,   about 0.1 for helical 4D-CT"),
        P("[[2|The maximum intensity projection keeps each voxel's highest value over the phases, so a tumour in lung shows the volume it sweeps, on which an ITV can be drawn; against the diaphragm, chest wall, or mediastinum, as dense as the tumour, its edge is lost and the phases are contoured.]] [[2|The average intensity projection is commonly used for the dose.]]"),
        EX("ITV of a moving tumour", STEM("A spherical lung tumour moves along a straight line between its end-exhale and end-inhale positions.", [f"diameter = {2 * R1} mm", f"motion: {SI1} mm superior–inferior and {AP1} mm anterior–posterior"], "Find the [[extent of the ITV]] along each axis and its [[volume]]."),
           [f"Extent: {2 * R1} + {SI1} = {2 * R1 + SI1} mm superior–inferior, {2 * R1} + {AP1} = {2 * R1 + AP1} mm anterior–posterior, {2 * R1} mm left–right",
            f"Path length = √({SI1}² + {AP1}²) = {path1:.0f} mm",
            f"Volume = (4/3)π × {R1}³ + π × {R1}² × {path1:.0f} = {v_sph1:,.0f} + {v_itv1 - v_sph1:,.0f} mm³"],
           f"{v_itv1 / 1000:.1f} cm³, {v_itv1 / v_sph1:.2f} times the {v_sph1 / 1000:.1f} cm³ of the tumour."),

        H("Managing respiratory motion"),
        P("TG-76 describes these approaches."),
        UL("[[1|<b>Encompassing the motion.</b> An ITV covers the target in every phase]], needing no device but irradiating all the tissue the target sweeps. Mid-ventilation planning uses the phase nearest the time-weighted mean position and puts the breathing in the margin as a random error, for a smaller PTV.",
           "[[1|<b>Abdominal compression.</b> A plate or belt on the upper abdomen limits the excursion of the diaphragm.]]",
           "[[1|<b>Breath hold.</b> The beam is on while the breath is held at a set level]], watched on an external signal or fixed by active breathing control, a spirometer valve that closes at a set lung volume. [[2|For the left breast, deep inspiration moves the heart away from the chest wall.]] Each hold has to be repeatable.",
           "[[1|<b>Gating.</b> The beam is on only while the breathing signal is inside a window, usually near end-exhale.]] [[1|The duty cycle, the fraction of the time the beam is on, is typically 30% to 50%]]; a wider window is faster and leaves more residual motion. An external signal can drift from the internal target, so imaging during treatment checks the correlation.",
           "[[1|<b>Tracking.</b> The MLC, the couch, or a robotic linac follows the target]], located by fiducials or by a model linking an external signal to them, predicting the motion to cover the system delay."),
        PHOTO("simulation-motion-compression-plate"),
        EQ("duty cycle = beam-on time / elapsed time", "[[1|delivery time = beam-on time / duty cycle]]"),
        EX("Delivery time with gating", STEM("A field is delivered with gating.", [f"{MU_G} MU at {RATE_G} MU/min", f"breathing period = {T_B:.1f} s", f"gate open for {GATE:.1f} s of each breath"], "Find the [[duty cycle]] and the [[delivery time]]."),
           [f"Beam-on time = {MU_G} / {RATE_G} = {ton_g:.1f} min", f"Duty cycle = {GATE:.1f} / {T_B:.1f} = {100 * duty_g:.0f}%", f"Delivery time = {ton_g:.1f} / {duty_g:.2f}"],
           f"{tdel_g:.1f} min, {tdel_g - ton_g:.1f} min longer than the {ton_g:.1f} min without gating."),

        H("Margins from combined errors"),
        P("The van Herk recipe, M = 2.5 Σ + 0.7 σ in each direction, aims for 90% of patients to receive at least 95% of the prescribed dose throughout the CTV. Σ is the standard deviation, across patients, of the systematic errors, which repeat in every fraction: delineation, the target position on the planning CT, and the mean setup offset. σ is that of the random errors, which change between fractions. [[2|A systematic error shifts the dose of the whole course, while a random error only blurs its edge]], hence the larger coefficient. [[1|Independent errors of each kind add in quadrature before the recipe is applied.]]"),
        EQ("[[1|Σ = √(Σ<sub>1</sub>² + Σ<sub>2</sub>² + …),   σ = √(σ<sub>1</sub>² + σ<sub>2</sub>² + …)]]", "[[1|M = 2.5 Σ + 0.7 σ]]"),
        EX("Margin from an error budget", STEM("Error estimates in one direction for a site.", [f"systematic: setup {SYS_EX[0]:.1f} mm, delineation {SYS_EX[1]:.1f} mm, target position {SYS_EX[2]:.1f} mm", f"random: setup {RND_EX[0]:.1f} mm, breathing {RND_EX[1]:.1f} mm"], "Find the [[CTV-to-PTV margin]]."),
           [f"Σ = √({SYS_EX[0]:.1f}² + {SYS_EX[1]:.1f}² + {SYS_EX[2]:.1f}²) = {S_ex:.1f} mm", f"σ = √({RND_EX[0]:.1f}² + {RND_EX[1]:.1f}²) = {s_ex:.1f} mm", f"M = 2.5 × {S_ex:.1f} + 0.7 × {s_ex:.1f} = {2.5 * S_ex:.2f} + {0.7 * s_ex:.2f}"],
           f"{m_ex:.2f} mm. Adding the components directly gives Σ = {sum(SYS_EX):.1f} mm and σ = {sum(RND_EX):.1f} mm, and a margin of {m_lin:.1f} mm."),
    ],
    cards=[
        F("Free-breathing CT of a moving tumour", "Each slice catches a different moment of the breath, so the tumour can look stretched, shortened, or split."),
        F("Phase and amplitude sorting", "Usually 10 bins. Phase sorting divides each breath by time, and amplitude sorting by the height of the breathing signal."),
        F("MIP and AIP", "The MIP shows the volume a tumour sweeps through lung, but not against the diaphragm or chest wall. The AIP is used for the dose."),
        F("Duty cycle", "The fraction of the time the beam is on in a gated delivery, typically 30% to 50%.",
          w=[f"Gate open {GATE:.1f} s of a {T_B:.1f} s breath: duty cycle {100 * duty_g:.0f}%", f"{ton_g:.1f} min of beam-on time takes {ton_g:.1f} / {duty_g:.2f} = {tdel_g:.1f} min"]),
        F("Deep inspiration breath hold", "Full lungs move the heart away from the chest wall, out of the tangential fields of a left breast."),
        F("Mid-ventilation planning", "Plans on the phase nearest the time-weighted mean position and adds the breathing to the margin as a random error."),
        F("Errors in quadrature", "Independent errors add as the square root of the sum of their squares, separately for the systematic and the random errors.",
          w=[f"Σ = √({SYS_EX[0]:.1f}² + {SYS_EX[1]:.1f}² + {SYS_EX[2]:.1f}²) = {S_ex:.1f} mm"]),
    ],
)

PROBLEMS = [
    # 1 to 3: CT simulation

    # 4 to 8: registration, MR, and PET
    PR(STEM("An FDG PET-CT of a lower-lobe lung tumour that moves 15 mm is used to define the target. The CT of the PET-CT is a fast helical scan in free breathing.", [], "Which statement describes the two images of the tumour?"),
       "The PET shows it smeared along its path; the CT shows it at one instant", ["The PET shows it at end-inhale; the CT shows its mean position", "Both images show it over its full range of motion", "The attenuation correction from the CT removes the motion from the PET"],
       "A PET acquisition lasts minutes, so the counts from a moving lesion spread along its path and its SUVmax falls, while a fast helical CT catches each slice at one moment. The two can disagree in position near the diaphragm, and the attenuation correction taken from the CT is then misplaced at the edge; the correction cannot remove motion from the PET.", lvl="Challenging"),

    # 9 to 12: respiratory motion and 4D-CT
    PRM(STEM("A lower-lobe lung tumour that moves 15 mm is scanned with a fast helical CT in free breathing.", [], "Which of the following can appear in the images?"),
        ["The tumour looks shorter or longer than it is", "The tumour appears as two separate pieces"],
        ["The tumour is shown at its time-averaged position", "The tumour is shown over its whole range of motion"],
        "Each slice catches the tumour at a different moment. Slices taken while it moves with or against the couch stretch or shorten it, and parts caught at different positions in neighbouring slices appear as separate pieces. The image shows neither the mean position nor the full range, which a 4D-CT is used to see.", lvl="Easy"),
    PR(STEM("A 4D-CT is acquired for a lung tumour that touches the dome of the diaphragm.", [], "Where is the ITV best drawn?"),
       "On the individual phases, because on the MIP the tumour merges with the diaphragm", ["On the MIP, because it always shows the whole swept volume", "On the average intensity projection, because it shows the full motion", "On the end-exhale phase alone, because the tumour rests there longest"],
       "The MIP keeps the highest value of each voxel over the phases. Where the diaphragm, as dense as the tumour, passes through a voxel, the MIP is bright there too, so the edge of the tumour is lost. Contouring the phases avoids this; the average intensity projection blurs the motion and understates its extent, and one phase shows one position.", lvl="Moderate"),

    # 13 to 16: managing motion
    PR(STEM("A patient is treated in breath holds with active breathing control.", [], "What sets the level of each breath hold?"),
       "A valve on a spirometer that closes at a set lung volume", ["A plate pressed on the abdomen at a set pressure", "A window on the breathing signal that turns the beam off", "An implanted marker tracked by x-ray imaging"],
       "The patient breathes through a spirometer, and its valve closes when the lung volume reaches the set value, so each hold is at the same volume. A compression plate limits the motion, a gating window controls the beam and not the breath, and fiducial tracking follows the target.", lvl="Easy"),
    PR(STEM("A patient with left-sided breast cancer is planned with tangential fields. On the free-breathing planning CT the heart lies against the chest wall, inside the fields.", [], "Which technique most reduces the dose to the heart?"),
       "Deep inspiration breath hold", ["Abdominal compression", "An ITV drawn on a 4D-CT", "Gating at end-exhale"],
       "A deep inspiration fills the lungs, which moves the heart away from the chest wall and out of the tangential fields. Compression limits the motion of the diaphragm without separating the heart from the chest wall, an ITV covers the motion instead of reducing it, and end-exhale gating treats with the lungs at their smallest, where the heart is not displaced.", lvl="Moderate"),
    PRN(STEM("A breathing signal is modelled as a sinusoid between end-exhale and end-inhale. An amplitude gate is open while the signal is in the lowest 25% of its range, next to end-exhale.", [], "What is the [[duty cycle]]?"),
        q_duty, [25.0, q_duty / 2, 100 - q_duty], "{:.1f}%",
        f"The signal is ½(1 − cos 2πt/T), which stays below 25% of its range while cos 2πt/T > 0.5, that is within 60° on either side of end-exhale: 120° of the 360° cycle, {q_duty:.1f}%. A sinusoid moves slowly near its turning points, so the gate holds more of the time than its share of the amplitude, 25%. Counting one side of end-exhale gives {q_duty / 2:.1f}%, and {100 - q_duty:.1f}% is the time outside the gate.", lvl="Challenging"),
    SORT("Match each technique to what it does.", ["Deep inspiration breath hold", "Gating", "Real-time tracking", "Abdominal compression", "Mid-ventilation planning"],
         [("Holds the lungs full during the beam, which moves the heart from the chest wall", 0), ("Turns the beam on only while the breathing signal is in a window", 1), ("Moves the beam with the target throughout the breath", 2),
          ("Limits the excursion of the diaphragm with a plate on the abdomen", 3), ("Plans on the mean position and puts the breathing in the margin", 4)],
         "A breath hold stops the motion at one level, gating limits the beam to part of the breath, tracking follows the target, compression shortens the excursion, and mid-ventilation planning treats the breathing as a random error around the mean position.", lvl="Moderate", mode="match", cap=1),

    # 17 and 18: choosing a technique, and delivery times
    PR(STEM("A lower-lobe lung tumour moves 20 mm with regular breathing. The patient cannot hold the breath, and the clinic has gating with an external breathing signal but no tracking.", [], "Which approach spares the most lung while covering the tumour?"),
       "Gating near end-exhale, with a margin for the residual motion in the window", ["An ITV covering the full 20 mm of motion, without gating", "Deep inspiration breath hold with voluntary holds", "A free-breathing helical CT with a standard setup margin"],
       "Gating limits the motion during the beam to the part of the breath inside the window, so the margin covers the residual motion instead of all 20 mm, and regular breathing keeps the external signal a reliable surrogate. The ITV irradiates all the lung the tumour sweeps, a breath hold needs a patient who can hold, and a free-breathing CT neither shows nor covers the motion.", lvl="Challenging"),
    SORT(f"Each field needs {T_ON} s of beam-on time. Rank the deliveries from shortest to longest.", ["1st (shortest)", "2nd", "3rd", "4th (longest)"],
         [(t, _order.index(i)) for i, (t, _) in enumerate(DELIVERIES)],
         f"Gating divides the beam-on time by the duty cycle: {T_ON} / 0.5 = {delivery(T_ON, 0.5):.0f} s and {T_ON} / 0.3 = {delivery(T_ON, 0.3):.0f} s. The breath holds need {n_hold} holds with {n_hold - 1} breaks: {T_ON} + {n_hold - 1} × 40 = {t_hold:.0f} s. Free breathing takes the beam-on time alone, {T_ON} s.", lvl="Moderate", mode="rank", cap=1),

    # 19 to 21: margins
    PR(STEM("A systematic error and a random error are both 3 mm.", [], "Why does the random error need the smaller margin?"),
       "It blurs the dose edge over the fractions, while the systematic error shifts the whole course", ["It averages to zero over the fractions, so it needs no margin", "It is always measured smaller than a systematic error", "It is removed by imaging before every fraction"],
       f"A random error moves the patient differently each day, so over many fractions it widens the penumbra, which costs little coverage, while a systematic error moves every fraction the same way. In the recipe, 3 mm of random error adds 0.7 × 3 = {margin(0, 3):.1f} mm and 3 mm of systematic error adds 2.5 × 3 = {margin(3, 0):.1f} mm. The random error does not vanish: its blurring still lowers the dose at the edge.", lvl="Moderate"),
    TYPED(STEM("Three independent systematic errors in one direction are estimated for a site.", ["setup, Σ<sub>1</sub> = 1.0 mm", "delineation, Σ<sub>2</sub> = 2.0 mm", "target position on the planning CT, Σ<sub>3</sub> = 2.0 mm"], "What is the [[total systematic error Σ]]?"), q_S, 0.01, "mm",
          f"Independent errors add in quadrature: Σ = √(1.0² + 2.0² + 2.0²) = √{1 + 4 + 4} = {q_S:.1f} mm. Adding them directly gives {1.0 + 2.0 + 2.0:.1f} mm, which overstates the total, because the three are unlikely to be at their extremes together.", lvl="Moderate"),
    PRN(STEM("Error estimates in one direction for a lung site.", ["systematic: setup 1.5 mm, delineation 2.0 mm", "random: setup 2.4 mm, breathing 3.2 mm"], "What [[CTV-to-PTV margin]] does the van Herk recipe give?"),
        q_m, [margin(1.5 + 2.0, 2.4 + 3.2), margin(s_q, S_q), margin(S_q, 0)], "{:.2f} mm",
        f"Σ = √(1.5² + 2.0²) = {S_q:.1f} mm and σ = √(2.4² + 3.2²) = {s_q:.1f} mm, so M = 2.5 × {S_q:.1f} + 0.7 × {s_q:.1f} = {q_m:.2f} mm. Adding the components directly gives {margin(1.5 + 2.0, 2.4 + 3.2):.2f} mm, exchanging Σ and σ gives {margin(s_q, S_q):.2f} mm, and leaving out the random errors gives {margin(S_q, 0):.2f} mm.", lvl="Challenging"),
]

INLINE = {1: [1], 2: [2, 3], 3: [4, 5, 6, 7]}

TERMS = ["CT simulator", "deformable registration", "mutual information", "synthetic CT", "maximum intensity projection", "duty cycle", "mid-ventilation", "quadrature"]

TAKE = [
    ["A CT simulator has a wide bore, a flat indexed couch top, and moveable lasers. Tissue outside the scanned field of view is lost from the dose calculation.",
     "TG-66, daily: lasers ±2 mm and water 0 ± 5 HU. One HU-to-electron-density curve per kVp, checked annually."],
    ["A rigid registration has six parameters; mutual information registers different modalities.",
     "TG-132: commission with phantoms of known transformation and check every registration; landmarks agree within about one voxel, 2 to 3 mm.",
     "MR holds no electron density: plan with a registered CT, bulk densities, or a synthetic CT."],
    ["Free-breathing CT can stretch, shorten, or split a moving tumour. A 4D-CT sorts the images into about 10 bins, by phase or by amplitude.",
     "The MIP shows the volume a tumour sweeps through lung, but loses its edge against the diaphragm or chest wall. The AIP is used for the dose."],
    ["Encompass, compress, hold, gate, or track. Gated delivery time = beam-on time / duty cycle, with duty cycles of 30% to 50%.",
     "Deep inspiration breath hold moves the heart away from the chest wall in left breast treatment."],
    ["Independent errors of each kind add in quadrature; then M = 2.5 Σ + 0.7 σ.",
     "A systematic error shifts the dose of the whole course; a random error only blurs its edge."],
]
