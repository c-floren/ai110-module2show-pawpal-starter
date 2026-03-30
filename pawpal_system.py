from dataclasses import dataclass, field
from datetime import date, time


# Maps time_preference to a sort key so morning tasks come before afternoon, etc.
_TIME_PREFERENCE_ORDER = {"morning": 0, "anytime": 1, "afternoon": 2, "evening": 3}

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

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class DailySchedule:
    date: date
    available_minutes: int                                              # owner's daily limit in minutes
    scheduled_tasks: list[tuple[Task, time]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_task(self, task: Task, start_time: time) -> None:
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

        return warnings
