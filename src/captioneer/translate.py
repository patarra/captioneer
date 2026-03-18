#!/usr/bin/env python3
"""Translate subtitle segments from one language to another."""
from deep_translator import GoogleTranslator

from captioneer.ui import console, make_progress


def translate_segments(
    segments: list[dict], source: str = "en", target: str = "es", verbose: bool = False
) -> list[dict]:
    """
    Translate text in each segment.
    Returns new list with 'text' replaced by translated text.
    Preserves start/end timestamps unchanged.
    """
    translator = GoogleTranslator(source=source, target=target)
    translated = []
    total = len(segments)

    with make_progress("Translating") as progress:
        task = progress.add_task("", total=total)
        for i, seg in enumerate(segments, start=1):
            text = seg["text"]
            try:
                translated_text = translator.translate(text)
            except Exception as e:
                console.print(f"  [yellow]WARNING segment {i}: {e} — keeping original[/]")
                translated_text = text

            if verbose:
                console.print(f"  [dim][{i}/{total}][/] {text!r} [dim]→[/] {translated_text!r}")

            translated.append({"start": seg["start"], "end": seg["end"], "text": translated_text})
            progress.update(task, completed=i)

    return translated
