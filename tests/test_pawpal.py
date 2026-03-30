from datetime import date, time
from pawpal_system import Pet, Task, Owner, Scheduler


def make_task(name="Morning Walk"):
    return Task(
        name=name,
        duration=30,
        priority=1,
        time_preference="morning",
        frequency="daily",
        assigned_pet="Biscuit",
    )


def make_scheduler(tasks):
    owner = Owner(name="Jordan", available_hours_per_day=8.0)
    pet = Pet(name="Biscuit", species="dog", breed="Beagle", age=3)
    return Scheduler(owner=owner, pets=[pet], tasks=tasks)


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog", breed="Beagle", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task("Morning Walk"))
    pet.add_task(make_task("Evening Walk"))
    assert len(pet.tasks) == 2


def test_sort_by_time_returns_chronological_order():
    """Tasks with later start times must come after earlier ones."""
    early = make_task("Early Task")
    late = make_task("Late Task")
    scheduler = make_scheduler([early, late])

    # Assign out-of-order start times
    scheduled = [(late, time(10, 0)), (early, time(8, 0))]
    result = scheduler.sort_by_time(scheduled)

    assert result[0][1] == time(8, 0)
    assert result[1][1] == time(10, 0)


def test_mark_task_complete_daily_creates_next_day_task():
    """Completing a daily task must append a new task due the following day."""
    task = make_task("Morning Walk")
    scheduler = make_scheduler([task])
    today = date(2026, 3, 30)

    next_task = scheduler.mark_task_complete(task, on_date=today)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 31)
    assert next_task.completed is False
    assert next_task in scheduler.tasks


def test_detect_conflicts_flags_duplicate_start_times():
    """Two tasks starting at the same time must produce a conflict warning."""
    task_a = make_task("Walk")
    task_b = Task(
        name="Feeding",
        duration=15,
        priority=1,
        time_preference="morning",
        frequency="daily",
        assigned_pet="Biscuit",
    )
    scheduler = make_scheduler([task_a, task_b])

    scheduled = [(task_a, time(8, 0)), (task_b, time(8, 0))]
    warnings = scheduler.detect_conflicts(scheduled)

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]
