from blocks import *
import math

# ---------------------------------------------------------------- NCRP 151 barrier equations. P in Sv/week, W in Gy/week at 1 m from the target, d in m, F in cm², thicknesses in cm.
def b_pri(P, W, U, T, d):
    """Transmission a primary barrier must give: B = P d² / (W U T)."""
    return P * d ** 2 / (W * U * T)

def b_sca(P, W, T, a, d_sca, d_sec, F=400.0):
    """Transmission for patient scatter: B = P d_sca² d_sec² / (a W T) × 400/F, with a the scatter fraction at 1 m for a 400 cm² field."""
    return P * d_sca ** 2 * d_sec ** 2 / (a * W * T) * 400.0 / F

def b_leak(P, W, T, d, CI=1.0):
    """Transmission for head leakage, 0.1% of the useful beam at 1 m, with the IMRT factor raising the leakage workload: B = 1000 P d² / (W C_I T)."""
    return 1000.0 * P * d ** 2 / (W * CI * T)

def n_tvl(B):
    """Number of tenth-value layers that give transmission B."""
    return math.log10(1.0 / B)

def thick(B, tvl1, tvle):
    """Thickness for transmission B: TVL1 + (n − 1) TVLe, or n TVL1 when less than one TVL is needed."""
    n = n_tvl(B)
    return tvl1 + (n - 1.0) * tvle if n >= 1.0 else n * tvl1

def trans(t, tvl1, tvle):
    """Transmission of a thickness t."""
    return 10 ** -(1.0 + (t - tvl1) / tvle) if t >= tvl1 else 10 ** -(t / tvl1)

# ---------------------------------------------------------------- constants quoted in the text (NCRP 151)
WEEKS = 50
P_C, P_U = 5e-3 / WEEKS, 1e-3 / WEEKS          # Sv/week from 5 mSv and 1 mSv a year
PRI6, PRI10, PRI18 = (37.0, 33.0), (41.0, 37.0), (45.0, 43.0)   # primary TVL1, TVLe in ordinary concrete (cm)
LEAK6 = (34.0, 29.0)                           # leakage at 90°, concrete, 6 MV
SCA6 = 17.0                                    # patient scatter at 90°, concrete, 6 MV (one TVL)
A6, A18 = 4.26e-4, 1.89e-4                     # scatter fraction at 90°, 400 cm² field
LOG2 = math.log10(2.0)

# ---------------------------------------------------------------- worked examples
W1 = 30 * 5 * 3.0                               # 30 patients a day, 5 days, 3 Gy at 1 m each: Gy/week
d1 = 6.0
B1 = b_pri(P_U, W1, 0.25, 1.0, d1); n1 = n_tvl(B1); t1 = thick(B1, *PRI6)
t2 = 200.0; n2 = 1.0 + (t2 - PRI6[0]) / PRI6[1]; B2 = trans(t2, *PRI6)
H2 = W1 * 0.25 * B2 / d1 ** 2; H2T = H2 * 0.2  # Sv/week at the point, and for a person with T = 1/5
B4 = b_pri(P_U, 2 * W1, 0.25, 0.2, d1); t4 = thick(B4, *PRI6)
dW = LOG2 * PRI6[1]; dT = math.log10(5.0) * PRI6[1]
d3, CI3 = 5.0, 5.0
Bs3 = b_sca(P_C, W1, 1.0, A6, 1.0, d3); ns3 = n_tvl(Bs3); ts3 = ns3 * SCA6
BL3 = b_leak(P_C, W1, 1.0, d3, CI3); nL3 = n_tvl(BL3); tL3 = thick(BL3, *LEAK6)
BL3c = b_leak(P_C, W1, 1.0, d3, 1.0); tL3c = thick(BL3c, *LEAK6)
DIAG = 0.40 * math.sqrt(2.0)                    # m: diagonal of a 40 × 40 cm field at 1 m
d_w = 7.0; width = DIAG * d_w + 2 * 0.3
us = lambda v: f"{v * 1e6:.1f}"                 # Sv to µSv for the text
mus = lambda v: f"{v * 1e3:g}"                  # Sv to mSv

TOPIC = dict(
    id="shielding", domain=7, sub="VII.B", title="Shielding design for linac vaults",
    ref=dict(aapm="", khan="", ford="25"),
    guide=[
        H("Design goals and workload"),
        P("A vault is shielded so that the weekly dose equivalent at any occupied point outside stays within a shielding design goal, P. NCRP Report 151 derives P from annual goals for controlled areas, open only to trained staff, and for uncontrolled areas, open to anyone. For photons 1 Gy corresponds to 1 Sv, so P and doses in grays combine directly."),
        EQ(f"controlled: P = 5 mSv / {WEEKS} weeks = {mus(P_C)} mSv per week", f"uncontrolled: P = 1 mSv / {WEEKS} weeks = {mus(P_U)} mSv per week"),
        UL(f"<b>W</b>, the workload: the absorbed dose per week at 1 m from the target (Gy/week), counted as patients per week × dose per patient, summed over all fields: 30 patients a day, 5 days a week, at 3 Gy each give {W1:.0f} Gy/week. Field directions enter through U.",
           "<b>U</b>, the use factor: the fraction of the workload for which the primary beam points at the barrier, often 0.25 for each wall, floor, or ceiling it can strike, and 1 for leakage and scatter, which reach every barrier at every angle.",
           "<b>T</b>, the occupancy factor: the fraction of the beam-on time that the most exposed person spends at the protected point.",
           "<b>d</b>, the distance in metres (W being defined at 1 m) from the target to the protected point, 0.3 m beyond the outer face of the barrier.",
           "<b>C<sub>I</sub></b>, the IMRT factor: the monitor units per unit dose with IMRT over those without, about 2 to 10; with mixed treatments it multiplies only the IMRT part of W."),
        TABLE(["T", "Areas beyond the barrier (NCRP 151)"], [
            ["1", "Offices, treatment planning areas, the treatment control area, nurse stations, reception and attended waiting areas"],
            ["1/2", "An adjacent treatment room or examination room"],
            ["1/5", "Corridors, staff lounges, staff rest rooms"],
            ["1/8", "Treatment room doors"],
            ["1/20", "Public toilets, storage rooms, unattended waiting rooms, outdoor areas with seating"],
            ["1/40", "Stairways, unattended elevators and parking lots, outdoor areas with only passing traffic"]]),

        H("Primary barriers"),
        P("A primary barrier is any wall, floor, or ceiling that the useful beam can strike. Behind it the weekly dose is W U B / d², where B, the transmission, is the fraction of the dose the barrier lets through; setting T times this equal to P fixes B, the number of tenth-value layers n, and the thickness t."),
        EQ("B = P d² / (W U T)", "n = log<sub>10</sub>(1/B)", "t = TVL<sub>1</sub> + (n − 1) TVL<sub>e</sub>"),
        P("In concrete the first tenth-value layer, TVL<sub>1</sub>, exceeds the equilibrium TVL<sub>e</sub> of later layers, because the spectrum and scatter settle only after the first layer. A TVL follows the attenuation coefficient. In concrete, Compton scattering dominates and falls with energy, so the TVL grows from 6 to 18 MV; in lead, rising pair production offsets the fall and the TVL stays near 5.7 cm. Ordinary concrete is 2.35 g/cm³; denser concrete, steel, and lead save space."),
        TABLE(["Primary beam", "Concrete TVL<sub>1</sub> (cm)", "Concrete TVL<sub>e</sub> (cm)", "Lead TVL (cm)"], [
            ["6 MV", f"{PRI6[0]:.0f}", f"{PRI6[1]:.0f}", "5.7"], ["10 MV", f"{PRI10[0]:.0f}", f"{PRI10[1]:.0f}", "5.7"], ["18 MV", f"{PRI18[0]:.0f}", f"{PRI18[1]:.0f}", "5.7"]]),
        P(f"The barrier width covers the diagonal of the largest field, 40 × 40 cm turned 45° by the collimator ({DIAG:.2f} m at 1 m), projected from the target to the far face of the barrier, with 0.3 m added on each side. A beam crossing at an angle θ from the normal traverses the slant thickness t / cos θ; at large angles this overstates the attenuation, because scattered photons take shorter paths out, so the dose beyond the wall can be underestimated."),
        EQ(f"width = {DIAG:.2f} m × d<sub>far</sub> + 2 × 0.3 m   (d<sub>far</sub> in m; {width:.1f} m at d<sub>far</sub> = {d_w:.1f} m)", "t<sub>slant</sub> = t / cos θ"),
        P(f"Each factor of 10 in W U T / (P d²) changes the thickness by one TVL<sub>e</sub>, and each factor of 2 by one HVL, {LOG2:.2f} TVL<sub>e</sub>."),
        EX("Primary barrier thickness", STEM("A 6 MV vault. The primary beam can strike a wall with an office (uncontrolled) behind it.",
                                             [f"P = {mus(P_U)} mSv/week = 2 × 10<sup>−5</sup> Sv/week", f"W = {W1:.0f} Gy/week", "U = 0.25", "T = 1", f"d = {d1:.1f} m, target to 0.3 m beyond the wall", f"ordinary concrete: TVL<sub>1</sub> = {PRI6[0]:.0f} cm, TVL<sub>e</sub> = {PRI6[1]:.0f} cm"],
                                             "Find the [[concrete thickness]]."),
           [f"B = P d² / (W U T) = 2 × 10<sup>−5</sup> × {d1:.1f}² / ({W1:.0f} × 0.25 × 1) = {sci(B1, 3)}", f"n = log<sub>10</sub>(1/B) = {n1:.2f}", f"t = {PRI6[0]:.0f} + ({n1:.2f} − 1) × {PRI6[1]:.0f} = {t1:.1f} cm"],
           f"{t1:.0f} cm of ordinary concrete."),
        EX("Dose beyond an existing wall", STEM("An existing 6 MV primary wall of ordinary concrete has a corridor (uncontrolled) behind it.",
                                                [f"t = {t2:.0f} cm, TVL<sub>1</sub> = {PRI6[0]:.0f} cm, TVL<sub>e</sub> = {PRI6[1]:.0f} cm", f"W = {W1:.0f} Gy/week", "U = 0.25", "T = 1/5", f"d = {d1:.1f} m"],
                                                "Find the [[transmission B]] and the [[weekly dose equivalent]] at the protected point."),
           [f"n = 1 + ({t2:.0f} − {PRI6[0]:.0f}) / {PRI6[1]:.0f} = {n2:.2f}, so B = 10<sup>−{n2:.2f}</sup> = {sci(B2, 3)}", f"Dose at the point = W U B / d² = {W1:.0f} × 0.25 × {sci(B2, 3)} / {d1:.1f}² = {us(H2)} µSv per week",
            f"Most exposed person: T × {us(H2)} = {H2T * 1e6:.2f} µSv per week, against P = {P_U * 1e6:.0f} µSv per week"],
           f"B = {sci(B2, 3)}, {us(H2)} µSv per week at the point, and {H2T * 1e6:.2f} µSv per week for the most exposed person, well within the goal."),
        EX("Doubled workload, new occupancy", STEM(f"A 6 MV primary wall of ordinary concrete was sized at {t1:.1f} cm for W = {W1:.0f} Gy/week with an office (T = 1) behind it.",
                                                    [f"new workload = {2 * W1:.0f} Gy/week", "new occupancy: corridor, T = 1/5", f"TVL<sub>e</sub> = {PRI6[1]:.0f} cm"], "Find the [[new thickness]]."),
           [f"Doubling W halves B, so n rises by log<sub>10</sub> 2 = {LOG2:.3f}, adding {LOG2:.3f} × {PRI6[1]:.0f} = {dW:.1f} cm", f"T falling to 1/5 multiplies B by 5, so n falls by log<sub>10</sub> 5 = {math.log10(5):.3f}, removing {math.log10(5):.3f} × {PRI6[1]:.0f} = {dT:.1f} cm",
            f"t = {t1:.1f} + {dW:.1f} − {dT:.1f} = {t4:.1f} cm"],
           f"{t4:.0f} cm. A factor of 10 in either quantity would change the wall by one TVL<sub>e</sub>, {PRI6[1]:.0f} cm."),

        H("Secondary barriers"),
        P("A secondary barrier is reached only by patient scatter and head leakage, each with its own equation and TVLs."),
        EQ("B<sub>s</sub> = P d<sub>sca</sub>² d<sub>sec</sub>² / (a W T) × (400 / F)", "B<sub>L</sub> = 1000 P d<sub>L</sub>² / (W C<sub>I</sub> T)"),
        UL("d<sub>sca</sub>: target to patient, usually 1 m; d<sub>sec</sub>: patient (isocenter) to the protected point; d<sub>L</sub>: isocenter to the protected point, accepted by NCRP 151 when the gantry angles are used about equally (otherwise the closest approach of the head); all in metres.",
           f"a, the scatter fraction: the dose 1 m from the patient over the dose at the isocenter, for a 400 cm² field; larger at forward angles (at 90°, {sci(A6, 3)} for 6 MV and {sci(A18, 3)} for 18 MV, NCRP 151). F: the field area at the patient (cm²).",
           "1000 = 1/0.001: head leakage is limited to 0.1% of the useful beam at 1 m.",
           "C<sub>I</sub> enters only the leakage term: IMRT needs more monitor units for the same patient dose, and leakage follows the monitor units."),
        P(f"Leakage and scatter penetrate less than the primary beam. At 6 MV the leakage TVLs of concrete are {LEAK6[0]:.0f} cm (first) and {LEAK6[1]:.0f} cm (later), and patient scatter at 90° has one TVL of {SCA6:.0f} cm, since a photon scattered through 90° keeps at most 511 keV. At large scatter angles leakage sets the thickness."),
        P("If the two thicknesses differ by at least one TVL the larger is used; otherwise one HVL (0.30 TVL<sub>e</sub> of the component that sets the larger thickness) is added to the larger, since two components each reaching P alone would together give up to 2P."),
        EX("Secondary wall at 90°", STEM("A 6 MV vault in which every patient is treated with IMRT. A side wall with a staff work area (controlled) behind it is reached only by patient scatter at 90° and by head leakage.",
                                          [f"P = {mus(P_C)} mSv/week = 10<sup>−4</sup> Sv/week", f"W = {W1:.0f} Gy/week", f"C<sub>I</sub> = {CI3:.0f}", "T = 1", "d<sub>sca</sub> = 1.0 m", f"d<sub>sec</sub> = d<sub>L</sub> = {d3:.1f} m", f"a(90°) = {sci(A6, 3)}", "F = 400 cm²",
                                           f"concrete TVLs: scatter {SCA6:.0f} cm; leakage TVL<sub>1</sub> = {LEAK6[0]:.0f} cm, TVL<sub>e</sub> = {LEAK6[1]:.0f} cm"],
                                          "Find the [[concrete thickness]]."),
           [f"Scatter: B<sub>s</sub> = 10<sup>−4</sup> × 1.0² × {d3:.1f}² / ({sci(A6, 3)} × {W1:.0f} × 1) × 400/400 = {sci(Bs3, 3)}, n = {ns3:.2f}, t = {ns3:.2f} × {SCA6:.0f} = {ts3:.1f} cm",
            f"Leakage: B<sub>L</sub> = 1000 × 10<sup>−4</sup> × {d3:.1f}² / ({W1:.0f} × {CI3:.0f} × 1) = {sci(BL3, 3)}, n = {nL3:.2f}, t = {LEAK6[0]:.0f} + ({nL3:.2f} − 1) × {LEAK6[1]:.0f} = {tL3:.1f} cm",
            f"The two differ by {tL3 - ts3:.1f} cm, more than one TVL, so the leakage thickness is used",
            f"With C<sub>I</sub> = 1 leakage would need {tL3c:.1f} cm; the IMRT factor adds log<sub>10</sub> {CI3:.0f} × {LEAK6[1]:.0f} = {tL3 - tL3c:.1f} cm"],
           f"{tL3:.0f} cm, set by leakage."),

        H("Neutrons and doors"),
        P("Above about 10 MV, photons striking the heavy metals of the head (target, collimators, flattening filter) release photoneutrons through (γ,n) reactions, with thresholds of about 6 to 8 MeV in tungsten and lead and 10 to 11 MeV in copper and iron. A 6 MV beam has almost no photons above these thresholds, so its vault needs no neutron shielding. Concrete thick enough for the photons of a high-energy beam is generally enough for its neutrons, which the hydrogen in its water slows; a barrier of lead or steel is not, and needs hydrogen-rich material added."),
        P("Neutrons slow as they scatter along the maze, reaching the door mostly as epithermal and thermal neutrons, and their capture in the walls makes gamma rays averaging about 3.6 MeV. An 18 MV door therefore holds borated polyethylene, whose hydrogen slows the neutrons and whose boron captures them with a 0.48 MeV gamma ray instead of the 2.2 MeV ray from hydrogen, and lead for the capture gamma rays (TVL about 6.1 cm)."),
        P("The maze keeps that door light: photons reach it only after scattering off the walls or through the inner maze wall, and, beyond the inner maze entrance, the neutron dose falls about tenfold for each 5 m along the maze (Kersey's tenth-value distance, which overestimates the door dose; the Wu–McGinley method in NCRP 151 uses 2.06 √S m, S being the maze cross-section in m<sup>2</sup>). Without a maze the door must attenuate as much as the wall around it."),
    ],
    cards=[
        F("Shielding design goals", f"P = {mus(P_C)} mSv per week for controlled areas and {mus(P_U)} mSv per week for uncontrolled areas (NCRP 151), from 5 mSv and 1 mSv a year over {WEEKS} weeks."),
        F("Workload", "The absorbed dose per week at 1 m from the target: patients per week × dose per patient, the dose summed over all the fields."),
        F("Use factor", "The fraction of the workload for which the primary beam points at a barrier: often 0.25 for each wall, the floor, and the ceiling that the beam can strike, and 1 for secondary barriers."),
        F("Occupancy factor", "The fraction of the beam-on time that the most exposed person spends beyond the barrier: 1 for offices, 1/5 for corridors, 1/8 for treatment room doors, 1/20 for toilets and storage, 1/40 for stairways."),
        F("Distance to the protected point", "From the target to a point 0.3 m beyond the outer face of the barrier, in metres."),
        F("Primary barrier calculation", "B = P d² / (W U T), n = log<sub>10</sub>(1/B), and t = TVL<sub>1</sub> + (n − 1) TVL<sub>e</sub>."),
        F("Concrete TVLs for a primary beam", f"Ordinary concrete, 2.35 g/cm³: TVL<sub>1</sub> {PRI6[0]:.0f} cm and TVL<sub>e</sub> {PRI6[1]:.0f} cm at 6 MV; {PRI18[0]:.0f} and {PRI18[1]:.0f} cm at 18 MV (NCRP 151)."),
        F("Effect of a factor of 10 or 2", f"A factor of 10 in W U T / (P d²) changes the barrier by one TVL<sub>e</sub>; a factor of 2 by one HVL, about {dW:.0f} cm of concrete at 6 MV.",
          w=[f"log<sub>10</sub> 2 = {LOG2:.3f}", f"{LOG2:.3f} × {PRI6[1]:.0f} cm = {dW:.1f} cm"]),
        F("Primary barrier width", "The diagonal of the largest field (40 × 40 cm turned 45°) projected from the target to the far face of the barrier, plus 0.3 m on each side."),
        F("Slant thickness", "A beam crossing a barrier at an angle θ from its normal traverses t / cos θ."),
        F("Patient-scatter barrier", "B<sub>s</sub> = P d<sub>sca</sub>² d<sub>sec</sub>² / (a W T) × 400/F, with a the scatter fraction at 1 m for a 400 cm² field, which depends on energy and angle."),
        F("Leakage barrier and the IMRT factor", "B<sub>L</sub> = 1000 P d<sub>L</sub>² / (W C<sub>I</sub> T). Leakage is 0.1% of the useful beam at 1 m, and C<sub>I</sub> raises only the leakage workload."),
        F("Secondary TVLs at 6 MV", f"Concrete: leakage TVL<sub>1</sub> {LEAK6[0]:.0f} cm and TVL<sub>e</sub> {LEAK6[1]:.0f} cm; patient scatter at 90°, {SCA6:.0f} cm. Both are below the primary values."),
        F("Two components within one TVL", "If the leakage and scatter thicknesses differ by less than one TVL, one HVL is added to the larger; otherwise the larger is used."),
        F("Photoneutron production", "(γ,n) reactions in the tungsten and lead of the head, with thresholds of about 6 to 8 MeV: a concern above 10 MV and negligible at 6 MV."),
        F("Maze door above 10 MV", "Borated polyethylene slows and captures the neutrons; lead stops the capture gamma rays, whose mean energy is about 3.6 MeV."),
    ],
)

# ---------------------------------------------------------------- practice questions
q_goal = 1.0 / WEEKS                                      # mSv/week
q_W = 30 * 5 * 3.0
qB = b_pri(P_C, 500.0, 0.25, 1.0, 5.5)
qB_noU, qB_d, qB_year = b_pri(P_C, 500.0, 1.0, 1.0, 5.5), P_C * 5.5 / (500.0 * 0.25), b_pri(5e-3, 500.0, 0.25, 1.0, 5.5)
qL = thick(b_leak(P_U, 400.0, 1.0, 6.0, 4.0), *LEAK6)
qL_noCI, qL_pri, qL_no1000 = thick(b_leak(P_U, 400.0, 1.0, 6.0, 1.0), *LEAK6), thick(b_leak(P_U, 400.0, 1.0, 6.0, 4.0), *PRI6), thick(b_leak(P_U, 400.0, 1.0, 6.0, 4.0) / 1000.0, *LEAK6)
q_hvl = 80.0 + LOG2 * LEAK6[1]
dA = n_tvl(b_pri(P_U, 450.0, 0.25, 1.0, 7.0)) - n_tvl(b_pri(P_U, 450.0, 0.25, 0.2, 4.0))     # extra TVLs that wall A needs over wall B
q_two, q_two_T, q_two_d = dA * PRI6[1], math.log10(5.0) * PRI6[1], math.log10(49.0 / 16.0) * PRI6[1]
q_ln2 = math.log(2.0) * PRI6[1]
q_slant = 150.0 / math.cos(math.radians(30.0))
q_t18 = thick(b_pri(P_U, 500.0, 0.25, 0.2, 7.0), *PRI18); q_B18 = b_pri(P_U, 500.0, 0.25, 0.2, 7.0)
RANK = [("Primary wall, office behind it, d = 6.0 m", thick(b_pri(P_U, W1, 0.25, 1.0, 6.0), *PRI6)),
        ("Primary ceiling under a roof with T = 1/40, d = 6.0 m", thick(b_pri(P_U, W1, 0.25, 1 / 40, 6.0), *PRI6)),
        ("Secondary wall for leakage, office behind it, d<sub>L</sub> = 6.0 m", thick(b_leak(P_U, W1, 1.0, 6.0), *LEAK6)),
        ("Secondary wall for patient scatter at 90°, office behind it, d<sub>sec</sub> = 6.0 m", n_tvl(b_sca(P_U, W1, 1.0, A6, 1.0, 6.0)) * SCA6)]
assert [x[1] for x in RANK] == sorted((x[1] for x in RANK), reverse=True)

PROBLEMS = [
    PRN(STEM("NCRP 151 bases the shielding design goal for an uncontrolled area on 1 mSv a year, spread over 50 working weeks.", [], "What is the [[weekly design goal P]]?"), q_goal, [5.0 / WEEKS, 1.0, q_goal / 10], lambda v: f"{v:g} mSv/week",
        f"P = 1 mSv / 50 weeks = {q_goal:g} mSv per week. The controlled-area goal, 5 mSv a year, gives {5.0 / WEEKS:g} mSv per week, and leaving the annual value undivided gives 1 mSv.", lvl="Easy"),
    PRN(STEM("A linac treats 30 patients a day, 5 days a week. Each treatment delivers 3 Gy at 1 m from the target, summed over its 4 fields.", [], "What is the [[workload W]]?"), q_W, [4 * q_W, 30 * 3.0, 30 * 5.0], "{:.0f} Gy/week",
        f"W = 30 × 5 × 3 Gy = {q_W:.0f} Gy per week at 1 m. The 3 Gy already sums the 4 fields, so multiplying by 4 again gives {4 * q_W:.0f} Gy, and leaving out the 5 days gives {30 * 3.0:.0f} Gy.", lvl="Easy"),
    PR(STEM("A primary barrier is designed with B = P d² / (W U T).", [], "Between which two points is the [[distance d]] measured?"),
       "From the target to a point 0.3 m beyond the outer face of the barrier", ["From the isocenter to a point 0.3 m beyond the outer face of the barrier", "From the target to the outer face of the barrier itself", "From the target to the inner face of the barrier itself"],
       "The design goal applies where a person can stand, taken as 0.3 m beyond the barrier, and the inverse square runs from the source of the beam, the target. Stopping at the face of the wall leaves out the 0.3 m and overstates the dose.", lvl="Easy"),
    PR(STEM("Two primary walls of one 6 MV vault receive the same workload and use factor, and the areas behind them have the same weekly dose goal.", ["wall A: office behind it, T = 1, d = 7.0 m", "wall B: corridor behind it, T = 1/5, d = 4.0 m", f"TVL<sub>e</sub> = {PRI6[1]:.0f} cm"], "Which wall needs the [[thicker concrete]], and by about how much?"),
       f"Wall A, by about {q_two:.0f} cm", [f"Wall B, by about {q_two:.0f} cm", f"Wall A, by about {q_two_T:.0f} cm", f"Wall B, by about {q_two_d:.0f} cm"],
       f"B is proportional to d² / T: 49 for wall A and 16 × 5 = 80 for wall B, so A needs log<sub>10</sub>(80/49) = {dA:.2f} TVL more, {q_two:.0f} cm. Counting only the occupancy gives {q_two_T:.0f} cm for A, and counting only the distance gives {q_two_d:.0f} cm for B.", lvl="Moderate"),
    PR(STEM("A 6 MV primary barrier of ordinary concrete was designed for the present workload. The workload will double and nothing else changes.", [f"TVL<sub>e</sub> = {PRI6[1]:.0f} cm"], "How much [[concrete]] must be added?"),
       f"About {dW:.0f} cm, one half-value layer", [f"About {PRI6[1]:.0f} cm, one tenth-value layer", f"About {q_ln2:.0f} cm, ln 2 tenth-value layers", f"About {math.floor(PRI6[1] / 2 + 0.5):.0f} cm, half a tenth-value layer"],
       f"B must halve, so n rises by log<sub>10</sub> 2 = {LOG2:.2f}: {LOG2:.3f} × {PRI6[1]:.0f} = {dW:.1f} cm. One TVL answers a tenfold increase, ln 2 in place of log<sub>10</sub> 2 gives {q_ln2:.0f} cm, and an HVL is 0.30 TVL, not half of one.", lvl="Moderate"),
    PR(STEM(f"The equilibrium TVL of ordinary concrete is {PRI6[1]:.0f} cm for a 6 MV beam and {PRI18[1]:.0f} cm for an 18 MV beam (NCRP 151).", [], "What [[causes the increase]]?"),
       "The Compton attenuation coefficient of concrete falls as the energy rises", ["Concrete becomes less dense under higher-energy photons", "Photoelectric absorption in concrete rises with the energy", "Pair production in concrete falls as the energy rises"],
       "Over the megavoltage range nearly all the attenuation in concrete is Compton scattering, whose coefficient falls with energy, so each TVL is thicker. Photoelectric absorption falls steeply with energy, and pair production rises with it.", lvl="Moderate"),
    TYPED(STEM("A primary beam crosses a concrete wall at 30° from the normal to the wall.", ["perpendicular thickness = 150 cm"], "What [[slant thickness]] does the beam traverse?"), q_slant, 0.01, "cm",
          f"t<sub>slant</sub> = t / cos θ = 150 / cos 30° = 150 / {math.cos(math.radians(30)):.3f} = {q_slant:.1f} cm. Multiplying by cos θ gives {150 * math.cos(math.radians(30)):.1f} cm, shorter than the wall itself.",
          w=[f"cos 30° = {math.cos(math.radians(30)):.4f}", f"150 / {math.cos(math.radians(30)):.4f} = {q_slant:.1f} cm"], lvl="Moderate"),
    PR(STEM("A side wall of a vault is never struck by the primary beam. Leakage from the head and radiation scattered by the patient reach it.", [], "What [[use factor]] does this secondary barrier take?"),
       "1, because leakage and scatter reach it at every gantry angle", ["0.25, because the gantry points at it a quarter of the time", "0, because the primary beam never points at it", "0.5, because half of the leakage travels toward it"],
       "U is the fraction of the workload for which the primary beam points at a barrier. Leakage and patient scatter leave in all directions at every gantry angle, so secondary barriers take U = 1; the value 0.25 belongs to primary barriers.", lvl="Easy"),
    PR(STEM("A clinic moves most of its treatments to IMRT. The number of patients and the prescribed doses stay the same.", [], "Which part of the shielding calculation [[changes]]?"),
       "The leakage workload of the secondary barriers rises by C<sub>I</sub>", ["The primary workload of the primary barriers rises by C<sub>I</sub>", "The scatter fraction of the patient rises by C<sub>I</sub>", "The use factor of each primary barrier falls by C<sub>I</sub>"],
       "IMRT needs more monitor units per unit dose, and head leakage follows the monitor units, so the leakage workload becomes W C<sub>I</sub>. The dose to the patient, and with it the primary and scatter workloads, does not change.", lvl="Moderate"),
    PRN(STEM("A 6 MV vault treats every patient with IMRT. A secondary wall with an office (uncontrolled) behind it is reached by head leakage.", ["P = 0.02 mSv/week", "W = 400 Gy/week", "C<sub>I</sub> = 4", "T = 1", "d<sub>L</sub> = 6.0 m", f"leakage TVL<sub>1</sub> = {LEAK6[0]:.0f} cm, TVL<sub>e</sub> = {LEAK6[1]:.0f} cm"], "What [[concrete thickness]] does leakage require?"),
        qL, [qL_noCI, qL_pri, qL_no1000], "{:.0f} cm",
        f"B<sub>L</sub> = 1000 × 2 × 10<sup>−5</sup> × 6.0² / (400 × 4 × 1) = {sci(b_leak(P_U, 400.0, 1.0, 6.0, 4.0), 3)}, so n = {n_tvl(b_leak(P_U, 400.0, 1.0, 6.0, 4.0)):.2f} and t = {LEAK6[0]:.0f} + ({n_tvl(b_leak(P_U, 400.0, 1.0, 6.0, 4.0)):.2f} − 1) × {LEAK6[1]:.0f} = {qL:.0f} cm. Leaving out C<sub>I</sub> gives {qL_noCI:.0f} cm, the primary TVLs give {qL_pri:.0f} cm, and leaving out the factor 1000 gives {qL_no1000:.0f} cm.", lvl="Challenging"),
    PRN(STEM("A 6 MV secondary barrier of concrete is calculated for each component separately.", ["thickness for leakage = 80 cm", "thickness for patient scatter = 72 cm", f"leakage TVL<sub>e</sub> = {LEAK6[1]:.0f} cm"], "What [[thickness]] is built?"),
        q_hvl, [80.0, 80.0 + LEAK6[1], 152.0], "{:.1f} cm",
        f"The two differ by 8 cm, less than one TVL, so one HVL of the leakage component that sets the larger thickness, {LOG2:.3f} × {LEAK6[1]:.0f} = {LOG2 * LEAK6[1]:.1f} cm, is added to 80 cm: {q_hvl:.1f} cm. With 80 cm alone the two components could together reach twice the goal, and adding the thicknesses gives 152 cm.", lvl="Challenging"),
    PR(STEM("A new vault is planned for a 6 MV linac.", [], "Why does it need [[no neutron shielding]]?"),
       "Few photons of a 6 MV beam exceed the (γ,n) thresholds of the head", ["The flattening filter stops every neutron made at 6 MV", "The concrete turns all 6 MV neutrons into gamma rays", "Neutrons at 6 MV are made only inside the patient"],
       "The (γ,n) thresholds of tungsten and lead are about 6 to 8 MeV, and a 6 MV beam has almost no photons that energetic, so the neutron yield is negligible. Above about 10 MV the yield rises steeply and the door needs neutron shielding.", lvl="Easy"),
    PR(STEM("A vault is built with a maze between the treatment room and the door.", [], "What does the [[maze]] do for the door?"),
       "Radiation reaches the door only after scattering, so the door can be far lighter", ["Radiation cannot turn corners, so the door needs no shielding at any energy", "The maze lowers the occupancy factor at the door, so the door can be thinner", "The maze lowers the workload at the door, so the door can be thinner"],
       "No straight path joins the target to the door, so photons arrive only after scattering off the walls or through the inner maze wall, and neutrons lose energy and intensity along the maze. A door still needs some shielding, and above 10 MV it needs neutron shielding.", lvl="Moderate"),
    PR(STEM("The maze door of an 18 MV vault holds a layer of borated polyethylene between sheets of lead.", [], "What does the [[boron]] in the polyethylene do?"),
       "It captures slowed neutrons, emitting 0.48 MeV gamma rays instead of 2.2 MeV ones", ["It slows the fast neutrons by elastic collisions, as hydrogen does", "It absorbs the capture gamma rays that the maze walls produce", "It raises the density so that the photon TVL of the door falls"],
       "Hydrogen in the polyethylene slows the neutrons, and boron-10, with its large capture cross section for slow neutrons, absorbs them with a 0.48 MeV gamma ray, easier to stop than the 2.2 MeV ray of capture in hydrogen. The capture gamma rays from the maze are stopped by the lead.", lvl="Challenging"),
    PRM("An 18 MV vault is being designed. Which of these statements about its photoneutrons are correct?",
        ["They come mainly from (γ,n) reactions in the heavy metals of the head", "Their capture in the vault produces gamma rays that reach the door", "They lose energy as they scatter along the maze toward the door"],
        ["A 6 MV beam produces them in similar numbers", "A layer of lead alone stops them at the door", "The first centimetre of concrete absorbs them all"],
        "Neutrons come from (γ,n) reactions in the tungsten and lead of the target, collimators, and filter, above thresholds of about 6 to 8 MeV, so a 6 MV beam makes almost none. They slow as they scatter along the maze, and their capture produces gamma rays of a few MeV. Lead does little to slow neutrons, so the door needs hydrogen-rich, borated material, and concrete attenuates them over tens of centimetres.", lvl="Moderate"),
    PRM("A 6 MV vault is being redesigned. Which of these changes raise the concrete needed in a secondary barrier for head leakage?",
        ["Treating a larger share of the patients with IMRT", "Turning a storage room behind the wall into an office"],
        ["Raising the largest field from 35 × 35 cm to 40 × 40 cm", "Lowering the use factor of the opposite primary wall", "Moving the protected point farther from the isocenter"],
        "B<sub>L</sub> = 1000 P d<sub>L</sub>² / (W C<sub>I</sub> T). More IMRT raises C<sub>I</sub> and an office raises T from 1/20 to 1, and both lower B. The field size enters the scatter term and the primary barrier width, not the leakage term, and a larger distance raises B.", lvl="Moderate"),
    TYPED(STEM("An 18 MV primary barrier of ordinary concrete protects a corridor (uncontrolled).", ["P = 0.02 mSv/week", "W = 500 Gy/week", "U = 0.25", "T = 1/5", "d = 7.0 m", f"TVL<sub>1</sub> = {PRI18[0]:.0f} cm, TVL<sub>e</sub> = {PRI18[1]:.0f} cm"], "What [[concrete thickness]] is required?"), q_t18, 0.01, "cm",
          f"B = 2 × 10<sup>−5</sup> × 7.0² / (500 × 0.25 × 0.2) = {sci(q_B18, 3)}, n = {n_tvl(q_B18):.3f}, and t = {PRI18[0]:.0f} + ({n_tvl(q_B18):.3f} − 1) × {PRI18[1]:.0f} = {q_t18:.1f} cm. Using TVL<sub>e</sub> for every layer gives {n_tvl(q_B18) * PRI18[1]:.1f} cm.",
          w=[f"B = {sci(q_B18, 3)}", f"n = log<sub>10</sub>(1/B) = {n_tvl(q_B18):.3f}", f"t = {PRI18[0]:.0f} + {n_tvl(q_B18) - 1:.3f} × {PRI18[1]:.0f} = {q_t18:.1f} cm"], lvl="Challenging"),
]

INLINE = {0: [1, 2, 3], 1: [4, 5, 7], 2: [8, 9, 10], 3: [12, 13, 14, 15]}

TERMS = ['shielding design goal', 'workload', 'use factor', 'occupancy factor', 'primary barrier', 'secondary barrier', 'IMRT factor', 'scatter fraction']

TAKE = [
    [f"P = {mus(P_C)} mSv/week for controlled and {mus(P_U)} mSv/week for uncontrolled areas (NCRP 151).",
     "W is the dose per week at 1 m; U the fraction aimed at the barrier (1 for secondary barriers); T the fraction of time the most exposed person is there.",
     "d runs from the target to 0.3 m beyond the barrier."],
    ["B = P d² / (W U T), n = log<sub>10</sub>(1/B), t = TVL<sub>1</sub> + (n − 1) TVL<sub>e</sub>.",
     f"6 MV concrete: TVL<sub>1</sub> {PRI6[0]:.0f} cm, TVL<sub>e</sub> {PRI6[1]:.0f} cm. A factor of 10 is one TVL, a factor of 2 one HVL.",
     "Width: the largest field's diagonal projected to the barrier plus 0.3 m each side. Slant thickness: t / cos θ."],
    ["B<sub>s</sub> = P d<sub>sca</sub>² d<sub>sec</sub>² / (a W T) × 400/F and B<sub>L</sub> = 1000 P d<sub>L</sub>² / (W C<sub>I</sub> T).",
     "IMRT raises only the leakage workload, by C<sub>I</sub>.",
     "Thicknesses within one TVL: add one HVL to the larger; otherwise use the larger."],
    ["Photoneutrons from (γ,n) in the head matter above 10 MV; a 6 MV vault needs no neutron shielding.",
     "Maze door above 10 MV: borated polyethylene for the neutrons, lead for the capture gamma rays."],
]
