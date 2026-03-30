from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta


# Maps time_preference to a sort key so morning tasks come before afternoon, etc.
_TIME_PREFERENCE_ORDER = {"morning": 0, "anytime": 1, "afternoon": 2, "evening": 3}

# How many days ahead each recurring frequency schedules its next occurrence.
# timedelta(days=N) is added to the completion date to get the new due_date.
_RECURRENCE_DAYS = {"daily": 1, "weekly": 7}

# Daily schedule starts at 8:00 AM
_SCHEDULE_START_HOUR = 8


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: str = ""
    tasks: list = field(default_factory=list)

    def add_task(self, task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    available_hours_per_day: float


@dataclass
class Task:
    name: str
    duration: int           # minutes
    priority: int           # 1 (highest) to 5 (lowest)
    time_preference: str    # "morning", "afternoon", "evening", "anytime"
    frequency: str          # "daily", "weekly", "once"
    assigned_pet: str       # pet name
    notes: str = ""
    completed: bool = False
    due_date: date | None = None  # None means due today; set by recurrence logic

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class DailySchedule:
    date: date
    available_minutes: int                                              # owner's daily limit in minutes
    scheduled_tasks: list[tuple[Task, time]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_task(self, task: Task, start_time: time) -> None:
        """Append a (Task, start_time) tuple to the scheduled task list."""
        self.scheduled_tasks.append((task, start_time))

    def get_total_duration(self) -> int:
        """Returns total scheduled minutes."""
        return sum(task.duration for task, _ in self.scheduled_tasks)

    def is_overbooked(self) -> bool:
        """Returns True if get_total_duration() exceeds available_minutes."""
        return self.get_total_duration() > self.available_minutes


class Scheduler:
    def __init__(self, owner: Owner, pets: list[Pet], tasks: list[Task]):
        self.owner = owner
        self.pets = pets
        self.tasks = tasks

    def generate(self, target_date: date) -> DailySchedule:
        """Build and return a DailySchedule for target_date from current tasks and constraints."""
        available_minutes = int(self.owner.available_hours_per_day * 60)
        schedule = DailySchedule(date=target_date, available_minutes=available_minutes)

        ordered = self.order_by_priority(self.tasks)
        elapsed = 0
        current_minutes = _SCHEDULE_START_HOUR * 60  # track position as minutes-since-midnight

        for task in ordered:
            if elapsed + task.duration > available_minutes:
                schedule.warnings.append(
                    f"'{task.name}' skipped — not enough time remaining "
                    f"({task.duration} min needed, {available_minutes - elapsed} min left)."
                )
                continue

            start_time = time(current_minutes // 60, current_minutes % 60)
            schedule.add_task(task, start_time)
            elapsed += task.duration
            current_minutes += task.duration

        schedule.warnings.extend(self.validate(schedule))
        return schedule

    def order_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by priority (ascending), then by time_preference."""
        return sorted(
            tasks,
            key=lambda t: (t.priority, _TIME_PREFERENCE_ORDER.get(t.time_preference, 1))
        )

    def sort_by_time(
        self, scheduled_tasks: list[tuple["Task", time]]
    ) -> list[tuple["Task", time]]:
        """Return scheduled_tasks sorted chronologically by start time.

        Uses a lambda key that formats each datetime.time as a zero-padded
        "HH:MM" string.  Zero-padding ensures lexicographic (string) order
        equals chronological order:

            "08:00" < "09:30" < "14:15"  →  correct chronological order

        Args:
            scheduled_tasks: List of (Task, start_time) pairs, as produced
                             by DailySchedule.scheduled_tasks.

        Returns:
            A new list of the same pairs sorted earliest-to-latest.
            The original list is not modified.
        """
        return sorted(
            scheduled_tasks,
            key=lambda pair: f"{pair[1].hour:02d}:{pair[1].minute:02d}"
        )

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list["Task"]:
        """Return tasks from self.tasks that match every supplied filter.

        Args:
            completed: If True, keep only completed tasks.
                       If False, keep only incomplete tasks.
                       If None, completion status is ignored.
            pet_name:  If provided, keep only tasks assigned to that pet.
                       If None, all pets are included.

        Returns:
            A filtered (and possibly empty) list of Task objects.
        """
        result = self.tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.assigned_pet == pet_name]
        return result

    def mark_task_complete(self, task: Task, on_date: date | None = None) -> "Task | None":
        """Mark task complete and, for recurring tasks, spawn the next occurrence.

        How timedelta works here:
            timedelta(days=N) represents a duration of N days.
            Adding it to a date shifts that date forward by exactly N days:

                date(2026, 3, 30) + timedelta(days=1)  ->  date(2026, 3, 31)  # daily
                date(2026, 3, 30) + timedelta(days=7)  ->  date(2026, 4, 6)   # weekly

            _RECURRENCE_DAYS maps each frequency string to the correct N,
            so we never hard-code the numbers outside that single dict.

        Args:
            task:    The Task to mark complete. Must already be in self.tasks.
            on_date: The date of completion (defaults to today).

        Returns:
            The newly created next-occurrence Task for "daily"/"weekly" tasks,
            or None if frequency is "once" (no recurrence needed).
        """
        task.mark_complete()

        days_ahead = _RECURRENCE_DAYS.get(task.frequency)
        if days_ahead is None:
            return None  # "once" — no next occurrence

        completion_date = on_date or date.today()
        next_due = completion_date + timedelta(days=days_ahead)

        # dataclasses.replace() copies every field from task, then applies
        # the keyword overrides — cleaner than calling Task(...) manually.
        next_task = replace(task, completed=False, due_date=next_due)
        self.tasks.append(next_task)
        return next_task

    def detect_conflicts(
        self, scheduled_tasks: list[tuple[Task, time]]
    ) -> list[str]:
        """Return a warning string for every pair of tasks whose time windows overlap.

        Uses the standard interval intersection test: two tasks A and B
        conflict when A starts before B ends AND B starts before A ends.
        Written in minutes-since-midnight:

            start_a < end_b  and  start_b < end_a

        Strict less-than means back-to-back tasks (end_a == start_b) are
        allowed and do not produce a warning.

        Each warning identifies whether the conflict is between tasks for
        the same pet or different pets, and reports the exact overlap window
        (HH:MM–HH:MM).  Warnings are returned rather than exceptions raised
        so the caller can surface them in the UI without crashing.

        Args:
            scheduled_tasks: List of (Task, start_time) pairs to check.
                             Typically DailySchedule.scheduled_tasks, but
                             any list of that shape works (useful for tests).

        Returns:
            A list of human-readable warning strings, one per conflicting
            pair.  Returns an empty list when no conflicts are found.
        """
        warnings = []

        # Convert each entry to (task, start_min, end_min) once up-front
        # so the inner loop does only arithmetic, no repeated time math.
        windows = [
            (task, start.hour * 60 + start.minute,
             start.hour * 60 + start.minute + task.duration)
            for task, start in scheduled_tasks
        ]

        for i in range(len(windows)):
            for j in range(i + 1, len(windows)):
                task_a, start_a, end_a = windows[i]
                task_b, start_b, end_b = windows[j]

                if start_a < end_b and start_b < end_a:
                    overlap_start = max(start_a, start_b)
                    overlap_end   = min(end_a, end_b)
                    scope = ("same pet" if task_a.assigned_pet == task_b.assigned_pet
                             else "different pets")
                    warnings.append(
                        f"Conflict ({scope}): '{task_a.name}' ({task_a.assigned_pet})"
                        f" and '{task_b.name}' ({task_b.assigned_pet})"
                        f" overlap {overlap_start // 60:02d}:{overlap_start % 60:02d}"
                        f"–{overlap_end // 60:02d}:{overlap_end % 60:02d}."
                    )

        return warnings

    def validate(self, schedule: DailySchedule) -> list[str]:
        """Check schedule for issues; return a list of warning strings."""
        warnings = []
        known_pets = {pet.name for pet in self.pets}

        for task, _ in schedule.scheduled_tasks:
            if task.assigned_pet and task.assigned_pet not in known_pets:
                warnings.append(
                    f"'{task.name}' is assigned to '{task.assigned_pet}', "
                    f"who is not in the pet list."
                )

        if schedule.is_overbooked():
            warnings.append(
                f"Schedule exceeds available time "
                f"({schedule.get_total_duration()} min scheduled, "
                f"{schedule.available_minutes} min available)."
            )

        warnings.extend(self.detect_conflicts(schedule.scheduled_tasks))
        return warnings
