"""Validate the rating system's delta and smoothing logic."""

import pytest

from school_sim.bootstrap import load_rooms, load_students, load_timetable
from school_sim.events.event_bus import EventBus
from school_sim.world import World


def _world_with_rating(config_overrides=None):
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    base_rating = {
        "base": 80.0,
        "flash_threshold": 2.0,
        "weights": {"needs": 0.6, "compliance": 0.2, "clubs": 0.1, "attendance": 0.1},
        "smoothing": 0.05,
        "needs_baseline": 0.9,
        "club_baseline": 0.5,
        "attendance_baseline": 0.95,
    }
    if config_overrides and "rating" in config_overrides:
        base_rating.update(config_overrides["rating"])
    config = {
        "start_rating": 80.0,
        "start_budget": 1000,
        "needs_overrides": {
            "stress": {"critical": 85, "preempt": 45, "room": "lounge"},
        },
        "room_effects": {},
        "rating": base_rating,
    }
    if config_overrides:
        config.update({k: v for k, v in config_overrides.items() if k != "rating"})
    return World(rooms, students, timetable, event_bus=EventBus(), game_config=config)


def test_rating_penalises_critical_needs_and_flashes():
    world = _world_with_rating()
    student = world.students[0]
    student.needs["stress"] = 90.0

    world.tick(dt_minutes=1)
    snapshot = world.get_debug_snapshot()
    assert snapshot["rating"] == pytest.approx(79.1583, rel=1e-3)
    assert snapshot["rating_flash"] is False
    assert snapshot["rating_delta"] == pytest.approx(-0.8417, rel=1e-3)

    student.needs["stress"] = 10.0
    world.tick(dt_minutes=1)
    snapshot = world.get_debug_snapshot()
    assert snapshot["rating"] == pytest.approx(79.4833, rel=1e-3)
    assert snapshot["rating_flash"] is False
    assert snapshot["rating_delta"] == pytest.approx(0.3250, rel=1e-3)
