from aether.memory.working.store import WorkingMemory


class AetherRuntime:
    def __init__(self):
        self.awake = False
        self.working_memory = WorkingMemory(max_events=30)

    def awaken(self) -> None:
        self.awake = True
        self.working_memory.set_milestone("Milestone 6 — Working Memory")
        self.working_memory.set_goal(
            "Maintain short-term session context during API runtime."
        )

    def status(self) -> str:
        return "awake" if self.awake else "ready"


runtime = AetherRuntime()