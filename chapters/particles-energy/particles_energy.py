from blocks import *
import math, calc

g6, b6 = calc.gamma_ke(6.0, calc.ME), calc.beta_ke(6.0, calc.ME)
cl6 = math.sqrt(2 * 6.0 / calc.ME)
b1 = calc.beta_ke(1.0, calc.ME); cl1 = math.sqrt(2 * 1.0 / calc.ME)
bp100, clp100 = calc.beta_ke(100, calc.MP), math.sqrt(2 * 100 / calc.MP)
gp100 = calc.gamma_ke(100, calc.MP)
u_mev = calc.U_MEV
rows = [["electron", f"{k:g}", f"{calc.gamma_ke(k, calc.ME):.2f}", f"{calc.beta_ke(k, calc.ME):.4f}"] for k in (0.1, 0.5, 1, 6, 20)] + \
       [["proton", f"{k:g}", f"{calc.gamma_ke(k, calc.MP):.3f}", f"{calc.beta_ke(k, calc.MP):.3f}"] for k in (10, 70, 150, 250)]

TOPIC = dict(
    id="particles-energy", domain=1, sub="I.A", title="Particles, mass, and energy",
    ref=dict(aapm="1.2, 1.4", khan="2", ford="1"),
    guide=[
        H("Rest energy"),
        P("A particle at rest has energy m₀c². Rest energies are quoted in MeV; [[1|1 u = 931.5 MeV]]."),
        TABLE(["Particle", "Symbol", "Charge", "Rest energy (MeV)", "Mass (u)"], [
            ["electron", "e⁻", "−1", f"[[1|{calc.ME:.3f}]]", "0.000549"],
            ["positron", "e⁺", "+1", f"{calc.ME:.3f}", "0.000549"],
            ["proton", "p", "+1", f"[[1|{calc.MP:.1f}]]", "1.00728"],
            ["neutron", "n", "0", f"{calc.MN:.1f}", "1.00866"],
            ["alpha", "α", "+2", f"{calc.MALPHA:.0f}", "4.00151"],
            ["photon", "γ", "0", "0", "0"]]),
        P(f"A proton is {calc.MP / calc.ME:.0f} times heavier than an electron. A neutron is slightly heavier than a proton."),

        H("Kinetic energy and speed"),
        EQ("E<sub>total</sub> = γm₀c² = KE + m₀c²", "[[1|KE = (γ − 1) m₀c²]],   γ = 1 / √(1 − β²),   β = v/c", "pc = √(KE² + 2·KE·m₀c²)"),
        P(f"At low speed KE ≈ ½mv². The approximation fails once KE is more than about 10% of the rest energy. [[1|That is 50 keV for an electron, so every therapy electron is relativistic.]] For a 6 MeV electron γ = {g6:.1f} and v = {b6:.4f}c; the classical formula would give {cl6:.1f}c, faster than light. [[1|Therapy protons (70–250 MeV) also need the relativistic formulas.]]"),
        FIG("beta_vs_ke", "Speed against kinetic energy. [[2|An electron reaches 0.94c at 1 MeV; a proton reaches 0.51c at 150 MeV.]]"),
        TABLE(["Particle", "KE (MeV)", "γ", "v/c"], rows),
        P("[[2|Near c, added energy raises momentum and total energy, not speed: electrons of 6 MeV and 20 MeV travel at almost the same speed.]]"),

        H("Annihilation and pair production"),
        P("When a positron meets an electron both vanish, and [[1|their rest energy appears as two 511 keV photons emitted in opposite directions]] (momentum is conserved when they start at rest). PET detects this pair."),
        P("[[2|A photon of at least 2m₀c² = 1.022 MeV passing a nucleus can become an electron–positron pair. Any excess is shared as kinetic energy.]]"),
        EQ("e⁻ + e⁺ → 2γ (511 keV each)", "[[2|hν → e⁻ + e⁺,   threshold 1.022 MeV,   KE<sub>pair</sub> = hν − 1.022 MeV]]"),

        EX("Mass to energy", STEM("A mass is converted entirely to energy.", ["m = 0.0020 u"], "Find the [[energy released]]."),
           ["1 u = 931.5 MeV", f"0.0020 × 931.5 = {0.0020 * u_mev:.2f} MeV"], f"{0.0020 * u_mev:.2f} MeV."),
        EX("Speed of a therapy electron", STEM("", ["kinetic energy = 6.0 MeV"], "Find the [[speed]] of the electron."),
           [f"γ = 1 + KE/m₀c² = 1 + 6.0/0.511 = {g6:.2f}", f"β = √(1 − 1/γ²) = {b6:.4f}"],
           f"{b6:.4f}c, about {sci(b6 * 2.998e8, 4)} m/s. The classical ½mv² would give {cl6:.1f}c, which is impossible."),
        EX("A 100 MeV proton", STEM("", ["kinetic energy = 100 MeV (proton)"], "Find the [[speed]] of the proton."),
           [f"γ = 1 + 100/938.3 = {gp100:.4f}", f"β = √(1 − 1/γ²) = {bp100:.4f}"], f"{bp100:.2f}c. The classical estimate is {clp100:.2f}c, about 8% too high."),
        P("A photon has no rest mass, yet it carries energy E and momentum E/c. The mass equivalent of its energy, E/c², is not a rest mass. A collision is elastic when the total kinetic energy is conserved, as when a neutron bounces off a hydrogen nucleus, and inelastic when part of the kinetic energy goes to excitation, radiation, or rest mass, as when an electron excites an atom or a photon creates a pair. Momentum is conserved in both."),
    ],
    cards=[
        C("What are the rest energies of the electron and the proton?", f"Electron {calc.ME:.3f} MeV. Proton {calc.MP:.1f} MeV (about 1836 times larger)."),
        C("How many MeV is 1 atomic mass unit?", "931.5 MeV."),
        C("How are total energy, kinetic energy, and rest energy related?", "E<sub>total</sub> = KE + m₀c² = γm₀c², so KE = (γ − 1)m₀c²."),
        C("When is KE = ½mv² valid?", "When KE is small compared with the rest energy (under about 10%). For electrons that is below ~50 keV, so therapy electrons need the relativistic expressions."),
        C("What happens when a positron at rest meets an electron at rest?", "They annihilate into two 511 keV photons emitted in opposite directions."),
        C("What is the threshold photon energy for pair production?", "1.022 MeV (2m₀c²). Any excess is shared as kinetic energy of the electron and positron."),
        C("Which is moving faster, a 20 MeV electron or a 150 MeV proton?", f"The electron: {calc.beta_ke(20, calc.ME):.5f}c against {calc.beta_ke(150, calc.MP):.2f}c. Electrons saturate near c; protons do not at therapy energies.", fig="beta_vs_ke"),
    ],
)

PROBLEMS = [
    PRN("What is the <f>rest energy</f> of an electron?", calc.ME, [calc.ME * 1e-3, calc.MP, 2 * calc.ME], "{:.3g} MeV", "m₀c² for the electron is 0.511 MeV. The proton's is 938 MeV, and 1.022 MeV is two electron masses.", lvl="Easy"),
    PR("An electron and a positron, both at rest, annihilate. What is produced?", "Two 511 keV photons moving in opposite directions",
       ["One 1.022 MeV photon", "Two 511 keV photons moving in the same direction", "A higher-energy electron–positron pair"],
       "Momentum is zero before, so it must be zero after: two photons of equal energy, back to back. A single photon could not conserve momentum.", lvl="Easy"),
    PRN("Approximately how many <f>times heavier</f> is a proton than an electron?", calc.MP / calc.ME, [184.0, 3672.0, 18360.0], lambda v: f"{v:,.0f}",
        f"{calc.MP:.1f} MeV / {calc.ME:.3f} MeV = {calc.MP / calc.ME:,.0f}.", lvl="Easy"),
    PRM("Which of these particles carry no electric charge?", ["neutron", "photon"], ["positron", "alpha particle", "proton"],
        "Neutrons and photons are neutral. The positron is +1, the proton +1, and the alpha particle +2.", lvl="Easy"),
    PRN("How much <f>energy</f> is equivalent to a mass of <v>0.0020 u</v>?", 0.0020 * u_mev, [0.0020 * u_mev / 10, 0.0020 * u_mev * 10, 0.0020 * u_mev * 100], "{:.3g} MeV",
        f"E = 0.0020 u × 931.5 MeV/u = {0.0020 * u_mev:.2f} MeV.", lvl="Moderate",
        calc=CALC("MeV", [TILE("m", 0.0020, "u", disp="0.0020"), CONV("u", "MeV", 931.5), TILE("mₑc²", 0.511, "MeV", id="mec2"), TILE("c", 3.00e8, "m/s", disp="3.00 × 10⁸")], solution=["m", "×", "u→MeV"])),
    PR("Using ½mv² for a 6 MeV electron gives a speed greater than c. Why is the formula wrong here?", "The kinetic energy is far larger than 10% of the rest energy, so relativistic expressions are needed",
       ["The electron is charged, so its kinetic energy is not ½mv²", "6 MeV is too low an energy for the classical formula", "The electron loses mass at high speed"],
       "KE = 6 MeV is about twelve times the 0.511 MeV rest energy. The classical formula assumes KE ≪ m₀c².", lvl="Moderate"),
    PRN("What is the <f>threshold photon energy</f> for pair production in the field of a nucleus?", 2 * calc.ME, [calc.ME, 4 * calc.ME, 8 * calc.ME], "{:.3f} MeV",
        "The photon must supply the rest energy of two electron masses: 2 × 0.511 = 1.022 MeV.", lvl="Moderate"),
    PRN("A <v>3.0 MeV</v> photon undergoes pair production in the field of a nucleus. What is the <f>combined kinetic energy</f> of the electron and positron?", 3.0 - 2 * calc.ME, [(3.0 - 2 * calc.ME) / 2, 3.0 - calc.ME, 3.0], "{:.3f} MeV",
        "KE<sub>pair</sub> = hν − 2m₀c² = 3.000 − 1.022 = 1.978 MeV (the nucleus takes a negligible recoil).", lvl="Moderate"),
    PRN("What is the <f>total energy</f>, including rest energy, of an electron with <v>2.0 MeV</v> of kinetic energy?", 2.0 + calc.ME, [2.0 - calc.ME, 2.0, 2.0 + 2 * calc.ME], "{:.3f} MeV",
        "E<sub>total</sub> = KE + m₀c² = 2.000 + 0.511 = 2.511 MeV.", lvl="Moderate"),
]

INLINE = {0: [1, 4, 5], 1: [6]}

TERMS = ['rest energies', 'positron']

TAKE = [
    [("Rest energies: electron 0.511 MeV, proton 938 MeV. 1 u = 931.5 MeV.", "rest-energy")],
    [("KE = (γ − 1)m₀c². Every therapy electron (above about 50 keV) and every therapy proton needs the relativistic formulas.", "ke-classical"),
     ("Electrons are near c by a few MeV; protons are not (a 150 MeV proton is at about 0.51c).", "speed-ke")],
    [("Annihilation gives two 511 keV photons, back to back.", "annihilation"),
     ("Pair production needs hν > 1.022 MeV; the pair shares hν − 1.022 MeV.", "pair-production")],
]


# ---------------------------------------------------------------- photons without rest mass, and collisions
PROBLEMS += [
    PR("Which statement about a photon is correct?", "It has no rest mass, and the mass equivalent of its energy is E / c²", ["It has a rest mass of E / c²", "It has no energy, because it has no rest mass", "It has no momentum, because it has no rest mass"],
       "A photon has zero rest mass, yet it carries energy E and momentum E/c. The quantity E/c² is the mass equivalent of its energy, and not its rest mass.", lvl="Moderate"),
    PR("In an elastic collision between two particles:", "the total kinetic energy and the total momentum are both conserved", ["the momentum is conserved, but the kinetic energy is not", "the kinetic energy is conserved, but the momentum is not", "neither is conserved, because part of the energy becomes heat"],
       "In an elastic collision no kinetic energy is converted to another form. In an inelastic collision part of it goes to excitation, radiation, or rest mass. The momentum is conserved in both.", lvl="Easy"),
    SORT("Is each collision elastic or inelastic?", ["Elastic", "Inelastic"],
         [("A neutron bounces off a hydrogen nucleus", 0), ("An α particle is deflected by a gold nucleus, which stays in its ground state", 0), ("Two protons are deflected by their Coulomb repulsion, with no radiation", 0),
          ("An electron excites an atom and slows down", 1), ("A photon creates an electron–positron pair", 1), ("An electron emits a bremsstrahlung photon in the field of a nucleus", 1)],
         "In an elastic collision the total kinetic energy is unchanged, so no energy goes to excitation, radiation, or new particles. Exciting an atom, creating a pair, and emitting bremsstrahlung each take kinetic energy for another purpose.", lvl="Moderate"),
]
