from engine.greedy import assign_rooms_greedy
from engine.hungarian import assign_rooms_hungarian
from engine.metrics import evaluate_assignments
from engine.models import Housekeeper, Room, RoomType


def build_sample_scenario() -> tuple[list[Room], list[Housekeeper]]:
    rooms = [
        Room(
            room_id="101",
            floor=1,
            position=10.0,
            room_type=RoomType.STANDARD,
            occupancy_nights=1,
            guests=1,
            priority=0,
            check_in_deadline_minute=240,
        ),
        Room(
            room_id="102",
            floor=1,
            position=30.0,
            room_type=RoomType.DELUXE,
            occupancy_nights=3,
            guests=2,
            priority=2,
            check_in_deadline_minute=120,
        ),
        Room(
            room_id="201",
            floor=2,
            position=15.0,
            room_type=RoomType.STANDARD,
            occupancy_nights=2,
            guests=1,
            priority=1,
            check_in_deadline_minute=180,
        ),
        Room(
            room_id="202",
            floor=2,
            position=40.0,
            room_type=RoomType.SUITE,
            occupancy_nights=4,
            guests=3,
            priority=2,
            check_in_deadline_minute=150,
        ),
        Room(
            room_id="301",
            floor=3,
            position=10.0,
            room_type=RoomType.DELUXE,
            occupancy_nights=1,
            guests=2,
            priority=0,
            check_in_deadline_minute=300,
        ),
        Room(
            room_id="302",
            floor=3,
            position=35.0,
            room_type=RoomType.STANDARD,
            occupancy_nights=5,
            guests=2,
            priority=1,
            check_in_deadline_minute=210,
        ),
    ]

    housekeepers = [
        Housekeeper(
            housekeeper_id="H1",
            start_floor=1,
            start_position=0.0,
            speed_multiplier=1.0,
            available_at_minute=0,
            certified_for_suites=False,
        ),
        Housekeeper(
            housekeeper_id="H2",
            start_floor=2,
            start_position=20.0,
            speed_multiplier=0.9,
            available_at_minute=0,
            certified_for_suites=True,
        ),
        Housekeeper(
            housekeeper_id="H3",
            start_floor=3,
            start_position=0.0,
            speed_multiplier=1.1,
            available_at_minute=15,
            certified_for_suites=True,
        ),
    ]

    return rooms, housekeepers


def print_assignments(name: str, assignments) -> None:
    print(f"\n{name} assignments")
    print("-" * 50)

    for assignment in assignments:
        print(
            f"{assignment.housekeeper.housekeeper_id} "
            f"slot {assignment.slot_index} -> "
            f"Room {assignment.room.room_id} "
            f"(cost={assignment.cost:.2f})"
        )


def print_metrics(name: str, assignments) -> None:
    metrics = evaluate_assignments(assignments)

    print(f"\n{name} metrics")
    print("-" * 50)
    print(f"Makespan:          {metrics.makespan:.2f}")
    print(f"Workload std:      {metrics.workload_std:.2f}")
    print(f"Total travel:      {metrics.total_travel:.2f}")
    print(f"VIP mean ready:    {metrics.vip_mean_ready:.2f}")
    print(f"Deadline misses:   {metrics.deadline_misses}")
    print(f"Total cost:        {metrics.total_cost:.2f}")


def main() -> None:
    rooms, housekeepers = build_sample_scenario()

    greedy_assignments = assign_rooms_greedy(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    hungarian_assignments = assign_rooms_hungarian(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    print_assignments("Greedy", greedy_assignments)
    print_metrics("Greedy", greedy_assignments)

    print_assignments("Hungarian", hungarian_assignments)
    print_metrics("Hungarian", hungarian_assignments)


if __name__ == "__main__":
    main()