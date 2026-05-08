# Deployment Guide

## Overview

This app uses SQLite for storage. The key constraint: **the database file must persist across restarts**.
Two recommended options are listed below — one free, one cheap-and-simple.

---

## Option A — Railway (~$5/month) ✅ Recommended

**Best for:** simplicity, no database changes needed, SQLite just works.

### Steps

1. **Push your code to GitHub** (already done).

2. **Create a Railway account** at https://railway.app and connect your GitHub.

3. **New Project → Deploy from GitHub repo** → select `football_betting_app`.

4. **Add a Persistent Volume:**
   - In your Railway service → *Settings* → *Volumes*
   - Mount path: `/app/data`
   - This is where SQLite will store `app.db`

5. **Set environment variable** in Railway dashboard:
   ```
   PYTHONPATH=/app
   ```

6. **Set the start command** (Railway → Settings → Deploy):
   ```
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

7. **Run init_users.py once** via Railway's shell or by temporarily adding it to the start command:
   ```
   python init_users.py && streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
   Remove `python init_users.py &&` after first run.

8. Railway gives you a public URL like `https://football-betting-app.up.railway.app`.

**Cost:** ~$5/month (Hobby plan). Free tier exists but has no persistent volumes.

---

## Option B — Streamlit Community Cloud (Free)

**Best for:** zero cost, but requires replacing SQLite with a cloud database.

### Why SQLite won't work here
Streamlit Community Cloud has an **ephemeral filesystem** — every restart (deploy, update, inactivity sleep) wipes the `data/` folder and you lose all user data.

### Solution: use Supabase (free PostgreSQL)

1. **Create a free Supabase project** at https://supabase.com.

2. In Supabase → SQL Editor, run:
   ```sql
   CREATE TABLE users (
       id            SERIAL PRIMARY KEY,
       username      TEXT UNIQUE NOT NULL,
       password_hash TEXT NOT NULL,
       points        INTEGER NOT NULL DEFAULT 100,
       created_at    TIMESTAMP DEFAULT NOW()
   );
   ```

3. **Update `database.py`** to use PostgreSQL instead of SQLite:
   - Replace `sqlite3` with `psycopg2`
   - Add `psycopg2-binary` to `requirements.txt`
   - Use `DATABASE_URL` from Supabase project settings

4. **Add secrets** to Streamlit Cloud (Settings → Secrets):
   ```toml
   DATABASE_URL = "postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres"
   ```

5. **Deploy:** go to https://share.streamlit.io → New app → connect GitHub repo → set main file to `app.py`.

**Cost:** Free. Supabase free tier supports up to 500MB and 2 projects.

---

## Local Development

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create users (edit init_users.py first)
python init_users.py

# 4. Run the app
streamlit run app.py
```

App will be at http://localhost:8501

---

## Security Checklist Before Going Live

- [ ] Change all default passwords in `init_users.py` before running it
- [ ] Never commit `data/` or `.streamlit/secrets.toml`
- [ ] Use strong passwords for all users (min 8 chars)
- [ ] Consider adding HTTPS (Railway and Streamlit Cloud both provide it automatically)
