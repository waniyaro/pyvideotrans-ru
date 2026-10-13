[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  Установка pyVideoTrans (Русская версия + Sber GigaAM)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# 1. Проверка Python
Write-Host "[1/3] Проверка Python..." -ForegroundColor Yellow
try {
    $pyVer = & python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Python not found" }
    Write-Host "Найден: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[ОШИБКА] Python не найден в системе!" -ForegroundColor Red
    Write-Host "Установите Python с https://www.python.org/downloads/ и отметьте 'Add Python to PATH'." -ForegroundColor Red
    Pause
    Exit
}

# 2. Создание .venv и установка библиотек
Write-Host "`n[2/3] Настройка виртуального окружения (.venv)..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    & python -m venv .venv
}

Write-Host "Установка библиотек..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pip install --upgrade pip

if (Test-Path "requirements.txt") {
    & .\.venv\Scripts\pip.exe install -r requirements.txt
} else {
    & .\.venv\Scripts\pip.exe install PySide6 requests aiohttp httpx tenacity soundfile
}

Write-Host "Установка Sber GigaAM..." -ForegroundColor Yellow
& .\.venv\Scripts\pip.exe install gigaam

# 3. Создание ярлыка
Write-Host "`n[3/3] Создание ярлыка на Рабочем столе..." -ForegroundColor Yellow
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "pyVideoTrans (Русская версия).lnk"
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($shortcutPath)
$s.TargetPath = (Join-Path $PSScriptRoot "Запустить pyVideoTrans.bat")
$s.WorkingDirectory = $PSScriptRoot
$s.Save()

Write-Host "`n=======================================================" -ForegroundColor Green
Write-Host "  Установка успешно завершена!" -ForegroundColor Green
Write-Host "  Ярлык на Рабочем столе: pyVideoTrans (Русская версия)" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Pause
