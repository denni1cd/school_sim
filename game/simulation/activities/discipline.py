from __future__ import annotations

from .base import PassiveActivity, ActivityState


class DisciplineActivity(PassiveActivity):
    """Reflective meeting that escalates tone over time."""

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("tone", "calm")
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        remaining_ratio = self.remaining / self.duration if self.duration else 0.0
        if remaining_ratio > 0.66:
            tone = "calm"
        elif remaining_ratio > 0.33:
            tone = "firm"
        else:
            tone = "resolution"
        if self.state.metadata.get("tone") != tone:
            self.state.metadata["tone"] = tone
            state = self.state
        return state
