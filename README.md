# HouseFlow

HouseFlow is a full-stack hotel housekeeping assignment platform powered by an optimization engine.

The project has two stages:

1. Benchmark multiple room-assignment algorithms using metrics such as workload balance, travel time, room readiness, deadline misses, and runtime.
2. Integrate the best-performing approach into a web application where hotel supervisors can enter room and staff information and automatically generate optimized assignments.

## Project Structure

- `experiments/` — algorithm implementations and benchmarks
- `backend/` — FastAPI application and production optimization engine
- `frontend/` — web interface for entering data and viewing assignments
- `docs/` — technical design and experiment documentation

## Planned Algorithms

- Greedy assignment
- Hungarian algorithm with slot expansion
- Additional optimization methods if needed

## Planned Evaluation Metrics

- Makespan
- Workload standard deviation
- Total travel time
- VIP room mean ready time
- Deadline misses
- Algorithm runtime

## Current Status

- [x] Define the project scope
- [x] Create the initial repository structure
- [ ] Define the first simulation scenario
- [ ] Implement the cleaning-time function
- [ ] Implement the greedy baseline
- [ ] Implement the Hungarian-based approach
- [ ] Run benchmarks
- [ ] Build the backend API
- [ ] Build the frontend