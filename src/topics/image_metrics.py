from blocks import *
import math

# ---------------------------------------------------------------- this chapter's formulas

def nyquist(pitch):
    """Nyquist frequency (lp/mm) for a pixel pitch in mm."""
    return 1 / (2 * pitch)

def alias(f, pitch):
    """Frequency (lp/mm) at which a pattern of frequency f appears after sampling at the pitch, folded into 0 to f_N."""
    fs = 1 / pitch; r = f % fs
    return min(r, fs - r)

def aperture(f, a):
    """MTF of a square pixel aperture of width a (mm) at f (lp/mm): |sin(πaf) / (πaf)|."""
    x = math.pi * a * f
    return abs(math.sin(x) / x) if x else 1.0

def cascade(*mtfs):
    """System MTF of stages in series: the product of their MTFs."""
    return math.prod(mtfs)

def neq(mtf, nnps):
    """Noise-equivalent quanta (photons per mm²): MTF² / NNPS, with NNPS in mm²."""
    return mtf ** 2 / nnps

def dqe(mtf, nnps, q):
    """Detective quantum efficiency: MTF² / (q × NNPS), with q the incident fluence in photons per mm²."""
    return neq(mtf, nnps) / q

def kerma_same_snr(k_a, dqe_a, dqe_b):
    """Air kerma that a detector of DQE dqe_b needs to match the SNR that one of DQE dqe_a gives at k_a: SNR² ∝ K × DQE."""
    return k_a * dqe_a / dqe_b

# ---------------------------------------------------------------- worked examples
P2, F2 = 0.20, 3.5                                  # pixel pitch (mm) and pattern frequency (lp/mm)
fn2, fs2, al2, ap2 = nyquist(P2), 1 / P2, alias(F2, P2), aperture(F2, P2)
K3, QK, M3, N3 = 2.5, 30000.0, 0.62, 1.14e-5        # µGy; photons mm⁻² µGy⁻¹; MTF and NNPS (mm²) at 1.0 lp/mm
q3 = K3 * QK; neq3 = neq(M3, N3); dqe3 = dqe(M3, N3, q3)
KA4, DA4, DB4 = 2.0, 0.65, 0.30                     # µGy for detector A; DQE of A and of B at low frequency
kb4 = kerma_same_snr(KA4, DA4, DB4); half4 = math.sqrt(0.5)

# ---------------------------------------------------------------- numbers in the questions
P_N = 0.125; fn_q = nyquist(P_N)
P_A, F_A = 0.40, 1.75; al_q = alias(F_A, P_A); fn_a = nyquist(P_A)
C_FS, C_SC, C_AP = 0.90, 0.55, 0.80                 # MTFs at 2.0 lp/mm in the detector plane
sys_q = cascade(C_FS, C_SC, C_AP); loss_q = 1 - ((1 - C_FS) + (1 - C_SC) + (1 - C_AP)); mean_q = (C_FS + C_SC + C_AP) / 3
S_OBJ, S_BG, SD_BG = 520.0, 480.0, 16.0
cnr_q = abs(S_OBJ - S_BG) / SD_BG
KA20, DA20, DB20 = 2.5, 0.60, 0.25
kb20 = kerma_same_snr(KA20, DA20, DB20)
kb20_sqrt, kb20_inv, kb20_sq = KA20 * math.sqrt(DA20 / DB20), KA20 * DB20 / DA20, KA20 * (DA20 / DB20) ** 2

TOPIC = dict(
    id="image-metrics", domain=4, sub="IV.A", title="Spatial resolution, noise power, and DQE",
    ref=dict(aapm="", khan="", ford="19"),
    guide=[
        H("Spread functions and the MTF"),
        P("Blur is described by the point spread function (PSF), line spread function (LSF), and edge spread function (ESF), the images of a point, a narrow line, and a sharp edge. The LSF is the PSF summed along the line and the derivative of the ESF across the edge."),
        TABLE(["Function", "Image of", "Test object"],
              [["PSF", "A point", "A pinhole in a metal plate; in CT, a thin wire along the scanner axis"],
               ["LSF", "A line", "A slit much narrower than a pixel, in a metal plate"],
               ["ESF", "An edge", "A plate of a dense metal such as tungsten, with a straight polished edge"]]),
        P("The modulation transfer function (MTF) is the magnitude of the Fourier transform of the LSF, normalized to 1 at zero frequency. Frequency is in line pairs (one bar and one gap) per mm, lp/mm, equal to cycles per mm. MTF(f) is the fraction of the modulation of a sinusoid of frequency f that reaches the image."),
        EQ("MTF(f) = |∫ LSF(x) e<sup>−2πifx</sup> dx| / ∫ LSF(x) dx",
           "modulation M = (max − min) / (max + min),   M<sub>image</sub>(f) = MTF(f) × M<sub>object</sub>(f)"),
        P("f<sub>50</sub> and f<sub>10</sub>, the frequencies at which the MTF falls to 0.5 and 0.1, summarize the curve; f<sub>10</sub> is often quoted as the limiting resolution."),

        H("Sampling, aliasing, and cascaded blur"),
        P("A detector samples the image once per pixel pitch Δ. The highest frequency it can represent is the Nyquist frequency, f<sub>N</sub> = 1/(2Δ), at which one bar spans one pixel. A frequency f between f<sub>N</sub> and 2f<sub>N</sub> reappears at 2f<sub>N</sub> − f as a coarser false pattern, and noise above f<sub>N</sub> folds back the same way: aliasing."),
        P("The presampling MTF covers the blur before sampling, in the converter and the pixel aperture, independent of where an object falls against the pixels. It is measured with an edge or slit tilted a few degrees from the pixel columns, so that the rows together sample it finely."),
        P("The blurs of stages in series, such as the focal spot, scintillator, and pixel aperture, convolve, so their MTFs multiply; the system MTF is never above that of the weakest stage."),
        EQ("f<sub>N</sub> = 1 / (2Δ),   a frequency f between f<sub>N</sub> and 2f<sub>N</sub> appears at 2f<sub>N</sub> − f",
           f"square aperture of width a:   MTF(f) = |sin(πaf) / (πaf)|,   {aperture(nyquist(1.0), 1.0):.2f} at f<sub>N</sub> when a = Δ",
           "MTF<sub>system</sub>(f) = MTF<sub>1</sub>(f) × MTF<sub>2</sub>(f) × MTF<sub>3</sub>(f) × …"),
        EX("Nyquist frequency and an alias", STEM("A kilovoltage flat panel with square pixels images a sinusoidal test pattern.", [f"pixel pitch Δ = {P2:.2f} mm, with an aperture as wide as the pitch", f"pattern frequency = {F2:.1f} lp/mm"], "Find the [[Nyquist frequency]] and the [[frequency at which the pattern appears]]."),
           [f"f<sub>N</sub> = 1 / (2 × {P2:.2f} mm) = {fn2:.2f} lp/mm, and the sampling frequency 1/Δ = {fs2:.1f} lp/mm",
            f"{F2:.1f} lp/mm lies between f<sub>N</sub> and 2f<sub>N</sub>, so it appears at 2f<sub>N</sub> − f = {fs2:.1f} − {F2:.1f} = {al2:.1f} lp/mm",
            f"The aperture alone passes |sin(π × {P2:.2f} × {F2:.1f}) / (π × {P2:.2f} × {F2:.1f})| = {ap2:.2f} of the modulation, so the false pattern reaches the image unless the converter blur removes it"],
           f"f<sub>N</sub> = {fn2:.2f} lp/mm. The pattern appears at {al2:.1f} lp/mm, with a period of {1 / al2:.2f} mm in place of {1 / F2:.2f} mm."),

        H("Noise and the noise power spectrum"),
        P("Noise is the random variation of pixel values about their mean in a uniformly exposed image, measured as the variance σ² in a region of interest; its sources scale differently with the exposure X."),
        TABLE(["Source", "Variance", "Relative noise σ/S", "Dominant at"],
              [["Quantum (Poisson)", "∝ X", "∝ 1/√X", "Most clinical exposures"],
               ["Electronic (readout)", "Independent of X", "∝ 1/X", "Low exposure"],
               ["Fixed pattern (gain differences between pixels)", "∝ X²", "Independent of X", "High exposure, unless a flat-field correction removes it"]]),
        P("The contrast-to-noise ratio, CNR = |S<sub>object</sub> − S<sub>background</sub>| / σ<sub>background</sub>, measures how far an object stands out from noise."),
        P("The noise power spectrum (NPS), or Wiener spectrum, divides the variance among spatial frequencies, and its integral is σ². Uncorrelated noise has a flat (white) NPS; scintillator blur makes the quantum NPS fall with frequency."),
        P("Divided by the square of the mean signal, the NPS of flat-field images becomes the normalized NPS (NNPS), in mm². A detector that counts every photon without blur has NNPS = 1/q, with q the incident fluence in photons per mm²."),
        EQ("NPS(u, v) = (Δx Δy / N<sub>x</sub>N<sub>y</sub>) ⟨|DFT[I(x, y) − Ī]|²⟩, averaged over many regions of N<sub>x</sub> × N<sub>y</sub> pixels",
           "σ² = ∫∫ NPS(u, v) du dv,   NNPS(f) = NPS(f) / S̄²"),

        H("Detective quantum efficiency"),
        P("NEQ(f) = MTF²(f)/NNPS(f), the noise-equivalent quanta, is the fluence in photons per mm² that an ideal detector would need to give the same SNR at frequency f. The detective quantum efficiency (DQE) divides it by the incident fluence q."),
        EQ("NEQ(f) = MTF²(f) / NNPS(f)",
           "DQE(f) = NEQ(f) / q = MTF²(f) / [q × NNPS(f)] = SNR²<sub>out</sub>(f) / SNR²<sub>in</sub>(f)",
           "q = K<sub>a</sub> × (q / K<sub>a</sub>),   SNR²<sub>in</sub> = q per unit area"),
        P(f"A DQE of 0.5 means the image has the SNR² that an ideal detector (DQE = 1) would give from half the photons: the SNR is √0.5 = {math.sqrt(0.5):.2f} of the ideal, and matching the ideal takes twice the exposure. DQE(0) cannot exceed the fraction of x-rays that interact, and the spread in light or charge per absorbed x-ray and the electronic noise lower it further."),
        P("DQE falls with frequency, and at low exposure, where electronic noise becomes a larger share of the total. DQE(0) is about 0.6 to 0.8 for a kilovoltage flat panel with a caesium iodide scintillator and about 0.01 for a megavoltage portal imager, which stops only a few percent of the photons."),
        P("Linear processing after readout, such as edge enhancement, multiplies the MTF by the filter gain and the NPS by its square, so the NEQ and DQE do not change; processing alters the look of the image, not its information."),
        EX("DQE at one frequency", STEM("The DQE of a flat-panel detector is measured at 1.0 lp/mm.", [f"air kerma at the detector = {K3:.1f} µGy", f"photon fluence per unit air kerma for this beam = {QK:,.0f} mm<sup>−2</sup> µGy<sup>−1</sup>", f"MTF(1.0 lp/mm) = {M3:.2f}", f"NNPS(1.0 lp/mm) = {sci(N3, 3)} mm²"], "Find the [[NEQ]] and the [[DQE]] at 1.0 lp/mm."),
           [f"q = {K3:.1f} µGy × {QK:,.0f} mm<sup>−2</sup> µGy<sup>−1</sup> = {q3:,.0f} photons/mm²",
            f"NEQ = MTF² / NNPS = {M3 ** 2:.4f} / ({sci(N3, 3)} mm²) = {neq3:,.0f} photons/mm²",
            f"DQE = NEQ / q = {neq3:,.0f} / {q3:,.0f}"],
           f"NEQ ≈ {round(neq3, -2):,.0f} photons/mm² and DQE = {dqe3:.2f}: the image has the SNR that an ideal detector would give with {100 * dqe3:.0f}% of the photons."),

        H("Detectability and trade-offs"),
        P("In the Rose model, an object of area A and low contrast C, imaged with a fluence q, has SNR = C√(qA), the difference in counts over its area divided by the Poisson noise of the background count. Rose found that reliable detection needs an SNR of about 5. A real detector replaces q by the NEQ, q × DQE."),
        P("Halving the pixel width at the same exposure quarters the photons in each pixel and halves the SNR per pixel. A thicker scintillator raises DQE(0) but lowers the MTF and the DQE at high frequency."),
        EQ("SNR = C √(q A),   reliable detection at SNR ≈ 5 (Rose)",
           "for a given SNR:   K<sub>a</sub> ∝ 1 / DQE"),
        EX("Air kerma for the same SNR", STEM("Two quantum-limited detectors image the same large, low-contrast object. Detector A gives the required SNR at 2.0 µGy.", [f"DQE of A at low frequency = {DA4:.2f}", f"DQE of B at low frequency = {DB4:.2f}"], "Find the [[air kerma that B needs for the same SNR]], and the [[change in the SNR of A when its air kerma is halved]]."),
           ["SNR² ∝ q × DQE, and q is proportional to the air kerma",
            f"B: K<sub>a</sub> = {KA4:.1f} µGy × {DA4:.2f} / {DB4:.2f} = {kb4:.2f} µGy",
            f"A at {KA4 / 2:.1f} µGy: the SNR changes by √({KA4 / 2:.1f} / {KA4:.1f}) = {half4:.3f}"],
           f"{kb4:.1f} µGy for B, {kb4 / KA4:.2f} times the air kerma of A. Halving the air kerma of A lowers its SNR by {100 * (1 - half4):.0f}%."),
    ],
    cards=[
        F("Point, line, and edge spread functions", ["PSF: the image of a point.", "LSF: the image of a narrow line, the PSF summed along it.", "ESF: the image of a sharp edge. Its derivative is the LSF."]),
        F("Modulation transfer function", "The magnitude of the Fourier transform of the LSF, normalized to 1 at zero frequency. MTF(f) is the fraction of the modulation of a sinusoid of frequency f, in lp/mm, that reaches the image."),
        F("Nyquist frequency", "f<sub>N</sub> = 1/(2Δ) for a pixel pitch Δ. At f<sub>N</sub> each bar of a bar pattern spans one pixel."),
        F("Aliasing", "A frequency f between f<sub>N</sub> and 2f<sub>N</sub> appears at 2f<sub>N</sub> − f as a coarser false pattern. Noise above f<sub>N</sub> folds back the same way."),
        F("Cascaded blur", "The MTFs of stages in series multiply, so the system MTF is never above that of its weakest stage."),
        F("Noise sources and exposure", ["Quantum noise: variance ∝ X.", "Electronic noise: variance independent of X, dominant at low exposure.", "Fixed-pattern noise: variance ∝ X², largely removed by a flat-field correction."]),
        F("Noise power spectrum", "The noise variance per unit spatial frequency, also called the Wiener spectrum. Its integral is the pixel variance, and divided by the square of the mean signal it becomes the NNPS, in mm²."),
        F("Noise-equivalent quanta and DQE", "NEQ(f) = MTF²(f) / NNPS(f), the fluence an ideal detector needs for the same SNR. DQE(f) = NEQ(f) / q, with q the incident photon fluence."),
        F("Meaning of the DQE", "The ratio SNR²<sub>out</sub> / SNR²<sub>in</sub>. For a given SNR the exposure scales as 1/DQE, so a DQE of 0.5 needs twice the exposure of an ideal detector."),
        F("Rose model of detectability", "SNR = C√(qA) for an object of area A and low contrast C at fluence q. Reliable detection needs an SNR of about 5."),
    ],
)

PROBLEMS = [
    # ---- 1-2: spread functions and the MTF
    PR(STEM("The line spread function of a detector is measured with a narrow slit.", [], "How is the [[MTF]] obtained from it?"),
       "The magnitude of its Fourier transform, divided by the value at zero frequency", ["Its derivative across the slit, divided by its maximum value", "Its running integral across the slit, divided by its total area", "The inverse of its full width at half maximum, in lp/mm"],
       "The MTF is the magnitude of the Fourier transform of the LSF, normalized to 1 at zero frequency. Differentiating an ESF gives the LSF, integrating the LSF gives the ESF, and the inverse of the width is one rough number, not a curve.", lvl="Easy"),
    PR(STEM("A detector has an MTF of 0.40 at 2 lp/mm.", [], "What does this value mean?"),
       "A sinusoidal pattern of 2 lp/mm keeps 40% of its modulation in the image", ["40% of the photons in a pattern of 2 lp/mm reach the detector", "Details 0.40 mm wide are the smallest that can be resolved", "The noise at 2 lp/mm is 40% of the signal at that frequency"],
       "MTF(f) is the output modulation divided by the input modulation for a sinusoid of frequency f. It describes the transfer of contrast, not the fraction of photons detected, not a smallest size, and not the noise, which the NPS describes.", lvl="Easy"),
    # ---- 3-5: sampling, aliasing, and cascaded blur
    PRN(STEM("A flat-panel detector for radiography has a square grid of pixels.", [f"pixel pitch = {P_N:.3f} mm"], "What is the [[Nyquist frequency]]?"), fn_q, [2 * fn_q, fn_q / 2, 10 * fn_q], "{:g} lp/mm",
        f"f<sub>N</sub> = 1/(2Δ) = 1 / (2 × {P_N:.3f} mm) = {fn_q:g} lp/mm. The sampling frequency 1/Δ = {2 * fn_q:g} lp/mm is twice the Nyquist frequency.", lvl="Easy"),
    PRN(STEM("A portal imager with square pixels images a sinusoidal test pattern. Its presampling MTF at the frequency of the pattern is above zero.", [f"pixel pitch = {P_A:.2f} mm", f"pattern frequency = {F_A:.2f} lp/mm"], "At what [[frequency]] does the pattern appear in the image?"),
        al_q, [F_A - fn_a, fn_a, F_A], "{:.2f} lp/mm",
        f"f<sub>N</sub> = 1 / (2 × {P_A:.2f}) = {fn_a:.2f} lp/mm, so {F_A:.2f} lp/mm lies above it and appears at 2f<sub>N</sub> − f = {2 * fn_a:.2f} − {F_A:.2f} = {al_q:.2f} lp/mm. Subtracting f<sub>N</sub> from f gives {F_A - fn_a:.2f}, and a pattern above f<sub>N</sub> cannot appear at its own frequency.", lvl="Moderate"),
    PRN(STEM("Three stages blur a radiograph. Their MTFs at 2.0 lp/mm, all referred to the detector plane, are known.", [f"focal spot = {C_FS:.2f}", f"scintillator = {C_SC:.2f}", f"pixel aperture = {C_AP:.2f}"], "What is the [[system MTF]] at 2.0 lp/mm?"),
        sys_q, [loss_q, C_SC, mean_q], "{:.2f}",
        f"The spread functions convolve, so the MTFs multiply: {C_FS:.2f} × {C_SC:.2f} × {C_AP:.2f} = {sys_q:.3f}. Subtracting each loss from 1 gives {loss_q:.2f}, the weakest stage alone gives {C_SC:.2f}, and the mean gives {mean_q:.2f}.", lvl="Moderate"),
    # ---- 6: noise
    TYPED(STEM("Regions of interest are drawn in an image, one inside a low-contrast object and one in the background beside it.", [f"mean in the object = {S_OBJ:.0f}", f"mean in the background = {S_BG:.0f}", f"standard deviation in the background = {SD_BG:.0f}"], "What is the [[CNR]]?"), cnr_q, 0.02, "(ratio)",
          f"CNR = |{S_OBJ:.0f} − {S_BG:.0f}| / {SD_BG:.0f} = {cnr_q:.1f}. Dividing by the variance, {SD_BG ** 2:.0f}, gives {(S_OBJ - S_BG) / SD_BG ** 2:.2f}, and dividing by the background mean gives the contrast, {(S_OBJ - S_BG) / S_BG:.3f}.", lvl="Easy"),
    # ---- 7-10: detective quantum efficiency
    SORT("Match each quantity to its definition.", ["MTF", "NNPS", "NEQ", "DQE"],
         [("Fraction of the modulation of a sinusoid kept at each frequency", 0), ("Noise variance per unit frequency, divided by the square of the mean signal", 1), ("Fluence that an ideal detector would need to give the same SNR", 2), ("Output SNR squared divided by input SNR squared", 3)],
         "The MTF describes the transfer of signal and the NNPS the noise relative to the signal. Their ratio MTF²/NNPS is the NEQ, and the NEQ divided by the incident fluence is the DQE, the ratio of the squared SNRs.", lvl="Easy", mode="match", cap=1),
    PR(STEM("A detector has a DQE of 0.50 at low frequency.", [], "Compared with an ideal detector at the same exposure, what does this mean for a large object?"),
       f"Its SNR is {math.sqrt(0.5):.2f} of the ideal; twice the exposure matches the ideal detector", ["Its SNR is 0.50 of the ideal; four times the exposure matches the ideal detector", "Its noise is 0.50 of the ideal; half the exposure matches the ideal detector", "Its MTF at zero frequency is 0.50; large objects keep half their contrast"],
       f"DQE is a ratio of squared SNRs, so the SNR is √0.50 = {math.sqrt(0.5):.2f} of the ideal, and twice the photons raise SNR² by 2 to match it. Reading the DQE as a ratio of SNRs gives half and four times, and the MTF at zero frequency is 1 by definition.", lvl="Moderate"),
    PRM(STEM("An indirect flat-panel detector, a scintillator on a photodiode array, has a DQE well below 1.", [], "Which of these lower its DQE?"),
        ["Some x-rays pass through the scintillator without interacting", "The light produced varies from one absorbed x-ray to the next", "Electronic noise is added when the pixels are read out"],
        ["Edge enhancement is applied to the image before display", "The image is displayed with a narrow window", "A flat-field correction is applied to each image"],
        "X-rays that do not interact carry no information, which caps DQE(0) at the fraction that interact, and the spread in light per x-ray and the readout noise add noise that the incident photons did not have. Linear processing scales the MTF² and the NPS alike, the window changes only the display, and the flat-field correction removes most of the fixed-pattern noise.", lvl="Challenging"),
    PR(STEM("Edge-enhancement processing is applied to a radiograph after readout. At 2.0 lp/mm it doubles the MTF.", [], "What happens to the [[DQE]] at 2.0 lp/mm?"),
       "It is unchanged, because the NPS there rises fourfold", ["It doubles, because the DQE rises with the MTF", "It rises fourfold, because the DQE follows the MTF squared", "It halves, because the filter amplifies the noise"],
       "A linear filter multiplies the MTF by its gain H and the NPS by H². With H = 2 both the MTF² and the NPS rise fourfold, so the NEQ and the DQE are unchanged: processing cannot add information the detector did not record. Counting the MTF² alone gives the factor of 4.", lvl="Challenging"),
    # ---- 11-12: detectability and trade-offs
    PRN(STEM("Two quantum-limited detectors with the same pixel size are compared for a large, low-contrast object, whose SNR is set by the DQE at low frequency. Detector A gives the required SNR at 2.5 µGy.", [f"DQE of A at low frequency = {DA20:.2f}", f"DQE of B at low frequency = {DB20:.2f}"], "What [[air kerma]] does detector B need for the same SNR?"),
        kb20, [kb20_sqrt, kb20_inv, kb20_sq], "{:.1f} µGy",
        f"SNR² is proportional to the air kerma times the DQE, so K<sub>B</sub> × {DB20:.2f} = {KA20:.1f} × {DA20:.2f} and K<sub>B</sub> = {kb20:.1f} µGy. The square root of the DQE ratio gives {kb20_sqrt:.1f}, the inverted ratio gives {kb20_inv:.1f}, and the squared ratio gives {kb20_sq:.1f} µGy.", lvl="Challenging"),
    PR(STEM("In the Rose model, a low-contrast disk is at the limit of detection. A second disk has half its diameter and the same contrast.", [], "What change in the [[photon fluence]] keeps the SNR of the smaller disk at that limit?"),
       "Four times the fluence, to keep the photon count over its area", ["Twice the fluence, to keep the photon count along its diameter", "Sixteen times the fluence, because the SNR falls as the square of the area", "The same fluence, because the contrast of the disk is unchanged"],
       "SNR = C√(qA), and halving the diameter divides the area by 4, so q must rise by 4 to keep qA. Scaling with the diameter gives twice, and the SNR depends on the square root of the area, not its square.", lvl="Moderate"),
]

INLINE = {0: [1, 2], 1: [3, 4, 5], 2: [6], 3: [7, 8]}       # the rest form the practice set

TERMS = ["line spread function", "modulation transfer function", "Nyquist frequency", "aliasing", "presampling MTF", "noise power spectrum", "noise-equivalent quanta", "detective quantum efficiency"]

TAKE = [
    ["The LSF is the PSF summed along a line and the derivative of the ESF.",
     "MTF(f) is the Fourier transform of the LSF normalized to 1 at f = 0: the fraction of a sinusoid's modulation kept at f, in lp/mm."],
    ["f<sub>N</sub> = 1/(2Δ). A frequency between f<sub>N</sub> and 2f<sub>N</sub> appears at 2f<sub>N</sub> − f, and noise aliases too.",
     "The MTFs of stages in series multiply."],
    ["Variance: quantum ∝ X, electronic independent of X, fixed pattern ∝ X². CNR = |ΔS| / σ.",
     "The NPS spreads the variance over frequency. NNPS = NPS / S̄², which is 1/q for an ideal photon counter."],
    ["DQE(f) = MTF²(f) / [q × NNPS(f)] = NEQ / q = SNR²<sub>out</sub> / SNR²<sub>in</sub>.",
     "DQE falls with frequency and at low exposure. Linear processing leaves it unchanged.",
     "DQE(0) is about 0.6 to 0.8 for a kV flat panel with caesium iodide and about 0.01 for an MV portal imager."],
    ["Rose: SNR = C√(qA), and reliable detection needs about 5. Half the diameter needs four times the fluence.",
     "For a given SNR the exposure scales as 1/DQE."],
]
