#!/bin/bash
# Part 6 - candidate designs (found with scripts/part6_search.py, a genetic algorithm), full 100M-instruction runs
source "$(dirname "$0")/lib.sh"
# default: W4_R16_I16K32B1w_D16K32B4w_L2256K_bimod2048  cost 86.0
for b in $BENCHES; do
  submit $b P6.default -fetch:ifqsize 4 -decode:width 4 -issue:width 4 -commit:width 4 -res:ialu 4 -res:memport 2 -ruu:size 16 -lsq:size 8 -cache:il1 il1:512:32:1:l -cache:dl1 dl1:128:32:4:l -cache:dl2 ul2:1024:64:4:l -bpred bimod -bpred:bimod 2048
done
# g1_best: W8_R32_I8K64B1w_D4K32B8w_L2256K_bimod2048  cost 86.0
for b in $BENCHES; do
  submit $b P6.g1_best -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 32 -lsq:size 16 -cache:il1 il1:128:64:1:l -cache:dl1 dl1:16:32:8:l -cache:dl2 ul2:1024:64:4:l -bpred bimod -bpred:bimod 2048
done
# g2_best: W8_R32_I16K64B4w_D4K32B8w_L2128K_bimod1024  cost 77.0
for b in $BENCHES; do
  submit $b P6.g2_best -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 32 -lsq:size 16 -cache:il1 il1:64:64:4:l -cache:dl1 dl1:16:32:8:l -cache:dl2 ul2:512:64:4:l -bpred bimod -bpred:bimod 1024
done
# g3_best: W8_R32_I16K64B4w_D8K16B4w_L2256K_bimod2048  cost 98.0
for b in $BENCHES; do
  submit $b P6.g3_best -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 32 -lsq:size 16 -cache:il1 il1:64:64:4:l -cache:dl1 dl1:128:16:4:l -cache:dl2 ul2:1024:64:4:l -bpred bimod -bpred:bimod 2048
done
# alt1: W8_R32_I16K64B2w_D4K16B8w_L2256K_comb  cost 98.0
for b in $BENCHES; do
  submit $b P6.alt1 -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 32 -lsq:size 16 -cache:il1 il1:128:64:2:l -cache:dl1 dl1:32:16:8:l -cache:dl2 ul2:1024:64:4:l -bpred comb -bpred:comb 1024
done
# alt2: W8_R32_I16K64B4w_D8K16B4w_L2256K_bimod1024  cost 97.0
for b in $BENCHES; do
  submit $b P6.alt2 -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 32 -lsq:size 16 -cache:il1 il1:64:64:4:l -cache:dl1 dl1:128:16:4:l -cache:dl2 ul2:1024:64:4:l -bpred bimod -bpred:bimod 1024
done
# final: W8_R32_I16K64B4w_D4K16B8w_L2256K_comb  cost 98.0
for b in $BENCHES; do
  submit $b P6.final -fetch:ifqsize 8 -decode:width 8 -issue:width 8 -commit:width 8 -res:ialu 8 -res:memport 4 -ruu:size 32 -lsq:size 16 -cache:il1 il1:64:64:4:l -cache:dl1 dl1:32:16:8:l -cache:dl2 ul2:1024:64:4:l -bpred comb -bpred:comb 1024
done
wait
