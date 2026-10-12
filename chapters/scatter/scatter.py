from blocks import *
import calc

es = calc.equiv_square(6, 18)

TOPIC = dict(
    id="scatter", domain=3, sub="III.A", title="Scatter factors and field shape",
    ref=dict(aapm="8.2", khan="9, 10", ford="11"),
    guide=[
        H("Collimator and phantom scatter"),
        P("Output per MU depends on field size for two separate reasons. Photons scattered in the treatment head (flattening filter, primary collimator, jaws) change the fluence that reaches the patient. This collimator scatter is set by the jaw opening. Photons scattered in the patient add dose at the point, and that depends on the field irradiating the phantom."),
        TABLE(["Factor", "Name", "How it is obtained", "Depends on"], [
            ["S<sub>c</sub>", "Collimator scatter factor (in-air output ratio)", "Chamber in air with a build-up cap at 100 cm; collimator setting A relative to 10 × 10 cm", "Collimator (jaw) opening"],
            ["S<sub>p</sub>", "Phantom scatter factor", "S<sub>cp</sub> / S<sub>c</sub>", "Field irradiating the phantom"],
            ["S<sub>cp</sub>", "Total scatter factor (output factor)", "Dose per MU in the phantom at the reference depth; field A relative to 10 × 10 cm", "Both"]]),
        EQ("S<sub>cp</sub>(A) = S<sub>c</sub>(A<sub>c</sub>) × S<sub>p</sub>(A)", "S<sub>p</sub> = S<sub>cp</sub> / S<sub>c</sub>"),
        P("All three equal 1.000 for the 10 × 10 cm reference field. Each rises with field size, so S<sub>cp</sub> is below 1 for smaller fields and above 1 for larger ones. S<sub>p</sub> cannot be measured on its own, so it is derived from S<sub>cp</sub> (phantom) and S<sub>c</sub> (air)."),
        P("The build-up cap for S<sub>c</sub> is thick enough to give electronic equilibrium in air at the chamber for the beam energy."),

        H("Blocked and shaped fields"),
        FIG("scatter_geometry", "A block under the collimators narrows the field in the phantom but leaves the jaw opening unchanged."),
        P("A shielding block changes the field reaching the phantom, not the jaw opening. Use S<sub>c</sub> for the jaw opening and S<sub>p</sub> for the equivalent square of the blocked field. The two scatter components are therefore tabulated separately."),

        H("Equivalent squares"),
        P("Output and depth-dose tables are measured for square fields. A rectangle is replaced by the square with the same area-to-perimeter ratio (Sterling's A/P rule)."),
        EQ("rectangle a × b: A/P = ab / [2(a + b)]", "square of side s: A/P = s/4", "s = 2ab / (a + b)"),
        EX("Equivalent square", STEM("", ["rectangular field = 6 × 18 cm"], "Find the [[equivalent square]]."), ["s = 2 × 6 × 18 / (6 + 18) = 216/24."], f"{es:.1f} cm."),
        P("The rule is least accurate for elongated rectangles. For irregular fields, Clarkson integration divides the field around the calculation point into sectors and sums their scatter contributions. Planning systems and second-check software do this; a hand calculation uses the equivalent square."),

    ],
    cards=[
        C("Name the two sources of scatter that make output depend on field size.", "Collimator (head) scatter, set by the jaw opening, and phantom (patient) scatter, set by the field that irradiates the phantom."),
        C("Define S<sub>c</sub> and say how it is measured.", "The collimator scatter factor: output in air for a given collimator setting relative to the 10 × 10 cm reference, measured with a chamber and build-up cap at 100 cm.", fig="scatter_geometry"),
        C("Define S<sub>p</sub> and say why it is derived, not measured directly.", "The phantom scatter factor. It cannot be isolated experimentally, so S<sub>p</sub> = S<sub>cp</sub>/S<sub>c</sub>, from a phantom measurement and an in-air measurement."),
        C("Define S<sub>cp</sub>. What is its value for the reference field?", "The total scatter factor (output factor): dose per MU in the phantom at the reference depth, relative to the 10 × 10 cm field. It is 1.000 for 10 × 10 cm."),
        C("A block narrows the field reaching the phantom while the jaws stay open. Which factor changes?", "S<sub>p</sub> changes, because the irradiated field is smaller. S<sub>c</sub> is set by the jaw opening and does not change."),
        C("What is the equivalent square of a 6 × 18 cm field?", f"{es:.1f} cm.", w=["s = 2ab/(a + b) = 2 × 6 × 18 / 24."]),
        C("State the A/P rule for equivalent squares.", "A rectangle and a square are equivalent when they have the same area-to-perimeter ratio. A/P = ab/[2(a + b)] for the rectangle and s/4 for the square, so s = 2ab/(a + b)."),
        C("When is Clarkson integration used instead of an equivalent square?", "For irregular or heavily blocked fields. The field around the calculation point is divided into sectors and their scatter contributions are summed."),
        C("S<sub>c</sub> = 0.985 and S<sub>p</sub> = 0.990. What is S<sub>cp</sub>?", "0.975.", w=["S<sub>cp</sub> = S<sub>c</sub> × S<sub>p</sub> = 0.985 × 0.990 = 0.975."]),
        C("Why does output per MU rise as the field gets larger?", "More scattering material, in the head and in the phantom, adds scattered photons at the point, so both S<sub>c</sub> and S<sub>p</sub> increase."),
        C("Why does the S<sub>c</sub> chamber need a build-up cap?", "To provide electronic equilibrium in air at the chamber, with a cap thick enough for d<sub>max</sub> at the beam energy."),
    ],
)

TERMS = ['collimator scatter', "Sterling's A/P rule", 'Clarkson integration']

TAKE = [
    [('S<sub>c</sub> follows the jaw opening (head scatter); S<sub>p</sub> follows the field irradiating the phantom. S<sub>cp</sub> = S<sub>c</sub> × S<sub>p</sub>, and all equal 1 for a 10 × 10 cm field.', 'scatter-factors')],
    [('A block changes S<sub>p</sub> but not S<sub>c</sub>.', 'block-effect')],
    [('Equivalent square of a rectangle: s = 2ab/(a + b). Clarkson integration handles irregular fields.', 'equivalent-square')],
]


# ---------------------------------------------------------------- practice questions
q_scp = 0.940 * 0.975
q_sp = 1.072 / 1.028
q_es820 = calc.equiv_square(8, 20)
q_blocked = 1.010
q_es618 = calc.equiv_square(6, 18); q_interp = 0.976 + (q_es618 - 8) / 2 * (1.000 - 0.976)
q_interp_area = 0.976 + ((6 * 18) ** 0.5 - 8) / 2 * (1.000 - 0.976)

PROBLEMS = [
    PR("The collimator scatter factor S<sub>c</sub> depends on:", "the jaw (collimator) opening", ["the field that irradiates the phantom", "the depth in the phantom", "the SSD"],
       "S<sub>c</sub> is the in-air output ratio. It changes with the jaw opening because scatter in the treatment head changes the fluence that leaves the machine. It does not depend on the patient or phantom.", lvl="Easy"),
    PR("The phantom scatter factor S<sub>p</sub> is obtained as:", "S<sub>cp</sub> divided by S<sub>c</sub>", ["S<sub>cp</sub> multiplied by S<sub>c</sub>", "S<sub>c</sub> divided by S<sub>cp</sub>", "a direct measurement with a chamber in air"],
       "S<sub>p</sub> cannot be measured on its own. A phantom measurement gives S<sub>cp</sub>, which contains both effects, and an in-air measurement gives S<sub>c</sub>. Then S<sub>p</sub> = S<sub>cp</sub> / S<sub>c</sub>.", lvl="Easy"),
    PR("Which statement is true for the 10 × 10 cm reference field?", "S<sub>c</sub>, S<sub>p</sub>, and S<sub>cp</sub> all equal 1.000", ["S<sub>c</sub> equals 1.000 but S<sub>p</sub> does not", "S<sub>cp</sub> equals 1.000 but S<sub>c</sub> and S<sub>p</sub> do not", "None of them is defined for this field"],
       "All three are ratios relative to the 10 × 10 cm field, so each is 1.000 there. They rise with field size and fall below 1 for smaller fields.", lvl="Easy"),
    PRN(STEM("A small field.", ["S<sub>c</sub> = 0.940", "S<sub>p</sub> = 0.975"], "What is the [[total scatter factor S<sub>cp</sub>]]?"), q_scp, [0.940 / 0.975, 0.975 / 0.940, 0.940 + 0.975], "{:.3f}",
        f"S<sub>cp</sub> = S<sub>c</sub> × S<sub>p</sub> = 0.940 × 0.975 = {q_scp:.3f}. Dividing the factors gives {0.940 / 0.975:.3f} or {0.975 / 0.940:.3f}, and adding them gives 1.915.", lvl="Moderate",
        calc=CALC("", [TILE("Sc", 0.940, "", disp="0.940"), TILE("Sp", 0.975, "", disp="0.975")], solution=["Sc", "×", "Sp"])),
    PR("S<sub>c</sub> is measured with a chamber in air. Why is a build-up cap placed on the chamber?", "To give electronic equilibrium at the chamber for the beam energy", ["To absorb photons scattered from the treatment head", "To add the backscatter that a phantom would provide", "To shield the chamber from contaminant electrons only"],
       "In air there is no surrounding material to set up electronic equilibrium, so the cap supplies it. It must be thick enough for the beam energy.", lvl="Moderate"),
    PR("A block is placed under the collimators and the jaws are left unchanged. Compared with the open field, the block changes:", "S<sub>p</sub>, but not S<sub>c</sub>", ["S<sub>c</sub>, but not S<sub>p</sub>", "both S<sub>c</sub> and S<sub>p</sub>", "neither S<sub>c</sub> nor S<sub>p</sub>"],
       "S<sub>c</sub> follows the jaw opening, which has not changed. S<sub>p</sub> follows the field that irradiates the phantom, which the block has narrowed.", lvl="Moderate"),
    PRN(STEM("Jaws open to 14 × 14 cm and blocks shape the field in the phantom to an equivalent square of 10 × 10 cm.", ["S<sub>c</sub>(14 × 14) = 1.010", "S<sub>p</sub>(14 × 14) = 1.012", "S<sub>p</sub>(10 × 10) = 1.000"], "What is the [[total scatter factor S<sub>cp</sub>]] of the blocked field?"), q_blocked, [1.010 * 1.012, 1.012, 1.000], "{:.3f}",
        f"S<sub>c</sub> uses the jaw opening (14 × 14 cm) and S<sub>p</sub> uses the irradiated field (10 × 10 cm): S<sub>cp</sub> = 1.010 × 1.000 = 1.010. Using the jaw field for S<sub>p</sub> as well gives {1.010 * 1.012:.3f}, and treating everything as 10 × 10 cm gives 1.000.", lvl="Challenging"),
    PR("Which statement about the equivalent square of a rectangular field is correct?", "The rectangle and its equivalent square have the same area-to-perimeter ratio", ["They have the same area", "They have the same perimeter", "They have the same diagonal"],
       "Sterling's rule matches A/P. A rectangle a × b has A/P = ab/[2(a + b)] and a square of side s has A/P = s/4.", lvl="Easy"),
    PRN(STEM("A rectangular field.", ["8 × 20 cm"], "What is the side of its [[equivalent square]]?"), q_es820, [(8 * 20) ** 0.5, (8 + 20) / 2, 8 * 20 / (8 + 20)], "{:.1f} cm",
        f"s = 2ab/(a + b) = 2 × 8 × 20 / 28 = {q_es820:.1f} cm. The equal-area square gives {(8 * 20) ** 0.5:.1f} cm, the average of the sides gives 14.0 cm, and leaving out the factor of 2 gives {8 * 20 / 28:.1f} cm.", lvl="Moderate",
        calc=CALC("cm", [TILE("2", 2), TILE("a", 8, "cm"), TILE("b", 20, "cm")], ops=("+", "×", "÷", "(", ")"), solution=["2", "×", "a", "×", "b", "÷", "(", "a", "+", "b", ")"])),
    PR("For which field is the equivalent square from the area-to-perimeter rule least accurate?", "An elongated rectangle, such as 2 × 30 cm", ["A 10 × 10 cm square", "A 10 × 12 cm rectangle", "A 15 × 15 cm square"],
       "The rule is an approximation that works well for fields close to square. It is least reliable for elongated rectangles, and irregular fields need Clarkson integration.", lvl="Moderate"),
]

INLINE = {0: [1, 2, 4, 5], 1: [6, 12], 2: [8, 9]}


# ---------------------------------------------------------------- practice questions that use a data table
import beamdata as bd
_es = calc.equiv_square(10, 20); q_sx1 = bd.sc_at(_es) * bd.sp_at(_es)
q_sx2 = bd.SC[15] * bd.SP[8]
q_sx3 = bd.SC[8] * bd.SP[8]

PROBLEMS += [
    PRN(STEM("An open rectangular field of 10 × 20 cm. Use the table and the equivalent square.", [], "Find the [[total scatter factor S<sub>cp</sub>]], interpolating linearly in field size.", tables=[bd.table_scatter([8, 10, 12, 15, 20])]),
        q_sx1, [bd.SC[12] * bd.SP[12], bd.SC[15] * bd.SP[15], bd.sc_at(200 ** 0.5) * bd.sp_at(200 ** 0.5)], "{:.3f}",
        f"The equivalent square is 2 × 10 × 20 / 30 = {_es:.1f} cm, between 12 and 15 cm. S<sub>c</sub> = 1.009 + (1.3/3) × (1.020 − 1.009) = {bd.sc_at(_es):.3f} and S<sub>p</sub> = 1.004 + (1.3/3) × (1.010 − 1.004) = {bd.sp_at(_es):.3f}, so S<sub>cp</sub> = {q_sx1:.3f}. Reading the 12 cm row gives {bd.SC[12] * bd.SP[12]:.3f}, the 15 cm row gives {bd.SC[15] * bd.SP[15]:.3f}, and the equal-area square (14.1 cm) gives {bd.sc_at(200 ** 0.5) * bd.sp_at(200 ** 0.5):.3f}.", lvl="Challenging",
        calc=CALC("", [TILE("Sc", bd.sc_at(_es), "", disp=f"{bd.sc_at(_es):.3f}"), TILE("Sp", bd.sp_at(_es), "", disp=f"{bd.sp_at(_es):.3f}")], solution=["Sc", "×", "Sp"])),
]


# ---------------------------------------------------------------- sorting and typed-number questions
PROBLEMS += [
    SORT("Does each statement describe S<sub>c</sub> or S<sub>p</sub>?", ["S<sub>c</sub>, collimator scatter", "S<sub>p</sub>, phantom scatter"],
         [("Follows the jaw opening", 0), ("Follows the field that reaches the phantom", 1), ("Measured in air with a build-up cap", 0), ("Obtained as S<sub>cp</sub> / S<sub>c</sub>", 1),
          ("Unchanged by a block under the jaws", 0), ("Falls when a block narrows the field", 1)],
         "S<sub>c</sub> describes the radiation leaving the head, which depends on the jaw opening and is measured in air with a build-up cap. S<sub>p</sub> describes the scatter inside the phantom, which depends on the field that reaches it, so a block changes S<sub>p</sub> but not S<sub>c</sub>.", lvl="Moderate"),
]
