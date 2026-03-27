# # #!/usr/bin/env python3
# # """
# # Multi-Part Video Pipeline
# # Orchestrates the generation of multi-part debate videos.
# # """

# # import json
# # import subprocess
# # import shutil
# # from pathlib import Path
# # from split_script import split_script

# # def generate_full_debate(topic, author_a="kafka", author_b="nietzsche", turns=6):
# #     """
# #     Generate a full debate script via the RAG service.
    
# #     Args:
# #         topic: Debate topic
# #         author_a: First author
# #         author_b: Second author
# #         turns: Total number of turns (default 6 for 3 parts)
    
# #     Returns:
# #         Path to the generated script file
# #     """
# #     import requests
    
# #     print(f"\n{'='*60}")
# #     print(f"GENERATING FULL DEBATE")
# #     print(f"{'='*60}")
# #     print(f"Topic: {topic}")
# #     print(f"Author A: {author_a}")
# #     print(f"Author B: {author_b}")
# #     print(f"Turns: {turns}")
# #     print(f"{'='*60}\n")
    
# #     # Call the RAG service
# #     response = requests.post(
# #         "http://localhost:8000/debate",
# #         json={
# #             "topic": topic,
# #             "author_a": author_a,
# #             "author_b": author_b,
# #             "turns": turns
# #         }
# #     )
    
# #     if response.status_code != 200:
# #         raise Exception(f"RAG service error: {response.text}")
    
# #     data = response.json()
    
# #     # Save the full script
# #     output_path = "output_script.json"
# #     with open(output_path, 'w') as f:
# #         json.dump(data, f, indent=2)
    
# #     print(f"✓ Full debate script saved to: {output_path}\n")
    
# #     return output_path

# # def generate_audio_for_part(part_script_path, audio_output_dir):
# #     """
# #     Generate audio files for a specific part.
    
# #     Args:
# #         part_script_path: Path to the part script JSON
# #         audio_output_dir: Directory to save audio files
# #     """
# #     from audio_service import generate_audio
    
# #     # Create part-specific audio directory
# #     part_dir = Path(audio_output_dir)
# #     part_dir.mkdir(parents=True, exist_ok=True)
    
# #     print(f"\nGenerating audio for: {part_script_path}")
# #     generate_audio(script_path=part_script_path, output_dir=str(part_dir))
    
# #     return str(part_dir)

# # def generate_video_for_part(part_script_path, audio_dir, video_output_path):
# #     """
# #     Generate video for a specific part.
    
# #     Args:
# #         part_script_path: Path to the part script JSON
# #         audio_dir: Directory containing audio files
# #         video_output_path: Output path for the video
# #     """
# #     from video_service import compose_video
    
# #     print(f"\nGenerating video for: {part_script_path}")
# #     result = compose_video(
# #         script_path=part_script_path,
# #         audio_dir=audio_dir,
# #         output_path=video_output_path
# #     )
    
# #     return result

# # def generate_multipart_videos(
# #     topic,
# #     author_a="kafka",
# #     author_b="nietzsche",
# #     turns=6,
# #     turns_per_part=2,
# #     output_base_dir="multipart_output"
# # ):
# #     """
# #     Complete pipeline: Generate debate, split, and create videos for all parts.
    
# #     Args:
# #         topic: Debate topic
# #         author_a: First author
# #         author_b: Second author
# #         turns: Total number of turns
# #         turns_per_part: Turns per video part
# #         output_base_dir: Base directory for all outputs
# #     """
# #     print(f"\n{'#'*60}")
# #     print(f"# MULTI-PART VIDEO GENERATION PIPELINE")
# #     print(f"{'#'*60}\n")
    
# #     # Create base output directory
# #     base_path = Path(output_base_dir)
# #     base_path.mkdir(exist_ok=True)
    
# #     # Step 1: Generate full debate
# #     full_script_path = generate_full_debate(topic, author_a, author_b, turns)
    
# #     # Step 2: Split into parts
# #     parts_dir = base_path / "parts"
# #     part_files = split_script(
# #         input_path=full_script_path,
# #         turns_per_part=turns_per_part,
# #         output_dir=str(parts_dir)
# #     )
    
# #     # Step 3: Generate audio and video for each part
# #     num_parts = len(part_files)
# #     video_files = []
    
# #     print(f"\n{'='*60}")
# #     print(f"GENERATING AUDIO & VIDEO FOR ALL PARTS")
# #     print(f"{'='*60}\n")
    
# #     for i, part_file in enumerate(part_files, 1):
# #         print(f"\n{'─'*60}")
# #         print(f"PROCESSING PART {i}/{num_parts}")
# #         print(f"{'─'*60}")
        
# #         # Create part-specific directories
# #         part_audio_dir = base_path / f"audio_part{i}"
# #         part_video_path = base_path / f"debate_part{i}.mp4"
        
# #         # Generate audio
# #         generate_audio_for_part(part_file, str(part_audio_dir))
        
# #         # Generate video
# #         video_path = generate_video_for_part(
# #             part_file,
# #             str(part_audio_dir),
# #             str(part_video_path)
# #         )
        
# #         if video_path:
# #             video_files.append(video_path)
# #             print(f"\n✓ Part {i} video saved to: {video_path}")
    
# #     # Final summary
# #     print(f"\n{'#'*60}")
# #     print(f"# PIPELINE COMPLETE!")
# #     print(f"{'#'*60}")
# #     print(f"\nGenerated {len(video_files)} video parts:")
# #     for i, vf in enumerate(video_files, 1):
# #         print(f"  Part {i}: {vf}")
# #     print(f"\nAll files saved in: {output_base_dir}/")
# #     print(f"{'#'*60}\n")
    
# #     return video_files

# # def main():
# #     """Command-line interface for multi-part video generation."""
# #     import argparse
    
# #     parser = argparse.ArgumentParser(
# #         description="Generate multi-part debate videos"
# #     )
# #     parser.add_argument(
# #         "topic",
# #         help="Debate topic"
# #     )
# #     parser.add_argument(
# #         "--author-a",
# #         default="kafka",
# #         help="First author (default: kafka)"
# #     )
# #     parser.add_argument(
# #         "--author-b",
# #         default="nietzsche",
# #         help="Second author (default: nietzsche)"
# #     )
# #     parser.add_argument(
# #         "--turns",
# #         type=int,
# #         default=6,
# #         help="Total number of turns (default: 6)"
# #     )
# #     parser.add_argument(
# #         "--turns-per-part",
# #         type=int,
# #         default=2,
# #         help="Turns per video part (default: 2)"
# #     )
# #     parser.add_argument(
# #         "--output-dir",
# #         default="multipart_output",
# #         help="Output directory (default: multipart_output/)"
# #     )
    
# #     args = parser.parse_args()
    
# #     # Run the pipeline
# #     generate_multipart_videos(
# #         topic=args.topic,
# #         author_a=args.author_a,
# #         author_b=args.author_b,
# #         turns=args.turns,
# #         turns_per_part=args.turns_per_part,
# #         output_base_dir=args.output_dir
# #     )

# # if __name__ == "__main__":
# #     main()


# #!/usr/bin/env python3
# """
# Multi-Part Video Pipeline
# Orchestrates the generation of multi-part debate videos.
# Auto-starts and stops the RAG service (FastAPI) as needed.
# """

# import json
# import subprocess
# import shutil
# import time
# import sys
# import signal
# import atexit
# from pathlib import Path
# from split_script import split_script

# # Global reference to the server process so we can clean it up
# _server_process = None

# def start_rag_server():
#     """
#     Start the RAG FastAPI server as a subprocess.
#     Waits until it's ready to accept connections.
#     Returns the subprocess.Popen object.
#     """
#     import requests

#     global _server_process

#     print("\n🚀 Starting RAG service...")

#     _server_process = subprocess.Popen(
#         ["uvicorn", "rag_service:app", "--host", "0.0.0.0", "--port", "8000"],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL
#     )

#     # Register cleanup so the server always shuts down on exit
#     atexit.register(stop_rag_server)

#     # Wait up to 30 seconds for the server to become ready
#     for attempt in range(30):
#         time.sleep(1)
#         try:
#             resp = requests.get("http://localhost:8000/health", timeout=2)
#             if resp.status_code == 200:
#                 print("✓ RAG service is up and running\n")
#                 return _server_process
#         except Exception:
#             pass
#         print(f"  Waiting for server... ({attempt + 1}/30)", end="\r")

#     # If we get here the server never came up
#     stop_rag_server()
#     raise RuntimeError(
#         "RAG service failed to start within 30 seconds. "
#         "Check that uvicorn and all dependencies are installed."
#     )

# def stop_rag_server():
#     """
#     Gracefully terminate the RAG server subprocess.
#     Safe to call multiple times.
#     """
#     global _server_process
#     if _server_process is not None:
#         print("\n🛑 Shutting down RAG service...")
#         _server_process.terminate()
#         try:
#             _server_process.wait(timeout=5)
#         except subprocess.TimeoutExpired:
#             _server_process.kill()
#         _server_process = None
#         print("✓ RAG service stopped\n")

# def is_rag_server_running():
#     """Return True if the RAG service is already up on port 8000."""
#     import requests
#     try:
#         resp = requests.get("http://localhost:8000/health", timeout=2)
#         return resp.status_code == 200
#     except Exception:
#         return False

# def generate_full_debate(topic, author_a="kafka", author_b="nietzsche", turns=6):
#     """
#     Generate a full debate script via the RAG service.

#     Args:
#         topic: Debate topic
#         author_a: First author
#         author_b: Second author
#         turns: Total number of turns (default 6 for 3 parts)

#     Returns:
#         Path to the generated script file
#     """
#     import requests

#     print(f"\n{'='*60}")
#     print(f"GENERATING FULL DEBATE")
#     print(f"{'='*60}")
#     print(f"Topic: {topic}")
#     print(f"Author A: {author_a}")
#     print(f"Author B: {author_b}")
#     print(f"Turns: {turns}")
#     print(f"{'='*60}\n")

#     # Call the RAG service
#     response = requests.post(
#         "http://localhost:8000/debate",
#         json={
#             "topic": topic,
#             "author_a": author_a,
#             "author_b": author_b,
#             "turns": turns
#         }
#     )

#     if response.status_code != 200:
#         raise Exception(f"RAG service error: {response.text}")

#     data = response.json()

#     # Save the full script
#     output_path = "output_script.json"
#     with open(output_path, 'w') as f:
#         json.dump(data, f, indent=2)

#     print(f"✓ Full debate script saved to: {output_path}\n")

#     return output_path

#     """
#     Generate audio files for a specific part.

#     Args:
#         part_script_path: Path to the part script JSON
#         audio_output_dir: Directory to save audio files
#     """
#     import asyncio
#     from voice_service import generate_audio_from_script

#     part_dir = Path(audio_output_dir)
#     part_dir.mkdir(parents=True, exist_ok=True)

#     # Load the script turns from the JSON file
#     with open(part_script_path, 'r') as f:
#         script_data = json.load(f)

#     # The JSON may be a dict with a "turns" key, or a bare list — handle both
#     if isinstance(script_data, dict):
#         script = script_data.get("script", [])
#     else:
#         script = script_data

#     print(f"\nGenerating audio for: {part_script_path}")
#     asyncio.run(generate_audio_from_script(script, str(part_dir)))

#     return str(part_dir)

# def generate_video_for_part(part_script_path, audio_dir, video_output_path):
#     """
#     Generate video for a specific part.

#     Args:
#         part_script_path: Path to the part script JSON
#         audio_dir: Directory containing audio files
#         video_output_path: Output path for the video
#     """
#     from video_service import compose_video

#     print(f"\nGenerating video for: {part_script_path}")
#     result = compose_video(
#         script_path=part_script_path,
#         audio_dir=audio_dir,
#         output_path=video_output_path
#     )

#     return result

# def generate_multipart_videos(
#     topic,
#     author_a="kafka",
#     author_b="nietzsche",
#     turns=6,
#     turns_per_part=2,
#     output_base_dir="multipart_output"
# ):
#     """
#     Complete pipeline: auto-start server → generate debate → split → create videos.

#     Args:
#         topic: Debate topic
#         author_a: First author
#         author_b: Second author
#         turns: Total number of turns
#         turns_per_part: Turns per video part
#         output_base_dir: Base directory for all outputs
#     """
#     print(f"\n{'#'*60}")
#     print(f"# MULTI-PART VIDEO GENERATION PIPELINE")
#     print(f"{'#'*60}\n")

#     # ── Auto-start the RAG server if it isn't already up ──────────────────
#     server_was_already_running = is_rag_server_running()
#     if server_was_already_running:
#         print("ℹ️  RAG service already running — skipping auto-start\n")
#     else:
#         start_rag_server()
#     # ──────────────────────────────────────────────────────────────────────

#     try:
#         # Create base output directory
#         base_path = Path(output_base_dir)
#         base_path.mkdir(exist_ok=True)

#         # Step 1: Generate full debate
#         full_script_path = generate_full_debate(topic, author_a, author_b, turns)

#         # Step 2: Split into parts
#         parts_dir = base_path / "parts"
#         part_files = split_script(
#             input_path=full_script_path,
#             turns_per_part=turns_per_part,
#             output_dir=str(parts_dir)
#         )

#         # Step 3: Generate audio and video for each part
#         num_parts = len(part_files)
#         video_files = []

#         print(f"\n{'='*60}")
#         print(f"GENERATING AUDIO & VIDEO FOR ALL PARTS")
#         print(f"{'='*60}\n")

#         for i, part_file in enumerate(part_files, 1):
#             print(f"\n{'─'*60}")
#             print(f"PROCESSING PART {i}/{num_parts}")
#             print(f"{'─'*60}")

#             part_audio_dir = base_path / f"audio_part{i}"
#             part_video_path = base_path / f"debate_part{i}.mp4"

#             generate_audio_for_part(part_file, str(part_audio_dir))

#             video_path = generate_video_for_part(
#                 part_file,
#                 str(part_audio_dir),
#                 str(part_video_path)
#             )

#             if video_path:
#                 video_files.append(video_path)
#                 print(f"\n✓ Part {i} video saved to: {video_path}")

#     finally:
#         # Only shut down the server if WE started it
#         if not server_was_already_running:
#             stop_rag_server()

#     # Final summary
#     print(f"\n{'#'*60}")
#     print(f"# PIPELINE COMPLETE!")
#     print(f"{'#'*60}")
#     print(f"\nGenerated {len(video_files)} video parts:")
#     for i, vf in enumerate(video_files, 1):
#         print(f"  Part {i}: {vf}")
#     print(f"\nAll files saved in: {output_base_dir}/")
#     print(f"{'#'*60}\n")

#     return video_files

# def main():
#     """Command-line interface for multi-part video generation."""
#     import argparse

#     parser = argparse.ArgumentParser(
#         description="Generate multi-part debate videos"
#     )
#     parser.add_argument(
#         "topic",
#         help="Debate topic"
#     )
#     parser.add_argument(
#         "--author-a",
#         default="kafka",
#         help="First author (default: kafka)"
#     )
#     parser.add_argument(
#         "--author-b",
#         default="nietzsche",
#         help="Second author (default: nietzsche)"
#     )
#     parser.add_argument(
#         "--turns",
#         type=int,
#         default=6,
#         help="Total number of turns (default: 6)"
#     )
#     parser.add_argument(
#         "--turns-per-part",
#         type=int,
#         default=2,
#         help="Turns per video part (default: 2)"
#     )
#     parser.add_argument(
#         "--output-dir",
#         default="multipart_output",
#         help="Output directory (default: multipart_output/)"
#     )

#     args = parser.parse_args()

#     generate_multipart_videos(
#         topic=args.topic,
#         author_a=args.author_a,
#         author_b=args.author_b,
#         turns=args.turns,
#         turns_per_part=args.turns_per_part,
#         output_base_dir=args.output_dir
#     )

# if __name__ == "__main__":
#     main()

"""
Multi-Part Video Pipeline
Orchestrates the generation of multi-part debate videos.
Auto-starts and stops the RAG service (FastAPI) as needed.
"""

import json
import subprocess
import shutil
import time
import sys
import signal
import atexit
import asyncio
from pathlib import Path
from split_script import split_script

# Global reference to the server process so we can clean it up
_server_process = None

def start_rag_server():
    """
    Start the RAG FastAPI server as a subprocess.
    Waits until it's ready to accept connections.
    Returns the subprocess.Popen object.
    """
    import requests

    global _server_process

    print("\n🚀 Starting RAG service...")

    _server_process = subprocess.Popen(
        ["uvicorn", "rag_service:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Register cleanup so the server always shuts down on exit
    atexit.register(stop_rag_server)

    # Wait up to 30 seconds for the server to become ready
    for attempt in range(30):
        time.sleep(1)
        try:
            resp = requests.get("http://localhost:8000/health", timeout=2)
            if resp.status_code == 200:
                print("✓ RAG service is up and running\n")
                return _server_process
        except Exception:
            pass
        print(f"  Waiting for server... ({attempt + 1}/30)", end="\r")

    # If we get here the server never came up
    stop_rag_server()
    raise RuntimeError(
        "RAG service failed to start within 30 seconds. "
        "Check that uvicorn and all dependencies are installed."
    )

def stop_rag_server():
    """
    Gracefully terminate the RAG server subprocess.
    Safe to call multiple times.
    """
    global _server_process
    if _server_process is not None:
        print("\n🛑 Shutting down RAG service...")
        _server_process.terminate()
        try:
            _server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _server_process.kill()
        _server_process = None
        print("✓ RAG service stopped\n")

def is_rag_server_running():
    """Return True if the RAG service is already up on port 8000."""
    import requests
    try:
        resp = requests.get("http://localhost:8000/health", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False

def generate_full_debate(topic, author_a="kafka", author_b="nietzsche", turns=6):
    """
    Generate a full debate script via the RAG service.

    Args:
        topic: Debate topic
        author_a: First author
        author_b: Second author
        turns: Total number of turns (default 6 for 3 parts)

    Returns:
        Path to the generated script file
    """
    import requests

    print(f"\n{'='*60}")
    print(f"GENERATING FULL DEBATE")
    print(f"{'='*60}")
    print(f"Topic: {topic}")
    print(f"Author A: {author_a}")
    print(f"Author B: {author_b}")
    print(f"Turns: {turns}")
    print(f"{'='*60}\n")

    # Call the RAG service
    response = requests.post(
        "http://localhost:8000/debate",
        json={
            "topic": topic,
            "author_a": author_a,
            "author_b": author_b,
            "turns": turns
        }
    )

    if response.status_code != 200:
        raise Exception(f"RAG service error: {response.text}")

    data = response.json()

    # Save the full script
    output_path = "output_script.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ Full debate script saved to: {output_path}\n")

    return output_path

def generate_audio_for_part(part_script_path, audio_output_dir):
    """
    Generate audio files for a specific part.

    Args:
        part_script_path: Path to the part script JSON
        audio_output_dir: Directory to save audio files
    """
    from voice_service import generate_audio_from_script

    part_dir = Path(audio_output_dir)
    part_dir.mkdir(parents=True, exist_ok=True)

    # Load the script turns from the JSON file
    with open(part_script_path, 'r') as f:
        script_data = json.load(f)

    # Extract the list of turns from the "script" key
    if isinstance(script_data, dict):
        script = script_data.get("script", [])
    else:
        script = script_data

    print(f"\nGenerating audio for: {part_script_path}")
    asyncio.run(generate_audio_from_script(script, str(part_dir)))

    return str(part_dir)

def generate_video_for_part(part_script_path, audio_dir, video_output_path):
    """
    Generate video for a specific part.

    Args:
        part_script_path: Path to the part script JSON
        audio_dir: Directory containing audio files
        video_output_path: Output path for the video
    """
    from video_service import compose_video

    print(f"\nGenerating video for: {part_script_path}")
    result = compose_video(
        script_path=part_script_path,
        audio_dir=audio_dir,
        output_path=video_output_path
    )

    return result

def generate_multipart_videos(
    topic,
    author_a="kafka",
    author_b="nietzsche",
    turns=6,
    turns_per_part=2,
    output_base_dir="multipart_output"
):
    """
    Complete pipeline: auto-start server → generate debate → split → create videos.

    Args:
        topic: Debate topic
        author_a: First author
        author_b: Second author
        turns: Total number of turns
        turns_per_part: Turns per video part
        output_base_dir: Base directory for all outputs
    """
    print(f"\n{'#'*60}")
    print(f"# MULTI-PART VIDEO GENERATION PIPELINE")
    print(f"{'#'*60}\n")

    # ── Auto-start the RAG server if it isn't already up ──────────────────
    server_was_already_running = is_rag_server_running()
    if server_was_already_running:
        print("ℹ️  RAG service already running — skipping auto-start\n")
    else:
        start_rag_server()
    # ──────────────────────────────────────────────────────────────────────

    try:
        # Create base output directory
        base_path = Path(output_base_dir)
        base_path.mkdir(exist_ok=True)

        # Step 1: Generate full debate
        full_script_path = generate_full_debate(topic, author_a, author_b, turns)

        # Step 2: Split into parts
        parts_dir = base_path / "parts"
        part_files = split_script(
            input_path=full_script_path,
            turns_per_part=turns_per_part,
            output_dir=str(parts_dir)
        )

        # Step 3: Generate audio and video for each part
        num_parts = len(part_files)
        video_files = []

        print(f"\n{'='*60}")
        print(f"GENERATING AUDIO & VIDEO FOR ALL PARTS")
        print(f"{'='*60}\n")

        for i, part_file in enumerate(part_files, 1):
            print(f"\n{'─'*60}")
            print(f"PROCESSING PART {i}/{num_parts}")
            print(f"{'─'*60}")

            part_audio_dir = base_path / f"audio_part{i}"
            part_video_path = base_path / f"debate_part{i}.mp4"

            generate_audio_for_part(part_file, str(part_audio_dir))

            video_path = generate_video_for_part(
                part_file,
                str(part_audio_dir),
                str(part_video_path)
            )

            if video_path:
                video_files.append(video_path)
                print(f"\n✓ Part {i} video saved to: {video_path}")

    finally:
        # Only shut down the server if WE started it
        if not server_was_already_running:
            stop_rag_server()

    # Final summary
    print(f"\n{'#'*60}")
    print(f"# PIPELINE COMPLETE!")
    print(f"{'#'*60}")
    print(f"\nGenerated {len(video_files)} video parts:")
    for i, vf in enumerate(video_files, 1):
        print(f"  Part {i}: {vf}")
    print(f"\nAll files saved in: {output_base_dir}/")
    print(f"{'#'*60}\n")

    return video_files

def main():
    """Command-line interface for multi-part video generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate multi-part debate videos"
    )
    parser.add_argument(
        "topic",
        help="Debate topic"
    )
    parser.add_argument(
        "--author-a",
        default="kafka",
        help="First author (default: kafka)"
    )
    parser.add_argument(
        "--author-b",
        default="nietzsche",
        help="Second author (default: nietzsche)"
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=6,
        help="Total number of turns (default: 6)"
    )
    parser.add_argument(
        "--turns-per-part",
        type=int,
        default=2,
        help="Turns per video part (default: 2)"
    )
    parser.add_argument(
        "--output-dir",
        default="multipart_output",
        help="Output directory (default: multipart_output/)"
    )

    args = parser.parse_args()

    generate_multipart_videos(
        topic=args.topic,
        author_a=args.author_a,
        author_b=args.author_b,
        turns=args.turns,
        turns_per_part=args.turns_per_part,
        output_base_dir=args.output_dir
    )

if __name__ == "__main__":
    main()