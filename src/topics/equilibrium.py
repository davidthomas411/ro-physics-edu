from blocks import *
import calc, math

TP, TD = 65.94, 6.0067        # Mo-99, Tc-99m half-lives (h)
BR = 0.88                      # fraction of Mo-99 decays feeding Tc-99m (about 87-89%)
lp, ld = calc.lam(TP), calc.lam(TD)
ratio = calc.transient_ratio(TP, TD); tmax = calc.t_max(TP, TD)
A0 = 18.5; t = 4.0
x1, x2 = math.exp(-lp * t), math.exp(-ld * t)
ad = A0 * calc.daughter_over_parent0(t, TP, TD)

TOPIC = dict(
    id="equilibrium", domain=1, sub="I.B", title="Parent–daughter decay and equilibrium",
    ref=dict(aapm="2.2", khan="2", ford="3"),
    guide=[
        H("Ingrowth of the daughter"),
        P("When a daughter nuclide is itself radioactive, its number rises by production from the parent and falls by its own decay. For a pure parent at t = 0 and a daughter fed by every parent decay:"),
        EQ(f"A<sub>d</sub>(t) = A<sub>p</sub>(0) · {fr('λ<sub>d</sub>', 'λ<sub>d</sub> − λ<sub>p</sub>')} · (e<sup>−λ<sub>p</sub>t</sup> − e<sup>−λ<sub>d</sub>t</sup>)"),
        P("If only a fraction f of parent decays feed the daughter, multiply by f."),

        H("Types of equilibrium"),
        FIG("equilibrium", "Left: the daughter activity peaks where it meets the parent curve, then both fall with the parent's half-life. Right: the daughter climbs to the parent's activity. Branching fraction ignored."),
        TABLE(["Case", "Condition", "Long-time behavior", "Example"], [
            ["Transient equilibrium", "Parent T<sub>1/2</sub> longer than daughter's, but not by a large factor", "A<sub>d</sub>/A<sub>p</sub> is constant and above 1. Both fall with the parent's half-life.", "Mo-99 → Tc-99m"],
            ["Secular equilibrium", "Parent T<sub>1/2</sub> much longer than daughter's", "A<sub>d</sub> ≈ A<sub>p</sub>. The parent activity is nearly constant.", "Ra-226 → Rn-222; Sr-90 → Y-90; Cs-137 → Ba-137m"],
            ["No equilibrium", "Parent T<sub>1/2</sub> shorter than daughter's", "The daughter outlives the parent and decays with its own half-life.", "Rare in practice"]]),
        EQ(f"transient: A<sub>d</sub>/A<sub>p</sub> = {fr('λ<sub>d</sub>', 'λ<sub>d</sub> − λ<sub>p</sub>')} = {fr('T<sub>1/2,p</sub>', 'T<sub>1/2,p</sub> − T<sub>1/2,d</sub>')}",
           f"peak of daughter: t<sub>max</sub> = {fr('ln(λ<sub>d</sub>/λ<sub>p</sub>)', 'λ<sub>d</sub> − λ<sub>p</sub>')}, where A<sub>d</sub> = A<sub>p</sub>"),
        P("At the peak the daughter's number is not changing, so its production rate equals its decay rate: λ<sub>d</sub>N<sub>d</sub> = λ<sub>p</sub>N<sub>p</sub>, that is A<sub>d</sub> = A<sub>p</sub>. Secular equilibrium is reached after about seven daughter half-lives, when the daughter has 99% of its final activity."),

        H("Mo-99 and Tc-99m"),
        P(f"Mo-99 has T<sub>1/2</sub> = 65.9 h and Tc-99m has T<sub>1/2</sub> = 6.01 h, so λ<sub>p</sub> = {lp:.4f} h<sup>−1</sup> and λ<sub>d</sub> = {ld:.4f} h<sup>−1</sup>. In transient equilibrium A<sub>d</sub>/A<sub>p</sub> = 65.9/(65.9 − 6.01) = {ratio:.2f}."),
        P(f"About {BR*100:.0f}% of Mo-99 decays feed Tc-99m (reported values are 87–89%); the rest go to Tc-99 directly. The Tc-99m activity therefore approaches {BR:.2f} × {ratio:.2f} = {BR*ratio:.2f} of the Mo-99 activity. Tc-99m regrows to its peak about {tmax:.0f} h after elution."),
        EX("Tc-99m 4 hours after elution",
           STEM("A Mo-99/Tc-99m generator is fully eluted at t = 0.", ["Mo-99 activity = 18.5 GBq", "time since elution = 4 h"], "Find the [[Tc-99m activity]] grown in."),
           [f"λ<sub>d</sub>/(λ<sub>d</sub> − λ<sub>p</sub>) = {ld:.4f} / {ld-lp:.4f} = {ratio:.3f}.",
            f"e<sup>−λ<sub>p</sub>t</sup> = e<sup>−{lp*t:.4f}</sup> = {x1:.4f}; e<sup>−λ<sub>d</sub>t</sup> = e<sup>−{ld*t:.4f}</sup> = {x2:.4f}.",
            f"A<sub>d</sub> = 18.5 × {ratio:.3f} × ({x1:.4f} − {x2:.4f}) = {ad:.2f} GBq.",
            f"Counting the branching fraction (0.88): {ad*BR:.1f} GBq."],
           f"About {ad:.1f} GBq if every Mo-99 decay feeds Tc-99m, or {ad*BR:.1f} GBq with the branching fraction."),

    ],
    cards=[
        C("State the condition and the result of transient equilibrium.", "Parent T<sub>1/2</sub> is longer than the daughter's but not by a large factor. After several daughter half-lives A<sub>d</sub>/A<sub>p</sub> = λ<sub>d</sub>/(λ<sub>d</sub> − λ<sub>p</sub>) = T<sub>1/2,p</sub>/(T<sub>1/2,p</sub> − T<sub>1/2,d</sub>) > 1, and both fall with the parent's half-life.", fig="equilibrium"),
        C("State the condition and the result of secular equilibrium.", "Parent T<sub>1/2</sub> is much longer than the daughter's. A<sub>d</sub> ≈ A<sub>p</sub>, and the parent activity is nearly constant over many daughter half-lives."),
        C("Name one example of transient and one of secular equilibrium.", "Transient: Mo-99 (66 h) → Tc-99m (6 h). Secular: Ra-226 (1600 y) → Rn-222 (3.8 d); also Sr-90 → Y-90 and Cs-137 → Ba-137m."),
        C("When does the daughter's activity peak, and how does it compare with the parent's then?", "At t<sub>max</sub> = ln(λ<sub>d</sub>/λ<sub>p</sub>) / (λ<sub>d</sub> − λ<sub>p</sub>). The daughter's number is not changing at the peak, so A<sub>d</sub> = A<sub>p</sub> (when every parent decay feeds the daughter)."),
        C("Mo-99 has T<sub>1/2</sub> = 65.9 h and Tc-99m has T<sub>1/2</sub> = 6.01 h. What is A<sub>d</sub>/A<sub>p</sub> in transient equilibrium, ignoring branching?", f"{ratio:.2f}.", w=["T<sub>1/2,p</sub>/(T<sub>1/2,p</sub> − T<sub>1/2,d</sub>) = 65.9 / (65.9 − 6.01)."]),
        C("About when does the Tc-99m activity of a freshly eluted generator peak?", f"About {tmax:.0f} h after elution."),
        C("A generator holds 18.5 GBq of Mo-99 when fully eluted. Estimate the Tc-99m activity 4 h later, ignoring branching.", f"About {ad:.1f} GBq.",
          w=[f"A<sub>d</sub> = A<sub>p</sub>(0) × {ratio:.3f} × (e<sup>−λ<sub>p</sub>t</sup> − e<sup>−λ<sub>d</sub>t</sup>).", f"= 18.5 × {ratio:.3f} × ({x1:.4f} − {x2:.4f}) = {ad:.2f} GBq."]),
        C("Why is the Tc-99m activity below the Mo-99 activity at equilibrium, even though the ratio is 1.10?", f"Only about 88% of Mo-99 decays feed Tc-99m; the rest decay straight to Tc-99. The activity ratio is 0.88 × 1.10 ≈ {BR*ratio:.2f}."),
        C("How many daughter half-lives until the daughter reaches 99% of its secular-equilibrium activity?", "About 7: 1 − (½)<sup>7</sup> = 99.2%."),
        C("A Cs-137 source emits 662 keV photons from Ba-137m (T<sub>1/2</sub> 2.55 min). Why does that output fall with Cs-137's 30-year half-life?", "Secular equilibrium: Ba-137m is continually regenerated, and its activity tracks Cs-137's (about 94% of it, from the branching). The output therefore decays with the parent's half-life."),
    ],
)

TERMS = ['secular equilibrium', 'transient equilibrium']

TAKE = [
    [("The daughter's activity starts at zero, rises to a peak, then decays with the parent. If only a fraction f of parent decays feed the daughter, multiply by f.", 'ingrowth')],
    [("The daughter's activity peaks where it equals the parent's.", 'peak-crossing'), ("Transient: the parent's half-life is longer than the daughter's, and A<sub>d</sub>/A<sub>p</sub> = T<sub>p</sub>/(T<sub>p</sub> − T<sub>d</sub>) > 1. Secular: the parent's half-life is much longer, and A<sub>d</sub> ≈ A<sub>p</sub> after about seven daughter half-lives.", 'equilibrium-types')],
    [('Mo-99/Tc-99m is transient: the ratio is 1.10 and Tc-99m peaks about 23 h after elution. The real ratio is lower because only about 88% of Mo-99 decays feed Tc-99m.', 'mo-tc-generator')],
]
