import math
from dataclasses import dataclass

import numpy as np

from engine.cost import assignment_cost
from engine.models import Housekeeper, Room


@dataclass(frozen=True)
class HousekeeperSlot:
    housekeeper: Housekeeper
    slot_index: int


def calculate_slots_per_housekeeper(
    number_of_rooms: int,
    number_of_housekeepers: int,
) -> int:
    if number_of_rooms < 0:
        raise ValueError("number_of_rooms cannot be negative")

    if number_of_housekeepers <= 0:
        raise ValueError(
            "number_of_housekeepers must be greater than 0"
        )

    average_rooms = math.ceil(
        number_of_rooms / number_of_housekeepers
    )

    # Add two safety slots so constraints such as suite certification
    # do not make an otherwise valid assignment impossible.
    # Later slots receive higher slot penalties, so the extra slots
    # should only be used when necessary.
    return average_rooms + 2


def build_slots(
    housekeepers: list[Housekeeper],
    slots_per_housekeeper: int,
) -> list[HousekeeperSlot]:
    if slots_per_housekeeper <= 0:
        raise ValueError(
            "slots_per_housekeeper must be greater than 0"
        )

    return [
        HousekeeperSlot(
            housekeeper=housekeeper,
            slot_index=slot_index,
        )
        for housekeeper in housekeepers
        for slot_index in range(slots_per_housekeeper)
    ]


def build_cost_matrix(
    rooms: list[Room],
    housekeepers: list[Housekeeper],
) -> tuple[np.ndarray, list[HousekeeperSlot]]:
    if not housekeepers:
        raise ValueError(
            "at least one housekeeper is required"
        )

    slots_per_housekeeper = calculate_slots_per_housekeeper(
        number_of_rooms=len(rooms),
        number_of_housekeepers=len(housekeepers),
    )

    slots = build_slots(
        housekeepers=housekeepers,
        slots_per_housekeeper=slots_per_housekeeper,
    )

    cost_matrix = np.array(
        [
            [
                assignment_cost(
                    room=room,
                    housekeeper=slot.housekeeper,
                    slot_index=slot.slot_index,
                )
                for slot in slots
            ]
            for room in rooms
        ],
        dtype=float,
    )

    return cost_matrix, slots