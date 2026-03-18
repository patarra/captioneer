#!/usr/bin/env python3
"""SRT format utilities: generate and parse subtitle files."""

import re


def seconds_to_srt_time(seconds: float) -> str:
    """Convert float seconds to SRT timestamp: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = min(int(round((seconds - int(seconds)) * 1000)), 999)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def segments_to_srt(segments: list[dict]) -> str:
    """
    Convert list of segments to SRT string.
    segments: [{"start": float, "end": float, "text": str}, ...]
    """
    blocks = []
    for i, seg in enumerate(segments, start=1):
        start = seconds_to_srt_time(seg["start"])
        end = seconds_to_srt_time(seg["end"])
        blocks.append(f"{i}\n{start} --> {end}\n{seg['text']}")
    return "\n\n".join(blocks) + "\n"


def write_srt(segments: list[dict], output_path: str) -> None:
    """Write segments to SRT file."""
    content = segments_to_srt(segments)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SRT written to: {output_path}")


def parse_srt(srt_path: str) -> list[dict]:
    """
    Parse an existing SRT file into segments.
    Returns: [{"start": float, "end": float, "text": str}, ...]
    """
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\n+", content.strip())
    segments = []
    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 3:
            continue
        times = lines[1].split(" --> ")
        segments.append(
            {
                "start": _srt_time_to_seconds(times[0].strip()),
                "end": _srt_time_to_seconds(times[1].strip()),
                "text": " ".join(lines[2:]),
            }
        )
    return segments


def _srt_time_to_seconds(t: str) -> float:
    """Convert SRT timestamp HH:MM:SS,mmm to float seconds."""
    t = t.replace(",", ".")
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)
