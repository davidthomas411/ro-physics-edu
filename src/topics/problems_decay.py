"""Problem sets for the three decay topics written before problem sets were added. Cards keep their ids; problems follow them."""
from blocks import *
import math, calc

a_tc = 925 * calc.frac_remaining(6.5, 6.0)
a_ir = 370 * calc.frac_remaining(120, 73.8)
a_seeds0 = 72 * 0.32; a_seeds = a_seeds0 * calc.frac_remaining(45, 59.4)
t_lu = calc.time_to_fraction(25 / 150, 6.65)
th6 = calc.LN2 / calc.pct_per_unit_to_lambda(0.06)
tau_i = calc.mean_life(59.4); d_inf = 7.5 * tau_i * 24 / 100
n_hl = calc.hvl_count(0.01)
tp_t, td_t = 36.0, 4.0; lp, ld = calc.lam(tp_t), calc.lam(td_t); tmax = math.log(ld / lp) / (ld - lp)
mo_tc = calc.transient_ratio(65.94, 6.0067)
emax_beta_plus = 1.70 - 2 * calc.ME

DECAY_LAW = [
    PRM("Which quantities determine the activity of a radioactive sample?", ["The number of radioactive nuclei present", "The decay constant"], ["The chemical form of the source", "The energy of the emitted photons"],
        "A = λN. Chemical form and photon energy do not enter.", lvl="Easy"),
    PRN("An activity of <v>1.48 GBq</v> is how many <f>millicuries</f>?", 40.0, [4.0, 400.0, 4000.0], "{:g} mCi", "1 mCi = 37 MBq, so 1480 MBq / 37 MBq/mCi = 40 mCi.", lvl="Easy"),
    PR("What fraction of the original activity remains after 5 half-lives?", "1/32, about 3%", ["1/10, or 10%", "1/16, about 6%", "1/64, about 1.6%"], "(½)<sup>5</sup> = 1/32 = 3.1%.", lvl="Easy"),
    PR("How is the mean life of a radionuclide related to its half-life?", "Mean life = 1.44 × half-life", ["Mean life = 0.693 × half-life", "Mean life = half-life", "Mean life = 2 × half-life"],
       "τ = 1/λ = T<sub>1/2</sub>/ln 2 = 1.443 T<sub>1/2</sub>.", lvl="Easy"),
    PRN(STEM("A Tc-99m syringe is calibrated at 08:00.", ["T<sub>1/2</sub> = 6.0 h", "A = 925 MBq at 08:00"], "What is the [[activity at 14:30]]?"), a_tc, [a_tc / 2, 925 / 2, 925 * calc.frac_remaining(3.0, 6.0)], "{:.0f} MBq",
        f"t = 6.5 h = 1.083 half-lives. A = 925 × 2<sup>−1.083</sup> = 925 × {calc.frac_remaining(6.5, 6.0):.4f} = {a_tc:.0f} MBq.", lvl="Moderate",
        calc=CALC("MBq", [TILE("A₀", 925, "MBq", id="A0"), TILE("t", 6.5, "h"), TILE("T½", 6.0, "h", id="T"), NUM(2), TILE("ln 2", 0.693, "", id="ln2")], ops=("×", "÷", "−", "(", ")", "2^("), solution=["A0", "×", "2^(", "−", "t", "÷", "T", ")"])),
    PRN(STEM("An Ir-192 HDR source.", ["T<sub>1/2</sub> = 73.8 d", "A = 370 GBq when installed"], "What is its [[activity after 120 days]]?"), a_ir, [92.5, 185.0, 233.0], "{:.0f} GBq",
        f"120 d / 73.8 d = 1.626 half-lives. A = 370 × 2<sup>−1.626</sup> = 370 × {calc.frac_remaining(120, 73.8):.4f} = {a_ir:.0f} GBq.", lvl="Moderate"),
    PRN(STEM("A prostate implant uses I-125 seeds.", ["72 seeds", "0.32 mCi each on the day of implant", "T<sub>1/2</sub> = 59.4 d"], "What is the [[total activity 45 days later]]?"), a_seeds, [0.32 * calc.frac_remaining(45, 59.4), a_seeds0 / 2, a_seeds0 * calc.frac_remaining(45, 85.69)], "{:.3g} mCi",
        f"Initial total = 72 × 0.32 = {a_seeds0:.2f} mCi. Fraction left = 2<sup>−45/59.4</sup> = {calc.frac_remaining(45, 59.4):.4f}. Total = {a_seeds:.2f} mCi.", lvl="Moderate"),
    PRN("A sample's activity falls from <v>120 MBq</v> to <v>15 MBq</v> in <v>9.0 hours</v>. What is its <f>half-life</f>?", 3.0, [1.5, 4.5, 9.0], "{:g} h",
        "120/15 = 8 = 2<sup>3</sup>, so three half-lives passed in 9.0 h: T<sub>1/2</sub> = 3.0 h.", lvl="Moderate"),
    PRN(STEM("A Lu-177 dose.", ["T<sub>1/2</sub> = 6.65 d", "150 MBq at calibration"], "[[How long]] until it has decayed to <v>25 MBq</v>?"), t_lu, [2 * 6.65, 3 * 6.65, 6.65], "{:.1f} d",
        f"150/25 = 6, so t = T<sub>1/2</sub> log<sub>2</sub>6 = 6.65 × 2.585 = {t_lu:.1f} d.", lvl="Moderate"),
    PR("Which of these has the largest decay constant: Cs-137 (30.1 y), Co-60 (5.27 y), Ir-192 (73.8 d), I-125 (59.4 d)?", "I-125", ["Cs-137", "Co-60", "Ir-192"],
       "λ = 0.693/T<sub>1/2</sub>, so the shortest half-life has the largest λ: 59.4 d is shorter than 73.8 d, 5.27 y, or 30.1 y.", lvl="Moderate"),
    PRN("A source loses <v>6.0%</v> of its activity each day. What is its <f>half-life</f>?", th6, [0.5 / 0.06, calc.LN2 / 0.06, 1 / 0.06], "{:.1f} d",
        f"The fraction remaining per day is 0.94, so λ = −ln 0.94 = {calc.pct_per_unit_to_lambda(0.06):.5f} d<sup>−1</sup> and T<sub>1/2</sub> = 0.693/λ = {th6:.1f} d. Using λ = 0.06 d<sup>−1</sup> directly gives {calc.LN2 / 0.06:.1f} d.", lvl="Challenging"),
    PRN(STEM("A permanent I-125 implant.", ["T<sub>1/2</sub> = 59.4 d", "initial dose rate = 7.5 cGy/h"], "What is the [[total dose]] to infinite time?"), d_inf, [7.5 * tau_i / 100, 7.5 * 59.4 * 24 / 100, 2 * d_inf], "{:.0f} Gy",
        f"D<sub>∞</sub> = Ḋ<sub>0</sub> τ = 7.5 cGy/h × (1.443 × 59.4 × 24 h) = {d_inf * 100:,.0f} cGy = {d_inf:.0f} Gy. Using T<sub>1/2</sub> instead of τ gives {7.5 * 59.4 * 24 / 100:.0f} Gy.", lvl="Challenging"),
    PRN("What <f>percentage of the total dose</f> from a permanent I-125 implant has been delivered after <v>119 days</v> (two half-lives)?", 75.0, [50.0, 63.2, 87.5], "{:g}%",
        "The fraction delivered is 1 − e<sup>−t/τ</sup> = 1 − 2<sup>−t/T<sub>1/2</sub></sup> = 1 − ¼ = 75%.", lvl="Challenging"),
    PRN("What is the <f>mean life</f> of Tc-99m (<v>T<sub>1/2</sub> = 6.0 h</v>)?", calc.mean_life(6.0), [0.693 * 6.0, 6.0, 12.0], "{:.2f} h",
        f"τ = 6.0 / 0.693 = {calc.mean_life(6.0):.2f} h.", lvl="Challenging"),
]

DECAY_MODES = [
    PR("What is the daughter nuclide when Po-210 (Z = 84) decays by α emission?", "Pb-206 (Z = 82)", ["Pb-210 (Z = 82)", "Bi-210 (Z = 83)", "Rn-206 (Z = 86)"],
       "An α particle carries off 2 protons and 2 neutrons: A falls by 4 and Z by 2.", lvl="Easy"),
    PR("Which of these radionuclides is a positron emitter used for PET?", "F-18", ["Tc-99m", "I-125", "Cs-137"], "F-18 is proton-rich and decays mainly by β⁺. Tc-99m emits γ-rays, I-125 decays by electron capture, and Cs-137 by β⁻.", lvl="Easy"),
    PR("Which decay raises Z by one without changing A?", "β⁻ decay", ["β⁺ decay", "Electron capture", "α decay"], "A neutron becomes a proton and an electron is emitted.", lvl="Easy"),
    PRM("Which radiations can follow an electron-capture event in the daughter atom?", ["Characteristic x-rays", "Auger electrons"], ["511 keV annihilation photons", "β⁻ particles"],
        "Capture leaves an inner-shell vacancy, which is filled with emission of a characteristic x-ray or an Auger electron. No positron is emitted, so there are no annihilation photons.", lvl="Easy"),
    PR("A nuclide has a decay energy (atomic mass difference) of <v>0.80 MeV</v> between parent and daughter. Which proton-rich <f>decay</f> can occur?", "Electron capture only", ["β⁺ decay only", "Both β⁺ decay and electron capture", "Neither"],
       "β⁺ decay needs at least 1.022 MeV (two electron masses) of available energy. Electron capture has no such threshold.", lvl="Moderate"),
    PR("Why does a positron emitter produce two 511 keV photons?", "The positron annihilates with an electron, and momentum conservation sends two photons in opposite directions",
       ["The nucleus emits two γ-rays at each decay", "The positron splits into two photons in flight", "Electron capture accompanies every β⁺ decay"],
       "Annihilation turns the two rest masses (2 × 511 keV) into radiation. Starting at rest, the photons must be back to back.", lvl="Moderate"),
    PRM("Which statements about internal conversion are correct?", ["The excitation energy is given to an orbital electron", "It leaves a shell vacancy, so characteristic x-rays or Auger electrons follow", "It competes with γ emission"], ["The atomic number changes by one", "A positron is ejected"],
        "Internal conversion is an alternative to γ emission: the nucleus de-excites by ejecting an orbital electron. Z and A are unchanged.", lvl="Moderate"),
    PR("I-131 (Z = 53) decays by β⁻ emission. What is the daughter nuclide?", "Xe-131 (Z = 54)", ["Te-131 (Z = 52)", "I-130 (Z = 53)", "Xe-127 (Z = 54)"], "β⁻ raises Z by one at constant A.", lvl="Moderate"),
    PR("Tc-99m decays by:", "isomeric transition (γ emission or internal conversion) to Tc-99, with no change in Z or A", ["β⁻ decay to Ru-99", "α decay to Nb-95", "electron capture to Mo-99"],
       "Tc-99m is an excited, metastable state of Tc-99. It drops to the ground state, emitting a 140 keV γ-ray.", lvl="Moderate"),
    PRN("A positron emitter has an atomic mass difference of <v>1.70 MeV</v> between parent and daughter. What is the <f>maximum positron kinetic energy</f>?", emax_beta_plus, [calc.ME, 1.70, 1.70 + 2 * calc.ME], "{:.3f} MeV",
        f"β⁺ decay must pay for creating the positron and for the extra electron: E<sub>max</sub> = 1.70 − 1.022 = {emax_beta_plus:.3f} MeV.", lvl="Challenging"),
    PR("A nuclide has too few neutrons for its number of protons. Which decay modes can bring it toward stability?", "β⁺ decay or electron capture, both of which convert a proton into a neutron",
       ["β⁻ decay, which converts a proton into a neutron", "α emission only", "γ emission, which changes the neutron-to-proton ratio"],
       "A proton-rich nucleus lies below the stable band. Turning a proton into a neutron (β⁺ or EC) moves it back. β⁻ does the opposite, and γ emission changes neither Z nor N.", lvl="Challenging"),
    PR("Why is an α emitter such as Ra-223 a small external hazard but effective in radiopharmaceutical therapy?", "Its α particles travel only tens of micrometres, so they are stopped by skin but deposit a high LET inside tissue next to the nuclide",
       ["Its α particles are highly penetrating and escape the body", "α particles have low LET, so only a small dose is delivered", "It emits mainly γ-rays that treat the tumour"],
       "A 5–7 MeV α particle travels less than 100 µm in tissue. Outside the body it cannot pass the outer skin layer; inside it delivers its energy within a few cell diameters.", lvl="Challenging"),
]

EQUILIBRIUM = [
    PR("Which condition gives secular equilibrium?", "The parent half-life is much longer than the daughter half-life", ["The parent half-life is slightly longer than the daughter's", "The parent half-life is shorter than the daughter's", "The two half-lives are equal"],
       "If the parent barely decays during many daughter half-lives, the daughter activity settles at the parent's activity.", lvl="Easy"),
    PR("In secular equilibrium, the activity of the daughter is:", "equal to the activity of the parent", ["twice the activity of the parent", "half the activity of the parent", "zero, because the daughter decays away"],
       "The daughter decays as fast as it is fed, so its activity settles at the parent's.", lvl="Easy"),
    PR("Which parent–daughter pair shows transient equilibrium?", "Mo-99 → Tc-99m", ["Ra-226 → Rn-222", "Sr-90 → Y-90", "Cs-137 → Ba-137m"],
       "Mo-99 (65.9 h) outlives Tc-99m (6.0 h) by a factor of 11, which is not large enough for secular equilibrium. The other three parents live far longer than their daughters.", lvl="Easy"),
    PRN(STEM("A parent decays to a daughter.", ["parent T<sub>1/2</sub> = 12.0 h", "daughter T<sub>1/2</sub> = 2.0 h"], "At transient equilibrium, what is the [[ratio of daughter activity to parent activity]] (ignoring branching)?"), 1.2, [1 / 1.2, 1.0, 6.0], "{:.2f}",
        "A<sub>d</sub>/A<sub>p</sub> = T<sub>p</sub>/(T<sub>p</sub> − T<sub>d</sub>) = 12.0 / (12.0 − 2.0) = 1.20.", lvl="Moderate"),
    PRN(STEM("", ["parent T<sub>1/2</sub> = 36 h", "daughter T<sub>1/2</sub> = 4 h", "no daughter present at t = 0"], "At what [[time]] does the daughter activity peak?"), tmax, [tmax / 2, 20.0, 36.0], "{:.1f} h",
        f"t<sub>max</sub> = ln(λ<sub>d</sub>/λ<sub>p</sub>) / (λ<sub>d</sub> − λ<sub>p</sub>) = ln(9) / ({ld:.4f} − {lp:.4f}) = {tmax:.1f} h.", lvl="Moderate"),
    PRN(STEM("A sealed Sr-90 source has stood for weeks.", ["Sr-90: T<sub>1/2</sub> = 28.8 y, A = 40 MBq", "Y-90: T<sub>1/2</sub> = 64 h"], "What is the [[activity of the Y-90 daughter]]?"), 40.0, [4.0, 20.0, 80.0], "{:g} MBq",
        "Sr-90 is long-lived compared with Y-90, so the pair is in secular equilibrium and the daughter activity equals the parent's, 40 MBq.", lvl="Moderate"),
    PR("In transient equilibrium the daughter activity is:", "higher than the parent's, by the factor T<sub>p</sub>/(T<sub>p</sub> − T<sub>d</sub>)", ["equal to the parent's", "lower than the parent's", "zero"],
       "With a shorter-lived daughter the activity ratio is above one: each daughter atom decays faster, so a given number of atoms gives more activity.", lvl="Moderate"),
    PRN("Ignoring branching, what is the <f>ratio of Tc-99m to Mo-99 activity</f> at transient equilibrium (T<sub>1/2</sub> = <v>6.01 h</v> and <v>65.94 h</v>)?", mo_tc, [1 / mo_tc, 1.0, 1.5], "{:.2f}",
        f"65.94 / (65.94 − 6.01) = {mo_tc:.2f}. (The real ratio is about 0.96 because only about 88% of Mo-99 decays feed Tc-99m.)", lvl="Moderate"),
    PRN("In secular equilibrium starting with no daughter, what <f>percentage</f> of the final daughter activity has grown in after <v>one daughter half-life</v>?", 50.0, [25.0, 63.2, 75.0], "{:g}%",
        "The daughter activity grows as 1 − 2<sup>−t/T<sub>d</sub></sup>. At t = T<sub>d</sub> that is 1 − ½ = 50%. (63.2% is the answer for one mean life.)", lvl="Challenging"),
    PRN("In secular equilibrium, about how many <f>daughter half-lives</f> are needed to reach <v>99%</v> of the equilibrium activity?", n_hl, [3.3, 5.0, 10.0], "{:.1f}",
        f"1 − 2<sup>−n</sup> = 0.99 gives 2<sup>−n</sup> = 0.01, so n = log<sub>2</sub>100 = {n_hl:.1f}.", lvl="Challenging"),
    PR("Which statement about transient equilibrium is correct?", "The daughter activity stays above the parent's by a constant factor, and both fall with the parent's half-life", ["The daughter and parent activities become equal", "The daughter activity stays constant while the parent decays", "The daughter decays with its own half-life from the start"],
       "In transient equilibrium the daughter activity is higher than the parent's by a constant factor, and both fall with the parent's half-life. Equal activities are the secular limit, a constant daughter activity needs a parent that barely decays, and the daughter's own half-life governs only the early build-up.", lvl="Challenging"),
]
EXTRA = {"decay-law": DECAY_LAW, "decay-modes": DECAY_MODES, "equilibrium": EQUILIBRIUM}
PLACE = {"decay-law": {0: [1, 2], 1: [3, 4], 2: [5, 8]}, "decay-modes": {0: [3, 11], 1: [1, 5, 6], 2: [4, 7]}, "equilibrium": {0: [5], 1: [1, 2, 3]}}


# ---------------------------------------------------------------- sorting, matching, and typed-number questions
import math as _m, calc as _calc
_n_dm = len(DECAY_MODES)
DECAY_MODES += [
    SORT("Sort each radionuclide into the decay mode it mainly uses.", ["β⁻ emitter", "β⁺ emitter", "Electron capture", "α emitter"],
         [("Y-90", 0), ("Lu-177", 0), ("I-131", 0), ("Ir-192", 0), ("F-18", 1), ("I-125", 2), ("Pd-103", 2), ("Ra-223", 3)],
         "Neutron-rich nuclei made in reactors decay by β⁻. Proton-rich nuclei decay by β⁺ or electron capture, and F-18 has enough energy (1.656 MeV, above the 1.022 MeV threshold) for β⁺. I-125 and Pd-103 have too little, so electron capture is their only route. Ra-223 is a heavy nucleus and emits α particles.", lvl="Easy"),
    SORT("Match each decay to what it does to the nucleus.", ["Z + 1, A unchanged", "Z − 1, A unchanged", "Z − 2, A − 4"],
         [("β⁻", 0), ("β⁺", 1), ("Electron capture", 1), ("α", 2)],
         "β⁻ turns a neutron into a proton. β⁺ and electron capture turn a proton into a neutron, so A does not change. An α particle carries away 2 protons and 2 neutrons.", lvl="Easy", mode="match"),
    SORT("Which of these processes leave a vacancy in an inner electron shell?", ["Leaves a shell vacancy", "Does not"],
         [("Electron capture", 0), ("Internal conversion", 0), ("β⁻ decay", 1), ("α decay", 1), ("γ emission", 1)],
         "Electron capture takes an inner-shell electron into the nucleus, and internal conversion ejects an orbital electron, so both leave a vacancy that is filled with a characteristic x-ray or an Auger electron. β⁻ decay, α decay, and γ emission do not remove an orbital electron.", lvl="Moderate"),
]
PLACE["decay-modes"].setdefault(3, []).append(_n_dm + 1); PLACE["decay-modes"].setdefault(1, []).append(_n_dm + 2); PLACE["decay-modes"].setdefault(2, []).append(_n_dm + 3)
_n_dl = len(DECAY_LAW)
DECAY_LAW += [
    TYPED(STEM("A Co-60 source with T<sub>1/2</sub> = 5.27 y.", ["time in use = 10 y"], "What [[percentage of the activity]] remains?"), 100 * 2 ** (-10 / 5.27), 0.015, "%",
        "10 y is 10/5.27 = 1.90 half-lives, so the fraction left is (½)<sup>1.90</sup> = 0.268, or 26.8%.", lvl="Moderate"),
    TYPED(STEM("A source loses 2.0% of its activity each day.", [], "What is its [[half-life]]?"), _m.log(2) / -_m.log(1 - 0.02), 0.004, "d",
        "“2% per day” means λ = −ln(1 − 0.02) = 0.0202 per day, not 0.02. T<sub>1/2</sub> = 0.693 / 0.0202 = 34.3 d. Taking λ = 0.02 gives 34.7 d, which is too long.", lvl="Challenging"),
]
PLACE["decay-law"].setdefault(2, []).extend([_n_dl + 1, _n_dl + 2])
_n_eq = len(EQUILIBRIUM)
EQUILIBRIUM += [
    TYPED(STEM("Mo-99 (T<sub>1/2</sub> = 65.94 h) decays to Tc-99m (T<sub>1/2</sub> = 6.007 h) in a generator immediately after elution.", [], "After how many hours is the [[Tc-99m activity at its peak]]?"), _calc.t_max(65.94, 6.0067), 0.015, "h",
        "The peak is at t = ln(λ<sub>d</sub>/λ<sub>p</sub>) / (λ<sub>d</sub> − λ<sub>p</sub>), with λ<sub>p</sub> = 0.01051 h<sup>−1</sup> and λ<sub>d</sub> = 0.1154 h<sup>−1</sup>: ln(10.98) / 0.1049 = 22.8 h. There the daughter activity equals the parent activity.", lvl="Challenging"),
]
PLACE["equilibrium"].setdefault(2, []).append(_n_eq + 1)


# ---------------------------------------------------------------- tap-the-figure questions
_t12 = 59.4
_fig_decay = FS(x=dict(min=0, max=180, ticks=[0, 30, 60, 90, 120, 150, 180], label="Time (days)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Activity (% of initial)", fmt="pct"),
                series=[dict(pts=PTS(lambda t: 100 * 0.5 ** (t / _t12), 0, 180), color="plot-1")], xunit=" d", xdec=0, xname="Time", label="Activity of an I-125 source against time")
_n_f = len(DECAY_LAW)
DECAY_LAW += [
    FIGQ(STEM("An I-125 source decays as shown.", ["T<sub>1/2</sub> = 59.4 d"], "Tap the [[time]] at which its activity has fallen to 25% of the initial value."), _fig_decay, [(2 * _t12 - 8, 2 * _t12 + 8)],
         "25% is two half-lives, because ½ × ½ = ¼. That is 2 × 59.4 = 118.8 d. On the graph, follow the 25% line across to the curve and read the time below it.", lvl="Easy", note="about 119 d"),
    FIGQ(STEM("The same I-125 source.", ["T<sub>1/2</sub> = 59.4 d"], "Tap the [[mean life]] τ on the time axis."), _fig_decay, [(_t12 / math.log(2) - 8, _t12 / math.log(2) + 8)],
         "The mean life is τ = T<sub>1/2</sub> / 0.693 = 1.44 × T<sub>1/2</sub> = 85.7 d. It is the time at which the activity has fallen to 1/e = 36.8%, not to 50%. The half-life (59.4 d) and two half-lives (118.8 d) are both wrong places.", lvl="Moderate", note="about 86 d"),
]
PLACE["decay-law"].setdefault(1, []).extend([_n_f + 1, _n_f + 2])
_lp, _ld = math.log(2) / 65.94, math.log(2) / 6.0067
_adf = lambda t: 0.88 * _ld / (_ld - _lp) * (math.exp(-_lp * t) - math.exp(-_ld * t))
_fig_eq = FS(x=dict(min=0, max=120, ticks=[0, 24, 48, 72, 96, 120], label="Time after elution (h)"), y=dict(min=0, max=100, ticks=[0, 25, 50, 75, 100], label="Activity (% of initial Mo-99)", fmt="pct"),
             series=[dict(pts=PTS(lambda t: 100 * math.exp(-_lp * t), 0, 120), color="plot-1")],
             texts=[dict(x=70, y=52, t="Mo-99", color="plot-1", b=True)], xunit=" h", xdec=0, xname="Time", label="Mo-99 activity after elution")
_n_f = len(EQUILIBRIUM)
EQUILIBRIUM += [
    FIGQ(STEM("A Mo-99/Tc-99m generator is eluted at time zero. The graph shows the Mo-99 activity only.", [], "Tap the [[time]] at which the Tc-99m activity is greatest."), _fig_eq, [(_calc.t_max(65.94, 6.0067) - 3, _calc.t_max(65.94, 6.0067) + 3)],
         "The daughter activity peaks at t<sub>max</sub> = ln(λ<sub>d</sub>/λ<sub>p</sub>) / (λ<sub>d</sub> − λ<sub>p</sub>), which is about 23 h for Tc-99m (6.01 h) growing from Mo-99 (65.9 h). The Tc-99m curve is not plotted, so the time has to be calculated or recalled.", lvl="Moderate", note="about 23 h"),
]
PLACE["equilibrium"].setdefault(2, []).append(_n_f + 1)
