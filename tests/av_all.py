"""Every diagram in every take-away: it builds, finishes, fits a phone, respects reduced motion, and shows the right numbers."""
import os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
from topics import TOPICS
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "ro-physics.html"
U = PAGE.resolve().as_uri(); fails, errors = [], []
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)
decl = {t["id"]: [x[1] for items in (t.get("take") or []) for x in (items or []) if isinstance(x, tuple)] + [b[1] for b in t["guide"] if b[0] == "avf"] for t in TOPICS}      # the take-away diagrams, then the interactive figures placed in the text
decl = {k: v for k, v in decl.items() if v}
# readouts that come from the shared beam model are worked out here from the model, so they follow it
import beamdata as _bd
_p = _bd.pdd_model; _t = _bd.tmr_model
_hs = lambda S, s: (100 + _p(S - _bd.DMAX, s)) / (2 * _p(S / 2, s))
_F = (((120 + 1.5) / (120 + 10)) / ((100 + 1.5) / (100 + 10))) ** 2
_isf = ((100 + 10) / (100 + 1.5)) ** 2; _spr = _bd._sp_ln(10 * 101.5 / 100) / _bd._sp_ln(10 * 110 / 100); _pd10 = _p(10, 10) / 100
MODEL_EXPECT = {"hotspot-separation": ["30 cm", f"{_hs(30, 10):.2f}", f"{_hs(30, 20):.2f}"], "parallel-opposed": ["S = 30 cm", f"{100 * _hs(30, 10):.0f}%", f"{_hs(30, 10):.2f}"],
                "pdd-factors": [f"{_p(10, 5):.1f}%", f"{_p(10, 10):.1f}%", f"{_p(10, 20):.1f}%"], "mayneord": ["120 cm", f"{_F:.3f}", f"{_p(10, 10) * _F:.1f}%", f"{_p(10, 10, 120):.1f}%"],
                "tmr-setup": ["Depth 10 cm", "SSD = 90 cm", f"{_t(10, 10):.3f}"], "pdd-vs-tmr": [f"{_p(10, 10):.1f}%", f"{_t(10, 10):.3f}", f"{_t(10, 10) / _pd10:.2f}"],
                "pdd-to-tmr": [f"{_pd10:.3f}", f"{_isf:.3f}", f"{_spr:.4f}", f"{_pd10 * _isf * _spr:.3f}"]}
# readouts at each diagram's default slider position, and after interacting with it
EXPECT = {"ke-classical": ["6 MeV", "0.997c", "4.85c", "faster than light"], "speed-ke": ["150 MeV", "0.507c"], "pair-production": ["3.00 MeV", "1.978 MeV"],
          "coulomb-inverse-square": ["2 r₀", "0.25 F₀"], "decay-atoms": ["2.00 T½", "25 of 100", "25%"], "half-life-mean-life": ["3.00 T½", "2.08 τ", "12.5%"], "percent-per-time": ["50%", "0.693", "not 0.50"], "decay-steps": ["β⁻", "Z + 1", "A unchanged"], "sa-formula": ["100 g/mol", "13100 Ci/g"], "activity-remaining": ["6 h", "50%", "10%", "73%"], "lor-events": ["6 events"], "suv-calc": ["20 kBq/mL", "4.0"], "pet-attenuation": ["1.00 g/cm³", "23.7%", "4.2"], "larmor-field": ["1.5 T", "63.9 MHz"], "gradient-slice": ["G = 6.0 mT/m", "2.6 kHz per cm", "3.9 mm"], "mz-recovery": ["TR 500 ms", "0.86", "0.15"], "te-decay": ["TE 100 ms", "0.33", "0.95"], "inversion-recovery": ["T1 = 3000 ms", "2079 ms"], "field-shift": ["G = 10 mT/m", "0.05 mT", "5.0 mm"], "backprojection": ["6 angles"], "hu-scale": ["1.10", "+100 HU"], "ct-density": ["0 HU", "1.00"], "pitch-time": ["pitch 1.5", "7.5 mm", "13.3 s"], "ct-noise": ["100 mAs", "2.00", "1.41", "1.00"], "bit-depth": ["8 bits", "256 levels"], "storage-size": ["Uncompressed", "104.9 MB"], "contrast-energy": ["50 keV", "3.2"], "magnification": ["20 cm", "1.25", "0.25 mm"], "snr-photons": ["5 mAs", "10000", "100"], "cost-function": ["weight 1.0", "36", "144"], "plan-tradeoff": ["26.0", "74.0"], "fluence-segments": ["4 segments", "100 MU", "70 MU"], "beam-time": ["600 MU/min", "60 s", "120 s"], "leakage-mu": ["3.5", "3.75", "13.1"], "dlg-error": ["5 mm", "7.7%"], "tongue-groove": ["1 field", "6.0%"], "sliding-window-mu": ["R = 10 MU/s", "4.0 MU"], "margin-recipe": ["2.0 mm", "6.4", "7.1", "7.8"], "dvh-curve": ["45 Gy", "100%", "2%"], "conformity-index": ["Over-coverage", "CI = 1.50", "0.581"], "lq-survival": ["α/β = 3.0 Gy", "0.368", "0.487"], "bed-compare": ["10 Gy", "57.6", "72.0"], "tcp-ntcp": ["N = 107.0", "46 Gy", "38%"], "virtual-source": ["105 cm", "0.894"], "electron-output": ["12 MeV", "6.0 cm", "0.93"], "electron-pdd": ["12 MeV", "3.6", "4.0", "5.2", "6.0"], "electron-range": ["12 MeV", "3.6", "4.0", "5.2", "6.0"], "electron-fieldsize": ["18 MeV", "9.0 cm", "2.5 cm"], "electron-penumbra": ["5.0 cm", "10.0 mm", "12.5 mm"], "electron-matching": ["5 mm", "+11%", "−6%"], "electron-obliquity": ["30°", "0.87"], "parallel-opposed": ["S = 30 cm", "121%", "1.21"], "hotspot-separation": ["30 cm", "1.21", "1.18"], "beam-count": ["3 beams", "1/3"], "wedge-profile": ["45°", "64%"], "wedge-hinge": ["100°", "40°"], "wedge-breast": ["39°", "100%", "70%"], "mlc-penumbra": ["6.0 mm", "5.5 mm"], "penumbra-geometry": ["3.0 mm", "5.3", "3.6", "2.5"], "penumbra-energy": ["1.00", "5.0 mm", "6.7 mm"], "profile-depth": ["10.0 cm", "100%", "flat"], "out-of-field": ["10 cm", "0.28", "0.15", "0.43"], "skin-dose": ["10 × 10 cm", "20%", "40%"], "device-skin": ["Open"],
          "bolus-shift": ["1.00 cm", "98%", "0.5 cm"], "terma-kernel": ["0.35 cm", "1.5 cm"], "lung-bone": ["0.30", "21%"], "pdd-buildup": ["6 MV", "1.5 cm"], "pdd-factors": ["65.6%", "67.4%", "69.2%"], "mayneord": ["120 cm", "1.026", "69.1%", "69.0%"], "field-divergence": ["10.0 cm", "11.0 × 11.0 cm"], "tmr-setup": ["10.0 cm", "90.0 cm", "0.787"],
          "pdd-vs-tmr": ["67.4%", "0.787", "1.17"], "pdd-to-tmr": ["0.674", "1.175", "0.9982", "0.790"], "scatter-factors": ["1.034", "1.019", "1.054"], "block-effect": ["Open", "1.034", "1.019", "1.054"], "equivalent-square": ["8.0 × 20.0 cm", "11.4 cm", "12.6 cm"],
          "ssd-term": ["120 cm", "0.698", "× 1.43"], "sad-formula": ["SSD calibration", "1.030", "0.786", "152.6 MU"], "accessory-factors": ["0.66", "272.7 MU", "281.2 MU"], "fluence-box": ["10 photons", "14 MeV"], "dose-rate-classes": ["0.5 Gy/h", "LDR"], "gamma-compare": ["1.88", "0.58", "3.2"], "sphere-shells": ["4 times", "25%"], "sk-decay": ["0.42 U"], "geometry-function": ["3.0 mm", "2.3%", "0.7%"], "cumulative-dose": ["59.4 d", "59 d", "197 d"], "ingrowth": ["0.88", "23 h", "69%"], "peak-crossing": ["11", "3.81", "79%"], "attenuation-curve": ["2.00 HVL", "1.39 mean free paths", "25%"],
          "interaction-regions-anim": ["1.25 MeV", "Compton scattering"], "compton-energies": ["1 MeV", "0.338", "0.662"], "mv-contrast": ["6 MeV", "4.8%", "0.99", "1.90"], "kerma-split": ["3.0%", "97.0%"], "carrier-atoms": ["20%"], "mo-tc-generator": ["96 h", "1.10", "0.97"], "magnetic-circle": ["0.20 T", "10.8 cm", "6.0 MeV"], "bend-radius": ["0.20 T", "10.8 cm"]}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page()
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errors.append(str(e)))
    def go(h): pg.goto(U + "#ref"); pg.goto(U + h); pg.wait_for_timeout(150)
    bad = []
    for tid, ids in decl.items():
        go(f"#t/{tid}"); n = pg.locator("figure.av").count()
        if n != len(ids): bad.append((tid, "figures on the page", n, len(ids))); continue
        pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())")
        for i in ids:
            f = pg.locator(f'figure.av[data-av="{i}"]')
            if f.locator("svg").count() != 1 or len(f.locator("figcaption").inner_text()) < 25: bad.append((tid, i, "no drawing or caption"))
    check(not bad, f"{sum(len(v) for v in decl.values())} diagrams across {len(decl)} chapters all build with a caption {bad}")
    EXPECT.update(MODEL_EXPECT)
    for i, want in EXPECT.items():
        tid = next(k for k, v in decl.items() if i in v); go(f"#t/{tid}"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())")
        t = pg.locator(f'figure.av[data-av="{i}"] output').inner_text(); miss = [w for w in want if w not in t]
        check(not miss, f"{i}: readout shows {want} (missing {miss}): {t!r}")
    go("#t/charges-atom"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); bf = pg.locator('figure.av[data-av="bohr-levels"]')
    for label, want in (("3 → 2", "1.89 eV"), ("2 → 1", "10.2 eV"), ("3 → 1", "12.1 eV")):
        bf.locator(f"button:has-text('{label}')").click(); pg.wait_for_timeout(2100); t = bf.locator("output").inner_text()
        check(want in t and bf.locator("button[aria-pressed='true']").count() == 1, f"bohr-levels {label}: {want}")
    for tid, i, expr in (("charges-atom", "bend-radius", 100), ("charges-atom", "magnetic-circle", 100)):
        go(f"#t/{tid}"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); f = pg.locator(f'figure.av[data-av="{i}"]')
        d0 = f.locator("output").inner_text(); f.locator("input").evaluate("e=>{e.value=100;e.dispatchEvent(new Event('input'))}"); d1 = f.locator("output").inner_text()
        check(d0 != d1 and "0.50 T" in d1 and "4.33 cm" in d1, f"{i}: at B = 0.50 T the radius is 4.33 cm ({d1[:60]!r})")
    go("#t/decay-modes"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); ds = pg.locator('figure.av[data-av="decay-steps"]')
    for label, svgwant, outwant in (("α", ["Ra-226 → Rn-222", "226 → 222", "88 → 86"], "A − 4"), ("β⁺ or EC", ["F-18 → O-18", "9 → 8", "9 → 10"], "Z − 1"), ("β⁻", ["Co-60 → Ni-60", "27 → 28", "33 → 32"], "A unchanged")):
        ds.locator(f"button:has-text('{label}')").click(); pg.wait_for_timeout(2150); st = ds.locator("svg").text_content(); ot = ds.locator("output").inner_text()
        check(all(w in st for w in svgwant) and outwant in ot, f"decay-steps {label}: {svgwant[0]}, readout says {outwant!r}")
    go("#t/decay-law"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); da = pg.locator('figure.av[data-av="decay-atoms"]')
    da.locator("input").evaluate("e=>{e.value=100;e.dispatchEvent(new Event('input'))}"); t5 = da.locator("output").inner_text()
    alive = da.locator("svg circle").evaluate_all("cs=>cs.filter(c=>c.getAttribute('r')==='7'&&c.style.fill==='var(--c1)').length")
    check("5.00 T½" in t5 and "3 of 100" in t5 and alive == 3, f"decay-atoms at 5 half-lives: 3 of 100 atoms left, and 3 are drawn alive ({alive}): {t5!r}")
    hid = []
    for tid, i in (("decay-modes", "source-half-lives"), ("decay-law", "half-life-steps"), ("particles-energy", "rest-energy")):
        go(f"#t/{tid}"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); n = pg.locator(f'figure.av[data-av="{i}"] svg text').evaluate_all("ts=>ts.filter(t=>t.style.display==='none').length")
        if n: hid.append((i, n))
    check(not hid, f"finished bar charts show every value label {hid}")
    go("#t/mu-calc"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); cp = pg.locator('figure.av[data-av="calibration-points"]')
    for label, want in (("SAD calibration", ["SAD calibration", "100 cm", "× 0.971", "× 1.000"]), ("SSD calibration", ["SSD calibration", "101.5 cm", "× 1.000", "× 1.030"])):
        cp.locator(f"button:has-text('{label}')").click(); pg.wait_for_timeout(1300); st = cp.locator("svg").text_content()
        check(all(w in st for w in want) and cp.locator("button[aria-pressed='true']").count() == 1, f"calibration-points {label}: {want}")
    go("#t/photon-interactions"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); mc = pg.locator('figure.av[data-av="mv-contrast"]')
    mc.locator("input").evaluate("e=>{e.value=100*Math.log(0.05/0.03)/Math.log(10/0.03);e.dispatchEvent(new Event('input'))}"); t50 = mc.locator("output").inner_text()
    check("0.05 MeV" in t50.replace("  ", " ") and "lowers transmission by 69" in t50 and "1.87" in t50 and "3.59" in t50, f"mv-contrast at 50 keV: 69% dip, 1.87 per gram, 3.59 per cm3 ({t50[:110]!r})")
    mc.locator("input").evaluate("e=>{e.value=100*Math.log(6/0.03)/Math.log(10/0.03);e.dispatchEvent(new Event('input'))}"); t6 = mc.locator("output").inner_text()
    check("4.8%" in t6 and "0.99" in t6 and "1.90" in t6, f"mv-contrast at 6 MeV: 4.8% dip, 0.99 per gram, 1.90 per cm3 ({t6[:110]!r})")
    go("#t/equilibrium"); pg.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())"); mt = pg.locator('figure.av[data-av="peak-crossing"]')
    mt.locator("input").evaluate("e=>{e.value=100;e.dispatchEvent(new Event('input'))}"); tp = mt.locator("output").inner_text()
    check("100" in tp and "A" in tp and "equals" not in tp, f"peak-crossing at the top of its range reads out a peak ({tp[:90]!r})")
    # motion: charts draw, timelines play
    go("#t/particles-energy"); f = pg.locator('figure.av[data-av="annihilation"]'); f.scroll_into_view_if_needed(); pg.wait_for_timeout(250); a = f.locator("svg").inner_html(); pg.wait_for_timeout(500)
    check(f.locator("svg").inner_html() != a, "annihilation: the particles move when it scrolls into view")
    # reduced motion and phone
    rc = b.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce"); rp = rc.new_page(); rp.on("pageerror", lambda e: errors.append(str(e)))
    ph = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pp = ph.new_page(); pp.on("pageerror", lambda e: errors.append(str(e)))
    worst, over, small, vis = 0, 0, 0, []
    for tid, ids in decl.items():
        rp.goto(U + "#ref"); rp.goto(U + f"#t/{tid}"); rp.wait_for_timeout(100); vis.append(rp.locator("figure.av .btn:has-text('Replay'):visible").count())
        pp.goto(U + "#ref"); pp.goto(U + f"#t/{tid}"); pp.wait_for_timeout(100); pp.evaluate("document.querySelectorAll('figure.av').forEach(f=>f._av&&f._av.finish())")
        worst = max(worst, pp.evaluate("document.documentElement.scrollWidth")); over += pp.evaluate("[...document.querySelectorAll('figure.av')].filter(f=>f.getBoundingClientRect().right>innerWidth+1).length")
        small += pp.evaluate("[...document.querySelectorAll('figure.av button, figure.av input')].filter(e=>e.getBoundingClientRect().height<28).length")
    check(sum(vis) == 0, f"reduced motion: no Replay buttons on any chapter ({sum(vis)})")
    check(worst <= 390 and over == 0 and small == 0, f"390 px: no sideways scroll, nothing outside the screen, every control at least 28 px ({worst}, {over}, {small})")
    check(not errors, f"no console or page errors {errors[:3]}")
    b.close()
print("av_all: PASS" if not fails else f"av_all: {len(fails)} FAILURES"); sys.exit(1 if fails else 0)
