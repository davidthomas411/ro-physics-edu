from blocks import *
import math, calc

GAMMA = 42.6                                                   # MHz per tesla, hydrogen
larmor = lambda B: GAMMA * B
f15, f3, f05, f035, f1 = larmor(1.5), larmor(3.0), larmor(0.5), larmor(0.35), larmor(1.0)
f_sup, f_inf = larmor(0.9985), larmor(1.0015)
df = f_inf - f_sup                                             # MHz across the patient, for the gradient in the example
z_of = lambda f: (f / GAMMA - 1) / 0.00006                     # position in cm for B = 1 + 0.00006 z, z positive toward the inferior end
B100 = 100 / GAMMA                                             # field at which hydrogen precesses at 100 MHz
sar = lambda p, m: p / m                                       # specific absorption rate in W/kg, for p watts of RF power absorbed in a mass of m kg
s_ex, s_q = sar(150, 60), sar(105, 70)

TOPIC = dict(
    id="mri-physics", domain=4, sub="IV.A", title="MRI physics: spin, precession, and signal",
    ref=dict(aapm="TG-284", khan="", ford="20"),
    guide=[
        H("Nuclear spin and precession"),
        P("Magnetic resonance imaging uses the properties of nuclei, usually the hydrogen nucleus, to visualize soft tissue. A large main magnetic field, the B<sub>0</sub> field, is applied to the patient, typically 1 to 3 tesla (the Earth's field is about 0.00005 T). Each nucleus that has a non-zero spin acts as a small magnet, with a magnetic dipole moment. When the moment is not aligned with B<sub>0</sub> there is a torque on it, and it precesses about the field like a gyroscope in a gravitational field."),
        P("The precession frequency is the Larmor frequency, proportional to the field: f = γ̄ B<sub>0</sub>. For hydrogen γ̄ = 42.6 MHz/T, so at 1 T the nucleus precesses at 42.6 MHz, in the radiofrequency range. A stronger field gives a faster precession. Some nuclei have zero spin and no magnetic moment. Helium-4 is one, so it cannot be imaged with MRI. A stronger field also raises the signal-to-noise ratio, roughly in proportion to B<sub>0</sub>, so a 1.5 T magnet gives about three times the SNR of a 0.5 T magnet."),
        EX("The Larmor frequency", STEM("Hydrogen nuclei, γ̄ = 42.6 MHz/T.", ["B<sub>0</sub> = 1.5 T", "B<sub>0</sub> = 3.0 T"], "Find the [[Larmor frequency]] at each field."), ["f = 42.6 × B<sub>0</sub>"], f"{f15:.1f} MHz at 1.5 T and {f3:.1f} MHz at 3.0 T. Both are radiofrequencies, and doubling the field doubles the frequency."),

        H("Signal and spin flips"),
        P("The precessing nuclear magnets generate a signal. The magnetic flux through a readout coil changes as the moments precess, and by Faraday's law a changing flux gives a current that can be measured. One nucleus gives a tiny signal, but a biological sample has billions of aligned nuclei that precess together."),
        P("The energy of a nuclear magnetic dipole depends on its orientation to the field. Energy supplied as radiofrequency waves at the Larmor frequency can flip the spins from the low-energy orientation, along the field, to a higher-energy orientation, perpendicular to the field or opposite to it. A spin in a high-energy state decays back to the lowest state over time, and it precesses as it does so, which produces the signal in the coil. Only radiation at the Larmor frequency flips the spins, which is what resonance means."),

        H("Image formation with gradients"),
        P("To form an image the signal must be tied to a position. Extra magnetic fields, much smaller than B<sub>0</sub>, are applied with gradient coils so that the field varies along an axis. If the field along the patient's superior–inferior axis is 1.0000 T at the center, it might be 0.9985 T at the superior end and 1.0015 T at the inferior end. The nuclei then precess a little faster in the inferior region. Choosing the frequency of the excitation chooses the slice, so that only that slice is probed. Gradients in other directions give the position within the slice, and together they allow the image to be formed."),
        EX("A field gradient", STEM("The field varies along the patient from 0.9985 T at the superior end to 1.0015 T at the inferior end.", [], "Find the [[difference in Larmor frequency]] across the patient."), ["f<sub>inf</sub> = 42.6 × 1.0015 = " + f"{f_inf:.4f} MHz", "f<sub>sup</sub> = 42.6 × 0.9985 = " + f"{f_sup:.4f} MHz"], f"{df:.4f} MHz, or {1000 * df:.0f} kHz. The frequency tells where in the patient the signal comes from."),

        H("MRI safety"),
        P("The scanner exposes the patient, and anything brought into the room, to three kinds of field, and each has its own hazard. The static field B<sub>0</sub> is on at all times, also between scans. It pulls on ferromagnetic objects, so a cylinder, a pair of scissors, or a wheelchair can be accelerated toward the magnet like a projectile, and a ferromagnetic implant feels a force and a torque. The gradient fields are switched on and off rapidly, and by Faraday's law they induce currents in conductors. In the body these can stimulate nerves, which is felt as tingling or twitching, and the gradient coils make a loud noise, so the patient wears ear protection. The radiofrequency field deposits energy in the tissue as heat."),
        P("The heating is described by the specific absorption rate (SAR), the RF power absorbed per kilogram of tissue. The scanner estimates it from the sequence and the weight of the patient and keeps it below a limit, which for the whole body is 2 W/kg in the normal operating mode. The SAR rises with the square of the main field and with the RF power per unit time, so fast sequences with large flip angles reach the limit first, especially at 3 T. A long conductor, such as an implanted lead, a cable, or a loop formed by skin touching skin, can concentrate the induced current at one point, and the heating there can be much larger than the average SAR suggests."),
        EX("The specific absorption rate", STEM("A sequence deposits 150 W of RF power in the body of a patient with a mass of 60 kg. The limit is 2 W/kg.", [], "Find the [[whole-body SAR]]."), ["SAR = absorbed power / mass", "SAR = 150 W / 60 kg"], f"{s_ex:.1f} W/kg, above the limit of 2 W/kg, so the scanner has to lower the RF power, for example with a smaller flip angle or a longer TR."),
        P("Implants are labelled by how they behave in the MR environment. MR Safe means that the item poses no known hazard in any MR environment, as for a plastic object. MR Conditional means that the item is safe only under stated conditions, for example a field strength, a maximum spatial field gradient, a maximum SAR, and a limit on the gradient switching rate, which the label gives. MR Unsafe means a known hazard, as for ferromagnetic scissors."),
        P("A pacemaker or defibrillator carries three risks. The RF field induces current in the leads, which heats the tissue at the tip of a lead and can injure the heart muscle. The gradient and RF fields can be sensed by the device as if they were a heart signal, which can inhibit the pacing or trigger an inappropriate shock, and the device can change its settings or fail. The static field exerts a force and a torque on the ferromagnetic parts of the device, which is why the label limits the field strength and the spatial field gradient, but the force on a modern device is not enough to pull it out of the chest, so heating and malfunction are the main concerns. A patient whose device is not MR Conditional is generally not scanned. A patient with an MR Conditional system, a generator and leads approved together, can be scanned under the stated conditions, after the device is programmed for the scan and with monitoring during it. MRI uses no ionizing radiation, so no radiation dose reaches the device: the hazards come from the three fields."),
    ],
    cards=[
        F("Basis of MRI", "Nuclei with non-zero spin, usually hydrogen, act as magnets and precess in a strong magnetic field."),
        F("Main field B<sub>0</sub>", "Typically 1 to 3 T. The Earth's field is about 0.00005 T."),
        F("Larmor frequency", "f = γ̄ B<sub>0</sub>, the precession frequency of the nuclear moment about the field. For hydrogen γ̄ = 42.6 MHz/T."),
        F("Zero-spin nuclei", "Helium-4, for example, has zero spin and no magnetic moment, so it cannot be imaged with MRI."),
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
    PRN(STEM("The Larmor frequency of hydrogen is 42.6 MHz/T.", [], "What is the [[Larmor frequency]] at 1.5 T?"), f15, [f1, f3, 42.6 / 1.5], "{:.1f} MHz",
        f"f = 42.6 × 1.5 = {f15:.1f} MHz. The value at 1 T is {f1:.1f} MHz, and dividing by the field gives {42.6 / 1.5:.1f}.", lvl="Moderate"),
    PR("The signal in MRI is detected because:", "the changing magnetic flux of the precessing nuclei induces a current in a readout coil", ["the nuclei emit positrons", "the nuclei absorb the main field", "the gradient coils measure the attenuation"],
       "By Faraday's law, a changing flux induces a current. Billions of aligned nuclei give a measurable signal.", lvl="Moderate"),
    PR("Spins are flipped into a higher-energy orientation by radiofrequency waves at:", "the Larmor frequency", ["any frequency, if the power is high enough", "the frequency of the gradient field", "half the Larmor frequency"],
       "The energy must be supplied at the resonance, the Larmor frequency, to flip the spins.", lvl="Moderate"),
    PR("A 1.5 T magnet compared with a 0.5 T magnet gives a signal-to-noise ratio that is approximately:", "three times larger", ["nine times smaller", "the same", "twelve times larger"],
       "The SNR rises roughly in proportion to the main field, and 1.5 / 0.5 = 3.", lvl="Moderate"),
    PR("A field gradient along the patient is used to:", "make the Larmor frequency depend on position, so that a slice can be selected by its frequency", ["raise the SNR", "flip the spins into the transverse plane", "remove distortions of the main field"],
       "With a gradient, the precession frequency varies with position, so exciting at one frequency selects one slice.", lvl="Moderate"),
]

TERMS = ['Larmor frequency', 'gradient', 'resonance', "Faraday's law", 'specific absorption rate', 'MR Conditional']

TAKE = [
    [('The Larmor frequency is f = γ̄ B<sub>0</sub>: 42.6 MHz/T for hydrogen, so 63.9 MHz at 1.5 T and 127.8 MHz at 3 T.', 'larmor-field')],
    [('Radiofrequency waves at the Larmor frequency flip the spins. The precessing moments change the flux through the readout coil and induce the signal.', 'precession-coil')],
    [('A field gradient makes the Larmor frequency depend on position, so choosing the excitation frequency chooses the slice.', 'gradient-slice')],
    ['The static field is always on and pulls on ferromagnetic objects. The switched gradients induce currents that can stimulate nerves, and the RF field heats tissue, which the SAR in W/kg describes.',
     'Implants are MR Safe, MR Conditional, or MR Unsafe. A pacemaker or defibrillator risks lead-tip heating and malfunction, and an MR Conditional system is scanned only under its stated conditions.'],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
PROBLEMS += [
    SORT("Which part of the MRI system does each role belong to?", ["Main field B<sub>0</sub>", "RF pulse", "Gradient", "Readout coil"],
         [("Sets the Larmor frequency and aligns the nuclei, 1 to 3 T", 0), ("Flips the spins at the Larmor frequency", 1), ("Makes the Larmor frequency depend on position", 2), ("Detects the changing flux as a current", 3), ("Selects the slice by frequency", 2), ("Supplies energy for resonance", 1)],
         "The main field sets the precession frequency. The RF pulse supplies the energy for resonance. The gradient ties the frequency to position, and the coil detects the signal by Faraday's law.", lvl="Moderate"),
]
INLINE = {0: [1, 3, 6], 1: [4, 5, 8], 2: [7]}


# ---------------------------------------------------------------- safety questions (they follow the last section, so they appear in the practice set)
PROBLEMS += [
]
