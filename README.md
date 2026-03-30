# PawPal+

## 📸 Demo

<a href="/course_images/ai110/pawpal_demo.png" target="_blank"><img src='/course_images/ai110/pawpal_demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

A Streamlit app that helps a busy pet owner plan and track daily care tasks for one or more pets. Enter your available time, add your pets, build a task list, and PawPal+ generates a conflict-aware, priority-sorted daily schedule.

---

## Features

### Schedule Generation
PawPal+ builds a daily care plan from your task list in two passes:

1. **Priority-based ordering** — tasks are sorted by `priority` (1 = highest) then by `time_preference` (`morning → anytime → afternoon → evening`) before scheduling begins, so the most important tasks always claim time first.
2. **Time-budget enforcement** — the scheduler allocates tasks sequentially starting at 8:00 AM, skipping any task that would exceed the owner's available hours and recording a warning for each skipped item.

### Chronological Display — `sort_by_time`
After the schedule is built, tasks are re-sorted into start-time order for display. The sort uses a zero-padded `"HH:MM"` string key so Python's default lexicographic comparison (`"08:00" < "09:30" < "14:15"`) produces correct chronological order without a custom comparator.

### Conflict Detection — `detect_conflicts`
Every pair of scheduled tasks is checked for overlapping time windows using the standard interval-intersection test:

```
conflict  iff  start_a < end_b  and  start_b < end_a
```

Back-to-back tasks (where one ends exactly when the next begins) are **not** flagged. Each conflict produces a human-readable warning that names both tasks, states whether they involve the same or different pets, and reports the exact overlap window (`HH:MM–HH:MM`).

### Task Filtering — `filter_tasks`
Filter the full task list by completion status, by pet, or both at once. Filters stack — only tasks that satisfy every supplied condition are returned. Powers the **Filter Tasks** panel in the UI for building per-pet to-do views or reviewing what's already done.

### Daily & Weekly Recurrence — `mark_task_complete`
Completing a recurring task automatically spawns the next occurrence:

| Frequency | Next `due_date` |
|-----------|----------------|
| `daily`   | completion date + 1 day |
| `weekly`  | completion date + 7 days |
| `once`    | — (no new task created) |

The new task is created with `dataclasses.replace()`, so every field is carried over and only `completed` (reset to `False`) and `due_date` change.

### Overbooking & Validation Warnings
`validate()` runs automatically after schedule generation and surfaces:
- Tasks assigned to a pet name that doesn't exist in the pet list
- A total-duration-exceeds-budget warning when the schedule is overbooked
- All conflict warnings from `detect_conflicts`

The UI groups warnings into **Conflicts**, **Skipped Tasks**, and **Other Warnings** sections so issues are easy to act on.

### Professional UI Display
- Current tasks table is always sorted by priority via `order_by_priority` before rendering.
- Priority values are shown as human-readable labels (`1 — High`, `3 — Medium`, `5 — Low`).
- Schedule metrics (Budget / Scheduled / On-track vs Overbooked) are displayed as `st.metric` columns.
- `st.success` / `st.warning` / `st.error` components give instant visual feedback throughout.

---

## Project Structure

```
pawpal_system.py   — data classes (Owner, Pet, Task, DailySchedule) + Scheduler logic
app.py             — Streamlit UI
tests/
  test_pawpal.py   — automated test suite
class_diagram.mmd  — final UML class diagram (Mermaid source)
uml_final.png      — rendered UML diagram
```

---

## Setup

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

---

## Running the Tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### Test Coverage

| Test | What it verifies |
|------|-----------------|
| `test_mark_complete_changes_status` | `Task.mark_complete()` flips `completed` to `True` |
| `test_add_task_increases_pet_task_count` | `Pet.add_task()` appends to the pet's task list |
| `test_sort_by_time_returns_chronological_order` | `sort_by_time()` reorders tasks earliest → latest |
| `test_mark_task_complete_daily_creates_next_day_task` | Completing a daily task spawns a new task due the next day |
| `test_detect_conflicts_flags_duplicate_start_times` | Two overlapping tasks produce exactly one conflict warning |

---

## UML Class Diagram

The five core classes and their relationships:

- **`Owner`** — stores the owner's name and daily time budget.
- **`Pet`** — holds pet details and owns a list of associated `Task` objects.
- **`Task`** — describes a single care activity: duration, priority, time preference, frequency, and completion state.
- **`DailySchedule`** — produced by `Scheduler.generate()`; holds the list of `(Task, start_time)` pairs and any warnings.
- **`Scheduler`** — orchestrates everything: accepts an `Owner`, a list of `Pet` objects, and a list of `Task` objects, and exposes all scheduling, filtering, and conflict-detection methods.

See [`class_diagram.mmd`](class_diagram.mmd) for the full Mermaid source or [`uml_final.png`](uml_final.png) for the rendered diagram.
