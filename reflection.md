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

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
