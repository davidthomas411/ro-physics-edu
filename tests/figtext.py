"""Text inside figures: on every chapter page and question page, no two labels overlap and none sits outside its drawing. The page moves a label that would collide
(declutter in src/app.js); this checks the result. Two identical labels that touch (the 0 at the corner of two axes) are not counted."""
import sys, os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
U = (ROOT / "dist" / "ro-physics.html").resolve().as_uri()
JS = """() => { const out = [];
  document.querySelectorAll('svg').forEach(svg => { if (!svg.getClientRects().length) return; const sr = svg.getBoundingClientRect();
    const bx = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim() && t.getClientRects().length).map(t => { const r = t.getBoundingClientRect(); return {t: t.textContent.trim().slice(0, 28), l: r.left, r: r.right, tp: r.top, b: r.bottom}; });
    for (let i = 0; i < bx.length; i++) for (let j = i + 1; j < bx.length; j++) { const a = bx[i], c = bx[j];
      if (a.t !== c.t && Math.min(a.r, c.r) - Math.max(a.l, c.l) > 1.5 && Math.min(a.b, c.b) - Math.max(a.tp, c.tp) > 2.5) out.push(a.t + ' / ' + c.t); }
    bx.forEach(a => { if (a.l < sr.left - 1 || a.r > sr.right + 1 || a.tp < sr.top - 1 || a.b > sr.bottom + 1) out.push(a.t + ' outside'); }); });
  return out; }"""
bad = []; n = 0
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None); errs = []
    pg = b.new_page(viewport={"width": 1280, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U + "#home"); pg.wait_for_timeout(300); topics = pg.evaluate("DATA.topics.map(t=>t.id)")
    for tid in topics:
        for suf in ("", "/q"):
            pg.goto(U + f"#t/{tid}{suf}"); pg.wait_for_timeout(260); r = pg.evaluate(JS); n += 1
            if r: bad.append(f"{tid}{suf}: {r[:4]}"); print("FAIL", bad[-1])
    if errs: bad.append(f"page errors {errs[:2]}")
    b.close()
print(f"figtext: {n} pages scanned"); print("figtext: PASS" if not bad else f"figtext: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
