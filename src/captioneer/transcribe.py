#!/usr/bin/env python3
"""Transcribe audio from a video file using faster-whisper."""

from faster_whisper import WhisperModel

from captioneer.ui import console, make_progress


def transcribe_video(
    video_path: str, model_size: str = "small", language: str = "auto", verbose: bool = False
) -> tuple[list[dict], str]:
    """
    Transcribe audio from video.
    language: ISO code (e.g. "en", "es") or "auto" to detect automatically.
    Returns (segments, detected_language).
    """
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    lang_arg = None if language == "auto" else language
    segments_gen, info = model.transcribe(video_path, language=lang_arg, task="transcribe")

    prob = f"{info.language_probability:.2f}"
    console.print(f"  [dim]Detected language:[/] [bold]{info.language}[/] [dim](prob {prob})[/]")

    duration = info.duration or 0.0
    result = []

    with make_progress("Transcribing") as progress:
        task = progress.add_task("", total=duration)
        for seg in segments_gen:
            result.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
            progress.update(task, completed=seg.end)
            if verbose:
                console.print(f"  [dim][{seg.start:.1f}s → {seg.end:.1f}s][/] {seg.text.strip()}")

    return result, info.language
