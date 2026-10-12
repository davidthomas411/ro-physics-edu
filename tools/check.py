"""Check one chapter (or all) with the static tests, printing only what concerns it.

  python tools/check.py pdd            the static tests, then only the lines that name the chapter, plus its numbers test
  python tools/check.py pdd --browser  also smoke and questions (needs Chromium; CHROME_PATH)
  python tools/check.py --all          every static test, one line each

Exit status 1 when a test that concerns the chapter fails. A test that fails only on another chapter is reported as "elsewhere".
"""
import sys, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
STATIC = "license style structure takeaway facts problems plan abrstyle tapquality mudata figq noslider".split()
BROWSER = ["smoke", "questions"]


def run(name):
    p = subprocess.run([sys.executable, str(TESTS / f"{name}.py")], cwd=ROOT, capture_output=True, text=True, timeout=290)
    return p.returncode, (p.stdout + p.stderr)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    chap = args[0] if args else None
    if not chap and "--all" not in flags: sys.exit(__doc__)
    sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src" / "topics")]
    mod = None
    if chap:
        import topics as T
        ids = {t["id"]: m.__name__.split(".")[-1] for m in T._ORDER for t in [m.TOPIC]}
        if chap not in ids: sys.exit(f"unknown chapter {chap!r}; known: {', '.join(sorted(ids))}")
        mod = ids[chap]
    names = list(STATIC) + [f[:-3] for f in sorted(os.listdir(TESTS)) if f.startswith("numbers") and f.endswith(".py")]
    if mod: names = [n for n in names if not n.startswith("numbers") or n == f"numbers_{mod}"] + [n for n in names if n.startswith("numbers") and n != f"numbers_{mod}"]
    if "--browser" in flags: names += BROWSER
    failed_here = failed_else = 0
    pat = re.compile(re.escape(chap)) if chap else None
    for n in names:
        rc, out = run(n)
        if rc == 0:
            if not chap: print(f"PASS {n}")
            continue
        lines = [l for l in out.splitlines() if re.search(r"FAIL|Error|assert", l)]
        mine = [l for l in lines if pat and pat.search(l)] if chap else lines
        own_numbers = bool(mod) and n == f"numbers_{mod}"
        if mine or own_numbers or not chap:
            failed_here += 1; print(f"FAIL {n}")
            for l in (mine or lines)[:6]: print("     " + l[:200])
        else:
            failed_else += 1; print(f"elsewhere {n}: {(lines or ['failed'])[0][:120]}")
    print(f"{'chapter ' + chap if chap else 'all'}: {failed_here} failing, {failed_else} failing elsewhere")
    sys.exit(1 if failed_here else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
