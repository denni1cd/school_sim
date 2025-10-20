from __future__ import annotations

from ..actors.base_actor import NPCState
from ..actors.npc import NPC
from ..logging import EventLogger
from ..simulation.activities import ActivityCatalog, ActivityFactory
from ..world import RoomManager


def _format_minutes(minutes: int) -> str:
    minutes %= 24 * 60
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}"


class ActivitySystem:
    """Coordinates activity lifecycle with room tracking and logging."""

    def __init__(
        self,
        *,
        catalog: ActivityCatalog,
        room_manager: RoomManager,
        event_logger: EventLogger,
    ) -> None:
        self._catalog = catalog
        self._room_manager = room_manager
        self._logger = event_logger

    def start_if_ready(self, npc: NPC, *, current_minutes: int, day_length_minutes: int) -> None:
        block = npc.pending_schedule
        if block is None or npc.state != NPCState.IDLE or npc.target is not None:
            return

        profile = block.profile or self._catalog.resolve(block.name)
        if profile is None:
            profile = self._catalog.resolve("Idle")
        if profile is None:
            return

        activity = ActivityFactory.create(
            profile,
            room_id=block.location,
            duration=block.duration,
        )
        npc.begin_activity(activity, current_minutes=current_minutes, day_length_minutes=day_length_minutes)
        start_state = activity.on_start()
        self._room_manager.start_activity(npc.name, activity)
        timestamp = _format_minutes(current_minutes)
        self._logger.log_activity_start(
            timestamp,
            npc=npc.name,
            activity=activity.label,
            room=activity.room_id,
            state=dict(start_state.metadata),
        )

    def on_arrival(self, npc: NPC, *, current_minutes: int, day_length_minutes: int) -> None:
        self.start_if_ready(npc, current_minutes=current_minutes, day_length_minutes=day_length_minutes)

    def tick_minute(self, npc: NPC, *, current_minutes: int) -> None:
        activity = npc.current_activity
        if not activity:
            return

        updated_state = activity.tick(1)
        if updated_state:
            self._room_manager.update_activity(npc.name, activity)

        if npc.tick_activity_minute():
            completion_state = activity.on_complete()
            self._room_manager.end_activity(npc.name, activity)
            timestamp = _format_minutes(current_minutes)
            self._logger.log_activity_end(
                timestamp,
                npc=npc.name,
                activity=activity.label,
                room=activity.room_id,
                state=dict(completion_state.metadata),
            )
            npc.clear_activity()

    def interrupt(self, npc: NPC, reason: str | None = None, *, current_minutes: int) -> None:
        activity = npc.current_activity
        if not activity:
            return
        interrupt_state = activity.on_interrupt(reason)
        self._room_manager.end_activity(npc.name, activity)
        timestamp = _format_minutes(current_minutes)
        self._logger.log_activity_interrupt(
            timestamp,
            npc=npc.name,
            activity=activity.label,
            room=activity.room_id,
            state=dict(interrupt_state.metadata),
        )
        npc.clear_activity()
