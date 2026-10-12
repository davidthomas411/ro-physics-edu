from blocks import *

TOPIC = dict(
    id="decay-modes", domain=1, sub="I.B", title="Decay modes",
    ref=dict(aapm="2.2", khan="2", ford="2"),
    guide=[
        H("Stability and decay mode"),
        P("A nucleus decays toward the band of stable nuclei. Light stable nuclei have about equal numbers of neutrons and protons; heavier ones have more neutrons than protons. Where a nucleus sits relative to that band predicts its mode."),
        FIG("nuclide_chart", "Each decay moves the nucleus toward the band of stability. Arrows show the change in neutrons N and protons Z."),
        TABLE(["Nuclear state", "Typical decay", "Effect"], [
            ["[[1|Too many neutrons]]", "[[1|β⁻]]", "n → p"],
            ["[[1|Too many protons]]", "[[1|β⁺ or electron capture]]", "p → n"],
            ["[[1|Heavy]]", "[[1|α]]", "Z − 2, A − 4"],
            ["Excited state", "γ emission or internal conversion", "Z and A unchanged"]]),

        H("Decay modes"),
        TABLE(["Mode", "ΔZ", "ΔA", "Emitted", "Notes"], [
            ["α", "[[1|−2]]", "[[1|−4]]", "Helium nucleus with discrete energy, several MeV", "Heavy nuclei. High LET; range in tissue under 0.1 mm."],
            ["β⁻", "[[1|+1]]", "[[1|0]]", "Electron and antineutrino", "Energy is shared, so the spectrum is continuous. Mean energy is about one third of E<sub>max</sub>."],
            ["β⁺", "[[1|−1]]", "[[1|0]]", "Positron and neutrino", "[[2|Needs an atomic mass difference above 2m<sub>e</sub>c² = 1.022 MeV.]] [[3|The positron annihilates into two 511 keV photons at about 180°.]]"],
            ["Electron capture (EC)", "[[1|−1]]", "[[1|0]]", "Neutrino; x-ray or Auger electron from the filled vacancy", "Competes with β⁺ and is [[2|the only route below 1.022 MeV]]."],
            ["Isomeric transition", "0", "0", "γ ray, or an internal conversion electron", "Excited nucleus drops to a lower state. Often follows another decay."]]),

        H("Internal conversion and Auger electrons"),
        P("In internal conversion the nucleus passes its excitation energy to an orbital electron, which leaves with kinetic energy E<sub>γ</sub> minus its binding energy. [[1|The vacancy it leaves, like the one after electron capture, is filled by an outer electron. The released energy appears as a characteristic x-ray or is given to another orbital electron, an Auger electron.]]"),
        P("Auger electrons carry eV to a few keV and travel nanometres to micrometres. They deposit energy densely, so they matter mainly when the decay occurs next to DNA."),

        H("Radionuclides used in radiation oncology"),
        TABLE(["Nuclide", "Decay", "Half-life", "Principal emissions", "Use"], [
            ["[[1|I-125]]", "[[1|EC]]", "[[1|59.4 d]]", "x-rays and γ, 27–35 keV", "LDR seeds, eye plaques"],
            ["[[1|Pd-103]]", "[[1|EC]]", "[[1|17.0 d]]", "Rh x-rays, 20–23 keV", "LDR seeds"],
            ["Cs-131", "EC", "9.7 d", "Xe x-rays, about 29–34 keV", "LDR seeds"],
            ["[[1|Ir-192]]", "[[1|β⁻ (95%), EC (5%)]]", "[[1|73.8 d]]", "γ lines, 0.14–1.06 MeV", "HDR and PDR brachytherapy"],
            ["[[1|Co-60]]", "[[1|β⁻]]", "[[1|5.27 y]]", "γ, 1.17 and 1.33 MeV", "Teletherapy, Gamma Knife"],
            ["[[1|Cs-137]]", "[[1|β⁻]]", "[[1|30.1 y]]", "γ, 662 keV, from Ba-137m", "Calibration sources, irradiators"],
            ["[[2|Y-90]]", "[[2|β⁻]]", "64 h", "β, E<sub>max</sub> 2.28 MeV", "Radioembolization"],
            ["[[2|Lu-177]]", "[[2|β⁻]]", "6.65 d", "β; γ, 208 and 113 keV", "Radiopharmaceutical therapy"],
            ["[[2|I-131]]", "[[2|β⁻]]", "8.0 d", "β; γ, 364 keV", "Thyroid therapy"],
            ["[[2|Ra-223]]", "[[2|α (decay chain)]]", "11.4 d", "α particles", "Bone-metastasis therapy"],
            ["[[2|F-18]]", "[[2|β⁺]]", "110 min", "511 keV photon pairs", "PET"],
            ["Tc-99m", "Isomeric transition", "6.0 h", "γ, 140 keV", "Imaging"]]),

    ],
    cards=[
        C("Which decay occurs in a neutron-rich nucleus, and what changes?", "β⁻: a neutron becomes a proton. Z increases by 1, A is unchanged, and an electron and an antineutrino are emitted.", fig="nuclide_chart"),
        C("Ra-226 (Z = 88) decays by α emission. Give the daughter's Z and A.", "Rn-222, with Z = 86 and A = 222: α decay lowers Z by 2 and A by 4."),
        C("A proton-rich nucleus can decay by β⁺ or electron capture. What decides which can occur?", "β⁺ needs the parent–daughter atomic mass difference to exceed 2m<sub>e</sub>c² = 1.022 MeV. Below that only EC is possible. Above it both can occur."),
        C("How do γ emission and internal conversion differ?", ["Both release nuclear excitation energy without changing Z or A.", "γ emission gives a photon. Internal conversion gives the energy to an orbital electron, ejected with E<sub>γ</sub> minus its binding energy."]),
        C("How does I-125 decay, and what photons result?", "By electron capture to an excited Te-125 state. The emissions are a 35.5 keV γ ray and Te characteristic x-rays of about 27–31 keV."),
        C("Ir-192 decays by which modes, and what photon energies result?", "β⁻ (about 95%) to Pt-192 and electron capture (about 5%) to Os-192. Many γ lines from 0.14 to 1.06 MeV; the mean photon energy is about 0.38–0.40 MeV."),
        C("Why does α decay deposit its energy over a short distance?", "An α particle is heavy and doubly charged, so its LET is high and its range in tissue is under 0.1 mm."),
    ],
)

TERMS = ['internal conversion', 'Auger electron']

TAKE = [
    [("Neutron-rich nuclei decay by β⁻, proton-rich nuclei by β⁺ or EC, and heavy nuclei by α.", "decay-map")],
    [("β⁻, β⁺, and EC change Z by one and leave A unchanged. α changes Z by 2 and A by 4.", "decay-steps"),
     ("β⁺ needs more than 1.022 MeV of available energy; below that only EC occurs.", "beta-plus-threshold"),
     ("A positron ends as two 511 keV photons at about 180°.", "pet-coincidence")],
    [("EC and internal conversion leave a shell vacancy, so characteristic x-rays or Auger electrons follow.", "vacancy-fates")],
    [("Sealed sources: I-125 (59.4 d, EC), Pd-103 (17.0 d, EC), Ir-192 (73.8 d, β⁻), Co-60 (5.27 y, β⁻), Cs-137 (30.1 y, β⁻).", "source-half-lives"),
     ("Y-90, Lu-177, and I-131 are β⁻ emitters, Ra-223 is an α emitter, and F-18 is a β⁺ emitter.", "nuclide-bins")],
]
