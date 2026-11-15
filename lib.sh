REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIM="$REPO/simplesim-3.0/sim-outorder"
ROOT="$REPO/bench"
OUT="$REPO/results"
mkdir -p "$OUT"
run() {
  local b=$1 tag=$2; shift 2
  local stats="$OUT/${b}_${tag}.txt"
  [ -s "$stats" ] && { echo "skip $b $tag"; return; }
  echo "running $b $tag"
  cd "$ROOT/Input" || exit 1
  case $b in
    anagram) env -i $SIM "$@" -redir:sim "$stats" ../Programs/anagram.ss words < anagram.in > "$OUT/${b}_${tag}.out" ;;
    go) env -i $SIM "$@" -redir:sim "$stats" ../Programs/go.ss 50 9 2stone9.in > "$OUT/${b}_${tag}.out" ;;
  esac
}
