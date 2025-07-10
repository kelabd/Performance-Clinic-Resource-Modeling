# In components/athlete_counts.py

import streamlit as st

def render_athlete_counts(levels=[3, 4, 5]):
    counts = {}
    with st.sidebar.expander("Number of Athletes", expanded=False):
        for level in levels:
            key = f"athletes_{level}"
            if key not in st.session_state:
                st.session_state[key] = 1
            counts[level] = st.number_input(
                f"Level {level}",
                min_value=0,
                value=st.session_state[key],
                key=key
            )
    return counts