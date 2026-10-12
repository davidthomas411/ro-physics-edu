"""Guide blocks and cards. Text is trusted HTML written in this repository (sub, sup, b, i and span.fr only)."""
def H(t): return ("h2", t)
def H3(t): return ("h3", t)
def P(t): return ("p", t)
def UL(*items): return ("ul", list(items))
def OL(*items): return ("ol", list(items))
def EQ(*lines): return ("eq", list(lines))
def FIG(fid, cap): return ("fig", fid, cap)
def AVF(fid): return ("avf", fid)                          # an interactive figure placed in the text; its caption is drawn by the figure itself
def PHOTO(pid): return ("photo", pid)                       # a real photograph from src/photos/manifest.json, with its caption and credit
def TABLE(head, rows): return ("table", list(head), [list(r) for r in rows])
def EX(title, problem, steps, answer): return ("ex", title, problem, list(steps), answer)
def KEY(*items): return ("key", list(items))
def MORE(title, *items, simple=None):
    """A collapsed 'Show more details' region at the end of a section: an optional plain-language restatement (simple) and further blocks (strings are paragraphs)."""
    return ("more", title, simple, [("p", x) if isinstance(x, str) else x for x in items])
def _more_html(p):
    """The 'Explain further' button inside a question's feedback, with its hidden body, when the question has one."""
    m = p.get("more")
    if not m: return ""
    return f'<div class="more"><button type="button" class="btn sm more-btn" aria-expanded="false">Explain further</button><div class="more-body" hidden>{m}</div></div>'

def fr(n, d):
    return f'<span class="fr"><span>{n}</span><span>{d}</span></span>'

import hashlib, json, re, html as _html
import photolib
LETTERS = "ABCDEFG"

def F(title, fact, w=None, fig=None):
    """One flash card written as a fact: a short title (a noun phrase, never a question) and the fact, a string or a list of strings. Optional working steps and a figure id."""
    return dict(q=title, a=fact if isinstance(fact, list) else [fact], w=list(w) if w else [], fig=fig, opts=None, lvl=None, fact=True)

def C(q, a, w=None, fig=None):
    """One flashcard: question, short answer (string or list of strings), optional working steps, optional figure id."""
    return dict(q=q, a=a if isinstance(a, list) else [a], w=list(w) if w else [], fig=fig, opts=None, lvl=None)

# ---------------------------------------------------------------- question structure and text roles
def _mark(s):
    """<v>given value</v>, <f>quantity to find</f>, <t>key term</t> become coloured spans."""
    for tag in ("v", "f", "t"): s = re.sub(rf"<{tag}>(.*?)</{tag}>", rf'<span class="{tag}">\1</span>', s, flags=re.S)
    return s

_SENT = re.compile(r"(?<=[.?!])\s+(?=[A-Z(μΔ0-9]|<[vft]>)")
def autostem(q):
    """Plain stem -> context paragraph + bold question line (the last sentence). A single sentence is the question."""
    if 'class="ask"' in q or "<p" in q or "<ul" in q: return q
    parts = [x for x in _SENT.split(q.strip()) if x]
    if len(parts) < 2: return f'<p class="ask">{q}</p>'
    return f'<p class="ctx">{" ".join(parts[:-1])}</p><p class="ask">{parts[-1]}</p>'

def DT(caption, head, rows, note=""):
    """A data table inside a question or the text: a caption, header cells, and rows of cell strings. The first cell of a row is its label."""
    th = "".join(f"<th>{c}</th>" for c in head)
    body = "".join("<tr><th scope=\"row\">" + r[0] + "</th>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
    return f'<div class="dt"><div class="dtc">{caption}</div><div class="tblwrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>' + (f'<div class="dtn">{note}</div>' if note else "") + "</div>"

def STEM(ctx="", given=(), ask="", tables=()):
    """A question in three parts: setup sentence, a list of givens (label = value), and the question line.
    Mark the quantity to find with [[...]]; values inside prose with <v>...</v>."""
    out = []
    if ctx: out.append(f'<p class="ctx">{ctx}</p>')
    if given:
        items = []
        for g in given:
            cut = [(g.find(sep), sep) for sep in (": ", " = ") if sep in g]
            if cut:
                i, sep = min(cut); items.append(f"<li>{g[:i]}{sep}<v>{g[i + len(sep):]}</v></li>")
            else: items.append(f"<li><v>{g}</v></li>")
        out.append('<ul class="given">' + "".join(items) + "</ul>")
    for t in tables: out.append(t)
    if ask: out.append('<p class="ask">' + re.sub(r"\[\[(.+?)\]\]", r"<f>\1</f>", ask) + "</p>")
    return "".join(out)

def _wrap_terms(s, terms, done):
    """Wrap the first occurrence of each key term, in text outside tags, as <span class="t">."""
    parts = re.split(r"(<[^>]+>)", s)
    for i, seg in enumerate(parts):
        if seg.startswith("<"): continue
        for term in terms:
            if term.lower() in done: continue
            m = re.search(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", seg, re.I)
            if m: seg = seg[:m.start()] + f'<span class="t">{m.group(0)}</span>' + seg[m.end():]; done.add(term.lower())
        parts[i] = seg
    return "".join(parts)


# ---------------------------------------------------------------- other question types: sorting, matching, ranking, and typed numbers
KIND_LABEL = {"sort": "Sort", "match": "Match", "rank": "Rank", "tf": "True or false"}
KIND_HINT = {"sort": "Drag each item into a bin, or tap an item and then tap a bin.", "match": "Drag each item onto its match, or tap an item and then tap its match.",
             "rank": "Drag the items into order, or tap an item and then tap a position.", "tf": "Drag each statement into True or False, or tap a statement and then tap a bin."}

def SORT(stem, bins, items, why, lvl="Moderate", mode="sort", cap=None, fig=None):
    """Put each item in the right bin. items are (text, bin index). mode: sort, match, rank, or tf, which sets the label and hint.
    cap is the most items a bin holds (1 for matching and ranking). Works by drag, by tap, and by keyboard."""
    assert all(0 <= b < len(bins) for _, b in items), stem[:50]; assert mode in KIND_LABEL
    chips = [dict(t=t, b=b) for t, b in items]; key = [f"{i}>{c['b']}" for i, c in enumerate(chips)]
    ans = "; ".join(f"<b>{bins[b]}</b>: " + ", ".join(t for t, bb in items if bb == b) for b in range(len(bins)) if any(bb == b for _, bb in items))
    sig = hashlib.md5((_plain(stem) + "|" + "|".join(_plain(x) for x in bins) + "|" + "|".join(_plain(t) + ">" + str(b) for t, b in items)).encode()).hexdigest()[:8]
    return dict(q=stem, opts=[], a=[ans, why], w=[], fig=fig, lvl=lvl, key=key, multi=False, calc=None, vals=None, sig=sig, kind="sort", mode=mode, bins=list(bins), chips=chips, cap=cap)

def STEP(label, sym, vals, result, where=""):
    """One step of a worked explanation (an item of the `w` list of PR, PRN, PRM, and TYPED): a short label of what is found,
    the relation in symbols, what its terms are (`where`, optional), the same relation with the values put in, and the result
    with its unit. The renderer lays the relation lines out on their own lines under the heading "Explanation"."""
    wh = f'<span class="wh">where {where}</span>' if where else ""
    return f'<span class="wl">{label}</span><span class="wq">{sym}</span>{wh}<span class="wq">{vals} = <b>{result}</b></span>'

def _explain(p):
    """The Explanation block of a question: numbered steps first when they were written with STEP, then the one-line reason.
    Working steps written as plain strings keep their old place, after the reason."""
    w = p["w"]; steps = ('<ol class="wk">' if w and all(x.startswith('<span class="wl">') for x in w) else "<ol>") + "".join(f"<li>{x}</li>" for x in w) + "</ol>" if w else ""
    first = steps if steps.startswith('<ol class="wk">') else ""
    return f'<div class="key"><div class="hd">Explanation</div>{first}<p>{p["a"][1]}</p>{"" if first else steps}</div>'

def _fmt_ans(v):
    if v != 0 and 1e4 <= abs(v) < 1e5: return f"{round(v):,}"
    return sci(v, 3) if v != 0 and (abs(v) >= 1e5 or abs(v) < 1e-3) else f"{v:.4g}"

_EXP = re.compile(r"\d+(?:\.\d+)?e[+-]\d+")
def _noexp(s):
    """A formatter must not put exponent notation on the page: 2.84e+03 is written 2,840 and 1.5e-05 is written 0.000015."""
    return _EXP.sub(lambda m: f"{float(m.group(0)):,.0f}" if abs(float(m.group(0))) >= 1 else f"{float(m.group(0)):.8f}".rstrip("0"), s)

def TYPED(stem, answer, tol, unit, why, lvl="Moderate", w=None, fig=None):
    """A typed numeric answer, correct within the relative tolerance tol. Mark the quantity to find in the stem with [[...]]."""
    show = (_fmt_ans(answer) + " " + unit).strip()
    sig = hashlib.md5((_plain(stem) + "|" + repr(float(answer)) + "|" + str(tol) + "|" + unit).encode()).hexdigest()[:8]
    return dict(q=stem, opts=[], a=[show, why], w=list(w or []), fig=fig, lvl=lvl, key=[repr(float(answer))], multi=False, calc=None, vals=None, sig=sig, kind="num", unit=unit, tol=tol, ans=float(answer), show=show)

def _sort_html(p, pid):
    order = sorted(range(len(p["chips"])), key=lambda i: hashlib.md5((p["sig"] + str(i)).encode()).hexdigest())
    chips = "".join(f'<button type="button" class="chip" data-i="{i}" aria-pressed="false">{p["chips"][i]["t"]}</button>' for i in order)
    bins = "".join(f'<div class="bin" data-b="{b}" role="group" aria-label="{_html.escape(_plain(label), quote=True)}"><div class="bhr"><div class="bh">{label}</div><button type="button" class="place" hidden>Place here</button></div><div class="slot"></div></div>' for b, label in enumerate(p["bins"]))
    return (f'<div class="pq sortq" data-id="{pid}" data-kind="sort" data-mode="{p["mode"]}" data-key="{_html.escape(",".join(p["key"]), quote=True)}" data-cap="{p.get("cap") or 0}" data-sig="{p["sig"]}" data-multi="0">'
            f'<div class="meta">{KIND_LABEL[p["mode"]]}</div><div class="prompt">{_mark(autostem(p["q"]))}</div>'
            f'<div class="tray" role="group" aria-label="Items to place">{chips}</div><div class="bins">{bins}</div><p class="hint">{KIND_HINT[p["mode"]]}</p>'
            f'<div class="acts chkrow"><button type="button" class="btn primary chk" disabled>Check answer</button><button type="button" class="btn sm reset" hidden>Start over</button></div>'
            f'<div class="fb" hidden><p class="res" role="status"></p><div class="key"><div class="hd">Explanation</div><p>{p["a"][1]}</p></div>{_more_html(p)}<div class="acts"><button type="button" class="btn sm again">Try again</button></div></div></div>')

def _num_html(p, pid):
    pct = f"{100 * p['tol']:.3g}"
    return (f'<div class="pq numq" data-id="{pid}" data-kind="num" data-ans="{p["ans"]!r}" data-tol="{p["tol"]}" data-show="{_html.escape(p["show"], quote=True)}" data-sig="{p["sig"]}" data-multi="0">'
            f'<div class="meta">Type the answer</div><div class="prompt">{_mark(autostem(p["q"]))}</div>'
            f'<div class="numrow"><input type="text" inputmode="decimal" autocomplete="off" autocapitalize="off" spellcheck="false" class="numin" aria-label="Your answer"><span class="unit">{p["unit"]}</span></div>'
            f'<p class="msg" role="status" hidden></p><p class="hint">Type a number. Powers of ten can be written 3.5e4 or 3.5 × 10^4. Within {pct}% counts as correct.</p>'
            f'<div class="acts chkrow"><button type="button" class="btn primary chk" disabled>Check answer</button></div>'
            f'<div class="fb" hidden><p class="res" role="status"></p>{_explain(p)}{_more_html(p)}<div class="acts"><button type="button" class="btn sm again">Try again</button></div></div></div>')


# ---------------------------------------------------------------- tap-the-figure questions
def PTS(f, a, b, n=140):
    """Sample f on [a, b] for a plotted curve."""
    return [[round(a + (b - a) * i / (n - 1), 4), round(f(a + (b - a) * i / (n - 1)), 4)] for i in range(n)]

def FS(x, y, series=(), texts=(), vlines=(), cells=None, label="", xunit="", xdec=1, h=290, xname="", dots=()):
    """A figure to tap. x and y are axes: dict(min, max, ticks, label, log, fmt). series: dict(pts, color, dash, w). texts: dict(x, y, t, anchor, color, b).
    cells: [(x, y, label)] draws a grid of labelled squares one unit wide, for nuclide charts."""
    return dict(x=x, y=y, series=list(series), texts=list(texts), vlines=list(vlines), cells=[list(c) for c in cells] if cells else None, label=label, xunit=xunit, xdec=xdec, h=h, xname=xname, dots=list(dots))

def FIGQ(stem, spec, targets, why, lvl="Moderate", note="the shaded region", fig=None):
    """Tap the right place on a drawn figure. targets are the correct regions in data coordinates: (x0, x1) or (x0, x1, y0, y1); a tap in any of them is correct."""
    T = [list(t) + [None] * (4 - len(t)) for t in targets]
    sig = hashlib.md5((_plain(stem) + "|" + json.dumps(spec, sort_keys=True) + "|" + json.dumps(T)).encode()).hexdigest()[:8]
    return dict(q=stem, opts=[], a=[note, why], w=[], fig=fig, lvl=lvl, key=[json.dumps(T)], multi=False, calc=None, vals=None, sig=sig, kind="fig", spec=spec, targets=T)

def _fig_html(p, pid):
    return (f'<div class="pq figq" data-id="{pid}" data-kind="fig" data-spec="{_html.escape(json.dumps(p["spec"], ensure_ascii=False, separators=(",", ":")), quote=True)}" data-targets="{_html.escape(json.dumps(p["targets"]), quote=True)}" data-sig="{p["sig"]}" data-multi="0">'
            f'<div class="meta">Tap the figure</div><div class="prompt">{_mark(autostem(p["q"]))}</div><div class="fgb"></div>'
            f'<p class="hint">Tap the figure to place your answer. Tap again to move it. With a keyboard, focus the figure and use the arrow keys.</p>'
            f'<div class="acts chkrow"><button type="button" class="btn primary chk" disabled>Check answer</button></div>'
            f'<div class="fb" hidden><p class="res" role="status"></p><p class="tapped"></p><div class="key"><div class="hd">Explanation</div><p>{p["a"][1]}</p></div>{_more_html(p)}<div class="acts"><button type="button" class="btn sm again">Try again</button></div></div></div>')

def qhtml(p, pid):
    """One interactive question. The page script handles selecting, checking, and feedback."""
    if p.get("kind") == "fig": return _fig_html(p, pid)
    if p.get("kind") == "sort": return _sort_html(p, pid)
    if p.get("kind") == "num": return _num_html(p, pid)
    opts = "".join(f'<li><button type="button" class="opt" data-k="{LETTERS[i]}" aria-pressed="false"><span class="k">{LETTERS[i]}</span><span class="tx">{o}</span></button></li>' for i, o in enumerate(p["opts"]))
    calc, extra = "", ""
    if p.get("calc"):
        spec = {k: p["calc"][k] for k in ("unit", "tiles", "ops")}
        calc = '<details class="calc"><summary>Work it out</summary><div class="cb"></div></details>'
        extra = f' data-calc="{_html.escape(json.dumps(spec, ensure_ascii=False), quote=True)}" data-vals="{_html.escape(json.dumps(p["vals"]), quote=True)}"'
    return (f'<div class="pq" data-id="{pid}" data-key="{",".join(p["key"])}" data-multi="{1 if p["multi"] else 0}" data-sig="{p["sig"]}"{extra}>'
            f'<div class="meta">Question</div><div class="prompt">{_mark(autostem(p["q"]))}</div><ol class="choices">{opts}</ol>{calc}'
            f'<div class="acts chkrow"><button type="button" class="btn primary chk" disabled>Check answer</button></div>'
            f'<div class="fb" hidden><p class="res" role="status"></p>{_explain(p)}{_more_html(p)}'
            f'<div class="acts"><button type="button" class="btn sm again">Try again</button></div></div></div>')

def render(blocks, figs, tid=None, ncards=0, problems=(), inline=None, num="", terms=(), take=()):
    """Guide HTML. `inline` maps a section index (order of the h2 headings) to problem numbers (1-based) that follow that section;
    questions for the last section, and any not placed, go to the practice set at the end, grouped by tier.
    `num` numbers the sections (1.4.1, 1.4.2, ...). `terms` are key terms wrapped at their first occurrence in the running text."""
    inline = inline or {}; out = []; sec = -1; placed = set(); done = set()
    qid = lambda n: f"{tid}:{ncards + n}"
    kk = lambda s: re.sub(r"\[\[(\d+)\|(.*?)\]\]", lambda m: f'<mark class="kn" data-k="{tid}-s{sec + 1}-{m.group(1)}">{m.group(2)}</mark>', s, flags=re.S)   # [[2|text]] marks the passage that Must know line 2 of the section summarises
    def box(i):
        items = take[i] if i < len(take) else None
        if not items: return ""
        kd = lambda j: f'class="kl" data-k="{tid}-s{i + 1}-{j}" tabindex="0"'
        lis = "".join((f'<li {kd(j)}><span class="tt">{_mark(x[0])}</span><figure class="av" data-av="{x[1]}"></figure></li>' if isinstance(x, tuple) else f"<li {kd(j)}>{_mark(x)}</li>") for j, x in enumerate(items, 1))
        return '<aside class="take"><div class="hd">Must know</div><ul>' + lis + "</ul></aside>"
    txt = lambda s: kk(_mark(_wrap_terms(s, terms, done)) if terms else _mark(s))
    def flush(i):
        ns = [n for n in inline.get(i, []) if 1 <= n <= len(problems)]
        if ns:
            out.append('<div class="checks">' + "".join(qhtml(problems[n - 1], qid(n)) for n in ns) + "</div>"); placed.update(ns)
    for b in blocks:
        k = b[0]
        if k == "h2":
            if sec >= 0: out.append(box(sec)); flush(sec)
            sec += 1
            out.append(f'<h2 id="{tid}-s{sec + 1}"><span class="sn">{num}.{sec + 1}</span>{b[1]}</h2>' if num else f"<h2>{b[1]}</h2>")
        elif k in ("h3", "p"): out.append(f"<{k}>{txt(b[1]) if k == 'p' else b[1]}</{k}>")
        elif k in ("ul", "ol"): out.append(f"<{k}>" + "".join(f"<li>{txt(i)}</li>" for i in b[1]) + f"</{k}>")
        elif k == "eq": out.append('<div class="eq">' + "<br>".join(kk(x) for x in b[1]) + "</div>")
        elif k == "avf":
            out.append(f'<figure class="av" data-av="{b[1]}"></figure>')
        elif k == "photo": out.append(photolib.figure_html(b[1]))
        elif k == "fig":
            assert b[1] in figs, b[1]
            out.append(f'<figure class="figure"><div class="fig">{figs[b[1]]}</div><div class="cap">{kk(b[2])}</div></figure>')
        elif k == "table":
            head = "".join(f"<th>{h}</th>" for h in b[1])
            rows = "".join("<tr>" + "".join(f"<td>{kk(c)}</td>" for c in r) + "</tr>" for r in b[2])
            out.append(f'<div class="tblwrap"><table class="tbl"><tr>{head}</tr>{rows}</table></div>')
        elif k == "ex":
            steps = "".join(f"<li>{s}</li>" for s in b[3])
            out.append(f'<div class="ex"><h3>{b[1]}</h3><div class="prompt">{_mark(autostem(b[2]))}</div><details><summary>Show solution</summary>'
                       f'<ol class="steps">{steps}</ol><p class="ans"><b>Answer:</b> {b[4]}</p></details></div>')
        elif k == "key":
            out.append('<div class="key"><div class="hd">Key points</div><ul>' + "".join(f"<li>{i}</li>" for i in b[1]) + "</ul></div>")
        elif k == "more":
            inner = []
            for x in b[3]:
                if x[0] == "p": inner.append(f"<p>{_mark(x[1])}</p>")
                elif x[0] in ("ul", "ol"): inner.append(f"<{x[0]}>" + "".join(f"<li>{_mark(i)}</li>" for i in x[1]) + f"</{x[0]}>")
                elif x[0] == "eq": inner.append('<div class="eq">' + "<br>".join(x[1]) + "</div>")
                elif x[0] == "h3": inner.append(f"<h3>{x[1]}</h3>")
                elif x[0] == "table":
                    inner.append('<div class="tblwrap"><table class="tbl"><tr>' + "".join(f"<th>{h}</th>" for h in x[1]) + "</tr>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in x[2]) + "</table></div>")
                else: raise ValueError(("a more block holds paragraphs, lists, equations, tables, and h3", x[0]))
            simple = f'<p class="simple">{_mark(b[2])}</p>' if b[2] else ""
            out.append(f'<div class="more"><button type="button" class="btn sm more-btn" aria-expanded="false">Show more details</button><div class="more-body" hidden><div class="mh">{b[1]}</div>{simple}{"".join(inner)}</div></div>')
        else: raise ValueError(k)
    if sec >= 0: out.append(box(sec))
    rest = [n for n in range(1, len(problems) + 1) if n not in placed]
    if rest:
        out.append(f'<h2 class="practice" id="{tid}-q">Practice questions</h2>')
        order = {"Easy": 0, "Moderate": 1, "Challenging": 2}          # the order questions are written in, from recall toward multi-step; it is not shown to the reader
        out.append("".join(qhtml(problems[n - 1], qid(n)) for n in sorted(rest, key=lambda n: (order.get(problems[n - 1]["lvl"], 1), n))))
    return "\n".join(out)

# ---------------------------------------------------------------- problems (multiple choice)
def _plain(s): return re.sub(r"<[^>]+>", "", s)
def _pos(stem, n): return int(hashlib.md5(_plain(stem).encode()).hexdigest(), 16) % n

def _problem(stem, opts, answer, why, w, lvl, fig, key, multi=False, calc=None, vals=None):
    assert len(set(opts)) == len(opts), ("duplicate options", stem[:50], opts)
    sig = hashlib.md5((_plain(stem) + "|" + "|".join(_plain(o) for o in opts) + "|" + ",".join(key)).encode()).hexdigest()[:8]   # changes if the options or their order change
    return dict(q=stem, opts=opts, a=[answer, why], w=list(w or []), fig=fig, lvl=lvl, key=list(key), multi=multi, calc=calc, vals=vals, sig=sig)

def PR(stem, correct, wrong, why, w=None, lvl="Moderate", fig=None):
    """One correct option. Its position comes from a hash of the stem: it varies between problems and never changes between builds."""
    opts = list(wrong); pos = _pos(stem, len(wrong) + 1); opts.insert(pos, correct)
    return _problem(stem, opts, f"<b>{LETTERS[pos]}.</b> {correct}", why, w, lvl, fig, [LETTERS[pos]])

def _generic(r): return any(abs(r / g - 1) < 1e-9 for g in (0.01, 0.1, 0.5, 2.0, 10.0, 100.0))

def PRN(stem, correct, wrong, fmt, why, w=None, lvl="Moderate", fig=None, calc=None):
    """Numeric choice: options sorted ascending (as on the exam) and formatted by fmt (a format string or a function).
    Distractors written to catch a specific mistake are always kept. Generic scale slips (half, double, a power of ten away) are
    interchangeable, so the engine picks which of them to show, placing the correct value at a rank set by a hash of the stem
    (whenever the kept traps allow it). The right answer's position then follows no pattern. Skipped for percentages and v/c,
    where scaled decoys could be impossible values."""
    g = fmt if callable(fmt) else (lambda v: fmt.format(v))
    f = lambda v: _noexp(g(v))
    wrong = list(wrong)
    skip = isinstance(fmt, str) and ("%" in fmt or fmt.rstrip().endswith("c"))
    if not skip and len(wrong) == 3 and correct > 0:
        fixed = [v for v in wrong if not _generic(v / correct)]
        bf = sum(v < correct for v in fixed); af = len(fixed) - bf
        want = min(max(_pos(stem, 4), bf), 3 - af)
        pb = [v for v in wrong if v < correct and _generic(v / correct)]; pa = [v for v in wrong if v > correct and _generic(v / correct)]
        below = [correct / 2, correct / 10, correct / 100, correct / 1000]; above = [correct * 2, correct * 10, correct * 100, correct * 1000]
        cand = fixed + (pb + [v for v in below if v not in pb])[:want - bf] + (pa + [v for v in above if v not in pa])[:3 - want - af]
        if len(cand) == 3 and len({correct, *cand}) == 4 and len({f(v) for v in [correct, *cand]}) == 4: wrong = cand
    vals = sorted(set([correct] + wrong)); opts = [f(v) for v in vals]; pos = vals.index(correct)
    return _problem(stem, opts, f"<b>{LETTERS[pos]}.</b> {opts[pos]}", why, w, lvl, fig, [LETTERS[pos]], calc=calc, vals=vals)

NUMW = {2: "two", 3: "three", 4: "four", 5: "five"}
def _count_stem(stem, n):
    """ABR form for a question with several correct answers: the stem says how many ('Which three of these ...') and ends with '(Please select three options.)'."""
    w = NUMW[n]; s = re.sub(r"\bWhich (of (?:these|the following))\b", rf"Which {w} \1", stem, count=1); tail = f" <i>(Please select {w} options.)</i>"
    return (s[:-4] + tail + "</p>") if s.endswith("</p>") else s + tail

def PRM(stem, correct, wrong, why, w=None, lvl="Moderate", fig=None):
    """Select the several correct options: options are shuffled deterministically and the answer lists every correct letter. The ABR asks for at least twice as many options as correct ones (checked in tests/abrstyle.py)."""
    items = sorted([(t, True) for t in correct] + [(t, False) for t in wrong], key=lambda x: hashlib.md5((stem + x[0]).encode()).hexdigest())
    opts = [t for t, _ in items]; letters = [LETTERS[i] for i, (_, ok) in enumerate(items) if ok]
    d = _problem(_count_stem(stem, len(correct)), opts, f"<b>{', '.join(letters)}</b>", why, w, lvl, fig, letters, True); d["stem0"] = stem; return d

import math
def sci(v, digits=2):
    """1.6e-13 -> '1.6 × 10<sup>−13</sup>'"""
    e = int(math.floor(math.log10(abs(v)))); m = v / 10 ** e
    return f"{m:.{digits - 1}f} × 10<sup>{e}</sup>".replace("<sup>-", "<sup>−")

# ---------------------------------------------------------------- "Work it out": specs for the unit-aware calculator
OPS = ("+", "−", "×", "÷", "(", ")", "²", "√(", "ln(", "log₂(", "log₁₀(", "2^(", "10^(", "e^(")
def _supstr(s): return str(s).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))
def _disp(v):
    if v != 0 and (abs(v) >= 1e5 or abs(v) < 1e-3):
        e = int(math.floor(math.log10(abs(v)))); m = v / 10 ** e
        return f"{m:.4g} × 10{_supstr(e)}"
    return f"{v:.6g}"
def TILE(name, v, unit="", disp=None, id=None):
    """A given or constant: label 'E = 25 keV'. `disp` fixes how the number is shown (for example '1.0')."""
    s = f"{disp or _disp(v)} {unit}".strip()
    return dict(id=id or name, t=(f"{name} = {s}" if name else s), s=s, v=float(v), u=unit)
def CONV(frm, to, factor, disp=None):
    """A conversion factor 1 frm = factor to, with unit to/frm. Multiply or divide by it so the units cancel."""
    d = disp or _disp(factor)
    return dict(id=f"{frm}→{to}", t=f"1 {frm} = {d} {to}", s=f"{d} {to}/{frm}", v=float(factor), u=f"{to}/{frm}")
def NUM(n): return dict(id=str(n), t=str(n), s=str(n), v=float(n), u="")
def CALC(unit, tiles, ops=("×", "÷"), solution=()):
    """unit: unit of the answer. solution: tile ids and operators that reach the correct option (used by tests, not shown)."""
    ids = [t["id"] for t in tiles]; assert len(set(ids)) == len(ids), ("duplicate tile ids", ids)
    for x in solution: assert x in ids or x in OPS, ("solution item is not a tile or operator", x)
    for o in ops: assert o in OPS, ("unknown operator", o)
    return dict(unit=unit, tiles=list(tiles), ops=list(ops), solution=list(solution))
