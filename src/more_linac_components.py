"""Explain further text for the questions of the linac components chapter (linac-components). Entries are registered with q() from more_content."""
import math
from more_content import q
from blocks import sci
import linac_components as X   # the chapter's constants, so that the numbers in an explanation match the chapter

T = "linac-components"
H = "How to decide"
ME = X.calc.ME                  # electron rest energy (MeV), as the chapter computes with it
PB = 299.792458                 # B [T] = pc [MeV] / (299.8 r [m])

# ---- 1-5: layout and RF power
q(T, "Which statement about the klystron of a linac is correct?",
  simple="A linac uses one of two microwave sources. A magnetron makes microwaves by itself, while a klystron makes none of its own: it takes a weak signal from an RF driver and gives it out again at a peak power of several megawatts. The power comes from the klystron's own electron beam, which the weak signal gathers into bunches that then give up their energy as microwaves in an output cavity.",
  steps=["Oscillator or amplifier: a magnetron oscillates on its own; a klystron amplifies, so it is the source that needs a driver.",
         "Accelerating the treatment electrons: done in the accelerating guide, which the microwaves from either source feed.",
         "Diverting reflected power: done by the circulator in the waveguide, which sends that power into a load."], how=H)
q(T, "A magnetron linac warms up over the first hour of treatment.",
  simple="The accelerating guide is a chain of copper cells, and each cell resonates at a frequency set by its size. As the copper warms it expands, its resonant frequency falls slightly, and a source left at its starting frequency would pass less of its power to the electrons. The AFC detects the frequency error and retunes the magnetron to follow the guide.",
  steps=["The problem is a drift in frequency, so the answer is the part that controls the frequency of the source: the automatic frequency control.",
         "Circulator: passes power forward to the guide and sends reflected power into a load. It protects the source but does not tune it.",
         "Pulse-forming network and thyratron: the network stores the energy of each pulse and the thyratron discharges it. Together they set when the source fires and how much power each pulse carries, not the frequency."], how=H)
q(T, "Match each part of a linac to its function.",
  simple="Each part does one job at one place along the machine: the modulator makes the pulses, the RF system carries the microwaves, the beam line selects the electrons, and the head measures the beam. Where a part sits along that chain points to its function.",
  steps=["Thyratron: a hydrogen-filled switch in the modulator. When it is triggered, the pulse-forming network discharges and a pulse of a few microseconds goes to the RF source and the gun.",
         "Circulator: sits between the source and the guide. Forward power passes to the guide, and power coming back is steered into a load before it reaches the source.",
         "SF<sub>6</sub>: an insulating gas under pressure in the waveguide. At megawatt peak powers the field in the waveguide can exceed what air withstands, and a spark would follow; the gas withstands a higher field.",
         "Energy slits: in the bending magnet, where electrons of different momenta follow arcs of different radius. Slits there block the electrons outside the window, for example ±3%.",
         "Segmented monitor chamber: its electrode is divided, so opposite halves of the beam give separate signals. Their difference drives the steering servo."], how=H)
q(T, "A linac runs at an S-band frequency.",
  simple="Microwaves are electromagnetic waves, so they travel at the speed of light, and one wavelength is the distance the wave covers in one cycle: the speed divided by the frequency. S-band frequencies near 3 GHz give wavelengths near 10 cm.",
  steps=["Write the frequency in hertz: 2856 MHz = 2.856 × 10<sup>9</sup> Hz.",
         f"λ = c / f = 2.998 × 10<sup>8</sup> m/s ÷ 2.856 × 10<sup>9</sup> s<sup>−1</sup> = {X.LAM_T / 100:.4f} m.",
         f"Convert to centimetres: {X.LAM_T / 100:.4f} m × 100 = {X.LAM_T:.1f} cm."],
  tip=f"Leaving the frequency in MHz gives 2.998 × 10<sup>8</sup> ÷ 2856 = {sci(2.998e8 / 2856, 3)} m, a million times too long.", check=X.LAM_T)
q(T, "A magnetron is pulsed by the modulator.",
  simple="The magnetron gives its 3.0 MW only while a pulse lasts and nothing between pulses. Averaged over a second, the power is the peak power times the fraction of the time the source is on, the duty cycle, which here is one part in a thousand.",
  steps=[f"Duty cycle = pulse length × repetition rate = 4.0 × 10<sup>−6</sup> s × 250 s<sup>−1</sup> = {X.DUTY:.3f}.",
         f"Average power = 3.0 MW × {X.DUTY:.3f} = {X.AVG / 1000:.4f} MW = {X.AVG:.1f} kW.",
         f"The same result from the energy of a pulse: 3.0 × 10<sup>6</sup> W × 4.0 × 10<sup>−6</sup> s = {3.0e6 * 4.0e-6:.0f} J per pulse, and 250 pulses per second give {3.0e6 * 4.0e-6 * 250:,.0f} J/s = {3.0e6 * 4.0e-6 * 250 / 1000:.1f} kW."],
  tip=f"Quoting the peak power, 3.0 MW, as the average overstates it by 1 / duty cycle = {1 / X.DUTY:,.0f} times.", check=X.AVG)

# ---- 6-10: electron beam path
q(T, "Why is a standing-wave guide shorter than a travelling-wave guide",
  simple="In a standing-wave guide the wave reflects back and forth between the ends, and in the usual operating mode, the π/2 mode, the cells alternate between a strong field and almost none. On the axis the empty cells would add length without adding energy, so the side-coupled design moves them off to the side, where they still carry power from one accelerating cell to the next.",
  steps=["Length = energy ÷ gain per metre, so a shorter guide for the same energy means a higher gain per metre.",
         "Side-coupled standing-wave guide: every cell the electrons cross accelerates them, giving about 12 to 20 MeV/m.",
         "Frequency: both designs run in the S band, near 3 GHz, so frequency does not separate them.",
         "Injection and bunching: both receive electrons of tens of keV from the gun and bunch them in their first cells."], how=H)
q(T, "Why do many linacs bend the beam through 270°",
  simple="The electrons leaving the guide have a small spread of energies, and in a magnetic field an electron with more momentum follows a wider arc. After a 90° bend the arcs end at different points, so the spot where the beam meets the target is smeared out by energy. A 270° achromatic magnet is shaped so that the wider and narrower arcs end at one point and in one direction, which keeps the focal spot small.",
  steps=["Achromatic means independent of energy: within the window that the slits pass, electrons of every momentum leave the magnet at one point and in one direction.",
         "Energy: a magnetic force is always at right angles to the motion, so it turns the electrons without speeding them up.",
         "Field strength: B = p / (e r) depends on the momentum and the radius of the path; the angle of the bend does not enter.",
         "Flattening filter: still needed, because the x-rays leaving the target are peaked forward whatever the bend."], how=H)
q(T, "A standing-wave guide raises electrons to 6 MeV over 30 cm",
  simple="Each metre of the guide adds the same energy, so the energy gained is proportional to the length; the injection energy, tens of keV, is too small to matter. Reaching 15 MeV, two and a half times 6 MeV, takes two and a half times the 30 cm.",
  steps=[f"Gain = energy ÷ length = 6 MeV ÷ 0.30 m = {X.G2:.0f} MeV/m, at the top of the range of about 12 to 20 MeV/m.",
         f"Length = 15 MeV ÷ {X.G2:.0f} MeV/m = {X.L15:.2f} m.",
         f"Check by proportion: 0.30 m × 15/6 = 0.30 × {15 / 6:.1f} = {0.30 * 15 / 6:.2f} m."],
  tip=f"Scaling by 6/15 instead of 15/6 gives {X.L15_inv:.2f} m, shorter than the 30 cm that reaches only 6 MeV.", check=X.L15)
q(T, "Electrons are bent in the magnet of a linac.",
  simple=f"The magnet holds the electrons on a circle of radius p / (eB), so the field needed grows with the momentum and falls with the radius. The kinetic energy of a 12 MeV electron is {12 / ME:.0f} times its rest energy, so the momentum must come from the relativistic formula, and pc comes out close to the total energy, {12 + ME:.1f} MeV.",
  steps=[f"Momentum: pc = √(T² + 2T m<sub>e</sub>c²) = √(12² + 2 × 12 × 0.511) = √{144 + 24 * ME:.2f} = {X.PC12:.2f} MeV.",
         f"Field times radius: p / e in tesla metres = pc [MeV] ÷ 299.8 = {X.PC12:.2f} ÷ 299.8 = {X.PC12 / PB:.4f} T·m.",
         f"Divide by the radius in metres, 8.0 cm = 0.080 m: B = {X.PC12 / PB:.4f} ÷ 0.080 = {X.BF12:.3f} T."],
  tip=f"Leaving the radius in centimetres, 8.0 in place of 0.080, gives a field a hundred times too small, {X.BF12 / 100:.5f} T.", check=X.BF12)
q(T, "A bending magnet holds electrons on a fixed path.",
  simple=f"On a fixed path the field must rise in step with the momentum. At these energies pc is close to the kinetic energy plus about 0.5 MeV ({X.PC6:.2f} MeV at 6 MeV and {X.PC20:.2f} MeV at 20 MeV), and adding about the same amount to both energies makes their ratio a little smaller than 20/6.",
  steps=["On a fixed radius B = p / (e r), so the ratio of the fields is the ratio of the momenta.",
         f"At 6 MeV: pc = √(6² + 2 × 6 × 0.511) = √{36 + 12 * ME:.2f} = {X.PC6:.2f} MeV.",
         f"At 20 MeV: pc = √(20² + 2 × 20 × 0.511) = √{400 + 40 * ME:.2f} = {X.PC20:.2f} MeV.",
         f"Ratio = {X.PC20:.2f} ÷ {X.PC6:.2f} = {X.RAT20:.2f}."],
  tip=f"The ratio of the kinetic energies, {20 / 6:.2f}, leaves out the rest energy. Dividing the other way, {1 / X.RAT20:.2f}, would mean a weaker field for faster electrons.", check=X.RAT20)

# ---- 11-15: treatment head
q(T, "Electrons of 6 MeV strike the target of a linac.",
  simple="An electron slowing in the target can give any part of its kinetic energy to a bremsstrahlung photon, from almost nothing up to all of it, so the beam is a continuous spectrum that ends at 6 MeV. Most photons carry much less than the maximum, and the mean is about a third of it. For this reason an x-ray beam is named by its accelerating potential, 6 MV, rather than by a photon energy.",
  steps=["Maximum photon energy = electron kinetic energy = 6 MeV, reached only when one photon takes all of an electron's energy.",
         f"Mean photon energy ≈ maximum ÷ 3 = 6 ÷ 3 = {X.M6:.1f} MeV."],
  tip="Reading the beam name, 6 MV, as the photon energy gives 6.0 MeV, which is the end point of the spectrum, not its mean.", check=X.M6)
q(T, "A linac is switched from photon mode to electron mode.",
  simple="Photons and electrons are stopped in different ways. A metal cone removes a fraction of the photons that depends on its thickness at each point, which is how it flattens a photon beam, but electrons lose energy steadily and stop after a definite thickness, their range. The electron beam reaches the head as a narrow pencil on the axis, where the filter is thickest, so almost all of it would be stopped there.",
  steps=["Photon mode: the cone attenuates the forward peak of the x-ray beam, more at the centre than at the edge.",
         "Electron mode: the centre of the cone is thicker than the electron range, so the beam would be absorbed, leaving bremsstrahlung and a few slowed electrons.",
         "A scattering foil is thin compared with the range: it spreads the electrons sideways while they keep most of their energy.",
         "Metal cannot add energy to electrons, and scattering in it spreads a beam rather than focusing it."], how=H)
q(T, "A linac changes from a photon beam to an electron beam.",
  simple="The change takes out the parts that turn the electrons into a flat x-ray beam and puts in parts that spread the electron beam itself. The parts that steer, select, and measure the beam stay where they are, and the beam current is turned down, because electrons used directly give far more dose per electron than the x-rays made from them.",
  steps=["Target: moved out, because the electrons themselves now form the treatment beam.",
         "Flattening filter: replaced by scattering foils, which spread the narrow electron beam over the field.",
         "Beam current: lowered by a factor of about 100 to 1000. In photon mode most of the electron energy becomes heat in the target, so a much larger current is needed for the same dose rate.",
         "Monitor chambers: stay in the beam, because they measure the dose and end the treatment at the set MU.",
         "Bending magnet: stays on, because it still turns the beam toward the patient and selects its energy."], how=H)
q(T, "The flattening filter is removed from a 6 MV beam",
  simple="In a 6 MV beam the flattening filter removes low-energy photons more readily than high-energy ones, so the beam that leaves it is harder. Without the filter more low-energy photons reach the patient, the dose falls off faster with depth, and both beam quality specifiers, TPR<sub>20,10</sub> and %dd(10)<sub>x</sub>, fall.",
  steps=["TPR<sub>20,10</sub> is the dose at 20 cm depth divided by the dose at 10 cm, at a fixed distance from the source. A more penetrating beam gives a larger ratio.",
         "Filter removed: the photons it used to absorb, mostly low-energy ones, now reach the phantom, so the ratio falls.",
         "Dose rate: a ratio of two doses from the same beam does not depend on how fast the dose is given.",
         "Head scatter: it does fall without the filter, but the loss of filtration outweighs it, and the measured specifier falls.",
         "Unchanged electron energy: the maximum photon energy stays the same, but the shape of the spectrum below it changes."], how=H)
q(T, "Monthly profiles of a 6 MV beam show the off-axis dose",
  simple="The flattening filter is matched to one energy: its cone cuts the forward peak of the x-rays by the amount that makes the profile flat at that energy. Electrons of lower energy make x-rays that are less sharply peaked forward, so the same cone now removes too much at the centre compared with the edges, and the off-axis dose rises equally on both sides, a pattern called horns. The softer beam also penetrates less, which accounts for the small fall in the PDD.",
  steps=["Both sides changed alike, with the symmetry unchanged: the shape of the forward peak has changed, which points to the energy, not the steering.",
         "PDD at 10 cm lower: the beam is softer, which confirms a lower energy.",
         "Off-centre electrons: the peak tilts, so one side rises and the other falls.",
         "A leaking sealed monitor chamber: the dose per MU changes, but the shape of the profile does not.",
         "Filter out of the beam: the profile would peak on the axis, with the off-axis dose far below the central dose."], how=H)

# ---- 16-21: collimation and dose monitoring, and the whole machine
q(T, "One jaw of a linac is closed to the central axis",
  simple="Every field edge lies along a ray from the source, and away from the axis those rays slope outward, so an ordinary edge spreads with depth. The central ray is the only ray perpendicular to the isocenter plane, so a field edge along it does not slope with depth. A neighbouring field with its edge on the same plane meets it at every depth without overlap or gap, for example where tangential breast fields meet a supraclavicular field.",
  steps=["Ordinary edge: follows the diverging ray through the edge of the jaw, so the field widens with depth.",
         "Half-beam block: the edge ray is the central ray, perpendicular to the isocenter plane, so the edge does not diverge.",
         "Penumbra: still present, from the size of the source, transmission through the edge of the jaw, and scatter.",
         "Wedged dose: needs a wedge filter or a moving jaw; a jaw parked at the axis blocks half of the field and leaves the other half unchanged."], how=H)
q(T, "The primary dose channel of a linac fails",
  simple="Beam termination is built in layers that do not depend on each other, so one failure cannot leave the beam running. The secondary channel measures the same beam with its own chamber and electronics and stops it a small margin above the set MU, and the backup timer stops it after a set time if both dose channels fail. The other parts listed handle the microwaves or the electron energy and have no measure of the dose.",
  steps=["Rule: only a part that measures dose or time can end the treatment when the primary channel does not.",
         "Secondary dose channel: measures dose, independently of the primary. It can stop the beam.",
         "Backup timer: measures time. It can stop the beam.",
         "Circulator: protects the RF source from reflected power. AFC: keeps the source tuned to the guide. Energy slits: select the electron energy. None of them measures dose or time."], how=H)
q(T, "A crossplane profile of a 6 MV beam is 4% higher on one side",
  simple="The x-rays from the target are peaked in the direction the electrons were travelling. If the electrons strike off-centre or at an angle, the peak no longer lines up with the cone of the flattening filter, so one side of the field gets more dose than the other. The energy and the number of electrons are unchanged, so the output and the PDD on the axis stay the same.",
  steps=["One side higher than the other: the position or direction of the beam on the target has changed, which is a steering fault.",
         "Both sides changed alike, with a lower PDD: a fall in energy.",
         "Output following temperature and pressure, with the profile unchanged: a leaking sealed monitor chamber.",
         "Lower dose rate: a drifting AFC, which feeds the guide less efficiently.",
         "The segmented monitor chamber senses this pattern by comparing opposite halves of the beam, and the servo or an interlock acts on it."], how=H)
q(T, "The daily output of a linac varies by up to 2%",
  simple="The linac stops the beam when its monitor chamber has collected a set charge. A sealed chamber holds a fixed mass of gas, so its charge per unit dose does not change with the weather, but once it leaks, the mass of air inside follows the room temperature and pressure. On a warm or low-pressure day the air in it is thinner, each unit of dose gives less charge, and more dose is delivered before the set count is reached.",
  steps=["The field chamber is corrected for temperature and pressure, so the variation is in the dose the linac gives per MU.",
         "Of the parts listed, only an ion chamber open to the air responds to the air density, which temperature and pressure set together: its reading is proportional to the mass of air it holds.",
         f"Output per MU ∝ 1 / (air density in the monitor chamber) ∝ T / P. A fall in pressure from 101.3 to 99.3 kPa raises the output per MU by {100 * (101.3 / 99.3 - 1):.1f}%.",
         "Bending magnet current: changes the energy or the steering. Filter shift: changes the profile. Ageing magnetron: changes the dose rate. None of them follows the weather."], how=H)
q(T, "A 10 MV FFF beam runs at its highest dose rate",
  simple="The beam is delivered in short pulses with nothing between them, and the dose rate in MU per minute is an average over many pulses. Dividing the dose given in one second by the number of pulses in that second gives the dose in each pulse. At a fixed pulse rate a higher dose rate means more dose in every pulse, which is why FFF beams have a high dose per pulse.",
  steps=[f"Dose per second: 2400 cGy/min ÷ 60 s/min = {2400 / 60:.0f} cGy/s.",
         f"Dose per pulse: {2400 / 60:.0f} cGy/s ÷ 360 pulses/s = {X.DP2400:.4f} cGy.",
         f"In milligray, with 1 cGy = 10 mGy: {X.DP2400:.4f} × 10 = {10 * X.DP2400:.2f} mGy.",
         f"Check per minute: 360 × 60 = {360 * 60:,} pulses, and 2400 cGy ÷ {360 * 60:,} = {2400 / (360 * 60):.4f} cGy.",
         f"For comparison, 600 MU/min at the same pulse rate gives {10 * X.DP600:.2f} mGy per pulse, a quarter as much."],
  tip=f"Stopping at {X.DP2400:.3f}, which is in cGy, and reading it as mGy gives a value ten times too small.", check=10 * X.DP2400)
q(T, "Rank these parts of a linac in photon mode",
  simple="Follow the beam from start to finish: electrons are made, accelerated, turned toward the patient, and stopped in the target, and the x-rays they make are then flattened and measured before the jaws shape the field.",
  steps=["Electron gun: a heated cathode releases electrons, which enter the guide with tens of keV.",
         "Accelerating guide: microwaves raise the electrons to the treatment energy.",
         "Bending magnet: turns the beam toward the patient and selects its energy.",
         "Target: the electrons give up their energy, part of it as bremsstrahlung x-rays peaked forward.",
         "Flattening filter: below the primary collimator, it evens out the forward peak.",
         "Monitor chambers: measure the flattened beam, before the jaws and the MLC define the field."], how=H)
