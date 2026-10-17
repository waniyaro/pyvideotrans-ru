@echo off
chcp 65001 > nul
cd /d "%~dp0"
title pyVideoTrans - Русская версия

set PYVIDEOTRANS_LANG=ru_RU

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" sp.py %*
) else (
    py sp.py %* 2>nul || python sp.py %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Ошибка запуска] Если программа не запустилась, запустите install.bat для восстановления.
    pause
)
