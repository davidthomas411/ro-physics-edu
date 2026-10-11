"""Real clinical images from open-licence TCIA collections (CC BY 3.0 and 4.0), built by tools/make_real_*.py from DICOM that the NCI Imaging Data Commons republishes.
Each figure is made of views, and each view of one to four panels (see realFig in app.js). SOURCES is the attribution list shown on the Reference page; STATS holds the measured values the chapter text quotes."""
import json, os
_d = os.path.dirname(os.path.abspath(__file__))
FIGS, STATS, _src = {}, {}, {}
for _n in ("ct", "pet", "mr", "nm", "dx"):
    _p = os.path.join(_d, f"real_{_n}.json")
    if not os.path.exists(_p): continue
    _j = json.load(open(_p)); FIGS.update(_j["figs"]); STATS[_n] = _j["stats"]
    for _s in _j["sources"]:
        _m = _src.setdefault(_s["id"], dict(collection=_s["collection"], id=_s["id"], doi=_s["doi"], license=_s["license"], citation=_s["citation"], figs=[]))
        _m["figs"] += [f for f in _s["figs"] if f not in _m["figs"]]
HDR = [h for _n in STATS for h in STATS[_n].get("hdr", [])]                                          # matrix, pixel size, and bit depth read from the DICOM headers of the images above
SOURCES = sorted(_src.values(), key=lambda s: s["collection"].lower())
REAL = dict(figs=FIGS, sources=SOURCES)
