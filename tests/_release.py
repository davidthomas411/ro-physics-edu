"""Shared by tests/license.py, tests/about.py, and tests/analytics.py: a complete configuration with made-up values, and a way to build the page with it.
Nothing here touches the real site_config.json."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

FULL = dict(
    title="Radiation oncology physics study site", abstract="A study guide for radiation oncology residents.", keywords=["radiation oncology", "medical physics", "education", "ABR"],
    authors=[dict(given_names="Ada B.", family_names="Lovelace", affiliation="Test University", orcid="0000-0002-1825-0097", role="Lead author"),
             dict(given_names="Charles", family_names="Babbage", affiliation="Test Institute", orcid="0000-0001-5109-3700", role="Content author")],
    contact_email="contact@example.org", repository_url="https://github.com/example-owner/ro-physics-edu", pages_url="https://example-owner.github.io/ro-physics-edu/",
    code_license="MIT", content_license="CC BY 4.0", acknowledgments=[dict(name="Dr. Grace Hopper", contribution="Lectures that gave the first list of topics")],
    physics_reviewers=[dict(name="Dr. Marie Curie", date="2026-10-01", scope="Chapters on the basic physics")], irb_number="IRB-TEST-0001",
    study_notice="This site is part of an education research study that records anonymous usage data.", survey_url="https://example.org/survey",
    analytics_mode="anonymous", analytics_backend="endpoint", analytics_site_code="", analytics_endpoint_url="http://127.0.0.1:8099/collect",
    data_access="Two named members of the study team", data_retention="Until the study closes", allow_indexing=False,
    third_party_confirmed=dict(openkbp=True, icbm152=True, linac_art=True), doi="10.5281/zenodo.1234567")

def notices_text(confirmed=True):
    t = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    return t.replace("| Not yet verified |", "| Terms read and confirmed |") if confirmed else t

def build(overrides=None, release=True, base=None, confirmed_notices=True, tmp=None):
    """Build with FULL (or base) plus overrides. Returns (exit code, output, path of the page)."""
    cfg = dict(FULL if base is None else base); cfg.update(overrides or {})
    d = Path(tmp or tempfile.mkdtemp(prefix="rophys_"))
    (d / "config.json").write_text(json.dumps(cfg), encoding="utf-8"); (d / "notices.md").write_text(notices_text(confirmed_notices), encoding="utf-8")
    env = dict(os.environ, SITE_CONFIG=str(d / "config.json"), NOTICES_FILE=str(d / "notices.md"), OUT=str(d / "out.html"))
    r = subprocess.run([sys.executable, str(ROOT / "build.py")] + (["--release"] if release else []), env=env, capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode, r.stdout + r.stderr, d / "out.html"
