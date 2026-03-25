# video_service.py
from PIL import Image, ImageDraw, ImageFont
import subprocess
import json
import os
from pathlib import Path

VIDEO_DIR = Path("video_output")
FRAMES_DIR = Path("video_output/frames")
VIDEO_DIR.mkdir(exist_ok=True)
FRAMES_DIR.mkdir(exist_ok=True)

W, H = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
ACTIVE_COLOR = (30, 30, 30)
DIM_COLOR = (200, 200, 200)
BUBBLE_COLOR = (240, 240, 240)
BUBBLE_BORDER = (100, 100, 100)

def draw_stick_figure(draw, cx, cy, color):
    """Draw a stick figure centered at cx, cy."""
    # Head
    head_r = 35
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r],
                 outline=color, width=4)
    # Body
    draw.line([cx, cy + head_r, cx, cy + head_r + 90], fill=color, width=4)
    # Arms
    draw.line([cx - 55, cy + head_r + 30, cx + 55, cy + head_r + 30],
              fill=color, width=4)
    # Left leg
    draw.line([cx, cy + head_r + 90, cx - 45, cy + head_r + 160],
              fill=color, width=4)
    # Right leg
    draw.line([cx, cy + head_r + 90, cx + 45, cy + head_r + 160],
              fill=color, width=4)

def wrap_text(text, max_chars=45):
    """Wrap text into lines of max_chars."""
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
    return lines

def draw_speech_bubble(draw, text, cx, cy_top, side="left"):
    """Draw a speech bubble above the stick figure."""
    lines = wrap_text(text, max_chars=40)
    font_size = 22
    line_h = font_size + 8
    padding = 18
    bubble_w = 380
    bubble_h = len(lines) * line_h + padding * 2

    if side == "left":
        bx = cx - bubble_w // 2
    else:
        bx = cx - bubble_w // 2

    by = cy_top - bubble_h - 30

    # Bubble background
    draw.rounded_rectangle(
        [bx, by, bx + bubble_w, by + bubble_h],
        radius=15, fill=BUBBLE_COLOR, outline=BUBBLE_BORDER, width=2
    )

    # Bubble tail pointing down to figure
    tail_x = cx
    draw.polygon([
        (tail_x - 12, by + bubble_h),
        (tail_x + 12, by + bubble_h),
        (tail_x, by + bubble_h + 25)
    ], fill=BUBBLE_COLOR, outline=BUBBLE_BORDER)

    # Text inside bubble
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    for i, line in enumerate(lines):
        draw.text((bx + padding, by + padding + i * line_h), line, fill=BLACK, font=font)

def draw_name(draw, name, cx, cy_bottom):
    """Draw author name below figure."""
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), name, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy_bottom + 10), name, fill=BLACK, font=font)

def generate_frame(speaker, text, author_a, author_b, frame_path):
    """Generate one debate frame."""
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # Figure centers
    cx_a = W // 4          # Left figure (author_a)
    cx_b = (W * 3) // 4    # Right figure (author_b)
    cy_fig = H // 2 - 30   # Vertical center of figures

    # Facing lines — figures lean inward slightly
    is_a_speaking = speaker.lower() == author_a.lower()

    color_a = ACTIVE_COLOR if is_a_speaking else DIM_COLOR
    color_b = DIM_COLOR if is_a_speaking else ACTIVE_COLOR

    draw_stick_figure(draw, cx_a, cy_fig, color_a)
    draw_stick_figure(draw, cx_b, cy_fig, color_b)

    # Name labels
    name_a = author_a.capitalize()
    name_b = author_b.capitalize()
    draw_name(draw, name_a, cx_a, cy_fig + 200)
    draw_name(draw, name_b, cx_b, cy_fig + 200)

    # Speech bubble on active speaker
    bubble_cy = cy_fig - 35
    if is_a_speaking:
        draw_speech_bubble(draw, text, cx_a, bubble_cy, side="left")
    else:
        draw_speech_bubble(draw, text, cx_b, bubble_cy, side="right")

    # Divider line between figures
    draw.line([(W // 2, 100), (W // 2, H - 100)], fill=(220, 220, 220), width=2)

    img.save(frame_path)

def get_audio_duration(audio_path):
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

def compose_video(
    script_path="output_script.json",
    audio_dir="audio_output",
    output_path="video_output/debate.mp4"
):
    with open(script_path) as f:
        data = json.load(f)

    script = data["script"]
    author_a = data["author_a"]
    author_b = data["author_b"]

    print(f"🎬 Generating {len(script)} frames...")

    # Generate one frame per dialogue turn
    frame_files = []
    durations = []

    for i, line in enumerate(script):
        speaker = line["speaker"]
        text = line["text"]

        # Match audio segment file
        audio_seg = os.path.join(audio_dir, f"line_{i:03d}_{speaker}.mp3")
        if not os.path.exists(audio_seg):
            print(f"⚠️  Missing audio segment: {audio_seg}")
            continue

        duration = get_audio_duration(audio_seg)
        durations.append(duration)

        frame_path = str(FRAMES_DIR / f"frame_{i:03d}.png")
        generate_frame(speaker, text, author_a, author_b, frame_path)
        frame_files.append((frame_path, duration))
        print(f"  ✅ Frame {i+1}/{len(script)} — {speaker} ({duration:.1f}s)")

    # Build ffmpeg concat input file
    concat_path = "video_output/concat.txt"
    with open(concat_path, "w") as f:
        for frame_path, duration in frame_files:
            f.write(f"file '{os.path.abspath(frame_path)}'\n")
            f.write(f"duration {duration}\n")
        # Repeat last frame to avoid ffmpeg cutting short
        f.write(f"file '{os.path.abspath(frame_files[-1][0])}'\n")

    print("\n⚙️  Composing video with ffmpeg...")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_path,
        "-i", os.path.join(audio_dir, "full_debate.mp3"),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ ffmpeg error:")
        print(result.stderr[-2000:])
        return None

    print(f"✅ Video saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    compose_video()