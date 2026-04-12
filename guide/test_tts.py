"""Quick test: check if TTS + CUDA works"""
import traceback
try:
    import torch
    print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    
    from TTS.api import TTS
    print("TTS imported OK")
    
    print("Available models (xtts):")
    models = TTS().list_models()
    for m in models:
        if "xtts" in str(m).lower():
            print(f"  {m}")
    
    print("\nLoading XTTS-v2...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    print("Model loaded OK!")
    
except Exception as e:
    traceback.print_exc()
