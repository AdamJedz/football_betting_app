import sqlite3
from pathlib import Path

import bcrypt

DB_PATH = Path("data/app.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                points        REAL    NOT NULL DEFAULT 100,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migrate bets table if old schema (home_pts/draw_pts/away_pts) is present
        try:
            conn.execute("SELECT outcome FROM bets LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("DROP TABLE IF EXISTS bets")
            conn.execute("""
                CREATE TABLE bets (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    username   TEXT    NOT NULL,
                    match_id   TEXT    NOT NULL,
                    outcome    TEXT    NOT NULL CHECK(outcome IN ('home', 'draw', 'away')),
                    amount     REAL    NOT NULL,
                    payout     REAL,
                    placed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(username, match_id)
                )
            """)
        # Add payout column if missing (migration for existing DBs)
        try:
            conn.execute("SELECT payout FROM bets LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE bets ADD COLUMN payout REAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS match_odds (
                match_id   TEXT PRIMARY KEY,
                home_odds  REAL NOT NULL,
                draw_odds  REAL NOT NULL,
                away_odds  REAL NOT NULL,
                updated_by TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS match_results (
                match_id   TEXT PRIMARY KEY,
                result     TEXT NOT NULL CHECK(result IN ('home', 'draw', 'away')),
                set_by     TEXT NOT NULL,
                set_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def get_match_odds(match_id: str) -> tuple[float, float, float] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT home_odds, draw_odds, away_odds FROM match_odds WHERE match_id = ?",
            (match_id,),
        ).fetchone()
    return (row["home_odds"], row["draw_odds"], row["away_odds"]) if row else None


def set_match_odds(
    match_id: str, home: float, draw: float, away: float, username: str
) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO match_odds (match_id, home_odds, draw_odds, away_odds, updated_by, updated_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(match_id) DO UPDATE SET
                   home_odds  = excluded.home_odds,
                   draw_odds  = excluded.draw_odds,
                   away_odds  = excluded.away_odds,
                   updated_by = excluded.updated_by,
                   updated_at = CURRENT_TIMESTAMP""",
            (match_id, round(home, 2), round(draw, 2), round(away, 2), username),
        )
        conn.commit()


def create_user(username: str, password: str, points: int = 100) -> bool:
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, points) VALUES (?, ?, ?)",
                (username, password_hash, points),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(username: str, password: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash, points FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return {"username": username, "points": row["points"]}
    return None


def get_user(username: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, points FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    return dict(row) if row else None


def update_points(username: str, delta: float) -> float:
    """Add or subtract points. Returns the new balance."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET points = ROUND(points + ?, 2) WHERE username = ?",
            (delta, username),
        )
        conn.commit()
        row = conn.execute(
            "SELECT points FROM users WHERE username = ?", (username,)
        ).fetchone()
    return row["points"] if row else 0


def upsert_bet(
    username: str,
    match_id: str,
    outcome: str,
    amount: float,
) -> tuple[bool, str]:
    """Place or update a bet. Returns (success, message)."""
    amount = round(amount, 2)

    if amount <= 0:
        return False, "Kwota musi być większa niż 0."
    if outcome not in ("home", "draw", "away"):
        return False, "Nieprawidłowy typ zakładu."

    with get_connection() as conn:
        user = conn.execute(
            "SELECT points FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not user:
            return False, "Użytkownik nie istnieje."

        current_pts = round(user["points"], 2)
        existing = conn.execute(
            "SELECT amount FROM bets WHERE username = ? AND match_id = ?",
            (username, match_id),
        ).fetchone()
        old_amount = round(existing["amount"], 2) if existing else 0.0

        # Effective balance = current + already staked on this match (will be refunded if editing)
        available = round(current_pts + old_amount, 2)
        max_allowed = available if available <= 10 else round(available * 0.5, 2)

        if amount > max_allowed:
            if available <= 10:
                return False, f"Za mało punktów. Masz dostępne {available:.2f} pkt."
            return False, (
                f"Maksymalny zakład to {max_allowed:.2f} pkt "
                f"(50% z {available:.2f} pkt)."
            )

        if existing:
            conn.execute(
                "UPDATE bets SET outcome = ?, amount = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE username = ? AND match_id = ?",
                (outcome, amount, username, match_id),
            )
            net = round(amount - old_amount, 2)
            conn.execute(
                "UPDATE users SET points = ROUND(points - ?, 2) WHERE username = ?",
                (net, username),
            )
            if net >= 0:
                msg = f"Zakład zaktualizowany! Odjęto dodatkowe {net:.2f} pkt."
            else:
                msg = f"Zakład zaktualizowany! Zwrócono {abs(net):.2f} pkt."
        else:
            conn.execute(
                "INSERT INTO bets (username, match_id, outcome, amount) VALUES (?, ?, ?, ?)",
                (username, match_id, outcome, amount),
            )
            conn.execute(
                "UPDATE users SET points = ROUND(points - ?, 2) WHERE username = ?",
                (amount, username),
            )
            msg = f"Zakład przyjęty! Odjęto {amount:.2f} pkt."

        conn.commit()

    return True, msg


def get_user_bet(username: str, match_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT outcome, amount FROM bets WHERE username = ? AND match_id = ?",
            (username, match_id),
        ).fetchone()
    return dict(row) if row else None


def get_match_bets(match_id: str) -> list[dict]:
    """All bets placed on a given match, ordered by time placed."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT username, outcome, amount, payout FROM bets WHERE match_id = ? ORDER BY placed_at",
            (match_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_match_result(match_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT result, set_by, set_at FROM match_results WHERE match_id = ?",
            (match_id,),
        ).fetchone()
    return dict(row) if row else None


def set_match_result(
    match_id: str, result: str, setter: str, odds: tuple[float, float, float]
) -> tuple[bool, str]:
    """Set or update match result. Reverts old payouts then applies new ones atomically."""
    if result not in ("home", "draw", "away"):
        return False, "Nieprawidłowy wynik."

    odds_map = {"home": odds[0], "draw": odds[1], "away": odds[2]}

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT result FROM match_results WHERE match_id = ?", (match_id,)
        ).fetchone()

        # Revert any existing payouts before applying new ones
        paid_bets = conn.execute(
            "SELECT username, payout FROM bets WHERE match_id = ? AND payout IS NOT NULL",
            (match_id,),
        ).fetchall()
        for b in paid_bets:
            conn.execute(
                "UPDATE users SET points = ROUND(points - ?, 2) WHERE username = ?",
                (b["payout"], b["username"]),
            )
        conn.execute("UPDATE bets SET payout = NULL WHERE match_id = ?", (match_id,))

        # Upsert result
        if existing:
            conn.execute(
                "UPDATE match_results SET result=?, set_by=?, set_at=CURRENT_TIMESTAMP WHERE match_id=?",
                (result, setter, match_id),
            )
        else:
            conn.execute(
                "INSERT INTO match_results (match_id, result, set_by) VALUES (?, ?, ?)",
                (match_id, result, setter),
            )

        # Pay out winning bets
        winning_bets = conn.execute(
            "SELECT id, username, amount FROM bets WHERE match_id = ? AND outcome = ?",
            (match_id, result),
        ).fetchall()
        winning_odds = odds_map[result]
        payout_count = 0
        for b in winning_bets:
            payout = round(b["amount"] * winning_odds, 2)
            conn.execute("UPDATE bets SET payout = ? WHERE id = ?", (payout, b["id"]))
            conn.execute(
                "UPDATE users SET points = ROUND(points + ?, 2) WHERE username = ?",
                (payout, b["username"]),
            )
            payout_count += 1

        conn.commit()

    action = "zaktualizowany" if existing else "zapisany"
    return True, f"Wynik {action}! Wypłacono punkty dla {payout_count} graczy."


def clear_match_result(match_id: str) -> tuple[bool, str]:
    """Remove result and reverse all payouts."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT result FROM match_results WHERE match_id = ?", (match_id,)
        ).fetchone()
        if not existing:
            return False, "Brak zapisanego wyniku."

        paid_bets = conn.execute(
            "SELECT username, payout FROM bets WHERE match_id = ? AND payout IS NOT NULL",
            (match_id,),
        ).fetchall()
        for b in paid_bets:
            conn.execute(
                "UPDATE users SET points = ROUND(points - ?, 2) WHERE username = ?",
                (b["payout"], b["username"]),
            )
        conn.execute("UPDATE bets SET payout = NULL WHERE match_id = ?", (match_id,))
        conn.execute("DELETE FROM match_results WHERE match_id = ?", (match_id,))
        conn.commit()

    return True, f"Wynik cofnięty, przywrócono punkty dla {len(paid_bets)} graczy."


def get_leaderboard() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT username, points FROM users ORDER BY points DESC"
        ).fetchall()
    return [dict(r) for r in rows]
