"""Explain further text for the questions of the attenuation coefficients chapter (attenuation). Entries are registered with q() from more_content."""
from more_content import q
from blocks import sci
import attenuation as X          # the chapter's constants, so that the numbers in an explanation match the chapter

T = "attenuation"
H_ = "How to decide"
W, B, L = X.WAT, X.BON, X.LEA
sg = X.sig4

q(T, "Ice, liquid water, and steam are each irradiated by photons of one energy.",
  simple="All three are the same molecule, H<sub>2</sub>O, packed at different densities. The chance of an interaction per gram depends only on which atoms are present and on the photon energy, so μ/ρ is shared. Anything quoted per centimetre scales with the number of molecules in each centimetre, so it changes with density.",
  steps=["Rule: μ = ρ × μ/ρ. Composition and energy fix μ/ρ; density then fixes μ.",
         "μ/ρ: the same for ice, water, and steam.",
         "μ: proportional to ρ, so far smaller in steam.",
         "HVL in cm = 0.693/μ and mean free path = 1/μ: both grow as the density falls."],
  tip="An HVL quoted as a mass thickness, in g/cm², would also be the same for all three; quoted in cm it is not.", how=H_)
q(T, "Lead in a Co-60 beam, with the photon energy taken as 1.25 MeV.",
  simple="The mass coefficient is a probability per gram per cm². Dividing it by the number of atoms in a gram turns it into an area per atom, the atomic cross-section, usually given in barns.",
  steps=[f"Atoms per gram = N<sub>A</sub> / A = 6.022 × 10<sup>23</sup> / {X.A['Pb']} = {sci(X.NA / X.A['Pb'], 4)}",
         f"<sub>a</sub>μ = {L[1.25][0]} cm²/g / {sci(X.NA / X.A['Pb'], 4)} g<sup>−1</sup> = {sci(X.p_at * X.BARN, 4)} cm²",
         f"1 b = 10<sup>−24</sup> cm², so <sub>a</sub>μ = {X.p_at:.1f} b",
         f"Per electron: {X.p_at:.1f} / {X.Z['Pb']} = {X.p_el:.3f} b, above the Klein–Nishina {X.kn125:.3f} b; photoelectric absorption and pair production add the rest."],
  tip=f"The density converts μ/ρ to μ and plays no part here; keeping it gives {X.p_lin:.1f} b.", check=X.p_at)
q(T, "Photons of one energy cross a material.",
  simple="Each coefficient answers a different question. μ and μ/ρ count how often a photon interacts, per centimetre or per g/cm², and so set how much of a narrow beam gets through. μ<sub>tr</sub>/ρ counts the energy handed to charged particles, which is kerma. μ<sub>en</sub>/ρ also removes the part those particles radiate away, which leaves the energy deposited locally: the dose under charged-particle equilibrium.",
  steps=["Transmission through x cm: e<sup>−μx</sup>.", "Transmission through ρx g/cm²: e<sup>−(μ/ρ)ρx</sup>.",
         "Kerma = Ψ μ<sub>tr</sub>/ρ.", "Dose under charged-particle equilibrium = collision kerma = Ψ μ<sub>en</sub>/ρ."],
  tip=f"μ<sub>en</sub>/μ is the fraction of an interacting photon's energy that stays locally: {X.r125:.2f} in water at 1.25 MeV and about {X.en_mu(W, 0.1):.2f} at 100 keV, about {100 * X.en_mu(W, 0.1):.0f} keV of a 100 keV photon. Using μ<sub>en</sub> for transmission overstates it.", how=H_)
q(T, "The transmission of Cs-137 γ rays (662 keV) through concrete slabs is measured with a wide field",
  simple="A wide field and a close detector let photons scattered in the slab reach the detector, so each reading is higher than the uncollided beam alone. The excess grows with thickness, so the readings fall more slowly than e<sup>−μx</sup> and a fitted exponential has a smaller coefficient.",
  steps=["Narrow beam: only uncollided photons are counted, so the slope is μ.",
         "Broad beam: reading = B e<sup>−μx</sup>, with the build-up factor B ≥ 1 rising with x.",
         "ln(reading) = ln B − μx; because ln B grows with x, the slope is less steep than μ.",
         "Cs-137 emits one energy, so the uncollided beam cannot harden; hardening is not the reason."],
  tip="A shield designed with the narrow-beam μ for a broad beam is too thin, because the scatter that reaches the far side was left out.", how=H_)
q(T, "A thick lead absorber is placed in a narrow 18 MV x-ray beam.",
  simple=f"An absorber removes fastest the photons for which μ is largest. In lead μ/ρ is large at low energy (photoelectric absorption), falls to a minimum between {X.PB_LO:g} and {X.PB_HI:g} MeV, and rises again as pair production grows. Photons near the minimum pass best, so both ends of a high-energy spectrum are trimmed.",
  steps=[f"Lead μ/ρ: {L[0.5][0]} cm²/g at 0.5 MeV, {L[X.PB_MIN][0]} at {X.PB_MIN:g} MeV, {L[10.0][0]} at 10 MeV, {L[15.0][0]} at 15 MeV.",
         "Below the minimum: photoelectric absorption removes the soft photons, as in any filter.",
         "Above the minimum: pair production, about Z per gram and rising with energy, removes the hardest photons.",
         "Water: μ/ρ falls with energy across the therapy range, so water only hardens the beam."],
  tip="Treating lead like a kilovoltage filter, which only removes low energies, misses the pair-production rise above a few MeV.", how=H_)
q(T, "Materials rich in hydrogen have more electrons per gram than other low-Z materials.",
  simple=f"Electrons per gram are N<sub>A</sub> Z/A. A hydrogen atom has one electron and a mass of about 1 u, while carbon, nitrogen, and oxygen carry about one neutron per proton, so they bring about half as many electrons per unit mass.",
  steps=[f"Z/A: hydrogen {X.zoa_el['H']:.3f}, carbon {X.zoa_el['C']:.3f}, oxygen {X.zoa_el['O']:.3f}, lead {X.zoa_el['Pb']:.3f}.",
         f"Electrons per gram (10<sup>23</sup>): water {X.EG['water'] / 1e23:.2f}, air {X.EG['air'] / 1e23:.2f}, cortical bone {X.EG['bone'] / 1e23:.2f}, lead {X.EG['lead'] / 1e23:.2f}.",
         "Compton scattering per gram follows these numbers, so hydrogen-rich materials attenuate slightly more per gram at megavoltage energies."],
  tip="Counting electrons per atom gives the opposite order: carbon has six electrons and hydrogen one, but carbon is twelve times heavier.", how=H_)
q(T, "Spongy bone is modelled, for illustration, as a mixture of cortical bone and water by mass.",
  simple="By the mixture rule, a mass coefficient of a mixture is the average of its components' values, each weighted by its fraction of the mass. The energy-absorption columns are read because the question asks for μ<sub>en</sub>/ρ.",
  steps=[f"Read at 30 keV: μ<sub>en</sub>/ρ = {sg(B[0.03][1])} cm²/g for cortical bone and {sg(W[0.03][1])} cm²/g for water.",
         f"Weight by mass: {X.FB:.2f} × {sg(B[0.03][1])} = {X.FB * B[0.03][1]:.4f}; {1 - X.FB:.2f} × {sg(W[0.03][1])} = {(1 - X.FB) * W[0.03][1]:.4f}.",
         f"Sum: {X.q_mix:.3f} cm²/g, {X.q_mix / W[0.03][1]:.2f} times that of water."],
  tip=f"Swapping the fractions gives {X.q_mix_swap:.3f} cm²/g; the attenuation columns give {X.q_mix_mu:.3f} cm²/g.", check=X.q_mix)
q(T, "At 40 keV, adipose tissue attenuates less per gram than water.",
  simple=f"At 40 keV both Compton scattering and photoelectric absorption matter. Fat and water have about the same electrons per gram, so they scatter alike per gram, but fat holds more carbon and less oxygen, so its effective atomic number is lower ({X.ZE['adipose']:.1f} against {X.ZE['water']:.2f}) and it absorbs fewer photons photoelectrically.",
  steps=[f"Electrons per gram: adipose tissue {X.EG['adipose'] / 1e23:.2f}, water {X.EG['water'] / 1e23:.2f} × 10<sup>23</sup>: Compton per gram is the same.",
         f"Photoelectric per gram ∝ Z<sub>eff</sub><sup>3</sup> roughly: ({X.ZE['adipose']:.1f}/{X.ZE['water']:.2f})<sup>3</sup> = {(X.ZE['adipose'] / X.ZE['water']) ** 3:.2f}.",
         "Density changes μ, not μ/ρ, and pair production needs more than 1.022 MeV."],
  tip="Lower density makes fat attenuate less per centimetre, a different statement from per gram.", how=H_)
q(T, "A physicist calculates μ/ρ of a new tissue-substitute plastic at 1.25 MeV",
  simple="The mixture rule needs two inputs: how much of each element the plastic holds by mass, and each element's μ/ρ at the energy. The answer is their weighted sum, and nothing about the bulk plastic enters it.",
  steps=["(μ/ρ)<sub>mix</sub> = Σ w<sub>i</sub> (μ/ρ)<sub>i</sub>.",
         "Mass fractions: from the chemical formula, w<sub>i</sub> = n<sub>i</sub>A<sub>i</sub>/M.",
         "Element values: from a table at 1.25 MeV.",
         "Density: needed only afterwards, to turn μ/ρ into μ. Z<sub>eff</sub> and the HVL are results, not inputs."],
  tip=f"For water at 1.25 MeV the rule gives {X.mu_mix:.5f} cm²/g from hydrogen and oxygen, the tabulated value.", how=H_)
q(T, "A treatment planning system needs the electron density of cortical bone relative to water.",
  simple="Electrons per cm³ are the density times the electrons per gram, ρ N<sub>A</sub> Z/A. Bone is denser than water but has slightly fewer electrons per gram, so its relative electron density is a little below its relative mass density.",
  steps=[f"Ratio of densities: {X.RHO['bone']} / {X.RHO['water']:.2f} = {X.RHO['bone'] / X.RHO['water']:.2f}",
         f"Ratio of Z/A: {X.ZA_B} / {X.ZA_W} = {X.ZA_B / X.ZA_W:.4f}",
         f"Relative electron density = {X.RHO['bone'] / X.RHO['water']:.2f} × {X.ZA_B / X.ZA_W:.4f} = {X.q_red:.3f}"],
  tip=f"Dividing by the Z/A ratio instead of multiplying gives {X.q_red_div:.2f}.", check=X.q_red)
q(T, "Orthovoltage therapy carried a risk of bone necrosis that megavoltage beams largely removed.",
  simple=f"Below about 150 keV photoelectric absorption, which rises steeply with atomic number, adds a large share of the energy absorbed. Calcium and phosphorus give bone an effective atomic number near {X.ZE['bone']:.0f} against about 7.4 for soft tissue, so bone absorbed several times more energy per gram in kilovoltage beams. At megavoltage energies Compton scattering dominates and only electrons per gram matter.",
  steps=[f"Bone to water, μ<sub>en</sub>/ρ: {X.bw(0.03):.2f} at 30 keV, {X.bw(0.1):.2f} at 100 keV, {X.bw(1.25):.3f} at 1.25 MeV.",
         "Density: affects energy per cm³, not per gram.",
         f"Electrons per gram: bone has {X.pct_b:.0f}% fewer than water.",
         "Pair production: none below 1.022 MeV."], how=H_)
q(T, "Cortical bone and water receive the same photon energy fluence, under charged-particle equilibrium.",
  simple="The energy absorbed per gram is the energy fluence times μ<sub>en</sub>/ρ, so bone and water compare through the ratio of their μ<sub>en</sub>/ρ. The ratio follows whichever interaction dominates at the energy.",
  steps=[f"Low energy, photoelectric (about Z<sup>3</sup> per gram): {X.bw(0.03):.2f} at 30 keV, {X.bw(0.06):.2f} at 60 keV, {X.bw(0.2):.2f} at 200 keV.",
         f"Compton region: {X.r_mv_lo:.3f} to {X.r_mv_hi:.3f} from 0.5 to 2 MeV, the ratio of electrons per gram ({X.re_bw:.3f}).",
         f"Pair production (about Z per gram): {X.bw(10.0):.2f} at 10 MeV and {X.bw(20.0):.2f} at 20 MeV; the ratio crosses 1 near {X.E_CROSS:.0f} MeV.",
         f"The densities ({X.RHO['bone']} against 1.00) never enter a quantity per gram."],
  tip="Applying the megavoltage ratio of electrons per gram at kilovoltage energies misses the photoelectric excess entirely.", how=H_)
