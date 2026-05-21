#!/usr/bin/env bash
set -euo pipefail

# Check for page-level Back buttons outside the global base template.
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES_DIR="$REPO_ROOT/web/templates"

if [ ! -d "$TEMPLATES_DIR" ]; then
  echo "No templates directory found; skipping check." >&2
  exit 0
fi

# Search for patterns that indicate a page-level Back button.
# Exclude base.html because it intentionally contains the global Back.
# The patterns include: window.history.back( , literal >Back<, or include of back_home_buttons.html
matches=$(grep -RIn --exclude="base.html" -nE "window.history.back\(|>\s*Back\s*<|back_home_buttons.html" "$TEMPLATES_DIR" || true)

if [ -n "$matches" ]; then
  echo "ERROR: Page-level Back buttons found in templates:" >&2
  echo "$matches" >&2
  exit 2
fi

echo "OK: no page-level Back buttons found"
exit 0
