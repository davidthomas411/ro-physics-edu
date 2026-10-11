from blocks import *
import math, calc

F2 = calc.coulomb_n(calc.E_CHG, calc.E_CHG, 2.0e-15)
F1 = calc.coulomb_n(calc.E_CHG, calc.E_CHG, 1.0e-15)
pc6 = calc.pc_ke(6.0, calc.ME); r6 = calc.bend_radius_m(pc6, 0.20) * 100
pc_cl = math.sqrt(2 * 6.0 * calc.ME); r_cl = calc.bend_radius_m(pc_cl, 0.20) * 100
E32, E21, E_21b = calc.h_photon_ev(3, 2), calc.h_photon_ev(2, 1), calc.h_photon_ev(2, 1)
lam32 = calc.nm_from_ev(E32)
K_W, L_W = 69.5, 10.2
Ka_W = K_W - L_W

TOPIC = dict(
    id="charges-atom", domain=1, sub="I.A", title="Charges, fields, and atomic structure",
    ref=dict(aapm="1.3, 2.1", khan="2", ford="1"),
    guide=[
        H("Charge and force"),
        P("Charge comes in units of e = 1.602 × 10<sup>−19</sup> C. Like charges repel and unlike charges attract, with a force given by Coulomb's law:"),
        EQ("F = k q₁q₂ / r²", "k = 8.99 × 10<sup>9</sup> N·m²/C²"),
        P(f"The force falls as the square of the separation: double the distance and it drops to one quarter. Two protons 2.0 fm apart, the scale inside a nucleus, repel each other with {F2:.0f} N. The nuclear strong force must beat that to hold the nucleus together."),

        H("Moving charges in a magnetic field"),
        EQ("F = q v B sin θ", "r = p / (qB)"),
        P("The magnetic force is perpendicular to both the velocity and the field. It bends the path but does no work, so the speed and kinetic energy do not change. In a uniform field a charged particle moves in a circle (a helix if it also has a component along the field). Linac bending magnets, cyclotrons, and synchrotrons use this."),
        EQ("r [m] = pc [MeV] / (299.8 × B [T])"),
        P(f"For a 6 MeV electron in a 0.20 T field, pc = {pc6:.2f} MeV, so r = {r6:.1f} cm. Using the non-relativistic momentum would give {r_cl:.1f} cm."),

        H("Atomic structure"),
        P("Rutherford fired α particles at thin gold foil. Most passed almost straight through, but a few bounced back at large angles. The positive charge and nearly all the mass must therefore sit in a tiny nucleus (about 10<sup>−15</sup> m) in an atom 10<sup>5</sup> times larger (about 10<sup>−10</sup> m), which is mostly empty space."),
        P("Bohr's model puts electrons in discrete shells (K, L, M, … moving outward). Energy is absorbed or released only in jumps between shells. For hydrogen:"),
        EQ("E<sub>n</sub> = −13.6 eV / n²", "photon emitted: hν = E<sub>initial</sub> − E<sub>final</sub>"),
        FIG("bohr_levels", "Hydrogen energy levels. Spacing shrinks toward the ionization limit."),
        P("The binding energy of an electron is the energy needed to remove it. It is largest for the innermost shell and increases steeply with atomic number, roughly as Z²: 13.6 eV in hydrogen, but 69.5 keV for the K shell of tungsten."),
        TABLE(["Process", "What happens", "Result"], [
            ["Excitation", "An electron moves to a higher shell; none is removed", "Atom de-excites later, releasing a photon"],
            ["Ionization", "An electron is removed from the atom", "Free electron and an ion"],
            ["Characteristic x-ray", "An outer electron fills an inner-shell vacancy", "Photon with the difference in binding energies"],
            ["Auger electron", "The same energy goes to another outer electron instead", "That electron is ejected; no photon"]]),

        EX("Coulomb repulsion in the nucleus", STEM("Two protons repel each other.", ["separation r = 2.0 fm"], "Find the [[repulsive force]]."),
           ["F = k e² / r² = (8.99 × 10<sup>9</sup>)(1.602 × 10<sup>−19</sup>)² / (2.0 × 10<sup>−15</sup>)²"], f"{F2:.1f} N. At 1.0 fm it would be {F1:.0f} N."),
        EX("A hydrogen transition", STEM("A hydrogen atom drops between energy levels.", ["initial level n = 3", "final level n = 2"], "Find the [[photon energy]] and its [[wavelength]]."),
           ["ΔE = 13.6 (1/2² − 1/3²) = 13.6 (1/4 − 1/9)", f"λ = 1240 eV·nm / {E32:.2f} eV"], f"{E32:.2f} eV, a red photon of {lam32:.0f} nm."),
        EX("Characteristic x-ray of tungsten", STEM("", ["K-shell binding energy = 69.5 keV", "L<sub>III</sub> binding energy = 10.2 keV"], "Find the [[photon energy]] of an L → K transition in tungsten."),
           ["The vacancy moves from K to L, releasing the difference in binding energies."], f"{K_W} − {L_W} = {Ka_W:.1f} keV."),
    ],
    cards=[
        C("State Coulomb's law. What happens if the distance doubles?", "F = kq₁q₂/r². Doubling r cuts the force to one quarter."),
        C("What does a magnetic field do to a moving charged particle's speed and energy?", "Nothing. The force is perpendicular to the velocity, does no work, and only bends the path."),
        C("What path does a charged particle take in a uniform magnetic field, and what sets the radius?", "A circle, with r = p/(qB). Higher momentum gives a larger radius.", w=["For electrons: r [m] = pc [MeV] / (299.8 × B [T])."]),
        C("What did Rutherford's gold-foil experiment show?", "Atoms have a small, dense, positively charged nucleus. Most α particles passed through; a few scattered at large angles."),
        C("Give the energy levels of hydrogen and its ionization energy.", "E<sub>n</sub> = −13.6 eV / n². Ionization from the ground state takes 13.6 eV."),
        C("What is the difference between excitation and ionization?", "Excitation lifts an electron to a higher shell without removing it. Ionization removes the electron from the atom."),
        C("How is a characteristic x-ray produced?", "An outer-shell electron fills an inner-shell vacancy, and the photon carries the difference in binding energies."),
        C("What is an Auger electron?", "The vacancy energy is transferred to another orbital electron, which is ejected instead of a photon being emitted. Its kinetic energy is the transition energy minus its own binding energy."),
        C("How does electron binding energy vary with shell and atomic number?", "It is highest for the innermost (K) shell and rises steeply with Z, roughly as Z². Hydrogen: 13.6 eV. Tungsten K shell: 69.5 keV."),
    ],
)

PROBLEMS = [
    PR("The distance between two charges is doubled. The Coulomb force between them:", "falls to one quarter", ["falls to one half", "doubles", "is unchanged"],
       "F ∝ 1/r². Twice the distance gives (½)² = ¼ of the force.", lvl="Easy"),
    PR("A charged particle moves perpendicular to a uniform magnetic field. Its kinetic energy:", "stays constant, because the magnetic force does no work",
       ["increases, because the force accelerates it", "decreases as it radiates energy to the field", "oscillates between zero and a maximum"],
       "The force is always perpendicular to the velocity, so it changes direction but not speed.", lvl="Easy"),
    PR("What did the scattering of α particles from gold foil show?", "The positive charge and most of the mass of an atom lie in a tiny nucleus",
       ["Electrons occupy fixed energy shells", "Atoms are uniform spheres of positive charge", "The nucleus contains neutrons"],
       "A few α particles scattered through large angles, which requires the positive charge to be concentrated in a small volume.", lvl="Easy"),
    PRN("What <f>energy</f> is needed to ionize a hydrogen atom in its ground state?", calc.RY_EV, [1.36, 136.0, 13600.0], "{:g} eV",
        "E<sub>1</sub> = −13.6 eV, so 13.6 eV lifts the electron to zero binding energy.", lvl="Easy"),
    PRN("Two protons are separated by <v>2.0 fm</v>. What is the <f>repulsive Coulomb force</f> between them?", F2, [F2 / 10, F1, 4 * F1], "{:.3g} N",
        f"F = ke²/r² = {F2:.1f} N. The answer at 1.0 fm would be {F1:.0f} N, and the strong force must exceed these.", lvl="Moderate",
        calc=CALC("N", [TILE("k", 8.99e9, "N·m²/C²", disp="8.99 × 10⁹"), TILE("e", 1.602e-19, "C", disp="1.602 × 10⁻¹⁹"), TILE("r", 2.0, "fm", disp="2.0"), CONV("fm", "m", 1e-15), TILE("c", 3.00e8, "m/s", disp="3.00 × 10⁸")], ops=("×", "÷", "(", ")", "²"), solution=["k", "×", "e", "²", "÷", "(", "r", "×", "fm→m", ")", "²"])),
    PRN("What is the <f>energy of the photon</f> emitted when hydrogen drops from <v>n = 2</v> to <v>n = 1</v>?", E21, [E32, 3.40, calc.RY_EV], "{:.3g} eV",
        f"ΔE = 13.6 (1/1² − 1/2²) = {E21:.1f} eV.", lvl="Moderate",
        calc=CALC("eV", [TILE("Ry", 13.6, "eV"), NUM(1), NUM(2), NUM(3), NUM(4)], ops=("×", "÷", "+", "−", "(", ")", "²"), solution=["Ry", "×", "(", "1", "÷", "1", "²", "−", "1", "÷", "2", "²", ")"])),
    PRN("What <f>energy</f> is needed to ionize a hydrogen atom whose electron is in the <v>n = 2</v> shell?", 3.40, [E32, 6.80, E21], "{:.3g} eV",
        "E<sub>2</sub> = −13.6/4 = −3.40 eV, so 3.40 eV is needed.", lvl="Moderate"),
    PRN(STEM("Tungsten has these electron binding energies.", ["K shell = 69.5 keV", "L<sub>III</sub> shell = 10.2 keV"], "What is the [[energy of the characteristic photon]] emitted in an L → K transition?"), Ka_W, [L_W, K_W, K_W + L_W], "{:.1f} keV",
        f"The photon carries the difference: 69.5 − 10.2 = {Ka_W:.1f} keV.", lvl="Moderate"),
    PR("Which transition in hydrogen emits the highest-energy photon?", "n = 2 → n = 1", ["n = 3 → n = 2", "n = 4 → n = 3", "n = 5 → n = 4"],
       "Levels crowd together at larger n, so the jump to the ground state is by far the largest (10.2 eV against 1.89, 0.66, and 0.31 eV).", lvl="Moderate"),
    PR("Compared with an outer-shell electron in the same atom, an inner-shell electron is:", "bound more tightly, so more energy is needed to remove it",
       ["bound less tightly, because it is shielded by outer electrons", "bound equally, because binding depends only on Z", "bound more tightly only in elements with Z above 50"],
       "Inner electrons feel almost the full nuclear charge; outer electrons are shielded. K-shell binding energy is the largest in every atom.", lvl="Moderate"),
    PRN("A <v>6.0 MeV</v> electron moves perpendicular to a uniform <v>0.20 T</v> magnetic field. What is the <f>radius</f> of its path?", r6, [r_cl, 2 * r6, 3 * r6], "{:.1f} cm",
        f"pc = √(KE² + 2·KE·m₀c²) = {pc6:.2f} MeV, so r = pc / (299.8 B) = {pc6:.3f} / (299.8 × 0.20) = {r6 / 100:.4f} m = {r6:.1f} cm. The non-relativistic momentum gives {r_cl:.1f} cm.", lvl="Challenging"),
    PR("An inner-shell vacancy in an atom can be filled with emission of a characteristic x-ray or an Auger electron. Which statement is correct?", "In the Auger process the transition energy is given to another orbital electron, which is ejected instead of a photon being emitted",
       ["Auger electrons come from the nucleus", "A characteristic x-ray has an energy that depends on the energy of the particle that created the vacancy", "The Auger electron always has more energy than the characteristic x-ray from the same transition"],
       "Both release the vacancy energy. The Auger electron carries away the transition energy minus its own binding energy, so it has less energy than the x-ray would. Characteristic x-ray energy is set by the shells, not by the projectile.", lvl="Challenging"),
    PRN("Two protons <v>2.0 fm</v> apart repel with a force of <v>57.7 N</v>. At what <f>separation</f> is the force <v>14.4 N</v>?", 4.0, [1.0, 2.8, 8.0], "{:g} fm",
        "F fell by a factor of 57.7 / 14.4 = 4, so r grew by √4 = 2: r = 4.0 fm.", lvl="Challenging"),
]

INLINE = {0: [1, 5], 1: [2, 11]}

TERMS = ["Coulomb's law", 'magnetic force', 'binding energy']

TAKE = [
    [("Coulomb force goes as 1/r²: double the distance and the force falls to one quarter.", "coulomb-inverse-square")],
    [("A magnetic force does no work: speed and kinetic energy stay constant while the path curves, with r = p/(qB).", "magnetic-circle"),
     ("For electrons, r (m) = pc (MeV) / (299.8 × B (T)).", "bend-radius")],
    [("Rutherford: a small, dense, positive nucleus.", "rutherford"),
     ("Bohr: discrete shells, with E<sub>n</sub> = −13.6/n² eV for hydrogen.", "bohr-levels"),
     ("Inner shells are bound most tightly, and binding energy rises with Z. A characteristic x-ray carries the difference between two shell binding energies.", "characteristic-xray")],
]
