from school_sim.bootstrap import load_policies_config, load_rooms, load_students, load_timetable
from school_sim.world import World


def _world_for_discipline(level: str) -> World:
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    policies = load_policies_config()
    policies["compliance_weight"] = 4.0
    config = {
        "start_budget": 1000,
        "start_rating": 75.0,
        "rating": {"base": 75.0, "critical_penalty": 0.0, "recovery_reward": 0.0, "flash_threshold": 5.0},
    }
    world = World(rooms, students, timetable, game_config=config, policy_config=policies)
    world.change_discipline_policy(level)
    return world


def _run_ticks(world: World, count: int = 6) -> float:
    for _ in range(count):
        world.tick(dt_minutes=1)
    return world.rating, world.last_compliance_score


def test_discipline_affects_compliance_and_rating():
    tough_world = _world_for_discipline("tough")
    lenient_world = _world_for_discipline("lenient")

    tough_rating, tough_compliance = _run_ticks(tough_world)
    lenient_rating, lenient_compliance = _run_ticks(lenient_world)

    assert tough_compliance > lenient_compliance
    assert tough_rating > lenient_rating
