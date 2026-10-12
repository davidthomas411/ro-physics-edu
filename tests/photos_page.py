"""A PHOTO in a chapter (browser): builds a temporary page with a synthetic image placed in the first chapter, then checks that the figure shows, its credit and links are there,
and that there is no console error and no sideways scroll at 1280 x 900 and 390 x 844, light and dark. The real manifest and chapters are not touched."""
import json, os, runpy, subprocess, sys, tempfile
from pathlib import Path
sys.path[:] = [x for x in sys.path if Path(x or ".").resolve() != Path(__file__).resolve().parent]      # tests/numbers.py must not shadow the standard library module that Pillow imports
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
d = Path(tempfile.mkdtemp(prefix="rophoto_"))
im = Image.new("RGB", (800, 500)); im.putdata([(x * 255 // 800, y * 255 // 500, 128) for y in range(500) for x in range(800)]); im.save(d / "fixture.jpg", quality=70)
import shutil
REAL = json.loads((ROOT / "src/photos/manifest.json").read_text(encoding="utf-8"))      # chapters already use real photos; they stay resolvable beside the fixture
for e in REAL: shutil.copy(ROOT / "src/photos" / e["file"], d / e["file"])
(d / "m.json").write_text(json.dumps(REAL + [dict(id="fixture", file="fixture.jpg", alt="A synthetic test image", caption="A synthetic gradient used only by the test, with a long caption so that the text wraps at phone width.", creator="Test Creator With A Long Name", licence="CC BY 4.0",
    licence_url="https://creativecommons.org/licenses/by/4.0/", source_url="https://commons.wikimedia.org/wiki/File:Test.jpg", title="Test")]))
(d / "build_with_photo.py").write_text(f'''import runpy, sys
sys.path[:0] = [{str(ROOT / "src")!r}, {str(ROOT / "src" / "topics")!r}] + {[str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]!r}
from topics import TOPICS
import blocks
g = TOPICS[0]["guide"]; i = next(k for k, b in enumerate(g) if b[0] == "h2"); g.insert(i + 1, blocks.PHOTO("fixture"))
print("TOPIC", TOPICS[0]["id"]); sys.argv = ["build.py"]; runpy.run_path({str(ROOT / "build.py")!r}, run_name="__main__")
''')
env = dict(os.environ, PHOTOS_MANIFEST=str(d / "m.json"), OUT=str(d / "out.html"))
r = subprocess.run([sys.executable, str(d / "build_with_photo.py")], env=env, capture_output=True, text=True, cwd=str(ROOT))
assert r.returncode == 0, r.stdout + r.stderr
tid = [l.split()[1] for l in r.stdout.splitlines() if l.startswith("TOPIC ")][0]
bad = []
def check(c, m):
    print("ok  " if c else "FAIL", m)
    if not c: bad.append(m)
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
    for w, h in ((1280, 900), (390, 844)):
        for scheme in ("light", "dark"):
            ctx = b.new_context(viewport={"width": w, "height": h}, color_scheme=scheme); pg = ctx.new_page(); errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto((d / "out.html").as_uri() + f"#t/{tid}"); pg.wait_for_timeout(300)
            f = pg.locator("figure.photo"); check(f.count() == 1, f"{w}px {scheme}: one photo figure")
            f.scroll_into_view_if_needed(); pg.wait_for_function("document.querySelector('figure.photo img').complete && document.querySelector('figure.photo img').naturalWidth > 0", timeout=5000)
            check(pg.evaluate("document.documentElement.scrollWidth") == w, f"{w}px {scheme}: no sideways scroll")
            box, col = f.bounding_box(), pg.locator("#main").bounding_box()
            check(box["x"] >= col["x"] - 1 and box["x"] + box["width"] <= col["x"] + col["width"] + 1, f"{w}px {scheme}: the figure fits the text column")
            check(pg.locator("figure.photo img").get_attribute("alt") == "A synthetic test image" and pg.locator("figure.photo img").get_attribute("loading") == "lazy", f"{w}px {scheme}: alt text and lazy loading")
            txt = pg.locator("figure.photo figcaption").inner_text()
            check("Image: Test Creator With A Long Name, CC BY 4.0" in txt and pg.locator("figure.photo figcaption a").count() == 2, f"{w}px {scheme}: caption and credit with two links")
            check(errs == [], f"{w}px {scheme}: no console error {errs}")
            ctx.close()
    b.close()
sys.exit(1 if bad else 0)
