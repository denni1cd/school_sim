from __future__ import annotations

from .base import PassiveActivity, ActivityState


class IdleActivity(PassiveActivity):
    """Short filler task cycling between casual states."""

    STATES = ("observing", "chatting", "waiting")

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("posture", "standing")
        self.state.metadata.setdefault("mode", self.STATES[0])
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        if self.duration:
            elapsed = self.duration - self.remaining
            index = (elapsed // max(1, self.duration // len(self.STATES))) % len(self.STATES)
            mode = self.STATES[int(index)]
            if self.state.metadata.get("mode") != mode:
                self.state.metadata["mode"] = mode
                state = self.state
        return state
