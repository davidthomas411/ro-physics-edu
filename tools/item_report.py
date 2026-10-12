"""Item analysis from the anonymous usage counts. Reads one or more exports and writes one row per question.
Input formats (detected from the content):
  GoatCounter CSV export        the column whose values start with ev/ is the path; a count column is used if there is one, else each row is one hit
  GoatCounter API JSON          objects with a path and a count, for example the output of /api/v0/stats/hits
  JSON lines or a JSON array    {"event": ..., "props": {...}} from a collector that the study team runs
Columns: item, kind, n_all (answers at any attempt), n1 (first attempts), pct_correct (first attempts), options (first-attempt count of each choice),
explain_opens and pct_explain (opens of Explain further per 100 first attempts, at most 100; one learner can open it more than once, so this is an upper bound),
the first-attempt count in each time bin, and flags.
Flags, for items with n1 of 10 or more: low (under 30% correct), high (over 95% correct), unchosen:X (an option nobody chose), above_key:X (an option chosen more often than the key).
--external leaves out every item with n1 under 5, as required for anything shared outside the study team.
Usage: python tools/item_report.py EXPORT [EXPORT ...] [--out report.csv] [--external]"""
import csv, io, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import analytics_schema as AS

MIN_FLAG, MIN_SHARE = 10, 5
BINS = AS.SECS

def _walk(o, out):
    """Collect (event, props, count) from a parsed JSON value."""
    if isinstance(o, list):
        for x in o: _walk(x, out)
    elif isinstance(o, dict):
        if isinstance(o.get("event"), str) and isinstance(o.get("props"), dict):
            c = AS.clean(o["event"], o["props"])
            if c is not None: out.append((o["event"], c, 1))
        elif isinstance(o.get("path"), str):
            d = AS.decode(o["path"])
            if d: out.append((d[0], d[1], int(o.get("count") or 1)))
        else:
            for v in o.values(): _walk(v, out)

def read_events(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace"); out = []
    t = text.lstrip()
    if t[:1] in "[{":
        try: _walk(json.loads(text), out); return out
        except ValueError:
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("{"):
                    try: _walk(json.loads(line), out)
                    except ValueError: pass
            return out
    rows = list(csv.reader(io.StringIO(text)))
    rx = re.compile(r"^/?ev/")
    col = Counter(i for r in rows[:200] for i, c in enumerate(r) if rx.match(c.strip()))
    if not col: return out
    pc = col.most_common(1)[0][0]
    head = next((r for r in rows[:5] if any(re.fullmatch(r"(count|hits|total)", c.strip().lower()) for c in r)), None)
    cc = next((i for i, c in enumerate(head) if re.fullmatch(r"(count|hits|total)", c.strip().lower())), None) if head else None
    for r in rows:
        if len(r) <= pc or not rx.match(r[pc].strip()): continue
        d = AS.decode(r[pc].strip())
        if not d: continue
        try: n = int(float(r[cc])) if cc is not None and cc < len(r) and r[cc].strip() else 1
        except ValueError: n = 1
        out.append((d[0], d[1], n))
    return out

def current_items():
    """The questions of this version of the site: item identifier -> option letters, the key, and the kind."""
    from topics import TOPICS
    L = "ABCDEFGH"; cur = {}
    for t in TOPICS:
        for n, p in enumerate(t["problems"], 1):
            letters = [L[i] for i in range(len(p["opts"]))] if p.get("opts") else []
            cur[f"{t['id']}:{n}:{p['sig'][:6]}"] = dict(options=letters, key=list(p["key"]) if p.get("opts") else [], multi=bool(p.get("multi")))
    return cur

def aggregate(events):
    items = defaultdict(lambda: dict(kind="", n_all=0, n1=0, ok1=0, choice=Counter(), secs=Counter(), opens=0))
    for ev, p, c in events:
        if ev == "ans":
            it = items[p["item"]]; it["kind"] = p["kind"]; it["n_all"] += c
            if p["attempt"] == 1:
                it["n1"] += c; it["ok1"] += c if p["ok"] else 0; it["choice"][p["choice"]] += c; it["secs"][p["secs"]] += c
        elif ev == "more_q": items[p["item"]]["opens"] += c
    return items

def rows(items, current=None, external=False):
    out = []
    for item in sorted(items, key=lambda s: (s.split(":")[0], int(s.split(":")[1]), s)):
        it = items[item]; n1 = it["n1"]
        if external and n1 < MIN_SHARE: continue
        flags = []; cur = (current or {}).get(item)
        if n1 >= MIN_FLAG:
            pc = 100 * it["ok1"] / n1
            if pc < 30: flags.append("low")
            if pc > 95: flags.append("high")
            if cur and cur["options"] and not cur["multi"]:
                flags += [f"unchosen:{o}" for o in cur["options"] if it["choice"].get(o, 0) == 0]
                k = cur["key"][0] if cur["key"] else None
                flags += [f"above_key:{o}" for o in cur["options"] if k and o != k and it["choice"].get(o, 0) > it["choice"].get(k, 0)]
        if current is not None and item not in current: flags.append("not_in_this_version")
        opts = " ".join(f"{k}:{v}" for k, v in sorted(it["choice"].items())) if it["kind"] in ("mc", "multi") else ""
        out.append(dict(item=item, kind=it["kind"], n_all=it["n_all"], n1=n1, pct_correct=(round(100 * it["ok1"] / n1, 1) if n1 else ""), options=opts,
                        explain_opens=it["opens"], pct_explain=(min(100, round(100 * it["opens"] / n1)) if n1 else ""),
                        **{f"secs_{b}": it["secs"].get(b, 0) for b in BINS}, flags=" ".join(flags)))
    return out

COLS = ["item", "kind", "n_all", "n1", "pct_correct", "options", "explain_opens", "pct_explain"] + [f"secs_{b}" for b in BINS] + ["flags"]

def main(argv):
    files = [a for a in argv if not a.startswith("--") and a != (argv[argv.index("--out") + 1] if "--out" in argv else None)]
    if not files: print(__doc__); return 2
    ev = [e for f in files for e in read_events(f)]
    rs = rows(aggregate(ev), current_items(), external="--external" in argv)
    if "--out" in argv:
        with open(argv[argv.index("--out") + 1], "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(rs)
    w = {c: max([len(c)] + [len(str(r[c])) for r in rs]) for c in COLS}
    print("  ".join(c.ljust(w[c]) for c in COLS))
    for r in rs: print("  ".join(str(r[c]).ljust(w[c]) for c in COLS))
    print(f"{len(rs)} items, {len(ev)} events" + (", items with fewer than 5 first answers left out" if "--external" in argv else ""))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
