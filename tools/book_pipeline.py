#!/usr/bin/env python3
"""Turn a screen recording of the e-book into ordered page text.

The recordings are variable frame rate: while the page moves the recorder writes a frame every ~33 ms; while it is
still it writes a heartbeat about every 0.23 s. A still page is therefore a frame followed by a gap of >= GAP seconds.

Stages (each writes into OUT/):
  frames VIDEO OUT   pick one sharp frame per still page            -> frames/*.png, frames.json
  ocr OUT            register pages, OCR them, assign each line to one page -> ocr_pages.json, lines.json, report.json
  text OUT           ordered text and a heading outline              -> text.txt, outline.json
Usage: python tools/book_pipeline.py frames|ocr|text ...
"""
import json, os, re, sys
from difflib import SequenceMatcher
from multiprocessing import Pool
from pathlib import Path
import cv2, numpy as np

TOP = 60             # height of the fixed reader toolbar (px)
GAP = 0.15           # seconds with no new frame => the screen was still
X0, X1 = 40, 1880    # text area (px)

def lap_var(gray): return float(cv2.Laplacian(gray, cv2.CV_64F).var())

# ---------------------------------------------------------------- stage 1: one sharp frame per still page
def select_frames(video, out):
    out = Path(out); (out / "frames").mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video)); T, S, SH = [], [], []
    while True:
        ok, fr = cap.read()
        if not ok: break
        T.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        g = cv2.cvtColor(fr[TOP:], cv2.COLOR_BGR2GRAY)
        S.append(cv2.resize(g, (480, 215), interpolation=cv2.INTER_AREA)); SH.append(lap_var(g))
    cap.release(); n = len(T)
    diff = lambda a, b: float(np.abs(S[a].astype(np.float32) - S[b].astype(np.float32)).mean())
    change = [0.0] + [diff(i, i - 1) for i in range(1, n)]
    gap = [T[i + 1] - T[i] for i in range(n - 1)] + [1.0]
    cand = []
    for i in range(n):
        if gap[i] >= GAP:
            j = i + 1 if (i + 1 < n and change[i + 1] < 0.3) else i     # the heartbeat after the gap is the refined frame
            cand.append(j if SH[j] >= SH[i] else i)
    keep = []
    for k in cand:                                                       # merge repeats of the same screen
        if keep and diff(k, keep[-1]) < 0.3:
            if SH[k] > SH[keep[-1]]: keep[-1] = k
            continue
        keep.append(k)
    meta = []; cap = cv2.VideoCapture(str(video)); idx = 0; want = {k: n_ for n_, k in enumerate(keep)}
    while True:
        ok, fr = cap.read()
        if not ok: break
        if idx in want:
            name = f"p{want[idx]:04d}.png"; cv2.imwrite(str(out / "frames" / name), fr[TOP:])
            meta.append(dict(file=name, t=round(T[idx], 3), still_s=round(gap[idx], 3), sharp=round(SH[idx], 1)))
        idx += 1
    cap.release()
    json.dump(dict(video=str(video), frames=n, duration=round(T[-1], 2), selected=meta), open(out / "frames.json", "w"), indent=1)
    print(f"{Path(video).name}: {n} frames, {T[-1]:.1f} s -> {len(meta)} still pages")

# ---------------------------------------------------------------- stage 2: duplicates, OCR, text-based registration
M_DUP = 3.0     # mean grey-level difference below which two frames are the same page (after the best shift of up to DUP px)
DUP = 30        # px
M_FIG = 14.0    # fallback for figure-heavy overlaps: largest image difference accepted at a shift near the usual page-down
DOI = re.compile(r"9781003345534-(\d+)")

def _blur(g): return cv2.GaussianBlur(g, (0, 0), 1.0)

def _shift_m(af, bf, dy):
    H = af.shape[0]
    if dy >= 0: ov = H - dy; return float(np.abs(af[dy:] - bf[:ov]).mean()), ov
    ov = H + dy; return float(np.abs(af[:ov] - bf[-dy:]).mean()), ov

def same_page(a, b):
    """True if b shows the same page as a, shifted by at most DUP px (the slow tail of a scroll animation)."""
    af, bf = _blur(a[:, X0:X1]).astype(np.float32), _blur(b[:, X0:X1]).astype(np.float32)
    return min(_shift_m(af, bf, dy)[0] for dy in range(-DUP, DUP + 1)) <= M_DUP

def image_shift_near(a, b, prior, span=25):
    """Best shift within span rows of the usual page-down, by image difference. Returns (dy, m, overlap)."""
    af, bf = _blur(a[:, X0:X1]).astype(np.float32), _blur(b[:, X0:X1]).astype(np.float32); best = (None, 1e9, 0)
    for dy in range(prior - span, prior + span + 1):
        m, ov = _shift_m(af, bf, dy)
        if m < best[1]: best = (dy, m, ov)
    return best

def image_shift_global(a, b):
    """Last-resort registration for figure-only pages: test every shift at quarter resolution, refine at full resolution.
    Accept only a distinctive minimum. Returns (dy, m, overlap, ratio)."""
    H = a.shape[0]; af, bf = _blur(a[:, X0:X1]).astype(np.float32), _blur(b[:, X0:X1]).astype(np.float32)
    aq = cv2.resize(af, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA); bq = cv2.resize(bf, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA); h = aq.shape[0]
    ms = {d: float(np.abs(aq[d:] - bq[:h - d]).mean()) for d in range(0, h - 25)}
    d0 = min(ms, key=ms.get); med = float(np.median(list(ms.values()))); ratio = ms[d0] / med if med > 0 else 1.0
    best = (None, 1e9, 0)
    for dy in range(4 * d0 - 5, 4 * d0 + 6):
        if dy < 0 or dy > H - 80: continue
        m, ov = _shift_m(af, bf, dy)
        if m < best[1]: best = (dy, m, ov)
    return best + (ratio,)

def text_register(l1, l2, H):
    """Shift between two pages from the text lines they share: a line at y1 in page 1 and y2 in page 2 votes for dy = y1 - y2."""
    A = [l for l in l1 if l["y"] >= 0.4 * H and len(l["text"]) >= 18 and l["conf"] >= 55 and not l["clipped"]]
    B = [l for l in l2 if l["y"] <= 0.6 * H and len(l["text"]) >= 18 and l["conf"] >= 55 and not l["clipped"]]
    votes = []
    for x in A:
        for y in B:
            if abs(len(x["text"]) - len(y["text"])) <= 6 and SequenceMatcher(None, x["text"], y["text"]).ratio() >= 0.9: votes.append(round(x["y"] - y["y"]))
    if not votes: return None, 0
    best = max(votes, key=lambda v: sum(abs(v - u) <= 4 for u in votes)); close = [u for u in votes if abs(best - u) <= 4]
    return int(round(float(np.mean(close)))), len(close)

def ocr_lines(path):
    import pytesseract
    from pytesseract import Output
    g = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE); H = g.shape[0]
    big = cv2.resize(g[:, X0:X1], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    d = pytesseract.image_to_data(big, lang="eng", config="--oem 1 --psm 6", output_type=Output.DICT)
    L = {}
    for i, t in enumerate(d["text"]):
        if not t.strip() or float(d["conf"][i]) < 0: continue
        L.setdefault((d["block_num"][i], d["par_num"][i], d["line_num"][i]), []).append(i)
    lines = []
    for ids in L.values():
        ids.sort(key=lambda i: d["left"][i])
        txt = " ".join(d["text"][i].strip() for i in ids)
        top = min(d["top"][i] for i in ids) / 2; bot = max(d["top"][i] + d["height"][i] for i in ids) / 2
        lines.append(dict(text=txt, x=round(X0 + min(d["left"][i] for i in ids) / 2, 1), y=round(top, 1), h=round(bot - top, 1),
                          conf=round(float(np.mean([float(d["conf"][i]) for i in ids])), 1), clipped=bool(top < 3 or bot > H - 3)))
    return sorted(lines, key=lambda l: l["y"])

def _ocr_job(p): return (Path(p).name, ocr_lines(p))

def run_ocr(out, procs=None):
    out = Path(out); meta = json.load(open(out / "frames.json"))["selected"]
    path = lambda i: out / "frames" / meta[i]["file"]; img = lambda i: cv2.imread(str(path(i)), cv2.IMREAD_GRAYSCALE)
    last = img(0); H = last.shape[0]; kept_i = [0]; dups = 0
    for i in range(1, len(meta)):                                   # 1. drop repeats of the page just kept
        cur = img(i)
        if same_page(last, cur): dups += 1; continue
        kept_i.append(i); last = cur
    cache = out / "ocr_pages.json"; done = json.load(open(cache)) if cache.exists() else {}
    todo = [str(path(i)) for i in kept_i if meta[i]["file"] not in done]
    if todo:                                                        # 2. OCR the kept pages (cached by file name)
        with Pool(procs or os.cpu_count()) as pool:
            for name, lines in pool.imap_unordered(_ocr_job, todo): done[name] = lines; json.dump(done, open(cache, "w"))
    lines_of = lambda i: done[meta[i]["file"]]
    pages = [dict(i=kept_i[0], seg=0, off=0, how="start", dy=None, support=0)]; seg = 0; off = 0; typical = [693]
    for k in range(1, len(kept_i)):                                 # 3. register each page against the one before
        i0, i1 = kept_i[k - 1], kept_i[k]; l2 = lines_of(i1)
        chapter_start = any(DOI.search(l["text"]) and l["y"] < 160 for l in l2)
        dy, support, how = None, 0, None
        if not chapter_start:
            d1, sup = text_register(lines_of(i0), l2, H)
            if d1 is not None and d1 > 40 and (sup >= 2 or any(len(l["text"]) >= 45 for l in l2)): dy, support, how = d1, sup, "text"
            else:
                d2, m2, ov2 = image_shift_near(img(i0), img(i1), int(np.median(typical)))
                if d2 is not None and m2 <= M_FIG: dy, how = d2, "image"
                else:
                    d3, m3, ov3, r3 = image_shift_global(img(i0), img(i1))
                    if d3 is not None and d3 > 40 and ov3 >= 100 and r3 <= 0.6 and m3 <= 12: dy, how = d3, "image-global"
        if how:
            off += dy; pages.append(dict(i=i1, seg=seg, off=off, how=how, dy=dy, support=support))
            if how == "text" and dy > 400: typical.append(dy)
        else:
            seg += 1; off = 0; pages.append(dict(i=i1, seg=seg, off=0, how="chapter_start" if chapter_start else "no_overlap", dy=None, support=0))
    out_lines = []
    for n, p in enumerate(pages):                                   # 4. every line belongs to exactly one page
        prev = pages[n - 1] if n and pages[n - 1]["seg"] == p["seg"] else None
        nxt = pages[n + 1] if n + 1 < len(pages) and pages[n + 1]["seg"] == p["seg"] else None
        lo = (p["off"] + prev["off"] + H) / 2 if prev else -1e9     # the cut between two pages is the middle of their overlap
        hi = (nxt["off"] + p["off"] + H) / 2 if nxt else 1e9
        for l in lines_of(p["i"]):
            gy = p["off"] + l["y"]
            if lo <= gy < hi: out_lines.append(dict(l, seg=p["seg"], gy=gy, t=meta[p["i"]]["t"]))
    out_lines.sort(key=lambda l: (l["seg"], l["gy"])); json.dump(out_lines, open(out / "lines.json", "w"))
    shifts = [p["dy"] for p in pages if p["how"] == "text" or p["how"].startswith("image")]
    jumps = [dict(t=meta[p["i"]]["t"], kind=p["how"]) for p in pages if p["how"] in ("chapter_start", "no_overlap")]
    segs = {}
    for l in out_lines: segs.setdefault(l["seg"], []).append(l)
    rep = dict(frames=len(meta), kept_pages=len(pages), duplicate_frames=dups, lines=len(out_lines), mean_conf=round(float(np.mean([l["conf"] for l in out_lines])), 1),
               by_text=sum(p["how"] == "text" for p in pages), by_image=sum(p["how"].startswith("image") for p in pages),
               scroll_dy=dict(min=min(shifts), median=float(np.median(shifts)), max=max(shifts)) if shifts else None, page_height=H,
               segments=[dict(seg=s, t=ls[0]["t"], first=ls[0]["text"][:70], last=ls[-1]["text"][:70], lines=len(ls)) for s, ls in sorted(segs.items())], jumps=jumps)
    json.dump(rep, open(out / "report.json", "w"), indent=1)
    print(f"{out.name}: {len(meta)} frames -> {len(pages)} pages ({dups} repeats), {rep['by_text']} joined by text, {rep['by_image']} by image, {len(jumps)} breaks "
          f"({sum(j['kind']=='chapter_start' for j in jumps)} chapter starts, {sum(j['kind']=='no_overlap' for j in jumps)} without overlap), {len(out_lines)} lines, conf {rep['mean_conf']}")

# ---------------------------------------------------------------- stage 3: ordered text and outline
HEAD = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){0,3})\s+[A-Z]")
def write_text(out):
    out = Path(out); lines = json.load(open(out / "lines.json")); hs = sorted(l["h"] for l in lines)
    med = hs[len(hs) // 2] if hs else 20; text = []; outline = []; last = None
    for l in lines:
        if last is not None and l["seg"] != last["seg"]: text.append(f"\n=== no overlap with the page before (jump at {l['t']} s) ===")
        elif last is not None and l["gy"] - last["gy"] > 1.9 * med: text.append("")
        text.append(l["text"]); last = l
        if HEAD.match(l["text"]) and len(l["text"]) < 90: outline.append(dict(seg=l["seg"], gy=l["gy"], t=l["t"], text=l["text"], conf=l["conf"]))
        m = re.search(r"9781003345534-(\d+)", l["text"])
        if m: outline.append(dict(seg=l["seg"], gy=l["gy"], t=l["t"], text=l["text"], chapter=int(m.group(1))))
    open(out / "text.txt", "w").write("\n".join(text)); json.dump(outline, open(out / "outline.json", "w"), indent=1)
    print("text lines:", len(lines), " outline entries:", len(outline))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "frames": select_frames(sys.argv[2], sys.argv[3])
    elif cmd == "ocr": run_ocr(sys.argv[2])
    elif cmd == "text": write_text(sys.argv[2])
