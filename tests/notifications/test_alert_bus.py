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
