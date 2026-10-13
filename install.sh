#!/bin/bash
# Автоматическая установка pyVideoTrans (Русская версия) для macOS и Linux

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================="
echo "  Установка pyVideoTrans (Русская версия + Sber GigaAM)"
echo "======================================================="

# 1. Проверка и удаление старых версий
OLD_DIRS=("$HOME/pyvideotrans" "$HOME/Downloads/pyvideotrans*")
for OLD in "${OLD_DIRS[@]}"; do
    if [ -d "$OLD" ] && [ "$OLD" != "$DIR" ]; then
        echo "Найдена старая версия: $OLD"
        read -p "Удалить старую версию $OLD? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$OLD"
            echo "Старая версия удалена."
        fi
    fi
done

# 2. Проверка python3 и uv
if command -v uv &> /dev/null; then
    echo "Используем uv для быстрой настройки..."
    uv venv --python 3.10 .venv
    uv pip install PySide6 requests aiohttp httpx tenacity soundfile gigaam
else
    echo "Создаем виртуальное окружение через python3..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install PySide6 requests aiohttp httpx tenacity soundfile gigaam
fi

chmod +x "$DIR/run.sh" "$DIR/Запустить pyVideoTrans.command"

echo "======================================================="
echo "  Установка завершена! Запуск: ./run.sh"
echo "======================================================="
