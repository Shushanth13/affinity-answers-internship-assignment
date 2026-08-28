#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <CSV_URL>" >&2
  exit 1
fi

URL="$1"
TMP_CSV="$(mktemp)"
trap 'rm -f "$TMP_CSV"' EXIT

echo "Fetching $URL ..." >&2
if ! curl -fsSL "$URL" -o "$TMP_CSV"; then
  echo "Error: failed to download CSV from $URL" >&2
  exit 1
fi

python3 - "$TMP_CSV" << 'PYEOF'
import csv
import re
import sys

path = sys.argv[1]

rows = []
with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("Security", "").strip()
        location = row.get("Headquarters Location", "").strip()
        founded_raw = row.get("Founded", "").strip()

        m = re.search(r"\d{4}", founded_raw)
        if not name or not location or not m:
            continue

        founded_year = int(m.group())
        rows.append((name, location, founded_year))

rows.sort(key=lambda r: r[2])

writer = csv.writer(sys.stdout)
writer.writerow(["Company", "Location", "Founded"])
for name, location, year in rows:
    writer.writerow([name, location, year])
PYEOF