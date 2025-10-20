from datetime import timedelta

from game.core.map import Room
from game.simulation.conflict_resolver import (
    ConflictRecord,
    detect_room_capacity_conflicts,
    resolve_with_staggering,
)
from game.simulation.schedule_generator import DailySchedule


def _make_room(name: str, capacity: int) -> Room:
    return Room(name=name, rect=(0, 0, 4, 4), doors=((0, 0),), room_type='Test', capacity=capacity)


def test_conflict_detection_and_resolution():
    room = _make_room('Library', capacity=1)
    schedules = [
        DailySchedule(
            actor_id='Alice',
            slot='study',
            activity_id='study',
            room_id='Library',
            start_tick=480,
            duration_minutes=60,
            day_length_minutes=1440,
        ),
        DailySchedule(
            actor_id='Bea',
            slot='study',
            activity_id='study',
            room_id='Library',
            start_tick=480,
            duration_minutes=60,
            day_length_minutes=1440,
        ),
    ]

    conflicts = detect_room_capacity_conflicts(schedules, {'Library': room})
    assert conflicts
    adjustment_records = resolve_with_staggering(schedules, {'Library': room}, increment=timedelta(minutes=5))
    assert adjustment_records
    shifted = next(block for block in schedules if block.actor_id == 'Bea')
    assert shifted.start_tick == 540
    # No conflicts remain after staggering.
    remaining = detect_room_capacity_conflicts(schedules, {'Library': room})
    assert not remaining
