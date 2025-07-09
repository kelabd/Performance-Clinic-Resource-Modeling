import streamlit as st
import pandas as pd

def render_weekly_hours_editor(assignments_df):
    with st.sidebar.expander("Weekly Hours per Role", expanded=False):

        # Initialize editable hours state
        if "weekly_hours" not in st.session_state:
            st.session_state.weekly_hours = {}
            for _, row in assignments_df.iterrows():
                key = (row["Level"], row["Role"])
                st.session_state.weekly_hours[key] = row["Hours_per_week"]

        # Show flat list of inputs for (level, role) pairs
        for _, row in assignments_df.iterrows():
            key = (row["Level"], row["Role"])
            current_val = st.session_state.weekly_hours.get(key, row["Hours_per_week"])
            st.session_state.weekly_hours[key] = st.number_input(
                label=f"Level {row['Level']} – {row['Role']}",
                min_value=0.0,
                max_value=20.0,
                step=0.25,
                value=current_val,
                key=f"number_input_{row['Level']}_{row['Role']}"
            )

def get_current_weekly_hours():
    """Returns a dictionary: (level, role) -> hours per week"""
    return st.session_state.get("weekly_hours", {})