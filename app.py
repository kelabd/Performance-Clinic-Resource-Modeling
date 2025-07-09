import streamlit as st
import pandas as pd
import os

from components.practitioner_hours import render_weekly_hours_editor, get_current_weekly_hours


# Load input files
input_dir = os.path.join(os.getcwd(), "Inputs")

athlete_levels = pd.read_csv(os.path.join(input_dir, "Athlete_Levels.csv"))
practitioner_roles = pd.read_csv(os.path.join(input_dir, "Practitioner_Roles.csv"))
assignments = pd.read_csv(os.path.join(input_dir, "Assignments.csv"))
monthly_allocation = pd.read_csv(os.path.join(input_dir, "Monthly_Allocation.csv"))

# Set constants
weeks_in_program = 12

# Sidebar inputs
st.sidebar.title("Clinic Input Settings")
athlete_counts = {}
for level in athlete_levels["Level"]:
    athlete_counts[level] = st.sidebar.number_input(f"Athletes in Level {level}", min_value=0, value=1)

# Editable tables
st.sidebar.markdown("### Practitioner Rates")
editable_rates = practitioner_roles.copy()
for i, row in editable_rates.iterrows():
    editable_rates.at[i, "Hourly_Rate"] = st.sidebar.number_input(
        f"{row['Role']} Hourly Rate", value=float(row["Hourly_Rate"]), step=5.0
    )

# Convert to lookup structures
monthly_fees = athlete_levels.set_index("Level").to_dict("index")
practitioner_info = editable_rates.set_index("Role").to_dict("index")

# UI input for weekly hours per role
render_weekly_hours_editor(assignments)

# Use updated hours in financial modeling
assignment_hours = get_current_weekly_hours()


# Main function
def calculate_per_athlete_financials(level):
    monthly_fee_data = monthly_fees[level]
    total_revenue = 0
    total_cost = 0
    practitioner_cost_breakdown = {}

    # One-time fees
    for role, info in practitioner_info.items():
        if info["Is_OneTime"]:
            cost = info["OneTime_Cost"]
            total_cost += cost
            practitioner_cost_breakdown[role] = practitioner_cost_breakdown.get(role, 0) + cost

    # Recurring hours
    for (lvl, role), hours_per_week in assignment_hours.items():
        if lvl == level:
            hourly_rate = practitioner_info[role]["Hourly_Rate"]
            role_cost = hourly_rate * hours_per_week * weeks_in_program
            total_cost += role_cost
            practitioner_cost_breakdown[role] = practitioner_cost_breakdown.get(role, 0) + role_cost

    # Revenue
    for month in [1, 2, 3]:
        monthly_fee = monthly_fee_data[f"Monthly_Fee_M{month}"]
        total_revenue += monthly_fee

    profit = total_revenue - total_cost
    return {
        "Level": level,
        "Total_Revenue": total_revenue,
        "Total_Cost": total_cost,
        "Profit": profit,
        "Practitioner_Cost_Breakdown": practitioner_cost_breakdown
    }

# Run model
st.title("Performance Clinic Financial Model")
results = []
for level in athlete_levels["Level"]:
    per_athlete_result = calculate_per_athlete_financials(level)
    n = athlete_counts[level]
    results.append({
        "Level": level,
        "Athletes": n,
        "Total_Revenue": per_athlete_result["Total_Revenue"] * n,
        "Total_Cost": per_athlete_result["Total_Cost"] * n,
        "Profit": per_athlete_result["Profit"] * n
    })

results_df = pd.DataFrame(results)
st.subheader("Financial Summary by Level")
st.dataframe(results_df.style.format({"Total_Revenue": "${:,.0f}", "Total_Cost": "${:,.0f}", "Profit": "${:,.0f}"}))

# Expandable details
st.subheader("Cost Breakdown by Level")
for level in athlete_levels["Level"]:
    with st.expander(f"Level {level} Breakdown"):
        n = athlete_counts[level]
        breakdown = calculate_per_athlete_financials(level)["Practitioner_Cost_Breakdown"]
        df = pd.DataFrame.from_dict(breakdown, orient='index', columns=['Cost_per_Athlete'])
        df["Total_for_Level"] = df["Cost_per_Athlete"] * n
        st.dataframe(df.style.format("${:,.2f}"))
