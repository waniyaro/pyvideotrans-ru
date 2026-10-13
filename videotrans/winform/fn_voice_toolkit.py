# -*- coding: utf-8 -*-
import os
import shutil
from pathlib import Path

from PySide6.QtCore import QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog

from videotrans.configure import constants
from videotrans.configure.config import tr, params, HOME_DIR
from videotrans.util.help_misc import show_error, show_popup
from videotrans.util.voice_toolkit import trim_media, enhance_voice, clean_text, clean_srt, transcribe_with_gigaam
from videotrans.winform import get_cls


def openwin():
    RESULT_DIR = HOME_DIR + "/voice_toolkit"
    Path(RESULT_DIR).mkdir(parents=True, exist_ok=True)

    class WorkerThread(QThread):
        finished_signal = Signal(bool, str)

        def __init__(self, action, kwargs):
            super().__init__()
            self.action = action
            self.kwargs = kwargs

        def run(self):
            try:
                if self.action == "trim":
                    ok, msg = trim_media(**self.kwargs)
                    self.finished_signal.emit(ok, msg)
                elif self.action == "enhance":
                    ok, msg = enhance_voice(**self.kwargs)
                    self.finished_signal.emit(ok, msg)
                elif self.action == "clean_srt":
                    ok, count, msg = clean_srt(**self.kwargs)
                    self.finished_signal.emit(ok, msg)
                elif self.action == "transcribe":
                    ok, text, segments = transcribe_with_gigaam(**self.kwargs)
                    self.finished_signal.emit(ok, text)
            except Exception as e:
                self.finished_signal.emit(False, str(e))

    winobj = get_cls(Path(__file__).stem)()

    def on_select_media():
        format_str = " ".join(["*." + f for f in constants.VIDEO_EXTS + constants.AUDIO_EXITS])
        fname, _ = QFileDialog.getOpenFileName(
            winobj,
            tr("Select Media File"),
            params.get("last_opendir", ""),
            f"Media files ({format_str})"
        )
        if fname:
            winobj.filepath = fname.replace("\\", "/")
            winobj.file_path_edit.setText(winobj.filepath)
            params["last_opendir"] = os.path.dirname(fname)
            winobj.status_label.setText(tr("File loaded:") + f" {Path(fname).name}")

    def on_select_srt():
        fname, _ = QFileDialog.getOpenFileName(
            winobj,
            tr("Select SRT File"),
            params.get("last_opendir", ""),
            "Subtitle files (*.srt)"
        )
        if fname:
            winobj.srtpath = fname.replace("\\", "/")
            winobj.srt_path_edit.setText(winobj.srtpath)
            params["last_opendir"] = os.path.dirname(fname)

    def on_finished(ok, msg):
        winobj.enhance_btn.setDisabled(False)
        winobj.trim_btn.setDisabled(False)
        winobj.clean_srt_btn.setDisabled(False)
        if ok:
            winobj.status_label.setText(tr("Completed:") + f" {Path(msg).name if os.path.exists(msg) else msg}")
            show_popup(tr("Success"), f"{tr('Operation finished successfully!')}\n{msg}")
        else:
            winobj.status_label.setText(tr("Error"))
            show_error(msg)

    def on_enhance():
        if not winobj.filepath or not os.path.exists(winobj.filepath):
            show_error(tr("Must select videos or audio"))
            return

        denoise_idx = winobj.denoise_combo.currentIndex()
        denoise_map = {0: "medium", 1: "light", 2: "strong", 3: "none"}
        denoise_level = denoise_map.get(denoise_idx, "medium")

        stem = Path(winobj.filepath).stem
        ext = Path(winobj.filepath).suffix
        out_file = f"{RESULT_DIR}/{stem}_enhanced{ext}"

        winobj.status_label.setText(tr("Processing voice enhancement & noise reduction..."))
        winobj.enhance_btn.setDisabled(True)

        task = WorkerThread(
            action="enhance",
            kwargs={
                "input_file": winobj.filepath,
                "output_file": out_file,
                "denoise_level": denoise_level,
                "clarity_boost": winobj.check_clarity.isChecked(),
                "normalize_speech": winobj.check_norm.isChecked(),
                "cut_subsonic": winobj.check_highpass.isChecked()
            }
        )
        task.finished_signal.connect(on_finished)
        task.start()
        winobj._task = task

    def on_trim():
        if not winobj.filepath or not os.path.exists(winobj.filepath):
            show_error(tr("Must select videos or audio"))
            return

        start_t = winobj.start_edit.text().strip()
        end_t = winobj.end_edit.text().strip()
        if not start_t:
            start_t = "0"

        stem = Path(winobj.filepath).stem
        ext = Path(winobj.filepath).suffix
        out_file = f"{RESULT_DIR}/{stem}_trim{ext}"

        winobj.status_label.setText(tr("Trimming media file..."))
        winobj.trim_btn.setDisabled(True)

        task = WorkerThread(
            action="trim",
            kwargs={
                "input_file": winobj.filepath,
                "output_file": out_file,
                "start_time": start_t,
                "end_time": end_t if end_t else None,
                "copy_codec": winobj.check_lossless.isChecked()
            }
        )
        task.finished_signal.connect(on_finished)
        task.start()
        winobj._task = task

    def on_clean_text():
        raw_text = winobj.text_edit.toPlainText().strip()
        if not raw_text:
            show_error(tr("Please enter or paste text to clean."))
            return

        cleaned = clean_text(
            raw_text,
            language="ru",
            remove_fillers=winobj.check_fillers.isChecked(),
            remove_stutters=winobj.check_stutters.isChecked(),
            remove_hallucinations=True,
            fix_punctuation=True
        )
        winobj.text_edit.setPlainText(cleaned)
        winobj.status_label.setText(tr("Text cleaned successfully!"))

    def on_clean_srt():
        if not winobj.srtpath or not os.path.exists(winobj.srtpath):
            show_error(tr("Please select an SRT subtitle file."))
            return

        stem = Path(winobj.srtpath).stem
        out_srt = f"{RESULT_DIR}/{stem}_cleaned.srt"

        winobj.status_label.setText(tr("Cleaning SRT subtitles..."))
        winobj.clean_srt_btn.setDisabled(True)

        task = WorkerThread(
            action="clean_srt",
            kwargs={
                "input_srt": winobj.srtpath,
                "output_srt": out_srt,
                "language": "ru",
                "remove_fillers": winobj.check_fillers.isChecked(),
                "remove_stutters": winobj.check_stutters.isChecked()
            }
        )
        task.finished_signal.connect(on_finished)
        task.start()
        winobj._task = task

    def on_transcribe():
        if not winobj.filepath or not os.path.exists(winobj.filepath):
            show_error(tr("Must select videos or audio"))
            return

        stem = Path(winobj.filepath).stem
        out_srt = f"{RESULT_DIR}/{stem}_gigaam.srt"

        winobj.status_label.setText(tr("Transcribing with Sber GigaAM..."))
        winobj.transcribe_btn.setDisabled(True)

        task = WorkerThread(
            action="transcribe",
            kwargs={
                "input_file": winobj.filepath,
                "output_srt": out_srt,
                "clean": winobj.check_fillers.isChecked()
            }
        )

        def _on_transcribe_done(ok, text):
            winobj.transcribe_btn.setDisabled(False)
            if ok:
                winobj.text_edit.setPlainText(text)
                winobj.status_label.setText(tr("Transcription completed!"))
                show_popup(tr("Success"), f"{tr('Speech transcribed and saved to:')}\n{out_srt}")
            else:
                winobj.status_label.setText(tr("Error"))
                show_error(text)

        task.finished_signal.connect(_on_transcribe_done)
        task.start()
        winobj._task = task

    def on_open_dir():
        QDesktopServices.openUrl(QUrl.fromLocalFile(RESULT_DIR))

    # Connect signals
    winobj.select_file_btn.clicked.connect(on_select_media)
    winobj.select_srt_btn.clicked.connect(on_select_srt)
    winobj.enhance_btn.clicked.connect(on_enhance)
    winobj.trim_btn.clicked.connect(on_trim)
    winobj.transcribe_btn.clicked.connect(on_transcribe)
    winobj.clean_text_btn.clicked.connect(on_clean_text)
    winobj.clean_srt_btn.clicked.connect(on_clean_srt)
    winobj.open_output_btn.clicked.connect(on_open_dir)

    return winobj
