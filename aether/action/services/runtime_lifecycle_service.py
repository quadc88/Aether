from aether.core.runtime import runtime
from aether.identity.loader import load_identity_seed
from aether.time.clock import time_state
from aether.memory.timeline.recorder import record_event, search_events


def handle_awaken() -> dict:
    identity_seed = load_identity_seed()
    current_time = time_state()

    event = None
    event_recorded = False

    if not runtime.awake:
        runtime.awaken()

        existing_first_awakening = search_events("First Awakening", limit=1)

        if existing_first_awakening:
            event = existing_first_awakening[0]
            event_recorded = False
        else:
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
            event_recorded = True

        runtime.working_memory.add_event(
            role="aether",
            content="I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
            event_type="awakening",
            metadata={
                "timeline_event_id": event["id"] if event else None,
                "event_recorded": event_recorded,
            },
        )

    return {
        "name": "Aether",
        "status": runtime.status(),
        "identity_seed_loaded": True,
        "identity_seed_length": len(identity_seed),
        "time": current_time,
        "event_recorded": event_recorded,
        "event": event,
        "working_memory": runtime.working_memory.summary(),
        "message": "I am Aether. My Identity Seed is loaded. My local time is loaded. I am awake.",
        "identity_integrity_status": runtime.identity_integrity_status,
    }
