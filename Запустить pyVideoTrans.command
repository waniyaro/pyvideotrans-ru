#!/bin/bash
# Запуск pyVideoTrans с русским интерфейсом и Sber GigaAM
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

export PYVIDEOTRANS_LANG="ru_RU"
"$DIR/.venv/bin/python" "$DIR/sp.py"
