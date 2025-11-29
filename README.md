# Smart Task Analyzer

Smart Task Analyzer is a Django + vanilla JavaScript mini-application that scores tasks, surfaces high-impact work, and exposes a REST API plus a single-page UI. The codebase follows a lightweight hexagonal structure: core domain scoring lives in `core/`, orchestration in `application/`, HTTP adapters in `infrastructure/`, and the UI in `frontend/` (served by Django).

## Quick Start
- **Python**: 3.8+ (developed on 3.13)
- **Install**: `python -m venv venv && venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS/Linux)
- **Dependencies**: `pip install -r backend/task_analyzer/requirements.txt`
- **Run server**:
  1. `cd backend/task_analyzer`
  2. `python manage.py migrate`
  3. `python manage.py runserver`
- **Open UI**: http://127.0.0.1:8000/
- **Run tests**: `python manage.py test tests`

## API Endpoints
- `POST /api/tasks/analyze/`
  - Body: `{ "tasks": [...], "config": { "weight_urgency": 2.0, ... } }`
  - Returns ordered `priority_list`, inferred `blocked_tasks`, `needs_attention`, `warnings`, and the resolved `config_used`.
- `GET /api/tasks/suggest/?top_n=3`
  - Optional POST to the same endpoint seeds the in-memory cache: `{ "tasks": [...] }`
  - Returns the top-N actionable tasks with short reasons.

## Frontend Walkthrough
The frontend is a single template (`frontend/index.html`) delivered by Django with static assets under `frontend/static/`. Users can:
- Add tasks via form or bulk JSON paste (IDs default to `task-n`).
- Pick a strategy (Smart Balance, Fastest Wins, High Impact, Deadline Driven).
- Trigger "Analyze" to hit the backend and display priority, blocked, and attention lists.
- Request "Get Suggestions" to fetch top tasks; the UI automatically seeds the cache if the current list is client-only.
- View the resolved scoring config and color-coded intensity for quick scanning.

## Algorithm Explanation (≈400 words)
Task scoring originates in the domain-layer `PriorityEngine`. Each task is first normalized into a `TaskDTO` so the application layer works with consistent types. The DTO parser tolerates imperfect inputs by filling defaults: titles fall back to "Untitled Task", dates use an ISO parser with a far-future fallback, hours coerce to positive floats, and importance values coerce to integers between one and ten. Before scoring, `TaskValidator` runs a light pass that records issues without dropping tasks; warnings flow through to the API so the user can fix them.

Scoring combines four signals, each mapped to a clearly defined function. Urgency uses the difference between the task's due date and today. Past-due work receives a base penalty that grows linearly with each additional overdue day, ensuring that deferred critical items bubble upward. Future tasks respect the selected urgency mode: linear mode rewards nearer dates with a reciprocal decay; exponential mode sharply discounts distant deadlines; and threshold mode maps dates inside a configurable window to a constant "high" urgency value. Importance simply reuses the human rating so that domain experts drive what "high impact" means.

Effort flips the usual cost framing—small estimated hours are considered "quick wins" by returning the inverse of the effort. That makes effortless tasks climb the list when urgency and importance are equal. Dependency contribution counts how many other tasks reference the current task's identifier. The more downstream work a task unlocks, the higher its dependency score, which keeps bottlenecks in the spotlight. These four subscores blend into the final value through weighted addition (`score = Σ weight_i * feature_i`). We expose these weights via the `ScoringConfig` dataclass and allow runtime overrides so users can experiment with strategies like Fastest Wins (heavier effort weight) or Deadline Driven (threshold urgency).

Circular dependencies are handled by constructing a `DependencyGraph` from the validated DTOs. The graph performs a depth-first search that tracks active recursion stacks; when it finds a back-edge it records the cycle and flags all nodes as blocked. Blocked tasks stay visible but are filtered into a separate list so the Priority list stays actionable. Suggestions reuse the same analysis but cap the output to the top-N unblocked tasks and produce human-readable reasons (e.g., "past due", "high impact", "quick win") to explain the recommendation.

## Design Decisions
- **Hexagonal layering** keeps HTTP concerns out of scoring code, enabling unit tests to hit pure functions.
- **Config-driven scoring** via `ScoringConfig` and merge helpers lets the UI switch strategies without code edits.
- **In-memory cache** in `infrastructure/api/state.py` keeps suggestion calls cheap while remaining stateless across deployments.
- **Validation with tolerance** logs issues yet keeps tasks in play, surfacing problems without blocking experimentation.

## Time Breakdown (≈ hours)
- Problem analysis & architecture sketch: 0.5
- Backend scaffolding, DTOs, validators, dependency graph: 1.5
- Scoring engine implementation & tuning: 1.25
- REST API wiring & caching: 0.75
- Frontend (UI + interactions + strategy toggles): 1.5
- Testing & test harness: 0.75
- Documentation polish: 0.5

## Bonus Challenges
- ✅ Circular dependency detection with user-facing feedback.
- ✅ Expanded unit test coverage (domain + API integration).

## Future Improvements
- Persist task lists per user session instead of in-memory cache.
- Add dependency graph visualization and Eisenhower matrix toggle.
- Incorporate calendar awareness (weekends/holidays) into urgency scoring.
- Introduce user-adjustable weight sliders stored via localStorage.
- Package Docker + compose recipe for streamlined local spin-up.
