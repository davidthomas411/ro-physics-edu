from blocks import *
import math, calc

# ---------------------------------------------------------------- this chapter's formulas
def wavelength_cm(f_mhz):
    """λ = c / f, in cm, for a frequency in MHz."""
    return 100 * calc.wavelength_m(f_mhz * 1e6)

def gain(t_mev, length_m):
    """Energy gain per metre of an accelerating guide (MeV/m); the injection energy, tens of keV, is neglected."""
    return t_mev / length_m

def guide_length(t_mev, g):
    """Length (m) that gives the kinetic energy t_mev at a gain g (MeV/m)."""
    return t_mev / g

def pc(t_mev):
    """Momentum × c (MeV) of an electron of kinetic energy t_mev: √(T² + 2T m<sub>e</sub>c²)."""
    return calc.pc_ke(t_mev, calc.ME)

def field_t(t_mev, r_m):
    """Field (T) that holds an electron of kinetic energy t_mev on a circle of radius r_m: B = p / (e r) = pc [MeV] / (299.8 r [m])."""
    return pc(t_mev) / (299.792458 * r_m)

def mean_photon(t_mev):
    """Mean photon energy of a megavoltage bremsstrahlung beam: about one third of the maximum, which is the electron kinetic energy."""
    return t_mev / 3

def per_pulse_cgy(rate_cgy_min, prf):
    """Dose per pulse (cGy) from a dose rate in cGy/min and a pulse repetition rate in pulses per second."""
    return rate_cgy_min / 60 / prf

def avg_kw(peak_mw, width_us, prf):
    """Average RF power (kW): the peak power times the duty cycle, which is the pulse length times the repetition rate."""
    return peak_mw * 1e3 * (width_us * 1e-6 * prf)

# ---------------------------------------------------------------- numbers used in the text, the worked examples, and the questions
LAM, LAM_T = wavelength_cm(2998), wavelength_cm(2856)                        # S band: worked example, typed question
B30, B2 = calc.beta_ke(0.030, calc.ME), calc.beta_ke(2.0, calc.ME)           # speed at injection (30 keV) and after the bunching cells (2 MeV)
G1 = gain(6, 0.40); L18 = guide_length(18, G1)                               # worked example: 6 MeV over 40 cm, then 18 MeV
G2 = gain(6, 0.30); L15 = guide_length(15, G2)                               # question: 6 MeV over 30 cm, then 15 MeV
L15_inv, L15_ratio = 0.30 * 6 / 15, 15 / 6                                   # decoys: inverted ratio; the energy ratio read as a length
PC18, PC6, PC12, PC20 = pc(18), pc(6), pc(12), pc(20)
BF18, BF6 = field_t(18, 0.10), field_t(6, 0.10); RAT18 = PC18 / PC6          # worked example: 10 cm path
BF12 = field_t(12, 0.080)                                                    # question: 12 MeV on an 8.0 cm path
PNR12 = math.sqrt(2 * calc.ME * 12); BNR12 = PNR12 / (299.792458 * 0.080)    # decoy: non-relativistic momentum
RAT20 = PC20 / PC6                                                           # question: 6 MeV to 20 MeV on one path
M6 = mean_photon(6)
DP600, DP1400, DP2400 = per_pulse_cgy(600, 360), per_pulse_cgy(1400, 360), per_pulse_cgy(2400, 360)   # cGy per pulse at 360 pulses per second
DUTY = 4.0e-6 * 250; AVG = avg_kw(3.0, 4.0, 250)                             # 3.0 MW peak, 4.0 µs pulses, 250 per second

TOPIC = dict(
    id="linac-components", domain=1, sub="I.D", title="Linac components",
    ref=dict(aapm="", khan="", ford="9"),
    guide=[
        H("Layout and RF power"),
        P("The gantry turns on a fixed stand, and its axis meets the collimator and couch axes at the isocenter, 100 cm from the source on most machines. A modulator charges a pulse-forming network, and a thyratron, a hydrogen-filled switching tube, discharges it. Each discharge sends a pulse of a few microseconds to the RF source and the electron gun together, a few hundred times per second."),
        P("The RF source makes microwaves in the S band, near 3 GHz (2856 and 2998 MHz are both used). A magnetron is an oscillator and generates them itself. A klystron is an amplifier that raises the output of a low-power RF driver."),
        TABLE(["", "Magnetron", "Klystron"], [["Kind of source", "Oscillator", "Amplifier of a low-power RF driver"], ["Peak power", "About 2 to 5 MW", "About 5 to 7 MW"],
                                              ["Typical use", "Compact and lower-energy machines, and some high-energy ones", "High-energy machines"]]),
        P("A waveguide filled with an insulating gas under pressure, usually SF<sub>6</sub>, carries the microwaves to the accelerating guide without arcing. A circulator in it diverts power reflected from the guide into a load, protecting the source. The resonant frequency of the guide shifts as its copper warms, so cooling water holds its temperature and an automatic frequency control (AFC) keeps the source tuned to it."),
        EX("Microwave wavelength", STEM("An S-band accelerating guide.", ["frequency f = 2998 MHz", "c = 2.998 × 10<sup>8</sup> m/s"], "Find the [[wavelength]] of the microwaves."),
           ["λ = c / f", f"λ = 2.998 × 10<sup>8</sup> m/s ÷ 2.998 × 10<sup>9</sup> s<sup>−1</sup> = {LAM / 100:.3f} m"], f"{LAM:.1f} cm."),

        H("Electron beam path"),
        P(f"In the electron gun a heated cathode releases electrons, and in a triode gun a grid gates them into pulses timed with the microwaves. They enter the guide with tens of keV ({B30:.2f}c at 30 keV). Discs with a central hole divide the copper guide into cells and slow the wave to the speed of the electrons; the shorter first cells gather the electrons into bunches, which reach {B2:.2f}c by 2 MeV. Ion pumps hold the vacuum; focusing and steering coils keep the beam narrow and centred."),
        P("A travelling-wave guide carries the wave along with the electrons and sends the power left at its end into a load. In a standing-wave guide the wave reflects at both ends, and the circulator diverts the returning power. In its usual mode every second cell carries almost no field. A side-coupled guide sets these coupling cells off the axis, so every cell on the axis accelerates and the guide is shorter for the same energy, gaining about 12 to 20 MeV/m."),
        EX("Energy gain per metre", STEM("A standing-wave guide (illustrative values).", ["final kinetic energy = 6 MeV", "length = 40 cm"], "Find the [[energy gain per metre]] and the length needed for 18 MeV at the same gain."),
           [f"Gain = 6 MeV ÷ 0.40 m = {G1:.0f} MeV/m; the injection energy, tens of keV, is negligible", f"Length = 18 MeV ÷ {G1:.0f} MeV/m"], f"{G1:.0f} MeV/m, and {L18:.1f} m for 18 MeV."),
        P("A 4 to 6 MV guide can point straight at the isocenter; a longer one lies along the gantry, and a bending magnet turns the beam toward the patient. The radius of each path grows with the momentum, so a 90° bend spreads electrons of different energies over the target and enlarges the focal spot. A 270° achromatic magnet returns them to one point and direction. Slits where the paths separate remove electrons outside a narrow window, for example ±3%, and the magnet current selects the energy."),
        EQ("r = p / (eB),   so   B [T] = pc [MeV] / (299.8 × r [m])", "pc = √(T² + 2T m<sub>e</sub>c²),   T = kinetic energy,   m<sub>e</sub>c² = 0.511 MeV"),
        EX("Field of the bending magnet", STEM("A 270° bending magnet.", ["electron kinetic energy T = 18 MeV", "radius of the central path r = 10 cm"], "Find the [[magnetic field]], and the field that holds 6 MeV electrons on the same path."),
           [f"pc = √(18² + 2 × 18 × 0.511) = {PC18:.2f} MeV", f"B = {PC18:.2f} ÷ (299.8 × 0.10) = {BF18:.3f} T", f"At 6 MeV, pc = {PC6:.2f} MeV and B = {BF6:.3f} T"],
           f"{BF18:.3f} T at 18 MeV and {BF6:.3f} T at 6 MeV. The field follows the momentum, which is {RAT18:.2f} times larger, not 3 times."),

        H("Treatment head"),
        P(f"In photon mode the electrons strike a transmission target, usually tungsten backed by copper that carries the heat away: at megavoltage energies the bremsstrahlung goes mainly forward, out of the far side. The maximum photon energy equals the electron kinetic energy, and the mean is about a third of it, about {M6:.0f} MeV for 6 MeV electrons."),
        P("A primary collimator, a tungsten block with a conical opening, sets the largest circular field. A conical flattening filter removes the central peak so that the profile is flat at about 10 cm depth; it lowers the dose rate and hardens the beam."),
        P("In electron mode the target moves out and a scattering foil replaces the filter; in a dual-foil system a thin high-Z foil spreads the narrow beam and a shaped second foil evens it out. The current is lowered: photon mode needs of the order of 100 times more, since most of the electron energy becomes heat in the target. A flattening filter would stop most electrons near the axis, where it is thicker than their range."),
        TABLE(["", "Photon mode", "Electron mode"], [["Target", "In the beam", "Moved out"], ["Filter or foil", "Flattening filter", "Scattering foils"],
                                                     ["Electron current", "High", "Of the order of 100 times lower"], ["Field near the patient", "Jaws and MLC", "Applicator and cutout, with the jaws set for the applicator"]]),
        P("A flattening-filter-free (FFF) beam leaves the filter out, sometimes with a thin metal plate in its place. At the same electron energy it is softer: one 6 MV beam had TPR<sub>20,10</sub> 0.629 without the filter and 0.665 with it. Other designs raise the electron energy to match the flattened depth dose. The spectrum varies less across the field, fewer electrons strike the target per MU, so head leakage per MU falls, and each pulse carries more dose."),

        H("Collimation and dose monitoring"),
        P("Two pairs of tungsten jaws, the secondary collimators, set a rectangular field, the upper pair moving at right angles to the lower. Each jaw moves independently. A jaw closed to the central axis forms a half-beam block: that edge lies along the central ray and does not diverge, for matching adjacent fields. An MLC sits below the jaws in some heads and replaces one pair in others."),
        P("A thin mirror in the beam reflects a lamp at the mirror image of the target, so the jaws cast a light field matching the radiation field. An optical distance indicator projects a scale onto the skin that reads the SSD."),
        P("Two independent transmission ion chambers, the monitor chambers, lie between the filter or foil and the jaws. Most are sealed, so the reading does not depend on air temperature and pressure unless the seal leaks. The primary channel stops the beam at the set MU, the secondary a small margin later if the primary fails, and a timer last. Segmented electrodes compare opposite halves of the beam, and a servo adjusts the steering coils to keep it symmetric. A steering fault, which makes the electrons strike the target off-centre or at an angle, makes the profile asymmetric; past a limit an interlock stops the beam, as others do for the dose rate, cooling water, vacuum, and doors."),
        EX("Dose per pulse", STEM("A flattened beam and an FFF beam (illustrative values).", ["dose rates = 600 MU/min flattened, 1400 MU/min FFF", "1 MU = 1 cGy at the reference point", "pulse repetition rate = 360 per second in both"], "Find the [[dose per pulse]] at the reference point in each beam."),
           ["600 cGy/min ÷ 60 s/min = 10 cGy/s", f"10 cGy/s ÷ 360 pulses/s = {DP600:.4f} cGy", f"FFF: 1400 ÷ 60 ÷ 360 = {DP1400:.4f} cGy"],
           f"{10 * DP600:.2f} mGy per pulse flattened and {10 * DP1400:.2f} mGy FFF, {DP1400 / DP600:.1f} times more."),
    ],
    cards=[
        F("Modulator", "A thyratron discharges the pulse-forming network, sending a high-voltage pulse of a few microseconds to the RF source and the gun, a few hundred times per second."),
        F("Magnetron and klystron", ["Magnetron: an oscillator, about 2 to 5 MW peak.", "Klystron: an amplifier of a low-power RF driver, about 5 to 7 MW peak."]),
        F("Circulator", "Passes RF power to the accelerating guide and diverts power reflected from it into a load, protecting the RF source."),
        F("Automatic frequency control", "Keeps the RF source tuned to the resonant frequency of the accelerating guide, which shifts as the guide warms."),
        F("Electron gun", "A heated cathode releases electrons, and in a triode gun a grid gates them into pulses. They enter the guide with tens of keV and are bunched in its first cells."),
        F("Standing-wave and travelling-wave guides", "A standing-wave guide is shorter for the same energy: its coupling cells, which carry almost no field, sit off the axis. A travelling-wave guide sends the power left at its end into a load."),
        F("270° achromatic bending magnet", "Returns electrons of slightly different energies to one spot on the target. Slits where the paths separate remove those outside a narrow energy window."),
        F("Transmission target", "Tungsten, often backed by copper. Megavoltage bremsstrahlung goes mainly forward, so the beam leaves through the far side."),
        F("Photon energies from the electron energy", "The maximum photon energy equals the electron kinetic energy; the mean is about one third of it.", w=[f"6 MeV electrons: maximum 6 MeV, mean about {M6:.0f} MeV"]),
        F("Electron mode", "Target out, scattering foils in place of the flattening filter, and an electron current of the order of 100 times lower than in photon mode."),
        F("FFF beam at the same electron energy", "Softer (lower TPR<sub>20,10</sub>), with less change of spectrum across the field, less head leakage per MU, and more dose per pulse."),
        F("Monitor chambers", "Two independent transmission chambers. The primary stops the beam at the set MU, the secondary a small margin later, and a timer last."),
        F("Leaking sealed monitor chamber", "Its reading, and so the output, follows the air temperature and pressure."),
        F("Steering servo and steering faults", "Segmented electrodes compare opposite halves of the beam and adjust the steering coils. A steering fault makes the profile asymmetric."),
        F("Half-beam block", "A jaw closed to the central axis gives an edge that does not diverge, for matching adjacent fields."),
        F("Light field", "A thin mirror reflects a lamp at the mirror image of the target, so the jaws cast a light field that matches the radiation field."),
    ],
)

PROBLEMS = [
    # ---- 1-5: layout and RF power
    PR(STEM(ask="Which statement about the klystron of a linac is correct?"), "It amplifies microwaves from a low-power RF driver",
       ["It generates microwaves by oscillating on its own", "It accelerates the electrons to the treatment energy", "It diverts reflected power away from the RF source"],
       "A klystron is an amplifier: an RF driver supplies a low-power signal and the klystron raises it to a peak of about 5 to 7 MW. A source that oscillates on its own is a magnetron, the electrons gain their energy in the accelerating guide, and the circulator handles reflected power.", lvl="Easy"),
    PR(STEM("A magnetron linac warms up over the first hour of treatment.", [], "Which part keeps the magnetron tuned to the resonant frequency of the accelerating guide?"), "The automatic frequency control",
       ["The circulator", "The pulse-forming network", "The thyratron"],
       "The resonant frequency of the guide shifts as its copper warms, and the AFC retunes the magnetron to follow it. The circulator diverts reflected power, the pulse-forming network stores the energy of each pulse, and the thyratron discharges it.", lvl="Easy"),
    SORT("Match each part of a linac to its function.", ["Thyratron", "Circulator", "SF<sub>6</sub> in the waveguide", "Energy slits", "Segmented monitor chamber"],
         [("Discharges the pulse-forming network to make each pulse", 0), ("Diverts power reflected from the guide into a load", 1), ("Prevents arcing at megawatt peak powers", 2),
          ("Remove electrons outside a narrow energy window", 3), ("Senses an asymmetric beam for the steering servo", 4)],
         "The thyratron is the switch of the modulator, and the circulator protects the RF source. The insulating gas lets the waveguide carry megawatt pulses without breakdown. The slits sit where the bending magnet separates the electrons by energy, and the segments of the monitor chamber compare opposite halves of the beam.", lvl="Moderate", mode="match", cap=1),
    TYPED(STEM("A linac runs at an S-band frequency.", ["f = 2856 MHz", "c = 2.998 × 10<sup>8</sup> m/s"], "What is the [[wavelength]] of the microwaves?"), LAM_T, 0.01, "cm",
          f"λ = c / f = 2.998 × 10<sup>8</sup> ÷ 2.856 × 10<sup>9</sup> = {LAM_T / 100:.4f} m = {LAM_T:.1f} cm.", lvl="Easy"),
    TYPED(STEM("A magnetron is pulsed by the modulator.", ["peak power = 3.0 MW", "pulse length = 4.0 µs", "pulse repetition rate = 250 per second"], "What is the [[average RF power]]?"), AVG, 0.02, "kW",
          f"The duty cycle is 4.0 µs × 250 s<sup>−1</sup> = {DUTY:.3f}, so the average power is 3.0 MW × {DUTY:.3f} = {AVG:.1f} kW. The source is on for {100 * DUTY:.1f}% of the time.", lvl="Moderate"),

    # ---- 6-10: electron beam path
    PR(STEM(ask="Why is a standing-wave guide shorter than a travelling-wave guide of the same energy?"), "Its coupling cells, which carry almost no field, sit off the beam axis",
       ["It runs at a higher microwave frequency, so each cell is shorter", "Its electrons are injected at a higher energy, so fewer cells are needed", "It has no bunching cells, so acceleration starts in the first cell"],
       "In the usual standing-wave mode every second cell carries almost no field, and a side-coupled guide moves those cells off the beam axis, so the electrons cross only accelerating cells. Both designs run in the S band, both inject the electrons with tens of keV, and both bunch them in their first cells.", lvl="Moderate"),
    PR(STEM(ask="Why do many linacs bend the beam through 270° rather than 90°?"), "It focuses electrons of slightly different energies onto one spot",
       ["It raises the energy of the electrons while it bends them", "It needs a weaker field than a 90° bend of the same radius", "It makes a flattening filter unnecessary in photon mode"],
       "The radius of each path grows with the momentum, so a 90° bend spreads electrons of different energies across the target and enlarges the focal spot; the 270° design brings them back together. A magnetic force does no work, so it adds no energy, and the field depends on the momentum and the radius, not on the angle of the bend.", lvl="Moderate"),
    PRN(STEM("A standing-wave guide raises electrons to 6 MeV over 30 cm (illustrative).", [], "At the same energy gain per metre, what [[length]] is needed for 15 MeV?"), L15, [L15_inv, L15_ratio, 2 * L15], "{:.2f} m",
        f"The gain is 6 MeV ÷ 0.30 m = {G2:.0f} MeV/m, so 15 MeV needs 15 ÷ {G2:.0f} = {L15:.2f} m. Inverting the ratio of the energies gives {L15_inv:.2f} m, and reading the ratio 15/6 as a length gives {L15_ratio:.2f} m.", lvl="Moderate"),
    PRN(STEM("Electrons are bent in the magnet of a linac.", ["kinetic energy T = 12 MeV", "radius of the path r = 8.0 cm", "m<sub>e</sub>c² = 0.511 MeV"], "What [[magnetic field]] holds them on this path?"), BF12, [BNR12, BF12 / 2, BF12 / 100], "{:.3g} T",
        f"pc = √(12² + 2 × 12 × 0.511) = {PC12:.2f} MeV, and B = pc / (299.8 r) = {PC12:.2f} ÷ (299.8 × 0.080) = {BF12:.3f} T. The non-relativistic momentum, √(2 m<sub>e</sub>c² T) = {PNR12:.2f} MeV, gives {BNR12:.3f} T, far too low for a 12 MeV electron.", lvl="Moderate"),
    PRN(STEM("A bending magnet holds electrons on a fixed path. The machine changes from a 6 MeV to a 20 MeV electron beam.", ["m<sub>e</sub>c² = 0.511 MeV"], "By what [[factor]] must the magnetic field rise?"), RAT20, [20 / 6, math.sqrt(20 / 6), 1 / RAT20], "{:.2f}",
        f"On a fixed radius B is proportional to p. pc = √(T² + 2T m<sub>e</sub>c²) is {PC6:.2f} MeV at 6 MeV and {PC20:.2f} MeV at 20 MeV, a ratio of {RAT20:.2f}. The ratio of the kinetic energies, {20 / 6:.2f}, ignores the rest energy, and its square root, {math.sqrt(20 / 6):.2f}, uses the non-relativistic momentum.", lvl="Challenging"),

    # ---- 11-15: treatment head
    PRN(STEM("Electrons of 6 MeV strike the target of a linac.", [], "About what [[mean photon energy]] does the x-ray beam have?"), M6, [6.0, 3.0, 1.0], "{:.1f} MeV",
        f"The bremsstrahlung spectrum runs from zero up to the electron kinetic energy, 6 MeV, and its mean is about one third of that, {M6:.0f} MeV. Few photons reach the maximum, and half of it overestimates the mean.", lvl="Easy"),
    PR(STEM("A linac is switched from photon mode to electron mode.", [], "Why is the flattening filter moved out of the beam?"), "It would stop most of the electrons that cross it near the axis",
       ["It would focus the electrons into a narrow pencil on the axis", "It would make the monitor chambers read the electrons as photons", "It would raise the energy of the electrons that pass through it"],
       "The filter is thickest on the axis, beyond the range of the electrons there, so it would leave a weak mix of bremsstrahlung and slowed electrons. A thin scattering foil spreads the beam instead. Metal in the beam cannot add energy, and it spreads the electrons rather than focusing them.", lvl="Moderate"),
    PRM("A linac changes from a photon beam to an electron beam. Which of these changes are made?", ["The target moves out of the beam", "A scattering foil replaces the flattening filter", "The electron beam current is lowered"],
        ["The electron beam current is raised", "The monitor chambers move out of the beam", "The bending magnet is switched off"],
        "Photon mode needs an electron current of the order of 100 times higher, because most of the electron energy becomes heat in the target, so the current is lowered once the target is out; the photon-mode current would overdose by about that factor. The monitor chambers stay in the beam to measure the electron dose, and the bending magnet still turns the beam and selects its energy.", lvl="Moderate"),
    PR(STEM("The flattening filter is removed from a 6 MV beam, and the electron energy is left unchanged.", [], "How does the beam quality specifier, TPR<sub>20,10</sub> or %dd(10)<sub>x</sub>, change?"), "It falls, because the filter no longer hardens the beam",
       ["It rises, because the dose rate on the axis is higher", "It stays the same, because the electron energy is unchanged", "It rises, because there is less head scatter"],
       "The filter removes more low-energy photons than high-energy ones, so without it the spectrum is softer and the depth dose falls faster: in one study TPR<sub>20,10</sub> was 0.629 without the filter and 0.665 with it. The dose rate does not change a ratio of doses, and a design that keeps the depth dose of the flattened beam must raise the electron energy.", lvl="Moderate"),
    PR(STEM("Monthly profiles of a 6 MV beam show the off-axis dose about 3% above baseline on both sides, with the symmetry unchanged. The PDD at 10 cm depth has fallen slightly.", [], "What is the most likely cause?"), "The energy of the electrons striking the target has fallen",
       ["The electron beam strikes the target off-centre", "A sealed monitor chamber has started to leak", "The flattening filter has moved out of the beam"],
       "At a lower energy the bremsstrahlung is less sharply peaked forward, so the filter over-corrects and the off-axis dose rises on both sides, while the PDD falls a little; off-axis ratios respond more than the PDD to an energy change. A steering fault makes the profile asymmetric, a leaking chamber changes the output rather than the shape, and without the filter the profile would peak on the axis.", lvl="Challenging"),

    # ---- 16-21: collimation and dose monitoring, and the whole machine (practice set)
    PR(STEM("One jaw of a linac is closed to the central axis as a half-beam block.", [], "What does it give at that edge of the field?"), "An edge that does not diverge",
       ["An edge with no penumbra", "A wedged dose across the field", "An edge that diverges twice as fast"],
       "The central ray meets the isocenter plane at a right angle, so an edge along it does not spread with depth, and an adjacent field can be matched along it without overlap. The penumbra is still present, and no wedge is formed.", lvl="Easy"),
    PRM("The primary dose channel of a linac fails during a treatment. Which of these can still stop the beam?", ["The secondary dose channel", "The backup timer"],
        ["The automatic frequency control", "The circulator", "The energy slits"],
        "The secondary channel of the monitor chambers stops the beam a small margin above the set MU, and the timer stops it after a set time if both channels fail. The AFC tunes the RF source, the circulator protects it, and the slits select the electron energy; none of them counts dose.", lvl="Moderate"),
    PR(STEM("A crossplane profile of a 6 MV beam is 4% higher on one side than on the other. The output and the PDD on the axis are unchanged.", [], "Which fault is most likely?"), "The electron beam strikes the target off-centre or at an angle",
       ["The energy of the electrons striking the target has fallen", "A sealed monitor chamber has started to exchange air with the room", "The automatic frequency control has drifted off the guide frequency"],
       "A steering error tilts the forward-peaked x-ray beam against the flattening filter, so one side of the profile is higher. The segmented monitor chamber senses it, and the servo corrects the steering coils or an interlock stops the beam. A lower energy changes both sides alike, a leaking chamber changes the output, and a drifting AFC lowers the dose rate.", lvl="Challenging"),
    PR(STEM("The daily output of a linac varies by up to 2% from day to day. The changes follow the room temperature and pressure, although the field chamber is corrected for both.", [], "Which fault is the most likely?"), "A sealed monitor chamber has started to exchange air with the room",
       ["The current of the bending magnet has drifted from its setting", "The flattening filter has shifted off the central axis", "The magnetron is near the end of its working life"],
       "A sealed monitor chamber reads the same at any air density. Once it leaks, its reading per unit dose follows temperature and pressure, and because the beam stops at a set reading, the dose per MU follows them too. The other faults would change the energy, the profile, or the dose rate, not in step with temperature and pressure.", lvl="Challenging"),
    PRN(STEM("A 10 MV FFF beam runs at its highest dose rate (illustrative values).", ["dose rate = 2400 MU/min", "1 MU = 1 cGy at the reference point", "pulse repetition rate = 360 per second"], "What is the [[dose per pulse]] at the reference point?"), 10 * DP2400, [10 * 2400 / 360, 10 * 2400 / 60, DP2400], "{:.3g} mGy",
        f"2400 cGy/min ÷ 60 = {2400 / 60:.0f} cGy/s, and ÷ 360 pulses/s = {DP2400:.4f} cGy = {10 * DP2400:.2f} mGy per pulse. Leaving out the 60 s per minute gives {10 * 2400 / 360:.1f} mGy, leaving out the pulse rate gives {10 * 2400 / 60:.0f} mGy, and stopping at cGy gives {DP2400:.3f}.", lvl="Challenging"),
    SORT("Rank these parts of a linac in photon mode in the order the beam passes through them.", ["1st", "2nd", "3rd", "4th", "5th", "6th"],
         [("Electron gun", 0), ("Accelerating guide", 1), ("Bending magnet", 2), ("Target", 3), ("Flattening filter", 4), ("Monitor chambers", 5)],
         "The gun injects electrons into the guide, and the bending magnet turns them onto the target. The x-rays from the target pass the primary collimator and the flattening filter, and then the monitor chambers, which measure the final beam ahead of the jaws.", lvl="Easy", mode="rank", cap=1),
]

INLINE = {0: [1, 2, 3, 4, 5], 1: [6, 7, 8, 9, 10], 2: [11, 12, 13, 14, 15]}     # questions on the last section, and the ranking, form the practice set

TERMS = ["pulse-forming network", "magnetron", "klystron", "circulator", "automatic frequency control", "scattering foil", "half-beam block", "monitor chambers"]

TAKE = [
    ["A thyratron discharges the pulse-forming network, sending pulses of a few microseconds, a few hundred times per second, to the RF source and the gun.",
     "Magnetron: an oscillator, about 2 to 5 MW peak. Klystron: an amplifier of a low-power RF driver, about 5 to 7 MW peak.",
     f"S band is near 3 GHz, a wavelength of about {LAM:.0f} cm. The circulator diverts reflected power from the source, and the AFC keeps the source tuned to the guide."],
    ["A standing-wave guide is shorter for the same energy because its coupling cells, which carry almost no field, sit off the axis. Gains are about 12 to 20 MeV/m.",
     "A 270° achromatic magnet returns electrons of slightly different energies to one spot on the target; slits remove those outside a narrow window.",
     "On a fixed path the field follows the momentum: B [T] = pc [MeV] / (299.8 r [m])."],
    ["Transmission target of tungsten: the maximum photon energy equals the electron kinetic energy, and the mean is about one third of it.",
     "Electron mode: target out, scattering foils in place of the flattening filter, and an electron current of the order of 100 times lower.",
     "At the same electron energy an FFF beam is softer, with less leakage per MU and more dose per pulse."],
    ["Jaws are the secondary collimators; a jaw closed to the central axis gives an edge that does not diverge. The lamp sits at the mirror image of the target.",
     "Two independent monitor chambers: the primary stops the beam at the set MU, the secondary a small margin later, then a timer. A leaking sealed chamber follows air temperature and pressure.",
     "Segmented electrodes feed the steering servo; a steering fault makes the profile asymmetric."],
]
