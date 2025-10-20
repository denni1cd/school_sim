from pathlib import Path

import pytest

from game.actors.base_actor import NPCState
from game.config import load_config
from game.simulation import Simulation, resolve_map_file

CFG = load_config()


def _position_in_room(position, room_rect):
    x, y = position
    rx, ry, rw, rh = room_rect
    return rx <= x < rx + rw and ry <= y < ry + rh


def _advance(simulation: Simulation, minutes: int) -> None:
    minutes_per_tick = simulation.cfg['time']['minutes_per_tick']
    ticks = int(round(minutes / minutes_per_tick))
    simulation.advance(ticks)


def test_npcs_arrive_for_class_activity():
    simulation = Simulation(CFG)
    assert len(simulation.npcs) >= 7

    dorm_rooms = {'Dorm_North', 'Dorm_South', 'Dorm_Commons'}
    for npc in simulation.npcs:
        room = simulation.grid.room_for_position(npc.x, npc.y)
        assert room is not None
        if npc.role == 'student':
            assert room.name in dorm_rooms

    _advance(simulation, 120)

    class_rect = simulation.grid.rooms['Classroom_STEM'].rect
    positions = {npc.name: (npc.x, npc.y) for npc in simulation.npcs}
    activities = {npc.name: getattr(npc.current_activity, 'name', None) for npc in simulation.npcs}

    in_class = [name for name, pos in positions.items() if _position_in_room(pos, class_rect)]
    assert in_class
    assert any(activity == 'class' for activity in activities.values())

    first_event_times = {npc.schedule[0][0] for npc in simulation.npcs}
    assert len(first_event_times) > 1


def test_library_hosting_librarian():
    simulation = Simulation(CFG)
    _advance(simulation, 200)

    library_rect = simulation.grid.rooms['Library'].rect
    positions = {npc.name: (npc.x, npc.y) for npc in simulation.npcs}
    gina_pos = positions.get('Gina')
    assert gina_pos is not None
    assert _position_in_room(gina_pos, library_rect)


def test_multiple_npcs_move_on_first_tick():
    simulation = Simulation(CFG)
    simulation.tick()
    moving = sum(1 for npc in simulation.npcs if npc.state == NPCState.MOVING)
    assert moving >= 2


def test_destinations_move_npcs_inside_rooms():
    simulation = Simulation(CFG)
    room = simulation.grid.rooms['Classroom_STEM']
    doors = set(room.doors)

    for _ in range(10):
        dest = simulation._select_destination(room.name)
        assert dest not in doors


def test_activity_logging_collects_events():
    simulation = Simulation(CFG)
    _advance(simulation, 180)
    events = list(simulation.event_logger.iter_events())
    assert events, 'Expected activity events to be recorded.'
    sample = events[0]
    assert sample.kind in {'activity_start', 'activity_end', 'activity_interrupt'}
    assert sample.activity


def test_campus_map_alias_uses_latest_layout():
    project_root = Path(__file__).resolve().parents[1]
    expected = project_root / 'data' / 'campus_map_v1.json'
    resolved = resolve_map_file('campus_map', 'data/campus_map_v1.json')
    assert resolved == expected
