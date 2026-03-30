from pawpal_system import Pet, Task


def make_task(name="Morning Walk"):
    return Task(
        name=name,
        duration=30,
        priority=1,
        time_preference="morning",
        frequency="daily",
        assigned_pet="Biscuit",
    )


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
