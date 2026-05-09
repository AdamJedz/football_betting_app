import os
from contextlib import contextmanager

import bcrypt
import psycopg2
import psycopg2.extras
import psycopg2.pool

# Streamlit is optional — not available when running init_users.py directly
try:
    import streamlit as st
    _HAS_ST = True
    _secrets = st.secrets
except Exception:
    st = None  # type: ignore
    _HAS_ST = False
    _secrets = {}


# ── URL ────────────────────────────────────────────────────────────────────────

def _get_url() -> str:
    url = (
        (getattr(_secrets, "get", lambda k, d=None: d)("DATABASE_URL"))
        or os.environ.get("DATABASE_URL")
    )
    if not url:
        raise RuntimeError(
            "DATABASE_URL not set. Add it to .streamlit/secrets.toml or environment."
        )
    return url


# ── Connection pool (Streamlit) / direct connection (scripts) ─────────────────

if _HAS_ST:
    @st.cache_resource
    def _pool() -> psycopg2.pool.ThreadedConnectionPool:
        """One pool shared across all Streamlit sessions — created once."""
        return psycopg2.pool.ThreadedConnectionPool(
            1, 10, _get_url(), cursor_factory=psycopg2.extras.RealDictCursor
        )

    @contextmanager
    def get_connection():
        pool = _pool()
        conn = pool.getconn()
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            # Return connection in a clean state
            if not conn.closed:
                try:
                    conn.rollback()  # no-op if already committed
                except Exception:
                    pass
            pool.putconn(conn)

    def _clear_caches() -> None:
        st.cache_data.clear()

else:
    @contextmanager
    def get_connection():
        conn = psycopg2.connect(
            _get_url(), cursor_factory=psycopg2.extras.RealDictCursor
        )
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _clear_caches() -> None:
        pass


# ── Cache decorator (no-op outside Streamlit) ─────────────────────────────────

def _cached(ttl: int = 30):
    """Apply st.cache_data(ttl=ttl) in Streamlit; identity decorator otherwise."""
    if _HAS_ST:
        return st.cache_data(ttl=ttl)
    return lambda f: f


# ── Schema init (runs once per process) ───────────────────────────────────────

_db_initialized = False


def init_db() -> None:
    global _db_initialized
    if _db_initialized:
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            SERIAL PRIMARY KEY,
                    username      TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    points        REAL NOT NULL DEFAULT 100,
                    created_at    TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bets (
                    id         SERIAL PRIMARY KEY,
                    username   TEXT NOT NULL,
                    match_id   TEXT NOT NULL,
                    outcome    TEXT NOT NULL CHECK(outcome IN ('home', 'draw', 'away')),
                    amount     REAL NOT NULL,
                    payout     REAL,
                    placed_at  TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(username, match_id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS match_odds (
                    match_id   TEXT PRIMARY KEY,
                    home_odds  REAL NOT NULL,
                    draw_odds  REAL NOT NULL,
                    away_odds  REAL NOT NULL,
                    updated_by TEXT,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS match_results (
                    match_id TEXT PRIMARY KEY,
                    result   TEXT NOT NULL CHECK(result IN ('home', 'draw', 'away')),
                    set_by   TEXT NOT NULL,
                    set_at   TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id          SERIAL PRIMARY KEY,
                    action_at   TIMESTAMP DEFAULT NOW(),
                    action_type TEXT NOT NULL,
                    username    TEXT NOT NULL,
                    details     TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS points_snapshots (
                    id          SERIAL PRIMARY KEY,
                    username    TEXT NOT NULL,
                    points      REAL NOT NULL,
                    match_id    TEXT,
                    recorded_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
    _db_initialized = True


# ── Internal helpers ───────────────────────────────────────────────────────────

def _log(cur, username: str, action_type: str, details: str) -> None:
    cur.execute(
        "INSERT INTO audit_log (username, action_type, details) VALUES (%s, %s, %s)",
        (username, action_type, details),
    )


def _snapshot(cur, match_id: str) -> None:
    cur.execute("SELECT username, points FROM users")
    users = cur.fetchall()
    cur.executemany(
        "INSERT INTO points_snapshots (username, points, match_id) VALUES (%s, %s, %s)",
        [(u["username"], round(u["points"], 2), match_id) for u in users],
    )


# ── Odds ───────────────────────────────────────────────────────────────────────

@_cached(ttl=30)
def get_match_odds(match_id: str) -> tuple[float, float, float] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT home_odds, draw_odds, away_odds FROM match_odds WHERE match_id = %s",
                (match_id,),
            )
            row = cur.fetchone()
    return (row["home_odds"], row["draw_odds"], row["away_odds"]) if row else None


def set_match_odds(
    match_id: str, home: float, draw: float, away: float, username: str
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO match_odds (match_id, home_odds, draw_odds, away_odds, updated_by, updated_at)
                   VALUES (%s, %s, %s, %s, %s, NOW())
                   ON CONFLICT (match_id) DO UPDATE SET
                       home_odds  = EXCLUDED.home_odds,
                       draw_odds  = EXCLUDED.draw_odds,
                       away_odds  = EXCLUDED.away_odds,
                       updated_by = EXCLUDED.updated_by,
                       updated_at = NOW()""",
                (match_id, round(home, 2), round(draw, 2), round(away, 2), username),
            )
            _log(cur, username, "kursy",
                 f"{match_id}: {home:.2f} / {draw:.2f} / {away:.2f}")
        conn.commit()
    _clear_caches()


# ── Users ──────────────────────────────────────────────────────────────────────

def create_user(username: str, password: str, points: int = 100) -> bool:
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash, points) VALUES (%s, %s, %s)",
                    (username, password_hash, points),
                )
            conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        return False


def verify_user(username: str, password: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash, points FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return {"username": username, "points": row["points"]}
    return None


@_cached(ttl=30)
def get_user(username: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT username, points FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
    return dict(row) if row else None


def update_points(username: str, delta: float) -> float:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET points = ROUND((points + %s)::numeric, 2) WHERE username = %s",
                (delta, username),
            )
            cur.execute("SELECT points FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
        conn.commit()
    _clear_caches()
    return row["points"] if row else 0


# ── Bets ───────────────────────────────────────────────────────────────────────

def upsert_bet(
    username: str,
    match_id: str,
    outcome: str,
    amount: float,
) -> tuple[bool, str]:
    amount = round(amount, 2)

    if amount <= 0:
        return False, "Kwota musi być większa niż 0."
    if outcome not in ("home", "draw", "away"):
        return False, "Nieprawidłowy typ zakładu."

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT points FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if not user:
                return False, "Użytkownik nie istnieje."

            current_pts = round(user["points"], 2)
            cur.execute(
                "SELECT amount FROM bets WHERE username = %s AND match_id = %s",
                (username, match_id),
            )
            existing = cur.fetchone()
            old_amount = round(existing["amount"], 2) if existing else 0.0

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
                cur.execute(
                    "UPDATE bets SET outcome = %s, amount = %s, updated_at = NOW() "
                    "WHERE username = %s AND match_id = %s",
                    (outcome, amount, username, match_id),
                )
                net = round(amount - old_amount, 2)
                cur.execute(
                    "UPDATE users SET points = ROUND((points - %s)::numeric, 2) WHERE username = %s",
                    (net, username),
                )
                _log(cur, username, "edycja zakładu",
                     f"{match_id}: {outcome}, {amount:.2f} pkt (poprzednio {old_amount:.2f} pkt)")
                msg = (f"Zakład zaktualizowany! Odjęto dodatkowe {net:.2f} pkt."
                       if net >= 0 else
                       f"Zakład zaktualizowany! Zwrócono {abs(net):.2f} pkt.")
            else:
                cur.execute(
                    "INSERT INTO bets (username, match_id, outcome, amount) VALUES (%s, %s, %s, %s)",
                    (username, match_id, outcome, amount),
                )
                cur.execute(
                    "UPDATE users SET points = ROUND((points - %s)::numeric, 2) WHERE username = %s",
                    (amount, username),
                )
                _log(cur, username, "zakład",
                     f"{match_id}: {outcome}, {amount:.2f} pkt")
                msg = f"Zakład przyjęty! Odjęto {amount:.2f} pkt."

        conn.commit()
    _clear_caches()
    return True, msg


@_cached(ttl=30)
def get_user_bet(username: str, match_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT outcome, amount FROM bets WHERE username = %s AND match_id = %s",
                (username, match_id),
            )
            row = cur.fetchone()
    return dict(row) if row else None


@_cached(ttl=30)
def get_match_bets(match_id: str) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT username, outcome, amount, payout FROM bets "
                "WHERE match_id = %s ORDER BY placed_at",
                (match_id,),
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]


# ── Results ────────────────────────────────────────────────────────────────────

@_cached(ttl=30)
def get_match_result(match_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT result, set_by, set_at FROM match_results WHERE match_id = %s",
                (match_id,),
            )
            row = cur.fetchone()
    return dict(row) if row else None


def set_match_result(
    match_id: str, result: str, setter: str, odds: tuple[float, float, float]
) -> tuple[bool, str]:
    if result not in ("home", "draw", "away"):
        return False, "Nieprawidłowy wynik."

    odds_map = {"home": odds[0], "draw": odds[1], "away": odds[2]}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT result FROM match_results WHERE match_id = %s", (match_id,)
            )
            existing = cur.fetchone()

            # Revert any existing payouts
            cur.execute(
                "SELECT username, payout FROM bets "
                "WHERE match_id = %s AND payout IS NOT NULL",
                (match_id,),
            )
            paid_bets = cur.fetchall()
            for b in paid_bets:
                cur.execute(
                    "UPDATE users SET points = ROUND((points - %s)::numeric, 2) WHERE username = %s",
                    (b["payout"], b["username"]),
                )
            cur.execute("UPDATE bets SET payout = NULL WHERE match_id = %s", (match_id,))

            # Upsert result
            if existing:
                cur.execute(
                    "UPDATE match_results SET result=%s, set_by=%s, set_at=NOW() "
                    "WHERE match_id=%s",
                    (result, setter, match_id),
                )
            else:
                cur.execute(
                    "INSERT INTO match_results (match_id, result, set_by) VALUES (%s, %s, %s)",
                    (match_id, result, setter),
                )

            # Pay out winning bets
            cur.execute(
                "SELECT id, username, amount FROM bets "
                "WHERE match_id = %s AND outcome = %s",
                (match_id, result),
            )
            winning_bets = cur.fetchall()
            winning_odds = odds_map[result]
            payout_count = 0
            for b in winning_bets:
                payout = round(b["amount"] * winning_odds, 2)
                cur.execute("UPDATE bets SET payout = %s WHERE id = %s", (payout, b["id"]))
                cur.execute(
                    "UPDATE users SET points = ROUND((points + %s)::numeric, 2) WHERE username = %s",
                    (payout, b["username"]),
                )
                payout_count += 1

            action = "zaktualizowany" if existing else "zapisany"
            _log(cur, setter, "wynik",
                 f"{match_id}: {result}, kurs {winning_odds:.2f}, wypłaty dla {payout_count} graczy")
            _snapshot(cur, match_id)

        conn.commit()
    _clear_caches()
    return True, f"Wynik {action}! Wypłacono punkty dla {payout_count} graczy."


def clear_match_result(match_id: str, username: str = "system") -> tuple[bool, str]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT result FROM match_results WHERE match_id = %s", (match_id,)
            )
            if not cur.fetchone():
                return False, "Brak zapisanego wyniku."

            cur.execute(
                "SELECT username, payout FROM bets "
                "WHERE match_id = %s AND payout IS NOT NULL",
                (match_id,),
            )
            paid_bets = cur.fetchall()
            for b in paid_bets:
                cur.execute(
                    "UPDATE users SET points = ROUND((points - %s)::numeric, 2) WHERE username = %s",
                    (b["payout"], b["username"]),
                )
            cur.execute("UPDATE bets SET payout = NULL WHERE match_id = %s", (match_id,))
            cur.execute("DELETE FROM match_results WHERE match_id = %s", (match_id,))

            _log(cur, username, "cofnięcie wyniku",
                 f"{match_id}: przywrócono punkty dla {len(paid_bets)} graczy")
            _snapshot(cur, match_id)

        conn.commit()
    _clear_caches()
    return True, f"Wynik cofnięty, przywrócono punkty dla {len(paid_bets)} graczy."


# ── Leaderboard ────────────────────────────────────────────────────────────────

@_cached(ttl=30)
def get_leaderboard() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username, points FROM users ORDER BY points DESC")
            rows = cur.fetchall()
    return [dict(r) for r in rows]


# ── Audit log ──────────────────────────────────────────────────────────────────

@_cached(ttl=30)
def get_audit_log(limit: int = 500) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT action_at, action_type, username, details "
                "FROM audit_log ORDER BY action_at DESC LIMIT %s",
                (limit,),
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]


# ── Points history ─────────────────────────────────────────────────────────────

@_cached(ttl=30)
def get_points_history() -> list[dict]:
    """Last snapshot per user per calendar day (server time)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT username,
                       DATE(recorded_at) AS day,
                       points
                FROM   points_snapshots
                WHERE  id IN (
                    SELECT MAX(id)
                    FROM   points_snapshots
                    GROUP  BY username, DATE(recorded_at)
                )
                ORDER  BY day, username
            """)
            rows = cur.fetchall()
    return [dict(r) for r in rows]
