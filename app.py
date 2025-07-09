import streamlit as st
import pandas as pd
import os

from components.practitioner_hours import render_weekly_hours_editor, get_current_weekly_hours
from components.practitioner_rates import render_hourly_rates_editor, get_current_hourly_rates
from components.athlete_fees import render_athlete_fee_editor, get_current_athlete_fees

# Load input files
input_dir = os.path.join(os.getcwd(), "Inputs")
athlete_levels = pd.read_csv(os.path.join(input_dir, "Athlete_Levels.csv"))
practitioner_roles = pd.read_csv(os.path.join(input_dir, "Practitioner_Roles.csv"))
assignments = pd.read_csv(os.path.join(input_dir, "Assignments.csv"))
monthly_allocation = pd.read_csv(os.path.join(input_dir, "Monthly_Allocation.csv"))

# Set constants
weeks_in_program = 12

# Sidebar title
st.sidebar.title("Input Settings")

if st.sidebar.button("Reset All to Defaults"):
    # Avoid deleting internal Streamlit keys
    for key in list(st.session_state.keys()):
        if not key.startswith("_"):  # Only clear user-defined keys
            del st.session_state[key]
    st.rerun()

# Section: Number of Athletes
athlete_counts = {}
with st.sidebar.expander("Number of Athletes", expanded=False):
    for level in athlete_levels["Level"]:
        athlete_counts[level] = st.number_input(
            f"Level {level}",
            min_value=0,
            value=1,
            key=f"athletes_{level}"
        )

# Section: Monthly Fees per Athlete
render_athlete_fee_editor(athlete_levels)
athlete_fees = get_current_athlete_fees()

# Section: Practitioner Hourly Rates
render_hourly_rates_editor(practitioner_roles)
editable_rates = practitioner_roles.copy()
editable_rates["Hourly_Rate"] = editable_rates["Role"].map(get_current_hourly_rates())
practitioner_data = editable_rates.set_index("Role").to_dict("index")

# Section: Weekly Hours per Role
render_weekly_hours_editor(assignments)
weekly_hours_by_level_and_role = get_current_weekly_hours()

# Financial modeling function
def calculate_per_athlete_financials(level, athlete_fees, practitioner_data, weekly_hours):
    total_revenue = 0
    total_cost = 0
    practitioner_cost_breakdown = {}

    # One-time fees
    for role, info in practitioner_data.items():
        if info["Is_OneTime"]:
            cost = info["OneTime_Cost"]
            total_cost += cost
            practitioner_cost_breakdown[role] = practitioner_cost_breakdown.get(role, 0) + cost

    # Recurring weekly hours
    for (lvl, role), hours_per_week in weekly_hours.items():
        if lvl == level:
            hourly_rate = practitioner_data[role]["Hourly_Rate"]
            role_cost = hourly_rate * hours_per_week * weeks_in_program
            total_cost += role_cost
            practitioner_cost_breakdown[role] = practitioner_cost_breakdown.get(role, 0) + role_cost

    # Monthly revenue
    for month in [1, 2, 3]:
        total_revenue += athlete_fees[(level, month)]

    profit = total_revenue - total_cost
    return {
        "Level": level,
        "Total_Revenue": total_revenue,
        "Total_Cost": total_cost,
        "Profit": profit,
        "Practitioner_Cost_Breakdown": practitioner_cost_breakdown
    }

# Main dashboard output
st.title("Performance Clinic Financial Model")

# Summary table
results = []
for level in athlete_levels["Level"]:
    n_athletes = athlete_counts[level]
    per_athlete = calculate_per_athlete_financials(level, athlete_fees, practitioner_data, weekly_hours_by_level_and_role)
    results.append({
        "Level": level,
        "Athletes": n_athletes,
        "Total_Revenue": per_athlete["Total_Revenue"] * n_athletes,
        "Total_Cost": per_athlete["Total_Cost"] * n_athletes,
        "Profit": per_athlete["Profit"] * n_athletes
    })

results_df = pd.DataFrame(results)
st.subheader("Financial Summary by Level")
st.dataframe(results_df.style.format({
    "Total_Revenue": "${:,.0f}",
    "Total_Cost": "${:,.0f}",
    "Profit": "${:,.0f}"
}))

# Detailed cost breakdown
st.subheader("Cost Breakdown by Level")
for level in athlete_levels["Level"]:
    with st.expander(f"Level {level} Breakdown"):
        n_athletes = athlete_counts[level]
        breakdown = calculate_per_athlete_financials(level, athlete_fees, practitioner_data, weekly_hours_by_level_and_role)["Practitioner_Cost_Breakdown"]
        df = pd.DataFrame.from_dict(breakdown, orient='index', columns=['Cost_per_Athlete'])
        df["Total_for_Level"] = df["Cost_per_Athlete"] * n_athletes
        st.dataframe(df.style.format("${:,.2f}"))

# Optional footer
st.markdown("---")
st.caption("Built by Cascaid Health · Contact: karam@cascaidhealth.com")
