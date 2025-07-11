from typing import List
import streamlit as st
import matplotlib.pyplot as plt

# Default fee splits per level
DEFAULT_SPLITS = {
    3: {"Executive Director": 15.0, "QB": 30.0, "Coach": 25.0, "Operations": 10.0, "Platform": 20.0},
    4: {"Executive Director": 15.0, "QB": 30.0, "Coach": 25.0, "Operations": 10.0, "Platform": 20.0},
    5: {"Executive Director": 15.0, "QB": 30.0, "Coach": 25.0, "Operations": 10.0, "Platform": 20.0}
}

# Optional: Cascaid-branded colors
ROLE_COLORS = {
    "Executive Director": "#025E68",
    "QB": "#6E8072",
    "Coach": "#3E5237",
    "Operations": "#B8B5C6",
    "Platform": "#F4864B"
}

def render_fee_split_editor(levels: List[int]):
    st.sidebar.markdown("### Fee Splits")

    if "fee_splits" not in st.session_state:
        st.session_state.fee_splits = {level: DEFAULT_SPLITS[level].copy() for level in levels}
    if "modified_splits" not in st.session_state:
        st.session_state.modified_splits = {level: DEFAULT_SPLITS[level].copy() for level in levels}
    if "normalize_requested_level" not in st.session_state:
        st.session_state.normalize_requested_level = None
    if "pending_normalization" not in st.session_state:
        st.session_state.pending_normalization = False

    # --- UI rendering phase ---
    for level in levels:
        with st.sidebar.expander(f"Level {level} Fee Splits"):
            for role in DEFAULT_SPLITS[level]:
                default_val = DEFAULT_SPLITS[level][role]
                current_val = st.session_state.modified_splits[level][role]

                total_pct = sum(st.session_state.modified_splits[level].values())
                is_invalid = abs(total_pct - 100.0) > 1e-6
                is_modified = abs(current_val - default_val) > 0.01

                if is_invalid and is_modified:
                    st.markdown(f"<span style='color:#F4864B;font-weight:bold'>{role} (%) - Level {level}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:#3E5237'>{role} (%) - Level {level}</span>", unsafe_allow_html=True)

                new_val = st.number_input(
                    label=f"{role} (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    value=current_val,
                    key=f"split_input_{role}_{level}",
                    label_visibility="collapsed"
                )
                st.session_state.modified_splits[level][role] = new_val

            total_pct = sum(st.session_state.modified_splits[level].values())
            if abs(total_pct - 100.0) > 1e-6:
                st.error(f"Current split total: {total_pct:.1f}%. Adjust or normalize.")
                if st.button(f"Normalize Splits for Level {level}", key=f"normalize_{level}"):
                    st.session_state.normalize_requested_level = level
                    st.session_state.pending_normalization = True
            else:
                st.session_state.fee_splits[level] = st.session_state.modified_splits[level].copy()

    # --- Safe normalization execution phase ---
    if st.session_state.pending_normalization and st.session_state.normalize_requested_level is not None:
        level = st.session_state.normalize_requested_level

        locked_roles = {
            role: val
            for role, val in st.session_state.modified_splits[level].items()
            if abs(val - DEFAULT_SPLITS[level][role]) > 0.01
        }
        remaining_roles = [r for r in DEFAULT_SPLITS[level] if r not in locked_roles]

        if not remaining_roles:
            st.warning("All roles have been edited. Please manually ensure the total adds to 100%.")
        else:
            remaining_pct = 100.0 - sum(locked_roles.values())
            even_split = round(remaining_pct / len(remaining_roles), 2)

            for role in DEFAULT_SPLITS[level]:
                if role in locked_roles:
                    new_val = locked_roles[role]
                else:
                    new_val = even_split
                st.session_state.fee_splits[level][role] = new_val
                st.session_state.modified_splits[level][role] = new_val

        st.session_state.normalize_requested_level = None
        st.session_state.pending_normalization = False
        st.session_state["trigger_fee_split_rerun"] = True


def get_current_fee_splits():
    return st.session_state.get("fee_splits", DEFAULT_SPLITS)

def display_fee_split_charts(levels: List[int]):
    st.subheader("Fee Split Visualization")
    for level in levels:
        splits = get_current_fee_splits()[level]
        labels = list(splits.keys())
        sizes = list(splits.values())
        colors = [ROLE_COLORS.get(label, "#999999") for label in labels]

        with st.expander(f"Level {level} Fee Split Chart", expanded=True):
            fig, ax = plt.subplots(figsize=(3, 3), facecolor='none')
            ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig, transparent=True)

