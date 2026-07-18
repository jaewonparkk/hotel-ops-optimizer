import { useMemo, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

type RoomType = "standard" | "deluxe" | "suite";

type Room = {
  room_id: string;
  floor: number;
  position: number;
  room_type: RoomType;
  occupancy_nights: number;
  guests: number;
  priority: number;
  check_in_deadline_minute: number;
};

type Housekeeper = {
  housekeeper_id: string;
  start_floor: number;
  start_position: number;
  speed_multiplier: number;
  available_at_minute: number;
  certified_for_suites: boolean;
};

type Assignment = {
  housekeeper_id: string;
  room_id: string;
  slot_index: number;
  estimated_travel_time: number;
  cleaning_time: number;
  cost: number;
};

type Metrics = {
  makespan: number;
  workload_std: number;
  total_travel: number;
  vip_mean_ready: number;
  deadline_misses: number;
  total_cost: number;
};

type AlgorithmResult = {
  assignments: Assignment[];
  metrics: Metrics;
};

type Improvement = {
  makespan_percent: number;
  workload_std_percent: number;
  total_travel_percent: number;
  vip_mean_ready_percent: number;
  deadline_misses_percent: number;
  total_cost_percent: number;
};

type CompareResponse = {
  greedy: AlgorithmResult;
  hungarian: AlgorithmResult;
  improvement: Improvement;
};

type GroupedAssignments = Record<string, Assignment[]>;

const initialRooms: Room[] = [
  {
    room_id: "101",
    floor: 1,
    position: 10,
    room_type: "standard",
    occupancy_nights: 2,
    guests: 2,
    priority: 0,
    check_in_deadline_minute: 240,
  },
  {
    room_id: "202",
    floor: 2,
    position: 30,
    room_type: "suite",
    occupancy_nights: 3,
    guests: 2,
    priority: 2,
    check_in_deadline_minute: 120,
  },
];

const initialHousekeepers: Housekeeper[] = [
  {
    housekeeper_id: "H1",
    start_floor: 1,
    start_position: 0,
    speed_multiplier: 1,
    available_at_minute: 0,
    certified_for_suites: false,
  },
  {
    housekeeper_id: "H2",
    start_floor: 2,
    start_position: 0,
    speed_multiplier: 0.9,
    available_at_minute: 0,
    certified_for_suites: true,
  },
  
];

const largeDemoRooms: Room[] = [
  {
    room_id: "101",
    floor: 1,
    position: 5,
    room_type: "standard",
    occupancy_nights: 1,
    guests: 1,
    priority: 0,
    check_in_deadline_minute: 300,
  },
  {
    room_id: "102",
    floor: 1,
    position: 45,
    room_type: "deluxe",
    occupancy_nights: 4,
    guests: 3,
    priority: 2,
    check_in_deadline_minute: 110,
  },
  {
    room_id: "201",
    floor: 2,
    position: 10,
    room_type: "standard",
    occupancy_nights: 2,
    guests: 2,
    priority: 1,
    check_in_deadline_minute: 170,
  },
  {
    room_id: "202",
    floor: 2,
    position: 50,
    room_type: "suite",
    occupancy_nights: 5,
    guests: 4,
    priority: 2,
    check_in_deadline_minute: 130,
  },
  {
    room_id: "301",
    floor: 3,
    position: 8,
    room_type: "deluxe",
    occupancy_nights: 1,
    guests: 2,
    priority: 0,
    check_in_deadline_minute: 320,
  },
  {
    room_id: "302",
    floor: 3,
    position: 42,
    room_type: "standard",
    occupancy_nights: 6,
    guests: 2,
    priority: 1,
    check_in_deadline_minute: 190,
  },
  {
    room_id: "401",
    floor: 4,
    position: 15,
    room_type: "suite",
    occupancy_nights: 3,
    guests: 3,
    priority: 2,
    check_in_deadline_minute: 150,
  },
  {
    room_id: "402",
    floor: 4,
    position: 48,
    room_type: "deluxe",
    occupancy_nights: 2,
    guests: 1,
    priority: 0,
    check_in_deadline_minute: 340,
  },
];

const largeDemoHousekeepers: Housekeeper[] = [
  {
    housekeeper_id: "H1",
    start_floor: 1,
    start_position: 0,
    speed_multiplier: 1.0,
    available_at_minute: 0,
    certified_for_suites: false,
  },
  {
    housekeeper_id: "H2",
    start_floor: 2,
    start_position: 25,
    speed_multiplier: 0.9,
    available_at_minute: 0,
    certified_for_suites: true,
  },
  {
    housekeeper_id: "H3",
    start_floor: 4,
    start_position: 0,
    speed_multiplier: 1.1,
    available_at_minute: 15,
    certified_for_suites: true,
  },
];

function groupAssignments(
  assignments: Assignment[],
): GroupedAssignments {
  return assignments.reduce<GroupedAssignments>(
    (groups, assignment) => {
      const currentAssignments =
        groups[assignment.housekeeper_id] ?? [];

      groups[assignment.housekeeper_id] = [
        ...currentAssignments,
        assignment,
      ].sort((a, b) => a.slot_index - b.slot_index);

      return groups;
    },
    {},
  );
}

function App() {
  const [rooms, setRooms] = useState<Room[]>(initialRooms);
  const [housekeepers, setHousekeepers] =
    useState<Housekeeper[]>(initialHousekeepers);

  const [comparison, setComparison] =
    useState<CompareResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const greedyAssignments = useMemo(() => {
    if (!comparison) {
      return {};
    }

    return groupAssignments(comparison.greedy.assignments);
  }, [comparison]);

  function loadLargeDemo(): void {
    setRooms(largeDemoRooms);
    setHousekeepers(largeDemoHousekeepers);
    setComparison(null);
    setError("");
  }
  const hungarianAssignments = useMemo(() => {
    if (!comparison) {
      return {};
    }

    return groupAssignments(comparison.hungarian.assignments);
  }, [comparison]);

  function updateRoom(
    index: number,
    field: keyof Room,
    value: string | number,
  ): void {
    setRooms((currentRooms) =>
      currentRooms.map((room, roomIndex) =>
        roomIndex === index
          ? {
              ...room,
              [field]: value,
            }
          : room,
      ),
    );
  }

  function updateHousekeeper(
    index: number,
    field: keyof Housekeeper,
    value: string | number | boolean,
  ): void {
    setHousekeepers((currentHousekeepers) =>
      currentHousekeepers.map(
        (housekeeper, housekeeperIndex) =>
          housekeeperIndex === index
            ? {
                ...housekeeper,
                [field]: value,
              }
            : housekeeper,
      ),
    );
  }

  function addRoom(): void {
    const nextNumber = rooms.length + 1;

    setRooms((currentRooms) => [
      ...currentRooms,
      {
        room_id: `R${nextNumber}`,
        floor: 1,
        position: 0,
        room_type: "standard",
        occupancy_nights: 1,
        guests: 1,
        priority: 0,
        check_in_deadline_minute: 240,
      },
    ]);
  }

  function addHousekeeper(): void {
    const nextNumber = housekeepers.length + 1;

    setHousekeepers((currentHousekeepers) => [
      ...currentHousekeepers,
      {
        housekeeper_id: `H${nextNumber}`,
        start_floor: 1,
        start_position: 0,
        speed_multiplier: 1,
        available_at_minute: 0,
        certified_for_suites: false,
      },
    ]);
  }

  function removeRoom(index: number): void {
    setRooms((currentRooms) =>
      currentRooms.filter(
        (_, roomIndex) => roomIndex !== index,
      ),
    );
  }

  function removeHousekeeper(index: number): void {
    setHousekeepers((currentHousekeepers) =>
      currentHousekeepers.filter(
        (_, housekeeperIndex) =>
          housekeeperIndex !== index,
      ),
    );
  }

  async function compareAlgorithms(): Promise<void> {
    if (rooms.length === 0) {
      setError("Add at least one room.");
      return;
    }

    if (housekeepers.length === 0) {
      setError("Add at least one housekeeper.");
      return;
    }

    if (rooms.some((room) => room.room_id.trim() === "")) {
      setError("Every room must have a Room ID.");
      return;
    }

    if (
      housekeepers.some(
        (housekeeper) =>
          housekeeper.housekeeper_id.trim() === "",
      )
    ) {
      setError("Every housekeeper must have an ID or name.");
      return;
    }

    setLoading(true);
    setError("");
    setComparison(null);

    try {
      const response = await fetch(`${API_URL}/compare`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          rooms,
          housekeepers,
        }),
      });

      const data: unknown = await response.json();

      if (!response.ok) {
        const detail =
          typeof data === "object" &&
          data !== null &&
          "detail" in data &&
          typeof data.detail === "string"
            ? data.detail
            : "Algorithm comparison failed.";

        throw new Error(detail);
      }

      setComparison(data as CompareResponse);
    } catch (caughtError) {
      if (
        caughtError instanceof TypeError &&
        caughtError.message === "Failed to fetch"
      ) {
        setError(
          `Could not connect to the backend at ${API_URL}. Make sure the FastAPI server is running and POST /compare is available.`,
        );
      } else {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Unable to compare algorithms.",
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <span className="eyebrow">
          HOUSEKEEPING OPTIMIZATION
        </span>

        <h1>Hotel Ops Optimizer</h1>

        <p>
          Enter today&apos;s rooms and staff, then compare
          Greedy and Hungarian housekeeping schedules.
        </p>
      </header>

      <section className="workspace">
      <div className="section-heading">
  <div>
    <p className="section-label">INPUT</p>
    <h2>Rooms</h2>
  </div>

  <div className="heading-actions">
    <button
      className="secondary-button"
      type="button"
      onClick={loadLargeDemo}
    >
      Use larger demo scenario
    </button>

    <button
      className="secondary-button"
      type="button"
      onClick={addRoom}
    >
      + Add room
    </button>
  </div>
</div>

        <div className="card-grid">
          {rooms.map((room, index) => (
            <article
              className="editor-card"
              key={`${room.room_id}-${index}`}
            >
              <div className="card-title-row">
                <label className="room-id-field">
                  <span>Room ID</span>

                  <input
                    className="title-input"
                    value={room.room_id}
                    placeholder="e.g. 303"
                    onChange={(event) =>
                      updateRoom(
                        index,
                        "room_id",
                        event.target.value,
                      )
                    }
                    aria-label="Room ID"
                  />
                </label>

                <button
                  className="remove-button"
                  type="button"
                  onClick={() => removeRoom(index)}
                  aria-label={`Remove room ${room.room_id}`}
                >
                  ×
                </button>
              </div>

              <div className="field-grid">
                <label>
                  Floor
                  <input
                    type="number"
                    min="1"
                    value={room.floor}
                    onChange={(event) =>
                      updateRoom(
                        index,
                        "floor",
                        Number(event.target.value),
                      )
                    }
                  />
                </label>

                <label>
                  Position
                  <input
                    type="number"
                    min="0"
                    value={room.position}
                    onChange={(event) =>
                      updateRoom(
                        index,
                        "position",
                        Number(event.target.value),
                      )
                    }
                  />
                </label>

                <label>
                  Room type
                  <select
                    value={room.room_type}
                    onChange={(event) =>
                      updateRoom(
                        index,
                        "room_type",
                        event.target.value as RoomType,
                      )
                    }
                  >
                    <option value="standard">
                      Standard
                    </option>
                    <option value="deluxe">
                      Deluxe
                    </option>
                    <option value="suite">
                      Suite
                    </option>
                  </select>
                </label>

                <label>
                  Guests
                  <input
                    type="number"
                    min="1"
                    value={room.guests}
                    onChange={(event) =>
                      updateRoom(
                        index,
                        "guests",
                        Number(event.target.value),
                      )
                    }
                  />
                </label>

                <label>
                  Stayed nights
                  <input
                    type="number"
                    min="1"
                    value={room.occupancy_nights}
                    onChange={(event) =>
                      updateRoom(
                        index,
                        "occupancy_nights",
                        Number(event.target.value),
                      )
                    }
                  />
                </label>

                <label>
                  Priority
                  <select
                    value={room.priority}
                    onChange={(event) =>
                      updateRoom(
                        index,
                        "priority",
                        Number(event.target.value),
                      )
                    }
                  >
                    <option value={0}>
                      General
                    </option>
                    <option value={1}>
                      Early check-in
                    </option>
                    <option value={2}>
                      VIP
                    </option>
                  </select>
                </label>

                <label className="wide-field">
                  Check-in deadline

                  <div className="input-with-unit">
                    <input
                      type="number"
                      min="0"
                      value={
                        room.check_in_deadline_minute
                      }
                      onChange={(event) =>
                        updateRoom(
                          index,
                          "check_in_deadline_minute",
                          Number(event.target.value),
                        )
                      }
                    />

                    <span>minutes</span>
                  </div>
                </label>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="workspace">
        <div className="section-heading">
          <div>
            <p className="section-label">STAFF</p>
            <h2>Housekeepers</h2>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={addHousekeeper}
          >
            + Add housekeeper
          </button>
        </div>

        <div className="card-grid">
          {housekeepers.map(
            (housekeeper, index) => (
              <article
                className="editor-card"
                key={`${housekeeper.housekeeper_id}-${index}`}
              >
                <div className="card-title-row">
                  <label className="room-id-field">
                    <span>
                      Housekeeper ID or name
                    </span>

                    <input
                      className="title-input"
                      value={
                        housekeeper.housekeeper_id
                      }
                      placeholder="e.g. H3 or Maria"
                      onChange={(event) =>
                        updateHousekeeper(
                          index,
                          "housekeeper_id",
                          event.target.value,
                        )
                      }
                      aria-label="Housekeeper ID or name"
                    />
                  </label>

                  <button
                    className="remove-button"
                    type="button"
                    onClick={() =>
                      removeHousekeeper(index)
                    }
                    aria-label={`Remove ${housekeeper.housekeeper_id}`}
                  >
                    ×
                  </button>
                </div>

                <div className="field-grid">
                  <label>
                    Start floor
                    <input
                      type="number"
                      min="1"
                      value={
                        housekeeper.start_floor
                      }
                      onChange={(event) =>
                        updateHousekeeper(
                          index,
                          "start_floor",
                          Number(event.target.value),
                        )
                      }
                    />
                  </label>

                  <label>
                    Start position
                    <input
                      type="number"
                      min="0"
                      value={
                        housekeeper.start_position
                      }
                      onChange={(event) =>
                        updateHousekeeper(
                          index,
                          "start_position",
                          Number(event.target.value),
                        )
                      }
                    />
                  </label>

                  <label>
                    Speed multiplier
                    <input
                      type="number"
                      min="0.1"
                      step="0.1"
                      value={
                        housekeeper.speed_multiplier
                      }
                      onChange={(event) =>
                        updateHousekeeper(
                          index,
                          "speed_multiplier",
                          Number(event.target.value),
                        )
                      }
                    />
                  </label>

                  <label>
                    Available after

                    <div className="input-with-unit">
                      <input
                        type="number"
                        min="0"
                        value={
                          housekeeper.available_at_minute
                        }
                        onChange={(event) =>
                          updateHousekeeper(
                            index,
                            "available_at_minute",
                            Number(event.target.value),
                          )
                        }
                      />

                      <span>minutes</span>
                    </div>
                  </label>
                </div>

                <label className="checkbox-field">
                  <input
                    type="checkbox"
                    checked={
                      housekeeper.certified_for_suites
                    }
                    onChange={(event) =>
                      updateHousekeeper(
                        index,
                        "certified_for_suites",
                        event.target.checked,
                      )
                    }
                  />

                  Certified to clean suites
                </label>
              </article>
            ),
          )}
        </div>
      </section>

      <section className="optimize-panel">
        <div>
          <p className="section-label">READY</p>

          <h2>Compare assignment algorithms</h2>

          <p>
            {rooms.length} rooms ·{" "}
            {housekeepers.length} housekeepers
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={compareAlgorithms}
          disabled={loading}
        >
          {loading
            ? "Comparing..."
            : "Compare algorithms"}
        </button>
      </section>

      {error && (
        <div
          className="error-message"
          role="alert"
        >
          {error}
        </div>
      )}

      {comparison && (
        <section className="results-section">
          <div className="section-heading">
            <div>
              <p className="section-label">
                COMPARISON
              </p>

              <h2>Algorithm performance</h2>
            </div>
          </div>

          <section className="summary-card">
  <div className="summary-header">
    🏆 Hungarian outperformed Greedy
  </div>

  <ul>
    <li>
      <strong>
        Makespan ↓
        {comparison.improvement.makespan_percent.toFixed(1)}%
      </strong>
      <br />
      The entire hotel finishes cleaning sooner.
    </li>

    <li>
      <strong>
        Travel ↓
        {comparison.improvement.total_travel_percent.toFixed(1)}%
      </strong>
      <br />
      Less walking between rooms.
    </li>

    <li>
      <strong>
        Workload imbalance ↓
        {comparison.improvement.workload_std_percent.toFixed(1)}%
      </strong>
      <br />
      Work is distributed more evenly.
    </li>

    <li>
      <strong>
        Total cost ↓
        {comparison.improvement.total_cost_percent.toFixed(1)}%
      </strong>
    </li>

    {comparison.improvement.vip_mean_ready_percent === 0 && (
      <li>
        ➖ VIP completion time unchanged.
      </li>
    )}

    {comparison.improvement.deadline_misses_percent === 0 && (
      <li>
        ➖ No additional deadline misses.
      </li>
    )}
  </ul>
</section>
          <div className="metrics-grid">
            <ComparisonMetricCard
              label="Makespan"
              greedy={comparison.greedy.metrics.makespan}
              hungarian={
                comparison.hungarian.metrics.makespan
              }
              unit="min"
              improvement={
                comparison.improvement.makespan_percent
              }
            />

            <ComparisonMetricCard
              label="Total travel"
              greedy={
                comparison.greedy.metrics.total_travel
              }
              hungarian={
                comparison.hungarian.metrics.total_travel
              }
              unit="min"
              improvement={
                comparison.improvement
                  .total_travel_percent
              }
            />

            <ComparisonMetricCard
              label="Workload deviation"
              greedy={
                comparison.greedy.metrics.workload_std
              }
              hungarian={
                comparison.hungarian.metrics.workload_std
              }
              improvement={
                comparison.improvement
                  .workload_std_percent
              }
            />

            <ComparisonMetricCard
              label="VIP mean ready"
              greedy={
                comparison.greedy.metrics
                  .vip_mean_ready
              }
              hungarian={
                comparison.hungarian.metrics
                  .vip_mean_ready
              }
              unit="min"
              improvement={
                comparison.improvement
                  .vip_mean_ready_percent
              }
            />

            <ComparisonMetricCard
              label="Deadline misses"
              greedy={
                comparison.greedy.metrics
                  .deadline_misses
              }
              hungarian={
                comparison.hungarian.metrics
                  .deadline_misses
              }
              decimals={0}
              improvement={
                comparison.improvement
                  .deadline_misses_percent
              }
            />

            <ComparisonMetricCard
              label="Total cost"
              greedy={
                comparison.greedy.metrics.total_cost
              }
              hungarian={
                comparison.hungarian.metrics.total_cost
              }
              improvement={
                comparison.improvement.total_cost_percent
              }
            />
          </div>

          <AlgorithmSchedule
            title="Greedy schedule"
            groupedAssignments={greedyAssignments}
          />

          <AlgorithmSchedule
            title="Hungarian schedule"
            groupedAssignments={hungarianAssignments}
          />
        </section>
      )}
    </main>
  );
}

function ComparisonMetricCard({
  label,
  greedy,
  hungarian,
  improvement,
  unit = "",
  decimals = 1,
}: {
  label: string;
  greedy: number;
  hungarian: number;
  improvement: number;
  unit?: string;
  decimals?: number;
}) {
  const formattedUnit = unit ? ` ${unit}` : "";
  const improvementIsPositive = improvement >= 0;

  return (
    <article className="metric-card">
      <span>{label}</span>

      <div>
        <small>Greedy</small>
        <strong>
          {greedy.toFixed(decimals)}
          {formattedUnit}
        </strong>
      </div>

      <div>
        <small>Hungarian</small>
        <strong>
          {hungarian.toFixed(decimals)}
          {formattedUnit}
        </strong>
      </div>

      <span>
        {improvementIsPositive ? "↓" : "↑"}{" "}
        {Math.abs(improvement).toFixed(1)}%
      </span>
    </article>
  );
}

function AlgorithmSchedule({
  title,
  groupedAssignments,
}: {
  title: string;
  groupedAssignments: GroupedAssignments;
}) {
  return (
    <section className="workspace">
      <div className="section-heading">
        <div>
          <p className="section-label">
            ASSIGNMENTS
          </p>

          <h2>{title}</h2>
        </div>
      </div>

      <div className="assignment-grid">
        {Object.entries(groupedAssignments).map(
          ([housekeeperId, assignments]) => (
            <article
              className="schedule-card"
              key={`${title}-${housekeeperId}`}
            >
              <div className="schedule-header">
                <span>{housekeeperId}</span>

                <small>
                  {assignments.length} rooms
                </small>
              </div>

              <ol>
                {assignments.map((assignment) => (
                  <li
                    key={`${housekeeperId}-${assignment.room_id}`}
                  >
                    <div>
                      <strong>
                        Room {assignment.room_id}
                      </strong>

                      <span>
                        {assignment.cleaning_time.toFixed(
                          1,
                        )}{" "}
                        min cleaning
                      </span>
                    </div>

                    <span className="slot-badge">
                      #{assignment.slot_index + 1}
                    </span>
                  </li>
                ))}
              </ol>
            </article>
          ),
        )}
      </div>
    </section>
  );
}

export default App;