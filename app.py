import streamlit as st

from auth import require_auth, logout, refresh_points
from database import init_db, get_leaderboard

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

# --- Main content ---
st.title("⚽ Football Betting App")
st.write(f"Welcome back, **{st.session_state['username']}**!")

st.divider()

# Leaderboard
st.subheader("🏆 Leaderboard")
leaderboard = get_leaderboard()
for i, user in enumerate(leaderboard, start=1):
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
    col1, col2 = st.columns([3, 1])
    with col1:
        name = f"**{user['username']}**" if user["username"] == st.session_state["username"] else user["username"]
        st.write(f"{medal} {name}")
    with col2:
        st.write(f"**{user['points']}** pts")

st.divider()
st.info("Betting features coming soon!")
