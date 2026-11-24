#!/bin/bash
# Part 2 - Machine width W = 1,2,4,8; out-of-order vs in-order issue (16 runs)
source "$(dirname "$0")/lib.sh"
declare -A MEMPORT=( [1]=1 [2]=1 [4]=2 [8]=4 )
for b in $BENCHES; do
  for W in 1 2 4 8; do
    WIDTH=(-fetch:ifqsize $W -decode:width $W -issue:width $W -commit:width $W -res:ialu $W -res:memport ${MEMPORT[$W]} -ruu:size 64 -lsq:size 32)
    submit $b P2.w$W.ooo     "${WIDTH[@]}"
    submit $b P2.w$W.inorder "${WIDTH[@]}" -issue:inorder true
  done
done
wait
