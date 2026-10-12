from blocks import *
import math, calc

q_co, lev_co = 2.824, 2.505
emax_co = q_co - lev_co
ph_cs = 0.944 * 0.9015 * 1000

TOPIC = dict(
    id="decay-schemes", domain=1, sub="I.B", title="Decay schemes and radionuclide production",
    ref=dict(aapm="2.2", khan="2", ford="2"),
    guide=[
        H("Reading a decay scheme"),
        P("A decay scheme plots nuclear energy upward and atomic number to the right. Each arrow is one transition, labelled with its branching ratio (percent of decays) and energy. The arrow direction gives the process:"),
        TABLE(["Arrow", "Process", "Z changes by", "What is emitted"], [
            ["[[1|Down and to the right]]", "[[1|β⁻ decay]]", "+1", "Electron and antineutrino"],
            ["[[1|Down and to the left]]", "[[1|β⁺ decay or electron capture]]", "−1", "Positron and neutrino (β⁺); neutrino, x-rays, Auger electrons (EC)"],
            ["[[1|Down and to the left, steep]]", "[[1|α decay]]", "−2 (A falls by 4)", "α particle"],
            ["[[1|Straight down]]", "[[1|γ emission or internal conversion]]", "0", "γ-ray, or a conversion electron followed by x-rays"]]),
        FIG("decay_schemes", "Decay schemes of Co-60 (left) and Cs-137 (right). Energy is not to the same scale in the two panels."),
        P("Co-60 decays by β⁻ almost entirely to the 2.505 MeV level of Ni-60, which drops to the ground state in two steps, [[2|so each decay emits a 1.173 and a 1.332 MeV photon (2.505 MeV together).]] Cs-137 decays by β⁻, and 94.4% of decays reach Ba-137m, a metastable level with a 2.55 min half-life. [[2|Ba-137m emits the 662 keV photon; Cs-137 itself does not.]]"),

        H("Discrete and continuous spectra"),
        TABLE(["Radiation", "Comes from", "Energy spectrum"], [
            ["β particles", "Nucleus; energy shared with the (anti)neutrino", "[[1|Continuous, from 0 up to E<sub>max</sub>; mean about E<sub>max</sub>/3]]"],
            ["α particles", "Nucleus", "[[1|Discrete]]"],
            ["γ-rays", "De-excitation of the daughter nucleus", "[[1|Discrete]]"],
            ["Internal-conversion electrons", "Excitation energy given to an orbital electron", "[[1|Discrete]]"],
            ["Characteristic x-rays, Auger electrons", "Atomic shell transitions", "[[1|Discrete]]"],
            ["Bremsstrahlung", "Electrons slowing down", "Continuous"]]),
        P("The β spectrum is continuous because the decay energy is split between the electron and the neutrino in every proportion. A β source is therefore described by its maximum energy and its mean energy, about one third of the maximum."),

        H("Radionuclide production"),
        P("Nuclear reactions are written target(projectile, ejected particle)product, for example <sup>59</sup>Co(n,γ)<sup>60</sup>Co. The production route predicts the decay mode: [[1|adding neutrons gives a neutron-rich nuclide that decays by β⁻; adding protons gives a proton-rich nuclide that decays by β⁺ or electron capture.]]"),
        TABLE(["Route", "Example reactions", "Products decay by"], [
            ["Reactor, neutron capture (n,γ)", "[[2|<sup>59</sup>Co(n,γ)<sup>60</sup>Co; <sup>191</sup>Ir(n,γ)<sup>192</sup>Ir]]; <sup>124</sup>Xe(n,γ)<sup>125</sup>Xe → EC → <sup>125</sup>I", "β⁻ (Xe-125 decays by EC)"],
            ["Reactor, fission of <sup>235</sup>U", "[[3|<sup>99</sup>Mo, <sup>131</sup>I, <sup>137</sup>Cs, <sup>90</sup>Sr as fission products]]", "β⁻"],
            ["Cyclotron, charged particles", "<sup>18</sup>O(p,n)<sup>18</sup>F; <sup>103</sup>Rh(p,n)<sup>103</sup>Pd", "β⁺ or EC"],
            ["Generator", "<sup>99</sup>Mo → <sup>99m</sup>Tc; <sup>68</sup>Ge → <sup>68</sup>Ga", "Daughter of a longer-lived parent"]]),

        EX("Photons per Co-60 decay", STEM("", ["1000 Co-60 decays"], "Find the [[number of photons]] emitted and their [[total energy]]."),
           ["Each decay populates the 2.505 MeV level (99.9%) and then emits the 1.173 and 1.332 MeV γ-rays in cascade."], "About 2000 photons, with 2.505 MeV of photon energy per decay."),
        EX("Maximum β energy of Co-60", STEM("The dominant β⁻ branch of Co-60 feeds an excited level of Ni-60.", ["decay energy to the ground state = 2.824 MeV", "level fed = 2.505 MeV"], "Find [[E<sub>max</sub>]] for this branch."),
           ["The γ cascade removes 2.505 MeV, so only the rest is available to the β⁻ and the antineutrino."], f"E<sub>max</sub> = 2.824 − 2.505 = {emax_co:.3f} MeV, with a mean β energy near 0.1 MeV."),
        EX("662 keV photons from Cs-137", STEM("", ["1000 Cs-137 decays", "94.4% of decays reach Ba-137m", "about 90.2% of Ba-137m transitions emit a photon (the rest are internal conversions)"], "Find the [[number of 662 keV photons]] emitted."),
           ["1000 × 0.944 × 0.902"], f"About {ph_cs:.0f}."),
    ],
    cards=[
        C("In a decay scheme, what do arrows going down-right, down-left, and straight down mean?", "Down-right: β⁻ (Z up by one). Down-left: β⁺ or electron capture (Z down by one), or a steeper α (Z down by two). Straight down: γ emission or internal conversion (no change in Z)."),
        C("Which radiations have continuous spectra and which have discrete lines?", "Continuous: β particles, bremsstrahlung. Discrete: α particles, γ-rays, conversion electrons, characteristic x-rays, Auger electrons."),
        C("Why is the β spectrum continuous?", "The decay energy is shared between the β particle and the neutrino in every possible proportion. The mean β energy is about one third of E<sub>max</sub>."),
        C("What does a Co-60 decay emit?", "A β⁻ (E<sub>max</sub> ≈ 0.32 MeV) and then two γ-rays in cascade, 1.173 and 1.332 MeV, 2.505 MeV in total.", fig="decay_schemes"),
        C("Where does the 662 keV photon of a Cs-137 source come from?", "From Ba-137m (T<sub>1/2</sub> = 2.55 min), populated by 94.4% of Cs-137 β⁻ decays. About 85 photons are emitted per 100 Cs-137 decays.", fig="decay_schemes"),
        C("How is a reaction like Co-59(n,γ)Co-60 read?", "Target Co-59 absorbs a neutron and emits a γ-ray, leaving Co-60: target(projectile, ejected particle)product."),
        C("Which production route gives which decay mode?", "Neutron capture and fission give neutron-rich nuclides (β⁻). Cyclotron bombardment with protons gives proton-rich nuclides (β⁺ or EC)."),
        C("How is Ir-192 produced? Co-60?", "In a reactor by neutron capture on the stable parent: <sup>191</sup>Ir(n,γ)<sup>192</sup>Ir and <sup>59</sup>Co(n,γ)<sup>60</sup>Co."),
        C("How are F-18 and Mo-99 produced?", "F-18: <sup>18</sup>O(p,n)<sup>18</sup>F in a cyclotron, β⁺ decay. Mo-99: mainly as a fission product of U-235 in a reactor; it feeds the Mo/Tc generator."),
        C("What is a radionuclide generator?", "A longer-lived parent held on a column that continuously decays to a shorter-lived daughter, which is eluted when needed (Mo-99 → Tc-99m)."),
    ],
)

PROBLEMS = [
    PR("Which radiation has a continuous energy spectrum?", "β⁻ particles", ["α particles", "Characteristic x-rays", "γ-rays from an isomeric transition"],
       "The decay energy is shared between the β particle and the antineutrino in every proportion. The others are emitted with fixed energies.", lvl="Easy"),
    PR("Which particle shares the decay energy with the electron in β⁻ decay?", "An antineutrino", ["A neutrino", "A positron", "An α particle"],
       "β⁻ decay emits an electron and an electron antineutrino; β⁺ decay emits a positron and a neutrino.", lvl="Easy"),
    PRN("A Co-60 nucleus emits γ-rays of <v>1.173 MeV</v> and <v>1.332 MeV</v> in cascade. What <f>total photon energy</f> is emitted per decay?", 1.173 + 1.332, [1.173, 1.332, q_co], "{:.3f} MeV",
        "Both photons are emitted in every decay: 1.173 + 1.332 = 2.505 MeV, the energy of the Ni-60 level.", lvl="Moderate"),
    PR("A nuclide produced by neutron capture in a reactor will most likely decay by:", "β⁻ decay, because the product is neutron-rich", ["β⁺ decay, because the product is proton-rich", "electron capture", "α decay"],
       "Adding neutrons moves the nucleus above the stable band. β⁻ decay converts a neutron to a proton and moves it back toward stability.", lvl="Moderate"),
    PRN("A β⁻ emitter has <v>E<sub>max</sub> = 1.80 MeV</v>. Approximately what is the <f>mean β energy</f>?", 0.60, [0.18, 0.90, 1.80], "{:.2f} MeV",
        "The mean of a β⁻ spectrum is roughly one third of E<sub>max</sub>: 1.80 / 3 = 0.60 MeV.", lvl="Challenging"),
]

INLINE = {0: [3, 6], 1: [1, 2, 7], 2: [8]}

TERMS = ['branching ratio', 'metastable']

TAKE = [
    [("Arrow direction gives the process: down-right β⁻, short down-left β⁺ or EC, steep down-left α, vertical γ or IC.", "scheme-arrows"),
     ("Co-60 emits 1.173 and 1.332 MeV per decay. The Cs-137 photon (662 keV) comes from Ba-137m.", "scheme-cascades")],
    [("β spectra are continuous, with a mean of about E<sub>max</sub>/3. α, γ, conversion electrons, characteristic x-rays, and Auger electrons are discrete.", "beta-spectrum")],
    [("Reactor products (neutron capture, fission) are neutron-rich and decay by β⁻; cyclotron products are proton-rich and decay by β⁺ or EC.", "production-routes"),
     ("Co-60 and Ir-192 come from neutron capture.", "neutron-capture"),
     ("Cs-137 and Mo-99 are fission products.", "fission-yield")],
]


# ---------------------------------------------------------------- sorting and matching questions
PROBLEMS += [
    SORT("Match each process to its arrow in a decay scheme.", ["Down and to the right", "Short, down and to the left", "Steep, down and to the left", "Straight down"],
         [("β⁻", 0), ("β⁺ or electron capture", 1), ("α", 2), ("γ or internal conversion", 3)],
         "Z increases to the right and energy increases upward. β⁻ raises Z by 1, so it goes right. β⁺ and electron capture lower Z by 1, a short step left. An α particle lowers Z by 2 with a large energy drop, so its arrow is steep. γ emission and internal conversion leave Z unchanged, so they go straight down.", lvl="Moderate", mode="match", cap=1),
    SORT("Does each radiation have a continuous energy spectrum or discrete lines?", ["Continuous spectrum", "Discrete lines"],
         [("β⁻ particles", 0), ("β⁺ particles", 0), ("α particles", 1), ("γ rays", 1), ("Conversion electrons", 1), ("Characteristic x-rays", 1), ("Auger electrons", 1)],
         "A β particle shares the decay energy with a neutrino, so its energy is spread up to E<sub>max</sub>, with a mean of about E<sub>max</sub>/3. The other radiations carry the energy difference between two fixed levels, so each appears at a single energy.", lvl="Moderate"),
    SORT("How is each nuclide produced?", ["Neutron capture in a reactor", "Fission product", "Cyclotron"],
         [("Co-60", 0), ("Ir-192", 0), ("Cs-137", 1), ("Mo-99", 1), ("F-18", 2)],
         "Stable Co-59 and Ir-191 each capture a neutron to become Co-60 and Ir-192, which are neutron-rich and decay by β⁻. Cs-137 and Mo-99 are products of fission, also neutron-rich. F-18 is made in a cyclotron by proton bombardment of O-18, which leaves a proton-rich nucleus that decays by β⁺.", lvl="Moderate"),
]


# ---------------------------------------------------------------- tap-the-figure question
import math as _math
_gb = lambda E: _math.sqrt(E) * (1 - E) ** 2 / 0.286216
PROBLEMS += [
]
