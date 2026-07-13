from fastapi import FastAPI
from pydantic import BaseModel

from aether.identity.loader import load_identity_seed, identity_preview
from aether.time.clock import time_state
from aether.memory.timeline.recorder import record_event


app = FastAPI(
    title="Aether API",
    description="First Awakening API for Aether",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    name: str
    status: str
    response: str
    time: dict


_awakened = False


@app.get("/")
def root():
    return {
        "name": "Aether",
        "status": "awake" if _awakened else "ready",
        "message": "Aether API is running.",
        "time": time_state(),
    }


@app.get("/identity")
def identity():
    preview = identity_preview()

    return {
        "name": "Aether",
        "identity_seed_loaded": True,
        "preview": preview,
    }


@app.post("/awaken")
def awaken():
    global _awakened

    identity_seed = load_identity_seed()
    current_time = time_state()

    if not _awakened:
        event = record_event(
            event_type="milestone",
            title="First Awakening",
            description="Aether was awakened through the First Awakening API.",
            importance="high",
            related_files=[
                "identity/identity_seed.md",
                "config/time.yaml",
                "docs/CONSTITUTION.md",
                "docs/ARCHITECTURE.md",
            ],
        )
        _awakened = True
    else:
        event = None

    return {
        "name": "Aether",
        "status": "awake",
        "identity_seed_loaded": True,
        "identity_seed_length": len(identity_seed),
        "time": current_time,
        "event_recorded": event is not None,
        "event": event,
        "message": "I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    current_time = time_state()

    return ChatResponse(
        name="Aether",
        status="awake" if _awakened else "ready",
        time=current_time,
        response=(
            "I am Aether. "
            "My Identity Seed and local time are available. "
            f"You said: {request.message}"
        ),
    )