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
                    placed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(username, match_id)
                )
            """)
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
            "SELECT username, outcome, amount FROM bets WHERE match_id = ? ORDER BY placed_at",
            (match_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_leaderboard() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT username, points FROM users ORDER BY points DESC"
        ).fetchall()
    return [dict(r) for r in rows]
