# VibeVoice Docker CLI

A tiny, Dockerized CLI that pipes text to Microsoft **VibeVoice** TTS and streams audio directly to your audio player or stdout.

## Installation

### Quick Installation (Recommended)

Install with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/fwdslsh/voice/main/install.sh | bash
```

This installer will:
- Check Docker installation and status
- Build the VibeVoice Docker image
- Install the `vibevoice` command to your PATH
- Verify installation with an audio test

### Manual Installation

If you prefer to install manually:

## Requirements
- Docker
- (Optional) NVIDIA GPU + NVIDIA Container Toolkit (Linux) for fast inference
- A host audio player, one of:
  - Linux: `ffplay` (ffmpeg), `aplay`, `paplay`, or `play` (sox)
  - macOS: `afplay` (built-in) or `ffplay`

## Build

```bash
docker build -t vibevoice:local .
```

### Install wrapper on your PATH

```bash
mkdir -p ~/.local/bin
cp scripts/vibevoice ~/.local/bin/vibevoice
chmod +x ~/.local/bin/vibevoice
# Add ~/.local/bin to your PATH if needed:
# echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Usage

```bash
# A) stdin (streams audio directly to your audio player)
echo "Hello from VibeVoice." | vibevoice

# B) literal text 
vibevoice --text "Shipping the demo is the best spec."

# C) save to file instead of playing
echo "Save this audio" | vibevoice --outfile my_audio.wav

# D) pipe to file or another program
echo "Pipe this audio" | vibevoice > output.wav
echo "Process audio" | vibevoice | ffmpeg -i - -f mp3 output.mp3

# E) choose model / speaker with command line options
vibevoice --speaker "Alice" --text "Using a specific speaker."
vibevoice --speaker "Bob" --text "Different speaker, same model."

# F) choose model / speaker with environment variables
VIBEVOICE_MODEL="microsoft/VibeVoice-1.5B" \
VIBEVOICE_SPEAKER="Alice" \
  vibevoice --text "Using environment variables for model and speaker."
```

> The default model (microsoft/VibeVoice-1.5B) is preloaded in the container for fast startup.  
> If no audio player is found, WAV data is output to stdout so you can pipe it to files or other programs.

## Notes

- Everything runs in Docker; your host only needs an audio player.
- The default model (microsoft/VibeVoice-1.5B) is preloaded during build for fast startup.
- A Hugging Face cache is mounted at `~/.cache/huggingface` to persist model data across runs.
- GPU is auto-enabled when `nvidia-smi` exists; otherwise it runs on CPU (slower).
- Audio streams directly from container to your audio player - no temporary files by default.
- You can save to files using `--outfile` or by redirecting stdout: `vibevoice > output.wav`

---

## Quick start (copy/paste)

```bash
# 1) create the project
mkdir -p vibevoice-docker-cli/scripts
cd vibevoice-docker-cli

# 2) create files from the snippets above (Dockerfile, vv_tts.py, scripts/vibevoice, .gitignore, README.md)

# 3) build
docker build -t vibevoice:local .

# 4) install wrapper
mkdir -p ~/.local/bin
cp scripts/vibevoice ~/.local/bin/vibevoice
chmod +x ~/.local/bin/vibevoice
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# 5) run
echo "This streams directly to your audio player." | vibevoice
```
