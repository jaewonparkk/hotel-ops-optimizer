import random

from engine.models import Housekeeper, Room, RoomType


ROOM_TYPES = [
    RoomType.STANDARD,
    RoomType.DELUXE,
    RoomType.SUITE,
]


def generate_random_scenario(
    number_of_rooms: int = 40,
    number_of_housekeepers: int = 6,
    seed: int | None = None,
) -> tuple[list[Room], list[Housekeeper]]:
    if number_of_rooms <= 0:
        raise ValueError("number_of_rooms must be greater than 0")

    if number_of_housekeepers <= 0:
        raise ValueError(
            "number_of_housekeepers must be greater than 0"
        )

    rng = random.Random(seed)

    rooms = [
        _generate_room(
            room_number=index + 1,
            rng=rng,
        )
        for index in range(number_of_rooms)
    ]

    housekeepers = [
        _generate_housekeeper(
            housekeeper_number=index + 1,
            rng=rng,
        )
        for index in range(number_of_housekeepers)
    ]

    _ensure_suite_coverage(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    return rooms, housekeepers


def _generate_room(
    room_number: int,
    rng: random.Random,
) -> Room:
    floor = rng.randint(1, 8)
    position = rng.uniform(0.0, 100.0)
    room_type = rng.choices(
        population=ROOM_TYPES,
        weights=[0.65, 0.25, 0.10],
        k=1,
    )[0]

    priority = rng.choices(
        population=[0, 1, 2],
        weights=[0.70, 0.20, 0.10],
        k=1,
    )[0]

    return Room(
        room_id=f"R{room_number:03d}",
        floor=floor,
        position=position,
        room_type=room_type,
        occupancy_nights=rng.randint(1, 7),
        guests=rng.randint(1, 4),
        priority=priority,
        check_in_deadline_minute=_generate_deadline(
            priority=priority,
            rng=rng,
        ),
    )


def _generate_housekeeper(
    housekeeper_number: int,
    rng: random.Random,
) -> Housekeeper:
    return Housekeeper(
        housekeeper_id=f"H{housekeeper_number:02d}",
        start_floor=rng.randint(1, 8),
        start_position=rng.uniform(0.0, 100.0),
        speed_multiplier=rng.uniform(0.85, 1.15),
        available_at_minute=rng.randint(0, 30),
        certified_for_suites=rng.random() < 0.5,
    )


def _generate_deadline(
    priority: int,
    rng: random.Random,
) -> int:
    if priority == 2:
        return rng.randint(90, 150)

    if priority == 1:
        return rng.randint(150, 210)

    return rng.randint(210, 360)


def _ensure_suite_coverage(
    rooms: list[Room],
    housekeepers: list[Housekeeper],
) -> None:
    has_suite = any(
        room.room_type == RoomType.SUITE
        for room in rooms
    )

    has_certified_housekeeper = any(
        housekeeper.certified_for_suites
        for housekeeper in housekeepers
    )

    if not has_suite or has_certified_housekeeper:
        return

    first_housekeeper = housekeepers[0]

    housekeepers[0] = Housekeeper(
        housekeeper_id=first_housekeeper.housekeeper_id,
        start_floor=first_housekeeper.start_floor,
        start_position=first_housekeeper.start_position,
        speed_multiplier=first_housekeeper.speed_multiplier,
        available_at_minute=first_housekeeper.available_at_minute,
        certified_for_suites=True,
    )