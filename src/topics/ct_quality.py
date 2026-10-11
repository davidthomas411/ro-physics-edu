from blocks import *
import math, calc, gal, real
GS = gal.ST
RC = real.STATS["ct"]; RN, RK, RB = RC["noise"], RC["kernel"], RC["cbct"]                    # measured on real scans: tools/make_real_ct.py

pitch = lambda d, s: d / s
scan_t = lambda length, d, rot: length / d * rot                          # seconds to cover a length (mm) with table travel d (mm) per rotation of time rot (s)
noise = lambda mas, s: math.sqrt(1000 / (mas * s))                         # noise relative to 200 mAs and 5 mm, which is taken as 1: noise goes as 1/sqrt(mAs x slice thickness)
t_p1, t_p15 = scan_t(200, 1.0 * 5, 0.5), scan_t(200, 1.5 * 5, 0.5)

TOPIC = dict(
    id="ct-quality", domain=4, sub="IV.A", title="CT acquisition, image quality, and artifacts",
    ref=dict(aapm="TG-66, TG-179", khan="", ford="19, 21"),
    guide=[
        H("Fan-beam and helical acquisition"),
        P("A diagnostic scanner uses a fan beam, collimated in the superior–inferior direction to a narrow extent, typically 1 to 5 mm. The detector can be a multislice detector with many rows, for example 4, 8, 16, or up to 128, and a slice is reconstructed with some thickness S. The scan can be acquired in serial mode, one slice at a time, but more often it is acquired in helical mode. The patient slides through the bore while the tube and the detectors rotate around the patient, and the pitch sets how tight the spiral is."),
        EQ("p = d / S", "d = distance the table travels in one tube rotation,   S = slice thickness"),
        P("A larger pitch gives a faster acquisition but a degraded slice sensitivity profile. After a helical scan the slices are reconstructed in straight axial planes, perpendicular to the table motion."),
        EX("Pitch and scan time", STEM("A helical scan covers 200 mm. The slice thickness is 5 mm and the rotation time is 0.5 s.", ["pitch 1.0", "pitch 1.5"], "Find the [[table travel per rotation]] and the [[scan time]] for each."), ["d = p × S", "Time = (length / d) × rotation time"], f"Pitch 1.0: d = 5.0 mm and the time is 200 / 5.0 × 0.5 = {t_p1:.1f} s. Pitch 1.5: d = 7.5 mm and the time is 200 / 7.5 × 0.5 = {t_p15:.1f} s. The larger pitch is {t_p1 / t_p15:.1f} times faster."),

        H("Noise and resolution in CT"),
        P("The image-quality parameters of Section 19.1 apply to CT: contrast, noise, and spatial resolution. The noise depends on the collimation or slice thickness, the reconstruction algorithm, the pitch, the kVp, the time, and the mA. CT reconstructions are limited by photon-counting noise, so the SNR is proportional to the square root of mA·s. Thicker slices have a higher SNR, because more photons are collected."),
        P("The spatial resolution depends on the focal spot size, the detector resolution, the pixel size, the reconstruction filter, and the slice thickness. A bone filter in the backprojection distinguishes smaller features, at the cost of a noisier image. Changing the mA affects the noise but not the spatial resolution."),
        EX("Noise and the exposure", STEM("A CT scan uses 100 mAs. The scan is repeated with 400 mAs.", [], "By what factor does the [[SNR]] change?"), ["SNR ∝ √(mA·s)", "√(400 / 100) = √4"], "The SNR doubles. Four times the exposure doubles the SNR and halves the relative noise."),

        P(f"The images below show these effects on a real CT slice. The slice comes from a head-and-neck patient of the open OpenKBP dataset, and the effects are simulated from the physics, so each image can be compared with a clean reference of the same anatomy. When the exposure falls by a factor of 16 the noise rises {GS['noise_low'] / GS['noise_high']:.1f} times, close to the factor of 4 that 1/√exposure predicts. A smooth reconstruction filter gives {GS['sd_smooth'] / GS['sd_sharp']:.2f} of the noise of the sharp filter, and the fine detail is softer."),
        AVF("ct-gallery-noise"),
        P(f"Real scans show the same dependence on the exposure. A uniform plastic block in a test phantom was scanned on one scanner at {RN['mA'][0]}, {RN['mA'][1]}, {RN['mA'][2]}, and {RN['mA'][3]} mA, with every other setting fixed. The noise, the standard deviation of the HU in the block, was {RN['sd'][0]:.1f}, {RN['sd'][1]:.1f}, {RN['sd'][2]:.1f}, and {RN['sd'][3]:.1f} HU. A factor of {RN['mA'][3] // RN['mA'][0]} in the tube current lowered the noise by a factor of {RN['sd'][0] / RN['sd'][3]:.2f}, close to √{RN['mA'][3] // RN['mA'][0]} = {math.sqrt(RN['mA'][3] / RN['mA'][0]):.2f}."),
        AVF("real-ct-noise"),
        P(f"The reconstruction kernel changes the noise at a fixed exposure. One scan of a phantom, reconstructed with four kernels, gave a noise of {RK['sd'][0]:.0f}, {RK['sd'][1]:.0f}, {RK['sd'][2]:.0f}, and {RK['sd'][3]:.0f} HU in a uniform block with the soft, standard, lung, and edge kernels. In the textured block the soft kernel smooths the fine structure, and the sharper kernels keep it, at the cost of noise. A soft kernel suits soft tissue, where noise limits the visibility of low contrast. A sharp kernel suits lung and bone, where detail matters more."),
        AVF("real-ct-kernel"),
        H("Cone-beam CT"),
        P("In cone-beam CT (CBCT) the thin-slice acquisition is replaced with a large detector that irradiates a cone through the patient. The whole volume can be acquired in a single revolution. That is an advantage on a C-arm linac, which cannot rotate as fast as a diagnostic scanner, whose rotation period is 1 s or even 0.5 s. A CBCT acquires roughly 700 images in a rotation while the patient stays in one position, so the patient can be imaged in the treatment position immediately before treatment, which makes image-guided radiation therapy possible."),
        P("The cone geometry has disadvantages. The acquisition is long, about 1 minute on a C-arm linac against under 1 second in diagnostic CT, so motion of the patient or of the anatomy degrades the image. The scatter is larger, which lowers the image quality as described in Section 19.1.5. Because of the larger scatter the HU are often not accurate representations of the linear attenuation coefficient, which is a challenge when CBCT is used for dose calculation."),

        P(f"The images below show one patient at the same level with a planning CT and with the CBCT acquired at treatment. In the liver the noise is {RB['sd_cbct']:.0f} HU on the CBCT against {RB['sd_ct']:.0f} HU on the planning CT, the contrast between organs is much lower, and the vessels that are bright on the planning CT are not enhanced. The field of view is also limited: at the level of the chest the right side of the patient lies outside the reconstructed region."),
        AVF("real-ct-cbct"),

        H("CT artifacts"),
        P("Artifacts are features of the image that do not come from the patient. Several come from beam hardening, in which the lower-energy photons are removed and the mean energy of the beam rises as it passes through the patient. Four are common."),
        UL("<b>Cupping.</b> The density appears lower in the center than at the periphery. The scatter contribution is larger in the center, especially in CBCT, and beam hardening also plays a part, because rays through the center are attenuated more and give a harder spectrum.",
           "<b>Streaking.</b> Beam hardening at the projection angles that pass laterally through two dense objects gives a harder spectrum. The detector registers fewer photons, and a low-density streak appears between the objects.",
           "<b>Motion.</b> Movement during the scan, for example of a gas bubble, blurs or distorts the structure.",
           "<b>Ring.</b> A faulty or miscalibrated detector pixel reconstructs as a ring."),
        P(f"Each artifact below was simulated on the same slice. Compare the image on the right with the reference on the left. Beam hardening and scatter both give cupping: the soft tissue in the centre reads {GS['bh_rim'] - GS['bh_core']:.0f} HU and {GS['sc_rim'] - GS['sc_core']:.0f} HU lower than the soft tissue at the periphery. The metal object raises the spread of the soft-tissue values away from it from {GS['metal_ref_sd']:.0f} HU to {GS['metal_sd']:.0f} HU, and the motion raises it to {GS['motion_sd']:.0f} HU. The faulty detector channel gives a ring of {abs(GS['ring_peak']):.0f} HU at {GS['ring_r'] * 0.977:.0f} mm from the centre of rotation."),
        AVF("ct-gallery-artifacts"),
        P("Metal implants are a common source of severe artifacts in radiotherapy planning. The images below are one real chest CT that was reconstructed twice from the same raw data, without and with an iterative metal artifact reduction (iMAR). Metal in the spine and the shoulder gives dark and bright streaks across the soft tissue in the standard reconstruction. The reduction removes most of them, and the vertebra and the soft tissue are easier to see. Near an implant the HU are still unreliable for dose calculation, so planning systems let the user contour the implant and assign it a density."),
        AVF("real-ct-metal"),
    ],
    cards=[
        F("Fan-beam CT", "The beam is collimated in the superior–inferior direction to 1–5 mm. A multislice detector may have 4, 8, 16, or up to 128 rows."),
        F("Helical CT", "The patient slides through the bore while the tube and detectors rotate. The slices are reconstructed in axial planes."),
        F("Pitch", "p = d / S: the table travel per tube rotation divided by the slice thickness."),
        F("Effect of a larger pitch", "A faster acquisition, but a degraded slice sensitivity profile."),
        F("Noise in CT", "Limited by photon counting: the SNR is proportional to the square root of mA·s, and thicker slices have a higher SNR."),
        F("Resolution in CT", "Depends on the focal spot, the detector, the pixel size, the reconstruction filter, and the slice thickness. Not on the mA."),
        F("Bone filter", "Resolves smaller features, at the cost of a noisier image."),
        F("Cone-beam CT", "A large detector irradiates a cone, so the whole volume is acquired in one revolution. About 700 images are acquired in a rotation."),
        F("CBCT rotation time", "About 1 minute on a C-arm linac, against under 1 second in diagnostic CT, so motion degrades the image."),
        F("CBCT scatter and HU", "Larger scatter lowers the image quality, and the HU are often not accurate, which makes dose calculation on CBCT difficult."),
        F("Cupping artifact", "The center looks less dense than the periphery, from the larger scatter and beam hardening in the center."),
        F("Streaking artifact", "A low-density streak between two dense objects, from beam hardening at the angles that pass through both."),
        F("Ring artifact", "A faulty or miscalibrated detector pixel reconstructs as a ring."),
    ],
)

PROBLEMS = [
    PR("In helical CT the pitch is defined as:", "the table travel per tube rotation divided by the slice thickness", ["the slice thickness divided by the table travel", "the number of detector rows", "the rotation time divided by the slice thickness"],
       "p = d / S. A larger pitch means that the table moves farther in each rotation.", lvl="Easy"),
    PR("Compared with a smaller pitch, a larger pitch gives:", "a faster acquisition and a degraded slice sensitivity profile", ["a slower acquisition and a better slice profile", "a higher mA", "a smaller pixel size"],
       "The table moves farther per rotation, so the volume is covered faster, with some loss of resolution along the table axis.", lvl="Easy"),
    PR("Changing the mA of a CT scan affects:", "the noise, but not the spatial resolution", ["the spatial resolution, but not the noise", "both the noise and the spatial resolution", "neither"],
       "The mA sets the number of photons, and so the noise. The resolution depends on the focal spot, the detector, the pixel size, the filter, and the slice thickness.", lvl="Easy"),
    PRN(STEM("The table travels 15 mm in each tube rotation. The slice thickness is 10 mm.", [], "What is the [[pitch]]?"), pitch(15, 10), [10 / 15, 150.0, 15 * 10 / 10], "{:.1f}",
        f"p = d / S = 15 / 10 = {pitch(15, 10):.1f}. Inverting the ratio gives {10 / 15:.2f}.", lvl="Moderate"),
    PRN(STEM("A helical scan covers 200 mm. The slice thickness is 5 mm, the pitch is 1.5, and the rotation time is 0.5 s.", [], "What is the [[scan time]]?"), t_p15, [t_p1, 200 / 1.5 * 0.5, 200 / 7.5], "{:.1f} s",
        f"The table travel is d = 1.5 × 5 = 7.5 mm per rotation. The scan needs 200 / 7.5 = 26.7 rotations, which take 26.7 × 0.5 = {t_p15:.1f} s.", lvl="Moderate"),
    PRN(STEM("A CT scan is repeated with four times the mAs, with everything else unchanged.", [], "By what factor does the [[SNR]] change?"), 2.0, [4.0, 0.5, 16.0], "{:.0f}",
        "The SNR is proportional to √(mA·s), and √4 = 2.", lvl="Moderate"),
    PR("Thicker CT slices have a higher SNR because:", "more photons are collected for each voxel", ["the pixel size is smaller", "the filter is sharper", "the focal spot is smaller"],
       "Photon-counting noise falls as the number of photons rises, and a thicker slice collects more of them.", lvl="Moderate"),
    PR("A bone filter used in reconstruction gives:", "a better resolution of small features, at the cost of a noisier image", ["a lower noise, at the cost of the resolution", "a change of the HU of water", "a faster acquisition"],
       "The filter controls the balance between resolution and noise in filtered backprojection.", lvl="Moderate"),
    PR("Why is a CBCT scan on a C-arm linac more affected by motion than a diagnostic CT scan?", "The acquisition takes about 1 minute, against under 1 second", ["The detector is smaller", "The mA is lower", "The slice thickness is larger"],
       "The linac gantry rotates slowly, so patient and organ motion during the scan degrades the image.", lvl="Moderate"),
    PR("Contrast and HU accuracy are worse in CBCT than in diagnostic CT mainly because of:", "the larger scatter in the cone-beam geometry", ["the higher energy of the beam", "the smaller number of images", "the thicker slices"],
       "The measured signal includes scattered photons, which are not related to the attenuation along the ray.", lvl="Challenging"),
    PR("The cupping artifact appears as:", "an apparent lower density in the center of the image than at the periphery", ["a bright ring around the center", "a dark streak between two dense objects", "a blur of the whole image"],
       "Scatter is larger in the center, and rays through the center are hardened more.", lvl="Challenging"),
    PR("A ring artifact in a CT image is caused by:", "a faulty or miscalibrated detector pixel", ["motion of the patient", "beam hardening between two dense objects", "a high pitch"],
       "A pixel that reads wrongly at every angle reconstructs as a ring around the center of rotation.", lvl="Challenging"),
]

TERMS = ['pitch', 'cone-beam CT', 'cupping', 'beam hardening']

TAKE = [
    [('Pitch p = d / S. A larger pitch covers the volume faster, at the cost of a degraded slice sensitivity profile.', 'pitch-time')],
    [('CT noise follows photon counting: the SNR rises as √(mA·s) and with slice thickness. The mA does not change the resolution.', 'ct-noise')],
    [('CBCT acquires the whole volume in one rotation, with a long acquisition and more scatter, so motion degrades the image and the HU are less accurate.', 'cbct-compare')],
    [('Cupping, streaking, motion, and ring artifacts each have their own cause: scatter and beam hardening, beam hardening between dense objects, movement, and a faulty detector pixel.', 'ct-artifacts')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Match each artifact to its cause.", ["Cupping", "Streaking", "Motion", "Ring"],
         [("Larger scatter in the center, with beam hardening of the central rays", 0), ("Beam hardening at angles that pass through two dense objects", 1), ("Anatomy moves during the scan", 2), ("A faulty or miscalibrated detector pixel", 3)],
         "Cupping comes from scatter and beam hardening at the center. Streaking comes from beam hardening between two dense objects. Motion comes from movement during the scan, and a ring comes from a detector pixel that reads wrongly.", lvl="Moderate", mode="match", cap=1),
    TYPED(STEM("The table travels 12 mm in each rotation. The slice thickness is 8 mm.", [], "What is the [[pitch]]?"), pitch(12, 8), 0.01, "(ratio)",
          f"p = 12 / 8 = {pitch(12, 8):.1f}.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the time to scan 200 mm against the pitch, for a slice thickness of 5 mm and a rotation time of 0.5 s.", [], "Tap the [[pitch at which the scan takes 10 s]]."),
         FS(x=dict(min=0.75, max=2.5, ticks=[1, 1.5, 2, 2.5], label="Pitch"), y=dict(min=0, max=30, ticks=[0, 8, 16, 24], label="Scan time (s)"), series=[dict(pts=PTS(lambda p: 20 / p, 0.75, 2.5), color="plot-1")], xunit="", xdec=2, xname="Pitch", label="Scan time against pitch"),
         [(1.88, 2.12)], "Time = (200 / (p × 5)) × 0.5 = 20 / p. Setting it to 10 s gives p = 2.0. The level 10 s is not marked on the axis.", lvl="Challenging", note="about 2.0"),
]
INLINE = {0: [1, 2, 4, _n0 + 2], 1: [3, 6, 7, 8], 2: [9, 10], 3: [11, 12, _n0 + 1]}
