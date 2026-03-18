"""Tests for transcribe.py — WhisperModel is mocked."""

from unittest.mock import MagicMock, patch

# ── helpers ───────────────────────────────────────────────────────────


def _make_segment(start, end, text):
    seg = MagicMock()
    seg.start = start
    seg.end = end
    seg.text = f"  {text}  "  # intentional whitespace — should be stripped
    return seg


def _make_model(segments, language="en", language_probability=0.99, duration=10.0):
    info = MagicMock()
    info.language = language
    info.language_probability = language_probability
    info.duration = duration

    model = MagicMock()
    model.transcribe.return_value = (iter(segments), info)
    return model


# ── tests ─────────────────────────────────────────────────────────────


@patch("captioneer.transcribe.WhisperModel")
def test_returns_segments_and_language(mock_cls):
    raw = [_make_segment(0.0, 1.0, "Hello"), _make_segment(1.0, 2.0, "World")]
    mock_cls.return_value = _make_model(raw, language="en")

    from captioneer.transcribe import transcribe_video

    segments, lang = transcribe_video("video.mp4")

    assert lang == "en"
    assert len(segments) == 2
    assert segments[0] == {"start": 0.0, "end": 1.0, "text": "Hello"}
    assert segments[1] == {"start": 1.0, "end": 2.0, "text": "World"}


@patch("captioneer.transcribe.WhisperModel")
def test_strips_whitespace_from_text(mock_cls):
    raw = [_make_segment(0.0, 1.0, "  padded  ")]
    mock_cls.return_value = _make_model(raw)

    from captioneer.transcribe import transcribe_video

    segments, _ = transcribe_video("video.mp4")

    assert segments[0]["text"] == "padded"


@patch("captioneer.transcribe.WhisperModel")
def test_uses_correct_model_size(mock_cls):
    mock_cls.return_value = _make_model([])

    from captioneer.transcribe import transcribe_video

    transcribe_video("video.mp4", model_size="medium")

    mock_cls.assert_called_once_with("medium", device="cpu", compute_type="int8")


@patch("captioneer.transcribe.WhisperModel")
def test_auto_language_passes_none(mock_cls):
    model = _make_model([])
    mock_cls.return_value = model

    from captioneer.transcribe import transcribe_video

    transcribe_video("video.mp4", language="auto")

    model.transcribe.assert_called_once_with("video.mp4", language=None, task="transcribe")


@patch("captioneer.transcribe.WhisperModel")
def test_explicit_language_is_passed(mock_cls):
    model = _make_model([])
    mock_cls.return_value = model

    from captioneer.transcribe import transcribe_video

    transcribe_video("video.mp4", language="es")

    model.transcribe.assert_called_once_with("video.mp4", language="es", task="transcribe")


@patch("captioneer.transcribe.WhisperModel")
def test_empty_video_returns_empty_segments(mock_cls):
    mock_cls.return_value = _make_model([], duration=0.0)

    from captioneer.transcribe import transcribe_video

    segments, _ = transcribe_video("video.mp4")

    assert segments == []
