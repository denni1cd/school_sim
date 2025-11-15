"""Assert student need decay and recovery rules match expectations."""

from school_sim.room import Room
from school_sim.student import (
    CRITICAL_ENERGY,
    CRITICAL_HUNGER,
    CRITICAL_HYGIENE,
    CRITICAL_STRESS,
    RECOVERY_ENERGY_EXIT,
    RECOVERY_HUNGER_EXIT,
    RECOVERY_HYGIENE_EXIT,
    RECOVERY_STRESS_EXIT,
    Student,
)


def make_rooms():
    return {
        "ClassroomA": Room("ClassroomA", "classroom", 0, 0, 10, 10),
        "Cafeteria": Room("Cafeteria", "cafeteria", 0, 0, 10, 10),
        "DormA": Room("DormA", "dorm", 0, 0, 10, 10),
        "Lounge": Room("Lounge", "lounge", 0, 0, 10, 10),
        "BathroomA": Room("BathroomA", "bathroom", 0, 0, 10, 10),
    }


def make_student():
    return Student(name="Alice", homeroom="homeroom_A", current_room="ClassroomA")


def test_decay_needs_matches_specification_rates():
    student = make_student()
    student.needs["hunger"] = 40.0
    student.needs["stress"] = 10.0
    student.needs["energy"] = 80.0
    student.needs["hygiene"] = 70.0

    student.decay_needs(minutes=2.0)

    assert student.needs["hunger"] == 41.0
    assert student.needs["stress"] == 10.4
    assert student.needs["energy"] == 79.2
    assert student.needs["hygiene"] == 69.6


def test_hunger_override_targets_cafeteria():
    student = make_student()
    student.needs["hunger"] = CRITICAL_HUNGER
    rooms = make_rooms()

    student.choose_target("09:00", {}, rooms)

    assert student.target_room == "Cafeteria"


def test_energy_override_targets_dorm():
    student = make_student()
    student.needs["energy"] = CRITICAL_ENERGY
    rooms = make_rooms()

    student.choose_target("02:00", {}, rooms)

    assert student.target_room == "DormA"


def test_hygiene_override_targets_bathroom():
    student = make_student()
    student.needs["hygiene"] = CRITICAL_HYGIENE
    rooms = make_rooms()

    student.choose_target("09:00", {}, rooms)

    assert student.target_room == "BathroomA"


def test_stress_override_targets_lounge():
    student = make_student()
    student.needs["stress"] = CRITICAL_STRESS
    rooms = make_rooms()

    student.choose_target("09:00", {}, rooms)

    assert student.target_room == "Lounge"


def test_student_stays_in_room_until_recovery_threshold_met():
    student = make_student()
    student.current_room = "Cafeteria"
    student.target_room = "Cafeteria"
    student.needs["hunger"] = RECOVERY_HUNGER_EXIT + 5.0
    rooms = make_rooms()

    student.choose_target("12:00", {}, rooms)

    assert student.target_room == "Cafeteria"


def test_student_leaves_room_after_recovery_threshold_crossed():
    student = make_student()
    student.current_room = "DormA"
    student.target_room = "DormA"
    student.needs["energy"] = RECOVERY_ENERGY_EXIT + 5.0
    rooms = make_rooms()
    schedule = {"09:00": "ClassroomA"}

    student.choose_target("09:00", schedule, rooms)

    assert student.target_room == "ClassroomA"


def test_stress_recovery_threshold_matches_specification():
    student = make_student()
    student.current_room = "Lounge"
    student.target_room = "Lounge"
    student.needs["stress"] = RECOVERY_STRESS_EXIT - 5.0
    rooms = make_rooms()

    student.choose_target("09:00", {}, rooms)

    assert student.target_room == "Lounge"


def test_hygiene_recovery_threshold_matches_specification():
    student = make_student()
    student.current_room = "BathroomA"
    student.target_room = "BathroomA"
    student.needs["hygiene"] = RECOVERY_HYGIENE_EXIT - 5.0
    rooms = make_rooms()

    student.choose_target("09:00", {}, rooms)

    assert student.target_room == "BathroomA"
