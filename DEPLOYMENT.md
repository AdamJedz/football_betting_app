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
Log in with any user from init_users.py to test.

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
4. Go to **SQL Editor** (left sidebar) → **New query** → paste and run:

```sql
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    points        INTEGER NOT NULL DEFAULT 100,
    created_at    TIMESTAMP DEFAULT NOW()
);
```

5. Go to **Project Settings → Database** → copy the **Connection string (URI)** — looks like:
   `postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres`

---

### Step 2 — Switch the app to PostgreSQL

Install the PostgreSQL driver locally:
```powershell
pip install psycopg2-binary
```

Add it to requirements.txt:
```
psycopg2-binary>=2.9.0
```

Replace `database.py` with the PostgreSQL version:

```python
# At the top of database.py, replace the SQLite imports/connection with:
import os
import psycopg2
import psycopg2.extras
import bcrypt

def get_connection():
    url = os.environ["DATABASE_URL"]
    return psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            SERIAL PRIMARY KEY,
                    username      TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    points        INTEGER NOT NULL DEFAULT 100,
                    created_at    TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
```
> The rest of database.py stays the same — just swap `?` placeholders to `%s` (PostgreSQL style).

Create `.streamlit/secrets.toml` locally (this file is gitignored — never commit it):
```toml
DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres"
```

In `database.py`, read it via:
```python
import streamlit as st
url = st.secrets.get("DATABASE_URL") or os.environ.get("DATABASE_URL")
```

---

### Step 3 — Create users in Supabase

Run `init_users.py` locally (with the DATABASE_URL secret in place) — it will insert users into Supabase.

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
- [ ] Never commit `.streamlit/secrets.toml` (already in .gitignore)
- [ ] Use a strong Supabase DB password
- [ ] HTTPS is provided automatically by both platforms
