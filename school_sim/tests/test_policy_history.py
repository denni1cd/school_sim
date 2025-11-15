from school_sim.bootstrap import load_policies_config, load_rooms, load_students, load_timetable
from school_sim.world import World


def _build_world():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    policies = load_policies_config()
    return World(rooms, students, timetable, policy_config=policies)


def test_policy_history_records_changes_and_limits():
    world = _build_world()
    assert not world.policy_history

    world.change_uniform_policy("strict")
    assert world.policy_history
    entry = world.policy_history[-1]
    assert entry["policy"] == "uniforms"
    assert entry["value"] == "Strict"
    assert entry["delta"] < 0
    assert "policy" in entry["caption"].lower()

    # Create enough history entries to exceed the cap (5 entries).
    for level in ["moderate", "relaxed", "strict", "moderate", "relaxed", "strict"]:
        world.change_uniform_policy(level)

    assert len(world.policy_history) <= 5
    for entry in world.policy_history:
        assert entry["policy"] == "uniforms"
        assert "time" in entry
