from game.interface import CommandDispatcher, CommandError, PrincipalControls


def test_override_schedule_updates_daily_plan(simulation) -> None:
    controls = PrincipalControls(simulation)
    blocks = controls.override_schedule(
        'Alice',
        [
            {
                'start': '08:00',
                'activity': 'study',
                'room': 'Library',
                'duration': '01:15',
            }
        ],
    )
    assert blocks[0].activity_id == 'study'
    plan = simulation.schedule_system.daily_plan['Alice']
    assert plan[0].activity_id == 'study'


def test_summon_sets_destination(simulation) -> None:
    controls = PrincipalControls(simulation)
    activity = controls.summon_student('Alice', 'Administration', duration_minutes=15)
    npc = simulation.get_npc('Alice')
    assert npc is not None
    assert npc.pending_schedule == activity
    assert npc.target is not None
    assert npc.state.value == 'moving'


def test_command_dispatcher_round_trip(simulation) -> None:
    controls = PrincipalControls(simulation)
    dispatcher = CommandDispatcher(controls)
    result = dispatcher.execute(
        'schedule override Alice start=09:00 activity=study room=Library duration=01:00'
    )
    assert 'Override applied' in result.message
    result = dispatcher.execute('summon Alice Administration duration=00:15')
    assert 'Summoning Alice' in result.message
    result = dispatcher.execute('broadcast message="Testing" audience.role=faculty')
    assert 'Broadcast queued' in result.message
    alert = simulation.alert_bus.publish(
        'Overcapacity',
        minute_stamp=120,
        severity='medium',
        message='Library crowding',
        room_id='Library',
        npc_ids=['Test'],
    )
    result = dispatcher.execute(f'alerts resolve {alert.id}')
    assert 'Alert' in result.message


def test_command_dispatcher_rejects_unknown(simulation) -> None:
    controls = PrincipalControls(simulation)
    dispatcher = CommandDispatcher(controls)
    try:
        dispatcher.execute('unknown command')
    except CommandError:
        pass
    else:
        raise AssertionError('CommandError not raised')
