"""Licenses, citation files, third-party notices, repository hygiene, and the release gate (static; runs the build several times with made-up configurations)."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _release as R
ROOT = R.ROOT
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
import siteinfo as about
sys.path.insert(0, str(ROOT / "tools"))

bad = []
def ok(cond, msg):
    if not cond: bad.append(msg)

cfg = about.load_config()
# ---------------------------------------------------------------- the files exist
for f in ("LICENSE", "LICENSE-CONTENT.md", "THIRD_PARTY_NOTICES.md", "CITATION.cff", ".zenodo.json", "CHANGELOG.md", "RELEASING.md", ".nojekyll", ".github/workflows/pages.yml", "site_config.json", "docs/irb-data-description.md"):
    ok((ROOT / f).exists(), f"missing file {f}")
lic, licc = (ROOT / "LICENSE").read_text(encoding="utf-8"), (ROOT / "LICENSE-CONTENT.md").read_text(encoding="utf-8")
ok(cfg["code_license"] in about.CODE_LICENSES and lic.startswith("MIT License"), "LICENSE is not the MIT text that code_license names")
ok({"CC BY 4.0": "Attribution 4.0", "CC BY-NC 4.0": "NonCommercial 4.0"}.get(cfg["content_license"], "?") in licc, "LICENSE-CONTENT.md does not name the content_license of site_config.json")

# ---------------------------------------------------------------- CITATION.cff and .zenodo.json
def parse_cff(text):
    d, cur = {}, None
    for line in text.splitlines():
        if not line.strip(): continue
        if not line.startswith(" "):
            k, _, v = line.partition(":"); v = v.strip()
            if v == "": d[k] = []; cur = k
            else: d[k] = json.loads(v) if v.startswith('"') else v; cur = None
        elif line.startswith("  - "):
            if cur == "keywords": d[cur].append(json.loads(line[4:]))
            elif cur == "authors": d[cur].append({}); k, _, v = line[4:].partition(":"); d[cur][-1][k.strip()] = json.loads(v.strip())
        elif line.startswith("    ") and cur == "authors": k, _, v = line.strip().partition(":"); d[cur][-1][k] = json.loads(v.strip())
    return d
cff = parse_cff((ROOT / "CITATION.cff").read_text(encoding="utf-8")); zen = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
try:
    import yaml
    y = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8")); ok(y.get("title") == cff["title"] and len(y["authors"]) == len(cff["authors"]), "CITATION.cff is not read the same way by a YAML parser")
except ImportError: pass
ok(cff.get("cff-version") == "1.2.0" and cff.get("type") == "software", "CITATION.cff: cff-version must be 1.2.0 and type software")
for k in ("message", "title", "abstract", "authors", "version", "date-released", "repository-code", "license", "keywords"): ok(cff.get(k), f"CITATION.cff lacks {k}")
ok(re.match(r"^\d{4}-\d{2}-\d{2}$", cff.get("date-released", "")), "CITATION.cff: date-released must be YYYY-MM-DD")
for w in ("radiation oncology", "medical physics", "education", "ABR"): ok(w in cff.get("keywords", []), f"CITATION.cff keywords lack {w}")
for a in cff.get("authors", []): ok(("family-names" in a and "given-names" in a) or "name" in a, f"CITATION.cff: author entry without a name: {a}")
if cfg.get("pages_url"): ok(cff.get("url") == cfg["pages_url"], "CITATION.cff: url is not the Pages URL")
if cfg.get("doi"): ok(cff.get("doi") == cfg["doi"], "CITATION.cff: doi differs from site_config.json")
for k in ("title", "upload_type", "description", "creators", "license", "keywords", "version"): ok(zen.get(k), f".zenodo.json lacks {k}")
ok(zen.get("upload_type") == "software", ".zenodo.json: upload_type must be software")
ok(zen.get("title") == cff.get("title") and zen.get("version") == cff.get("version"), "CITATION.cff and .zenodo.json differ in title or version")
ok(zen.get("keywords") == cff.get("keywords"), "CITATION.cff and .zenodo.json differ in keywords")
names_cff = [f"{a.get('family-names', '')}, {a.get('given-names', '')}" if "family-names" in a else a.get("name") for a in cff.get("authors", [])]
ok(names_cff == [c["name"] for c in zen.get("creators", [])], "CITATION.cff and .zenodo.json differ in authors or their order")
ok(about.CONTENT_LICENSES.get(cfg["content_license"], {}).get("spdx") == cff.get("license") and about.CONTENT_LICENSES.get(cfg["content_license"], {}).get("zenodo") == zen.get("license"), "CITATION.cff and .zenodo.json do not carry the content_license of site_config.json")
top = about.changelog()[0]
ok(top["version"] == cff.get("version") == zen.get("version"), "the version differs between CHANGELOG.md, CITATION.cff, and .zenodo.json")
if about.ISO.match(top["date"]): ok(top["date"] == cff.get("date-released"), "CITATION.cff date-released differs from the newest CHANGELOG.md entry")
r = subprocess.run([sys.executable, str(ROOT / "tools" / "sync_release_files.py"), "--check"], capture_output=True, text=True, cwd=str(ROOT))
ok(r.returncode == 0, "the release files are out of date: " + (r.stdout + r.stderr).strip()[:300])

# ---------------------------------------------------------------- THIRD_PARTY_NOTICES.md
nt = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8"); rows = about.notices()
ok(len(rows) >= 10, "THIRD_PARTY_NOTICES.md has too few rows")
for r in rows:
    for k in ("source", "what", "files", "url", "terms", "status"): ok(r[k], f"THIRD_PARTY_NOTICES.md: row '{r['source'][:30]}' has an empty {k} cell")
    ok(r["url"] == "-" or r["url"].startswith("http"), f"THIRD_PARTY_NOTICES.md: row '{r['source'][:30]}': the URL cell must be a URL or -")
for f in sorted((ROOT / "src").glob("*.json")) + [ROOT / "src" / "nistdata.py"]: ok(f.name in nt or f"src/{f.name}" in nt, f"THIRD_PARTY_NOTICES.md does not cover {f.name}")
import real
for s in real.SOURCES: ok(s["collection"] in nt and s["doi"].lower() in nt.lower(), f"THIRD_PARTY_NOTICES.md lacks the collection {s['collection']} or its DOI")
for needle in ("nilearn", "OpenKBP", "NIST", "Ford", "AAPM"): ok(needle in nt, f"THIRD_PARTY_NOTICES.md lacks {needle}")
for r in rows:
    if r["confirm"]: ok(r["confirm"] in cfg["third_party_confirmed"], f"third_party_confirmed has no entry {r['confirm']}, which THIRD_PARTY_NOTICES.md names")
for k in cfg["third_party_confirmed"]: ok(k in nt, f"third_party_confirmed.{k} is not named in THIRD_PARTY_NOTICES.md")

# ---------------------------------------------------------------- no OCR or book text is tracked
tf = about.tracked_files()
ok(tf is not None, "git ls-files is not available")
if tf is not None:
    for p in about.forbidden(tf): ok(False, f"tracked third-party document or OCR text: {p}")
    for w in about.warn_tracked(tf): print("WARN", w)
gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
ok(re.search(r"^ocr/", gi, re.M) is not None, ".gitignore has no entry for the OCR folder")
ok("ROECSG" in gi, ".gitignore does not keep the ROECSG guide out")

# ---------------------------------------------------------------- the Pages workflow
wf = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
for needle in ("tags:", '"v*"', "workflow_dispatch", "actions/setup-python", "python build.py --release", "actions/upload-pages-artifact", "actions/deploy-pages", "index.html", ".nojekyll", "python tests/"):
    ok(needle in wf, f"pages.yml lacks {needle}")
ok((ROOT / ".nojekyll").read_text() == "", ".nojekyll must be empty")
ok("RELEASING" in (ROOT / "README.md").read_text(encoding="utf-8"), "README.md does not point to RELEASING.md")

# ---------------------------------------------------------------- the release gate
rc, out, _ = R.build(release=True, base=cfg, confirmed_notices=False)                  # the real configuration
need = about.missing(cfg) + about.unconfirmed(cfg)
if need:
    ok(rc != 0 and "Release build stopped" in out, "a release build with the real, incomplete site_config.json must stop")
    for n in need: ok(n.split(" ")[0] in out, f"the release build's list does not name {n.split(' ')[0]}")
rc, out, page = R.build(release=True)                                                  # complete and confirmed: builds, and carries the build information
ok(rc == 0 and page.exists(), "a release build with a complete configuration failed: " + out[-400:])
if rc == 0:
    h = page.read_text(encoding="utf-8"); ok(re.search(r'"commit": "[0-9a-f]{7,40}"', h) and re.search(r'"built": "\d{4}-\d{2}-\d{2}"', h), "the release page lacks the build date or the commit")
    ok('<meta name="robots" content="noindex">' in h, "allow_indexing false must add the noindex meta tag")
rc, out, _ = R.build(dict(third_party_confirmed=dict(openkbp=False, icbm152=True, linac_art=True)), release=True)
ok(rc != 0 and "openkbp" in out, "a release build must stop while third_party_confirmed has a false entry (and name it)")
rc, out, _ = R.build(release=True, confirmed_notices=False)
ok(rc != 0 and "not verified" in out, "a confirmation with its notice row still reading 'Not yet verified' must stop the release build")
for key in ("contact_email", "authors", "physics_reviewers", "pages_url", "analytics_endpoint_url"):
    rc, out, _ = R.build({key: "" if key not in ("authors", "physics_reviewers") else []}, release=True)
    ok(rc != 0 and key in out, f"a release build with {key} missing must stop and name it")
rc, out, _ = R.build(dict(analytics_mode="linked"), release=True)
ok(rc != 0 and "analytics_mode" in out, 'analytics_mode "linked" must be refused')
rc, out, page = R.build(dict(analytics_mode="none", irb_number="", survey_url=""), release=True)
ok(rc == 0 and "const ANALYTICS=null;" in page.read_text(encoding="utf-8"), "with analytics_mode none the release page must carry no collector")
rc, out, page = R.build(dict(allow_indexing=True), release=False)
ok(rc == 0 and 'name="robots"' not in page.read_text(encoding="utf-8"), "allow_indexing true must leave out the noindex meta tag")
rc, out, page = R.build(release=False)
ok(rc == 0 and "const ANALYTICS=null;" in page.read_text(encoding="utf-8"), "a development build must never carry a collector, whatever the configuration says")

# ---------------------------------------------------------------- the overlap check
import check_overlap as CO
texts = CO.site_passages(); ok(len(texts) > 1000, "check_overlap reads too little site text")
sample = next(t for w, t in texts if w.endswith(" p") and len(CO.words(t)) > 30)
ws = CO.words(sample); tmp = Path(tempfile.mkdtemp()); (tmp / "ocr.txt").write_text("unrelated words " + " ".join(ws[5:15]) + " more unrelated words", encoding="utf-8"); (tmp / "other.txt").write_text("nothing in common with the site text at all here", encoding="utf-8")
ok(CO.find_overlaps(texts, (tmp / "ocr.txt").read_text()), "check_overlap misses a shared run of 8 words")
ok(not CO.find_overlaps(texts, (tmp / "other.txt").read_text()), "check_overlap reports a match for unrelated text")
ok(subprocess.run([sys.executable, str(ROOT / "tools" / "check_overlap.py"), str(tmp / "ocr.txt")], capture_output=True, cwd=str(ROOT)).returncode == 1, "check_overlap must exit 1 on a match")
ok(subprocess.run([sys.executable, str(ROOT / "tools" / "check_overlap.py"), str(tmp / "other.txt")], capture_output=True, cwd=str(ROOT)).returncode == 0, "check_overlap must exit 0 without a match")

for b in bad: print("FAIL", b)
print("license: PASS" if not bad else f"license: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
