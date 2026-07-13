from fastapi import FastAPI
from pydantic import BaseModel

from aether.identity.loader import load_identity_seed, identity_preview
from aether.time.clock import time_state
from aether.memory.timeline.recorder import record_event
from aether.core.runtime import runtime


app = FastAPI(
    title="Aether API",
    description="First Awakening API with Working Memory for Aether",
    version="0.2.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    name: str
    status: str
    response: str
    time: dict
    working_memory_event_count: int


class GoalRequest(BaseModel):
    goal: str


class MilestoneRequest(BaseModel):
    milestone: str


@app.get("/")
def root():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Aether API is running.",
        "time": time_state(),
        "working_memory": {
            "event_count": runtime.working_memory.summary()["event_count"],
            "current_goal": runtime.working_memory.current_goal,
            "current_milestone": runtime.working_memory.current_milestone,
        },
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
    identity_seed = load_identity_seed()
    current_time = time_state()

    event = None

    if not runtime.awake:
        runtime.awaken()

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

        runtime.working_memory.add_event(
            role="aether",
            content="I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
            event_type="awakening",
            metadata={"timeline_event_id": event["id"]},
        )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "identity_seed_loaded": True,
        "identity_seed_length": len(identity_seed),
        "time": current_time,
        "event_recorded": event is not None,
        "event": event,
        "working_memory": runtime.working_memory.summary(),
        "message": "I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    current_time = time_state()

    runtime.working_memory.add_event(
        role="user",
        content=request.message,
        event_type="message",
    )

    response_text = (
        "I am Aether. "
        "I can now keep short-term Working Memory during this runtime. "
        f"You said: {request.message}"
    )

    runtime.working_memory.add_event(
        role="aether",
        content=response_text,
        event_type="message",
    )

    summary = runtime.working_memory.summary()

    return ChatResponse(
        name="Aether",
        status=runtime.status(),
        time=current_time,
        response=response_text,
        working_memory_event_count=summary["event_count"],
    )


@app.get("/memory/working")
def get_working_memory():
    return {
        "name": "Aether",
        "status": runtime.status(),
        "time": time_state(),
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/goal")
def set_working_goal(request: GoalRequest):
    runtime.working_memory.set_goal(request.goal)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory goal updated.",
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/milestone")
def set_working_milestone(request: MilestoneRequest):
    runtime.working_memory.set_milestone(request.milestone)

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory milestone updated.",
        "working_memory": runtime.working_memory.summary(),
    }


@app.post("/memory/working/clear")
def clear_working_memory():
    runtime.working_memory.clear()

    return {
        "name": "Aether",
        "status": runtime.status(),
        "message": "Working Memory cleared.",
        "working_memory": runtime.working_memory.summary(),
    }