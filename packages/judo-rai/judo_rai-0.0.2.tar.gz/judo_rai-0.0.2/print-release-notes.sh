#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>" >&2
  echo "Example: $0 v0.0.2" >&2
  exit 1
fi

version="$1"            # e.g. "v0.0.2"
changelog="CHANGELOG.md"

awk -v VER="$version" '
  # when we see the exact version header, start printing
  $0 == "# " VER {
    in_section = 1
    next
  }

  # once we hit the next top-level header, stop
  in_section && $0 ~ "^# " {
    exit
  }

  # if we are in the wanted section, print the line
  in_section {
    print
  }
' "$changelog"
