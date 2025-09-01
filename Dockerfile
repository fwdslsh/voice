# Minimal CUDA-enabled PyTorch runtime. Works on CPU too (slower).
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

# System deps for audio and git
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg git tini && \
    rm -rf /var/lib/apt/lists/*

# Install VibeVoice + helpers
WORKDIR /app
RUN git clone https://github.com/microsoft/VibeVoice.git
RUN pip install -U pip setuptools wheel && \
    pip install -e VibeVoice soundfile scipy

# Predownload the default model to cache for faster startup
RUN python -c "from vibevoice.processor.vibevoice_processor import VibeVoiceProcessor; from vibevoice.modular.modeling_vibevoice_inference import VibeVoiceForConditionalGenerationInference; VibeVoiceProcessor.from_pretrained('microsoft/VibeVoice-1.5B'); VibeVoiceForConditionalGenerationInference.from_pretrained('microsoft/VibeVoice-1.5B', torch_dtype='auto')"

# Copy our tiny entrypoint
COPY vv_tts.py /usr/local/bin/vv_tts.py

# Nicer signal handling
ENTRYPOINT ["/usr/bin/tini","--","python","/usr/local/bin/vv_tts.py"]