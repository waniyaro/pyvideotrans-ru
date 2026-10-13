# -*- coding: utf-8 -*-
"""
Voice & Audio Engineering Toolkit for pyVideoTrans
Features:
1. trim_media: Fast lossless or re-encoded cut of audio/video by time range.
2. enhance_voice: Professional speech enhancement pipeline:
   - High-pass rumble filter (80Hz cut)
   - FFT adaptive denoiser (afftdn)
   - Speech presence & clarity EQ (3.2kHz boost, warmth de-boxiness, de-ess)
   - Broadcast speech loudness normalization (speechnorm / dynaudnorm / loudnorm)
3. clean_text: Removes filler words, interjections, stutters, and Whisper hallucinations.
4. clean_srt: Cleans subtitle files with re-indexing and empty line elimination.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Union


def get_ffmpeg_path() -> str:
    """Find FFmpeg binary path cross-platform (Windows / macOS / Linux)."""
    for bin_name in ["ffmpeg", "ffmpeg.exe"]:
        p = shutil.which(bin_name)
        if p:
            return p
    try:
        from videotrans.configure.config import ROOT_DIR
        for p in [f"{ROOT_DIR}/ffmpeg/ffmpeg.exe", f"{ROOT_DIR}/ffmpeg.exe", f"{ROOT_DIR}/ffmpeg/ffmpeg"]:
            if os.path.exists(p):
                return p
    except Exception:
        pass
    for p in ["/Users/waniyaro/.local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/usr/bin/ffmpeg"]:
        if os.path.exists(p):
            return p
    return "ffmpeg"


def time_to_seconds(t: Union[str, float, int]) -> float:
    """Convert time representation (seconds, 'MM:SS', 'HH:MM:SS', 'HH:MM:SS.mmm') to seconds float."""
    if isinstance(t, (int, float)):
        return float(t)
    t = str(t).strip()
    if not t:
        return 0.0
    # Replace comma with dot
    t = t.replace(",", ".")
    parts = t.split(":")
    if len(parts) == 1:
        return float(parts[0])
    elif len(parts) == 2:
        return float(parts[0]) * 60.0 + float(parts[1])
    elif len(parts) == 3:
        return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
    return float(t)


def seconds_to_time(sec: float) -> str:
    """Convert seconds float to 'HH:MM:SS.mmm'."""
    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    seconds = sec % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def trim_media(
    input_file: str,
    output_file: str,
    start_time: Union[str, float, int],
    end_time: Optional[Union[str, float, int]] = None,
    duration: Optional[Union[str, float, int]] = None,
    copy_codec: bool = True
) -> Tuple[bool, str]:
    """
    Trim video or audio file.
    :param input_file: Path to source file
    :param output_file: Path to destination file
    :param start_time: Start timestamp (e.g. 10.5, '00:01:15')
    :param end_time: Optional end timestamp
    :param duration: Optional duration in seconds
    :param copy_codec: If True, uses fast stream copy (-c copy) without re-encoding
    :return: (success: bool, message: str)
    """
    ffmpeg = get_ffmpeg_path()
    start_sec = time_to_seconds(start_time)
    
    cmd = [ffmpeg, "-y", "-ss", str(start_sec)]
    
    if end_time is not None:
        end_sec = time_to_seconds(end_time)
        dur = max(0.0, end_sec - start_sec)
        cmd.extend(["-t", str(dur)])
    elif duration is not None:
        cmd.extend(["-t", str(time_to_seconds(duration))])
        
    cmd.extend(["-i", input_file])
    
    if copy_codec:
        cmd.extend(["-c", "copy"])
    else:
        # High quality re-encode
        ext = Path(output_file).suffix.lower()
        if ext in [".wav", ".pcm"]:
            cmd.extend(["-c:a", "pcm_s16le", "-ar", "44100"])
        elif ext in [".mp3"]:
            cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k"])
        elif ext in [".m4a", ".aac"]:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        elif ext in [".mp4", ".mkv", ".mov"]:
            cmd.extend(["-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "aac", "-b:a", "192k"])
            
    cmd.append(output_file)
    
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            return False, f"FFmpeg error: {proc.stderr[-400:]}"
        return True, output_file
    except Exception as e:
        return False, str(e)


def enhance_voice(
    input_file: str,
    output_file: str,
    denoise_level: str = "medium",  # "none", "light", "medium", "strong"
    clarity_boost: bool = True,
    normalize_speech: bool = True,
    cut_subsonic: bool = True,
    target_lufs: float = -16.0
) -> Tuple[bool, str]:
    """
    Enhance vocal recording: reduce noise, remove low-end rumble, enhance speech intelligibility and normalize loudness.
    :param input_file: Source audio or video file
    :param output_file: Destination file
    :param denoise_level: Noise reduction strength ('none', 'light', 'medium', 'strong')
    :param clarity_boost: Boost speech presence band (2.8 - 3.5 kHz) and tame harshness
    :param normalize_speech: Apply broadcast speech loudness normalization
    :param cut_subsonic: Highpass filter at 80Hz to eliminate table thumps and AC rumble
    :param target_lufs: Target loudness (default -16 LUFS for podcasts/YouTube)
    :return: (success: bool, message: str)
    """
    ffmpeg = get_ffmpeg_path()
    filters = []
    
    # 1. Highpass filter to eliminate sub-bass rumble
    if cut_subsonic:
        filters.append("highpass=f=80:p=2")
        
    # 2. Adaptive FFT Denoiser
    if denoise_level != "none":
        noise_floors = {
            "light": -32,
            "medium": -25,
            "strong": -18
        }
        nf = noise_floors.get(denoise_level, -25)
        # afftdn: noise floor in dB, tracking noise enabled
        filters.append(f"afftdn=nf={nf}:tn=1")
        
    # 3. Speech Clarity & Vocal EQ
    if clarity_boost:
        # Cut muddy low-mid boxiness at 350Hz (-1.5dB)
        filters.append("equalizer=f=350:t=q:w=1.5:g=-1.5")
        # Boost intelligibility presence at 3200Hz (+3.0dB)
        filters.append("equalizer=f=3200:t=q:w=1.2:g=3.0")
        # Gentle de-essing / harshness reduction at 7500Hz (-2.0dB)
        filters.append("equalizer=f=7500:t=q:w=2.0:g=-2.0")
        
    # 4. Speech Normalization & Dynamics Control
    if normalize_speech:
        # speechnorm filter designed specifically for speech dynamic control
        filters.append("speechnorm=e=4:r=0.0001:l=1")
        # Followed by EBU R128 loudness normalization
        filters.append(f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11")
        
    filter_complex = ",".join(filters) if filters else "anull"
    
    in_ext = Path(input_file).suffix.lower()
    out_ext = Path(output_file).suffix.lower()
    is_video = out_ext in [".mp4", ".mkv", ".mov", ".avi", ".webm"]
    
    cmd = [ffmpeg, "-y", "-i", input_file]
    
    if is_video:
        # Keep original video stream, apply filter to audio
        cmd.extend(["-c:v", "copy", "-af", filter_complex, "-c:a", "aac", "-b:a", "192k"])
    else:
        # Audio output
        cmd.extend(["-af", filter_complex])
        if out_ext in [".wav"]:
            cmd.extend(["-c:a", "pcm_s16le", "-ar", "44100"])
        elif out_ext in [".mp3"]:
            cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k"])
        else:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
            
    cmd.append(output_file)
    
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            return False, f"FFmpeg error: {proc.stderr[-400:]}"
        return True, output_file
    except Exception as e:
        return False, str(e)


# ==================== Text Cleaning Engine ====================

RUSSIAN_FILLERS = [
    # Interjections
    r"\b[эЭ][\-—–]*[эЭ]+[\-—–]*[эЭ]*\b",
    r"\b[мМ][\-—–]*[мМ]+[\-—–]*[мМ]*\b",
    r"\b[аА][\-—–]*[аА]+[\-—–]*[аА]*\b",
    r"\b[уУ][\-—–]*[уУ]+[\-—–]*[уУ]*\b",
    r"\b[оО][\-—–]*[оО]+[\-—–]*[оО]*\b",
    # Filler phrases
    r"\b(?:как бы|в общем-то|так сказать|собственно говоря|дело в том, что)\b",
    # Standalone filler words (when used as parasites)
    r"\b(?:типа|короче)\b",
]

ENGLISH_FILLERS = [
    r"\b(?:uh|um|er|ah|eh)\b",
    r"\b(?:you know|sort of|kind of|as a matter of fact)\b",
    r"\b(?:basically|actually|literally)\b",
]


def clean_text(
    text: str,
    language: str = "ru",
    remove_fillers: bool = True,
    remove_stutters: bool = True,
    remove_hallucinations: bool = True,
    fix_punctuation: bool = True
) -> str:
    """
    Clean transcribed speech text by removing filler words, stutters, and hallucinations.
    :param text: Raw text from STT
    :param language: Language code ('ru' or 'en')
    :param remove_fillers: Remove 'эээ', 'ммм', 'типа', 'как бы', etc.
    :param remove_stutters: Remove repeated stuttered words ('я я пошел' -> 'я пошел')
    :param remove_hallucinations: Remove Whisper looped hallucination sentences
    :param fix_punctuation: Polish spacing, punctuation marks and sentence capitalization
    :return: Cleaned polished text
    """
    if not text or not text.strip():
        return ""
        
    res = text
    
    # 1. Hallucination loop removal (repeated identical sentences)
    if remove_hallucinations:
        # Detect sequences of repeated phrases like "phrase. phrase. phrase."
        res = re.sub(r"((?:[A-Za-zА-Яа-яЁё0-9\s,]{4,}[.!?]\s*))\1{2,}", r"\1", res)

    # 2. Filler words removal
    if remove_fillers:
        fillers = RUSSIAN_FILLERS if language.startswith("ru") else ENGLISH_FILLERS
        for pattern in fillers:
            res = re.sub(pattern, "", res, flags=re.IGNORECASE)

    # 3. Stutters & stuttered repetitions
    if remove_stutters:
        # Match repeated words separated by spaces, dots, commas or dashes
        # e.g. "я, я" -> "я", "мы мы" -> "мы", "this this" -> "this"
        res = re.sub(r"\b([а-яёА-ЯЁa-zA-Z]+)(?:[,\s\.\-—–]+)+\1\b", r"\1", res, flags=re.IGNORECASE)
        # Handle word fragments e.g. "п-пошел" -> "пошел"
        res = re.sub(r"\b([а-яёА-ЯЁa-zA-Z])\-([а-яёА-ЯЁa-zA-Z]{2,})\b", r"\2", res, flags=re.IGNORECASE)

    # 4. Punctuation & sentence polishing
    if fix_punctuation:
        # Collapse multiple spaced dots into ellipsis or single period
        res = re.sub(r"(?:\.\s*){3,}", "... ", res)
        # Collapse multiple commas
        res = re.sub(r"(?:,\s*){2,}", ", ", res)
        # Clean comma/semicolon before period/question/exclamation
        res = re.sub(r"[,;]\s*([.!?])", r"\1", res)
        # Clean comma/semicolon right after period/question/exclamation
        res = re.sub(r"([.!?])\s*[,;]", r"\1", res)
        # Normalize spaces around commas
        res = re.sub(r"\s*,\s*", ", ", res)
        # Clean punctuation after ellipsis
        res = re.sub(r"\.\.\.\s*[,;]+", "... ", res)
        # Remove leading comma/punctuation in text and at sentence starts
        res = re.sub(r"(^|[.!?]\s+)[,;\s]+", r"\1", res)
        res = re.sub(r"^[,\s\-—–]+", "", res)
        res = re.sub(r"\s+", " ", res).strip()
        
        # Capitalize start of sentences
        def _capitalize_match(m):
            return m.group(1) + m.group(2).upper()
            
        res = re.sub(r"(^|[.!?]\s+)([а-яёa-z])", _capitalize_match, res)
        
    return res.strip()


def clean_srt(
    input_srt: str,
    output_srt: str,
    language: str = "ru",
    remove_fillers: bool = True,
    remove_stutters: bool = True
) -> Tuple[bool, int, str]:
    """
    Clean SRT subtitle file: remove filler words, drop empty subtitles, and re-number timestamps.
    :param input_srt: Path to source .srt
    :param output_srt: Path to output .srt
    :param language: Language ('ru' or 'en')
    :return: (success: bool, dropped_empty_count: int, message: str)
    """
    if not os.path.exists(input_srt):
        return False, 0, f"File not found: {input_srt}"
        
    try:
        with open(input_srt, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return False, 0, str(e)
        
    # Split into subtitle blocks by double newline
    blocks = re.split(r"\n\s*\n", content.strip())
    cleaned_blocks = []
    dropped_count = 0
    new_index = 1
    
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if len(lines) < 2:
            continue
            
        # Line 0 is usually index number, Line 1 is timing
        if "-->" in lines[0]:
            timing = lines[0]
            text_lines = lines[1:]
        elif "-->" in lines[1]:
            timing = lines[1]
            text_lines = lines[2:]
        else:
            continue
            
        raw_text = " ".join(text_lines)
        cleaned = clean_text(
            raw_text,
            language=language,
            remove_fillers=remove_fillers,
            remove_stutters=remove_stutters,
            remove_hallucinations=True,
            fix_punctuation=True
        )
        
        if not cleaned:
            # Subtitle became empty after filler word removal!
            dropped_count += 1
            continue
            
        cleaned_blocks.append(f"{new_index}\n{timing}\n{cleaned}\n")
        new_index += 1
        
    try:
        with open(output_srt, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_blocks) + "\n")
        return True, dropped_count, f"Processed {len(cleaned_blocks)} subtitles, dropped {dropped_count} empty filler lines."
    except Exception as e:
        return False, dropped_count, str(e)


_GIGAAM_MODEL = None


def get_audio_duration(file_path: str) -> float:
    """Get media duration in seconds via ffprobe or ffmpeg cross-platform."""
    ffprobe_candidates = ["ffprobe", "ffprobe.exe"]
    ffprobe_bin = None
    for cand in ffprobe_candidates:
        p = shutil.which(cand)
        if p:
            ffprobe_bin = p
            break
    if not ffprobe_bin:
        try:
            from videotrans.configure.config import ROOT_DIR
            for cand in [f"{ROOT_DIR}/ffmpeg/ffprobe.exe", f"{ROOT_DIR}/ffprobe.exe"]:
                if os.path.exists(cand):
                    ffprobe_bin = cand
                    break
        except Exception:
            pass
    if not ffprobe_bin:
        ffprobe_bin = "ffprobe"

    try:
        proc = subprocess.run(
            [ffprobe_bin, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return float(proc.stdout.strip())
    except Exception:
        pass
    return 0.0


def transcribe_with_gigaam(
    input_file: str,
    output_srt: Optional[str] = None,
    clean: bool = True,
    model_name: str = "v2_ctc",
    device: Optional[str] = None
) -> Tuple[bool, str, List[Dict]]:
    """
    Transcribe speech using Sber GigaAM model.
    Produces full text and timestamped SRT subtitles, with optional filler word cleaning.
    """
    global _GIGAAM_MODEL
    import tempfile
    try:
        import torch
        import gigaam
    except ImportError:
        return False, "GigaAM is not installed. Please run: uv pip install gigaam", []

    if not os.path.exists(input_file):
        return False, f"Input file not found: {input_file}", []

    # 1. Device selection
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

    # 2. Load model
    try:
        if _GIGAAM_MODEL is None:
            _GIGAAM_MODEL = gigaam.load_model(model_name, device=device)
    except Exception as e:
        return False, f"Failed to load GigaAM model ({model_name}): {e}", []

    # 3. Convert input to 16kHz mono PCM wav
    ffmpeg = get_ffmpeg_path()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_f:
        temp_wav = tmp_f.name

    try:
        cmd = [ffmpeg, "-y", "-i", input_file, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", temp_wav]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            return False, f"FFmpeg audio extraction failed: {res.stderr.decode('utf-8', errors='ignore')[-300:]}", []

        duration = get_audio_duration(temp_wav)

        segments = []
        # Short audio (< 25s): transcribe directly
        if duration > 0 and duration < 25.0:
            text = _GIGAAM_MODEL.transcribe(temp_wav).strip()
            if text:
                segments.append({"start": 0.0, "end": duration, "text": text})
        else:
            # Detect speech/silence segments using FFmpeg silencedetect
            cmd_silence = [
                ffmpeg, "-i", temp_wav,
                "-af", "silencedetect=noise=-30dB:d=0.45",
                "-f", "null", "-"
            ]
            proc = subprocess.run(cmd_silence, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            silence_spans = []
            cur_start = None
            for line in proc.stderr.split("\n"):
                if "silence_start:" in line:
                    m = re.search(r"silence_start:\s*([0-9\.]+)", line)
                    if m:
                        cur_start = float(m.group(1))
                elif "silence_end:" in line and cur_start is not None:
                    m = re.search(r"silence_end:\s*([0-9\.]+)", line)
                    if m:
                        silence_spans.append((cur_start, float(m.group(1))))
                        cur_start = None

            # Invert silences into speech intervals
            speech_spans = []
            prev_end = 0.0
            for s_start, s_end in silence_spans:
                if s_start > prev_end + 0.3:
                    speech_spans.append((prev_end, s_start))
                prev_end = s_end
            if duration > prev_end + 0.3:
                speech_spans.append((prev_end, duration))

            if not speech_spans:
                speech_spans = [(0.0, duration if duration > 0 else 10.0)]

            # Transcribe each segment
            for start_sec, end_sec in speech_spans:
                seg_dur = end_sec - start_sec
                if seg_dur < 0.2:
                    continue
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as chunk_f:
                    chunk_wav = chunk_f.name
                try:
                    subprocess.run(
                        [ffmpeg, "-y", "-ss", str(start_sec), "-t", str(seg_dur), "-i", temp_wav, "-c", "copy", chunk_wav],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    chunk_text = _GIGAAM_MODEL.transcribe(chunk_wav).strip()
                    if chunk_text:
                        segments.append({"start": start_sec, "end": end_sec, "text": chunk_text})
                finally:
                    if os.path.exists(chunk_wav):
                        os.remove(chunk_wav)

        # 4. Clean text if requested
        full_text_list = []
        srt_lines = []
        sub_idx = 1

        for seg in segments:
            t = seg["text"]
            if clean:
                t = clean_text(t, language="ru", remove_fillers=True, remove_stutters=True, remove_hallucinations=True, fix_punctuation=True)
            if not t:
                continue

            full_text_list.append(t)
            start_str = seconds_to_time(seg["start"]).replace(".", ",")
            end_str = seconds_to_time(seg["end"]).replace(".", ",")
            srt_lines.append(f"{sub_idx}\n{start_str} --> {end_str}\n{t}\n")
            sub_idx += 1

        full_text = " ".join(full_text_list)
        srt_content = "\n".join(srt_lines)

        if output_srt:
            with open(output_srt, "w", encoding="utf-8") as f:
                f.write(srt_content + "\n")

        return True, full_text, segments
    except Exception as e:
        return False, str(e), []
    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Voice & Audio Engineering Toolkit for pyVideoTrans")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: enhance
    p_enhance = subparsers.add_parser("enhance", help="Enhance vocal audio: denoise, highpass 80Hz, EQ, normalize")
    p_enhance.add_argument("-i", "--input", required=True, help="Input media file")
    p_enhance.add_argument("-o", "--output", required=True, help="Output media file")
    p_enhance.add_argument("--denoise", default="medium", choices=["none", "light", "medium", "strong"], help="Denoise level")
    p_enhance.add_argument("--no-clarity", action="store_true", help="Disable vocal clarity EQ")
    p_enhance.add_argument("--no-norm", action="store_true", help="Disable speech loudness normalization")

    # Command: trim
    p_trim = subparsers.add_parser("trim", help="Cut audio/video between timestamps")
    p_trim.add_argument("-i", "--input", required=True, help="Input media file")
    p_trim.add_argument("-o", "--output", required=True, help="Output media file")
    p_trim.add_argument("-s", "--start", required=True, help="Start time (e.g. 00:00:15 or 15.5)")
    p_trim.add_argument("-e", "--end", help="End time (e.g. 00:01:30 or 90)")
    p_trim.add_argument("--reencode", action="store_true", help="Re-encode instead of fast stream copy")

    # Command: clean-text
    p_text = subparsers.add_parser("clean-text", help="Clean filler words and stutters from transcript text")
    p_text.add_argument("-t", "--text", required=True, help="Text to clean")
    p_text.add_argument("-l", "--lang", default="ru", choices=["ru", "en"], help="Language")

    # Command: clean-srt
    p_srt = subparsers.add_parser("clean-srt", help="Clean filler words from .srt subtitles file")
    p_srt.add_argument("-i", "--input", required=True, help="Input .srt file")
    p_srt.add_argument("-o", "--output", required=True, help="Output .srt file")
    p_srt.add_argument("-l", "--lang", default="ru", choices=["ru", "en"], help="Language")

    # Command: transcribe (Sber GigaAM)
    p_tr = subparsers.add_parser("transcribe", help="Transcribe Russian speech using Sber GigaAM")
    p_tr.add_argument("-i", "--input", required=True, help="Input audio or video file")
    p_tr.add_argument("-o", "--output-srt", help="Optional output .srt subtitle file path")
    p_tr.add_argument("--no-clean", action="store_true", help="Do not clean filler words from transcript")

    args = parser.parse_args()

    if args.command == "enhance":
        ok, msg = enhance_voice(
            input_file=args.input,
            output_file=args.output,
            denoise_level=args.denoise,
            clarity_boost=not args.no_clarity,
            normalize_speech=not args.no_norm
        )
        print("Success:" if ok else "Error:", msg)

    elif args.command == "trim":
        ok, msg = trim_media(
            input_file=args.input,
            output_file=args.output,
            start_time=args.start,
            end_time=args.end,
            copy_codec=not args.reencode
        )
        print("Success:" if ok else "Error:", msg)

    elif args.command == "clean-text":
        cleaned = clean_text(args.text, language=args.lang)
        print(cleaned)

    elif args.command == "clean-srt":
        ok, count, msg = clean_srt(args.input, args.output, language=args.lang)
        print("Success:" if ok else "Error:", msg)

    elif args.command == "transcribe":
        ok, text, _ = transcribe_with_gigaam(
            input_file=args.input,
            output_srt=args.output_srt,
            clean=not args.no_clean
        )
        if ok:
            print("Transcript:", text)
            if args.output_srt:
                print(f"SRT saved to: {args.output_srt}")
        else:
            print("Transcription failed:", text)

    else:
        parser.print_help()


