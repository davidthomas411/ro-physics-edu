from blocks import *
import math, calc

GAMMA = 42.6                                                   # MHz per tesla, hydrogen
larmor = lambda B: GAMMA * B
f15, f3, f05, f035, f1 = larmor(1.5), larmor(3.0), larmor(0.5), larmor(0.35), larmor(1.0)
f_sup, f_inf = larmor(0.9985), larmor(1.0015)
df = f_inf - f_sup                                             # MHz across the patient, for the gradient in the example
z_of = lambda f: (f / GAMMA - 1) / 0.00006                     # position in cm for B = 1 + 0.00006 z, z positive toward the inferior end
B100 = 100 / GAMMA                                             # field at which hydrogen precesses at 100 MHz

TOPIC = dict(
    id="mri-physics", domain=4, sub="IV.A", title="MRI physics: spin, precession, and signal",
    ref=dict(aapm="TG-284", khan="", ford="20"),
    guide=[
        H("Nuclear spin and precession"),
        P("Magnetic resonance imaging uses the properties of nuclei, usually the hydrogen nucleus, to visualize soft tissue. A large main magnetic field, the B<sub>0</sub> field, is applied to the patient, typically 1 to 3 tesla (the Earth's field is about 0.0001 T). Each nucleus that has a non-zero spin acts as a small magnet, with a magnetic dipole moment. When the moment is not aligned with B<sub>0</sub> there is a torque on it, and it precesses about the field like a gyroscope in a gravitational field."),
        P("The precession frequency is the Larmor frequency, proportional to the field: f = γ̄ B<sub>0</sub>. For hydrogen γ̄ = 42.6 MHz/T, so at 1 T the nucleus precesses at 42.6 MHz, in the radiofrequency range. A stronger field gives a faster precession. Some nuclei have zero spin and no magnetic moment. Helium is one, so it cannot be imaged with MRI. A stronger field also raises the signal-to-noise ratio, roughly in proportion to B<sub>0</sub>, so a 1.5 T magnet gives about three times the SNR of a 0.5 T magnet."),
        EX("The Larmor frequency", STEM("Hydrogen nuclei, γ̄ = 42.6 MHz/T.", ["B<sub>0</sub> = 1.5 T", "B<sub>0</sub> = 3.0 T"], "Find the [[Larmor frequency]] at each field."), ["f = 42.6 × B<sub>0</sub>"], f"{f15:.1f} MHz at 1.5 T and {f3:.1f} MHz at 3.0 T. Both are radiofrequencies, and doubling the field doubles the frequency."),

        H("Signal and spin flips"),
        P("The precessing nuclear magnets generate a signal. The magnetic flux through a readout coil changes as the moments precess, and by Faraday's law a changing flux gives a current that can be measured. One nucleus gives a tiny signal, but a biological sample has billions of aligned nuclei that precess together."),
        P("The energy of a nuclear magnetic dipole depends on its orientation to the field. Energy supplied as radiofrequency waves at the Larmor frequency can flip the spins from the low-energy orientation, along the field, to a higher-energy orientation, perpendicular to the field or opposite to it. A spin in a high-energy state decays back to the lowest state over time, and it precesses as it does so, which produces the signal in the coil. Only radiation at the Larmor frequency flips the spins, which is what resonance means."),

        H("Image formation with gradients"),
        P("To form an image the signal must be tied to a position. Extra magnetic fields, much smaller than B<sub>0</sub>, are applied with gradient coils so that the field varies along an axis. If the field along the patient's superior–inferior axis is 1.0000 T at the center, it might be 0.9985 T at the superior end and 1.0015 T at the inferior end. The nuclei then precess a little faster in the inferior region. Choosing the frequency of the excitation chooses the slice, so that only that slice is probed. Gradients in other directions give the position within the slice, and together they allow the image to be formed."),
        EX("A field gradient", STEM("The field varies along the patient from 0.9985 T at the superior end to 1.0015 T at the inferior end.", [], "Find the [[difference in Larmor frequency]] across the patient."), ["f<sub>inf</sub> = 42.6 × 1.0015 = " + f"{f_inf:.4f} MHz", "f<sub>sup</sub> = 42.6 × 0.9985 = " + f"{f_sup:.4f} MHz"], f"{df:.4f} MHz, or {1000 * df:.0f} kHz. The frequency tells where in the patient the signal comes from."),
    ],
    cards=[
        F("Basis of MRI", "Nuclei with non-zero spin, usually hydrogen, act as magnets and precess in a strong magnetic field."),
        F("Main field B<sub>0</sub>", "Typically 1 to 3 T. The Earth's field is about 0.0001 T."),
        F("Larmor frequency", "f = γ̄ B<sub>0</sub>, the precession frequency of the nuclear moment about the field. For hydrogen γ̄ = 42.6 MHz/T."),
        F("Larmor frequency at 1 T", "42.6 MHz for hydrogen, in the radiofrequency range. It rises in proportion to the field."),
        F("Zero-spin nuclei", "Helium, for example, has zero spin and no magnetic moment, so it cannot be imaged with MRI."),
        F("Field strength and SNR", "The SNR rises roughly in proportion to B<sub>0</sub>: a 1.5 T magnet gives about three times the SNR of a 0.5 T magnet."),
        F("MRI signal detection", "A precessing moment changes the flux through a readout coil, which gives a current by Faraday's law. There are billions of aligned nuclei."),
        F("RF pulse", "Radiofrequency waves at the Larmor frequency flip the spins into a higher-energy orientation. That is resonance."),
        F("Relaxation", "A spin in a high-energy state decays back toward the field, precessing as it does so, which produces the signal."),
        F("Gradient fields", "Small extra fields that vary along an axis, so that the Larmor frequency depends on position."),
        F("Slice selection", "Choosing the frequency of the excitation picks the slice, because the Larmor frequency varies along the gradient."),
    ],
)

PROBLEMS = [
    PR("What property of materials is used for imaging in an MR scanner?", "Nuclear magnetic moments precessing in a strong magnetic field", ["Electron spins precessing in a strong magnetic field", "Attenuation of the beam in tissue", "The positrons emitted by a tracer"],
       "MRI uses the magnetic moments of nuclei, mainly hydrogen, which precess about the main field.", lvl="Easy"),
    PR("The Larmor frequency is:", "the precession frequency of the nuclear magnetic moment, proportional to the magnetic field", ["the frequency of the gradient coils", "the repetition time of the pulse sequence", "the frequency of the 180° pulse only"],
       "f = γ̄ B<sub>0</sub>. A stronger field gives a faster precession.", lvl="Easy"),
    PR("Which nucleus cannot be imaged with MRI?", "Helium, which has zero spin", ["Hydrogen", "A nucleus with a non-zero spin", "Any nucleus in a magnetic field"],
       "Helium has no magnetic dipole moment, because its spin is zero.", lvl="Easy"),
    PRN(STEM("The Larmor frequency of hydrogen is 42.6 MHz/T.", [], "What is the [[Larmor frequency]] at 1.5 T?"), f15, [f1, f3, 42.6 / 1.5], "{:.1f} MHz",
        f"f = 42.6 × 1.5 = {f15:.1f} MHz. The value at 1 T is {f1:.1f} MHz, and dividing by the field gives {42.6 / 1.5:.1f}.", lvl="Moderate"),
    PRN(STEM("The Larmor frequency of hydrogen is 42.6 MHz/T.", [], "What is the [[Larmor frequency]] at 3.0 T?"), f3, [f15, 42.6 / 3, 42.6 + 3], "{:.1f} MHz",
        f"f = 42.6 × 3.0 = {f3:.1f} MHz.", lvl="Moderate"),
    PR("The signal in MRI is detected because:", "the changing magnetic flux of the precessing nuclei induces a current in a readout coil", ["the nuclei emit positrons", "the nuclei absorb the main field", "the gradient coils measure the attenuation"],
       "By Faraday's law, a changing flux induces a current. Billions of aligned nuclei give a measurable signal.", lvl="Moderate"),
    PR("Spins are flipped into a higher-energy orientation by radiofrequency waves at:", "the Larmor frequency", ["any frequency, if the power is high enough", "the frequency of the gradient field", "half the Larmor frequency"],
       "The energy must be supplied at the resonance, the Larmor frequency, to flip the spins.", lvl="Moderate"),
    PR("A 1.5 T magnet compared with a 0.5 T magnet gives a signal-to-noise ratio that is approximately:", "three times larger", ["nine times smaller", "the same", "twelve times larger"],
       "The SNR rises roughly in proportion to the main field, and 1.5 / 0.5 = 3.", lvl="Moderate"),
    PR("A field gradient along the patient is used to:", "make the Larmor frequency depend on position, so that a slice can be selected by its frequency", ["raise the SNR", "flip the spins into the transverse plane", "remove distortions of the main field"],
       "With a gradient, the precession frequency varies with position, so exciting at one frequency selects one slice.", lvl="Moderate"),
    PRN(STEM("The field varies along the patient from 0.9985 T at the superior end to 1.0015 T at the inferior end.", ["γ̄ = 42.6 MHz/T"], "What is the [[difference in Larmor frequency]] between the two ends?"), df, [df * 10, df / 10, GAMMA * 0.003 / 2], "{:.3f} MHz",
        f"f<sub>inf</sub> − f<sub>sup</sub> = 42.6 × (1.0015 − 0.9985) = 42.6 × 0.003 = {df:.3f} MHz. The units are megahertz, and a slip of a power of ten gives {df * 10:.2f} or {df / 10:.4f}.", lvl="Challenging"),
    PR("In the field gradient of the example, the nuclei at the inferior end precess:", "faster than those at the superior end, because the field is larger there", ["slower, because the field is larger there", "at the same frequency, because B<sub>0</sub> is the same", "faster, because the nuclei are lighter"],
       "The Larmor frequency is proportional to the local field, and the field is 1.0015 T at the inferior end and 0.9985 T at the superior end.", lvl="Challenging"),
    PR("Why is the signal from a single nucleus not used in MRI?", "It is far too small, and a sample has billions of aligned nuclei that together give a measurable signal", ["A single nucleus does not precess", "A single nucleus has no magnetic moment", "A single nucleus relaxes instantly"],
       "The signal from one precessing nucleus is tiny. Billions of nuclei in tissue, precessing together, induce a measurable current.", lvl="Challenging"),
]

TERMS = ['Larmor frequency', 'gradient', 'resonance', "Faraday's law"]

TAKE = [
    [('The Larmor frequency is f = γ̄ B<sub>0</sub>: 42.6 MHz/T for hydrogen, so 63.9 MHz at 1.5 T and 127.8 MHz at 3 T.', 'larmor-field')],
    [('Radiofrequency waves at the Larmor frequency flip the spins. The precessing moments change the flux through the readout coil and induce the signal.', 'precession-coil')],
    [('A field gradient makes the Larmor frequency depend on position, so choosing the excitation frequency chooses the slice.', 'gradient-slice')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Which part of the MRI system does each role belong to?", ["Main field B<sub>0</sub>", "RF pulse", "Gradient", "Readout coil"],
         [("Sets the Larmor frequency and aligns the nuclei, 1 to 3 T", 0), ("Flips the spins at the Larmor frequency", 1), ("Makes the Larmor frequency depend on position", 2), ("Detects the changing flux as a current", 3), ("Selects the slice by frequency", 2), ("Supplies energy for resonance", 1)],
         "The main field sets the precession frequency. The RF pulse supplies the energy for resonance. The gradient ties the frequency to position, and the coil detects the signal by Faraday's law.", lvl="Moderate"),
    TYPED(STEM("A low-field MR unit has B<sub>0</sub> = 0.35 T. γ̄ = 42.6 MHz/T.", [], "What is the [[Larmor frequency]]?"), f035, 0.01, "MHz",
          f"f = 42.6 × 0.35 = {f035:.2f} MHz.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the Larmor frequency of hydrogen against the main field.", [], "Tap the [[field at which hydrogen precesses at 100 MHz]]."),
         FS(x=dict(min=0, max=3, ticks=[0, 0.5, 1, 1.5, 2, 2.5, 3], label="Main field B<sub>0</sub> (T)"), y=dict(min=0, max=130, ticks=[0, 40, 80, 120], label="Larmor frequency (MHz)"), series=[dict(pts=PTS(lambda b: GAMMA * b, 0, 3), color="plot-1")], xunit=" T", xdec=2, xname="Field", label="Larmor frequency against main field"),
         [(B100 - 0.25, B100 + 0.25)], f"f = 42.6 B gives B = 100 / 42.6 = {B100:.2f} T. The level 100 MHz is not marked on the axis.", lvl="Challenging", note=f"about {B100:.1f} T"),
]
INLINE = {0: [1, 3, 4, 8], 1: [6, 7, _n0 + 1], 2: [9, 10, _n0 + 3]}
