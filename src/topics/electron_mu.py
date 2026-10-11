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
        F("Limit of the virtual-source formalism", "Reasonable for moderate air gaps, up to an SSD of about 115 cm. Beyond that, measure the output at the treatment SSD."),
        F("Prescribing electrons to a depth", "The MU are divided by the PDD there, so the 80% depth needs more MU than the 90% depth for the same dose."),
        F("Choosing the prescription depth", "The depth that covers the distal edge of the target, as the R<sub>90</sub> or R<sub>80</sub> of the energy chosen."),
    ],
)

PROBLEMS = [
    PR("In the electron MU calculation, the output factor S<sub>e</sub> depends on:", "the energy, the applicator, and the cutout", ["the patient's thickness only", "the wedge angle", "the field size at the isocenter"],
       "It is the dose per MU at d<sub>max</sub> for the applicator and cutout used, measured at commissioning.", lvl="Easy"),
    PR("Electron beams appear to diverge from:", "a virtual source whose position depends on the energy", ["the target of the linac", "the flattening filter", "the surface of the patient"],
       "The scattering foils and collimation make the electrons diverge from a point that is not the x-ray target.", lvl="Easy"),
    PR("When the SSD of an electron field is increased from 100 cm to 110 cm, the dose per MU at d<sub>max</sub>:", "falls, following the inverse square from the virtual source", ["rises, because the beam is wider", "does not change", "falls only for photons"],
       "The distance from the virtual source increases, so the fluence and the dose per MU fall.", lvl="Easy"),
    PRN(STEM("A 9 MeV beam.", ["effective SSD = 85 cm", "d<sub>max</sub> = 1.8 cm", "treatment SSD = 105 cm"], "What is the [[inverse-square term]]?"), inv(5), [(86.8 / 91.8), (100 / 105) ** 2, (91.8 / 86.8) ** 2], "{:.3f}",
        f"g = 105 − 100 = 5 cm, so INV² = (86.8 / 91.8)² = {inv(5):.3f}. Leaving out the square gives {86.8 / 91.8:.3f}, using the nominal SSD gives {(100 / 105) ** 2:.3f}, and inverting the ratio gives {(91.8 / 86.8) ** 2:.3f}.", lvl="Moderate"),
    PRN(STEM("A 9 MeV field at SSD 100 cm.", ["prescription = 200 cGy at the 90% depth", "S<sub>e</sub> = 0.97"], "What is the [[MU]]?"), mu_a, [200 / 0.97, 200 * 0.9 / 0.97, 200 / 0.90], "{:.1f} MU",
        f"MU = 200 / (0.90 × 0.97) = {mu_a:.1f}. Ignoring the PDD gives {200 / 0.97:.1f}, multiplying by the PDD gives {200 * 0.9 / 0.97:.1f}, and ignoring the output factor gives {200 / 0.9:.1f}.", lvl="Moderate"),
    PR("A small electron cutout, much smaller than the practical range, usually has an output factor:", "below 1, because lateral scatter is lost", ["above 1, because the beam is more concentrated", "exactly 1 for every cutout", "equal to the PDD at d<sub>max</sub>"],
       "Electrons scatter out of a small field and are not replaced from the sides, so less dose is delivered per MU.", lvl="Moderate"),
    PRM("Which quantities does the MU calculation for an electron field at an extended SSD need?", ["The effective SSD of the virtual source", "The air gap", "The output factor of the applicator and cutout"], ["The wedge factor", "The TMR at the isocenter"],
        "The extended-SSD calculation combines the PDD, the output factor, and the inverse-square term from the virtual source. Wedges and the TMR belong to photon beams.", lvl="Moderate"),
    PR("A fixed dose is prescribed at the 80% depth rather than at the 90% depth of the same beam. The MU needed:", "are larger", ["are smaller", "are the same", "depend only on the field size"],
       "MU = D / [ (PDD/100) × S<sub>e</sub> × INV² ]. A smaller PDD in the denominator gives more MU.", lvl="Moderate"),
    PRN(STEM("A 9 MeV electron field at SSD 110 cm.", ["effective SSD = 85 cm, d<sub>max</sub> = 1.8 cm", "prescription = 200 cGy at the 90% depth, S<sub>e</sub> = 0.97"], "What is the [[MU]]?"), mu_c, [mu_a, mu_b, 200 / (0.90 * 0.97 * (100 / 110) ** 2)], "{:.0f} MU",
        f"INV² = (86.8 / 96.8)² = {inv(10):.3f}, so MU = 200 / (0.90 × 0.97 × {inv(10):.3f}) = {mu_c:.0f}. At SSD 100 cm it is {mu_a:.0f}, and at SSD 105 cm it is {mu_b:.0f}.", lvl="Challenging"),
    PR("Beyond an SSD of about 115 cm, the output of an electron beam is best:", "measured at the treatment SSD", ["calculated with a larger effective SSD", "taken from the 100 cm value", "ignored"],
       "The virtual-source description is no longer reliable, because scattering in air and by the collimation changes the beam.", lvl="Challenging"),
    PR("The electron MU calculation for a given prescription depth uses the PDD at that depth because the:", "calibration gives 1 cGy/MU at d<sub>max</sub>, and the dose at the prescription depth is a fraction of that", ["calibration is made at the prescription depth", "PDD is always 100% at the surface", "output factor already contains the PDD"],
       "The dose at d<sub>max</sub> is the prescription divided by the PDD, and the MU deliver that dose at 1 cGy/MU, corrected by the output factor and the inverse-square term.", lvl="Challenging"),
]

INLINE = {0: [1, 4, 5], 1: [2, 3, 7], 2: [8]}

TERMS = ['output factor', 'virtual source', 'effective SSD']

TAKE = [
    [('MU = D / [ (PDD/100) × S<sub>e</sub> × INV² ] for a calibration of 1 cGy/MU at d<sub>max</sub>. S<sub>e</sub> is the output factor of the applicator and cutout.', 'electron-mu-chain')],
    [('Electron beams diverge from a virtual source. INV² = [ (SSD<sub>eff</sub> + d<sub>max</sub>) / (SSD<sub>eff</sub> + d<sub>max</sub> + g) ]², with g the air gap.', 'virtual-source')],
    [('A cutout smaller than the practical range lowers the output factor, because lateral scatter is lost. Measure S<sub>e</sub> for each cutout.', 'electron-output')],
]


# ---------------------------------------------------------------- ranking, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
_g80 = (SSDEFF + DM) * (1 / math.sqrt(0.80) - 1)                  # air gap at which the dose per MU is 80% of its value at SSD 100 cm
PROBLEMS += [
    SORT("Does the MU needed for the same dose rise or fall with each change?", ["MU rise", "MU fall"],
         [("A larger air gap", 0), ("A smaller output factor", 0), ("Prescribing at the 80% depth instead of the 90% depth", 0), ("A higher prescribed dose", 0), ("An output factor above 1", 1), ("Prescribing to d<sub>max</sub> instead of the 90% depth", 1)],
         "Anything that lowers the dose per MU, or lowers the fraction of the d<sub>max</sub> dose at the prescription point, raises the MU. A larger output factor and a prescription at d<sub>max</sub> lower it.", lvl="Moderate"),
    TYPED(STEM("A 12 MeV field at SSD 100 cm.", ["prescription = 250 cGy at the 80% depth", "S<sub>e</sub> = 1.02"], "What is the [[MU]]?"), mu_t, 0.01, "MU",
          f"MU = 250 / (0.80 × 1.02) = {mu_t:.1f}.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the inverse-square term of a 9 MeV electron beam with a virtual source at 85 cm (d<sub>max</sub> = 1.8 cm) against SSD.", [], "Tap the [[SSD at which the dose per MU is 80%]] of its value at SSD 100 cm."),
         FS(x=dict(min=100, max=120, ticks=[100, 105, 110, 115, 120], label="SSD (cm)"), y=dict(min=0.6, max=1.02, ticks=[0.6, 0.85, 1.0], label="Inverse-square term"), series=[dict(pts=PTS(lambda s: inv(s - 100), 100, 120), color="plot-1")], xunit=" cm", xdec=1, xname="SSD", label="Inverse-square term against SSD"),
         [(100 + _g80 - 1.2, 100 + _g80 + 1.2)], f"The term is 0.80 when (86.8 / (86.8 + g))² = 0.80, so g = 86.8 × (1/√0.80 − 1) = {_g80:.1f} cm and the SSD is {100 + _g80:.1f} cm. The level 0.80 is not marked on the axis.", lvl="Challenging", note=f"about {100 + _g80:.0f} cm"),
]
INLINE = {0: [1, 4, 5, _n0 + 2], 1: [2, 3, 7, _n0 + 3], 2: [8, _n0 + 1]}
