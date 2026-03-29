# Phil 🎭

**AI-generated debate videos between philosophers — grounded in their actual writings.**

Kafka and Nietzsche argue about existence. The pipeline writes the script, speaks the lines, and cuts the video. Fully automated, end to end.

---

## What it does

Give Phil a topic. It generates a YouTube/Instagram-ready debate video where two philosophers argue in their own voice — not generic LLM output, but responses grounded via RAG against their actual texts stored in a vector database.

```
Topic: "The nature of existence"
     ↓
Background image (HuggingFace / n8n)
     ↓
Debate script (RAG from Qdrant + Groq LLM)
     ↓
Audio per line (TTS)
     ↓
Word-level caption timing (Whisper / stable-ts)
     ↓
Frames + ffmpeg → debate_part1.mp4, part2.mp4, part3.mp4
```

---

## Why it's cool

Most "AI philosopher" content is just a chatbot playing dress-up. Phil is different — every line of dialogue is retrieved from and grounded in the philosopher's real writing. Kafka's responses draw from his actual prose. Nietzsche's from his. The LLM voices the character; the RAG keeps it honest.

The whole thing runs in one command.

---

## Tech stack

| Layer | Tool |
|---|---|
| Orchestration | n8n (Docker) |
| Image generation | HuggingFace — `stabilityai/stable-diffusion-xl-base-1.0` |
| Vector database | Qdrant (Docker) |
| Embeddings | FastEmbed |
| RAG + script generation | FastAPI + Groq (`llama-3.3-70b-versatile`) |
| Text-to-speech | Edge TTS |
| Caption alignment | stable-ts (Whisper-based word-level timing) |
| Video composition | ffmpeg + Pillow |
| Runtime | Python 3.12, WSL2 |

---

## Project structure

```
Phil/
├── run_pipeline.py           # Entry point — triggers n8n then runs video pipeline
├── multipart_pipeline.py     # Orchestrates debate → audio → video for all parts
├── rag_service.py            # FastAPI RAG service (Qdrant + Groq)
├── video_service.py          # Frame generation + ffmpeg composition
├── voice_service.py          # TTS audio generation per line
├── split_script.py           # Splits full debate JSON into per-part files
├── ingest.py                 # PDF → chunks → embeddings → Qdrant
├── config.py                 # API keys, paths, and author config (not committed)
├── data/
│   ├── kafka/                # Source PDFs for Kafka
│   └── nietzsche/            # Source PDFs for Nietzsche
├── assets/                   # Generated background images land here
├── audio_output/             # Per-line .mp3 files
├── video_output/             # Final .mp4 output
├── multipart_output/         # Multi-part video outputs
└── Image generator/
    └── n8n/
        └── Image_generator.json   # Exported n8n workflow
```

---

## Setup

### Prerequisites

- WSL2 with Python 3.12
- Docker (running inside WSL)
- ffmpeg (`sudo apt install ffmpeg`)
- A HuggingFace API key
- A Groq API key

### 1. Clone and install dependencies

```bash
git clone https://github.com/Ashutosh777777/phil.git
cd phil
pip install -r requirements.txt
pip install stable-ts
```

### 2. Configure environment

Create a `config.py` with your API keys and paths:

```python
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
GROQ_API_KEY = "your_groq_key"
HUGGINGFACE_API_KEY = "your_huggingface_key"
```

> ⚠️ Make sure `config.py` is in your `.gitignore` so your API keys are never committed.

### 3. Start Docker containers

```bash
docker start n8n && docker start qdrant
```

n8n runs on port `5678`, Qdrant on port `6333`.

### 4. Import the n8n workflow

- Open n8n at `http://localhost:5678`
- Import `Image generator/n8n/Image_generator.json`
- Activate the workflow

### 5. Ingest philosopher texts into Qdrant

Add your source PDFs into the directories configured per author in `config.py`:

```python
AUTHORS = {
    "kafka": {
        "pdf_dir": "data/kafka",
        "collection": "kafka"
    },
    "nietzsche": {
        "pdf_dir": "data/nietzsche",
        "collection": "nietzsche"
    }
}

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_DIM = 384  # matches BAAI/bge-small-en-v1.5
```

Then run:

```bash
python3 ingest.py
```

This extracts text from each PDF page by page, splits it into chunks, embeds them with FastEmbed, and upserts into Qdrant. Each author gets their own collection. You'll see a progress bar per author — on first run it also creates the collections automatically.

The more texts you ingest per philosopher, the richer and more grounded the debate responses will be.

---

## How to run

```bash
cd phil
python3 run_pipeline.py
```

That's it. The pipeline:
1. Clears old background images
2. Calls n8n webhook → HuggingFace → saves `assets/background.png`
3. Auto-starts the RAG service
4. Generates a 6-turn debate script (3 parts × 2 turns)
5. Generates audio for each line
6. Aligns captions word-by-word with Whisper
7. Renders frames and composes videos via ffmpeg
8. Outputs `multipart_output/debate_part1.mp4`, `part2.mp4`, `part3.mp4`

To change the topic, edit `run_pipeline.py`:

```python
topic = "The nature of existence"
```

---

## How it works

### Pipeline diagram

```
run_pipeline.py
    │
    ├─► n8n webhook ──► HuggingFace SDXL ──► assets/background.png
    │
    └─► multipart_pipeline.py
            │
            ├─► RAG service (FastAPI :8000)
            │       ├─► Qdrant: retrieve top-k chunks for each author
            │       └─► Groq LLM: generate debate turns in character
            │
            ├─► voice_service.py
            │       └─► TTS per line ──► audio_output/line_NNN_speaker.mp3
            │           + stitched ──► full_debate.mp3
            │
            └─► video_service.py
                    ├─► stable-ts: word-level timestamp alignment
                    ├─► Pillow: render frames with speaker highlight + captions
                    └─► ffmpeg: concat frames + audio ──► debate_partN.mp4
```

### RAG grounding

Each philosopher's writings are chunked and stored in Qdrant under their own collection. At generation time, the RAG service embeds the topic, retrieves the top-6 most relevant chunks per author, and injects them as context into the LLM prompt. The LLM responds in character — but constrained by what the philosopher actually wrote.

### Caption system

Rather than burning static subtitles, Phil uses `stable-ts` (a Whisper wrapper) to get word-level timestamps from each audio segment. Words are grouped into 6-word chunks and rendered directly into the video frames, so captions are perfectly sync'd to speech — no SRT files, no ffmpeg subtitle filter.

---

## Configuration

| Parameter | Location | Default |
|---|---|---|
| Topic | `run_pipeline.py` | `"The nature of existence"` |
| Authors | `multipart_pipeline.py` | `kafka`, `nietzsche` |
| Debate turns | `multipart_pipeline.py` | `6` |
| Turns per part | `multipart_pipeline.py` | `2` |
| Words per caption | `video_service.py` | `6` |
| Whisper model size | `video_service.py` | `base` |

---

## Adding new philosophers

1. Add their PDFs to a new folder under `data/`
2. Add their entry to `AUTHORS` in `config.py`:
```python
"camus": {
    "pdf_dir": "data/camus",
    "collection": "camus"
}
```
3. Run `python3 ingest.py` — it will create the Qdrant collection and ingest automatically
4. Add their persona to the `personas` dict in `rag_service.py`:
```python
"camus": "You are Albert Camus. You speak of absurdity, revolt, and the struggle to find meaning in an indifferent universe."
```
5. Update the author names in `run_pipeline.py`

---

## License

MIT
