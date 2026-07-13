from collections import deque
from typing import Any
from aether.time.clock import now_iso


class WorkingMemory:
    def __init__(self, max_events: int = 30):
        self.max_events = max_events
        self.events = deque(maxlen=max_events)
        self.current_goal: str | None = None
        self.current_milestone: str | None = None
        self.session_notes: list[str] = []

    def add_event(
        self,
        role: str,
        content: str,
        event_type: str = "message",
        metadata: dict[str, Any] | None = None,
    ) -> dict:
        event = {
            "time": now_iso(),
            "type": event_type,
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }

        self.events.append(event)
        return event

    def set_goal(self, goal: str) -> None:
        self.current_goal = goal
        self.add_event(
            role="system",
            content=f"Current goal set: {goal}",
            event_type="goal_update",
        )

    def set_milestone(self, milestone: str) -> None:
        self.current_milestone = milestone
        self.add_event(
            role="system",
            content=f"Current milestone set: {milestone}",
            event_type="milestone_update",
        )

    def add_note(self, note: str) -> None:
        self.session_notes.append(note)
        self.add_event(
            role="system",
            content=note,
            event_type="session_note",
        )

    def summary(self) -> dict:
        return {
            "current_goal": self.current_goal,
            "current_milestone": self.current_milestone,
            "session_notes": self.session_notes,
            "recent_events": list(self.events),
            "event_count": len(self.events),
            "max_events": self.max_events,
        }

    def clear(self) -> None:
        self.events.clear()
        self.current_goal = None
        self.current_milestone = None
        self.session_notes.clear()