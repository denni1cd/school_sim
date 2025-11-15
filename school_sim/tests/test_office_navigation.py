"""Verify office tab navigation cycles correctly."""

import copy
import pytest

from school_sim.bootstrap import (
    load_clubs_config,
    load_game_config,
    load_policies_config,
    load_rooms,
    load_students,
    load_timetable,
)
from school_sim.events.event_bus import EventBus
from school_sim.office import OfficeScreen
from school_sim.world import World


def _world_with_office():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    policies = load_policies_config()
    clubs = load_clubs_config()
    world = World(
        rooms,
        students,
        timetable,
        event_bus=EventBus(),
        game_config=load_game_config(),
        policy_config=policies,
        clubs_config=clubs,
    )
    office = OfficeScreen(policies=policies, clubs=clubs)
    office.bind_world(world)
    office.open()
    return world, office


def test_office_enter_changes_uniform_policy():
    world, office = _world_with_office()
    view = office.get_active_view()
    assert view.title == "Policies"

    office.set_policy_target("uniforms", "strict")
    result = office.activate(world)
    assert result is not None
    assert "Strict" in (result.message or "")
    assert result.overlay_caption == result.message
    assert world.policy_state["uniforms"] == "strict"

    cost = world.policy_config.get("costs", {}).get("change_policy", 0)
    assert world.budget == 1000 - cost

    refreshed = office.get_active_view()
    assert any("Uniforms: Strict" in line for line in refreshed.lines)


def test_office_cursor_switches_between_policies():
    world, office = _world_with_office()
    office.focus_policy_option(1)
    office.set_policy_target("discipline", "tough")
    result = office.activate(world)
    assert result is not None and "Discipline" in (result.message or "")
    assert world.policy_state["discipline"] == "tough"


def test_office_reports_include_club_members():
    world, office = _world_with_office()
    clubs = load_clubs_config()
    club_id = clubs["clubs"][0]["id"]
    world.assign_student_to_club(world.students[0].name, club_id)
    office.select_tab(1)  # Clubs tab
    snapshot = world.get_debug_snapshot()
    view = office.get_active_view(snapshot)
    assert any("Members" in line for line in view.lines)
    assert world.students[0].name in " ".join(view.lines)
