from collections import defaultdict

from scipy.optimize import linear_sum_assignment

from engine.cost import INFEASIBLE_COST
from engine.matrix import build_cost_matrix
from engine.models import Housekeeper, Room


def assign_rooms_hungarian(
    rooms: list[Room],
    housekeepers: list[Housekeeper],
) -> dict[str, list[Room]]:
    if not rooms:
        return {
            housekeeper.housekeeper_id: []
            for housekeeper in housekeepers
        }

    cost_matrix, slots = build_cost_matrix(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    room_indices, slot_indices = linear_sum_assignment(
        cost_matrix
    )

    assignments_with_slots: dict[
        str,
        list[tuple[int, Room]],
    ] = defaultdict(list)

    for room_index, slot_index in zip(
        room_indices,
        slot_indices,
        strict=True,
    ):
        selected_cost = cost_matrix[
            room_index,
            slot_index,
        ]

        if selected_cost >= INFEASIBLE_COST:
            raise ValueError(
                "No feasible assignment exists for all rooms"
            )

        room = rooms[room_index]
        slot = slots[slot_index]

        assignments_with_slots[
            slot.housekeeper.housekeeper_id
        ].append(
            (slot.slot_index, room)
        )

    assignments: dict[str, list[Room]] = {}

    for housekeeper in housekeepers:
        housekeeper_id = housekeeper.housekeeper_id

        ordered_assignments = sorted(
            assignments_with_slots[housekeeper_id],
            key=lambda item: item[0],
        )

        assignments[housekeeper_id] = [
            room
            for _, room in ordered_assignments
        ]

    return assignments