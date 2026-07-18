from collections import defaultdict
from dataclasses import dataclass
from statistics import mean, pstdev

from engine.models import Assignment
from engine.travel import calculate_travel_time


@dataclass(frozen=True)
class EvaluationMetrics:
    makespan: float
    workload_std: float
    total_travel: float
    vip_mean_ready: float
    deadline_misses: int
    total_cost: float


def group_assignments_by_housekeeper(
    assignments: list[Assignment],
) -> dict[str, list[Assignment]]:
    assignments_by_housekeeper: dict[
        str,
        list[Assignment],
    ] = defaultdict(list)

    for assignment in assignments:
        housekeeper_id = assignment.housekeeper.housekeeper_id
        assignments_by_housekeeper[housekeeper_id].append(assignment)

    return dict(assignments_by_housekeeper)


def calculate_route_travel_times(
    assignments: list[Assignment],
) -> dict[str, float]:
    """
    Calculate actual travel time for each assigned room.

    The first room is reached from the housekeeper's starting location.
    Every later room is reached from the previously assigned room.
    """
    assignments_by_housekeeper = group_assignments_by_housekeeper(
        assignments
    )

    travel_times: dict[str, float] = {}

    for housekeeper_assignments in assignments_by_housekeeper.values():
        ordered_assignments = sorted(
            housekeeper_assignments,
            key=lambda assignment: assignment.slot_index,
        )

        housekeeper = ordered_assignments[0].housekeeper

        previous_floor = housekeeper.start_floor
        previous_position = housekeeper.start_position

        for assignment in ordered_assignments:
            room = assignment.room

            travel_time = calculate_travel_time(
                start_floor=previous_floor,
                start_position=previous_position,
                end_floor=room.floor,
                end_position=room.position,
            )

            travel_times[room.room_id] = travel_time

            previous_floor = room.floor
            previous_position = room.position

    return travel_times


def calculate_completion_times(
    assignments: list[Assignment],
) -> dict[str, float]:
    """
    Calculate each room's completion time.

    Assignments are processed by housekeeper and slot order.
    Completion time includes:
    - housekeeper availability
    - actual route travel time
    - cleaning time
    """
    assignments_by_housekeeper = group_assignments_by_housekeeper(
        assignments
    )

    route_travel_times = calculate_route_travel_times(assignments)

    room_completion_times: dict[str, float] = {}

    for housekeeper_assignments in assignments_by_housekeeper.values():
        ordered_assignments = sorted(
            housekeeper_assignments,
            key=lambda assignment: assignment.slot_index,
        )

        current_time = (
            ordered_assignments[0]
            .housekeeper
            .available_at_minute
        )

        for assignment in ordered_assignments:
            room_id = assignment.room.room_id

            current_time += (
                route_travel_times[room_id]
                + assignment.cleaning_time
            )

            room_completion_times[room_id] = current_time

    return room_completion_times


def calculate_workloads(
    assignments: list[Assignment],
) -> dict[str, float]:
    """
    Calculate total working time for each housekeeper.

    Workload includes actual route travel time and cleaning time.
    """
    route_travel_times = calculate_route_travel_times(assignments)

    workloads: dict[str, float] = defaultdict(float)

    for assignment in assignments:
        housekeeper_id = assignment.housekeeper.housekeeper_id
        room_id = assignment.room.room_id

        workloads[housekeeper_id] += (
            route_travel_times[room_id]
            + assignment.cleaning_time
        )

    return dict(workloads)


def evaluate_assignments(
    assignments: list[Assignment],
) -> EvaluationMetrics:
    if not assignments:
        return EvaluationMetrics(
            makespan=0.0,
            workload_std=0.0,
            total_travel=0.0,
            vip_mean_ready=0.0,
            deadline_misses=0,
            total_cost=0.0,
        )

    completion_times = calculate_completion_times(assignments)
    workloads = calculate_workloads(assignments)
    route_travel_times = calculate_route_travel_times(assignments)

    makespan = max(completion_times.values())

    workload_values = list(workloads.values())

    workload_std = (
        pstdev(workload_values)
        if len(workload_values) > 1
        else 0.0
    )

    total_travel = sum(route_travel_times.values())

    vip_ready_times = [
        completion_times[assignment.room.room_id]
        for assignment in assignments
        if assignment.room.priority == 2
    ]

    vip_mean_ready = (
        mean(vip_ready_times)
        if vip_ready_times
        else 0.0
    )

    deadline_misses = sum(
        completion_times[assignment.room.room_id]
        > assignment.room.check_in_deadline_minute
        for assignment in assignments
    )

    total_cost = sum(
        assignment.cost
        for assignment in assignments
    )

    return EvaluationMetrics(
        makespan=makespan,
        workload_std=workload_std,
        total_travel=total_travel,
        vip_mean_ready=vip_mean_ready,
        deadline_misses=deadline_misses,
        total_cost=total_cost,
    )