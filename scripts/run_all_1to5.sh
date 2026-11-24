#!/bin/bash
# runs Parts 1-5 in order (Part 6 is run separately)
D="$(dirname "$0")"
for p in 1 2 3 3_extra 4 5; do
  f="$D/run_part$p.sh"; [ "$p" = 3_extra ] && f="$D/run_part3_extra.sh"
  echo "== part $p start $(date +%T)"; bash "$f"; echo "== part $p done $(date +%T)"
done
