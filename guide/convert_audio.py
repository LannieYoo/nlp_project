"""Convert m4a to wav using imageio_ffmpeg (already installed with moviepy)"""
import subprocess
import imageio_ffmpeg

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
src = r"c:\Users\40270\Desktop\workspace\nlp\guide\클로닝.m4a"
dst = r"c:\Users\40270\Desktop\workspace\nlp\guide\voice_sample.wav"

result = subprocess.run(
    [ffmpeg_path, "-y", "-i", src, "-ar", "22050", "-ac", "1", dst],
    capture_output=True, text=True
)
if result.returncode == 0:
    print(f"OK: {dst}")
else:
    print(f"Error: {result.stderr}")
