# caption_service.py
import json
import os
import subprocess
import stable_whisper

# Loaded once and reused across calls to avoid reloading on every run
_model = None

def get_model(model_size="base"):
    global _model
    if _model is None:
        print(f"Loading stable-ts Whisper model ({model_size})...")
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

def seconds_to_srt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def generate_captions(
    script_path="output_script.json",
    audio_dir="audio_output",
    pause=0.6,
    model_size="base",
    words_per_line=6
):
    with open(script_path) as f:
        data = json.load(f)

    script = data["script"]
    model = get_model(model_size)

    entries = []
    idx = 1
    time_offset = 0.0

    for i, line in enumerate(script):
        speaker = line["speaker"]
        text = line["text"]
        audio_path = os.path.join(audio_dir, f"line_{i:03d}_{speaker}.mp3")

        if not os.path.exists(audio_path):
            print(f"Missing: {audio_path}")
            continue

        duration = get_audio_duration(audio_path)
        print(f"  Aligning line {i+1}/{len(script)} — {speaker} ({duration:.1f}s)")

        # Use stable-ts to align the known text to the audio segment.
        # This gives accurate word-level timestamps without full transcription.
        try:
            result = model.align(audio_path, text, language="en")
            words = result.all_words()  # list of WordTiming objects with .word, .start, .end
        except Exception as e:
            print(f"  Alignment failed for line {i}, falling back to even split. Error: {e}")
            words = _even_split_words(text, duration)

        # Offset word timestamps by how far into the full audio we are
        # and group into caption chunks of N words
        chunk = []
        chunk_start = None

        for w in words:
            abs_start = time_offset + w.start
            abs_end = time_offset + w.end
            word_str = w.word.strip()

            if not word_str:
                continue

            if chunk_start is None:
                chunk_start = abs_start

            chunk.append((word_str, abs_end))

            if len(chunk) >= words_per_line:
                chunk_text = " ".join(wd for wd, _ in chunk)
                chunk_end = chunk[-1][1]
                entries.append(
                    f"{idx}\n"
                    f"{seconds_to_srt(chunk_start)} --> {seconds_to_srt(chunk_end)}\n"
                    f"{chunk_text}\n"
                )
                idx += 1
                chunk = []
                chunk_start = None

        # Flush any remaining words in the last chunk
        if chunk:
            chunk_text = " ".join(wd for wd, _ in chunk)
            chunk_end = time_offset + duration
            entries.append(
                f"{idx}\n"
                f"{seconds_to_srt(chunk_start)} --> {seconds_to_srt(chunk_end)}\n"
                f"{chunk_text}\n"
            )
            idx += 1

        time_offset += duration + pause

    srt_path = "captions.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))

    print(f"\ncaptions.srt saved — {len(entries)} caption entries, {time_offset:.1f}s total")
    return srt_path


def _even_split_words(text, duration):
    """Fallback: evenly distribute word timings if alignment fails."""
    class FakeWord:
        def __init__(self, word, start, end):
            self.word = word
            self.start = start
            self.end = end

    words = text.split()
    n = max(len(words), 1)
    word_dur = duration / n
    return [FakeWord(w, i * word_dur, (i + 1) * word_dur) for i, w in enumerate(words)]


if __name__ == "__main__":
    generate_captions()