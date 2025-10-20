from __future__ import annotations

from .base import PassiveActivity, ActivityState


class MedicalActivity(PassiveActivity):
    """Brief care session that notes triage phase."""

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("phase", "intake")
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        progress = self.remaining / self.duration if self.duration else 0.0
        if progress > 0.66:
            phase = "wrap_up"
        elif progress > 0.33:
            phase = "treatment"
        else:
            phase = "intake"
        if self.state.metadata.get("phase") != phase:
            self.state.metadata["phase"] = phase
            state = self.state
        return state
