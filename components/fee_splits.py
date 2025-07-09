import streamlit as st

# Default splits for each role
DEFAULT_SPLITS = {
    "Executive Director": 17.0,
    "QB": 32.0,
    "Coach": 25.0,
    "Operations": 7.0,
    "Platform": 20.0,
}

def render_fee_split_editor(levels):
    st.sidebar.markdown("### Monthly Fee Splits")

    if "fee_splits" not in st.session_state:
        st.session_state.fee_splits = {
            level: DEFAULT_SPLITS.copy() for level in levels
        }

    for level in levels:
        with st.sidebar.expander(f"Level {level} Fee Splits", expanded=False):
            for role in DEFAULT_SPLITS:
                current_value = float(st.session_state.fee_splits[level].get(role, DEFAULT_SPLITS[role]))
                updated = st.number_input(
                    f"{role} (%) - Level {level}",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    value=current_value,
                    key=f"split_input_{role}_{level}"
                )
                st.session_state.fee_splits[level][role] = updated

def get_current_fee_splits():
    return st.session_state.get("fee_splits", {})
