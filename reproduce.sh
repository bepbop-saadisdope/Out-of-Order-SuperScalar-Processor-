#!/bin/bash
# Rebuilds everything: simulator -> Parts 1-5 -> Part 6 search + runs -> stats -> graphs -> report
set -e
cd "$(dirname "$0")"
export JOBS=${JOBS:-$(nproc)}
[ -x simplesim-3.0/sim-outorder ] || ./build.sh
: > commands.log
bash scripts/run_all_1to5.sh
python3 scripts/part6_search.py search     # GA, fixed seed 13 (reuses data/part6_search_cache.json if present)
python3 scripts/make_part6.py              # writes data/part6_designs.json + scripts/run_part6.sh
bash scripts/run_part6.sh
python3 scripts/extract_stats.py           # results/*.txt -> data/all_stats.csv
python3 scripts/make_part6_csv.py
python3 scripts/make_graphs.py
python3 scripts/build_report.py            # -> report/Project_Report_G13.docx
echo "DONE"
