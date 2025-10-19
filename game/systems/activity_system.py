
from ..actors.base_actor import NPCState


class ActivitySystem:
    def start_if_ready(self, npc, *, current_minutes: int, day_length_minutes: int) -> None:
        if npc.pending_activity and npc.state == NPCState.IDLE and npc.target is None:
            npc.begin_activity(
                npc.pending_activity,
                current_minutes=current_minutes,
                day_length_minutes=day_length_minutes,
            )

    def on_arrival(self, npc, *, current_minutes: int, day_length_minutes: int) -> None:
        if npc.pending_activity:
            npc.begin_activity(
                npc.pending_activity,
                current_minutes=current_minutes,
                day_length_minutes=day_length_minutes,
            )

    def tick_minute(self, npc) -> None:
        npc.tick_activity_minute()
