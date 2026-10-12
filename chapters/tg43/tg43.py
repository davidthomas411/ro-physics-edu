from blocks import *
import math, calc

SEEDS = [("Amersham 6711", "I-125", 0.965, 0.370, 0.814, 0.30), ("Amersham 6702", "I-125", 1.036, 0.420, 0.861, 0.30), ("Theragenics 200", "Pd-103", 0.686, 0.541, 0.555, 0.423)]   # name, isotope, Lambda, F(1 cm, 0), g(2 cm), L in cm
LAM, FAX, G2, L6711 = 0.965, 0.370, 0.814, 0.30
d_tr1 = calc.tg43_rate(1, LAM, 1, 90, L6711, 1, 1)                      # 6711, transverse axis, 1 cm
d_ax1 = calc.tg43_rate(1, LAM, 1, 0, L6711, 1, FAX)                     # 6711, long axis, 1 cm
d_tr2 = calc.tg43_rate(1, LAM, 2, 90, L6711, G2, 1)                     # 6711, transverse axis, 2 cm
lam_pd, g_pd, l_pd = 0.686, 0.555, 0.423
d_pd2 = calc.tg43_rate(1, lam_pd, 2, 90, l_pd, g_pd, 1)                 # Pd-103 Model 200, transverse axis, 2 cm
gr_ax, gr_tr = calc.tg43_gl(1, 0, L6711), calc.tg43_gl(1, 90, L6711)    # line-source G at 1 cm
g_ratio = gr_ax / gr_tr
tot5 = calc.implant_total_dose(5.0, 60 * 24) / 100                      # Gy: 5 cGy/h, T1/2 = 60 d = 1440 h
d7 = calc.implant_dose_to(5.0, 60 * 24, 7 * 24) / 100                   # Gy after 7 d
rate145 = 14500 / calc.implant_total_dose(1.0, 59.4 * 24)               # cGy/h giving 145 Gy over the life of an I-125 implant
rate145_wrong = 14500 / (59.4 * 24)
r_1pct = next(i / 1000 for i in range(300, 5000) if calc.tg43_gl(i / 1000, 0, 0.3) * (i / 1000) ** 2 < 1.01)   # distance where G_L on the axis is within 1% of 1/r^2
d_ax_ratio = calc.tg43_gl(1, 0, 0.3)

TOPIC = dict(
    id="tg43", domain=5, sub="V", title="TG-43 dose calculation",
    ref=dict(aapm="", khan="15", ford="4"),
    guide=[
        H("Dose-rate equation"),
        P("The AAPM Task Group 43 formalism calculates the dose rate in water around a sealed source from five factors. For a line source it is written as follows."),
        EQ("[[1|Ḋ(r, θ) = S<sub>K</sub> · Λ · [G(r, θ) / G(r₀, θ₀)] · g(r) · F(r, θ)]]", "[[1|r₀ = 1 cm,   θ₀ = 90° (the transverse axis)]]"),
        UL("<b>S<sub>K</sub></b>, air kerma strength (U). It is the factor that depends on the particular source and it decays with time.",
           "<b>Λ</b>, dose rate constant (cGy h<sup>−1</sup> U<sup>−1</sup>): the dose rate to water at the reference point (1 cm, transverse axis) per unit S<sub>K</sub>. It is fixed by the seed model.",
           "<b>G</b>, geometry function: the inverse-square fall-off for the shape of the source, divided by its value at the reference point.",
           "<b>g(r)</b>, radial dose function: scatter and attenuation in water along the transverse axis, with g(1 cm) = 1.",
           "<b>F(r, θ)</b>, anisotropy function: the angular variation of the dose caused by absorption in the capsule and marker, with F(r, 90°) = 1."),
        P("The product S<sub>K</sub> Λ has units of cGy/h. [[1|At the reference point every other factor equals 1, so the dose rate there is S<sub>K</sub> Λ.]]"),

        H("Geometry function"),
        P("[[1|For a point source G = 1/r².]] A real seed is a short line of radioactive material of active length L, and the dose at a point is the inverse-square law averaged over the length of the line."),
        EQ("G<sub>L</sub>(r, θ) = β / (L r sin θ)   (θ ≠ 0)", "[[1|G<sub>L</sub>(r, 0) = 1 / (r² − L²/4)]]", "β = angle subtended by the source at the point"),
        P(f"Close to a seed the line source differs from the point approximation. For L = 3 mm at r = 1 cm, G<sub>L</sub> is {100 * (d_ax_ratio - 1):.1f}% above 1/r² on the long axis ({d_ax_ratio:.3f}) and {100 * (1 - gr_tr):.1f}% below it on the transverse axis ({gr_tr:.3f}). [[1|Beyond about five source lengths, {r_1pct:.1f} cm for a 3 mm seed, the two agree to within 1%.]]"),

        H("Radial dose function and anisotropy"),
        P("g(r) is normalized to 1 at 1 cm. It accounts for scatter and attenuation in water beyond the geometry. For a high-energy source such as Ir-192 it stays close to 1 over several centimetres. [[1|For a low-energy source it falls more steeply, because the photons are strongly attenuated]]: at 2 cm, g is 0.81 for an I-125 seed and 0.56 for a Pd-103 seed."),
        P("F(r, θ) is the dose at angle θ divided by the dose at the same distance on the transverse axis, after the geometry is removed. [[1|It equals 1 at 90° and is lower along the seed axis, where the marker, welds, and capsule absorb photons.]] Averaging F over angle gives the anisotropy factor φ<sub>an</sub>(r), the single number used when the orientations of the seeds are unknown, as in a prostate implant. [[1|Setting φ<sub>an</sub> = 1 neglects this self-absorption and overestimates the delivered dose.]]"),

        H("Seed data and worked doses"),
        TABLE(["Seed", "Isotope", "Λ (cGy h<sup>−1</sup> U<sup>−1</sup>)", "F(1 cm, 0°)", "g(2 cm)", "L (mm)"], [[n, i, f"{lm:.3f}", f"{f:.3f}", f"{g:.3f}", f"{L * 10:.2f}".rstrip("0").rstrip(".")] for n, i, lm, f, g, L in SEEDS]),
        P(f"Rounded consensus values from the AAPM TG-43 update (Rivard, 2004). The examples below use S<sub>K</sub> = 1 U and the line-source geometry function. [[1|At 2 cm on the transverse axis the dose rate is {100 * d_tr2 / d_tr1:.0f}% of its value at 1 cm for the Model 6711 seed and {100 * d_pd2 / lam_pd:.0f}% for the Model 200 seed, where inverse square alone would give 25%.]]"),
        EX("Transverse axis at the reference point", STEM("An I-125 Model 6711 seed.", ["S<sub>K</sub> = 1 U", "Λ = 0.965 cGy h<sup>−1</sup> U<sup>−1</sup>", "point: r = 1 cm on the transverse axis"], "Find the [[dose rate]]."),
           ["At the reference point G(r, θ) / G(r₀, θ₀) = 1, g = 1, and F = 1", "Ḋ = S<sub>K</sub> Λ = 1 × 0.965"], f"{d_tr1:.3f} cGy/h."),
        EX("On the long axis", STEM("An I-125 Model 6711 seed.", ["S<sub>K</sub> = 1 U", "Λ = 0.965 cGy h<sup>−1</sup> U<sup>−1</sup>", "L = 3 mm,   F(1 cm, 0°) = 0.370", "point: r = 1 cm on the seed axis"], "Find the [[dose rate]]."),
           [f"G<sub>L</sub>(1, 0) = 1 / (1 − 0.15²) = {gr_ax:.3f} cm<sup>−2</sup>", f"G<sub>L</sub>(1, 90°) = β / (L r) = {gr_tr:.3f} cm<sup>−2</sup>, so G / G₀ = {g_ratio:.3f}", f"Ḋ = 1 × 0.965 × {g_ratio:.3f} × 1 × 0.370"], f"{d_ax1:.3f} cGy/h, well below the transverse value because of F."),
        EX("A low-energy seed at 2 cm", STEM("A Pd-103 Model 200 seed.", ["S<sub>K</sub> = 1 U", "Λ = 0.686 cGy h<sup>−1</sup> U<sup>−1</sup>", "L = 4.23 mm,   g(2 cm) = 0.555", "point: r = 2 cm on the transverse axis"], "Find the [[dose rate]]."),
           [f"G<sub>L</sub>(2, 90°) = {calc.tg43_gl(2, 90, l_pd):.4f} cm<sup>−2</sup>, G<sub>L</sub>(1, 90°) = {calc.tg43_gl(1, 90, l_pd):.4f} cm<sup>−2</sup>, ratio = {calc.tg43_gl(2, 90, l_pd) / calc.tg43_gl(1, 90, l_pd):.4f}", f"Ḋ = 1 × 0.686 × {calc.tg43_gl(2, 90, l_pd) / calc.tg43_gl(1, 90, l_pd):.4f} × 0.555 × 1"], f"{d_pd2:.4f} cGy/h, about {100 * d_pd2 / lam_pd:.0f}% of the dose rate at the reference point."),

        H("Permanent implants"),
        P("A permanent implant delivers its dose as the sources decay. [[1|The dose rate falls as e<sup>−λt</sup>, so the total dose is the integral from zero to infinity, Ḋ₀/λ.]] The mean life is 1/λ = T<sub>1/2</sub> / ln 2 = 1.44 T<sub>1/2</sub>."),
        EQ("[[1|D<sub>total</sub> = Ḋ₀ / λ = 1.44 T<sub>1/2</sub> Ḋ₀]]", "D(t) = D<sub>total</sub> (1 − e<sup>−λt</sup>)"),
        P("[[1|Half of the total dose is delivered in one half-life]] and 90% in 3.3 half-lives. For I-125 (59.4 d) those times are 59 d and 197 d. A short half-life delivers the dose sooner, which is why Pd-103 needs a higher starting dose rate than I-125 for the same total."),
        EX("Total dose of an implant", STEM("A permanent implant.", ["initial dose rate = 5 cGy/h", "T<sub>1/2</sub> = 60 d = 1440 h"], "Find the [[total dose]] delivered."),
           ["D<sub>total</sub> = 1.44 × T<sub>1/2</sub> × Ḋ₀", f"= 1.44 × 1440 h × 5 cGy/h = {calc.implant_total_dose(5.0, 1440):,.0f} cGy"], f"{tot5:.0f} Gy."),
        EX("Dose after one week", STEM("A permanent implant.", ["initial dose rate = 5 cGy/h", "T<sub>1/2</sub> = 60 d", "time = 7 d"], "Find the [[dose delivered in the first 7 d]]."),
           [f"D(7 d) = D<sub>total</sub> (1 − ½<sup>7/60</sup>) = {tot5:.1f} Gy × {1 - 0.5 ** (7 / 60):.4f}"], f"{d7:.1f} Gy, only 8% of the total."),
        EX("Initial dose rate for a prescription", STEM("An I-125 prostate implant.", ["prescription = 145 Gy", "T<sub>1/2</sub> = 59.4 d"], "Find the [[initial dose rate]] that delivers 145 Gy over the life of the implant."),
           [f"Mean life = 1.44 × 59.4 d × 24 h/d = {calc.implant_total_dose(1.0, 59.4 * 24):,.0f} h", f"Ḋ₀ = 14,500 cGy / {calc.implant_total_dose(1.0, 59.4 * 24):,.0f} h"], f"{rate145:.2f} cGy/h."),
    ],
    cards=[
        C("Write the TG-43 dose rate equation for a line source.", "Ḋ(r, θ) = S<sub>K</sub> Λ [G(r, θ) / G(r₀, θ₀)] g(r) F(r, θ), with r₀ = 1 cm and θ₀ = 90°."),
        C("What is the TG-43 reference point?", "1 cm from the source on the transverse axis (perpendicular bisector), at θ₀ = 90°."),
        C("What is the dose rate at the reference point?", "S<sub>K</sub> Λ, because G/G₀, g, and F are all 1 there."),
        C("Define the dose rate constant Λ and give its units.", "The dose rate to water at the reference point per unit air kerma strength, in cGy h<sup>−1</sup> U<sup>−1</sup>. It is fixed by the seed model."),
        C("What does the geometry function G account for?", "The inverse-square fall-off for the shape of the source. For a point source G = 1/r²."),
        C("Write the line-source geometry function.", "G<sub>L</sub>(r, θ) = β / (L r sin θ) off the axis, and 1 / (r² − L²/4) on the axis. L is the active length and β the angle the source subtends."),
        C("What does the radial dose function g(r) account for, and what is g(1 cm)?", "Scatter and attenuation in water along the transverse axis. g(1 cm) = 1 by definition."),
        C("How does g(r) depend on photon energy?", "It falls faster for low-energy sources (Pd-103, I-125) than for high-energy ones (Ir-192), because low-energy photons are attenuated more."),
        C("What does the anisotropy function F(r, θ) account for?", "The angular dependence of the dose from absorption in the capsule, welds, and marker. F = 1 at 90°, and it is lower along the seed axis."),
        C("What happens if φ<sub>an</sub> = 1 is used for a prostate implant?", "The self-absorption is ignored, so the calculated dose is higher than the delivered dose."),
        C("Write the total dose from a permanent implant.", "D<sub>total</sub> = Ḋ₀ / λ = 1.44 T<sub>1/2</sub> Ḋ₀, where Ḋ₀ is the initial dose rate."),
        C("What fraction of the total dose of a permanent implant is delivered after n half-lives?", "1 − 2<sup>−n</sup>: half after one half-life and 90% after 3.3 half-lives."),
        C("Why does Pd-103 need a higher initial dose rate than I-125 for the same total dose?", "Its half-life is shorter (17.0 d against 59.4 d), so its mean life is shorter and the dose is delivered sooner."),
    ],
)

PROBLEMS = [
    PR("Which TG-43 quantity is specified when seeds are ordered from a manufacturer?", "Air kerma strength", ["Dose rate constant", "Radial dose function", "Anisotropy function"],
       "The user orders a source strength, S<sub>K</sub>, which depends on how long the seeds have decayed. Λ, g, G, and F are properties of the seed model and cannot be ordered.", lvl="Easy"),
    PR("The dose rate constant Λ is:", "a property of the seed model that the user cannot adjust", ["chosen by the user when ordering seeds", "proportional to the activity ordered", "the same for every seed model"],
       "Λ is measured and calculated for each seed model and published by the AAPM. Different models of the same isotope have different values.", lvl="Easy"),
    PR("In the TG-43 formalism the reference point is at:", "1 cm from the seed on the transverse axis", ["1 cm from the seed on the long axis", "1 m from the seed on the transverse axis", "the surface of the capsule"],
       "r₀ = 1 cm and θ₀ = 90°. Λ is defined there, and g and F are normalized to 1 at that point.", lvl="Easy"),
    PR("With all other parameters unchanged, which dose-calculation factor changes if the active length of a seed changes?", "The line-source geometry function G<sub>L</sub>", ["The W/e factor", "The half-life", "The radial dose function, through the half-life"],
       "G<sub>L</sub> depends on L through β and the factor 1/L. W/e is a property of air and the half-life is a property of the nuclide.", lvl="Moderate"),
    PR("The radial dose function g(r) depends mainly on:", "the photon energy", ["the activity of the source", "the length of the source", "the half-life"],
       "g(r) describes scatter and attenuation in water, which depend on the photon energy.", lvl="Moderate"),
    PRN(STEM("An I-125 Model 6711 seed.", ["S<sub>K</sub> = 1 U", "Λ = 0.965 cGy h<sup>−1</sup> U<sup>−1</sup>", "point: r = 1 cm on the transverse axis"], "What is the [[dose rate]]?"), d_tr1, [d_ax1, 1.0, 1.32], "{:.3f} cGy/h",
        f"That is the reference point, where G/G₀, g, and F are all 1, so Ḋ = S<sub>K</sub> Λ = {d_tr1:.3f} cGy/h. The value on the long axis ({d_ax1:.3f}) would apply at the same distance along the seed axis.", lvl="Moderate"),
    PRN(STEM("An I-125 Model 6711 seed.", ["S<sub>K</sub> = 1 U", "Λ = 0.965 cGy h<sup>−1</sup> U<sup>−1</sup>", "L = 3 mm,   F(1 cm, 0°) = 0.370", "point: r = 1 cm on the seed axis"], "What is the [[dose rate]]?"), d_ax1, [LAM * FAX, LAM * g_ratio, FAX * g_ratio], "{:.3f} cGy/h",
        f"Ḋ = Λ × [G<sub>L</sub>(1, 0) / G<sub>L</sub>(1, 90°)] × g × F = 0.965 × {g_ratio:.3f} × 1 × 0.370 = {d_ax1:.3f} cGy/h. Leaving out the geometry ratio gives {LAM * FAX:.3f}; leaving out F gives {LAM * g_ratio:.3f}; leaving out Λ gives {FAX * g_ratio:.3f}.", lvl="Moderate"),
    PRN(STEM("A permanent implant.", ["initial dose rate = 5 cGy/h", "T<sub>1/2</sub> = 60 d"], "What is the [[total dose]] delivered over the life of the implant?"), tot5, [5 * 1440 / 100, tot5 * 1.4427, 15.0], "{:.0f} Gy",
        f"D<sub>total</sub> = 1.4427 × T<sub>1/2</sub> × Ḋ₀ = 1.4427 × 1440 h × 5 cGy/h = {tot5 * 100:,.0f} cGy = {tot5:.0f} Gy. Using the half-life in place of the mean life gives 72 Gy.", lvl="Moderate"),
    PRN(STEM("A permanent implant.", ["initial dose rate = 5 cGy/h", "T<sub>1/2</sub> = 60 d", "time = 7 d"], "What [[dose]] is delivered in the first 7 d?"), d7, [5 * 7 * 24 / 100, tot5, d7 / 10], "{:.1f} Gy",
        f"D(7 d) = D<sub>total</sub> (1 − ½<sup>7/60</sup>) = {tot5:.1f} × {1 - 0.5 ** (7 / 60):.4f} = {d7:.1f} Gy. Ignoring the decay gives 8.4 Gy, which is too high.", lvl="Moderate"),
    PR("What is the effect of using an anisotropy factor φ<sub>an</sub> = 1 in the calculation for a permanent prostate implant?", "The calculated dose is higher than the delivered dose", ["The calculated dose is lower than the delivered dose", "The dose distribution shifts laterally", "The calculated dose is unchanged"],
       "φ<sub>an</sub> is below 1 because the capsule and marker absorb photons. Setting it to 1 ignores that absorption, so the calculation overestimates the dose.", lvl="Moderate"),
    PRN(STEM("A Pd-103 Model 200 seed.", ["S<sub>K</sub> = 1 U", "Λ = 0.686 cGy h<sup>−1</sup> U<sup>−1</sup>", "L = 4.23 mm,   g(2 cm) = 0.555", "point: r = 2 cm on the transverse axis"], "What is the [[dose rate]]?"), d_pd2, [lam_pd * g_pd, lam_pd * calc.tg43_gl(2, 90, l_pd) / calc.tg43_gl(1, 90, l_pd), lam_pd], "{:.4f} cGy/h",
        f"The geometry ratio G<sub>L</sub>(2, 90°) / G<sub>L</sub>(1, 90°) is {calc.tg43_gl(2, 90, l_pd) / calc.tg43_gl(1, 90, l_pd):.4f}, close to 1/4. Ḋ = 0.686 × {calc.tg43_gl(2, 90, l_pd) / calc.tg43_gl(1, 90, l_pd):.4f} × 0.555 = {d_pd2:.4f} cGy/h. Leaving out g gives {lam_pd * calc.tg43_gl(2, 90, l_pd) / calc.tg43_gl(1, 90, l_pd):.4f}.", lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4], 2: [5, 10, 12], 3: [6, 7], 4: [8, 9, 13]}

TERMS = ['air kerma strength', 'dose rate constant', 'geometry function', 'radial dose function', 'anisotropy function']

TAKE = [
    [('Ḋ = S<sub>K</sub> Λ [G(r, θ) / G(r₀, θ₀)] g(r) F(r, θ), with r₀ = 1 cm and θ₀ = 90°. At the reference point it reduces to S<sub>K</sub> Λ.', 'tg43-factors')],
    [('G is 1/r² for a point and 1/(r² − L²/4) on the axis of a line source. The two agree to within 1% beyond about five source lengths.', 'geometry-function')],
    [('g(r) falls faster for low-energy sources, and F(r, θ) is below 1 near the seed axis. Using φ<sub>an</sub> = 1 overestimates the dose.', 'radial-dose')],
    [('At 2 cm on the transverse axis the dose rate is 20% of its value at 1 cm for an I-125 Model 6711 seed and 14% for a Pd-103 Model 200 seed. Inverse square alone would give 25%.', 'dose-at-2cm')],
    [('A permanent implant delivers D = 1.44 T<sub>1/2</sub> Ḋ₀ in total, and half of it within one half-life.', 'cumulative-dose')],
]


# ---------------------------------------------------------------- matching, typed, and tap-the-figure questions
_t12 = 59.4
_t131 = 9.7
_fig_rate = FS(x=dict(min=0, max=300, ticks=[0, 50, 100, 150, 200, 250, 300], label="Time after implant (days)"), y=dict(min=0, max=100, ticks=[0, 20, 40, 60, 80, 100], label="Dose rate (% of the initial dose rate)", fmt="pct"),
               series=[dict(pts=PTS(lambda t: 100 * 0.5 ** (t / _t12), 0, 300), color="plot-1")], xunit=" d", xdec=0, xname="Time", label="Dose rate of a permanent I-125 implant against time")
PROBLEMS += [
    SORT("Match each TG-43 factor to what it accounts for.", ["G, geometry function", "g, radial dose function", "F, anisotropy function", "Λ, dose rate constant", "S<sub>K</sub>, air kerma strength"],
         [("Inverse-square fall-off for the shape of the source", 0), ("Scatter and attenuation in water", 1), ("Absorption in the capsule and marker along the seed axis", 2),
          ("Dose rate at 1 cm per unit source strength, for the seed model", 3), ("The strength of the source, which decays with time", 4)],
         "G removes the geometry, g describes how water attenuates and scatters the photons along the transverse axis, and F describes the angular dependence caused by the source construction. Λ links source strength to dose rate for a given seed model, and S<sub>K</sub> is the strength itself.", lvl="Moderate", mode="match", cap=1),
    FIGQ(STEM("The graph shows the dose rate of a permanent I-125 implant (T<sub>1/2</sub> = 59.4 d) as a percentage of its initial value.", [], "Tap the [[time by which 75% of the total dose]] has been delivered."), _fig_rate, [(2 * _t12 - 12, 2 * _t12 + 12)],
         "The fraction of the total dose delivered by time t is 1 − R(t)/R(0), where R is the dose rate. So 75% delivered means the rate has fallen to 25%, which takes two half-lives: 2 × 59.4 = 118.8 d. The graph shows the rate, not the cumulative dose.", lvl="Moderate", note="about 119 d"),
]
