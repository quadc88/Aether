from aether.verification.risk import verification_plan
from aether.core.runtime import runtime
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge


def handle_create_verification_plan(text: str) -> dict:
    plan = verification_plan(text)
    runtime.working_memory.add_event(
        role="aether",
        content=f"Verification plan created for {plan['action_type']} request.",
        event_type="verification_plan_created",
        metadata={
            "risk_level": plan["risk_level"],
            "action_type": plan["action_type"],
            "requires_verification": plan["requires_verification"],
            "requires_user_approval": plan["requires_user_approval"],
        },
    )

    warnings = []
    timeline_event = None
    graph_relationship = None
    if plan["risk_level"] == "high":
        timeline_event = record_event(
            event_type="verification",
            title=f"High-risk verification plan: {plan['action_type']}",
            description="Aether created a verification plan for a high-risk request.",
            importance="high",
        )
        try:
            graph_relationship = add_edge(
                "Aether",
                "created_verification_plan_for",
                plan["action_type"],
            )
            graph_relationship.pop("created_new", None)
        except Exception as error:
            warnings.append(f"Graph Memory integration was unavailable: {error}")

    return {
        "name": "Aether",
        "status": runtime.status(),
        "plan": plan,
        "timeline_event": timeline_event,
        "graph_relationship": graph_relationship,
        "warnings": warnings,
    }
