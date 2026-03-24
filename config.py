import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # local, free, fast
EMBEDDING_DIM = 384                    # dimension for this model

QDRANT_URL = "http://localhost:6333"

AUTHORS = {
    "nietzsche": {
        "pdf_dir": "data/author_a",
        "collection": "nietzsche"
    },
    "marx": {
        "pdf_dir": "data/author_b",
        "collection": "marx"
    }
}