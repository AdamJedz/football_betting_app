from datetime import timedelta

import pandas as pd
import streamlit as st

from auth import logout, refresh_points, require_auth
from database import get_leaderboard, get_user_bet, init_db, place_bet
from matches import (
    format_day_label,
    get_matches_by_day,
    is_betting_open,
    kickoff_datetime,
)

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
    st.metric("Punkty", f"{st.session_state['points']:.2f}")
    st.divider()
    if st.button("Wyloguj", use_container_width=True):
        logout()

# --- Tabs ---
tab1, tab2 = st.tabs(["🏆 Tabela", "⚽ Kolejka 1"])

# ── Tab 1: Tabela ─────────────────────────────────────────────────────────────
with tab1:
    st.subheader("🏆 Tabela")

    leaderboard = get_leaderboard()

    if not leaderboard:
        st.info("Brak graczy.")
    else:
        MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

        df = pd.DataFrame(leaderboard).rename(columns={"username": "Gracz", "points": "Punkty"})
        df.insert(0, "Miejsce", [MEDALS.get(i, str(i)) for i in range(1, len(df) + 1)])

        def _row_color(row):
            rank = row.name + 1
            points = row["Punkty"]
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

# ── Tab 2: Kolejka 1 ──────────────────────────────────────────────────────────
with tab2:
    st.subheader("⚽ Kolejka 1 — MŚ 2026")

    username = st.session_state["username"]
    matches_by_day = get_matches_by_day()
    sorted_days = sorted(matches_by_day.keys())
    day_labels = [format_day_label(d) for d in sorted_days]

    subtabs = st.tabs(day_labels)

    for subtab, day in zip(subtabs, sorted_days):
        with subtab:
            for match in matches_by_day[day]:
                betting_open = is_betting_open(match["date"], match["time"])
                existing_bet = get_user_bet(username, match["id"])
                kickoff = kickoff_datetime(match["date"], match["time"])

                with st.container(border=True):
                    col_title, col_time = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"#### {match['home']} vs {match['away']}")
                    with col_time:
                        st.markdown(f"🕐 **{match['time']}** (PL)")

                    if existing_bet:
                        c1, c2, c3 = st.columns(3)
                        c1.metric(f"🏠 {match['home']}", f"{existing_bet['home_pts']:.2f} pkt")
                        c2.metric("🤝 Remis", f"{existing_bet['draw_pts']:.2f} pkt")
                        c3.metric(f"✈️ {match['away']}", f"{existing_bet['away_pts']:.2f} pkt")
                        st.success(f"✅ Zakład złożony — łącznie **{existing_bet['total_pts']:.2f} pkt**")

                    elif not betting_open:
                        cutoff = (kickoff - timedelta(hours=1)).strftime("%H:%M")
                        st.warning(f"🔒 Zakłady zamknięte — start o {match['time']}, przyjmowaliśmy do {cutoff}")

                    elif st.session_state["points"] <= 0:
                        st.error("❌ Nie masz punktów do postawienia.")

                    else:
                        with st.form(key=f"bet_{match['id']}"):
                            c1, c2, c3 = st.columns(3)
                            home_pts = c1.number_input(
                                f"🏠 {match['home']} wygra",
                                min_value=0.0, value=0.0, step=1.0, format="%.2f",
                            )
                            draw_pts = c2.number_input(
                                "🤝 Remis",
                                min_value=0.0, value=0.0, step=1.0, format="%.2f",
                            )
                            away_pts = c3.number_input(
                                f"✈️ {match['away']} wygra",
                                min_value=0.0, value=0.0, step=1.0, format="%.2f",
                            )

                            total_to_bet = home_pts + draw_pts + away_pts
                            st.caption(
                                f"Łącznie do odjęcia: **{total_to_bet:.2f} pkt** | "
                                f"Twoje saldo: **{st.session_state['points']:.2f} pkt**"
                            )

                            submitted = st.form_submit_button(
                                "🎯 Postaw zakład", use_container_width=True
                            )

                            if submitted:
                                ok, msg = place_bet(username, match["id"], home_pts, draw_pts, away_pts)
                                if ok:
                                    st.success(msg)
                                    refresh_points()
                                    st.rerun()
                                else:
                                    st.error(msg)
