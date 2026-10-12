"""Release information. Reads the owner's values (site_config.json), the changelog, and the third-party table; builds the About page, the citation texts, and the
checks that a release build must pass. build.py calls build_about() and release_problems(); tools/sync_release_files.py writes CITATION.cff, .zenodo.json, the README
citation block, and docs/irb-data-description.md from the same functions, so none of them can differ."""
import datetime, html, json, os, re, subprocess
from pathlib import Path
import analytics_schema as AS

ROOT = Path(__file__).resolve().parent.parent
CODE_LICENSES = {"MIT": dict(spdx="MIT", zenodo="mit", file="LICENSE")}
CONTENT_LICENSES = {"CC BY 4.0": dict(spdx="CC-BY-4.0", zenodo="cc-by-4.0", file="LICENSE-CONTENT.md"),
                    "CC BY-NC 4.0": dict(spdx="CC-BY-NC-4.0", zenodo="cc-by-nc-4.0", file="LICENSE-CONTENT.md")}
CONFIRM_TEXT = {"openkbp": "read the OpenKBP terms and confirm that this use is allowed",
                "icbm152": "read the ICBM152 terms and confirm that this use is allowed",
                "photos": "confirm that each photograph in src/photos/manifest.json has the licence, creator, and source that it states",
                "linac_art": "confirm who made the linac illustration in assets/linac and under what terms"}
ORCID = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
esc = lambda s: html.escape(str(s), quote=True)

def config_path(): return Path(os.environ.get("SITE_CONFIG") or ROOT / "site_config.json")
def load_config(path=None): return json.loads(Path(path or config_path()).read_text(encoding="utf-8"))
def blank(v): return v is None or (isinstance(v, str) and not v.strip())
def miss(what): return f'<span class="miss">[{esc(what)} missing]</span>'

# ---------------------------------------------------------------- changelog and third-party table
def changelog(path=None):
    entries, cur = [], None
    for line in Path(path or ROOT / "CHANGELOG.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\d+\.\d+\.\d+)(?: - (.+))?\s*$", line.strip())
        if m: cur = dict(version=m.group(1), date=(m.group(2) or "").strip(), items=[]); entries.append(cur)
        elif cur is not None and line.startswith("- "): cur["items"].append(line[2:].strip())
        elif cur is not None and line.startswith("  ") and line.strip() and cur["items"]: cur["items"][-1] += " " + line.strip()
    return entries

def notices(path=None):
    rows, head = [], None
    for line in Path(path or os.environ.get("NOTICES_FILE") or ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if head is None: head = [c.lower() for c in cells]; continue
        if all(re.match(r"^:?-+:?$", c) for c in cells): continue
        r = dict(zip(head, cells)); m = re.search(r"third_party_confirmed\.([a-z0-9_]+)", r.get("status", ""))
        rows.append(dict(source=r.get("source", ""), what=r.get("what it is", ""), files=r.get("files", ""), url=r.get("url", ""), terms=r.get("terms", ""), status=r.get("status", ""), confirm=m.group(1) if m else None))
    return rows

# ---------------------------------------------------------------- build information
def git(*args):
    try: return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception: return ""

def build_info(release):
    top = (changelog() or [dict(version="", date="")])[0]
    info = dict(version=top["version"], released=top["date"] if ISO.match(top["date"]) else "", release=bool(release), built="", commit="")
    if release:
        info["built"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        info["commit"] = (os.environ.get("GITHUB_SHA") or git("rev-parse", "HEAD"))
    return info

def tracked_files():
    out = git("ls-files")
    return [x for x in out.split("\n") if x] if out else None

FORBIDDEN_EXT = {".pdf", ".epub", ".djvu", ".mobi", ".azw3", ".ppt", ".pptx", ".key", ".odp"}
FORBIDDEN_DIR = re.compile(r"(^|/)(ocr|book|books|slides|decks|lectures)(/|$)", re.I)
FORBIDDEN_NAME = re.compile(r"(^|[^a-z])ocr([^a-z]|$)", re.I)
WARN_PATHS = [(re.compile(r"^tools/(book_|scan_video|page_counter|sanity_pdf|run_all)"), "it reads text from the e-book; decide whether it belongs in the public repository"),
              (re.compile(r"^docs/roecsg-audit"), "it is a working document about a third-party study guide; decide whether it belongs in the public repository")]
def forbidden(paths):
    return [p for p in paths if Path(p).suffix.lower() in FORBIDDEN_EXT or FORBIDDEN_DIR.search(p) or FORBIDDEN_NAME.search(Path(p).name)]
def warn_tracked(paths): return [f"{p} is tracked: {why}" for p in paths for rx, why in WARN_PATHS if rx.match(p)]

# ---------------------------------------------------------------- the owner's values
def missing(cfg):
    out = []
    def need(key, ok=None, label=None):
        v = cfg.get(key); good = ok(v) if ok else not blank(v)
        if not good: out.append(label or key)
    need("title"); need("abstract")
    need("keywords", lambda v: isinstance(v, list) and len(v) > 0 and all(isinstance(x, str) and x.strip() for x in v))
    A = cfg.get("authors")
    if not isinstance(A, list) or not A: out.append("authors")
    else:
        for i, a in enumerate(A, 1):
            for k in ("given_names", "family_names", "affiliation", "role"):
                if blank(a.get(k)): out.append(f"authors[{i}].{k}")
            if not ORCID.match(str(a.get("orcid") or "")): out.append(f"authors[{i}].orcid (format 0000-0000-0000-0000)")
    need("contact_email", lambda v: isinstance(v, str) and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v))
    need("repository_url", lambda v: isinstance(v, str) and re.match(r"^https://github\.com/[^/\s]+/[^/\s]+$", v))
    m = re.match(r"^https://github\.com/([^/\s]+)/([^/\s]+)$", cfg.get("repository_url") or "")
    hint = f" (for this repository: https://{m.group(1).lower()}.github.io/{m.group(2)}/)" if m else ""
    need("pages_url", lambda v: isinstance(v, str) and v.startswith("https://"), "pages_url" + hint)
    need("code_license", lambda v: v in CODE_LICENSES, "code_license (one of: " + ", ".join(CODE_LICENSES) + ")")
    need("content_license", lambda v: v in CONTENT_LICENSES, "content_license (one of: " + ", ".join(CONTENT_LICENSES) + ")")
    ak = cfg.get("acknowledgments")
    if ak is None: out.append("acknowledgments (a list; use [] for none)")
    elif not isinstance(ak, list) or any(blank(x.get("name")) or blank(x.get("contribution")) for x in ak): out.append("acknowledgments (each needs name and contribution)")
    R = cfg.get("physics_reviewers")
    if not isinstance(R, list) or not R: out.append("physics_reviewers")
    else:
        for i, r in enumerate(R, 1):
            if blank(r.get("name")): out.append(f"physics_reviewers[{i}].name")
            if not ISO.match(str(r.get("date") or "")): out.append(f"physics_reviewers[{i}].date (YYYY-MM-DD)")
    if not isinstance(cfg.get("allow_indexing"), bool): out.append("allow_indexing (true or false)")
    mode = cfg.get("analytics_mode")
    if mode not in ("none", "anonymous"): out.append('analytics_mode ("none" or "anonymous"; linked analytics is not built)')
    if mode == "anonymous":
        need("irb_number")
        be = cfg.get("analytics_backend")
        if be not in ("goatcounter", "endpoint"): out.append('analytics_backend ("goatcounter" or "endpoint")')
        elif be == "goatcounter": need("analytics_site_code", lambda v: isinstance(v, str) and re.match(r"^[a-z0-9][a-z0-9-]*$", v))
        else: need("analytics_endpoint_url", lambda v: isinstance(v, str) and (v.startswith("https://") or re.match(r"^http://(127\.0\.0\.1|localhost)(:\d+)?/", v)))
    if cfg.get("survey_url") and not str(cfg["survey_url"]).startswith("https://"): out.append("survey_url (must start with https://)")
    if not isinstance(cfg.get("doi"), str): out.append("doi (a string; empty until the first Zenodo release)")
    elif cfg["doi"] and not re.match(r"^10\.\d{4,9}/\S+$", cfg["doi"]): out.append("doi (format 10.5281/zenodo.1234567)")
    return out

def unconfirmed(cfg):
    t = cfg.get("third_party_confirmed")
    if not isinstance(t, dict): return ["third_party_confirmed"]
    keys = set(t) | {r["confirm"] for r in notices() if r["confirm"]}
    return [f"third_party_confirmed.{k} is not true: " + CONFIRM_TEXT.get(k, "confirm the terms listed in THIRD_PARTY_NOTICES.md") for k in sorted(keys) if t.get(k) is not True]

def release_problems(cfg):
    P = dict(missing=missing(cfg), unconfirmed=unconfirmed(cfg), tracked=[], changelog=[], warnings=[])
    tf = tracked_files()
    if tf is None: P["tracked"] = ["this is not a git checkout, so the tracked files cannot be checked"]
    else:
        P["tracked"] = [f"{p} is tracked: third-party documents and OCR text must stay out of the repository" for p in forbidden(tf)]
        P["warnings"] = warn_tracked(tf)
    for r in notices():
        if r["confirm"] and (cfg.get("third_party_confirmed") or {}).get(r["confirm"]) is True and r["terms"].lower().startswith("not yet verified"):
            P["unconfirmed"].append(f"THIRD_PARTY_NOTICES.md still says the terms of {r['source']} are not verified: write the terms in the row")
    ch = changelog()
    if not ch: P["changelog"].append("CHANGELOG.md has no version entry")
    elif not ISO.match(ch[0]["date"]): P["changelog"].append(f"CHANGELOG.md: the newest entry ({ch[0]['version']}) needs a release date, YYYY-MM-DD")
    return P

def analytics_config(cfg, release):
    """What the page script gets. None unless this is a release build with analytics_mode anonymous."""
    if not release or cfg.get("analytics_mode") != "anonymous": return None
    if cfg.get("analytics_backend") == "endpoint": return dict(backend="endpoint", url=cfg["analytics_endpoint_url"])
    return dict(backend="goatcounter", url=f"https://{cfg['analytics_site_code']}.goatcounter.com/count")

# ---------------------------------------------------------------- citations
def _initials(given, sep):
    parts = [p for p in re.split(r"[\s.]+", given or "") if p]
    return sep.join(p[0].upper() for p in parts)
def _authors(cfg): return cfg.get("authors") or []

def citations(cfg, version, year):
    A = _authors(cfg); title = cfg.get("title") or "[title missing]"; yr = str(year) if year else "[year missing]"; ver = version or "[version missing]"
    doi = cfg.get("doi") or ""; url = cfg.get("pages_url") or ""
    def apa_name(a): return f"{a['family_names']}, " + ". ".join(_initials(a["given_names"], " ").split()) + "."
    def ama_name(a): return f"{a['family_names']} {_initials(a['given_names'], '')}"
    if A:
        n = [apa_name(a) for a in A]; apa_a = n[0] if len(n) == 1 else (n[0] + ", & " + n[1] if len(n) == 2 else ", ".join(n[:-1]) + ", & " + n[-1])
        ama_n = [ama_name(a) for a in A]; ama_a = ", ".join(ama_n if len(ama_n) <= 6 else ama_n[:3] + ["et al"])
        bib_a = " and ".join(f"{a['family_names']}, {a['given_names']}" for a in A)
        key = re.sub(r"[^a-z0-9]", "", A[0]["family_names"].lower()) or "author"
    else: apa_a = ama_a = bib_a = "[authors missing]"; key = "author"
    link = f"https://doi.org/{doi}" if doi else (url or "[URL missing]")
    pub = "Zenodo" if doi else "GitHub Pages"
    apa = f"{apa_a} ({yr}). {title} (Version {ver}) [Computer software]. {pub}. {link}"
    ama = f"{ama_a}. {title}. Version {ver}. {pub}; {yr}. " + (f"doi:{doi}" if doi else (url or "[URL missing]"))
    word = re.sub(r"[^a-z0-9]", "", (title.split() or ["site"])[0].lower())
    bib = ["@software{" + f"{key}{year or ''}{word}" + ",", f"  author    = {{{bib_a}}},", f"  title     = {{{title}}},", f"  year      = {{{yr}}},", f"  version   = {{{ver}}},", f"  publisher = {{{pub}}},"]
    if doi: bib.append(f"  doi       = {{{doi}}},")
    bib.append(f"  url       = {{{link}}}"); bib.append("}")
    return dict(ama=ama, apa=apa, bibtex="\n".join(bib))

# ---------------------------------------------------------------- the About page (sections of blocks; app.js draws them)
def license_notice(cfg):
    c, k = cfg.get("code_license") or "[code license missing]", cfg.get("content_license") or "[content license missing]"
    return f"Code: {c}. Text, questions, flash cards, and diagrams: {k}. Reuse needs attribution. Third-party material keeps its own terms (see About)."

def link(url, text): return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'

def privacy_blocks(cfg, backend):
    """Section 10. backend is None (nothing is sent), 'goatcounter', or 'endpoint'. The event list comes from analytics_schema, so it matches what app.js can send."""
    b = [["p", "There are no accounts. Progress is stored only in this browser, and the Reference page has a Clear button that removes it."]]
    if backend is None:
        b.append(["p", "This version records no usage data. It sends nothing about what is read, answered, or opened."])
    else:
        b.append(["p", "This version records anonymous usage data for a research study of how the questions perform. Each event below is sent with the listed properties and with nothing else. Any property that is not listed, or whose value does not fit its description, is dropped before sending."])
        rows = []
        for e in AS.EVENTS:
            props = "<br>".join(f"<b>{esc(p['name'])}</b>: {esc(p['what'])}" for p in e["props"]) or "None."
            rows.append([f"<b>{esc(e['name'])}</b>", esc(e["what"]), props])
        b.append(["table", ["Event", "Sent when", "Properties"], rows])
        b.append(["p", "The site records no " + ", ".join(AS.NEVER[:-1]) + ", or " + AS.NEVER[-1] + ". Learners see no difficulty labels and no results from other learners. Only the study team sees the data, and it reports aggregates."])
        if backend == "goatcounter":
            b.append(["p", "Events go to GoatCounter, a hosted counter that does not use cookies. Each request carries the event as a page address and nothing else from the page: no referrer, screen size, or title. As with any web request, the service receives the IP address and browser string of the sender, and its privacy policy describes how it handles them."])
        else:
            b.append(["p", "Events go to a collector that the study team runs. As with any web request, the collector receives the IP address and browser string of the sender."])
    study = []
    if cfg.get("study_notice"): study.append(["p", esc(cfg["study_notice"])])
    if cfg.get("irb_number"): study.append(["p", "IRB protocol: " + esc(cfg["irb_number"]) + "."])
    elif backend is not None: study.append(["p", "IRB protocol: " + miss("IRB number")])
    if cfg.get("survey_url"): study.append(["p", "Resident survey: " + link(cfg["survey_url"], cfg["survey_url"]) + "."])
    return b + study

def build_about(cfg, build, counts, real_sources, photos=()):
    repo = (cfg.get("repository_url") or "").rstrip("/"); pages = cfg.get("pages_url") or ""
    cites = citations(cfg, build["version"], (build["released"] or "")[:4])
    S = []
    def sec(id, title, blocks): S.append(dict(id=f"about-{id}", title=title, blocks=blocks))
    sec("what", "What this is", [["p", f"A study site for radiation oncology residents who are preparing for the ABR Medical Physics for Radiation Oncology exam. It has {counts['chapters']} chapters, {counts['flash']:,} flash cards, and {counts['questions']:,} questions, arranged by the seven ABR content domains."]])
    A = cfg.get("authors") or []
    people = ["ul", [f"<b>{esc(a.get('given_names', ''))} {esc(a.get('family_names', ''))}</b>, {esc(a.get('affiliation', ''))}. {esc(a.get('role', ''))}." + (f" ORCID {link('https://orcid.org/' + a['orcid'], a['orcid'])}." if a.get("orcid") else "") for a in A]] if A else ["p", miss("author names")]
    blocks = [["h3", "Authors"], people]
    ak = cfg.get("acknowledgments")
    blocks += [["h3", "Acknowledgments"], ["p", miss("acknowledgments")]] if ak is None else ([["h3", "Acknowledgments"], ["ul", [f"<b>{esc(x['name'])}</b>. {esc(x['contribution'])}" for x in ak]]] if ak else [])
    R = cfg.get("physics_reviewers") or []
    blocks += [["h3", "Physics review"], (["ul", [f"<b>{esc(r['name'])}</b>, reviewed {esc(r['date'])}" + (f". {esc(r['scope'])}" if r.get("scope") else "") + "." for r in R]] if R else ["p", miss("physics reviewers")])]
    sec("authors", "Authors and acknowledgments", blocks)
    rel = build["release"]
    kv = [["Version", esc(build["version"]) if build["version"] else miss("version")],
          ["Build date", esc(build["built"]) if build["built"] else ("<span class=\"miss\">[set by the release build]</span>" if not rel else miss("build date"))],
          ["Commit", (link(f"{repo}/commit/{build['commit']}", build["commit"][:7]) if repo else esc(build["commit"][:7])) if build["commit"] else "<span class=\"miss\">[set by the release build]</span>"],
          ["DOI", link(f"https://doi.org/{cfg['doi']}", cfg["doi"]) if cfg.get("doi") else "<span class=\"miss\">[DOI pending]</span>"]]
    sec("version", "Version", [["kv", kv]])
    sec("cite", "How to cite", [["p", "The citation names this version."], ["cite", "AMA", cites["ama"], "ama"], ["cite", "APA", cites["apa"], "apa"], ["cite", "BibTeX", cites["bibtex"], "bibtex"]])
    code, cont = cfg.get("code_license"), cfg.get("content_license")
    lic = [["p", "Code: " + (esc(code) + (" (" + link(f"{repo}/blob/main/{CODE_LICENSES[code]['file']}", "LICENSE") + ")" if code in CODE_LICENSES and repo else "") if code else miss("code license")) + ". Text, questions, flash cards, and diagrams: " + (esc(cont) + (" (" + link(f"{repo}/blob/main/{CONTENT_LICENSES[cont]['file']}", "LICENSE-CONTENT.md") + ")" if cont in CONTENT_LICENSES and repo else "") if cont else miss("content license")) + ". Reuse needs attribution."],
           ["p", "Third-party material keeps its own terms."]]
    rows, grouped = [], False
    for r in notices():
        if r["status"].startswith("Not part of the site"): continue                      # a source that was only used privately is listed in the notices file, not on the page
        if r["what"].startswith("TCIA collection"):
            if not grouped: rows.append(["Collections of The Cancer Imaging Archive", "Clinical images in the figures marked as real. The collections are listed under Images", "CC BY 3.0 or CC BY 4.0, by collection"]); grouped = True
            continue
        if r["confirm"] == "photos":                                                      # one row for all photographs: the count, then each creator and licence
            if photos: rows.append([link(r["url"], f"Photographs ({len(photos)})"), "Photographs of equipment in the chapters", "<br>".join(f"{esc(e['creator'])}, {esc(e['licence'])}" for e in photos)])
            continue
        rows.append([(link(r["url"], r["source"]) if r["url"].startswith("http") else esc(r["source"])), esc(r["what"]), esc(r["terms"])])
    lic.append(["table", ["Source", "Use", "Terms"], rows])
    sec("license", "License", lic)
    sec("basis", "Content basis", [["p", "The chapters follow the ABR content domains and subsections, and the scope comes from the ABR study guide and the AAPM/ASTRO 2023 core curriculum. The content is checked against Ford, <i>Primer on Radiation Oncology Physics</i> (2nd edition), and against AAPM reports. It is written in the authors' own words."],
                                  ["p", "This site is not affiliated with or endorsed by the ABR, AAPM, ASTRO, or the publisher of the textbook."]])
    imgs = ["ul", [f"{link('https://doi.org/' + s['doi'], s['collection'])} ({esc(s['license'])})" for s in real_sources]]
    sec("images", "Images", [["p", "Real clinical images come from open collections of The Cancer Imaging Archive, read as DICOM through the NCI Imaging Data Commons. The collections, with their licenses:"], imgs,
                             ["p", "The head-and-neck plan figures use the OpenKBP data set (Babier et al., Med Phys 2021). The MR brain figures start from the ICBM152 (MNI152 2009) average brain. Images computed from physics, and images with simulated contrast or artifacts, are simulated, and their captions say so."]])
    sec("ai", "AI assistance", [["p", "The text, questions, and code were drafted with Claude (Anthropic) and Claude Code. Faculty reviewed the content. Automated tests check the numbers in the worked examples."]])
    issues = f"{repo}/issues" if repo else ""
    sec("use", "Use and limits", [["p", "For education only. Not for clinical decisions. Worked examples use illustrative factors and data, not data from a machine."],
                                  ["p", "To report an error, open an issue at " + (link(issues, issues) if issues else miss("repository URL")) + " or write to " + (link("mailto:" + cfg["contact_email"], cfg["contact_email"]) if cfg.get("contact_email") else miss("contact email")) + "."]])
    sec("privacy", "Privacy and data", [])
    S[-1]["variants"] = dict(off=privacy_blocks(cfg, None), goatcounter=privacy_blocks(cfg, "goatcounter"), endpoint=privacy_blocks(cfg, "endpoint"))
    sec("changelog", "Changelog", [x for e in changelog() for x in (["h3", f"{esc(e['version'])}" + (f", {esc(e['date'])}" if e["date"] else "")], ["ul", [esc(i) for i in e["items"]]])])
    return dict(sections=S, cite=cites, notice=license_notice(cfg), title=cfg.get("title") or "", counts=counts, build=build, issues=issues)

def counts_from(topics, cards):
    q = [c for c in cards if isinstance(c.get("opts"), list)]
    return dict(chapters=len(topics), flash=len(cards) - len(q), questions=len(q))

def plain(s):
    """Text of an HTML string, for the style test and the tests that compare About text with the page."""
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("  ", " ").strip()
