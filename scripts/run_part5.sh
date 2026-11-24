#!/bin/bash
# Part 5 - Branch prediction: six predictors (12 runs)
source "$(dirname "$0")/lib.sh"
for b in $BENCHES; do
  submit $b P5.perfect   -bpred perfect
  submit $b P5.nottaken  -bpred nottaken
  submit $b P5.bimod512  -bpred bimod -bpred:bimod 512
  submit $b P5.bimod2048 -bpred bimod -bpred:bimod 2048
  submit $b P5.2lev      -bpred 2lev  -bpred:2lev 1 1024 8 0
  submit $b P5.comb      -bpred comb  -bpred:comb 1024
done
wait
