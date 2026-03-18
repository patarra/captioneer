#!/usr/bin/env python3
"""Embed SRT subtitles into a video using ffmpeg: soft track or hardcoded."""
import json
import re
import subprocess
import sys

from captioneer.ui import console, make_progress


def get_duration(video_path: str) -> float:
    """Return video duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_entries", "format=duration",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(json.loads(result.stdout)["format"]["duration"])
    except Exception:
        return 0.0


def embed_subtitles(
    video_path: str, srt_path: str, output_path: str,
    language: str = "spa", duration: float = 0.0,
) -> None:
    """Soft subtitles: pista seleccionable en MKV."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", srt_path,
        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "srt",
        "-metadata:s:s:0", f"language={language}",
        "-metadata:s:s:0", "title=Español",
        "-disposition:s:0", "default",
        output_path,
    ]
    _run_ffmpeg(cmd, duration or get_duration(video_path))


def hardcode_subtitles(
    video_path: str, srt_path: str, output_path: str, duration: float = 0.0,
) -> None:
    """Hard subtitles: quemados en el stream de vídeo. Output: MP4."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy",
        output_path,
    ]
    _run_ffmpeg(cmd, duration or get_duration(video_path))


def _run_ffmpeg(cmd: list[str], duration: float) -> None:
    # -progress pipe:2 makes ffmpeg emit machine-readable progress to stderr
    full_cmd = cmd[:-1] + ["-progress", "pipe:2", "-nostats", cmd[-1]]

    proc = subprocess.Popen(full_cmd, stderr=subprocess.PIPE, text=True)

    time_pattern = re.compile(r"out_time_ms=(\d+)")
    completed = 0.0

    with make_progress("Encoding") as progress:
        task = progress.add_task("", total=max(duration, 1.0))
        for line in proc.stderr:
            m = time_pattern.search(line)
            if m:
                completed = int(m.group(1)) / 1_000_000
                progress.update(task, completed=min(completed, duration))

    proc.wait()
    if proc.returncode != 0:
        console.print("[red]ffmpeg failed[/]", file=sys.stderr)
        raise RuntimeError(f"ffmpeg failed with code {proc.returncode}")
