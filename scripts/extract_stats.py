#!/usr/bin/env python3
"""extract_stats.py - read every raw sim-outorder output in results/ and write data/all_stats.csv

One row per run. File names look like  <bench>.<part>.<label>.txt  (for example anagram.P3.ruu32.txt).
Usage:  python3 scripts/extract_stats.py
"""
import csv, glob, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "data", "all_stats.csv")

WANTED = [
    "sim_num_insn", "sim_cycle", "sim_IPC", "sim_CPI",
    "sim_num_loads", "sim_num_stores", "sim_num_branches",
    "ruu_occupancy", "ruu_full", "lsq_occupancy", "lsq_full",
    "il1.accesses", "il1.misses", "il1.miss_rate",
    "dl1.accesses", "dl1.misses", "dl1.miss_rate",
    "ul2.accesses", "ul2.misses", "ul2.miss_rate",
]

def parse(path):
    stats = {}
    with open(path) as f:
        for line in f:
            m = re.match(r"^(\S+)\s+(-?[0-9.]+(?:e[-+]?\d+)?)\s+#", line)
            if m:
                stats[m.group(1)] = float(m.group(2))
    return stats

def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(RES, "*.txt"))):
        parts = os.path.basename(path)[:-4].split(".")
        if len(parts) < 3:
            continue
        bench, part, label = parts[0], parts[1], ".".join(parts[2:])
        s = parse(path)
        row = {"file": os.path.basename(path), "bench": bench, "part": part, "label": label}
        for k in WANTED:
            row[k] = s.get(k, "")
        # branch predictor statistics are named after the predictor, e.g. bpred_bimod.misses
        bp = sorted({k.split(".")[0] for k in s if k.startswith("bpred_") and "." in k})
        row["bpred_name"] = bp[0][len("bpred_"):] if bp else ""
        row["bpred_dir_rate"] = s.get(bp[0] + ".bpred_dir_rate", "") if bp else ""
        row["bpred_misses"] = s.get(bp[0] + ".misses", "") if bp else ""
        n = s.get("sim_num_insn", 0)
        if n:
            row["load_pct"] = 100 * s.get("sim_num_loads", 0) / n
            row["store_pct"] = 100 * s.get("sim_num_stores", 0) / n
            row["branch_pct"] = 100 * s.get("sim_num_branches", 0) / n
            row["other_pct"] = 100 - row["load_pct"] - row["store_pct"] - row["branch_pct"]
            row["mpki"] = 1000 * s.get(bp[0] + ".misses", 0) / n if bp else ""
        rows.append(row)
    cols = ["file", "bench", "part", "label"] + WANTED + [
        "bpred_name", "bpred_dir_rate", "bpred_misses",
        "load_pct", "store_pct", "branch_pct", "other_pct", "mpki"]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: (round(r[c], 6) if isinstance(r.get(c), float) else r.get(c, "")) for c in cols})
    print(f"wrote {OUT} with {len(rows)} runs")

if __name__ == "__main__":
    sys.exit(main())
