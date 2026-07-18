import numpy as np
import pytest

from engine.cost import INFEASIBLE_COST, assignment_cost
from engine.matrix import (
    HousekeeperSlot,
    build_cost_matrix,
    build_slots,
    calculate_slots_per_housekeeper,
)
from engine.models import Housekeeper, Room, RoomType


def make_housekeeper(
    housekeeper_id: str = "H1",
    certified_for_suites: bool = True,
) -> Housekeeper:
    return Housekeeper(
        housekeeper_id=housekeeper_id,
        start_floor=1,
        start_position=0.0,
        speed_multiplier=1.0,
        available_at_minute=0,
        certified_for_suites=certified_for_suites,
    )


def make_room(
    room_id: str = "101",
    room_type: RoomType = RoomType.STANDARD,
    priority: int = 0,
) -> Room:
    return Room(
        room_id=room_id,
        floor=1,
        position=10.0,
        room_type=room_type,
        occupancy_nights=1,
        guests=1,
        priority=priority,
        check_in_deadline_minute=240,
    )


def test_calculate_slots_per_housekeeper() -> None:
    result = calculate_slots_per_housekeeper(
        number_of_rooms=40,
        number_of_housekeepers=6,
    )

    assert result == 9


def test_calculate_slots_rejects_zero_housekeepers() -> None:
    with pytest.raises(
        ValueError,
        match="number_of_housekeepers must be greater than 0",
    ):
        calculate_slots_per_housekeeper(
            number_of_rooms=40,
            number_of_housekeepers=0,
        )


def test_calculate_slots_rejects_negative_rooms() -> None:
    with pytest.raises(
        ValueError,
        match="number_of_rooms cannot be negative",
    ):
        calculate_slots_per_housekeeper(
            number_of_rooms=-1,
            number_of_housekeepers=2,
        )


def test_build_slots_creates_expected_order() -> None:
    housekeepers = [
        make_housekeeper("H1"),
        make_housekeeper("H2"),
    ]

    slots = build_slots(
        housekeepers=housekeepers,
        slots_per_housekeeper=3,
    )

    assert len(slots) == 6
    assert all(
        isinstance(slot, HousekeeperSlot)
        for slot in slots
    )

    assert slots[0].housekeeper.housekeeper_id == "H1"
    assert slots[0].slot_index == 0

    assert slots[2].housekeeper.housekeeper_id == "H1"
    assert slots[2].slot_index == 2

    assert slots[3].housekeeper.housekeeper_id == "H2"
    assert slots[3].slot_index == 0


def test_build_slots_rejects_nonpositive_slot_count() -> None:
    with pytest.raises(
        ValueError,
        match="slots_per_housekeeper must be greater than 0",
    ):
        build_slots(
            housekeepers=[make_housekeeper()],
            slots_per_housekeeper=0,
        )


def test_build_cost_matrix_returns_numpy_array() -> None:
    rooms = [
        make_room("101"),
        make_room("102"),
        make_room("103"),
        make_room("104"),
    ]

    housekeepers = [
        make_housekeeper("H1"),
        make_housekeeper("H2"),
    ]

    cost_matrix, slots = build_cost_matrix(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    # ceil(4 / 2) + 2 = 4 slots per housekeeper
    # 2 housekeepers * 4 slots = 8 columns
    assert isinstance(cost_matrix, np.ndarray)
    assert cost_matrix.dtype == float
    assert cost_matrix.shape == (4, 8)
    assert len(slots) == 8


def test_build_cost_matrix_uses_assignment_cost() -> None:
    room = make_room()
    housekeeper = make_housekeeper()

    cost_matrix, slots = build_cost_matrix(
        rooms=[room],
        housekeepers=[housekeeper],
    )

    first_slot = slots[0]

    expected = assignment_cost(
        room=room,
        housekeeper=first_slot.housekeeper,
        slot_index=first_slot.slot_index,
    )

    assert cost_matrix[0, 0] == pytest.approx(expected)


def test_later_slots_have_higher_cost() -> None:
    room = make_room()
    housekeeper = make_housekeeper()

    cost_matrix, _ = build_cost_matrix(
        rooms=[room],
        housekeepers=[housekeeper],
    )

    assert cost_matrix[0, 0] < cost_matrix[0, 1]
    assert cost_matrix[0, 1] < cost_matrix[0, 2]


def test_uncertified_housekeeper_cannot_clean_suite() -> None:
    room = make_room(room_type=RoomType.SUITE)
    housekeeper = make_housekeeper(
        certified_for_suites=False
    )

    cost_matrix, _ = build_cost_matrix(
        rooms=[room],
        housekeepers=[housekeeper],
    )

    assert np.all(cost_matrix[0] == INFEASIBLE_COST)


def test_build_cost_matrix_rejects_empty_housekeepers() -> None:
    with pytest.raises(
        ValueError,
        match="at least one housekeeper is required",
    ):
        build_cost_matrix(
            rooms=[make_room()],
            housekeepers=[],
        )