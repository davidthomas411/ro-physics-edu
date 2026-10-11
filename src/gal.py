"""The simulated CT artifact images on a real anatomical slice, built by tools/make_ct_artifacts.py (anatomy: OpenKBP patient pt_14, Babier et al., Med Phys 2021)."""
import json, os
GAL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gal_ct.json")))
ITEMS = {i["id"]: i for i in GAL["items"]}
ST = GAL["stats"]
PICKS = GAL["picks"]
FOV = GAL["fov_mm"]
DRR = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gal_drr.json")))
DRR_ST = DRR["stats"]
