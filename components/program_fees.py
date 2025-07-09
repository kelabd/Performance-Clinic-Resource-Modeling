import streamlit as st
import pandas as pd

DEFAULT_PROGRAM_FEES = {
    3: 1500,
    4: 7500,
    5: 15000,
}

def render_program_fee_editor(athlete_levels_df):
    st.sidebar.markdown("### Program Fee per Athlete")

    if "program_fees" not in st.session_state:
        st.session_state.program_fees = {}
        for level in athlete_levels_df["Level"]:
            st.session_state.program_fees[level] = DEFAULT_PROGRAM_FEES.get(level, 1000)

    for level in sorted(athlete_levels_df["Level"].unique()):
        with st.sidebar.expander(f"Level {level} Fee"):
            st.session_state.program_fees[level] = st.number_input(
                f"Program Fee (Level {level})",
                min_value=0,
                step=100,
                value=st.session_state.program_fees[level],
                key=f"program_fee_input_{level}"
            )

def get_current_program_fees():
    return st.session_state.get("program_fees", DEFAULT_PROGRAM_FEES)
