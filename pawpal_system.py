from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: str = ""


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


@dataclass
class DailySchedule:
    date: date
    scheduled_tasks: list = field(default_factory=list)  # list of (Task, start_time)
    warnings: list = field(default_factory=list)

    def add_task(self, task: Task, start_time: time) -> None:
        pass

    def get_total_duration(self) -> int:
        """Returns total scheduled minutes."""
        pass

    def is_overbooked(self) -> bool:
        """Returns True if total duration exceeds owner's available hours."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pets: list[Pet], tasks: list[Task]):
        self.owner = owner
        self.pets = pets
        self.tasks = tasks

    def generate(self) -> DailySchedule:
        """Build and return a DailySchedule from the current tasks and constraints."""
        pass

    def order_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by priority (ascending), then by time_preference."""
        pass

    def validate(self, schedule: DailySchedule) -> list[str]:
        """Check schedule for issues; return a list of warning strings."""
        pass
