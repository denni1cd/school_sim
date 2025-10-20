from __future__ import annotations

from .base import GradualActivity, ActivityState


class MaintenanceActivity(GradualActivity):
    """Upkeep-oriented activity that cycles through subtasks."""

    SUBTASKS = ("setup", "main_work", "cleanup")

    def on_start(self) -> ActivityState:
        state = super().on_start()
        self.state.metadata.setdefault("subtask", self.SUBTASKS[0])
        return state

    def tick(self, minutes: int = 1) -> ActivityState | None:
        state = super().tick(minutes)
        if self.duration:
            progress = self.state.metadata.get("progress", 0.0)
            if progress < 0.2:
                subtask = self.SUBTASKS[0]
            elif progress < 0.8:
                subtask = self.SUBTASKS[1]
            else:
                subtask = self.SUBTASKS[2]
            if self.state.metadata.get("subtask") != subtask:
                self.state.metadata["subtask"] = subtask
                state = self.state
        return state
