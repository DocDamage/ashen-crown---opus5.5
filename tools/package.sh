#!/bin/bash
# Clean-source release build (AC064): export from a fresh `git archive` of HEAD, not from the working tree.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
G=${GODOT:-/home/claude/tools/godot/Godot_v4.7.2-stable_linux.x86_64}
REV=$(cd "$ROOT" && git rev-parse --short HEAD)
DIST=$ROOT/dist; REL=$ROOT/reports/evidence/release
CLEAN=/tmp/ashen_clean_$REV
rm -rf "$DIST" "$CLEAN"; mkdir -p "$DIST/AshenCrown_Windows" "$CLEAN" "$REL"
(cd "$ROOT" && git archive HEAD) | tar -x -C "$CLEAN"
# Licensed library art is not in git (no redistribution of raw files): ship it inside the exported .pck only.
if [ -d "$ROOT/game/assets/ext" ]; then cp -r "$ROOT/game/assets/ext" "$CLEAN/game/assets/ext"; echo "ext assets: $(find "$ROOT/game/assets/ext" -name '*.png' | wc -l) png" > "$REL/ext_assets.txt"; fi
cd "$CLEAN/game"
"$G" --headless --path . --import > "$REL/clean_import.txt" 2>&1 || true
"$G" --headless --path . --import > "$REL/clean_import_second_pass.txt" 2>&1
"$G" --headless --path . --export-release "Windows Desktop" "$DIST/AshenCrown_Windows/AshenCrown.exe" > "$REL/clean_export.txt" 2>&1
echo "revision $REV exported from clean archive $CLEAN" >> "$REL/clean_export.txt"
cp -r "$ROOT/game/licenses" "$DIST/AshenCrown_Windows/"
cp "$ROOT/README.md" "$DIST/AshenCrown_Windows/README.md"
(cd "$DIST/AshenCrown_Windows" && sha256sum AshenCrown.exe > SHA256SUMS.txt)
(cd "$ROOT" && git archive --format=tar.gz --prefix=AshenCrown_source/ -o "$DIST/AshenCrown_source_$REV.tar.gz" HEAD)
ls -la "$DIST" "$DIST/AshenCrown_Windows"
