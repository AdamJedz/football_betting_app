"""
Run this script ONCE to create all users.

Usage:
    python init_users.py

Edit the USERS list below before running.
Passwords should be changed by users after first login (feature to add later).
"""

from database import init_db, create_user

USERS = [
    # ("username", "password", starting_points)
    ("admin",   "changeme123", 100),
    ("tester1", "test1234",    100),
    ("tester2", "test1234",    100),
]

if __name__ == "__main__":
    init_db()
    for username, password, points in USERS:
        if create_user(username, password, points):
            print(f"  Created : {username}")
        else:
            print(f"  Skipped : {username} (already exists)")
    print("\nDone. Remember to change default passwords!")
