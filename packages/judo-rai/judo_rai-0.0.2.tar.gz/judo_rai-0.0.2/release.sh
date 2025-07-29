#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <version-without-v>" >&2
  echo "Example: $0 0.0.2" >&2
  exit 1
fi

bare="$1"            # e.g. 0.0.2
full="v$bare"        # e.g. v0.0.2

# extract only the lines under "# v<version>"
notes=$(
  awk -v VER="$full" '
    BEGIN {
      header = "# " VER
      in_section = 0
    }
    $0 == header {
      in_section = 1
      next
    }
    in_section && $0 ~ "^# " {
      exit
    }
    in_section {
      print
    }
  ' CHANGELOG.md
)

# create the release with tag=0.0.2, title=v0.0.2, and the right notes
gh release create "$bare" \
  --title "$full" \
  --notes "$notes"
