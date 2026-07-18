from dataclasses import asdict
from statistics import mean

from engine.greedy import assign_rooms_greedy
from engine.hungarian import assign_rooms_hungarian
from engine.metrics import EvaluationMetrics, evaluate_assignments
from engine.scenario_generator import generate_random_scenario


NUMBER_OF_TRIALS = 100
NUMBER_OF_ROOMS = 40
NUMBER_OF_HOUSEKEEPERS = 6


def run_trial(seed: int) -> tuple[EvaluationMetrics, EvaluationMetrics]:
    rooms, housekeepers = generate_random_scenario(
        number_of_rooms=NUMBER_OF_ROOMS,
        number_of_housekeepers=NUMBER_OF_HOUSEKEEPERS,
        seed=seed,
    )

    greedy_assignments = assign_rooms_greedy(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    hungarian_assignments = assign_rooms_hungarian(
        rooms=rooms,
        housekeepers=housekeepers,
    )

    greedy_metrics = evaluate_assignments(greedy_assignments)
    hungarian_metrics = evaluate_assignments(hungarian_assignments)

    return greedy_metrics, hungarian_metrics


def average_metrics(
    metrics_list: list[EvaluationMetrics],
) -> dict[str, float]:
    metric_dicts = [
        asdict(metrics)
        for metrics in metrics_list
    ]

    return {
        metric_name: mean(
            metrics[metric_name]
            for metrics in metric_dicts
        )
        for metric_name in metric_dicts[0]
    }


def percentage_improvement(
    baseline: float,
    optimized: float,
) -> float:
    if baseline == 0:
        return 0.0

    return (
        (baseline - optimized)
        / baseline
        * 100
    )


def count_wins(
    greedy_results: list[EvaluationMetrics],
    hungarian_results: list[EvaluationMetrics],
    metric_name: str,
) -> int:
    return sum(
        getattr(hungarian, metric_name)
        < getattr(greedy, metric_name)
        for greedy, hungarian in zip(
            greedy_results,
            hungarian_results,
            strict=True,
        )
    )


def print_comparison(
    greedy_average: dict[str, float],
    hungarian_average: dict[str, float],
    greedy_results: list[EvaluationMetrics],
    hungarian_results: list[EvaluationMetrics],
) -> None:
    lower_is_better_metrics = [
        "makespan",
        "workload_std",
        "total_travel",
        "vip_mean_ready",
        "deadline_misses",
        "total_cost",
    ]

    print("\nHouseFlow Algorithm Benchmark")
    print("=" * 78)
    print(
        f"Trials: {NUMBER_OF_TRIALS} | "
        f"Rooms: {NUMBER_OF_ROOMS} | "
        f"Housekeepers: {NUMBER_OF_HOUSEKEEPERS}"
    )
    print("=" * 78)

    print(
        f"{'Metric':<22}"
        f"{'Greedy':>14}"
        f"{'Hungarian':>14}"
        f"{'Improvement':>16}"
        f"{'H Wins':>10}"
    )
    print("-" * 78)

    for metric_name in lower_is_better_metrics:
        greedy_value = greedy_average[metric_name]
        hungarian_value = hungarian_average[metric_name]

        improvement = percentage_improvement(
            baseline=greedy_value,
            optimized=hungarian_value,
        )

        wins = count_wins(
            greedy_results=greedy_results,
            hungarian_results=hungarian_results,
            metric_name=metric_name,
        )

        print(
            f"{metric_name:<22}"
            f"{greedy_value:>14.2f}"
            f"{hungarian_value:>14.2f}"
            f"{improvement:>15.2f}%"
            f"{wins:>10}"
        )


def main() -> None:
    greedy_results: list[EvaluationMetrics] = []
    hungarian_results: list[EvaluationMetrics] = []

    for seed in range(NUMBER_OF_TRIALS):
        greedy_metrics, hungarian_metrics = run_trial(seed)

        greedy_results.append(greedy_metrics)
        hungarian_results.append(hungarian_metrics)

    greedy_average = average_metrics(greedy_results)
    hungarian_average = average_metrics(hungarian_results)

    print_comparison(
        greedy_average=greedy_average,
        hungarian_average=hungarian_average,
        greedy_results=greedy_results,
        hungarian_results=hungarian_results,
    )


if __name__ == "__main__":
    main()