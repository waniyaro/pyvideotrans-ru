@echo off
chcp 65001 > nul
title Обновление pyVideoTrans (Русская версия)

cd /d "%~dp0"

echo =======================================================
echo   Обновление pyVideoTrans до последней версии
echo =======================================================
echo.

if exist ".git" (
    echo [1/2] Обновление через Git...
    git pull origin main
    if %ERRORLEVEL% EQU 0 (
        echo Код успешно обновлен!
        goto check_deps
    )
)

echo [1/2] Загрузка обновлений с GitHub...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Скачивание обновлений...' -ForegroundColor Cyan; Invoke-WebRequest -Uri 'https://github.com/waniyaro/pyvideotrans-ru/archive/refs/heads/main.zip' -OutFile 'update_temp.zip'; Write-Host 'Распаковка...' -ForegroundColor Cyan; Expand-Archive -Path 'update_temp.zip' -DestinationPath 'update_unpacked' -Force; Copy-Item -Path 'update_unpacked\pyvideotrans-ru-main\*' -Destination '.' -Recurse -Force; Remove-Item 'update_temp.zip', 'update_unpacked' -Recurse -Force; Write-Host 'Файлы успешно обновлены!' -ForegroundColor Green"

:check_deps
echo.
echo [2/2] Проверка зависимостей...
if exist ".venv\Scripts\pip.exe" (
    ".venv\Scripts\pip.exe" install -r requirements.txt --quiet
)

echo.
echo =======================================================
echo   Обновление успешно завершено!
echo =======================================================
echo.
pause
