"""Confirm saves persist and restore world state accurately."""

from pathlib import Path

import json
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
from school_sim.save_system import SaveSystem
from school_sim.world import World


def build_world():
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
        clubs_config=load_clubs_config(),
    )


def test_save_load_roundtrip(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path)
    clubs_config = load_clubs_config()
    club_id = clubs_config["clubs"][0]["id"]
    world.assign_student_to_club(world.students[0].name, club_id)
    delta = 4321 - world.budget
    assert world._adjust_budget(delta, reason="Testing grant")
    world.rating = 88.8
    world.rating_breakdown = {"needs": 60.0, "compliance": 20.0}
    world.policy_state = {"uniforms": "strict", "discipline": "fair"}
    world.curriculum_state = {"active_track": "STEM"}

    result = system.save(world)
    world.time_minutes += 25
    for student in world.students:
        student.needs["hunger"] = 99.0

    system.load(result.path, world)

    assert world.time_minutes == result.snapshot["time_minutes"]
    for snapshot_student, student in zip(result.snapshot["students"], world.students):
        assert pytest.approx(snapshot_student["needs"]["hunger"]) == student.needs["hunger"]
        assert snapshot_student["room"] == student.current_room
        if snapshot_student["name"] == world.students[0].name:
            assert snapshot_student.get("club") == club_id
            assert student.club_id == club_id
    assert world.budget == 4321
    assert pytest.approx(world.rating) == 88.8
    assert world.policy_state["uniforms"] == "strict"
    assert world.curriculum_state["active_track"] == "STEM"
    assert world.economy_history
    assert world.economy_history[-1].balance == 4321
    assert world.rating_breakdown.get("needs") == 60.0

    payload = json.loads(result.path.read_text(encoding="utf-8"))
    assert payload["budget"] == 4321
    assert payload["rating"] == pytest.approx(88.8)
    assert payload["students"][0].get("club") == club_id
    assert "policy" in payload and "curriculum" in payload
    assert "economy_history" in payload
    assert payload["economy_history"][-1]["balance"] == 4321
    assert payload["rating_breakdown"]["needs"] == 60.0


def test_load_latest_handles_missing(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path)

    latest = system.load_latest(world)
    assert latest is None


def test_apply_snapshot_handles_legacy_payload(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path)

    legacy_snapshot = {"time_minutes": 480, "students": []}
    system.apply_snapshot(world, legacy_snapshot)
    assert world.time_minutes == 480


def test_invalid_snapshot_raises(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path)
    bad_snapshot = tmp_path / "bad.json"
    bad_snapshot.write_text(json.dumps({"students": []}), encoding="utf-8")

    with pytest.raises(ValueError):
        system.load(bad_snapshot, world)
