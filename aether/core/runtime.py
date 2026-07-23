from aether.identity.guard import (
    initialize_identity_guard,
    load_identity_guard_state,
    verify_identity_integrity,
)
from aether.memory.working.store import WorkingMemory


class AetherRuntime:
    def __init__(self):
        self.awake = False
        self.working_memory = WorkingMemory(max_events=30)
        self.identity_integrity_status: dict | None = None

    def awaken(self) -> None:
        self.awake = True
        self._initialize_or_verify_identity_guard()
        self.working_memory.set_milestone("Milestone 6 — Working Memory")
        self.working_memory.set_goal(
            "Maintain short-term session context during API runtime."
        )

    def _initialize_or_verify_identity_guard(self) -> None:
        from pathlib import Path

        guard_path = Path(__file__).parent.parent / "identity" / "guard.py"
        seed_path_str = "identity/identity_seed.md"
        if not Path(seed_path_str).exists():
            self.identity_integrity_status = {
                "status": "missing",
                "message": "Identity Seed file is missing. Cannot initialize guard.",
            }
            self.working_memory.add_event(
                role="system",
                content=f"Identity Seed not found at {seed_path_str}. Awakening without guard.",
                event_type="identity_guard_skipped",
            )
            return

        try:
            state = load_identity_guard_state()
            if state is None:
                initialize_identity_guard()
                self.identity_integrity_status = {"initialized": True}
                self.working_memory.add_event(
                    role="system",
                    content="Identity seed guard initialized.",
                    event_type="identity_guard_initialized",
                )
            else:
                result = verify_identity_integrity()
                self.identity_integrity_status = result
                if result.get("changed"):
                    self.working_memory.add_event(
                        role="system",
                        content=(
                            f"Identity seed integrity ALERT: checksum changed. "
                            f"known={result.get('known_sha256', '')} "
                            f"current={result.get('current_sha256', '')}"
                        ),
                        event_type="identity_guard_changed",
                    )
                elif result.get("status") == "failed":
                    self.working_memory.add_event(
                        role="system",
                        content="Identity seed guard status: failed.",
                        event_type="identity_guard_failed",
                    )
                else:
                    self.working_memory.add_event(
                        role="system",
                        content="Identity seed verified on awakening.",
                        event_type="identity_guard_verified",
                    )
        except FileNotFoundError as exc:
            self.identity_integrity_status = {
                "status": "error",
                "message": str(exc),
            }
            self.working_memory.add_event(
                role="system",
                content=f"Identity guard error: {exc}",
                event_type="identity_guard_error",
            )
        except Exception as exc:
            self.identity_integrity_status = {
                "status": "error",
                "message": str(exc),
            }
            self.working_memory.add_event(
                role="system",
                content=f"Identity guard unexpected error: {exc}",
                event_type="identity_guard_error",
            )

    def status(self) -> str:
        return "awake" if self.awake else "ready"


runtime = AetherRuntime()