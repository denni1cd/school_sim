from game.core.map import MapGrid
from game.simulation.activities import ActivityCatalog, ActivityFactory
from game.world import RoomManager


def test_room_manager_tracks_activity_counts():
    grid = MapGrid('data/campus_map_v1.json')
    catalog = ActivityCatalog.load('config/activities.yaml')
    room_manager = RoomManager(grid)

    breakfast_profile = catalog.resolve('breakfast')
    assert breakfast_profile is not None
    breakfast = ActivityFactory.create(breakfast_profile, room_id='Cafeteria', duration=30)
    sleep_profile = catalog.resolve('Sleeping')
    assert sleep_profile is not None
    sleep = ActivityFactory.create(sleep_profile, room_id='Dorm_North', duration=480)

    room_manager.start_activity('Alice', breakfast)
    room_manager.start_activity('Bob', sleep)
    snapshot_cafe = room_manager.snapshot('Cafeteria')
    snapshot_dorm = room_manager.snapshot('Dorm_North')

    assert snapshot_cafe.activity_counts['Breakfast'] == 1
    assert 'Alice' in snapshot_cafe.occupants
    assert snapshot_dorm.activity_counts['Sleeping'] == 1
    assert 'Bob' in snapshot_dorm.occupants

    breakfast.tick(10)
    room_manager.update_activity('Alice', breakfast)
    updated = room_manager.snapshot('Cafeteria')
    assert updated.activity_counts['Breakfast'] == 1

    room_manager.end_activity('Alice', breakfast)
    finished = room_manager.snapshot('Cafeteria')
    assert finished.activity_counts == {}
    assert not finished.occupants
