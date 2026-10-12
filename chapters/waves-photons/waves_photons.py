from blocks import *
import math, calc

f_lin = 2.998e9
lam_lin_cm = calc.wavelength_m(f_lin) * 100
e_lin_uev = calc.ev_from_hz(f_lin) * 1e6
lam_100k_pm = calc.nm_from_ev(100e3) * 1e3
lam_6m_pm = calc.nm_from_ev(6e6) * 1e3
lam_25k_A = calc.nm_from_ev(25e3) * 10
lam_511_pm = calc.nm_from_ev(511e3) * 1e3
f_tc = calc.hz_from_ev(140e3)
e_micro = calc.ev_from_hz(2.45e9)
orders = math.log10(100e3 / e_micro)
e_green = calc.ev_from_nm(532)
e_uv100 = calc.ev_from_nm(100)
lam_e100_pm = calc.debroglie_pm(0.1, calc.ME)
pc_e100 = calc.pc_ke(0.1, calc.ME)
b_mm = calc.ev_from_nm(1e6) * 1e3
b_ir, b_vis, b_uv = calc.ev_from_nm(700), calc.ev_from_nm(400), calc.ev_from_nm(10)

TOPIC = dict(
    id="waves-photons", domain=1, sub="I.A", title="Waves, photons, and units",
    ref=dict(aapm="1.1, 1.3", khan="2", ford="1"),
    guide=[
        H("Electromagnetic waves and photons"),
        P("Radio waves, light, and x-rays are electromagnetic waves: coupled electric and magnetic fields travelling at c = 3.00 × 10<sup>8</sup> m/s in vacuum. They differ only in frequency ν and wavelength λ."),
        P("Electromagnetic waves are transverse: the electric and magnetic fields oscillate perpendicular to the direction of travel, and no medium is needed. Sound is a longitudinal wave, in which the particles of the medium oscillate along the direction of travel, and it needs a medium. Ultrasound imaging uses sound."),
        EQ("c = λν"),
        P("In absorption and scattering, radiation behaves as particles called photons. Photon energy is set by frequency alone:"),
        EQ("E = hν = hc/λ", "h = 4.136 × 10<sup>−15</sup> eV·s", "hc = 1240 eV·nm = 12.4 keV·Å = 1.24 MeV·pm"),
        P("In practical units, wavelength (nm) = 1240 / energy (eV)."),
        TABLE(["Region", "Wavelength", "Photon energy", "Where it occurs"], [
            ["Radio and microwave", "> 1 mm", f"< {b_mm:.1f} meV", f"Linac RF power (3 GHz is {e_lin_uev:.0f} µeV), MRI"],
            ["Infrared", "700 nm – 1 mm", f"{b_mm:.1f} meV – {b_ir:.1f} eV", "Heat, thermal cameras"],
            ["Visible", "400 – 700 nm", f"{b_ir:.1f} – {b_vis:.1f} eV", f"Field light, alignment lasers (532 nm is {e_green:.2f} eV)"],
            ["Ultraviolet", "10 – 400 nm", f"{b_vis:.1f} – {b_uv:.0f} eV", "Sterilization, tanning"],
            ["X-ray and γ-ray", "< 10 nm", f"> {b_uv:.0f} eV", "Diagnostic 20–150 keV; therapy 0.1–25 MeV"]]),
        P("Region boundaries are conventional. The main elements in tissue have ionization energies of about 10 to 15 eV, so photons above that energy ionize. Therapy photons are 10<sup>4</sup> to 10<sup>6</sup> times above it."),
        P("X-rays and γ-rays differ in origin, not energy: γ-rays come from the nucleus, x-rays from electrons (bremsstrahlung or atomic transitions)."),
        P("Intensity and photon energy are independent: doubling the intensity of a monochromatic beam doubles the photons per second and leaves each photon's energy unchanged."),

        H("Units and prefixes"),
        TABLE(["Prefix", "Symbol", "Factor", "Prefix", "Symbol", "Factor"], [
            ["nano", "n", "10<sup>−9</sup>", "kilo", "k", "10<sup>3</sup>"],
            ["micro", "µ", "10<sup>−6</sup>", "mega", "M", "10<sup>6</sup>"],
            ["milli", "m", "10<sup>−3</sup>", "giga", "G", "10<sup>9</sup>"],
            ["centi", "c", "10<sup>−2</sup>", "tera", "T", "10<sup>12</sup>"]]),
        P("The electron-volt (eV) is the energy an electron gains crossing one volt:"),
        EQ("1 eV = 1.602 × 10<sup>−19</sup> J", "1 MeV = 1.602 × 10<sup>−13</sup> J"),
        P("Units of energy: joule, electron-volt, kilowatt-hour. Power is energy per unit time (watt). Frequency is cycles per second (hertz)."),

        H("Matter waves"),
        P(f"A particle with momentum p has wavelength λ = h/p (de Broglie). A 100 keV electron has λ = {lam_e100_pm:.1f} pm, far smaller than an atom (about 100 pm), so electron beams can resolve atomic structure. A 100 keV photon has λ = {lam_100k_pm:.1f} pm."),

        EX("Linac microwaves", STEM("A linac accelerating structure is driven at a microwave frequency.", ["f = 2.998 GHz"], "Find the [[wavelength]] and the [[photon energy]]."),
           ["λ = c/ν = (2.998 × 10<sup>8</sup> m/s) / (2.998 × 10<sup>9</sup> s<sup>−1</sup>) = 0.100 m", f"E = hν = (4.136 × 10<sup>−15</sup> eV·s)(2.998 × 10<sup>9</sup> s<sup>−1</sup>) = {e_lin_uev:.1f} µeV"],
           f"{lam_lin_cm:.1f} cm and {e_lin_uev:.1f} µeV, about ten orders of magnitude below a diagnostic x-ray photon."),
        EX("Wavelength from energy", STEM("", ["photon 1: E = 100 keV", "photon 2: E = 6 MeV, the most energetic photon in a 6 MV beam"], "Find the [[wavelength]] of each photon."),
           ["λ = hc/E with hc = 1240 eV·nm.", f"100 keV: λ = 1240 / 10<sup>5</sup> = 0.0124 nm = {lam_100k_pm:.1f} pm", f"6 MeV: λ = 1240 / (6 × 10<sup>6</sup>) = 2.07 × 10<sup>−4</sup> nm = {lam_6m_pm:.3f} pm"],
           f"{lam_100k_pm:.1f} pm and {lam_6m_pm:.3f} pm."),
    ],
    cards=[
        C("How are the speed, frequency, and wavelength of an electromagnetic wave related?", "c = λν, with c = 3.00 × 10<sup>8</sup> m/s in vacuum."),
        C("What is the energy of a photon in terms of frequency and wavelength?", "E = hν = hc/λ, with h = 4.136 × 10<sup>−15</sup> eV·s."),
        C("Give hc in practical units.", "hc = 1240 eV·nm = 12.4 keV·Å = 1.24 MeV·pm.", w=["So λ (nm) = 1240 / E (eV)."]),
        C("Put these in order of increasing photon energy: x-ray, visible light, microwave, ultraviolet, infrared.", "Microwave, infrared, visible light, ultraviolet, x-ray."),
        C("What distinguishes an x-ray from a γ-ray?", "Origin, not energy. γ-rays come from the nucleus; x-rays come from electrons (bremsstrahlung or characteristic transitions)."),
        C("What does doubling the intensity of a monochromatic beam change?", "The number of photons per unit time and area doubles. Each photon's energy and wavelength are unchanged."),
        C("How many joules are in 1 eV? In 1 MeV?", "1 eV = 1.602 × 10<sup>−19</sup> J. 1 MeV = 1.602 × 10<sup>−13</sup> J."),
        C("State the de Broglie relation and what it says about electron beams.", f"λ = h/p. Particles have wavelengths: a 100 keV electron has {lam_e100_pm:.1f} pm, far below atomic spacing, so electron beams resolve atoms."),
    ],
)

PROBLEMS = [
    PR("Which radiation has the highest photon energy?", "An 80 keV x-ray",
       ["A 2.998 GHz microwave", "532 nm green laser light", "A 100 nm ultraviolet photon"],
       f"Photon energy rises with frequency. The x-ray carries 80,000 eV. The 100 nm ultraviolet photon carries {e_uv100:.1f} eV, the green light {e_green:.2f} eV, and the microwave {e_lin_uev:.1f} µeV.", lvl="Easy"),
    PRN(STEM("Light has a known frequency.", ["frequency = 6.0 × 10<sup>14</sup> Hz"], "What is its [[wavelength]]?"), 500.0, [50.0, 5000.0, 5e6],
        lambda v: f"{v:g} nm" if v < 1e3 else (f"{v/1e3:g} µm" if v < 1e6 else f"{v/1e6:g} mm"),
        "λ = c/ν = (3.00 × 10<sup>8</sup> m/s) / (6.0 × 10<sup>14</sup> s<sup>−1</sup>) = 5.0 × 10<sup>−7</sup> m = 500 nm.", lvl="Easy",
        calc=CALC("nm", [TILE("c", 3.00e8, "m/s", disp="3.00 × 10⁸"), TILE("ν", 6.0e14, "Hz", disp="6.0 × 10¹⁴", id="nu"), CONV("m", "nm", 1e9), TILE("h", 4.136e-15, "eV·s", disp="4.136 × 10⁻¹⁵"), TILE("hc", 1240, "eV·nm")], solution=["c", "÷", "nu", "×", "m→nm"])),
    PRN("How many <f>joules</f> are in <v>1.0 MeV</v>?", 1.602e-13, [1.602e-19, 1.602e-16, 1.602e-10], lambda v: sci(v) + " J",
        "1 eV = 1.602 × 10<sup>−19</sup> J, so 10<sup>6</sup> eV = 1.602 × 10<sup>−13</sup> J.", lvl="Easy",
        calc=CALC("J", [TILE("E", 1.0, "MeV", disp="1.0"), CONV("MeV", "eV", 1e6), CONV("eV", "J", 1.602e-19, disp="1.602 × 10⁻¹⁹"), TILE("hc", 1240, "eV·nm")], solution=["E", "×", "MeV→eV", "×", "eV→J"])),
    PRM("Which of these are units of energy?", ["joule", "electron-volt", "kilowatt-hour"], ["watt", "pascal"],
        "Joules, electron-volts, and kilowatt-hours all measure energy. The watt is energy per time (power) and the pascal is pressure.", lvl="Easy"),
    PRN(STEM("A linac is driven at a microwave frequency.", ["f = 2.998 GHz"], "What is the [[free-space wavelength]]?"), lam_lin_cm, [1.0, 3.0, 30.0], "{:.3g} cm",
        "λ = c/ν = (2.998 × 10<sup>8</sup> m/s) / (2.998 × 10<sup>9</sup> s<sup>−1</sup>) = 0.100 m = 10 cm.", lvl="Moderate",
        calc=CALC("cm", [TILE("c", 3.00e8, "m/s", disp="3.00 × 10⁸"), TILE("f", 2.998, "GHz", disp="2.998"), CONV("GHz", "Hz", 1e9), CONV("m", "cm", 100), TILE("h", 4.136e-15, "eV·s", disp="4.136 × 10⁻¹⁵"), TILE("hc", 1240, "eV·nm")], solution=["c", "÷", "f", "÷", "GHz→Hz", "×", "m→cm"])),
    PR("The wavelength of a photon is halved. Its energy:", "doubles",
       ["is halved", "is unchanged", "increases fourfold"], "E = hc/λ, so energy is inversely proportional to wavelength.", lvl="Moderate"),
    PRN("What is the <f>wavelength</f> of a <v>25 keV</v> photon?", lam_25k_A, [lam_25k_A / 10, lam_25k_A * 10, lam_25k_A * 100], "{:.3g} Å",
        f"λ = 12.4 keV·Å / 25 keV = {lam_25k_A:.3f} Å (0.0496 nm).", lvl="Moderate",
        calc=CALC("Å", [TILE("hc", 12.4, "keV·Å", id="hcA"), TILE("hc", 1240, "eV·nm", id="hcnm"), TILE("E", 25, "keV"), CONV("keV", "eV", 1e3), CONV("nm", "Å", 10), TILE("h", 4.136e-15, "eV·s", disp="4.136 × 10⁻¹⁵"), TILE("c", 3.00e8, "m/s", disp="3.00 × 10⁸")], solution=["hcA", "÷", "E"])),
    PRN("Tc-99m emits a <v>140 keV</v> γ-ray. What is its <f>frequency</f>?", f_tc, [f_tc / 1e3, f_tc * 1e3, f_tc * 1e6], lambda v: sci(v) + " Hz",
        f"ν = E/h = (1.40 × 10<sup>5</sup> eV) / (4.136 × 10<sup>−15</sup> eV·s) = {sci(f_tc)} Hz.", lvl="Moderate",
        calc=CALC("Hz", [TILE("E", 140, "keV"), TILE("h", 4.136e-15, "eV·s", disp="4.136 × 10⁻¹⁵"), CONV("keV", "eV", 1e3), TILE("c", 3.00e8, "m/s", disp="3.00 × 10⁸"), TILE("hc", 1240, "eV·nm")], solution=["E", "×", "keV→eV", "÷", "h"])),
    PR("The intensity of a monochromatic x-ray beam is doubled with no change in wavelength. What happens?", "The number of photons per second doubles; each photon's energy is unchanged",
       ["The energy of each photon doubles", "The wavelength halves", "Each photon's energy halves because the beam is spread over more photons"],
       "At a fixed photon energy, intensity is proportional to the number of photons. Photon energy is set by wavelength, which did not change.", lvl="Moderate"),
    PRN(STEM("Compare two photons.", ["x-ray photon: E = 100 keV", "microwave photon: f = 2.45 GHz"], "How many [[times more energy]] does the x-ray photon carry?"), 10, [4, 7, 13], lambda v: f"10<sup>{v}</sup> times",
        f"The microwave photon has E = hν = {sci(e_micro)} eV. The ratio is 10<sup>5</sup> / {sci(e_micro)} = {sci(1e5 / e_micro)}, about 10<sup>10</sup>.", lvl="Challenging",
        calc=CALC("", [TILE("E", 100, "keV"), TILE("h", 4.136e-15, "eV·s", disp="4.136 × 10⁻¹⁵"), TILE("f", 2.45, "GHz", disp="2.45"), CONV("keV", "eV", 1e3), CONV("GHz", "Hz", 1e9)], ops=("×", "÷", "(", ")", "log₁₀("), solution=["log₁₀(", "E", "×", "keV→eV", "÷", "(", "h", "×", "f", "×", "GHz→Hz", ")", ")"])),
]

INLINE = {0: [1, 2, 11], 1: [3, 4]}

TERMS = ['electromagnetic waves', 'photons', 'electron-volt', 'de Broglie']

TAKE = [
    [("In practical units, λ (nm) = 1240 / E (eV); equivalently E (keV) × λ (Å) = 12.4.", "wave-energy"),
     ("x-rays and γ-rays differ in origin, not energy.", "photon-origin"),
     ("At a fixed photon energy, intensity is proportional to the number of photons; photon energy is set by frequency alone.", "intensity-energy")],
    [("1 eV = 1.602 × 10<sup>−19</sup> J, so 1 MeV = 1.602 × 10<sup>−13</sup> J.", "ev-gain"),
     ("Length units: 1 nm = 10 Å = 1000 pm.", "length-units")],
    [("A particle has wavelength λ = h/p. It matters only at atomic scales: a 100 keV electron has λ = 3.7 pm.", "matter-wave")],
]


# ---------------------------------------------------------------- wave types
PROBLEMS += [
    SORT("Is each wave transverse or longitudinal?", ["Transverse", "Longitudinal"],
         [("Visible light", 0), ("An x-ray", 0), ("A wave on a stretched string", 0), ("Sound in air", 1), ("Ultrasound in soft tissue", 1), ("A compression pulse along a spring", 1)],
         "In a transverse wave the oscillation is perpendicular to the direction of travel, as for light, x-rays, and a wave on a string. In a longitudinal wave the oscillation is along the direction of travel, as for sound in air or in tissue.", lvl="Easy"),
]
