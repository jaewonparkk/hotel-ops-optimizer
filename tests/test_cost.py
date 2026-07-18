import pytest

from engine.cost import (
    INFEASIBLE_COST,
    assignment_cost,
    priority_penalty,
    slot_penalty,
)
from engine.models import Housekeeper, Room, RoomType


def make_room(
    room_type: RoomType = RoomType.STANDARD,
    priority: int = 0,
) -> Room:
    return Room(
        room_id="101",
        floor=1,
        position=10.0,
        room_type=room_type,
        occupancy_nights=1,
        guests=1,
        priority=priority,
        check_in_deadline_minute=240,
    )


def make_housekeeper(
    certified_for_suites: bool = True,
) -> Housekeeper:
    return Housekeeper(
        housekeeper_id="H1",
        start_floor=1,
        start_position=0.0,
        speed_multiplier=1.0,
        available_at_minute=0,
        certified_for_suites=certified_for_suites,
    )


def test_slot_penalty_increases_linearly() -> None:
    assert slot_penalty(0) == 0.0
    assert slot_penalty(1) == 5.0
    assert slot_penalty(2) == 10.0


def test_priority_penalty_is_zero_for_general_room() -> None:
    room = make_room(priority=0)

    assert priority_penalty(room, slot_index=4) == 0.0


def test_priority_penalty_increases_for_later_vip_slots() -> None:
    room = make_room(priority=2)

    assert priority_penalty(room, slot_index=0) == 0.0
    assert priority_penalty(room, slot_index=2) == 40.0


def test_uncertified_housekeeper_cannot_clean_suite() -> None:
    room = make_room(room_type=RoomType.SUITE)
    housekeeper = make_housekeeper(certified_for_suites=False)

    assert assignment_cost(room, housekeeper, slot_index=0) == INFEASIBLE_COST


def test_assignment_cost_combines_all_components() -> None:
    room = make_room(priority=1)
    housekeeper = make_housekeeper()

    # Travel: 5 minutes
    # Cleaning: 25 minutes
    # Slot penalty at k=2: 10
    # Priority penalty: 10 * 1 * 2 = 20
    # Total: 60
    assert assignment_cost(
        room,
        housekeeper,
        slot_index=2,
    ) == pytest.approx(60.0)