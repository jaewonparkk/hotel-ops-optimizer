from engine.models import Housekeeper, Room, RoomType
import pytest


def test_base_clean_time() -> None:
    room = Room(
        room_id="301",
        floor=3,
        position=20.0,
        room_type=RoomType.SUITE,
        occupancy_nights=3,
        guests=2,
        priority=2,
        check_in_deadline_minute=180,
    )

    assert room.base_clean_time() == 57.0


def test_housekeeper_clean_time() -> None:
    room = Room(
        room_id="301",
        floor=3,
        position=20.0,
        room_type=RoomType.SUITE,
        occupancy_nights=3,
        guests=2,
        priority=2,
        check_in_deadline_minute=180,
    )

    housekeeper = Housekeeper(
        housekeeper_id="H1",
        start_floor=1,
        start_position=10.0,
        speed_multiplier=0.9,
        available_at_minute=0,
        certified_for_suites=True,
    )

    assert housekeeper.clean_time(room) == pytest.approx(51.3)


def test_travel_time() -> None:
    room = Room(
        room_id="301",
        floor=3,
        position=20.0,
        room_type=RoomType.SUITE,
        occupancy_nights=1,
        guests=1,
        priority=0,
        check_in_deadline_minute=180,
    )

    housekeeper = Housekeeper(
        housekeeper_id="H1",
        start_floor=1,
        start_position=10.0,
        speed_multiplier=1.0,
        available_at_minute=0,
        certified_for_suites=True,
    )

    assert housekeeper.travel_time(room) == pytest.approx(11.0)