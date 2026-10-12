from blocks import *
import math
import nistdata as N

# ---------------------------------------------------------------- protection quantities (ICRP 103)
WT = [(0.12, ["red bone marrow", "colon", "lung", "stomach", "breast", "remainder tissues (13 in each sex)"]),
      (0.08, ["gonads"]),
      (0.04, ["bladder", "oesophagus", "liver", "thyroid"]),
      (0.01, ["bone surface", "brain", "salivary glands", "skin"])]
W = {t.split(" (")[0]: w for w, ts in WT for t in ts}                    # tissue weighting factor of each tissue
WT_SUM = sum(W.values())
W60_GONADS, W26_GONADS = 0.20, 0.25                                       # the gonads in ICRP 60 and in ICRP 26 (the weights 10 CFR 20 uses)
Q_UNKNOWN_N = 10                                                          # 10 CFR 20 quality factor for neutrons of unknown energy

def wr_neutron(e):
    """ICRP 103 radiation weighting factor for neutrons of energy e in MeV: one continuous function written in three branches."""
    if e < 1.0: return 2.5 + 18.2 * math.exp(-math.log(e) ** 2 / 6)
    if e <= 50.0: return 5.0 + 17.0 * math.exp(-math.log(2 * e) ** 2 / 6)
    return 2.5 + 3.25 * math.exp(-math.log(0.04 * e) ** 2 / 6)

def eff_dose(h): return sum(W[t] * v for t, v in h.items())             # E = sum of w_T H_T
def equiv_dose(parts): return sum(w * d for w, d in parts)                # H = sum of w_R D_R, mSv from mGy
def at_r(rate, r0, r): return rate * (r0 / r) ** 2                       # dose rate at r from a point source that gives `rate` at r0
REM = 10.0                                                                # mSv per rem
def mr(v): return f"{v:g} mSv ({v / REM:g} rem)"                          # a limit in mSv with its value in rem

wr_th, wr_1, wr_10 = wr_neutron(2.5e-8), wr_neutron(1.0), wr_neutron(10.0)    # thermal (0.025 eV), 1 MeV, 10 MeV
skin_all = 500.0; skin_e = W["skin"] * skin_all                           # a uniform 500 mSv to the whole skin adds 5 mSv to E

# ---------------------------------------------------------------- limits, in mSv, by document
NRC = dict(tede=50.0, organ=500.0, lens=150.0, skin=500.0, minor=0.10, fetus=5.0, fetus_near=0.5, public=1.0, hour=0.02)   # 10 CFR 20.1201, .1207, .1208, .1301
ICRP = dict(avg=20.0, years=5, max1=50.0, skin=500.0, public=1.0, fetus=1.0)                                            # ICRP 103; lens: ICRP 118
NCRP = dict(annual=50.0, per_age=10.0, lens=150.0, skin=500.0, fetus_month=0.5, public=1.0, public_rare=5.0)             # NCRP 116
LENS_C26 = 50.0                                                           # mGy per year, NCRP Commentary 26 (2016)
GOAL = dict(ctrl=0.1, unctrl=0.02, weeks=50)                              # NCRP 151 design goals, mSv per week
RA, HRA = 0.05, 1.0                                                       # radiation area and high radiation area: mSv in 1 h at 30 cm
def inv_level(frac, limit): return frac * limit / 4                       # investigation level per quarter
l1, l2 = inv_level(0.10, NRC["tede"]), inv_level(0.30, NRC["tede"])

# ---------------------------------------------------------------- worked examples
EX1 = {"lung": 6.0, "red bone marrow": 2.0, "thyroid": 10.0, "skin": 20.0}
e1 = eff_dose(EX1)
c1 = {t: W[t] * v for t, v in EX1.items()}                               # contribution of each tissue
ex1_steps = [f"Lung and marrow: {W['lung']:.2f} × ({EX1['lung']:.1f} + {EX1['red bone marrow']:.1f}) = {c1['lung'] + c1['red bone marrow']:.2f} mSv",
             f"Thyroid: {W['thyroid']:.2f} × {EX1['thyroid']:.1f} = {c1['thyroid']:.2f} mSv;   skin: {W['skin']:.2f} × {EX1['skin']:.1f} = {c1['skin']:.2f} mSv"]
ex1_least = min(c1, key=c1.get) == max(EX1, key=EX1.get) == "skin"       # the largest organ dose makes the smallest contribution

d_ph, d_n, wr_n = 0.40, 0.030, 10.0                                       # mGy, mGy, w_R of the neutrons
h2 = equiv_dose([(1.0, d_ph), (wr_n, d_n)])
n_share, d_share = 100 * wr_n * d_n / h2, 100 * d_n / (d_ph + d_n)

r3_rate, r3_r0, r3_r, r3_far = 0.40, 0.50, 2.0, 4.0                       # mSv/h at r3_r0 (m); working distance and a farther one (m)
rate3 = at_r(r3_rate, r3_r0, r3_r)
t3 = NCRP["fetus_month"] / rate3                                          # h to reach 0.5 mSv
t3x = NCRP["fetus_month"] / at_r(r3_rate, r3_r0, r3_far)

r4_rate, r4_r0, r4_r, r4_min, T4 = 2.0, 1.0, 1.5, 6, 0.05                 # mSv/h at r4_r0 (m), distance (m), minutes, apron transmission (given)
rate4 = at_r(r4_rate, r4_r0, r4_r)
collar4 = rate4 * r4_min / 60
under4 = collar4 * T4

# ---------------------------------------------------------------- numbers in the questions
QE = {"stomach": 4.0, "colon": 3.0, "liver": 5.0, "gonads": 2.0}
e_q = eff_dose(QE); e_sum = sum(QE.values()); e_all12 = W["lung"] * e_sum; e_mean = e_sum / len(QE)
e_q_sum = " + ".join(f"{W[t]:.2f} × {v:.1f}" for t, v in QE.items())

wr2 = round(wr_neutron(2.0), 1)                                           # 2 MeV neutrons, rounded as printed
dq_ph, dq_n = 1.2, 0.040
h_q = equiv_dose([(1.0, dq_ph), (wr2, dq_n)]); h_raw = dq_ph + dq_n; h_w20 = equiv_dose([(1.0, dq_ph), (20.0, dq_n)]); h_nonly = wr2 * dq_n

age = 45
cum = NCRP["per_age"] * age; cum_annual = NCRP["annual"] * age; cum_18 = NCRP["per_age"] * (age - 18)

b_rate, b_r0 = 0.50, 1.0                                                  # mSv/h at b_r0 (m)
r_hr = b_r0 * math.sqrt(b_rate / NRC["hour"])                             # distance at which the rate falls to the hourly limit
r_hr_lin = b_r0 * b_rate / NRC["hour"]                                    # 1/r in place of 1/r^2
r_hr_rem = b_r0 * math.sqrt(b_rate / (NRC["hour"] / REM))                 # 2 mrem read as 0.002 mSv (its value in rem)
r_hr_tenx = b_r0 * math.sqrt(b_rate / (NRC["hour"] * REM))                # 2 mrem read as 0.2 mSv

mu_pb = N.LEAD[0.4][0]; rho_pb = N.DENS["lead"]; x_ap = 0.05              # cm^2/g at 0.4 MeV, g/cm^3, cm
t_ap = math.exp(-mu_pb * rho_pb * x_ap)
t_ap_abs = 1 - t_ap; t_ap_mm = math.exp(-mu_pb * rho_pb * 0.5); t_ap_rho = math.exp(-mu_pb * x_ap)

dq_rate, dq_r0, dq_r, dq_min = 0.90, 1.0, 3.0, 40                         # mSv/h at dq_r0 (m), distance (m), min
dq_at = at_r(dq_rate, dq_r0, dq_r)
d_typed = dq_at * dq_min / 60 * 1000                                      # µSv
q_mrem = 120; q_msv = q_mrem / 1000 * REM                                 # a badge reading in mrem, and in mSv

pg_before = 1.0; pg_left = NRC["fetus"] - pg_before
badge_q = 2.0                                                             # mSv in one quarter
badge_level = "I" if l1 < badge_q <= l2 else ("II" if badge_q > l2 else "none")
wr_hour, wr_year = 0.03, 0.6                                              # waiting room: mSv in the busiest hour, mSv in a year
assert wr_year <= NRC["public"] and wr_hour > NRC["hour"], "the waiting room passes the annual limit and fails the hourly one"
assert badge_level == "I", "the badge reading lies between level I and level II"
assert ex1_least, "in the example the skin has the largest equivalent dose and the smallest contribution"

TOPIC = dict(
    id="dose-limits", domain=7, sub="VII.B", title="Dose limits and ALARA",
    ref=dict(aapm="", khan="", ford="25"),
    guide=[
        H("Protection quantities"),
        EQ("H<sub>T</sub> = Σ<sub>R</sub> w<sub>R</sub> D<sub>T,R</sub>", "E = Σ<sub>T</sub> w<sub>T</sub> H<sub>T</sub>", "1 Sv = 100 rem,   1 rem = 10 mSv,   1 mrem = 10 µSv"),
        P(f"In ICRP 103, w<sub>R</sub> is 1 for photons and electrons, 2 for protons, and 20 for α particles. For neutrons it varies continuously with energy: {wr_th:.1f} for thermal neutrons, a peak of {wr_1:.1f} at 1 MeV, and {wr_10:.1f} at 10 MeV."),
        P("The tissue weighting factor w<sub>T</sub> is the share of the stochastic detriment, cancer and heritable effects, attributed to one tissue. The factors sum to 1, so a uniform exposure gives an effective dose E equal to the equivalent dose. E describes a reference person and compares exposures with each other and with limits, not the risk to one patient."),
        TABLE(["w<sub>T</sub>", "Tissues (ICRP 103)", "Group total"], [[f"{w:.2f}", ", ".join(ts).capitalize(), f"{w * len(ts):.2f}"] for w, ts in WT] + [["", "All tissues", f"{WT_SUM:.2f}"]]),
        P(f"10 CFR 20 still uses quality factors ({Q_UNKNOWN_N} for neutrons of unknown energy) and the ICRP 26 tissue weights ({W26_GONADS:.2f} for the gonads)."),
        P(f"A limit on E controls stochastic risk but does not protect a tissue irradiated alone: the lens has no w<sub>T</sub>, and {skin_all:.0f} mSv to the whole skin adds {skin_e:.0f} mSv to E. The lens, skin, and extremities therefore have separate limits, set to prevent tissue reactions such as cataract and skin injury."),
        EX("Effective dose from organ doses", STEM("A worker receives a non-uniform exposure. The other tissues receive no dose.", [f"{t} = {v:.1f} mSv" for t, v in EX1.items()], "Find the [[effective dose]]."),
           [f"E = Σ w<sub>T</sub> H<sub>T</sub>, with w<sub>T</sub> = {W['lung']:.2f} for lung and marrow, {W['thyroid']:.2f} for thyroid, and {W['skin']:.2f} for skin", *ex1_steps],
           f"{e1:.2f} mSv. The skin has the largest equivalent dose and adds the least."),
        EX("Equivalent dose with neutrons", STEM("Near the door of a vault for an 18 MV beam, a worker is exposed to photons and neutrons.", [f"photon absorbed dose = {d_ph:.2f} mGy", f"neutron absorbed dose = {d_n:.3f} mGy", f"w<sub>R</sub> for the neutrons = {wr_n:.0f}"], "Find the [[equivalent dose]]."),
           ["H = Σ w<sub>R</sub> D<sub>R</sub>", f"Photons: 1 × {d_ph:.2f} = {d_ph:.2f} mSv;   neutrons: {wr_n:.0f} × {d_n:.3f} = {wr_n * d_n:.2f} mSv"],
           f"{h2:.2f} mSv. The neutrons give {n_share:.0f}% of it from {d_share:.0f}% of the absorbed dose."),

        H("Dose limits"),
        P("Limits cover workers and the public, not background or a patient's own medical exposure. 10 CFR 20, or an Agreement State's matching rule, covers radioactive material such as an HDR source; linacs fall under state rules with the same limits. ICRP and NCRP values are recommendations and change between editions."),
        TABLE(["Limit per year, unless stated", "10 CFR 20 (NRC)", "ICRP 103 and 118", "NCRP 116"], [
            ["Worker, effective dose", f"{mr(NRC['tede'])} TEDE", f"{ICRP['avg']:g} mSv averaged over {ICRP['years']} years, at most {ICRP['max1']:g} mSv in one year", f"{NCRP['annual']:g} mSv; lifetime {NCRP['per_age']:g} mSv × age"],
            ["Worker, lens of the eye", mr(NRC["lens"]), "the same values (ICRP 118)", f"{NCRP['lens']:g} mSv; {LENS_C26:g} mGy in Commentary 26"],
            ["Worker, skin and extremities", mr(NRC["skin"]), f"{ICRP['skin']:g} mSv", f"{NCRP['skin']:g} mSv"],
            ["Embryo/fetus, declared pregnancy", f"{mr(NRC['fetus'])} per pregnancy", f"about {ICRP['fetus']:g} mSv after declaration", f"{NCRP['fetus_month']:g} mSv per month"],
            ["Member of the public", f"{mr(NRC['public'])}; {mr(NRC['hour'])} in any hour in an unrestricted area", f"{ICRP['public']:g} mSv", f"{NCRP['public']:g} mSv; {NCRP['public_rare']:g} mSv if infrequent"]]),
        P(f"Under 10 CFR 20 a worker's annual limit is the more limiting of {NRC['tede']:g} mSv total effective dose equivalent (TEDE) and {NRC['organ']:g} mSv to any organ except the lens, both counting external dose and intakes. A minor, under 18, has {100 * NRC['minor']:.0f}% of each adult limit."),
        P(f"A declared pregnant worker has told her employer in writing of the pregnancy and the estimated date of conception; declaring is voluntary, and until then the adult limits apply. The embryo/fetus may then receive {NRC['fetus']:g} mSv over the whole pregnancy, spread roughly evenly by month, or {NRC['fetus_near']:g} mSv more if {NRC['fetus'] - NRC['fetus_near']:g} mSv or more had accrued by the declaration."),
        P(f"In an unrestricted area, one whose access the licensee neither limits nor controls, the dose from external sources may not exceed {NRC['hour']:g} mSv in any one hour."),

        H("ALARA and area controls"),
        P("ALARA, as low as reasonably achievable, requires every reasonable effort to keep doses below the limits, weighing cost against benefit (10 CFR 20.1101). External dose is controlled by time, distance (1/r² from a point source), and shielding (a factor of 2 per half-value layer)."),
        P(f"Shielding is designed to the NCRP 151 goals of {GOAL['ctrl']:g} mSv per week ({GOAL['ctrl'] * GOAL['weeks']:g} mSv per year) in controlled and {GOAL['unctrl']:g} mSv per week ({GOAL['unctrl'] * GOAL['weeks']:g} mSv per year) in uncontrolled areas, with an occupancy factor T, the fraction of beam-on time the most exposed person spends there: 1 for an office, 1/40 for a stairway. Signs mark radiation areas and high radiation areas, where a person could receive more than {RA:g} mSv and {HRA:g} mSv, respectively, in 1 h at 30 cm."),
        P(f"The radiation safety officer (RSO) runs the program, with a radiation safety committee where a hospital has several types of medical use. Dose reports are compared with investigation levels, which are not limits; NUREG-1556, Volume 9, puts level I at 10% and level II at 30% of a quarter of the annual limit, {l1:.2f} and {l2:.2f} mSv for the TEDE. Above level I the RSO reviews the dose; above level II the RSO investigates. Workers likely to exceed 1 mSv a year are trained (10 CFR 19.12)."),
        EX("Time to reach a dose", STEM("A declared pregnant worker works near a source. Her deep dose counts as the dose to the embryo/fetus.", [f"dose-equivalent rate = {r3_rate:.2f} mSv/h at {r3_r0:.2f} m", f"working distance = {r3_r:.1f} m", f"dose to reach = {NCRP['fetus_month']:g} mSv, the NCRP 116 monthly value"], "Find the [[working time]] that reaches this dose."),
           [f"Rate at {r3_r:.1f} m = {r3_rate:.2f} × ({r3_r0:.2f} / {r3_r:.1f})² = {rate3:.3f} mSv/h", f"Time = {NCRP['fetus_month']:g} / {rate3:.3f}"],
           f"{t3:.0f} h. At {r3_far:.1f} m the time would be {t3x:.0f} h."),
        EX("Dose under a lead apron", STEM("During an applicator insertion under fluoroscopy, a resident stands near the patient, who scatters the beam like a point source.", [f"scattered dose-equivalent rate = {r4_rate:.1f} mSv/h at {r4_r0:.1f} m", f"distance = {r4_r:.1f} m", f"fluoroscopy time = {r4_min} min", f"apron transmission = {T4:.2f}"], "Find the [[dose at the collar]], outside the apron, and the [[dose under the apron]]."),
           [f"Rate at {r4_r:.1f} m = {r4_rate:.1f} × ({r4_r0:.1f} / {r4_r:.1f})² = {rate4:.3f} mSv/h", f"Collar: {rate4:.3f} mSv/h × {r4_min / 60:g} h = {collar4:.4f} mSv", f"Under the apron: {collar4:.4f} × {T4:.2f} = {under4:.5f} mSv"],
           f"{1000 * collar4:.0f} µSv at the collar and {1000 * under4:.1f} µSv under the apron, 1/{1 / T4:.0f} of the collar value."),

        H("Personal dosimeters"),
        P("A badge integrates the dose where it is worn, over a month or a quarter, and reports the deep dose (1 cm), the lens dose (0.3 cm), and the shallow dose (0.007 cm). It misses intakes, parts of the body away from it, and the dose rate. 10 CFR 20 requires one for an adult likely to receive more than 10% of a limit."),
        P("An OSL badge (Al<sub>2</sub>O<sub>3</sub>:C) is read with light and can be read again. A TLD (LiF) is read by heating, which erases it; small and nearly tissue equivalent, it suits a ring badge. Film, which over-responds to low-energy photons, has been largely replaced. An electronic dosimeter or a pocket ion chamber reads at once."),
        P("The whole-body badge goes on the trunk, at the collar outside a lead apron; a declared pregnant worker adds one at the waist, under the apron. A ring badge goes under the glove on the hand nearer the source, chip facing the source."),

        H("Survey instruments"),
        P("An ion chamber survey meter collects the charge released in its gas, so it reads exposure rate with a nearly flat energy response over a wide range of rates; it is the instrument for linac and HDR surveys."),
        P("A Geiger–Mueller (GM) counter turns each ionizing event into a discharge of the same size, so it is sensitive but records no energy; without a compensating filter it over-responds to low-energy photons. After each discharge the tube is insensitive for its dead time, of the order of 100 µs. A linac delivers pulses a few microseconds long a few hundred times per second, so a whole pulse falls within one dead time: the counter registers at most one count per pulse and reads far too low. It suits a search for a lost seed."),
        P("A neutron rem meter surrounds a BF<sub>3</sub> or He-3 counter with a polyethylene moderator, which slows fast neutrons for capture and is sized so that the reading follows the dose equivalent. Survey meters are calibrated before first use, yearly, and after repair, against sources traceable to NIST directly or through an ADCL; a meter more than 20% off is withdrawn (10 CFR 35.61)."),
    ],
    cards=[
        F("ICRP 103 tissue weights of 0.12", "Red bone marrow, colon, lung, stomach, breast, and the remainder tissues."),
        F("ICRP 103 tissue weights below 0.12", ["0.08: gonads", "0.04: bladder, oesophagus, liver, thyroid", "0.01: bone surface, brain, salivary glands, skin"],
          w=[f"6 × 0.12 + 0.08 + 4 × 0.04 + 4 × 0.01 = {WT_SUM:.2f}"]),
        F("Radiation weighting factor for neutrons", f"A continuous function of energy in ICRP 103: {wr_th:.1f} for thermal neutrons, a peak of {wr_1:.1f} at 1 MeV, and {wr_10:.1f} at 10 MeV."),
        F("NRC limit on whole-body dose for a worker", f"The more limiting of {mr(NRC['tede'])} TEDE per year and {mr(NRC['organ'])} to any organ except the lens (10 CFR 20)."),
        F("NRC limits for lens, skin, and extremities", f"Lens {mr(NRC['lens'])} per year. Skin and extremities {mr(NRC['skin'])} shallow dose per year."),
        F("Occupational limits for minors", f"{100 * NRC['minor']:.0f}% of each adult limit under 10 CFR 20, so {NRC['minor'] * NRC['tede']:g} mSv TEDE per year."),
        F("Embryo/fetus of a declared pregnant worker", f"{mr(NRC['fetus'])} over the whole pregnancy under 10 CFR 20, at a roughly uniform monthly rate. NCRP 116 gives {NCRP['fetus_month']:g} mSv per month."),
        F("NRC limits for members of the public", f"{mr(NRC['public'])} per year, and {mr(NRC['hour'])} in any one hour in an unrestricted area."),
        F("ICRP occupational and lens limits", f"{ICRP['avg']:g} mSv per year averaged over {ICRP['years']} years, at most {ICRP['max1']:g} mSv in one year (ICRP 103). ICRP 118 sets the same numbers for the lens."),
        F("NCRP 116 cumulative limit", f"Lifetime effective dose at most {NCRP['per_age']:g} mSv × age in years, with {NCRP['annual']:g} mSv in any one year."),
        F("NCRP 151 shielding design goals", f"Controlled areas {GOAL['ctrl']:g} mSv per week ({GOAL['ctrl'] * GOAL['weeks']:g} mSv per year). Uncontrolled areas {GOAL['unctrl']:g} mSv per week ({GOAL['unctrl'] * GOAL['weeks']:g} mSv per year)."),
        F("Investigation levels", f"Level I at 10% and level II at 30% of a quarter of the annual limit: {l1:.2f} and {l2:.2f} mSv per quarter for the TEDE (NUREG-1556, Volume 9)."),
        F("OSL and TLD read-out", "OSL (Al<sub>2</sub>O<sub>3</sub>:C) is read with light and can be read again. TLD (LiF) is read by heating, which erases the signal."),
        F("Badge positions with a lead apron", "Whole-body badge at the collar, outside the apron. A declared pregnant worker adds a badge at the waist, under the apron."),
        F("GM counter in a pulsed beam", "Its dead time, of the order of 100 µs, allows at most one count per linac pulse, so it reads far too low. An ion chamber survey meter is used."),
        F("Neutron survey meter", "A BF<sub>3</sub> or He-3 counter inside a polyethylene moderator, which slows fast neutrons for capture. The reading follows the dose equivalent."),
    ],
)

PROBLEMS = [
    # ---- protection quantities
    PRN(STEM("", [], "In ICRP 103, what is the [[tissue weighting factor of the gonads]]?"), W["gonads"], [W60_GONADS, W26_GONADS, W["lung"]], "{:.2f}",
        f"ICRP 103 gives the gonads {W['gonads']:.2f}, down from {W60_GONADS:.2f} in ICRP 60. The value {W26_GONADS:.2f} comes from ICRP 26, which 10 CFR 20 still uses, and {W['lung']:.2f} belongs to lung, colon, stomach, breast, marrow, and the remainder.", lvl="Easy"),
    PRM("Which of these tissues have a tissue weighting factor of 0.12 in ICRP 103?", ["Lung", "Stomach", "Red bone marrow"], ["Thyroid", "Gonads", "Skin"],
        "Lung, stomach, and red bone marrow are in the 0.12 group with colon, breast, and the remainder tissues. The thyroid has 0.04, the gonads 0.08, and the skin 0.01.", lvl="Moderate"),
    PRN(STEM("A worker receives a non-uniform exposure. The other tissues receive no dose.", [f"{t} = {v:.1f} mSv" for t, v in QE.items()], "What is the [[effective dose]]?"), e_q, [e_sum, e_all12, e_mean], "{:.2f} mSv",
        f"E = {e_q_sum} = {e_q:.2f} mSv. Adding the equivalent doses without weights gives {e_sum:.2f} mSv, weighting every tissue by 0.12 gives {e_all12:.2f} mSv, and averaging them gives {e_mean:.2f} mSv.", lvl="Moderate"),
    PRN(STEM("A tissue is exposed to photons and to 2 MeV neutrons.", [f"photon absorbed dose = {dq_ph:.1f} mGy", f"neutron absorbed dose = {dq_n:.3f} mGy", f"w<sub>R</sub> for 2 MeV neutrons = {wr2:.1f} (ICRP 103)"], "What is the [[equivalent dose]]?"), h_q, [h_raw, h_w20, h_nonly], "{:.2f} mSv",
        f"H = 1 × {dq_ph:.1f} + {wr2:.1f} × {dq_n:.3f} = {h_q:.2f} mSv. Leaving out the weighting gives {h_raw:.2f} mSv, taking w<sub>R</sub> = 20 for all neutrons gives {h_w20:.2f} mSv, and the neutron term alone is {h_nonly:.2f} mSv.", lvl="Moderate"),

    # ---- dose limits
    SORT("Match each person or organ to its limit under 10 CFR 20.", [f"{mr(NRC['tede'])} per year", f"{mr(NRC['lens'])} per year", f"{mr(NRC['skin'])} per year", f"{mr(NRC['public'])} per year", f"{mr(NRC['fetus'])} per pregnancy"],
         [("Adult worker, total effective dose equivalent", 0), ("Adult worker, lens of the eye", 1), ("Adult worker, skin of the hands", 2), ("Member of the public, total effective dose equivalent", 3), ("Embryo/fetus of a declared pregnant worker", 4)],
         "The whole-body limit for a worker controls stochastic risk. The lens and skin limits are higher because they guard against tissue reactions with thresholds. The public and the embryo/fetus neither choose the exposure nor benefit from the work, so their limits are lower.", lvl="Easy", mode="match", cap=1),
    PR(STEM("A 17-year-old student works in a radiation area during a summer program.", [], "Which limit on the total effective dose equivalent applies under 10 CFR 20?"),
       f"{NRC['minor'] * NRC['tede']:g} mSv per year, because a minor has {100 * NRC['minor']:.0f}% of each adult limit", [f"{NRC['tede']:g} mSv per year, because the work is occupational", f"{NRC['public']:g} mSv per year, because she counts as a member of the public", "0 mSv per year, because exposure under 18 is not permitted"],
       f"10 CFR 20.1207 limits a minor to 10% of each adult limit, {NRC['minor'] * NRC['tede']:g} mSv TEDE per year. Exposure under 18 is permitted, so the full adult limit and a ban are both wrong.", lvl="Easy"),
    PRN(STEM("A physicist is 45 years old.", [], f"What [[lifetime effective dose]] does NCRP 116 allow at this age?"), cum, [cum_annual, cum_18, NCRP["annual"]], "{:,.0f} mSv",
        f"NCRP 116 caps the lifetime effective dose at 10 mSv × age = 10 × {age} = {cum:,.0f} mSv. Multiplying the annual limit by the age gives {cum_annual:,.0f} mSv, and counting only the years since age 18 gives {cum_18:,.0f} mSv.", lvl="Easy"),
    PR(STEM(f"A radiation therapist declares her pregnancy in writing. The deep dose on her badge since conception is {pg_before:.1f} mSv, all occupational.", [], "How much more dose may the embryo/fetus receive during the rest of the pregnancy under 10 CFR 20?"),
       f"{pg_left:.1f} mSv, because the {NRC['fetus']:g} mSv limit covers the whole pregnancy", [f"{NRC['fetus']:.1f} mSv, because the limit counts from the declaration", f"{ICRP['fetus']:.1f} mSv, because the limit after declaration is {ICRP['fetus']:g} mSv", f"{NRC['fetus_near']:.1f} mSv, because some dose was received before declaration"],
       f"The {NRC['fetus']:g} mSv limit of 10 CFR 20.1208 covers the entire pregnancy, so {NRC['fetus']:g} − {pg_before:.1f} = {pg_left:.1f} mSv remains. The {ICRP['fetus']:g} mSv value is ICRP's advice, and the {NRC['fetus_near']:g} mSv allowance applies only when {NRC['fetus'] - NRC['fetus_near']:g} mSv or more has accrued at declaration.", lvl="Moderate"),
    PR("10 CFR 20 limits the dose to the lens of the eye separately from the total effective dose equivalent. What is the reason?",
       "Cataract has a dose threshold, and the lens adds nothing to the effective dose", ["The lens has the largest tissue weighting factor, so it dominates the effective dose", "Lens doses come only from neutrons, which the effective dose leaves out", "The lens is the tissue most likely to develop a radiation-induced cancer"],
       "An effective dose limit controls stochastic risk. The lens has no tissue weighting factor, so a high lens dose can coexist with a low effective dose, and a separate limit guards against cataract, a tissue reaction with a threshold. With no weight the lens cannot dominate E, and photons, not neutrons, give most lens doses.", lvl="Challenging"),
    PR(STEM(f"A waiting room next to an HDR vault is an unrestricted area. A survey with a treatment in progress finds {wr_hour:g} mSv in one hour at the chair nearest the wall. With the expected occupancy, the annual dose there is {wr_year:g} mSv.", [], "Does the waiting room meet the public limits of 10 CFR 20?"),
       f"No: {wr_hour:g} mSv in one hour exceeds the {NRC['hour']:g} mSv hourly limit",
       [f"Yes: the {wr_year:g} mSv annual dose is below the {NRC['public']:g} mSv public limit", "Yes: the hourly limit applies only inside restricted areas", "No: an unrestricted area may receive no dose from the source"],
       f"An unrestricted area must meet both conditions of 10 CFR 20.1301: at most {NRC['public']:g} mSv per year and at most {NRC['hour']:g} mSv in any one hour. The annual dose passes and the hourly dose fails; checking only the annual total misses the hourly condition, and the public may receive some dose.", lvl="Challenging"),

    # ---- ALARA and area controls
    TYPED(STEM("A worker stands near a point source.", [f"dose-equivalent rate = {dq_rate:.2f} mSv/h at {dq_r0:.1f} m", f"distance = {dq_r:.1f} m", f"time = {dq_min} min"], "What [[dose]] does the worker receive?"), d_typed, 0.02, "µSv",
          f"Rate at {dq_r:.1f} m = {dq_rate:.2f} × ({dq_r0:.1f} / {dq_r:.1f})² = {dq_at:.3f} mSv/h. Dose = {dq_at:.3f} × {dq_min} / 60 = {d_typed / 1000:.4f} mSv = {d_typed:.1f} µSv.", lvl="Moderate"),
    PRN(STEM(f"An unshielded point source gives a dose-equivalent rate of {b_rate:.2f} mSv/h at {b_r0:.1f} m. A boundary is set where the rate meets the hourly limit of 10 CFR 20 for an unrestricted area.", [], "How far from the source is the [[boundary]]?"), r_hr, [r_hr_lin, r_hr_rem, r_hr_tenx], "{:.1f} m",
        f"The limit is {NRC['hour'] / REM * 1000:g} mrem = {NRC['hour']:g} mSv in any one hour. r = {b_r0:.1f} × √({b_rate:.2f} / {NRC['hour']:g}) = {r_hr:.1f} m. Using 1/r in place of 1/r² gives {r_hr_lin:.1f} m, reading {NRC['hour'] / REM * 1000:g} mrem as {NRC['hour'] / REM:g} mSv gives {r_hr_rem:.1f} m, and reading it as {NRC['hour'] * REM:g} mSv gives {r_hr_tenx:.1f} m.", lvl="Challenging"),
    PR(STEM(f"A radiation therapist's badge shows a deep dose of {badge_q:.1f} mSv for one quarter. The program sets level I at 10% and level II at 30% of a quarter of the annual TEDE limit of {NRC['tede']:g} mSv.", [], "What follows from this report?"),
       "Level I is exceeded but level II is not, so the RSO reviews the dose",
       [f"Nothing, because {badge_q:.1f} mSv is far below the {NRC['tede']:g} mSv annual limit", "Level II is exceeded, so the RSO investigates the cause", "The NRC is notified, because a dose limit has been exceeded"],
       f"Level I = 0.10 × {NRC['tede']:g} / 4 = {l1:.2f} mSv and level II = 0.30 × {NRC['tede']:g} / 4 = {l2:.2f} mSv, so {badge_q:.1f} mSv lies between them and calls for a review by the RSO. An investigation level is not a limit, so no report to the NRC is due, and comparing with the annual limit alone skips the review.", lvl="Challenging"),
    PRN(STEM("A worker who handles Ir-192 seed ribbons wears a lead apron. Take 0.4 MeV as the photon energy and narrow-beam attenuation.", ["lead equivalence = 0.5 mm", f"μ/ρ of lead at 0.4 MeV = {mu_pb:.4f} cm²/g", f"density of lead = {rho_pb:.2f} g/cm³"], "What [[fraction of the photons]] does the apron transmit?"), t_ap, [t_ap_abs, t_ap_mm, t_ap_rho], "{:.2f}",
        f"μ = {mu_pb:.4f} × {rho_pb:.2f} = {mu_pb * rho_pb:.3f} cm<sup>−1</sup>, and T = e<sup>−{mu_pb * rho_pb:.3f} × 0.05</sup> = {t_ap:.2f}, so the apron removes only about {100 * t_ap_abs:.0f}% of Ir-192 photons. {t_ap_abs:.2f} is the fraction removed, {t_ap_mm:.2f} treats 0.5 mm as 0.5 cm, and {t_ap_rho:.2f} leaves out the density.", lvl="Challenging"),

    # ---- personal dosimeters
    PR("Which detector and read-out does an OSL badge use?", "Carbon-doped aluminium oxide, read with light", ["Lithium fluoride, read by heating it in a reader", "Silver bromide film, read by developing it", "A silicon diode, read on a built-in display"],
       "OSL stands for optically stimulated luminescence: light releases the stored signal from Al<sub>2</sub>O<sub>3</sub>:C, and the reading can be repeated. Heating lithium fluoride describes a TLD, and the diode describes an electronic dosimeter.", lvl="Easy"),
    PR(STEM("A physicist loads I-125 seeds into needles by hand behind an L-block shield.", [], "Where is the ring dosimeter worn?"),
       "On the hand nearer the seeds, under the glove, with the chip facing the seeds", ["On the hand farther from the seeds, over the glove, with the chip facing out", "On either hand, over the glove, with the chip on the back of the finger", "On the wrist of the hand nearer the seeds, over the glove, facing the seeds"],
       "The ring should record the highest skin dose to the hands, so it goes on the hand that handles the seeds, with the chip toward them; a glove over it keeps it clean without shielding much. A chip on the back of the finger or a wrist position records a lower dose than the fingertips receive.", lvl="Moderate"),
    TYPED(STEM("A dosimetry report lists a quarterly deep dose.", [f"deep dose = {q_mrem} mrem"], "What is the [[deep dose]] in mSv?"), q_msv, 0.01, "mSv",
          f"1 rem = {REM:g} mSv, so 1 mrem = {REM / 1000:g} mSv and {q_mrem} mrem = {q_msv:.1f} mSv.", lvl="Easy"),

    # ---- survey instruments
    PR("How often does 10 CFR 35.61 require a survey meter used to show compliance to be calibrated?", "Before first use, annually, and after a repair that affects calibration", ["Before first use only, unless the daily check source reading changes", "Every two years, and after a repair that affects calibration", "Every month, against the check source supplied with the meter"],
       "Calibration is required before first use, annually, and after a repair that affects it, and a meter that reads more than 20% from the expected value is not used. A check source confirms that the meter works on the day, but it does not calibrate it.", lvl="Easy"),
    PR("Why does a neutron survey meter surround its BF<sub>3</sub> or He-3 counter with polyethylene?", "To slow fast neutrons to energies at which the counter captures them", ["To shield the counter from the photons that come with the neutrons", "To absorb thermal neutrons before they reach the counter", "To convert the neutrons into photons that the counter detects"],
       "B-10 and He-3 capture slow neutrons far more readily than fast ones, so the hydrogen in the polyethylene moderates the neutrons first. Photons are rejected by the size of the pulse, not by the polyethylene, which barely attenuates them.", lvl="Moderate"),
    PRM(STEM("A GM counter is held outside the door of a linac vault while the beam is on.", [], "Which of these limit the accuracy of its reading?"),
        ["Its dead time lets it register at most about one count per beam pulse", "Without energy compensation it over-responds to low-energy photons"],
        ["Its pulse height is proportional to the energy each photon deposits", "It needs a polyethylene moderator before it can detect photons"],
        "The linac delivers each pulse within a few microseconds, far shorter than a dead time of the order of 100 µs, so the counter misses all but one event per pulse. An uncompensated tube also over-responds to low-energy scatter. Every GM pulse has the same size, and a moderator is needed only for neutrons.", lvl="Moderate"),
    SORT("Match each task to the instrument used for it.", ["Ion chamber survey meter", "GM counter", "Moderated BF<sub>3</sub> or He-3 counter", "TLD ring badge", "OSL badge"],
         [("Survey outside a linac vault with the beam on", 0), ("Search of an operating room floor for a dropped seed", 1), ("Neutron dose equivalent at the door of an 18 MV vault", 2), ("Dose to the fingers of a worker who loads seeds", 3), ("Monthly whole-body dose of a radiation therapist", 4)],
         "The ion chamber reads exposure rate correctly in a pulsed beam. Of these instruments, the GM counter is the most sensitive for finding a source. Neutrons need a moderated counter, the fingers need a small TLD ring, and the whole-body record comes from a badge.", lvl="Moderate", mode="match", cap=1),
]

INLINE = {0: [1, 2, 3, 4], 1: [5, 6, 8, 9], 2: [11, 12, 13], 3: [15, 16, 17]}

TERMS = ["tissue weighting factor", "declared pregnant worker", "unrestricted area", "ALARA", "occupancy factor", "investigation levels", "dead time", "moderator"]

TAKE = [
    ["ICRP 103 w<sub>T</sub>: " + "; ".join(f"{w:.2f} " + ", ".join(t.split(" (")[0].replace("red bone marrow", "marrow").replace(" tissues", "") for t in ts) for w, ts in WT) + ".",
     f"Neutron w<sub>R</sub> peaks at {wr_1:.1f} at 1 MeV. 1 rem = {REM:g} mSv.",
     "An effective dose limit does not protect the lens or the skin, which have separate limits."],
    [f"10 CFR 20, per year: worker {NRC['tede']:g} mSv, lens {NRC['lens']:g} mSv, skin {NRC['skin']:g} mSv, minors 10%, public {NRC['public']:g} mSv ({NRC['hour']:g} mSv in any hour).",
     f"Embryo/fetus of a declared pregnant worker: {NRC['fetus']:g} mSv per pregnancy (NCRP 116: {NCRP['fetus_month']:g} mSv per month).",
     f"ICRP: {ICRP['avg']:g} mSv per year averaged over {ICRP['years']} years, also for the lens. NCRP 116: {NCRP['per_age']:g} mSv × age."],
    ["Time, distance (1/r²), and shielding.",
     f"NCRP 151 design goals: {GOAL['ctrl']:g} mSv per week controlled, {GOAL['unctrl']:g} mSv per week uncontrolled.",
     "Investigation levels at 10% and 30% of the quarterly share of a limit prompt a review, not a report of overexposure."],
    ["OSL is read with light and can be read again; TLD is read by heat, which erases it, and suits ring badges.",
     "Collar badge outside the apron; a declared pregnant worker adds one at the waist under it."],
    ["Ion chamber for linac and HDR surveys. A GM counter registers at most one count per linac pulse.",
     "Neutrons need a moderated BF<sub>3</sub> or He-3 counter. Survey meters are calibrated yearly and withdrawn when more than 20% off."],
]
