import pytest

from engine.greedy import assign_rooms_greedy
from engine.models import Assignment, Housekeeper, Room, RoomType


def make_room(
    room_id: str,
    floor: int = 1,
    position: float = 10.0,
    room_type: RoomType = RoomType.STANDARD,
    priority: int = 0,
) -> Room:
    return Room(
        room_id=room_id,
        floor=floor,
        position=position,
        room_type=room_type,
        occupancy_nights=1,
        guests=1,
        priority=priority,
        check_in_deadline_minute=240,
    )


def make_housekeeper(
    housekeeper_id: str,
    start_floor: int = 1,
    start_position: float = 0.0,
    certified_for_suites: bool = True,
) -> Housekeeper:
    return Housekeeper(
        housekeeper_id=housekeeper_id,
        start_floor=start_floor,
        start_position=start_position,
        speed_multiplier=1.0,
        available_at_minute=0,
        certified_for_suites=certified_for_suites,
    )


def test_returns_assignment_objects() -> None:
    assignments = assign_rooms_greedy(
        rooms=[make_room("101")],
        housekeepers=[make_housekeeper("H1")],
    )

    assert len(assignments) == 1
    assert isinstance(assignments[0], Assignment)


def test_assigns_every_room_once() -> None:
    rooms = [
        make_room("101"),
        make_room("102"),
        make_room("201", floor=2),
        make_room("202", floor=2),
    ]

    assignments = assign_rooms_greedy(
        rooms=rooms,
        housekeepers=[
            make_housekeeper("H1", start_floor=1),
            make_housekeeper("H2", start_floor=2),
        ],
    )

    assigned_room_ids = [
        assignment.room.room_id
        for assignment in assignments
    ]

    assert sorted(assigned_room_ids) == [
        "101",
        "102",
        "201",
        "202",
    ]

    assert len(assigned_room_ids) == len(set(assigned_room_ids))


def test_suite_is_assigned_to_certified_housekeeper() -> None:
    assignments = assign_rooms_greedy(
        rooms=[
            make_room(
                "301",
                room_type=RoomType.SUITE,
            )
        ],
        housekeepers=[
            make_housekeeper(
                "H1",
                certified_for_suites=False,
            ),
            make_housekeeper(
                "H2",
                certified_for_suites=True,
            ),
        ],
    )

    assert len(assignments) == 1
    assert assignments[0].housekeeper.housekeeper_id == "H2"


def test_raises_when_no_feasible_assignment_exists() -> None:
    with pytest.raises(
        ValueError,
        match="No feasible assignment exists",
    ):
        assign_rooms_greedy(
            rooms=[
                make_room(
                    "301",
                    room_type=RoomType.SUITE,
                )
            ],
            housekeepers=[
                make_housekeeper(
                    "H1",
                    certified_for_suites=False,
                )
            ],
        )


def test_empty_rooms_returns_empty_list() -> None:
    assignments = assign_rooms_greedy(
        rooms=[],
        housekeepers=[make_housekeeper("H1")],
    )

    assert assignments == []


def test_rejects_empty_housekeepers() -> None:
    with pytest.raises(
        ValueError,
        match="at least one housekeeper is required",
    ):
        assign_rooms_greedy(
            rooms=[make_room("101")],
            housekeepers=[],
        )