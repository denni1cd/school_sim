from game.simulation.activities import ActivityCatalog, ActivityFactory


CATALOG_PATH = 'config/activities.yaml'


def test_breakfast_activity_has_meal_metadata():
    catalog = ActivityCatalog.load(CATALOG_PATH)
    profile = catalog.resolve('breakfast')
    assert profile is not None
    activity = ActivityFactory.create(profile, room_id='Cafeteria', duration=45)
    assert activity.label == 'Breakfast'
    assert activity.room_id == 'Cafeteria'
    assert activity.state.metadata['meal'] == 'breakfast'


def test_sleeping_activity_uses_progress_metadata():
    catalog = ActivityCatalog.load(CATALOG_PATH)
    profile = catalog.resolve('Sleeping')
    assert profile is not None
    activity = ActivityFactory.create(profile, room_id='Dorm_North', duration=120)
    state = activity.on_start()
    assert state.status == 'active'
    activity.tick(60)
    updated = activity.tick(1)
    assert updated is not None
    assert 'stage' in updated.metadata
