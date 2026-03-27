# # from fastapi import FastAPI
# # from pydantic import BaseModel
# # from fastembed import TextEmbedding
# # from qdrant_client import QdrantClient
# # from groq import Groq
# # from config import QDRANT_URL, EMBEDDING_MODEL, GROQ_API_KEY

# # app = FastAPI()
# # embedding_model = TextEmbedding(EMBEDDING_MODEL)
# # qdrant = QdrantClient(url=QDRANT_URL)
# # groq_client = Groq(api_key=GROQ_API_KEY)

# # class RetrieveRequest(BaseModel):
# #     author: str
# #     query: str
# #     top_k: int = 5

# # class DebateRequest(BaseModel):
# #     topic: str
# #     author_a: str
# #     author_b: str
# #     turns: int = 6

# # @app.post("/retrieve")
# # def retrieve(req: RetrieveRequest):
# #     query_vector = list(embedding_model.embed([req.query]))[0].tolist()
# #     results = qdrant.query_points(
# #         collection_name=req.author,
# #         query=query_vector,
# #         limit=req.top_k,
# #         with_payload=True
# #     ).points
# #     return {
# #         "author": req.author,
# #         "query": req.query,
# #         "chunks": [
# #             {
# #                 "text": r.payload["text"],
# #                 "book": r.payload["book"],
# #                 "page": r.payload["page"],
# #                 "score": r.score
# #             }
# #             for r in results
# #         ]
# #     }

# # @app.post("/debate")
# # def generate_debate(req: DebateRequest):
# #     query_vector_a = list(embedding_model.embed([req.topic]))[0].tolist()
# #     query_vector_b = list(embedding_model.embed([req.topic]))[0].tolist()

# #     chunks_a = qdrant.query_points(
# #         collection_name=req.author_a,
# #         query=query_vector_a,
# #         limit=6,
# #         with_payload=True
# #     ).points

# #     chunks_b = qdrant.query_points(
# #         collection_name=req.author_b,
# #         query=query_vector_b,
# #         limit=6,
# #         with_payload=True
# #     ).points

# #     context_a = "\n\n".join([c.payload["text"] for c in chunks_a])
# #     context_b = "\n\n".join([c.payload["text"] for c in chunks_b])

# #     personas = {
# #         "nietzsche": "You are Friedrich Nietzsche. You speak in aphorisms, champion the will to power, reject slave morality, and speak with fierce poetic intensity.",
# #         "kafka": "You are Franz Kafka. You speak with quiet anxiety, focus on alienation, bureaucratic absurdity, and the helplessness of the individual against incomprehensible systems."
# #     }

# #     script = []
# #     authors = [req.author_a, req.author_b]
# #     contexts = [context_a, context_b]
# #     conversation_history = []

# #     for turn in range(req.turns):
# #         speaker = authors[turn % 2]
# #         context = contexts[turn % 2]
# #         persona = personas.get(speaker, f"You are {speaker}.")

# #         conversation_history.append({
# #             "role": "user",
# #             "content": f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nRespond in character in 3-4 sentences. Be direct and philosophical."
# #         })

# #         response = groq_client.chat.completions.create(
# #             model="llama-3.3-70b-versatile",
# #             messages=[{"role": "system", "content": persona}] + conversation_history,
# #             max_tokens=200
# #         )

# #         reply = response.choices[0].message.content
# #         script.append({"speaker": speaker, "text": reply})
# #         conversation_history.append({"role": "assistant", "content": reply})

# #     return {
# #         "topic": req.topic,
# #         "author_a": req.author_a,
# #         "author_b": req.author_b,
# #         "script": script
# #     }

# # @app.get("/health")
# # def health():
# #     return {"status": "ok"}



# #----------------------------------------The above code created ~2 minutes of videos. The below code creates a video of under 1 minute

# from fastapi import FastAPI
# from pydantic import BaseModel
# from fastembed import TextEmbedding
# from qdrant_client import QdrantClient
# from groq import Groq
# from config import QDRANT_URL, EMBEDDING_MODEL, GROQ_API_KEY

# app = FastAPI()
# embedding_model = TextEmbedding(EMBEDDING_MODEL)
# qdrant = QdrantClient(url=QDRANT_URL)
# groq_client = Groq(api_key=GROQ_API_KEY)

# class RetrieveRequest(BaseModel):
#     author: str
#     query: str
#     top_k: int = 5

# class DebateRequest(BaseModel):
#     topic: str
#     author_a: str
#     author_b: str
#     turns: int = 4  # Reduced from 6 to 4 for shorter videos

# @app.post("/retrieve")
# def retrieve(req: RetrieveRequest):
#     query_vector = list(embedding_model.embed([req.query]))[0].tolist()
#     results = qdrant.query_points(
#         collection_name=req.author,
#         query=query_vector,
#         limit=req.top_k,
#         with_payload=True
#     ).points
#     return {
#         "author": req.author,
#         "query": req.query,
#         "chunks": [
#             {
#                 "text": r.payload["text"],
#                 "book": r.payload["book"],
#                 "page": r.payload["page"],
#                 "score": r.score
#             }
#             for r in results
#         ]
#     }

# @app.post("/debate")
# def generate_debate(req: DebateRequest):
#     query_vector_a = list(embedding_model.embed([req.topic]))[0].tolist()
#     query_vector_b = list(embedding_model.embed([req.topic]))[0].tolist()

#     # Reduce chunk count from 6 to 4 for more focused context
#     chunks_a = qdrant.query_points(
#         collection_name=req.author_a,
#         query=query_vector_a,
#         limit=4,
#         with_payload=True
#     ).points

#     chunks_b = qdrant.query_points(
#         collection_name=req.author_b,
#         query=query_vector_b,
#         limit=4,
#         with_payload=True
#     ).points

#     context_a = "\n\n".join([c.payload["text"] for c in chunks_a])
#     context_b = "\n\n".join([c.payload["text"] for c in chunks_b])

#     personas = {
#         "nietzsche": "You are Friedrich Nietzsche. You speak in aphorisms, champion the will to power, reject slave morality, and speak with fierce poetic intensity.",
#         "kafka": "You are Franz Kafka. You speak with quiet anxiety, focus on alienation, bureaucratic absurdity, and the helplessness of the individual against incomprehensible systems."
#     }

#     script = []
#     authors = [req.author_a, req.author_b]
#     contexts = [context_a, context_b]
#     conversation_history = []

#     # Calculate target words per turn to stay under 60 seconds total
#     # Average speech rate: ~150 words per minute = ~2.5 words per second
#     # For 60 seconds: ~150 words total
#     # With 4 turns: ~37 words per turn
#     # Being conservative: target 30-35 words per turn
    
#     for turn in range(req.turns):
#         speaker = authors[turn % 2]
#         context = contexts[turn % 2]
#         persona = personas.get(speaker, f"You are {speaker}.")

#         # More aggressive length constraints for 1-minute video
#         if turn == 0:
#             # First speaker - introduce the position
#             prompt = f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nAs the opening statement, respond in character with 2 concise sentences (30-35 words total). Be direct and philosophical. Make a strong, clear point."
#         elif turn == req.turns - 1:
#             # Last turn - concluding statement
#             prompt = f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nGiven the discussion so far, provide a final concise response in 2 sentences (30-35 words total). Be conclusive and impactful."
#         else:
#             # Middle turns - engage with the debate
#             prompt = f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nRespond to the previous point in character with 2 concise sentences (30-35 words total). Be direct and engaging."

#         conversation_history.append({
#             "role": "user",
#             "content": prompt
#         })

#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "system", "content": persona}] + conversation_history,
#             max_tokens=100,  # Reduced from 200 to 100
#             temperature=0.8  # Slightly higher for more dynamic responses
#         )

#         reply = response.choices[0].message.content.strip()
        
#         # Post-process to ensure we're not too verbose
#         # Split into sentences and take only first 2-3 if needed
#         sentences = [s.strip() + '.' for s in reply.replace('!', '.').replace('?', '.').split('.') if s.strip()]
#         if len(sentences) > 3:
#             reply = ' '.join(sentences[:3])
        
#         script.append({"speaker": speaker, "text": reply})
#         conversation_history.append({"role": "assistant", "content": reply})

#     return {
#         "topic": req.topic,
#         "author_a": req.author_a,
#         "author_b": req.author_b,
#         "script": script
#     }

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# After i decided to create a longer video that can be broken down into parts

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
    turns: int = 6  # Default 6 turns for 3-part videos (2 turns per part)

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

        # Dynamic prompting based on position in conversation
        if turn == 0:
            prompt = f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nAs the opening statement, respond in character with 2-3 concise sentences. Introduce your perspective on this topic."
        elif turn == req.turns - 1:
            prompt = f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nProvide a final response in 2-3 sentences. Make a conclusive statement."
        else:
            prompt = f"Topic: {req.topic}\n\nYour source texts:\n{context}\n\nRespond to the previous point in character with 2-3 sentences. Engage directly with the debate."

        conversation_history.append({
            "role": "user",
            "content": prompt
        })

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": persona}] + conversation_history,
            max_tokens=150,
            temperature=0.85
        )

        reply = response.choices[0].message.content.strip()
        
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