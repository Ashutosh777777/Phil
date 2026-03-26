# # video_service.py
# from PIL import Image, ImageDraw, ImageFont, ImageEnhance
# import subprocess
# import json
# import os
# from pathlib import Path

# VIDEO_DIR = Path("video_output")
# FRAMES_DIR = Path("video_output/frames")
# VIDEO_DIR.mkdir(exist_ok=True)
# FRAMES_DIR.mkdir(exist_ok=True)

# W, H = 1920, 1080

# def wrap_text(text, max_chars=32):  # reduced from 38
#     words = text.split()
#     lines, current = [], ""
#     for word in words:
#         if len(current) + len(word) + 1 <= max_chars:
#             current += ("" if not current else " ") + word
#         else:
#             if current:
#                 lines.append(current)
#             current = word
#     if current:
#         lines.append(current)
#     return lines[:6]

# def draw_speech_bubble(draw, text, side, font):
#     lines = wrap_text(text)
#     line_h = 36
#     padding = 22
#     bubble_w = 460  # reduced from 520
#     bubble_h = len(lines) * line_h + padding * 2

#     if side == "left":
#         bx = 60
#     else:
#         bx = W - bubble_w - 60  # stays within frame
#     by = 60

#     draw.rounded_rectangle(
#         [bx + 4, by + 4, bx + bubble_w + 4, by + bubble_h + 4],
#         radius=16, fill=(0, 0, 0, 120)
#     )
#     draw.rounded_rectangle(
#         [bx, by, bx + bubble_w, by + bubble_h],
#         radius=16, fill=(255, 255, 255, 210), outline=(180, 140, 80, 255), width=3
#     )
#     for i, line in enumerate(lines):
#         draw.text(
#             (bx + padding, by + padding + i * line_h),
#             line, fill=(30, 20, 10), font=font
#         )

# def draw_name_labels(draw, font_bold, active_speaker, author_a, author_b):
#     name_a = "Franz Kafka"
#     name_b = "Friedrich Nietzsche"
#     alpha_a = 255 if active_speaker.lower() == author_a.lower() else 140
#     alpha_b = 255 if active_speaker.lower() == author_b.lower() else 140
#     draw.text((120, H - 100), name_a, fill=(255, 220, 150, alpha_a), font=font_bold)
#     bbox = draw.textbbox((0, 0), name_b, font=font_bold)
#     tw = bbox[2] - bbox[0]
#     draw.text((W - tw - 120, H - 100), name_b, fill=(255, 220, 150, alpha_b), font=font_bold)

# def apply_speaker_highlight(img, active_speaker, author_a):
#     left_half = img.crop((0, 0, W // 2, H))
#     right_half = img.crop((W // 2, 0, W, H))
#     if active_speaker.lower() == author_a.lower():
#         left_half = ImageEnhance.Brightness(left_half).enhance(1.15)
#         right_half = ImageEnhance.Brightness(right_half).enhance(0.72)
#     else:
#         left_half = ImageEnhance.Brightness(left_half).enhance(0.72)
#         right_half = ImageEnhance.Brightness(right_half).enhance(1.15)
#     result = Image.new("RGB", (W, H))
#     result.paste(left_half, (0, 0))
#     result.paste(right_half, (W // 2, 0))
#     return result

# def generate_frame(speaker, text, author_a, author_b, bg_img, frame_path, font, font_bold):
#     img = apply_speaker_highlight(bg_img, speaker, author_a)
#     overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
#     draw = ImageDraw.Draw(overlay)
#     side = "left" if speaker.lower() == author_a.lower() else "right"
#     draw_speech_bubble(draw, text, side, font)
#     draw_name_labels(draw, font_bold, speaker, author_a, author_b)
#     img = img.convert("RGBA")
#     img = Image.alpha_composite(img, overlay)
#     img = img.convert("RGB")
#     img.save(frame_path, quality=95)

# def get_audio_duration(audio_path):
#     result = subprocess.run([
#         "ffprobe", "-v", "quiet", "-print_format", "json",
#         "-show_format", audio_path
#     ], capture_output=True, text=True)
#     data = json.loads(result.stdout)
#     return float(data["format"]["duration"])

# def compose_video(
#     script_path="output_script.json",
#     audio_dir="audio_output",
#     output_path="video_output/debate.mp4"
# ):
#     from caption_service import generate_captions
#     generate_captions(script_path=script_path, audio_dir=audio_dir)

#     with open(script_path) as f:
#         data = json.load(f)

#     script = data["script"]
#     author_a = data["author_a"]
#     author_b = data["author_b"]

#     bg = Image.open("assets/background.jpg").convert("RGB")
#     bg = bg.resize((W, H), Image.LANCZOS)

#     try:
#         font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
#         font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
#     except:
#         font = ImageFont.load_default()
#         font_bold = font

#     print(f"Generating {len(script)} frames...")
#     frame_files = []

#     for i, line in enumerate(script):
#         speaker = line["speaker"]
#         text = line["text"]
#         audio_seg = os.path.join(audio_dir, f"line_{i:03d}_{speaker}.mp3")
#         if not os.path.exists(audio_seg):
#             print(f"Missing: {audio_seg}")
#             continue
#         duration = get_audio_duration(audio_seg)
#         frame_path = str(FRAMES_DIR / f"frame_{i:03d}.png")
#         generate_frame(speaker, text, author_a, author_b, bg, frame_path, font, font_bold)
#         frame_files.append((frame_path, duration))
#         print(f"  Frame {i+1}/{len(script)} — {speaker} ({duration:.1f}s)")

#     concat_path = "video_output/concat.txt"
#     with open(concat_path, "w") as f:
#         for frame_path, duration in frame_files:
#             f.write(f"file '{os.path.abspath(frame_path)}'\n")
#             f.write(f"duration {duration}\n")
#         f.write(f"file '{os.path.abspath(frame_files[-1][0])}'\n")

#     captions_path = "captions.srt"

#     print("\nComposing video with ffmpeg...")
#     cmd = [
#         "ffmpeg", "-y",
#         "-f", "concat", "-safe", "0", "-i", concat_path,
#         "-i", os.path.join(audio_dir, "full_debate.mp3"),
#         "-vf", (
#             f"subtitles={captions_path}:force_style='"
#             "FontName=DejaVu Sans,"
#             "FontSize=20,"
#             "PrimaryColour=&H00FFFFFF,"
#             "OutlineColour=&H00000000,"
#             "Outline=3,"
#             "Shadow=1,"
#             "Alignment=2,"
#             "MarginV=30'"
#         ),
#         "-c:v", "libx264", "-crf", "18",
#         "-c:a", "aac", "-b:a", "192k",
#         "-pix_fmt", "yuv420p",
#         "-shortest",
#         output_path
#     ]
#     result = subprocess.run(cmd, capture_output=True, text=True)
#     if result.returncode != 0:
#         print("ffmpeg error:")
#         print(result.stderr[-2000:])
#         return None
#     print(f"Video saved to: {output_path}")
#     return output_path

# if __name__ == "__main__":
#     compose_video()



# video_service.py
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import subprocess
import json
import os
from pathlib import Path
import stable_whisper

VIDEO_DIR = Path("video_output")
FRAMES_DIR = Path("video_output/frames")
VIDEO_DIR.mkdir(exist_ok=True)
FRAMES_DIR.mkdir(exist_ok=True)

W, H = 1920, 1080

_model = None

def get_model(model_size="base"):
    global _model
    if _model is None:
        print(f"Loading Whisper model ({model_size})...")
        _model = stable_whisper.load_model(model_size)
        print("Model loaded.")
    return _model

def get_audio_duration(audio_path):
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

def wrap_text(text, max_chars=32):
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current += ("" if not current else " ") + word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:6]

def draw_speech_bubble(draw, text, side, font):
    lines = wrap_text(text)
    line_h = 36
    padding = 22
    bubble_w = 460
    bubble_h = len(lines) * line_h + padding * 2

    bx = 60 if side == "left" else W - bubble_w - 60
    by = 60

    draw.rounded_rectangle(
        [bx + 4, by + 4, bx + bubble_w + 4, by + bubble_h + 4],
        radius=16, fill=(0, 0, 0, 120)
    )
    draw.rounded_rectangle(
        [bx, by, bx + bubble_w, by + bubble_h],
        radius=16, fill=(255, 255, 255, 210), outline=(180, 140, 80, 255), width=3
    )
    for i, line in enumerate(lines):
        draw.text(
            (bx + padding, by + padding + i * line_h),
            line, fill=(30, 20, 10), font=font
        )

def draw_name_labels(draw, font_bold, active_speaker, author_a, author_b):
    name_a = "Franz Kafka"
    name_b = "Friedrich Nietzsche"
    alpha_a = 255 if active_speaker.lower() == author_a.lower() else 140
    alpha_b = 255 if active_speaker.lower() == author_b.lower() else 140
    draw.text((120, H - 100), name_a, fill=(255, 220, 150, alpha_a), font=font_bold)
    bbox = draw.textbbox((0, 0), name_b, font=font_bold)
    tw = bbox[2] - bbox[0]
    draw.text((W - tw - 120, H - 100), name_b, fill=(255, 220, 150, alpha_b), font=font_bold)

def apply_speaker_highlight(img, active_speaker, author_a):
    left_half = img.crop((0, 0, W // 2, H))
    right_half = img.crop((W // 2, 0, W, H))
    if active_speaker.lower() == author_a.lower():
        left_half = ImageEnhance.Brightness(left_half).enhance(1.15)
        right_half = ImageEnhance.Brightness(right_half).enhance(0.72)
    else:
        left_half = ImageEnhance.Brightness(left_half).enhance(0.72)
        right_half = ImageEnhance.Brightness(right_half).enhance(1.15)
    result = Image.new("RGB", (W, H))
    result.paste(left_half, (0, 0))
    result.paste(right_half, (W // 2, 0))
    return result

def draw_caption_bar(draw, caption_text, font_caption):
    """Burn caption text into the bottom center of the frame."""
    if not caption_text:
        return
    bar_h = 70
    bar_y = H - bar_h - 10
    # Semi-transparent black bar
    draw.rectangle([0, bar_y, W, bar_y + bar_h], fill=(0, 0, 0, 160))
    bbox = draw.textbbox((0, 0), caption_text, font=font_caption)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = bar_y + (bar_h - th) // 2
    # Outline for readability
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        draw.text((tx + dx, ty + dy), caption_text, fill=(0, 0, 0, 255), font=font_caption)
    draw.text((tx, ty), caption_text, fill=(255, 255, 255, 255), font=font_caption)

def generate_base_frame(speaker, text, author_a, author_b, bg_img, font, font_bold):
    """Generate the base frame (highlight + bubble + names) without caption."""
    img = apply_speaker_highlight(bg_img, speaker, author_a)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    side = "left" if speaker.lower() == author_a.lower() else "right"
    draw_speech_bubble(draw, text, side, font)
    draw_name_labels(draw, font_bold, speaker, author_a, author_b)
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")

def generate_frame_with_caption(base_img, caption_text, frame_path, font_caption):
    """Take a base frame and burn in the current caption chunk."""
    img = base_img.copy()
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw_caption_bar(draw, caption_text, font_caption)
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    img.save(frame_path, quality=92)

def align_words(audio_path, text, model):
    """Get word-level timestamps from stable-ts."""
    try:
        result = model.align(audio_path, text, language="en")
        return result.all_words()
    except Exception as e:
        print(f"  Alignment failed: {e}, using even split")
        return None

def even_split_words(text, duration):
    class FakeWord:
        def __init__(self, word, start, end):
            self.word = word
            self.start = start
            self.end = end
    words = text.split()
    n = max(len(words), 1)
    d = duration / n
    return [FakeWord(w, i*d, (i+1)*d) for i, w in enumerate(words)]

def compose_video(
    script_path="output_script.json",
    audio_dir="audio_output",
    output_path="video_output/debate.mp4",
    words_per_caption=6,
    model_size="base"
):
    with open(script_path) as f:
        data = json.load(f)

    script = data["script"]
    author_a = data["author_a"]
    author_b = data["author_b"]

    model = get_model(model_size)

    bg = Image.open("assets/background.jpg").convert("RGB")
    bg = bg.resize((W, H), Image.LANCZOS)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_caption = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
    except:
        font = ImageFont.load_default()
        font_bold = font
        font_caption = font

    print(f"Generating frames with burned-in captions...")
    frame_files = []  # list of (frame_path, duration_seconds)
    frame_idx = 0

    for i, line in enumerate(script):
        speaker = line["speaker"]
        text = line["text"]
        audio_seg = os.path.join(audio_dir, f"line_{i:03d}_{speaker}.mp3")

        if not os.path.exists(audio_seg):
            print(f"Missing: {audio_seg}")
            continue

        duration = get_audio_duration(audio_seg)
        print(f"  Line {i+1}/{len(script)} — {speaker} ({duration:.1f}s), aligning words...")

        # Get word timings
        words = align_words(audio_seg, text, model)
        if words is None:
            words = even_split_words(text, duration)

        # Generate base frame (bubble + highlight, no caption)
        base_img = generate_base_frame(speaker, text, author_a, author_b, bg, font, font_bold)

        # Group words into caption chunks
        chunks = []  # list of (caption_text, start_time, end_time)
        chunk_words = []
        chunk_start = None

        for w in words:
            word_str = w.word.strip()
            if not word_str:
                continue
            if chunk_start is None:
                chunk_start = w.start
            chunk_words.append((word_str, w.end))
            if len(chunk_words) >= words_per_caption:
                chunk_text = " ".join(wd for wd, _ in chunk_words)
                chunk_end = chunk_words[-1][1]
                chunks.append((chunk_text, chunk_start, chunk_end))
                chunk_words = []
                chunk_start = None

        # Flush remaining words
        if chunk_words:
            chunk_text = " ".join(wd for wd, _ in chunk_words)
            chunk_end = duration
            chunks.append((chunk_text, chunk_start, chunk_end))

        # Generate one frame image per caption chunk, with its duration
        prev_end = 0.0
        for caption_text, start, end in chunks:
            # If there's a gap before this chunk, emit a no-caption frame
            if start > prev_end + 0.05:
                frame_path = str(FRAMES_DIR / f"frame_{frame_idx:04d}.png")
                generate_frame_with_caption(base_img, "", frame_path, font_caption)
                frame_files.append((frame_path, start - prev_end))
                frame_idx += 1

            frame_path = str(FRAMES_DIR / f"frame_{frame_idx:04d}.png")
            generate_frame_with_caption(base_img, caption_text, frame_path, font_caption)
            frame_files.append((frame_path, end - start))
            frame_idx += 1
            prev_end = end

        # Any remaining time after last word
        if prev_end < duration - 0.05:
            frame_path = str(FRAMES_DIR / f"frame_{frame_idx:04d}.png")
            generate_frame_with_caption(base_img, "", frame_path, font_caption)
            frame_files.append((frame_path, duration - prev_end))
            frame_idx += 1

        print(f"    → {len(chunks)} caption chunks, {frame_idx} total frames so far")

    # Write concat file
    concat_path = "video_output/concat.txt"
    with open(concat_path, "w") as f:
        for frame_path, dur in frame_files:
            f.write(f"file '{os.path.abspath(frame_path)}'\n")
            f.write(f"duration {dur:.4f}\n")
        # ffmpeg concat needs last frame repeated
        f.write(f"file '{os.path.abspath(frame_files[-1][0])}'\n")

    print(f"\nTotal frames: {len(frame_files)}")
    print("Composing video with ffmpeg (no subtitle filter)...")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_path,
        "-i", os.path.join(audio_dir, "full_debate.mp3"),
        "-c:v", "libx264", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg error:")
        print(result.stderr[-2000:])
        return None

    print(f"✓ Video saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    compose_video()