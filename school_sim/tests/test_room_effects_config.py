"""Ensure room effect configuration layers defaults and overrides."""

import pytest

from school_sim.bootstrap import load_rooms, load_students, load_timetable
from school_sim.events.event_bus import EventBus
from school_sim.world import World


def test_room_effects_respect_config_values():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    config = {
        "room_effects": {"cafeteria": {"hunger": -5.0}, "classroom": {"stress": 0.2, "knowledge": 1.5}},
        "needs_overrides": {},
        "rating": {},
    }
    world = World(rooms, students, timetable, event_bus=EventBus(), game_config=config)
    student = world.students[0]
    student.current_room = "Cafeteria"
    cafeteria = world.rooms[student.current_room]

    baseline = student.needs["hunger"]
    delta = cafeteria.apply_effects(student, minutes=1.0)
    assert pytest.approx(baseline - 5.0, rel=1e-3) == student.needs["hunger"]
    assert pytest.approx(-5.0, rel=1e-3) == delta["hunger"]

    classroom = world.rooms["ClassroomA"]
    student.current_room = "ClassroomA"
    delta = classroom.apply_effects(student, minutes=1.0)
    assert pytest.approx(0.2, rel=1e-3) == delta["stress"]
    assert pytest.approx(1.5, rel=1e-3) == delta["knowledge"]
