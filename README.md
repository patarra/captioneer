# captioneer

Automatically transcribe, translate and embed subtitles in any video — from the command line.

```
captioneer caption lecture.mp4 --lang es --mode hard
```

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/)

**macOS**
```bash
brew install ffmpeg        # Homebrew
port install ffmpeg        # MacPorts
```

**Linux**
```bash
sudo apt install ffmpeg                  # Ubuntu / Debian
sudo pacman -S ffmpeg                    # Arch
sudo emerge --ask media-video/ffmpeg     # Gentoo
```

## Installation

```bash
uv add captioneer
# or: pip install captioneer
```

## Usage

### Full pipeline — transcribe → translate → embed

```bash
captioneer caption video.mp4 --lang es
```

Output: `video.es.soft.mkv` with selectable Spanish subtitles.

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--lang` / `-l` | `es` | Target language code (`es`, `fr`, `de`, `ja`…) |
| `--mode` | `soft` | `soft` — selectable track (MKV) · `hard` — burned-in (MP4, works on iPhone) |
| `--model` / `-m` | `small` | Whisper model size: `tiny` `base` `small` `medium` `large-v3` |
| `--source-lang` / `-s` | `auto` | Source language, or `auto` to detect automatically |
| `--output` / `-o` | auto | Custom output path |
| `--keep-srt` | off | Keep the intermediate SRT file |
| `--verbose` / `-v` | off | Print each segment as it's processed |

**Examples:**

```bash
# Burned-in subtitles, compatible with iPhone native player
captioneer caption video.mp4 --lang es --mode hard

# Force English as source, French as target, large model
captioneer caption video.mp4 --lang fr --source-lang en --model large-v3

# Keep the generated SRT file
captioneer caption video.mp4 --lang es --keep-srt
```

**Auto output naming:**

| Mode | Output |
|------|--------|
| `--mode soft` | `video.es.soft.mkv` |
| `--mode hard` | `video.es.hard.mp4` |

---

### Individual commands

Use each step independently if you need more control.

#### `transcribe` — audio to SRT

```bash
captioneer transcribe video.mp4
# → video.srt

captioneer transcribe video.mp4 --output subtitles.srt --model medium
```

#### `translate` — translate an existing SRT

```bash
captioneer translate subtitles.srt --lang es
# → subtitles.es.srt

captioneer translate subtitles.srt --lang fr --output subtitles.fr.srt
```

#### `burn` — embed subtitles into video

```bash
# Soft subtitles (selectable track, MKV)
captioneer burn video.mp4 subtitles.es.srt --mode soft
# → video.soft.mkv

# Hard subtitles (burned-in, MP4)
captioneer burn video.mp4 subtitles.es.srt --mode hard
# → video.hard.mp4
```

---

## Soft vs Hard subtitles

| | Soft | Hard |
|---|---|---|
| Format | MKV | MP4 |
| Toggle on/off | ✓ | ✗ |
| iPhone native player | ✗ | ✓ |
| VLC / Infuse | ✓ | ✓ |
| Re-encodes video | No (fast) | Yes (slower) |

## Whisper model sizes

| Model | Speed | Quality | VRAM |
|-------|-------|---------|------|
| `tiny` | fastest | lowest | ~1 GB |
| `base` | fast | low | ~1 GB |
| `small` | balanced | good | ~2 GB |
| `medium` | slow | better | ~5 GB |
| `large-v3` | slowest | best | ~10 GB |

`small` is the default and works well for most content. Use `large-v3` for difficult audio, strong accents or technical content.

## License

MIT — see [LICENSE](LICENSE).
