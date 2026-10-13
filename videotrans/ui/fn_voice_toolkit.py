# -*- coding: utf-8 -*-
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from videotrans.configure.config import tr, ROOT_DIR


class Ui_fn_voice_toolkit(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(f"{ROOT_DIR}/videotrans/styles/icon.ico"))
        self.setupUi(self)

    def setupUi(self, form):
        self.filepath = ""
        self.srtpath = ""
        self.has_done = False

        form.setObjectName("voice_toolkit")
        form.setWindowTitle(tr("Voice & Audio Toolkit"))
        form.resize(650, 680)
        form.setMinimumSize(580, 600)

        main_layout = QtWidgets.QVBoxLayout(form)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 1. Source Media File Selector
        file_box = QtWidgets.QGroupBox(tr("Select Media File (Audio or Video)"))
        file_layout = QtWidgets.QHBoxLayout(file_box)
        
        self.select_file_btn = QtWidgets.QPushButton(tr("Browse..."))
        self.select_file_btn.setMinimumSize(QtCore.QSize(110, 32))
        self.select_file_btn.setCursor(Qt.PointingHandCursor)
        
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_edit.setMinimumSize(QtCore.QSize(0, 32))
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText(tr("Select video or audio file to process..."))
        
        file_layout.addWidget(self.select_file_btn)
        file_layout.addWidget(self.file_path_edit)
        main_layout.addWidget(file_box)

        # Tab Widget for Trimming, Voice Enhancement, and Text/SRT Cleaner
        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs, stretch=1)

        # ================= TAB 1: Voice Enhancement =================
        tab_enhance = QtWidgets.QWidget()
        t1_layout = QtWidgets.QVBoxLayout(tab_enhance)
        t1_layout.setSpacing(10)

        # Denoise level
        denoise_row = QtWidgets.QHBoxLayout()
        denoise_label = QtWidgets.QLabel(tr("Denoise Strength:"))
        self.denoise_combo = QtWidgets.QComboBox()
        self.denoise_combo.addItems([
            tr("Medium (-25 dB) [Recommended]"),
            tr("Light (-32 dB)"),
            tr("Strong (-18 dB)"),
            tr("Disable Denoise")
        ])
        denoise_row.addWidget(denoise_label)
        denoise_row.addWidget(self.denoise_combo, stretch=1)
        t1_layout.addLayout(denoise_row)

        # Checkboxes for voice processing
        self.check_highpass = QtWidgets.QCheckBox(tr("Cut sub-bass rumble & mic thumps (High-pass 80 Hz)"))
        self.check_highpass.setChecked(True)
        t1_layout.addWidget(self.check_highpass)

        self.check_clarity = QtWidgets.QCheckBox(tr("Speech Clarity EQ (Boost voice presence 3.2 kHz & de-box)"))
        self.check_clarity.setChecked(True)
        t1_layout.addWidget(self.check_clarity)

        self.check_norm = QtWidgets.QCheckBox(tr("Loudness Normalization (Broadcast Speech Standard EBU R128)"))
        self.check_norm.setChecked(True)
        t1_layout.addWidget(self.check_norm)

        t1_layout.addStretch(1)

        self.enhance_btn = QtWidgets.QPushButton(tr("Enhance Voice & Denoise"))
        self.enhance_btn.setMinimumSize(QtCore.QSize(0, 38))
        self.enhance_btn.setCursor(Qt.PointingHandCursor)
        t1_layout.addWidget(self.enhance_btn)

        self.tabs.addTab(tab_enhance, tr("Voice Enhancement"))

        # ================= TAB 2: Trim / Cut Media =================
        tab_trim = QtWidgets.QWidget()
        t2_layout = QtWidgets.QVBoxLayout(tab_trim)
        t2_layout.setSpacing(10)

        trim_inputs = QtWidgets.QHBoxLayout()
        lbl_start = QtWidgets.QLabel(tr("Start Time:"))
        self.start_edit = QtWidgets.QLineEdit("00:00:00")
        self.start_edit.setPlaceholderText("00:00:00")
        
        lbl_end = QtWidgets.QLabel(tr("End Time:"))
        self.end_edit = QtWidgets.QLineEdit("")
        self.end_edit.setPlaceholderText("00:01:30")

        trim_inputs.addWidget(lbl_start)
        trim_inputs.addWidget(self.start_edit)
        trim_inputs.addWidget(lbl_end)
        trim_inputs.addWidget(self.end_edit)
        t2_layout.addLayout(trim_inputs)

        self.check_lossless = QtWidgets.QCheckBox(tr("Fast stream copy (lossless, no re-encoding)"))
        self.check_lossless.setChecked(True)
        t2_layout.addWidget(self.check_lossless)

        t2_layout.addStretch(1)

        self.trim_btn = QtWidgets.QPushButton(tr("Cut / Trim Media"))
        self.trim_btn.setMinimumSize(QtCore.QSize(0, 38))
        self.trim_btn.setCursor(Qt.PointingHandCursor)
        t2_layout.addWidget(self.trim_btn)

        self.tabs.addTab(tab_trim, tr("Trim / Cut"))

        # ================= TAB 3: Text & Subtitle Cleaner =================
        tab_clean = QtWidgets.QWidget()
        t3_layout = QtWidgets.QVBoxLayout(tab_clean)
        t3_layout.setSpacing(8)

        # SRT File Selector
        srt_row = QtWidgets.QHBoxLayout()
        self.select_srt_btn = QtWidgets.QPushButton(tr("Select SRT File..."))
        self.select_srt_btn.setCursor(Qt.PointingHandCursor)
        self.srt_path_edit = QtWidgets.QLineEdit()
        self.srt_path_edit.setReadOnly(True)
        self.srt_path_edit.setPlaceholderText(tr("Optional: Select .srt file to clean subtitles"))
        srt_row.addWidget(self.select_srt_btn)
        srt_row.addWidget(self.srt_path_edit)
        t3_layout.addLayout(srt_row)

        # Direct text input/output area
        self.text_edit = QtWidgets.QPlainTextEdit()
        self.text_edit.setPlaceholderText(tr("Or paste transcription text here to clean..."))
        t3_layout.addWidget(self.text_edit, stretch=1)

        # Cleaning checkboxes
        clean_opts = QtWidgets.QHBoxLayout()
        self.check_fillers = QtWidgets.QCheckBox(tr("Remove filler words (э-э, типа, ну, как бы)"))
        self.check_fillers.setChecked(True)
        self.check_stutters = QtWidgets.QCheckBox(tr("Remove stutters & repetitions"))
        self.check_stutters.setChecked(True)
        clean_opts.addWidget(self.check_fillers)
        clean_opts.addWidget(self.check_stutters)
        t3_layout.addLayout(clean_opts)

        self.transcribe_btn = QtWidgets.QPushButton(tr("Transcribe Russian Speech (Sber GigaAM)"))
        self.transcribe_btn.setMinimumSize(QtCore.QSize(0, 36))
        self.transcribe_btn.setCursor(Qt.PointingHandCursor)
        t3_layout.addWidget(self.transcribe_btn)

        clean_btns = QtWidgets.QHBoxLayout()
        self.clean_text_btn = QtWidgets.QPushButton(tr("Clean Text"))
        self.clean_text_btn.setMinimumSize(QtCore.QSize(0, 36))
        self.clean_text_btn.setCursor(Qt.PointingHandCursor)
        
        self.clean_srt_btn = QtWidgets.QPushButton(tr("Clean Selected SRT File"))
        self.clean_srt_btn.setMinimumSize(QtCore.QSize(0, 36))
        self.clean_srt_btn.setCursor(Qt.PointingHandCursor)
        
        clean_btns.addWidget(self.clean_text_btn)
        clean_btns.addWidget(self.clean_srt_btn)
        t3_layout.addLayout(clean_btns)

        self.tabs.addTab(tab_clean, tr("Clean Text & Subtitles"))

        # Bottom Bar: Status label and Open Output Folder
        bottom_layout = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel(tr("Ready"))
        self.status_label.setStyleSheet("color: #848f9c;")
        
        self.open_output_btn = QtWidgets.QPushButton(tr("Open Output Folder"))
        self.open_output_btn.setCursor(Qt.PointingHandCursor)

        bottom_layout.addWidget(self.status_label, stretch=1)
        bottom_layout.addWidget(self.open_output_btn)
        main_layout.addLayout(bottom_layout)
