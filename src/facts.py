"""Titles for the flash cards. A flash card is a fact: a short label on top and the fact below, never a question.
The text under each title is the card's answer. Card ids are topic:number, in the order the cards are written in the topic file."""
_RAW = r"""
waves-photons:1|Speed, frequency, and wavelength of an electromagnetic wave
waves-photons:2|Photon energy from frequency and wavelength
waves-photons:3|hc in practical units
waves-photons:4|Electromagnetic spectrum by photon energy
waves-photons:5|X-rays and γ-rays
waves-photons:6|Doubling the intensity of a monochromatic beam
waves-photons:7|The electron volt in joules
waves-photons:8|De Broglie relation
particles-energy:1|Rest energies of the electron and the proton
particles-energy:2|One atomic mass unit in MeV
particles-energy:3|Total, kinetic, and rest energy
particles-energy:4|Validity of KE = ½mv²
particles-energy:5|Positron–electron annihilation at rest
particles-energy:6|Pair production threshold
particles-energy:7|Speed of a 20 MeV electron and a 150 MeV proton
charges-atom:1|Coulomb's law
charges-atom:2|Magnetic force on a moving charge
charges-atom:3|Circular path in a uniform magnetic field
charges-atom:4|Rutherford's gold-foil experiment
charges-atom:5|Hydrogen energy levels and ionization energy
charges-atom:6|Excitation and ionization
charges-atom:7|Characteristic x-ray production
charges-atom:8|Auger electron
charges-atom:9|Electron binding energy by shell and atomic number
nuclear-structure:1|Z, N, and A
nuclear-structure:2|Isotopes, isotones, isobars, and isomers
nuclear-structure:3|Size of the nucleus and of the atom
nuclear-structure:4|Nuclear force and the neutron excess of heavy nuclei
nuclear-structure:5|Mass defect and binding energy
nuclear-structure:6|Binding energy of the deuteron
nuclear-structure:7|Binding energy per nucleon
nuclear-structure:8|Energy release in fusion and fission
nuclear-structure:9|Energy of D–T fusion and of U-235 fission
decay-modes:1|β⁻ decay of a neutron-rich nucleus
decay-modes:2|Ra-226 α decay
decay-modes:3|β⁺ decay and electron capture: the energy condition
decay-modes:4|γ emission and internal conversion
decay-modes:5|I-125 decay and its photons
decay-modes:6|Ir-192 decay modes and photon energies
decay-modes:7|Range of α particles
decay-schemes:1|Arrows in a decay scheme
decay-schemes:2|Continuous and discrete spectra
decay-schemes:3|Continuous β spectrum
decay-schemes:4|Co-60 emissions
decay-schemes:5|Origin of the 662 keV photon of Cs-137
decay-schemes:6|Reading Co-59(n,γ)Co-60
decay-schemes:7|Production route and decay mode
decay-schemes:8|Production of Ir-192 and Co-60
decay-schemes:9|Production of F-18 and Mo-99
decay-schemes:10|Radionuclide generator
decay-law:1|Decay constant λ
decay-law:2|Decay law for nuclei and for activity
decay-law:3|Becquerel and curie: 5 mCi in MBq
decay-law:4|Half-life, decay constant, and mean life
decay-law:5|Activity left after one mean life
decay-law:6|Fraction left after 4 and after 10 half-lives
decay-law:7|I-125 seed: time to 10% of its activity
decay-law:8|Ir-192: percentage lost per day
decay-law:9|Total dose of a permanent implant
specific-activity:1|Specific activity and its units
specific-activity:2|Specific activity formula
specific-activity:3|Factors that raise specific activity
specific-activity:4|Specific activity ranking of brachytherapy nuclides
specific-activity:5|Specific activity of Ra-226
specific-activity:6|Real sources and the theoretical specific activity
specific-activity:7|High specific activity in HDR brachytherapy
specific-activity:8|Specific activity in radiopharmaceutical therapy
equilibrium:1|Transient equilibrium
equilibrium:2|Secular equilibrium
equilibrium:3|Examples of transient and secular equilibrium
equilibrium:4|Transient equilibrium ratio for Mo-99 and Tc-99m
equilibrium:5|Tc-99m peak after elution
equilibrium:6|Daughter half-lives to reach secular equilibrium
photon-interactions:1|Directly and indirectly ionizing radiation
photon-interactions:2|Attenuation law, μ, HVL, and TVL
photon-interactions:3|Transmission through 5 HVLs
photon-interactions:4|Beam hardening of a polyenergetic beam
photon-interactions:5|Photoelectric effect: dependence on Z and E
photon-interactions:6|Compton scattering: dependence on Z and MV image contrast
photon-interactions:7|Pair production threshold and the positron
photon-interactions:8|Energy ranges of the photon interactions in water
photon-interactions:9|Compton scattering of a 1.0 MeV photon at 90°
photon-interactions:10|Highest scattered-photon energies at 90° and 180°
photon-interactions:11|Photodisintegration in high-energy beams
kerma-dose:1|Fluence and energy fluence
kerma-dose:2|Kerma and energy fluence
kerma-dose:3|Kerma and absorbed dose
kerma-dose:4|Kerma and collision kerma
kerma-dose:5|D and K<sub>col</sub> in each region
kerma-dose:6|Dose above K<sub>col</sub> beyond d<sub>max</sub>
kerma-dose:7|Exposure: definition, unit, and energy limit
kerma-dose:8|Dose per roentgen from W<sub>air</sub>/e
kerma-dose:9|Equivalent dose, effective dose, and w<sub>R</sub>
kerma-dose:10|Gy, cGy, rad, Sv, and rem
pdd:1|Dose build-up below the surface
pdd:2|d<sub>max</sub> and its change with energy
pdd:3|Surface dose of 6 MV and 15 MV beams
pdd:4|Percent depth dose
pdd:5|Dependence of the PDD
pdd:6|PDD and field size
pdd:7|PDD and SSD
pdd:8|Mayneord F factor and its assumption
pdd:9|PDD at SSD 120 cm from the value at 100 cm
pdd:10|Field size at depth in a diverging beam
pdd:11|PDD falling with depth beyond d<sub>max</sub>
tmr:1|Purpose of the TMR
tmr:2|Tissue maximum ratio
tmr:3|TMR at d<sub>max</sub>
tmr:4|Dependence of the TMR
tmr:5|PDD and TMR techniques
tmr:6|Measuring a TMR
tmr:7|TMR and TPR
tmr:8|TMR at 10 cm from a PDD of 67.0%
tmr:9|Inverse-square factor in the PDD-to-TMR conversion
tmr:10|Field size for a PDD and for a TMR
scatter:1|Sources of field-size dependence of output
scatter:2|Collimator scatter factor S<sub>c</sub>
scatter:3|Phantom scatter factor S<sub>p</sub>
scatter:4|Total scatter factor S<sub>cp</sub>
scatter:5|Effect of a block on S<sub>c</sub> and S<sub>p</sub>
scatter:6|Equivalent square of a 6 × 18 cm field
scatter:7|Area-to-perimeter rule
scatter:8|Clarkson integration
scatter:9|S<sub>cp</sub> from S<sub>c</sub> = 0.985 and S<sub>p</sub> = 0.990
scatter:10|Output and field size
scatter:11|Build-up cap on the S<sub>c</sub> chamber
mu-calc:1|Hand monitor unit calculation
mu-calc:2|Dose per MU, SSD technique
mu-calc:3|Dose per MU, SAD technique
mu-calc:4|Fields used for S<sub>c</sub> and S<sub>p</sub>
mu-calc:5|Collimator setting for 12 × 12 cm at SSD 120 cm
mu-calc:6|MU for 200 cGy at 8 cm depth, SSD 100 cm
mu-calc:7|MU for 200 cGy at 8 cm depth, SSD 120 cm
mu-calc:8|MU per field for a 6 MV AP/PA pair
mu-calc:9|MU rise at an extended SSD
mu-calc:10|Wedge factor 0.60 and the MU
mu-calc:11|SSD calibration and SAD calibration
mu-calc:12|Inverse-square term rule
profiles:1|Beam profile
profiles:2|Field edge on a profile
profiles:3|80%–20% penumbra
profiles:4|Contributions to the penumbra
profiles:5|Geometric penumbra
profiles:6|Geometric penumbra: source size, SSD, depth, and SCD
profiles:7|Radiological penumbra: energy and density
profiles:8|Flattening depth of a linac profile
profiles:9|Horns
profiles:10|Profile shape against depth
profiles:11|Harder spectrum on the axis
profiles:12|Sources of out-of-field dose
profiles:13|Planning systems and out-of-field dose
skin-bolus:1|Basal layer of the skin
skin-bolus:2|Skin dose of a 6 MV beam
skin-bolus:3|Origin of the skin dose
skin-bolus:4|Skin dose and field size
skin-bolus:5|Skin dose and beam energy
skin-bolus:6|Skin dose and beam angle
skin-bolus:7|Effects of the couch
skin-bolus:8|Devices that raise the skin dose
skin-bolus:9|Block tray position
skin-bolus:10|Bolus
skin-bolus:11|Dose below the skin with bolus
skin-bolus:12|Bolus thickness for d<sub>max</sub> at the skin
skin-bolus:13|MU with bolus over a deep target
skin-bolus:14|Air gap under bolus
dose-algorithms:1|Voxel
dose-algorithms:2|TERMA
dose-algorithms:3|Radiological path length
dose-algorithms:4|Kernel
dose-algorithms:5|Convolution dose calculation
dose-algorithms:6|Kernel in lung
dose-algorithms:7|Dose algorithms by accuracy
dose-algorithms:8|Monte Carlo
dose-algorithms:9|TPS beam model
dose-algorithms:10|Beam-model parameters and what they set
dose-algorithms:11|CT-to-density calibration
dose-algorithms:12|Lung in the dose distribution
dose-algorithms:13|Dose in bone by energy
brachy-sources:1|ICRU 38 dose-rate classes
brachy-sources:2|Permanent and temporary brachytherapy
brachy-sources:3|LDR seed isotopes
brachy-sources:4|Ir-192 decay and photon energy
brachy-sources:5|Ir-192 half-life
brachy-sources:6|I-125 and Pd-103: half-lives and photon energies
brachy-sources:7|Phase-out of Cs-137 and Ra-226
brachy-sources:8|Seed capsule
brachy-sources:9|Remote afterloader
brachy-sources:10|Low-energy photons in LDR seeds
brachy-sources:11|Brachytherapy without seeds
brachy-exposure:1|Exposure
brachy-exposure:2|Exposure rate from a point source
brachy-exposure:3|Exposure rate constant Γ
brachy-exposure:4|Ir-192 and I-125 at equal activity
brachy-exposure:5|Inverse-square law
brachy-exposure:6|Air kerma strength
brachy-exposure:7|Units of air kerma strength
brachy-exposure:8|Air kerma strength from Γ and activity
brachy-exposure:9|W/e for dry air
brachy-exposure:10|Ordering seeds by air kerma strength
brachy-exposure:11|Decay of air kerma strength
tg43:1|TG-43 dose rate equation
tg43:2|TG-43 reference point
tg43:3|Dose rate at the reference point
tg43:4|Dose rate constant Λ
tg43:5|Geometry function G
tg43:6|Line-source geometry function
tg43:7|Radial dose function g(r)
tg43:8|g(r) and photon energy
tg43:9|Anisotropy function F(r, θ)
tg43:10|Using φ<sub>an</sub> = 1 in a prostate implant
tg43:11|Total dose of a permanent implant
tg43:12|Implant dose in one half-life and in 3.3 half-lives
tg43:13|Starting dose rates of Pd-103 and I-125
"""
TITLES = dict(l.split("|", 1) for l in _RAW.strip().split("\n"))

# The first line of an answer, reworded where it was written as a reply to its question. The rest of the answer and the working stay as written.
HEADS = {
    "nuclear-structure:9": "Fusion and fission both move nuclei toward the peak of the binding-energy curve, where they are more tightly bound. The extra binding energy is released.",
    "decay-modes:7": "γ emission and internal conversion both release nuclear excitation energy without changing Z or A.",
    "decay-law:8": "197 d: the activity of an I-125 seed (T<sub>1/2</sub> = 59.4 d) falls to 10% after 3.32 half-lives.",
    "equilibrium:5": "A<sub>d</sub>/A<sub>p</sub> = 1.10 for Mo-99 (65.9 h) and Tc-99m (6.01 h), ignoring branching.",
    "scatter:6": "9.0 cm: s = 2ab/(a + b) for a 6 × 18 cm rectangle.",
    "scatter:9": "S<sub>cp</sub> = 0.975, the product of S<sub>c</sub> = 0.985 and S<sub>p</sub> = 0.990.",
    "mu-calc:6": "262 MU for a 6 MV beam calibrated 1 cGy/MU at d<sub>max</sub> = 1.5 cm, with S<sub>c</sub> = 1.012, S<sub>p</sub> = 1.008, and PDD = 74.8%.",
    "mu-calc:8": "121 MU per field for 100 cGy per field at an 11 cm mid-plane isocenter, with S<sub>c</sub> = 1.021, S<sub>p</sub> = 1.013, and TMR = 0.776.",
    "profiles:13": "The planning system predicts dose far from the field poorly and should not be used for it. AAPM TG-158 covers out-of-field dose.",
}
