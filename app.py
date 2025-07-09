import streamlit as st
import pandas as pd
import os

from components.program_fees import render_program_fee_editor, get_current_program_fees
from components.fee_splits import render_fee_split_editor, get_current_fee_splits, display_fee_split_charts


# Load input files
input_dir = os.path.join(os.getcwd(), "Inputs")
athlete_levels = pd.read_csv(os.path.join(input_dir, "Athlete_Levels.csv"))

# Sidebar title
st.sidebar.title("Input Settings")

# Reset functionality
if st.sidebar.button("Reset All to Defaults"):
    for key in list(st.session_state.keys()):
        if not key.startswith("_"):
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

# Section: Program Fees per Athlete
render_program_fee_editor(athlete_levels)
program_fees = get_current_program_fees()


# Section: Fee Splits
render_fee_split_editor(athlete_levels["Level"].tolist())
fee_splits = get_current_fee_splits()

# Financial modeling function
def calculate_per_athlete_financials(level, program_fees, fee_splits):
    total_revenue = program_fees[level]
    total_cost = 0
    cost_breakdown = {}

    for role, pct in fee_splits[level].items():
        role_cost = total_revenue * (pct / 100)
        total_cost += role_cost
        cost_breakdown[role] = role_cost

    profit = total_revenue - total_cost
    return {
        "Level": level,
        "Total_Revenue": total_revenue,
        "Total_Cost": total_cost,
        "Profit": profit,
        "Practitioner_Cost_Breakdown": cost_breakdown
    }

# Main dashboard output
st.title("Performance Clinic Financial Model")

# Summary table
results = []
for level in athlete_levels["Level"]:
    n_athletes = athlete_counts[level]
    per_athlete = calculate_per_athlete_financials(level, program_fees, fee_splits)
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
        breakdown = calculate_per_athlete_financials(level, program_fees, fee_splits)["Practitioner_Cost_Breakdown"]
        df = pd.DataFrame.from_dict(breakdown, orient='index', columns=['Cost_per_Athlete'])
        df["Total_for_Level"] = df["Cost_per_Athlete"] * n_athletes
        st.dataframe(df.style.format("${:,.2f}"))
        
# Visualize fee splits
display_fee_split_charts(athlete_levels["Level"].tolist())

# Optional footer
st.markdown("---")
st.caption("Built by Cascaid Health · Contact: karam@cascaidhealth.com")
