"""Tests for srt_utils.py — pure functions, no external dependencies."""
import textwrap
import tempfile
import os

import pytest

from captioneer.srt_utils import (
    seconds_to_srt_time,
    segments_to_srt,
    parse_srt,
    write_srt,
    _srt_time_to_seconds,
)


# ── seconds_to_srt_time ───────────────────────────────────────────────

def test_seconds_to_srt_time_zero():
    assert seconds_to_srt_time(0.0) == "00:00:00,000"

def test_seconds_to_srt_time_whole_seconds():
    assert seconds_to_srt_time(61.0) == "00:01:01,000"

def test_seconds_to_srt_time_with_millis():
    assert seconds_to_srt_time(3723.5) == "01:02:03,500"

def test_seconds_to_srt_time_millis_capped_at_999():
    # Even if rounding would give 1000, it must be capped at 999
    assert seconds_to_srt_time(1.9999) == "00:00:01,999"

def test_seconds_to_srt_time_hours():
    assert seconds_to_srt_time(3600.0) == "01:00:00,000"


# ── _srt_time_to_seconds ──────────────────────────────────────────────

def test_srt_time_to_seconds_zero():
    assert _srt_time_to_seconds("00:00:00,000") == 0.0

def test_srt_time_to_seconds_with_millis():
    assert _srt_time_to_seconds("01:02:03,500") == pytest.approx(3723.5)

def test_srt_time_to_seconds_whole():
    assert _srt_time_to_seconds("00:01:01,000") == pytest.approx(61.0)


# ── round-trip ────────────────────────────────────────────────────────

def test_round_trip_timestamp():
    for s in [0.0, 61.0, 3723.5, 3600.0]:
        assert _srt_time_to_seconds(seconds_to_srt_time(s)) == pytest.approx(s, abs=0.001)


# ── segments_to_srt ───────────────────────────────────────────────────

def test_segments_to_srt_single():
    segments = [{"start": 0.0, "end": 1.5, "text": "Hello"}]
    result = segments_to_srt(segments)
    assert result == "1\n00:00:00,000 --> 00:00:01,500\nHello\n"

def test_segments_to_srt_multiple():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "First"},
        {"start": 2.0, "end": 3.0, "text": "Second"},
    ]
    result = segments_to_srt(segments)
    assert "1\n" in result
    assert "2\n" in result
    assert "First" in result
    assert "Second" in result
    assert " --> " in result

def test_segments_to_srt_numbering():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "A"},
        {"start": 1.0, "end": 2.0, "text": "B"},
        {"start": 2.0, "end": 3.0, "text": "C"},
    ]
    result = segments_to_srt(segments)
    lines = result.strip().split("\n\n")
    assert lines[0].startswith("1\n")
    assert lines[1].startswith("2\n")
    assert lines[2].startswith("3\n")


# ── parse_srt ─────────────────────────────────────────────────────────

def test_parse_srt_single_block(tmp_path):
    content = "1\n00:00:00,000 --> 00:00:01,500\nHello\n"
    srt_file = tmp_path / "test.srt"
    srt_file.write_text(content, encoding="utf-8")

    segments = parse_srt(str(srt_file))
    assert len(segments) == 1
    assert segments[0]["text"] == "Hello"
    assert segments[0]["start"] == pytest.approx(0.0)
    assert segments[0]["end"] == pytest.approx(1.5)

def test_parse_srt_multiple_blocks(tmp_path):
    content = textwrap.dedent("""\
        1
        00:00:00,000 --> 00:00:01,000
        First

        2
        00:00:02,000 --> 00:00:03,000
        Second
    """)
    srt_file = tmp_path / "test.srt"
    srt_file.write_text(content, encoding="utf-8")

    segments = parse_srt(str(srt_file))
    assert len(segments) == 2
    assert segments[0]["text"] == "First"
    assert segments[1]["text"] == "Second"

def test_parse_srt_preserves_timestamps(tmp_path):
    content = "1\n01:02:03,500 --> 01:02:05,000\nText\n"
    srt_file = tmp_path / "test.srt"
    srt_file.write_text(content, encoding="utf-8")

    segments = parse_srt(str(srt_file))
    assert segments[0]["start"] == pytest.approx(3723.5)
    assert segments[0]["end"] == pytest.approx(3725.0)


# ── write_srt + parse_srt round-trip ─────────────────────────────────

def test_write_and_parse_round_trip(tmp_path):
    original = [
        {"start": 0.0, "end": 1.5, "text": "Hello"},
        {"start": 2.0, "end": 3.0, "text": "World"},
    ]
    srt_file = str(tmp_path / "output.srt")
    write_srt(original, srt_file)
    parsed = parse_srt(srt_file)

    assert len(parsed) == len(original)
    for orig, result in zip(original, parsed):
        assert result["text"] == orig["text"]
        assert result["start"] == pytest.approx(orig["start"], abs=0.001)
        assert result["end"] == pytest.approx(orig["end"], abs=0.001)
