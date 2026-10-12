"""Equipment photographs (static; needs Pillow): every manifest entry is complete, its file exists, is at most 800 px wide and 150 KB, carries no metadata, has an allowed
licence, and comes from a named host; ids are unique; every PHOTO in a chapter is in the manifest. PHOTOS_MANIFEST names another manifest. The checks themselves are
tried on a synthetic image made in a temporary folder, so no fake photo is committed."""
import json, os, re, struct, sys, tempfile
from pathlib import Path
sys.path[:] = [x for x in sys.path if Path(x or ".").resolve() != Path(__file__).resolve().parent]      # tests/numbers.py must not shadow the standard library module that Pillow imports
from urllib.parse import urlparse
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import photolib

FIELDS, ALLOWED = photolib.FIELDS, set(photolib.ALLOWED)
HOSTS = ("wikimedia.org", "wikipedia.org", "flickr.com", "nih.gov", "nasa.gov", "energy.gov")       # hosts a source_url may be on; add a host here only when a photo needs it
MAX_W, MAX_KB = 800, 150

def metadata(path):
    """Names of metadata blocks in a JPEG or WebP file (EXIF, XMP, IPTC, comments)."""
    b = path.read_bytes(); found = []
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 4 <= len(b) and b[i] == 0xFF:
            m = b[i + 1]
            if m == 0xDA: break
            n = struct.unpack(">H", b[i + 2:i + 4])[0]
            if m == 0xE1: found.append("APP1 (EXIF or XMP)")
            if m == 0xED: found.append("APP13 (IPTC)")
            if m == 0xFE: found.append("comment")
            i += 2 + n
    elif b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        i = 12
        while i + 8 <= len(b):
            tag, n = b[i:i + 4], struct.unpack("<I", b[i + 4:i + 8])[0]
            if tag in (b"EXIF", b"XMP "): found.append(tag.decode().strip())
            i += 8 + n + (n & 1)
    else: found.append("not JPEG or WebP")
    return found

def problems(manifest):
    out = []; base = manifest.parent
    try: data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception as e: return [f"manifest unreadable: {e}"]
    if not isinstance(data, list): return ["manifest is not a list"]
    seen = set()
    for k, e in enumerate(data):
        w = f"entry {k} ({e.get('id') if isinstance(e, dict) else '?'})"
        if not isinstance(e, dict): out.append(f"{w}: not an object"); continue
        for f in FIELDS:
            if not isinstance(e.get(f), str) or not e[f].strip(): out.append(f"{w}: field {f} is missing or empty")
        if set(e) - set(FIELDS): out.append(f"{w}: unknown fields {sorted(set(e) - set(FIELDS))}")
        if e.get("id") in seen: out.append(f"{w}: duplicate id")
        seen.add(e.get("id"))
        if e.get("licence") not in ALLOWED: out.append(f"{w}: licence {e.get('licence')!r} is not one of {sorted(ALLOWED)}")
        for f in ("licence_url", "source_url"):
            u = urlparse(e.get(f) or "")
            if u.scheme != "https" or not u.hostname: out.append(f"{w}: {f} must be an https URL")
        host = urlparse(e.get("source_url") or "").hostname or ""
        if not any(host == h or host.endswith("." + h) for h in HOSTS): out.append(f"{w}: source_url host {host!r} is not on the named list {HOSTS}")
        p = base / (e.get("file") or "\0")
        if not e.get("file") or not p.is_file(): out.append(f"{w}: file {e.get('file')!r} does not exist"); continue
        if p.suffix.lower() not in photolib.MIME: out.append(f"{w}: file must be JPEG or WebP")
        if p.stat().st_size > MAX_KB * 1024: out.append(f"{w}: {p.stat().st_size // 1024} KB is over {MAX_KB} KB")
        try:
            im = Image.open(p); im.load()
            if im.width > MAX_W: out.append(f"{w}: {im.width} px wide, over {MAX_W}")
            if im.getexif(): out.append(f"{w}: Pillow reads EXIF tags")
        except Exception as ex: out.append(f"{w}: image unreadable: {ex}")
        for m in metadata(p): out.append(f"{w}: contains metadata: {m}")
    return out

def entry(**kw):
    e = dict(id="fixture", file="fixture.jpg", alt="A synthetic test image", caption="Test caption.", creator="Test Creator", licence="CC BY 4.0",
             licence_url="https://creativecommons.org/licenses/by/4.0/", source_url="https://commons.wikimedia.org/wiki/File:Test.jpg", title="Test"); e.update(kw); return e

bad = []
def check(cond, msg):
    if not cond: bad.append(msg)

# ---------------------------------------------------------------- the real manifest (or the one PHOTOS_MANIFEST names)
real = photolib.manifest_path()
if real.exists():
    bad += [f"{real.name}: {x}" for x in problems(real)]
    ids = {e["id"] for e in photolib.load()}
    from topics import TOPICS
    for t in TOPICS:
        for b in t["guide"]:
            if b[0] == "photo": check(b[1] in ids, f"{t['id']}: PHOTO({b[1]!r}) is not in the manifest")
else: bad.append(f"{real} is missing")

# ---------------------------------------------------------------- the checks themselves, on a synthetic image
with tempfile.TemporaryDirectory() as d:
    d = Path(d); im = Image.new("RGB", (320, 200)); im.putdata([(x * 255 // 320, y * 255 // 200, 128) for y in range(200) for x in range(320)])
    im.save(d / "fixture.jpg", quality=80); im.resize((900, 560)).save(d / "wide.jpg", quality=80)
    ex = Image.Exif(); ex[0x010E] = "caption"; im.save(d / "exif.jpg", exif=ex)
    im.save(d / "fixture.webp", quality=80); im.save(d / "exif.webp", exif=ex)
    Image.effect_noise((800, 800), 200).convert("RGB").save(d / "big.jpg", quality=100)
    def run(entries, name="m.json"):
        (d / name).write_text(json.dumps(entries)); return problems(d / name)
    check(run([entry()]) == [], f"a complete entry must pass: {run([entry()])}")
    check(run([entry(file="fixture.webp", id="w")]) == [], "a WebP entry must pass")
    check(run([entry(licence="CC BY-SA 4.0")]) == [], "a CC BY-SA entry must pass")
    cases = [("a missing field", entry(alt=""), "alt"), ("a missing file", entry(file="none.jpg"), "does not exist"), ("a wide image", entry(file="wide.jpg"), "px wide"),
             ("EXIF in a JPEG", entry(file="exif.jpg"), "metadata"), ("EXIF in a WebP", entry(file="exif.webp"), "metadata"), ("a large file", entry(file="big.jpg"), "KB"),
             ("a GFDL-only licence", entry(licence="GFDL"), "licence"), ("a NoDerivatives licence", entry(licence="CC BY-ND 4.0"), "licence"), ("a NonCommercial licence", entry(licence="CC BY-NC 2.0"), "licence"),
             ("an unnamed host", entry(source_url="https://example.com/x.jpg"), "host"), ("an http URL", entry(licence_url="http://creativecommons.org/licenses/by/4.0/"), "https")]
    for what, e, needle in cases:
        r = run([e]); check(any(needle in x for x in r), f"{what} must be reported ({needle}): {r}")
    check(any("duplicate" in x for x in run([entry(), entry()])), "a duplicate id must be reported")
    # the figure that PHOTO draws
    os.environ["PHOTOS_MANIFEST"] = str(d / "m.json"); run([entry()])
    h = photolib.figure_html("fixture")
    for needle in ('<figure class="photo">', 'src="data:image/jpeg;base64,', 'loading="lazy"', 'decoding="async"', 'alt="A synthetic test image"', "<figcaption>", "Test caption.", "Photo: Test Creator, ", '>CC BY 4.0</a>', 'href="https://commons.wikimedia.org/wiki/File:Test.jpg"'):
        check(needle in h, f"the photo figure lacks {needle}")
    try: photolib.get("nope"); check(False, "an unknown photo id must raise")
    except KeyError: pass
if bad:
    print("FAIL"); [print(" -", b) for b in bad]; sys.exit(1)
print("photos ok")
