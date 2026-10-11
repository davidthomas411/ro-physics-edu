from blocks import *
import math, calc, gal, real
import nistdata as N
DS = gal.DRR_ST
RX = real.STATS["dx"]["dx"]                                                      # read from the DICOM header of a real radiograph: tools/make_real_dx.py

# the bone-to-soft-tissue contrast: 10 cm of soft tissue (water) in which 2 cm is replaced by cortical bone, compared with 10 cm of soft tissue alone
ratio_bone = lambda E: math.exp(2 * (N.BONE[E][0] * 1.92 - N.WATER[E][0] * 1.00))          # E in MeV, a tabulated energy
r30, r50, r100, r125 = ratio_bone(0.03), ratio_bone(0.05), ratio_bone(0.1), ratio_bone(1.25)
mag = lambda a, b: (a + b) / a                                                             # a = source to object, b = object to detector
blur = lambda s, a, b: s * b / a                                                           # penumbra of a sharp edge for a source of size s
m_a, b_a = mag(90, 10), blur(1.0, 90, 10)
m_b, b_b = mag(70, 30), blur(1.0, 70, 30)
mas_sid = lambda mas, d1, d2: mas * (d2 / d1) ** 2                                       # the mAs that keeps the exposure at the receptor when the distance changes from d1 to d2
mas_far = mas_sid(20, 100, 140)
npix = lambda mas: 2000 * mas                                                              # photons per pixel, illustrative: 2000 per mAs
snr = lambda n: math.sqrt(n)
skin = lambda kvp, mas: mas * kvp ** 2                                                     # exposure at the skin is proportional to mA x kVp^2

TOPIC = dict(
    id="radiographic-quality", domain=4, sub="IV.A", title="Radiographic image quality",
    ref=dict(aapm="TG-58", khan="", ford="19"),
    guide=[
        H("Contrast"),
        P("Radiographic imaging means imaging with x-ray photons that are transmitted through the patient, which includes planar x-ray images and CT. One goal is to tell materials apart, for example bone from muscle. Photons from the source pass through the patient and some are transmitted to the detector, which might be film or an electronic portal imaging device (EPID). The contrast is the difference in how much the paths through different materials transmit."),
        P("For a narrow monoenergetic beam the transmitted fluence is I = I₀ e<sup>−μx</sup>. Compare 10 cm of soft tissue with 10 cm in which 2 cm has been replaced by bone. The ratio of the transmitted fluences measures the contrast, and it depends strongly on the photon energy. At low energy the photoelectric effect, which depends on Z<sup>3</sup>/E<sup>3</sup>, attenuates bone far more than soft tissue. At megavoltage energies there is very little Z-dependence in the mass attenuation coefficient, so any contrast comes from density alone."),
        EX("Contrast at two energies", STEM("10 cm of water, compared with 8 cm of water and 2 cm of cortical bone (density 1.92 g/cm³).", ["30 keV: μ/ρ = 0.3756 cm²/g for water and 1.331 cm²/g for bone", "1.25 MeV: μ/ρ = 0.06323 cm²/g for water and 0.05871 cm²/g for bone"], "Find the [[contrast ratio]] at each energy."), ["Ratio = e<sup>(μ<sub>bone</sub> − μ<sub>water</sub>) × 2 cm</sup>, with μ = (μ/ρ) × ρ", "30 keV: μ<sub>bone</sub> = 1.331 × 1.92 = 2.556 cm<sup>−1</sup>, so the exponent is (2.556 − 0.376) × 2 = 4.36", "1.25 MeV: μ<sub>bone</sub> = 0.05871 × 1.92 = 0.1127 cm<sup>−1</sup>, so the exponent is (0.1127 − 0.0632) × 2 = 0.099"], f"{r30:.0f} at 30 keV and {r125:.2f} at 1.25 MeV. The bone is easy to see at kilovoltage energy and hard to see at megavoltage energy, which is why a kV image shows much better contrast than an MV image of the same patient."),

        P(f"The figure shows the same effect on a real patient. It is an AP radiograph simulated from the CT volume of a head-and-neck patient, made once with a kilovoltage spectrum and once with a megavoltage spectrum. Replacing 2 cm of water by 2 cm of bone changes −ln(I) by {DS['c_kv']:.2f} at kV and {DS['c_mv']:.3f} at MV, a factor of {DS['c_kv'] / DS['c_mv']:.0f}. With the same soft-tissue window, the bone region differs from the soft-tissue region by {100 * DS['gray_kv'] / 255:.0f}% of the display range at kV and {100 * DS['gray_mv'] / 255:.0f}% at MV."),
        AVF("drr-gallery-contrast"),
        H("Resolution and magnification"),
        P("Spatial resolution describes whether objects look sharp or blurry. The edge of a high-contrast object, such as a bone, is blurred by the size of the source in the way that a penumbra is. For a source of size s at a distance a from the object, with the detector a distance b behind the object, the blur is proportional to s·b/a. The blur falls as the object is moved closer to the detector."),
        P("The object also appears larger on the detector, because the rays diverge. By similar triangles an object of size r appears as R, with R/r = (a + b)/a, and the magnification is m = 1 + b/a. Moving the object away from the detector raises the magnification and worsens the resolution. There is a trade-off between the two."),
        EQ("blur = s · b / a   m = (a + b) / a = 1 + b / a", "s = source size,   a = source to object,   b = object to detector"),
        EX("Magnification and blur", STEM("A 1.0 mm source with a source-to-detector distance of 100 cm.", ["case 1: the object is 10 cm from the detector, so a = 90 cm", "case 2: the object is 30 cm from the detector, so a = 70 cm"], "Find the [[magnification]] and the [[blur]] in each case."), ["m = (a + b) / a and blur = s·b/a", "Case 1: m = 100 / 90, blur = 1.0 × 10 / 90", "Case 2: m = 100 / 70, blur = 1.0 × 30 / 70"], f"Case 1: m = {m_a:.2f}, blur = {b_a:.2f} mm. Case 2: m = {m_b:.2f}, blur = {b_b:.2f} mm. Moving the object away from the detector magnifies it and blurs it."),

        H("Detectors, noise, and exposure"),
        P("The detector affects resolution too. In an EPID a photon most often interacts in a conversion layer, a copper plate, by Compton scattering, which releases an electron. The electron produces light in a scintillator layer, typically a rare-earth material such as gadolinium oxysulfide. A photodiode array of amorphous silicon registers the light as a charge that is roughly proportional to the number of photons. Each pixel is read out in turn: gate lines select a row, the data lines carry the charge from each pixel, and the image is read row by row. A thicker conversion layer or scintillator detects more photons, but it spreads the light over a larger area and blurs the image. The modulation transfer function describes this trade-off, and it gives the response of the detector for features of different spatial frequency."),
        P("Noise is how grainy an image looks. In x-ray imaging the main source is the random fluctuation in the number of photons registered in a pixel, which follows the Poisson distribution. For a mean of N photons the standard deviation is √N. That is the noise, and N is the signal, so the signal-to-noise ratio is N/√N = √N. More photons give a higher SNR. The user can raise the number of photons with a longer exposure, a higher mA, or a higher kVp, or by imaging a thinner part of the body. The cost is exposure to the patient: the exposure at the skin is proportional to mA·kVp², while the exposure transmitted through the patient rises faster with kVp, roughly as the fifth power."),
        EX("Signal-to-noise ratio", STEM("A pixel registers an average of 10,000 photons.", [], "Find the [[noise]] and the [[SNR]], and the SNR if the exposure is quadrupled."), ["Noise = √N = √10,000", "SNR = N / √N = √N", "4 × the exposure gives 40,000 photons"], f"Noise = {snr(10000):.0f} photons, SNR = {snr(10000):.0f}. With 40,000 photons the SNR is {snr(40000):.0f}, twice as high: the SNR grows as the square root of the exposure."),
        P("On film, the darkening is measured as the optical density, the base-10 logarithm of the ratio of the light that falls on the film to the light that passes through it. The film darkens more as the exposure to it rises, so at a fixed kVp and distance the mAs sets the darkness. The exposure at the receptor also falls with the square of the source-to-detector distance, so a longer distance needs more mAs: mAs<sub>2</sub> = mAs<sub>1</sub> (d<sub>2</sub> / d<sub>1</sub>)<sup>2</sup>. A digital detector responds over a much wider range and its image is rescaled for display, so a higher exposure does not darken the image. It lowers the noise instead, and an exposure index reports how much exposure the detector received."),

        P(f"The figure shows the noise in the same radiograph at three exposures. When the exposure falls by a factor of 16, the noise in −ln(I) rises {DS['noise_low'] / DS['noise_high']:.1f} times, close to the factor of 4 that 1/√exposure predicts, and the grain starts to hide the weak contrast."),
        AVF("drr-gallery-noise"),
        P(f"A real radiograph shows what the exposure factors are in practice. The portable chest image below was made at {RX['kvp']:g} kVp and {RX['mas']:.1f} mAs in {RX['ms']:g} ms, on a flat-panel detector with a scintillator, and with no anti-scatter grid. The factors are stored in the DICOM header. The matrix is {RX['cols']} × {RX['rows']} pixels of {RX['pixel_mm']:.3f} mm, a field of {RX['cols'] * RX['pixel_mm'] / 10:.0f} × {RX['rows'] * RX['pixel_mm'] / 10:.0f} cm, and each pixel is stored with {RX['stored']} bits."),
        AVF("real-dx-chest"),
        H("Scatter and grids"),
        P("Some photons scatter in the patient before they reach the detector. They do not travel in a straight line from the source, so they carry no information about what lies along the path. Scatter raises the signal but it is an unwanted signal, and it lowers the contrast and the SNR. Scatter depends on the geometry. If the patient is farther from the detector, fewer scattered photons reach it. A thinner part of the body, and a smaller field, give less scatter."),
        P("A grid reduces scatter. It consists of thin metal fins arranged to point back toward the source. A photon travelling along a line to the source passes between the fins. A scattered photon does not, so it is stopped by the fins and does not reach the detector."),
        P(f"The figure shows scatter and a grid on the same radiograph. With a scatter-to-primary ratio of {DS['SPR']:.0f}, the contrast between the bone region and the soft-tissue region falls to {DS['con_scatter'] / DS['con_primary']:.2f} of its primary-only value. A grid that passes {100 * DS['TP']:.0f}% of the primary photons and {100 * DS['TS']:.0f}% of the scattered photons restores it to {DS['con_with_grid'] / DS['con_primary']:.2f}, at the cost of {DS['bucky']:.1f} times the exposure. That ratio of the exposures is the Bucky factor."),
        AVF("drr-gallery-scatter"),
    ],
    cards=[
        F("Contrast in radiography", "The difference in transmission between paths through different materials, for example bone and muscle."),
        F("Contrast and photon energy", "Contrast between bone and soft tissue is much larger at kilovoltage energy than at megavoltage energy, because of the photoelectric effect."),
        F("Contrast at megavoltage energy", "Little Z-dependence in the mass attenuation coefficient, so contrast comes from density alone."),
        F("Resolution and source size", "The edge of a high-contrast object blurs by s·b/a, with s the source size, a the source to object distance, and b the object to detector distance."),
        F("Magnification", "m = (a + b)/a = 1 + b/a. It rises as the object moves away from the detector."),
        F("Magnification and resolution trade-off", "Moving the object away from the detector magnifies it and worsens the resolution."),
        F("EPID layers", "A copper conversion plate (Compton electrons), a scintillator such as gadolinium oxysulfide, and an amorphous-silicon photodiode array."),
        F("EPID readout", "Gate lines select a row and data lines carry the charge from each pixel. The image is read row by row."),
        F("Thickness trade-off in a detector", "A thicker conversion layer or scintillator detects more photons but spreads the light and blurs the image. The modulation transfer function quantifies it."),
        F("Noise in x-ray imaging", "Random fluctuation in the number of photons per pixel, a Poisson process: for a mean N the noise is √N."),
        F("Signal-to-noise ratio", "SNR = N/√N = √N. Four times the photons doubles the SNR."),
        F("Exposure scaling", "Exposure at the skin is proportional to mA·kVp². Transmitted exposure rises faster with kVp, roughly as the fifth power."),
        F("Scatter in radiography", "Scattered photons add signal without information, and lower the contrast and SNR. Less with a thinner patient, a smaller field, and a larger air gap."),
        F("Anti-scatter grid", "Thin metal fins pointing to the source. Primary photons pass between them and scattered photons are stopped."),
    ],
)

PROBLEMS = [
    PR("Bone and soft tissue show better contrast on a kV image than on an MV image because at kV energies:", "the photoelectric effect depends strongly on atomic number", ["Compton scattering depends strongly on atomic number", "pair production is larger", "the beam is more penetrating"],
       "The photoelectric effect varies as Z<sup>3</sup>/E<sup>3</sup>, so bone attenuates much more than soft tissue at low energy.", lvl="Easy"),
    PR("In a megavoltage image, differences in contrast between materials are caused mainly by differences in:", "density", ["atomic number", "photoelectric absorption", "pair production"],
       "There is little Z-dependence of the mass attenuation coefficient at megavoltage energies, so only density matters.", lvl="Easy"),
    PR("Moving an object closer to the detector, with the source position fixed:", "improves the resolution and lowers the magnification", ["improves both the resolution and the magnification", "worsens the resolution and raises the magnification", "changes neither"],
       "The blur s·b/a falls with b, and m = 1 + b/a falls too.", lvl="Easy"),
    PRN(STEM("An object lies 90 cm from the source and 10 cm from the detector.", [], "What is the [[magnification]]?"), m_a, [10 / 90, 1 + 90 / 10, 90 / 100], "{:.2f}",
        f"m = (a + b)/a = 100 / 90 = {m_a:.2f}. Using b/a alone gives {10 / 90:.2f}, and inverting the ratio gives {1 + 90 / 10:.2f}.", lvl="Moderate"),
    PRN(STEM("A 1.0 mm source. An object lies 90 cm from the source and 10 cm from the detector.", [], "What is the [[blur]] of its edge on the detector?"), b_a, [1.0 * 90 / 10, 1.0 * 10 / 100, 1.0], "{:.2f} mm",
        f"Blur = s·b/a = 1.0 × 10 / 90 = {b_a:.2f} mm. Using a/b gives {1.0 * 90 / 10:.0f} mm, and using the source-to-detector distance for a gives {1.0 * 10 / 100:.2f} mm.", lvl="Moderate"),
    PRN(STEM("10 cm of water, compared with 8 cm of water and 2 cm of cortical bone.", ["50 keV: μ/ρ = 0.2269 cm²/g for water and 0.4242 cm²/g for bone", "bone density = 1.92 g/cm³"], "What is the [[ratio of the transmitted fluences]]?"), r50, [r30, 0.4242 / 0.2269, 1 + 2 * (0.4242 * 1.92 - 0.2269)], "{:.2f}",
        f"μ<sub>bone</sub> = 0.4242 × 1.92 = 0.8145 cm<sup>−1</sup>. The exponent is (0.8145 − 0.2269) × 2 = 1.175, and the ratio is e<sup>1.175</sup> = {r50:.2f}. The ratio of the mass coefficients, 1.87, ignores the density and the thickness.", lvl="Moderate"),
    PR("The dominant source of noise in x-ray imaging is:", "random fluctuation in the number of photons registered in each pixel", ["scatter in the patient", "the size of the focal spot", "the thickness of the scintillator"],
       "Photon counting follows the Poisson distribution, in which the noise is √N for a mean of N.", lvl="Moderate"),
    PRN(STEM("A pixel registers an average of 10,000 photons.", [], "What is the [[SNR]]?"), snr(10000), [10000.0, 10000 / 100 / 100, math.sqrt(100)], "{:.0f}",
        f"SNR = N / √N = √N = {snr(10000):.0f}. The signal is 10,000 and the noise is 100.", lvl="Moderate"),
    PRN(STEM("The mAs of a radiograph is increased fourfold, with everything else unchanged.", [], "By what factor does the [[SNR]] change?"), snr(4), [4.0, 0.5, 16.0], "{:.0f}",
        "The number of photons rises fourfold, and the SNR rises as the square root of the number of photons: √4 = 2.", lvl="Moderate"),
    PR("Scatter lowers the quality of a radiograph because the scattered photons:", "add signal that carries no information about the path through the patient", ["reduce the signal", "improve the contrast", "increase the resolution"],
       "They raise the signal, but they did not travel along a straight line from the source, so they add noise and lower the contrast.", lvl="Moderate"),
    PR("Which technique gives the lowest exposure at the skin of the patient?", "60 kVp, 16 mAs", ["80 kVp, 10 mAs", "100 kVp, 8 mAs", "120 kVp, 5 mAs"],
       f"Skin exposure is proportional to mAs × kVp². The values are {skin(60, 16):,} for 60 kVp and 16 mAs, {skin(80, 10):,} for 80 kVp and 10 mAs, {skin(100, 8):,} for 100 kVp and 8 mAs, and {skin(120, 5):,} for 120 kVp and 5 mAs.", lvl="Challenging"),
    PR("A thicker scintillator in an EPID detects more photons. The cost is:", "a blurrier image, because the light spreads over a larger area", ["a higher noise level", "a lower sensitivity", "a smaller magnification"],
       "More photons raise the SNR, but the light from each photon spreads, which lowers the resolution. The modulation transfer function describes it.", lvl="Challenging"),
    PR("The field size of a radiograph is increased with the mAs unchanged. The image will show:", "more scatter, and lower contrast", ["less scatter, and higher contrast", "less noise, with the same scatter", "no change in the scatter"],
       "A larger field irradiates more tissue, so more photons scatter toward the detector.", lvl="Challenging"),
]

TERMS = ['contrast', 'magnification', 'signal-to-noise ratio', 'grid']

TAKE = [
    [('Contrast between bone and soft tissue is large at kV energy, where the photoelectric effect is strong, and small at MV energy, where only density matters.', 'contrast-energy')],
    [('Blur = s·b/a and magnification m = (a + b)/a. Moving an object away from the detector magnifies it and blurs it.', 'magnification')],
    [('The noise is √N and the SNR is √N for a mean of N photons. Four times the photons doubles the SNR.', 'snr-photons')],
    [('Scattered photons add signal with no information. A grid of fins pointing to the source stops them and passes the primary photons.', 'scatter-grid')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
_n0 = len(PROBLEMS)
PROBLEMS += [
    SORT("Does each change improve, worsen, or leave unchanged the sharpness of a radiograph?", ["Improves sharpness", "Worsens sharpness", "No change"],
         [("The object is moved closer to the detector", 0), ("A larger focal spot", 1), ("Smaller detector pixels", 0), ("A thicker scintillator", 1), ("A higher mA", 2), ("The object is moved closer to the source", 1)],
         "Blur grows with the source size and with the object to detector distance. Smaller pixels sample finely, and a thicker scintillator spreads the light. A higher mA changes the noise and not the sharpness.", lvl="Moderate"),
    TYPED(STEM("The source-to-detector distance is 100 cm, and an object lies 25 cm from the detector.", [], "What is the [[magnification]]?"), mag(75, 25), 0.01, "(ratio)",
          f"a = 75 cm, so m = (75 + 25) / 75 = {mag(75, 25):.2f}.", lvl="Moderate"),
    FIGQ(STEM("The graph shows the magnification against the distance of the object from the detector, for a source-to-detector distance of 100 cm.", [], "Tap the [[object-to-detector distance at which the magnification is 1.25]]."),
         FS(x=dict(min=0, max=40, ticks=[0, 10, 20, 30, 40], label="Object to detector distance (cm)"), y=dict(min=1.0, max=1.7, ticks=[1.0, 1.2, 1.4, 1.6], label="Magnification"), series=[dict(pts=PTS(lambda b: 100 / (100 - b), 0, 40), color="plot-1")], xunit=" cm", xdec=1, xname="Distance", label="Magnification against object to detector distance"),
         [(17.0, 23.0)], "m = 100 / (100 − b) = 1.25 gives b = 20 cm. The level 1.25 is not marked on the axis.", lvl="Challenging", note="about 20 cm"),
]
INLINE = {0: [1, 2, 6], 1: [3, 4, _n0 + 1, _n0 + 3], 2: [7, 8, 11, 12], 3: [10, 13]}


# ---------------------------------------------------------------- exposure factors and the interactions behind the contrast
_n1 = len(PROBLEMS)
PROBLEMS += [
    SORT("Which interaction accounts for each feature of a radiograph made at diagnostic energy?", ["Photoelectric effect", "Compton scattering"],
         [("The attenuation per gram rises steeply with the atomic number", 0), ("Bone shows more contrast against soft tissue at a lower kVp", 0), ("The photon is absorbed and all of its energy goes to one electron", 0),
          ("Scattered photons reach the detector and lower the contrast", 1), ("The attenuation per electron hardly depends on the atomic number", 1), ("Most of the interactions in soft tissue above about 30 keV", 1)],
         "The photoelectric effect varies as Z<sup>3</sup>/E<sup>3</sup>. It gives the contrast between bone and soft tissue, and it falls quickly as the energy rises. Compton scattering depends on the electron density, and it produces most of the scatter that reaches the detector and that a grid removes.", lvl="Moderate"),
    PR("With the kVp and the geometry fixed, the darkness of a screen-film radiograph is set mainly by:", "the mAs, which sets the number of photons that reach the film", ["the focal spot size", "the brightness of the viewing box", "the magnification of the image"],
       "More photons expose the film more and darken it. The optical density is the logarithm of the ratio of the light that enters the film to the light that passes through it, so it does not depend on the brightness of the viewing box.", lvl="Easy"),
    PR("A digital radiograph is made with four times the mAs that the image needs, and everything else is unchanged. Compared with the correct exposure, the displayed image has:", "about the same brightness and half the relative noise, and the patient received four times the exposure", ["four times the brightness, as a film would show", "the same noise and four times the contrast", "the same brightness and the same noise, because the detector saturates"],
       "The signal is rescaled to a standard display range, so a higher exposure does not darken the image. The extra photons lower the quantum noise by a factor of √4 = 2, which looks like a better image. The patient receives the full extra exposure, so an overexposure goes unnoticed unless the exposure index is checked.", lvl="Moderate"),
    SORT("Which exposure factor mainly sets each property of a radiograph?", ["kVp", "mAs"],
         [("The penetration of the beam", 0), ("The mean energy of the photons", 0), ("The contrast between bone and soft tissue", 0),
          ("The number of photons that reach the detector at a fixed kVp", 1), ("The noise at a fixed kVp", 1), ("The exposure at the skin, in direct proportion", 1)],
         "The kVp sets the energy spectrum, and so the penetration and the subject contrast. The mAs sets the number of photons at a fixed kVp, and with it the noise and the exposure, which rises in proportion.", lvl="Moderate"),
]
PROBLEMS += [
    PRN(STEM("A screen-film radiograph at a source-to-detector distance of 100 cm with 20 mAs gives the right optical density. The distance is increased to 140 cm, with the same kVp and film.", [], "What [[mAs]] keeps the optical density?"), mas_far, [20 * 100 / 140, 20.0, 20 * 140 / 100], "{:.1f} mAs",
        f"The exposure at the film falls with the square of the distance, by (100 / 140)² = {(100 / 140) ** 2:.2f}, so the mAs has to rise by (140 / 100)² = {(140 / 100) ** 2:.2f}: 20 × {(140 / 100) ** 2:.2f} = {mas_far:.1f} mAs. Leaving the mAs unchanged gives 20.0, scaling with the distance alone gives {20 * 140 / 100:.1f}, and inverting the ratio gives {20 * 100 / 140:.1f}.", lvl="Moderate"),
]
INLINE[0].append(_n1 + 1)
INLINE[2].append(_n1 + 5)
