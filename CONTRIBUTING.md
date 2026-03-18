# Contributing to captioneer

Thanks for your interest in contributing!

## Setup

```bash
git clone https://github.com/patarra/captioneer
cd captioneer
uv sync
```

You'll also need `ffmpeg` and Python 3.10+ installed.

**macOS**
```bash
brew install python ffmpeg     # Homebrew
port install python313 ffmpeg  # MacPorts
```

**Ubuntu / Debian**
```bash
sudo apt install python3 python3-pip ffmpeg
```

**Arch**
```bash
sudo pacman -S python ffmpeg
```

**Gentoo**
```bash
sudo emerge --ask dev-lang/python media-video/ffmpeg
```

Then install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Running tests

```bash
uv run pytest
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
