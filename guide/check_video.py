from moviepy import VideoFileClip
v = VideoFileClip(r'c:\Users\40270\Desktop\workspace\nlp\guide\record_nlp.mp4')
print(f'Duration: {v.duration:.1f}s ({v.duration/60:.1f}min)')
print(f'Size: {v.size}')
print(f'FPS: {v.fps}')
print(f'Has audio: {v.audio is not None}')
v.close()
