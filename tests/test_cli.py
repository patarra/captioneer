"""Tests for cli.py — core functions are mocked, CliRunner invokes commands."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from captioneer.cli import app

runner = CliRunner()


# ── fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def video_file(tmp_path):
    f = tmp_path / "video.mp4"
    f.write_bytes(b"fake video")
    return f


@pytest.fixture
def srt_file(tmp_path):
    f = tmp_path / "subs.srt"
    f.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")
    return f


# ── captioneer transcribe ─────────────────────────────────────────────


@patch("captioneer.cli.transcribe_video")
@patch("captioneer.cli.write_srt")
def test_transcribe_command_exits_ok(mock_write, mock_transcribe, video_file):
    mock_transcribe.return_value = ([{"start": 0.0, "end": 1.0, "text": "Hi"}], "en")

    result = runner.invoke(app, ["transcribe", str(video_file)])

    assert result.exit_code == 0


@patch("captioneer.cli.transcribe_video")
@patch("captioneer.cli.write_srt")
def test_transcribe_calls_transcribe_video(mock_write, mock_transcribe, video_file):
    mock_transcribe.return_value = ([], "en")

    runner.invoke(app, ["transcribe", str(video_file), "--model", "medium"])

    mock_transcribe.assert_called_once()
    call_kwargs = mock_transcribe.call_args
    assert call_kwargs[1]["model_size"] == "medium"


@patch("captioneer.cli.transcribe_video")
@patch("captioneer.cli.write_srt")
def test_transcribe_default_output_path(mock_write, mock_transcribe, video_file):
    mock_transcribe.return_value = ([], "en")

    runner.invoke(app, ["transcribe", str(video_file)])

    out_path = mock_write.call_args[0][1]
    assert out_path.endswith(".srt")
    assert "video" in out_path


# ── captioneer translate ──────────────────────────────────────────────


@patch("captioneer.cli.parse_srt")
@patch("captioneer.cli.translate_segments")
@patch("captioneer.cli.write_srt")
def test_translate_command_exits_ok(mock_write, mock_translate, mock_parse, srt_file):
    mock_parse.return_value = [{"start": 0.0, "end": 1.0, "text": "Hello"}]
    mock_translate.return_value = [{"start": 0.0, "end": 1.0, "text": "Hola"}]

    result = runner.invoke(app, ["translate", str(srt_file), "--lang", "es"])

    assert result.exit_code == 0


@patch("captioneer.cli.parse_srt")
@patch("captioneer.cli.translate_segments")
@patch("captioneer.cli.write_srt")
def test_translate_passes_target_lang(mock_write, mock_translate, mock_parse, srt_file):
    mock_parse.return_value = []
    mock_translate.return_value = []

    runner.invoke(app, ["translate", str(srt_file), "--lang", "fr"])

    call_kwargs = mock_translate.call_args[1]
    assert call_kwargs["target"] == "fr"


# ── captioneer burn ───────────────────────────────────────────────────


@patch("captioneer.cli.embed_subtitles")
def test_burn_soft_exits_ok(mock_embed, video_file, srt_file):
    result = runner.invoke(app, ["burn", str(video_file), str(srt_file), "--mode", "soft"])

    assert result.exit_code == 0
    mock_embed.assert_called_once()


@patch("captioneer.cli.hardcode_subtitles")
def test_burn_hard_exits_ok(mock_hard, video_file, srt_file):
    result = runner.invoke(app, ["burn", str(video_file), str(srt_file), "--mode", "hard"])

    assert result.exit_code == 0
    mock_hard.assert_called_once()


@patch("captioneer.cli.embed_subtitles")
def test_burn_soft_output_is_mkv(mock_embed, video_file, srt_file):
    runner.invoke(app, ["burn", str(video_file), str(srt_file), "--mode", "soft"])

    out_path = mock_embed.call_args[0][2]
    assert out_path.endswith(".mkv")


@patch("captioneer.cli.hardcode_subtitles")
def test_burn_hard_output_is_mp4(mock_hard, video_file, srt_file):
    runner.invoke(app, ["burn", str(video_file), str(srt_file), "--mode", "hard"])

    out_path = mock_hard.call_args[0][2]
    assert out_path.endswith(".mp4")


# ── captioneer caption ────────────────────────────────────────────────


@patch("captioneer.cli.transcribe_video")
@patch("captioneer.cli.translate_segments")
@patch("captioneer.cli.write_srt")
@patch("captioneer.cli.embed_subtitles")
@patch("pathlib.Path.unlink")
def test_caption_full_pipeline_exits_ok(mock_unlink, mock_embed, mock_write, mock_tr, mock_tx, video_file):
    mock_tx.return_value = ([{"start": 0.0, "end": 1.0, "text": "Hi"}], "en")
    mock_tr.return_value = [{"start": 0.0, "end": 1.0, "text": "Hola"}]

    result = runner.invoke(app, ["caption", str(video_file), "--lang", "es"])

    assert result.exit_code == 0


@patch("captioneer.cli.transcribe_video")
@patch("captioneer.cli.translate_segments")
@patch("captioneer.cli.write_srt")
@patch("captioneer.cli.hardcode_subtitles")
@patch("pathlib.Path.unlink")
def test_caption_hard_mode_calls_hardcode(mock_unlink, mock_hard, mock_write, mock_tr, mock_tx, video_file):
    mock_tx.return_value = ([{"start": 0.0, "end": 1.0, "text": "Hi"}], "en")
    mock_tr.return_value = [{"start": 0.0, "end": 1.0, "text": "Hola"}]

    result = runner.invoke(app, ["caption", str(video_file), "--lang", "es", "--mode", "hard"])

    assert result.exit_code == 0
    mock_hard.assert_called_once()


@patch("captioneer.cli.transcribe_video")
@patch("captioneer.cli.translate_segments")
@patch("captioneer.cli.write_srt")
@patch("captioneer.cli.embed_subtitles")
def test_caption_cleans_up_tmp_srt(mock_embed, mock_write, mock_translate, mock_transcribe, video_file, tmp_path):
    mock_transcribe.return_value = ([{"start": 0.0, "end": 1.0, "text": "Hi"}], "en")
    mock_translate.return_value = [{"start": 0.0, "end": 1.0, "text": "Hola"}]

    runner.invoke(app, ["caption", str(video_file), "--lang", "es"])

    # tmp srt should not exist after the command (no --keep-srt)
    tmp_srt = video_file.with_name(f"{video_file.stem}.es.tmp.srt")
    assert not tmp_srt.exists()
