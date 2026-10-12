"""Explain further text for the questions of the kV x-ray production chapter (xray-tube). Entries are registered with q() from more_content."""
import math
from more_content import q
import xray_tube as X          # the chapter's constants, so that the numbers in an explanation match the chapter

T = "xray-tube"
H_ = "How to decide"
sind, tand = (lambda d: math.sin(math.radians(d))), (lambda d: math.tan(math.radians(d)))

# ---- production
q(T, "An x-ray tube runs at a set kVp, mA, and filtration.",
  simple="The highest photon energy in the beam is a ceiling set by the fastest electrons. At the peak of the voltage an electron reaches the anode with an energy in keV equal to the kVp, and a photon cannot carry more energy than the electron that made it, so no other setting can move the ceiling.",
  steps=["Rule: E<sub>max</sub> (keV) = kVp. Only a setting that changes the energy of each electron can change it.",
         "Peak tube voltage: sets the electron energy, so it sets E<sub>max</sub>.",
         "Atomic number of the anode: changes how many photons are made and where the characteristic lines lie, not the ceiling.",
         "Tube current: changes how many electrons arrive each second, not the energy of each one.",
         "Added filtration: removes mostly low-energy photons and adds energy to none, so the end of the spectrum stays at the kVp."],
  tip="Filtration raises the mean energy and the HVL, which is easy to mistake for a rise in the maximum energy. The end point of the spectrum does not move.",
  how=H_)
q(T, "Electrons strike a thick tungsten target, and no filtration is in the beam.",
  simple="The question asks for the shape of the raw spectrum, drawn as energy fluence per unit energy. The electrons slow down gradually inside the target, and each thin layer they cross adds a flat strip of the same height, which ends at the energy the electrons still have in that layer. The deeper the layer, the shorter its strip, so the strips pile up into a triangle that is highest at zero energy and falls in a straight line to zero at E<sub>max</sub>.",
  steps=["A thin layer gives a flat spectrum: the same energy fluence per unit energy from zero up to the energy of the electrons in that layer.",
         "Deeper layers see slower electrons, so their flat spectra end at lower energies.",
         "At an energy E, only the layers where the electrons still have more than E contribute. Their number is proportional to E<sub>max</sub> − E, which gives the triangle I(E) ∝ Z (E<sub>max</sub> − E).",
         "Against the options: a rising line reverses the slope, a flat line is a single thin layer, and a hump is the spectrum after filtration."],
  tip="The hump that peaks near one third of E<sub>max</sub> is the shape of most textbook spectra, because those show a filtered beam. The filter removes the low-energy part of the triangle.",
  how=H_)
q(T, "A diagnostic tube runs at 80 kVp.",
  simple="The shortest wavelength belongs to the most energetic photon, and at 80 kVp that photon has 80 keV. Energy and wavelength are inversely related, λ = hc / E, so the largest energy gives the smallest wavelength.",
  steps=["E<sub>max</sub> = 80 keV, the kVp read in keV.",
         f"λ<sub>min</sub> = hc / E<sub>max</sub> = {X.HC} keV nm / 80 keV = {X.q_lam:.4f} nm.",
         "Units: keV nm divided by keV leaves nm.",
         f"In picometres: {X.q_lam:.4f} nm × 1000 = {1000 * X.q_lam:.1f} pm."],
  tip=f"Multiplying in place of dividing gives {X.HC * 80:.1f} nm, an ultraviolet wavelength, far too long for an x-ray. {10 * X.q_lam:.3f} nm has the right digits with the decimal point one place off: 1.24 / 80 is about 0.015, not 0.15.",
  check=X.q_lam)
q(T, "The tungsten anode of a tube operated at 100 kVp is replaced by a molybdenum anode.",
  simple=f"Changing the target changes two separate things. The characteristic lines are set by how tightly the target holds its inner electrons, and molybdenum holds its K electrons with 20.0 keV against 69.5 keV for tungsten, so its lines lie much lower. The bremsstrahlung yield rises with the charge of the nucleus, and Z falls from {X.Z_W} to {X.Z_MO}, so the continuum is weaker.",
  steps=["Lines: each is a difference of two binding energies of the target. Molybdenum Kα is 17.5 keV, against 58.0 and 59.3 keV for tungsten Kα.",
         f"Bremsstrahlung: the efficiency is about k Z V, so at the same kVp and mA the output scales with Z: {X.Z_MO} / {X.Z_W} = {X.Z_MO / X.Z_W:.2f}, a fall of {100 * (1 - X.Z_MO / X.Z_W):.0f}%.",
         "Maximum energy: eV, set by the voltage alone, so it stays at the kVp.",
         "Lower lines and a lower output together match one option only."],
  tip="The K-shell energy of molybdenum decides whether its K lines appear (the kVp must exceed 20.0 kV), not where the continuum ends: the continuum still reaches the kVp.",
  how=H_)
e5, P5 = X.eff(X.Z_W, 200e3), 200e3 * 20e-3
q(T, "An orthovoltage tube with a tungsten anode runs at constant potential.",
  simple="Only the fraction k Z V of the power carried by the electron beam comes out as x-rays; the rest heats the anode. At constant potential the voltage stays at 200 kV throughout the exposure, so the beam power is V × I with no waveform factor, and the x-ray power is that fraction of it.",
  steps=["Write V in volts and I in amperes: 200 kV = 2.0 × 10<sup>5</sup> V and 20 mA = 0.020 A.",
         f"Efficiency = 9 × 10<sup>−10</sup> × {X.Z_W} × 2.0 × 10<sup>5</sup> = {e5:.5f}, or {100 * e5:.2f}%.",
         f"Beam power = 2.0 × 10<sup>5</sup> V × 0.020 A = {P5:,.0f} W.",
         f"X-ray power = {e5:.5f} × {P5:,.0f} W = {X.q_px:.2f} W.",
         f"The same from k Z I V²: 9 × 10<sup>−10</sup> × {X.Z_W} × 0.020 × (2.0 × 10<sup>5</sup>)² = {X.K_BR * X.Z_W * 0.020 * 2.0e5 ** 2:.2f} W."],
  tip=f"With V in kilovolts the efficiency is a thousand times too small, and the x-ray power comes out as {X.eff(X.Z_W, 200) * P5:.4f} W. With the current left in milliamperes the beam power is a thousand times too large, and it comes out as {e5 * 200e3 * 20:,.0f} W.",
  check=X.q_px)

# ---- the tube
q(T, "Most diagnostic tubes have a rotating anode.",
  simple="The electron beam always lands on the same small spot in space, but the disc turns beneath it, so each part of the track is heated for a moment once per turn and cools for the rest of the turn. The heat is spread over a ring many times longer than the spot, so a small spot can take a power that would melt a fixed target.",
  steps=["Rule: rotation changes where the heat goes. It leaves the geometry of the spot, the anode angle, and the physics of x-ray production as they were.",
         "Effective focal spot: actual length × sin θ, and rotation changes neither.",
         "Heel effect: set by the anode angle and the path of the photons through the anode, which rotation does not change.",
         "Efficiency: about k Z V, set by the target and the voltage.",
         "Heat: shared around the whole circular track, which is what the rotation is for."],
  tip="Rotation and the anode angle do different jobs: the angle makes the spot look small, and the rotation lets a small spot take a high power.",
  how=H_)
q(T, "Match each part of an x-ray tube to its purpose.",
  simple="The parts can be matched by following one electron through the tube: what releases it, what aims it, what it travels through, and what stops it, and then what copes with the high voltage and the heat around the tube. Each part does one of these jobs.",
  steps=["Filament: a tungsten coil heated by the filament current until electrons escape from its surface (thermionic emission). Its temperature sets the tube current.",
         "Focusing cup: a metal cup around the filament, at the cathode potential. Its field squeezes the electrons into a beam aimed at the focal spot.",
         "Rotating anode: the target turns, so the heat is spread around a circular track instead of one spot.",
         "Evacuated envelope: with no gas in the way, the electrons cross from cathode to anode without collisions.",
         "Oil bath: oil insulates the high-voltage parts from the earthed housing and carries the heat of the tube out to the housing."],
  tip="The focusing cup shapes the electron stream; it does not produce electrons. Emission comes from the filament alone.",
  how=H_)
q(T, "A tube has a small anode angle.",
  simple="The electrons strike a strip 6.0 mm long on the anode face, but the face is turned almost edge-on to the patient, so seen along the central ray the strip looks much shorter. That apparent length, the effective focal spot, is the actual length times sin θ, and it is what sets the geometric blur in the image.",
  steps=[f"sin 10° = {X.s10:.4f}.",
         f"Effective spot = 6.0 mm × {X.s10:.4f} = {X.q_spot:.2f} mm.",
         f"The heat still falls on the whole 6.0 mm strip, {6.0 / X.q_spot:.1f} times the effective length: a small spot in the image with a large area for the heat."],
  tip=f"For anode angles below 20°, sin θ is below {sind(20):.3f}, so the effective spot is always less than about a third of the actual length. Using cos θ gives {6.0 * X.cs10:.2f} mm and dividing by sin θ gives {6.0 / X.s10:.2f} mm; both fail this test.",
  check=X.q_spot)
q(T, "An exposure is made with a three-phase six-pulse generator.",
  simple=f"Heat units measure the heat an exposure puts into the anode, so that it can be compared with the tube's heat limits. The product kVp × mA × s counts it for a single-phase supply; a three-phase supply stays nearer its peak, so at the same settings it delivers more energy, and the factor {X.F_6P} adds that.",
  steps=[f"kVp × mA = 80 × 300 = {80 * 300:,}.",
         f"× time: {80 * 300:,} × 0.20 s = {80 * 300 * 0.20:,.0f}.",
         f"× waveform factor: {80 * 300 * 0.20:,.0f} × {X.F_6P} = {X.q_hu:,.0f} HU.",
         f"As energy, 1 HU ≈ 1/{X.F_12P} J = {1 / X.F_12P:.2f} J, so the anode takes about {X.q_hu / X.F_12P / 1000:.1f} kJ."],
  tip=f"The factor multiplies. A supply with less ripple puts more energy into the anode than single-phase at the same settings, so its heat units must exceed {X.q_hu0:,.0f}; dividing by {X.F_6P} gives {X.q_hudiv:,.0f} HU, less than single-phase, which cannot be right.",
  check=X.q_hu)
q(T, "A radiograph shows a heel effect across the field.",
  simple="The heel effect is the fall in intensity toward the anode side of the field. Photons are made a little below the anode surface, and those heading toward the anode side leave at a shallow angle to the face, so they cross more tungsten on the way out; anything that makes the rays in use run closer to the face strengthens the effect.",
  steps=["Rule: a ray that leaves toward the anode side at an angle φ from the central ray runs at only θ − φ to the anode face. The smaller θ − φ, the longer its path through tungsten and the weaker the ray.",
         "A smaller anode angle: θ − φ shrinks for every ray on that side. Stronger.",
         "A shorter source-to-image distance: the same receptor takes in rays at larger φ. Stronger.",
         "A longer distance or a smaller field: only rays close to the central ray are used. Weaker.",
         "A higher tube current: every ray grows in proportion, so the relative fall across the field stays the same. No change."],
  tip="A higher tube current makes the whole field brighter but leaves the ratio between the anode and cathode sides unchanged, and the heel effect is that ratio.",
  how=H_)
q(T, "A body part is radiographed with its long axis",
  simple="The beam is stronger under the cathode and weaker under the anode. Putting the thick 20 cm end under the stronger part and the thin 12 cm end under the weaker part lets each end send a similar signal to the receptor, so the image is more even from end to end.",
  steps=["Heel effect: the intensity falls from the cathode side to the anode side of the field.",
         "The 20 cm end attenuates more than the 12 cm end, so it needs more of the beam.",
         "Cathode over the 20 cm end: the strong part of the beam meets the thick end and the weak part meets the thin end, so the two differences offset each other.",
         "Cathode over the 12 cm end: the weak part of the beam meets the thick end, so the two differences add.",
         "The heel effect is not symmetric about the central ray, so the choice of end matters."],
  how=H_)
q(T, "A tube is replaced by one with a smaller anode angle",
  simple="All three changes come from one change of geometry: the anode face turns closer to the direction of the central ray. Seen along the central ray the focal strip then looks shorter, the face cuts off the beam closer to the central ray on the anode side, and the rays left on that side run closer to the face, through more tungsten.",
  steps=[f"Effective spot ∝ sin θ: sin 10° / sin 16° = {sind(10):.4f} / {sind(16):.4f} = {X.q_shrink:.2f}, so the spot is {100 * (1 - X.q_shrink):.0f}% smaller.",
         f"Field covered: rays more than θ from the central ray on the anode side run into the anode. At 100 cm from the focal spot the anode side reaches at most 100 × tan 16° = {100 * tand(16):.1f} cm from the central ray with the old tube and 100 × tan 10° = {100 * tand(10):.1f} cm with the new one.",
         "Heel effect: a ray at φ from the central ray toward the anode runs at θ − φ to the face, so a smaller θ lengthens the path through the anode of every such ray.",
         "Smaller spot, smaller field, stronger heel effect: one option has all three."],
  tip="The anode angle is a trade-off: no angle gives both a smaller spot and a larger field.",
  how=H_)

# ---- filtration, technique, and waveform
q(T, "Two generators make exposures at the same kVp and mAs",
  simple="The kVp is only the peak of the voltage. A single-phase supply reaches it twice per cycle and spends much of each cycle well below it, while a high-frequency supply stays close to the peak throughout. The same mAs sends the same charge across the tube, but with the high-frequency supply each electron arrives with more energy on average, so it makes more photons and harder ones.",
  steps=[f"Ripple: single-phase full-wave falls to zero between pulses ({100 * X.ripple(2):.0f}% ripple); a high-frequency generator is nearly constant.",
         "Output: the x-ray yield of an electron rises with its energy (efficiency ≈ k Z V), so a voltage that stays near the peak gives more output per mAs.",
         "Mean energy: less of the exposure is made at low voltage, where only soft photons can be made, so the mean energy rises.",
         "Maximum energy: set by the peak voltage, the same kVp in both, so it does not change."],
  tip="The maximum energy depends only on the peak voltage, so an option with a higher maximum energy cannot be right when the kVp is the same.",
  how=H_)
q(T, "The first HVL of an x-ray beam is measured before and after a change.",
  simple="The HVL measures how penetrating the photons are, which depends on the shape of the spectrum, not on the number of photons. Only a change that shifts the spectrum toward higher energies raises it: a higher kVp adds photons at the top, and copper removes photons at the bottom.",
  steps=["Rule: the HVL depends on the spectral shape, not on the number of photons.",
         "Raising the kVp: extends the spectrum upward and raises the mean energy. Raises the HVL.",
         "Adding copper: absorbs low-energy photons far more than high-energy ones (beam hardening). Raises the HVL.",
         "Raising the tube current or lengthening the time: more photons at every energy, in the same proportions. No change.",
         "Using the larger focal spot: changes the blur of the image, not the photon energies. No change."],
  tip="Doubling the mAs doubles the reading behind every thickness of absorber, so the thickness that halves it stays the same.",
  how=H_)
t15 = 0.20 * X.RHO_AL
q(T, "An extra 2 mm of aluminium is placed in a 100 kVp beam.",
  simple="A filter can only take photons away, so the output falls. It takes the low-energy photons far more readily than the high-energy ones, so the photons that remain are on average more penetrating, and the HVL rises.",
  steps=[f"2 mm of aluminium is 0.20 cm × {X.RHO_AL} g/cm³ = {t15:.3f} g/cm².",
         f"Transmission at 20 keV: e<sup>−{X.AL[20]} × {t15:.3f}</sup> = {math.exp(-X.AL[20] * t15):.2f}. At 50 keV: e<sup>−{X.AL[50]} × {t15:.3f}</sup> = {math.exp(-X.AL[50] * t15):.2f}.",
         "Output: every energy loses some photons, so the output falls.",
         "HVL: the 20 keV photons are mostly removed and the 50 keV photons mostly kept, so the mean energy and the HVL rise.",
         "E<sub>max</sub>: still 100 keV."],
  tip="Output and HVL need not move together: a filter lowers the output and raises the HVL, while a higher kVp raises both.",
  how=H_)
q(T, "A technique is changed from 80 kVp to 100 kVp",
  simple="Raising the kVp gives every electron more energy, so whatever depends on the electron energy changes: the top of the spectrum, the x-ray yield per electron, and the penetration of the beam. Properties fixed by the anode material and the construction of the tube stay as they were.",
  steps=["Maximum photon energy: rises from 80 to 100 keV. Changes.",
         f"Output per mAs: rises about as kVp², by (100 / 80)² = {(100 / 80) ** 2:.2f}, and more in a filtered beam. Changes.",
         "First HVL: the spectrum reaches higher and its mean energy rises. Changes.",
         "Tungsten K lines: their energies are differences of tungsten binding energies. Both 80 and 100 kVp exceed the 69.5 keV K-shell energy, so the lines appear at both, at the same energies. No change.",
         "Inherent filtration: the target, envelope, oil, and window belong to the tube. No change.",
         "Effective to actual focal spot: sin θ, fixed by the anode angle. No change."],
  tip="The K lines grow stronger at 100 kVp, because the electrons spend more of their path above the 69.5 keV K-shell energy, but their energies stay where they were.",
  how=H_)

# ---- beam quality and kV therapy
q(T, "A 250 kV orthovoltage beam is commissioned for treatment.",
  simple="The quality of a kilovoltage beam is its penetrating power, and two numbers describe it: the kVp, which fixes the top of the spectrum, and the HVL, which shows how penetrating the filtered spectrum is. Copper attenuates far more than aluminium, so at orthovoltage energies its HVLs are a few millimetres (about 0.5 to 4 mm), where aluminium would need layers several times thicker.",
  steps=["Copper HVL with the kVp: the usual specifier for orthovoltage beams (150 to 500 kV).",
         "Lead HVL: used for shielding barriers, not for the quality of a treatment beam.",
         "%dd(10)<sub>x</sub>: the TG-51 specifier for megavoltage photon beams.",
         "Tube current and exposure time: set how much radiation is delivered, not its quality."],
  tip="The kVp alone does not fix the quality: the same 250 kV with different filters gives beams of different HVL, so the HVL is quoted with it.",
  how=H_)
q(T, "Narrow-beam transmission measurements are made for a superficial beam.",
  simple="The homogeneity coefficient compares the first two half-value layers, and so shows how far the beam is from a single energy. The second layer, the extra thickness from 50% to 25%, is thicker than the first because the first has already removed the softest photons, so the ratio comes out below 1.",
  steps=["HVL<sub>1</sub>: the thickness that leaves 50%, 2.5 mm Al.",
         f"HVL<sub>2</sub>: the thickness added to go from 50% to 25%, 6.0 − 2.5 = {6.0 - 2.5:.1f} mm Al.",
         f"HC = HVL<sub>1</sub> / HVL<sub>2</sub> = 2.5 / {6.0 - 2.5:.1f} = {X.q_hc:.2f}.",
         "For a single energy both layers would be 2.5 mm and HC would be 1."],
  tip=f"6.0 mm is a total depth, not a layer: using it as HVL<sub>2</sub> gives 2.5 / 6.0 = {2.5 / 6.0:.2f}, and 6.0 / 2.5 = {6.0 / 2.5:.2f} compares two depths, not two layers.",
  check=X.q_hc)
q(T, "Four kilovoltage beams are described by their first HVL.",
  simple=f"The effective energy is the energy of a single-energy beam with the same first HVL, and the same number of millimetres means different things in different metals. Copper (Z = 29, ρ = {X.RHO_CU} g/cm³) stops far more photons per millimetre than aluminium (Z = 13, ρ = {X.RHO_AL} g/cm³), so a beam that needs 1 mm of copper to halve it is harder than one that needs 4 mm of aluminium.",
  steps=["Within one metal, a thicker HVL means a harder beam: 4 mm Al above 2 mm Al, and 3 mm Cu above 1 mm Cu.",
         "Between metals, find each effective energy: μ/ρ = ln 2 / (HVL in cm × ρ), then the energy with that μ/ρ in the table for the same metal.",
         f"2 mm Al: {X.mu_rho(2.0, X.RHO_AL):.3f} cm²/g, about {X.RANK[0][1]:.0f} keV. 4 mm Al: {X.mu_rho(4.0, X.RHO_AL):.3f} cm²/g, about {X.RANK[1][1]:.0f} keV.",
         f"1 mm Cu: {X.mu_rho(1.0, X.RHO_CU):.3f} cm²/g, about {X.RANK[2][1]:.0f} keV. 3 mm Cu: {X.mu_rho(3.0, X.RHO_CU):.3f} cm²/g, about {X.RANK[3][1]:.0f} keV.",
         "Order: 2 mm Al, 4 mm Al, 1 mm Cu, 3 mm Cu."],
  tip=f"A μ/ρ value means an energy only in the table of its own metal: 1 mm Cu gives {X.mu_rho(1.0, X.RHO_CU):.3f} cm²/g, more than the {X.mu_rho(4.0, X.RHO_AL):.3f} cm²/g of 4 mm Al, yet it marks the higher energy, because copper attenuates far more per gram than aluminium at kilovoltage energies.",
  how=H_)
lin20 = 30 + 10 * (X.AL[30] - X.q_mr) / (X.AL[30] - X.AL[40])
q(T, "A 100 kVp superficial beam has a first HVL of 3.0 mm Al.",
  simple="The question asks which single photon energy would be halved by the same 3.0 mm of aluminium. The HVL gives the attenuation coefficient; the table lists it per gram, so the coefficient is divided by the density before the energy is looked up.",
  steps=[f"μ<sub>eff</sub> = ln 2 / HVL = {X.LN2:.4f} / 0.30 cm = {X.q_mu:.3f} cm<sup>−1</sup>.",
         f"μ<sub>eff</sub>/ρ = {X.q_mu:.3f} / {X.RHO_AL} = {X.q_mr:.4f} cm²/g, between the 30 keV value ({X.AL[30]}) and the 40 keV value ({X.AL[40]}).",
         f"Between two table entries μ/ρ falls as E<sup>−n</sup>, a straight line on log–log axes, with n = ln({X.AL[30]} / {X.AL[40]}) / ln(40 / 30) = {X.q_n:.3f}.",
         f"E = 30 keV × ({X.AL[30]} / {X.q_mr:.4f})<sup>1/{X.q_n:.3f}</sup> = {X.q_E:.1f} keV, which rounds to {X.q_E:.0f} keV, about one third of the 100 kVp peak.",
         f"A straight-line interpolation of μ/ρ gives {lin20:.1f} keV, which points to the same option."],
  tip=f"The table is per gram. Treating {X.q_mu:.3f} cm<sup>−1</sup> as μ/ρ, without dividing by the density, gives {X.q_E_nd:.0f} keV.",
  check=X.q_E)
r21a, r21b = math.log(54.5 / 50.0), math.log(54.5 / 45.2)
q(T, "Narrow-beam readings are taken for a superficial beam with aluminium added.",
  simple="The HVL is the thickness at which the reading falls to half the open value, 50.0 here. No reading was taken there, but the 2.0 mm and 3.0 mm readings (54.5 and 45.2) bracket it. Over a step that short the fall is close to exponential, so ln(reading) runs on a straight line between them, and the 50.0 point can be read off that line.",
  steps=["Target: half of 100.0 = 50.0, between 54.5 at 2.0 mm and 45.2 at 3.0 mm.",
         f"Fall in ln(reading) over the 1.0 mm step: ln(54.5 / 45.2) = {r21b:.4f}.",
         f"Fall needed from 54.5 to 50.0: ln(54.5 / 50.0) = {r21a:.4f}.",
         f"Fraction of the step: {r21a:.4f} / {r21b:.4f} = {r21a / r21b:.3f}.",
         f"HVL = 2.0 mm + {r21a / r21b:.3f} × 1.0 mm = {X.q_x50:.2f} mm Al."],
  tip=f"One exponential from zero through the 2.0 mm point gives {X.q_x50_one:.2f} mm Al, too low, because the first millimetres remove the softest photons faster than later ones. A straight line through the two readings gives {X.q_x50_lin:.2f} mm Al, close here only because both readings lie near 50.",
  check=X.q_x50)
q(T, "A 70 kV superficial beam treats a skin lesion",
  simple="The dose is wanted at the skin surface, from a beam below 100 kV. TG-61 handles that case by measuring free in air with a chamber calibrated in air kerma and converting to dose to water at the surface; the backscatter factor adds the radiation scattered back from the tissue under the surface, which a free-in-air reading cannot see.",
  steps=["Point of interest at or near the surface: the in-air method, for 40 to 300 kV.",
         "In-air method: D<sub>w,z=0</sub> = M N<sub>K</sub> B<sub>w</sub> P<sub>stem,air</sub> [(μ̄<sub>en</sub>/ρ)<sup>w</sup><sub>air</sub>]<sub>air</sub>. M N<sub>K</sub> is the air kerma free in air, B<sub>w</sub> adds the backscatter, and the ratio of mass energy-absorption coefficients turns air kerma into dose to water.",
         "In-phantom method at 2 cm depth: for 100 kV and above, and it gives the dose at depth, not at the surface.",
         "TG-51 with k<sub>Q</sub>: for megavoltage beams, with a chamber calibrated in dose to water.",
         "Depth of maximum dose: a megavoltage idea; a kilovoltage beam has its maximum at the surface."],
  how=H_)
