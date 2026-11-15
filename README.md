# Out-of-Order Superscalar Processor: Design-Space Exploration

Computer Architecture (BCS-5F) project using SimpleScalar sim-outorder.
Group 13. Benchmarks: anagram, go.

## Layout
- lib.sh: run() helper used by every experiment
- partN.sh: batch scripts for each project part
- extract.py: pulls stats from results/ into all_results.csv
- results/: raw sim-outorder outputs (unedited)

## Reproduce
1. Clone and build https://github.com/toddmaustin/simplesim-3.0 (PISA target).
2. Clone the SPEC95 binaries from https://github.com/priyankarroychowdhury3/Simplescalar.
3. Edit SIM and ROOT in lib.sh, then run: bash partN.sh
