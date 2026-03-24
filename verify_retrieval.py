from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from config import QDRANT_URL, EMBEDDING_MODEL

def retrieve(query, collection, top_k=5):
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(url=QDRANT_URL)

    query_vector = model.encode(query).tolist()
    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )

    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {r.score:.3f}) ---")
        print(f"Book: {r.payload['book']} | Page: {r.payload['page']}")
        print(r.payload['text'][:300])

if __name__ == "__main__":
    print("=== NIETZSCHE: morality and power ===")
    retrieve("what is the will to power and slave morality", "nietzsche")

    print("\n\n=== MARX: class struggle ===")
    retrieve("how does class struggle drive history", "marx")