from scipy.optimize import linear_sum_assignment

from engine.cost import INFEASIBLE_COST
from engine.matrix import build_cost_matrix
from engine.models import Assignment, Housekeeper, Room


def assign_rooms_hungarian(
    rooms: list[Room],
    housekeepers: list[Housekeeper],
) -> list[Assignment]:
    if not rooms:
        return []

    cost_matrix, slots = build_cost_matrix(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    room_indices, column_indices = linear_sum_assignment(
        cost_matrix
    )

    assignments: list[Assignment] = []

    for room_index, column_index in zip(
        room_indices,
        column_indices,
        strict=True,
    ):
        selected_cost = float(
            cost_matrix[room_index, column_index]
        )

        if selected_cost >= INFEASIBLE_COST:
            raise ValueError(
                "No feasible assignment exists for all rooms"
            )

        room = rooms[room_index]
        slot = slots[column_index]

        assignments.append(
            Assignment(
                housekeeper=slot.housekeeper,
                room=room,
                slot_index=slot.slot_index,
                travel_time=slot.housekeeper.travel_time(room),
                cleaning_time=slot.housekeeper.clean_time(room),
                cost=selected_cost,
            )
        )

    assignments.sort(
        key=lambda assignment: (
            assignment.housekeeper.housekeeper_id,
            assignment.slot_index,
        )
    )

    return assignments