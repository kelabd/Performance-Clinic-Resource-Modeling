import streamlit as st
import pandas as pd

def render_hourly_rates_editor(practitioner_roles_df):
    st.sidebar.markdown("### Practitioner Hourly Rates")

    # Initialize session state
    if "hourly_rates" not in st.session_state:
        st.session_state.hourly_rates = {
            row["Role"]: row["Hourly_Rate"]
            for _, row in practitioner_roles_df.iterrows()
        }

    # Render number inputs for each role
    for _, row in practitioner_roles_df.iterrows():
        role = row["Role"]
        st.session_state.hourly_rates[role] = st.sidebar.number_input(
            f"{role}",
            min_value=0.0,
            step=5.0,
            value=float(st.session_state.hourly_rates.get(role, float(row["Hourly_Rate"]))),
            key=f"rate_input_{role}"
        )

def get_current_hourly_rates():
    """Returns a dictionary: role -> hourly rate"""
    return st.session_state.get("hourly_rates", {})
