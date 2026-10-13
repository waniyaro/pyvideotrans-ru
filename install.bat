@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Установка pyVideoTrans (Русская версия)

cd /d "%~dp0"

echo =======================================================
echo   Установка pyVideoTrans (Русская версия + Sber GigaAM)
echo =======================================================
echo.

echo [1/3] Проверка Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Python не найден в системе!
    echo.
    echo Пожалуйста, установите Python 3.10 (или 3.11/3.12) с сайта:
    echo https://www.python.org/downloads/
    echo.
    echo ОБЯЗАТЕЛЬНО отметьте галочку: "Add Python to PATH" при установке!
    echo.
    pause
    exit /b 1
)

python --version
echo Python найден.
echo.

echo [2/3] Настройка виртуального окружения и установка зависимостей...
if not exist ".venv" (
    echo Создание .venv...
    python -m venv .venv
)

echo Обновление pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo Установка requirements.txt...
    pip install -r requirements.txt
) else (
    echo Установка базовых библиотек...
    pip install PySide6 requests aiohttp httpx tenacity soundfile
)

echo Установка Sber GigaAM...
pip install gigaam

echo.
echo [3/3] Создание ярлыка на Рабочем столе...
set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGET=%~dp0Запустить pyVideoTrans.bat"
set "SHORTCUT=%DESKTOP%\pyVideoTrans (Русская версия).lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%~dp0'; $s.Save()"

echo.
echo =======================================================
echo   Установка успешно завершена!
echo   Ярлык создан на Рабочем столе: pyVideoTrans (Русская версия)
echo =======================================================
echo.
pause
