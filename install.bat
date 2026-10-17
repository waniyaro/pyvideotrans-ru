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
set "PY_CMD="

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=py"
) else (
    python --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ОШИБКА] Python не найден в системе!
    echo.
    echo Пожалуйста, установите Python с сайта: https://www.python.org/downloads/
    echo При установке ОБЯЗАТЕЛЬНО отметьте галочку: "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

%PY_CMD% --version
echo Python успешно обнаружен!
echo.

echo [2/3] Настройка виртуального окружения и установка библиотек...
echo (Это займет 1-3 минуты, пожалуйста, подождите...)
echo.

if not exist ".venv" (
    echo Создание изолированного окружения .venv...
    %PY_CMD% -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
    echo [ОШИБКА] Не удалось создать .venv!
    pause
    exit /b 1
)

echo Обновление pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo Установка необходимых библиотек (PySide6, aiohttp, GigaAM, PyTorch)...
".venv\Scripts\pip.exe" install -r requirements.txt

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
