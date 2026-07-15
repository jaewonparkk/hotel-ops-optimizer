from dataclasses import dataclass


@dataclass
class Room:
    room_id: str
    floor: int
    position: float

@dataclass
class Housekeeper:
    housekeeper_id: str
    start_floor: int
    start_position: float