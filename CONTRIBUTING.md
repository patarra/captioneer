# Contributing to captioneer

Thanks for your interest in contributing!

## Setup

```bash
git clone https://github.com/patarra/captioneer
cd captioneer
pip install -e .
```

You'll also need `ffmpeg` installed:

```bash
brew install ffmpeg   # macOS
```

## Project structure

```
src/captioneer/
├── cli.py          # Typer commands (transcribe, translate, burn, caption)
├── transcribe.py   # faster-whisper integration
├── translate.py    # deep-translator integration
├── srt_utils.py    # SRT parsing and generation
├── embed.py        # ffmpeg soft/hard subtitle embedding
└── ui.py           # Rich console and progress bars
```

## Making changes

- One feature or fix per pull request
- Keep the modules independent — `transcribe`, `translate` and `embed` should not import from each other
- New CLI options go in `cli.py`; logic goes in the relevant module

## Reporting bugs

Open an issue with:
- The command you ran
- The error output
- Your OS and Python version (`python --version`)
