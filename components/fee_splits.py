from typing import List
import streamlit as st
import matplotlib.pyplot as plt

# Default fee splits per level
DEFAULT_SPLITS = {
    3: {"Executive Director": 15.0, "QB": 30.0, "Coach": 25.0, "Operations": 10.0, "Platform": 20.0},
    4: {"Executive Director": 15.0, "QB": 30.0, "Coach": 25.0, "Operations": 10.0, "Platform": 20.0},
    5: {"Executive Director": 15.0, "QB": 30.0, "Coach": 25.0, "Operations": 10.0, "Platform": 20.0}
}

def render_fee_split_editor(levels: List[int]):
    st.sidebar.markdown("### Fee Splits (by % of Monthly Fee)")

    if "fee_splits" not in st.session_state:
        st.session_state.fee_splits = {level: DEFAULT_SPLITS[level].copy() for level in levels}
    if "modified_splits" not in st.session_state:
        st.session_state.modified_splits = {level: DEFAULT_SPLITS[level].copy() for level in levels}

    for level in levels:
        with st.sidebar.expander(f"Level {level} Fee Splits"):
            for role in DEFAULT_SPLITS[level]:
                default_val = DEFAULT_SPLITS[level][role]
                current_val = st.session_state.modified_splits[level][role]
            
                # Highlight if changed from default and total is invalid
                total_pct = sum(st.session_state.modified_splits[level].values())
                is_invalid = abs(total_pct - 100.0) > 1e-6
                is_modified = abs(current_val - default_val) > 0.01
            
                if is_invalid and is_modified:
                    st.markdown(f"<span style='color:#F4864B;font-weight:bold'>{role} (%) - Level {level}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:#3E5237'>{role} (%) - Level {level}</span>", unsafe_allow_html=True)
            
                new_val = st.number_input(
                    label=" ",  # Empty label since we used custom markdown above
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    value=current_val,
                    key=f"split_input_{role}_{level}"
                )
                st.session_state.modified_splits[level][role] = new_val

            # Check if the split adds to 100%
            total_pct = sum(st.session_state.modified_splits[level].values())
            if abs(total_pct - 100.0) > 1e-6:
                st.error(f"Current split total: {total_pct:.1f}%. Adjust or normalize.")
                if st.button(f"Normalize Splits for Level {level}", key=f"normalize_{level}"):
                    locked_roles = {
                        role: val
                        for role, val in st.session_state.modified_splits[level].items()
                        if val != DEFAULT_SPLITS[level][role]
                    }
                    remaining_roles = [r for r in DEFAULT_SPLITS[level] if r not in locked_roles]

                    remaining_pct = 100.0 - sum(locked_roles.values())
                    even_split = round(remaining_pct / len(remaining_roles), 2) if remaining_roles else 0.0

                    # Update modified splits
                    for role in DEFAULT_SPLITS[level]:
                        if role in locked_roles:
                            st.session_state.fee_splits[level][role] = locked_roles[role]
                            st.session_state.modified_splits[level][role] = locked_roles[role]
                        else:
                            st.session_state.fee_splits[level][role] = even_split
                            st.session_state.modified_splits[level][role] = even_split
                    st.experimental_rerun()
            else:
                st.session_state.fee_splits[level] = st.session_state.modified_splits[level].copy()

def get_current_fee_splits():
    return st.session_state.get("fee_splits", DEFAULT_SPLITS)

def display_fee_split_charts(levels: List[int]):
    st.subheader("Fee Split Visualization")
    for level in levels:
        splits = get_current_fee_splits()[level]
        labels = list(splits.keys())
        sizes = list(splits.values())

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
