#!/usr/bin/env python3
"""Build a sanity-check PDF from the pipeline output: coverage summary, an index of every page pulled, and a verification sample
(the frame next to what was read from it, low-confidence lines in grey).  Usage: python tools/sanity_pdf.py ROOT OUT.pdf"""
import base64, html, json, os, re, shutil, sys
from pathlib import Path
import cv2, numpy as np
sys.path.insert(0, str(Path(__file__).parent)); import page_counter

ROOT = Path(sys.argv[1]); OUT = Path(sys.argv[2]); TMP = Path("/tmp/sanity"); shutil.rmtree(TMP, ignore_errors=True); TMP.mkdir()
DOI = re.compile(r"9781003345534-(\d+)"); HEAD = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){1,3})\s+[A-Z]"); OPT = re.compile(r"^[a-e]\s?[.,]\s")
vids = sorted([p.parent for p in ROOT.glob("v*/report.json")], key=lambda p: int(p.name[1:]))
esc = lambda s: html.escape(s, quote=False)

pages = []; recs = []
for v in vids:
    meta = json.load(open(v / "frames.json")); sel = meta["selected"]; ocr = json.load(open(v / "ocr_pages.json")); rep = json.load(open(v / "report.json"))
    if not (v / "counter.json").exists(): page_counter.run(v)
    raw = json.load(open(v / "counter.json")); seq = [c["page"] for c in raw]; chain = page_counter.consistent(seq)
    cnt = {raw[i]["file"]: raw[i]["page"] for i in chain}; n_read = sum(x is not None for x in seq)
    kept = [m for m in sel if m["file"] in ocr]
    vp = []
    for m in kept:
        lines = ocr[m["file"]]; good = [l for l in lines if len(l["text"]) >= 5]
        conf = float(np.mean([l["conf"] for l in good])) if good else 0.0
        heads = [l["text"][:70] for l in lines if HEAD.match(l["text"]) and len(l["text"]) < 90 and l["conf"] >= 60]
        dois = [int(DOI.search(l["text"]).group(1)) for l in lines if DOI.search(l["text"])]
        symb = np.mean([sum(not (c.isalnum() or c.isspace()) for c in l["text"]) / max(1, len(l["text"])) for l in good]) if good else 0
        opts = sum(bool(OPT.match(l["text"])) for l in lines)
        vp.append(dict(rec=v.name, file=m["file"], path=str(v / "frames" / m["file"]), t=m["t"], page=cnt.get(m["file"]), conf=conf, nlines=len(lines),
                       heads=heads, chapter=(dois[0] if dois else None), symb=float(symb), opts=opts, lines=lines))
    pages += vp
    steps = [seq[b] - seq[a] for a, b in zip(chain, chain[1:]) if b - a == 1]
    seen_ch = set(); chs = []
    for p in vp:
        if p["chapter"] and p["chapter"] not in seen_ch: seen_ch.add(p["chapter"]); chs.append((p["chapter"], p["t"], p["page"]))
    recs.append(dict(rec=v.name, duration=meta["duration"], frames=meta["frames"], pages=len(vp), read=len(chain), excluded=n_read - len(chain), total=len(seq),
                     first=seq[chain[0]] if chain else None, last=seq[chain[-1]] if chain else None, max_fwd=max(steps) if steps else None,
                     conf=float(np.mean([p["conf"] for p in vp])), breaks=rep["jumps"], chapters=chs))

# verification sample: per recording a chapter start, the least legible page, a problem page, an equation/table-heavy page
sample = []
for r in recs:
    vp = [p for p in pages if p["rec"] == r["rec"]]; pick = []
    def add(p, why):
        if p and all(p["file"] != q["file"] or p["rec"] != q["rec"] for q, _ in pick): pick.append((p, why))
    add(next((p for p in vp if p["chapter"]), None), "chapter start")
    add(max((p for p in vp if p["opts"] >= 4), key=lambda p: p["opts"], default=None), "problem page")
    add(max((p for p in vp if p["nlines"] >= 10 and p["conf"] >= 55), key=lambda p: p["symb"], default=None), "equations, tables, or notation")
    add(min((p for p in vp if p["nlines"] >= 10), key=lambda p: p["conf"], default=None), "least legible page in this recording")
    sample += pick

def img_tag(p, name):
    g = cv2.imread(p["path"]); cv2.imwrite(str(TMP / name), g, [cv2.IMWRITE_JPEG_QUALITY, 74]); return f'<img src="{(TMP / name).as_uri()}">'

css = """@page{size:Letter;margin:0.45in} body{font:9.5pt/1.35 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;color:#111}
h1{font-size:17pt;margin:0 0 4pt} h2{font-size:12pt;margin:14pt 0 4pt} p{margin:3pt 0} table{border-collapse:collapse;width:100%;font-size:7.6pt}
th{text-align:left;border-bottom:1px solid #111;color:#555;font-weight:600;padding:2pt 4pt 2pt 0} td{padding:1.5pt 4pt 1.5pt 0;border-top:0.5px solid #ddd;vertical-align:top}
tr{break-inside:avoid} .s{break-before:page} .m{color:#555;font-size:8pt} img{width:100%;border:0.5px solid #bbb;margin:4pt 0}
pre{font:6.7pt/1.28 "DejaVu Sans Mono",Menlo,monospace;white-space:pre-wrap;margin:2pt 0} .lo{color:#999;font-style:italic} .bad{color:#B3261E}"""
H = [f"<style>{css}</style><h1>Book OCR sanity check</h1><p class='m'>Pages pulled from the screen recordings, what was read from them, and where the reading is shaky. Frames are shown as captured. Grey italic lines in the sample pages have OCR confidence below 60.</p>"]
H.append("<h2>Coverage by recording</h2><table><tr><th>Rec</th><th>Length</th><th>Distinct pages pulled</th><th>Book page counter</th><th>Counter readings kept</th><th>Largest step between adjacent frames</th><th>Mean OCR conf.</th><th>Breaks</th></tr>")
for r in recs:
    br = ", ".join(f"{b['kind'].replace('_', ' ')} at {b['t']:.0f}s" for b in r["breaks"])
    H.append(f"<tr><td>{r['rec']}</td><td>{r['duration']:.0f} s</td><td>{r['pages']} (from {r['frames']} frames)</td><td>{r['first']} to {r['last']}</td><td>{r['read']} of {r['read'] + r['excluded']} ({r['excluded']} excluded)</td><td>{r['max_fwd']}</td><td>{r['conf']:.0f}</td><td>{esc(br)}</td></tr>")
H.append("</table>")
joins = [(a["rec"], b["rec"], a["last"], b["first"]) for a, b in zip(recs, recs[1:])]
H.append("<p class='m'>Joins between recordings (last counter value of one, first of the next): " + "; ".join(f"{a}→{b}: {x} → {y}" for a, b, x, y in joins) + ". The counter advances by 1 to 3 per screen. Readings that break that pattern (the digit 5 is often misread as 9 or dropped) are excluded rather than trusted.</p>")
H.append("<h2>Chapter starts captured</h2><table><tr><th>Chapter</th><th>Recording</th><th>Time</th><th>Book page counter</th></tr>")
for r in recs:
    for ch, t, pg in r["chapters"]: H.append(f"<tr><td>{ch}</td><td>{r['rec']}</td><td>{t:.1f} s</td><td>{pg}</td></tr>")
H.append("</table>")
H.append(f"<h2>Verification sample ({len(sample)} pages)</h2><p class='m'>Each is shown with the frame first and the text read from it after. Chosen to include the hard cases: chapter starts, problem sets, equations and tables, and the least legible page of each recording.</p>")
for n, (p, why) in enumerate(sample, 1):
    body = "\n".join(f"<span class='lo'>{esc(l['text'])}</span>" if l["conf"] < 60 else esc(l["text"]) for l in p["lines"])
    H.append(f"<div class='s'><h2>{n}. Recording {p['rec']} · {p['t']:.1f} s · book page {p['page']} · {why}</h2><p class='m'>{p['nlines']} lines read, mean confidence {p['conf']:.0f}</p>{img_tag(p, f's{n:02d}.jpg')}<pre>{body}</pre></div>")
H.append("<div class='s'><h2>Index of every page pulled</h2><table><tr><th>Rec</th><th>Time</th><th>Book p.</th><th>Conf.</th><th>Lines</th><th>Section headings read on the page</th></tr>")
for p in pages:
    cls = " class='bad'" if p["conf"] < 55 else ""
    H.append(f"<tr><td>{p['rec']}</td><td>{p['t']:.1f}</td><td>{p['page'] if p['page'] is not None else ''}</td><td{cls}>{p['conf']:.0f}</td><td>{p['nlines']}</td><td>{esc('; '.join(p['heads']))}</td></tr>")
H.append("</table></div>")
(TMP / "index.html").write_text("\n".join(H), encoding="utf-8")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); pg = b.new_page()
    pg.goto((TMP / "index.html").as_uri()); pg.wait_for_timeout(800)
    pg.pdf(path=str(OUT), format="Letter", margin=dict(top="0.45in", bottom="0.45in", left="0.45in", right="0.45in"), print_background=True); b.close()
print(f"wrote {OUT} ({OUT.stat().st_size/1e6:.1f} MB): {len(recs)} recordings, {len(pages)} pages indexed, {len(sample)} in the sample")
for r in recs: print(" ", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items() if k not in ("breaks", "chapters")})
