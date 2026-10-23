#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
[[ -x .venv/bin/python ]] || { echo "Run ./setup.sh --install-only first." >&2; exit 1; }
view=${1:-automotive}
case "$view" in
  automotive|industrial) if [[ $# -gt 0 ]]; then shift; fi ;;
  *) echo "Usage: ./run.sh [automotive|industrial] [display options]" >&2; exit 2 ;;
esac
if [[ $view == automotive ]]; then exec .venv/bin/python -m gauges.automotive_gauge "$@"
else exec .venv/bin/python -m gauges.industrial_panel "$@"; fi
