from game.notifications import AlertBus


def test_publish_and_acknowledge() -> None:
    bus = AlertBus(cooldown_minutes=10)
    observed = []

    def _listener(alert):  # type: ignore[no-redef]
        observed.append(alert.id)

    bus.subscribe(_listener)
    alert = bus.publish(
        'Overcapacity',
        minute_stamp=100,
        severity='medium',
        message='Test alert',
        room_id='Library',
        npc_ids=['Alice'],
    )
    assert alert.id in observed
    bus.acknowledge(alert.id, minute_stamp=105)
    assert not bus.active_alerts()
    bus.unsubscribe(_listener)


def test_cooldown_returns_existing_alert() -> None:
    bus = AlertBus(cooldown_minutes=15)
    first = bus.publish(
        'CurfewViolation',
        minute_stamp=60,
        severity='medium',
        message='Initial',
        room_id=None,
        npc_ids=['Bea'],
    )
    second = bus.publish(
        'CurfewViolation',
        minute_stamp=70,
        severity='medium',
        message='Repeat',
        room_id=None,
        npc_ids=['Bea'],
    )
    assert first.id == second.id


def test_acknowledged_alert_respects_cooldown_and_persists_history() -> None:
    bus = AlertBus(cooldown_minutes=10)
    first = bus.publish(
        'Overcapacity',
        minute_stamp=100,
        severity='high',
        message='Dorm crowding',
        room_id='Dorm_South',
        npc_ids=['Alice', 'Bea'],
    )
    bus.acknowledge(first.id, minute_stamp=103)

    repeat = bus.publish(
        'Overcapacity',
        minute_stamp=105,
        severity='high',
        message='Dorm crowding again',
        room_id='Dorm_South',
        npc_ids=['Alice', 'Bea'],
    )
    assert repeat.id == first.id

    later = bus.publish(
        'Overcapacity',
        minute_stamp=120,
        severity='medium',
        message='Dorm relieved',
        room_id='Dorm_South',
        npc_ids=['Alice', 'Bea'],
    )
    assert later.id != first.id

    history = list(bus.iter_history())
    assert len(history) == 2
    assert history[0].id == first.id
    assert history[1].id == later.id
