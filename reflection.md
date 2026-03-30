# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
- Classes:
    - **Pet**: Data holder for pet profile information
        - Attributes: name, species, breed, age, special_needs
    - **Owner**: Data holder for owner constraints
        - Attributes: name, available_hours_per_day
    - **Task**: A single care task with scheduling metadata
        - Attributes: name, duration, priority, time_preference, frequency, assigned_pet, notes
    - **DailySchedule**: The output of one scheduling run
        - Attributes: date, scheduled_tasks (list of (Task, start_time)), warnings
        - Methods: add_task(task, start_time), get_total_duration(), is_overbooked()
    - **Scheduler**: Core scheduling logic
        - Attributes: owner, pets (list), tasks
        - Methods: generate(), order_by_priority(tasks), validate(schedule)

**b. Design changes**

Three issues were caught during skeleton review before any logic was implemented:

1. **`Scheduler.generate()` gained a `target_date: date` parameter.**
   The original stub took no arguments, but `DailySchedule` requires a date. Without this parameter there was no way to produce a correctly dated schedule.

2. **`DailySchedule` gained an `available_minutes: int` field.**
   `is_overbooked()` compares total scheduled time against the owner's daily limit, but `DailySchedule` had no reference to that limit — making the method unimplementable. The `Scheduler` now passes `int(owner.available_hours_per_day * 60)` at construction time so the schedule is self-contained.

3. **`scheduled_tasks` and `warnings` were given explicit types (`list[tuple[Task, time]]` and `list[str]`).**
   The original `list` with a comment left the structure ambiguous. Typed lists make `get_total_duration()` straightforward to implement and allow static analysis to catch misuse early.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler uses a **greedy, first-fit strategy**: it sorts all tasks once by priority and time preference, then walks the list in order, placing each task immediately after the previous one. If a task doesn't fit in the remaining time budget it is skipped and a warning is issued — the scheduler never goes back to try a different arrangement.

**What this gives up:** a greedy first-fit pass cannot find the globally optimal schedule. For example, if a 40-minute grooming task (priority 3) is placed and leaves only 5 minutes, a 10-minute feeding task (priority 1) that arrives later will be skipped — even though dropping the grooming task would have left enough room for several higher-value tasks. A backtracking or dynamic-programming approach could find that better arrangement.

**Why it is reasonable here:** for a single pet owner with a small number of daily tasks (typically under 20), the greedy approach produces a schedule in O(n log n) time with no risk of hanging or crashing on edge cases. The priority sort already ensures the most important tasks land first, which aligns with what a pet owner actually needs — missing a low-priority grooming session is far less harmful than missing a feeding or medication. The skipped-task warnings make the limitation visible rather than hiding it, so the owner can manually adjust if needed.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used across every phase of the project, but with a different purpose at each stage:

- **Design phase (UML):** Used Copilot Chat with `#codebase` to brainstorm what attributes and methods each class needed. Prompts like *"What methods should a Scheduler class have if it needs to handle priority, time preferences, and overbooking?"* surfaced ideas quickly and helped catch missing fields (like `available_minutes` on `DailySchedule`) before any code was written.
- **Implementation phase:** Used inline Copilot completions to fill in method bodies once the signatures were already defined. The most useful prompts were specific: *"Implement `detect_conflicts` using an interval intersection test and return warning strings — do not raise exceptions."* Vague prompts produced vague code.
- **UI phase:** Asked Copilot to suggest which Streamlit components fit each use case (e.g., `st.metric` for the budget summary, `st.table` for sorted task lists), then manually wired them to the correct Scheduler methods.
- **Debugging:** When `sort_by_time` initially failed on edge-case times, describing the exact input and expected output to Copilot pointed directly to the missing zero-padding in the sort key.

The most effective prompt pattern was: *describe the contract* (inputs, outputs, constraints) first, then ask for an implementation — rather than asking for code and hoping the contract would be inferred.

**b. Judgment and verification**

When implementing `mark_task_complete`, Copilot's first suggestion created the next occurrence by calling `Task(name=task.name, duration=task.duration, ...)` and manually listing every field. This was rejected for two reasons: it was brittle (any new field added to `Task` would silently break recurrence) and it duplicated the dataclass constructor logic that `dataclasses.replace()` already handles correctly. The suggestion was modified to use `replace(task, completed=False, due_date=next_due)`, which copies all fields automatically and only overrides the two that change. The verification step was to add a field (`notes`) to a test task, complete it, and confirm the spawned task still carried the notes through — which the original Copilot version would have dropped.

---

## 4. Testing and Verification

**a. What you tested**

Five behaviors were covered by automated tests:

1. **`Task.mark_complete()` flips `completed` to `True`** — the simplest unit test, but critical because `filter_tasks` and `mark_task_complete` both depend on this flag being accurate.
2. **`Pet.add_task()` appends correctly** — verifies the Pet–Task relationship that the UML shows as a one-to-many association.
3. **`sort_by_time()` returns chronological order** — tested with out-of-order start times to confirm the zero-padded string key sorts correctly.
4. **Completing a daily task spawns the next day's task** — the most complex unit test: checks that `due_date` advances by exactly one day, `completed` resets to `False`, and the original task is not mutated.
5. **Overlapping tasks produce exactly one conflict warning** — validates the interval-intersection logic and confirms the warning names both tasks.

These tests were prioritized because they cover the four features that were newly added in the second implementation pass and are most likely to break silently under refactoring.

**b. Confidence**

**3 / 5.** The core happy paths are tested and passing. Confidence is limited by untested edge cases: tasks whose combined duration lands exactly on the budget boundary (off-by-one in `is_overbooked`), completing an already-completed recurring task (currently spawns a duplicate), zero-duration tasks in conflict detection, and `generate()` behavior when the task list is empty. These would be the first tests added in the next iteration.

---

## 5. Reflection

**a. What went well**

The most satisfying part was `detect_conflicts`. It required real algorithmic thinking — choosing the interval intersection test, deciding that back-to-back tasks should *not* conflict, and formatting warnings that are genuinely useful (overlap window, same-pet vs. different-pet scope) rather than just flagging a boolean. Seeing it surface meaningful warnings in the UI with `st.warning` validated both the logic and the design decision to return strings instead of raising exceptions.

The separation between `DailySchedule` (a data container produced by one scheduling run) and `Scheduler` (the stateful engine that owns pets and tasks across many runs) also held up well. When the UI needed to call `detect_conflicts` independently from `generate()`, that clean boundary made it trivial.

**b. What you would improve**

The greedy scheduler's biggest weakness is that it never backtracks. A next iteration would explore a simple knapsack approach: after the greedy pass, check whether any skipped task could fit if a lower-priority scheduled task were swapped out, and make that swap automatically. This would require changing `generate()` to return not just the schedule but also a list of considered-but-rejected swaps, which is a design change worth doing in a new method rather than mutating the existing one.

On the UI side, the "Apply filters" button requires a click after every dropdown change. Removing it in favor of reactive `st.selectbox` callbacks (using `st.session_state`) would feel more natural and reduce the chance of a user reading stale filter results.

**c. Key takeaway**

The most important lesson was that **AI tools amplify the quality of your design decisions — they do not replace them.** When the class structure was clear and the method contracts were precise, Copilot produced useful, correct code quickly. When a prompt was vague or a design decision was deferred, the suggestions were either generic or subtly wrong in ways that only became visible later (like the `Task(...)` recurrence bug). Being the lead architect meant making every structural decision *before* asking the AI to fill in the implementation — not the other way around.

Separate chat sessions for each phase (design → logic → UI → testing) reinforced this discipline. Starting a new session forced an explicit hand-off: the output of the UML phase became the input specification for the logic phase. Without that boundary, it was easy for earlier AI suggestions to silently influence later decisions in ways that were hard to trace. The session boundary made the architect — not the AI's conversation history — the source of continuity.
