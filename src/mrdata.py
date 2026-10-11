"""Real-anatomy MR examples from the ICBM152 average brain (shipped with nilearn); built by tools/make_mr.py. The contrast weighting and the artifacts are simulated."""
import json, os
_d = os.path.dirname(os.path.abspath(__file__))
MR = json.load(open(os.path.join(_d, "mr_case.json")))
GAL_MR = json.load(open(os.path.join(_d, "gal_mr.json")))
TISSUE = MR["tissue"]; MST = GAL_MR["stats"]
