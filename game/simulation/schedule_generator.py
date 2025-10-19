from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, MutableMapping, Optional, Sequence

from ..core.map import MapGrid
from ..core.pathfinding import astar


def parse_hhmm(value: str) -> int:
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


def format_minutes(minutes: int) -> str:
    minutes %= 24 * 60
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}"


def parse_duration(value: str | None) -> int:
    if not value:
        return 0
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


@dataclass
class DailySchedule:
    actor_id: str
    slot: str
    activity_id: str
    room_id: str
    start_tick: int
    duration_minutes: int
    day_length_minutes: int
    notes: str | None = None
    travel_buffer: int = 0
    expected_travel: Optional[int] = None
    travel_path: Optional[List[tuple[int, int]]] = None
    stagger_applied: int = 0

    def clone_for_actor(self, actor_id: str) -> "DailySchedule":
        return DailySchedule(
            actor_id=actor_id,
            slot=self.slot,
            activity_id=self.activity_id,
            room_id=self.room_id,
            start_tick=self.start_tick,
            duration_minutes=self.duration_minutes,
            day_length_minutes=self.day_length_minutes,
            notes=self.notes,
            travel_buffer=self.travel_buffer,
        )

    @property
    def end_tick(self) -> int:
        return (self.start_tick + self.duration_minutes) % self.day_length_minutes

    def absolute_interval(self) -> tuple[int, int]:
        start = self.start_tick
        end = self.start_tick + self.duration_minutes
        if self.duration_minutes <= 0:
            end = start
        elif end <= start:
            end += self.day_length_minutes
        return start, end

    def set_start(self, minutes: int) -> None:
        self.start_tick = minutes % self.day_length_minutes
        self.stagger_applied = 0

    def set_duration(self, minutes: int) -> None:
        self.duration_minutes = max(0, minutes)

    def set_travel_buffer(self, minutes: int) -> None:
        self.travel_buffer = max(0, minutes)

    def set_activity(self, activity_id: str) -> None:
        self.activity_id = activity_id

    def set_room(self, room_id: str) -> None:
        self.room_id = room_id

    def set_notes(self, value: str | None) -> None:
        self.notes = value

    def shift_by(self, minutes: int) -> None:
        if minutes == 0:
            return
        self.start_tick = (self.start_tick + minutes) % self.day_length_minutes
        self.stagger_applied += minutes


class ScheduleTemplate:
    def __init__(self, name: str, raw_data: Mapping[str, Sequence[Mapping[str, object]]], *, day_length_minutes: int):
        self.name = name
        self.day_length_minutes = day_length_minutes
        self._variants: Dict[str, List[DailySchedule]] = {}
        for variant, entries in raw_data.items():
            slots: List[DailySchedule] = []
            for entry in entries:
                slot_name = str(entry["slot"])
                start = parse_hhmm(str(entry["start"]))
                duration = parse_duration(str(entry.get("duration", "00:00")))
                activity = str(entry["activity"])
                room = str(entry.get("room", ""))
                notes = entry.get("notes")
                travel_buffer = parse_duration(str(entry.get("travel_buffer", "00:00")))
                slots.append(
                    DailySchedule(
                        actor_id="",
                        slot=slot_name,
                        activity_id=activity,
                        room_id=room,
                        start_tick=start,
                        duration_minutes=duration,
                        day_length_minutes=day_length_minutes,
                        notes=str(notes) if notes is not None else None,
                        travel_buffer=travel_buffer,
                    )
                )
            self._variants[variant] = slots

    def instantiate(self, actor_id: str, variant: str) -> List[DailySchedule]:
        if variant not in self._variants:
            raise KeyError(f"Template {self.name} missing variant {variant}")
        return [slot.clone_for_actor(actor_id) for slot in self._variants[variant]]


@dataclass
class ScheduleAssignment:
    actor_id: str
    template_name: str
    template: ScheduleTemplate
    variant: str = "weekday"
    overrides: Sequence[Mapping[str, object]] = field(default_factory=list)
    notes: str | None = None

    def apply(self) -> List[DailySchedule]:
        slots = self.template.instantiate(self.actor_id, self.variant)
        slot_lookup: Dict[str, DailySchedule] = {slot.slot: slot for slot in slots}
        for override in self.overrides:
            slot_name = str(override.get("slot"))
            slot = slot_lookup.get(slot_name)
            if not slot:
                continue
            if "start" in override:
                slot.set_start(parse_hhmm(str(override["start"])))
            if "duration" in override:
                slot.set_duration(parse_duration(str(override["duration"])))
            if "activity" in override:
                slot.set_activity(str(override["activity"]))
            if "room" in override:
                slot.set_room(str(override["room"]))
            if "travel_buffer" in override:
                slot.set_travel_buffer(parse_duration(str(override["travel_buffer"])))
            if "notes" in override:
                slot.set_notes(str(override["notes"]))
        slots.sort(key=lambda item: item.start_tick)
        return slots

    def to_dict(self) -> dict:
        payload = {
            "name": self.actor_id,
            "template": self.template_name,
            "variant": self.variant,
        }
        if self.notes:
            payload["notes"] = self.notes
        if self.overrides:
            payload["overrides"] = list(self.overrides)
        return payload

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, object],
        *,
        templates: Mapping[str, ScheduleTemplate],
    ) -> "ScheduleAssignment":
        name = str(data["name"])
        template_name = str(data["template"])
        template = templates[template_name]
        variant = str(data.get("variant", "weekday"))
        overrides = data.get("overrides", [])
        if not isinstance(overrides, Sequence):
            overrides = []
        notes = data.get("notes")
        return cls(
            actor_id=name,
            template_name=template_name,
            template=template,
            variant=variant,
            overrides=overrides,  # type: ignore[arg-type]
            notes=str(notes) if notes is not None else None,
        )


class TravelEstimator:
    def __init__(self, grid: MapGrid):
        self.grid = grid

    def _room_anchor(self, room_id: str) -> tuple[int, int]:
        interior = self.grid.room_interior_targets(room_id)
        if interior:
            return interior[0]
        return self.grid.room_center(room_id)

    def annotate(
        self,
        schedules: MutableMapping[str, List[DailySchedule]],
        *,
        adjust_buffers: bool = True,
    ) -> None:
        for actor_id, blocks in schedules.items():
            blocks.sort(key=lambda block: block.start_tick)
            previous: DailySchedule | None = None
            for block in blocks:
                if previous is None:
                    block.expected_travel = 0
                    block.travel_path = []
                    previous = block
                    continue
                start_room = previous.room_id or previous.activity_id
                end_room = block.room_id or block.activity_id
                try:
                    start_point = self._room_anchor(start_room)
                    end_point = self._room_anchor(end_room)
                except KeyError:
                    block.expected_travel = None
                    block.travel_path = None
                    previous = block
                    continue
                path = astar(self.grid, start_point, end_point)
                if path:
                    block.travel_path = path
                    travel_steps = max(len(path) - 1, 0)
                    block.expected_travel = travel_steps
                    if adjust_buffers and travel_steps > (block.travel_buffer or 0):
                        block.travel_buffer = travel_steps
                else:
                    block.travel_path = None
                    block.expected_travel = None
                previous = block


__all__ = [
    "DailySchedule",
    "ScheduleTemplate",
    "ScheduleAssignment",
    "TravelEstimator",
    "parse_hhmm",
    "parse_duration",
    "format_minutes",
]
