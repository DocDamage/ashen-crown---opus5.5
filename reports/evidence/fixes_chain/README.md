# Normal-input chain, 2026-10-01 (commits 143d902..0ddce3d)

Run in the cloud with `QA_FLAT=1 tools/run_from.sh <out> ...` (Xvfb, software rendering, HD-2D and the Mode-7
world view off). Result: **b1 through seg8 and segq all PASS** — the game plays to the ending, post-clear, and
all twelve optional quests (q_all).

- b1-seg5 ran on 143d902 + the flat world view. seg6 was restarted with the cached-path walker (the per-step
  BFS made it crawl); seg8 first failed walking from Hearthward to Veyr (water after the fault) and passed once
  the route flies there. segq resumed from that run's post-clear chain milestone ch20_done.
- Unit tests on the PC: 167/167 (content 2bf01df477999197). Windows build SHA-256 in Windows\SHA256SUMS.txt.
