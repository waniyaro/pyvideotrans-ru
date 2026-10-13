@echo off
chcp 65001 > nul
cd /d "%~dp0"
title pyVideoTrans - Русская версия

set PYVIDEOTRANS_LANG=ru_RU

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" sp.py %*
) else if exist "python.exe" (
    python.exe sp.py %*
) else (
    python sp.py %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Ошибка запуска] Если программа не запустилась, проверьте .venv или запустите install.bat заново.
    pause
)
