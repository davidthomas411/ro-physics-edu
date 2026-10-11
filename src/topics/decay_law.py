from blocks import *
import calc

TH_TC, TH_I125, TH_IR = 6.0, 59.4, 73.8
f_tc = calc.frac_remaining(3.5, TH_TC); a_tc = 740 * f_tc
t10 = calc.time_to_fraction(0.10, TH_I125)
lam_ir = calc.lam(TH_IR)
tau_i = calc.mean_life(TH_I125); dinf = 7.0 * tau_i * 24
lam10 = calc.pct_per_unit_to_lambda(0.10)

TOPIC = dict(
    id="decay-law", domain=1, sub="I.B", title="Decay law and activity",
    ref=dict(aapm="2.2", khan="2", ford="2, 3"),
    guide=[
        H("Decay rate and the decay constant"),
        P("Decay is random, and every nucleus of a nuclide has the same chance of decaying per unit time, whatever its age. That probability per unit time is the decay constant, λ."),
        P("The decay rate is proportional to the number of nuclei present. Solving dN/dt = −λN gives:"),
        EQ("N(t) = N<sub>0</sub> e<sup>−λt</sup>"),
        P("Activity is the number of decays per unit time, A = λN, so it falls with the same exponential:"),
        EQ("A = λN", "A(t) = A<sub>0</sub> e<sup>−λt</sup>"),
        P("Units: 1 Bq = 1 decay per second. 1 Ci = 3.7 × 10<sup>10</sup> Bq exactly, so 1 mCi = 37 MBq."),

        H("Half-life and mean life"),
        EQ("T<sub>1/2</sub> = ln 2 / λ = 0.693 / λ", "τ = 1/λ = T<sub>1/2</sub> / ln 2 = 1.443 T<sub>1/2</sub>"),
        P("The half-life is the time for activity to fall to one half. The mean life, τ, is the average lifetime of a nucleus. After one mean life the activity has fallen to 1/e = 36.8%."),
        FIG("decay_curve", "Activity after each half-life. The dashed line marks one mean life, 1.44 half-lives."),
        P("After n half-lives the fraction left is (½)<sup>n</sup>. Seven half-lives leave under 1%; ten leave about 0.1%."),
        EQ("A = A<sub>0</sub> (½)<sup>t/T½</sup>", "t = T<sub>1/2</sub> log<sub>2</sub>(A<sub>0</sub>/A) = ln(A<sub>0</sub>/A) / λ"),

        H("Methods of calculation"),
        UL("t is a whole number of half-lives: halve repeatedly.",
           "Any other t: A = A<sub>0</sub> e<sup>−0.693 t / T½</sup>, with t and T<sub>1/2</sub> in the same unit.",
           "Time to reach a fraction: t = T<sub>1/2</sub> × log<sub>2</sub>(1/fraction). Reaching 10% takes 3.32 half-lives.",
           f"A rate quoted as “x% per hour” is the fraction lost each hour, so 1 − x remains after an hour and λ = −ln(1 − x). For 10% per hour, λ = {lam10:.3f} h<sup>−1</sup> and T<sub>1/2</sub> = {calc.LN2/lam10:.1f} h. Taking λ = 0.10 h<sup>−1</sup> gives 6.9 h."),

        H("Worked examples"),
        EX("Calibrated dose", STEM("A Tc-99m syringe is calibrated at 07:00.", ["T<sub>1/2</sub> = 6.0 h", "A = 740 MBq at 07:00"], "Find the [[activity at 10:30]]."),
           ["t = 3.5 h, so t/T<sub>1/2</sub> = 0.583 half-lives.", f"Fraction remaining = 2<sup>−0.583</sup> = {f_tc:.3f}.", f"A = 740 × {f_tc:.3f} = {a_tc:.0f} MBq."],
           f"{a_tc:.0f} MBq ({a_tc/37:.1f} mCi)."),
        EX("Time to decay", STEM("An I-125 seed is in storage.", ["T<sub>1/2</sub> = 59.4 d", "remaining activity = 10% of the original"], "Find the [[time]] to reach this activity."),
           ["t = T<sub>1/2</sub> × log<sub>2</sub>(1/0.10) = 59.4 × 3.32."], f"{t10:.0f} d, about 6.5 months."),
        EX("Percent lost per day", STEM("", ["Ir-192: T<sub>1/2</sub> = 73.8 d"], "Find the [[percentage of activity lost per day]]."),
           [f"λ = 0.693 / 73.8 d = {lam_ir:.5f} d<sup>−1</sup>."],
           "About 0.9% per day. The same method gives about 1.1% per month for Co-60 (T<sub>1/2</sub> 5.27 y) and 2.3% per year for Cs-137 (T<sub>1/2</sub> 30.1 y)."),

        H("Permanent implants"),
        P("A permanent implant delivers dose until the source has decayed. Integrating the falling dose rate gives a total dose equal to the initial dose rate times the mean life:"),
        EQ("D<sub>∞</sub> = Ḋ<sub>0</sub> τ = 1.443 Ḋ<sub>0</sub> T<sub>1/2</sub>", "D(t) = D<sub>∞</sub> (1 − e<sup>−t/τ</sup>)"),
        P("At t = T<sub>1/2</sub> the implant has delivered half of D<sub>∞</sub>."),
        EX("Total dose", STEM("A permanent I-125 implant.", ["T<sub>1/2</sub> = 59.4 d", "initial dose rate = 7.0 cGy/h"], "Find the [[total dose]]."),
           [f"τ = 59.4 / 0.693 = {tau_i:.1f} d = {tau_i*24:.0f} h.", f"D<sub>∞</sub> = 7.0 cGy/h × {tau_i*24:.0f} h."], f"{round(dinf,-2):,.0f} cGy ({dinf/100:.0f} Gy)."),

    ],
    cards=[
        C("What does the decay constant λ represent?", "The probability that a given nucleus decays per unit time (units 1/time). It is the same for every nucleus of a nuclide, whatever its age."),
        C("Write the decay law for the number of nuclei and for activity.", "N(t) = N<sub>0</sub> e<sup>−λt</sup> and A(t) = A<sub>0</sub> e<sup>−λt</sup>, because A = λN."),
        C("Define the becquerel and the curie. Convert 5 mCi to MBq.", ["1 Bq = 1 decay per second. 1 Ci = 3.7 × 10<sup>10</sup> Bq exactly.", "5 mCi = 5 × 37 = 185 MBq."]),
        C("Relate half-life, decay constant, and mean life.", "T<sub>1/2</sub> = ln 2 / λ = 0.693/λ, and τ = 1/λ = 1.443 T<sub>1/2</sub>."),
        C("What fraction of the activity remains after one mean life?", "1/e = 36.8%."),
        C("What fraction remains after 4 half-lives? After 10?", "(½)<sup>4</sup> = 1/16 = 6.25%. (½)<sup>10</sup> ≈ 0.1%.", fig="decay_curve"),
        C("A Tc-99m dose (T<sub>1/2</sub> = 6.0 h) holds 740 MBq at 07:00. What is the activity at 10:30?", f"{a_tc:.0f} MBq ({a_tc/37:.1f} mCi).",
          w=["t/T<sub>1/2</sub> = 3.5/6.0 = 0.583 half-lives.", f"Fraction = 2<sup>−0.583</sup> = {f_tc:.3f}.", f"740 × {f_tc:.3f} = {a_tc:.0f} MBq."]),
        C("An I-125 seed (T<sub>1/2</sub> = 59.4 d): how long until 10% of its activity remains?", f"{t10:.0f} d.", w=["t = T<sub>1/2</sub> × log<sub>2</sub>(10) = 59.4 × 3.32."]),
        C("Ir-192 has T<sub>1/2</sub> = 73.8 d. Roughly what percentage of its activity is lost per day?", "About 0.9% per day.", w=[f"λ = 0.693 / 73.8 = {lam_ir:.5f} d<sup>−1</sup> ≈ 0.94% per day."]),
        C("A source decays 10% per hour. What is its half-life?", f"About 6.6 h (roughly 7 h).",
          w=[f"Fraction remaining per hour is 0.90, so λ = −ln 0.90 = {lam10:.3f} h<sup>−1</sup>.", f"T<sub>1/2</sub> = 0.693 / {lam10:.3f} = {calc.LN2/lam10:.1f} h.", "Using λ = 0.10 h<sup>−1</sup> instead gives 6.9 h."]),
        C("A source decays from 12.0 mCi to 3.0 mCi in 9 days. What is its half-life?", "4.5 d.", w=["3.0/12.0 = ¼ = (½)<sup>2</sup>, so two half-lives in 9 d."]),
        C("How is the total dose from a permanent implant related to its initial dose rate?", "D<sub>∞</sub> = Ḋ<sub>0</sub> τ = 1.443 Ḋ<sub>0</sub> T<sub>1/2</sub>. At t = T<sub>1/2</sub> half of D<sub>∞</sub> has been delivered."),
        C("An I-125 implant (T<sub>1/2</sub> = 59.4 d) starts at 7.0 cGy/h. What total dose does it deliver?", f"About {round(dinf,-2):,.0f} cGy ({dinf/100:.0f} Gy).", w=[f"τ = 59.4/0.693 = {tau_i:.1f} d = {tau_i*24:.0f} h.", f"D<sub>∞</sub> = 7.0 × {tau_i*24:.0f} = {round(dinf,-2):,.0f} cGy."]),
    ],
)

TERMS = ['decay constant', 'activity', 'half-life', 'mean life']

TAKE = [
    [("A = λN and A = A<sub>0</sub>e<sup>−λt</sup>.", "decay-atoms"),
     ("1 Ci = 3.7 × 10<sup>10</sup> Bq, so 1 mCi = 37 MBq.", "ci-bq")],
    [("T<sub>1/2</sub> = 0.693/λ and τ = 1/λ = 1.443 T<sub>1/2</sub>. After one mean life, 36.8% remains.", "half-life-mean-life")],
    [("After n half-lives, (½)<sup>n</sup> remains. Keep time units consistent.", "half-life-steps"),
     ("“x% per time” means λ = −ln(1 − x), not λ = x.", "percent-per-time")],
    None,
    [("Total dose from a permanent implant = initial dose rate × mean life (1.443 T<sub>1/2</sub>).", "implant-dose")],
]
