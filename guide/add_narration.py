"""
Add voice-cloned narration to the demo video.
Replaces original audio with narration segments at timed positions.
Uses background music if available, otherwise just narration.
"""
import os
import sys

# ── Video & Audio paths ──
VIDEO_IN  = r"c:\Users\40270\Desktop\workspace\nlp\guide\record_nlp.mp4"
VIDEO_OUT = r"c:\Users\40270\Desktop\workspace\nlp\guide\record_nlp_narrated.mp4"
NARR_DIR  = r"c:\Users\40270\Desktop\workspace\nlp\guide\narration"

from moviepy import (
    VideoFileClip, AudioFileClip,
    CompositeAudioClip, concatenate_audioclips
)
import numpy as np

def make_silence(duration, fps=22050):
    """Create a silent audio clip of given duration."""
    # Create a lambda-based audio clip
    from moviepy import AudioClip
    silent = AudioClip(lambda t: np.zeros((1 if np.isscalar(t) else len(t), 2)),
                       duration=duration, fps=fps)
    return silent

def main():
    print(f"Loading video: {VIDEO_IN}")
    video = VideoFileClip(VIDEO_IN)
    vid_duration = video.duration
    print(f"Video duration: {vid_duration:.1f}s ({vid_duration/60:.1f}min)")

    # ── Narration timing ──
    # Each tuple: (filename, start_time_seconds)
    # Distribute narration across the video timeline to match visual content
    # Video is ~160s, narration total is ~116s
    # We space them with small gaps between segments
    TIMED_SEGMENTS = [
        ("scene1_opening.wav",  1.0),    # Opening intro
        ("scene2_search.wav",  20.0),    # Search demo starts
        ("scene3_answer.wav",  42.0),    # Answer display
        ("scene4_sources.wav", 62.0),    # Sources section
        ("scene5_pdf.wav",     84.0),    # PDF viewer
        ("scene6_library.wav", 106.0),   # Library & settings
        ("scene7_closing.wav", 125.0),   # Closing
    ]

    # Build narration audio clips at their positions
    narration_clips = []
    for filename, start_time in TIMED_SEGMENTS:
        filepath = os.path.join(NARR_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  WARNING: {filepath} not found, skipping")
            continue

        clip = AudioFileClip(filepath)
        # Ensure narration doesn't exceed video duration
        if start_time + clip.duration > vid_duration:
            print(f"  WARNING: {filename} at {start_time}s would exceed video, adjusting...")
            start_time = max(0, vid_duration - clip.duration - 0.5)

        clip = clip.with_start(start_time)
        narration_clips.append(clip)
        print(f"  {filename}: {start_time:.1f}s -> {start_time + clip.duration:.1f}s ({clip.duration:.1f}s)")

    print(f"\nTotal narration clips: {len(narration_clips)}")

    # Compose: narration only (replace original audio)
    final_audio = CompositeAudioClip(narration_clips)

    # Set audio on video
    final_video = video.with_audio(final_audio)

    # Write output
    print(f"\nWriting: {VIDEO_OUT}")
    print("This may take a few minutes...")
    final_video.write_videofile(
        VIDEO_OUT,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="256k",
        fps=video.fps,
        preset="slow",
        threads=4,
        logger="bar",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
    )

    print(f"\nDone! Output: {VIDEO_OUT}")
    print(f"Size: {os.path.getsize(VIDEO_OUT) / 1024 / 1024:.1f} MB")

    # Cleanup
    video.close()
    for c in narration_clips:
        c.close()

if __name__ == "__main__":
    main()
