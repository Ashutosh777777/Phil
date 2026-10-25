import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384

QDRANT_URL = "http://localhost:6333"

# YouTube scheduling (override in .env or with --time / --tz on the command line)
DEFAULT_TOPIC = "The nature of existence"
PUBLISH_TIME = os.getenv("PUBLISH_TIME", "18:00")        # 24h HH:MM
PUBLISH_TZ = os.getenv("PUBLISH_TZ", "Asia/Kolkata")     # IANA timezone name

AUTHORS = {
    "kafka": {
        "pdf_dir": "data/author_a",
        "collection": "kafka"
    },
    "nietzsche": {
        "pdf_dir": "data/author_b",
        "collection": "nietzsche"
    }
}
