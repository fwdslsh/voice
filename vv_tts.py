import argparse, os, sys
from pathlib import Path

def read_input(args):
    if args.text:
        return args.text
    if args.input:
        return Path(args.input).read_text(encoding="utf-8")
    data = sys.stdin.read()
    if not data.strip():
        print("No input provided. Use --text, --input or pipe stdin.", file=sys.stderr)
        sys.exit(2)
    return data

def main():
    p = argparse.ArgumentParser(description="VibeVoice TTS (stdin -> stdout WAV)")
    p.add_argument("--model", default=os.environ.get("VIBEVOICE_MODEL","microsoft/VibeVoice-1.5B"))
    p.add_argument("--speaker", default=os.environ.get("VIBEVOICE_SPEAKER","Alice"))
    p.add_argument("--text", help="Input text to synthesize")
    p.add_argument("--input", help="Read text from file instead of stdin")
    p.add_argument("--output", help="Save WAV output to file instead of stdout")
    args = p.parse_args()
import argparse, os, sys, re
from pathlib import Path
import numpy as np
import torch
import soundfile as sf
from vibevoice.processor.vibevoice_processor import VibeVoiceProcessor
from vibevoice.modular.modeling_vibevoice_inference import VibeVoiceForConditionalGenerationInference

class VoiceMapper:
    """Maps speaker names to voice file paths"""
    def __init__(self, voices_dir):
        self.voice_presets = {}
        self.available_voices = {}
        self.setup_voice_presets(voices_dir)
    def setup_voice_presets(self, voices_dir):
        if not os.path.isdir(voices_dir):
            print(f"Voices directory not found: {voices_dir}", file=sys.stderr)
            return
        wav_files = [f for f in os.listdir(voices_dir) if f.endswith('.wav') and os.path.isfile(os.path.join(voices_dir, f))]
        for wav_file in wav_files:
            name = os.path.splitext(wav_file)[0]
            full_path = os.path.join(voices_dir, wav_file)
            self.voice_presets[name] = full_path
        self.available_voices = dict(sorted(self.voice_presets.items()))
    def get_voice_path(self, speaker_name):
        # Try exact match
        if speaker_name in self.voice_presets:
            return self.voice_presets[speaker_name]
        # Try partial match
        speaker_lower = speaker_name.lower()
        for preset_name, path in self.voice_presets.items():
            if preset_name.lower() in speaker_lower or speaker_lower in preset_name.lower():
                return path
        # Default to first voice
        default_voice = list(self.voice_presets.values())[0]
        print(f"Warning: No voice preset found for '{speaker_name}', using default voice.", file=sys.stderr)
        return default_voice

def parse_txt_script(txt_content):
    """
    Parse txt script content and extract speakers and their text
    Returns: (scripts, speaker_numbers)
    """
    lines = txt_content.strip().split('\n')
    scripts = []
    speaker_numbers = []
    speaker_pattern = r'^Speaker\s+(\d+):\s*(.*)$'
    current_speaker = None
    current_text = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.match(speaker_pattern, line, re.IGNORECASE)
        if match:
            if current_speaker and current_text:
                scripts.append(current_text.strip())
                speaker_numbers.append(current_speaker)
            current_speaker = match.group(1).strip()
            current_text = match.group(2).strip()
        else:
            if current_text:
                current_text += " " + line
            else:
                current_text = "Speaker 1: " + line
                current_speaker = "1"

    if current_speaker and current_text:
        scripts.append(current_text.strip())
        speaker_numbers.append(current_speaker)
    return scripts, speaker_numbers

def read_input(args):
    if args.text:
        return args.text
    if args.input:
        return Path(args.input).read_text(encoding="utf-8")
    data = sys.stdin.read()
    if not data.strip():
        print("No input provided. Use --text, --input or pipe stdin.", file=sys.stderr)
        sys.exit(2)
    return data

def main():
    p = argparse.ArgumentParser(description="VibeVoice TTS (stdin -> stdout WAV)")
    p.add_argument("--model", default=os.environ.get("VIBEVOICE_MODEL","microsoft/VibeVoice-1.5B"))
    p.add_argument("--speaker", default=os.environ.get("VIBEVOICE_SPEAKER","Alice"))
    p.add_argument("--text", help="Input text to synthesize")
    p.add_argument("--input", help="Read text from file instead of stdin")
    p.add_argument("--output", help="Save WAV output to file instead of stdout")
    p.add_argument("--voices_dir", default="voices", help="Directory containing speaker wav files")
    args = p.parse_args()

    # get text
    txt_content = read_input(args).strip()
    if not txt_content:
        print("Empty text after trimming.", file=sys.stderr)
        sys.exit(2)

    # Parse script and speakers
    scripts, speaker_numbers = parse_txt_script(txt_content)
    if not scripts:
        print("No valid script found.", file=sys.stderr)
        sys.exit(2)

    # Map speaker numbers to names
    speaker_name_mapping = {}
    speaker_name_mapping['1'] = args.speaker
    # If more speakers, add mapping logic here

    # Setup voice mapper
    voice_mapper = VoiceMapper(args.voices_dir)

    # Prepare voice samples
    voice_samples = []
    for speaker_num in speaker_numbers:
        speaker_name = speaker_name_mapping.get(speaker_num, args.speaker)
        voice_path = voice_mapper.get_voice_path(speaker_name)
        ref_audio, sr = sf.read(voice_path)
        voice_samples.append(ref_audio)

    # Device/dtype/attention selection
    device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
    if device == "cuda":
        torch_dtype = torch.bfloat16
        try:
            import flash_attn
            attn_impl = "flash_attention_2"
        except ImportError:
            print("Warning: flash-attn not installed, falling back to SDPA.", file=sys.stderr)
            attn_impl = "sdpa"
    elif device == "mps":
        torch_dtype = torch.float32
        attn_impl = "sdpa"
    else:
        torch_dtype = torch.float32
        attn_impl = "sdpa"

    # load model/processor
    processor = VibeVoiceProcessor.from_pretrained(args.model)
    model = VibeVoiceForConditionalGenerationInference.from_pretrained(
        args.model,
        torch_dtype=torch_dtype,
        device_map=(device if device in ("cuda", "cpu") else None),
        attn_implementation=attn_impl
    )
    if device == "mps":
        model.to("mps")
    model.eval()

    # Patch: ensure speech_bias_factor is on the correct device (if possible)
    if hasattr(model, "speech_bias_factor"):
        bias = getattr(model, "speech_bias_factor")
        if hasattr(bias, "to"):
            bias.to(model.device)

    # Prepare inputs
    inputs = processor(
        text=scripts,
        speaker_names=[[args.speaker] for _ in scripts],
        voice_samples=[voice_samples],
        return_tensors="pt",
        return_attention_mask=True,
    )
    for k, v in inputs.items():
        if torch.is_tensor(v):
            inputs[k] = v.to(model.device)
        if v is None:
            print(f"Error: processor returned None for input '{k}'. Check input formatting and model requirements.", file=sys.stderr)
            sys.exit(2)

    # infer
    with torch.no_grad():
        outputs = model.generate(**inputs, tokenizer=processor.tokenizer)

    # Handle output
    arr = None
    sr = getattr(processor, "sample_rate", 24000)
    if hasattr(outputs, "speech_outputs"):
        arr = outputs.speech_outputs[0].detach().to(torch.float32).cpu().numpy()
    elif torch.is_tensor(outputs):
        arr = outputs.squeeze().detach().cpu().numpy().astype("float32")
    else:
        arr = outputs

    # Save audio
    def write_wav_file(data, sample_rate, file_path=None):
        import soundfile as sf
        import numpy as np
        # Ensure mono and float32
        data = np.asarray(data)
        if data.ndim > 1:
            data = data.squeeze()
        data = data.astype(np.float32)
        if file_path:
            sf.write(file_path, data, sample_rate, format='WAV')
        else:
            import io
            buf = io.BytesIO()
            sf.write(buf, data, sample_rate, format='WAV')
            buf.seek(0)
            return buf.getvalue()

    if args.output:
        try:
            processor.save_audio(arr, output_path=args.output)
        except Exception:
            write_wav_file(arr, sr, args.output)
    else:
        wav_data = write_wav_file(arr, sr)
        sys.stdout.buffer.write(wav_data)

if __name__ == "__main__":
    main()