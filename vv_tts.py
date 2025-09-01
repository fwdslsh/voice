import argparse, os, sys
from pathlib import Path

def read_input(args):
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    data = sys.stdin.read()
    if not data.strip():
        print("No input provided. Use --file or pipe stdin.", file=sys.stderr)
        sys.exit(2)
    return data

def main():
    p = argparse.ArgumentParser(description="VibeVoice TTS (stdin -> stdout WAV)")
    p.add_argument("--model", default=os.environ.get("VIBEVOICE_MODEL","microsoft/VibeVoice-1.5B"))
    p.add_argument("--speaker", default=os.environ.get("VIBEVOICE_SPEAKER","Alice"))
    p.add_argument("--file", help="Read text from file instead of stdin")
    args = p.parse_args()

    # get text
    text = read_input(args).strip()
    if not text:
        print("Empty text after trimming.", file=sys.stderr)
        sys.exit(2)

    # lazy imports so --help is fast
    import torch
    from vibevoice.processor.vibevoice_processor import VibeVoiceProcessor
    from vibevoice.modular.modeling_vibevoice_inference import VibeVoiceForConditionalGenerationInference

    # load model/processor
    processor = VibeVoiceProcessor.from_pretrained(args.model)
    model = VibeVoiceForConditionalGenerationInference.from_pretrained(
        args.model, torch_dtype="auto", device_map="auto"
    )

    # prepare inputs
    inputs = processor(text=text, speaker_names=[args.speaker], return_tensors="pt").to(model.device)

    # infer
    with torch.no_grad():
        wav = model.generate(**inputs)  # [1, samples], float32 in [-1,1]

    # sample rate (VibeVoice commonly 24k)
    sr = processor.acoustic_codec_config.get("sample_rate", 24000)

    # write WAV
    import numpy as np
    arr = wav.squeeze().detach().cpu().numpy().astype("float32")
    
    # Write WAV to stdout
    import io
    try:
        import soundfile as sf
        # Write WAV data to a bytes buffer
        buf = io.BytesIO()
        sf.write(buf, arr, sr, format='WAV')
        buf.seek(0)
        sys.stdout.buffer.write(buf.getvalue())
    except Exception:
        # Fallback to manual WAV format
        from scipy.io.wavfile import write as wavwrite
        buf = io.BytesIO()
        wavwrite(buf, sr, (arr * 32767).astype("int16"))
        buf.seek(0)
        sys.stdout.buffer.write(buf.getvalue())

if __name__ == "__main__":
    main()