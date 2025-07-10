#Financial Modeling

import streamlit as st
import pandas as pd
import os

from components.program_fees import render_program_fee_editor, get_current_program_fees
from components.fee_splits import render_fee_split_editor, get_current_fee_splits, display_fee_split_charts
from components.athlete_counts import render_athlete_counts

# Trigger rerun safely if needed
if st.session_state.get("trigger_fee_split_rerun"):
    del st.session_state["trigger_fee_split_rerun"]
    st.rerun()


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
athlete_counts = render_athlete_counts(athlete_levels["Level"].tolist())

# Section: Program Fees per Athlete
render_program_fee_editor(athlete_levels)
program_fees = get_current_program_fees()


# Section: Fee Splits
render_fee_split_editor(athlete_levels["Level"].tolist())
fee_splits = get_current_fee_splits()

# Financial modeling function
def calculate_per_athlete_financials(level, program_fees, fee_splits):
    total_fee = program_fees[level]
    splits = fee_splits[level]

    platform_pct = splits.get("Platform", 0)
    revenue = total_fee * (platform_pct / 100)

    cost_breakdown = {
        role: total_fee * (pct / 100)
        for role, pct in splits.items()
        if role != "Platform"
    }
    total_cost = sum(cost_breakdown.values())

    profit = revenue - total_cost

    return {
        "Level": level,
        "Total_Revenue": revenue,
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
