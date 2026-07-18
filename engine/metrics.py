from collections import defaultdict
from dataclasses import dataclass
from statistics import mean, pstdev

from engine.models import Assignment


@dataclass(frozen=True)
class EvaluationMetrics:
    makespan: float
    workload_std: float
    total_travel: float
    vip_mean_ready: float
    deadline_misses: int
    total_cost: float


def calculate_completion_times(
    assignments: list[Assignment],
) -> dict[str, float]:
    """
    Calculate each room's completion time.

    Assignments are processed by housekeeper and slot order.
    Completion time includes:
    - housekeeper availability
    - travel time
    - cleaning time
    """
    assignments_by_housekeeper: dict[str, list[Assignment]] = defaultdict(list)

    for assignment in assignments:
        assignments_by_housekeeper[
            assignment.housekeeper.housekeeper_id
        ].append(assignment)

    room_completion_times: dict[str, float] = {}

    for housekeeper_assignments in assignments_by_housekeeper.values():
        ordered_assignments = sorted(
            housekeeper_assignments,
            key=lambda assignment: assignment.slot_index,
        )

        current_time = ordered_assignments[
            0
        ].housekeeper.available_at_minute

        for assignment in ordered_assignments:
            current_time += (
                assignment.travel_time
                + assignment.cleaning_time
            )

            room_completion_times[
                assignment.room.room_id
            ] = current_time

    return room_completion_times


def calculate_workloads(
    assignments: list[Assignment],
) -> dict[str, float]:
    """
    Calculate total working time for each housekeeper.
    """
    workloads: dict[str, float] = defaultdict(float)

    for assignment in assignments:
        housekeeper_id = assignment.housekeeper.housekeeper_id

        workloads[housekeeper_id] += (
            assignment.travel_time
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

    makespan = max(completion_times.values())

    workload_values = list(workloads.values())
    workload_std = (
        pstdev(workload_values)
        if len(workload_values) > 1
        else 0.0
    )

    total_travel = sum(
        assignment.travel_time
        for assignment in assignments
    )

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