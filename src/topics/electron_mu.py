from blocks import *
import math, calc

SSDEFF, DM = 85.0, 1.8                                           # effective SSD of the virtual source and d_max for the 9 MeV example
inv = lambda g, ssde=SSDEFF, dm=DM: ((ssde + dm) / (ssde + dm + g)) ** 2
mu_f = lambda D, pdd, se, g=0.0: D / (pdd * se * inv(g))
mu_a, mu_b, mu_c = mu_f(200, 0.90, 0.97), mu_f(200, 0.90, 0.97, 5), mu_f(200, 0.90, 0.97, 10)
mu_t = 250 / (0.80 * 1.02)
se_small = lambda fs, rp: 1.0 if fs >= rp else 1 - 0.35 * (1 - fs / rp) ** 1.5      # schematic output factor against field side

TOPIC = dict(
    id="electron-mu", domain=3, sub="III.B", title="Electron output and monitor units",
    ref=dict(aapm="TG-25, TG-51", khan="14", ford="15"),
    guide=[
        H("The electron MU calculation"),
        P("An electron beam is normally calibrated to give 1 cGy per MU at d<sub>max</sub> for the 10 × 10 cm applicator with its standard cutout at SSD 100 cm. Every other condition changes the dose per MU, and the monitor-unit calculation puts the changes back. The prescription is often at the 90% depth, so the dose at d<sub>max</sub> is the prescription divided by the PDD there."),
        EQ("MU = D / [ (PDD / 100) × S<sub>e</sub> × INV² ]", "D = prescribed dose,   PDD = percent depth dose at the prescription depth,   S<sub>e</sub> = output factor of the applicator and cutout,   INV² = inverse-square term"),
        P("The output factor S<sub>e</sub> is the dose per MU at d<sub>max</sub> for a given applicator and cutout, relative to the reference. It is measured at commissioning for each energy, applicator, and cutout. A small cutout lowers it when the field is smaller than the practical range, because lateral scatter is lost."),
        EX("MU at the standard SSD", STEM("A 9 MeV electron field at SSD 100 cm.", ["prescription = 200 cGy at the 90% depth, so PDD = 90%", "output factor S<sub>e</sub> = 0.97"], "Find the [[MU]]."), ["MU = 200 / (0.90 × 0.97 × 1)"], f"{mu_a:.1f} MU."),

        H("Virtual source and extended SSD"),
        P("The electrons in a therapy beam appear to diverge from a virtual source, not from the target. Its position depends on the energy. The effective SSD is the distance from the virtual source to the nominal SSD of 100 cm, for example 85 cm. Treating at a larger SSD leaves an air gap g, and the dose per MU falls as the inverse square of the distance from the virtual source."),
        EQ("INV² = [ (SSD<sub>eff</sub> + d<sub>max</sub>) / (SSD<sub>eff</sub> + d<sub>max</sub> + g) ]²", "g = air gap = SSD − 100 cm"),
        P("This formalism is a reasonable description for moderate air gaps, up to an SSD of about 115 cm. Beyond that the output should be measured at the treatment SSD, because the electrons scattered in air and by the collimation change the beam."),
        EX("Inverse-square term at an extended SSD", STEM("A 9 MeV beam.", ["effective SSD = 85 cm", "d<sub>max</sub> = 1.8 cm", "treatment SSD = 105 cm"], "Find the [[inverse-square term]]."), ["Air gap g = 105 − 100 = 5 cm", "INV² = [ (85 + 1.8) / (85 + 1.8 + 5) ]² = (86.8 / 91.8)²"], f"{inv(5):.3f}: the output at SSD 105 cm is {100 * (1 - inv(5)):.1f}% lower than at SSD 100 cm."),
        EX("MU at an extended SSD", STEM("A 9 MeV electron field at an extended SSD.", ["effective SSD = 85 cm", "d<sub>max</sub> = 1.8 cm", "treatment SSD = 110 cm", "prescription = 200 cGy at the 90% depth", "S<sub>e</sub> = 0.97"], "Find the [[MU]]."), [f"INV² = (86.8 / 96.8)² = {inv(10):.3f}", f"MU = 200 / (0.90 × 0.97 × {inv(10):.3f})"], f"{mu_c:.0f} MU, which is {100 * (mu_c / mu_a - 1):.0f}% more than at SSD 100 cm."),

        H("Output and prescription"),
        P("Prescribing to a depth other than d<sub>max</sub> divides the MU by the PDD there: a dose prescribed to the 80% depth needs more MU than the same dose at the 90% depth. The usual rule is to prescribe to the depth that covers the distal edge of the target, as the R<sub>90</sub> or R<sub>80</sub> chosen for the energy. Bolus or an oblique surface changes the depth and the PDD, and the calculation uses the values at the new geometry."),
        EX("Prescription at the 80% depth", STEM("A 12 MeV field at SSD 100 cm.", ["prescription = 250 cGy at the 80% depth", "S<sub>e</sub> = 1.02"], "Find the [[MU]]."), ["MU = 250 / (0.80 × 1.02 × 1)"], f"{mu_t:.1f} MU."),
    ],
    cards=[
        F("Electron calibration", "Usually 1 cGy/MU at d<sub>max</sub> for the 10 × 10 cm applicator with its standard cutout at SSD 100 cm."),
        F("Electron MU formula", "MU = D / [ (PDD/100) × S<sub>e</sub> × INV² ]."),
        F("Output factor S<sub>e</sub>", "The dose per MU at d<sub>max</sub> for a given applicator and cutout, relative to the reference. Measured for each energy, applicator, and cutout."),
        F("Small cutouts", "When the field is smaller than the practical range, lateral scatter is lost and the output factor falls below 1."),
        F("Virtual source", "Electrons in a therapy beam appear to diverge from a virtual source whose position depends on the energy, not from the target."),
        F("Effective SSD", "The distance from the virtual source to the nominal SSD of 100 cm, for example 85 cm."),
        F("Inverse-square term for electrons", "INV² = [ (SSD<sub>eff</sub> + d<sub>max</sub>) / (SSD<sub>eff</sub> + d<sub>max</sub> + g) ]², with g the air gap, SSD − 100 cm."),
        F("Output at an extended SSD", "It falls as the inverse square of the distance from the virtual source. At 9 MeV, an air gap of 5 cm lowers it by about 11%."),
        F("Prescribing electrons to a depth", "The MU are divided by the PDD there, so the 80% depth needs more MU than the 90% depth for the same dose."),
    ],
)

PROBLEMS = [
    PR("In the electron MU calculation, the output factor S<sub>e</sub> depends on:", "the energy, the applicator, and the cutout", ["the patient's thickness only", "the wedge angle", "the field size at the isocenter"],
       "It is the dose per MU at d<sub>max</sub> for the applicator and cutout used, measured at commissioning.", lvl="Easy"),
    PR("Electron beams appear to diverge from:", "a virtual source whose position depends on the energy", ["the target of the linac", "the flattening filter", "the surface of the patient"],
       "The scattering foils and collimation make the electrons diverge from a point that is not the x-ray target.", lvl="Easy"),
    PR("When the SSD of an electron field is increased from 100 cm to 110 cm, the dose per MU at d<sub>max</sub>:", "falls, following the inverse square from the virtual source", ["rises, because the beam is wider", "does not change", "falls only for photons"],
       "The distance from the virtual source increases, so the fluence and the dose per MU fall.", lvl="Easy"),
    PRN(STEM("A 9 MeV field at SSD 100 cm.", ["prescription = 200 cGy at the 90% depth", "S<sub>e</sub> = 0.97"], "What is the [[MU]]?"), mu_a, [200 / 0.97, 200 * 0.9 / 0.97, 200 / 0.90], "{:.1f} MU",
        f"MU = 200 / (0.90 × 0.97) = {mu_a:.1f}. Ignoring the PDD gives {200 / 0.97:.1f}, multiplying by the PDD gives {200 * 0.9 / 0.97:.1f}, and ignoring the output factor gives {200 / 0.9:.1f}.", lvl="Moderate"),
    PR("A small electron cutout, much smaller than the practical range, usually has an output factor:", "below 1, because lateral scatter is lost", ["above 1, because the beam is more concentrated", "exactly 1 for every cutout", "equal to the PDD at d<sub>max</sub>"],
       "Electrons scatter out of a small field and are not replaced from the sides, so less dose is delivered per MU.", lvl="Moderate"),
    PR("A fixed dose is prescribed at the 80% depth rather than at the 90% depth of the same beam. The MU needed:", "are larger", ["are smaller", "are the same", "depend only on the field size"],
       "MU = D / [ (PDD/100) × S<sub>e</sub> × INV² ]. A smaller PDD in the denominator gives more MU.", lvl="Moderate"),
    PRN(STEM("A 9 MeV electron field at SSD 110 cm.", ["effective SSD = 85 cm, d<sub>max</sub> = 1.8 cm", "prescription = 200 cGy at the 90% depth, S<sub>e</sub> = 0.97"], "What is the [[MU]]?"), mu_c, [mu_a, mu_b, 200 / (0.90 * 0.97 * (100 / 110) ** 2)], "{:.0f} MU",
        f"INV² = (86.8 / 96.8)² = {inv(10):.3f}, so MU = 200 / (0.90 × 0.97 × {inv(10):.3f}) = {mu_c:.0f}. At SSD 100 cm it is {mu_a:.0f}, and at SSD 105 cm it is {mu_b:.0f}.", lvl="Challenging"),
]

INLINE = {0: [1, 4], 1: [2, 3], 2: [6]}

TERMS = ['output factor', 'virtual source', 'effective SSD']

TAKE = [
    [('MU = D / [ (PDD/100) × S<sub>e</sub> × INV² ] for a calibration of 1 cGy/MU at d<sub>max</sub>. S<sub>e</sub> is the output factor of the applicator and cutout.', 'electron-mu-chain')],
    [('Electron beams diverge from a virtual source. INV² = [ (SSD<sub>eff</sub> + d<sub>max</sub>) / (SSD<sub>eff</sub> + d<sub>max</sub> + g) ]², with g the air gap.', 'virtual-source')],
    [('A cutout smaller than the practical range lowers the output factor, because lateral scatter is lost. Measure S<sub>e</sub> for each cutout.', 'electron-output')],
]


# ---------------------------------------------------------------- ranking, typed, and tap-the-figure questions
_g80 = (SSDEFF + DM) * (1 / math.sqrt(0.80) - 1)                  # air gap at which the dose per MU is 80% of its value at SSD 100 cm
PROBLEMS += [
]
