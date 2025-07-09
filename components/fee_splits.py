import streamlit as st

DEFAULT_SPLITS = {
    3: {"Executive Director": 17, "QB": 32, "Coach": 25, "Operations": 7, "Platform": 20},
    4: {"Executive Director": 17, "QB": 32, "Coach": 25, "Operations": 7, "Platform": 20},
    5: {"Executive Director": 17, "QB": 32, "Coach": 25, "Operations": 7, "Platform": 20},
}

def render_fee_split_editor(levels):
    st.sidebar.markdown("### Monthly Fee Splits by Role")
    
    if "fee_splits" not in st.session_state:
        st.session_state.fee_splits = DEFAULT_SPLITS.copy()

    for level in levels:
        with st.sidebar.expander(f"Level {level} Fee Splits"):
            total = 0
            for role in DEFAULT_SPLITS[level]:
                current = st.session_state.fee_splits[level].get(role, 0)
                updated = st.number_input(
                    f"{role} (%) - Level {level}",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    value=current,
                    key=f"split_input_{role}_{level}"
                )
                st.session_state.fee_splits[level][role] = updated
                total += updated
            st.caption(f"Total: {total}%")

def get_current_fee_splits():
    return st.session_state.get("fee_splits", DEFAULT_SPLITS)
