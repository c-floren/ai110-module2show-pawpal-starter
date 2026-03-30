from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, DailySchedule

# --- Setup ---

owner = Owner(name="Jordan", available_hours_per_day=3.0)

biscuit = Pet(name="Biscuit", species="dog", breed="Beagle",        age=3)
mochi   = Pet(name="Mochi",   species="cat", breed="Scottish Fold", age=5, special_needs="joint supplements")

# Tasks added OUT OF ORDER: evening before morning, low-priority before high,
# completed tasks mixed in — so sorting and filtering have real work to do.
tasks = [
    Task("Biscuit Evening Walk",  duration=25, priority=2, time_preference="evening",   frequency="daily",  assigned_pet="Biscuit"),
    Task("Mochi Grooming",        duration=20, priority=3, time_preference="anytime",   frequency="weekly", assigned_pet="Mochi",    completed=True),
    Task("Biscuit Breakfast",     duration=10, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Biscuit"),
    Task("Mochi Play Session",    duration=15, priority=2, time_preference="afternoon", frequency="daily",  assigned_pet="Mochi"),
    Task("Mochi Joint Suppl.",    duration=5,  priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Mochi"),
    Task("Biscuit Grooming",      duration=40, priority=3, time_preference="anytime",   frequency="weekly", assigned_pet="Biscuit",   completed=True),
    Task("Mochi Breakfast",       duration=10, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Mochi"),
    Task("Biscuit Morning Walk",  duration=30, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Biscuit"),
    Task("Biscuit Play Session",  duration=20, priority=2, time_preference="afternoon", frequency="daily",  assigned_pet="Biscuit"),
    Task("Mochi Window Perch",    duration=10, priority=4, time_preference="afternoon", frequency="daily",  assigned_pet="Mochi"),
]

scheduler = Scheduler(owner=owner, pets=[biscuit, mochi], tasks=tasks)
schedule  = scheduler.generate(date.today())

# -----------------------------------------------------------------------
# 1. FULL SCHEDULE — as generated (priority-ordered, not time-sorted)
# -----------------------------------------------------------------------

def _row(task, start):
    end_min = start.hour * 60 + start.minute + task.duration
    return (
        f"  {start.strftime('%I:%M %p')} -> {end_min // 60:02d}:{end_min % 60:02d}"
        f"  [P{task.priority}] {task.name:<24} ({task.assigned_pet})"
    )

print("=" * 60)
print("       PAWPAL+  |  TODAY'S SCHEDULE (priority order)")
print("=" * 60)
print(f"  Owner : {owner.name}   Budget: {schedule.available_minutes} min")
print(f"  Date  : {schedule.date.strftime('%A, %B %d %Y')}")
print("-" * 60)
for task, start in schedule.scheduled_tasks:
    print(_row(task, start))
print("-" * 60)
print(f"  Scheduled: {schedule.get_total_duration()} min  |  "
      f"Remaining: {schedule.available_minutes - schedule.get_total_duration()} min  |  "
      f"Overbooked: {'Yes' if schedule.is_overbooked() else 'No'}")
if schedule.warnings:
    print("\n  Warnings:")
    for w in schedule.warnings:
        print(f"    ! {w}")

# -----------------------------------------------------------------------
# 2. sort_by_time — same tasks, re-ordered chronologically by HH:MM key
# -----------------------------------------------------------------------

print()
print("=" * 60)
print("       PAWPAL+  |  TODAY'S SCHEDULE (sorted by time)")
print("=" * 60)
print("  lambda key: f\"{pair[1].hour:02d}:{pair[1].minute:02d}\"")
print("  Zero-padded HH:MM strings sort lexicographically == chronologically")
print("-" * 60)
time_sorted = scheduler.sort_by_time(schedule.scheduled_tasks)
for task, start in time_sorted:
    print(_row(task, start))

# -----------------------------------------------------------------------
# 3. filter_tasks demos
# -----------------------------------------------------------------------

print()
print("=" * 60)
print("       PAWPAL+  |  FILTER: incomplete tasks only")
print("=" * 60)
incomplete = scheduler.filter_tasks(completed=False)
for t in incomplete:
    status = "DONE" if t.completed else "TODO"
    print(f"  [{status}] {t.name:<26} -> {t.assigned_pet}")

print()
print("=" * 60)
print("       PAWPAL+  |  FILTER: completed tasks only")
print("=" * 60)
done = scheduler.filter_tasks(completed=True)
for t in done:
    print(f"  [DONE] {t.name:<26} -> {t.assigned_pet}")

print()
print("=" * 60)
print("       PAWPAL+  |  FILTER: Biscuit's tasks (any status)")
print("=" * 60)
biscuit_tasks = scheduler.filter_tasks(pet_name="Biscuit")
for t in biscuit_tasks:
    status = "DONE" if t.completed else "TODO"
    print(f"  [{status}] {t.name:<26} (P{t.priority}, {t.time_preference})")

print()
print("=" * 60)
print("       PAWPAL+  |  FILTER: Mochi's incomplete tasks")
print("=" * 60)
mochi_todo = scheduler.filter_tasks(completed=False, pet_name="Mochi")
for t in mochi_todo:
    print(f"  [TODO] {t.name:<26} (P{t.priority}, {t.time_preference})")

# -----------------------------------------------------------------------
# 4. mark_task_complete — recurrence demo
# -----------------------------------------------------------------------
# timedelta recap:
#   timedelta(days=N) shifts a date forward by N calendar days.
#   date.today() + timedelta(days=1)  ->  tomorrow      (daily tasks)
#   date.today() + timedelta(days=7)  ->  one week out  (weekly tasks)

print()
print("=" * 60)
print("       PAWPAL+  |  RECURRENCE DEMO")
print("=" * 60)

today = date.today()

# Use fresh Task objects so the demo is self-contained and not affected
# by which tasks in the main list happen to already be completed.
daily_task  = Task("Biscuit Morning Walk", duration=30, priority=1,
                   time_preference="morning", frequency="daily",  assigned_pet="Biscuit")
weekly_task = Task("Biscuit Grooming",     duration=40, priority=3,
                   time_preference="anytime", frequency="weekly", assigned_pet="Biscuit")
once_task   = Task("Vet checkup",          duration=60, priority=1,
                   time_preference="morning", frequency="once",   assigned_pet="Biscuit")

for t in (daily_task, weekly_task, once_task):
    scheduler.tasks.append(t)

# --- daily task ---
next_daily = scheduler.mark_task_complete(daily_task, on_date=today)
print(f"\n  [DAILY]  Completed : {daily_task.name!r} (due {today})")
print(f"           Spawned   : {next_daily.name!r}")
print(f"           Next due  : {next_daily.due_date}  (today + timedelta(days=1))")

# --- weekly task ---
next_weekly = scheduler.mark_task_complete(weekly_task, on_date=today)
print(f"\n  [WEEKLY] Completed : {weekly_task.name!r} (due {today})")
print(f"           Spawned   : {next_weekly.name!r}")
print(f"           Next due  : {next_weekly.due_date}  (today + timedelta(days=7))")

# --- once task — no recurrence ---
result = scheduler.mark_task_complete(once_task, on_date=today)
print(f"\n  [ONCE]   Completed : {once_task.name!r}")
print(f"           Spawned   : {result}  (None — no recurrence for 'once')")

# --- show all tasks now in scheduler (completed + next occurrences) ---
print()
print("-" * 60)
print("  All tasks in scheduler after recurrence:")
print("-" * 60)
for t in scheduler.tasks:
    due = f"  due {t.due_date}" if t.due_date else ""
    status = "DONE" if t.completed else "TODO"
    print(f"  [{status}] {t.name:<28} freq={t.frequency:<7}{due}")

print("=" * 60)

# -----------------------------------------------------------------------
# 5. detect_conflicts — conflict detection demo
# -----------------------------------------------------------------------
# The normal generate() assigns tasks back-to-back so they never overlap.
# To exercise detect_conflicts we build a DailySchedule manually, placing
# tasks at explicit start times that intentionally overlap.
#
# Three scenarios tested:
#   A) Same pet, exact same start time       -> hard conflict
#   B) Same pet, second task starts mid-way  -> partial overlap
#   C) Different pets, overlapping windows   -> cross-pet conflict
#   D) Back-to-back tasks (end == start)     -> NOT a conflict (strict <)

print()
print("=" * 60)
print("       PAWPAL+  |  CONFLICT DETECTION DEMO")
print("=" * 60)

conflict_scheduler = Scheduler(
    owner=Owner("Jordan", 8.0),
    pets=[biscuit, mochi],
    tasks=[],
)

# Build a schedule manually so we control the exact start times
manual = DailySchedule(date=today, available_minutes=480)

walk       = Task("Morning Walk",  duration=30, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Biscuit")
feeding    = Task("Biscuit Feed",  duration=15, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Biscuit")
meds       = Task("Mochi Meds",    duration=10, priority=1, time_preference="morning",   frequency="daily",  assigned_pet="Mochi")
play       = Task("Biscuit Play",  duration=20, priority=2, time_preference="afternoon", frequency="daily",  assigned_pet="Biscuit")
mochi_play = Task("Mochi Play",    duration=20, priority=2, time_preference="afternoon", frequency="daily",  assigned_pet="Mochi")
groom      = Task("Biscuit Groom", duration=40, priority=3, time_preference="anytime",   frequency="weekly", assigned_pet="Biscuit")

# A) Same pet, exact same start -> conflict
manual.add_task(walk,       time(8, 0))   # Biscuit  08:00-08:30
manual.add_task(feeding,    time(8, 0))   # Biscuit  08:00-08:15  <- overlaps walk

# B) Same pet, starts mid-way through walk -> conflict
manual.add_task(groom,      time(8, 15))  # Biscuit  08:15-08:55  <- overlaps walk + feeding

# C) Different pets, overlapping window -> cross-pet conflict
manual.add_task(meds,       time(8, 20))  # Mochi    08:20-08:30  <- overlaps walk (diff pet)

# D) Back-to-back — should NOT be flagged (strict < means touching is fine)
manual.add_task(play,       time(9, 0))   # Biscuit  09:00-09:20
manual.add_task(mochi_play, time(9, 20))  # Mochi    09:20-09:40  <- touches, no overlap

print()
print("  Scheduled tasks (manual start times):")
print(f"  {'Task':<20} {'Pet':<10} {'Start':>6}  {'End':>6}")
print("  " + "-" * 46)
for t, s in manual.scheduled_tasks:
    end_min = s.hour * 60 + s.minute + t.duration
    print(f"  {t.name:<20} {t.assigned_pet:<10} "
          f"{s.hour:02d}:{s.minute:02d}   {end_min // 60:02d}:{end_min % 60:02d}")

conflicts = conflict_scheduler.detect_conflicts(manual.scheduled_tasks)
print()
if conflicts:
    print(f"  {len(conflicts)} conflict(s) detected:")
    for w in conflicts:
        print(f"    ! {w}")
else:
    print("  No conflicts detected.")

print("=" * 60)
