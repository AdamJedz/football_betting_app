"""
Run this script ONCE to create all users.

Usage:
    python init_users.py

Edit the USERS list below before running.
Passwords should be changed by users after first login (feature to add later).
"""

from database import init_db, create_user

USERS = [
    # ("username", "password"),
    ("admin", "changeme123"),
    ("player1", "pass1234"),
    ("player2", "pass1234"),
    # Add all 20 users here...
]

if __name__ == "__main__":
    init_db()
    for username, password in USERS:
        if create_user(username, password):
            print(f"  Created : {username}")
        else:
            print(f"  Skipped : {username} (already exists)")
    print("\nDone. Remember to change default passwords!")
