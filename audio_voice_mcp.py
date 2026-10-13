#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Context Protocol (MCP) Server for Voice & Audio Engineering:
- enhance_voice: Denoising, high-pass rumble cut, speech clarity EQ, loudness normalization.
- trim_media: Fast lossless or high-quality cut of audio/video.
- clean_text: Removes filler words, interjections, stutters, and hallucinations.
- clean_srt: Cleans SRT subtitles, drops empty lines, re-indexes timestamps.

Runs over stdio (JSON-RPC 2.0).
Zero third-party dependencies required.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR / "videotrans" / "util"))

from voice_toolkit import trim_media, enhance_voice, clean_text, clean_srt, transcribe_with_gigaam


TOOLS = [
    {
        "name": "enhance_voice",
        "description": "Professional vocal enhancement: adaptive FFT denoiser, 80Hz rumble cut, speech presence EQ (3.2kHz boost & de-box), and broadcast loudness normalization (EBU R128).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Absolute path to source audio or video file"
                },
                "output_file": {
                    "type": "string",
                    "description": "Optional output path. If omitted, saves with '_enhanced' suffix in same folder."
                },
                "denoise_level": {
                    "type": "string",
                    "enum": ["none", "light", "medium", "strong"],
                    "default": "medium",
                    "description": "Noise reduction strength. 'medium' (-25dB) is recommended for most voices."
                },
                "clarity_boost": {
                    "type": "boolean",
                    "default": True,
                    "description": "Boost speech presence and intelligibility frequency bands"
                },
                "normalize_speech": {
                    "type": "boolean",
                    "default": True,
                    "description": "Normalize vocal loudness to broadcast standards (EBU R128 / -16 LUFS)"
                }
            },
            "required": ["input_file"]
        }
    },
    {
        "name": "trim_media",
        "description": "Cut or trim audio or video file between start_time and end_time. Supports lossless stream copy or re-encoding.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Absolute path to source audio or video file"
                },
                "output_file": {
                    "type": "string",
                    "description": "Destination file path"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start timestamp (e.g. '00:00:15', '15.5', '01:20')"
                },
                "end_time": {
                    "type": "string",
                    "description": "End timestamp (e.g. '00:01:45', '105.0')"
                },
                "lossless": {
                    "type": "boolean",
                    "default": True,
                    "description": "If True, performs fast stream copy (-c copy) without quality loss or re-encoding"
                }
            },
            "required": ["input_file", "output_file", "start_time"]
        }
    },
    {
        "name": "clean_transcript_text",
        "description": "Cleans speech transcription text by removing filler words ('эээ', 'типа', 'как бы', 'короче'), interjections, stutters/repetitions, and fixing punctuation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Raw transcribed text to clean"
                },
                "language": {
                    "type": "string",
                    "enum": ["ru", "en"],
                    "default": "ru",
                    "description": "Language of the text ('ru' for Russian, 'en' for English)"
                },
                "remove_fillers": {
                    "type": "boolean",
                    "default": True,
                    "description": "Remove parasite words and interjections"
                },
                "remove_stutters": {
                    "type": "boolean",
                    "default": True,
                    "description": "Remove stuttered word repetitions ('я я пошел' -> 'я пошел')"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "clean_srt_subtitles",
        "description": "Cleans SRT subtitle files: removes parasite filler words, drops subtitle lines that became empty, and re-indexes all subtitles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_srt": {
                    "type": "string",
                    "description": "Path to input .srt file"
                },
                "output_srt": {
                    "type": "string",
                    "description": "Path to output cleaned .srt file"
                },
                "language": {
                    "type": "string",
                    "enum": ["ru", "en"],
                    "default": "ru",
                    "description": "Language ('ru' or 'en')"
                }
            },
            "required": ["input_srt", "output_srt"]
        }
    },
    {
        "name": "transcribe_audio_gigaam",
        "description": "Transcribe Russian speech from audio or video using Sber GigaAM (SOTA Russian ASR). Produces clean text and optional timestamped .srt subtitles without Whisper hallucinations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to audio or video file"
                },
                "output_srt": {
                    "type": "string",
                    "description": "Optional path to save generated .srt subtitles"
                },
                "clean_fillers": {
                    "type": "boolean",
                    "default": True,
                    "description": "Clean parasite filler words ('эээ', 'типа', 'как бы', etc.)"
                }
            },
            "required": ["input_file"]
        }
    }
]


def handle_tool_call(name: str, args: dict) -> dict:
    if name == "enhance_voice":
        inp = args["input_file"]
        if not os.path.exists(inp):
            return {"error": f"File not found: {inp}"}
            
        outp = args.get("output_file")
        if not outp:
            p = Path(inp)
            outp = str(p.parent / f"{p.stem}_enhanced{p.suffix}")
            
        denoise_level = args.get("denoise_level", "medium")
        clarity_boost = args.get("clarity_boost", True)
        normalize_speech = args.get("normalize_speech", True)
        
        ok, msg = enhance_voice(
            input_file=inp,
            output_file=outp,
            denoise_level=denoise_level,
            clarity_boost=clarity_boost,
            normalize_speech=normalize_speech
        )
        if ok:
            return {"success": True, "output_file": outp, "message": "Voice enhanced and denoised successfully."}
        return {"success": False, "error": msg}

    elif name == "trim_media":
        inp = args["input_file"]
        outp = args["output_file"]
        start_t = args["start_time"]
        end_t = args.get("end_time")
        lossless = args.get("lossless", True)
        
        ok, msg = trim_media(
            input_file=inp,
            output_file=outp,
            start_time=start_t,
            end_time=end_t,
            copy_codec=lossless
        )
        if ok:
            return {"success": True, "output_file": outp, "message": "Media trimmed successfully."}
        return {"success": False, "error": msg}

    elif name == "clean_transcript_text":
        txt = args["text"]
        lang = args.get("language", "ru")
        remove_fillers = args.get("remove_fillers", True)
        remove_stutters = args.get("remove_stutters", True)
        
        cleaned = clean_text(
            text=txt,
            language=lang,
            remove_fillers=remove_fillers,
            remove_stutters=remove_stutters,
            remove_hallucinations=True,
            fix_punctuation=True
        )
        return {"cleaned_text": cleaned}

    elif name == "clean_srt_subtitles":
        inp = args["input_srt"]
        outp = args["output_srt"]
        lang = args.get("language", "ru")
        
        ok, dropped, msg = clean_srt(
            input_srt=inp,
            output_srt=outp,
            language=lang,
            remove_fillers=True,
            remove_stutters=True
        )
        if ok:
            return {"success": True, "output_srt": outp, "dropped_empty_subtitles": dropped, "message": msg}
        return {"success": False, "error": msg}

    elif name == "transcribe_audio_gigaam":
        inp = args["input_file"]
        out_srt = args.get("output_srt")
        clean_f = args.get("clean_fillers", True)

        ok, text, segments = transcribe_with_gigaam(
            input_file=inp,
            output_srt=out_srt,
            clean=clean_f
        )
        if ok:
            res_dict = {
                "success": True,
                "transcript": text,
                "segments_count": len(segments)
            }
            if out_srt:
                res_dict["output_srt"] = out_srt
            return res_dict
        return {"success": False, "error": text}

    return {"error": f"Unknown tool: {name}"}


def main():
    """Main JSON-RPC stdio event loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "audio-voice-toolkit",
                        "version": "1.0.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS}
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            result_data = handle_tool_call(name, args)
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(result_data, ensure_ascii=False, indent=2)}
                    ]
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "ping":
            res = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        else:
            if msg_id is not None:
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    main()
