import streamlit as st
import pandas as pd

def render_athlete_fee_editor(athlete_levels_df):
    with st.sidebar.expander("Monthly Fee per Athlete", expanded=False):
        # Initialize session state if needed
        if "athlete_fees" not in st.session_state:
            st.session_state.athlete_fees = {}
            for _, row in athlete_levels_df.iterrows():
                level = row["Level"]
                st.session_state.athlete_fees[(level, 1)] = row["Monthly_Fee_M1"]
                st.session_state.athlete_fees[(level, 2)] = row["Monthly_Fee_M2"]
                st.session_state.athlete_fees[(level, 3)] = row["Monthly_Fee_M3"]

        for level in sorted(athlete_levels_df["Level"].unique()):
            with st.expander(f"Level {level} Fees"):
                for month in [1, 2, 3]:
                    st.session_state.athlete_fees[(level, month)] = st.number_input(
                        f"Month {month} Fee",
                        min_value=0,
                        step=50,
                        value=st.session_state.athlete_fees[(level, month)],
                        key=f"fee_input_{level}_{month}"
                    )

def get_current_athlete_fees():
    return st.session_state.get("athlete_fees", {})
