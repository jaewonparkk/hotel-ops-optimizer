import pytest

from engine.models import RoomType
from engine.scenario_generator import generate_random_scenario


def test_generates_requested_number_of_objects() -> None:
    rooms, housekeepers = generate_random_scenario(
        number_of_rooms=40,
        number_of_housekeepers=6,
        seed=42,
    )

    assert len(rooms) == 40
    assert len(housekeepers) == 6


def test_same_seed_produces_same_scenario() -> None:
    first_rooms, first_housekeepers = generate_random_scenario(
        seed=42
    )

    second_rooms, second_housekeepers = generate_random_scenario(
        seed=42
    )

    assert first_rooms == second_rooms
    assert first_housekeepers == second_housekeepers


def test_suite_scenario_has_certified_housekeeper() -> None:
    rooms, housekeepers = generate_random_scenario(
        number_of_rooms=100,
        number_of_housekeepers=6,
        seed=42,
    )

    has_suite = any(
        room.room_type == RoomType.SUITE
        for room in rooms
    )

    if has_suite:
        assert any(
            housekeeper.certified_for_suites
            for housekeeper in housekeepers
        )


def test_rejects_nonpositive_room_count() -> None:
    with pytest.raises(
        ValueError,
        match="number_of_rooms must be greater than 0",
    ):
        generate_random_scenario(
            number_of_rooms=0,
            number_of_housekeepers=6,
        )


def test_rejects_nonpositive_housekeeper_count() -> None:
    with pytest.raises(
        ValueError,
        match="number_of_housekeepers must be greater than 0",
    ):
        generate_random_scenario(
            number_of_rooms=40,
            number_of_housekeepers=0,
        )