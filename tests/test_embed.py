"""Tests for embed.py — subprocess is mocked."""

import json
from unittest.mock import MagicMock, patch

import pytest


def _make_proc(returncode=0, stderr_lines=None):
    proc = MagicMock()
    proc.returncode = returncode
    proc.stderr = iter(stderr_lines or [])
    proc.wait.return_value = None
    return proc


# ── get_duration ──────────────────────────────────────────────────────


@patch("captioneer.embed.subprocess.run")
def test_get_duration_returns_float(mock_run):
    mock_run.return_value.stdout = json.dumps({"format": {"duration": "123.456"}})

    from captioneer.embed import get_duration

    assert get_duration("video.mp4") == pytest.approx(123.456)


@patch("captioneer.embed.subprocess.run")
def test_get_duration_returns_zero_on_error(mock_run):
    mock_run.return_value.stdout = "{}"  # missing key

    from captioneer.embed import get_duration

    assert get_duration("video.mp4") == 0.0


# ── embed_subtitles (soft) ────────────────────────────────────────────


@patch("captioneer.embed.subprocess.Popen")
def test_embed_subtitles_uses_mkv_copy(mock_popen):
    mock_popen.return_value = _make_proc()

    from captioneer.embed import embed_subtitles

    embed_subtitles("video.mp4", "subs.srt", "output.mkv", duration=10.0)

    cmd = mock_popen.call_args[0][0]
    assert "ffmpeg" in cmd
    assert "-c:v" in cmd
    assert "copy" in cmd
    assert "-c:s" in cmd
    assert "srt" in cmd
    assert "output.mkv" in cmd


@patch("captioneer.embed.subprocess.Popen")
def test_embed_subtitles_sets_language_metadata(mock_popen):
    mock_popen.return_value = _make_proc()

    from captioneer.embed import embed_subtitles

    embed_subtitles("video.mp4", "subs.srt", "out.mkv", language="eng", duration=10.0)

    cmd = mock_popen.call_args[0][0]
    assert any("language=eng" in arg for arg in cmd)


# ── hardcode_subtitles (hard) ─────────────────────────────────────────


@patch("captioneer.embed.subprocess.Popen")
def test_hardcode_subtitles_uses_vf_filter(mock_popen):
    mock_popen.return_value = _make_proc()

    from captioneer.embed import hardcode_subtitles

    hardcode_subtitles("video.mp4", "subs.srt", "output.mp4", duration=10.0)

    cmd = mock_popen.call_args[0][0]
    assert "-vf" in cmd
    assert any("subtitles=" in arg for arg in cmd)
    assert "output.mp4" in cmd


# ── ffmpeg failure ────────────────────────────────────────────────────


@patch("captioneer.embed.subprocess.Popen")
def test_embed_raises_on_ffmpeg_failure(mock_popen):
    mock_popen.return_value = _make_proc(returncode=1)

    from captioneer.embed import embed_subtitles

    with pytest.raises(RuntimeError, match="ffmpeg failed"):
        embed_subtitles("video.mp4", "subs.srt", "out.mkv", duration=10.0)


@patch("captioneer.embed.subprocess.Popen")
def test_hardcode_raises_on_ffmpeg_failure(mock_popen):
    mock_popen.return_value = _make_proc(returncode=1)

    from captioneer.embed import hardcode_subtitles

    with pytest.raises(RuntimeError, match="ffmpeg failed"):
        hardcode_subtitles("video.mp4", "subs.srt", "out.mp4", duration=10.0)
