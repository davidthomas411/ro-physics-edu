from blocks import *
import math, calc, mrdata
MS = mrdata.MST

shift = lambda dB, G: dB / G * 1000                             # apparent shift in mm for a field error dB (mT) and a gradient G (mT/m)
s_a, s_b = shift(0.05, 10), shift(0.05, 5)
stretch = lambda true, frac: true * (1 + frac)                  # a gradient that is larger by frac than the system assumes places a point at x G / G0: the image is stretched
g_a = stretch(200, 0.05)
ppm = lambda dB_mT, B_T: dB_mT * 1e-3 / B_T * 1e6               # parts per million of the main field
p_a = ppm(0.01, 1.5)
dB_3 = 3 * 10 / 1000                                            # the field error (mT) that moves a pixel by 3 mm for G = 10 mT/m

TOPIC = dict(
    id="mri-artifacts", domain=4, sub="IV.A", title="MRI distortion and artifacts",
    ref=dict(aapm="TG-284", khan="", ford="20"),
    guide=[
        H("Distortion from field errors"),
        P("Distortion matters in radiation oncology because the positions of the target and the organs at risk taken from the image are used to place the beams. Distortion follows from how position is encoded. A frequency corresponds to a position in the patient, because the field varies along the gradient. If the frequency is fixed and the local magnetic field is changed instead, the signal comes from a different position. A change in the local magnetic field is equivalent to moving the pixel in space."),
        P("Ideally the B<sub>0</sub> field is uniform throughout the patient. In practice there are non-uniformities, for example where the field bows out at the edge of the bore opening, and they distort the image. A phantom made of a grid of regularly spaced plastic rods tests the distortion. In an image without distortion the lines are regular and straight, and with field inhomogeneities they are bent, most strongly near the edge."),
        EQ("apparent shift = ΔB / G", "ΔB = local field error,   G = gradient strength (field per unit length)"),
        EX("A pixel moved by a field error", STEM("A local field error of 0.05 mT. The gradient is 10 mT/m, or 5 mT/m in a second sequence.", [], "Find the [[shift]] of the pixel in each case."), ["Shift = ΔB / G = 0.05 mT / 10 mT/m", "Shift = 0.05 mT / 5 mT/m"], f"{s_a:.0f} mm for the stronger gradient and {s_b:.0f} mm for the weaker one. A weaker gradient makes the same field error move the pixel farther, so the geometric accuracy needs a field that is uniform to a few parts per million."),

        H("Other artifacts"),
        UL("<b>Magnetic susceptibility artifact.</b> A metallic object in or near the field distorts the local field, which gives an artifact in the image, most typically a signal void near the metal.",
           "<b>Gradient distortion.</b> The system converts each frequency to a position with the gradient it assumes. If the gradient is larger than the system assumes, the image is stretched in that dimension, and if it is smaller, the image is compressed.",
           "<b>Chemical shift artifact.</b> Fat protons precess about 3.5 ppm more slowly than water protons because of their chemical environment. The system converts frequency to position, so the fat signal is displaced from the water signal along the frequency-encoding direction."),
        EX("A gradient that is too strong", STEM("A gradient is 5% stronger than the system assumes.", ["a true length of 200 mm"], "Find the [[apparent length]]."), ["Apparent length = true length × 1.05"], f"{g_a:.1f} mm. The image is stretched, so the object looks longer."),
        P("The magnetic susceptibility artifact, the gradient distortion, and the chemical shift artifact differ in their causes. Geometric accuracy is checked with phantoms and corrected where possible. For treatment planning the distortion must be small compared with the margins that are used."),
        P(f"In a simulation on a real brain slice, with a 20 mm grid that plays the part of the distortion phantom, a field error that grows from zero at the centre to 0.06 mT at the edge, with a gradient of 10 mT/m, shifts the pixels sideways by up to {MS['dx_max']:.1f} mm, and the grid lines bend. A gradient 5% too strong stretches the brain from {MS['w_true']:.0f} mm to {MS['w_str']:.0f} mm across. A metal object of 10 mm leaves a signal void about {MS['sus_void_mm']:.0f} mm across, with bright pile-up where the pixels are squeezed together. The chemical shift artifact is not shown, because this brain image has no fat."),
        AVF("mr-gallery-artifacts"),
    ],
    cards=[
        F("Importance of MRI distortion in radiation oncology", "The positions of the target and the organs at risk taken from the MR image are used to place the beams, so a geometric error shifts the delivered dose."),
        F("Position and field", "A change in the local magnetic field is equivalent to moving the pixel in space, because position is encoded by frequency."),
        F("B<sub>0</sub> inhomogeneity", "Non-uniformity of the main field, for example where it bows out at the edge of the bore, distorts the image."),
        F("Distortion phantom", "A grid of regularly spaced plastic rods. Lines that should be straight and regular are bent where the field is not uniform."),
        F("Apparent shift", "ΔB / G: the local field error divided by the gradient strength."),
        F("Magnetic susceptibility artifact", "A metallic object distorts the local field and gives a signal void near the metal."),
        F("Gradient distortion", "If the gradient is larger than the system assumes, the image is stretched in that dimension. If it is smaller, the image is compressed."),
        F("Chemical shift artifact", "Fat protons precess about 3.5 ppm more slowly than water protons, so the fat signal is displaced from the water signal along the frequency-encoding direction."),
    ],
)

PROBLEMS = [
    PR("In MRI, a change in the local magnetic field is equivalent to:", "moving the pixel in space", ["a change in the TR", "a change of the T1 of the tissue", "a change of the flip angle"],
       "Position is encoded by the Larmor frequency, so an error in the local field shifts the apparent position.", lvl="Easy"),
    PR("A metallic object near the field produces:", "a signal void near the metal, from a distortion of the local field", ["a chemical shift between fat and water", "a ring around the object", "an increase of the T1 of the tissue"],
       "This is the magnetic susceptibility artifact.", lvl="Easy"),
    PR("If the field gradient is larger than the system assumes, the image appears:", "stretched in that dimension", ["compressed in that dimension", "shifted without a change of size", "unchanged"],
       "The system converts frequency to position with the gradient it assumes, so a stronger actual gradient places features farther apart in the reconstructed image.", lvl="Easy"),
    PR("The chemical shift artifact arises because:", "protons in different chemical environments precess at slightly different frequencies", ["the gradient is uneven", "the metal distorts the field", "the coil is faulty"],
       "A small difference in frequency is read as a difference in position, so the signal shifts.", lvl="Moderate"),
    PR("A phantom made of a grid of regularly spaced plastic rods is used to:", "measure the geometric distortion of the images", ["measure the SNR", "calibrate the HU", "measure the dose"],
       "In an undistorted image the grid lines are straight and regular.", lvl="Moderate"),
    PRN(STEM("A local field error of 0.05 mT. The gradient is 10 mT/m.", [], "What is the [[shift of the pixel]]?"), s_a, [0.05 * 10, 0.05 / 10, s_a * 10], "{:.1f} mm",
        f"Shift = ΔB / G = 0.05 mT / 10 mT/m = 0.005 m = {s_a:.1f} mm. An error in the units gives 0.5 mm or 50 mm.", lvl="Moderate"),
    PRN(STEM("A local field error of 0.05 mT. The gradient is 5 mT/m.", [], "What is the [[shift of the pixel]]?"), s_b, [s_a, s_b * 2, s_b / 10], "{:.1f} mm",
        f"Shift = 0.05 / 5 = {s_b / 1000:.2f} m = {s_b:.0f} mm. The weaker gradient doubles the shift.", lvl="Moderate"),
    PRN(STEM("A gradient is 5% larger than the system assumes. An object is 200 mm long.", [], "What [[length]] does it appear to have?"), g_a, [200 / 1.05, 200 * 0.95, 200 - 5], "{:.1f} mm",
        f"Apparent length = 200 × 1.05 = {g_a:.1f} mm, stretched. Dividing by 1.05 gives {200 / 1.05:.1f}, and multiplying by 0.95 gives {200 * 0.95:.0f}.", lvl="Moderate"),
    PRN(STEM("The gradient is 10 mT/m, and the main field is 1.5 T.", [], "How uniform must the local field be, in parts per million of the main field, for a [[shift of 0.1 mm]] at most?"), ppm(1.0 * 10 / 1000 * 0.1, 1.5), [ppm(10 / 1000 * 0.1, 1.5) * 10, ppm(10 / 1000 * 0.1, 1.5) / 10, 0.1], "{:.2f} ppm",
        f"ΔB = shift × G = 0.0001 m × 10 mT/m = 0.001 mT = 1 µT. As a fraction of 1.5 T that is {ppm(10 / 1000 * 0.1, 1.5):.2f} parts per million.", lvl="Challenging"),
    PR("Why do MRI distortions matter more in radiation oncology than in many diagnostic studies?", "The positions of the target and organs are used directly to place the treatment beams", ["The patient is larger", "The field is weaker", "The gradient is not used"],
       "The delivery needs accurate geometry, so a few millimetres of distortion changes where the dose is delivered.", lvl="Challenging"),
]

TERMS = ['distortion', 'susceptibility', 'chemical shift', 'gradient']

TAKE = [
    [('A change in the local field moves the pixel: shift = ΔB / G. The same field error moves a pixel farther when the gradient is weaker.', 'field-shift')],
    [('Susceptibility gives a signal void near metal, a too-strong gradient stretches the image, and the chemical shift displaces the fat signal from the water signal.', 'mri-artifact-list')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Match each MRI artifact to its cause.", ["Susceptibility", "Gradient distortion", "Chemical shift", "B<sub>0</sub> inhomogeneity"],
         [("A metallic object distorts the local field", 0), ("The gradient is larger than expected", 1), ("Protons in different environments precess at different frequencies", 2), ("The main field bows out at the edge of the bore", 3)],
         "Susceptibility comes from metal in the field. Gradient distortion comes from a gradient that is not what the system assumes. The chemical shift comes from the chemical environment, and B<sub>0</sub> inhomogeneity bends the grid lines near the edge of the bore.", lvl="Moderate", mode="match", cap=1),
    TYPED(STEM("A local field error of 0.02 mT. The gradient is 10 mT/m.", [], "What is the [[shift of the pixel]] in millimetres?"), shift(0.02, 10), 0.02, "mm",
          f"Shift = 0.02 / 10 = 0.002 m = {shift(0.02, 10):.0f} mm.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the shift of a pixel against the local field error, for a gradient of 10 mT/m.", [], "Tap the [[field error that moves a pixel by 3 mm]]."),
         FS(x=dict(min=0, max=0.1, ticks=[0, 0.02, 0.04, 0.06, 0.08, 0.1], label="Local field error (mT)"), y=dict(min=0, max=10, ticks=[0, 2.5, 5, 7.5, 10], label="Shift (mm)"), series=[dict(pts=PTS(lambda b: b / 10 * 1000, 0, 0.1), color="plot-1")], xunit=" mT", xdec=3, xname="Field error", label="Shift against local field error"),
         [(dB_3 - 0.008, dB_3 + 0.008)], f"Shift = ΔB / G, so ΔB = 3 mm × 10 mT/m = {dB_3:.2f} mT. The level 3 mm is not marked on the axis.", lvl="Challenging", note=f"about {dB_3:.2f} mT"),
]
INLINE = {0: [1, 6, 7, _n0 + 2], 1: [2, 3, 4, _n0 + 1]}
