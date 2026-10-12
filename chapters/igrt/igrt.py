from blocks import *
import math

# ---------------------------------------------------------------- this chapter's formulas
def vec(*d):
    """Length of a shift vector from its components."""
    return math.sqrt(sum(x * x for x in d))

def rot_shift(r, deg):
    """Displacement of a point at distance r from the axis of a small rotation of deg degrees: r sin θ (the exact chord is 2r sin(θ/2))."""
    return r * math.sin(math.radians(deg))

def mean(xs):
    return sum(xs) / len(xs)

def resid_sys(sigma, n):
    """Standard deviation of the systematic error left after correcting by the mean of n fractions whose random error is sigma: σ/√n."""
    return sigma / math.sqrt(n)

def d_weighted(dc, dp):
    """Weighted dose in a cylindrical phantom: one-third of the dose at the center plus two-thirds of the mean dose at the periphery."""
    return dc / 3 + 2 * dp / 3

def share(d_cgy, n, rx_gy):
    """Imaging dose of a course as a percentage of the prescription: n scans of d_cgy against rx_gy."""
    return 100 * n * d_cgy / (100 * rx_gy)

ME, CB = 0.511, 299.8                               # electron rest energy (MeV); r [m] = pc [MeV] / (299.8 B [T])
def pc_rel(t):
    """Momentum times c (MeV) of an electron of kinetic energy t (MeV)."""
    return math.sqrt(t * t + 2 * t * ME)

def radius(pc, b):
    """Radius (mm) of the path of an electron moving perpendicular to a field of b tesla."""
    return 1000 * pc / (CB * b)

sgn = lambda v, d=1: f"{v:+.{d}f}".replace("-", "−")

# ---------------------------------------------------------------- values quoted in the text (ranges where they vary)
FOV_FULL, FOV_HALF = 25, 45                         # cm, approximate CBCT fields of view: panel centered, panel offset
TG142_ISO, TG142_SRS = 2.0, 1.0                     # mm, TG-142 daily imaging and treatment isocenter coincidence; also the monthly CBCT geometric distortion
TG180_PCT = 5                                       # %, TG-180: imaging dose above this share of the target dose is included in the plan
DOSE = [
    ["MV portal image pair", "Field edges, bone", "[[1|About 1–5 cGy]]"],
    ["kV radiograph pair", "Bone, implanted markers", "Well under 1 cGy"],
    ["kV CBCT", "Bone and soft tissue", "[[1|About 0.2–2 cGy, highest in the pelvis]]"],
    ["MV CBCT", "Bone and soft tissue at lower contrast", "[[1|About 3–10 cGy]]"],
    ["Surface imaging", "Skin surface", "None"],
    ["Ultrasound", "Soft tissue", "None"],
    ["Electromagnetic transponders", "Implanted transponders", "None"],
    ["MR", "Soft tissue", "None"],
]
r1_15, r1_035 = radius(pc_rel(1.0), 1.5), radius(pc_rel(1.0), 0.35)      # 1 MeV electron at the two field strengths
card_rot = rot_shift(100, 1.0)                                           # mm at 10 cm for 1°

# ---------------------------------------------------------------- worked examples
ex_d, ex_al = (2.0, -2.8, 1.5), 3.0                 # couch shifts (mm): lateral, longitudinal, vertical; action level on the length
ex_len = vec(*ex_d)
ex_r, ex_th = 80.0, 1.5                             # mm from the isocenter, degrees of yaw left uncorrected
ex_rot = rot_shift(ex_r, ex_th)
ex_sh, ex_sig = (3.2, 1.4, 2.6), 2.0                # vertical shifts of fractions 1 to 3 (mm), random error (mm)
ex_mean, ex_res = mean(ex_sh), resid_sys(ex_sig, len(ex_sh))
ex_dc, ex_dp, ex_n, ex_rx = 1.2, 1.8, 39, 78.0      # cGy at the center and the periphery, fractions, prescription (Gy)
ex_dw = d_weighted(ex_dc, ex_dp)
ex_tot, ex_pct = ex_n * ex_dw, share(ex_dw, ex_n, ex_rx)

# ---------------------------------------------------------------- numbers in the questions
q_d = (2.5, -3.0, 1.0)                              # couch shifts (mm)
q_len = vec(*q_d)
q_abs, q_sum, q_max = sum(abs(x) for x in q_d), sum(q_d), max(abs(x) for x in q_d)
t_r, t_th = 100.0, 2.0                              # mm, degrees of roll
t_rot = rot_shift(t_r, t_th)
s_sig, s_n = 3.0, 3                                 # random error (mm), imaged fractions
s_res = resid_sys(s_sig, s_n)
m_t, m_b = 2.0, 1.5                                 # MeV, T
m_r = radius(pc_rel(m_t), m_b)
m_cl, m_ke, m_lo = radius(math.sqrt(2 * m_t * ME), m_b), radius(m_t, m_b), radius(pc_rel(m_t), 0.35)
w_dc, w_dp = 1.0, 1.9                               # cGy
w_dw, w_avg, w_swap = d_weighted(w_dc, w_dp), (w_dc + w_dp) / 2, d_weighted(w_dp, w_dc)
f_d, f_n, f_rx = 1.8, 28, 70.0                      # cGy per scan, fractions, Gy
f_pct, f_tot = share(f_d, f_n, f_rx), f_n * f_d
o_sig = resid_sys(3.0, 3)                           # offline residual quoted in the online-against-offline question

TOPIC = dict(
    id="igrt", domain=4, sub="IV.B", title="Image guidance and treatment verification",
    ref=dict(aapm="TG-104, TG-142, TG-179, TG-180", khan="", ford="21"),
    guide=[
        H("Planar imaging and EPID"),
        P("An electronic portal imaging device (EPID), an amorphous-silicon flat panel with a scintillator opposite the treatment head, forms a megavoltage portal image with the treatment beam. [[1|It shows the field edges, air, and bone at low contrast, with little soft tissue.]] Its images of each field, before treatment or through the patient (transit dosimetry), also verify the delivered dose."),
        P("Kilovoltage imaging uses an x-ray tube and flat panel on the gantry at 90° to the beam, or two tubes and panels fixed in the room. Two radiographs at different angles locate the patient in three dimensions, [[1|with better bone contrast than MV, at well under 1 cGy per pair]]. Each is matched to a digitally reconstructed radiograph (DRR), a projection through the planning CT from the source position."),
        P("[[2|A bony match places the skeleton, not the target. The prostate moves relative to the pelvic bones as the rectum and bladder fill, at times by several millimetres.]] [[2|Gold markers implanted in the gland show on the radiographs and locate it directly]], though not its shape."),

        H("Cone-beam CT and setup correction"),
        P(f"Kilovoltage cone-beam CT (CBCT) rotates the same tube and panel with the gantry and reconstructs by filtered back-projection adapted to the cone (the Feldkamp algorithm). [[1|A centered panel (full fan) gives a field of view about {FOV_FULL} cm across, for the head; an offset panel (half-fan), about {FOV_HALF} cm for the pelvis and chest, with a 360° rotation.]] Its HU are less reliable than the planning CT's, so dose calculation on a CBCT needs its own calibration or the planning CT deformed onto it."),
        P("The CBCT is registered to the planning CT within a region of interest, on bone or on soft tissue, and that choice decides the shift: three translations, plus three rotations (pitch, roll, and yaw) of up to a few degrees on a six-degree-of-freedom couch. The shift is applied when its length exceeds an action level set for the site."),
        EQ("|d| = [[2|√(Δx² + Δy² + Δz²)]]", "[[2|δ ≈ r sin θ]]   (a point at distance r from the axis of a rotation θ; the exact chord is 2r sin(θ/2))"),
        EX("Length of a shift", STEM("A CBCT match before a fraction.", [f"lateral = {sgn(ex_d[0])} mm", f"longitudinal = {sgn(ex_d[1])} mm", f"vertical = {sgn(ex_d[2])} mm", f"action level on the length = {ex_al:.1f} mm"], "Find the [[length of the shift]] and whether it is applied."),
           [f"|d| = √({ex_d[0]:.1f}² + {abs(ex_d[1]):.1f}² + {ex_d[2]:.1f}²) = √{sum(x * x for x in ex_d):.2f}", f"Compare with {ex_al:.1f} mm"],
           f"{ex_len:.1f} mm, so the shift is applied, although every component is below {ex_al:.1f} mm."),
        EX("Rotation left uncorrected", STEM("A CBCT shows a yaw that a couch correcting translations only cannot remove.", [f"yaw = {ex_th:.1f}°", f"distance of the superior edge of the target from the isocenter = {ex_r / 10:.1f} cm"], "Find the [[displacement of the edge]]."),
           [f"δ ≈ r sin θ = {ex_r:.0f} mm × sin {ex_th:.1f}°", f"= {ex_r:.0f} × {math.sin(math.radians(ex_th)):.5f}"],
           f"{ex_rot:.1f} mm, while the isocenter itself does not move."),
        P("[[3|Online correction before every fraction removes each day's error, systematic and random, at the cost of daily imaging dose.]] [[3|An offline protocol moves the setup by the mean shift of the first few fractions: the daily random error remains, and since the mean carries the average of n random errors, a systematic error with a standard deviation of about σ/√n is left.]] [[3|Neither corrects motion during the fraction or a change in the target's shape.]]"),
        EX("Offline correction", STEM("An offline protocol for one patient, with no time trend.", [f"vertical shifts on fractions 1, 2, and 3 = {sgn(ex_sh[0])}, {sgn(ex_sh[1])}, {sgn(ex_sh[2])} mm", f"random error σ = {ex_sig:.1f} mm"], "Find the [[correction]] applied from fraction 4 and the [[standard deviation of the systematic error]] left after it."),
           [f"Mean = ({ex_sh[0]:.1f} + {ex_sh[1]:.1f} + {ex_sh[2]:.1f}) / 3 = {ex_mean:.1f} mm", f"Systematic error left = σ/√n = {ex_sig:.1f} / √3"],
           f"The setup is moved by {sgn(ex_mean)} mm, and a systematic error with a standard deviation of {ex_res:.1f} mm remains."),

        H("Surface, ultrasound, and electromagnetic guidance"),
        P("Surface-guided radiotherapy (SGRT) projects light onto the patient and reconstructs the skin from ceiling-mounted cameras, [[1|with no ionizing dose]], and gives its offset from a reference surface. [[1|It serves for setup, for monitoring during the beam, for breath-hold in left-breast treatment]], and for frameless SRS in an open-face mask. [[1|It sees only the skin, so a target that moves relative to it, such as a lung tumour, is not tracked.]]"),
        PHOTO("igrt-sgrt-bore-cameras"),
        P("[[2|Transabdominal ultrasound shows the prostate, bladder, and rectum with no dose, but depends on the operator, and probe pressure can displace the prostate.]] Electromagnetic transponders, usually three implanted in the prostate, are [[2|located continuously by an array over the patient]], and the beam is held when the target moves. [[2|They are invasive]], lose accuracy far from the array, and cause artifacts on MR. Gold markers serve the same purpose with kV imaging, and a robotic linac can follow them. [[2|Transponders add no ionizing dose.]]"),

        H("MR-guided treatment"),
        P("[[1|Two commercial systems combine a treatment unit with an MR scanner: a 7 MV linac with a 1.5 T magnet, and a 0.35 T magnet with three cobalt-60 sources, later a 6 MV linac. In both the field is perpendicular to the beam.]] Cine MR of a plane through the target, several images a second, allows gating on the target itself with no ionizing dose."),
        P(f"[[2|In the magnetic field, an electron leaving tissue for air turns back and deposits its energy near the surface it left, raising the dose at the exit skin and around air in the lungs and bowel: the electron return effect.]] The field also skews the penumbra and shortens the build-up, so [[2|the dose calculation includes the field]], usually by Monte Carlo. The radius of the path goes as 1/B: {r1_15:.1f} mm at 1.5 T and {r1_035:.1f} mm at 0.35 T for a 1 MeV electron moving across the field."),
        P("MR carries no electron density, so the daily dose uses the planning CT deformed onto the MR or densities assigned to the contours. [[3|In online adaptive treatment the patient stays on the couch while the target and organs are recontoured and the plan is reoptimized, checked by an independent calculation, and delivered, often in 45 minutes or more.]] Phantoms check the MR distortion and its isocenter against the radiation isocenter."),

        H("Imaging dose and QA"),
        P(f"Imaging adds dose outside the plan, and [[1|at kilovoltage energy the photoelectric effect gives bone two to four times the dose to soft tissue]]. [[2|TG-180 recommends including the imaging dose in the plan when it exceeds {TG180_PCT}% of the therapeutic target dose.]] A shorter scan, a lower mAs, less frequent imaging, or a non-ionizing method lowers it."),
        TABLE(["Method", "What it locates", "Ionizing dose per session"], DOSE),
        P("The dose of a CBCT protocol is measured at the center and the periphery of a cylindrical phantom and weighted as for the weighted CTDI of CT."),
        EQ("D<sub>w</sub> = ⅓ D<sub>center</sub> + ⅔ D<sub>periphery</sub>"),
        EX("Imaging dose of a course", STEM("A kV CBCT before each fraction of a prostate course (illustrative values).", [f"dose at the center of the phantom = {ex_dc:.1f} cGy", f"mean dose at the periphery = {ex_dp:.1f} cGy", f"fractions = {ex_n}", f"prescription = {ex_rx:.0f} Gy"], "Find the [[weighted dose]] of a scan and the [[imaging dose of the course]] as a percentage of the prescription."),
           [f"D<sub>w</sub> = {ex_dc:.1f} / 3 + 2 × {ex_dp:.1f} / 3 = {ex_dw:.1f} cGy", f"Course = {ex_n} × {ex_dw:.1f} = {ex_tot:.1f} cGy", f"{ex_tot:.1f} cGy / {100 * ex_rx:,.0f} cGy"],
           f"{ex_dw:.1f} cGy per scan and {ex_pct:.2f}% of the prescription, well below the TG-180 threshold of {TG180_PCT}%."),
        P(f"[[3|TG-142 checks daily that a phantom aligned to the treatment isocenter appears at the imaging isocenter within {TG142_ISO:g} mm, or {TG142_SRS:g} mm for SRS and SBRT]], and that the calculated couch shift returns a phantom set up off center. [[3|Monthly, the CBCT geometric distortion is held to the same limits, and resolution, contrast, uniformity, noise, and HU constancy are compared with the baseline]]; the imaging dose is measured yearly."),
    ],
    cards=[
        F("Portal image", "A megavoltage image made with the treatment beam on the EPID. Low contrast: the field edges, air, and bone show, with little soft tissue."),
        F("Kilovoltage planar imaging", "Two radiographs at different angles, from gantry-mounted or room-mounted tubes, matched to DRRs computed from the planning CT. Better bone contrast than MV, at well under 1 cGy per pair."),
        F("Limit of a bony match", "It places the skeleton, not the target. The prostate moves relative to the pelvic bones as the rectum and bladder fill."),
        F("CBCT field of view", f"Full fan, panel centered: about {FOV_FULL} cm across, for the head. Half-fan, panel offset: about {FOV_HALF} cm, for the pelvis and chest, with a 360° rotation."),
        F("Displacement from a rotation", f"About r sin θ for a point at distance r from the axis: {card_rot:.1f} mm at 10 cm for 1°.", w=[f"δ = 100 mm × sin 1° = {card_rot:.2f} mm"]),
        F("Offline correction", "The setup is moved by the mean shift of the first n imaged fractions. The systematic error left has a standard deviation of about σ/√n, and the daily random error remains."),
        F("Limits of a pre-treatment correction", "It removes the setup error at the time of imaging, not motion during the fraction or a change in the shape of the target and organs."),
        F("Surface guidance", "Projected light and ceiling cameras track the skin with no ionizing dose, for setup, monitoring, breath-hold, and frameless SRS. It does not see the internal target."),
        F("Ultrasound guidance", "Soft-tissue images of the prostate with no dose. The image depends on the operator, and probe pressure can displace the prostate."),
        F("Electromagnetic transponders", "Usually three implanted in the prostate, located continuously by an array over the patient with no ionizing dose. Invasive, and they cause artifacts on MR."),
        F("Commercial MR-linacs", "1.5 T with a 7 MV linac; 0.35 T with three cobalt-60 sources, later a 6 MV linac. The field is perpendicular to the beam."),
        F("Electron return effect", "Electrons leaving tissue for air curve back in the magnetic field and raise the dose in the tissue at the interface. The dose calculation includes the field."),
        F("Online adaptive treatment", "Recontouring, reoptimizing, and an independent dose check with the patient on the couch. A fraction often takes 45 minutes or more."),
        F("TG-142 imaging tests", f"Daily: imaging and treatment isocenters within {TG142_ISO:g} mm ({TG142_SRS:g} mm for SRS/SBRT). Monthly: CBCT distortion within {TG142_ISO:g} mm ({TG142_SRS:g} mm), and image quality and HU constancy against baseline."),
    ],
)

PROBLEMS = [
    # ---- 1-3: planar imaging
    PR(STEM("A megavoltage portal image of a pelvic field is acquired on the EPID before treatment.", ask="Which features does the image show best?"),
       "The field edges and the pelvic bones", ["The prostate and the rectal wall", "The bladder and the seminal vesicles", "The skin surface and its contour"],
       "The megavoltage image has low contrast, so the aperture of the field and the bones show and the soft-tissue organs do not; the prostate needs implanted markers, CBCT, ultrasound, or MR. The skin contour is what a surface-imaging system measures.", lvl="Easy"),
    PR(STEM("A prostate patient is set up each day by matching orthogonal kV radiographs to DRRs on the pelvic bones. On day 10 a CBCT shows the bones aligned and the prostate 6 mm anterior to its planned position.", ask="What is the most likely cause?"),
       "The prostate moved relative to the bones as the rectum filled", ["The kV imaging isocenter is offset from the treatment isocenter", "The DRRs were computed from another patient's planning CT", "The couch sagged under the weight of the patient"],
       "A bony match aligns the skeleton, and the prostate moves relative to the pelvic bones as the rectum and bladder fill. An isocenter offset, a wrong CT, or couch sag would misplace the bones as well, and the CBCT shows them aligned.", lvl="Moderate"),
    SORT("Rank these images from the least to the most soft-tissue contrast.", ["1st (least)", "2nd", "3rd", "4th (most)"],
         [("MV portal image", 0), ("kV radiograph", 1), ("kV CBCT", 2), ("MR image", 3)],
         "A portal image shows little but bone and air. A kV radiograph has more contrast but superimposes every organ along each ray. A kV CBCT separates the organs in three dimensions, with contrast limited by scatter, and MR gives the most soft-tissue contrast.", lvl="Easy", mode="rank", cap=1),
    # ---- 4-10: cone-beam CT and setup correction
    PRN(STEM("A CBCT match gives the couch shifts below.", [f"lateral = {sgn(q_d[0])} mm", f"longitudinal = {sgn(q_d[1])} mm", f"vertical = {sgn(q_d[2])} mm"], "What is the [[length of the shift vector]]?"), q_len, [q_abs, q_sum, q_max], "{:.1f} mm",
        f"|d| = √({q_d[0]:.1f}² + {abs(q_d[1]):.1f}² + {q_d[2]:.1f}²) = √{sum(x * x for x in q_d):.2f} = {q_len:.1f} mm. Adding the magnitudes gives {q_abs:.1f} mm, adding the signed values {q_sum:.1f} mm, and the largest component alone {q_max:.1f} mm.", lvl="Moderate"),
    TYPED(STEM("A CBCT shows a roll of the patient, and the couch corrects translations only.", [f"roll = {t_th:.1f}°", f"distance of a point from the axis of the roll = {t_r / 10:.0f} cm"], "How far is the [[point displaced]] by the uncorrected roll?"), t_rot, 0.02, "mm",
          f"δ ≈ r sin θ = {t_r:.0f} mm × sin {t_th:.1f}° = {t_r:.0f} × {math.sin(math.radians(t_th)):.4f} = {t_rot:.2f} mm. The exact chord, 2r sin(θ/2), differs by less than 0.01 mm, and a point on the axis does not move.", lvl="Moderate"),
    PRN(STEM("An offline protocol corrects each patient's setup by the mean shift of the first imaged fractions. There is no time trend.", [f"random setup error σ = {s_sig:.1f} mm", f"imaged fractions n = {s_n}"], "What is the [[standard deviation of the systematic error]] left after the correction?"), s_res, [s_sig / s_n, s_sig, s_sig * math.sqrt(s_n)], "{:.1f} mm",
        f"The mean of {s_n} fractions includes the average of {s_n} random errors, whose standard deviation is σ/√n = {s_sig:.1f} / √{s_n} = {s_res:.1f} mm, and that average stays in the setup as a systematic error. Dividing by n in place of √n gives {s_sig / s_n:.1f} mm, and multiplying by √n gives {s_sig * math.sqrt(s_n):.1f} mm.", lvl="Challenging"),
    PR(STEM("A pelvic CBCT is acquired with the panel centered (full fan).", ["width of the patient = 40 cm"], "What is the main problem with the image?"),
       "The sides of the pelvis are truncated outside the field of view", ["The scan exceeds the TG-180 imaging dose threshold", "The rotation is too short to reconstruct the center", "The kV beam cannot pass through 40 cm of tissue"],
       f"Full fan reconstructs a field of view about {FOV_FULL} cm across, so a 40 cm pelvis is cut off at the sides, which adds artifacts and loses the skin contour. Offsetting the panel (half-fan) widens the field of view to about {FOV_HALF} cm with a 360° rotation. A single scan is far below {TG180_PCT}% of the target dose.", lvl="Moderate"),
    PR(STEM("A head-and-neck patient has lost weight during treatment, and the dose is to be recalculated on the day's CBCT.", ask="What does an accurate calculation on the CBCT require?"),
       "Its own density calibration, or the planning CT deformed onto it", ["The planning CT's density table, applied unchanged to the CBCT", "A finer dose grid, to average out the noise of the CBCT", "A repeat CBCT with a longer scan and more projections"],
       "Scatter, truncation, and the cone geometry make CBCT numbers differ from those of the planning CT and change with the size of the patient, so the planning CT's table assigns wrong densities. A calibration made for the CBCT, or the planning CT deformed to the day's anatomy, supplies the densities; a finer grid or a longer scan does not correct them.", lvl="Challenging"),
    PRM(STEM("A prostate is matched on soft tissue in a CBCT, and the shift is applied with a six-degree-of-freedom couch. The beam then runs for 10 minutes.", ask="Which of these errors remain after the correction?"),
        ["Drift of the prostate as the rectum fills during the beam", "Deformation of the prostate and seminal vesicles since planning"],
        ["Rotation of the prostate by 2° at the time of the CBCT", "Random part of that day's setup error"],
        "The shift removes the error present when the image was taken, translation and rotation, systematic and random alike. Motion after the image, such as drift as the rectum fills, and changes of shape, which no rigid shift corrects, remain.", lvl="Moderate"),
    PR(STEM("A group of patients is treated in 30 fractions, with the setup errors below.", ["systematic error Σ = 3 mm", "random error σ = 3 mm"], "Which strategy reduces both components?"),
       "Online CBCT and correction before every fraction", ["Offline correction by the mean of the first three fractions", "Weekly kV images with a 5 mm action level", "A larger PTV margin with no daily imaging"],
       f"Daily online correction measures and removes the error of each fraction, systematic and random. The offline mean removes most of the systematic error, leaving about σ/√3 = {o_sig:.1f} mm, but none of the random error. Weekly images with a large action level miss most errors, and a larger margin covers the errors without reducing them.", lvl="Challenging"),
    # ---- 11-14: surface, ultrasound, and electromagnetic guidance
    PR(STEM("A lung SBRT patient is set up with surface guidance. The chest surface matches the reference within 1 mm, but a CBCT shows the spine aligned and the tumour 7 mm superior to its planned position.", ask="What best explains the difference?"),
       "The tumour moved relative to the chest surface", ["The surface system is miscalibrated by 7 mm", "The couch moved 7 mm after the surface match", "The CBCT reconstruction displaces the tumour superiorly"],
       "Surface imaging measures the skin, which the cameras see, and a lung tumour can shift relative to the chest wall from day to day, so a surface match does not place it. A miscalibration or a couch movement would also misplace the spine, which the CBCT shows aligned.", lvl="Moderate"),
    PR(STEM("A left-breast patient is treated in deep-inspiration breath-hold.", ask="Which system monitors the position of the chest during the beam without adding dose?"),
       "Surface imaging with ceiling-mounted cameras", ["A kV CBCT acquired before each beam", "Continuous kV fluoroscopy of the chest", "Orthogonal kV radiographs before each beam"],
       "Surface imaging tracks the chest continuously with light and holds the beam when the chest leaves its window. Fluoroscopy adds dose, and a CBCT or a pair of radiographs before each beam adds dose and shows nothing during the beam.", lvl="Easy"),
    PRM(STEM(ask="Which of these guidance methods add no ionizing radiation dose?"),
        ["Surface imaging", "Transabdominal ultrasound", "Electromagnetic transponder tracking"],
        ["Kilovoltage CBCT", "Megavoltage portal imaging", "Stereoscopic kV imaging of implanted markers"],
        "Surface imaging uses visible light, ultrasound uses sound, and the transponders respond to an alternating electromagnetic field, so none adds ionizing dose. Every x-ray method does, from well under 1 cGy for a kV pair to several cGy for an MV pair.", lvl="Easy"),
    # ---- 15-18: MR-guided treatment
    PR(STEM(ask="What field strengths do the two commercial MR-linac designs use?"), "1.5 T and 0.35 T", ["3.0 T and 1.5 T", "7.0 T and 3.0 T", "0.5 T and 0.1 T"],
       "One design pairs a 7 MV linac with a 1.5 T magnet; the other uses 0.35 T, first with three cobalt-60 sources and later with a 6 MV linac. 3.0 T and 7.0 T magnets serve diagnostic and research MR.", lvl="Easy"),
    PR(STEM("A beam on a 1.5 T MR-linac exits the patient through the skin into air.", ask="Where does the magnetic field raise the dose most?"),
       "In the tissue at the exit surface", ["In the air beyond the exit surface", "In the build-up region at the entrance", "Evenly throughout the target"],
       "Electrons that leave the tissue are turned back by the field and deposit their energy in the tissue they left, the electron return effect. Air absorbs almost nothing, and the entrance build-up changes less.", lvl="Moderate"),
    PR(STEM("In an online adaptive fraction on an MR-linac, the plan is reoptimized on the day's anatomy while the patient lies on the couch.", ask="How is the new plan checked before delivery?"),
       "By an independent calculation of its dose", ["By a measurement of the new plan in a phantom", "By the QA of the original plan, which covers it", "By the morning output check of the linac"],
       "A phantom measurement is not possible with the patient on the couch, so the dose of the new plan is checked by an independent calculation before the beam. The QA of the original plan does not cover the new fluences, and the output check tests the machine, not the plan.", lvl="Challenging"),
    # ---- 19-21: imaging dose and QA
    PRN(STEM("A linac is used for SRS and SBRT.", ask="What is the TG-142 [[tolerance]] for the daily coincidence of the imaging and treatment isocenters?"), TG142_SRS, [0.5, TG142_ISO, 3.0, 5.0], "{:.1f} mm",
        f"TG-142 sets {TG142_SRS:g} mm for SRS and SBRT and {TG142_ISO:g} mm for a conventional machine. A machine is held to the tolerance of its most demanding use.", lvl="Easy"),
    PRN(STEM("A kV CBCT protocol is measured in a cylindrical body phantom.", [f"dose at the center = {w_dc:.1f} cGy", f"mean dose at the periphery = {w_dp:.1f} cGy"], "What is the [[weighted dose]] of the scan?"), w_dw, [w_avg, w_swap, w_dp], "{:.2f} cGy",
        f"D<sub>w</sub> = ⅓ × {w_dc:.1f} + ⅔ × {w_dp:.1f} = {w_dw:.2f} cGy. The periphery carries two-thirds of the weight because it stands for the larger part of the cross-section. The plain mean gives {w_avg:.2f} cGy, and swapping the weights gives {w_swap:.2f} cGy.", lvl="Moderate"),
]

INLINE = {0: [1, 2], 1: [4, 5, 7, 9], 2: [11, 12], 3: [14, 15]}

TERMS = ["electronic portal imaging device", "digitally reconstructed radiograph", "half-fan", "action level", "offline protocol", "surface-guided radiotherapy", "electron return effect", "online adaptive treatment"]

TAKE = [
    ["Portal images show the field edges and bone at low contrast; kV radiographs show bone better, at well under 1 cGy per pair.",
     "A DRR match places the skeleton or implanted markers, not soft tissue: the prostate moves relative to the pelvic bones."],
    [f"Full fan: about {FOV_FULL} cm field of view. Half-fan, panel offset: about {FOV_HALF} cm, with a 360° rotation.",
     "Shift length √(Δx² + Δy² + Δz²); a rotation θ moves a point at distance r by about r sin θ.",
     "Online correction removes the day's setup error; correcting by the mean of n fractions leaves σ/√n. Neither removes motion during the fraction or deformation."],
    ["Surface imaging: no dose; setup, monitoring, and breath-hold. It sees the skin, not the target.",
     "Ultrasound depends on the operator and the probe pressure. Transponders are tracked continuously with no dose but must be implanted."],
    ["MR-linacs: 1.5 T with 7 MV; 0.35 T with cobalt-60 or 6 MV. The field is perpendicular to the beam.",
     "The electron return effect raises the dose in tissue at tissue–air interfaces; the dose calculation includes the field.",
     "Online adaptation recontours, reoptimizes, and checks the plan with the patient on the couch, often in 45 minutes or more."],
    ["Per session: MV portal pair 1–5 cGy, kV CBCT 0.2–2 cGy, MV CBCT 3–10 cGy; at kV energy bone gets two to four times the soft-tissue dose.",
     f"TG-180: include imaging dose in the plan above {TG180_PCT}% of the target dose.",
     f"TG-142: imaging and treatment isocenters within {TG142_ISO:g} mm daily ({TG142_SRS:g} mm for SRS/SBRT); image quality and HU constancy monthly against baseline."],
]
