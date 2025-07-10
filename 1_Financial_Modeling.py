#Financial Modeling

import streamlit as st
import pandas as pd
import os
import io
from pandas import ExcelWriter

from components.program_fees import render_program_fee_editor, get_current_program_fees
from components.fee_splits import render_fee_split_editor, get_current_fee_splits, display_fee_split_charts

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
    total_program_fee = program_fees[level]
    splits = fee_splits[level]

    revenue = total_program_fee

    # Cost = sum of all splits except Platform
    cost_breakdown = {
        role: total_program_fee * (pct / 100)
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

# -- Button to trigger export --
output = io.BytesIO()

with ExcelWriter(output, engine='xlsxwriter') as writer:
    # Sheet 1: Athlete Counts
    pd.DataFrame({
        "Level": athlete_counts.keys(),
        "Number of Athletes": athlete_counts.values()
    }).to_excel(writer, sheet_name="Athlete Counts", index=False)

    # Sheet 2: Program Fees
    pd.DataFrame({
        "Level": program_fees.keys(),
        "Program Fee per Athlete": program_fees.values()
    }).to_excel(writer, sheet_name="Program Fees", index=False)

    # Sheet 3: Fee Splits
    fee_split_rows = []
    for level, splits in fee_splits.items():
        for role, pct in splits.items():
            fee_split_rows.append({"Level": level, "Role": role, "Percentage": pct})
    pd.DataFrame(fee_split_rows).to_excel(writer, sheet_name="Fee Splits", index=False)

    # Sheet 4: Financial Summary
    results_df.to_excel(writer, sheet_name="Financial Summary", index=False)

st.download_button(
    label="Download Financial Model as Spreadsheet",
    data=output.getvalue(),
    file_name="Financial_Model_Snapshot.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


# Optional footer
st.markdown("---")
st.caption("Built by Cascaid Health · Contact: karam@cascaidhealth.com")
