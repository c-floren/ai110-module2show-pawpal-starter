from datetime import date
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session state initialization ---

if "owner" not in st.session_state:
    st.session_state.owner = None

if "pets" not in st.session_state:
    st.session_state.pets = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# -----------------------------------------------------------------------
# SECTION 1: Owner setup
# -----------------------------------------------------------------------

st.subheader("Owner")

with st.form("owner_form"):
    owner_name  = st.text_input("Your name", value="Jordan")
    avail_hours = st.number_input("Hours available today", min_value=0.5, max_value=16.0, value=3.0, step=0.5)
    if st.form_submit_button("Save owner"):
        st.session_state.owner = Owner(name=owner_name, available_hours_per_day=avail_hours)
        st.success(f"Owner saved: {owner_name} ({avail_hours} hrs available)")

# -----------------------------------------------------------------------
# SECTION 2: Add a pet
# -----------------------------------------------------------------------

st.divider()
st.subheader("Pets")

with st.form("pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name      = st.text_input("Pet name", value="Biscuit")
        species       = st.selectbox("Species", ["dog", "cat", "other"])
        breed         = st.text_input("Breed", value="Beagle")
    with col2:
        age           = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
        special_needs = st.text_input("Special needs (optional)", value="")

    if st.form_submit_button("Add pet"):
        pet = Pet(name=pet_name, species=species, breed=breed,
                  age=age, special_needs=special_needs)
        st.session_state.pets.append(pet)
        st.success(f"Added pet: {pet_name}")

if st.session_state.pets:
    st.write("**Current pets:**")
    for p in st.session_state.pets:
        needs = f" — {p.special_needs}" if p.special_needs else ""
        st.markdown(f"- **{p.name}** ({p.breed}, {p.species}, age {p.age}){needs}")
else:
    st.info("No pets added yet.")

# -----------------------------------------------------------------------
# SECTION 3: Add a task
# -----------------------------------------------------------------------

st.divider()
st.subheader("Tasks")

pet_names = [p.name for p in st.session_state.pets]

with st.form("task_form"):
    col1, col2 = st.columns(2)
    with col1:
        task_name       = st.text_input("Task name", value="Morning Walk")
        duration        = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        priority        = st.selectbox("Priority", [1, 2, 3, 4, 5],
                                        format_func=lambda x: f"{x} — {'High' if x == 1 else 'Low' if x == 5 else 'Medium'}")
    with col2:
        time_pref       = st.selectbox("Time preference", ["morning", "afternoon", "evening", "anytime"])
        frequency       = st.selectbox("Frequency", ["daily", "weekly", "once"])
        assigned_pet    = st.selectbox("Assign to pet", pet_names if pet_names else ["(add a pet first)"])
        notes           = st.text_input("Notes (optional)", value="")

    if st.form_submit_button("Add task"):
        if not pet_names:
            st.warning("Add a pet before adding tasks.")
        else:
            task = Task(name=task_name, duration=int(duration), priority=priority,
                        time_preference=time_pref, frequency=frequency,
                        assigned_pet=assigned_pet, notes=notes)
            # link task to its pet
            for pet in st.session_state.pets:
                if pet.name == assigned_pet:
                    pet.add_task(task)
            st.session_state.tasks.append(task)
            st.success(f"Added task: {task_name} -> {assigned_pet}")

if st.session_state.tasks:
    st.write("**Current tasks:**")
    st.table([
        {"Task": t.name, "Pet": t.assigned_pet, "Duration": f"{t.duration} min",
         "Priority": t.priority, "Time": t.time_preference, "Freq": t.frequency}
        for t in st.session_state.tasks
    ])
else:
    st.info("No tasks added yet.")

# -----------------------------------------------------------------------
# SECTION 4: Generate schedule
# -----------------------------------------------------------------------

st.divider()
st.subheader("Generate Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.owner:
        st.warning("Save an owner first.")
    elif not st.session_state.pets:
        st.warning("Add at least one pet first.")
    elif not st.session_state.tasks:
        st.warning("Add at least one task first.")
    else:
        scheduler = Scheduler(
            owner=st.session_state.owner,
            pets=st.session_state.pets,
            tasks=st.session_state.tasks,
        )
        schedule = scheduler.generate(date.today())

        st.success(f"Schedule for {schedule.date.strftime('%A, %B %d %Y')}")
        st.markdown(f"**Budget:** {schedule.available_minutes} min &nbsp;|&nbsp; "
                    f"**Scheduled:** {schedule.get_total_duration()} min &nbsp;|&nbsp; "
                    f"**Overbooked:** {'Yes' if schedule.is_overbooked() else 'No'}")

        st.markdown("#### Today's Plan (sorted by time)")
        sorted_tasks = scheduler.sort_by_time(schedule.scheduled_tasks)
        for task, start in sorted_tasks:
            end_min = start.hour * 60 + start.minute + task.duration
            end_str = f"{end_min // 60:02d}:{end_min % 60:02d}"
            st.markdown(
                f"- **{start.strftime('%I:%M %p')} → {end_str}** &nbsp; "
                f"[P{task.priority}] {task.name} *({task.assigned_pet})*"
            )

        if schedule.warnings:
            st.markdown("#### Warnings")
            for w in schedule.warnings:
                st.warning(w)

# -----------------------------------------------------------------------
# SECTION 5: Filter tasks
# -----------------------------------------------------------------------

st.divider()
st.subheader("Filter Tasks")

if not st.session_state.tasks:
    st.info("Add tasks above to use filters.")
else:
    col1, col2 = st.columns(2)
    with col1:
        filter_pet = st.selectbox(
            "Filter by pet",
            ["All pets"] + [p.name for p in st.session_state.pets],
        )
    with col2:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Incomplete", "Completed"],
        )

    if st.button("Apply filters"):
        scheduler = Scheduler(
            owner=st.session_state.owner or Owner("", 0),
            pets=st.session_state.pets,
            tasks=st.session_state.tasks,
        )

        # Build kwargs for filter_tasks based on UI selections
        pet_arg = None if filter_pet == "All pets" else filter_pet
        completed_arg = None if filter_status == "All" else (filter_status == "Completed")

        results = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)

        if results:
            st.table([
                {
                    "Task": t.name,
                    "Pet": t.assigned_pet,
                    "Duration": f"{t.duration} min",
                    "Priority": t.priority,
                    "Time": t.time_preference,
                    "Done": "Yes" if t.completed else "No",
                }
                for t in results
            ])
        else:
            st.info("No tasks match the selected filters.")
