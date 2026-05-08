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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL,
                match_id   TEXT    NOT NULL,
                home_pts   REAL    NOT NULL DEFAULT 0,
                draw_pts   REAL    NOT NULL DEFAULT 0,
                away_pts   REAL    NOT NULL DEFAULT 0,
                total_pts  REAL    NOT NULL DEFAULT 0,
                placed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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


def update_points(username: str, delta: int) -> int:
    """Add or subtract points. Returns the new balance."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET points = points + ? WHERE username = ?",
            (delta, username),
        )
        conn.commit()
        row = conn.execute(
            "SELECT points FROM users WHERE username = ?", (username,)
        ).fetchone()
    return row["points"] if row else 0


def place_bet(
    username: str,
    match_id: str,
    home_pts: float,
    draw_pts: float,
    away_pts: float,
) -> tuple[bool, str]:
    home_pts = round(home_pts, 2)
    draw_pts = round(draw_pts, 2)
    away_pts = round(away_pts, 2)
    total = round(home_pts + draw_pts + away_pts, 2)

    if total <= 0:
        return False, "Podaj punkty do postawienia (łącznie > 0)."

    with get_connection() as conn:
        user = conn.execute(
            "SELECT points FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not user:
            return False, "Użytkownik nie istnieje."
        if round(user["points"], 2) < total:
            return False, f"Za mało punktów. Masz {user['points']:.2f} pkt, potrzebujesz {total:.2f} pkt."

        existing = conn.execute(
            "SELECT id FROM bets WHERE username = ? AND match_id = ?", (username, match_id)
        ).fetchone()
        if existing:
            return False, "Zakład na ten mecz już został złożony."

        conn.execute(
            "INSERT INTO bets (username, match_id, home_pts, draw_pts, away_pts, total_pts) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (username, match_id, home_pts, draw_pts, away_pts, total),
        )
        conn.execute(
            "UPDATE users SET points = ROUND(points - ?, 2) WHERE username = ?",
            (total, username),
        )
        conn.commit()

    return True, f"Zakład przyjęty! Odjęto {total:.2f} pkt."


def get_user_bet(username: str, match_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT home_pts, draw_pts, away_pts, total_pts FROM bets "
            "WHERE username = ? AND match_id = ?",
            (username, match_id),
        ).fetchone()
    return dict(row) if row else None


def get_leaderboard() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT username, points FROM users ORDER BY points DESC"
        ).fetchall()
    return [dict(r) for r in rows]
