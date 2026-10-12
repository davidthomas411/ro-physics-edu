from blocks import *
import math, calc
import beamdata as bd

layers = [(3.0, 1.0), (6.0, 0.3), (3.0, 1.0)]                       # thickness (cm), density (g/cm3): soft tissue, lung, soft tissue
rad = sum(t * r for t, r in layers); phys = sum(t for t, _ in layers)
_tmr_simple = lambda d: math.exp(-0.0282 * (d - 1.5))                  # the one-line TMR given in the example, so it can be followed by hand
ratio_lung = _tmr_simple(rad) / _tmr_simple(phys)                       # dose from the radiological depth against the physical depth
rad_typed = 2.0 * 1.0 + 5.0 * 0.25 + 4.0 * 1.0                       # 2 cm tissue, 5 cm lung of density 0.25, 4 cm tissue
MU, LK = 0.045, 0.35                                                 # attenuation per cm and kernel length (cm) of the one-dimensional illustration
dose_1d = lambda d: (math.exp(-MU * d) - math.exp(-d / LK)) / (1 - MU * LK)
dmax_1d = LK * math.log(1 / (MU * LK)) / (1 - MU * LK)

TOPIC = dict(
    id="dose-algorithms", domain=3, sub="III.A", title="Photon dose calculation algorithms",
    ref=dict(aapm="", khan="10", ford="12"),
    guide=[
        H("TERMA and kernels"),
        P("The planning system represents the patient as a grid of voxels, typically 2 to 4 mm on a side, and calculates the dose in each one. Many algorithms work in two steps. [[1|The first finds the TERMA, the total energy released per unit mass, in every voxel.]] For each voxel the system traces a line from the source and finds the radiological path length: the path length weighted by density, using the density from the CT scan. [[1|The photon fluence, and then the TERMA, follow from the attenuation along that path.]]"),
        P("The second step spreads the energy. Energy released in one voxel is not deposited there, because scattered photons and the electrons they set in motion carry it to neighbouring voxels. A kernel describes how the energy released at a point is distributed around it. [[1|The dose is the convolution of the TERMA with the kernel.]] Kernels are calculated with Monte Carlo simulation, and their size and shape depend on the beam energy. Many algorithms scale the kernel with density, so it is larger in lung, where electrons travel farther."),
        EQ("[[1|D = TERMA ⊗ kernel]]", "radiological path length = Σ ρ<sub>i</sub> Δx<sub>i</sub>   (density times thickness, summed along the ray)"),
        EX("Radiological path length", STEM("A ray crosses three layers on its way to a point.", ["3.0 cm of soft tissue, ρ = 1.0 g/cm³", "6.0 cm of lung, ρ = 0.3 g/cm³", "3.0 cm of soft tissue, ρ = 1.0 g/cm³"], "Find the [[radiological path length]]."),
           ["3.0 × 1.0 + 6.0 × 0.3 + 3.0 × 1.0 = 3.0 + 1.8 + 3.0"], f"{rad:.1f} g/cm², compared with a physical depth of {phys:.0f} cm."),
        EX("Dose beyond lung", STEM("A ray that crosses lung, for a 10 × 10 cm field.", ["TMR(d) = e<sup>−0.0282 (d − 1.5)</sup>", f"physical depth = {phys:.0f} cm,   radiological depth = {rad:.1f} cm"], "How many [[times larger]] is the dose from the radiological depth than from the physical depth?"),
           [f"TMR({rad:.1f}) = e<sup>−0.0282 × {rad - 1.5:.1f}</sup> = {_tmr_simple(rad):.3f}", f"TMR({phys:.0f}) = e<sup>−0.0282 × {phys - 1.5:.1f}</sup> = {_tmr_simple(phys):.3f}"], f"{ratio_lung:.3f}: about {100 * (ratio_lung - 1):.0f}% more dose, because the lung attenuates less than the same thickness of soft tissue."),

        H("Algorithm classes"),
        P("Algorithms differ in how much of the physics they model, and accuracy generally rises with run time. Correction-based methods, such as Clarkson integration and tissue-air ratios, resemble the TMR calculation of the monitor-unit chapter with empirical corrections for patient shape and density. They do not follow scatter in three dimensions. Pencil beam algorithms add the dose of many narrow beams using a kernel. Convolution algorithms with a kernel that does not change with density are fast but treat lung poorly."),
        P("Convolution and superposition algorithms with a density-scaled kernel, including the collapsed cone method and the analytical anisotropic algorithm (AAA), are accurate in most situations and include a model of the source in the head of the machine. Acuros XB solves the linear Boltzmann transport equation on a grid. Monte Carlo follows individual particle histories, simulating billions of them, and is the reference standard for accuracy, at the cost of run time and statistical noise."),
        TABLE(["Algorithm", "Idea", "Accuracy"],
              [["Correction-based (Clarkson, TAR)", "Tabulated factors with empirical corrections", "[[1|Lowest]]"], ["Pencil beam", "Sum of narrow beams with a depth kernel", "[[1|Low]]"], ["Convolution / superposition", "TERMA convolved with a density-scaled kernel", "[[1|Good]]"],
               ["Acuros XB", "Boltzmann transport equation on a grid", "[[1|High]]"], ["Monte Carlo", "Individual particle histories", "[[1|Reference standard]]"]]),

        H("Beam model and dose reporting"),
        P("Whatever the algorithm, the planning system needs a beam model: [[1|a description of the source and of the devices that shape the beam, such as the MLC, with parameters fitted to measured data.]] [[1|The photon energy spectrum sets the slope of the PDD, because a harder spectrum falls off more slowly. The flux of electrons from the head sets the dose near the surface. The size of the source sets the penumbra.]] Some systems let the user adjust many parameters and others lock most of them."),
        P("Dose can be reported as dose to water or dose to the medium. They differ because the stopping powers of the secondary electrons differ between tissue and water. Averaged over tissues, dose to medium is about 1% lower than dose to water. Current recommendations favour commissioning the system to report dose to medium (AAPM TG-329)."),

        H("Lung and bone"),
        P("The planning system converts the CT number of each voxel to density with a CT-to-density calibration, set up by scanning a phantom with inserts of known density. Lung has a density near 0.3 g/cm³ and compact bone about 1.85 g/cm³."),
        P("[[1|In lung the beam is attenuated less, so the dose beyond the lung is higher than a water-equivalent calculation predicts. The penumbra is wider because the electrons travel farther,]] and the effect is larger at higher energy. In small fields in lung, methods built on TMR-like corrections are the least accurate, and Monte Carlo is the most accurate. [[1|In bone the beam is attenuated more,]] and the soft tissue immediately beyond the bone receives extra dose from backscattered electrons. At about 6 MV the dose inside bone is close to the dose in soft tissue, [[1|but at higher energies pair production, which grows with atomic number, raises the dose in bone.]]"),
    ],
    cards=[
        C("What is a voxel in dose calculation, and how big is it?", "A three-dimensional pixel of the dose grid, typically 2 to 4 mm on a side."),
        C("What does TERMA stand for?", "Total energy released per unit mass: the energy released by photon interactions at a point, before it is spread by the kernel."),
        C("What is the radiological path length?", "The path length through the patient weighted by density, Σ ρ Δx, using densities from the CT scan."),
        C("What does a kernel describe?", "How the energy released at one point is distributed around it by scattered photons and secondary electrons."),
        C("Write the convolution dose calculation.", "Dose = TERMA convolved with the kernel."),
        C("How does the kernel change in lung?", "A density-scaled kernel is larger in lung, because the electrons travel farther."),
        C("List the dose algorithms in order of increasing accuracy.", "Correction-based (Clarkson, TAR), pencil beam, convolution/superposition, Acuros XB, Monte Carlo."),
        C("Why is Monte Carlo the reference standard, and what is its drawback?", "It follows individual particle histories with the full interaction physics. It is slow and has statistical noise."),
        C("What does a TPS beam model include?", "A model of the source and of the beam-shaping devices such as the MLC, with parameters fitted to measured data."),
        C("Which physical parameters of the beam model set the PDD slope, the superficial dose, and the penumbra?", "The photon spectrum sets the PDD slope, the electron flux from the head sets the superficial dose, and the source size sets the penumbra."),
        C("How is the CT number converted to density?", "With a CT-to-density calibration, made by scanning a phantom with inserts of known density."),
        C("What does lung do to the dose distribution?", "Less attenuation, so higher dose beyond the lung, and a wider penumbra, more so at higher energy."),
        C("How does the dose in bone compare with soft tissue at 6 MV and at higher energy?", "Close to soft tissue at about 6 MV. Higher at greater energies, because pair production grows with atomic number."),
    ],
)

PROBLEMS = [
    PR("In convolution dose calculation, the TERMA is:", "the energy released per unit mass by photon interactions at a point, before it is spread by the kernel", ["the dose after the kernel has been applied", "the number of photons per unit area", "the range of the secondary electrons"],
       "TERMA is calculated from the photon fluence along the radiological path. The kernel then spreads that energy to give the dose.", lvl="Easy"),
    PR("Which dose calculation algorithm is generally regarded as the most accurate?", "Monte Carlo", ["Clarkson integration", "Pencil beam", "Tissue-air ratio with corrections"],
       "Monte Carlo follows particle histories with the full interaction physics and is used to benchmark the others.", lvl="Easy"),
    PR("Compared with soft tissue, a density-scaled dose kernel in lung is:", "larger, because the electrons travel farther", ["smaller, because there is less scatter", "the same", "more asymmetric only"],
       "Electron range scales inversely with density, so the energy is spread over a larger region in lung.", lvl="Easy"),
    PR("The radiological path length through a voxel is:", "its thickness multiplied by its density relative to water", ["its thickness only", "its density only", "its thickness divided by its density"],
       "The attenuation of the beam depends on the mass thickness, so the path length is weighted by density.", lvl="Moderate"),
    PRN(STEM("A ray crosses three layers.", ["3.0 cm of soft tissue, ρ = 1.0 g/cm³", "6.0 cm of lung, ρ = 0.3 g/cm³", "3.0 cm of soft tissue, ρ = 1.0 g/cm³"], "What is the [[radiological path length]]?"), rad, [phys, 6 * 0.3, 6.0], "{:.1f} g/cm²",
        f"Σ ρ Δx = 3.0 + 1.8 + 3.0 = {rad:.1f} g/cm². The physical depth is {phys:.0f} cm. Using the lung alone gives 1.8, and the soft tissue alone gives 6.0.", lvl="Moderate"),
    PRM("Which parameters of a beam model are fitted to measured data?", ["The photon energy spectrum, which sets the PDD slope", "The electron flux from the head, which sets the superficial dose", "The size of the source, which sets the penumbra"], ["The weight of the patient", "The slice thickness of the CT scan"],
        "The beam model describes the machine, and its parameters are tuned so that the calculation matches measurements in a water tank. Patient properties are not part of it.", lvl="Moderate"),
    PR("Beyond a slab of lung, the dose calculated with a heterogeneity correction, compared with a calculation that treats the patient as water, is:", "higher", ["lower", "the same", "zero"],
       "The lung attenuates the beam less than the same thickness of water, so more dose arrives beyond it.", lvl="Moderate"),
    PR("Within bone, compared with soft tissue, the dose from an 18 MV beam is:", "somewhat higher, because pair production grows with atomic number", ["lower, because bone is denser", "the same at every energy", "much lower, because bone absorbs electrons"],
       "At about 6 MV the two are similar. At higher energy pair production, which depends on Z, adds dose in bone.", lvl="Challenging"),
]

INLINE = {0: [1, 3, 4, 5], 1: [2, 9], 2: [6], 3: [7]}

TERMS = ['TERMA', 'kernel', 'radiological path length', 'convolution', 'Monte Carlo']

TAKE = [
    [('TERMA is the energy released per unit mass from the fluence along the radiological path. The dose is the TERMA spread by a kernel: D = TERMA ⊗ kernel.', 'terma-kernel')],
    [('Accuracy rises from correction-based methods to pencil beam, convolution/superposition, Acuros XB, and Monte Carlo.', 'algorithm-ladder')],
    [('The beam model is fitted to measured data: the spectrum sets the PDD slope, head electrons set the superficial dose, and the source size sets the penumbra.', 'beam-model')],
    [('In lung the beam is attenuated less and the penumbra is wider. In bone attenuation rises, and above about 6 MV pair production raises the dose within bone.', 'lung-bone')],
]


# ---------------------------------------------------------------- matching, ranking, typed, and tap-the-figure questions
PROBLEMS += [
    SORT("Match each algorithm to its central idea.", ["Correction-based (Clarkson, TAR)", "Pencil beam", "Convolution / superposition", "Acuros XB", "Monte Carlo"],
         [("Tabulated factors with empirical corrections for shape and density", 0), ("A sum of narrow beams, each with a depth kernel", 1), ("TERMA convolved with a density-scaled kernel", 2), ("The Boltzmann transport equation solved on a grid", 3), ("Individual particle histories sampled at random", 4)],
         "Each class models more of the physics than the one before it. Correction-based methods use tables. Pencil beams add kernels. Convolution spreads TERMA in three dimensions. Acuros XB solves the transport equation, and Monte Carlo simulates the particles.", lvl="Moderate", mode="match", cap=1),
]


# ---------------------------------------------------------------- the edge of a lung tumour
PROBLEMS += [
    PR("A 2 cm lung tumour is treated with 6 MV through small fields. The plan, calculated with an algorithm that scales only the primary beam by the radiological path length, is recalculated with Monte Carlo at the same monitor units. Which change at the edge of the tumour is most likely?", "a lower dose and a wider penumbra, because lateral electron equilibrium is lost in the low-density lung", ["a higher dose, because lung attenuates the beam less than water", "no change, because both calculations use the same CT densities", "a higher dose and a sharper penumbra, because the scatter in lung is lower"],
       "Secondary electrons travel far in lung and leave a small field sideways. A path-length correction scales the primary attenuation only, so it overestimates the dose at the edge and underestimates the width of the penumbra. The smaller attenuation in lung is the effect that the correction does model.", lvl="Challenging"),
]
