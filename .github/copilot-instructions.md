# VibeVoice Docker CLI

Always follow these instructions first and only fall back to additional search and context gathering if the information here is incomplete or found to be in error.

VibeVoice Docker CLI is a containerized text-to-speech application that pipes text to Microsoft VibeVoice TTS and streams audio directly to host audio players or saves to files. Everything runs in Docker containers.

## Working Effectively

### Requirements and Setup
- Install Docker and ensure the daemon is running: `docker --version && docker info`
- Install a host audio player: `sudo apt-get update && sudo apt-get install -y ffmpeg` (provides `ffplay`)
- NEVER CANCEL: Build and dependency installation commands can take 3-5 minutes. Set timeout to 10+ minutes.

### Building the Application
- **CRITICAL**: Docker builds may fail due to SSL certificate verification in some environments
- **Local build** (from repository): `docker build -t vibevoice:local .` -- takes 3-5 minutes. NEVER CANCEL. Set timeout to 10+ minutes.
- **Known Issue**: Build may fail with "certificate verify failed" errors - this is environment-specific and expected in restricted/sandboxed environments

### Installation Methods

#### Method 1: Local Installation (if in repository)
```bash
# Build Docker image locally
docker build -t fwdslsh/voice:latest .
# Install wrapper script
mkdir -p ~/.local/bin
cp scripts/vibevoice ~/.local/bin/vibevoice
chmod +x ~/.local/bin/vibevoice
# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Method 2: Remote Installation (from anywhere)
```bash
# Quick install (when GitHub repository is accessible)
curl -fsSL https://raw.githubusercontent.com/fwdslsh/voice/main/install.sh | bash
```

#### Method 3: Manual Wrapper Setup
```bash
# Copy wrapper script locally and modify to use any VibeVoice image
mkdir -p ~/.local/bin
cp scripts/vibevoice ~/.local/bin/vibevoice
chmod +x ~/.local/bin/vibevoice
# Edit the image name in the wrapper if using alternative images
```

### Testing and Validation

#### Basic Functionality Test
```bash
# Test help output
vibevoice --help
# Test text-to-speech (saves to file)
vibevoice --text "Hello from VibeVoice" --output test.wav
ls -la test.wav
# Test with file input
echo "This is a test" > test.txt
vibevoice --input test.txt --output test2.wav
```

#### Audio Playback Test
```bash
# Test direct audio streaming (requires audio player)
echo "Testing audio playback" | vibevoice
# Test with specific speaker
vibevoice --speaker Alice --text "Hello from Alice"
```

#### Manual Validation Scenarios
ALWAYS test these scenarios after making changes:
1. **Text-to-file conversion**: `vibevoice --text "Test message" --output validation.wav && ls -la validation.wav`
2. **Stdin processing**: `echo "Pipeline test" | vibevoice --output pipeline.wav`
3. **File input processing**: Create a text file and use `--input` flag
4. **Audio streaming**: Test direct audio output (will work only with audio players available)

### Expected Behavior and Limitations

#### Working Scenarios
- Text-to-speech conversion works with Docker available
- WAV file output always works (validated: creates proper RIFF WAVE files)
- Audio streaming works when host audio players (ffplay, aplay, etc.) are available
- Wrapper script handles GPU detection automatically
- Python TTS script provides proper argument parsing and help output

#### Known Limitations
- **Docker Build Issues**: SSL certificate verification WILL fail in restricted/sandboxed environments - this is expected and environment-specific
- **Remote Installation**: May fail with 404 errors if GitHub raw content is not accessible
- **Audio Playback**: Direct audio streaming requires host audio players; fails gracefully in headless environments
- **Network Dependencies**: Requires internet access for Docker image pulls and model downloads
- **Resource Requirements**: Initial run downloads ~1.5GB model; subsequent runs are faster

#### Validation Status
✅ Docker functionality confirmed  
✅ Audio infrastructure confirmed (ffplay available)  
✅ Python TTS script structure validated  
✅ Repository structure matches documentation  
✅ Audio file creation workflow tested  
⚠️ Docker builds fail in sandboxed environments (documented limitation)  
⚠️ Remote installations may fail due to network restrictions

### Timing Expectations
- **NEVER CANCEL**: Docker build: 3-5 minutes (set timeout to 10+ minutes)
- **NEVER CANCEL**: First run: 2-3 minutes for model download (set timeout to 5+ minutes)
- **Subsequent runs**: 5-15 seconds for short text
- **Install script**: 30-60 seconds for remote installation

### Troubleshooting Commands
- Check Docker status: `docker info`
- Check available images: `docker images | grep vibevoice`
- Check audio players: `which ffplay aplay paplay play afplay`
- Test audio system: Create test WAV and play with `ffplay -nodisp -autoexit test.wav`
- Check wrapper script: `cat ~/.local/bin/vibevoice | head -20`

### Development Workflow
- Build locally: `docker build -t vibevoice:local .`
- Test changes: `vibevoice --text "Test change" --output test.wav`
- Validate audio: `ffplay -nodisp -autoexit test.wav`
- Check wrapper behavior: Test both file output and streaming modes

## Key Project Components

### Core Files
- `Dockerfile`: Container definition using PyTorch with CUDA support
- `vv_tts.py`: Python TTS implementation with argparse interface
- `scripts/vibevoice`: Bash wrapper script handling Docker execution and audio routing
- `install.sh`: Installation script with validation and PATH setup
- `README.md`: User documentation with usage examples
- `.github/workflows/docker-publish.yml`: CI/CD workflow for automated Docker publishing and GitHub releases

### Repository Structure
```
/home/runner/work/voice/voice/
├── Dockerfile              # Container build definition
├── vv_tts.py               # Main TTS Python script
├── scripts/
│   └── vibevoice           # Wrapper script for Docker execution
├── .github/
│   ├── workflows/
│   │   └── docker-publish.yml  # CI/CD workflow for Docker publishing
│   └── copilot-instructions.md # Development guidelines
├── install.sh              # Automated installer with validation
├── README.md               # Documentation
└── .gitignore             # Excludes caches and audio files
```

### Common Command Outputs

#### Repository Root Listing
```
$ ls -la
total 28
drwxr-xr-x 3 runner docker  160 Sep  1 19:17 .
drwxr-xr-x 4 runner docker   80 Sep  1 19:17 ..
-rw-r--r-- 1 runner docker 1082 Sep  1 19:17 Dockerfile
-rw-r--r-- 1 runner docker 4753 Sep  1 19:17 README.md
drwxr-xr-x 8 runner docker  220 Sep  1 19:17 .git
-rw-r--r-- 1 runner docker   68 Sep  1 19:17 .gitignore
-rwxr-xr-x 1 runner docker 4347 Sep  1 19:17 install.sh
drwxr-xr-x 2 runner docker   60 Sep  1 19:17 scripts
-rw-r--r-- 1 runner docker 2375 Sep  1 19:17 vv_tts.py
```

#### TTS Script Help Output
```
$ python3 vv_tts.py --help
usage: vv_tts.py [-h] [--model MODEL] [--speaker SPEAKER] [--text TEXT] [--input INPUT] [--output OUTPUT]

VibeVoice TTS (stdin -> stdout WAV)

options:
  -h, --help         show this help message and exit
  --model MODEL
  --speaker SPEAKER
  --text TEXT        Input text to synthesize
  --input INPUT      Read text from file instead of stdin
  --output OUTPUT    Save WAV output to file instead of stdout
```

### Environment-Specific Notes
- **SSL Certificate Issues**: Common in containerized/sandboxed environments; affects GitHub and PyPI access during builds
- **Audio System Availability**: Direct audio playback requires host audio infrastructure; gracefully degrades to file output
- **GPU Support**: Automatically detected and used when NVIDIA Container Toolkit is available
- **Cache Persistence**: Hugging Face models cached in `~/.cache/huggingface` for faster subsequent runs

### CI/CD and Release Process
- **Automated Docker Publishing**: GitHub Actions workflow builds and publishes Docker images to Docker Hub on version tags
- **Version Tags**: Push tags in format `v*` (e.g., `v1.0.0`, `v2.1.3`) to trigger automatic builds
- **Docker Hub Images**: Published to `fwdslsh/voice` with both `latest` and version-specific tags
- **GitHub Releases**: Automatically created with release notes containing install script instructions
- **Multi-Platform**: Docker images built for both `linux/amd64` and `linux/arm64` architectures
- **Required Secrets**: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` must be configured in repository secrets

### Release Workflow
1. Commit changes to main branch
2. Create and push version tag: `git tag v1.0.0 && git push origin v1.0.0`
3. GitHub Actions automatically:
   - Builds Docker image for multiple platforms
   - Pushes to Docker Hub with `latest` and version tags
   - Creates GitHub release with installation instructions
4. Users can immediately install via: `curl -fsSL https://raw.githubusercontent.com/fwdslsh/voice/main/install.sh | bash`

### Critical Validation Steps
Before committing changes, ALWAYS:
1. Test Docker build (if possible in environment): `docker build -t vibevoice:test .`
2. Test wrapper script functionality: `vibevoice --text "Validation test" --output validation.wav`
3. Verify audio file creation: `ls -la validation.wav && file validation.wav`
4. Test streaming (if audio available): `echo "Stream test" | vibevoice`
5. Validate help output: `vibevoice --help`
6. Validate GitHub Actions workflow syntax: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/docker-publish.yml'))"`
