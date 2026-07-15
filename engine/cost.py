from engine.models import Housekeeper, Room


FLOOR_CHANGE_COST = 20.0


def calculate_travel_distance(
    housekeeper: Housekeeper,
    room: Room,
) -> float:
    floor_distance = (
        abs(housekeeper.start_floor - room.floor)
        * FLOOR_CHANGE_COST
    )

    hallway_distance = abs(
        housekeeper.start_position - room.position
    )

    

    return floor_distance + hallway_distance


