from fastapi import FastAPI
from pydantic import BaseModel
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from groq import Groq
from config import QDRANT_URL, EMBEDDING_MODEL, GROQ_API_KEY

app = FastAPI()
embedding_model = TextEmbedding(EMBEDDING_MODEL)
qdrant = QdrantClient(url=QDRANT_URL)
groq_client = Groq(api_key=GROQ_API_KEY)

class RetrieveRequest(BaseModel):
    author: str
    query: str
    top_k: int = 5

class DebateRequest(BaseModel):
    topic: str
    author_a: str
    author_b: str
    turns: int = 6

@app.post("/retrieve")
def retrieve(req: RetrieveRequest):
    query_vector = list(embedding_model.embed([req.query]))[0].tolist()
    results = qdrant.query_points(
        collection_name=req.author,
        query=query_vector,
        limit=req.top_k,
        with_payload=True
    ).points
    return {
        "author": req.author,
        "query": req.query,
        "chunks": [
            {
                "text": r.payload["text"],
                "book": r.payload["book"],
                "page": r.payload["page"],
                "score": r.score
            }
            for r in results
        ]
    }

@app.post("/debate")
def generate_debate(req: DebateRequest):
    query_vector_a = list(embedding_model.embed([req.topic]))[0].tolist()
    query_vector_b = list(embedding_model.embed([req.topic]))[0].tolist()

    chunks_a = qdrant.query_points(
        collection_name=req.author_a,
        query=query_vector_a,
        limit=6,
        with_payload=True
    ).points

    chunks_b = qdrant.query_points(
        collection_name=req.author_b,
        query=query_vector_b,
        limit=6,
        with_payload=True
    ).points

    context_a = "\n\n".join([c.payload["text"] for c in chunks_a])
    context_b = "\n\n".join([c.payload["text"] for c in chunks_b])

    personas = {
        "nietzsche": "You are Friedrich Nietzsche. You speak in aphorisms, champion the will to power, reject slave morality, and speak with fierce poetic intensity.",
        "kafka": "You are Franz Kafka. You speak with quiet anxiety, focus on alienation, bureaucratic absurdity, and the helplessness of the individual against incomprehensible systems."
    }

    script = []
    authors = [req.author_a, req.author_b]
    contexts = [context_a, context_b]
    conversation_history = []

    for turn in range(req.turns):
        speaker = authors[turn % 2]
        context = contexts[turn % 2]
        persona = personas.get(speaker, f"You are {speaker}.")

        conversation_history.append({
            "role": "user",
            "content": f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nRespond in character in 3-4 sentences. Be direct and philosophical."
        })

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": persona}] + conversation_history,
            max_tokens=200
        )

        reply = response.choices[0].message.content
        script.append({"speaker": speaker, "text": reply})
        conversation_history.append({"role": "assistant", "content": reply})

    return {
        "topic": req.topic,
        "author_a": req.author_a,
        "author_b": req.author_b,
        "script": script
    }

@app.get("/health")
def health():
    return {"status": "ok"}
