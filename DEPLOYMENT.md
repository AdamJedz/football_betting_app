# Deployment Guide

## Part 1 — Run locally first

```powershell
# 1. Go to the project folder
cd C:\Users\adami\football_betting_app

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Edit init_users.py — add your 20 users and their passwords
#    Then run it once:
python init_users.py

# 5. Start the app
streamlit run app.py
```

App opens at http://localhost:8501  
Log in with any user from `init_users.py` to test.

---

## Part 2 — Deploy for free (Streamlit Community Cloud + Supabase)

### Why two services?
- **Streamlit Community Cloud** hosts the app (free, connects to GitHub)
- **Supabase** hosts the database (free PostgreSQL) — needed because Streamlit Cloud has no persistent disk

---

### Step 1 — Create a free Supabase database

1. Go to https://supabase.com → **Start for free** → create account
2. Click **New project**, give it any name (e.g. `football-betting`), set a strong DB password, save it somewhere
3. Wait ~1 minute for the project to be ready
4. Go to **SQL Editor** (left sidebar) → **New query** → paste and run the full schema below:

```sql
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    points        REAL NOT NULL DEFAULT 100,
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bets (
    id         SERIAL PRIMARY KEY,
    username   TEXT NOT NULL,
    match_id   TEXT NOT NULL,
    outcome    TEXT NOT NULL CHECK(outcome IN ('home', 'draw', 'away')),
    amount     REAL NOT NULL,
    payout     REAL,
    placed_at  TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(username, match_id)
);

CREATE TABLE match_odds (
    match_id   TEXT PRIMARY KEY,
    home_odds  REAL NOT NULL,
    draw_odds  REAL NOT NULL,
    away_odds  REAL NOT NULL,
    updated_by TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE match_results (
    match_id TEXT PRIMARY KEY,
    result   TEXT NOT NULL CHECK(result IN ('home', 'draw', 'away')),
    set_by   TEXT NOT NULL,
    set_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_log (
    id          SERIAL PRIMARY KEY,
    action_at   TIMESTAMP DEFAULT NOW(),
    action_type TEXT NOT NULL,
    username    TEXT NOT NULL,
    details     TEXT
);

CREATE TABLE points_snapshots (
    id          SERIAL PRIMARY KEY,
    username    TEXT NOT NULL,
    points      REAL NOT NULL,
    match_id    TEXT,
    recorded_at TIMESTAMP DEFAULT NOW()
);
```

5. Go to **Project Settings → Database** → copy the **Connection string (URI)**:
   `postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres`

---

### Step 2 — Switch the app to PostgreSQL

Install the PostgreSQL driver locally:
```powershell
pip install psycopg2-binary
```

Add it to `requirements.txt`:
```
psycopg2-binary>=2.9.0
```

At the **top of `database.py`**, replace the SQLite imports and connection helpers with:

```python
import os
import psycopg2
import psycopg2.extras
import bcrypt
import streamlit as st

def get_connection():
    url = st.secrets.get("DATABASE_URL") or os.environ["DATABASE_URL"]
    return psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
```

**Important:** PostgreSQL uses `%s` placeholders instead of SQLite's `?`.  
Do a project-wide find-and-replace: `", ?"` → `", %s"` and `"(?,"` → `"(%s,"` etc.  
The easiest way is to open `database.py` and replace every `?` inside SQL strings with `%s`.

Also change `conn.row_factory = sqlite3.Row` references — with `RealDictCursor` you already get dict-like rows, so `dict(row)` still works.

Remove the `sqlite3` import and `DB_PATH` variable — they are no longer needed.

The `init_db()` function can be simplified to a no-op (tables already exist in Supabase):
```python
def init_db() -> None:
    pass  # tables created via Supabase SQL editor
```

Create `.streamlit/secrets.toml` locally (this file is gitignored — never commit it):
```toml
DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres"
```

---

### Step 3 — Create users in Supabase

Run `init_users.py` locally (with the `DATABASE_URL` secret in place) — it will insert users into Supabase.

---

### Step 4 — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io → **Sign in with GitHub**
2. Click **New app**
3. Select your repo `football_betting_app`, branch `main`, main file `app.py`
4. Click **Advanced settings → Secrets** and paste:
   ```toml
   DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres"
   ```
5. Click **Deploy** — takes ~1 minute

You get a free public URL like `https://adamjedz-football-betting-app.streamlit.app`

---

## Auto-refresh

The app refreshes automatically **every 5 minutes** in every connected browser (via `streamlit-autorefresh`). This means:
- New bets placed by other users appear without anyone needing to reload the page
- Results and leaderboard update across all sessions automatically
- The Streamlit Cloud app also stays awake as long as any user has it open

If you want a different refresh interval, change this line in `app.py`:
```python
st_autorefresh(interval=5 * 60 * 1000, key="autorefresh")  # milliseconds
```
For example, `2 * 60 * 1000` = every 2 minutes, `10 * 60 * 1000` = every 10 minutes.

---

## Limits of the free tier

| | Streamlit Community Cloud | Supabase Free |
|---|---|---|
| Cost | Free | Free |
| Apps | Unlimited public | 2 projects |
| DB storage | — | 500 MB |
| Inactivity sleep | After ~7 days no visits | Never |
| Users | 20 ✅ | No limit |

For ~20 users and a betting app, both free tiers are more than enough.

---

## Security checklist before going live

- [ ] Change all default passwords in `init_users.py` before running it
- [ ] Never commit `.streamlit/secrets.toml` (already in `.gitignore`)
- [ ] Use a strong Supabase DB password
- [ ] HTTPS is provided automatically by both platforms
