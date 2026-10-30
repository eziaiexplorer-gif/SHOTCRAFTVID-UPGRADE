#!/usr/bin/env sh
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="python3"
if ! command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi
"$PYTHON_BIN" "$DIR/install.py" "$@"
