from __future__ import annotations

from .base import GradualActivity, ActivityState


class StudyActivity(GradualActivity):
    """Focused academic work with intensity drift."""

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("focus", "high")
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        if self.duration:
            progress = self.state.metadata.get("progress", 0.0)
            if progress < 0.5:
                intensity = "absorbed"
            elif progress < 0.85:
                intensity = "steady"
            else:
                intensity = "winding_down"
            if self.state.metadata.get("intensity") != intensity:
                self.state.metadata["intensity"] = intensity
                state = self.state
        return state
