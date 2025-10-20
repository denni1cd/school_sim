from __future__ import annotations

from .base import GradualActivity, ActivityState


class RecreationActivity(GradualActivity):
    """General recreation activity capturing energy level."""

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("energy", "warming_up")
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        if self.duration:
            progress = self.state.metadata.get("progress", 0.0)
            if progress < 0.3:
                energy = "warming_up"
            elif progress < 0.7:
                energy = "peak"
            else:
                energy = "cooldown"
            if self.state.metadata.get("energy") != energy:
                self.state.metadata["energy"] = energy
                state = self.state
        return state
