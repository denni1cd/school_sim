from __future__ import annotations

from .base import GradualActivity, ActivityState


class TeachActivity(GradualActivity):
    """Instruction-focused activity with segment markers."""

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("segment", "intro")
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        if self.duration:
            progress = self.state.metadata.get("progress", 0.0)
            if progress < 0.2:
                segment = "intro"
            elif progress < 0.8:
                segment = "lesson"
            else:
                segment = "wrap_up"
            if self.state.metadata.get("segment") != segment:
                self.state.metadata["segment"] = segment
                state = self.state
        return state
