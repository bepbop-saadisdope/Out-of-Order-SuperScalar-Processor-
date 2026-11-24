#!/bin/bash
# Part 3 - RUU (instruction window) size 4..128, LSQ = half of RUU, width stays 4 (12 runs)
source "$(dirname "$0")/lib.sh"
for b in $BENCHES; do
  for R in 4 8 16 32 64 128; do
    submit $b P3.ruu$R -ruu:size $R -lsq:size $((R/2))
  done
done
wait
