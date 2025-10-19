import math
from pathlib import Path

import yaml

from game.simulation import Simulation


def _load_config_with_extensibility_data():
    cfg = yaml.safe_load((Path('config') / 'settings.yaml').read_text())
    cfg = dict(cfg)
    data_cfg = dict(cfg.get('data', {}))
    data_cfg['map_file'] = 'data/campus_map_m5.json'
    data_cfg['npc_schedule_file'] = 'data/npc_schedules_m5.json'
    cfg['data'] = data_cfg
    return cfg


def test_extensible_dataset_adds_new_room_and_npc():
    cfg = _load_config_with_extensibility_data()
    simulation = Simulation(cfg)

    maker_lab = simulation.grid.rooms['MakerLab']
    assert maker_lab.doors
    assert all(simulation.grid.walkable(x, y) for x, y in maker_lab.doors)

    hana = next(npc for npc in simulation.npcs if npc.name == 'Hana')
    assert hana.role == 'student'

    lab_start_time = next(time for time, activity in hana.schedule if activity.name == 'lab_research')
    minutes_until_start = simulation.clock.minutes_until(lab_start_time)
    minutes_per_tick = cfg['time']['minutes_per_tick']
    ticks_to_start = math.ceil(minutes_until_start / minutes_per_tick)
    simulation.advance(ticks_to_start + 150)

    rx, ry, rw, rh = maker_lab.rect
    assert rx <= hana.x < rx + rw
    assert ry <= hana.y < ry + rh
    assert getattr(hana.current_activity, 'name', None) == 'lab_research'

