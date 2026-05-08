from datetime import timedelta

import pandas as pd
import streamlit as st

from auth import logout, refresh_points, require_auth
from database import get_leaderboard, get_match_bets, get_user_bet, init_db, upsert_bet
from matches import (
    flag,
    format_day_label,
    get_matches_by_day,
    is_betting_open,
    kickoff_datetime,
    outcome_label,
    team_label,
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
                all_bets = get_match_bets(match["id"])

                kickoff = kickoff_datetime(match["date"], match["time"])
                cutoff_time = (kickoff - timedelta(hours=1)).strftime("%H:%M")

                # Current available points for max-bet calculation
                current_pts = st.session_state["points"]
                old_amount = existing_bet["amount"] if existing_bet else 0.0
                available = round(current_pts + old_amount, 2)
                max_allowed = available if available <= 10 else round(available * 0.5, 2)

                with st.container(border=True):
                    # Header row
                    o = match["odds"]
                    col_title, col_time = st.columns([4, 1])
                    with col_title:
                        st.markdown(
                            f"#### {team_label(match['home'], o[0])}"
                            f" &nbsp;vs&nbsp; "
                            f"{team_label(match['away'], o[2])}"
                            f" &nbsp;·&nbsp; 🤝 Remis ({o[1]:.2f})"
                        )
                    with col_time:
                        st.markdown(f"🕐 **{match['time']}**")

                    # ── Other users' bets (always visible) ───────────────────
                    other_bets = [b for b in all_bets if b["username"] != username]
                    with st.expander(f"👥 Zakłady graczy ({len(other_bets)})"):
                        if other_bets:
                            for bet in other_bets:
                                label = outcome_label(bet["outcome"], match)
                                st.write(f"**{bet['username']}**: {label} — {bet['amount']:.2f} pkt")
                        else:
                            st.caption("Nikt jeszcze nie postawił zakładu.")

                    # ── Existing bet ──────────────────────────────────────────
                    if existing_bet:
                        label = outcome_label(existing_bet["outcome"], match)
                        st.info(
                            f"Twój zakład: **{label}** — **{existing_bet['amount']:.2f} pkt**"
                        )

                        if betting_open:
                            with st.expander("✏️ Edytuj zakład"):
                                _outcome_opts = {
                                    "home":  outcome_label("home", match),
                                    "draw":  outcome_label("draw", match),
                                    "away":  outcome_label("away", match),
                                }
                                with st.form(key=f"bet_{match['id']}"):
                                    new_outcome = st.radio(
                                        "Typ zakładu",
                                        options=list(_outcome_opts.keys()),
                                        format_func=lambda k: _outcome_opts[k],
                                        index=list(_outcome_opts.keys()).index(
                                            existing_bet["outcome"]
                                        ),
                                        horizontal=True,
                                    )
                                    new_amount = st.number_input(
                                        "Kwota (pkt)",
                                        min_value=0.01,
                                        max_value=float(max_allowed),
                                        value=float(existing_bet["amount"]),
                                        step=0.5,
                                        format="%.2f",
                                    )
                                    st.caption(
                                        f"Maks. zakład: **{max_allowed:.2f} pkt** "
                                        f"({'całe saldo' if available <= 10 else '50% salda'})"
                                        f" | Zakłady przyjmujemy do **{cutoff_time}**"
                                    )
                                    if st.form_submit_button(
                                        "💾 Zapisz zmiany", use_container_width=True
                                    ):
                                        ok, msg = upsert_bet(
                                            username, match["id"], new_outcome, new_amount
                                        )
                                        if ok:
                                            st.success(msg)
                                            refresh_points()
                                            st.rerun()
                                        else:
                                            st.error(msg)
                        else:
                            st.caption(f"🔒 Zakłady zamknięte (przyjmowaliśmy do {cutoff_time})")

                    # ── Betting closed, no bet ────────────────────────────────
                    elif not betting_open:
                        st.warning(
                            f"🔒 Zakłady zamknięte — przyjmowaliśmy do **{cutoff_time}**"
                        )

                    # ── No points ────────────────────────────────────────────
                    elif current_pts <= 0:
                        st.error("❌ Nie masz punktów do postawienia.")

                    # ── New bet form ──────────────────────────────────────────
                    else:
                        _outcome_opts = {
                            "home": f"🏠 {match['home']} wygra",
                            "draw": "🤝 Remis",
                            "away": f"✈️ {match['away']} wygra",
                        }
                        with st.form(key=f"bet_{match['id']}"):
                            selected_outcome = st.radio(
                                "Typ zakładu",
                                options=list(_outcome_opts.keys()),
                                format_func=lambda k: _outcome_opts[k],
                                horizontal=True,
                            )
                            amount = st.number_input(
                                "Kwota (pkt)",
                                min_value=0.01,
                                max_value=float(max_allowed),
                                value=1.0,
                                step=0.5,
                                format="%.2f",
                            )
                            st.caption(
                                f"Maks. zakład: **{max_allowed:.2f} pkt** "
                                f"({'całe saldo' if current_pts <= 10 else '50% salda'})"
                                f" | Zakłady przyjmujemy do **{cutoff_time}**"
                            )
                            if st.form_submit_button(
                                "🎯 Postaw zakład", use_container_width=True
                            ):
                                ok, msg = upsert_bet(
                                    username, match["id"], selected_outcome, amount
                                )
                                if ok:
                                    st.success(msg)
                                    refresh_points()
                                    st.rerun()
                                else:
                                    st.error(msg)

