#!/bin/bash
# Final evidence chain: b1 from New Game, then each segment resumes the milestone the previous segment wrote.
# usage: run_chain.sh <outdir>
OUT=${1:-/tmp/qa_final}
G=${GODOT:-/home/claude/tools/godot/Godot_v4.7.2-stable_linux.x86_64}
cd "$(dirname "$0")/../game"
mkdir -p "$OUT"
run() {
  local r=$1; local wd=${2:-3000}
  echo "=== $r $(date -u +%FT%TZ)" >> "$OUT/chain.txt"
  timeout $((wd + 120)) xvfb-run -a -s "-screen 0 1280x1024x24" "$G" --path . -- --qa-route "$r" --qa-capture --qa-out "$OUT" --qa-speed 4 --qa-watchdog "$wd" > "$OUT/$r.txt" 2>&1
  grep -a "ROUTE PASS\|ROUTE FAIL" "$OUT/$r.txt" | tail -1 >> "$OUT/chain.txt"
  grep -aq "ROUTE PASS" "$OUT/$r.txt"
}
run b1 1200 && run seg2 && run seg3 && run seg4 && run seg5 && run seg6 && run seg7 || { echo "CHAIN STOPPED" >> "$OUT/chain.txt"; exit 1; }
# the final dungeon and the optional-quest window both start from ch20_done; run them side by side
run seg8 6000 & P1=$!
run segq 7000 & P2=$!
wait $P1; A=$?; wait $P2; B=$?
echo "seg8=$A segq=$B" >> "$OUT/chain.txt"
[ $A -eq 0 ] && [ $B -eq 0 ] && echo "CHAIN PASS" >> "$OUT/chain.txt" || echo "CHAIN PARTIAL" >> "$OUT/chain.txt"
