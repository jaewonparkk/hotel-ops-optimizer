from engine.cost import INFEASIBLE_COST, assignment_cost
from engine.matrix import build_slots, calculate_slots_per_housekeeper
from engine.models import Assignment, Housekeeper, Room


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

    unassigned_rooms = list(rooms)
    assignments: list[Assignment] = []

    while unassigned_rooms:
        best_choice: tuple[
            float,
            int,
            int,
        ] | None = None

        for room_index, room in enumerate(unassigned_rooms):
            for slot_index, slot in enumerate(available_slots):
                cost = assignment_cost(
                    room=room,
                    housekeeper=slot.housekeeper,
                    slot_index=slot.slot_index,
                )

                if cost >= INFEASIBLE_COST:
                    continue

                if best_choice is None or cost < best_choice[0]:
                    best_choice = (
                        cost,
                        room_index,
                        slot_index,
                    )

        if best_choice is None:
            raise ValueError(
                "No feasible assignment exists for all rooms"
            )

        cost, room_index, slot_index = best_choice

        room = unassigned_rooms.pop(room_index)
        slot = available_slots.pop(slot_index)

        assignments.append(
            Assignment(
                housekeeper=slot.housekeeper,
                room=room,
                slot_index=slot.slot_index,
                travel_time=slot.housekeeper.travel_time(room),
                cleaning_time=slot.housekeeper.clean_time(room),
                cost=cost,
            )
        )

    assignments.sort(
        key=lambda assignment: (
            assignment.housekeeper.housekeeper_id,
            assignment.slot_index,
        )
    )

    return assignments