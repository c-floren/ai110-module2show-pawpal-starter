from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---

owner = Owner(name="Jordan", available_hours_per_day=3.0)

biscuit = Pet(name="Biscuit", species="dog", breed="Beagle",        age=3)
mochi   = Pet(name="Mochi",   species="cat", breed="Scottish Fold", age=5, special_needs="joint supplements")

tasks = [
    # Morning essentials — both pets eat first (priority 1)
    Task("Biscuit Breakfast",    duration=10, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Biscuit"),
    Task("Mochi Breakfast",      duration=10, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Mochi"),
    Task("Mochi Joint Suppl.",   duration=5,  priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Mochi"),

    # Morning walk — dog only (priority 1)
    Task("Biscuit Morning Walk", duration=30, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Biscuit"),

    # Afternoon enrichment — both pets (priority 2)
    Task("Biscuit Play Session", duration=20, priority=2, time_preference="afternoon", frequency="daily",  assigned_pet="Biscuit"),
    Task("Mochi Play Session",   duration=15, priority=2, time_preference="afternoon", frequency="daily",  assigned_pet="Mochi"),

    # Weekly grooming — both pets (priority 3)
    Task("Biscuit Grooming",     duration=40, priority=3, time_preference="anytime",   frequency="weekly", assigned_pet="Biscuit"),
    Task("Mochi Grooming",       duration=20, priority=3, time_preference="anytime",   frequency="weekly", assigned_pet="Mochi"),
]

# --- Generate schedule ---

scheduler = Scheduler(owner=owner, pets=[biscuit, mochi], tasks=tasks)
schedule  = scheduler.generate(date.today())

# --- Display ---

print("=" * 48)
print("          PAWPAL+  |  TODAY'S SCHEDULE")
print("=" * 48)
print(f"  Owner : {owner.name}")
print(f"  Pets  : {biscuit.name} ({biscuit.breed}), {mochi.name} ({mochi.breed})")
print(f"  Date  : {schedule.date.strftime('%A, %B %d %Y')}")
print(f"  Budget: {owner.available_hours_per_day:.0f} hrs ({schedule.available_minutes} min)")
print("-" * 48)

for task, start in schedule.scheduled_tasks:
    end_minutes = start.hour * 60 + start.minute + task.duration
    end = f"{end_minutes // 60:02d}:{end_minutes % 60:02d}"
    print(f"  {start.strftime('%I:%M %p')} -> {end}  "
          f"[P{task.priority}] {task.name}")

print("-" * 48)
print(f"  Scheduled : {schedule.get_total_duration()} min")
print(f"  Remaining : {schedule.available_minutes - schedule.get_total_duration()} min")
print(f"  Overbooked: {'Yes' if schedule.is_overbooked() else 'No'}")

if schedule.warnings:
    print()
    print("  Warnings:")
    for w in schedule.warnings:
        print(f"    ! {w}")

print("=" * 48)
