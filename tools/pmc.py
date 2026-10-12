"""Find and add open-access figures from PubMed Central (Europe PMC REST for search and full text, the PMC CDN for the image).

  python tools/pmc.py search "winston-lutz phantom" [n]    articles with a CC BY, CC BY-SA, or CC0 licence: pmcid, licence, title
  python tools/pmc.py figs PMC11466459                      the figures of one article: id, label, caption, size
  python tools/pmc.py get PMC11466459 acm214470-fig-0001 OUT.jpg   download one figure, resized to at most 800 px and 150 KB, no metadata
  python tools/pmc.py add PMC11466459 acm214470-fig-0001 PHOTO_ID "alt text" "caption"
        download it, write src/photos/<PHOTO_ID>.jpg, and add the manifest entry (creator is the first author and 'et al.', the licence and the source link come from the article)

The licence is read from the article, never assumed; an article that is not CC BY, CC BY-SA, or CC0 is refused. Check the picture by eye before using it:
no patient name, date, or identifier, and nothing that is only a screenshot of a table. Write the alt text and caption yourself, in your own words.
Requests are spaced and retried; one request at a time.
"""
import sys, re, io, json, time, fcntl, html, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "RoPhysicsEduBot/1.0 (https://github.com/davidthomas411/ro-physics-edu; david.thomas2@jefferson.edu)"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
OK_LIC = re.compile(r"^(cc by|cc by-sa|cc0)( |$)", re.I)
BAD_LIC = re.compile(r"-nc|-nd", re.I)


def call(url, binary=False):
    for wait in (0, 5, 20, 60):
        time.sleep(wait or 0.4)
        try:
            d = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read()
            return d if binary else d.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503): raise
    raise SystemExit("rate limited or unavailable: " + url)


def plain(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def search(q, n=8):
    qs = urllib.parse.urlencode(dict(query=f"({q}) AND OPEN_ACCESS:y", format="json", pageSize=int(n) * 3, resultType="core"))
    d = json.loads(call(EPMC + "search?" + qs)); out = []
    for r in d["resultList"]["result"]:
        lic = (r.get("license") or "").strip()
        if r.get("pmcid") and OK_LIC.match(lic) and not BAD_LIC.search(lic): out.append((r["pmcid"], lic, r.get("pubYear", ""), plain(r["title"])[:100]))
    return out[: int(n)]


def article(pmcid):
    x = call(EPMC + f"{pmcid}/fullTextXML")
    lic_url = next(iter(re.findall(r'<license[^>]*xlink:href="([^"]+)"', x)), "") or next(iter(re.findall(r'https://creativecommons.org/[a-z/\-.0-9]+', x)), "")
    m = re.search(r"creativecommons.org/(licenses/([a-z\-]+)/([0-9.]+)|publicdomain/zero)", lic_url)
    if not m: raise SystemExit(f"{pmcid}: no Creative Commons licence found in the article ({lic_url!r})")
    lic = "CC0" if "zero" in lic_url else f"CC {m.group(2).upper()} {m.group(3)}"
    if BAD_LIC.search(lic) or not OK_LIC.match(lic): raise SystemExit(f"{pmcid}: licence {lic} is not allowed")
    title = plain(re.search(r"<article-title[^>]*>(.*?)</article-title>", x, re.S).group(1))
    au = re.search(r"<surname[^>]*>(.*?)</surname>", x, re.S)
    n_au = len(re.findall(r"<contrib [^>]*contrib-type=.author.", x))
    first = plain(au.group(1)) if au else "Authors"
    year = (re.findall(r"<pub-date[^>]*>.*?<year>(\d{4})</year>", x, re.S) or [""])[0]
    jr = plain((re.findall(r"<journal-title>(.*?)</journal-title>", x, re.S) or [""])[0])
    figs = []
    for fm in re.finditer(r"<fig id=\"([^\"]+)\".*?</fig>", x, re.S):
        b = fm.group(0)
        label = plain((re.findall(r"<label>(.*?)</label>", b, re.S) or [""])[0]); cap = plain((re.findall(r"<caption>(.*?)</caption>", b, re.S) or [""])[0])
        path = (re.findall(r"cloudpmc-path ([^ ?]+)", b) or [""])[0]; w = (re.findall(r"original-width (\d+)", b) or ["0"])[0]
        href = (re.findall(r'content-type="image"[^>]*xlink:href="([^"]+)"', b) or [""])[0]
        figs.append(dict(id=fm.group(1), label=label, caption=cap, path=path, width=int(w), file=href))
    return dict(pmcid=pmcid, licence=lic, licence_url=lic_url.replace("http://", "https://"), title=title, first=first, n_au=n_au, year=year, journal=jr, figs=figs)


def fetch(pmcid, figid, out=None):
    from PIL import Image
    a = article(pmcid); f = next((f for f in a["figs"] if f["id"] == figid), None)
    if not f or not f["path"]: raise SystemExit(f"{pmcid}: figure {figid!r} not found or has no image path")
    im = Image.open(io.BytesIO(call("https://cdn.ncbi.nlm.nih.gov/pmc/" + f["path"], True))); im = im.convert("RGB")
    if im.width > 800: im = im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS)
    q = 85
    while True:
        b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True)
        if b.tell() <= 150000 or q <= 40: break
        q -= 8
    if out: Path(out).write_bytes(b.getvalue())
    return a, f, b.getvalue(), im.size


def add(pmcid, figid, pid, alt, caption):
    a, f, data, size = fetch(pmcid, figid)
    (ROOT / "src" / "photos" / f"{pid}.jpg").write_bytes(data)
    creator = a["first"] + " et al."
    entry = dict(id=pid, file=f"{pid}.jpg", alt=alt, caption=caption, creator=f"{creator}, {a['journal']} {a['year']}".strip(", "), licence=a["licence"], licence_url=a["licence_url"],
                 source_url=f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/", title=a["title"][:160])
    mp = ROOT / "src" / "photos" / "manifest.json"
    with open(ROOT / "src" / "photos" / ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        man = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else []
        man = [e for e in man if e["id"] != pid] + [entry]
        mp.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"added {pid}: {size[0]}x{size[1]}, {len(data)} bytes, {a['licence']}, {entry['creator']}")


if __name__ == "__main__":
    c = sys.argv[1:2]
    if c == ["search"]:
        for r in search(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 8): print(*r, sep=" | ")
    elif c == ["figs"]:
        a = article(sys.argv[2]); print(f"{a['pmcid']} | {a['licence']} | {a['first']} {a['year']} | {a['title'][:90]}")
        for f in a["figs"]: print(f"  {f['id']} | {f['label']} | {f['width']}px | {f['caption'][:150]}")
    elif c == ["get"]:
        a, f, d, s = fetch(sys.argv[2], sys.argv[3], sys.argv[4]); print(f"saved {sys.argv[4]} {s[0]}x{s[1]} {len(d)} bytes {a['licence']}")
    elif c == ["add"]: add(*sys.argv[2:7])
    else: sys.exit(__doc__)
