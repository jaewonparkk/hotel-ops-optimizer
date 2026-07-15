from dataclasses import dataclass
from enum import Enum

class RoomType(str, Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"

@dataclass
class Room:
    room_id: str
    floor: int
    position: float
    room_type: RoomType
    occupancy_nights: int
    guests: int
    priority: int
    check_in_deadline_minute: int

    def base_clean_time(self) -> float:
        base_times = {
            RoomType.STANDARD: 25.0,
            RoomType.DELUXE: 35.0,
            RoomType.SUITE: 50.0,
        }
        base_time = base_times[self.room_type]

        extra_nights = max(0, self.occupancy_nights - 1)
        extra_guests = max(0, self.guests - 1)

        night_adjustment = extra_nights * 2.0
        guest_adjustment = extra_guests * 3.0

        return base_time + night_adjustment + guest_adjustment

@dataclass
class Housekeeper:
    housekeeper_id: str
    start_floor: int
    start_position: float
    speed_multiplier: float
    available_at_minute: int
    certified_for_suites: bool

    def clean_time(self, room: Room) -> float:
        return room.base_clean_time() * self.speed_multiplier