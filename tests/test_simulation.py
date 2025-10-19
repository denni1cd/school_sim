from pathlib import Path

import pytest

from game.actors.base_actor import NPCState
from game.config import load_config
from game.simulation import Simulation

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

    dorm_center = simulation.grid.room_center('Dorm')
    assert all((npc.x, npc.y) == dorm_center for npc in simulation.npcs)

    _advance(simulation, 70)

    class_rect = simulation.grid.rooms['ClassA'].rect
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
    assert moving >= 3
