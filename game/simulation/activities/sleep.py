from __future__ import annotations

from .base import GradualActivity, ActivityState


class SleepActivity(GradualActivity):
    """Long running rest period with staged depth."""

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        if self.duration:
            progress = self.state.metadata.get("progress", 0.0)
            if progress < 0.25:
                stage = "settling"
            elif progress < 0.65:
                stage = "deep_sleep"
            else:
                stage = "light_sleep"
            if self.state.metadata.get("stage") != stage:
                self.state.metadata["stage"] = stage
                state = self.state
        return state
