import os
import sqlite3

from werkzeug.security import generate_password_hash

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(_THIS_DIR, "..", "spendly.db"))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );
        """)
    conn.close()


def seed_db():
    conn = get_db()
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    pw = generate_password_hash("demo123")
    with conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", pw),
        )
        user_id = cursor.lastrowid

        expenses = [
            (user_id, 12.50,  "Food",          "2026-06-01", "Lunch at cafe"),
            (user_id, 35.00,  "Transport",     "2026-06-02", "Monthly bus pass top-up"),
            (user_id, 120.00, "Bills",         "2026-06-03", "Electricity bill"),
            (user_id, 45.00,  "Health",        "2026-06-04", "Pharmacy"),
            (user_id, 18.00,  "Entertainment", "2026-06-05", "Movie ticket"),
            (user_id, 62.00,  "Shopping",      "2026-06-06", "New shoes"),
            (user_id, 9.99,   "Other",         "2026-06-07", "Miscellaneous"),
            (user_id, 22.00,  "Food",          "2026-06-08", "Grocery run"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
    conn.close()
