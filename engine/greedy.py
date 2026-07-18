from engine.cost import INFEASIBLE_COST, assignment_cost
from engine.matrix import build_slots, calculate_slots_per_housekeeper
from engine.models import Assignment, Housekeeper, Room, RoomType


def assign_rooms_greedy(
    rooms: list[Room],
    housekeepers: list[Housekeeper],
) -> list[Assignment]:
    if not rooms:
        return []

    if not housekeepers:
        raise ValueError("at least one housekeeper is required")

    slots_per_housekeeper = calculate_slots_per_housekeeper(
        number_of_rooms=len(rooms),
        number_of_housekeepers=len(housekeepers),
    )

    available_slots = build_slots(
        housekeepers=housekeepers,
        slots_per_housekeeper=slots_per_housekeeper,
    )

    # Process the most constrained rooms first.
    # Suites require certified housekeepers, so assigning them first
    # prevents certified slots from being consumed by standard rooms.
    ordered_rooms = sorted(
        rooms,
        key=lambda room: (
            room.room_type != RoomType.SUITE,
            -room.priority,
            room.check_in_deadline_minute,
        ),
    )

    assignments: list[Assignment] = []

    for room in ordered_rooms:
        best_slot_index: int | None = None
        best_cost: float | None = None

        for slot_index, slot in enumerate(available_slots):
            cost = assignment_cost(
                room=room,
                housekeeper=slot.housekeeper,
                slot_index=slot.slot_index,
            )

            if cost >= INFEASIBLE_COST:
                continue

            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_slot_index = slot_index

        if best_slot_index is None or best_cost is None:
            raise ValueError(
                "No feasible assignment exists for all rooms"
            )

        selected_slot = available_slots.pop(best_slot_index)

        assignments.append(
            Assignment(
                housekeeper=selected_slot.housekeeper,
                room=room,
                slot_index=selected_slot.slot_index,
                travel_time=selected_slot.housekeeper.travel_time(room),
                cleaning_time=selected_slot.housekeeper.clean_time(room),
                cost=best_cost,
            )
        )

    assignments.sort(
        key=lambda assignment: (
            assignment.housekeeper.housekeeper_id,
            assignment.slot_index,
        )
    )

    return assignments