#!/usr/bin/env python3
"""make_part6_csv.py - after run_part6.sh and extract_stats.py: write data/part6_candidates.csv
(name, cost, anagram_ipc, go_ipc, geomean_ipc, final) from the candidate list and data/all_stats.csv."""
import csv, json, math, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
des = json.load(open(os.path.join(ROOT, "data", "part6_designs.json")))
ipc = {}
for r in csv.DictReader(open(os.path.join(ROOT, "data", "all_stats.csv"))):
    if r["part"] == "P6":
        ipc[(r["bench"], r["label"])] = float(r["sim_IPC"])
with open(os.path.join(ROOT, "data", "part6_candidates.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["name", "design", "cost", "anagram_ipc", "go_ipc", "geomean_ipc", "final"])
    for c in des:
        a, b = ipc[("anagram", c["label"])], ipc[("go", c["label"])]
        w.writerow([c["label"], c["name"], c["cost"], f"{a:.4f}", f"{b:.4f}", f"{math.sqrt(a*b):.4f}", 1 if c["label"] == "final" else 0])
print(open(os.path.join(ROOT, "data", "part6_candidates.csv")).read())
