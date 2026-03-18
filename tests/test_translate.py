"""Tests for translate.py — GoogleTranslator is mocked."""

from unittest.mock import MagicMock, patch

SEGMENTS = [
    {"start": 0.0, "end": 1.0, "text": "Hello"},
    {"start": 1.0, "end": 2.0, "text": "World"},
]


def _mock_translator(translations):
    """Return a mock GoogleTranslator that yields translations in order."""
    translator = MagicMock()
    translator.translate.side_effect = translations
    return translator


# ── tests ─────────────────────────────────────────────────────────────


@patch("captioneer.translate.GoogleTranslator")
def test_translates_each_segment(mock_cls):
    mock_cls.return_value = _mock_translator(["Hola", "Mundo"])

    from captioneer.translate import translate_segments

    result = translate_segments(SEGMENTS, source="en", target="es")

    assert result[0]["text"] == "Hola"
    assert result[1]["text"] == "Mundo"


@patch("captioneer.translate.GoogleTranslator")
def test_preserves_timestamps(mock_cls):
    mock_cls.return_value = _mock_translator(["Hola", "Mundo"])

    from captioneer.translate import translate_segments

    result = translate_segments(SEGMENTS, source="en", target="es")

    assert result[0]["start"] == 0.0
    assert result[0]["end"] == 1.0
    assert result[1]["start"] == 1.0
    assert result[1]["end"] == 2.0


@patch("captioneer.translate.GoogleTranslator")
def test_falls_back_to_original_on_error(mock_cls):
    translator = MagicMock()
    translator.translate.side_effect = [Exception("network error"), "Mundo"]
    mock_cls.return_value = translator

    from captioneer.translate import translate_segments

    result = translate_segments(SEGMENTS, source="en", target="es")

    assert result[0]["text"] == "Hello"  # original kept
    assert result[1]["text"] == "Mundo"


@patch("captioneer.translate.GoogleTranslator")
def test_uses_correct_source_and_target(mock_cls):
    mock_cls.return_value = _mock_translator(["Bonjour", "Monde"])

    from captioneer.translate import translate_segments

    translate_segments(SEGMENTS, source="en", target="fr")

    mock_cls.assert_called_once_with(source="en", target="fr")


@patch("captioneer.translate.GoogleTranslator")
def test_returns_same_number_of_segments(mock_cls):
    mock_cls.return_value = _mock_translator(["A", "B"])

    from captioneer.translate import translate_segments

    result = translate_segments(SEGMENTS)

    assert len(result) == len(SEGMENTS)


@patch("captioneer.translate.GoogleTranslator")
def test_empty_input_returns_empty(mock_cls):
    mock_cls.return_value = _mock_translator([])

    from captioneer.translate import translate_segments

    result = translate_segments([])

    assert result == []
