source "$(dirname "$0")/lib.sh"
run anagram P1_default &
run go P1_default &
wait
