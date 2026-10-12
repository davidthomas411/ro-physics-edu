"""Flags any run of 8 or more consecutive words that the site text shares with a local text file, such as OCR of a textbook or a slide deck.
Keep those files outside the repository. The words are compared in lower case with punctuation removed, so a match survives a change of case or markup.
Usage: python tools/check_overlap.py PATH [PATH ...] [--words 8] [--include-docs]
PATH is a text file or a folder of .txt files. The site text is every chapter, flash card, question, and explanation; --include-docs adds the Markdown files in docs/.
Exit status 1 if there is any match. A match is a reason to read both passages, not proof of copying: standard phrases and definitions can repeat."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))

def words(text):
    return re.findall(r"[a-z0-9]+(?:[.'][a-z0-9]+)*", re.sub(r"<[^>]+>", " ", text).lower())

def grams(ws, n):
    return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)}

def site_passages():
    """(where, text) for every piece of text on the site."""
    from topics import TOPICS
    from facts import TITLES
    out = []
    for t in TOPICS:
        tid = t["id"]
        for b in t["guide"]:
            k = b[0]
            if k in ("h2", "h3", "p"): out.append((f"{tid} {k}", b[1]))
            elif k in ("ul", "ol", "key"): out += [(f"{tid} {k}", x) for x in b[1]]
            elif k == "fig": out.append((f"{tid} caption", b[2]))
            elif k == "ex": out += [(f"{tid} example {b[1][:30]}", x) for x in [b[2], b[4], *b[3]]]
            elif k == "more":
                out.append((f"{tid} more", " ".join(str(x) for x in b[1:3] if x)))
                for x in b[3]:
                    if x[0] == "p": out.append((f"{tid} more", x[1]))
                    elif x[0] in ("ul", "ol"): out += [(f"{tid} more", y) for y in x[1]]
        for i, c in enumerate(t["cards"], 1): out += [(f"{tid}:{i} card", x) for x in [TITLES.get(f"{tid}:{i}", c["q"]), *c["a"], *c["w"]]]
        for j, p in enumerate(t["problems"], len(t["cards"]) + 1):
            out += [(f"{tid}:{j} question", x) for x in [p["q"], *(p.get("opts") or []), p["a"][1], *p["w"], p.get("more") or ""] if x]
    return out

def reference_files(paths):
    fs = []
    for p in map(Path, paths):
        fs += sorted(p.rglob("*.txt")) if p.is_dir() else [p]
    return fs

def find_overlaps(passages, ref_text, n=8):
    """Passages that share an n-word run with ref_text. Returns [(where, shared run)]."""
    ref = grams(words(ref_text), n); hits = []
    for where, text in passages:
        ws = words(text); seen = set()
        for i in range(len(ws) - n + 1):
            g = " ".join(ws[i:i + n])
            if g in ref and g not in seen: seen.add(g); hits.append((where, g))
    return hits

def main(argv):
    n = int(argv[argv.index("--words") + 1]) if "--words" in argv else 8
    skip = {argv[argv.index("--words") + 1]} if "--words" in argv else set()
    paths = [a for a in argv if not a.startswith("--") and a not in skip]
    if not paths: print(__doc__); return 2
    files = reference_files(paths)
    if not files: print("no text files found"); return 2
    passages = site_passages()
    if "--include-docs" in argv: passages += [(f"docs/{p.name}", p.read_text(encoding="utf-8")) for p in sorted((ROOT / "docs").glob("*.md"))]
    total = 0
    for f in files:
        hits = find_overlaps(passages, f.read_text(encoding="utf-8", errors="replace"), n)
        for where, g in hits: print(f"{f.name}: {where}: \"{g}\"")
        total += len(hits)
    print(f"{total} shared runs of {n} words in {len(files)} file(s)")
    return 1 if total else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
