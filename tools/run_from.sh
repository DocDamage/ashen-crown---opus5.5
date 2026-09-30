#!/bin/bash
# Resume the evidence chain from a given segment: run_from.sh <outdir> seg3 seg4 ... (each resumes its milestone)
OUT=$1; shift
G=${GODOT:-/home/claude/tools/godot/Godot_v4.7.2-stable_linux.x86_64}
cd "$(dirname "$0")/../game"
mkdir -p "$OUT"
for r in "$@"; do
  wd=3000; [ "$r" = "seg8" ] && wd=6000; [ "$r" = "segq" ] && wd=7000
  echo "=== $r $(date -u +%FT%TZ)" >> "$OUT/chain.txt"
  timeout $((wd + 120)) xvfb-run -a -s "-screen 0 1280x1024x24" "$G" --path . -- --qa-route "$r" --qa-capture --qa-out "$OUT" --qa-speed 4 --qa-watchdog "$wd" > "$OUT/$r.txt" 2>&1
  grep -a "ROUTE PASS\|ROUTE FAIL" "$OUT/$r.txt" | tail -1 >> "$OUT/chain.txt"
  grep -aq "ROUTE PASS" "$OUT/$r.txt" || { echo "CHAIN STOPPED at $r" >> "$OUT/chain.txt"; exit 1; }
done
echo "CHAIN PASS ($*)" >> "$OUT/chain.txt"
