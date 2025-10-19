import math

from game.config import load_config
from game.simulation import Simulation


def _advance_minutes(simulation: Simulation, minutes: float) -> None:
    minutes_per_tick = simulation.cfg['time']['minutes_per_tick']
    ticks = math.ceil(minutes / minutes_per_tick)
    simulation.advance(ticks)


def _get_npc(simulation: Simulation, name: str):
    return next(npc for npc in simulation.npcs if npc.name == name)


def test_library_interaction_uses_room_message():
    simulation = Simulation(load_config())
    _advance_minutes(simulation, 200)
    gina = _get_npc(simulation, 'Gina')
    message = simulation.interact_with(gina)
    assert 'whispers' in message.lower()
    assert 'gina' in message.lower()


def test_makerlab_interaction_uses_activity_message():
    simulation = Simulation(load_config(profile='makerlab'))
    hana = _get_npc(simulation, 'Hana')
    lab_start_time = next(time for time, activity in hana.schedule if activity.name == 'lab_research')
    minutes_until_start = simulation.clock.minutes_until(lab_start_time)
    _advance_minutes(simulation, minutes_until_start + 60)
    message = simulation.interact_with(hana)
    assert 'prototype' in message.lower()
    assert 'hana' in message.lower()
