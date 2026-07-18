import pytest

from engine.metrics import (
    calculate_completion_times,
    calculate_workloads,
    evaluate_assignments,
)
from engine.models import Assignment, Housekeeper, Room, RoomType


def make_room(
    room_id: str,
    floor: int = 1,
    position: float = 10.0,
    priority: int = 0,
    check_in_deadline_minute: int = 240,
) -> Room:
    return Room(
        room_id=room_id,
        floor=floor,
        position=position,
        room_type=RoomType.STANDARD,
        occupancy_nights=1,
        guests=1,
        priority=priority,
        check_in_deadline_minute=check_in_deadline_minute,
    )


def make_housekeeper(
    housekeeper_id: str,
    start_floor: int = 1,
    start_position: float = 0.0,
    available_at_minute: int = 0,
) -> Housekeeper:
    return Housekeeper(
        housekeeper_id=housekeeper_id,
        start_floor=start_floor,
        start_position=start_position,
        speed_multiplier=1.0,
        available_at_minute=available_at_minute,
        certified_for_suites=True,
    )


def make_assignment(
    housekeeper: Housekeeper,
    room: Room,
    slot_index: int,
    travel_time: float,
    cleaning_time: float,
    cost: float,
) -> Assignment:
    return Assignment(
        housekeeper=housekeeper,
        room=room,
        slot_index=slot_index,
        travel_time=travel_time,
        cleaning_time=cleaning_time,
        cost=cost,
    )


def test_calculate_completion_times() -> None:
    housekeeper = make_housekeeper(
        "H1",
        available_at_minute=10,
    )

    assignments = [
        make_assignment(
            housekeeper=housekeeper,
            room=make_room(
                room_id="101",
                floor=1,
                position=10.0,
            ),
            slot_index=0,
            travel_time=5.0,
            cleaning_time=25.0,
            cost=30.0,
        ),
        make_assignment(
            housekeeper=housekeeper,
            room=make_room(
                room_id="102",
                floor=1,
                position=18.0,
            ),
            slot_index=1,
            travel_time=9.0,
            cleaning_time=20.0,
            cost=29.0,
        ),
    ]

    completion_times = calculate_completion_times(assignments)

    # H1 available at minute 10.
    # Start position 0 -> Room 101 position 10:
    # travel = 10 * 0.5 = 5 minutes.
    # Room 101 completion = 10 + 5 + 25 = 40.
    assert completion_times["101"] == pytest.approx(40.0)

    # Room 101 position 10 -> Room 102 position 18:
    # travel = 8 * 0.5 = 4 minutes.
    # Room 102 completion = 40 + 4 + 20 = 64.
    assert completion_times["102"] == pytest.approx(64.0)


def test_calculate_workloads() -> None:
    h1 = make_housekeeper(
        "H1",
        start_position=0.0,
    )
    h2 = make_housekeeper(
        "H2",
        start_position=0.0,
    )

    assignments = [
        make_assignment(
            housekeeper=h1,
            room=make_room(
                room_id="101",
                position=10.0,
            ),
            slot_index=0,
            travel_time=5.0,
            cleaning_time=25.0,
            cost=30.0,
        ),
        make_assignment(
            housekeeper=h2,
            room=make_room(
                room_id="102",
                position=20.0,
            ),
            slot_index=0,
            travel_time=10.0,
            cleaning_time=20.0,
            cost=30.0,
        ),
    ]

    workloads = calculate_workloads(assignments)

    assert workloads == {
        "H1": 30.0,
        "H2": 30.0,
    }


def test_evaluate_assignments() -> None:
    h1 = make_housekeeper(
        "H1",
        start_position=0.0,
    )
    h2 = make_housekeeper(
        "H2",
        start_position=0.0,
    )

    assignments = [
        make_assignment(
            housekeeper=h1,
            room=make_room(
                room_id="101",
                position=10.0,
                priority=2,
                check_in_deadline_minute=40,
            ),
            slot_index=0,
            travel_time=5.0,
            cleaning_time=25.0,
            cost=30.0,
        ),
        make_assignment(
            housekeeper=h2,
            room=make_room(
                room_id="102",
                position=20.0,
                priority=0,
                check_in_deadline_minute=20,
            ),
            slot_index=0,
            travel_time=10.0,
            cleaning_time=20.0,
            cost=35.0,
        ),
    ]

    metrics = evaluate_assignments(assignments)

    assert metrics.makespan == pytest.approx(30.0)
    assert metrics.workload_std == pytest.approx(0.0)
    assert metrics.total_travel == pytest.approx(15.0)
    assert metrics.vip_mean_ready == pytest.approx(30.0)
    assert metrics.deadline_misses == 1
    assert metrics.total_cost == pytest.approx(65.0)


def test_empty_assignments_return_zero_metrics() -> None:
    metrics = evaluate_assignments([])

    assert metrics.makespan == 0.0
    assert metrics.workload_std == 0.0
    assert metrics.total_travel == 0.0
    assert metrics.vip_mean_ready == 0.0
    assert metrics.deadline_misses == 0
    assert metrics.total_cost == 0.0