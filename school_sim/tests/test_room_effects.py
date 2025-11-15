"""Verify room effects adjust student needs as configured."""

import math

from school_sim.room import Room
from school_sim.student import Student


def make_room(name: str, room_type: str) -> Room:
    return Room(name=name, room_type=room_type, x=0, y=0, width=10, height=10)


def make_student(**needs_overrides):
    student = Student(name="Test", homeroom="homeroom_A", current_room="ClassroomA")
    for key, value in needs_overrides.items():
        student.needs[key] = value
    return student


def test_cafeteria_reduces_hunger_and_clamps_to_zero():
    student = make_student(hunger=95.0)
    room = make_room("Cafeteria", "cafeteria")

    deltas = room.apply_effects(student, minutes=10.0)

    assert math.isclose(student.needs["hunger"], 83.0)
    assert math.isclose(deltas["hunger"], -12.0)


def test_dorm_increases_energy_and_clamps_to_hundred():
    student = make_student(energy=99.0)
    room = make_room("Dorm", "dorm")

    room.apply_effects(student, minutes=5.0)

    assert math.isclose(student.needs["energy"], 100.0)


def test_lounge_reduces_stress_without_going_negative():
    student = make_student(stress=2.0)
    room = make_room("Lounge", "lounge")

    deltas = room.apply_effects(student, minutes=5.0)

    assert student.needs["stress"] == 0.0
    assert math.isclose(deltas["stress"], -2.0)


def test_classroom_increases_stress_and_knowledge():
    student = make_student(stress=10.0)
    room = make_room("Classroom", "classroom")

    deltas = room.apply_effects(student, minutes=3.0)

    assert math.isclose(student.needs["stress"], 11.8)
    assert math.isclose(deltas["stress"], 1.8)
    assert math.isclose(student.stats["knowledge"], 1.5)
    assert math.isclose(deltas["knowledge"], 1.5)
