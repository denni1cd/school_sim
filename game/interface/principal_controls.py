from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, MutableMapping, Sequence

from ..actors.base_actor import NPCState
from ..notifications import AlertBus
from ..simulation.schedule_generator import DailySchedule, format_minutes
from ..systems.schedule_system import ScheduledActivity

if False:  # pragma: no cover - type checking helper
    from ..simulation import Simulation


@dataclass
class OverrideRecord:
    npc_id: str
    blocks: List[DailySchedule]
    reason: str
    timestamp: str


class PrincipalControls:
    """High-level façade for principal actions over the simulation."""

    def __init__(self, simulation: "Simulation") -> None:
        self._simulation = simulation
        self._history: List[OverrideRecord] = []

    @property
    def alert_bus(self) -> AlertBus:
        return self._simulation.alert_bus

    def override_schedule(
        self,
        npc_id: str,
        new_blocks: Sequence[Mapping[str, object]],
        *,
        reason: str = "principal_override",
    ) -> List[DailySchedule]:
        schedule_system = self._simulation.schedule_system
        updated = schedule_system.override_plan(npc_id, new_blocks, source=reason)
        current_minutes = int(self._simulation.clock.minute) % self._simulation.clock.day_length_minutes
        record = OverrideRecord(
            npc_id=npc_id,
            blocks=list(updated),
            reason=reason,
            timestamp=format_minutes(current_minutes),
        )
        self._history.append(record)
        npc = self._simulation.get_npc(npc_id)
        if npc and npc.current_activity:
            self._simulation.activity_system.interrupt(
                npc,
                reason="override",
                current_minutes=current_minutes,
            )
        self._simulation.event_logger.log_principal_action(
            format_minutes(current_minutes),
            action="override_schedule",
            subject=npc_id,
            details={"blocks": [block.activity_id for block in updated]},
        )
        schedule_system.update(self._simulation.clock.get_time_str())
        return updated

    def summon_student(
        self,
        npc_id: str,
        target_room_id: str,
        *,
        duration_minutes: int = 30,
    ) -> ScheduledActivity:
        npc = self._simulation.get_npc(npc_id)
        if npc is None:
            raise ValueError(f"Unknown NPC '{npc_id}'")
        current_minutes = int(self._simulation.clock.minute) % self._simulation.clock.day_length_minutes
        if npc.current_activity:
            self._simulation.activity_system.interrupt(
                npc,
                reason="summoned",
                current_minutes=current_minutes,
            )
        profile = (
            self._simulation.activity_catalog.resolve("prefect_rounds")
            or self._simulation.activity_catalog.resolve("Discipline")
            or self._simulation.activity_catalog.resolve("Idle")
        )
        activity = ScheduledActivity(
            name="summoned",
            duration=duration_minutes,
            location=target_room_id,
            notes="Principal summons",
            expected_travel=0,
            travel_buffer=0,
            profile=profile,
        )
        npc.assign_activity(activity, current_minutes)
        destination = self._simulation.select_destination(target_room_id)
        npc.pending_destination = destination
        npc.set_target(*destination)
        npc.state = NPCState.MOVING
        self._simulation.event_logger.log_principal_action(
            format_minutes(current_minutes),
            action="summon_student",
            subject=npc_id,
            details={"room": target_room_id},
        )
        return activity

    def mark_alert_resolved(self, alert_id: str) -> None:
        current_minutes = int(self._simulation.clock.minute) % self._simulation.clock.day_length_minutes
        alert = self.alert_bus.acknowledge(alert_id, minute_stamp=current_minutes)
        self._simulation.event_logger.log_principal_action(
            alert.acknowledged_at or alert.created_at,
            action="resolve_alert",
            subject=alert_id,
            details={"category": alert.category},
        )

    def broadcast_message(self, message: str, audience_filter: Mapping[str, object] | None = None) -> None:
        current_minutes = int(self._simulation.clock.minute) % self._simulation.clock.day_length_minutes
        payload: MutableMapping[str, object] = {"message": message}
        if audience_filter:
            payload["audience"] = dict(audience_filter)
        self._simulation.event_logger.log_principal_action(
            format_minutes(current_minutes),
            action="broadcast",
            subject="principal",
            details=payload,
        )

    def recent_overrides(self, limit: int = 5) -> Iterable[OverrideRecord]:
        return self._history[-limit:]
