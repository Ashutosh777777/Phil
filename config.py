import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384

QDRANT_URL = "http://localhost:6333"

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
