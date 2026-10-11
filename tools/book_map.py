#!/usr/bin/env python3
"""Merge the per-recording outputs into one map of the book: chapters, sections, problem sets, where recordings join,
and anything that looks missing.  Usage: python tools/book_map.py [ROOT]   (ROOT holds v1/, v2/, ... from book_pipeline.py)
Writes ROOT/book_map.json and ROOT/book_map.md."""
import json, re, sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/claude/book")
DOI = re.compile(r"9781003345534-(\d+)")
SEC = re.compile(r"^(\d{1,2})\.(\d{1,2})(?:\.(\d{1,2}))?\s+(\S.*)$")
ITEM = re.compile(r"^(\d{1,3})\s?[.,]\s+\S")
TIER = re.compile(r"^(easy|moderate|challenging)\b", re.I)
vids = sorted([p.parent for p in root.glob("v*/lines.json")], key=lambda p: int(p.name[1:]))

rows = []
for v in vids:
    for l in json.load(open(v / "lines.json")): rows.append(dict(l, video=v.name))

chapters, cur, in_problems, tier = {}, None, False, None
prev_video = None; joins = []
def ch_rec(n): return chapters.setdefault(n, dict(chapter=n, videos=set(), sections={}, problems={"Easy": set(), "Moderate": set(), "Challenging": set()}, first_t=None, problem_set_seen=False, start_seen=False))
for i, l in enumerate(rows):
    txt = l["text"].strip()
    if l["video"] != prev_video:
        joins.append(dict(video=l["video"], first=txt[:70], after=(rows[i - 1]["text"][:70] if i else None), prev_video=prev_video)); prev_video = l["video"]
    m = DOI.search(txt)
    if m:
        cur = int(m.group(1)); in_problems = False; tier = None; r = ch_rec(cur); r["start_seen"] = True; r["videos"].add(l["video"])
        prev = rows[i - 1]["text"].strip() if i else ""
        if not r.get("title") and len(prev) < 70 and rows[i - 1]["conf"] >= 60 and not prev.isdigit(): r["title"] = prev
        continue
    s = SEC.match(txt)
    if s and len(txt) < 100 and l["conf"] >= 60:
        ch = int(s.group(1))
        if cur is not None and ch == cur:   # only headings of the chapter we are in (cross-references to other chapters are ignored)
            r = ch_rec(ch); key = ".".join(x for x in s.groups()[:3] if x); r["sections"].setdefault(key, dict(title=s.group(4)[:70], video=l["video"], t=l["t"])); r["videos"].add(l["video"]); continue
    if cur is None: continue
    ch_rec(cur)["videos"].add(l["video"])
    if re.search(r"Problem\s*Sets?", txt, re.I): in_problems = True; ch_rec(cur)["problem_set_seen"] = True; tier = None; continue
    if in_problems:
        t = TIER.match(txt)
        if t and len(txt) < 20: tier = t.group(1).capitalize(); continue
        it = ITEM.match(txt)
        if it and tier: ch_rec(cur)["problems"][tier].add(int(it.group(1)))

report = []
for n in sorted(chapters):
    r = chapters[n]; secs = sorted(r["sections"], key=lambda k: [int(x) for x in k.split(".")])
    top = sorted({int(k.split(".")[1]) for k in secs}); gaps = [x for x in range(1, (max(top) if top else 0) + 1) if x not in top]
    pc = {k: len(v) for k, v in r["problems"].items()}
    report.append(dict(chapter=n, title=r.get("title", ""), videos=sorted(r["videos"], key=lambda s: int(s[1:])), sections=len(secs), second_level_missing=gaps,
                       headings=[f"{k} {r['sections'][k]['title']}" for k in secs], start_seen=r["start_seen"], problem_set_seen=r["problem_set_seen"],
                       problems_seen=pc, problems_max_number=max([max(v) for v in r["problems"].values() if v] or [0])))
json.dump(dict(chapters=report, joins=joins), open(root / "book_map.json", "w"), indent=1)
md = ["| Ch | Title | Recordings | Start read | Sections | Missing 2nd-level | Problem set | Problems seen E/M/C | Highest no. |", "|---|---|---|---|---|---|---|---|---|"]
for r in report:
    p = r["problems_seen"]; md.append(f"| {r['chapter']} | {r['title']} | {', '.join(r['videos'])} | {'yes' if r['start_seen'] else 'no'} | {r['sections']} | {r['second_level_missing'] or ''} | {'yes' if r['problem_set_seen'] else 'no'} | {p['Easy']}/{p['Moderate']}/{p['Challenging']} | {r['problems_max_number']} |")
md.append("\nRecording joins (last line of the previous recording, first line of the next):")
for j in joins[1:]: md.append(f"- {j['prev_video']} -> {j['video']}: ... {j['after']!r} | {j['first']!r}")
open(root / "book_map.md", "w").write("\n".join(md)); print("\n".join(md))
