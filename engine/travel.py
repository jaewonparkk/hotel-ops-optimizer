FLOOR_CHANGE_MINUTES = 3.0
POSITION_CHANGE_MINUTES = 0.5


def calculate_travel_time(
    start_floor: int,
    start_position: float,
    end_floor: int,
    end_position: float,
) -> float:
    floor_time = (
        abs(start_floor - end_floor)
        * FLOOR_CHANGE_MINUTES
    )

    hallway_time = (
        abs(start_position - end_position)
        * POSITION_CHANGE_MINUTES
    )

    return floor_time + hallway_time
