"""MU module data: the tables are physically sensible and agree with each other, for all four energies."""
import sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics")); sys.path[:0] = [str(d) for d in (ROOT / "chapters").iterdir() if d.is_dir()]
import mudata as M, beamdata as bd
bad = []; n = 0
def check(c, m):
    global n; n += 1
    if not c: bad.append(m); print("FAIL", m)
def lin(x, xs, ys): return bd.interp(x, xs, ys)
ALL = M.all_tables()
check(set(ALL) == {6, 10, 15, 18}, "tables exist for 6, 10, 15, and 18 MV")
for E, T in ALL.items():
    P = M.ENERGY[E]; S = T["sizes"]; D = T["depths"]; col = lambda s: S.index(s)
    pdd = lambda d, s: T["pdd"][D.index(d)][col(s)]; tmr = lambda d, s: T["tmr"][T["tmr_depths"].index(d)][col(s)]
    # ---- shape
    check(len(T["pdd"]) == len(D) and all(len(r) == len(S) for r in T["pdd"]), f"{E} MV: the PDD table is {len(D)} depths by {len(S)} field sizes")
    check(T["tmr_depths"][0] == T["dmax"] and all(tmr(T["dmax"], s) == 1.0 for s in S), f"{E} MV: the TMR table starts at d_max with every entry 1.000")
    check(all(pdd(T["dmax"], s) == 100.0 for s in S), f"{E} MV: the PDD is 100.0% at d_max for every field size")
    check(D == sorted(D) and len(set(D)) == len(D) and T["dmax"] in D, f"{E} MV: the depths are in order, with no repeats, and include d_max (the old data had 1.5 before 1)")
    # ---- trends
    after = [d for d in D if d >= T["dmax"]]
    check(all(pdd(a, s) > pdd(b, s) for s in S for a, b in zip(after, after[1:])), f"{E} MV: the PDD falls with depth beyond d_max for every field size")
    check(all(tmr(a, s) > tmr(b, s) for s in S for a, b in zip(T["tmr_depths"], T["tmr_depths"][1:])), f"{E} MV: the TMR falls with depth for every field size")
    check(all(pdd(d, a) <= pdd(d, b) for d in after[1:] for a, b in zip(S, S[1:])) and all(pdd(d, a) < pdd(d, b) for d in after if d >= 10 for a, b in zip(S, S[1:])), f"{E} MV: the PDD never falls with field size beyond d_max, and rises strictly from 10 cm on")
    check(all(tmr(d, a) <= tmr(d, b) for d in T["tmr_depths"][1:] for a, b in zip(S, S[1:])) and all(tmr(d, a) < tmr(d, b) for d in T["tmr_depths"] if d >= 10 for a, b in zip(S, S[1:])), f"{E} MV: the TMR never falls with field size beyond d_max, and rises strictly from 10 cm on")
    build = [d for d in D if d < T["dmax"]]
    check(all(pdd(a, 10) < pdd(b, 10) for a, b in zip(build, build[1:] + [T["dmax"]])), f"{E} MV: the dose builds up from the surface to d_max")
    check(all(pdd(0, a) < pdd(0, b) for a, b in zip(S, S[1:])) and 1.6 <= pdd(0, 40) / pdd(0, 10) <= 2.3, f"{E} MV: the surface dose rises with field size, about double from 10 × 10 to 40 × 40 cm ({pdd(0, 40) / pdd(0, 10):.2f}×)")
    check(10 <= pdd(0, 10) <= 30, f"{E} MV: the surface dose of the 10 × 10 cm field is {pdd(0, 10)}%, within the usual 10% to 30%")
    # ---- anchors for a 10 x 10 cm field
    check(abs(pdd(10, 10) - P["pdd10"]) <= 0.15, f"{E} MV: PDD(10 cm) = {pdd(10, 10)}%, target {P['pdd10']}%")
    tpr = tmr(20, 10) / tmr(10, 10); check(abs(tpr - P["tpr"]) <= 0.004, f"{E} MV: TPR20,10 = {tpr:.3f}, target {P['tpr']}")
    check({6: 1.5, 10: 2.5, 15: 3.0, 18: 3.5}[E] == T["dmax"], f"{E} MV: d_max = {T['dmax']} cm")
    # ---- scatter, wedge, tray
    check(T["sc"][col(10)] == 1.0 and T["sp"][col(10)] == 1.0, f"{E} MV: Sc and Sp are 1.000 for the 10 × 10 cm reference field")
    check(all(a < b for a, b in zip(T["sc"], T["sc"][1:])) and all(a < b for a, b in zip(T["sp"], T["sp"][1:])), f"{E} MV: Sc and Sp rise with field size")
    scp40 = T["sc"][-1] * T["sp"][-1]; check(1.05 <= scp40 <= 1.14, f"{E} MV: Scp(40 × 40) = {scp40:.3f}")
    wf = T["wf"]; check(all(wf[a][3] > wf[b][3] for a, b in zip(T["wf_angles"], T["wf_angles"][1:])), f"{E} MV: the wedge factor falls with wedge angle")
    check(all(a < b for a in T["wf_angles"] for a, b in zip(wf[a], wf[a][1:])) and all(0.5 < v < 0.99 for r in wf.values() for v in r), f"{E} MV: wedge factors rise slightly with field size and stay between 0.5 and 0.99")
    check(0.96 <= T["tf"] <= 0.99, f"{E} MV: the tray factor is {T['tf']}")
    # ---- the PDD and TMR tables agree: TMR(d, s_d) = PDD/100 x [(100 + d)/(100 + d_max)]^2 x Sp(A_dmax)/Sp(A_d), read from the printed tables
    worst = 0.0; sp = lambda s: lin(s, S, T["sp"]); trow = lambda d, s: lin(s, S, T["tmr"][T["tmr_depths"].index(d)])
    for s in (6, 10, 15, 20):
        for d in (5, 10, 15, 20):
            sd, sm = s * (100 + d) / 100, s * (100 + T["dmax"]) / 100
            est = pdd(d, s) / 100 * ((100 + d) / (100 + T["dmax"])) ** 2 * sp(sm) / sp(sd); worst = max(worst, abs(est - trow(d, sd)) / trow(d, sd))
    check(worst < 0.008, f"{E} MV: the TMR table follows from the PDD table by the chapter's conversion, to within {100 * worst:.2f}%")
# ---- the module's 6 MV tables are the same beam as the rest of the site
T6 = ALL[6]; same = all(abs(T6["pdd"][T6["depths"].index(d)][T6["sizes"].index(s)] - round(bd.pdd_model(d, s), 1)) < 1e-9 for d in (1.5, 2, 5, 10, 15, 20, 30) for s in (4, 10, 40))
check(same and T6["sc"] == [bd.SC[s] for s in T6["sizes"]] and T6["sp"] == [bd.SP[s] for s in T6["sizes"]], "the 6 MV tables of the module equal the shared beam model used in the chapters")
# ---- physical order between energies
check(all(ALL[a]["pdd10"] < ALL[b]["pdd10"] and ALL[a]["tpr"] < ALL[b]["tpr"] for a, b in ((6, 10), (10, 15), (15, 18))), "a higher energy penetrates more: PDD(10 cm) and TPR20,10 rise with energy")
check(all(ALL[a]["tf"] <= ALL[b]["tf"] for a, b in ((6, 10), (10, 15), (15, 18))) and all(ALL[a]["wf"][45][3] < ALL[b]["wf"][45][3] for a, b in ((6, 10), (10, 15), (15, 18))), "wedge and tray factors rise toward 1 with energy")
print(f"mudata: {n} checks"); print("mudata: PASS" if not bad else f"mudata: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
