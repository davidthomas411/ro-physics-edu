from blocks import *
import math, calc, mrdata, real
MT = mrdata.TISSUE
RM = real.STATS["mr"]["params"]                                              # read from the DICOM headers of real scans: tools/make_real_mr.py

T1 = {"fat": 250.0, "csf": 3000.0}                              # illustrative longitudinal relaxation times, ms
T2 = {"brain": 90.0, "csf": 2000.0}                             # illustrative transverse relaxation times, ms
mz = lambda t, t1: 1 - math.exp(-t / t1)                        # recovery of M_z from zero after a 90 degree pulse, as a fraction of M_0
mxy = lambda te, t2: math.exp(-te / t2)                         # decay of M_xy after the 90 degree pulse
ir = lambda t, t1: 1 - 2 * math.exp(-t / t1)                    # recovery after a 180 degree inversion pulse
null = lambda t1: t1 * math.log(2)                              # the time at which an inverted tissue passes through zero
fat500, csf500, fat4000, csf4000 = mz(500, T1["fat"]), mz(500, T1["csf"]), mz(4000, T1["fat"]), mz(4000, T1["csf"])
b15, c15, b100, c100 = mxy(15, T2["brain"]), mxy(15, T2["csf"]), mxy(100, T2["brain"]), mxy(100, T2["csf"])
tr_04 = -T1["csf"] * math.log(1 - 0.4)                          # time at which M_z of CSF has recovered to 0.4 of M_0
def t1_nulled(ti, tr):                                          # the T1 that an inversion time ti nulls at a repetition time tr: 1 - 2 exp(-ti/T1) + exp(-tr/T1) = 0, solved by bisection
    lo, hi = 100.0, 20000.0
    for _ in range(80):
        mid = (lo + hi) / 2; lo, hi = (lo, mid) if 1 - 2 * math.exp(-ti / mid) + math.exp(-tr / mid) < 0 else (mid, hi)
    return (lo + hi) / 2
T1_FLAIR = t1_nulled(RM["flair"]["ti"], RM["flair"]["tr"])

TOPIC = dict(
    id="mri-sequences", domain=4, sub="IV.A", title="MRI pulse sequences and contrast",
    ref=dict(aapm="TG-284", khan="", ford="20"),
    guide=[
        H("Longitudinal magnetization and T1"),
        P("The nuclei in a sample have a net magnetization M. It has a longitudinal component, M<sub>z</sub>, along the B<sub>0</sub> field, and a transverse component, M<sub>xy</sub>, in the plane perpendicular to it. M<sub>z</sub> = 0 immediately after an RF pulse has flipped the spins into the transverse plane. The spins then decay back toward alignment with B<sub>0</sub>, and M<sub>z</sub> grows. After a time an RF pulse flips them again, and the interval between repeated pulses is the repetition time, TR."),
        EQ("M<sub>z</sub>(t) = M<sub>0</sub> (1 − e<sup>−t/T1</sup>)", "M<sub>0</sub> = the equilibrium magnetization,   T1 = the spin-lattice relaxation time of the tissue"),
        P("TR sets how much M<sub>z</sub> can grow before the next pulse, and different tissues have different T1, the exponential constant of this spin-lattice relaxation, which describes the interaction of the nuclei with the surrounding material, the lattice. At a long TR most tissues have recovered fully and M<sub>z</sub> is nearly the same in all of them. At a short TR the magnetization is still growing, and the tissues differ a great deal. A short TR therefore gives a T1-weighted image, in which fat is bright and fluids such as cerebrospinal fluid (CSF) are dark."),
        EX("T1 contrast at two repetition times", STEM("Illustrative values: T1 = 250 ms for fat and 3000 ms for CSF.", ["TR = 500 ms", "TR = 4000 ms"], "Find the [[M<sub>z</sub> / M<sub>0</sub>]] of each tissue at each TR."), ["M<sub>z</sub>/M<sub>0</sub> = 1 − e<sup>−TR/T1</sup>", "TR = 500: fat 1 − e<sup>−2</sup>, CSF 1 − e<sup>−0.167</sup>", "TR = 4000: fat 1 − e<sup>−16</sup>, CSF 1 − e<sup>−1.33</sup>"], f"TR = 500 ms: fat {fat500:.2f} and CSF {csf500:.2f}, a large difference, so a T1-weighted image. TR = 4000 ms: fat {fat4000:.2f} and CSF {csf4000:.2f}, a small difference."),

        H("Spin echo, TE, and T2"),
        P("The transverse component is read out with a spin-echo sequence. With all spins along B<sub>0</sub>, a 90° pulse flips them into the transverse plane, and the pulse is shut off at that point. The spins then precess in the plane, but local differences in the field make some precess slightly faster and some slower, so they spread out in angle and the net M<sub>xy</sub> falls. At a chosen time a 180° pulse reverses the spins, so that the faster ones start to catch up with the slower ones. When they have caught up, the net M<sub>xy</sub> rises abruptly and an echo is recorded. The time from the 90° pulse to the echo is the echo time, TE, set by the delay between the two pulses."),
        P("The M<sub>xy</sub> measured this way decays with an exponential constant T2, the spin-spin relaxation time, which describes the interaction of the nuclear spins with each other. It differs between tissues, and the contrast is larger at a longer TE. In such a T2-weighted image, fat and brain are relatively dark and fluids such as CSF are bright. A T1-weighted image has a short TR and a short TE, and a T2-weighted image has a long TR and a long TE."),
        EQ("M<sub>xy</sub>(TE) = M<sub>0</sub> e<sup>−TE/T2</sup>"),
        EX("T2 contrast at two echo times", STEM("Illustrative values: T2 = 90 ms for brain and 2000 ms for CSF.", ["TE = 15 ms", "TE = 100 ms"], "Find the [[M<sub>xy</sub> / M<sub>0</sub>]] of each tissue at each TE."), ["M<sub>xy</sub>/M<sub>0</sub> = e<sup>−TE/T2</sup>", "TE = 15: brain e<sup>−0.167</sup>, CSF e<sup>−0.0075</sup>", "TE = 100: brain e<sup>−1.11</sup>, CSF e<sup>−0.05</sup>"], f"TE = 15 ms: brain {b15:.2f} and CSF {c15:.2f}. TE = 100 ms: brain {b100:.2f} and CSF {c100:.2f}. The difference grows with TE, and CSF is bright."),
        P("The gadolinium contrast agent shortens T1, which gives a brighter signal on T1-weighted images. After an intravenous injection the normal vessels are bright. The gadolinium chelate does not cross the blood-brain barrier, so normal brain is not enhanced, but in a tumour where the barrier is disrupted and the vessels leak, the signal is enhanced."),

        H("Inversion recovery and FLAIR"),
        P("An inversion recovery sequence begins with a 180° pulse, which inverts the longitudinal magnetization. It then recovers from −M<sub>0</sub>, passes through zero, and approaches +M<sub>0</sub>. At the moment when the magnetization of one tissue is zero, the signal from that tissue is nulled out. If the rest of the sequence starts at that time, the tissue gives no signal. Fluid-attenuated inversion recovery (FLAIR) nulls the CSF. The image is still T2-weighted because of the long TE, but the CSF appears dark."),
        EQ("M<sub>z</sub>(t) = M<sub>0</sub> (1 − 2 e<sup>−t/T1</sup>),   null at t = T1 ln 2 ≈ 0.69 T1"),
        EX("Nulling the CSF", STEM("A tissue with T1 = 3000 ms is to be nulled in an inversion recovery sequence.", [], "Find the [[inversion time]]."), ["t = T1 ln 2 = 3000 × 0.693"], f"{null(3000):.0f} ms. At that time the magnetization of the CSF is zero, so it gives no signal."),
        P(f"In the simulated contrast of a real brain slice, the signal of each tissue is PD × (1 − 2e<sup>−TI/T1</sup> + e<sup>−TR/T1</sup>) × e<sup>−TE/T2</sup> for an inversion recovery sequence, and PD × (1 − e<sup>−TR/T1</sup>) × e<sup>−TE/T2</sup> without inversion, with illustrative values at 1.5 T: T1 = {MT['WM']['T1']} ms, {MT['GM']['T1']} ms, and {MT['CSF']['T1']} ms and T2 = {MT['WM']['T2']} ms, {MT['GM']['T2']} ms, and {MT['CSF']['T2']} ms for white matter, gray matter, and CSF. A short TR and a short TE make the CSF dark and the white matter brighter than the gray matter. A long TE makes the CSF bright. A TI that nulls the CSF removes it from a T2-weighted image, which is FLAIR."),
        AVF("mr-contrast"),
        P(f"In the real images, from one session on a 3 T scanner, the T1 sequence is an inversion-prepared gradient echo with TR {RM['t1']['tr']:g} ms, TE {RM['t1']['te']:g} ms, and TI {RM['t1']['ti']:g} ms, and the second T1 image follows an injection of gadolinium. The T2 sequence is a 3D fast spin echo with TR {RM['t2']['tr']:g} ms and an effective TE of {RM['t2']['te']:g} ms. The FLAIR sequence has TR {RM['flair']['tr']:g} ms, TE {RM['flair']['te']:g} ms, and TI {RM['flair']['ti']:g} ms. As in the simulation, the CSF is dark on T1 and FLAIR and bright on T2. The tumour rim enhances after gadolinium, and the surrounding oedema is bright on T2 and FLAIR. The FLAIR inversion time nulls a tissue with a T1 of {T1_FLAIR / 1000:.1f} s at that TR, close to the T1 of CSF at 3 T (about 4 to 4.5 s)."),
        AVF("real-mr-seq"),
    ],
    cards=[
        F("Longitudinal and transverse magnetization", "M<sub>z</sub> lies along B<sub>0</sub> and M<sub>xy</sub> lies in the plane perpendicular to it."),
        F("Repetition time TR", "The interval between repeated RF pulses. It sets how much M<sub>z</sub> grows before the next pulse."),
        F("T1 relaxation", "The spin-lattice relaxation time: the exponential constant for the growth of M<sub>z</sub>, M<sub>z</sub> = M<sub>0</sub>(1 − e<sup>−t/T1</sup>)."),
        F("T1-weighted image", "A short TR. Fat is bright and fluids such as CSF are dark. Usually also a short TE."),
        F("90° pulse", "Flips the spins from the B<sub>0</sub> direction into the transverse plane."),
        F("180° pulse in spin echo", "Reverses the spins in the plane, so the faster ones catch up with the slower ones and an echo appears."),
        F("Echo time TE", "The time from the 90° pulse to the echo, set by the delay between the 90° and 180° pulses."),
        F("T2 relaxation", "The spin-spin relaxation time: the exponential constant for the decay of M<sub>xy</sub>, M<sub>xy</sub> = M<sub>0</sub>e<sup>−TE/T2</sup>."),
        F("T2-weighted image", "A long TE (and a long TR). CSF is bright, and fat and brain are relatively dark."),
        F("Gadolinium contrast", "Shortens T1 and brightens the signal on T1-weighted images. It enhances a tumour where the blood-brain barrier is disrupted."),
        F("Inversion recovery", "Begins with a 180° pulse. Starting the sequence when one tissue's magnetization is zero nulls its signal."),
        F("FLAIR", "Fluid-attenuated inversion recovery: T2-weighted, with the CSF signal nulled so that CSF appears dark."),
    ],
)

PROBLEMS = [
    PR("A 90° pulse in a spin-echo sequence:", "flips the net magnetization into the transverse plane", ["encodes the location of the signal", "aligns electron spins", "inverts the longitudinal magnetization"],
       "After the 90° pulse the spins precess in the x–y plane, and M<sub>xy</sub> then decays as they spread out.", lvl="Easy"),
    PR("A T1-weighted image is obtained with:", "a short TR", ["a long TR and a long TE", "a 180° pulse first", "a high mA"],
       "A short TR leaves the longitudinal magnetization of the tissues still growing, so the tissues differ.", lvl="Easy"),
    PR("On a T1-weighted image, cerebrospinal fluid appears:", "dark", ["bright", "the same as fat", "null in every sequence"],
       "CSF has a long T1, so at a short TR little M<sub>z</sub> has recovered. Fat has a short T1 and is bright.", lvl="Easy"),
    PR("The time from the 90° pulse to the spin echo is:", "the echo time, TE", ["the repetition time, TR", "the inversion time", "the Larmor period"],
       "The echo time is set by the delay between the 90° and 180° pulses.", lvl="Easy"),
    PRN(STEM("Illustrative values: T1 = 250 ms for fat and 3000 ms for CSF.", ["TR = 500 ms"], "What is [[M<sub>z</sub> / M<sub>0</sub>]] for fat at the end of the repetition time?"), fat500, [csf500, math.exp(-2), 1.0], "{:.2f}",
        f"M<sub>z</sub>/M<sub>0</sub> = 1 − e<sup>−500/250</sup> = 1 − e<sup>−2</sup> = {fat500:.2f}. The CSF value is {csf500:.2f}, and e<sup>−2</sup> alone is {math.exp(-2):.2f}.", lvl="Moderate"),
    PR("Gadolinium contrast shortens T1, so on a T1-weighted image the enhanced tissue appears:", "brighter", ["darker", "unchanged", "as null"],
       "A shorter T1 gives more recovered M<sub>z</sub> at the end of a short TR, so a larger signal.", lvl="Moderate"),
    PRN(STEM("Illustrative values: T2 = 90 ms for brain and 2000 ms for CSF.", ["TE = 100 ms"], "What is [[M<sub>xy</sub> / M<sub>0</sub>]] for brain at the echo?"), b100, [c100, 1 - b100, math.exp(-90 / 100)], "{:.2f}",
        f"M<sub>xy</sub>/M<sub>0</sub> = e<sup>−100/90</sup> = e<sup>−1.11</sup> = {b100:.2f}. For CSF the value is {c100:.2f}, so CSF is much brighter on this T2-weighted image.", lvl="Moderate"),
    PR("Which pair of times gives a T2-weighted image?", "A long TR and a long TE", ["A short TR and a short TE", "A short TR and a long TE", "A long TR and a short TE"],
       "T1 weighting needs a short TR. T2 weighting needs a long TE, with a long TR so that T1 differences have recovered.", lvl="Moderate"),
    PRN(STEM("A tissue with T1 = 3000 ms is to be nulled by an inversion recovery sequence.", [], "What is the [[inversion time]]?"), null(3000), [3000.0, 3000 * 0.5, 3000 * math.log(10)], "{:.0f} ms",
        f"M<sub>z</sub> = 0 when 1 − 2 e<sup>−t/T1</sup> = 0, so t = T1 ln 2 = 3000 × 0.693 = {null(3000):.0f} ms. Using T1 itself gives 3000, and using half of T1 gives 1500.", lvl="Challenging"),
    PR("In FLAIR the CSF appears dark on a T2-weighted image because:", "the sequence starts when the CSF magnetization passes through zero, which nulls its signal", ["CSF has a short T2", "CSF has no hydrogen", "the TE is too short for CSF"],
       "Without the nulling, CSF would be bright on a T2-weighted image. FLAIR removes its signal with an inversion pulse.", lvl="Challenging"),
]

TERMS = ['repetition time', 'spin-echo', 'inversion recovery', 'T1-weighted']

TAKE = [
    [('M<sub>z</sub> = M<sub>0</sub>(1 − e<sup>−t/T1</sup>). A short TR leaves the tissues still recovering, which gives a T1-weighted image: fat bright, CSF dark.', 'mz-recovery')],
    [('M<sub>xy</sub> = M<sub>0</sub>e<sup>−TE/T2</sup>. A long TE separates the tissues by T2, and CSF is bright. The 180° pulse makes the echo.', 'te-decay')],
    [('An inversion pulse inverts M<sub>z</sub>, and it passes through zero at t = T1 ln 2. Starting the sequence then nulls that tissue: CSF in FLAIR.', 'inversion-recovery')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
PROBLEMS += [
    SORT("Is the tissue bright or dark on each type of image?", ["Bright", "Dark"],
         [("CSF on a T2-weighted image", 0), ("Fat on a T1-weighted image", 0), ("CSF on a T1-weighted image", 1), ("Brain on a T2-weighted image, relative to CSF", 1), ("CSF on a FLAIR image", 1), ("A tumour enhanced by gadolinium on a T1-weighted image", 0)],
         "CSF has a long T1 and a long T2, so it is dark on T1 and bright on T2. Fat has a short T1, so it is bright on T1. FLAIR nulls the CSF. Gadolinium shortens T1 and brightens an enhanced tumour.", lvl="Moderate"),
]
INLINE = {0: [2, 3, 5], 1: [1, 4, 7], 2: [9, 10]}
