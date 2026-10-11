"""Original figures for the study site. Every function returns an inline SVG string.
Colors are CSS variables so figures follow light/dark: --fg ink, --mu muted, --c1..--c4 plot colors, --gr grid."""
import math
import calc

FS = "font-family:inherit;"

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg(w, h, body, label=""):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}" '
            f'style="{FS}font-size:13px">{body}</svg>')

def txt(x, y, s, size=13, anchor="start", color="var(--fg)", weight=400, rot=None, italic=False):
    t = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    st = f"font-size:{size}px;font-weight:{weight};" + ("font-style:italic;" if italic else "")
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{color}" style="{st}"{t}>{s}</text>'

def path(d, color="var(--c1)", w=2, dash=None, fill="none", op=1):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{ds} stroke-linejoin="round" stroke-linecap="round" opacity="{op}"/>'

def line(x1, y1, x2, y2, color="var(--fg)", w=1.5, dash=None, marker=False):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    mk = ' marker-end="url(#arr)"' if marker else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"{ds}{mk}/>'

def rect(x, y, w, h, fill="none", stroke="var(--fg)", sw=1.5, rx=0, op=1, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}" opacity="{op}"{ds}/>'

def circ(cx, cy, r, fill="none", stroke="var(--fg)", sw=1.5):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

ARROW = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0,0 L10,5 L0,10 z" fill="var(--fg)"/></marker></defs>')

def frange(a, b, n): return [a + (b - a) * i / (n - 1) for i in range(n)]

class Plot:
    """Minimal x/y plot with linear axes."""
    def __init__(self, w=560, h=340, ml=58, mr=18, mt=18, mb=50, xr=(0, 1), yr=(0, 1)):
        self.w, self.h, self.ml, self.mr, self.mt, self.mb = w, h, ml, mr, mt, mb
        self.xr, self.yr = xr, yr
        self.parts = []
    def X(self, x): a, b = self.xr; return self.ml + (x - a) / (b - a) * (self.w - self.ml - self.mr)
    def Y(self, y): a, b = self.yr; return self.h - self.mb - (y - a) / (b - a) * (self.h - self.mt - self.mb)
    def axes(self, xlab="", ylab="", xticks=(), yticks=(), grid=True, yfmt=None, xfmt=None):
        x0, x1, y0, y1 = self.ml, self.w - self.mr, self.h - self.mb, self.mt
        p = self.parts
        if grid:
            for v in yticks: p.append(line(x0, self.Y(v), x1, self.Y(v), "var(--gr)", 1))
            for v in xticks: p.append(line(self.X(v), y0, self.X(v), y1, "var(--gr)", 1))
        p.append(line(x0, y0, x1, y0, "var(--fg)", 1.5)); p.append(line(x0, y0, x0, y1, "var(--fg)", 1.5))
        for v in xticks:
            p.append(line(self.X(v), y0, self.X(v), y0 + 5, "var(--fg)", 1))
            p.append(txt(self.X(v), y0 + 19, (xfmt(v) if xfmt else f"{v:g}"), 12, "middle", "var(--mu)"))
        for v in yticks:
            p.append(line(x0 - 5, self.Y(v), x0, self.Y(v), "var(--fg)", 1))
            p.append(txt(x0 - 9, self.Y(v) + 4, (yfmt(v) if yfmt else f"{v:g}"), 12, "end", "var(--mu)"))
        if xlab: p.append(txt((x0 + x1) / 2, self.h - 9, xlab, 13, "middle"))
        if ylab: p.append(txt(15, (y0 + y1) / 2, ylab, 13, "middle", rot=-90))
        return self
    def curve(self, pts, color="var(--c1)", w=2.4, dash=None):
        d = "M" + " L".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        self.parts.append(path(d, color, w, dash)); return self
    def add(self, s): self.parts.append(s); return self
    def label(self, x, y, s, color="var(--fg)", size=13, anchor="start", weight=400, dx=0, dy=0):
        self.parts.append(txt(self.X(x) + dx, self.Y(y) + dy, s, size, anchor, color, weight)); return self
    def dot(self, x, y, color="var(--c1)", r=4):
        self.parts.append(circ(self.X(x), self.Y(y), r, color, color, 1)); return self
    def body(self): return "".join(self.parts)
    def out(self, label=""): return svg(self.w, self.h, ARROW + self.body(), label)

# ------------------------------------------------------------------ decay
def decay_curve():
    P = Plot(w=560, h=330, xr=(0, 5.2), yr=(0, 108))
    P.axes("Time (half-lives)", "Activity (% of initial)", [0, 1, 2, 3, 4, 5], [0, 25, 50, 75, 100])
    P.curve([(t, 100 * 2 ** (-t)) for t in frange(0, 5.2, 140)])
    labels = {0: "100", 1: "50", 2: "25", 3: "12.5", 4: "6.25", 5: "3.1"}
    for n in range(6):
        v = 100 * 2 ** (-n); P.dot(n, v)
        P.label(n, v, labels[n], "var(--fg)", 13, "start", 600, dx=8, dy=-8)
    tau = 1 / math.log(2)
    P.add(line(P.X(tau), P.Y(0), P.X(tau), P.Y(100 * math.exp(-1)), "var(--c2)", 1.6, "5 4"))
    P.dot(tau, 100 * math.exp(-1), "var(--c2)", 4.5)
    P.label(tau, 100 * math.exp(-1), "mean life: 36.8%", "var(--c2)", 13, "start", 600, dx=10, dy=-12)
    return P.out("Activity falls by half with each half-life; 36.8% remains after one mean life")

# ------------------------------------------------------------------ decay modes on a chart of the nuclides
def nuclide_chart():
    W, H = 600, 380
    b = [ARROW]
    b.append(path("M85,330 Q310,235 520,52", "var(--gr)", 38, None, "none", 1))
    b.append(txt(338, 160, "stable nuclei", 13, "middle", "var(--mu)", 600, rot=-33))
    b.append(line(60, 345, 570, 345, "var(--fg)", 1.5, marker=True))
    b.append(line(60, 345, 60, 22, "var(--fg)", 1.5, marker=True))
    b.append(txt(315, 372, "Neutrons, N", 13, "middle"))
    b.append(txt(22, 190, "Protons, Z", 13, "middle", rot=-90))
    u = 24
    def mover(x, y, dx, dy, col):
        ex, ey = x + dx * u, y + dy * u
        ang = math.atan2(dy, dx); L = 11
        head = path(f"M{ex:.1f},{ey:.1f} L{ex - L * math.cos(ang - 0.45):.1f},{ey - L * math.sin(ang - 0.45):.1f} "
                    f"L{ex - L * math.cos(ang + 0.45):.1f},{ey - L * math.sin(ang + 0.45):.1f} Z", col, 1.5, None, col)
        return circ(x, y, 5, col, col, 1) + line(x, y, ex, ey, col, 2.6) + head
    def two(x, y, a, b2, col, anchor):
        return txt(x, y, a, 15, anchor, col, 700) + txt(x, y + 17, b2, 13, anchor, col, 600)
    # beta minus: Z + 1 (up), N - 1 (left)
    b.append(mover(262, 302, -1, -1, "var(--c2)")); b.append(two(280, 314, "β⁻", "n → p, Z + 1", "var(--c2)", "start"))
    # beta plus or EC: Z - 1 (down), N + 1 (right)
    b.append(mover(190, 232, 1, 1, "var(--c3)")); b.append(two(176, 206, "β⁺ or EC", "p → n, Z − 1", "var(--c3)", "end"))
    # alpha: Z - 2, N - 2
    b.append(mover(452, 100, -2, 2, "var(--c4)")); b.append(two(478, 190, "α", "Z − 2, A − 4", "var(--c4)", "middle"))
    return svg(W, H, "".join(b), "Chart of the nuclides: beta-minus, beta-plus or electron capture, and alpha decay move a nucleus toward the band of stable nuclei")

# ------------------------------------------------------------------ parent-daughter equilibrium
def equilibrium():
    W, H = 700, 330
    out = [ARROW]
    tp, td = 65.94, 6.0067
    yf = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")
    A = Plot(w=330, h=H, ml=52, mr=10, mt=44, mb=50, xr=(0, 120), yr=(0, 1.05))
    A.axes("Time (h)", "Activity (relative to initial parent)", [0, 24, 48, 72, 96, 120], [0, 0.25, 0.5, 0.75, 1.0], yfmt=yf)
    A.curve([(t, math.exp(-calc.lam(tp) * t)) for t in frange(0, 120, 160)], "var(--c1)")
    A.curve([(t, calc.daughter_over_parent0(t, tp, td)) for t in frange(0, 120, 240)], "var(--c2)")
    tm = calc.t_max(tp, td); pk = calc.daughter_over_parent0(tm, tp, td)
    A.add(line(A.X(tm), A.Y(0), A.X(tm), A.Y(pk), "var(--mu)", 1.2, "4 4")).dot(tm, pk, "var(--fg)", 4)
    A.label(tm, 0, f"{tm:.0f} h", "var(--mu)", 12, "middle", dy=-6)
    A.label(58, 0.80, "Tc-99m (daughter)", "var(--c2)", 13, "start", 600)
    A.label(66, 0.33, "Mo-99 (parent)", "var(--c1)", 13, "start", 600)
    out.append(A.body())
    out.append(txt(52, 20, "Transient: Mo-99 → Tc-99m", 14, "start", "var(--fg)", 700))
    tp2, td2 = 28.8 * 365.25 * 24, 64.0
    ox = 360
    B = Plot(w=330, h=H, ml=52, mr=10, mt=44, mb=50, xr=(0, 450), yr=(0, 1.05))
    B.axes("Time (h)", "Activity (relative to initial parent)", [0, 100, 200, 300, 400], [0, 0.25, 0.5, 0.75, 1.0], yfmt=yf)
    B.curve([(t, math.exp(-calc.lam(tp2) * t)) for t in frange(0, 450, 20)], "var(--c1)")
    B.curve([(t, calc.daughter_over_parent0(t, tp2, td2)) for t in frange(0, 450, 200)], "var(--c2)")
    B.label(8, 1.0, "Sr-90 (parent, T½ 28.8 y)", "var(--c1)", 13, "start", 600, dy=-12)
    B.label(150, 0.55, "Y-90 (daughter, T½ 64 h)", "var(--c2)", 13, "start", 600, dy=22)
    out.append(f'<g transform="translate({ox},0)">{B.body()}</g>')
    out.append(txt(ox + 52, 20, "Secular: Sr-90 → Y-90", 14, "start", "var(--fg)", 700))
    return svg(W, H, "".join(out), "Activity of parent and daughter over time for a transient and a secular equilibrium")

# ------------------------------------------------------------------ PDD curves (schematic)
def _pdd_fit(dmax, pdd10, surf, f=100.0):
    def g(d, k, mu): return (1 - (1 - surf) * math.exp(-k * d)) * math.exp(-mu * d) / (f + d) ** 2
    def k_for(mu):
        lo, hi = 0.05, 20.0
        for _ in range(80):
            k = (lo + hi) / 2
            val = (1 - surf) * k * math.exp(-k * dmax) / (1 - (1 - surf) * math.exp(-k * dmax)) - mu - 2 / (f + dmax)
            if val > 0: lo = k
            else: hi = k
        return (lo + hi) / 2
    lo, hi = 0.001, 0.2
    for _ in range(80):
        mu = (lo + hi) / 2; k = k_for(mu)
        p10 = 100 * g(10, k, mu) / g(dmax, k, mu)
        if p10 > pdd10: lo = mu
        else: hi = mu
    mu = (lo + hi) / 2; k = k_for(mu)
    return lambda d: 100 * g(d, k, mu) / g(dmax, k, mu)

def pdd_curves():
    P = Plot(w=580, h=350, xr=(0, 30), yr=(0, 105))
    P.axes("Depth in water (cm)", "Percent depth dose", [0, 5, 10, 15, 20, 25, 30], [0, 20, 40, 60, 80, 100])
    P.add(line(P.X(10), P.Y(0), P.X(10), P.Y(105), "var(--mu)", 1.2, "4 4"))
    spec = ((3.0, 77.0, 0.11, "var(--c3)", "15 MV", "≈77", -14, 96), (2.5, 73.5, 0.13, "var(--c1)", "10 MV", "≈74", 4, 88), (1.5, 67.0, 0.17, "var(--c2)", "6 MV", "≈67", 22, 80))
    for dmax, p10, s, col, nm, lab, dyend, ylab in spec:
        fn = _pdd_fit(dmax, p10, s)
        P.curve([(d, min(100.0, fn(d))) for d in frange(0.0, 30, 200)], col, 2.4)
        P.dot(10, fn(10), col, 4)
        P.label(10.6, ylab, f"{nm}: {lab} at 10 cm", col, 13, "start", 600)
    P.label(0.4, 8, "10 × 10 cm, SSD 100 cm", "var(--mu)", 12)
    return P.out("Schematic percent depth dose curves for 6, 10 and 15 MV photons")

# ------------------------------------------------------------------ PDD versus TMR geometry
def pdd_vs_tmr():
    W, H = 700, 320
    b = [ARROW]
    def src(cx): return circ(cx, 34, 5, "var(--fg)", "var(--fg)", 1) + txt(cx + 10, 30, "Source", 12, "start", "var(--mu)")
    def beam(cx, ytop, ybot, half_at_ybot):
        k = half_at_ybot / (ybot - ytop)
        return (line(cx, ytop, cx - k * (ybot - ytop), ybot, "var(--mu)", 1.2, "5 4") + line(cx, ytop, cx + k * (ybot - ytop), ybot, "var(--mu)", 1.2, "5 4"))
    cx = 170
    b.append(txt(20, 20, "PDD: surface fixed, point moves", 14, "start", "var(--fg)", 700))
    b.append(src(cx)); b.append(beam(cx, 34, 285, 120))
    b.append(rect(55, 150, 230, 130, "var(--gr)", "var(--fg)", 1.5, 0, 0.55))
    b.append(line(35, 34, 35, 150, "var(--fg)", 1.2, marker=True) + line(35, 150, 35, 34, "var(--fg)", 1.2, marker=True))
    b.append(txt(28, 98, "SSD", 13, "end"))
    b.append(circ(cx, 168, 5, "var(--c2)", "var(--c2)", 1) + txt(cx + 12, 172, "dmax", 13, "start", "var(--c2)", 600))
    b.append(circ(cx, 236, 5, "var(--c1)", "var(--c1)", 1) + txt(cx + 12, 240, "d", 13, "start", "var(--c1)", 600))
    b.append(txt(170, 304, "PDD = D(d) / D(dmax), two points on the axis", 13, "middle", "var(--mu)"))
    ox = 380; cx2 = ox + 150
    b.append(txt(ox, 20, "TMR: point fixed at SAD, surface moves", 14, "start", "var(--fg)", 700))
    b.append(src(cx2)); b.append(beam(cx2, 34, 285, 120))
    b.append(rect(ox + 15, 150, 270, 130, "var(--gr)", "var(--fg)", 1.5, 0, 0.55))
    b.append(rect(ox + 15, 226, 270, 54, "none", "var(--c2)", 1.5, 0, 1, "5 4"))
    b.append(circ(cx2, 240, 5.5, "var(--fg)", "var(--fg)", 1) + txt(cx2 + 12, 244, "P", 14, "start", "var(--fg)", 700))
    b.append(line(ox + 5, 150, ox + 5, 240, "var(--c1)", 1.2, marker=True) + line(ox + 5, 240, ox + 5, 150, "var(--c1)", 1.2, marker=True))
    b.append(txt(ox - 1, 200, "d", 13, "end", "var(--c1)", 600))
    b.append(txt(ox + 280, 221, "dmax", 13, "end", "var(--c2)", 600))
    b.append(txt(ox + 150, 304, "TMR = D(P, depth d) / D(P, depth dmax)", 13, "middle", "var(--mu)"))
    return svg(W, H, "".join(b), "PDD is measured at a fixed surface distance with the detector moving; TMR is measured at a fixed point with the phantom thickness above it changing")

# ------------------------------------------------------------------ collimator and phantom scatter
def scatter_geometry():
    W, H = 600, 350
    b = [ARROW]
    sx, sy = 300, 26
    b.append(circ(sx, sy, 5, "var(--fg)", "var(--fg)", 1) + txt(sx + 10, sy + 4, "Source", 12, "start", "var(--mu)"))
    yj, half_open = 84, 46
    b.append(rect(170, yj - 12, 84, 24, "var(--gr)", "var(--fg)", 1.5)); b.append(rect(346, yj - 12, 84, 24, "var(--gr)", "var(--fg)", 1.5))
    yp = 240
    def edge(y_from, half_from, sign):
        k = half_from / (y_from - sy); return (sx + sign * k * (yp - sy), yp)
    for sgn in (-1, 1):
        x2, y2 = edge(yj, half_open, sgn); b.append(line(sx, sy, x2, y2, "var(--mu)", 1.3, "5 4"))
    yb, bh, inner_half = 150, 16, 58
    b.append(rect(190, yb, 242 - 190, bh, "var(--fg)", "var(--fg)", 1, 0, 0.75)); b.append(rect(358, yb, 410 - 358, bh, "var(--fg)", "var(--fg)", 1, 0, 0.75))
    for sgn in (-1, 1):
        x2, y2 = edge(yb + bh / 2, inner_half, sgn); b.append(line(sx, sy, x2, y2, "var(--c1)", 2.4))
    b.append(rect(90, yp, 420, 50, "var(--gr)", "var(--fg)", 1.5, 0, 0.55))
    b.append(txt(160, yj + 4, "jaws", 12, "end", "var(--mu)"))
    b.append(txt(420, yb + 12, "block", 12, "start", "var(--mu)"))
    b.append(txt(16, 40, "Sc follows the jaw opening", 13, "start", "var(--c2)", 600))
    b.append(txt(16, 56, "(head scatter)", 12, "start", "var(--c2)"))
    b.append(txt(300, yp + 74, "Sp follows the field that reaches the phantom (solid lines).", 13, "middle", "var(--c1)", 600))
    b.append(txt(300, yp + 92, "The block changes Sp but not Sc.", 12, "middle", "var(--c1)"))
    return svg(W, 345, "".join(b), "A block under the collimators narrows the field in the phantom but leaves the collimator opening unchanged")

# ------------------------------------------------------------------ regions of photon interaction dominance (schematic)
def interaction_regions():
    P = Plot(w=580, h=360, xr=(-2, 2), yr=(0, 100))
    P.axes("Photon energy (MeV)", "Atomic number Z", [-2, -1, 0, 1, 2], [0, 20, 40, 60, 80, 100], xfmt=lambda v: f"{10 ** v:g}")
    left = lambda Z: 10 ** (-2.5395) * Z ** 1.1697        # photoelectric = Compton
    right = lambda Z: 10 ** 1.947 * Z ** -0.6522          # Compton = pair production
    zs = frange(1.5, 100, 160)
    P.curve([(math.log10(left(z)), z) for z in zs if -2 <= math.log10(left(z)) <= 2], "var(--c2)", 2.4)
    P.curve([(math.log10(right(z)), z) for z in zs if -2 <= math.log10(right(z)) <= 2], "var(--c1)", 2.4)
    for Z, nm, e1, e2, l1, l2 in ((7.4, "Water, Z ≈ 7.4", 0.03, 24, "30 keV", "24 MeV"), (82, "Lead, Z = 82", 0.5, 5, "0.5 MeV", "5 MeV")):
        P.add(line(P.X(-2), P.Y(Z), P.X(2), P.Y(Z), "var(--mu)", 1.1, "4 4"))
        P.dot(math.log10(e1), Z, "var(--c2)", 4.5); P.dot(math.log10(e2), Z, "var(--c1)", 4.5)
        P.label(math.log10(e1), Z, l1, "var(--c2)", 12, "start", 600, dx=9, dy=-10)
        if Z > 50: P.label(math.log10(e2), Z, l2, "var(--c1)", 12, "end", 600, dx=-9, dy=-8)
        else: P.label(math.log10(e2), Z, l2, "var(--c1)", 12, "start", 600, dx=10, dy=-12)
        P.label(-1.98, Z, nm, "var(--mu)", 12, "start", 400, dy=15 if Z > 50 else -7)
    P.label(-1.55, 66, "Photoelectric", "var(--fg)", 14, "middle", 700)
    P.label(0.15, 30, "Compton", "var(--fg)", 14, "middle", 700)
    P.label(1.45, 66, "Pair production", "var(--fg)", 14, "middle", 700)
    return P.out("Regions where the photoelectric effect, Compton scattering, or pair production dominates, by photon energy and atomic number")

# ------------------------------------------------------------------ kerma and absorbed dose with depth (schematic)
def kerma_dose():
    mu, R = 0.07, 2.5
    K = lambda d: 100 * math.exp(-mu * d)
    def D(d):
        if d <= R: return 100 * (1 - math.exp(-mu * d)) / (mu * R)
        return 100 * math.exp(-mu * d) * (math.exp(mu * R) - 1) / (mu * R)
    P = Plot(w=580, h=340, xr=(0, 14), yr=(0, 110))
    P.axes("Depth (cm)", "Relative to surface kerma (%)", [0, 2, 4, 6, 8, 10, 12, 14], [0, 20, 40, 60, 80, 100])
    P.curve([(d, K(d)) for d in frange(0, 14, 100)], "var(--c2)")
    P.curve([(d, D(d)) for d in frange(0, 14, 240)], "var(--c1)")
    P.add(line(P.X(R), P.Y(0), P.X(R), P.Y(D(R)), "var(--mu)", 1.2, "4 4"))
    P.label(R, 0, "dmax", "var(--mu)", 12, "middle", dy=-6)
    P.label(9.5, D(9.5), "Dose", "var(--c1)", 13, "middle", 600, dy=-12)
    P.label(9.5, K(9.5), "Kerma", "var(--c2)", 13, "middle", 600, dy=22)
    P.label(4.6, 8, "Contamination electrons ignored", "var(--mu)", 12, "start")
    return P.out("Kerma falls with depth; absorbed dose builds up to dmax and then stays slightly above kerma")

# ------------------------------------------------------------------ relativity: speed versus kinetic energy
def beta_vs_ke():
    P = Plot(w=560, h=330, xr=(-2, 3), yr=(0, 1.06))
    P.axes("Kinetic energy (MeV)", "Speed (fraction of c)", [-2, -1, 0, 1, 2, 3], [0, 0.25, 0.5, 0.75, 1.0], xfmt=lambda v: f"{10 ** v:g}")
    xs = frange(-2, 3, 200)
    P.curve([(x, calc.beta_ke(10 ** x, calc.ME)) for x in xs], "var(--c1)")
    P.curve([(x, calc.beta_ke(10 ** x, calc.MP)) for x in xs], "var(--c2)")
    P.add(line(P.X(-2), P.Y(1), P.X(3), P.Y(1), "var(--mu)", 1.2, "5 4"))
    P.label(2.95, 1.0, "c", "var(--mu)", 13, "end", 600, dy=-6)
    P.label(-1.75, 0.40, "electron", "var(--c1)", 14, "start", 600)
    P.label(2.3, 0.45, "proton", "var(--c2)", 14, "start", 600)
    be6 = calc.beta_ke(6, calc.ME); P.dot(math.log10(6), be6, "var(--c1)", 4.5)
    P.label(math.log10(6), be6, f"6 MeV electron: {be6:.3f}c", "var(--fg)", 13, "start", 600, dx=10, dy=24)
    bp = calc.beta_ke(150, calc.MP); P.dot(math.log10(150), bp, "var(--c2)", 4.5)
    P.label(math.log10(150), bp, f"150 MeV proton: {bp:.2f}c", "var(--fg)", 13, "end", 600, dx=-10, dy=-8)
    return P.out("Speed against kinetic energy: electrons reach nearly the speed of light by a few MeV; protons are still at half of it at 150 MeV")

# ------------------------------------------------------------------ hydrogen energy levels
def bohr_levels():
    P = Plot(w=560, h=340, ml=60, mr=20, mt=16, mb=16, xr=(0, 10), yr=(-14.8, 1.0))
    P.add(line(P.ml, P.Y(1.0), P.ml, P.Y(-14.8), "var(--fg)", 1.5))
    for v in (0, -5, -10):
        P.add(line(P.ml - 5, P.Y(v), P.ml, P.Y(v), "var(--fg)", 1)); P.add(txt(P.ml - 9, P.Y(v) + 4, f"{v}", 12, "end", "var(--mu)"))
    P.add(txt(14, (P.Y(1.0) + P.Y(-14.8)) / 2, "Energy (eV)", 13, "middle", rot=-90))
    for n in range(1, 5):
        e = calc.h_level(n); P.add(line(P.X(1.0), P.Y(e), P.X(6.2), P.Y(e), "var(--c1)", 2.4))
        P.add(txt(P.X(6.4), P.Y(e) + 4, f"n = {n}", 13, "start", "var(--fg)", 600)); P.add(txt(P.X(7.7), P.Y(e) + 4, f"{e:.1f} eV".replace("-", "−") if abs(e) > 10 else f"{e:.2f} eV".replace("-", "−"), 13, "start", "var(--mu)"))
    P.add(line(P.X(1.0), P.Y(0), P.X(6.2), P.Y(0), "var(--mu)", 1.6, "6 4"))
    P.add(txt(P.X(6.4), P.Y(0) + 4, "ionized", 13, "start", "var(--mu)")); P.add(txt(P.X(7.7), P.Y(0) + 4, "0 eV", 13, "start", "var(--mu)"))
    e1, e2, e3 = calc.h_level(1), calc.h_level(2), calc.h_level(3)
    P.add(line(P.X(2.0), P.Y(e2), P.X(2.0), P.Y(e1) - 3, "var(--c2)", 2, marker=True))
    P.add(txt(P.X(2.15), P.Y((e1 + e2) / 2) + 4, f"{calc.h_photon_ev(2, 1):.1f} eV photon", 13, "start", "var(--c2)", 600))
    P.add(line(P.X(4.6), P.Y(e3), P.X(4.6), P.Y(e2) - 3, "var(--c2)", 2, marker=True))
    P.add(txt(P.X(4.75), P.Y((e2 + e3) / 2) + 4, f"{calc.h_photon_ev(3, 2):.2f} eV", 13, "start", "var(--c2)", 600))
    P.add(line(P.X(5.7), P.Y(e1), P.X(5.7), P.Y(0) + 3, "var(--mu)", 1.6, "5 4", marker=True))
    P.add(txt(P.X(5.55), P.Y(-8.0), f"ionization {-e1:.1f} eV", 13, "end", "var(--mu)", 600))
    return P.out("Hydrogen energy levels; levels crowd together toward the ionization limit; arrows mark photon emission")

# ------------------------------------------------------------------ binding energy per nucleon
def be_curve():
    pts = [(2, 1.112), (4, 7.074), (12, 7.680), (16, 7.976), (28, 8.448), (40, 8.551), (56, 8.790), (62, 8.795), (90, 8.710), (120, 8.505), (208, 7.867), (238, 7.570)]
    P = Plot(w=560, h=330, xr=(0, 250), yr=(0, 10))
    P.axes("Mass number A", "Binding energy per nucleon (MeV)", [0, 50, 100, 150, 200, 250], [0, 2, 4, 6, 8, 10])
    P.curve(pts, "var(--c1)", 2.2)
    for a, e in pts: P.dot(a, e, "var(--c1)", 3.6)
    for a, e, s, anc, dx, dy in [(2, 1.112, "H-2", "start", 9, 4), (4, 7.074, "He-4", "start", 6, 20), (12, 7.680, "C-12", "start", 8, 20), (56, 8.790, "Fe-56", "middle", 0, -12), (238, 7.570, "U-238", "end", -2, -12)]:
        P.label(a, e, s, "var(--fg)", 13, anc, 600, dx=dx, dy=dy)
    P.label(22, 4.6, "light nuclei fuse: energy released", "var(--mu)", 13, "start", 400)
    P.label(118, 5.9, "heavy nuclei split: energy released", "var(--mu)", 13, "start", 400)
    return P.out("Binding energy per nucleon against mass number: it peaks near iron and nickel")

# ------------------------------------------------------------------ decay schemes: Co-60 and Cs-137
def decay_schemes():
    W, Hh, base = 700, 352, 306
    p = []
    def lev(x1, x2, y, color="var(--fg)", w=2.4): p.append(line(x1, y, x2, y, color, w))
    # ---- Co-60 -> Ni-60
    s = 240 / 2.824; yp, y25, y13 = base - 2.824 * s, base - 2.505 * s, base - 1.333 * s
    p.append(txt(170, 20, "Co-60 → Ni-60", 14, "middle", "var(--fg)", 600)); p.append(txt(170, 37, "T½ = 5.27 y", 12, "middle", "var(--mu)"))
    lev(30, 100, yp, "var(--c1)"); lev(150, 300, y25); lev(150, 300, y13); lev(150, 300, base)
    p.append(line(100, yp, 150, y25 - 2, "var(--c1)", 2, marker=True)); p.append(txt(106, yp - 5, "β⁻ 99.9%", 12, "start", "var(--c1)", 600))
    p.append(line(185, y25, 185, y13 - 3, "var(--c2)", 2, marker=True)); p.append(txt(192, (y25 + y13) / 2 + 4, "γ 1.173", 12, "start", "var(--c2)", 600))
    p.append(line(250, y13, 250, base - 3, "var(--c2)", 2, marker=True)); p.append(txt(257, (y13 + base) / 2 + 4, "γ 1.332", 12, "start", "var(--c2)", 600))
    for y, t in ((y25, "2.505"), (y13, "1.333"), (base, "0")): p.append(txt(306, y + 4, t, 12, "start", "var(--mu)"))
    p.append(txt(306, 60, "MeV", 11, "start", "var(--mu)"))
    p.append(txt(65, base + 20, "Z = 27", 12, "middle", "var(--mu)")); p.append(txt(225, base + 20, "Z = 28", 12, "middle", "var(--mu)"))
    # ---- Cs-137 -> Ba-137
    ox = 350; s2 = 240 / 1.176; yq, y66 = base - 1.176 * s2, base - 0.662 * s2
    p.append(txt(ox + 170, 20, "Cs-137 → Ba-137", 14, "middle", "var(--fg)", 600)); p.append(txt(ox + 170, 37, "T½ = 30.1 y", 12, "middle", "var(--mu)"))
    lev(ox + 30, ox + 100, yq, "var(--c1)"); lev(ox + 150, ox + 300, y66); lev(ox + 150, ox + 300, base)
    p.append(line(ox + 100, yq, ox + 150, y66 - 3, "var(--c1)", 2, marker=True)); p.append(txt(ox + 120, yq + 62, "β⁻ 94.4%", 12, "end", "var(--c1)", 600))
    p.append(line(ox + 100, yq, ox + 150, base - 3, "var(--c1)", 2, marker=True)); p.append(txt(ox + 130, yq + 190, "β⁻ 5.6%", 12, "end", "var(--c1)", 600))
    p.append(line(ox + 215, y66, ox + 215, base - 3, "var(--c2)", 2, marker=True)); p.append(txt(ox + 222, (y66 + base) / 2 + 4, "γ 0.662", 12, "start", "var(--c2)", 600))
    p.append(txt(ox + 155, y66 - 7, "Ba-137m, T½ = 2.55 min", 12, "start", "var(--mu)"))
    for y, t in ((y66, "0.662"), (base, "0")): p.append(txt(ox + 306, y + 4, t, 12, "start", "var(--mu)"))
    p.append(txt(ox + 306, yq, "MeV", 11, "start", "var(--mu)"))
    p.append(txt(ox + 65, base + 20, "Z = 55", 12, "middle", "var(--mu)")); p.append(txt(ox + 225, base + 20, "Z = 56", 12, "middle", "var(--mu)"))
    return svg(W, Hh, ARROW + "".join(p), "Decay schemes of Co-60 and Cs-137: energy upward, atomic number to the right")

# ================================================================== multileaf collimator leaves (panels: one svg each, so that they stack on a phone)
def _panel(w, h, body, label):
    """One panel of a multi-panel figure: its own svg, so that panels sit side by side on a wide screen and stack on a phone."""
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label)}" '
            f'style="{FS}font-size:13px;display:block;flex:0 1 {w}px;width:{w}px;max-width:100%;height:auto">{ARROW}{body}</svg>')

def _panels(*ps): return '<div class="panels">' + "".join(ps) + "</div>"

def _poly(pts, color="var(--fg)", w=1.5, fill="none", op=1, dash=None):
    return path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", color, w, dash, fill, op)

def _tickv(x, y1, y2, color="var(--fg)", w=1.3, cap=4):
    return line(x, y1, x, y2, color, w) + line(x - cap, y1, x + cap, y1, color, w) + line(x - cap, y2, x + cap, y2, color, w)

def _tickh(x1, x2, y, color="var(--fg)", w=1.3, cap=4):
    return line(x1, y, x2, y, color, w) + line(x1, y - cap, x1, y + cap, color, w) + line(x2, y - cap, x2, y + cap, color, w)

def _title(x, s): return txt(x, 18, s, 14, "start", "var(--fg)", 700)

def _halo(t): return t.replace("<text ", '<text stroke="var(--paper)" stroke-width="4" stroke-linejoin="round" paint-order="stroke" ', 1)   # a label that stays readable over a thin line

# ------------------------------------------------------------------ the leaf bank: side view and beam's-eye view
def mlc_bank():
    H = 266
    # side view of two opposing leaves under the source
    b = [_title(6, "Side view")]
    sx, sy = 108, 42; yt, yb = 104, 164; ym = (yt + yb) / 2; R = 44.0; s = R - math.sqrt(R * R - (ym - yt) ** 2); tl, tr = 92, 124; plane = 232
    b.append(circ(sx, sy, 5, "var(--fg)", "var(--fg)", 1) + txt(sx + 10, sy + 4, "Source", 12, "start", "var(--mu)"))
    k = (plane - sy) / (ym - sy)
    for xt in (tl, tr): b.append(line(sx, sy, sx + (xt - sx) * k, plane, "var(--mu)", 1.2, "5 4"))
    b.append(path(f"M 6,{yt} L {tl - s:.1f},{yt} A {R:g} {R:g} 0 0 1 {tl - s:.1f},{yb} L 6,{yb} Z", "var(--fg)", 1.5, None, "var(--gr)"))
    b.append(path(f"M 194,{yt} L {tr + s:.1f},{yt} A {R:g} {R:g} 0 0 0 {tr + s:.1f},{yb} L 194,{yb} Z", "var(--fg)", 1.5, None, "var(--gr)"))
    b.append(line(16, yt + 1, 16, yb - 1, "var(--fg)", 1.2, marker=True)); b.append(line(16, yb - 1, 16, yt + 1, "var(--fg)", 1.2, marker=True)); b.append(txt(24, ym + 4, "thickness", 12, "start"))
    b.append(line(20, yt - 12, 64, yt - 12, "var(--fg)", 1.2, marker=True)); b.append(line(64, yt - 12, 20, yt - 12, "var(--fg)", 1.2, marker=True)); b.append(txt(42, yt - 20, "travel", 12, "middle", "var(--mu)"))
    b.append(txt((tr + s + 194) / 2, ym + 4, "tungsten", 12, "middle", "var(--fg)"))
    b.append(line(36, plane, 180, plane, "var(--fg)", 1.2))
    xl, xr = sx + (tl - sx) * k, sx + (tr - sx) * k
    b.append(line(xl, plane - 7, xl, plane + 7, "var(--fg)", 1.5)); b.append(line(xr, plane - 7, xr, plane + 7, "var(--fg)", 1.5))
    b.append(txt(108, plane + 24, "isocenter plane", 12, "middle", "var(--mu)"))
    P = [_panel(200, H, "".join(b), "Side view of two opposing tungsten leaves with rounded ends, with the beam from the source passing between them to the isocenter plane")]
    # beam's-eye view of the same circular target with wide and narrow leaves
    def bev(rowh):
        w = 190; xc = w / 2; cy = 118; r = 56; top = cy - 90; n = int(180 / rowh)
        out = [_title(6, f"{rowh / 20:.1f} cm leaves"), txt(6, 36, "Beam's-eye view", 12, "start", "var(--mu)")]
        for i in range(n):
            ya, yb2 = top + i * rowh, top + (i + 1) * rowh
            dmin = 0 if ya <= cy <= yb2 else min(abs(ya - cy), abs(yb2 - cy))
            half = math.sqrt(r * r - dmin * dmin) if dmin < r else 0.0
            out.append(rect(2, ya, xc - half - 2, rowh, "var(--gr)", "var(--fg)", 1)); out.append(rect(xc + half, ya, w - 2 - xc - half, rowh, "var(--gr)", "var(--fg)", 1))
        out.append(path(f"M {xc - r},{cy} A {r} {r} 0 1 1 {xc + r},{cy} A {r} {r} 0 1 1 {xc - r},{cy} Z", "var(--c2)", 2.2, "6 4"))
        out.append(txt(xc, cy + 4, "target", 13, "middle", "var(--c2)", 600))
        yr = top + (n // 2 + 1) * rowh                              # one row on the right, marked with its width
        out.append(_tickv(w - 14, yr, yr + rowh, "var(--fg)", 1.5, 4)); out.append(txt(w - 21, yr + rowh / 2 + 5, "w", 13, "end", "var(--fg)", 700))
        return _panel(w, 218, "".join(out), f"Beam's-eye view of a circular target shaped by two opposing banks of leaves {rowh / 20:.1f} cm wide at the isocenter, with a stepped edge")
    P += [bev(20), bev(10)]
    return _panels(*P)

# ------------------------------------------------------------------ leaf ends: straight, divergent, rounded
MLC_END = dict(ys=-300.0, y1=118.0, y2=188.0, yp=262.0, R=50.0, edges={-1: -14.0, 1: 60.0})   # geometry of the leaf-end figure in drawing units: the source (above the panel), the top and bottom of the leaf, the plane, the radius of the rounded end, and the edges (left near the axis, right far from it)

def _end_kx(y): return (y - MLC_END["ys"]) / (MLC_END["y1"] - MLC_END["ys"])           # how far a ray from the source has spread at height y, relative to the top of the leaf

def _end_face(design, side, e):
    """Lateral position of the end face at height y, for an edge e from the axis at the top of the leaf."""
    y1, y2, R = MLC_END["y1"], MLC_END["y2"], MLC_END["R"]; ym = (y1 + y2) / 2
    if design == "straight": return lambda y: e
    if design == "divergent": return lambda y: e * _end_kx(y)
    em = e * _end_kx(ym)                                        # rounded: the tip lies on the ray through the middle of the leaf
    if side < 0:
        cx = em - R; return lambda y: cx + math.sqrt(R * R - (y - ym) ** 2)
    cx = em + R; return lambda y: cx - math.sqrt(R * R - (y - ym) ** 2)

def _end_rays(bx):
    """Offsets, at the top of the leaf, of the ray that first crosses all of the leaf and of the ray that first touches it (the smaller offset first)."""
    yy = [MLC_END["y1"] + (MLC_END["y2"] - MLC_END["y1"]) * i / 120 for i in range(121)]
    def root(which):
        lo, hi = -300.0, 300.0
        for _ in range(80):
            m = (lo + hi) / 2; d = [m * _end_kx(y) - bx(y) for y in yy]; v = (min(d), max(d))[which]
            lo, hi = (m, hi) if v < 0 else (lo, m)
        return (lo + hi) / 2
    return root(1), root(0)

def mlc_end_bands():
    """Width, at the top of the leaf, of the part of the beam that crosses only part of a leaf end, for each design and side."""
    out = {}
    for d in ("straight", "divergent", "rounded"):
        out[d] = {}
        for side, e in MLC_END["edges"].items():
            lo, hi = _end_rays(_end_face(d, side, e)); out[d][side] = hi - lo
    return out

def mlc_leaf_ends():
    H = 330
    ys, y1, y2, yp = MLC_END["ys"], MLC_END["y1"], MLC_END["y2"], MLC_END["yp"]
    ym = (y1 + y2) / 2; R = MLC_END["R"]; hh = (y2 - y1) / 2
    kx, face, rays = _end_kx, _end_face, _end_rays
    E = MLC_END["edges"]
    out = []
    for pi, (d, name, note) in enumerate((("straight", "Straight end", ("narrow near the axis,", "wide far from it")), ("divergent", "Divergent end", ("narrow everywhere", "")), ("rounded", "Rounded end", ("nearly the same width", "everywhere")))):
        w = 197; ax = 56.0; xr = w - 8; b = [_title(6, name)]
        b.append(line(ax, 48, ax, yp, "var(--mu)", 1, "2 4")); b.append(txt(w / 2, 38, "from the source", 12, "middle", "var(--mu)"))
        if pi == 0: b.append(_halo(txt(ax + 5, 100, "axis", 12, "start", "var(--mu)")))
        for side in (-1, 1):
            bx = face(d, side, E[side]); lo_, hi_ = rays(bx)
            free, full = (hi_, lo_) if side < 0 else (lo_, hi_)
            xf = lambda t0, y: ax + t0 * kx(y)
            b.append(_poly([(xf(free, y2), y2), (xf(full, y2), y2), (xf(full, yp), yp), (xf(free, yp), yp)], "none", 0, "var(--c2)", 0.30))
            b.append(line(xf(free, 58), 58, xf(free, y1), y1, "var(--mu)", 1.2, "5 4"))
            for t0 in (free, full): b.append(line(xf(t0, y2), y2, xf(t0, yp), yp, "var(--c2)", 1.6))
            if d == "rounded":
                s = R - math.sqrt(R * R - hh * hh); em = E[side] * kx(ym)
                if side < 0:
                    tx = ax + em - s; b.append(path(f"M 6,{y1} L {tx:.1f},{y1} A {R:g} {R:g} 0 0 1 {tx:.1f},{y2} L 6,{y2} Z", "var(--fg)", 1.5, None, "var(--gr)"))
                else:
                    tx = ax + em + s; b.append(path(f"M {xr},{y1} L {tx:.1f},{y1} A {R:g} {R:g} 0 0 0 {tx:.1f},{y2} L {xr},{y2} Z", "var(--fg)", 1.5, None, "var(--gr)"))
            else:
                pts = [(6, y1), (ax + bx(y1), y1), (ax + bx(y2), y2), (6, y2)] if side < 0 else [(xr, y1), (ax + bx(y1), y1), (ax + bx(y2), y2), (xr, y2)]
                b.append(_poly(pts, "var(--fg)", 1.5, "var(--gr)"))
            b.append(line(xf(free, yp), yp, xf(full, yp), yp, "var(--c2)", 5))
            if pi == 0 and side > 0: b.append(_halo(txt(xf(free, 236) - 6, 226, "partly", 12, "end", "var(--c2)", 600))); b.append(_halo(txt(xf(free, 236) - 6, 240, "transmitted", 12, "end", "var(--c2)", 600)))
        if pi == 0: b.append(txt(xr - 10, y1 + 40, "leaf", 12, "end", "var(--mu)"))
        b.append(line(6, yp, xr, yp, "var(--fg)", 1.2))
        if pi == 0: b.append(txt(6, yp + 18, "isocenter plane", 12, "start", "var(--mu)"))
        b.append(txt(w / 2, yp + 42, note[0], 13, "middle", "var(--fg)"))
        if note[1]: b.append(txt(w / 2, yp + 59, note[1], 13, "middle", "var(--fg)"))
        out.append(_panel(w, H, "".join(b), f"Side view of the ends of two opposing leaves, one near the beam axis and one far from it, with a {name.lower()} and the part of the beam that crosses only part of the leaf end"))
    return _panels(*out)

# ------------------------------------------------------------------ rounded ends, the gap, and the dosimetric leaf gap
def mlc_dlg():
    H = 302
    t = 80.0; yt, yb = 64.0, 144.0; R = 58.0; s = R - math.sqrt(R * R - (t / 2) ** 2)           # s = 16: the lateral extent of the rounded end
    base, top, leak = 258.0, 180.0, 3.0                          # zero and full fluence under the leaves, and the transmission of a leaf
    out = []
    for name, g in (("Closed, g = 0", 0.0), ("Open, gap g", 30.0)):
        w = 292; xc = w / 2 + 6; xl, xr = xc - g / 2, xc + g / 2; L, Rr = 22.0, w - 4.0
        b = [_title(6, name)]
        for k in range(8): xx = 36 + k * 34; b.append(line(xx, 28, xx, 56, "var(--mu)", 1.3, None, True))
        b.append(path(f"M {L},{yt} L {xl - s:.1f},{yt} A {R:g} {R:g} 0 0 1 {xl - s:.1f},{yb} L {L},{yb} Z", "var(--fg)", 1.5, None, "var(--gr)"))
        b.append(path(f"M {Rr},{yt} L {xr + s:.1f},{yt} A {R:g} {R:g} 0 0 0 {xr + s:.1f},{yb} L {Rr},{yb} Z", "var(--fg)", 1.5, None, "var(--gr)"))
        pts = [(L, base - leak), (xl - s, base - leak), (xl, top), (xr, top), (xr + s, base - leak), (Rr, base - leak)]
        pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
        b.append(_poly([(L, base)] + pts + [(Rr, base)], "none", 0, "var(--c1)", 0.28)); b.append(path("M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts), "var(--c1)", 2))
        b.append(line(L, base, Rr, base, "var(--fg)", 1.2))
        ex0, ex1 = xl - s / 2, xr + s / 2                        # each rounded end adds s/2 to the width of the equal-area opening
        b.append(rect(ex0, top, ex1 - ex0, base - leak - top, "none", "var(--c2)", 1.8, 0, 1, "5 4"))
        b.append(txt(4, top - 10, "fluence", 12, "start", "var(--mu)")); b.append(txt(4, top + 4, "1", 12, "start", "var(--mu)")); b.append(txt(4, base + 4, "0", 12, "start", "var(--mu)"))
        if g > 0:
            b.append(_tickh(xl, xr, (yt + yb) / 2)); b.append(txt(xc, (yt + yb) / 2 - 8, "g", 14, "middle", "var(--fg)", 700))
            b.append(_tickh(ex0, ex1, base + 16, "var(--c2)")); b.append(txt(xc, base + 34, "g + DLG", 14, "middle", "var(--c2)", 700))
        else:
            b.append(txt(xc, yb + 18, "tips touch", 12, "middle", "var(--mu)"))
            b.append(_tickh(ex0, ex1, base + 16, "var(--c2)")); b.append(txt(xc, base + 34, "DLG", 14, "middle", "var(--c2)", 700))
        out.append(_panel(w, H, "".join(b), f"{name}: two leaves with rounded ends and the relative fluence below them, with an opening of equal area (dashed)"))
    return _panels(*out)

# ------------------------------------------------------------------ tongue and groove
def mlc_tg():
    H = 236
    Wd, tau, gp = 72.0, 16.0, 4.0; ytop, ybot = 92.0, 192.0; ym = (ytop + ybot) / 2
    b = [_title(6, "End view of three leaves")]
    for i in range(3):
        X = 8 + i * (Wd + gp)
        b.append(_poly([(X + tau, ytop), (X + Wd + tau, ytop), (X + Wd + tau, ym), (X + Wd, ym), (X + Wd, ybot), (X, ybot), (X, ym + gp), (X + tau, ym + gp)], "var(--fg)", 1.5, "var(--gr)"))
    xj = 8 + Wd + tau + gp / 2                                   # the upper vertical gap of the first joint
    b.append(line(xj, 40, xj, ym + gp - 1, "var(--mu)", 1.3, "5 4", True)); b.append(txt(xj + 8, 52, "beam", 12, "start", "var(--mu)"))
    b.append(line(xj - 6, ym + gp + 3, xj + 6, ym + gp + 3, "var(--c2)", 2.6))
    b.append(txt(xj + 8, ym + gp + 20, "blocked", 12, "start", "var(--fg)"))
    jx, jy = 8 + Wd + tau / 2, ym + gp / 2                       # the horizontal part of the air gap, under the tongue
    b.append(txt(jx - 26, ybot + 28, "tongue and groove", 12, "start", "var(--fg)")); b.append(line(jx, ybot + 16, jx, jy + 2, "var(--mu)", 1)); b.append(circ(jx, jy, 2.2, "var(--fg)", "var(--fg)", 1))
    A = _panel(290, H, "".join(b), "End view of three neighbouring leaves with interlocking tongues and grooves, and a beam that cannot pass straight through the joint")
    w2 = 272; yA, w = 62.0, 56.0; yB = yA + w; xA, xB = 104.0, 206.0; xl = 4.0; tau2 = 12.0
    b = [_title(6, "Beam's-eye view of two leaves")]
    b.append(rect(xl, yA, xA - xl, w, "var(--gr)", "var(--fg)", 1.5)); b.append(rect(xl, yB, xB - xl, w + 8, "var(--gr)", "var(--fg)", 1.5))
    b.append(rect(xl, yB - tau2, xA - xl, tau2, "var(--gr)", "var(--fg)", 1.5)); b.append(rect(xA, yB - tau2, xB - xA, tau2, "var(--c2)", "var(--c2)", 1.5, 0, 0.4))
    b.append(txt(xl + 10, yA + 32, "leaf A", 13, "start")); b.append(txt(xl + 10, yB + 38, "leaf B", 13, "start"))
    b.append(txt(xA + 12, yA + 22, "strip shielded by", 12, "start", "var(--c2)", 600)); b.append(txt(xA + 12, yA + 38, "the tongue of leaf B", 12, "start", "var(--c2)", 600))
    B = _panel(w2, 200, "".join(b), "Beam's-eye view of two neighbouring leaves at different positions, with the strip along their boundary that the tongue of the extended leaf shields")
    return _panels(A, B)

def build():
    return dict(decay_curve=decay_curve(), nuclide_chart=nuclide_chart(), equilibrium=equilibrium(),
                pdd_curves=pdd_curves(), pdd_vs_tmr=pdd_vs_tmr(), scatter_geometry=scatter_geometry(),
                interaction_regions=interaction_regions(), kerma_dose=kerma_dose(),
                beta_vs_ke=beta_vs_ke(), bohr_levels=bohr_levels(), be_curve=be_curve(), decay_schemes=decay_schemes(),
                mlc_bank=mlc_bank(), mlc_leaf_ends=mlc_leaf_ends(), mlc_dlg=mlc_dlg(), mlc_tg=mlc_tg())
