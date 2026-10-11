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
        P("The precession frequency is the Larmor frequency, proportional to the field: f = γ̄ B<sub>0</sub>. For hydrogen γ̄ = 42.6 MHz/T, so at 1 T the nucleus precesses at 42.6 MHz, in the radiofrequency range. A stronger field gives a faster precession. Some nuclei have zero spin and no magnetic moment. Helium is one, so it cannot be imaged with MRI. A stronger field also raises the signal-to-noise ratio, roughly in proportion to B<sub>0</sub>, so a 1.5 T magnet gives about three times the SNR of a 0.5 T magnet."),
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

TERMS = ['Larmor frequency', 'gradient', 'resonance', "Faraday's law", 'specific absorption rate', 'MR Conditional']

TAKE = [
    [('The Larmor frequency is f = γ̄ B<sub>0</sub>: 42.6 MHz/T for hydrogen, so 63.9 MHz at 1.5 T and 127.8 MHz at 3 T.', 'larmor-field')],
    [('Radiofrequency waves at the Larmor frequency flip the spins. The precessing moments change the flux through the readout coil and induce the signal.', 'precession-coil')],
    [('A field gradient makes the Larmor frequency depend on position, so choosing the excitation frequency chooses the slice.', 'gradient-slice')],
    ['The static field is always on and pulls on ferromagnetic objects. The switched gradients induce currents that can stimulate nerves, and the RF field heats tissue, which the SAR in W/kg describes.',
     'Implants are MR Safe, MR Conditional, or MR Unsafe. A pacemaker or defibrillator risks lead-tip heating and malfunction, and an MR Conditional system is scanned only under its stated conditions.'],
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


# ---------------------------------------------------------------- safety questions (they follow the last section, so they appear in the practice set)
PROBLEMS += [
    PR("Which field of an MR scanner pulls on a ferromagnetic object that is brought into the room?", "the static field B<sub>0</sub>, which is on at all times", ["the radiofrequency field, during the pulses", "the gradient field, while it switches", "the field of the readout coil, while it receives"],
       "The static field of a superconducting magnet is on also when no scan is running. The RF and gradient fields are applied during the sequence, and they act through induced currents and heating, not through a pull on iron.", lvl="Easy"),
    SORT("Which field causes each hazard?", ["Static field B<sub>0</sub>", "Gradient field", "RF field"],
         [("A pair of scissors accelerates toward the magnet", 0), ("A torque turns a ferromagnetic implant", 0), ("Tingling or twitching from nerve stimulation", 1), ("The loud knocking noise during the scan", 1), ("Heating of the tissue at the tip of a lead", 2), ("A rise of the body temperature that the SAR describes", 2)],
         "The static field is always on, and it acts on ferromagnetic objects with a force and a torque. The gradients switch rapidly, which induces currents that stimulate nerves, and the vibration of the gradient coils makes the noise. The RF field is absorbed as heat, which the SAR measures, and the heating is largest at the tip of a lead.", lvl="Moderate"),
    PRN(STEM("A sequence deposits 105 W of RF power in the body of a patient with a mass of 70 kg.", [], "What is the [[whole-body SAR]]?"), s_q, [70 / 105, s_q * 2, s_q / 10], "{:.1f} W/kg",
        f"SAR = absorbed power / mass = 105 / 70 = {s_q:.1f} W/kg, below the normal-mode limit of 2 W/kg. Inverting the ratio gives {70 / 105:.1f}.", lvl="Moderate"),
    PR("A pacemaker system is labelled MR Conditional. This means that:", "the patient can be scanned if the stated conditions, such as the field strength and the SAR limit, are met", ["the device is unaffected by any scanner at any setting", "the device contains no metal", "the patient can be scanned as long as the magnet is switched off"],
       "MR Conditional means that safety has been shown within defined conditions, which the label lists. A superconducting magnet is never switched off between scans, and the conditions also cover the generator and the leads as a system.", lvl="Moderate"),
    PR("In a patient with a pacemaker, the main cause of tissue injury at the tip of a lead during MRI is:", "heating from the current that the RF field induces in the lead", ["the force of the static field on the lead", "ionizing radiation from the RF coil", "the vibration of the gradient coils"],
       "The long lead acts as an antenna for the RF field, and the induced current deposits its energy in a small volume of tissue at the tip. The static field exerts a force, but not one that pulls the device out of the chest, and MRI uses no ionizing radiation.", lvl="Challenging"),
    PRM("A patient with a cardiac pacemaker system labelled MR Conditional is to have an MR simulation of the brain. Which of the following apply before the scan?", ["The field strength and the SAR limit of the scan are within the conditions on the label", "The device is programmed for the scan beforehand, and the patient is monitored during it"], ["The generator is covered with lead during the scan", "The magnet is ramped down before the patient enters the room", "The ionizing dose to the device stays below the labelled limit"],
        "The label lists the conditions, such as the field strength, the spatial field gradient, and the SAR, and the device is set to its MRI mode before the scan, with monitoring during it. Lead does not shield the static or RF fields, a superconducting magnet is not ramped down between patients, and MRI delivers no ionizing dose.", lvl="Challenging"),
    PR("The same sequence, with the same flip angles and timing, is run at 3 T instead of 1.5 T. The SAR is approximately:", "four times larger, because it rises with the square of the main field", ["twice as large, because it rises in proportion to the main field", "the same, because the SAR depends only on the flip angle", "half as large, because the signal is higher"],
       "The electric field that the RF pulse induces in the body rises in proportion to the frequency, which is proportional to B<sub>0</sub>, and the heating rises with the square of that field: (3 / 1.5)<sup>2</sup> = 4.", lvl="Challenging"),
]
