# pipeline.py
import httpx
import asyncio
import json
from voice_service import generate_audio_from_script

API_BASE = "http://localhost:8000"

async def run_pipeline(topic: str, author_a: str = "kafka", author_b: str = "nietzsche", turns: int = 4):
    print(f"\n🎭 Generating debate on: '{topic}'")
    
    # Stage 2 — Generate debate script
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(f"{API_BASE}/debate", json={
            "topic": topic,
            "author_a": author_a,
            "author_b": author_b,
            "turns": turns
        })
        response.raise_for_status()
        data = response.json()

    script = data["script"]
    print(f"✅ Script generated — {len(script)} turns")

    # Save script to JSON for reference
    with open("output_script.json", "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Script saved to output_script.json")

    # Stage 3 — Voice synthesis
    print("\n🎙️ Synthesizing voices...")
    final_audio, segments = await generate_audio_from_script(script)
    print(f"✅ Audio saved to: {final_audio}")

    return {
        "topic": topic,
        "script": script,
        "audio_path": final_audio
    }

if __name__ == "__main__":
    asyncio.run(run_pipeline("the burden of freedom"))