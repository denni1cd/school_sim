from __future__ import annotations

from .base import GradualActivity, ActivityState


class EatActivity(GradualActivity):
    """Meal time activity with course tracking."""

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("course", "starter")
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        if self.duration:
            progress = self.state.metadata.get("progress", 0.0)
            if progress < 0.33:
                course = "starter"
            elif progress < 0.66:
                course = "main"
            else:
                course = "dessert"
            if self.state.metadata.get("course") != course:
                self.state.metadata["course"] = course
                state = self.state
        return state
