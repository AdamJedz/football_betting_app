import streamlit as st

from database import verify_user, get_user


def login_page() -> None:
    st.title("⚽ Football Betting App")
    st.subheader("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("Please enter your username and password.")
            return
        user = verify_user(username, password)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["username"] = user["username"]
            st.session_state["points"] = user["points"]
            st.rerun()
        else:
            st.error("Invalid username or password.")


def logout() -> None:
    for key in ["authenticated", "username", "points"]:
        st.session_state.pop(key, None)
    st.rerun()


def require_auth() -> None:
    """Call at the top of every page. Stops rendering and shows login if not authenticated."""
    if not st.session_state.get("authenticated"):
        login_page()
        st.stop()


def refresh_points() -> None:
    """Sync points from DB into session state (call after any points change)."""
    user = get_user(st.session_state["username"])
    if user:
        st.session_state["points"] = user["points"]
