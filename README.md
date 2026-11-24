# Out-of-Order Superscalar Processor: Design-Space Exploration

Group 13, Computer Architecture (BCS-5F). Design-space exploration of an out-of-order superscalar
processor with SimpleScalar 3.0 `sim-outorder`.

Benchmarks: **anagram** and **go** (group 13: (13-1) mod 6 = 0). Every run is capped at
100 M instructions (`-max:inst 100000000`), except Part 1, which runs to completion.

## Parts

| Part | Study |
|------|-------|
| 1 | Baseline and verification: default configuration, program output checked against `Expected_Output` |
| 2 | Machine width W = 1, 2, 4, 8; out-of-order vs in-order issue |
| 3 | RUU size 4 to 128 (plus W=8 with RUU=16 vs W=4 with RUU=64) |
| 4 | Memory hierarchy: L1-D capacity, L1-D block size, memory latency with/without L2 |
| 5 | Branch prediction: perfect, not-taken, bimodal 512/2048, 2-level, combined |
| 6 | Best design within a cost budget of 100 units, found with a genetic algorithm (seed 13) |

## Part 6 result

| Design | Cost | anagram IPC | go IPC | Geomean IPC |
|--------|------|-------------|--------|-------------|
| default | 86 | 2.0372 | 0.9070 | 1.3593 |
| **final** `W8_R32_I16K64B4w_D4K16B8w_L2256K_comb` | 98 | 2.8639 | 1.3491 | **1.9656** |

Name format: W = machine width, R = RUU entries, I/D = L1 instruction/data cache
(size, block size, associativity), L2 = unified L2 size, then the branch predictor.
All candidates: `data/part6_candidates.csv`.

## Repository layout

```
bench/          benchmark programs, inputs and Expected_Output
simplesim-3.0/  vendored SimpleScalar 3.0 source (built by build.sh)
build.sh        builds simplesim-3.0/sim-outorder
reproduce.sh    runs the whole pipeline end to end
scripts/        run_part*.sh batch runs, lib.sh (shared settings), part6_search.py (genetic algorithm),
                extract_stats.py, make_graphs.py, build_report.py
configs/        the .cfg file of every run (made with -dumpconfig)
results/        raw simulator outputs (-redir:sim), unedited
progout/        program outputs of the Part 1 runs
data/           all_stats.csv and the Part 6 search data
graphs/         all figures used in the report
report/         Project_Report_G13.docx and Report.pdf
commands.log    every simulator command that was run
```

## Reproducing the results

Requirements: Linux, gcc and make (to build the simulator), Python 3 with
`matplotlib numpy pandas python-docx`.

```bash
git clone https://github.com/bepbop-saadisdope/Out-of-Order-SuperScalar-Processor-.git
cd Out-of-Order-SuperScalar-Processor-
./reproduce.sh              # JOBS=4 ./reproduce.sh to limit parallel simulations
git diff --stat data/all_stats.csv   # empty = numbers match the committed ones
```

`reproduce.sh` runs, in order:

1. `./build.sh` (only if `sim-outorder` is missing)
2. `scripts/run_all_1to5.sh` (Parts 1 to 5)
3. `scripts/part6_search.py search`, then `scripts/make_part6.py` and `scripts/run_part6.sh` (Part 6)
4. `scripts/extract_stats.py`, `make_part6_csv.py`, `make_graphs.py`, `build_report.py`
   (CSV, graphs and `report/Project_Report_G13.docx`)

Notes:
- Raw `results/*.txt` contain wall-clock lines (elapsed time, simulation rate) that change on every run.
  Compare `data/all_stats.csv` instead; it holds only deterministic statistics.
- The Part 6 search is seeded and reuses `data/part6_search_cache.json`. Delete that file to rerun it from scratch.
- Run a single part with `bash scripts/run_part4.sh` etc. Override paths with `SIM=... BENCH=...` if needed.
