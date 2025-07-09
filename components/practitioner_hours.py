import streamlit as st
import pandas as pd

def render_weekly_hours_editor(assignments_df):
    st.sidebar.markdown("### Weekly Hours per Role")

    # Initialize editable hours state
    if "weekly_hours" not in st.session_state:
        st.session_state.weekly_hours = {}
        for _, row in assignments_df.iterrows():
            key = (row["Level"], row["Role"])
            st.session_state.weekly_hours[key] = row["Hours_per_week"]

    # Show number input per role per level
    levels = sorted(assignments_df["Level"].unique())
    for level in levels:
        with st.sidebar.expander(f"Level {level} Weekly Hours"):
            level_assignments = assignments_df[assignments_df["Level"] == level]
            for _, row in level_assignments.iterrows():
                key = (row["Level"], row["Role"])
                st.session_state.weekly_hours[key] = st.number_input(
                    f"{row['Role']} (Level {level})",
                    min_value=0.0,
                    max_value=20.0,
                    step=0.25,
                    value=st.session_state.weekly_hours.get(key, row["Hours_per_week"]),
                    key=f"number_input_{level}_{row['Role']}"
                )

def get_current_weekly_hours():
    """Returns a dictionary: (level, role) -> hours per week"""
    return st.session_state.get("weekly_hours", {})
