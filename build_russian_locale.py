#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate complete, high-quality Russian localizations for pyVideoTrans:
1. videotrans/language/ru_RU.json (Desktop UI)
2. videotrans/webui_languages/ru_RU.json (WebUI)
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Curated terminology dictionary for accurate and natural audio/video/UI translations
GLOSSARY = {
    "&Help": "Справка / О программе (&H)",
    "&RECOGNsetting": "Настройки распознавания речи (&R)",
    "&Setting": "Настройки перевода (&S)",
    "&TTSsetting": "Настройки озвучки (TTS) (&E)",
    "&Tools": "Инструменты / Опции (&T)",
    "softname": "pyVideoTrans — Перевод и озвучка видео",
    "Trial dubbing": "Прослушать голос",
    "Select audio & video": "Выбрать видео/аудио",
    "Select Video/Audio": "Выбрать видео/аудио",
    "Save to..": "Сохранить в...",
    "Start": "Старт",
    "Restart": "Перезапуск",
    "Retry failed": "Повторить ошибки",
    "Dubbing acceler": "Ускорять озвучку",
    "Slow video": "Замедлять видео",
    "Del inline mute?": "Удалять паузы между репликами?",
    "Align subtitles and audio": "Синхронизировать субтитры и речь",
    "Sync Subtitles & Speech": "Синхронизировать субтитры и речь",
    "Retain original background sound": "Сохранить оригинальный фоновый звук",
    "Add background audio": "Добавить фоновую музыку",
    "Add BGM": "Добавить фоновую музыку",
    "Options": "Настройки",
    "Save and Close": "Сохранить и закрыть",
    "Save & Close": "Сохранить и закрыть",
    "save_settings": "Сохранить и закрыть",
    "Standard Function Mode": "Стандартный режим (перевод и дубляж)",
    "Extract Srt And Translate": "Извлечение субтитров и перевод",
    "Speech Recognition Text": "Распознавание речи в текст (STT)",
    "From Text Into Speech": "Синтез речи из текста (TTS)",
    "From  Text  Into  Speech": "Синтез речи из текста (TTS)",
    "Text Or Srt Translation": "Перевод текста или субтитров",
    "Text  Or Srt  Translation": "Перевод текста или субтитров",
    "Multi voice dubbing for SRT": "Многоголосая озвучка субтитров",
    "Video Subtitles Merging": "Сведение видео, аудио и субтитров",
    "Separate Video to audio": "Извлечь аудио из видео",
    "Vocal & instrument Separate": "Разделение вокала и музыки/фона",
    "Vocal / Background Audio Separation": "Разделение вокала и музыки/фона",
    "Combine Two Subtitles": "Объединить два файла субтитров",
    "Batch video/audio merger": "Пакетное объединение видео и аудио",
    "Batch Video Srt merger": "Пакетное объединение видео и субтитров",
    "Merge Video & Audio": "Объединить видео и аудио",
    "Merge Video & Subtitles": "Объединить видео и субтитры",
    "Mixing 2 Audio Streams": "Микширование 2 аудиодорожек",
    "Batch Audio/Video conver": "Пакетный конвертер медиа",
    "Conversion Subtitle Format": "Конвертер форматов субтитров",
    "Add watermark to video": "Добавление водяного знака",
    "Edit video on subtitles": "Нарезка видео по субтитрам",
    "Real-time speech-to-text": "Распознавание речи в реальном времени",
    "Text matching and timing": "Синхронизация текста со звуком",
    "Batch create folder structure": "Пакетное создание структуры папок",
    "Import spoken SRT": "Импорт оригинальных субтитров (SRT)",
    "Import target language SRT": "Импорт переведенных субтитров (SRT)",
    "Speech language": "Язык оригинала",
    "Target lang": "Язык перевода",
    "Translate channel": "Канал перевода",
    "Dubbing channel": "Канал озвучки (TTS)",
    "Dubbing role": "Голос / Диктор",
    "Dubbing speed": "Скорость озвучки",
    "Enable CUDA?": "Включить CUDA (GPU)?",
    "CUDA GPU acceleration unavailable. Verify NVIDIA GPU & CUDA installation (Help -> CUDA Help).": "Ускорение CUDA недоступно. Проверьте установку видеокарты NVIDIA и CUDA.",
    "Open Documents": "Документация",
    "juanzhu": "Поддержать проект",
    "Donating developers": "Поддержать разработчиков",
    "Documents": "Документация",
    "Having problems? Ask": "Форум вопросов и ответов",
    "Github Repository": "Репозиторий GitHub",
    "Post issue": "Сообщить об ошибке на GitHub",
    "Solution to model download failure": "Что делать, если не скачиваются модели",
    "CUDA & cuDNN": "Справка по CUDA и cuDNN",
    "FFmpeg": "Официальный сайт FFmpeg",
    "Download Hard Subtitle Extraction Software": "Скачать утилиту для извлечения вшитых субтитров",
    "Disclaimer": "Отказ от ответственности",
    "Proxy": "Прокси",
    "Trial dubbing": "Прослушать голос",
    "nosubtitle": "Без субтитров",
    "embedsubtitle": "Вшить субтитры в видео (хардсаб)",
    "softsubtitle": "Мягкие субтитры (отдельная дорожка)",
    "embedsubtitle2": "Вшить двуязычные субтитры",
    "softsubtitle2": "Мягкие двуязычные субтитры",

    # Language codes
    "zh-cn": "Китайский (упрощенный)",
    "en": "Английский",
    "ja": "Японский",
    "ko": "Корейский",
    "zh-tw": "Китайский (традиционный)",
    "yue": "Кантонский",
    "fr": "Французский",
    "de": "Немецкий",
    "es": "Испанский",
    "es-419": "Испанский (Латинская Америка)",
    "pt": "Португальский",
    "pt-br": "Португальский (Бразилия)",
    "it": "Итальянский",
    "ru": "Русский",
    "hu": "Венгерский",
    "pl": "Польский",
    "nl": "Нидерландский",
    "sv": "Шведский",
    "uk": "Украинский",
    "cs": "Чешский",
    "el": "Греческий",
    "nb": "Норвежский (Букмол)",
    "ro": "Румынский",
    "bg": "Болгарский",
    "fi": "Финский",
    "vi": "Вьетнамский",
    "th": "Тайский",
    "id": "Индонезийский",
    "ms": "Малайский",
    "fil": "Филиппинский",
    "km": "Кхмерский",
    "lo": "Лаосский",
    "my": "Бирманский",
    "hi": "Хинди",
    "ur": "Урду",
    "bn": "Бенгальский",
    "ar": "Арабский",
    "tr": "Турецкий",
    "fa": "Персидский",
    "kk": "Казахский",
    "uz": "Узбекский",
    "he": "Иврит",
    "af": "Африкаанс",
    "sq": "Албанский",
    "am": "Амхарский",
    "az": "Азербайджанский",
    "bs": "Боснийский",
    "ca": "Каталанский",
    "hr": "Хорватский",
    "da": "Датский",
    "et": "Эстонский",
    "gl": "Галисийский",
    "ka": "Грузинский",
    "gu": "Гуджарати",
    "is": "Исландский",
    "iu": "Инуктитут",
    "ga": "Ирландский",
    "jv": "Яванский",
    "kn": "Каннада",
    "lv": "Латышский",
    "lt": "Литовский",
    "mk": "Македонский",
    "ml": "Малаялам",
    "mt": "Мальтийский",
    "mr": "Маратхи",
    "mn": "Монгольский",
    "ne": "Непальский",
    "ps": "Пушту",
    "sr": "Сербский",
    "si": "Сингальский",
    "sk": "Словацкий",
    "sl": "Словенский",
    "so": "Сомалийский",
    "su": "Сунданский",
    "sw": "Суахили",
    "ta": "Тамильский",
    "te": "Телугу",
    "cy": "Валлийский",
    "zu": "Зулу",
    "auto": "Автоопределение",
}


def translate_text(text: str, sl="en", tl="ru") -> str:
    """Translate single string via google endpoint."""
    if not text or not text.strip():
        return text
    # Avoid translating pure URLs, numbers, or technical names
    if text.startswith("http://") or text.startswith("https://"):
        return text

    # Protect placeholders like {} or {0}
    placeholders = re.findall(r"\{[0-9]*\}", text)
    temp_text = text
    for i, ph in enumerate(placeholders):
        temp_text = temp_text.replace(ph, f"__PH{i}__", 1)

    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl="
        + sl
        + "&tl="
        + tl
        + "&dt=t&q="
        + urllib.parse.quote(temp_text)
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = "".join([x[0] for x in data[0] if x[0]])
    except Exception as e:
        print(f"Warn: failed to translate '{text[:30]}...': {e}")
        return text

    # Restore placeholders
    for i, ph in enumerate(placeholders):
        # account for accidental spaces introduced around placeholder
        translated = re.sub(rf"__\s*PH{i}\s*__", ph, translated)
        translated = translated.replace(f"__PH{i}__", ph)

    return translated


def translate_batch(texts: list[str], sl="en", tl="ru") -> list[str]:
    """Translate batch of strings."""
    if not texts:
        return []

    # Map placeholders for each item
    protected_texts = []
    item_placeholders = []
    for text in texts:
        if not text or not text.strip() or text.startswith("http"):
            protected_texts.append(text)
            item_placeholders.append([])
            continue
        phs = re.findall(r"\{[0-9]*\}", text)
        item_placeholders.append(phs)
        temp_text = text
        for i, ph in enumerate(phs):
            temp_text = temp_text.replace(ph, f"XYZ{i}XYZ", 1)
        protected_texts.append(temp_text)

    sep = "\n---QSEP---\n"
    combined = sep.join(protected_texts)
    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl="
        + sl
        + "&tl="
        + tl
        + "&dt=t&q="
        + urllib.parse.quote(combined)
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            full = "".join([x[0] for x in data[0] if x[0]])
            parts = full.split("---QSEP---")
            if len(parts) != len(texts):
                # Fallback to single translations if separator was corrupted
                print(
                    f"Warning: batch count mismatch ({len(parts)} != {len(texts)}), falling back to individual..."
                )
                return [translate_text(t, sl, tl) for t in texts]

            results = []
            for part, phs, orig in zip(parts, item_placeholders, texts):
                clean_part = part.strip()
                for i, ph in enumerate(phs):
                    clean_part = re.sub(rf"XYZ\s*{i}\s*XYZ", ph, clean_part)
                    clean_part = clean_part.replace(f"XYZ{i}XYZ", ph)
                results.append(clean_part)
            return results
    except Exception as e:
        print(f"Batch failed ({e}), falling back to individual calls...")
        return [translate_text(t, sl, tl) for t in texts]


def build_locale(source_file: Path, target_file: Path, zh_file: Path = None):
    print(f"\nProcessing {source_file} -> {target_file}...")
    with open(source_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    zh_data = {}
    if zh_file and zh_file.exists():
        with open(zh_file, "r", encoding="utf-8") as f:
            zh_data = json.load(f)

    result = {}
    to_translate_keys = []
    to_translate_vals = []

    for k, v in source_data.items():
        if k in GLOSSARY:
            result[k] = GLOSSARY[k]
        elif v in GLOSSARY:
            result[k] = GLOSSARY[v]
        elif k.startswith("http") or v.startswith("http"):
            result[k] = v
        else:
            to_translate_keys.append(k)
            to_translate_vals.append(v)

    print(
        f"Pre-matched with glossary: {len(result)}, remaining to translate: {len(to_translate_keys)}"
    )

    batch_size = 30
    for i in range(0, len(to_translate_keys), batch_size):
        chunk_keys = to_translate_keys[i : i + batch_size]
        chunk_vals = to_translate_vals[i : i + batch_size]
        print(
            f"Translating {i+1} to {min(i+batch_size, len(to_translate_keys))} of {len(to_translate_keys)}..."
        )
        translated_chunk = translate_batch(chunk_vals)
        for k, orig_v, trans_v in zip(chunk_keys, chunk_vals, translated_chunk):
            # Check placeholders sanity
            orig_phs = re.findall(r"\{[0-9]*\}", orig_v)
            trans_phs = re.findall(r"\{[0-9]*\}", trans_v)
            if len(orig_phs) != len(trans_phs):
                # Placeholder lost, fix by appending or falling back
                trans_v = orig_v
            result[k] = trans_v
        time.sleep(0.3)

    # If Chinese source had language names that english didn't have as keys, also add them
    for k, v in zh_data.items():
        if k not in result and k in GLOSSARY:
            result[k] = GLOSSARY[k]

    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {target_file} with {len(result)} keys!")


if __name__ == "__main__":
    app_en = BASE_DIR / "videotrans" / "language" / "en_US.json"
    app_zh = BASE_DIR / "videotrans" / "language" / "zh_CN.json"
    app_ru = BASE_DIR / "videotrans" / "language" / "ru_RU.json"

    web_en = BASE_DIR / "videotrans" / "webui_languages" / "en_US.json"
    web_zh = BASE_DIR / "videotrans" / "webui_languages" / "zh_CN.json"
    web_ru = BASE_DIR / "videotrans" / "webui_languages" / "ru_RU.json"

    build_locale(app_en, app_ru, app_zh)
    build_locale(web_en, web_ru, web_zh)
    print("\nAll Russian localizations generated successfully!")
