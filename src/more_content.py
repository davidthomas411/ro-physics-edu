"""Extra explanation for the complex parts of the course. Two kinds, both hidden until asked for:
  - 'Show more details': a block at the end of a chapter section (more_text below, registered with g()).
  - 'Explain further': a plainer restatement and the calculation step by step, after a question has been answered (registered with q()).
A question is found by the start of its plain-text stem. Numeric explanations record the value they arrive at, and tests/more.py checks it against the answer.
Style: no second person, and none of the words the style test bans."""
import math, re
from blocks import MORE, OL, UL, TABLE, EQ

plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
QM, GM, CHECKS = {}, {}, {}                      # topic id -> question entries, topic id -> chapter blocks, (topic id, stem start) -> the value the explanation reaches

def _q_html(simple=None, steps=None, tip=None, how="How the calculation is done"):
    out = []
    if simple: out.append(f"<p>{simple}</p>")
    if steps: out.append(f'<div class="mh">{how}</div><ol>' + "".join(f"<li>{s}</li>" for s in steps) + "</ol>")
    if tip: out.append(f'<p class="tip"><b>Watch for.</b> {tip}</p>')
    return "".join(out)

def q(topic, start, simple=None, steps=None, tip=None, check=None, how="How the calculation is done"):
    QM.setdefault(topic, []).append(dict(start=start, html=_q_html(simple, steps, tip, how)))
    if check is not None: CHECKS[(topic, start)] = check

def g(topic, section, block): GM.setdefault(topic, []).append((section, block))

def apply(topics):
    """Attach the explanations to the questions and insert the chapter blocks at the end of their sections."""
    for t in topics:
        for e in QM.get(t["id"], []):
            hits = [p for p in t["problems"] if plain(p.get("stem0", p["q"])).startswith(e["start"])]      # select-several questions are found by their original stem
            assert len(hits) == 1, (t["id"], e["start"], len(hits)); hits[0]["more"] = e["html"]
        for section, block in GM.get(t["id"], []):
            guide = t["guide"]; i = next(k for k, b in enumerate(guide) if b[0] == "h2" and plain(b[1]) == section)
            j = next((k for k in range(i + 1, len(guide)) if guide[k][0] == "h2"), len(guide)); guide.insert(j, block)

# ================================================================ 1.2 Particles, mass, and energy
ME, MP = 0.511, 938.3
beta = lambda ke, m0: math.sqrt(1 - 1 / (1 + ke / m0) ** 2)
T = "particles-energy"
rows = []
for ke in (0.05, 0.1, 0.5, 1.0, 6.0, 20.0):
    cl = math.sqrt(2 * ke / ME); rows.append([f"{ke:g}", f"{1 + ke / ME:.3f}", f"{beta(ke, ME):.4f}", f"{cl:.2f}" + (" (above c)" if cl > 1 else "")])
g(T, "Kinetic energy and speed", MORE("Using the relativistic formulas step by step",
    OL("Write the kinetic energy and the rest energy in the same unit, usually MeV.",
       f"Divide the kinetic energy by the rest energy, KE / m₀c². For a 2.0 MeV electron this is 2.0 / {ME} = {2.0 / ME:.2f}.",
       f"Add 1 to get γ. Here γ = {1 + 2.0 / ME:.2f}. The 1 stands for the rest energy and the {2.0 / ME:.2f} for the kinetic energy, both in units of m₀c².",
       f"Calculate β = √(1 − 1/γ²). Here 1/γ² = {1 / (1 + 2.0 / ME) ** 2:.4f}, so β = √{1 - 1 / (1 + 2.0 / ME) ** 2:.4f} = {beta(2.0, ME):.3f}.",
       f"Multiply by c: v = {beta(2.0, ME):.3f}c = {beta(2.0, ME) * 2.998:.2f} × 10⁸ m/s.",
       "Check that β is below 1. A value above 1 means the classical formula was used by mistake."),
    f"Setting KE = ½m₀v² gives β² = 2 KE / m₀c². For a 6 MeV electron β² = 2 × 6 / {ME} = {2 * 6 / ME:.1f}, so β = {math.sqrt(2 * 6 / ME):.2f}, which is impossible. The relativistic result is {beta(6, ME):.4f}.",
    TABLE(["Electron KE (MeV)", "γ", "v/c, relativistic", "v/c from ½mv²"], rows),
    f"The classical value is already 7% too high at 0.05 MeV and passes the speed of light at 0.5 MeV. Beyond a few MeV the relativistic speed barely changes: from 0.5 MeV to 20 MeV the speed rises only from {beta(0.5, ME):.2f}c to {beta(20, ME):.4f}c, although the energy is 40 times larger.",
    simple="Rest energy is the energy a particle has when it is not moving: 0.511 MeV for an electron. Kinetic energy is extra energy on top of that. When the extra energy is small compared with the rest energy, the old formula ½mv² works. When it is large, the extra energy mostly raises the momentum and the total energy, and the speed hardly changes, because nothing can go faster than light."))
g(T, "Annihilation and pair production", MORE("Energy and momentum in annihilation and pair production",
    UL("<b>Annihilation at rest.</b> The particles carry no momentum, so the photons must carry none in total. Two photons of 0.511 MeV leave in opposite directions.",
       "<b>Annihilation in flight.</b> Add the total energy of each particle, kinetic plus rest. The photons carry that sum, and they no longer leave in exactly opposite directions.",
       "<b>Pair production.</b> Photon energy = 1.022 MeV + the kinetic energy of the electron and the positron.",
       "<b>Why a nucleus is needed.</b> In empty space no electron–positron pair can have exactly the energy and the momentum of a single photon. A nearby nucleus takes up the missing momentum. It is heavy, so the energy it takes is negligible, and the threshold stays at 1.022 MeV."),
    simple="Both processes turn energy into mass or mass into energy. The total energy stays the same, and so does the total momentum. Momentum is the reason pair production needs a nucleus."))

q(T, "An electron and a positron, both at rest, annihilate.",
  simple="Before the annihilation nothing is moving, so the total momentum is zero. Momentum has a direction, so it must still add up to zero afterwards. One photon would carry momentum in one direction with nothing to balance it. Two photons of equal energy going in opposite directions balance exactly.",
  steps=[f"The particles at rest have a total rest energy of {ME} + {ME} = {2 * ME:.3f} MeV.", f"All of it becomes photon energy. The two photons are equal, so each carries {ME} MeV, which is 511 keV.", "The photons leave 180° apart so that their momenta cancel."],
  tip="One photon, or two photons going the same way, would leave a net momentum that did not exist before.")
q(T, "How much energy is equivalent to a mass of 0.0020 u?",
  simple="Mass and energy are two forms of the same thing, linked by E = mc². For atomic masses the conversion has a ready-made factor: one atomic mass unit is equivalent to 931.5 MeV.",
  steps=["Write the mass in u: 0.0020 u.", f"Multiply by 931.5 MeV per u: 0.0020 × 931.5 = {0.0020 * 931.5:.3f} MeV.", "Round to the precision of the data: 1.86 MeV."],
  tip="The factor is 931.5 MeV per u. The electron rest energy, 0.511 MeV, is a different quantity and is not used here.", check=1.86)
q(T, "What is the speed of an electron with 1.0 MeV of kinetic energy?",
  simple="The ratio of the total energy to the rest energy is γ, and γ shows how close the speed is to the speed of light. Rest energy is 0.511 MeV, so 1.0 MeV of kinetic energy is about twice the rest energy and the electron is strongly relativistic.",
  steps=[f"Divide the kinetic energy by the rest energy: 1.0 / {ME} = {1.0 / ME:.3f}.", f"Add 1 to get γ: 1 + {1.0 / ME:.3f} = {1 + 1.0 / ME:.3f}.", f"Square γ and invert: γ² = {(1 + 1.0 / ME) ** 2:.3f}, so 1/γ² = {1 / (1 + 1.0 / ME) ** 2:.4f}.", f"Subtract from 1: 1 − {1 / (1 + 1.0 / ME) ** 2:.4f} = {1 - 1 / (1 + 1.0 / ME) ** 2:.4f}.", f"Take the square root: β = {beta(1.0, ME):.4f}. The speed is {beta(1.0, ME):.3f}c."],
  tip=f"β must be below 1. The classical formula gives β = √(2 × 1.0 / {ME}) = {math.sqrt(2 / ME):.2f}, which is impossible.", check=beta(1.0, ME))
q(T, "Using ½mv² for a 6 MeV electron gives a speed greater than c.",
  simple="The formula ½mv² is a good approximation only when the kinetic energy is a small fraction of the rest energy. The speed can never exceed c, but the formula has no such limit, so its error grows as the speed approaches c.",
  steps=[f"Compare the kinetic energy with the rest energy: 6 / {ME} = {6 / ME:.1f} times larger.", f"The classical formula is used when the kinetic energy is below about 10% of the rest energy, which is {0.1 * ME * 1000:.0f} keV for an electron.", f"Setting ½m₀v² = KE gives β² = 2 KE / m₀c² = 2 × 6 / {ME} = {2 * 6 / ME:.1f}, so β = {math.sqrt(2 * 6 / ME):.2f}, which is impossible."])
q(T, "What is the threshold photon energy for pair production in the field of a nucleus?",
  simple="Pair production turns the energy of a photon into the mass of two particles, an electron and a positron. Each has a rest energy of 0.511 MeV, so the photon needs at least that much for both.",
  steps=[f"The electron has a rest energy of {ME} MeV, and the positron has the same.", f"Threshold = 2 × {ME} = {2 * ME:.3f} MeV.", "At exactly the threshold the pair is created with no kinetic energy. Any photon energy above 1.022 MeV becomes kinetic energy of the pair."],
  tip="The nucleus is needed to take up momentum. It is heavy, so it takes negligible energy and the threshold stays at 1.022 MeV.", check=2 * ME)
q(T, "A 3.0 MeV photon undergoes pair production",
  simple="The photon's energy works like a budget. The first 1.022 MeV pays for the mass of the pair. What is left becomes motion of the two particles.",
  steps=["Photon energy: 3.000 MeV.", f"Subtract the rest energy of the pair: 3.000 − {2 * ME:.3f} = {3.0 - 2 * ME:.3f} MeV.", "This is the combined kinetic energy of the electron and the positron. It is shared between them, not always equally. The nucleus takes a negligible amount."], check=3.0 - 2 * ME)
q(T, "What is the total energy, including rest energy, of an electron with 2.0 MeV of kinetic energy?",
  simple="Total energy is the energy of the particle as a whole: its motion plus the energy it has at rest. Kinetic energy is the motion part alone.",
  steps=["Kinetic energy: 2.000 MeV.", f"Rest energy of an electron: {ME} MeV.", f"Total = 2.000 + {ME} = {2.0 + ME:.3f} MeV."],
  tip=f"The total energy is the same as γm₀c². Here γ = {(2.0 + ME) / ME:.3f}.", check=2.0 + ME)
q(T, "A therapy proton has 100 MeV of kinetic energy.",
  simple=f"The proton rest energy is {MP} MeV, so 100 MeV is about {100 / MP * 100:.0f}% of it. The proton is only moderately relativistic, and the classical formula is a poor estimate but not an absurd one.",
  steps=[f"Divide the kinetic energy by the rest energy: 100 / {MP} = {100 / MP:.4f}.", f"γ = 1 + {100 / MP:.4f} = {1 + 100 / MP:.4f}.", f"γ² = {(1 + 100 / MP) ** 2:.4f}, so 1/γ² = {1 / (1 + 100 / MP) ** 2:.4f}.", f"1 − {1 / (1 + 100 / MP) ** 2:.4f} = {1 - 1 / (1 + 100 / MP) ** 2:.4f}.", f"β = √{1 - 1 / (1 + 100 / MP) ** 2:.4f} = {beta(100, MP):.4f}. The speed is {beta(100, MP):.2f}c."],
  tip=f"The classical formula gives β = √(2 × 100 / {MP}) = {math.sqrt(200 / MP):.3f}, about {100 * (math.sqrt(200 / MP) / beta(100, MP) - 1):.0f}% too high.", check=beta(100, MP))
q(T, "An electron and a positron, each with 1.00 MeV of kinetic energy, annihilate in flight",
  simple="Energy is conserved. The energy of the photons afterwards is the total energy of both particles before the annihilation, and the total energy includes the rest energy.",
  steps=[f"Each particle has a kinetic energy of 1.00 MeV and a rest energy of {ME} MeV, so each has {1.0 + ME:.3f} MeV.", f"Together: 2 × {1.0 + ME:.3f} = {2 * (1.0 + ME):.3f} MeV.", "All of it becomes photon energy. The photons are not 511 keV each, because the particles were moving. The total momentum is not zero, so the photons need not be equal or back to back."],
  tip="Using the kinetic energies alone gives 2.00 MeV, which leaves out the rest energy that is converted.", check=2 * (1.0 + ME))
q(T, "What photon energy creates a pair in which the electron and the positron each receive 0.50 MeV",
  simple="The photon's energy pays for two things: the mass of the pair, and the motion of the particles.",
  steps=["Photon energy = rest energy of the pair + kinetic energy of the electron + kinetic energy of the positron.", f"Rest energy of the pair: {2 * ME:.3f} MeV.", "Kinetic energies: 0.50 + 0.50 = 1.00 MeV.", f"Photon energy: {2 * ME:.3f} + 1.00 = {2 * ME + 1.0:.3f} MeV."], check=2 * ME + 1.0)

# ================================================================ 1.7 Decay law and activity
from blocks import sci
LN2 = math.log(2)
T = "decay-law"
pct_rows = [[f"{100 * p:g}%", f"{-math.log(1 - p):.4f}", f"{p:g}", f"{100 * (p / -math.log(1 - p) - 1):+.1f}%".replace("-", "−")] for p in (0.01, 0.02, 0.06, 0.10, 0.20)]
g(T, "Half-life and mean life", MORE("Working with half-lives, logarithms, and percentages",
    OL(f"<b>Activity after a time t.</b> Put t in the same unit as the half-life and form n = t / T½. The fraction left is 2<sup>−n</sup> = e<sup>−0.693 n</sup>. Multiply by the starting activity. For 6.5 h of Tc-99m (T½ = 6.0 h), n = {6.5 / 6.0:.3f} and the fraction left is {2 ** (-6.5 / 6.0):.3f}.",
       f"<b>Time to reach a given fraction.</b> t = T½ × log₂(A₀/A) = T½ × ln(A₀/A) / 0.693. For Lu-177 (T½ = 6.65 d) falling from 150 MBq to 25 MBq, the ratio is 6, log₂ 6 = {math.log2(6):.3f}, and t = {6.65 * math.log2(6):.1f} d.",
       "<b>Half-life from two measurements.</b> Find n = log₂(A₀/A), then T½ = t / n. A fall from 120 MBq to 15 MBq in 9.0 h is a ratio of 8 = 2³, so n = 3 and T½ = 3.0 h.",
       f"<b>Half-life from a percentage lost per interval.</b> If p is lost per interval, the fraction remaining is 1 − p. Then λ = −ln(1 − p) and T½ = 0.693 / λ. For 6% per day, λ = −ln 0.94 = {-math.log(0.94):.4f} per day and T½ = {LN2 / -math.log(0.94):.1f} d."),
    "The percentage lost compounds from interval to interval, so λ is not equal to the percentage. The approximation λ ≈ p is acceptable for small p and gets worse as p grows:",
    TABLE(["Lost per day", "Exact λ = −ln(1 − p), per day", "Approximation λ ≈ p", "Error of the approximation"], pct_rows),
    "Keep the units the same. If the half-life is in days and the time in hours, convert one of them first: 6.5 h is 0.271 d. A quick check: one half-life leaves 50% and two leave 25%, so an answer outside the range set by these is wrong.",
    simple="A half-life is a repeating halving. In every interval of one half-life the activity is cut to half of what it was at the start of that interval. Parts of a half-life work the same way, so after 1.5 half-lives the activity is one half and then a further factor of 0.707. A calculator, or a table of powers of two, does the arithmetic."))
fr_rows = [[f"{n:g}", f"{100 * (1 - 2 ** (-n)):.1f}%"] for n in (0.5, 1, 2, 3, 4, 7)]
g(T, "Permanent implants", MORE("Where D∞ = Ḋ₀τ comes from",
    OL("The dose rate is proportional to the activity, so it falls exponentially: Ḋ(t) = Ḋ₀ e<sup>−t/τ</sup>.",
       "The total dose is the area under the dose-rate curve: D∞ = ∫ Ḋ₀ e<sup>−t/τ</sup> dt from 0 to infinity = Ḋ₀ τ.",
       "The dose delivered up to time t is D(t) = Ḋ₀ τ (1 − e<sup>−t/τ</sup>), so the fraction delivered is 1 − e<sup>−t/τ</sup> = 1 − 2<sup>−t/T½</sup>.",
       "After one half-life half of the total dose has been delivered. After two half-lives it is 75%. After one mean life it is 63.2%."),
    TABLE(["Time (half-lives)", "Fraction of the total dose delivered"], fr_rows),
    f"Units must agree. If the dose rate is in cGy per hour, τ must be in hours: for I-125, τ = 59.4 d / 0.693 = 85.7 d = {59.4 / LN2 * 24:.0f} h.",
    f"A common error is to use T½ in place of τ. Because τ is {1 / LN2:.3f} times T½, the total dose then comes out {100 * (1 - LN2):.0f}% too low.",
    simple="A seed's dose rate falls as its activity falls. The total dose is the area under that falling dose-rate curve, from the start to infinite time. For an exponential curve, that area equals the starting dose rate times the mean life τ."))

q(T, "An activity of 1.48 GBq is how many millicuries?",
  simple="A curie is a much larger unit than a becquerel, so the number of curies is smaller than the number of becquerels. The conversion is 1 mCi = 37 MBq.",
  steps=["Write 1.48 GBq in MBq: 1.48 × 1000 = 1480 MBq.", f"Divide by 37 MBq per mCi: 1480 / 37 = {1480 / 37:.1f} mCi."],
  tip="1 Ci = 3.7 × 10<sup>10</sup> Bq. A slip of a power of ten gives 4 or 400, so check that the answer is smaller than the number of MBq.", check=40.0)
q(T, "A Tc-99m syringe is calibrated at 08:00.",
  simple="Every 6.0 h the activity halves. At 6.5 h, a little more than one half-life has passed, so the activity should be a little less than half of 925 MBq.",
  steps=["Find the elapsed time: 08:00 to 14:30 is 6.5 h.", f"Divide by the half-life, in the same unit: n = 6.5 / 6.0 = {6.5 / 6.0:.3f} half-lives.", f"The fraction left is 2<sup>−n</sup> = 2<sup>−{6.5 / 6.0:.3f}</sup> = {2 ** (-6.5 / 6.0):.4f}.", f"Multiply the starting activity by the fraction: 925 × {2 ** (-6.5 / 6.0):.4f} = {925 * 2 ** (-6.5 / 6.0):.1f} MBq."], check=925 * 2 ** (-6.5 / 6.0))
q(T, "An Ir-192 HDR source.",
  simple="The source is 120 days old, which is between one and two half-lives of 73.8 d. The activity must therefore be between 50% and 25% of the starting value.",
  steps=[f"n = 120 / 73.8 = {120 / 73.8:.3f} half-lives.", f"Fraction left = 2<sup>−{120 / 73.8:.3f}</sup> = {2 ** (-120 / 73.8):.4f}.", f"Activity = 370 × {2 ** (-120 / 73.8):.4f} = {370 * 2 ** (-120 / 73.8):.1f} GBq."], check=370 * 2 ** (-120 / 73.8))
q(T, "A prostate implant uses I-125 seeds.",
  simple="The activity of every seed falls in the same way, so the total falls in the same way. Add the seeds first, or decay each one, and the result is the same.",
  steps=[f"Total starting activity: 72 × 0.32 = {72 * 0.32:.2f} mCi.", f"n = 45 / 59.4 = {45 / 59.4:.4f} half-lives.", f"Fraction left = 2<sup>−{45 / 59.4:.4f}</sup> = {2 ** (-45 / 59.4):.4f}.", f"Total activity = {72 * 0.32:.2f} × {2 ** (-45 / 59.4):.4f} = {72 * 0.32 * 2 ** (-45 / 59.4):.2f} mCi."], check=72 * 0.32 * 2 ** (-45 / 59.4))
q(T, "A sample's activity falls from 120 MBq to 15 MBq in 9.0 hours.",
  simple="Count the halvings. 120 becomes 60, then 30, then 15. That is three halvings in 9.0 h, so each half-life is 3.0 h.",
  steps=["Find the ratio of the activities: 120 / 15 = 8.", f"Write the ratio as a power of two: 8 = 2<sup>3</sup>, so n = log₂ 8 = {math.log2(8):.0f} half-lives.", f"Divide the time by the number of half-lives: T½ = 9.0 / {math.log2(8):.0f} = {9.0 / 3:.1f} h."], check=3.0)
q(T, "A Lu-177 dose.",
  simple="The activity must fall to one sixth. One sixth lies between one quarter (two half-lives) and one eighth (three half-lives), so the time lies between 13.3 d and 20 d.",
  steps=["Find the ratio of the activities: 150 / 25 = 6.", f"The number of half-lives is n = log₂ 6 = ln 6 / ln 2 = {math.log(6):.3f} / {LN2:.3f} = {math.log2(6):.3f}.", f"Multiply by the half-life: t = 6.65 × {math.log2(6):.3f} = {6.65 * math.log2(6):.1f} d."], check=6.65 * math.log2(6))
q(T, "Which of these has the largest decay constant",
  simple="A short half-life means fast decay, and fast decay means a large decay constant. The two are inversely related, λ = 0.693 / T½, so the shortest half-life has the largest λ.",
  steps=["Put the half-lives in the same unit, days: Cs-137 30.1 y = 10,994 d; Co-60 5.27 y = 1925 d; Ir-192 73.8 d; I-125 59.4 d.", f"Divide 0.693 by each: Cs-137 {sci(LN2 / (30.1 * 365.25), 2)} per day; Co-60 {sci(LN2 / (5.27 * 365.25), 2)}; Ir-192 {sci(LN2 / 73.8, 2)}; I-125 {sci(LN2 / 59.4, 2)}.", "The largest is I-125, which has the shortest half-life."])
q(T, "A source loses 6.0% of its activity each day.",
  simple="A loss of 6% per day does not mean that the decay constant is 0.06 per day. The loss is applied to what is left each day, so it compounds. The fraction that remains after one day is 0.94, and λ comes from the logarithm of that.",
  steps=["The fraction remaining after one day is 1 − 0.060 = 0.940.", f"λ = −ln 0.940 = {-math.log(0.94):.5f} per day.", f"T½ = 0.693 / λ = {LN2:.4f} / {-math.log(0.94):.5f} = {LN2 / -math.log(0.94):.1f} d."],
  tip=f"Taking λ = 0.06 per day gives {LN2 / 0.06:.1f} d, which is too long.", check=LN2 / -math.log(0.94))
q(T, "A permanent I-125 implant.T1/2 = 59.4 dinitial dose rate = 7.5",
  simple="The total dose is the area under the falling dose-rate curve. For an exponential fall, the area equals the starting dose rate times the mean life, which is longer than the half-life.",
  steps=[f"Mean life: τ = 59.4 / 0.693 = {59.4 / LN2:.1f} d.", f"Put τ in hours to match the dose rate in cGy/h: {59.4 / LN2:.1f} × 24 = {59.4 / LN2 * 24:.0f} h.", f"D∞ = 7.5 cGy/h × {59.4 / LN2 * 24:.0f} h = {7.5 * 59.4 / LN2 * 24:,.0f} cGy.", f"Convert to gray: {7.5 * 59.4 / LN2 * 24:,.0f} cGy = {7.5 * 59.4 / LN2 * 24 / 100:.0f} Gy."],
  tip=f"Using T½ in place of τ gives {7.5 * 59.4 * 24 / 100:.0f} Gy, which is {100 * (1 - LN2):.0f}% too low.", check=7.5 * 59.4 / LN2 * 24 / 100)
q(T, "What percentage of the total dose from a permanent I-125 implant has been delivered after 119 days",
  simple="Each half-life delivers half of the dose that is still to come. After one half-life, 50% has been delivered. After two, half of the remaining 50% has been delivered too, which makes 75%.",
  steps=["119 d is two half-lives, because 2 × 59.4 = 118.8 d.", "The fraction not yet delivered is 2<sup>−2</sup> = 1/4 = 25%.", "The fraction delivered is 1 − 1/4 = 75%."], check=75.0)
q(T, "What is the mean life of Tc-99m",
  simple="The mean life is the average lifetime of a nucleus. It is longer than the half-life because a few nuclei survive much longer than most.",
  steps=[f"τ = T½ / 0.693 = 6.0 / {LN2:.4f} = {6.0 / LN2:.2f} h."], tip="τ = 1.443 × T½. Multiplying by 0.693 instead gives the wrong direction (4.16 h).", check=6.0 / LN2)
q(T, "A Co-60 source with T1/2 = 5.27 y.",
  simple="Ten years is nearly two half-lives, so the activity should be a little more than a quarter of the starting value.",
  steps=[f"n = 10 / 5.27 = {10 / 5.27:.4f} half-lives.", f"Fraction left = 2<sup>−{10 / 5.27:.4f}</sup> = {2 ** (-10 / 5.27):.4f}.", f"As a percentage: {100 * 2 ** (-10 / 5.27):.2f}%."], check=100 * 2 ** (-10 / 5.27))
q(T, "A source loses 2.0% of its activity each day.",
  simple="The loss compounds from day to day, so λ is not exactly 0.02 per day. The fraction left after a day is 0.98, and λ comes from its logarithm.",
  steps=["The fraction remaining after one day is 1 − 0.020 = 0.980.", f"λ = −ln 0.980 = {-math.log(0.98):.5f} per day.", f"T½ = 0.693 / {-math.log(0.98):.5f} = {LN2 / -math.log(0.98):.2f} d."],
  tip=f"Taking λ = 0.02 gives {LN2 / 0.02:.1f} d. The error is small for 2% and grows for larger percentages.", check=LN2 / -math.log(0.98))
q(T, "An I-125 source decays as shown",
  simple="Each half-life takes the activity to half of what it was. Two half-lives take it to half of a half, which is a quarter.",
  steps=["25% is ½ × ½, so it is two half-lives.", f"t = 2 × 59.4 = {2 * 59.4:.1f} d.", "On the graph, find 25% on the vertical axis, move across to the curve, and read straight down to the time axis."])
q(T, "The same I-125 source.",
  simple="The mean life is the average lifetime of a nucleus. It is longer than the half-life, because a few nuclei last much longer than most.",
  steps=[f"τ = 1.443 × T½ = 1.443 × 59.4 = {59.4 / LN2:.1f} d.", "At t = τ the activity has fallen to 1/e, which is 36.8% of the starting value. Tap where the curve is at 36.8%, which is between the 50% and 25% levels, closer to 25%."],
  tip="The half-life (59.4 d) is where the curve reaches 50%. Two half-lives (118.8 d) is where it reaches 25%.")

# ================================================================ 1.9 Parent-daughter equilibrium
T = "equilibrium"
lp, ld = LN2 / 65.94, LN2 / 6.007
g(T, "Ingrowth of the daughter", MORE("Where the ingrowth equation comes from",
    OL("The number of daughter nuclei changes by two processes: it gains nuclei when the parent decays and loses nuclei when the daughter decays. dN<sub>d</sub>/dt = λ<sub>p</sub>N<sub>p</sub> − λ<sub>d</sub>N<sub>d</sub>.",
       "The parent follows the decay law, N<sub>p</sub> = N<sub>p</sub>(0) e<sup>−λ<sub>p</sub>t</sub>. Putting that in and solving gives N<sub>d</sub> = N<sub>p</sub>(0) λ<sub>p</sub>/(λ<sub>d</sub> − λ<sub>p</sub>) × (e<sup>−λ<sub>p</sub>t</sub> − e<sup>−λ<sub>d</sub>t</sup>).",
       "Multiply by λ<sub>d</sub> to turn the number into an activity: A<sub>d</sub> = A<sub>p</sub>(0) λ<sub>d</sub>/(λ<sub>d</sub> − λ<sub>p</sub>) × (e<sup>−λ<sub>p</sub>t</sup> − e<sup>−λ<sub>d</sub>t</sup>).",
       "The two exponentials are the two decays. The first is the slow fall of the parent. The second is the daughter's own decay, which is fast and dies away first. At t = 0 they cancel, so the daughter activity starts at zero.",
       "At late times e<sup>−λ<sub>d</sub>t</sup> is negligible, and A<sub>d</sub> = A<sub>p</sub>(t) × λ<sub>d</sub>/(λ<sub>d</sub> − λ<sub>p</sub>). That constant factor is the transient equilibrium ratio."),
    f"For the Mo-99 example, λ<sub>p</sub> = {lp:.4f} per hour and λ<sub>d</sub> = {ld:.4f} per hour. After 4 h, e<sup>−λ<sub>p</sub>t</sup> = {math.exp(-4 * lp):.4f} and e<sup>−λ<sub>d</sub>t</sup> = {math.exp(-4 * ld):.4f}. The difference is {math.exp(-4 * lp) - math.exp(-4 * ld):.4f}. Multiplied by the factor {ld / (ld - lp):.3f} and by 18.5 GBq it gives {18.5 * ld / (ld - lp) * (math.exp(-4 * lp) - math.exp(-4 * ld)):.2f} GBq.",
    simple="The daughter gains atoms when the parent decays and loses atoms when it decays itself. At first the gain wins and the daughter grows. As the daughter builds up, its own loss grows too, until the two balance. The equation is the solution of that balance."))
g(T, "Types of equilibrium", MORE("Telling the cases apart, and where the ratios come from",
    UL("<b>Compare the half-lives first.</b> The parent much longer than the daughter: secular. The parent longer, but by a modest factor: transient. The parent shorter: no equilibrium.",
       f"<b>The transient ratio.</b> At late times A<sub>d</sub>/A<sub>p</sub> = λ<sub>d</sub>/(λ<sub>d</sub> − λ<sub>p</sub>). With λ = 0.693/T½ the 0.693 cancels, leaving T<sub>p</sub>/(T<sub>p</sub> − T<sub>d</sub>). For T<sub>p</sub> = 12 h and T<sub>d</sub> = 2 h that is 12/10 = 1.20. For Mo-99 and Tc-99m it is 65.94/(65.94 − 6.01) = {65.94 / (65.94 - 6.01):.2f}.",
       "<b>The secular limit.</b> When T<sub>p</sub> is much larger than T<sub>d</sub>, the ratio T<sub>p</sub>/(T<sub>p</sub> − T<sub>d</sub>) approaches 1, so the activities become equal.",
       f"<b>The peak.</b> The daughter activity stops rising when production equals decay, λ<sub>p</sub>N<sub>p</sub> = λ<sub>d</sub>N<sub>d</sub>. That is the moment when A<sub>d</sub> = A<sub>p</sub>. Setting the slope to zero gives t<sub>max</sub> = ln(λ<sub>d</sub>/λ<sub>p</sub>) / (λ<sub>d</sub> − λ<sub>p</sub>). For Mo-99 and Tc-99m, ln({ld / lp:.2f}) / {ld - lp:.4f} = {math.log(ld / lp) / (ld - lp):.1f} h.",
       "<b>Growth in secular equilibrium.</b> The daughter closes half of the remaining gap to the equilibrium activity in every daughter half-life: 50% after one, 75% after two, 87.5% after three, and 99% after 6.6.",
       "<b>Branching.</b> If only a fraction f of the parent decays feed the daughter, multiply the daughter activity by f. For Mo-99 this is about 0.88, which turns the ratio of 1.10 into about 0.97."),
    simple="Compare the half-lives. If the parent lives far longer than the daughter, the parent hardly changes while the daughter builds up, and the daughter ends up decaying as fast as it is fed, so the activities are equal. If the parent lives longer by a modest factor, the parent keeps falling during the build-up, and the daughter's activity settles above the parent's by a constant factor."))

q(T, "Which parent–daughter pair shows transient equilibrium?",
  simple="Transient equilibrium needs a parent that outlives its daughter by a modest factor. Mo-99 has a half-life of 65.9 h and Tc-99m has 6.0 h, a factor of about 11. The other three parents live thousands of times longer than their daughters, which gives secular equilibrium.")
q(T, "A parent decays to a daughter.parent T1/2 = 12.0 hdaughter T1/2 = 2.0 h",
  simple="Each daughter nucleus decays faster than a parent nucleus, so a given number of daughter nuclei gives more decays per second. In transient equilibrium the daughter activity is therefore larger than the parent activity, by a fixed factor.",
  steps=["Check that the parent half-life (12.0 h) is longer than the daughter's (2.0 h), but not by a very large factor. It is 6 times longer, so the equilibrium is transient.", "Use A<sub>d</sub>/A<sub>p</sub> = T<sub>p</sub> / (T<sub>p</sub> − T<sub>d</sub>).", f"Substitute: 12.0 / (12.0 − 2.0) = 12.0 / 10.0 = {12.0 / 10.0:.2f}."],
  tip="Reversing the half-lives gives 0.83, which would mean the daughter has the lower activity.", check=1.2)
q(T, "parent T1/2 = 36 hdaughter T1/2 = 4 hno daughter present at t = 0",
  simple="The daughter activity grows while production from the parent exceeds its own decay, and falls once its decay exceeds production. The peak is the moment when the two are equal, which is when the daughter activity equals the parent activity.",
  steps=[f"λ<sub>p</sub> = 0.693 / 36 = {LN2 / 36:.4f} per hour, and λ<sub>d</sub> = 0.693 / 4 = {LN2 / 4:.4f} per hour.", f"The ratio λ<sub>d</sub>/λ<sub>p</sub> = {(LN2 / 4) / (LN2 / 36):.0f}, and ln 9 = {math.log(9):.4f}.", f"The difference λ<sub>d</sub> − λ<sub>p</sub> = {LN2 / 4 - LN2 / 36:.4f} per hour.", f"t<sub>max</sub> = ln(λ<sub>d</sub>/λ<sub>p</sub>) / (λ<sub>d</sub> − λ<sub>p</sub>) = {math.log(9):.4f} / {LN2 / 4 - LN2 / 36:.4f} = {math.log(9) / (LN2 / 4 - LN2 / 36):.1f} h."],
  tip="The peak is earlier than one parent half-life (36 h) and later than one daughter half-life (4 h).", check=math.log(9) / (LN2 / 4 - LN2 / 36))
q(T, "A sealed Sr-90 source has stood for weeks.",
  simple="The parent lives for 28.8 years and the daughter for 64 hours, so the parent hardly decays while the daughter builds up. The daughter ends up decaying as fast as it is fed.",
  steps=["Compare the half-lives: 28.8 y is about 252,000 h, which is about 3900 times the daughter's 64 h. The parent is much longer-lived, so this is secular equilibrium.", f"Equilibrium needs about seven daughter half-lives, 7 × 64 h = {7 * 64} h = {7 * 64 / 24:.1f} d. Weeks are longer than that.", "In secular equilibrium A<sub>d</sub> = A<sub>p</sub>, so the Y-90 activity is 40 MBq."], check=40.0)
q(T, "In transient equilibrium the daughter activity is:",
  simple="Activity is the number of nuclei times the decay constant. The daughter has a larger decay constant than the parent, so even though there are fewer daughter nuclei the activity ratio comes out above 1: T<sub>p</sub>/(T<sub>p</sub> − T<sub>d</sub>).")
q(T, "Ignoring branching, what is the ratio of Tc-99m to Mo-99 activity at transient equilibrium",
  simple="The Tc-99m decays faster than the Mo-99, so each Tc-99m nucleus counts for more activity. The ratio is the longer half-life divided by the difference between the half-lives.",
  steps=["Use A<sub>d</sub>/A<sub>p</sub> = T<sub>p</sub> / (T<sub>p</sub> − T<sub>d</sub>).", f"Substitute T<sub>p</sub> = 65.94 h and T<sub>d</sub> = 6.01 h: 65.94 / (65.94 − 6.01) = 65.94 / {65.94 - 6.01:.2f} = {65.94 / (65.94 - 6.01):.3f}."],
  tip="Only about 88% of Mo-99 decays feed Tc-99m. Including that fraction gives about 0.97.", check=65.94 / (65.94 - 6.01))
q(T, "In secular equilibrium starting with no daughter, what percentage of the final daughter activity has grown in after one daughter half-life?",
  simple="The daughter closes half of the remaining gap to its final activity in every half-life. After one half-life the gap has halved, so half of the final activity has grown in.",
  steps=["The fraction grown in is 1 − 2<sup>−t/T<sub>d</sub></sup>.", "At t = T<sub>d</sub>, 2<sup>−1</sup> = 0.5, so the fraction is 1 − 0.5 = 0.5.", "As a percentage: 50%."],
  tip="63.2% is the fraction reached after one mean life, not after one half-life.", check=50.0)
q(T, "In secular equilibrium, about how many daughter half-lives are needed to reach 99%",
  simple="After each half-life, half of the remaining gap is closed. The gap must shrink to 1%, which is 1/100, and the number of halvings needed is the base-2 logarithm of 100.",
  steps=["Reaching 99% means the gap is 1%, so 2<sup>−n</sup> = 0.01.", f"n = log₂ 100 = ln 100 / ln 2 = {math.log(100):.3f} / {LN2:.3f} = {math.log2(100):.2f}.", "About 6.6 half-lives. Seven is a convenient round figure."], check=math.log2(100))
q(T, "Which statement about transient equilibrium is correct?",
  simple="In transient equilibrium the daughter activity is above the parent's by a constant factor, and both fall with the parent's half-life. Equal activities are the secular case, and they also occur at the single instant of the daughter's peak.")
q(T, "Mo-99 (T1/2 = 65.94 h) decays to Tc-99m",
  simple="After elution the Tc-99m grows in while the Mo-99 slowly decays. The Tc-99m activity peaks when its production equals its decay, which is when its activity equals the Mo-99 activity.",
  steps=[f"λ<sub>p</sub> = 0.693 / 65.94 = {lp:.5f} per hour, and λ<sub>d</sub> = 0.693 / 6.007 = {ld:.4f} per hour.", f"The ratio λ<sub>d</sub>/λ<sub>p</sub> = {ld / lp:.2f}, and ln({ld / lp:.2f}) = {math.log(ld / lp):.3f}.", f"The difference λ<sub>d</sub> − λ<sub>p</sub> = {ld - lp:.4f} per hour.", f"t<sub>max</sub> = {math.log(ld / lp):.3f} / {ld - lp:.4f} = {math.log(ld / lp) / (ld - lp):.2f} h."],
  tip="A common slip is to use half-lives in place of decay constants in this formula. It needs λ.", check=math.log(ld / lp) / (ld - lp))
q(T, "A Mo-99/Tc-99m generator is eluted at time zero.",
  simple="The Tc-99m grows in until its activity equals the Mo-99 activity, and the Mo-99 curve alone does not show where that happens. The time comes from the formula.",
  steps=[f"t<sub>max</sub> = ln(λ<sub>d</sub>/λ<sub>p</sub>) / (λ<sub>d</sub> − λ<sub>p</sub>) = ln({ld / lp:.2f}) / {ld - lp:.4f} = {math.log(ld / lp) / (ld - lp):.1f} h.", "Tap the time axis at about 23 h."],
  tip="One Tc-99m half-life (6 h) is far too early, and one Mo-99 half-life (66 h) is far too late.")

# ================================================================ 1.10 Photon interactions with matter
T = "photon-interactions"
nh_rows = [[f"{n:g}", f"{100 * 0.5 ** n:.3g}%"] for n in (1, 2, 3, 4, 5, 6.64, 10)]
cs = lambda E, th: E / (1 + (E / ME) * (1 - math.cos(math.radians(th))))
ang_rows = [[f"{th}°", f"{1 - math.cos(math.radians(th)):.4f}", f"{cs(1.0, th):.3f}", f"{1.0 - cs(1.0, th):.3f}"] for th in (0, 45, 90, 180)]
g(T, "Attenuation", MORE("Attenuation calculations step by step",
    OL(f"<b>Transmission from the number of half-value layers.</b> Each HVL halves the beam. After n HVLs the fraction left is (½)<sup>n</sup> = 2<sup>−n</sup>, where n = thickness / HVL.",
       f"<b>Thickness for a required transmission T.</b> Find the number of HVLs, n = log₂(1/T) = ln(1/T) / ln 2, then multiply by the HVL. For T = 5%, n = log₂ 20 = {math.log2(20):.2f}, and with an HVL of 0.80 cm the thickness is {math.log2(20) * 0.8:.2f} cm.",
       f"<b>From a table of coefficients.</b> Multiply the mass attenuation coefficient by the density to get the linear coefficient, μ = (μ/ρ) × ρ. Then I/I₀ = e<sup>−μx</sup>. For 1.25 MeV photons in lead, μ = 0.05876 × 11.35 = {0.05876 * 11.35:.3f} cm<sup>−1</sup>. A thickness of 3.0 cm gives μx = {0.05876 * 11.35 * 3:.2f} and I/I₀ = {100 * math.exp(-0.05876 * 11.35 * 3):.1f}%.",
       "<b>Converting between layers.</b> HVL = 0.693 / μ. TVL = 2.303 / μ = 3.32 × HVL. Mean free path = 1/μ = 1.44 × HVL."),
    TABLE(["Number of half-value layers", "Fraction transmitted"], nh_rows),
    "Use the column for attenuation, μ/ρ, when the question is about the transmission of a narrow beam. The energy-absorption column, μ<sub>en</sub>/ρ, describes the energy deposited in the material and gives a different number. In water at 1.25 MeV, using it would give an HVL of 23.4 cm in place of 11.0 cm.",
    "The natural logarithm ln(1/T) equals μx, the number of mean free paths. The number of half-value layers is log₂(1/T), which is 1.44 times larger.",
    simple="Each layer of material removes the same fraction of the photons that reach it. One half-value layer removes half, the next removes half of the rest, and so on. The transmitted fraction after n half-value layers is (½)<sup>n</sup>."))
g(T, "Compton scattering", MORE("Using the Compton equation",
    OL(f"Express the photon energy and the electron rest energy in the same unit and form E / 0.511 MeV. For a 1.0 MeV photon this is {1.0 / ME:.3f}.",
       "Calculate 1 − cos θ for the scattering angle. It is 0 at 0°, 0.293 at 45°, 0.5 at 60°, 1 at 90°, and 2 at 180°.",
       f"Put both into E′ = E / [ 1 + (E / 0.511 MeV)(1 − cos θ) ]. At 90° the bracket is 1 + {1.0 / ME:.3f} × 1 = {1 + 1.0 / ME:.3f}, so E′ = {cs(1.0, 90):.3f} MeV.",
       "The electron receives what the photon lost: E<sub>electron</sub> = E − E′."),
    TABLE(["Angle θ", "1 − cos θ", "Scattered photon (MeV)", "Electron (MeV)"], ang_rows),
    f"The photon always keeps some energy. As the incident energy becomes very large, the scattered photon at 90° approaches 0.511 MeV and at 180° it approaches {ME / 2:.3f} MeV.",
    "Common slips are using cos θ in place of 1 − cos θ, giving the electron's energy as the scattered photon's, and mixing keV with MeV.",
    simple="In Compton scattering the photon bounces off an electron that is nearly free, and it gives up part of its energy. The more the photon is deflected, the more energy the electron receives. The electron gets nothing for no deflection and the most for a photon that comes straight back."))
g(T, "Interaction processes", MORE("How the interactions depend on atomic number and energy",
    UL("<b>Photoelectric effect.</b> The photon is absorbed by a bound electron, so the effect is strong in high-Z materials and at low energy. The mass attenuation coefficient varies as Z<sup>3</sup>/E<sup>3</sup>, with sharp rises at absorption edges. Doubling the photon energy reduces it by a factor of 8.",
       "<b>Compton scattering.</b> The photon interacts with loosely bound electrons, so per electron it does not depend on Z. Per gram it depends on the number of electrons per gram, which is nearly the same for all materials except hydrogen. It falls slowly with energy.",
       "<b>Pair production.</b> It needs at least 1.022 MeV. Above the threshold it rises with energy and with Z, and in water it becomes the dominant process only above about 24 MeV."),
    "These dependencies explain clinical facts. Lead and tungsten shield well at low energy because of the photoelectric Z<sup>3</sup> dependence. Bone shows strongly on a kilovoltage radiograph for the same reason. Megavoltage beams sit in the Compton range, where the interaction depends on electrons per gram, so bone and soft tissue look alike per gram and contrast in a megavoltage portal image comes mainly from the difference in density.",
    simple="Which interaction occurs depends on the photon energy and on the atoms. The photoelectric effect needs a bound electron, so it favours high atomic number and low energy. Compton scattering depends on the electron density, which is nearly the same per gram for every material. Pair production needs high energy."))

q(T, "A lead shield (illustrative value).HVL = 0.80 cm",
  simple="Each half-value layer halves the beam: 100% becomes 50%, 25%, 12.5%, 6.25%, and 3.1%. A transmission of 5% lies between 4 HVLs (6.25%) and 5 HVLs (3.1%), so the thickness lies between 3.2 and 4.0 cm.",
  steps=["The transmission is 5% = 0.05, so 1/T = 20.", f"The number of HVLs is n = log₂ 20 = ln 20 / ln 2 = {math.log(20):.3f} / {LN2:.3f} = {math.log2(20):.2f}.", f"Thickness = n × HVL = {math.log2(20):.2f} × 0.80 = {math.log2(20) * 0.8:.2f} cm."],
  tip="The natural logarithm ln 20 = 3.00 counts mean free paths, not half-value layers. Using it as n gives 2.40 cm.", check=math.log2(20) * 0.8)
q(T, "A shielding material.HVL = 2.2 cm",
  simple="A half-value layer cuts the beam to a half, and a tenth-value layer cuts it to a tenth. Cutting to a tenth takes a little more than three halvings, because 2<sup>3</sup> = 8 and 2<sup>3.32</sup> = 10.",
  steps=["The number of HVLs in one TVL is log₂ 10 = ln 10 / ln 2 = 2.303 / 0.693 = 3.32.", f"TVL = 3.32 × 2.2 = {math.log2(10) * 2.2:.2f} cm."], check=math.log2(10) * 2.2)
q(T, "A narrow beam of Co-60 photons, taking 1.25 MeV, in water.",
  simple="The table gives the attenuation per gram per cm². Multiplying by the density turns it into the attenuation per centimetre, and the half-value layer follows from it.",
  steps=["Read the mass attenuation coefficient at 1.25 MeV from the μ/ρ column: 0.06323 cm²/g.", "Multiply by the density: μ = 0.06323 × 1.00 = 0.06323 cm<sup>−1</sup>.", f"HVL = 0.693 / μ = 0.693 / 0.06323 = {LN2 / 0.06323:.2f} cm."],
  tip="The μ<sub>en</sub>/ρ column answers a different question, the energy deposited, and gives 23.4 cm.", check=LN2 / 0.06323)
q(T, "A narrow beam of 1.25 MeV photons passes through lead.",
  simple="The coefficient from the table is per gram. Lead is dense, so the attenuation per centimetre is much larger. Multiply by the density first, then by the thickness, then take the exponential.",
  steps=[f"Read the mass attenuation coefficient at 1.25 MeV: 0.05876 cm²/g. Multiply by the density: μ = 0.05876 × 11.35 = {0.05876 * 11.35:.3f} cm<sup>−1</sup>.", f"Multiply by the thickness: μx = {0.05876 * 11.35:.3f} × 3.0 = {0.05876 * 11.35 * 3:.3f}.", f"I/I₀ = e<sup>−{0.05876 * 11.35 * 3:.3f}</sup> = {math.exp(-0.05876 * 11.35 * 3):.4f}, which is {100 * math.exp(-0.05876 * 11.35 * 3):.1f}%."],
  tip="Leaving out the density gives 83.8%, because the coefficient would then be per gram and not per centimetre.", check=100 * math.exp(-0.05876 * 11.35 * 3))
q(T, "The photoelectric mass attenuation coefficient varies approximately as:",
  simple="The photoelectric effect needs a bound electron, so it is strong for heavy atoms and weak for light ones. It also falls quickly as the photon energy rises, because a high-energy photon is harder for the atom to absorb.",
  steps=["Atomic number: the coefficient rises as Z<sup>3</sup>.", "Energy: the coefficient falls as 1/E<sup>3</sup>.", "Together, Z<sup>3</sup>/E<sup>3</sup>. For example, doubling the photon energy divides the coefficient by 2<sup>3</sup> = 8."])
q(T, "A photon is Compton scattered.incident energy = 1.0 MeVscattering angle = 45°",
  simple="The photon gives part of its energy to the electron. The deflection angle sets how much. The scattered photon keeps E′ and the electron gets the rest.",
  steps=[f"E / 0.511 = 1.0 / 0.511 = {1.0 / ME:.3f}.", f"1 − cos 45° = 1 − 0.7071 = {1 - math.cos(math.radians(45)):.4f}.", f"E′ = 1.0 / [1 + {1.0 / ME:.3f} × {1 - math.cos(math.radians(45)):.4f}] = 1.0 / {1 + 1.0 / ME * (1 - math.cos(math.radians(45))):.4f} = {cs(1.0, 45):.3f} MeV.", f"Electron energy = 1.0 − {cs(1.0, 45):.3f} = {1.0 - cs(1.0, 45):.3f} MeV."],
  tip="Using cos θ in place of 1 − cos θ gives the wrong scattered energy. The scattered photon energy is 0.636 MeV, not the answer.", check=1.0 - cs(1.0, 45))
q(T, "Why do megavoltage portal images show little difference between bone and soft tissue per gram?",
  simple="At megavoltage energies Compton scattering dominates. It depends on the number of electrons per gram, which is nearly the same for bone and soft tissue. Contrast in the image comes from differences in density, not from differences in atomic number. At kilovoltage energies the photoelectric effect and its Z<sup>3</sup> dependence give strong bone contrast.")
q(T, "Cortical bone and water at a photon energy of 6 MeV.",
  simple="At 6 MeV the mass attenuation coefficients of bone and water are almost the same. The attenuation per centimetre then differs mainly because bone is denser.",
  steps=["Convert each mass coefficient to a linear coefficient: μ = (μ/ρ) × ρ.", f"Bone: 0.02734 × 1.92 = {0.02734 * 1.92:.4f} cm<sup>−1</sup>. Water: 0.0277 × 1.00 = {0.0277:.4f} cm<sup>−1</sup>.", f"Ratio = {0.02734 * 1.92:.4f} / {0.0277:.4f} = {0.02734 * 1.92 / 0.0277:.2f}."],
  tip="The ratio is close to the density ratio, 1.92, because the mass coefficients are nearly equal.", check=0.02734 * 1.92 / 0.0277)
q(T, "A narrow beam of 1.5 MeV photons strikes a lead shield.",
  simple="Lead attenuates strongly because it is dense. Convert the coefficient from per gram to per centimetre by multiplying by the density, then use the exponential.",
  steps=[f"μ = 0.0522 × 11.35 = {0.0522 * 11.35:.3f} cm<sup>−1</sup>.", f"μx = {0.0522 * 11.35:.3f} × 5.0 = {0.0522 * 11.35 * 5:.2f}.", f"I/I₀ = e<sup>−{0.0522 * 11.35 * 5:.2f}</sup> = {math.exp(-0.0522 * 11.35 * 5):.4f}, which is about {100 * math.exp(-0.0522 * 11.35 * 5):.1f}%."], check=100 * math.exp(-0.0522 * 11.35 * 5))
q(T, "A photon is Compton scattered.incident energy = 2.0 MeVscattering angle = 60°",
  simple="The electron gets the energy that the scattered photon does not keep.",
  steps=[f"E / 0.511 = 2.0 / 0.511 = {2.0 / ME:.3f}.", f"1 − cos 60° = 1 − 0.5 = 0.5.", f"E′ = 2.0 / [1 + {2.0 / ME:.3f} × 0.5] = 2.0 / {1 + 2.0 / ME * 0.5:.3f} = {cs(2.0, 60):.3f} MeV.", f"Electron energy = 2.0 − {cs(2.0, 60):.3f} = {2.0 - cs(2.0, 60):.3f} MeV."], check=2.0 - cs(2.0, 60))
q(T, "A narrow photon beam is attenuated by a uniform absorber, as shown.",
  simple="The half-value layer is the thickness that cuts the beam to half. On the graph it is where the curve crosses the 50% level.",
  steps=["Find 50% on the vertical axis.", "Move across to the curve.", "Read straight down to the thickness axis. This is the half-value layer, about 3.5 cm for this absorber."])
q(T, "The same absorber.Tap the thickness that leaves one eighth",
  simple="One eighth is half of a half of a half. The beam must pass through three half-value layers.",
  steps=["One eighth is (½)<sup>3</sup>, so n = 3 half-value layers.", f"Read one half-value layer at the 50% level of the graph: 3.47 cm.", f"Thickness = 3 × 3.47 = {3 * 3.47:.1f} cm."],
  tip="The 12.5% level is not marked on the axis, so the thickness is found from the half-value layer.")

# ================================================================ 1.8 Specific activity
T = "specific-activity"
NA, DAY, YR = 6.022e23, 86400.0, 3.156e7
spec = lambda t_s, M: LN2 / t_s * NA / M                     # Bq/g from the half-life in seconds and the molar mass in g/mol
S_I = spec(59.4 * DAY, 124.9); S_H = spec(100 * DAY, 100.0)
g(T, "Activity per gram", MORE("Calculating specific activity step by step",
    OL("<b>Half-life in seconds.</b> A becquerel is one decay per second, so convert: days × 86,400, or years × 3.156 × 10<sup>7</sup>.",
       "<b>Decay constant.</b> λ = 0.693 / T½, in s<sup>−1</sup>.",
       "<b>Atoms in one gram.</b> N<sub>A</sub> / M, with N<sub>A</sub> = 6.022 × 10<sup>23</sup> per mole and M the molar mass in g/mol.",
       "<b>Multiply.</b> S = λ × (atoms per gram), in Bq/g.",
       "<b>Convert to curies if needed.</b> Divide by 3.7 × 10<sup>10</sup> Bq per Ci."),
    f"For I-125 (T½ = 59.4 d, M = 124.9 g/mol): T½ = {59.4 * DAY:,.0f} s, λ = {sci(LN2 / (59.4 * DAY), 4)} s<sup>−1</sup>, atoms per gram = {sci(NA / 124.9, 4)}, and S = {sci(S_I, 3)} Bq/g, which is {S_I / 3.7e10:,.0f} Ci/g.".replace("e+14", " × 10<sup>14</sup>").replace("e+21", " × 10<sup>21</sup>").replace("e-07", " × 10<sup>−7</sup>"),
    f"A shortcut for comparing nuclides is S ∝ 1/(T½ × M). For Pd-103 against I-125, S<sub>Pd</sub>/S<sub>I</sub> = (59.4 / 17.0) × (124.9 / 102.9) = {59.4 / 17.0:.2f} × {124.9 / 102.9:.2f} = {(59.4 / 17.0) * (124.9 / 102.9):.1f}.",
    "Common slips: leaving out ln 2 (the result is 1.44 times too large) and leaving the half-life in days (the result in Bq/g is 86,400 times too small).",
    simple="Specific activity counts the decays per second that come from one gram. One gram contains a fixed number of atoms, N<sub>A</sub> / M. Each atom has a probability λ of decaying every second. The number of atoms times λ is the specific activity."))
g(T, "Source size and carrier", MORE("From activity to mass",
    OL("Put the activity in becquerels. For 0.50 mCi, 0.50 × 3.7 × 10<sup>7</sup> = 1.85 × 10<sup>7</sup> Bq.",
       "Divide by the specific activity: m = A / S. For I-125, 1.85 × 10<sup>7</sup> / 6.5 × 10<sup>14</sup> = 2.8 × 10<sup>−8</sup> g.",
       "Express the mass in a convenient unit: 2.8 × 10<sup>−8</sup> g = 28 ng."),
    f"The same method gives {370e9 / 3.4e14 * 1000:.2f} mg for 370 GBq of Ir-192 (S = 3.4 × 10<sup>14</sup> Bq/g) and {185e12 / 4.19e13:.2f} g for 185 TBq of Co-60 (S = 4.19 × 10<sup>13</sup> Bq/g). For the same activity the mass is proportional to 1/S, so Cs-137 (S = 3.2 × 10<sup>12</sup> Bq/g) needs about {3.41e14 / 3.21e12:.0f} times the mass of Ir-192.",
    simple="Mass is activity divided by specific activity. A nuclide with a very high specific activity needs only a tiny mass for a large activity, which is why short-lived sources can be made small."))

q(T, "A hypothetical nuclide.T1/2 = 100 dmolar mass = 100 g/molWhat is its specific activity?",
  simple="Specific activity is the number of atoms in a gram multiplied by the chance that each decays every second.",
  steps=[f"Half-life in seconds: 100 × 86,400 = {100 * DAY:,.0f} s.", f"λ = 0.693 / {100 * DAY:,.0f} = {sci(LN2 / (100 * DAY), 4)} s<sup>−1</sup>.", f"Atoms per gram = 6.022 × 10<sup>23</sup> / 100 = {sci(NA / 100, 4)}.", f"S = {sci(LN2 / (100 * DAY), 4)} × {sci(NA / 100, 4)} = {sci(S_H, 3)} Bq/g."],
  tip="Leaving out ln 2 gives 7.0 × 10<sup>14</sup>, and leaving the half-life in days gives a value 86,400 times too small.", check=S_H)
q(T, "A hypothetical nuclide.T1/2 = 100 dmolar mass = 100 g/molWhat is its specific activity in Ci/g?",
  simple="Work out the specific activity in Bq/g first, then change the unit. One curie is 3.7 × 10<sup>10</sup> Bq.",
  steps=[f"S = ln 2 × N<sub>A</sub> / (T½ × M) = {sci(S_H, 4)} Bq/g, with T½ in seconds.", f"Divide by 3.7 × 10<sup>10</sup> Bq/Ci: {sci(S_H, 4)} / 3.7 × 10<sup>10</sup> = {S_H / 3.7e10:,.0f} Ci/g."], check=S_H / 3.7e10)
q(T, "S (Ir-192) = 3.4 × 10",
  simple="Mass is activity divided by specific activity. The activity must be in becquerels to match Bq/g.",
  steps=["Convert the activity: 370 GBq = 3.7 × 10<sup>11</sup> Bq.", f"m = A / S = 3.7 × 10<sup>11</sup> / 3.4 × 10<sup>14</sup> = {sci(3.7e11 / 3.4e14, 3)} g.".replace("e-03", " × 10<sup>−3</sup>"), f"In milligrams: {3.7e11 / 3.4e14 * 1000:.2f} mg."], check=3.7e11 / 3.4e14 * 1000)
q(T, "Which has the higher specific activity: 1 g of Co-60 or 1 g of Cs-137?",
  simple="A shorter half-life means more decays per atom, and a lighter atom means more atoms per gram. Co-60 is better on both counts.",
  steps=[f"S ∝ 1/(T½ × M). Co-60: T½ = 5.27 y, M = 59.9 g/mol. Cs-137: T½ = 30.1 y, M = 136.9 g/mol.", f"Ratio S<sub>Co</sub>/S<sub>Cs</sub> = (30.1 / 5.27) × (136.9 / 59.9) = {30.1 / 5.27:.2f} × {136.9 / 59.9:.2f} = {(30.1 / 5.27) * (136.9 / 59.9):.0f}.", "Co-60 has about 13 times the specific activity of Cs-137."])
q(T, "The activity of 1 g of Ra-226 is closest to:",
  simple="The curie was first defined as the activity of one gram of radium-226, so the answer is close to 1 Ci by construction.",
  steps=[f"T½ = 1600 y = {sci(1600 * YR, 4)} s, so λ = {sci(LN2 / (1600 * YR), 4)} s<sup>−1</sup>.", f"Atoms per gram = 6.022 × 10<sup>23</sup> / 226 = {sci(NA / 226, 4)}.", f"S = {sci(LN2 / (1600 * YR) * NA / 226, 3)} Bq/g = {LN2 / (1600 * YR) * NA / 226 / 3.7e10:.2f} Ci/g."])
q(T, "seed activity = 0.50 mCiS (I-125) = 6.5",
  simple="Mass is activity divided by specific activity, and the activity must be in becquerels.",
  steps=["Convert the activity: 0.50 mCi × 3.7 × 10<sup>7</sup> Bq/mCi = 1.85 × 10<sup>7</sup> Bq.", f"m = A / S = 1.85 × 10<sup>7</sup> / 6.5 × 10<sup>14</sup> = {sci(1.85e7 / 6.5e14, 3)} g.".replace("e-08", " × 10<sup>−8</sup>"), f"A nanogram is 10<sup>−9</sup> g, so m = {1.85e7 / 6.5e14 * 1e9:.1f} ng."], check=1.85e7 / 6.5e14 * 1e9)
q(T, "Compare two seed isotopes.",
  simple="Specific activity is proportional to 1 / (half-life × molar mass). Compare the two products, with the shorter-lived and lighter nuclide ahead.",
  steps=["S ∝ 1/(T½ × M), so S<sub>Pd</sub>/S<sub>I</sub> = (T½,I × M<sub>I</sub>) / (T½,Pd × M<sub>Pd</sub>).", f"= (59.4 × 124.9) / (17.0 × 102.9) = {59.4 * 124.9:,.0f} / {17.0 * 102.9:,.0f} = {(59.4 * 124.9) / (17.0 * 102.9):.2f}."], check=(59.4 * 124.9) / (17.0 * 102.9))
q(T, "A Co-60 teletherapy source.",
  simple="Mass is activity divided by specific activity, with both in becquerels.",
  steps=["Convert the activity: 185 TBq = 1.85 × 10<sup>14</sup> Bq.", f"m = A / S = 1.85 × 10<sup>14</sup> / 4.19 × 10<sup>13</sup> = {185e12 / 4.19e13:.2f} g."], check=185e12 / 4.19e13)
q(T, "Compare the mass needed for the same activity.",
  simple="For the same activity, mass is inversely proportional to specific activity, so the nuclide with the lower specific activity needs more mass. The ratio of the masses is the inverse ratio of the specific activities.",
  steps=["m = A / S, so m<sub>Cs</sub> / m<sub>Ir</sub> = S<sub>Ir</sub> / S<sub>Cs</sub>.", f"= 3.41 × 10<sup>14</sup> / 3.21 × 10<sup>12</sup> = {3.41e14 / 3.21e12:.0f}."], check=3.41e14 / 3.21e12)
q(T, "If the half-life and the molar mass of a nuclide were both doubled",
  simple="Specific activity falls when the half-life is longer, because each atom is less likely to decay in any second, and when the atom is heavier, because a gram holds fewer atoms. Each doubling halves S.",
  steps=["S ∝ 1/(T½ × M).", "Doubling T½ multiplies S by ½, and doubling M multiplies it by ½ again.", "S becomes ½ × ½ = ¼ of its value."])

# ================================================================ 1.3 Charges, fields, and atomic structure
T = "charges-atom"
KC, QE = 8.99e9, 1.602e-19
coul = lambda r_fm: KC * QE ** 2 / (r_fm * 1e-15) ** 2
pc_of = lambda ke: math.sqrt(ke ** 2 + 2 * ke * ME)
rad_cm = lambda ke, B: 100 * pc_of(ke) / (299.8 * B)
En = lambda n: -13.6 / n ** 2
h_rows = [[f"{n}", f"{En(n):.2f}", f"{-En(n):.2f}"] for n in (1, 2, 3, 4, 5)]
g(T, "Charge and force", MORE("Using Coulomb's law",
    OL("Put every quantity in SI units: charges in coulombs (the proton charge is 1.602 × 10<sup>−19</sup> C) and the distance in metres (1 fm = 10<sup>−15</sup> m).",
       f"Multiply the constant by the charges: k q₁q₂ = 8.99 × 10<sup>9</sup> × (1.602 × 10<sup>−19</sup>)² = {sci(KC * QE ** 2, 3)} N·m².",
       f"Divide by the square of the distance. For r = 2.0 fm, r² = {sci((2.0e-15) ** 2, 2)} m², so F = {sci(KC * QE ** 2, 3)} / {sci((2.0e-15) ** 2, 2)} = {coul(2.0):.1f} N."),
    f"A scaling shortcut avoids the constants. F ∝ 1/r², so halving the distance multiplies the force by 4: at 1.0 fm the force is {coul(1.0):.0f} N. To find the distance for a given force, r = r₀ √(F₀/F). From 57.7 N at 2.0 fm to 14.4 N, F₀/F = {57.7 / 14.4:.2f}, √ of that is {math.sqrt(57.7 / 14.4):.2f}, so r = {2.0 * math.sqrt(57.7 / 14.4):.1f} fm.",
    simple="Two charges push apart, or pull together, with a force that falls with the square of the distance between them. Doubling the distance cuts the force to a quarter, and halving it makes the force four times larger."))
g(T, "Moving charges in a magnetic field", MORE("The radius of a charged particle's path",
    OL(f"<b>Momentum.</b> For a relativistic particle pc = √(KE² + 2·KE·m₀c²). For a 6.0 MeV electron, pc = √({6.0 ** 2:.1f} + 2 × 6.0 × {ME}) = √{6.0 ** 2 + 2 * 6.0 * ME:.3f} = {pc_of(6.0):.3f} MeV.",
       f"<b>Radius.</b> r [m] = pc [MeV] / (299.8 × B [T]). With B = 0.20 T, r = {pc_of(6.0):.3f} / (299.8 × 0.20) = {pc_of(6.0) / (299.8 * 0.2):.4f} m = {rad_cm(6.0, 0.2):.1f} cm.",
       f"<b>Why not the classical momentum?</b> The classical result p = √(2m·KE) gives pc = {math.sqrt(2 * ME * 6.0):.3f} MeV and r = {100 * math.sqrt(2 * ME * 6.0) / (299.8 * 0.2):.1f} cm, which is {rad_cm(6.0, 0.2) / (100 * math.sqrt(2 * ME * 6.0) / (299.8 * 0.2)):.1f} times too small. A 6 MeV electron is far into the relativistic range."),
    "The formula r = p/(qB) follows from setting the magnetic force qvB equal to the force needed to keep the particle on a circle. It holds with the relativistic momentum. The number 299.8 is c in units of 10<sup>6</sup> m/s, and it appears because pc is quoted in MeV and not in SI units.",
    simple="A magnetic force acts sideways on a moving charge, so the path bends into a circle and the speed does not change. A particle with more momentum makes a larger circle, and a stronger field makes a smaller one."))
g(T, "Atomic structure", MORE("Energy levels, transitions, and binding energies",
    UL("<b>Hydrogen levels.</b> E<sub>n</sub> = −13.6 eV / n². The energy to ionize from level n is +13.6 / n² eV.",
       "<b>Photon energy for a transition</b> = E<sub>initial</sub> − E<sub>final</sub>, with the levels as negative numbers. From n = 2 to n = 1: −3.40 − (−13.6) = 10.2 eV.",
       "<b>Wavelength.</b> λ [nm] = 1240 / E [eV]. A 1.89 eV photon has λ = 1240 / 1.89 = 656 nm.",
       "<b>Characteristic x-rays.</b> The photon carries the difference of the binding energies of the two shells. For tungsten, K minus L<sub>III</sub> is 69.5 − 10.2 = 59.3 keV.",
       "<b>Auger electrons.</b> The energy released by the transition goes to another electron, which leaves the atom with the transition energy minus its own binding energy, so less than the characteristic x-ray would carry."),
    TABLE(["Level n", "Energy (eV)", "Energy to ionize (eV)"], h_rows),
    f"The levels crowd together as n rises, so the jump to the ground state is by far the largest: 2→1 is {13.6 * (1 - 1 / 4):.1f} eV, 3→2 is {13.6 * (1 / 4 - 1 / 9):.2f} eV, 4→3 is {13.6 * (1 / 9 - 1 / 16):.2f} eV, and 5→4 is {13.6 * (1 / 16 - 1 / 25):.2f} eV.",
    simple="Electrons in an atom can only have certain energies. Moving between two levels releases or absorbs a photon whose energy is the difference between them. Inner levels are bound more tightly, so transitions that end in the K shell give the highest photon energies."))

q(T, "Two protons are separated by 2.0 fm.",
  simple="The force between two charges falls with the square of the distance. At nuclear distances it is large, which is why the strong force has to be stronger still.",
  steps=["Convert the distance: 2.0 fm = 2.0 × 10<sup>−15</sup> m.", f"k e² = 8.99 × 10<sup>9</sup> × (1.602 × 10<sup>−19</sup>)² = {sci(KC * QE ** 2, 3)} N·m².", f"r² = {sci((2.0e-15) ** 2, 2)} m².", f"F = {sci(KC * QE ** 2, 3)} / {sci((2.0e-15) ** 2, 2)} = {coul(2.0):.1f} N."], check=coul(2.0))
q(T, "What is the energy of the photon emitted when hydrogen drops from n = 2 to n = 1?",
  simple="The photon carries away the difference between the two energy levels.",
  steps=["E<sub>n</sub> = −13.6 / n² eV. E<sub>2</sub> = −13.6 / 4 = −3.40 eV, and E<sub>1</sub> = −13.6 eV.", "Photon energy = E<sub>initial</sub> − E<sub>final</sub> = −3.40 − (−13.6) = 10.2 eV."], check=10.2)
q(T, "What energy is needed to ionize a hydrogen atom whose electron is in the n = 2 shell?",
  simple="Ionization means lifting the electron to zero energy. The energy needed is the size of the level's negative energy.",
  steps=["E<sub>2</sub> = −13.6 / 2<sup>2</sup> = −13.6 / 4 = −3.40 eV.", "To reach zero energy, 3.40 eV must be supplied."], tip="13.6 eV is the energy needed from the ground state (n = 1), not from n = 2.", check=3.4)
q(T, "Tungsten has these electron binding energies.",
  simple="A characteristic x-ray is emitted when an electron falls from an outer shell into a vacancy in an inner shell. The photon carries the difference in the binding energies.",
  steps=["The electron moves from L<sub>III</sub> (binding energy 10.2 keV) into the K-shell vacancy (69.5 keV).", "Photon energy = 69.5 − 10.2 = 59.3 keV."], check=59.3)
q(T, "Which transition in hydrogen emits the highest-energy photon?",
  simple="Levels crowd together at larger n, so the largest jump is the one that ends in the ground state.",
  steps=[f"2 → 1: 13.6 × (1 − 1/4) = {13.6 * 0.75:.1f} eV.", f"3 → 2: 13.6 × (1/4 − 1/9) = {13.6 * (1 / 4 - 1 / 9):.2f} eV.", f"4 → 3: 13.6 × (1/9 − 1/16) = {13.6 * (1 / 9 - 1 / 16):.2f} eV.", f"5 → 4: 13.6 × (1/16 − 1/25) = {13.6 * (1 / 16 - 1 / 25):.2f} eV."])
q(T, "A 6.0 MeV electron moves perpendicular to a uniform 0.20 T magnetic field.",
  simple="The magnetic force bends the path into a circle. A larger momentum gives a larger circle and a stronger field gives a smaller one. At 6 MeV the electron is relativistic, so the momentum must come from the relativistic formula.",
  steps=[f"pc = √(KE² + 2·KE·m₀c²) = √({6.0 ** 2:.1f} + 2 × 6.0 × 0.511) = √{6.0 ** 2 + 2 * 6.0 * ME:.3f} = {pc_of(6.0):.3f} MeV.", f"r = pc / (299.8 × B) = {pc_of(6.0):.3f} / (299.8 × 0.20) = {pc_of(6.0) / (299.8 * 0.2):.4f} m.", f"In centimetres: {rad_cm(6.0, 0.2):.1f} cm."],
  tip=f"The classical momentum, pc = √(2 m KE), gives {100 * math.sqrt(2 * ME * 6.0) / (299.8 * 0.2):.1f} cm, which is wrong by a factor of 2.6.", check=rad_cm(6.0, 0.2))
q(T, "Two protons 2.0 fm apart repel with a force of 57.7 N.",
  simple="The force falls with the square of the distance. The force dropped by a factor of 4, so the distance grew by the square root of 4, which is 2.",
  steps=[f"Ratio of the forces: 57.7 / 14.4 = {57.7 / 14.4:.2f}, close to 4.", f"F ∝ 1/r², so r grows by the square root of the ratio: √{57.7 / 14.4:.2f} = {math.sqrt(57.7 / 14.4):.2f}.", f"New distance = 2.0 × {math.sqrt(57.7 / 14.4):.2f} = {2.0 * math.sqrt(57.7 / 14.4):.1f} fm."], check=4.0)
q(T, "A charged particle moves perpendicular to a uniform magnetic field.",
  simple="A force that is always at right angles to the motion changes the direction of the velocity and does no work on the particle, so the speed and the kinetic energy stay the same. The path is a circle.")
q(T, "Compared with an outer-shell electron in the same atom, an inner-shell electron is:",
  simple="Inner electrons are close to the nucleus and feel almost the full nuclear charge. Outer electrons are shielded by the electrons inside them. More tightly bound means more energy is needed to remove the electron, and the K shell is the most tightly bound in every atom.")
q(T, "An inner-shell vacancy in an atom can be filled with emission of a characteristic x-ray or an Auger electron.",
  simple="Both processes release the same energy, the difference between the binding energies of the two shells. A characteristic x-ray carries all of it away. In the Auger process the energy goes to another electron, which has to overcome its own binding energy to leave the atom, so it emerges with less.")

# ================================================================ 1.4 Nuclear structure and binding energy
T = "nuclear-structure"
M1H, MN = 1.007825, 1.008665
def defect(Z, N, M): return Z * M1H + N * MN - M
d2, d16 = defect(1, 1, 2.014102), defect(8, 8, 15.994915)
g(T, "Nuclide notation and classification", MORE("Telling isotopes, isobars, isotones, and isomers apart",
    OL("Write Z (the proton number, fixed by the element) and A (the mass number, the number after the name) for each nuclide.", "Find the neutron number N = A − Z. For Ir-192, N = 192 − 77 = 115.", "Compare the numbers the two nuclides share, using the table below."),
    TABLE(["Relationship", "What is the same", "Example"], [["Isotopes", "Z", "I-125 and I-131 (Z = 53)"], ["Isobars", "A", "Co-60 and Ni-60 (A = 60)"], ["Isotones", "N", "C-14 (N = 8) and N-15 (N = 8)"], ["Isomers", "Z and A, with a different energy state", "Tc-99m and Tc-99"]]),
    "The prefix is the clue: iso- means same, and the second part says what is the same. Isotopes share the number of protons, which is why they are the same element. Isobars share the mass number. Isotones share the neutron number. Isomers are the same nuclide in different energy states.",
    simple="Four words say which numbers two nuclides have in common. Same proton number: isotopes, so the same element. Same mass number: isobars. Same neutron number: isotones. Same protons and mass number but a different energy state: isomers."))
g(T, "Mass defect and binding energy", MORE("Calculating binding energy step by step",
    OL("Count the protons Z and the neutrons N of the nucleus.", f"Add the masses of the separate parts: Z × M(¹H) + N × m<sub>n</sub>, with M(¹H) = {M1H} u and m<sub>n</sub> = {MN} u. The hydrogen atom mass is used in place of the proton mass so that the electron masses balance the electrons of the atom whose mass is tabulated.",
       "Subtract the tabulated atomic mass of the nucleus. The difference is the mass defect Δm.", "Multiply by 931.5 MeV per u to get the binding energy, and divide by A for the energy per nucleon."),
    f"Deuteron: Δm = {M1H} + {MN} − 2.014102 = {d2:.6f} u, so BE = {d2:.6f} × 931.5 = {d2 * 931.5:.3f} MeV, or {d2 * 931.5 / 2:.2f} MeV per nucleon.",
    f"O-16 (8 protons, 8 neutrons): 8 × {M1H} = {8 * M1H:.5f} u and 8 × {MN} = {8 * MN:.5f} u, which add to {8 * M1H + 8 * MN:.5f} u. Subtracting 15.994915 u leaves Δm = {d16:.6f} u. BE = {d16:.6f} × 931.5 = {d16 * 931.5:.1f} MeV, and per nucleon {d16 * 931.5 / 16:.2f} MeV.",
    "The defect is a small difference of two nearly equal numbers, so keep all six decimal places. Rounding the three deuteron masses to three decimals would give a defect of 0.003 u and a binding energy of 2.8 MeV, instead of 2.2 MeV.",
    f"Energy is released when nucleons move to a higher binding energy per nucleon. For fission of U-235, each of 235 nucleons moves from about 7.6 to about 8.5 MeV: 235 × 0.9 = {235 * 0.9:.0f} MeV. For D–T fusion, 17.6 MeV from 5 nucleons is {17.6 / 5:.2f} MeV per nucleon, against {200 / 235:.2f} for fission, which is {(17.6 / 5) / (200 / 235):.1f} times more per nucleon.",
    simple="When nucleons join to make a nucleus they give up energy, and by E = mc² the finished nucleus weighs a little less than its separate parts. The missing mass is the mass defect. Multiplied by 931.5 MeV per u it gives the energy that holds the nucleus together."))

q(T, "Which pair are isobars?",
  simple="Isobars have the same mass number A but different proton numbers. In the names, A is the number after the element. Co-60 and Ni-60 both have A = 60, and Co and Ni are different elements.")
q(T, "M(1H) = 1.007825 umn = 1.008665 uM(2H) = 2.014102 u",
  simple="The deuteron is made of one proton and one neutron. Its measured mass is a little less than the sum of the two parts, and that missing mass is the binding energy in mass form.",
  steps=[f"Add the separate parts: 1.007825 + 1.008665 = {M1H + MN:.6f} u.", f"Subtract the atomic mass of H-2: {M1H + MN:.6f} − 2.014102 = {d2:.6f} u.", f"BE = {d2:.6f} × 931.5 = {d2 * 931.5:.3f} MeV."],
  tip="Half of this, 1.11 MeV, is the energy per nucleon, not the total.", check=d2 * 931.5)
q(T, "The He-4 nucleus has a total binding energy of 28.3 MeV.",
  simple="Binding energy per nucleon is the total divided by the number of nucleons.",
  steps=["He-4 has A = 4 nucleons.", f"28.3 / 4 = {28.3 / 4:.3f} MeV per nucleon."], check=28.3 / 4)
q(T, "Why do heavy stable nuclei contain more neutrons than protons?",
  simple="Every proton repels every other proton, and that repulsion reaches across the whole nucleus. The strong force acts only between close neighbours. Neutrons add strong-force attraction without adding repulsion, so a heavy nucleus needs extra neutrons to stay bound.")
q(T, "Which nucleus has the highest binding energy per nucleon of those listed?",
  simple="The binding energy per nucleon rises quickly for the lightest nuclei, peaks near iron and nickel at about 8.8 MeV per nucleon, and then falls slowly for heavy nuclei. Fe-56 sits at the peak, which is why it is the most tightly bound of the choices.")
q(T, "Energy is released in nuclear reactions when:",
  simple="A reaction releases energy when its products are more tightly bound per nucleon than the starting nuclei. Light nuclei that fuse climb the curve toward the peak, and heavy nuclei that split also move up toward it. Both release energy.")
q(T, "U-235: 7.6 MeV per nucleonfission fragments: 8.5 MeV per nucleonEstimate",
  simple="Splitting the nucleus moves every nucleon to a more tightly bound state. Each nucleon gains the difference in binding energy per nucleon, and that gain is released.",
  steps=["The gain per nucleon is 8.5 − 7.6 = 0.9 MeV.", f"There are 235 nucleons, so the energy released is 235 × 0.9 = {235 * 0.9:.1f} MeV."], tip="The accepted value is about 200 MeV. The estimate is rough because the two binding energies per nucleon are rounded.", check=235 * 0.9)
q(T, "M(O-16) = 15.994915 uM(1H) = 1.007825 u",
  simple="The method is the same as for any nucleus: add up the separate parts, subtract the real mass, and convert the difference to energy.",
  steps=[f"Protons: 8 × 1.007825 = {8 * M1H:.5f} u. Neutrons: 8 × 1.008665 = {8 * MN:.5f} u. Sum = {8 * M1H + 8 * MN:.5f} u.", f"Mass defect: {8 * M1H + 8 * MN:.5f} − 15.994915 = {d16:.6f} u.", f"BE = {d16:.6f} × 931.5 = {d16 * 931.5:.1f} MeV.", f"Per nucleon: {d16 * 931.5:.1f} / 16 = {d16 * 931.5 / 16:.2f} MeV."], check=d16 * 931.5 / 16)
q(T, "D–T fusion: 17.6 MeV from 5 nucleons",
  simple="Compare the energy per nucleon, not the energy per reaction. A fusion reaction involves only 5 nucleons and a fission involves 235.",
  steps=[f"Fusion: 17.6 / 5 = {17.6 / 5:.2f} MeV per nucleon.", f"Fission: 200 / 235 = {200 / 235:.2f} MeV per nucleon.", f"Ratio: {17.6 / 5:.2f} / {200 / 235:.2f} = {(17.6 / 5) / (200 / 235):.1f}."], check=(17.6 / 5) / (200 / 235))

# ================================================================ 1.5 Decay modes
T = "decay-modes"
g(T, "Stability and decay mode", MORE("Finding the daughter, and which mode applies",
    OL("Write down Z and A of the parent. The element name fixes Z, and the number after the name is A.", "Apply the change that the decay makes to Z and A, using the table below.", "Find the element with the new Z. That, with the new A, is the daughter."),
    TABLE(["Decay", "What happens in the nucleus", "Z", "A", "Example"], [["α", "Two protons and two neutrons are emitted", "−2", "−4", "Po-210 (Z = 84) → Pb-206 (Z = 82)"], ["β⁻", "A neutron becomes a proton and an electron is emitted", "+1", "same", "I-131 (Z = 53) → Xe-131 (Z = 54)"],
                                                                               ["β⁺", "A proton becomes a neutron and a positron is emitted", "−1", "same", "F-18 → O-18"], ["Electron capture", "A proton and an orbital electron become a neutron", "−1", "same", "I-125 → Te-125"], ["γ or isomeric transition", "An excited nucleus drops to a lower state", "same", "same", "Tc-99m → Tc-99"]]),
    "The mode depends on where the nucleus sits relative to the stable band. A nucleus with too many neutrons turns a neutron into a proton: β⁻. A nucleus with too many protons turns a proton into a neutron: β⁺ or electron capture. A very heavy nucleus sheds mass by α emission. An excited nucleus, with Z and N already right, only has to lose energy: γ emission.",
    simple="A nucleus decays to move toward the band of stable nuclei. Too many neutrons: a neutron turns into a proton. Too many protons: a proton turns into a neutron. Very heavy: an α particle carries away two protons and two neutrons. An excited nucleus with the right numbers of protons and neutrons gives off its extra energy."))
g(T, "Decay modes", MORE("The energy needed for β⁺ decay and the maximum positron energy",
    OL("Find the energy available, the difference between the atomic masses of the parent and the daughter, expressed in MeV.",
       "Compare it with 1.022 MeV. β⁺ decay creates a positron (0.511 MeV) and the atom must also shed one extra orbital electron (0.511 MeV), so it needs at least two electron rest energies.",
       "If the energy available is below 1.022 MeV, only electron capture is possible. If it is above, β⁺ decay can occur, usually together with electron capture.",
       "The most energetic positron has kinetic energy = (energy available) − 1.022 MeV."),
    f"For an available energy of 0.80 MeV, β⁺ decay is not possible and electron capture is the only proton-rich decay. For 1.70 MeV, the maximum positron energy is 1.70 − 1.022 = {1.70 - 2 * ME:.3f} MeV. For β⁻ decay no such subtraction is made, and the energy available is shared directly between the electron, the antineutrino, and the daughter.",
    "The positron and the neutrino share the energy, so positrons come out with a continuous spectrum from zero up to this maximum.",
    simple="β⁺ decay makes a positron, and the atom also has to lose one orbital electron because the daughter has one fewer proton. Together those cost two electron rest energies, 1.022 MeV. Electron capture needs no such payment, which is why it can occur when the energy available is small."))
g(T, "Internal conversion and Auger electrons", MORE("What leaves the atom, and with what energy",
    UL("<b>γ emission.</b> The nucleus drops to a lower state and a photon carries away the energy.",
       "<b>Internal conversion.</b> The nucleus passes the energy to an orbital electron instead. The electron leaves with kinetic energy E<sub>γ</sub> minus its binding energy. For a 140 keV transition converting in a shell with 21 keV binding energy, the electron has 119 keV.",
       "<b>The vacancy.</b> Internal conversion and electron capture both leave a vacancy in an inner shell. Outer electrons fall in and the energy is released as a characteristic x-ray (the difference of the two binding energies) or is passed to another electron, which leaves as an Auger electron.",
       "<b>Auger electron energy.</b> It is the energy released by the transition minus the binding energy of the electron that leaves, so it is smaller than the characteristic x-ray energy."),
    "In every one of these processes the nucleus ends with the same Z and A as it had before the conversion: only its energy state changes.",
    simple="An excited nucleus can lose its energy in two ways. It can emit a γ-ray, or it can hand the energy to an orbital electron, which leaves the atom. That second way is internal conversion. Either way the nucleus ends in a lower state with the same Z and A, and any inner-shell vacancy is filled by a characteristic x-ray or an Auger electron."))

q(T, "What is the daughter nuclide when Po-210 (Z = 84) decays by α emission?",
  simple="An α particle is a helium nucleus: two protons and two neutrons. When it leaves, the nucleus loses both.",
  steps=["Mass number: 210 − 4 = 206.", "Proton number: 84 − 2 = 82.", "The element with Z = 82 is lead, so the daughter is Pb-206."])
q(T, "Which radiations can follow an electron-capture event in the daughter atom?",
  simple="In electron capture a proton and an inner-shell electron become a neutron. The missing inner electron leaves a vacancy, and an outer electron falls in to fill it. The energy released appears as a characteristic x-ray or as an Auger electron. No positron is emitted, so there are no annihilation photons.")
q(T, "A nuclide has a decay energy (atomic mass difference) of 0.80 MeV",
  simple="β⁺ decay needs enough energy to create a positron and to shed an extra electron from the atom. Electron capture has no such requirement.",
  steps=["The energy needed for β⁺ decay is 2 × 0.511 = 1.022 MeV.", "The energy available is 0.80 MeV, which is less than 1.022 MeV, so β⁺ decay cannot occur.", "Electron capture has no threshold, so it is the only proton-rich decay that can occur."])
q(T, "Why does a positron emitter produce two 511 keV photons?",
  simple="A positron soon slows down and meets an electron. They annihilate, and their rest energy, 2 × 511 keV, becomes radiation. Starting almost at rest they have no net momentum, so the photons must leave in opposite directions with equal energies.",
  steps=["Rest energy of the two particles: 0.511 + 0.511 = 1.022 MeV.", "Zero net momentum requires two photons with equal energy in opposite directions.", "Each photon carries 1.022 / 2 = 0.511 MeV, which is 511 keV."])
q(T, "Which statements about internal conversion are correct?",
  simple="Internal conversion is an alternative to γ emission. The nucleus passes its energy to an orbital electron, which leaves the atom. The nucleus itself keeps the same Z and A, because only its energy state changes. The ejected electron leaves a vacancy that is filled by a characteristic x-ray or an Auger electron.")
q(T, "I-131 (Z = 53) decays by β⁻ emission.",
  simple="In β⁻ decay a neutron in the nucleus becomes a proton, and an electron and an antineutrino are emitted. The number of nucleons does not change, but there is one more proton.",
  steps=["Mass number: unchanged, so A = 131.", "Proton number: 53 + 1 = 54.", "The element with Z = 54 is xenon, so the daughter is Xe-131."])
q(T, "A positron emitter has an atomic mass difference of 1.70 MeV",
  simple="Of the energy available, 1.022 MeV is spent creating the positron and shedding the extra electron. What is left is shared as kinetic energy, and the most energetic positron receives all of it.",
  steps=["Energy available: 1.70 MeV.", f"Subtract the two electron rest energies: 1.70 − 1.022 = {1.70 - 2 * ME:.3f} MeV.", "That is the maximum kinetic energy of the positron."], check=1.70 - 2 * ME)
q(T, "A nuclide has too few neutrons for its number of protons.",
  simple="Too few neutrons means too many protons, so the nucleus lies on the proton-rich side of the stable band. To move toward the band, a proton must change into a neutron. β⁺ decay and electron capture both do that. β⁻ decay does the opposite, and γ emission changes neither number.")
q(T, "Why is an α emitter such as Ra-223 a small external hazard",
  simple="An α particle has a large charge and a large mass, so it loses its energy in a very short distance. In tissue it travels less than 100 µm, so from outside the body it does not get through the outer layer of skin to living cells. Inside the body, the same short range deposits all of its energy within a few cell diameters, which suits radiopharmaceutical therapy.")
q(T, "Which decay raises Z by one without changing A?",
  simple="Raising Z by one with the same number of nucleons means a neutron has become a proton. That is what happens in β⁻ decay, where an electron is emitted at the same time.")
q(T, "Which of these radionuclides is a positron emitter used for PET?",
  simple="PET needs a nuclide that emits positrons, because each positron produces the two 511 keV photons that the scanner detects. F-18 has too many protons for its neutrons and decays mainly by β⁺. Tc-99m emits γ-rays, I-125 decays by electron capture, and Cs-137 by β⁻.")
q(T, "Tc-99m decays by:",
  simple="The m in Tc-99m stands for metastable, an excited state with a measurable lifetime. It drops to the ground state, Tc-99, and emits a 140 keV γ-ray. Z and A do not change.")

# ================================================================ 1.6 Decay schemes and radionuclide production
T = "decay-schemes"
g(T, "Reading a decay scheme", MORE("Reading a scheme and adding up the radiation",
    OL("Find the level that the decay feeds. A decay scheme plots energy upward, so a lower arrow end means less energy. For Co-60, almost every decay feeds the 2.505 MeV level of Ni-60.",
       "Follow the transitions down to the ground state. If every decay passes through the same cascade, every decay emits one photon of each energy. For Co-60 that is 1.173 MeV and 1.332 MeV, and together 1.173 + 1.332 = 2.505 MeV, the energy of the level.",
       "Multiply the branching fractions along the path to count the photons that are emitted. For Cs-137, 94.4% of decays reach Ba-137m, and about 90% of Ba-137m transitions emit a photon (the rest are internal conversions). Per 1000 Cs-137 decays, 1000 × 0.944 × 0.90 = 850 photons of 662 keV.",
       f"For the energy of the β particle, take the decay energy to the ground state and subtract the energy of the level fed. For Co-60, 2.824 − 2.505 = {2.824 - 2.505:.3f} MeV is the maximum β energy, and the mean is about one third of that, near 0.1 MeV."),
    "The direction of an arrow tells the process. Atomic number increases to the right, so an arrow down and to the right is β⁻. An arrow down and to the left is β⁺ or electron capture, and a longer one to the left is α emission. A vertical arrow is γ emission or internal conversion, with Z and A unchanged.",
    simple="A decay scheme is a map of energy levels. Going down means the nucleus loses energy, and moving to the right means that Z goes up. Each arrow is one process, labelled with how often it happens and the energy involved. To count the radiation, follow the arrows from the level that the decay feeds and multiply the fractions."))
g(T, "Discrete and continuous spectra", MORE("Why the β spectrum is continuous, and its mean energy",
    UL("<b>Discrete.</b> α particles, γ-rays, characteristic x-rays, and Auger electrons come from a transition between two fixed levels. One particle or photon carries the whole energy difference, so the energy has a single value.",
       "<b>Continuous.</b> In β decay the energy is shared between the electron (or positron), the neutrino, and the daughter nucleus. The electron can take any energy from zero up to the maximum, and the neutrino takes the rest, so the spectrum is continuous. Bremsstrahlung is continuous because the electron can give any fraction of its energy to the photon.",
       f"<b>Mean energy.</b> It is roughly one third of the maximum energy. For E<sub>max</sub> = 1.80 MeV, the mean is 1.80 / 3 = {1.80 / 3:.2f} MeV. For Co-60, with E<sub>max</sub> = 0.319 MeV, it is about {0.319 / 3:.2f} MeV."),
    simple="When a nucleus drops between two fixed levels, one photon or one particle carries all of the energy difference, so it always has the same energy. In β decay the energy is split between two or three bodies, and it can be split in any proportion, so the electron energies form a smooth spread up to a maximum."))
g(T, "Radionuclide production", MORE("Predicting the decay from the production route",
    OL("Write the reaction as target(projectile, ejected particle)product, for example <sup>18</sup>O(p,n)<sup>18</sup>F.",
       "Compare the product with the target. Count its protons and neutrons.",
       "A product with extra neutrons lies above the stable band and decays by β⁻. A product with extra protons, or with fewer neutrons, lies below it and decays by β⁺ or electron capture."),
    f"<sup>59</sup>Co(n,γ)<sup>60</sup>Co adds a neutron, so Co-60 is neutron-rich and decays by β⁻ to Ni-60. <sup>191</sup>Ir(n,γ)<sup>192</sup>Ir also adds a neutron, so Ir-192 is neutron-rich and decays mainly by β⁻. <sup>18</sup>O(p,n)<sup>18</sup>F adds a proton and removes a neutron: O-18 has 8 protons and 10 neutrons, and F-18 has 9 and 9, so F-18 is proton-rich and decays by β⁺.",
    "Neutron capture takes place in a reactor, and the product is the same element as the target, so stable atoms of that element remain in the source as carrier. Charged-particle reactions are done in a cyclotron, and a reaction such as (p,n) changes the element, so the product can be separated chemically and can have a high specific activity.",
    simple="Adding neutrons to a nucleus leaves it with too many neutrons, and it decays by β⁻ to move back. Adding protons, or removing neutrons, leaves it with too many protons, and it decays by β⁺ or electron capture. The production route therefore tells which way the product will decay."))

q(T, "In a decay scheme, an arrow that slants down and to the right indicates:",
  simple="Atomic number increases to the right in a decay scheme. Down means that the nucleus loses energy. A neutron turning into a proton raises Z by one, and that is β⁻ decay.")
q(T, "A straight vertical downward arrow in a decay scheme indicates:",
  simple="A vertical arrow does not move left or right, so Z does not change. The nucleus only drops to a lower energy level, which is γ emission or internal conversion.")
q(T, "Which radiation has a continuous energy spectrum?",
  simple="Most radiations are emitted with fixed energies, because they come from a transition between two fixed levels. In β⁻ decay the energy is shared between the electron and the antineutrino in any proportion, so the electron energy forms a continuous spread up to a maximum.")
q(T, "Which particle shares the decay energy with the electron in β⁻ decay?",
  simple="β⁻ decay emits an electron and an electron antineutrino. β⁺ decay emits a positron and a neutrino. The antineutrino carries off the part of the energy that the electron does not take, which is why the electron energy is not fixed.")
q(T, "Which of these radiations are emitted with discrete energies?",
  simple="Radiation from a transition between two fixed levels has a single energy: α particles, γ-rays, and characteristic x-rays. Radiation from a shared decay energy (β particles) or from a slowing electron (bremsstrahlung) has a continuous spectrum.")
q(T, "A Co-60 nucleus emits γ-rays of 1.173 MeV and 1.332 MeV in cascade.",
  simple="In nearly every decay the nucleus passes through both transitions, so both photons are emitted in each decay and their energies add.",
  steps=["Add the two photon energies: 1.173 + 1.332 = 2.505 MeV.", "This equals the energy of the Ni-60 level that the decay feeds."], check=1.173 + 1.332)
q(T, "1000 Cs-137 decays94.4% of decays reach Ba-137m",
  simple="Not every decay leads to a photon. The photon comes from Ba-137m, and only some of the Ba-137m transitions emit it. Multiply the fractions along the path.",
  steps=["Number of decays that reach Ba-137m: 1000 × 0.944 = 944.", "Of those, about 90% emit a photon: 944 × 0.90 = 850.", "About 850 photons, which rounds to the choice 851. The remaining Ba-137m transitions are internal conversions, which emit an electron and not a photon."], check=1000 * 0.944 * 0.90)
q(T, "Which production route is used for Ir-192 sources for HDR brachytherapy?",
  simple="Ir-191 is a stable and abundant isotope of iridium. Placing it in a reactor lets it capture a neutron and become Ir-192. The reaction is written <sup>191</sup>Ir(n,γ)<sup>192</sup>Ir.")
q(T, "A nuclide produced by neutron capture in a reactor will most likely decay by:",
  simple="Neutron capture adds a neutron, so the product has more neutrons than the stable band allows. To return, a neutron must turn into a proton, which is β⁻ decay.")
q(T, "F-18 is made by the reaction 18O(p,n)18F.",
  simple="The reaction is written target(projectile, ejected particle)product. A proton enters O-18 and a neutron leaves, so the product has one more proton and one less neutron.",
  steps=["O-18 has 8 protons and 10 neutrons. F-18 has 9 protons and 9 neutrons.", "The product has extra protons, so it lies below the stable band and decays by β⁺ or electron capture.", "Bombarding with protons needs a charged-particle accelerator, which is a cyclotron."])
q(T, "decay energy to the Ni-60 ground state = 2.824 MeV",
  simple="The decay releases 2.824 MeV in all. The γ-rays that follow take away the energy of the level that is fed, 2.505 MeV. What remains is shared by the electron and the antineutrino, and the most energetic electron takes all of it.",
  steps=["Energy to the ground state: 2.824 MeV.", "Energy carried off by the γ cascade: 2.505 MeV.", f"E<sub>max</sub> = 2.824 − 2.505 = {2.824 - 2.505:.3f} MeV."], check=2.824 - 2.505)
q(T, "A β⁻ emitter has Emax = 1.80 MeV.",
  simple="The electron energies spread from zero up to Emax, with most electrons well below the maximum. The mean is about one third of Emax.",
  steps=[f"Mean energy ≈ E<sub>max</sub> / 3 = 1.80 / 3 = {1.80 / 3:.2f} MeV."], tip="Half of Emax, 0.90 MeV, is too high.", check=1.80 / 3)
q(T, "Which statement about a Cs-137 source is correct?",
  simple="Cs-137 does not emit the 662 keV photon directly. It decays by β⁻ to Ba-137m, a metastable state with a half-life of 2.55 minutes, and Ba-137m emits the photon when it drops to the ground state. In a sealed source the Ba-137m is in equilibrium with the Cs-137, so the photon is emitted at the rate of the Cs-137 decays, reduced by the branching fractions.")
q(T, "A β⁻ emitter has the energy spectrum shown.",
  simple="The spectrum is a spread of electron energies from zero up to the maximum. The mean energy is the average of all of them, about one third of the maximum, which on the axis of Emax is 0.33.",
  steps=["The horizontal axis is the energy as a fraction of E<sub>max</sub>.", "The mean energy is about E<sub>max</sub> / 3, so tap near 0.33 on the axis."],
  tip="The peak of the spectrum is below the mean, and half of the maximum, 0.5, is too high.")

# ================================================================ 1.1 Waves, photons, and units
T = "waves-photons"
HC, HEV, CC = 1240.0, 4.136e-15, 3.00e8                       # eV·nm, eV·s, m/s
pcm = lambda ke: math.sqrt(ke ** 2 + 2 * ke * ME)
g(T, "Electromagnetic waves and photons", MORE("Converting between wavelength, frequency, and photon energy",
    OL("<b>Frequency to wavelength.</b> λ = c / ν. For ν = 6.0 × 10<sup>14</sup> Hz, λ = (3.00 × 10<sup>8</sup>) / (6.0 × 10<sup>14</sup>) = 5.0 × 10<sup>−7</sup> m = 500 nm.",
       f"<b>Energy to wavelength.</b> λ = hc / E. With hc = 1240 eV·nm and E in eV, λ comes out in nm. For 25 keV, E = 25,000 eV and λ = 1240 / 25,000 = {1240 / 25000:.4f} nm = {12.4 / 25:.3f} Å.",
       f"<b>Energy to frequency.</b> ν = E / h, with h = 4.136 × 10<sup>−15</sup> eV·s. For 140 keV, ν = 1.40 × 10<sup>5</sup> / (4.136 × 10<sup>−15</sup>) = {sci(1.40e5 / HEV, 2)} Hz.",
       f"<b>Frequency to energy.</b> E = hν. For 2.45 GHz, E = 4.136 × 10<sup>−15</sup> × 2.45 × 10<sup>9</sup> = {sci(HEV * 2.45e9, 2)} eV."),
    TABLE(["Energy unit", "Value of hc", "Wavelength comes out in"], [["eV", "1240 eV·nm", "nm"], ["keV", "12.4 keV·Å", "Å (10<sup>−10</sup> m)"], ["MeV", "1.24 MeV·pm", "pm (10<sup>−12</sup> m)"]]),
    f"Use the row that matches the unit of the energy. For 511 keV (0.511 MeV), λ = 1.24 / 0.511 = {1.24 / 0.511:.2f} pm. For 6.0 MeV, λ = 1.24 / 6.0 = {1.24 / 6.0:.3f} pm.",
    "Two checks catch most mistakes. Higher energy means a shorter wavelength, so halving the wavelength doubles the energy. And the prefixes must be handled with care: GHz is 10<sup>9</sup> Hz, and 1 nm is 10<sup>−9</sup> m.",
    simple="Frequency, wavelength, and photon energy describe the same wave in three ways. The wavelength and the frequency are tied together by the speed of light, and the photon energy is set by the frequency alone. A short wavelength means a high frequency and a high photon energy."))
g(T, "Units and prefixes", MORE("Converting prefixes and units",
    OL("Write the number in scientific notation with the prefix as a power of ten: 140 keV = 140 × 10<sup>3</sup> eV = 1.40 × 10<sup>5</sup> eV.",
       "Convert eV to joules by multiplying by 1.602 × 10<sup>−19</sup> J per eV. For 1.0 MeV = 10<sup>6</sup> eV, E = 10<sup>6</sup> × 1.602 × 10<sup>−19</sup> = 1.602 × 10<sup>−13</sup> J.",
       "Convert length units with the same rule: 500 nm = 500 × 10<sup>−9</sup> m = 5.00 × 10<sup>−7</sup> m, and 12.4 pm = 0.0124 nm."),
    TABLE(["Prefix", "Factor", "Prefix", "Factor"], [["pico (p)", "10<sup>−12</sup>", "kilo (k)", "10<sup>3</sup>"], ["nano (n)", "10<sup>−9</sup>", "mega (M)", "10<sup>6</sup>"], ["micro (µ)", "10<sup>−6</sup>", "giga (G)", "10<sup>9</sup>"], ["milli (m)", "10<sup>−3</sup>", "tera (T)", "10<sup>12</sup>"]]),
    "Units of energy are the joule, the electron-volt, and the kilowatt-hour (3.6 × 10<sup>6</sup> J). The watt is energy per second, which is power, and the pascal is pressure.",
    simple="A prefix is a power of ten. To convert, write the number in scientific notation with the prefix as a power of ten, and multiply by the conversion factor for the unit."))
g(T, "Matter waves", MORE("Wavelength of a particle, step by step",
    OL(f"A particle's wavelength is λ = h/p, so it needs the momentum. For a relativistic electron, pc = √(KE² + 2·KE·m₀c²). For KE = 0.100 MeV, pc = √({0.1 ** 2:.2f} + 2 × 0.100 × 0.511) = √{0.1 ** 2 + 2 * 0.1 * ME:.4f} = {pcm(0.1):.4f} MeV.",
       f"Use hc = 1.240 MeV·pm: λ = 1.240 / {pcm(0.1):.4f} = {1.240 / pcm(0.1):.2f} pm.",
       f"A 100 keV photon has pc = E = 0.100 MeV, so λ = 1.240 / 0.100 = {1.240 / 0.100:.1f} pm."),
    f"The electron has the shorter wavelength by a factor of {pcm(0.1) / 0.1:.2f}. Its momentum, {pcm(0.1):.3f} MeV/c, is larger than the {0.1:.3f} MeV/c of the photon, because the electron has mass as well as energy. The electron wavelength is much smaller than an atom (about 100 pm), which is why electron beams can resolve atomic structure.",
    simple="Particles have a wavelength too, set by their momentum: the more momentum, the shorter the wavelength. A photon and an electron with the same energy do not have the same momentum, because the electron also has mass, so its wavelength is shorter."))

q(T, "Which radiation has the highest photon energy?",
  simple="Compare all of the photon energies in the same unit, electron-volts. The wavelength 100 nm gives E = 1240 / 100 nm = 12.4 eV, and the x-ray is already 80 keV = 80,000 eV.",
  steps=["Energy in eV = 1240 / wavelength in nm.", "100 nm ultraviolet: 1240 / 100 = 12.4 eV. Green light of 532 nm: 1240 / 532 = 2.33 eV.", "The 80 keV x-ray: 80 × 1000 = 80,000 eV, which is far larger."])
q(T, "Light has a known frequency.",
  simple="Light travels at c, so the wavelength is the speed divided by the frequency. A high frequency gives a short wavelength.",
  steps=[f"λ = c / ν = 3.00 × 10<sup>8</sup> / 6.0 × 10<sup>14</sup> = {CC / 6.0e14:.1e} m.".replace("e-07", " × 10<sup>−7</sup>"), f"Convert to nanometres: {CC / 6.0e14 * 1e9:.0f} nm."], check=CC / 6.0e14 * 1e9)
q(T, "How many joules are in 1.0 MeV?",
  simple="An electron-volt is a very small unit of energy. One eV is 1.602 × 10<sup>−19</sup> J, and a megaelectron-volt is a million of them.",
  steps=["1.0 MeV = 1.0 × 10<sup>6</sup> eV.", f"Multiply by 1.602 × 10<sup>−19</sup> J per eV: 10<sup>6</sup> × 1.602 × 10<sup>−19</sup> = {sci(1.602e-13, 4)} J."], check=1.602e-13)
q(T, "The most energetic photon in a 6 MV x-ray beam.",
  simple="A photon's wavelength is inversely proportional to its energy, so a 6 MeV photon has a very short wavelength. Use the version of hc that matches MeV.",
  steps=["hc = 1.24 MeV·pm, which gives the wavelength in picometres for an energy in MeV.", f"λ = 1.24 / 6.0 = {1.24 / 6.0:.4f} pm."], tip="This is 0.207 pm, or 2.07 × 10<sup>−4</sup> nm. It is far smaller than an atom.", check=1.24 / 6.0)
q(T, "A linac is driven at a microwave frequency.",
  simple="Microwaves are electromagnetic waves, so the wavelength is the speed of light divided by the frequency.",
  steps=["Write the frequency in hertz: 2.998 GHz = 2.998 × 10<sup>9</sup> Hz.", "λ = c / f = 2.998 × 10<sup>8</sup> / 2.998 × 10<sup>9</sup> = 0.100 m.", "In centimetres: 10 cm."], check=10.0)
q(T, "The wavelength of a photon is halved.",
  simple="Photon energy is inversely proportional to wavelength: E = hc/λ. Making the wave half as long doubles the energy.",
  steps=["Write the energy as E = hc / λ.", "Replace λ by λ/2: E′ = hc / (λ/2) = 2 × hc / λ = 2E.", "Example: a 10 keV photon has λ = 12.4 / 10 = 1.24 Å. At half the wavelength, 0.62 Å, the energy is 12.4 / 0.62 = 20 keV, which is double."],
  tip="Energy is not proportional to the wavelength. A shorter wavelength means a higher energy.")
q(T, "What is the wavelength of a 25 keV photon?",
  simple="Choose the version of hc that matches the unit of the energy. For keV, hc = 12.4 keV·Å gives the wavelength in angstroms.",
  steps=[f"λ = 12.4 keV·Å / 25 keV = {12.4 / 25:.3f} Å.", f"In nanometres, 1 Å = 0.1 nm, so λ = {12.4 / 25 / 10:.4f} nm."], check=12.4 / 25)
q(T, "Tc-99m emits a 140 keV γ-ray.",
  simple="Energy and frequency are proportional: E = hν. Divide the energy by Planck's constant, with both in electron-volts.",
  steps=["Convert the energy to eV: 140 keV = 1.40 × 10<sup>5</sup> eV.", f"ν = E / h = 1.40 × 10<sup>5</sup> / 4.136 × 10<sup>−15</sup> = {sci(1.40e5 / HEV, 2)} Hz."], check=1.40e5 / HEV)
q(T, "The intensity of a monochromatic x-ray beam is doubled",
  simple="Photon energy depends only on wavelength. Doubling the intensity at the same wavelength means twice as many photons each second, each with the same energy as before.")
q(T, "What is the wavelength of a 511 keV annihilation photon?",
  simple="Use hc = 1.24 MeV·pm and the energy in MeV.",
  steps=["511 keV = 0.511 MeV.", f"λ = 1.24 / 0.511 = {1.24 / 0.511:.2f} pm."], tip="This is the Compton wavelength of the electron.", check=1.24 / 0.511)
q(T, "Compare two photons.",
  simple="Compare the two energies in the same unit. The x-ray energy is given in electron-volts, so convert the microwave frequency to an energy in electron-volts with E = hν.",
  steps=["Microwave photon: E = hν = 4.136 × 10<sup>−15</sup> × 2.45 × 10<sup>9</sup> = 1.01 × 10<sup>−5</sup> eV.", "X-ray photon: E = 100 keV = 1.00 × 10<sup>5</sup> eV.", f"Ratio = 1.00 × 10<sup>5</sup> / 1.01 × 10<sup>−5</sup> = {1.0e5 / (HEV * 2.45e9):.2e}, about 10<sup>10</sup>.".replace("e+09", " × 10<sup>9</sup>")], check=math.log10(1.0e5 / (HEV * 2.45e9)))      # the answer options are powers of ten, stored as the exponent
q(T, "Which has the shorter wavelength: a 100 keV electron or a 100 keV photon?",
  simple="A particle's wavelength is h/p. A photon and an electron with the same energy do not have the same momentum, because the electron also has mass. Its momentum is larger, so its wavelength is shorter.",
  steps=["Photon: λ = hc / E = 1.24 MeV·pm / 0.100 MeV = 12.4 pm.", f"Electron: pc = √(KE² + 2·KE·m₀c²) = √(0.0100 + 0.1022) = {pcm(0.1):.3f} MeV.", f"λ = 1.24 / {pcm(0.1):.3f} = {1.24 / pcm(0.1):.2f} pm, which is shorter than the photon's 12.4 pm."])
q(T, "Which of these are units of energy?",
  simple="Energy can be measured in joules, in electron-volts, and in kilowatt-hours. The watt measures power, which is energy per second, and the pascal measures pressure. A kilowatt-hour is power multiplied by time, which gives energy.")

# ================================================================ Basic physics: the remaining questions (recall, sorting, and tap-the-figure)
H_, M_ = "How to decide", None
# ---- 1.2
T = "particles-energy"
q(T, "What is the rest energy of an electron?",
  simple="Mass and energy are two forms of the same thing, E = mc². An electron at rest has the energy equivalent of its mass, and that value, 0.511 MeV, is used throughout radiation physics.",
  steps=["The electron mass is 9.109 × 10<sup>−31</sup> kg, and c = 2.998 × 10<sup>8</sup> m/s.", f"E = mc² = 9.109 × 10<sup>−31</sup> × (2.998 × 10<sup>8</sup>)² = {sci(9.109e-31 * 2.998e8 ** 2, 3)} J.", f"Divide by 1.602 × 10<sup>−13</sup> J per MeV: {9.109e-31 * 2.998e8 ** 2 / 1.602e-13:.3f} MeV."])
q(T, "Approximately how many times heavier is a proton than an electron?",
  simple="The rest energies are proportional to the masses, so the ratio of the rest energies is the ratio of the masses.",
  steps=[f"Proton: 938.3 MeV. Electron: 0.511 MeV.", f"Ratio = 938.3 / 0.511 = {938.3 / 0.511:.0f}."])
q(T, "Which of these particles carry no electric charge?",
  simple="Only two of the common particles are neutral: the neutron and the photon. The positron has a charge of +1, the proton +1, and the α particle +2, because it is a helium nucleus with two protons.",
  steps=["Neutron: charge 0. Photon: charge 0.", "Positron: +1. Proton: +1. α particle: +2. Electron: −1."], how=H_)
# ---- 1.3
T = "charges-atom"
q(T, "The distance between two charges is doubled.",
  simple="The Coulomb force falls with the square of the distance. Twice as far means the force is one quarter as large.",
  steps=["F ∝ 1/r².", "Replace r by 2r: F′ ∝ 1/(2r)² = 1/(4r²) = F/4."])
q(T, "What did the scattering of α particles from gold foil show?",
  simple="Most α particles passed straight through the foil, but a few bounced back through large angles. That could only happen if the positive charge and most of the mass were packed into a very small core, the nucleus, with the electrons far outside it.")
q(T, "What energy is needed to ionize a hydrogen atom in its ground state?",
  simple="The ground state has an energy of −13.6 eV, which means 13.6 eV of energy is needed to lift the electron to zero energy, free of the atom.",
  steps=["E<sub>1</sub> = −13.6 eV / 1² = −13.6 eV.", "Ionization takes the electron to E = 0, so the energy needed is 0 − (−13.6) = 13.6 eV."], tip="Ionizing from n = 2 needs only 3.40 eV.")
# ---- 1.4
T = "nuclear-structure"
q(T, "Which pair are isotopes of the same element?",
  simple="Isotopes have the same number of protons Z, so they are the same element, and different numbers of neutrons. Look up Z for each pair.",
  steps=["I-125 and I-131: both iodine, Z = 53, with 72 and 78 neutrons. Isotopes.", "C-14 and N-14 have the same A but different Z (6 and 7): isobars.", "C-14 and N-15 have the same N (8) but different Z: isotones.", "Mo-99 and Tc-99m are different elements, Z = 42 and 43."], how=H_)
q(T, "How many neutrons are in an Ir-192 nucleus",
  simple="The mass number counts all the nucleons, protons and neutrons together. The neutron number is what is left after the protons are taken away.",
  steps=["N = A − Z.", "A = 192 and Z = 77, so N = 192 − 77 = 115."])
q(T, "Which force holds protons together in the nucleus",
  simple="The protons repel each other by the Coulomb force. At distances of a few femtometres, the strong nuclear force between neighbouring nucleons is stronger than that repulsion and binds the nucleus. It acts only over very short range.")
q(T, "Tc-99m and Tc-99 are best described as:",
  simple="Both are technetium with 99 nucleons, so they have the same Z and the same A. They differ only in energy: Tc-99m is an excited state with a measurable lifetime, and the m stands for metastable. Nuclides that differ only in energy state are isomers.")
q(T, "Is each pair of nuclides isotopes, isotones, isobars, or isomers?",
  simple="Find Z, N, and A for each nuclide, and decide which number the two nuclides share.",
  steps=["C-12 and C-14: Z = 6 for both, so isotopes. I-125 and I-131: Z = 53 for both, so isotopes.", "C-14 (Z = 6) and N-15 (Z = 7): N = 8 for both, so isotones. I-131 (N = 78) and Xe-132 (N = 78): isotones.", "C-14 and N-14: A = 14 for both, so isobars. Mo-99 and Tc-99: A = 99 for both, so isobars.", "Tc-99m and Tc-99, and Co-60m and Co-60: the same Z and A in different energy states, so isomers."], how=H_)
q(T, "A small part of the chart of the nuclides.",
  simple="On the chart of the nuclides, protons run up the vertical axis and neutrons along the horizontal axis. Isotones have the same number of neutrons, so they lie in the same vertical column.",
  steps=["C-14 has N = 8. An isotone must also have N = 8.", "In the nitrogen row (Z = 7), N = 8 means A = 15, so the nuclide is N-15.", "It sits directly above C-14 in the chart."])
q(T, "The same chart.",
  simple="Isobars have the same mass number. On the chart, A = Z + N, so isobars lie along a diagonal line.",
  steps=["C-14 has A = 14.", "In the nitrogen row (Z = 7), A = 14 means N = 7, so the nuclide is N-14.", "It lies on the diagonal through C-14 in the chart."])
# ---- 1.5
T = "decay-modes"
q(T, "Sort each radionuclide into the decay mode it mainly uses.",
  simple="The mode depends on whether the nucleus has too many neutrons or too many protons, and on how much energy is available.",
  steps=["Neutron-rich nuclides decay by β⁻. Y-90, Lu-177, I-131, and Ir-192 are made by neutron capture or fission, so they have extra neutrons.", "F-18 is proton-rich and has more than 1.022 MeV available, so it decays mainly by β⁺.", "I-125 and Pd-103 are proton-rich, but their decay energies are below 1.022 MeV (about 0.19 MeV and 0.54 MeV), so β⁺ is not possible. They decay by electron capture.", "Ra-223 is a very heavy nucleus and decays by α emission."], how=H_)
q(T, "Match each decay to what it does to the nucleus.",
  simple="The changes in Z and A follow from what leaves the nucleus or changes inside it.",
  steps=["β⁻: a neutron becomes a proton, so Z increases by 1 and A is unchanged.", "β⁺ and electron capture: a proton becomes a neutron, so Z decreases by 1 and A is unchanged.", "α: two protons and two neutrons leave, so Z decreases by 2 and A by 4."], how=H_)
q(T, "Which of these processes leave a vacancy in an inner electron shell?",
  simple="A vacancy appears when an electron is removed from an inner shell. That happens when the nucleus captures an inner electron, or when it passes its energy to an inner electron that then leaves the atom.",
  steps=["Electron capture: the nucleus takes an inner-shell electron. A vacancy remains.", "Internal conversion: an inner-shell electron is ejected with the nuclear energy. A vacancy remains.", "β⁻ decay, α decay, and γ emission do not remove an orbital electron, so they leave no vacancy."], how=H_)
# ---- 1.6
T = "decay-schemes"
q(T, "Match each process to its arrow in a decay scheme.",
  simple="Atomic number increases to the right and energy goes up the page. The direction of the arrow shows the change in Z, and its length shows the size of the change.",
  steps=["β⁻ raises Z by one: down and to the right.", "β⁺ and electron capture lower Z by one: a short arrow down and to the left.", "α lowers Z by two: a steep arrow down and to the left.", "γ emission or internal conversion does not change Z: straight down."], how=H_)
q(T, "Does each radiation have a continuous energy spectrum or discrete lines?",
  simple="A single particle or photon that carries a whole transition energy has a fixed energy and gives a line. When the energy is shared between two bodies, the spectrum is continuous.",
  steps=["β⁻ and β⁺ particles share the decay energy with a neutrino, so their spectra are continuous.", "α particles, γ-rays, conversion electrons, characteristic x-rays, and Auger electrons each come from a transition between fixed levels, so they have discrete energies."], how=H_)
q(T, "How is each nuclide produced?",
  simple="The production route depends on whether neutrons or protons are added, or whether the nuclide is a fragment of fission.",
  steps=["Co-60 and Ir-192 are made by neutron capture in a reactor: <sup>59</sup>Co(n,γ)<sup>60</sup>Co and <sup>191</sup>Ir(n,γ)<sup>192</sup>Ir.", "Cs-137 and Mo-99 are fission products of uranium, separated from spent fuel or from irradiated targets.", "F-18 is made in a cyclotron by proton bombardment: <sup>18</sup>O(p,n)<sup>18</sup>F."], how=H_)
# ---- 1.7
T = "decay-law"
q(T, "Which quantities determine the activity of a radioactive sample?",
  simple="Activity is the number of decays per second. It is the number of radioactive nuclei times the chance that each decays per second, and that chance is the decay constant.",
  steps=["A = λN.", "The number of nuclei N and the decay constant λ both enter.", "The chemical form of the source and the energy of the emitted photons do not."], how=H_)
q(T, "What fraction of the original activity remains after 5 half-lives?",
  simple="Each half-life halves the activity. Five halvings give one half five times over.",
  steps=["After 1 half-life: 1/2. After 2: 1/4. After 3: 1/8. After 4: 1/16. After 5: 1/32.", f"(½)<sup>5</sup> = 1/32 = {100 / 32:.1f}%."])
q(T, "How is the mean life of a radionuclide related to its half-life?",
  simple="The mean life is the average lifetime of a nucleus, and it is longer than the half-life, because the average includes nuclei that survive much longer than most.",
  steps=["The decay constant gives both: τ = 1/λ and T½ = ln 2 / λ = 0.693 / λ.", f"Divide: τ / T½ = 1 / 0.693 = {1 / LN2:.3f}, so τ = 1.443 × T½."])
# ---- 1.8
T = "specific-activity"
q(T, "Specific activity is defined as:",
  simple="Specific activity measures how much activity a given mass of the material provides. It is the activity divided by the mass of the radioactive material, so its unit has activity on top and mass underneath.")
q(T, "Which unit is used for specific activity?",
  simple="Specific activity is activity per mass, so its unit is an activity unit divided by a mass unit: becquerels per gram, or curies per gram.")
q(T, "Two radionuclides have the same atomic mass.",
  simple="With equal molar masses, a gram of each contains the same number of atoms. The one with the shorter half-life has the larger decay constant, so each atom is more likely to decay in any second, and the activity per gram is higher.",
  steps=["S = λ × (atoms per gram) = ln 2 × N<sub>A</sub> / (T½ × M).", "With M equal, S is proportional to 1/T½. The shorter half-life gives the higher S."])
q(T, "Why is a high specific activity valuable for an HDR brachytherapy source?",
  simple="A high specific activity means that a large activity fits in a very small mass. A small source can pass through a narrow catheter and acts nearly like a point, which makes the dose calculation simpler.",
  steps=[f"For 370 GBq of Ir-192 (S = 3.4 × 10<sup>14</sup> Bq/g), m = A / S = {370e9 / 3.4e14 * 1000:.2f} mg.", f"The same activity of Cs-137 would need about {370e9 / 3.2e12:.0f} mg, which is far too bulky for an HDR source."])
q(T, "Why is the specific activity of a real Ir-192 source lower than the theoretical value?",
  simple="The theoretical value assumes that every atom in the sample is Ir-192. A real source is made by placing stable Ir-191 in a reactor, and only a small fraction of its atoms capture a neutron. The rest stay as stable iridium. They add mass but no activity, so the activity per gram is lower.")
q(T, "Rank these nuclides by specific activity, highest first.",
  simple="Specific activity is proportional to 1/(T½ × M). A short half-life raises it far more than the molar mass lowers it, so the nuclides with the shortest half-lives come first.",
  steps=[f"Pd-103 (17.0 d, 102.9 g/mol): {sci(spec(17.0 * DAY, 102.9), 2)} Bq/g.", f"I-125 (59.4 d, 124.9 g/mol): {sci(spec(59.4 * DAY, 124.9), 2)} Bq/g.", f"Ir-192 (73.8 d, 191.96 g/mol): {sci(spec(73.8 * DAY, 191.96), 2)} Bq/g.", f"Co-60 (5.27 y, 59.93 g/mol): {sci(spec(5.27 * YR, 59.93), 2)} Bq/g.", f"Cs-137 (30.1 y, 136.9 g/mol): {sci(spec(30.1 * YR, 136.9), 2)} Bq/g.", f"Ra-226 (1600 y, 226.03 g/mol): {sci(spec(1600 * YR, 226.03), 2)} Bq/g."], how=H_)
# ---- 1.9
T = "equilibrium"
q(T, "Which condition gives secular equilibrium?",
  simple="Secular equilibrium needs a parent that lives far longer than its daughter. The parent then hardly changes while the daughter builds up, and the daughter ends up decaying as fast as it is fed.")
q(T, "In secular equilibrium, the activity of the daughter is:",
  simple="At equilibrium the daughter decays as fast as the parent feeds it, and the parent activity is nearly constant. The daughter activity therefore equals the parent activity.")
# ---- 1.10
T = "photon-interactions"
q(T, "Which of these is indirectly ionizing radiation?",
  simple="Charged particles ionize directly as they move through matter. Photons and neutrons are uncharged, so they first transfer energy to charged particles, and those charged particles then ionize.")
q(T, "The attenuation of a narrow beam of monoenergetic photons",
  simple="Every thin layer of the absorber removes the same fraction of the photons that reach it. A constant fraction removed per layer is an exponential fall with thickness.",
  steps=["After a layer of thickness x, the fraction that is left is e<sup>−μx</sup>.", "So I = I₀ e<sup>−μx</sup>, where μ is the linear attenuation coefficient."])
q(T, "In water, which interaction dominates for photons from about 30 keV to 24 MeV?",
  simple="The photoelectric effect dominates below about 30 keV and pair production above about 24 MeV. Between them, which includes every therapy beam, Compton scattering is the main interaction.")
q(T, "What is the threshold photon energy for pair production in the field of a nucleus?",
  simple="Pair production turns a photon's energy into the mass of an electron and a positron. Each has a rest energy of 0.511 MeV, so the photon must carry at least 1.022 MeV.",
  steps=["2 × 0.511 = 1.022 MeV.", "In the field of an electron (triplet production), the threshold is 2.044 MeV, because the struck electron also takes up recoil energy."])
q(T, "Which of the following are true of Compton scattering?",
  simple="Compton scattering is an interaction with loosely bound electrons. Three statements are true of it, and the other two belong to different interactions.",
  steps=["True: the electron receives the most energy when the photon is scattered straight back (180°).", "True: the scattered photon at 90° has energy E / (1 + E/0.511), which approaches 0.511 MeV for very high E and never exceeds it.", "True: it involves loosely bound electrons, so per electron it does not depend on Z.", "Not Compton: a characteristic x-ray follows the photoelectric effect, and a threshold of 1.022 MeV belongs to pair production."], how=H_)
q(T, "Is each radiation directly or indirectly ionizing?",
  simple="Charged particles ionize directly along their tracks. Uncharged radiation has to transfer energy to a charged particle first.",
  steps=["Electrons, protons, and α particles are charged: directly ionizing.", "Photons and neutrons are uncharged: indirectly ionizing."], how=H_)
q(T, "Which interaction does each statement describe?",
  simple="Each statement points to one interaction through what it depends on or what it produces.",
  steps=["Photoelectric effect: proportional to Z<sup>3</sup>/E<sup>3</sup>; followed by a characteristic x-ray or Auger electron; gives bone contrast at kilovoltage energies.", "Compton scattering: per electron independent of Z; dominates in water from about 30 keV to 24 MeV; the electron gets the most energy when the photon backscatters.", "Pair production: needs at least 1.022 MeV; ends with two 511 keV photons from the annihilation of the positron."], how=H_)
q(T, "Water, photon energy on a logarithmic axis.",
  simple="On a logarithmic axis equal distances are equal ratios. The Compton region in water runs from about 30 keV to about 24 MeV, which covers most of the middle of the axis.",
  steps=["Find 30 keV and 24 MeV on the axis.", "Tap anywhere between them. For example, 1 MeV is inside the range."])
q(T, "Photon energy on a logarithmic axis.",
  simple="The threshold is the smallest photon energy that can make a pair, and it is the sum of the rest energies of the electron and the positron.",
  steps=["2 × 0.511 MeV = 1.022 MeV.", "On a logarithmic axis, 1.022 MeV lies slightly above 1 MeV."])


# ================================================================ Basic physics: questions added after the audit against the study guide
T = "waves-photons"
q(T, "Is each wave transverse or longitudinal?",
  simple="The two kinds differ in how the oscillation lies compared with the direction in which the wave travels. In a transverse wave the oscillation is sideways to the direction of travel. In a longitudinal wave it is along the direction of travel, as in a compression that runs along a spring.",
  steps=["Light, x-rays, and other electromagnetic waves: the electric and magnetic fields oscillate perpendicular to the direction of travel, so they are transverse.", "A wave on a stretched string: the string moves up and down while the wave runs along it, so it is transverse.", "Sound in air, ultrasound in tissue, and a compression pulse along a spring: the particles of the medium move back and forth along the direction of travel, so they are longitudinal."], how=H_)
T = "particles-energy"
q(T, "Which statement about a photon is correct?",
  simple="A photon has no mass at rest, and it never is at rest. It still carries energy and momentum, which follow from its frequency. Dividing its energy by c² gives the mass that would be equivalent to that energy, but this is not a rest mass.",
  steps=["Rest mass: zero, as the table of rest energies shows.", "Energy E = hν, and momentum p = E/c.", "Mass equivalent of the energy: E/c². A 1.022 MeV photon has the energy of two electron rest masses, which is why it can create a pair, yet the photon itself has no rest mass."], tip="Having no rest mass does not mean having no energy or no momentum.", how=H_)
q(T, "In an elastic collision between two particles:",
  simple="Elastic means that nothing is converted to another form of energy: the kinetic energy after the collision equals the kinetic energy before it. Momentum is conserved in every collision between particles that are not acted on from outside, elastic or not.",
  steps=["Elastic: the total kinetic energy and the total momentum are both unchanged.", "Inelastic: the total momentum is unchanged, but part of the kinetic energy goes to excitation, radiation, or rest mass."], how=H_)
q(T, "Is each collision elastic or inelastic?",
  simple="The test is whether any kinetic energy goes to another purpose. If none does, the collision is elastic.",
  steps=["Elastic: a neutron bouncing off a hydrogen nucleus, an α particle deflected by a gold nucleus that stays in its ground state, and two protons deflected by their Coulomb repulsion without radiation. The particles only exchange kinetic energy.", "Inelastic: an electron that excites an atom, a photon that creates a pair, and an electron that emits bremsstrahlung. In each, kinetic energy goes into excitation, rest mass, or a photon."], how=H_)
T = "charges-atom"
q(T, "Which of these is a unit of electric field?",
  simple="The electric field is the force on a unit charge, so newtons per coulomb is a unit of field. The same field can be written as the change of potential per unit length, which gives volts per metre. The two are the same unit.",
  steps=["E = F/q, so the unit is N/C.", "E = ΔV/d, so the unit is V/m.", "Joule per coulomb is the volt, coulomb per volt is the farad, and ampere second is the coulomb. None of these is a field."], how=H_)
q(T, "An electron crosses a gap of 2.5 cm along a uniform electric field",
  simple="A charge gains energy equal to its charge times the potential difference that it crosses. In a uniform field the potential difference across a gap is the field times the length of the gap. An electron carries one elementary charge, so a potential difference in volts gives an energy in electron-volts.",
  steps=["Write the length in metres: 2.5 cm = 0.025 m.", "ΔV = E d = 8.0 × 10<sup>6</sup> V/m × 0.025 m = 2.0 × 10<sup>5</sup> V.", "Energy gained = eΔV = 2.0 × 10<sup>5</sup> eV = 200 keV."],
  tip="Centimetres have to be converted to metres before the length is multiplied by a field in volts per metre.", check=8.0e6 * 0.025 / 1e3)
q(T, "Which statement about electric current is correct?",
  simple="Current is a flow of charge. Its direction was fixed by convention, before electrons were known, as the direction in which positive charge would move. Electrons are negative, so in a wire they move the opposite way.",
  steps=["Conventional current points from the positive terminal toward the negative terminal.", "In a metal wire the electrons move from the negative terminal toward the positive one, opposite to the conventional current.", "Direct current keeps one direction, and alternating current reverses periodically. The unit of current is the ampere, one coulomb per second."], how=H_)
q(T, "The current through a resistor and the potential difference across it are to be measured.",
  simple="The two instruments measure different things in different ways. Current is the flow through the component, so the meter has to sit in the path of that flow. Potential difference compares two points, so the meter is connected across them.",
  steps=["Ammeter: in series, so that all of the current passes through it. Its resistance is very small, so it hardly changes the current.", "Voltmeter: in parallel, across the component. Its resistance is very large, so it draws almost no current."], how=H_)
q(T, "In the accelerating waveguide of a linac, the electrons gain energy from:",
  simple="An electron gains energy when it crosses a potential difference. A constant voltage of several million volts across the whole structure would be hard to build, so the linac uses an alternating field at microwave frequency and times the electrons so that the field points forward whenever they are in a gap. Each gap adds a little energy, and the sum along the structure is the final energy.",
  steps=["Microwaves at about 3 GHz set up an electric field along the waveguide.", "The gun injects bunches so that the field points forward when the electrons are in the accelerating gaps.", "Each gap adds qΔV. A magnetic field only bends the path, because the magnetic force does no work."], how=H_)
q(T, "The SI unit of magnetic field is the tesla.",
  simple="The tesla is the large unit and the gauss the small one. One tesla is ten thousand gauss, so a field of 1.5 T is 15,000 G, and the Earth's field is about half a gauss.",
  steps=["1 G = 10<sup>−4</sup> T, so 1 T = 10<sup>4</sup> G.", "1.5 T × 10<sup>4</sup> G/T = 15,000 G.", "The Earth's field, about 0.5 G, is 0.5 × 10<sup>−4</sup> T = 0.05 mT."])
q(T, "Electrons of 50 keV strike a tungsten target.",
  simple="A characteristic x-ray needs a vacancy in an inner shell, and an incoming electron can make a vacancy only if its energy is at least the binding energy of that shell. The K shell is bound most tightly, so it needs the most energy.",
  steps=["Compare 50 keV with each binding energy: 69.5 keV for the K shell and 10.2 keV for the L<sub>III</sub> shell.", "50 keV is below 69.5 keV, so no K vacancy is made and the K-series lines are not produced.", "50 keV is above 10.2 keV, so L vacancies are made and the L-series lines are produced."],
  tip="The energy of the x-ray photon is a difference between two shells and is always smaller than the energy needed to make the vacancy.", how=H_)
T = "nuclear-structure"
q(T, "Which list orders the four fundamental forces from the strongest to the weakest?",
  simple="The strong force holds the nucleons together against the repulsion between the protons, so it is the strongest. The electromagnetic force comes next. The weak force acts in beta decay and is weaker than electromagnetism. Gravity is far weaker than all of them.",
  steps=["Strong: binds nucleons, over about 1 to 3 fm.", "Electromagnetic: acts between charges, over long range.", "Weak: acts in beta decay, over a very short range.", "Gravitational: far weaker than the other three."], how=H_)
q(T, "Which nucleus is especially stable because both its proton number and its neutron number are magic numbers?",
  simple="Protons and neutrons fill shells in the nucleus, in the way that electrons fill shells in an atom. A shell is closed at the magic numbers 2, 8, 20, 28, 50, 82, and 126, and a nucleus with closed shells is held more tightly than its neighbours.",
  steps=["Pb-208: 82 protons and 208 − 82 = 126 neutrons. Both are magic.", "Co-60: 27 protons and 33 neutrons. Neither is magic.", "Ir-192: 77 protons and 115 neutrons. Neither is magic.", "I-131: 53 protons and 78 neutrons. Neither is magic."], how=H_)
T = "decay-law"
q(T, "Source X has an activity of 9.0 mCi and a half-life of 12 d.",
  simple="Each source follows its own exponential, and the two curves cross when the activities are equal. The time of the crossing comes from setting the two expressions equal and solving for t.",
  steps=["λ<sub>X</sub> = 0.693 / 12 = 0.05776 d<sup>−1</sup> and λ<sub>Y</sub> = 0.693 / 40 = 0.01733 d<sup>−1</sup>.", "9.0 e<sup>−λ<sub>X</sub>t</sup> = 2.5 e<sup>−λ<sub>Y</sub>t</sup>.", "Divide both sides by 2.5 and by e<sup>−λ<sub>Y</sub>t</sup>: 3.6 e<sup>−(λ<sub>X</sub> − λ<sub>Y</sub>)t</sup> = 1.", "Take logarithms: t = ln 3.6 / (λ<sub>X</sub> − λ<sub>Y</sub>) = 1.281 / 0.04043 = 31.7 d."],
  tip="Source X falls to 2.5 mCi after 22.2 d only if source Y did not decay, but Y decays too.", check=math.log(3.6) / (LN2 / 12 - LN2 / 40))
q(T, "A radionuclide has a half-life of 10 days.",
  simple="Radioactive decay has no memory. Each nucleus has the same chance of decaying in any interval, whatever its age, and the decay constant is that chance per unit time. A nucleus that has lasted 30 days is as likely to decay in the next 10 days as a new one.",
  steps=["The probability that a nucleus decays within one half-life is 1 − ½ = 50%.", "The history of the nucleus does not change this, so the probability for the next 10 days is again 50%."],
  tip="The activity of a sample is low after three half-lives because few nuclei are left, not because the survivors are less likely to decay.", how=H_)
T = "photon-interactions"
q(T, "A radiograph is made at 100 kVp, with an effective photon energy of about 50 keV.",
  simple="Two questions are mixed here: which interaction happens most often, and which interaction makes the picture. Compton scattering happens most often in soft tissue at this energy. The photoelectric effect depends strongly on the atomic number, so it makes the difference between bone and soft tissue, and that difference is the contrast.",
  steps=["Frequency: in water at 50 keV Compton scattering is roughly 80% of the attenuation, and the photoelectric effect and coherent scattering share the rest.", "Contrast: per gram, bone attenuates about 1.9 times as much as water at 50 keV, but only about 1.1 times as much at 100 keV. The extra comes from the photoelectric effect, which varies as Z<sup>3</sup>.", "Electrons per gram differ little between bone and soft tissue, so Compton scattering gives little contrast.", "Pair production needs a photon of more than 1.022 MeV, so it does not occur at 50 keV."], how=H_)
q(T, "A lead barrier must reduce a beam to 1.0% of the unshielded intensity.",
  simple="The build-up factor says that scattered photons add to the transmitted beam, so the barrier has to remove more of the primary beam than the narrow-beam calculation suggests. Dividing the required transmission by the build-up factor gives the attenuation that the exponential has to supply.",
  steps=["The transmission is B e<sup>−μx</sup> = 0.010, so e<sup>−μx</sup> = 0.010 / 2.0 = 0.0050.", "The number of half-value layers is log<sub>2</sub>(1 / 0.0050) = log<sub>2</sub>(200) = 7.64.", "Thickness = 7.64 × 0.80 cm = 6.1 cm."],
  tip="The narrow-beam answer is 6.64 half-value layers, or 5.3 cm. A broad beam always needs more.", check=0.80 * math.log2(200))
q(T, "In a narrow-beam measurement of attenuation, the small detector behind the absorber registers:",
  simple="The geometry is chosen so that a photon that scatters in the absorber is not counted. The beam is collimated and the detector is small and far from the absorber, so only photons that crossed it without interacting arrive. That is the case in which the simple exponential law holds.",
  steps=["Narrow beam: collimated, with a small distant detector, so scatter is not registered and I = I₀ e<sup>−μx</sup>.", "Broad beam: the scattered photons also arrive, so the reading is larger by the build-up factor B."], how=H_)
