"""Equipment photographs. src/photos/manifest.json lists them (id, file, alt, caption, creator, licence, licence_url, source_url, title); PHOTO(id) in a chapter
draws one as a figure with its credit. PHOTOS_MANIFEST names another manifest (tests); its image files sit beside it."""
import base64, html, json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
FIELDS = ("id", "file", "alt", "caption", "creator", "licence", "licence_url", "source_url", "title")
ALLOWED = ("Public domain", "CC0", "CC BY 2.0", "CC BY 2.5", "CC BY 3.0", "CC BY 4.0")
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
esc = lambda s: html.escape(str(s), quote=True)

def manifest_path(): return Path(os.environ.get("PHOTOS_MANIFEST") or ROOT / "photos" / "manifest.json")
def load():
    p = manifest_path()
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
def get(pid):
    for e in load():
        if e["id"] == pid: return e
    raise KeyError(f"PHOTO({pid!r}) is not in the photo manifest")

def figure_html(pid):
    e = get(pid)
    assert all(e.get(k) for k in FIELDS), (pid, "manifest entry lacks a field")
    assert e["licence"] in ALLOWED, (pid, "licence not allowed", e["licence"])
    f = manifest_path().parent / e["file"]
    src = f"data:{MIME[f.suffix.lower()]};base64," + base64.b64encode(f.read_bytes()).decode()
    return (f'<figure class="photo"><img src="{src}" alt="{esc(e["alt"])}" loading="lazy" decoding="async">'
            f'<figcaption><div class="cap">{e["caption"]}</div><div class="credit">Photo: {esc(e["creator"])}, '
            f'<a href="{esc(e["licence_url"])}" target="_blank" rel="noopener">{esc(e["licence"])}</a>. '
            f'<a href="{esc(e["source_url"])}" target="_blank" rel="noopener">Source</a></div></figcaption></figure>')
