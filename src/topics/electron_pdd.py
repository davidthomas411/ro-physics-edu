from blocks import *
import math, calc
from curves import pchip

r90 = lambda E: E / 3.3
r80 = lambda E: E / 3.0
r50 = lambda E: E / 2.33
rp = lambda E: E / 2.0
dref = lambda E: 0.6 * r50(E) - 0.1
def pdd_e(E):
    """A schematic electron PDD through the R90, R80, R50, and practical-range points of the rules of thumb."""
    a, b, c, d = r90(E), r80(E), r50(E), rp(E)
    return pchip([0, .5 * a, .75 * a, a, b, (b + c) / 2, c, (c + d) / 2, d, d + 1.5, d + 6], [85, 99, 100, 90, 80, 66, 50, 24, 4, 2.5, 1.5])
E_need = 3.3 * 3.0                                                       # energy whose R90 is 3.0 cm

TOPIC = dict(
    id="electron-pdd", domain=3, sub="III.B", title="Electron beam depth dose and range",
    ref=dict(aapm="TG-25, TG-51", khan="14", ford="15"),
    guide=[
        H("Shape of the electron depth dose"),
        P("Electrons lose energy continuously as they travel through tissue and stop at a finite depth. If all the electrons had the same energy and travelled in straight lines, they would all stop at about the same depth and the PDD would fall off sharply there. A real beam has a spectrum of energies, and the higher-energy electrons go farther. Electrons also change direction by Coulomb scattering. Both effects spread the fall-off over a range of depths."),
        P("The PDD of an electron beam has a surface dose that is already high, a broad region of maximum dose, a steep fall-off, and a small tail at depth. The tail is not electrons, because they have stopped. It is bremsstrahlung photons, produced in the head of the linac, mainly in the scattering foil, and in the patient. This photon contamination is about 1% to 5% of the maximum dose and is larger at higher energy, because the radiative stopping power rises with energy."),

        H("Range parameters and rules of thumb"),
        P("The PDD is described by the depths at which the dose has fallen to a given percentage of the maximum: R<sub>90</sub>, R<sub>80</sub>, and R<sub>50</sub>. The practical range R<sub>p</sub> is the depth where the steepest part of the fall-off, extended as a straight line, meets the bremsstrahlung tail. It is close to the greatest depth that electrons reach."),
        EQ("R<sub>90</sub> ≈ E / 3.3     R<sub>80</sub> ≈ E / 3     R<sub>50</sub> ≈ E / 2.33     R<sub>p</sub> ≈ E / 2", "depths in cm for a beam energy E in MeV"),
        P("The electron dose maximum covers a wide range of depths, so calibration is not done at d<sub>max</sub>. The reference depth is d<sub>ref</sub> = 0.6 R<sub>50</sub> − 0.1 cm, which is the calibration depth in dosimetry protocols and plays the role that d<sub>max</sub> plays for photons."),
        TABLE(["Energy (MeV)", "R<sub>90</sub> (cm)", "R<sub>80</sub> (cm)", "R<sub>50</sub> (cm)", "R<sub>p</sub> (cm)"], [[str(E), f"{r90(E):.1f}", f"{r80(E):.1f}", f"{r50(E):.1f}", f"{rp(E):.1f}"] for E in (6, 9, 12, 16, 20)]),
        EX("Range parameters of a 12 MeV beam", STEM("A 12 MeV electron beam.", [], "Find [[R<sub>90</sub>, R<sub>80</sub>, R<sub>50</sub>, and R<sub>p</sub>]] and the reference depth."),
           ["R<sub>90</sub> = 12 / 3.3", "R<sub>80</sub> = 12 / 3", "R<sub>50</sub> = 12 / 2.33", "R<sub>p</sub> = 12 / 2", "d<sub>ref</sub> = 0.6 × 5.15 − 0.1"], f"R<sub>90</sub> = {r90(12):.2f} cm, R<sub>80</sub> = {r80(12):.2f} cm, R<sub>50</sub> = {r50(12):.2f} cm, R<sub>p</sub> = {rp(12):.2f} cm, d<sub>ref</sub> = {dref(12):.2f} cm."),
        EX("Choosing an energy", STEM("A target whose distal edge is 3.0 cm deep, to be covered by the 90% line.", [], "Estimate the [[energy]] needed."), ["R<sub>90</sub> = E / 3.3, so E = 3.3 × 3.0"], f"{E_need:.1f} MeV, so the next standard energy, 12 MeV, is used."),

        H("Energy and field size"),
        P("A higher energy gives a deeper range, a broader region of maximum dose, and a larger photon tail. The surface dose also rises with the energy, from roughly 80% of the maximum at 6 MeV to above 90% at the highest energies, because faster electrons scatter less, so less build-up of the electron fluence is needed. That is the opposite of a photon beam, whose surface dose falls as the energy rises. The field size changes the PDD when the field is smaller than the practical range, because lateral electronic equilibrium is lost. For an 18 MeV beam R<sub>p</sub> is about 9 cm, so for fields of 9 × 9 cm and larger the PDD curves are the same. For smaller fields the depth of maximum dose moves toward the surface and the surface dose increases."),
    ],
    cards=[
        F("Electron PDD", "A high surface dose, a broad dose maximum, a steep fall-off, and a small tail from bremsstrahlung photons."),
        F("Fall-off of the electron PDD", "It is not sharp, because the beam has a spectrum of energies and the electrons scatter. Higher-energy electrons go farther."),
        F("Photon contamination", "The dose at depth beyond the electron range, about 1% to 5% of the maximum, from bremsstrahlung in the head (mainly the scattering foil) and in the patient. It is larger at higher energy."),
        F("R<sub>90</sub>, R<sub>80</sub>, and R<sub>50</sub>", "The depths at which the dose has fallen to 90%, 80%, and 50% of the maximum."),
        F("Practical range R<sub>p</sub>", "The depth where the steepest part of the fall-off, extended as a straight line, meets the bremsstrahlung tail. It is close to the greatest depth the electrons reach."),
        F("Rules of thumb for range", "R<sub>90</sub> ≈ E/3.3, R<sub>80</sub> ≈ E/3, R<sub>50</sub> ≈ E/2.33, and R<sub>p</sub> ≈ E/2, in cm for E in MeV."),
        F("Reference depth for electron calibration", "d<sub>ref</sub> = 0.6 R<sub>50</sub> − 0.1 cm. It replaces d<sub>max</sub>, because the dose maximum covers a wide range of depths."),
        F("Choosing the electron energy", "Choose the energy whose R<sub>90</sub> (or R<sub>80</sub>) reaches the distal edge of the target: E ≈ 3.3 × depth for R<sub>90</sub>."),
        F("Energy and the dose maximum", "A higher energy gives a broader dose maximum and a deeper range."),
        F("Small electron fields", "For fields smaller than R<sub>p</sub>, the depth of maximum dose moves toward the surface and the surface dose increases."),
        F("Large electron fields", "For fields at least as large as R<sub>p</sub>, the PDD curves are the same. For 18 MeV, R<sub>p</sub> is about 9 cm."),
    ],
)

PROBLEMS = [
    PR("The fall-off of an electron PDD is not perfectly sharp because:", "the beam has a spectrum of energies and the electrons scatter", ["all the electrons stop at exactly the same depth", "photons carry the dose to depth", "the dose maximum is at the surface"],
       "Higher-energy electrons go farther and Coulomb scattering changes their paths, so the end of the range is spread over depth.", lvl="Easy"),
    PR("The practical range of a 12 MeV electron beam is about:", "6 cm", ["2.4 cm", "3.6 cm", "12 cm"],
       "R<sub>p</sub> ≈ E / 2 in cm for E in MeV, so 12 / 2 = 6 cm.", lvl="Easy"),
    PR("The dose beyond the range of the electrons in a therapy beam comes from:", "bremsstrahlung photons from the head and from the patient", ["electrons that travel farther than the practical range", "neutrons from the target", "scattered light"],
       "The electrons have stopped. The remaining dose, about 1% to 5% of the maximum, is photon contamination.", lvl="Easy"),
    PRN(STEM("A 15 MeV electron beam.", [], "What is [[R<sub>90</sub>]]?"), r90(15), [15 / 3.0, 15 / 2.0, 15 / 2.33], "{:.1f} cm",
        f"R<sub>90</sub> ≈ E / 3.3 = 15 / 3.3 = {r90(15):.1f} cm. The factors 3, 2.33, and 2 belong to R<sub>80</sub>, R<sub>50</sub>, and R<sub>p</sub>.", lvl="Moderate"),
    PRN(STEM("A 12 MeV electron beam.", [], "What is the [[reference depth]] d<sub>ref</sub> = 0.6 R<sub>50</sub> − 0.1?"), dref(12), [0.6 * r50(12), r50(12), 0.6 * 6.0 - 0.1], "{:.2f} cm",
        f"R<sub>50</sub> = 12 / 2.33 = {r50(12):.2f} cm, so d<sub>ref</sub> = 0.6 × {r50(12):.2f} − 0.1 = {dref(12):.2f} cm.", lvl="Moderate"),
    PR("A target extends to 3.0 cm depth and is to be covered by the 90% line. The lowest standard energy that does this is:", "12 MeV", ["6 MeV", "9 MeV", "16 MeV"],
       "R<sub>90</sub> ≈ E / 3.3, so E ≈ 3.3 × 3.0 = 9.9 MeV. A 9 MeV beam has R<sub>90</sub> = 2.7 cm and falls short. The next standard energy, 12 MeV, has R<sub>90</sub> = 3.6 cm.", lvl="Moderate"),
    PR("Compared with a 9 MeV beam, an 18 MeV electron beam has:", "a broader dose maximum, a deeper range, and a larger photon tail", ["a narrower dose maximum and a shorter range", "a higher surface dose and a smaller photon tail", "the same range but a larger photon tail"],
       "Higher energy raises the range, widens the dose maximum, and raises the radiative stopping power, which increases the photon contamination.", lvl="Moderate"),
    PR("An 18 MeV beam has a practical range of about 9 cm. Compared with a 12 × 12 cm field, a 6 × 6 cm field has:", "a depth of maximum dose closer to the surface and a higher surface dose", ["the same PDD", "a deeper maximum and a lower surface dose", "a longer practical range"],
       "The field is smaller than R<sub>p</sub>, so lateral equilibrium is lost and the PDD changes.", lvl="Challenging"),
    PR("The reference depth for calibrating an electron beam is based on R<sub>50</sub> rather than d<sub>max</sub> because:", "the dose maximum of an electron beam covers a wide range of depths", ["R<sub>50</sub> is always the deepest point", "d<sub>max</sub> is at the surface", "photon contamination is zero at R<sub>50</sub>"],
       "A calibration point must be well defined. The broad maximum makes d<sub>max</sub> ambiguous, whereas 0.6 R<sub>50</sub> − 0.1 cm is a definite depth.", lvl="Challenging"),
]

INLINE = {0: [1, 3], 1: [4, 6], 2: [7, 11]}

TERMS = ['bremsstrahlung', 'practical range', 'reference depth']

TAKE = [
    [('Electrons lose energy and scatter, so the PDD has a broad dose maximum, a steep but not sharp fall-off, and a small bremsstrahlung tail of about 1%–5%.', 'electron-pdd')],
    [('R<sub>90</sub> ≈ E/3.3, R<sub>80</sub> ≈ E/3, R<sub>50</sub> ≈ E/2.33, and R<sub>p</sub> ≈ E/2 (cm, E in MeV). The calibration depth is d<sub>ref</sub> = 0.6 R<sub>50</sub> − 0.1.', 'electron-range')],
    [('Fields at least as large as R<sub>p</sub> give the same PDD. Smaller fields move the dose maximum toward the surface and raise the surface dose.', 'electron-fieldsize')],
]


# ---------------------------------------------------------------- ranking, typed, and tap-the-figure questions
PROBLEMS += [
    SORT("Rank these depths for one electron beam, most superficial first.", ["1st (most superficial)", "2nd", "3rd", "4th (deepest)"],
         [("R<sub>90</sub>", 0), ("R<sub>80</sub>", 1), ("R<sub>50</sub>", 2), ("R<sub>p</sub>", 3)],
         "The dose falls with depth, so the depth at 90% is shallower than the depth at 80%, which is shallower than the depth at 50%. The practical range is the deepest, where the steepest fall-off meets the bremsstrahlung tail.", lvl="Moderate", mode="rank", cap=1),
]


# ---------------------------------------------------------------- surface dose against energy
PROBLEMS += [
    PR("An open photon beam and an open electron beam are each used without bolus. As the beam energy rises, the surface dose relative to the maximum:", "falls for the photon beam and rises for the electron beam", ["falls for both beams", "rises for both beams", "rises for the photon beam and falls for the electron beam"],
       "Higher-energy photons set the electrons in motion more forward, so the dose maximum is deeper and the surface dose is lower. Higher-energy electrons scatter less, so less build-up of the fluence is needed, and the surface dose is a larger fraction of the maximum, roughly 80% at 6 MeV and above 90% at the highest energies.", lvl="Moderate"),
]
