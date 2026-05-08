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
                points        INTEGER NOT NULL DEFAULT 100,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


def get_leaderboard() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT username, points FROM users ORDER BY points DESC"
        ).fetchall()
    return [dict(r) for r in rows]
