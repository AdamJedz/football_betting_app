from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from auth import logout, refresh_points, require_auth
from database import (
    clear_match_result,
    get_leaderboard,
    get_match_bets,
    get_match_odds,
    get_match_result,
    get_user_bet,
    init_db,
    set_match_odds,
    set_match_result,
    upsert_bet,
)
from matches import (
    can_set_result,
    flag,
    format_day_label,
    get_matches_by_day,
    is_betting_open,
    kickoff_datetime,
    outcome_label,
    outcome_opts,
    result_unlock_time,
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

        st.dataframe(df.style.apply(_row_color, axis=1), use_container_width=True, hide_index=True)

# ── Tab 2: Kolejka 1 ──────────────────────────────────────────────────────────
with tab2:
    st.subheader("⚽ Kolejka 1 — MŚ 2026")

    username = st.session_state["username"]
    matches_by_day = get_matches_by_day()
    sorted_days = sorted(matches_by_day.keys())

    subtabs = st.tabs([format_day_label(d) for d in sorted_days])

    for subtab, day in zip(subtabs, sorted_days):
        with subtab:
            for match in matches_by_day[day]:
                betting_open  = is_betting_open(match["date"], match["time"])
                existing_bet  = get_user_bet(username, match["id"])
                all_bets      = get_match_bets(match["id"])
                kickoff       = kickoff_datetime(match["date"], match["time"])
                cutoff_time   = (kickoff - timedelta(hours=1)).strftime("%H:%M")

                # Odds: DB value overrides the static default
                odds = get_match_odds(match["id"]) or match["odds"]

                current_pts = st.session_state["points"]
                old_amount  = existing_bet["amount"] if existing_bet else 0.0
                available   = round(current_pts + old_amount, 2)
                max_allowed = available if available <= 10 else round(available * 0.5, 2)

                with st.container(border=True):

                    # ── Header: Team1 (odds) — Remis (odds) — Team2 (odds) ────
                    col_title, col_time = st.columns([4, 1])
                    with col_title:
                        st.markdown(
                            f"#### {flag(match['home'])} {match['home']} ({odds[0]:.2f})"
                            f" — Remis ({odds[1]:.2f}) —"
                            f" {flag(match['away'])} {match['away']} ({odds[2]:.2f})"
                        )
                    with col_time:
                        st.markdown(f"🕐 **{match['time']}**")

                    # ── Other users' bets ─────────────────────────────────────
                    other_bets = [b for b in all_bets if b["username"] != username]
                    with st.expander(f"👥 Zakłady graczy ({len(other_bets)})"):
                        if other_bets:
                            for bet in other_bets:
                                st.write(
                                    f"**{bet['username']}**: "
                                    f"{outcome_label(bet['outcome'], match)} "
                                    f"— {bet['amount']:.2f} pkt"
                                )
                        else:
                            st.caption("Nikt jeszcze nie postawił zakładu.")

                    # ── Existing bet ──────────────────────────────────────────
                    if existing_bet:
                        st.info(
                            f"Twój zakład: **{outcome_label(existing_bet['outcome'], match)}**"
                            f" — **{existing_bet['amount']:.2f} pkt**"
                        )
                        if betting_open:
                            with st.expander("✏️ Edytuj zakład"):
                                opts = outcome_opts(match, odds)
                                with st.form(key=f"bet_{match['id']}"):
                                    new_outcome = st.radio(
                                        "Typ zakładu",
                                        options=list(opts.keys()),
                                        format_func=lambda k: opts[k],
                                        index=list(opts.keys()).index(existing_bet["outcome"]),
                                        horizontal=True,
                                    )
                                    new_amount = st.number_input(
                                        "Kwota (pkt)",
                                        min_value=0.01, max_value=float(max_allowed),
                                        value=float(existing_bet["amount"]),
                                        step=0.5, format="%.2f",
                                    )
                                    st.caption(
                                        f"Maks: **{max_allowed:.2f} pkt** "
                                        f"({'całe saldo' if available <= 10 else '50% salda'})"
                                        f" | Zakłady do **{cutoff_time}**"
                                    )
                                    if st.form_submit_button("💾 Zapisz zmiany", use_container_width=True):
                                        ok, msg = upsert_bet(username, match["id"], new_outcome, new_amount)
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
                        st.warning(f"🔒 Zakłady zamknięte — przyjmowaliśmy do **{cutoff_time}**")

                    # ── No points ────────────────────────────────────────────
                    elif current_pts <= 0:
                        st.error("❌ Nie masz punktów do postawienia.")

                    # ── New bet form ──────────────────────────────────────────
                    else:
                        opts = outcome_opts(match, odds)
                        with st.form(key=f"bet_{match['id']}"):
                            selected_outcome = st.radio(
                                "Typ zakładu",
                                options=list(opts.keys()),
                                format_func=lambda k: opts[k],
                                horizontal=True,
                            )
                            amount = st.number_input(
                                "Kwota (pkt)",
                                min_value=0.01, max_value=float(max_allowed),
                                value=1.0, step=0.5, format="%.2f",
                            )
                            st.caption(
                                f"Maks: **{max_allowed:.2f} pkt** "
                                f"({'całe saldo' if current_pts <= 10 else '50% salda'})"
                                f" | Zakłady do **{cutoff_time}**"
                            )
                            if st.form_submit_button("🎯 Postaw zakład", use_container_width=True):
                                ok, msg = upsert_bet(username, match["id"], selected_outcome, amount)
                                if ok:
                                    st.success(msg)
                                    refresh_points()
                                    st.rerun()
                                else:
                                    st.error(msg)

                    # ── Odds editor (any user) ────────────────────────────────
                    with st.expander("⚙️ Ustaw kursy"):
                        with st.form(key=f"odds_{match['id']}"):
                            c1, c2, c3 = st.columns(3)
                            new_home = c1.number_input(
                                f"{flag(match['home'])} {match['home']}",
                                min_value=1.01, value=float(odds[0]), step=0.05, format="%.2f",
                            )
                            new_draw = c2.number_input(
                                "Remis",
                                min_value=1.01, value=float(odds[1]), step=0.05, format="%.2f",
                            )
                            new_away = c3.number_input(
                                f"{flag(match['away'])} {match['away']}",
                                min_value=1.01, value=float(odds[2]), step=0.05, format="%.2f",
                            )
                            if st.form_submit_button("💾 Zapisz kursy", use_container_width=True):
                                set_match_odds(match["id"], new_home, new_draw, new_away, username)
                                st.success("Kursy zaktualizowane!")
                                st.rerun()

                    # ── Kto zwyciężył ─────────────────────────────────────────
                    match_result = get_match_result(match["id"])
                    user_can_set = can_set_result(match["date"], match["time"], username)

                    with st.expander("🏆 Kto zwyciężył?"):
                        if match_result:
                            st.success(
                                f"Wynik: **{outcome_label(match_result['result'], match)}** "
                                f"— ustawił {match_result['set_by']}"
                            )
                            # Payout summary
                            paid = [b for b in all_bets if b.get("payout")]
                            if paid:
                                st.markdown("**Wypłaty:**")
                                for b in paid:
                                    st.write(
                                        f"  {flag(match['home'] if b['outcome']=='home' else match['away']) if b['outcome']!='draw' else '🤝'} "
                                        f"**{b['username']}**: +{b['payout']:.2f} pkt"
                                    )

                        if user_can_set:
                            r_opts = outcome_opts(match, odds)
                            with st.form(key=f"result_{match['id']}"):
                                selected_result = st.radio(
                                    "Wynik meczu",
                                    options=list(r_opts.keys()),
                                    format_func=lambda k: r_opts[k],
                                    index=(
                                        list(r_opts.keys()).index(match_result["result"])
                                        if match_result else 0
                                    ),
                                    horizontal=True,
                                )
                                col_save, col_revert = st.columns(2)
                                save = col_save.form_submit_button(
                                    "✅ Zapisz wynik", use_container_width=True
                                )
                                revert = col_revert.form_submit_button(
                                    "🔄 Cofnij wynik",
                                    use_container_width=True,
                                    disabled=not match_result,
                                )

                            if save:
                                ok, msg = set_match_result(match["id"], selected_result, username, odds)
                                if ok:
                                    st.success(msg)
                                    refresh_points()
                                    st.rerun()
                                else:
                                    st.error(msg)

                            if revert:
                                ok, msg = clear_match_result(match["id"])
                                if ok:
                                    st.success(msg)
                                    refresh_points()
                                    st.rerun()
                                else:
                                    st.error(msg)

                        elif not match_result:
                            unlock = result_unlock_time(match["date"], match["time"])
                            now_w = datetime.now(ZoneInfo("Europe/Warsaw"))
                            if now_w < kickoff:
                                st.caption("⏳ Mecz jeszcze się nie rozpoczął.")
                            else:
                                mins = max(0, int((unlock - now_w).total_seconds() / 60))
                                st.caption(f"⏳ Dostępne za ~{mins} min (2h po starcie)")
