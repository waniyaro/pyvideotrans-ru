# Инструкция для ИИ-агента Antigravity (Развертывание на компьютере отца)

Привет, агент! Если пользователь дал тебе ссылку на этот репозиторий, твоя задача — настроить **pyVideoTrans (Русскую версию)** на компьютере пользователя, удалить любые старые версии, подключить MCP-сервер и создать удобный запуск в 1 клик.

Выполни следующие 5 шагов автономно:

---

### Шаг 1. Найти и удалить старую версию pyVideoTrans
Проверь систему на наличие предыдущих установок или распакованных архивов pyVideoTrans:
* **На Windows:**
  - Проверь папки: `C:\pyVideoTrans`, `%USERPROFILE%\pyvideotrans`, `%USERPROFILE%\Downloads\pyvideotrans*`, `%USERPROFILE%\Desktop\pyvideotrans*`.
  - Если найдена старая версия — удали её (`rmdir /s /q ...`), сохранив файлы пользователя при необходимости.
* **На macOS / Linux:**
  - Проверь папки `~/pyvideotrans`, `~/Downloads/pyvideotrans*`.

---

### Шаг 2. Развернуть текущий репозиторий
Склонируй этот репозиторий в постоянную рабочую директорию:
* Рекомендуемый путь:
  - Windows: `C:\pyvideotrans-ru` или `%USERPROFILE%\pyvideotrans-ru`
  - macOS: `~/pyvideotrans-ru`
```bash
git clone https://github.com/waniyaro/pyvideotrans-ru.git
cd pyvideotrans-ru
```

---

### Шаг 3. Установить зависимости и Sber GigaAM
Создай виртуальное окружение Python 3.10 и установи зависимости:
* **На Windows:**
  ```cmd
  python -m venv .venv
  .venv\Scripts\pip.exe install --upgrade pip
  .venv\Scripts\pip.exe install PySide6 requests aiohttp httpx tenacity soundfile gigaam
  ```
* **На macOS / Linux:**
  ```bash
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install PySide6 requests aiohttp httpx tenacity soundfile gigaam
  ```
*(Или просто запусти `install.bat` на Windows / `./install.sh` на Mac).*

---

### Шаг 4. Подключить MCP-сервер для Antigravity
В проекте есть готовый инструмент: `audio_voice_mcp.py`.
Пропиши его в конфигурацию MCP (`~/.gemini/antigravity/mcp.json` или в активный проект):
```json
{
  "mcpServers": {
    "voice-toolkit": {
      "command": "<ПУТЬ_К_ПРОЕКТУ>/.venv/Scripts/python.exe",
      "args": ["<ПУТЬ_К_ПРОЕКТУ>/audio_voice_mcp.py"]
    }
  }
}
```
*(Для macOS путь к python: `<ПУТЬ_К_ПРОЕКТУ>/.venv/bin/python`).*

---

### Шаг 5. Создать ярлык на Рабочем столе и проверить запуск
1. Создай ярлык на Рабочем столе:
   * **На Windows:** Создай ярлык `pyVideoTrans (Русская версия).lnk`, ведущий на `Запустить pyVideoTrans.bat`.
   * **На macOS:** Создай симлинк или покажи пользователю файл `Запустить pyVideoTrans.command`.
2. Проверь тестовый запуск скрипта:
   - Проверь, что `sp.py` стартует без ошибок импортов.
   - Отчитайся пользователю: подтверди, что старая версия удалена, новая установлена, ярлык на рабочем столе готов, и MCP-сервер подключен!
