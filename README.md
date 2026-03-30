# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Four algorithmic features were added to `Scheduler` in `pawpal_system.py` after the initial implementation:

**`sort_by_time(scheduled_tasks)`**
Re-orders a schedule's tasks chronologically by start time. It uses a lambda key that formats each `datetime.time` as a zero-padded `"HH:MM"` string so that Python's default lexicographic sort gives correct chronological order without any custom comparator.

**`filter_tasks(completed, pet_name)`**
Returns a subset of `self.tasks` matching any combination of completion status and pet name. Both filters are optional and stack — passing both returns only the tasks that satisfy both conditions. Useful for building to-do views or per-pet task lists.

**`mark_task_complete(task, on_date)`**
Marks a task complete and automatically spawns the next occurrence for recurring tasks. Daily tasks reappear with `due_date = on_date + timedelta(days=1)`; weekly tasks with `+timedelta(days=7)`. One-time tasks (`frequency="once"`) return `None` with no new task created. The new task is copied via `dataclasses.replace()` so every field carries over and only `completed` and `due_date` change.

**`detect_conflicts(scheduled_tasks)`**
Checks every pair of scheduled tasks for overlapping time windows using the standard interval intersection test (`start_a < end_b and start_b < end_a`). Back-to-back tasks are not flagged. Each conflict produces a human-readable warning string that identifies the two tasks, whether they involve the same or different pets, and the exact overlap window — no exceptions are raised so the app continues running.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
