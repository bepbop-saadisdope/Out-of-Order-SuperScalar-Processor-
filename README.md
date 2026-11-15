# Design-Space Exploration of an Out-of-Order Superscalar Processor

CS Computer Architecture BCS-5F project (FAST-NUCES Lahore), Group 13.
Simulator: SimpleScalar 3.0 sim-outorder (PISA). Benchmarks: anagram, go.

## Layout
- lib.sh: run <bench> <tag> [options] helper. Saves stats to results/<bench>_<tag>.txt
- partN.sh: batch script for each project part
- extract.py: collects all stats into all_results.csv
- results/: raw -redir:sim outputs, unedited

## Setup notes
- Build: make config-pisa; make sim-outorder CC="gcc -fcommon" OFLAGS="-O2"
- Modern glibc has no termio.h. Patch first:
  sed -i "s|#include <termio.h>|#include <termios.h>|" syscall.c target-pisa/syscall.c
- Scripts are bash. Run them with: bash partN.sh
- Paths assume ~/project is a symlink to this folder.
