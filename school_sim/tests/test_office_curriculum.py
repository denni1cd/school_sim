from school_sim.bootstrap import (
    load_clubs_config,
    load_curriculum_config,
    load_game_config,
    load_policies_config,
    load_rooms,
    load_students,
    load_timetable,
)
from school_sim.events.event_bus import EventBus
from school_sim.office import OfficeScreen
from school_sim.world import World


def build_world_and_office():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    game_config = load_game_config()
    policies = load_policies_config()
    clubs = load_clubs_config()
    curriculum = load_curriculum_config()
    bus = EventBus()
    world = World(
        rooms,
        students,
        timetable,
        event_bus=bus,
        game_config=game_config,
        policy_config=policies,
        clubs_config=clubs,
        curriculum_config=curriculum,
    )
    office = OfficeScreen(
        policies=policies,
        clubs=clubs,
        curriculum=curriculum,
    )
    office.bind_world(world)
    office.open()
    return world, office, bus


def test_office_curriculum_switch_triggers_world_and_overlay():
    world, office, bus = build_world_and_office()
    captured = []
    bus.subscribe("curriculum_overlay", lambda payload: captured.append(payload))

    office.select_tab(2)  # Curriculum tab
    office.focus_policy_option(1)  # highlight STEM
    result = office.activate(world)

    assert result is not None
    assert result.overlay_caption is not None
    assert "Curriculum focus" in result.overlay_caption
    assert world.curriculum_state["active_track"] == "STEM"
    assert captured, "curriculum overlay event should be emitted"
    view = office.get_active_view(world.get_debug_snapshot())
    assert any("STEM" in line for line in view.lines)
