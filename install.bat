@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title Установка pyVideoTrans (Русская версия)

echo =======================================================
echo   Установка pyVideoTrans (Русская версия + Sber GigaAM)
echo =======================================================
echo.

cd /d "%~dp0"

:: 1. Проверка и удаление старых версий
echo [1/4] Проверка предыдущих версий...
set "OLD_DIRS=%USERPROFILE%\pyvideotrans C:\pyVideoTrans"
for %%D in (%OLD_DIRS%) do (
    if exist "%%D" (
        echo Найдена старая версия в: %%D
        set /p DEL_OLD="Удалить старую версию %%D? (Y/N): "
        if /i "!DEL_OLD!"=="Y" (
            echo Удаление %%D...
            rmdir /s /q "%%D"
            echo Старая версия удалена.
        )
    )
)

:: 2. Проверка Python
echo.
echo [2/4] Проверка Python 3...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Python не найден!
    echo Пожалуйста, установите Python 3.10 с сайта https://www.python.org/downloads/
    echo Обязательно отметьте галочку "Add Python to PATH" при установке!
    pause
    exit /b 1
)

:: 3. Создание виртуального окружения
echo.
echo [3/4] Настройка виртуального окружения (.venv)...
if not exist ".venv" (
    echo Создание .venv...
    python -m venv .venv
)

echo Обновление pip и установка зависимостей...
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

:: 4. Создание ярлыка на рабочем столе
echo.
echo [4/4] Создание ярлыка на Рабочем столе...
set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGET=%~dp0Запустить pyVideoTrans.bat"
set "SHORTCUT=%DESKTOP%\pyVideoTrans (Русская версия).lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%~dp0'; $s.Save()"

echo.
echo =======================================================
echo   Установка успешно завершена!
echo   Ярлык создан на Рабочем столе: pyVideoTrans (Русская версия)
echo =======================================================
echo.
pause
