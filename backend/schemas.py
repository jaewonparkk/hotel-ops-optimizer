from pydantic import BaseModel, Field

from engine.models import RoomType


class RoomInput(BaseModel):
    room_id: str
    floor: int = Field(ge=1)
    position: float = Field(ge=0)
    room_type: RoomType
    occupancy_nights: int = Field(ge=1)
    guests: int = Field(ge=1)
    priority: int = Field(ge=0, le=2)
    check_in_deadline_minute: int = Field(ge=0)


class HousekeeperInput(BaseModel):
    housekeeper_id: str
    start_floor: int = Field(ge=1)
    start_position: float = Field(ge=0)
    speed_multiplier: float = Field(gt=0)
    available_at_minute: int = Field(ge=0)
    certified_for_suites: bool


class OptimizeRequest(BaseModel):
    rooms: list[RoomInput]
    housekeepers: list[HousekeeperInput]


class AssignmentOutput(BaseModel):
    housekeeper_id: str
    room_id: str
    slot_index: int
    estimated_travel_time: float
    cleaning_time: float
    cost: float


class MetricsOutput(BaseModel):
    makespan: float
    workload_std: float
    total_travel: float
    vip_mean_ready: float
    deadline_misses: int
    total_cost: float


class OptimizeResponse(BaseModel):
    assignments: list[AssignmentOutput]
    metrics: MetricsOutput

class AlgorithmResult(BaseModel):
    assignments: list[AssignmentOutput]
    metrics: MetricsOutput


class ImprovementOutput(BaseModel):
    makespan_percent: float
    workload_std_percent: float
    total_travel_percent: float
    vip_mean_ready_percent: float
    deadline_misses_percent: float
    total_cost_percent: float


class CompareResponse(BaseModel):
    greedy: AlgorithmResult
    hungarian: AlgorithmResult
    improvement: ImprovementOutput