from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import QueryRequest
from config import QDRANT_URL, EMBEDDING_MODEL

def retrieve(query, collection, top_k=5):
    model = TextEmbedding(EMBEDDING_MODEL)
    client = QdrantClient(url=QDRANT_URL)
    query_vector = list(model.embed([query]))[0].tolist()
    results = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=top_k,
        with_payload=True
    ).points

    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {r.score:.3f}) ---")
        print(f"Book: {r.payload['book']} | Page: {r.payload['page']}")
        print(r.payload['text'][:300])

if __name__ == "__main__":
    print("=== NIETZSCHE: morality and power ===")
    retrieve("what is the will to power and slave morality", "nietzsche")
    print("\n\n=== KAFKA: transformation and identity ===")
    retrieve("what happens when gregor transforms", "kafka")
