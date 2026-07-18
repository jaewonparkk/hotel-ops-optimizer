from backend.schemas import (
    AlgorithmResult,
    AssignmentOutput,
    CompareResponse,
    ImprovementOutput,
    MetricsOutput,
    OptimizeRequest,
)
from engine.greedy import assign_rooms_greedy
from engine.hungarian import assign_rooms_hungarian
from engine.metrics import EvaluationMetrics, evaluate_assignments
from engine.models import Assignment, Housekeeper, Room


def _serialize_result(
    assignments: list[Assignment],
    metrics: EvaluationMetrics,
) -> AlgorithmResult:
    return AlgorithmResult(
        assignments=[
            AssignmentOutput(
                housekeeper_id=assignment.housekeeper.housekeeper_id,
                room_id=assignment.room.room_id,
                slot_index=assignment.slot_index,
                estimated_travel_time=assignment.travel_time,
                cleaning_time=assignment.cleaning_time,
                cost=assignment.cost,
            )
            for assignment in assignments
        ],
        metrics=MetricsOutput(
            makespan=metrics.makespan,
            workload_std=metrics.workload_std,
            total_travel=metrics.total_travel,
            vip_mean_ready=metrics.vip_mean_ready,
            deadline_misses=metrics.deadline_misses,
            total_cost=metrics.total_cost,
        ),
    )


def _percentage_improvement(
    baseline: float,
    optimized: float,
) -> float:
    if baseline == 0:
        return 0.0

    return (baseline - optimized) / baseline * 100


def compare_housekeeping_algorithms(
    request: OptimizeRequest,
) -> CompareResponse:
    rooms = [
        Room(**room.model_dump())
        for room in request.rooms
    ]

    housekeepers = [
        Housekeeper(**housekeeper.model_dump())
        for housekeeper in request.housekeepers
    ]

    greedy_assignments = assign_rooms_greedy(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    hungarian_assignments = assign_rooms_hungarian(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    greedy_metrics = evaluate_assignments(greedy_assignments)
    hungarian_metrics = evaluate_assignments(
        hungarian_assignments
    )

    return CompareResponse(
        greedy=_serialize_result(
            assignments=greedy_assignments,
            metrics=greedy_metrics,
        ),
        hungarian=_serialize_result(
            assignments=hungarian_assignments,
            metrics=hungarian_metrics,
        ),
        improvement=ImprovementOutput(
            makespan_percent=_percentage_improvement(
                greedy_metrics.makespan,
                hungarian_metrics.makespan,
            ),
            workload_std_percent=_percentage_improvement(
                greedy_metrics.workload_std,
                hungarian_metrics.workload_std,
            ),
            total_travel_percent=_percentage_improvement(
                greedy_metrics.total_travel,
                hungarian_metrics.total_travel,
            ),
            vip_mean_ready_percent=_percentage_improvement(
                greedy_metrics.vip_mean_ready,
                hungarian_metrics.vip_mean_ready,
            ),
            deadline_misses_percent=_percentage_improvement(
                float(greedy_metrics.deadline_misses),
                float(hungarian_metrics.deadline_misses),
            ),
            total_cost_percent=_percentage_improvement(
                greedy_metrics.total_cost,
                hungarian_metrics.total_cost,
            ),
        ),
    )