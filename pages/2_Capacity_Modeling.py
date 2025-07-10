# Capacity Modeling

import streamlit as st
import pandas as pd

# --- Configurable defaults ---
DEFAULT_QB_HOURS_PER_ATHLETE = {3: 0.5, 4: 3, 5: 4}
DEFAULT_COACH_HOURS_PER_ATHLETE = {3: 2, 4: 4, 5: 5}
ATHLETE_LEVELS = [3, 4, 5]

# --- Input: Total number of athletes (carried from Financial Modeling page) ---
st.title("Capacity Modeling")

st.header("Athlete Counts")
athlete_counts = {}
for level in ATHLETE_LEVELS:
    key = f"capacity_athletes_{level}"
    default_val = st.session_state.get(key, 1)
    athlete_counts[level] = st.number_input(
        f"Number of Level {level} Athletes",
        min_value=0,
        value=default_val,
        key=key
    )

# --- Input: Available Practitioners ---
st.header("Practitioner Availability")

col1, col2 = st.columns(2)
with col1:
    num_qbs = st.number_input("Number of QBs", min_value=0, value=2)
    max_qb_hours = st.number_input("Max Hours per QB per Week", min_value=0.0, value=20.0)
with col2:
    num_coaches = st.number_input("Number of Coaches", min_value=0, value=2)
    max_coach_hours = st.number_input("Max Hours per Coach per Week", min_value=0.0, value=20.0)

# --- Input: Weekly Hours per Athlete per Role ---
st.header("Weekly Service Time per Athlete")
qb_hours = {}
coach_hours = {}

for level in ATHLETE_LEVELS:
    col1, col2 = st.columns(2)
    with col1:
        qb_hours[level] = st.number_input(
            f"QB Hours for Level {level} Athlete",
            min_value=0.0,
            value=float(DEFAULT_QB_HOURS_PER_ATHLETE[level]),
            key=f"qb_hours_{level}"
        )
    with col2:
        coach_hours[level] = st.number_input(
            f"Coach Hours for Level {level} Athlete",
            min_value=0.0,
            value=float(DEFAULT_COACH_HOURS_PER_ATHLETE[level]),
            key=f"coach_hours_{level}"
        )

# --- Calculation ---
st.header("Capacity Check")

def compute_required_hours(counts, per_athlete_hours):
    return sum(counts[lvl] * per_athlete_hours[lvl] for lvl in ATHLETE_LEVELS)

total_required_qb_hours = compute_required_hours(athlete_counts, qb_hours)
total_required_coach_hours = compute_required_hours(athlete_counts, coach_hours)

available_qb_hours = num_qbs * max_qb_hours
available_coach_hours = num_coaches * max_coach_hours

# --- Results ---
st.subheader("QB Capacity")
st.write(f"Required: **{total_required_qb_hours:.1f}** hrs/week")
st.write(f"Available: **{available_qb_hours:.1f}** hrs/week")
if total_required_qb_hours > available_qb_hours:
    st.error("Not enough QB capacity!")
else:
    st.success("QB capacity is sufficient.")

st.subheader("Coach Capacity")
st.write(f"Required: **{total_required_coach_hours:.1f}** hrs/week")
st.write(f"Available: **{available_coach_hours:.1f}** hrs/week")
if total_required_coach_hours > available_coach_hours:
    st.error("Not enough Coach capacity!")
else:
    st.success("Coach capacity is sufficient.")
