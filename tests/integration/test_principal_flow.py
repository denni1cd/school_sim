from game.simulation import _hhmm_to_minutes


def test_missed_class_alert(simulation) -> None:
    simulation.alert_bus.clear()
    npc = simulation.get_npc('Alice')
    assert npc is not None
    target_block = None
    start_hhmm = None
    for hhmm, activity in npc.schedule:
        if activity.name == 'class':
            target_block = activity
            start_hhmm = hhmm
            break
    assert target_block is not None
    start_minutes = _hhmm_to_minutes(start_hhmm)
    npc.assign_activity(target_block, start_minutes)
    npc.pending_activity_start_minutes = start_minutes
    npc.pending_destination = None
    npc.x, npc.y = 0, 0
    current = (start_minutes + 40) % simulation.clock.day_length_minutes
    simulation._check_missed_class(npc, current)
    alerts = simulation.alert_bus.active_alerts()
    assert any(alert.category == 'MissedClass' for alert in alerts)


def test_curfew_violation_alert(simulation) -> None:
    simulation.alert_bus.clear()
    npc = simulation.get_npc('Alice')
    assert npc is not None
    npc.current_activity = None
    npc.x, npc.y = 0, 0
    simulation._check_curfew(npc, 23 * 60)
    alerts = simulation.alert_bus.active_alerts()
    assert any(alert.category == 'CurfewViolation' for alert in alerts)


def test_overcapacity_alert(simulation) -> None:
    simulation.alert_bus.clear()
    crowded_room = next(room for room in simulation.grid.rooms.values() if room.capacity and room.capacity <= 6)
    for idx in range(crowded_room.capacity + 1):
        simulation.room_manager.track_entry(f'TestNPC{idx}', crowded_room.name)
    simulation._evaluate_capacity_alerts(480)
    alerts = simulation.alert_bus.active_alerts()
    assert any(alert.category == 'Overcapacity' for alert in alerts)
