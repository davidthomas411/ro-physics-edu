"""Explain further text for the questions of the neutron interactions chapter (neutron-interactions). Entries are registered with q() from more_content."""
import math
from more_content import q
import neutron_interactions as X          # the chapter's constants, so that the numbers in an explanation match the chapter

T = "neutron-interactions"
H_ = "How to decide"

# ---- energy classes and cross sections
q(T, "A 2 MeV neutron and a 2 MeV electron enter soft tissue.",
  simple="A charged particle pulls on every electron it passes, so it loses energy in many small steps all along its track. A neutron has no charge: it notices matter only when it comes within about 10<sup>−12</sup> cm of a nucleus, and nuclei fill a tiny fraction of the space in an atom. Most of the time it flies straight through.",
  steps=["Rule: ionization along a track needs a charge, because it comes from the Coulomb force.",
         "The neutron is uncharged, so its only interactions are with nuclei, through the nuclear force.",
         "Mass: a proton is almost as heavy as a neutron and ionizes densely, so mass is not the reason.",
         "Speed: at the same kinetic energy the neutron, about 1,800 times heavier, is far slower than the electron.",
         "Magnetic moment: its interaction with electrons is negligible."],
  tip="Neutrons and photons are both indirectly ionizing: they deposit dose through the charged particles they set in motion, recoil protons for the neutron and electrons for the photon.",
  how=H_)
q(T, "The capture cross section of B-10 follows the 1/v law at low energies.",
  simple="A slow neutron spends more time near each nucleus it passes, so its chance of being captured is larger. For B-10 the capture cross section is inversely proportional to the speed v, and the speed goes as the square root of the energy, so the cross section goes as E<sup>−1/2</sup>.",
  steps=["σ(E) = σ<sub>0</sub> × √(E<sub>0</sub> / E), with σ<sub>0</sub> at E<sub>0</sub> = 0.025 eV.",
         f"E<sub>0</sub> / E = 0.025 / 1.0 = 0.025, and √0.025 = {math.sqrt(X.E_TH):.4f}.",
         f"σ = {X.S_B:,.0f} b × {math.sqrt(X.E_TH):.4f} = {X.s_1ev:,.0f} b."],
  tip=f"Scaling with 1/E instead of 1/√E gives {X.s_1ev_e:,.0f} b. The energy rose 40-fold, so the speed rose √40 = {math.sqrt(40):.2f}-fold and the cross section fell by the same factor.",
  check=X.s_1ev)

# ---- elastic scattering and moderation
q(T, "Why is hydrogen the most effective nucleus for slowing fast neutrons?",
  simple="In a collision between two balls of equal mass, a head-on hit stops the first ball and sends the second off with all of its energy. A proton has almost the same mass as a neutron, so it behaves in the same way. A heavy nucleus acts more like a wall: the neutron bounces off with most of its energy.",
  steps=["Largest fraction transferred = 4A/(1 + A)².",
         f"A = 1 (hydrogen): 4/4 = 1. A = 12 (carbon): {X.f_c:.3f}. A = 16 (oxygen): {X.f_o:.3f}. A = 208 (lead): {X.f_pb:.4f}.",
         "On average a collision with hydrogen removes half the energy, so about 18 collisions bring a 2 MeV neutron to thermal energy.",
         "Water, polyethylene, paraffin, and tissue are rich in hydrogen and therefore good moderators."],
  tip="Hydrogen is a good moderator because of elastic scattering, not capture: its thermal capture cross section is only 0.33 b.",
  how=H_)
q(T, "A fast neutron scatters elastically from a Pb-208 nucleus (Z = 82).",
  simple="The largest loss happens in a head-on collision. With a nucleus 208 times heavier than the neutron, even that collision takes less than 2% of the energy, which is why lead barely slows fast neutrons by elastic scattering.",
  steps=["Use the mass number, A = 208, not the atomic number.",
         f"4A / (1 + A)² = 832 / 209² = 832 / {209 ** 2:,} = {X.f_pb:.4f}.",
         f"As a percentage: {100 * X.f_pb:.2f}%."],
  tip=f"Using Z = 82 gives {100 * X.e_max(82):.2f}%. The mean loss over all angles is half the largest, {100 * X.ml_pb:.2f}%.",
  check=100 * X.f_pb)
q(T, "A 1.0 MeV neutron slows to 0.025 eV in graphite by elastic scattering.",
  simple="Each collision lowers the logarithm of the energy by the same amount on average, ξ, so the number of collisions is the total drop in ln E divided by ξ. For carbon ξ is small, about one sixth of the value for hydrogen, so graphite needs about six times as many collisions.",
  steps=[f"Energy ratio: 1.0 × 10<sup>6</sup> eV / 0.025 eV = 4.0 × 10<sup>7</sup>.",
         f"ln(4.0 × 10<sup>7</sup>) = {X.L1:.2f}.",
         f"n = {X.L1:.2f} / {X.xi_c:.3f} = {X.n_g:.0f}."],
  tip=f"The natural logarithm is needed: log<sub>10</sub> gives {X.n_g_log10:.0f}. Dividing by the mean fractional loss ({X.ml_c:.3f}) in place of ξ gives {X.n_g_mean:.0f}.",
  check=X.n_g)

# ---- capture and other reactions
q(T, "What distinguishes inelastic from elastic scattering of a neutron?",
  simple="In elastic scattering the nucleus recoils but stays in its ground state, so the kinetic energy of neutron and nucleus together is conserved. In inelastic scattering some of the energy lifts the nucleus to an excited state, and the nucleus then gives that energy off as a γ ray.",
  steps=["Elastic, (n,n): kinetic energy conserved; the nucleus is left unexcited.",
         "Inelastic, (n,n′): kinetic energy not conserved; the nucleus emits a γ ray.",
         f"Threshold: a little more than the excitation energy, E* (A + 1)/A: about {X.thr_c:.1f} MeV for carbon, over 6 MeV for oxygen, about {X.thr_w:.1f} MeV for tungsten.",
         "Absorption followed by a proton leaving is an (n,p) reaction, not scattering."],
  tip="Because the thresholds in carbon and oxygen are several MeV, inelastic scattering matters in tissue only for fast neutrons above a few MeV, while in heavy metals it is the main way fast neutrons lose energy.",
  how=H_)
q(T, "Slowed neutrons are captured in a water phantom.",
  simple="Water holds two hydrogen nuclei for each oxygen nucleus, and hydrogen captures thermal neutrons about 1,700 times more readily than oxygen. Almost every capture is therefore H(n,γ)H-2, which makes a deuteron and one γ ray carrying the binding energy of the deuteron, 2.2 MeV.",
  steps=[f"Captures per molecule are in proportion to 2 × {X.S_H} b for hydrogen and {X.S_O} b for oxygen.",
         f"Share on hydrogen: {2 * X.S_H:.3f} / ({2 * X.S_H:.3f} + {X.S_O}) = {100 * X.cap_h_frac:.2f}%.",
         "Each capture gives one 2.2 MeV γ ray, which can travel tens of centimetres."],
  tip="The 0.48 MeV γ ray comes from B-10 capture, which is why borated materials give softer capture γ rays than plain hydrogenous ones.",
  how=H_)
q(T, "Which of these nuclides detect slow neutrons through the charged particles of a capture reaction?",
  simple="A detector needs a reaction that is likely with slow neutrons and that releases its energy to charged particles, which ionize the detector at once. B-10, He-3, and Li-6 do both: cross sections of hundreds to thousands of barns, and an α particle, proton, or triton with a large energy.",
  steps=[f"B-10(n,α)Li-7: {X.S_B:,.0f} b, {X.Q_B1:.2f} MeV in most captures: BF<sub>3</sub> counters.",
         f"He-3(n,p)H-3: {X.S_HE:,.0f} b, {X.Q_HE:.2f} MeV: He-3 counters.",
         f"Li-6(n,α)H-3: {X.S_LI:.0f} b, {X.Q_LI:.2f} MeV: TLD-600 chips and lithium scintillators.",
         "Cd-113 and H-1 capture by (n,γ) and give γ rays; C-12 hardly captures."],
  tip="A pair of TLD-600 (Li-6) and TLD-700 (Li-7) chips separates neutrons from photons: both respond to photons, only the Li-6 chip to slow neutrons, so the difference of the readings is the neutron signal. Bonner spheres of several moderator sizes around a small detector unfold a neutron spectrum.",
  how=H_)

# ---- kerma, dose, and radiation weighting
q(T, "Adipose tissue, muscle, and cortical bone receive the same fluence of 1 MeV neutrons.",
  simple="Fast neutrons give their energy mostly to hydrogen nuclei, because a proton can take up to all of the energy in one collision while carbon and oxygen take far less. The tissue with the most hydrogen per gram therefore absorbs the most energy per gram.",
  steps=[f"Hydrogen by mass: about {X.H_FAT}% in fat, {X.H_MUS}% in muscle, {X.H_BONE}% in bone.",
         "Dose per gram follows the hydrogen per gram: fat > muscle > bone.",
         "Kilovoltage photons give the opposite order (photoelectric effect, higher Z in bone); megavoltage photons give nearly equal doses per gram (Compton, electrons per gram)."],
  tip="The water content is not the measure: most of the hydrogen in fat is in the fat molecules themselves.",
  how=H_)
q(T, "Thermal neutrons irradiate a 1 g tissue sample and, in a separate exposure, the trunk of an adult.",
  simple="Thermal neutrons in tissue release energy in two ways. Capture by nitrogen gives a proton that stops within about 10 µm, so its energy stays wherever the capture happens. Capture by hydrogen releases far more energy, but as 2.2 MeV γ rays that cross tens of centimetres: they leave a small sample almost untouched but deposit much of their energy in a large body.",
  steps=[f"Energy per unit fluence ∝ (w/M) σ E: hydrogen (0.101/1.008) × {X.S_H} × {X.Q_H}; nitrogen (0.026/14.007) × {X.S_N} × {X.Q_N}.",
         f"Ratio, hydrogen to nitrogen: about {X.r_hn:.0f}.",
         "Small sample: the γ rays escape, so the nitrogen protons dominate.",
         "Whole trunk: a large share of the γ-ray energy is absorbed, so the capture γ rays dominate."],
  tip="This is why ICRP 103 gives thermal neutrons a low weighting factor, about 2.5: much of their dose in the body is delivered by low-LET γ rays.",
  how=H_)
q(T, "How does the radiation weighting factor w",
  simple="Both factors scale absorbed dose for the biological effectiveness of the radiation, but they are attached to different things. w<sub>R</sub> is a single number chosen from the kind and energy of the radiation arriving at the body, used for equivalent and effective dose. Q is a function of the LET of the charged particles at the point of interest, used for dose equivalent in the operational quantities that instruments estimate.",
  steps=["w<sub>R</sub> (ICRP 60 and 103): radiation incident on the body; multiplies the mean organ dose. For neutrons it ranges from about 2.5 (thermal) to a peak near 21 at 1 MeV.",
         "Q(L) (ICRP 60): 1 below 10 keV/µm, rising to about 30 near 100 keV/µm, falling above.",
         "The tissue enters through w<sub>T</sub>, not w<sub>R</sub>.",
         "10 CFR 20 still uses quality factors, with Q = 10 for neutrons of unknown energy."],
  how=H_)

# ---- neutrons in radiotherapy
q(T, "In boron neutron capture therapy, thermal neutrons are captured throughout the irradiated tissue.",
  simple="BNCT relies on the short range of the capture products, not on where the neutrons go. Neutrons are captured in every tissue, but only B-10 releases an α particle and a lithium ion, and both stop within about one cell diameter. A cell that has taken up boron therefore receives a large local dose that its neighbours without boron do not.",
  steps=[f"Energy shared by the two products in most captures: {X.Q_B1:.2f} MeV, α {X.e_a:.2f} MeV and Li {X.e_li:.2f} MeV (equal and opposite momenta).",
         "Ranges in tissue: about 5 to 9 µm.",
         f"Example: a thermal fluence of 10<sup>12</sup> cm<sup>−2</sup> with 30 µg/g of B-10 gives about {X.d_b:.1f} Gy from boron, against {X.d_n:.2f} Gy from nitrogen capture.",
         "The beam is epithermal so that it penetrates a few centimetres before slowing to thermal energies, where the B-10 cross section is large."],
  tip=f"The {X.G_B:.2f} MeV γ ray from the excited lithium nucleus escapes the cell and adds to the low-LET background dose.",
  how=H_)
