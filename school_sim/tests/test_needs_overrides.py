import pytest

from school_sim.bootstrap import load_rooms, load_students, load_timetable
from school_sim.events.event_bus import EventBus
from school_sim.world import World


def _make_world(overrides):
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    config = {
        "start_rating": 75.0,
        "start_budget": 1000,
        "needs_overrides": overrides,
        "room_effects": {},
        "rating": {"base": 75.0, "critical_penalty": 0.5, "recovery_reward": 0.0, "flash_threshold": 2.0},
    }
    return World(rooms, students, timetable, event_bus=EventBus(), game_config=config)


def test_needs_override_critical_reroutes_to_configured_room():
    overrides = {
        "hunger": {"critical": 80, "preempt": 60, "room": "cafeteria"},
        "stress": {"critical": 85, "preempt": 45, "room": "lounge"},
    }
    world = _make_world(overrides)
    student = world.students[0]
    rooms = world.rooms
    schedule = world.timetable.homeroom_schedules.get(student.homeroom, {})

    student.needs["hunger"] = 82.0
    student.choose_target("08:00", schedule, rooms, world.needs_overrides)
    assert student.target_room == "Cafeteria"

    student.needs["hunger"] = 40.0
    student.needs["stress"] = 90.0
    student.choose_target("08:30", schedule, rooms, world.needs_overrides)
    assert student.target_room == "Lounge"


def test_preemptive_override_triggers_during_meal_window():
    overrides = {"hunger": {"critical": 90, "preempt": 60, "room": "cafeteria"}}
    world = _make_world(overrides)
    student = world.students[0]
    rooms = world.rooms

    student.needs["hunger"] = 65.0
    student.choose_target("07:30", {}, rooms, world.needs_overrides)
    assert student.target_room == "Cafeteria"

    student.needs["hunger"] = 40.0
    student.current_room = "ClassroomA"
    student.target_room = None
    student.choose_target("07:30", {}, rooms, world.needs_overrides)
    assert student.target_room != "Cafeteria"


