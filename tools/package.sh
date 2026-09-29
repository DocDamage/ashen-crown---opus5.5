#!/bin/bash
# Build the delivery set: Windows build (exe + notices + README), source archive, evidence archive.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
G=${GODOT:-/home/claude/tools/godot/Godot_v4.7.2-stable_linux.x86_64}
DIST=$ROOT/dist
rm -rf "$DIST"; mkdir -p "$DIST/AshenCrown_Windows"
cd "$ROOT/game"
"$G" --headless --path . --import >/dev/null 2>&1
"$G" --headless --path . --export-release "Windows Desktop" "$DIST/AshenCrown_Windows/AshenCrown.exe" > "$ROOT/reports/evidence/release/export.txt" 2>&1
cp -r "$ROOT/game/licenses" "$DIST/AshenCrown_Windows/"
cp "$ROOT/README.md" "$DIST/AshenCrown_Windows/README.md"
cd "$DIST" && sha256sum AshenCrown_Windows/AshenCrown.exe > AshenCrown_Windows/SHA256SUMS.txt
cd "$ROOT" && git archive --format=tar.gz -o "$DIST/AshenCrown_source.tar.gz" HEAD
tar -czf "$DIST/AshenCrown_evidence.tar.gz" -C "$ROOT" reports
ls -la "$DIST" "$DIST/AshenCrown_Windows"
