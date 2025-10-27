from game.actors.base_actor import NPCState
from game.simulation import _hhmm_to_minutes


def test_activity_interrupt_clears_room_state(simulation) -> None:
    npc = simulation.get_npc('Alice')
    assert npc is not None

    block_entry = next((entry for entry in npc.schedule if entry[1].location), None)
    assert block_entry is not None
    start_time, scheduled = block_entry
    start_minutes = _hhmm_to_minutes(start_time)

    simulation.event_logger.clear()
    npc.assign_activity(scheduled, start_minutes)
    npc.target = None
    npc.pending_destination = None
    npc.state = NPCState.IDLE
    npc.x, npc.y = simulation.grid.room_center(scheduled.location)

    simulation.activity_system.start_if_ready(
        npc,
        current_minutes=start_minutes,
        day_length_minutes=simulation.clock.day_length_minutes,
    )

    assert npc.current_activity is not None

    snapshot = simulation.room_manager.snapshot(scheduled.location)
    assert npc.name in snapshot.occupants

    simulation.activity_system.interrupt(npc, reason='test', current_minutes=start_minutes + 5)

    assert npc.current_activity is None
    updated = simulation.room_manager.snapshot(scheduled.location)
    assert npc.name not in updated.occupants

    events = list(simulation.event_logger.iter_events())
    assert any(event.kind == 'activity_interrupt' and event.npc == npc.name for event in events)
