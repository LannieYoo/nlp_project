"""
Final Video Render v2: Narrator PIP + Chunked Subtitles + Slower Voice Clone
Fixes:
  1. Photo crop: offset upward so full head is visible
  2. Subtitles: larger font, split into timed chunks (2 lines max at a time)
  3. Audio: uses slower narration (speed=0.82)
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Paths ──
VIDEO_IN   = r"c:\Users\40270\Desktop\workspace\nlp\guide\record_nlp.mp4"
VIDEO_OUT  = r"c:\Users\40270\Desktop\workspace\nlp\guide\record_nlp_final.mp4"
NARR_DIR   = r"c:\Users\40270\Desktop\workspace\nlp\guide\narration"
PHOTO_PATH = r"c:\Users\40270\Desktop\workspace\nlp\guide\lannie.jpg"

from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip,
    CompositeVideoClip, CompositeAudioClip,
)
from moviepy.video.fx import FadeIn, FadeOut

# ── Narration segments: (filename, start_time, script_text) ──
SEGMENTS = [
    ("scene1_opening.wav", 1.0,
     "Hi, I'm Lannie. This is our AI Textbook Q&A system. "
     "We built this with Peng Wang for CST 8507, Natural Language Processing. "
     "Let me show you how it works."),

    ("scene2_search.wav", 20.0,
     "This is the search page. You can type any question here. "
     "The system will show you topic ideas as you type. "
     "Let me try, What is SVM?"),

    ("scene3_answer.wav", 40.0,
     "Here is the answer. It only uses information from our textbooks. "
     "You can see related topics at the top. "
     "Click on them to learn more about other topics."),

    ("scene4_sources.wav", 58.0,
     "Below the answer, you can see which books were used. "
     "Each book has a score from zero to one. "
     "Higher score means the book is more relevant. "
     "We use four different search methods to find the best results."),

    ("scene5_pdf.wav", 78.0,
     "If you click View PDF, you can see the original textbook page. "
     "It goes to the exact page where the answer came from. "
     "You can zoom in or make it full screen. "
     "This way, you can always check the source."),

    ("scene6_library.wav", 100.0,
     "On the side, there is a Library section. "
     "You can see all forty-six textbooks here. "
     "You can also change settings, like how many results to show."),

    ("scene7_closing.wav", 120.0,
     "So, our system can search through eighty-five thousand text pieces "
     "from forty-six books. It works on a normal computer. "
     "Thank you for watching."),
]


def create_circular_photo(photo_path, size=200):
    """Create circular presenter photo - crop biased upward so head isn't cut off."""
    img = Image.open(photo_path).convert("RGBA")
    w, h = img.size

    # Square crop biased toward top (show forehead fully)
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    # Bias upward: start from top with small offset instead of center
    top = max(0, int((h - min_dim) * 0.15))  # 15% from top instead of 50%
    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize((size, size), Image.LANCZOS)

    # Create circular mask
    border_width = 4
    total_size = size + border_width * 2
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)

    # Result with border
    result = Image.new("RGBA", (total_size, total_size), (0, 0, 0, 0))

    # White border circle
    border_draw = ImageDraw.Draw(result)
    border_draw.ellipse((0, 0, total_size - 1, total_size - 1), fill=(255, 255, 255, 220))

    # Inner shadow circle for depth
    border_draw.ellipse((1, 1, total_size - 2, total_size - 2), fill=(240, 240, 240, 200))

    # Paste circular photo
    circular = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circular.paste(img, (0, 0), mask)
    result.paste(circular, (border_width, border_width), circular)

    return np.array(result)


def split_script_to_chunks(text, max_chars_per_chunk=70):
    """Split script text into display chunks of ~2 short lines each.
    Returns list of chunk strings."""
    words = text.split()
    chunks = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        if len(test) <= max_chars_per_chunk:
            current = test
        else:
            if current:
                chunks.append(current)
            current = word
    if current:
        chunks.append(current)

    return chunks


def create_subtitle_image(text, video_width, font_size=40):
    """Create a single subtitle frame as RGBA numpy array."""
    line_height = font_size + 14
    padding_x = 40
    padding_y = 20

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Word-wrap the chunk into lines (~40 chars per line for larger font)
    words = text.split()
    lines = []
    current = ""
    max_line_chars = 45
    for w in words:
        test = f"{current} {w}".strip()
        if len(test) <= max_line_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)

    # Dimensions
    text_height = len(lines) * line_height
    bar_height = text_height + padding_y * 2
    bar_width = video_width

    # Create image
    img = Image.new("RGBA", (bar_width, bar_height), (0, 0, 0, 0))

    # Semi-transparent dark background
    bg = Image.new("RGBA", (bar_width, bar_height), (15, 15, 25, 180))
    img = Image.alpha_composite(img, bg)
    draw = ImageDraw.Draw(img)

    # Draw centered text
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (bar_width - tw) // 2
        y = padding_y + i * line_height

        # Shadow
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 220))
        # Main text (warm white)
        draw.text((x, y), line, font=font, fill=(255, 255, 245, 255))

    return np.array(img)


def main():
    print(f"Loading video: {VIDEO_IN}")
    video = VideoFileClip(VIDEO_IN)
    vid_w, vid_h = video.size
    vid_duration = video.duration
    print(f"Video: {vid_w}x{vid_h}, {vid_duration:.1f}s, {video.fps}fps")

    # ── Circular photo ──
    print("Creating circular presenter photo (head-aware crop)...")
    photo_size = 180
    photo_array = create_circular_photo(PHOTO_PATH, photo_size)
    print(f"  Photo clip size: {photo_array.shape[1]}x{photo_array.shape[0]}")

    # ── Build overlay clips ──
    narration_clips = []
    overlay_clips = [video]

    for seg_idx, (filename, start_time, script_text) in enumerate(SEGMENTS):
        filepath = os.path.join(NARR_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  WARNING: {filepath} not found, skipping")
            continue

        audio_clip = AudioFileClip(filepath)
        seg_duration = audio_clip.duration

        # Clamp
        if start_time + seg_duration > vid_duration:
            start_time = max(0, vid_duration - seg_duration - 0.5)

        print(f"\n  [{seg_idx+1}] {filename}: {start_time:.1f}s -> {start_time + seg_duration:.1f}s ({seg_duration:.1f}s)")

        # Audio
        narration_clips.append(audio_clip.with_start(start_time))

        # ── PIP photo (bottom-right, above subtitle area) ──
        pip_margin = 30
        pip_x = vid_w - photo_array.shape[1] - pip_margin
        pip_y = vid_h - photo_array.shape[0] - 160  # above subtitle

        photo_clip = (
            ImageClip(photo_array)
            .with_duration(seg_duration)
            .with_start(start_time)
            .with_position((pip_x, pip_y))
            .with_effects([FadeIn(0.4), FadeOut(0.4)])
        )
        overlay_clips.append(photo_clip)

        # ── Chunked subtitles ──
        chunks = split_script_to_chunks(script_text, max_chars_per_chunk=70)
        num_chunks = len(chunks)
        chunk_duration = seg_duration / num_chunks

        print(f"    Script split into {num_chunks} chunks, {chunk_duration:.1f}s each")

        for ci, chunk_text in enumerate(chunks):
            chunk_start = start_time + ci * chunk_duration
            sub_img = create_subtitle_image(chunk_text, vid_w, font_size=40)
            sub_y = vid_h - sub_img.shape[0]

            sub_clip = (
                ImageClip(sub_img)
                .with_duration(chunk_duration)
                .with_start(chunk_start)
                .with_position((0, sub_y))
                .with_effects([FadeIn(0.2), FadeOut(0.2)])
            )
            overlay_clips.append(sub_clip)
            print(f"    chunk {ci+1}: \"{chunk_text[:50]}...\" @ {chunk_start:.1f}s")

    print(f"\n  Total overlay clips: {len(overlay_clips)}")

    # ── Compose ──
    final_video = CompositeVideoClip(overlay_clips, size=(vid_w, vid_h))
    final_audio = CompositeAudioClip(narration_clips)
    final_video = final_video.with_audio(final_audio)
    final_video = final_video.with_duration(vid_duration)

    # ── Render ──
    print(f"\nRendering: {VIDEO_OUT}")
    print("This will take ~20 minutes...")
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

    output_size = os.path.getsize(VIDEO_OUT) / 1024 / 1024
    print(f"\n✅ Done! Output: {VIDEO_OUT}")
    print(f"   Size: {output_size:.1f} MB")

    video.close()
    for c in narration_clips:
        c.close()


if __name__ == "__main__":
    main()
