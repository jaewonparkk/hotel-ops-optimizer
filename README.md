# 🏨 Hotel Ops Optimizer

An end-to-end optimization platform that generates efficient housekeeping
schedules using the Hungarian Algorithm, and compares them against a greedy
baseline.

![Demo](docs/demo.gif)

---

## Overview

Hotel housekeeping managers often assign rooms manually or with simple greedy
heuristics. As rooms and staff grow, that leads to long completion times,
excessive staff travel, uneven workloads, and missed high-priority rooms.

Hotel Ops Optimizer models housekeeping as a constrained assignment problem
and solves it two ways, a greedy dispatcher and the Hungarian algorithm, then
reports exactly where and why the optimizer wins.

---

## Features

- Interactive React frontend
- FastAPI backend
- Hungarian assignment optimization
- Greedy baseline for comparison
- Automatic performance metrics
- Scenario benchmarking
- REST API
- Tested with pytest

---

## How it works

### Cost of a single assignment

For a given (room, housekeeper, slot):

```
cost = TRAVEL_WEIGHT   * travel_time(housekeeper_start -> room)
     + CLEAN_WEIGHT    * clean_time(room, housekeeper)
     + SLOT_WEIGHT     * slot_index
     + PRIORITY_WEIGHT * room.priority * slot_index
```

Travel and cleaning are real minutes, so both carry weight 1.0. A suite
assigned to an uncertified housekeeper gets a prohibitive `INFEASIBLE_COST`
instead, turning a hard skill constraint into a number the solver avoids.

### Turning 1:N into 1:1 (slot replication)

Hungarian matches one row to one column, but each housekeeper must take several
rooms. Each housekeeper is expanded into K virtual columns, one per slot (their
1st room, 2nd room, and so on), with `ceil(rooms / housekeepers) + 2` slots
each. Every column carries a `HousekeeperSlot` that remembers which housekeeper
and slot it is, so decoding the solution needs no index arithmetic.

### Why slot_index drives load balancing

Charging `SLOT_WEIGHT * slot_index` means a housekeeper taking *m* rooms pays
`SLOT_WEIGHT * (0 + 1 + ... + (m-1))`, which is quadratic in *m*. The quadratic
penalty makes piling rooms on one person expensive, so balanced workloads fall
out of the objective without an explicit fairness rule. The `priority *
slot_index` term uses the same idea to push VIP rooms into early slots.

### Assignment vs routing (an intentional approximation)

Travel depends on visit order, but order isn't known until after assignment,
a circular dependency. So assignment (who cleans what, solved by Hungarian) is
separated from routing (visit order, an NP-hard TSP-flavored problem). During
assignment, travel is approximated from the housekeeper's shift-start location;
both algorithms use the same approximation, so the comparison stays fair. The
evaluation step then recomputes real room-to-room travel, so reported makespan
and travel reflect what actually happens on the floor. Approximate while
assigning, measure honestly while evaluating.

---

## Algorithms

### Greedy (baseline)
Repeatedly picks the cheapest remaining room-slot pair. Fast and simple, but
each choice is locally optimal and never reconsidered, so early picks can
strand later rooms. Naturally strong at load balancing, which makes it a fair,
non-strawman opponent.

### Hungarian
Builds the full assignment cost matrix and computes the globally optimal
assignment (minimizing total cost). Balances makespan, travel, workload, and
priority through the cost design above.

---

## Metrics

Each schedule reports makespan, total travel, workload standard deviation, VIP
mean completion time, deadline misses, and total optimization cost.

---

## Demo

Small interactive scenario (8 rooms, 3 housekeepers). Numbers below are for
this single demo shift, not the aggregate benchmark.

### 1. Input interface
<img src="docs/1.png" width="900">

### 2. Greedy vs Hungarian comparison
<img src="docs/2.png" width="900">

### 3. Generated housekeeping schedule
<img src="docs/3.png" width="900">

### 4. Benchmark results
<img src="docs/4.png" width="900">

On this 8-room demo, Hungarian cut makespan 27.8% (212.3 → 153.3 min), travel
22.8% (114.0 → 88.0 min), and workload deviation 68.0% (44.5 → 14.2), with VIP
ready time and deadline misses unchanged.

---

## Benchmark (aggregate)

Separately from the demo above, a benchmark runs many randomized shifts to test
whether the advantage holds on average rather than on one lucky layout. Across
**100 randomized 40-room, 6-housekeeper shifts** (each shift solved by both
algorithms on identical data, seeded for reproducibility):

| Metric | Greedy | Hungarian | Improvement | Hungarian wins |
|---|---|---|---|---|
| makespan | 497.32 | 477.37 | 4.01% | 72 / 100 |
| workload_std | 73.63 | 65.67 | 10.81% | 65 / 100 |
| total_travel | 596.88 | 512.92 | 14.07% | 88 / 100 |
| vip_mean_ready | 77.59 | 68.43 | 11.80% | 61 / 100 |
| deadline_misses | 16.72 | 13.56 | 18.90% | 74 / 100 |
| total_cost | 2811.50 | 2731.55 | 2.84% | 100 / 100 |

Two honest caveats worth reading. Total cost wins 100% of shifts because it is
exactly what Hungarian minimizes; makespan improves only 4% because it is a
side effect, not a direct target. And makespan and workload win only ~65-72% of
shifts, not all, because greedy's least-loaded rule is genuinely good at
balancing. The improvement is real and consistent, but it is a trade-off, not a
clean sweep.

```bash
python -m experiments.benchmark2
```

---

## Tech stack

Frontend: React, TypeScript, Vite
Backend: FastAPI, Pydantic
Optimization: NumPy, SciPy (Hungarian algorithm)
Testing: pytest

---

## Project structure

```text
backend/
engine/
  models.py              Room, Housekeeper, Assignment
  cost.py                single-assignment cost + weights + INFEASIBLE_COST
  travel.py              shared travel-time function
  matrix.py              slot replication + cost-matrix construction
  hungarian.py           Hungarian solver (scipy) + result decoding
  greedy.py              greedy baseline
  metrics.py             simulation + makespan/travel/workload/VIP/deadline
  scenario_generator.py  seeded random shifts, feasibility-guaranteed
frontend/
experiments/
tests/
```

---

## Running locally

### Backend
```bash
python -m uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Documentation

Detailed project documentation is available in Google Drive:
[Google Drive Folder](https://drive.google.com/drive/u/0/folders/1mfeK7ix8SiyJAVVtCKV1Qs0J_rruAPv5)

- Research and current solutions
- Project overview
- Algorithm and cost-function design
- Technical architecture

---

## Known limitations / future work

- **Deadlines aren't in the objective yet.** `check_in_deadline_minute` is
  measured but not part of the cost, so the optimizer doesn't actively chase
  it. Folding in a deadline term is the most promising next improvement.
- **Routing is order-by-slot, not optimal.** A per-housekeeper TSP would cut
  travel further.
- **Benchmarks report means and win rates but not variance.**
- **Input validation** in the domain models is still a TODO.
- Multi-day scheduling, shift constraints, dynamic room arrivals, interactive
  floor map, real PMS integration.

---

## Author

Jaewon Park
