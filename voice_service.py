"""
Voice service file
"""

import asyncio
import edge_tts
from pydub import AudioSegment
import os

# Voice assignments
VOICES = {
    "kafka": "en-US-GuyNeural",
    "nietzsche": "en-GB-RyanNeural"
}

async def synthesize_line(text: str, speaker: str, output_path: str):
    voice = VOICES.get(speaker.lower(), "en-US-GuyNeural")  # .lower() added
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

async def generate_audio_from_script(script: list, output_dir: str = "audio_output"):
    os.makedirs(output_dir, exist_ok=True)
    segment_paths = []

    for i, line in enumerate(script):
        speaker = line["speaker"]
        text = line["text"]
        path = os.path.join(output_dir, f"line_{i:03d}_{speaker}.mp3")
        print(f"Synthesizing line {i+1}/{len(script)} — {speaker}")
        await synthesize_line(text, speaker, path)
        segment_paths.append(path)

    print("Stitching segments...")
    combined = AudioSegment.empty()
    pause = AudioSegment.silent(duration=600)

    for path in segment_paths:
        segment = AudioSegment.from_mp3(path)
        combined += segment + pause

    final_path = os.path.join(output_dir, "full_debate.mp3")
    combined.export(final_path, format="mp3")
    print(f"✓ Audio saved to: {final_path}")
    return final_path, segment_paths

if __name__ == "__main__":
    test_script = [
        {"speaker": "Kafka", "text": "We live in a world of invisible walls. The system devours us before we even understand what it is."},
        {"speaker": "Nietzsche", "text": "Stop waiting to be devoured. Become the one who devours. Will yourself beyond the walls."},
        {"speaker": "Kafka", "text": "But what if the very act of willing is itself another trap? Another corridor that leads nowhere?"},
        {"speaker": "Nietzsche", "text": "Then make the corridor your home. Dance in it. That is what it means to overcome."}
    ]

    asyncio.run(generate_audio_from_script(test_script))