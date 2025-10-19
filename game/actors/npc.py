
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Tuple

from .base_actor import Actor, NPCState


if TYPE_CHECKING:
    from ..simulation.schedule_generator import DailySchedule


@dataclass
class NPC(Actor):
    role: str = "student"
    schedule: List[Tuple[str, object]] = field(default_factory=list)
    pending_activity: Optional[object] = None
    pending_activity_start_minutes: Optional[int] = None
    current_activity: Optional[object] = None
    current_activity_start_minutes: Optional[int] = None
    activity_remaining: int = 0
    pending_destination: Optional[Tuple[int, int]] = None
    daily_plan: List["DailySchedule"] = field(default_factory=list)

    def assign_activity(self, activity, start_minutes: Optional[int] = None) -> None:
        self.pending_activity = activity
        self.pending_activity_start_minutes = start_minutes
        self.pending_destination = None

    def begin_activity(self, activity, current_minutes: Optional[int] = None, *, day_length_minutes: Optional[int] = None) -> None:
        start_minutes = self.pending_activity_start_minutes
        self.pending_activity = None
        self.pending_activity_start_minutes = None
        self.pending_destination = None
        self.current_activity = activity
        self.current_activity_start_minutes = start_minutes
        duration = getattr(activity, "duration", 0)
        remaining = duration
        if (
            current_minutes is not None
            and start_minutes is not None
            and day_length_minutes
        ):
            elapsed = (current_minutes - start_minutes) % day_length_minutes
            remaining = max(duration - elapsed, 0)
        self.activity_remaining = remaining
        self.state = NPCState.PERFORMING_TASK

    def clear_activity(self) -> None:
        self.current_activity = None
        self.current_activity_start_minutes = None
        self.activity_remaining = 0
        self.pending_destination = None
        self.state = NPCState.IDLE

    def tick_activity_minute(self) -> None:
        if self.current_activity and self.activity_remaining > 0:
            self.activity_remaining -= 1
            if self.activity_remaining <= 0:
                self.clear_activity()
