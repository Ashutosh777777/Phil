"""
Phil entry point.

Generate a new set of debate videos and schedule them on YouTube, one part per day:

    python3 run_pipeline.py "The nature of existence"
    python3 run_pipeline.py "The burden of freedom" --time 19:30
    python3 run_pipeline.py "Is suffering necessary?" --start-date 2026-11-02 --time 18:00

Other modes:

    python3 run_pipeline.py "topic" --skip-upload     # generate only
    python3 run_pipeline.py --upload-only             # upload videos already in multipart_output/
    python3 run_pipeline.py --upload-only --dry-run   # show the schedule, upload nothing

The daily publish time defaults to PUBLISH_TIME / PUBLISH_TZ (see config.py or .env)
and can be overridden per run with --time. Part N goes public N-1 days after Part 1.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from config import DEFAULT_TOPIC, PUBLISH_TIME, PUBLISH_TZ

IMAGE_FOLDER = "/mnt/d/AI_Projects/GH/Phil/assets"
N8N_WEBHOOK = "http://localhost:5678/webhook/a3267b49-21b4-47a2-8bfd-c27cbf7a528e"
OUTPUT_DIR = Path("multipart_output")
SCRIPT_PATH = Path("output_script.json")

# YouTube rejects a publish time that is too close to now.
MIN_LEAD = timedelta(minutes=20)


# ── Image + video generation ──────────────────────────────────────────────────

def clear_old_images():
    for f in glob.glob(os.path.join(IMAGE_FOLDER, "*.png")) + glob.glob(os.path.join(IMAGE_FOLDER, "*.jpg")):
        os.remove(f)
        print(f"Deleted old image: {f}")


def generate_image():
    print("Generating new background image...")
    response = requests.post(N8N_WEBHOOK, timeout=120)
    if response.status_code == 200:
        image_path = os.path.join(IMAGE_FOLDER, "background.png")
        with open(image_path, "wb") as f:
            f.write(response.content)
        print(f"Image saved to {image_path}")
    else:
        raise Exception(f"Failed: {response.text}")


def ensure_services():
    """Best-effort start of the n8n and Qdrant containers."""
    try:
        subprocess.run(["docker", "start", "n8n", "qdrant"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        pass  # docker not on PATH; assume the services are already running


def video_parts():
    """Part videos in numeric order (part2 before part10)."""
    def part_no(p):
        m = re.search(r"(\d+)", p.stem)
        return int(m.group(1)) if m else 0
    return sorted(OUTPUT_DIR.glob("debate_part*.mp4"), key=part_no)


def run_video_pipeline(topic):
    # Remove last run's videos so a failed run can never leave stale ones to upload.
    for old in video_parts():
        old.unlink()
    subprocess.run([sys.executable, "multipart_pipeline.py", topic], check=True)
    if not video_parts():
        raise RuntimeError("Video pipeline finished but produced no videos")


# ── Scheduling + upload ───────────────────────────────────────────────────────

def parse_hhmm(value):
    try:
        hour, minute = (int(x) for x in value.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
        return hour, minute
    except ValueError:
        raise SystemExit(f"Invalid time '{value}'. Use 24-hour HH:MM, e.g. 18:00 or 07:30")


def build_schedule(count, hhmm, tz_name, start_date=None):
    """Publish datetimes for `count` parts: one per day at HH:MM in tz_name."""
    tz = ZoneInfo(tz_name)
    hour, minute = parse_hhmm(hhmm)
    now = datetime.now(tz)

    if start_date:
        first = datetime.strptime(start_date, "%Y-%m-%d").replace(
            hour=hour, minute=minute, tzinfo=tz)
        if first < now + MIN_LEAD:
            raise SystemExit(
                f"{first:%Y-%m-%d %H:%M %Z} is in the past or less than "
                f"{int(MIN_LEAD.total_seconds() // 60)} minutes away. Pick a later start."
            )
    else:
        first = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if first < now + MIN_LEAD:
            first += timedelta(days=1)

    return [first + timedelta(days=i) for i in range(count)]


def read_script_meta(topic_override=None):
    topic, author_a, author_b = topic_override, "kafka", "nietzsche"
    if SCRIPT_PATH.exists():
        data = json.loads(SCRIPT_PATH.read_text())
        topic = topic_override or data.get("topic")
        author_a = data.get("author_a", author_a)
        author_b = data.get("author_b", author_b)
    if not topic:
        raise SystemExit("No topic found. Pass one, e.g. --upload-only --topic \"...\"")
    return topic, author_a.title(), author_b.title()


def upload_all(topic, hhmm, tz_name, start_date=None, dry_run=False, force=False):
    parts = video_parts()
    if not parts:
        raise SystemExit(f"No debate_part*.mp4 files in {OUTPUT_DIR}/ to upload")

    topic, a, b = read_script_meta(topic)
    schedule = build_schedule(len(parts), hhmm, tz_name, start_date)

    print(f"\nTopic: {topic}")
    print("Publish schedule:")
    for p, when in zip(parts, schedule):
        print(f"  {p.name}  ->  {when:%a %d %b %Y, %H:%M %Z}")

    if dry_run:
        print("\nDry run: nothing uploaded.")
        return

    from youtube_uploader import upload_video

    n = len(parts)
    for i, (p, when) in enumerate(zip(parts, schedule), start=1):
        title = f"{a} vs {b}: {topic} (Part {i}/{n})"
        description = (
            f"Part {i} of {n}. An AI-generated debate between {a} and {b} on "
            f"\"{topic}\", grounded in their actual writings."
        )
        video_id = upload_video(
            str(p), title, description, publish_at=when,
            tags=["philosophy", a.lower(), b.lower(), "debate", "AI"], force=force,
        )
        print(f"Part {i}/{n} scheduled for {when:%d %b %H:%M %Z}: https://youtu.be/{video_id}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Generate Phil debate videos and schedule them on YouTube")
    ap.add_argument("topic", nargs="?", default=None,
                    help=f"Debate topic (default when generating: \"{DEFAULT_TOPIC}\")")
    ap.add_argument("--time", default=PUBLISH_TIME, metavar="HH:MM",
                    help=f"Daily publish time, 24h (default {PUBLISH_TIME})")
    ap.add_argument("--tz", default=PUBLISH_TZ,
                    help=f"Timezone for --time (default {PUBLISH_TZ})")
    ap.add_argument("--start-date", metavar="YYYY-MM-DD",
                    help="Date Part 1 goes public (default: next occurrence of --time)")
    ap.add_argument("--upload-only", action="store_true",
                    help="Skip generation; upload the videos already in multipart_output/")
    ap.add_argument("--skip-upload", action="store_true",
                    help="Generate videos but do not upload")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the publish schedule without uploading")
    ap.add_argument("--force", action="store_true",
                    help="Upload even if this exact file was uploaded before")
    args = ap.parse_args()

    if args.upload_only and args.skip_upload:
        ap.error("--upload-only and --skip-upload cancel each other out")

    parse_hhmm(args.time)  # fail fast on a bad time, before any slow work

    topic = args.topic
    if not args.upload_only:
        topic = topic or DEFAULT_TOPIC
        ensure_services()
        clear_old_images()
        generate_image()
        run_video_pipeline(topic)

    if not args.skip_upload:
        upload_all(topic, args.time, args.tz, args.start_date,
                   dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
