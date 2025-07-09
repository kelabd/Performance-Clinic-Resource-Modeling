import streamlit as st
import matplotlib.pyplot as plt

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
            total = 0
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
                total += updated

            # Warning if not 100%
            if abs(total - 100.0) > 0.1:
                st.warning(f"Total is {total:.1f}%. Adjust splits or normalize.")

            # Normalize button
            if st.button(f"Normalize Level {level} Splits", key=f"normalize_btn_{level}"):
                _normalize_splits(level)

def _normalize_splits(level):
    """Rescale values so that they sum to 100%."""
    splits = st.session_state.fee_splits[level]
    total = sum(splits.values())
    if total == 0:
        return
    for role in splits:
        splits[role] = round((splits[role] / total) * 100, 2)
    st.session_state.fee_splits[level] = splits
    st.success(f"Splits for Level {level} normalized.")

def display_fee_split_charts(levels):
    st.subheader("Fee Split Visualization by Level")
    for level in levels:
        splits = st.session_state.fee_splits.get(level, DEFAULT_SPLITS)
        labels = list(splits.keys())
        sizes = list(splits.values())

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

def get_current_fee_splits():
    return st.session_state.get("fee_splits", {})
