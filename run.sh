#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export PYVIDEOTRANS_LANG="ru_RU"
"$DIR/.venv/bin/python" "$DIR/sp.py" "$@"
