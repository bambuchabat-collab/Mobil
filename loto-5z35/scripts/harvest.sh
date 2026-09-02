#!/bin/bash
# Fetch one draw date from the official TIPOS endpoint
fetch() {
  local D="$1"
  local OUT="draws/$D.json"
  [ -s "$OUT" ] && return 0
  curl -sS -L --max-time 25 -X POST \
    -H "X-Requested-With: XMLHttpRequest" \
    -H "Referer: https://www.tipos.sk/loterie/loto-5-z-35" \
    --data-urlencode "datumZrebovania=$D" \
    "https://www.tipos.sk/Millennium.CiselneLoterie/Loto5z35/GetForDate" -o "$OUT" 2>/dev/null
  # drop "null" responses (non-draw days)
  if [ "$(head -c 6 "$OUT")" = '"null"' ]; then rm -f "$OUT"; fi
}
export -f fetch
