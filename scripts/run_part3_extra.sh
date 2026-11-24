#!/bin/bash
# Part 3(c) extra runs: the designer question "W = 8 with a 16-entry RUU, or W = 4 with a 64-entry RUU?"
# W = 4 with RUU = 64 already exists (Part 2: P2.w4.ooo uses ruu 64, lsq 32, memport 2), so only W = 8 with RUU = 16 is new.
source "$(dirname "$0")/lib.sh"
for b in $BENCHES; do
  submit $b P3x.w8_ruu16 -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 16 -lsq:size 8
done
wait
