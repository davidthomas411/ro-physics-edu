#!/usr/bin/env python3
"""Read the reader's page counter ("N / 462", bottom-right of every frame) for each selected frame of a recording.
Usage: python tools/page_counter.py OUT   (OUT has frames.json and frames/; writes counter.json)"""
import json, re, sys
from pathlib import Path
import cv2, numpy as np

def _digits(box, scale, interp, otsu):
    import pytesseract
    big = cv2.resize(box, None, fx=scale, fy=scale, interpolation=interp)
    if otsu: big = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    big = cv2.copyMakeBorder(big, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)
    t = pytesseract.image_to_string(big, config="--psm 7 -c tessedit_char_whitelist=0123456789").strip()
    return int(t) if t.isdigit() and 1 <= int(t) <= 999 else None

def read_counter(img_gray):
    """The counter is a small bordered box (digits) followed by "/ 462" in the bottom bar. Three preprocessing variants vote;
    the value two or more agree on wins. Returns the page number or None."""
    H = img_gray.shape[0]; box = img_gray[H - 47:H - 23, 1768:1810]
    votes = [v for v in (_digits(box, 6, cv2.INTER_CUBIC, False), _digits(box, 8, cv2.INTER_LANCZOS4, True), _digits(box, 4, cv2.INTER_CUBIC, True)) if v is not None]
    if not votes: return None
    best = max(set(votes), key=votes.count)
    return best if votes.count(best) >= 2 else votes[0]

def consistent(seq, step=4):
    """Indices of the longest chain of readings that never decreases and rises by at most `step` per frame between chosen ones.
    The rest are OCR confusions (5 for 9, a dropped digit) and are excluded from statistics."""
    idx = [i for i, v in enumerate(seq) if v is not None]; n = len(idx)
    if not n: return []
    best = [1] * n; prev = [-1] * n
    for a in range(n):
        for b in range(a):
            i, j = idx[b], idx[a]
            if seq[j] >= seq[i] and seq[j] - seq[i] <= step * (j - i) and best[b] + 1 > best[a]: best[a] = best[b] + 1; prev[a] = b
    k = max(range(n), key=lambda x: best[x]); chain = []
    while k != -1: chain.append(idx[k]); k = prev[k]
    return chain[::-1]

def run(out):
    out = Path(out); meta = json.load(open(out / "frames.json"))["selected"]; res = []
    for m in meta:
        g = cv2.imread(str(out / "frames" / m["file"]), cv2.IMREAD_GRAYSCALE); p = read_counter(g)
        res.append(dict(file=m["file"], t=m["t"], page=p))
    json.dump(res, open(out / "counter.json", "w")); return res

if __name__ == "__main__":
    r = run(sys.argv[1]); print(f"{len(r)} frames; read {sum(x['page'] is not None for x in r)}; pages:", [x["page"] for x in r])
