import pytest

from school_sim.bootstrap import load_policies_config, load_rooms, load_students, load_timetable
from school_sim.world import World


def _build_world(policy_config=None):
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    policies = policy_config or load_policies_config()
    config = {"start_budget": 1000, "start_rating": 75.0}
    return World(rooms, students, timetable, game_config=config, policy_config=policies)


def test_uniform_change_affects_needs_and_budget():
    baseline_world = _build_world()
    student = baseline_world.students[0]
    before = {"stress": student.needs["stress"], "hygiene": student.needs["hygiene"]}
    baseline_world.tick(dt_minutes=1)
    moderate_stress_delta = student.needs["stress"] - before["stress"]
    moderate_hygiene_delta = student.needs["hygiene"] - before["hygiene"]

    strict_world = _build_world()
    cost = strict_world.policy_config.get("costs", {}).get("change_policy", 0)
    budget_before = strict_world.budget
    message = strict_world.change_uniform_policy("strict")
    assert "Strict" in message
    assert strict_world.policy_state["uniforms"] == "strict"
    assert strict_world.budget == budget_before - cost

    student_strict = strict_world.students[0]
    before_strict = {"stress": student_strict.needs["stress"], "hygiene": student_strict.needs["hygiene"]}
    strict_world.tick(dt_minutes=1)
    strict_stress_delta = student_strict.needs["stress"] - before_strict["stress"]
    strict_hygiene_delta = student_strict.needs["hygiene"] - before_strict["hygiene"]

    assert strict_stress_delta == pytest.approx(moderate_stress_delta + 0.15, abs=1e-6)
    assert strict_hygiene_delta == pytest.approx(moderate_hygiene_delta + 0.10, abs=1e-6)
