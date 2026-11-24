#!/bin/bash
# Part 4 - Memory hierarchy (32 runs): (a) L1-D capacity, (b) L1-D block size, (c) memory latency with/without L2
source "$(dirname "$0")/lib.sh"
for b in $BENCHES; do
  # (a) capacity, 4-way, 32 B blocks, LRU
  submit $b P4a.dl1_1KB  -cache:dl1 dl1:8:32:4:l
  submit $b P4a.dl1_4KB  -cache:dl1 dl1:32:32:4:l
  submit $b P4a.dl1_16KB -cache:dl1 dl1:128:32:4:l
  submit $b P4a.dl1_64KB -cache:dl1 dl1:512:32:4:l
  # (b) block size, 16 KB, 4-way, LRU
  submit $b P4b.blk8   -cache:dl1 dl1:512:8:4:l
  submit $b P4b.blk16  -cache:dl1 dl1:256:16:4:l
  submit $b P4b.blk32  -cache:dl1 dl1:128:32:4:l
  submit $b P4b.blk64  -cache:dl1 dl1:64:64:4:l
  # (c) main-memory latency, with the default L2 and without any L2
  for L in 25 50 100 200; do
    submit $b P4c.mem${L}_L2    -mem:lat $L 2
    submit $b P4c.mem${L}_noL2  -mem:lat $L 2 -cache:dl2 none -cache:il2 none
  done
done
wait
