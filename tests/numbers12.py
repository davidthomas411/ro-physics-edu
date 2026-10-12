"""Inverse planning, IMRT and VMAT delivery, and MLC effects: every worked number and tap target re-derived by another route."""
import sys, re, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "topics"))
from topics import TOPICS
plain = lambda s: re.sub(r"<[^>]+>", "", s).strip()
T = {t["id"]: t for t in TOPICS}; bad = []; n = 0
def close(a, b, tol=1e-6, what=""):
    global n; n += 1
    if abs(a - b) > tol * max(1.0, abs(b)): bad.append((what, a, b))
import inverse_planning as IP, imrt_delivery as ID, mlc_imrt as ML
# ---- inverse planning: the cost function by hand
close(IP.f_t, (76 - 78) ** 2 + (78 - 78) ** 2 + (80 - 78) ** 2, 1e-12, "target cost 8"); close(IP.f_o1, 0.1 * ((35 - 30) ** 2 + (45 - 30) ** 2), 1e-12, "organ cost at weight 0.1"); close(IP.f_o3, 0.3 * 250, 1e-12, "organ cost at weight 0.3")
close(IP.f_tot1, 33.0, 1e-12, "total 33"); close(IP.f_tot3, 83.0, 1e-12, "total 83"); close(IP.cost([70], 78, 1), 64, 1e-12, "a voxel at 70 Gy costs 64"); close(IP.cost([68, 70, 71, 73], 70, 2), 2 * (4 + 0 + 1 + 9), 1e-12, "typed cost 28")
close(IP.trade(0)[0], 32.0, 1e-12, "organ mean at weight 0"); close(IP.trade(1)[0], 26.0, 1e-12, "organ mean at weight 1"); close(IP.trade(1)[1], 74.0, 1e-12, "D95 at weight 1")
close(1 if IP.trade(2)[0] < IP.trade(1)[0] and IP.trade(2)[1] < IP.trade(1)[1] else 0, 1, 0, "a heavier organ weight lowers both the organ dose and the target D95")
# ---- IMRT delivery
seg = [(5.0, 40), (4.0, 30), (3.0, 20), (1.5, 10)]; fl = lambda x: sum(w for h, w in seg if abs(x) <= h)
close(ID.flu(3.5), fl(3.5), 1e-12, "fluence at 3.5 cm"); close(fl(3.5), 70, 1e-12, "it is 70 MU"); close(fl(0), 100, 1e-12, "fluence at the center"); close(fl(4.5), 40, 1e-12, "fluence at 4.5 cm")
close(ID.t_on(540, 600), 540 / 600 * 60, 1e-12, "beam-on time 54 s"); close(ID.t_on(540, 600), 54.0, 1e-12, "it is 54 s"); close(ID.t_on(450, 600), 45.0, 1e-12, "typed beam-on time"); close(ID.arc_t(360, 4), 90.0, 1e-12, "arc time"); close(ID.arc_mu(600, 90), 10 * 90, 1e-12, "the most MU in the arc is 900")
close(540 / 1400 * 60, 23.1428, 1e-4, "540 MU at 1400 MU/min takes 23 s")
# ---- MLC effects
close(ML.leak_c, 250 * 0.015, 1e-12, "conventional leakage"); close(ML.leak_c, 3.75, 1e-12, "it is 3.75 cGy"); close(ML.leak_i, 875 * 0.015, 1e-12, "IMRT leakage"); close(ML.leak_i, 13.125, 1e-12, "it is 13.125 cGy"); close(ML.leak_i / ML.leak_c, 3.5, 1e-12, "the leakage ratio equals the MU ratio")
close(ML.dlg_ratio(5, 1.5), 6.5 / 5, 1e-12, "(g + DLG)/g for 5 mm"); close(ML.dlg_err(5, 1.5, 0.5), 0.5 / 6.5, 1e-12, "DLG error for 5 mm"); close(ML.dlg_err(20, 1.5, 0.5), 0.5 / 21.5, 1e-12, "DLG error for 20 mm")
close(ML.dlg_err(5, 1.5, 0.5) / ML.dlg_err(20, 1.5, 0.5), 21.5 / 6.5, 1e-12, "a 5 mm gap is 3.3 times more sensitive than a 20 mm gap")
close(ML.sw_mu(10, 1, 2), 5.0, 1e-12, "MU through the gap at 2 cm/s"); close(ML.sw_mu(10, 1, 1.5), 10 / 1.5, 1e-12, "typed sliding-window MU"); close(ML.sw_rate(2, 1, 2.5), 5.0, 1e-12, "highest dose rate for 2 MU is 5 MU/s"); close(60 * ML.sw_rate(2, 1, 2.5), 300.0, 1e-12, "300 MU/min")
close(ML.sw_mu(ML.sw_rate(2, 1, 2.5), 1, 2.5), 2.0, 1e-12, "at that dose rate and the maximum speed the gap delivers exactly 2 MU")
for b in bad: print("FAIL", b)
print(f"numbers12: {n} numbers re-derived"); print("numbers12: PASS" if not bad else f"numbers12: {len(bad)} FAILURES"); sys.exit(1 if bad else 0)
