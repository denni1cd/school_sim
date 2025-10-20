from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Mapping, Sequence

from ..core.map import Room
from .schedule_generator import DailySchedule


@dataclass
class ConflictRecord:
    room: str
    start_tick: int
    end_tick: int
    capacity: int
    actors: tuple[str, ...]
    shift_minutes: int = 0


def detect_room_capacity_conflicts(
    schedules: Sequence[DailySchedule],
    room_metadata: Mapping[str, Room],
) -> list[ConflictRecord]:
    conflicts: list[ConflictRecord] = []
    seen: set[tuple[str, int, tuple[str, ...]]] = set()
    for room_name, room in room_metadata.items():
        if not room.capacity:
            continue
        room_blocks = [block for block in schedules if block.room_id == room_name and block.duration_minutes > 0]
        if not room_blocks:
            continue
        events: list[tuple[int, int, DailySchedule]] = []
        for block in room_blocks:
            start, end = block.absolute_interval()
            events.append((int(start), 1, block))
            events.append((int(end), -1, block))
        events.sort(key=lambda item: (item[0], item[1]))
        active: list[DailySchedule] = []
        for time, delta, block in events:
            if delta == 1:
                active.append(block)
                if len(active) > room.capacity:
                    actor_ids = tuple(sorted({slot.actor_id for slot in active}))
                    key = (room_name, time, actor_ids)
                    if key not in seen:
                        seen.add(key)
                        conflicts.append(
                            ConflictRecord(
                                room=room_name,
                                start_tick=time % block.day_length_minutes,
                                end_tick=time % block.day_length_minutes,
                                capacity=room.capacity,
                                actors=actor_ids,
                            )
                        )
            else:
                if block in active:
                    active.remove(block)
    return conflicts


def resolve_with_staggering(
    schedules: Sequence[DailySchedule],
    room_metadata: Mapping[str, Room],
    *,
    increment: timedelta = timedelta(minutes=5),
) -> list[ConflictRecord]:
    increment_minutes = max(int(increment.total_seconds() // 60), 1)
    adjustments: list[ConflictRecord] = []
    flat_list = list(schedules)
    max_iterations = len(flat_list) * 12 if flat_list else 0
    iteration = 0
    while iteration < max_iterations:
        conflicts = detect_room_capacity_conflicts(flat_list, room_metadata)
        if not conflicts:
            break
        conflict = conflicts[0]
        room_blocks = [block for block in flat_list if block.room_id == conflict.room and block.actor_id in conflict.actors]
        if not room_blocks:
            break
        block_to_shift = max(room_blocks, key=lambda block: (block.start_tick, block.actor_id))
        original_start = block_to_shift.start_tick
        block_to_shift.shift_by(increment_minutes)
        adjustments.append(
            ConflictRecord(
                room=conflict.room,
                start_tick=original_start,
                end_tick=block_to_shift.start_tick,
                capacity=conflict.capacity,
                actors=conflict.actors,
                shift_minutes=increment_minutes,
            )
        )
        iteration += 1
    return adjustments


__all__ = ["ConflictRecord", "detect_room_capacity_conflicts", "resolve_with_staggering"]
