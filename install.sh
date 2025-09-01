#!/usr/bin/env bash
set -euo pipefail

# VibeVoice Docker CLI Installer
# This script installs the VibeVoice Docker CLI tool and verifies the installation

echo "🎤 VibeVoice Docker CLI Installer"
echo "=================================="

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Error: Docker is not installed or not in PATH."
    echo "   Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found"

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker daemon is not running."
    echo "   Please start Docker and try again."
    exit 1
fi

echo "✅ Docker daemon is running"

# Create the installation directory
INSTALL_DIR="$HOME/.local/bin"
echo "📁 Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Check if we're running from the repository or downloading from GitHub
if [[ -f "scripts/voice" && -f "Dockerfile" && -f "vv_tts.py" ]]; then
    echo "📦 Installing from local repository"
    
    # Build the Docker image locally
    echo "🔨 Building Docker image..."
    docker build -t fwdslsh/voice:latest . || {
        echo "❌ Error: Failed to build Docker image"
        exit 1
    }
    echo "✅ Docker image built successfully"
    
    # Copy the wrapper script
    cp scripts/voice "$INSTALL_DIR/voice"
    
else
    echo "📦 Installing from GitHub repository"
    
    # Download the wrapper script
    echo "⬇️  Downloading wrapper script..."
    curl -fsSL https://raw.githubusercontent.com/fwdslsh/voice/main/scripts/voice -o "$INSTALL_DIR/voice" || {
        echo "❌ Error: Failed to download wrapper script"
        exit 1
    }
    
    # For remote installation, pull the pre-built image from Docker Hub
    echo "⬇️  Pulling Docker image from Docker Hub..."
    docker pull fwdslsh/voice:latest || {
        echo "❌ Error: Failed to pull Docker image from Docker Hub"
        echo "   Please check your internet connection and Docker Hub access"
        exit 1
    }
    
    echo "✅ Docker image pulled successfully"
fi

# Make the wrapper script executable
chmod +x "$INSTALL_DIR/voice"
echo "✅ Wrapper script installed to $INSTALL_DIR/voice"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "⚠️  Warning: $HOME/.local/bin is not in your PATH"
    echo "   Adding it to your shell configuration..."
    
    # Detect shell and add to appropriate config file
    if [[ -n "${BASH_VERSION:-}" ]] || [[ "$SHELL" =~ bash$ ]]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [[ -n "${ZSH_VERSION:-}" ]] || [[ "$SHELL" =~ zsh$ ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    # Check if the PATH export already exists
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_CONFIG" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"
        echo "✅ Added $HOME/.local/bin to PATH in $SHELL_CONFIG"
        echo "   Please run: source $SHELL_CONFIG"
        echo "   Or restart your terminal to use the 'voice' command"
    else
        echo "✅ PATH already configured in $SHELL_CONFIG"
    fi
    
    # Add to current session PATH
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "✅ $HOME/.local/bin is already in PATH"
fi

# Test the installation
echo ""
echo "🧪 Testing installation..."

# Test with a simple text input
TEST_OUTPUT=$(mktemp --suffix=.wav)
cleanup_test() {
    rm -f "$TEST_OUTPUT"
}
trap cleanup_test EXIT

if "$INSTALL_DIR/voice" --text "VibeVoice installation successful!" --output "$TEST_OUTPUT" 2>/dev/null; then
    echo "✅ Installation test passed (audio file created)"
    
    # Try to play the audio if an audio player is available
    echo "🔊 Playing installation success announcement..."
    if "$INSTALL_DIR/voice" --text "VibeVoice Docker CLI has been successfully installed and is ready to use!" 2>/dev/null; then
        echo "✅ Audio playback test successful"
    else
        echo "⚠️  Audio playback test failed (no audio player found or audio system not available)"
        echo "   This is normal in headless environments"
    fi
else
    echo "❌ Installation test failed"
    echo "   The voice command could not generate audio"
    echo "   Please check the Docker installation and try again"
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Usage examples:"
echo "  echo 'Hello from VibeVoice!' | voice"
echo "  voice --text 'Hello world'"
echo "  voice --speaker Alice --text 'Hello from Alice'"
echo "  voice --text 'Save this' --output output.wav"
echo "  voice --input mytext.txt --output result.wav"
echo "  voice --update    # Update to latest version"
echo ""
echo "For more information, visit: https://github.com/fwdslsh/voice"