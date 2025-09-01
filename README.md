# VibeVoice Docker CLI

A tiny, Dockerized CLI that pipes text to Microsoft **VibeVoice** TTS, writes a WAV inside the container, then your host plays it and deletes it.

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
# Add ~/.local/bin to your PATH if needed:
# echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Usage

```bash
# A) stdin
echo "Hello from VibeVoice." | vibevoice

# B) read a text file
vibevoice --file notes.txt

# C) literal text
vibevoice --text "Shipping the demo is the best spec."

# D) choose model / speaker
VIBEVOICE_MODEL="microsoft/VibeVoice-1.5B" \
VIBEVOICE_SPEAKER="Alice" \
  vibevoice --text "Using a specific model and speaker."
```

> If no host audio player is found, the script prints the WAV path and keeps the temp folder so you can inspect it.

## Notes

- Everything runs in Docker; your host only needs an audio player.
- A Hugging Face cache is mounted at `~/.cache/huggingface` to avoid re-downloading models each run.
- GPU is auto-enabled when `nvidia-smi` exists; otherwise it runs on CPU (slower).

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
echo "This is fully isolated via Docker." | vibevoice
```
