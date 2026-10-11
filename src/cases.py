"""The real clinical plan used in the case figures: CT, structure contours, delivered dose, and DVHs from one head-and-neck IMRT patient of the OpenKBP dataset.
Built by tools/make_case.py. Babier A, et al. OpenKBP: the open-access knowledge-based planning grand challenge and dataset. Med Phys 2021;48:5549-5561."""
import json, os
CASE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "case_hn1.json")))
S = {s["name"]: s for s in CASE["structures"]}
ST = {s["name"]: s["stats"] for s in CASE["structures"]}
