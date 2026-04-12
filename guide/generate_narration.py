"""
Voice Cloning Narration Generator using Coqui TTS XTTS-v2
With monkey-patches for transformers 5.x compatibility
"""
import os
import sys

# ── Monkey-patch transformers for coqui-tts compatibility ──
# coqui-tts references functions removed in transformers 5.x
import torch
import transformers.pytorch_utils as _pu
if not hasattr(_pu, 'isin_mps_friendly'):
    _pu.isin_mps_friendly = torch.isin

import transformers.utils.import_utils as _iu
if not hasattr(_iu, 'is_torch_greater_or_equal'):
    def _is_torch_greater_or_equal(version):
        from packaging.version import parse
        return parse(torch.__version__.split('+')[0]) >= parse(version)
    _iu.is_torch_greater_or_equal = _is_torch_greater_or_equal

# Now import TTS
from TTS.api import TTS

VOICE_SAMPLE = r"c:\Users\40270\Desktop\workspace\nlp\guide\voice_sample.wav"
OUTPUT_DIR = r"c:\Users\40270\Desktop\workspace\nlp\guide\narration"

SEGMENTS = [
    ("scene1_opening.wav",
     "Hi, I'm Lannie. This is our AI Textbook Q and A system. "
     "We built this with Peng Wang for CST 8507, Natural Language Processing. "
     "Let me show you how it works."),

    ("scene2_search.wav",
     "This is the search page. You can type any question here. "
     "The system will show you topic ideas as you type. "
     "Let me try, What is SVM?"),

    ("scene3_answer.wav",
     "Here is the answer. It only uses information from our textbooks. "
     "You can see related topics at the top. "
     "Click on them to learn more about other topics."),

    ("scene4_sources.wav",
     "Below the answer, you can see which books were used. "
     "Each book has a score from zero to one. "
     "Higher score means the book is more relevant. "
     "We use four different search methods to find the best results."),

    ("scene5_pdf.wav",
     "If you click View PDF, you can see the original textbook page. "
     "It goes to the exact page where the answer came from. "
     "You can zoom in or make it full screen. "
     "This way, you can always check the source."),

    ("scene6_library.wav",
     "On the side, there is a Library section. "
     "You can see all forty-six textbooks here. "
     "You can also change settings, like how many results to show."),

    ("scene7_closing.wav",
     "So, our system can search through eighty-five thousand text pieces "
     "from forty-six books. It works on a normal computer. "
     "Thank you for watching."),
]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading XTTS-v2 model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device} ({torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'})")

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    print(f"Voice sample: {VOICE_SAMPLE}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Segments: {len(SEGMENTS)}")
    print()

    for i, (filename, text) in enumerate(SEGMENTS, 1):
        out_path = os.path.join(OUTPUT_DIR, filename)
        print(f"[{i}/{len(SEGMENTS)}] Generating: {filename}")
        print(f"  Text: {text[:80]}...")

        tts.tts_to_file(
            text=text,
            speaker_wav=VOICE_SAMPLE,
            language="en",
            file_path=out_path,
            speed=0.92,
        )
        print(f"  -> Saved: {out_path}")
        print()

    print("All segments generated!")
    print(f"Files in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
