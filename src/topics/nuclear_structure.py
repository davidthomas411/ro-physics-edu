from blocks import *
import math, calc

dm_h2 = calc.M_H1 + calc.M_N - calc.M_H2
be_h2 = calc.binding_mev(1, 2, calc.M_H2)
dm_he4 = 2 * calc.M_H1 + 2 * calc.M_N - calc.M_HE4
be_he4 = calc.binding_mev(2, 4, calc.M_HE4)
be_c12 = calc.binding_mev(6, 12, calc.M_C12)
be_o16 = calc.binding_mev(8, 16, calc.M_O16)
fis = 235 * (8.5 - 7.6)
dt_per_nuc, u_per_nuc = 17.6 / 5, 200 / 235

TOPIC = dict(
    id="nuclear-structure", domain=1, sub="I.B", title="Nuclear structure and binding energy",
    ref=dict(aapm="2.1", khan="2", ford="2"),
    guide=[
        H("Nuclide notation and classification"),
        P("A nuclide is specified by its proton number Z (which sets the element), neutron number N, and mass number A = Z + N. Ir-192 has Z = 77, so N = 115."),
        TABLE(["Family", "Same", "Different", "Example"], [
            ["Isotopes", "Z", "N and A", "I-125 and I-131"],
            ["Isotones", "N", "Z and A", "C-14 and N-15 (both N = 8)"],
            ["Isobars", "A", "Z and N", "Mo-99, Tc-99, Ru-99"],
            ["Isomers", "Z and A", "Energy state of the nucleus", "Tc-99m and Tc-99"]]),
        P("An isomer is an excited nucleus with a measurable lifetime, marked m. Tc-99m has a 6.0 h half-life and drops to Tc-99 by emitting a γ-ray."),

        H("Size and the nuclear force"),
        P("An atom is about 10<sup>−10</sup> m across; the nucleus is about 10<sup>−15</sup> m (a few fm), a hundred-thousandth of the diameter. Protons repel each other by the Coulomb force, which acts over long range. The strong force attracts every pair of nucleons but acts only over about 1 to 3 fm."),
        P("Neutrons add strong-force attraction without adding repulsion, so heavy nuclei need extra neutrons: stable light nuclei have N ≈ Z, while Pb-208 has N/Z = 1.5. On a chart of the nuclides, stable nuclei lie along a narrow band, and nuclei off the band decay toward it."),
        FIG("nuclide_chart", "Chart of the nuclides. Stable nuclei lie along a narrow band; unstable nuclei decay toward it."),

        H("Mass defect and binding energy"),
        P("A nucleus weighs less than the separate nucleons that make it. The difference is the mass defect, and its energy equivalent is the binding energy: the work needed to pull the nucleus apart."),
        EQ("Δm = Z·M(<sup>1</sup>H) + N·m<sub>n</sub> − M(atom)", "BE = Δm × 931.5 MeV/u"),
        P("Using the hydrogen atom mass M(<sup>1</sup>H) instead of the proton mass balances the electron masses, so tabulated atomic masses can be used directly."),
        FIG("be_curve", "Binding energy per nucleon. It rises steeply for light nuclei, peaks near iron and nickel, then falls slowly."),
        TABLE(["Nuclide", "A", "BE per nucleon (MeV)"], [
            ["H-2", "2", f"{be_h2 / 2:.2f}"], ["He-4", "4", f"{be_he4 / 4:.2f}"], ["C-12", "12", f"{be_c12 / 12:.2f}"], ["O-16", "16", f"{be_o16 / 16:.2f}"],
            ["Fe-56", "56", "8.79"], ["U-238", "238", "7.57"]]),
        P("Fusing light nuclei and splitting heavy nuclei both move the products up the curve toward the peak, so both release energy. D + T → He-4 + n gives 17.6 MeV; fission of U-235 gives about 200 MeV."),

        EX("Binding energy of the deuteron", STEM("", ["M(<sup>1</sup>H) = 1.007825 u", "m<sub>n</sub> = 1.008665 u", "M(<sup>2</sup>H) = 2.014102 u"], "Find the [[binding energy]] of the deuteron, in total and per nucleon."),
           [f"Δm = 1.007825 + 1.008665 − 2.014102 = {dm_h2:.6f} u", f"BE = {dm_h2:.6f} × 931.5 = {be_h2:.3f} MeV"], f"{be_h2:.2f} MeV, or {be_h2 / 2:.2f} MeV per nucleon."),
        EX("Fission energy from the binding energy curve", STEM("", ["U-235: 7.6 MeV per nucleon", "typical fission fragments: 8.5 MeV per nucleon"], "Estimate the [[energy released]] per fission."),
           ["All 235 nucleons move up the curve by about 8.5 − 7.6 = 0.9 MeV each.", "235 × 0.9 ≈ 212 MeV."], f"About {fis:.0f} MeV (the accepted value is about 200 MeV)."),
    ],
    cards=[
        C("What do Z, N, and A stand for, and how are they related?", "Z = protons (sets the element), N = neutrons, A = Z + N = mass number."),
        C("Define isotopes, isotones, isobars, and isomers, with an example of each.", "Isotopes: same Z (I-125, I-131). Isotones: same N (C-14, N-15). Isobars: same A (Mo-99, Tc-99, Ru-99). Isomers: same Z and A, different energy state (Tc-99m, Tc-99)."),
        C("How big is a nucleus compared with an atom?", "About 10<sup>−15</sup> m against 10<sup>−10</sup> m, a ratio of roughly 1 : 100,000."),
        C("What holds the nucleus together, and why do heavy nuclei contain extra neutrons?", "The strong force, which is attractive but short range. Neutrons add attraction without Coulomb repulsion, so heavy stable nuclei have N > Z (Pb-208: N/Z = 1.5)."),
        C("Define mass defect and binding energy.", "Mass defect: the separate nucleons weigh more than the nucleus. Binding energy: the energy equivalent of that difference, the work needed to disassemble the nucleus."),
        C("How is binding energy computed from atomic masses?", "BE = [Z·M(<sup>1</sup>H) + N·m<sub>n</sub> − M(atom)] × 931.5 MeV/u. The hydrogen atom mass balances the electron masses."),
        C("What is the binding energy of the deuteron?", f"{be_h2:.2f} MeV in total, {be_h2 / 2:.2f} MeV per nucleon."),
        C("Describe the shape of the binding-energy-per-nucleon curve.", "Steep rise for light nuclei, a broad peak near Fe-56 and Ni-62 (about 8.8 MeV), then a slow decline to about 7.6 MeV for uranium.", fig="be_curve"),
        C("Why do both fusion and fission release energy?", "Both move nuclei toward the peak of the curve, where they are more tightly bound. The extra binding energy is released.", fig="be_curve"),
        C("How much energy does D–T fusion release? U-235 fission?", f"D + T → He-4 + n: 17.6 MeV. U-235 fission: about 200 MeV. Per nucleon, fusion releases {dt_per_nuc:.1f} MeV and fission {u_per_nuc:.2f} MeV."),
    ],
)

PROBLEMS = [
    PR("Which pair are isotopes of the same element?", "I-125 and I-131", ["C-14 and N-14", "Tc-99m and Mo-99", "C-14 and N-15"],
       "Isotopes share Z. I-125 and I-131 both have Z = 53. C-14 and N-14 are isobars, C-14 and N-15 are isotones, and Mo-99 is a different element from Tc-99m.", lvl="Easy"),
    PRN("How many <f>neutrons</f> are in an Ir-192 nucleus (<v>Z = 77</v>)?", 115, [77, 192, 269], "{}", "N = A − Z = 192 − 77 = 115.", lvl="Easy"),
    PR("Which force holds protons together in the nucleus despite their mutual repulsion?", "The strong nuclear force", ["The gravitational force", "The magnetic force", "The Coulomb force"],
       "The Coulomb force pushes protons apart. At nuclear distances the short-range strong force between nucleons exceeds it and binds them.", lvl="Easy"),
    PR("Tc-99m and Tc-99 are best described as:", "isomers", ["isotopes of different elements", "isobars", "isotones"],
       "They have the same Z and A and differ in the energy state of the nucleus, which defines isomers. They are also isotopes of one element, but isomer is the specific relationship.", lvl="Easy"),
    PR("Which pair are isobars?", "Co-60 and Ni-60", ["Co-60 and Co-59", "Ni-60 and Ni-62", "Ni-60 and Zn-62"],
       "Isobars share A. Co-60 and Ni-60 both have A = 60 with different Z. The Co and Ni pairs are isotopes, and Ni-60 and Zn-62 differ in A.", lvl="Moderate"),
    PRN(STEM("", ["M(<sup>1</sup>H) = 1.007825 u", "m<sub>n</sub> = 1.008665 u", "M(<sup>2</sup>H) = 2.014102 u"], "What is the [[binding energy]] of the deuteron?"), be_h2, [be_h2 / 2, 2 * be_h2, calc.ME], "{:.2f} MeV",
        f"Δm = {dm_h2:.6f} u, so BE = {dm_h2:.6f} × 931.5 = {be_h2:.2f} MeV. Half of that, {be_h2 / 2:.2f} MeV, is the value per nucleon.", lvl="Moderate",
        calc=CALC("MeV", [TILE("M(¹H)", 1.007825, "u", id="H1"), TILE("mₙ", 1.008665, "u", id="n"), TILE("M(²H)", 2.014102, "u", id="H2"), CONV("u", "MeV", 931.5), TILE("mₑ", 0.000549, "u", id="me")], ops=("×", "÷", "+", "−", "(", ")"), solution=["(", "H1", "+", "n", "−", "H2", ")", "×", "u→MeV"])),
    PRN("The He-4 nucleus has a total binding energy of <v>28.3 MeV</v>. What is its <f>binding energy per nucleon</f>?", be_he4 / 4, [be_he4 / 8, be_he4 / 2, be_he4], "{:.2f} MeV",
        "28.3 MeV / 4 nucleons = 7.07 MeV per nucleon.", lvl="Moderate"),
    PR("Why do heavy stable nuclei contain more neutrons than protons?", "Extra neutrons add strong-force attraction without adding Coulomb repulsion",
       ["Neutrons carry the positive charge that stabilizes the nucleus", "Neutrons are lighter than protons, so they lower the total mass", "The strong force acts only between neutrons"],
       "Protons repel one another over long range. Neutrons dilute that repulsion while still binding through the strong force.", lvl="Moderate"),
    PR("Which nucleus has the highest binding energy per nucleon of those listed?", "Fe-56", ["H-2", "He-4", "U-238"],
       "The curve peaks near Fe-56 and Ni-62 at about 8.8 MeV per nucleon, against 1.1 for H-2, 7.1 for He-4, and 7.6 for U-238.", lvl="Moderate"),
    PR("Energy is released in nuclear reactions when:", "light nuclei fuse or heavy nuclei split, because both move the products toward the peak of the binding energy curve",
       ["only light nuclei fuse", "only heavy nuclei split", "nuclei near the peak of the curve fuse"],
       "Any change that increases the binding energy per nucleon releases energy. Fusing nuclei at the peak would move them down the curve and need energy.", lvl="Moderate"),
    PRN(STEM("", ["U-235: 7.6 MeV per nucleon", "fission fragments: 8.5 MeV per nucleon"], "Estimate the [[energy released]] per fission."), fis, [fis / 10, fis / 2, fis * 2], "{:.0f} MeV",
        f"235 nucleons × (8.5 − 7.6) MeV = {fis:.0f} MeV.", lvl="Challenging"),
    PRN(STEM("", ["M(O-16) = 15.994915 u", "M(<sup>1</sup>H) = 1.007825 u", "m<sub>n</sub> = 1.008665 u"], "What is the [[binding energy per nucleon]] of O-16?"), be_o16 / 16, [be_o16 / 32, be_o16 / 8, be_o16], "{:.2f} MeV",
        f"Δm = 8(1.007825) + 8(1.008665) − 15.994915 = {8 * calc.M_H1 + 8 * calc.M_N - calc.M_O16:.6f} u, so BE = {be_o16:.1f} MeV. Per nucleon: {be_o16:.1f}/16 = {be_o16 / 16:.2f} MeV.", lvl="Challenging"),
    PRN(STEM("", ["D–T fusion: 17.6 MeV from 5 nucleons", "U-235 fission: about 200 MeV from 235 nucleons"], "Fusion releases how many [[times more energy per nucleon]]?"), dt_per_nuc / u_per_nuc, [1.0, 0.24, 41.0], "{:.1f}",
        f"Fusion: 17.6/5 = {dt_per_nuc:.2f} MeV per nucleon. Fission: 200/235 = {u_per_nuc:.2f} MeV per nucleon. Ratio {dt_per_nuc / u_per_nuc:.1f}.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 4], 1: [3, 8]}

TERMS = ['nuclide', 'isomer', 'strong force', 'mass defect', 'binding energy']

TAKE = [
    [("Isotopes share Z, isotones share N, isobars share A. Isomers share Z and A and differ only in energy state (Tc-99m and Tc-99).", "nuclide-families")],
    [("The strong force is attractive and short range; the Coulomb force is repulsive and long range.", "nuclear-forces"),
     ("Heavy stable nuclei have N > Z.", "stability-line")],
    [("BE = Δm × 931.5 MeV/u, using atomic masses with M(<sup>1</sup>H).", "mass-defect"),
     ("BE per nucleon peaks near Fe-56 at about 8.8 MeV, so fusion of light nuclei and fission of heavy nuclei both release energy.", "be-curve")],
]


# ---------------------------------------------------------------- sorting question
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Is each pair of nuclides isotopes, isotones, isobars, or isomers?", ["Isotopes", "Isotones", "Isobars", "Isomers"],
         [("C-12 and C-14", 0), ("I-125 and I-131", 0), ("C-14 and N-15", 1), ("I-131 and Xe-132", 1), ("C-14 and N-14", 2), ("Mo-99 and Tc-99", 2), ("Tc-99m and Tc-99", 3), ("Co-60m and Co-60", 3)],
         "Isotopes share Z, so they are the same element. Isotones share N: C-14 has 6 protons and 8 neutrons and N-15 has 7 and 8. Isobars share A: C-14 and N-14 are both A = 14. Isomers are the same nuclide in different energy states, with the same Z and A.", lvl="Moderate"),
]
INLINE.setdefault(0, []).append(_n0 + 1)


# ---------------------------------------------------------------- tap-the-figure questions
_zn = {5: range(5, 9), 6: range(4, 9), 7: range(5, 10), 8: range(6, 10)}; _sy = {5: "B", 6: "C", 7: "N", 8: "O"}
_chart = FS(x=dict(min=3.5, max=9.5, ticks=[4, 5, 6, 7, 8, 9], label="Neutron number N"), y=dict(min=4.5, max=8.5, ticks=[5, 6, 7, 8], label="Proton number Z"),
            cells=[(n, z, f"{_sy[z]}-{z + n}") for z, ns in _zn.items() for n in ns], h=300, label="A small part of the chart of the nuclides")
_n1 = len(PROBLEMS)
PROBLEMS += [
    FIGQ(STEM("A small part of the chart of the nuclides. Each square is one nuclide.", ["reference nuclide: C-14 (Z = 6, N = 8)"], "Tap the [[isotone of C-14]] in the nitrogen row (Z = 7)."), _chart, [(7.5, 8.5, 6.5, 7.5)],
         "Isotones have the same number of neutrons. C-14 has N = 8, so the isotone in the nitrogen row is N-15 (7 protons, 8 neutrons). It sits directly above C-14 in the chart.", lvl="Moderate", note="N-15"),
    FIGQ(STEM("The same chart.", ["reference nuclide: C-14 (A = 14)"], "Tap the [[isobar of C-14]] in the nitrogen row (Z = 7)."), _chart, [(6.5, 7.5, 6.5, 7.5)],
         "Isobars have the same mass number A = Z + N. In the nitrogen row, A = 14 means N = 7, so the isobar is N-14. Isobars lie along a diagonal in the chart.", lvl="Moderate", note="N-14"),
]
INLINE.setdefault(0, []).extend([_n1 + 1, _n1 + 2])
