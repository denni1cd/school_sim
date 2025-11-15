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


def _build_world(clubs_config: dict | None = None) -> World:
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    clubs = copy.deepcopy(clubs_config or load_clubs_config())
    return World(
        rooms,
        students,
        timetable,
        event_bus=EventBus(),
        game_config=load_game_config(),
        policy_config=load_policies_config(),
        clubs_config=clubs,
    )


def test_club_assignment_deducts_budget():
    clubs = load_clubs_config()
    world = _build_world(clubs)
    club_id = clubs["clubs"][0]["id"]
    assign_cost = clubs["costs"].get("assign_student", 0)
    starting_budget = world.budget

    assert world.assign_student_to_club(world.students[0].name, club_id) is True
    assert world.budget == starting_budget - assign_cost
    assert world.get_student(world.students[0].name).club_id == club_id

    # Insufficient budget blocks assignment
    world.budget = 0
    assert world.assign_student_to_club(world.students[1].name, club_id) is False
