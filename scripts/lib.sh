#!/bin/bash
# lib.sh - shared settings and helper functions for all run_partN.sh scripts.
# Edit the two paths below (or export SIM and BENCH before running) to match your PC.

ROOT=${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}   # repo root
SIM=${SIM:-$ROOT/simplesim-3.0/sim-outorder}                     # built by ./build.sh
BENCH=${BENCH:-$ROOT/bench}                                      # needs Input/ Programs/ Expected_Output/
[ -d "$BENCH/Input" ] || { [ -d "$BENCH/BenchMarks_Little/Input" ] && BENCH=$BENCH/BenchMarks_Little; }
[ -x "$SIM" ] || { echo "sim-outorder not found at $SIM - run ./build.sh first" >&2; exit 1; }
[ -d "$BENCH/Input" ] || { echo "benchmarks not found at $BENCH (need Input/ Programs/ Expected_Output/)" >&2; exit 1; }
RES=$ROOT/results      # raw -redir:sim outputs (unedited)
CFG=$ROOT/configs      # one .cfg per run (made with -dumpconfig)
PROG=$ROOT/progout     # program outputs (only kept for Part 1)
JOBS=${JOBS:-2}        # how many simulations to run at the same time
MAXI=${MAXI-100000000} # -max:inst cap. Part 1 sets MAXI="" so the programs run to completion.
BENCHES=${BENCHES:-"anagram go"}   # group 13 = (13-1) mod 6 = 0 -> anagram + go

mkdir -p "$RES" "$CFG" "$PROG"

# run_one <bench> <name> [simulator options...]
#   Result file: results/<bench>.<name>.txt     Config file: configs/<bench>.<name>.cfg
run_one() {
  local b=$1 name=$2; shift 2
  local tag="$b.$name"
  local cap=(); [ -n "$MAXI" ] && cap=(-max:inst "$MAXI")
  local tmp; tmp=$(mktemp -d)                       # private copy of Input/ so parallel runs never clash
  cp "$BENCH"/Input/{words,anagram.in,1stmt.i,2stone9.in,compress95.in} "$tmp"/
  local prog args stdin
  case $b in
    anagram)    prog="$BENCH/Programs/anagram.ss";    args=(words);                 stdin=anagram.in ;;
    cc1)        prog="$BENCH/Programs/cc1.ss";        args=(-O 1stmt.i);            stdin=/dev/null ;;
    go)         prog="$BENCH/Programs/go.ss";         args=(50 9 2stone9.in);       stdin=/dev/null ;;
    compress95) prog="$BENCH/Programs/compress95.ss"; args=();                      stdin=compress95.in ;;
  esac
  ( cd "$tmp"
    # 1) configuration file for this run (the simulator writes it and stops)
    env -i "$SIM" "${cap[@]}" "$@" -dumpconfig "$CFG/$tag.cfg" "$prog" "${args[@]}" < "$stdin" > /dev/null 2>&1
    # 2) the real run
    echo "env -i $SIM ${cap[*]} $* -redir:sim $RES/$tag.txt $prog ${args[*]}" >> "$ROOT/commands.log"
    env -i "$SIM" "${cap[@]}" "$@" -redir:sim "$RES/$tag.txt" "$prog" "${args[@]}" < "$stdin" > "$tmp/prog.out" 2> "$tmp/prog.err"
    # keep the program's own output only when asked (Part 1 verification)
    if [ -n "$SAVE_PROG" ]; then
      case $b in
        *)   cp "$tmp/prog.out" "$PROG/$tag.out" ;;
      esac
    fi
  )
  rm -rf "$tmp"
}

# submit <bench> <name> [options...]  - run_one in the background, at most $JOBS at a time
submit() {
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  run_one "$@" &
}
