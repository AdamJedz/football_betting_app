import pandas as pd
import streamlit as st

from auth import logout, refresh_points, require_auth
from database import get_leaderboard, init_db

st.set_page_config(
    page_title="Football Betting App",
    page_icon="⚽",
    layout="wide",
)

init_db()
require_auth()
refresh_points()

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['username']}")
    st.metric("Points", st.session_state["points"])
    st.divider()
    if st.button("Logout", use_container_width=True):
        logout()

# --- Tabs ---
tab1, = st.tabs(["🏆 Leaderboard"])

with tab1:
    st.subheader("🏆 Leaderboard")

    leaderboard = get_leaderboard()

    if not leaderboard:
        st.info("No players yet.")
    else:
        MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

        df = pd.DataFrame(leaderboard, columns=["Player", "Points"])
        df.insert(0, "Rank", [MEDALS.get(i, str(i)) for i in range(1, len(df) + 1)])

        def _row_color(row):
            rank = row.name + 1  # .name is 0-based positional index after reset
            points = row["Points"]
            if points == 0:
                color = "#FF4444"
            elif rank == 1:
                color = "#FFD700"
            elif rank == 2:
                color = "#C0C0C0"
            elif rank == 3:
                color = "#CD7F32"
            else:
                return [""] * len(row)
            return [f"color: {color}; font-weight: bold"] * len(row)

        styled = df.style.apply(_row_color, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)
