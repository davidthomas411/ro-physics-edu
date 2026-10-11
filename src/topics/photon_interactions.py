from blocks import *
import calc

HVL = 1.5
n1 = calc.hvl_count(0.01); x1 = n1 * HVL; tvl = calc.hvl_count(0.1) * HVL
t5 = 0.5 ** 5 * 100
e90 = calc.compton_scattered(1.0, 90); e180 = calc.compton_scattered(1.0, 180)

TOPIC = dict(
    id="photon-interactions", domain=1, sub="I.E", title="Photon interactions with matter",
    ref=dict(aapm="5.1, 5.2, 5.4", khan="5", ford="5"),
    guide=[
        H("Directly and indirectly ionizing radiation"),
        P("Charged particles (electrons, protons, α particles) ionize directly along their tracks. Photons and neutrons are indirectly ionizing: they first transfer energy to charged particles, and those charged particles deposit the dose. A photon either passes through, is scattered, or is absorbed."),

        H("Attenuation"),
        EQ("I = I<sub>0</sub> e<sup>−μx</sup>", "HVL = ln 2 / μ = 0.693 / μ", "TVL = ln 10 / μ = 3.32 HVL", "mean free path = 1/μ = 1.44 HVL"),
        P("μ is the linear attenuation coefficient (1/cm). The mass attenuation coefficient μ/ρ (cm²/g) removes the dependence on density. The exponential holds for a narrow beam of single-energy photons. In a broad beam, scattered photons also reach the detector, so the transmission is larger by a build-up factor B ≥ 1: I = B I<sub>0</sub> e<sup>−μx</sup>. A polyenergetic beam hardens as it passes through material, so its HVL grows with thickness."),
        EX("Shield thickness", STEM("A lead shield (illustrative values).", [f"HVL = {HVL} cm", "transmission = 1%"], "Find the [[shield thickness]]."),
           [f"Number of HVLs = log<sub>2</sub>(1/0.01) = {n1:.2f}.", f"Thickness = {n1:.2f} × {HVL} cm = {x1:.1f} cm.", f"Check: TVL = 3.32 × {HVL} = {tvl:.1f} cm, and 1% is two TVLs."], f"About {x1:.0f} cm."),

        H("Interaction processes"),
        TABLE(["Interaction", "What happens", "Z and energy dependence", "Dominant in water"], [
            ["Coherent (Rayleigh) scattering", "The photon changes direction with no energy loss and no ionization.", "Small, at low energy only", "Never dominant"],
            ["Photoelectric effect", "The photon is absorbed by a bound electron, which leaves with the photon energy minus its binding energy. The vacancy gives a characteristic x-ray or an Auger electron.", "τ/ρ ∝ Z³/E³, with sharp rises at absorption edges", "Below about 30 keV"],
            ["Compton scattering", "The photon scatters from a loosely bound electron and gives it part of its energy.", "Per electron it does not depend on Z, so per gram it is nearly the same for all tissues. It falls slowly with energy.", "About 30 keV to 24 MeV"],
            ["Pair production", "In the field of a nucleus the photon becomes an electron and a positron. Threshold 1.022 MeV; the excess is kinetic energy. The positron then annihilates into two 511 keV photons.", "Per atom ∝ Z², per gram ∝ Z. Rises with energy above threshold.", "Above about 24 MeV"],
            ["Triplet production", "Pair production in the field of an electron. Threshold 2.044 MeV.", "Small compared with pair production in the nuclear field", "Not dominant"],
            ["Photodisintegration", "The nucleus absorbs the photon and ejects a neutron or proton. Thresholds are typically 8–10 MeV or more, depending on the nuclide.", "Needs photon energy above the threshold", "Matters for beams of 10 MV and above"]]),
        FIG("interaction_regions", "Schematic. The left curve marks equal probability of photoelectric and Compton interactions; the right curve marks equal probability of Compton and pair production."),

        H("Compton scattering"),
        EQ("E′ = E / [1 + (E / 511 keV)(1 − cos θ)]", "E<sub>electron</sub> = E − E′"),
        UL("The scattered photon keeps less energy as the angle grows. The electron gets the most at θ = 180° (backscatter).",
           "As the incident energy rises, the scattered photon approaches 511 keV at 90° and 255 keV at 180°, and cannot exceed those.",
           "At megavoltage energies the electrons travel mostly forward."),
        EX("Compton energies", STEM("A photon undergoes Compton scattering.", ["incident energy = 1.0 MeV", "scattering angle θ = 90°"], "Find the [[scattered photon energy]] and the [[electron energy]]."),
           [f"E/511 keV = 1.0/0.511 = {1.0/0.511:.3f}.", f"E′ = 1.0 / (1 + {1.0/0.511:.3f} × 1) = {e90:.3f} MeV.", f"Electron: 1.0 − {e90:.3f} = {1.0-e90:.3f} MeV."],
           f"Photon {e90:.3f} MeV, electron {1.0-e90:.3f} MeV. (At 180° they would be {e180:.3f} and {1.0-e180:.3f} MeV.)"),

        H("Clinical consequences"),
        UL("At megavoltage energies in tissue Compton scattering dominates. It depends on electrons per gram, which is nearly the same for every element except hydrogen. Bone and soft tissue absorb alike per gram, and MV images show contrast from density, not atomic number.",
           "At kilovoltage energies the photoelectric effect, which scales as Z³, gives strong contrast between bone (effective Z about 13) and soft tissue (about 7.4). It is also why lead and tungsten shield well.",
           "Pair production and photodisintegration matter for beams of 10 MV and above. Photoneutrons add to the shielding requirements.",
           "In the diagnostic range the two main interactions play different parts. Compton scattering is the most frequent interaction in soft tissue above about 30 keV, and it produces the scatter that degrades a radiograph. The photoelectric effect, which depends on Z<sup>3</sup>, produces most of the difference in attenuation between bone and soft tissue, so it forms the contrast."),

    ],
    cards=[
        C("What is the difference between directly and indirectly ionizing radiation?", "Directly ionizing radiation is charged (electrons, protons, α) and ionizes along its own track. Indirectly ionizing radiation (photons, neutrons) first transfers energy to charged particles, which then ionize."),
        C("Write the attenuation law and define μ, HVL, and TVL.", "I = I<sub>0</sub>e<sup>−μx</sup>, with μ the linear attenuation coefficient (1/cm). HVL = 0.693/μ is the thickness that halves the beam, and TVL = 2.303/μ = 3.32 HVL reduces it to 10%."),
        C("Relate the mean free path to the HVL.", "Mean free path = 1/μ = 1.44 HVL."),
        C(f"A lead shield has an HVL of {HVL} cm (illustrative). What thickness gives 1% transmission?", f"About {x1:.0f} cm.", w=[f"log<sub>2</sub>(100) = {n1:.2f} HVLs.", f"{n1:.2f} × {HVL} cm = {x1:.1f} cm.", f"Check: TVL = 3.32 × {HVL} = {tvl:.2f} cm, and 1% is two TVLs = {2*tvl:.1f} cm."]),
        C("What fraction of a narrow beam is transmitted through 5 HVLs?", f"(½)<sup>5</sup> = 1/32 = {t5:.1f}%."),
        C("Why does the HVL of a polyenergetic beam increase as it passes through material?", "Low-energy photons are removed preferentially (beam hardening), so the remaining beam is more penetrating and needs a greater thickness to halve it."),
        C("How does the photoelectric effect depend on Z and E, and where does it dominate in tissue?", "τ/ρ ∝ Z³/E³, with rises at absorption edges. It dominates in tissue below about 30 keV, and in high-Z materials at low and moderate energies."),
        C("How does Compton scattering depend on Z, and why do MV images show little bone contrast?", "Per electron it is independent of Z, so per gram it is nearly the same for all tissues. At MV energies contrast comes from differences in density, not atomic number."),
        C("State the threshold for pair production and what happens to the positron.", "1.022 MeV (2m<sub>e</sub>c²). The excess energy is shared as kinetic energy. The positron slows, annihilates with an electron, and gives two 511 keV photons at about 180°."),
        C("At what energies does each interaction dominate in water?", "Photoelectric below about 30 keV, Compton from about 30 keV to 24 MeV, pair production above about 24 MeV.", fig="interaction_regions"),
        C("A 1.0 MeV photon Compton scatters at 90°. Find the scattered photon and electron energies.", f"Photon {e90:.3f} MeV, electron {1.0-e90:.3f} MeV.", w=[f"E′ = E / [1 + (E/0.511)(1 − cos 90°)] = 1.0 / (1 + {1.0/0.511:.3f}) = {e90:.3f} MeV.", f"Electron = 1.0 − {e90:.3f} = {1.0-e90:.3f} MeV."]),
        C("What are the highest scattered-photon energies at 90° and 180° in Compton scattering?", "They approach 511 keV at 90° and 255 keV at 180° as the incident energy rises, and never exceed them."),
        C("Why does photodisintegration matter for high-energy beams?", "Above its threshold (typically 8–10 MeV or more, depending on the nuclide) a photon can eject a neutron from a nucleus. Beams of 10 MV and above therefore produce photoneutrons, which add to shielding requirements."),
    ],
)

TERMS = ['indirectly ionizing', 'linear attenuation coefficient', 'mass attenuation coefficient', 'build-up factor']

TAKE = [
    [('Photons are indirectly ionizing: the electrons they set in motion deposit the dose.', 'indirect-ionization')],
    [('I = I<sub>0</sub>e<sup>−μx</sup>. HVL = 0.693/μ, TVL = 3.32 HVL, and mean free path = 1.44 HVL.', 'attenuation-curve')],
    [('Photoelectric ∝ Z³/E³ and dominates in tissue below about 30 keV. Compton is nearly independent of Z and dominates from about 30 keV to 24 MeV. Pair production needs 1.022 MeV and dominates above about 24 MeV.', 'interaction-regions-anim')],
    [('Compton: E′ = E / [1 + (E/511 keV)(1 − cos θ)]. The electron gets the most energy at θ = 180°.', 'compton-energies')],
    [('At megavoltage energies in tissue Compton dominates, so MV images show density, not atomic number.', 'mv-contrast'), ('At kilovoltage energies the photoelectric effect (∝ Z³) gives bone–soft-tissue contrast and makes lead and tungsten good shields.', 'pe-z-cubed')],
]


# ---------------------------------------------------------------- practice questions
import math, nistdata as nd
q_th = 0.8 * math.log2(1 / 0.05)
q_tvl = 2.2 * math.log(10) / math.log(2)
_cth = 1 - math.cos(math.radians(45)); q_e45 = 1.0 - 1.0 / (1 + (1.0 / 0.511) * _cth)
q_hvl_w = math.log(2) / (nd.WATER[1.25][0] * nd.DENS["water"])
q_pb = 100 * math.exp(-nd.LEAD[1.25][0] * nd.DENS["lead"] * 3.0)
q_bw6 = nd.BONE[6.0][0] * nd.DENS["bone"] / (nd.WATER[6.0][0] * nd.DENS["water"])

PROBLEMS = [
    PR("Which of these is indirectly ionizing radiation?", "Photons", ["Electrons", "Protons", "α particles"],
       "Photons and neutrons first transfer energy to charged particles, and those charged particles ionize. Electrons, protons, and α particles ionize directly along their own tracks.", lvl="Easy"),
    PR("The attenuation of a narrow beam of monoenergetic photons by a uniform absorber follows:", "I = I<sub>0</sub> e<sup>−μx</sup>", ["I = I<sub>0</sub> / (1 + μx)", "I = I<sub>0</sub> e<sup>+μx</sup>", "I = I<sub>0</sub> − μx"],
       "Each thin layer removes the same fraction of the photons, so the transmitted intensity falls exponentially with thickness. A linear fall would eventually go below zero, and a rising exponential would amplify the beam.", lvl="Easy"),
    PRN(STEM("A lead shield (illustrative value).", ["HVL = 0.80 cm", "required transmission = 5%"], "What [[thickness]] of lead is needed?"), q_th, [0.8 * math.log(20), 0.8 * 5, 0.8 * 20], "{:.2f} cm",
        f"The number of HVLs is log<sub>2</sub>(1/0.05) = {math.log2(20):.2f}, so the thickness is {math.log2(20):.2f} × 0.80 = {q_th:.2f} cm. Using the natural logarithm gives {0.8 * math.log(20):.2f} cm, taking 5 HVLs (3.1% transmitted) gives 4.00 cm, and using the ratio 20 as the number of HVLs gives 16.00 cm.", lvl="Moderate",
        calc=CALC("cm", [TILE("HVL", 0.80, "cm"), TILE("T", 0.05, "", disp="0.05"), TILE("1", 1)], ops=("×", "÷", "log₂(", ")"), solution=["HVL", "×", "log₂(", "1", "÷", "T", ")"])),
    PRN(STEM("A shielding material.", ["HVL = 2.2 cm"], "What is its [[tenth-value layer]]?"), q_tvl, [2 * 2.2, 1.44 * 2.2, 10 * 2.2], "{:.2f} cm",
        f"TVL = ln 10 / μ and HVL = ln 2 / μ, so TVL = (ln 10 / ln 2) × HVL = 3.32 × 2.2 = {q_tvl:.2f} cm. Doubling the HVL gives 4.40 cm, multiplying by 1.44 gives the mean free path ({1.44 * 2.2:.2f} cm), and multiplying by 10 gives 22.0 cm.", lvl="Moderate"),
    PRN(STEM("A narrow beam of Co-60 photons in water. Take the photon energy as 1.25 MeV. Use the table.", ["density of water = 1.00 g/cm³"], "What is the [[half-value layer]] in water?", tables=[nd.table_one("water", [0.5, 1.0, 1.25, 1.5, 2.0])]),
        q_hvl_w, [math.log(2) / nd.WATER[1.25][1], math.log(10) / nd.WATER[1.25][0], math.log(2) / nd.WATER[1.0][0]], "{:.1f} cm",
        f"Read μ/ρ = {nd.WATER[1.25][0]} cm²/g at 1.25 MeV. μ = μ/ρ × ρ = {nd.WATER[1.25][0]} cm<sup>−1</sup>, and HVL = 0.693 / μ = {q_hvl_w:.1f} cm. The energy-absorption column gives {math.log(2) / nd.WATER[1.25][1]:.1f} cm (it answers a different question), using ln 10 gives the TVL ({math.log(10) / nd.WATER[1.25][0]:.1f} cm), and reading the 1.0 MeV row gives {math.log(2) / nd.WATER[1.0][0]:.1f} cm.", lvl="Moderate",
        calc=CALC("cm", [TILE("ln 2", 0.6931, "", disp="0.693", id="ln2"), TILE("μ/ρ", nd.WATER[1.25][0], "cm²/g", id="mr"), TILE("ρ", 1.00, "g/cm³", id="rho")], ops=("×", "÷", "(", ")"), solution=["ln2", "÷", "(", "mr", "×", "rho", ")"])),
    PRN(STEM("A narrow beam of 1.25 MeV photons passes through lead. Use the table.", ["thickness = 3.0 cm", "density of lead = 11.35 g/cm³"], "What [[percentage of the beam]] is transmitted?", tables=[nd.table_one("lead", [0.5, 1.0, 1.25, 1.5, 2.0])]),
        q_pb, [100 * math.exp(-nd.LEAD[1.25][1] * 11.35 * 3.0), 100 * math.exp(-nd.LEAD[1.25][0] * 3.0), 100 * math.exp(-nd.LEAD[1.0][0] * 11.35 * 3.0)], "{:.1f}%",
        f"μ = (μ/ρ) × ρ = {nd.LEAD[1.25][0]} × 11.35 = {nd.LEAD[1.25][0] * 11.35:.3f} cm<sup>−1</sup>. μx = {nd.LEAD[1.25][0] * 11.35 * 3.0:.3f}, so I/I<sub>0</sub> = e<sup>−{nd.LEAD[1.25][0] * 11.35 * 3.0:.3f}</sup> = {q_pb:.1f}%. The energy-absorption column gives {100 * math.exp(-nd.LEAD[1.25][1] * 11.35 * 3.0):.1f}%, leaving out the density gives {100 * math.exp(-nd.LEAD[1.25][0] * 3.0):.1f}%, and reading the 1.0 MeV row gives {100 * math.exp(-nd.LEAD[1.0][0] * 11.35 * 3.0):.1f}%.", lvl="Challenging",
        calc=CALC("", [TILE("100", 100), TILE("μ/ρ", nd.LEAD[1.25][0], "cm²/g", id="mr"), TILE("ρ", 11.35, "g/cm³", id="rho"), TILE("x", 3.0, "cm")], ops=("×", "÷", "(", ")", "e^("), solution=["100", "÷", "e^(", "mr", "×", "rho", "×", "x", ")"])),
    PR("In water, which interaction dominates for photons from about 30 keV to 24 MeV?", "Compton scattering", ["The photoelectric effect", "Pair production", "Coherent scattering"],
       "The photoelectric effect dominates below about 30 keV and pair production above about 24 MeV. In between, which includes every megavoltage therapy beam, Compton scattering dominates.", lvl="Easy"),
    PR("What is the threshold photon energy for pair production in the field of a nucleus?", "1.022 MeV", ["0.511 MeV", "2.044 MeV", "10 MeV"],
       "The photon must supply the rest energy of an electron and a positron, 2 × 0.511 = 1.022 MeV. Triplet production, in the field of an electron, has a threshold of 2.044 MeV. Photodisintegration thresholds are around 8 to 10 MeV.", lvl="Easy"),
    PR("The photoelectric mass attenuation coefficient varies approximately as:", "Z<sup>3</sup> / E<sup>3</sup>", ["Z / E", "Z<sup>2</sup> E", "1/E, independent of Z"],
       "The photoelectric effect rises steeply with atomic number and falls steeply with energy, with sharp rises at absorption edges. This makes lead and tungsten good shields and gives bone strong contrast at kilovoltage energies.", lvl="Moderate"),
    PRN(STEM("A photon is Compton scattered.", ["incident energy = 1.0 MeV", "scattering angle = 45°"], "What kinetic energy does the [[recoil electron]] receive?"), q_e45, [1.0 - q_e45, 1.0 - 1.0 / (1 + (1.0 / 0.511) * math.cos(math.radians(45))), 1.0 - 1.0 / (1 + _cth)], "{:.3f} MeV",
        f"E′ = E / [1 + (E/0.511)(1 − cos θ)] = 1.0 / [1 + 1.957 × {_cth:.4f}] = {1.0 - q_e45:.3f} MeV, so the electron receives 1.0 − {1.0 - q_e45:.3f} = {q_e45:.3f} MeV. The scattered photon energy is {1.0 - q_e45:.3f} MeV. Using cos θ instead of 1 − cos θ gives {1.0 - 1.0 / (1 + (1.0 / 0.511) * math.cos(math.radians(45))):.3f} MeV, and leaving out the 0.511 MeV scale gives {1.0 - 1.0 / (1 + _cth):.3f} MeV.", lvl="Moderate"),
    PRM("Which of the following are true of Compton scattering?", ["Per electron it does not depend on Z", "The electron receives the most energy when the photon is backscattered through 180°", "The scattered photon cannot exceed 511 keV at 90°, however high the incident energy"], ["It produces a characteristic x-ray", "It has a threshold of 1.022 MeV"],
        "Compton scattering is from loosely bound electrons, so per electron it is independent of Z. The electron gets the most energy at 180°. At 90° the scattered photon energy tends to 511 keV as the incident energy rises. Characteristic x-rays follow the photoelectric effect, and the 1.022 MeV threshold belongs to pair production.", lvl="Challenging"),
    PR("Why do megavoltage portal images show little difference between bone and soft tissue per gram?", "Compton scattering dominates, and it depends on electrons per gram, which is nearly the same for both", ["The photoelectric effect dominates and does not depend on Z", "Pair production dominates and cancels the difference", "Coherent scattering dominates at these energies"],
       "At megavoltage energies Compton scattering dominates. It depends on the number of electrons per gram, which is nearly the same for every element except hydrogen. Contrast in a megavoltage image therefore comes mostly from density, not atomic number.", lvl="Moderate"),
    PRN(STEM("Cortical bone and water at a photon energy of 6 MeV. Use the table.", ["density of bone = 1.92 g/cm³", "density of water = 1.00 g/cm³"], "The linear attenuation coefficient of bone is how many [[times that of water]]?", tables=[nd.table_two(["bone", "water"], [0.05, 0.5, 6.0])]),
        q_bw6, [nd.BONE[0.05][0] * 1.92 / nd.WATER[0.05][0], nd.BONE[6.0][0] / nd.WATER[6.0][0], nd.BONE[0.05][0] / nd.WATER[0.05][0]], "{:.2f}",
        f"μ = (μ/ρ) × ρ. At 6 MeV: bone {nd.BONE[6.0][0]} × 1.92 = {nd.BONE[6.0][0] * 1.92:.4f} cm<sup>−1</sup>, water {nd.WATER[6.0][0]} cm<sup>−1</sup>, ratio {q_bw6:.2f}, which is about the density ratio. At this energy the mass coefficients are nearly equal, so contrast comes from density. At 50 keV the same calculation gives {nd.BONE[0.05][0] * 1.92 / nd.WATER[0.05][0]:.2f}, because the photoelectric effect favours bone (higher Z). The per-gram ratios are {nd.BONE[6.0][0] / nd.WATER[6.0][0]:.2f} at 6 MeV and {nd.BONE[0.05][0] / nd.WATER[0.05][0]:.2f} at 50 keV.", lvl="Challenging"),
]
INLINE = {0: [0], 1: [1, 2], 2: [6, 7], 3: [9], 4: [11]}


# ---------------------------------------------------------------- sorting and typed-number questions
_n0 = len(PROBLEMS)
q_pb15 = 100 * math.exp(-nd.LEAD[1.5][0] * nd.DENS["lead"] * 5.0)
q_e60 = 2.0 - 2.0 / (1 + (2.0 / 0.511) * (1 - math.cos(math.radians(60))))
PROBLEMS += [
    SORT("Is each radiation directly or indirectly ionizing?", ["Directly ionizing", "Indirectly ionizing"],
         [("Electrons", 0), ("Protons", 0), ("α particles", 0), ("Photons", 1), ("Neutrons", 1)],
         "Charged particles ionize directly through their electric fields. Photons and neutrons are uncharged, so they ionize indirectly: they first set charged particles in motion (electrons for photons, protons and heavier recoils for neutrons), and those particles do the ionizing.", lvl="Easy"),
    SORT("Which interaction does each statement describe?", ["Photoelectric effect", "Compton scattering", "Pair production"],
         [("Coefficient proportional to Z<sup>3</sup>/E<sup>3</sup>", 0), ("Per electron, independent of Z", 1), ("Needs a photon of at least 1.022 MeV", 2), ("Followed by a characteristic x-ray or Auger electron", 0),
          ("Dominates in water from about 30 keV to 24 MeV", 1), ("Ends with two 511 keV photons", 2), ("The electron gets the most energy when the photon backscatters", 1), ("Gives bone–soft-tissue contrast at kilovoltage energies", 0)],
         "The photoelectric effect depends strongly on Z and E, leaves an inner-shell vacancy, and explains kilovoltage bone contrast. Compton scattering acts on loosely bound electrons, so it does not depend on Z, and it dominates in water across the therapy range. Pair production needs the 1.022 MeV threshold, and the positron later annihilates into two 511 keV photons.", lvl="Moderate"),
    TYPED(STEM("A narrow beam of 1.5 MeV photons strikes a lead shield. Use the table.", ["thickness = 5.0 cm", "density of lead = 11.35 g/cm³"], "What [[percentage of the beam]] is transmitted?", tables=[nd.table_one("lead", [0.5, 1.0, 1.25, 1.5, 2.0])]), q_pb15, 0.02, "%",
          f"At 1.5 MeV, μ/ρ = {nd.LEAD[1.5][0]:.5f} cm²/g, so μ = {nd.LEAD[1.5][0]:.5f} × 11.35 = {nd.LEAD[1.5][0] * 11.35:.4f} cm<sup>−1</sup>. Then μx = {nd.LEAD[1.5][0] * 11.35 * 5:.3f} and e<sup>−μx</sup> = {q_pb15 / 100:.4f}, or {q_pb15:.1f}%.", lvl="Moderate"),
    TYPED(STEM("A photon is Compton scattered.", ["incident energy = 2.0 MeV", "scattering angle = 60°"], "What kinetic energy does the [[recoil electron]] receive?"), q_e60, 0.015, "MeV",
          f"E′ = 2.0 / [1 + (2.0/0.511)(1 − cos 60°)] = 2.0 / {1 + (2.0 / 0.511) * 0.5:.3f} = {2.0 - q_e60:.3f} MeV. The electron receives the difference: 2.0 − {2.0 - q_e60:.3f} = {q_e60:.3f} MeV.", lvl="Moderate"),
]
INLINE = {0: [1, _n0 + 1], 1: [2, 3, _n0 + 3], 2: [7, 8, _n0 + 2], 3: [10, _n0 + 4], 4: [12]}


# ---------------------------------------------------------------- tap-the-figure questions
_mu = 0.2
_fig_att = FS(x=dict(min=0, max=14, ticks=[0, 2, 4, 6, 8, 10, 12, 14], label="Thickness of absorber (cm)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Transmitted (%)", fmt="pct"),
              series=[dict(pts=PTS(lambda x: 100 * math.exp(-_mu * x), 0, 14), color="plot-1")], xunit=" cm", xdec=1, xname="Thickness", label="Narrow-beam transmission against absorber thickness")
_fig_en = lambda: FS(x=dict(min=0.01, max=100, log=True, ticks=[0.01, 0.1, 1, 10, 100], label="Photon energy (MeV), log scale"), y=dict(min=0, max=1, ticks=[]), xunit=" MeV", xname="Energy", label="A photon energy axis in MeV", h=170)
_n1 = len(PROBLEMS)
PROBLEMS += [
    FIGQ(STEM("A narrow photon beam is attenuated by a uniform absorber, as shown.", [], "Tap the [[thickness that halves the beam]] on the thickness axis."), _fig_att, [(math.log(2) / _mu - 0.5, math.log(2) / _mu + 0.5)],
         "This thickness is the half-value layer, which cuts the beam to 50%. Follow the 50% line to the curve and read the thickness: ln 2 / 0.2 cm<sup>−1</sup> = 3.5 cm.", lvl="Easy", note="about 3.5 cm"),
    FIGQ(STEM("A narrow photon beam is attenuated by a uniform absorber, as shown.", [], "Tap the [[thickness that leaves one eighth of the beam]]."), _fig_att, [(3 * math.log(2) / _mu - 0.7, 3 * math.log(2) / _mu + 0.7)],
         "One eighth is (½)<sup>3</sup>, so the beam has passed through three half-value layers: 3 × 3.47 = 10.4 cm. The 12.5% level is not marked, so the thickness is found from the half-value layer, which can be read at 50%.", lvl="Moderate", note="about 10.4 cm"),
    FIGQ(STEM("Water, photon energy on a logarithmic axis.", [], "Tap an [[energy at which Compton scattering dominates]]."), _fig_en(), [(0.03, 24)],
         "In water, Compton scattering dominates from about 30 keV to 24 MeV. Below that the photoelectric effect wins, and above it pair production. Every megavoltage therapy beam sits inside the Compton range.", lvl="Moderate", note="0.03 to 24 MeV"),
    FIGQ(STEM("Photon energy on a logarithmic axis.", [], "Tap the [[threshold energy for pair production]]."), _fig_en(), [(0.8, 1.3)],
         "The photon must supply the rest energy of an electron and a positron, 2 × 0.511 = 1.022 MeV, so that is the threshold. Pair production only becomes the dominant process much higher, near 24 MeV in water.", lvl="Moderate", note="1.022 MeV"),
]
INLINE.setdefault(1, []).extend([_n1 + 1, _n1 + 2]); INLINE.setdefault(2, []).extend([_n1 + 3, _n1 + 4])


# ---------------------------------------------------------------- interaction share against contrast, and the build-up factor
_n2 = len(PROBLEMS)
_hvl_b, _B, _T = 0.80, 2.0, 0.010
x_broad = _hvl_b * math.log2(_B / _T)                                              # B e^(-mu x) = T, so the beam must be attenuated to T / B
PROBLEMS += [
    PRM("A radiograph is made at 100 kVp, with an effective photon energy of about 50 keV. Which of the following statements about soft tissue and bone are correct?", ["Most of the interactions in soft tissue are Compton scattering", "The photoelectric effect, which varies roughly as Z<sup>3</sup>, produces most of the contrast between bone and soft tissue"],
        ["Most of the interactions in soft tissue are photoelectric absorption", "Compton scattering produces most of the contrast, because bone has many more electrons per gram", "Pair production accounts for a few percent of the interactions in bone"],
        "At 50 keV Compton scattering accounts for roughly 80% of the attenuation in water. The photoelectric effect rises steeply with Z, so that bone attenuates about 1.9 times as much per gram as water at 50 keV, against 1.1 times at 100 keV, while the number of electrons per gram differs little. Pair production needs a photon of more than 1.022 MeV.", lvl="Challenging"),
    PRN(STEM("A lead barrier must reduce a beam to 1.0% of the unshielded intensity. Narrow-beam measurements give an HVL of 0.80 cm of lead (illustrative). Scatter in the barrier gives a build-up factor of 2.0, taken as constant.", [], "What [[thickness]] is needed?"), x_broad,
        [_hvl_b * math.log2(1 / (_T * _B)), _hvl_b * math.log2(1 / _T), _hvl_b * math.log2(1 / _T) + _B * _hvl_b], "{:.1f} cm",
        f"With the build-up factor the transmission is B e<sup>−μx</sup>, so the barrier has to attenuate the beam to 0.010 / 2.0 = 0.0050. That is log<sub>2</sub>(200) = {math.log2(_B / _T):.2f} half-value layers, and x = 0.80 × {math.log2(_B / _T):.2f} = {x_broad:.1f} cm. The narrow-beam value is {_hvl_b * math.log2(1 / _T):.1f} cm, putting B on the wrong side gives {_hvl_b * math.log2(1 / (_T * _B)):.1f} cm, and adding B × HVL gives {_hvl_b * math.log2(1 / _T) + _B * _hvl_b:.1f} cm.", lvl="Challenging"),
    PR("In a narrow-beam measurement of attenuation, the small detector behind the absorber registers:", "only photons that crossed the absorber without interacting", ["the photons scattered in the absorber, as in a broad beam", "more photons than were incident, because of the build-up factor", "photons whose number follows I = I<sub>0</sub> e<sup>+μx</sup>"],
       "The beam is collimated and the detector is small and far from the absorber, so scattered photons miss it. Only then does the transmission follow I = I<sub>0</sub> e<sup>−μx</sup>. In a broad beam the scatter raises the reading by the build-up factor.", lvl="Easy"),
]
INLINE.setdefault(1, []).append(_n2 + 3)
INLINE.setdefault(4, []).append(_n2 + 1)
