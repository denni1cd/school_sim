"""Check budget adjustments and transaction history management."""

import pytest

from school_sim import economy
from school_sim.bootstrap import (
    load_clubs_config,
    load_game_config,
    load_policies_config,
    load_rooms,
    load_students,
    load_timetable,
)
from school_sim.events.event_bus import EventBus
from school_sim.world import World


def build_world() -> World:
    return World(
        load_rooms(),
        load_students(),
        load_timetable(),
        event_bus=EventBus(),
        game_config=load_game_config(),
        policy_config=load_policies_config(),
        clubs_config=load_clubs_config(),
    )


def test_adjust_budget_prevents_negative_balances():
    assert economy.adjust_budget(1000, -250) == 750
    with pytest.raises(ValueError):
        economy.adjust_budget(50, -100)


def test_policy_change_records_transaction():
    world = build_world()
    initial_history_len = len(world.economy_history)

    world.change_uniform_policy("strict")

    assert len(world.economy_history) == initial_history_len + 1
    entry = world.economy_history[-1]
    assert "Policy change" in entry.reason
    assert entry.delta < 0
    assert entry.balance == world.budget
