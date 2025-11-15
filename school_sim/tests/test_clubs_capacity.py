import copy

from school_sim.bootstrap import (
    load_clubs_config,
    load_game_config,
    load_policies_config,
    load_rooms,
    load_students,
    load_timetable,
)
from school_sim.events.event_bus import EventBus
from school_sim.world import World


def _build_world(clubs_config: dict) -> World:
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    return World(
        rooms,
        students,
        timetable,
        event_bus=EventBus(),
        game_config=load_game_config(),
        policy_config=load_policies_config(),
        clubs_config=copy.deepcopy(clubs_config),
    )


def test_club_overflow_applies_penalty_and_event():
    clubs = load_clubs_config()
    clubs = copy.deepcopy(clubs)
    clubs["clubs"][0]["capacity"] = 1
    world = _build_world(clubs)
    club_id = clubs["clubs"][0]["id"]
    initial_rating = world.rating
    baseline_stress = {student.name: student.needs["stress"] for student in world.students}

    for student in world.students:
        assert world.assign_student_to_club(student.name, club_id)

    world.tick(dt_minutes=10)
    world.tick(dt_minutes=10)
    world.tick(dt_minutes=10)

    stresses = {student.name: student.needs["stress"] for student in world.students}
    assert any(stresses[name] > baseline_stress[name] for name in stresses)
    assert world.rating_breakdown["clubs"] < 0
    overflow_events = [event for event in world.event_history if event["id"] == "club_overflow"]
    assert overflow_events
