from engine.models import Housekeeper, Room, RoomType


TRAVEL_WEIGHT = 1.0
CLEAN_WEIGHT = 1.0
SLOT_WEIGHT = 5.0
PRIORITY_WEIGHT = 10.0
INFEASIBLE_COST = 1_000_000.0


def slot_penalty(slot_index: int) -> float:
    return SLOT_WEIGHT * slot_index


def priority_penalty(room: Room, slot_index: int) -> float:
    return PRIORITY_WEIGHT * room.priority * slot_index


def assignment_cost(
    room: Room,
    housekeeper: Housekeeper,
    slot_index: int,
) -> float:
    if (
        room.room_type == RoomType.SUITE
        and not housekeeper.certified_for_suites
    ):
        return INFEASIBLE_COST

    travel_cost = (
        TRAVEL_WEIGHT
        * housekeeper.travel_time(room)
    )

    clean_cost = (
        CLEAN_WEIGHT
        * housekeeper.clean_time(room)
    )

    return (
        travel_cost
        + clean_cost
        + slot_penalty(slot_index)
        + priority_penalty(room, slot_index)
    )