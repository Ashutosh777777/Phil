import fitz  # PyMuPDF
import uuid
from pathlib import Path
from tqdm import tqdm

from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from config import OPENAI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, QDRANT_URL, AUTHORS


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text page by page from a PDF, preserving page numbers."""
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append({
                "text": text,
                "page": page_num,
                "source": Path(pdf_path).name
            })
    return pages


def chunk_pages(pages: list[dict], author: str, book_title: str) -> list[dict]:
    """Split pages into overlapping chunks, carrying metadata forward."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = []
    for page in pages:
        splits = splitter.split_text(page["text"])
        for i, split in enumerate(splits):
            chunks.append({
                "text": split,
                "metadata": {
                    "author": author,
                    "book": book_title,
                    "page": page["page"],
                    "source": page["source"],
                    "chunk_index": i
                }
            })
    return chunks

def embed_and_upsert(chunks, collection_name, model, client):
    BATCH_SIZE = 100

    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        print(f"Created collection: {collection_name}")

    texts = [c["text"] for c in chunks]

    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc=f"Upserting to {collection_name}"):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_chunks = chunks[i:i+BATCH_SIZE]

        vectors = model.encode(batch_texts, show_progress_bar=False).tolist()

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={**chunk["metadata"], "text": chunk["text"]}
            )
            for vector, chunk in zip(vectors, batch_chunks)
        ]

        client.upsert(collection_name=collection_name, points=points)


def ingest_author(author_key):
    author_config = AUTHORS[author_key]
    pdf_dir = Path(author_config["pdf_dir"])
    collection = author_config["collection"]

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(url=QDRANT_URL)

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {pdf_dir}")
        return

    print(f"\nIngesting {len(pdf_files)} PDFs for author: {author_key}")

    all_chunks = []
    for pdf_path in pdf_files:
        book_title = pdf_path.stem
        print(f"  Extracting: {pdf_path.name}")
        pages = extract_text_from_pdf(str(pdf_path))
        chunks = chunk_pages(pages, author=author_key, book_title=book_title)
        all_chunks.extend(chunks)
        print(f"    -> {len(pages)} pages, {len(chunks)} chunks")

    print(f"  Total chunks: {len(all_chunks)}")
    embed_and_upsert(all_chunks, collection, model, client)
    print(f"  Done. Collection '{collection}' ready.\n")
if __name__ == "__main__":
    for author_key in AUTHORS:
        ingest_author(author_key)