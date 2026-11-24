#!/bin/bash
# Part 1 - Baseline and verification: default configuration, run to COMPLETION (no -max:inst)
source "$(dirname "$0")/lib.sh"
MAXI=""            # no instruction cap in Part 1
SAVE_PROG=1        # keep the program output so we can diff it with Expected_Output
for b in $BENCHES; do submit $b P1.default; done
wait
{
  echo "# Part 1(a): does the program output match Expected_Output?  (empty output after each command = identical)"
  echo '$ diff progout/anagram.P1.default.out Expected_Output/anagram.out'
  diff "$PROG/anagram.P1.default.out" "$BENCH/Expected_Output/anagram.out"
  echo '$ diff progout/go.P1.default.out Expected_Output/go.out'
  diff "$PROG/go.P1.default.out" "$BENCH/Expected_Output/go.out"
} 2>&1 | tee "$ROOT/results/part1_diff_check.log"
