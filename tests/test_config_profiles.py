import os

import pytest

from game.config import available_profiles, load_config


def test_profile_override_updates_data_paths():
    cfg = load_config(profile='makerlab')
    assert cfg['data']['map_file'] == 'data/campus_map_m5.json'
    assert cfg['data']['npc_schedule_file'] == 'data/npc_schedules_m5.json'


def test_environment_variable_profile(monkeypatch):
    monkeypatch.setenv('SCHOOL_SIM_PROFILE', 'makerlab')
    cfg = load_config()
    assert cfg['data']['map_file'] == 'data/campus_map_m5.json'


def test_unknown_profile_raises():
    available = ', '.join(sorted(available_profiles()))
    with pytest.raises(ValueError):
        load_config(profile='unknown_profile')
