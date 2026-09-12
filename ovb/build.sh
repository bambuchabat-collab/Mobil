#!/usr/bin/env bash
# Generovanie PDF z HTML predlôh (Chromium headless).
set -euo pipefail
CHROME="${CHROME:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}"
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR/out"
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$DIR/out/OVB-prezentacia.pdf" "$DIR/prezentacia.html"
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$DIR/out/OVB-schema-A4.pdf" "$DIR/schema-a4.html"
echo "Hotovo: out/OVB-prezentacia.pdf (10 slajdov 16:9), out/OVB-schema-A4.pdf (A4)"
