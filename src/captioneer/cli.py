#!/usr/bin/env python3
"""
captioneer — CLI de subtítulos automáticos.

  captioneer transcribe video.mp4
  captioneer translate subs.srt --lang es
  captioneer burn video.mp4 subs.srt --mode hard
  captioneer caption video.mp4 --lang es --mode soft
"""

from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from captioneer.embed import embed_subtitles, hardcode_subtitles
from captioneer.srt_utils import parse_srt, write_srt
from captioneer.transcribe import transcribe_video
from captioneer.translate import translate_segments
from captioneer.ui import console, print_done, print_header, print_info, print_step

app = typer.Typer(
    name="captioneer",
    help="Transcribe, translate and embed subtitles in videos.",
    no_args_is_help=True,
)


class WhisperModel(str, Enum):
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large-v3"


class BurnMode(str, Enum):
    hard = "hard"
    soft = "soft"


# ── captioneer transcribe ─────────────────────────────────────────────


@app.command()
def transcribe(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output SRT file (default: <video>.srt)"),
    model: WhisperModel = typer.Option(WhisperModel.small, "--model", "-m", help="Whisper model size"),
    source_lang: str = typer.Option("auto", "--source-lang", "-s", help="Source language code or 'auto' to detect"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print each segment as it's processed"),
):
    """Transcribe video audio to SRT in the original language."""
    out = output or video.with_suffix(".srt")

    print_header("captioneer transcribe", f"{video.name}  →  {out.name}")
    print_info("Model", model.value)
    print_info("Source lang", source_lang)
    console.print()

    segments, detected = transcribe_video(str(video), model_size=model.value, language=source_lang, verbose=verbose)
    print_info("Segments", str(len(segments)))
    write_srt(segments, str(out))
    print_done(str(out))


# ── captioneer translate ──────────────────────────────────────────────


@app.command()
def translate(
    srt: Path = typer.Argument(..., help="Input SRT file", exists=True),
    lang: str = typer.Option("es", "--lang", "-l", help="Target language code (e.g. es, fr, de)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output SRT file (default: <srt>.<lang>.srt)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print each segment as it's translated"),
):
    """Translate an existing SRT file to another language."""
    out = output or srt.with_suffix("").with_suffix(f".{lang}.srt")

    print_header("captioneer translate", f"{srt.name}  →  {out.name}")
    print_info("Target lang", lang)
    console.print()

    segments = parse_srt(str(srt))
    translated = translate_segments(segments, target=lang, verbose=verbose)
    write_srt(translated, str(out))
    print_done(str(out))


# ── captioneer burn ───────────────────────────────────────────────────


@app.command()
def burn(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    srt: Path = typer.Argument(..., help="Input SRT subtitle file", exists=True),
    mode: BurnMode = typer.Option(BurnMode.soft, "--mode", help="soft: selectable track (MKV) | hard: burned-in (MP4)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output video file"),
):
    """Embed subtitles into a video as soft track (MKV) or burned-in (MP4)."""
    if output:
        out = output
    elif mode == BurnMode.hard:
        out = video.with_name(f"{video.stem}.hard.mp4")
    else:
        out = video.with_name(f"{video.stem}.soft.mkv")

    print_header("captioneer burn", f"{video.name}  →  {out.name}")
    print_info("Mode", mode.value)
    console.print()

    if mode == BurnMode.hard:
        hardcode_subtitles(str(video), str(srt), str(out))
    else:
        embed_subtitles(str(video), str(srt), str(out))
    print_done(str(out))


# ── captioneer caption ────────────────────────────────────────────────


@app.command()
def caption(
    video: Path = typer.Argument(..., help="Input video file", exists=True),
    lang: str = typer.Option("es", "--lang", "-l", help="Target language code (default: es)"),
    mode: BurnMode = typer.Option(BurnMode.soft, "--mode", help="soft: selectable track (MKV) | hard: burned-in (MP4)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output video file"),
    model: WhisperModel = typer.Option(WhisperModel.small, "--model", "-m", help="Whisper model size"),
    source_lang: str = typer.Option("auto", "--source-lang", "-s", help="Source language code or 'auto' to detect"),
    keep_srt: bool = typer.Option(False, "--keep-srt", help="Keep the intermediate SRT file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print each segment as it's processed"),
):
    """Full pipeline: transcribe → translate → burn subtitles into video."""
    ext = "mp4" if mode == BurnMode.hard else "mkv"
    out = output or video.with_name(f"{video.stem}.{lang}.{mode.value}.{ext}")
    srt_path = video.with_name(f"{video.stem}.{lang}.tmp.srt")

    print_header(
        "captioneer caption",
        f"{video.name}  →  {out.name}\n[dim]{source_lang} → {lang}  |  {mode.value}  |  {model.value}[/dim]",
    )
    console.print()

    print_step(1, 3, "Transcribing...")
    segments, detected = transcribe_video(str(video), model_size=model.value, language=source_lang, verbose=verbose)
    print_info("Detected", detected)
    print_info("Segments", str(len(segments)))

    print_step(2, 3, "Translating...")
    translated = translate_segments(segments, source=detected, target=lang, verbose=verbose)
    write_srt(translated, str(srt_path))

    print_step(3, 3, "Burning subtitles...")
    duration = segments[-1]["end"] if segments else 0.0
    if mode == BurnMode.hard:
        hardcode_subtitles(str(video), str(srt_path), str(out), duration=duration)
    else:
        embed_subtitles(str(video), str(srt_path), str(out), duration=duration)

    if not keep_srt:
        srt_path.unlink()

    print_done(str(out))


if __name__ == "__main__":
    app()
