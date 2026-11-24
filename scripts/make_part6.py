#!/usr/bin/env python3
"""make_part6.py - turn the genetic-algorithm result into the Part 6 candidate list.
Candidates = the default design, every design that was the best of its generation so far (the search path),
the runner-up designs of the full 100M-instruction runs, and the FINAL design (best geometric mean at 100M).
Writes data/part6_designs.json and scripts/run_part6.sh (full 100M-instruction runs of each candidate)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import part6_search as P
ROOT = P.ROOT
S = json.load(open(os.path.join(ROOT, "data", "part6_search_summary.json")))
t = lambda d: (d[0], d[1], tuple(d[2]), tuple(d[3]), tuple(d[4]) if d[4] else None, d[5])
path = [t(p) for p in S["path"]]
fin = [t(d) for d in S["finalists"][0]]
full = lambda d: S["full"][P.name_of(d)][2]
final = max(fin, key=full)
cands = [("default", path[0])]
for i, d in enumerate(path[1:], 1):
    if d != final:
        cands.append((f"g{i}_best", d))
runners = [d for d in sorted(fin, key=lambda d: -full(d)) if d != final and d not in [c[1] for c in cands]][:2]
for i, d in enumerate(runners, 1):
    cands.append((f"alt{i}", d))
cands.append(("final", final))
out = [{"label": l, "design": list(d), "name": P.name_of(d), "cost": P.cost(d)} for l, d in cands]
json.dump(out, open(os.path.join(ROOT, "data", "part6_designs.json"), "w"), indent=1, default=list)
with open(os.path.join(ROOT, "scripts", "run_part6.sh"), "w") as f:
    f.write('#!/bin/bash\n# Part 6 - candidate designs (found with scripts/part6_search.py, a genetic algorithm), full 100M-instruction runs\n'
            'source "$(dirname "$0")/lib.sh"\n')
    for c in out:
        d = t(tuple(c["design"]))
        f.write(f'# {c["label"]}: {c["name"]}  cost {c["cost"]}\nfor b in $BENCHES; do\n  submit $b P6.{c["label"]} ' + " ".join(P.options(d)) + "\ndone\n")
    f.write("wait\n")
for c in out: print(c["label"], c["cost"], c["name"])
