import sqlite3
from passlib.hash import bcrypt
from datetime import datetime
from vault import get_secret

# -------------------------------------------------------------
# Secure Configuration (from .env / encrypted .env)
# -------------------------------------------------------------
DB_NAME = get_secret("DB_NAME", "taskwise.db")
ADMIN_DEFAULT_PASSWORD = get_secret("ADMIN_DEFAULT_PASSWORD", "Admin123")

# -------------------------------------------------------------
# Utility
# -------------------------------------------------------------
def get_db_path():
    return DB_NAME

def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# -------------------------------------------------------------
# Database Initialization
# -------------------------------------------------------------
def init_db():
    conn = connect()
    cursor = conn.cursor()

    # USERS TABLE — updated to match your UI (name + email + password_hash)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_banned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ✅ SAFE MIGRATIONS (SQLite cannot add non-constant defaults)
    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]

    if "is_banned" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")

    if "created_at" not in cols:
        # add column WITHOUT default (SQLite restriction)
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
        # backfill existing rows
        cursor.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    # TASKS TABLE — per user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # PER-USER SETTINGS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            UNIQUE(user_id, key),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # SYSTEM LOGS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            email TEXT,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Create default admin if not exists (admin@taskwise.com)
    cursor.execute("SELECT * FROM users WHERE email = 'admin@taskwise.com'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, is_banned) VALUES (?, ?, ?, ?, ?)",
            (
                "Admin",
                "admin@taskwise.com",
                bcrypt.hash(ADMIN_DEFAULT_PASSWORD),  # ← SECRET USED HERE
                "admin",
                0,
            )
        )
        conn.commit()

    conn.close()

# -------------------------------------------------------------
# User Functions
# -------------------------------------------------------------
def create_user(name, email, password_hash, role="user"):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, is_banned, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, password_hash, role, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user_by_email(email):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, password_hash, role, COALESCE(is_banned, 0) FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "password_hash": row[3],
            "role": row[4],
            "is_banned": bool(row[5]),
        }
    return None

def get_user_by_id(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, password_hash, role, COALESCE(is_banned, 0) FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "password_hash": row[3],
            "role": row[4],
            "is_banned": bool(row[5]),
        }
    return None

def get_user(user_id):
    return get_user_by_id(user_id)

def get_user_by_username(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, password_hash, role, COALESCE(is_banned, 0) FROM users WHERE name = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "password_hash": row[3],
            "role": row[4],
            "is_banned": bool(row[5]),
        }
    return None

def update_user_password(user_id, new_password_hash):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (new_password_hash, user_id)
    )
    conn.commit()
    conn.close()

# --- Admin: Users list + ban/unban + delete ---
def get_users():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, role, COALESCE(is_banned, 0)
        FROM users
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    users = []
    for r in rows:
        users.append({
            "id": r[0],
            "name": r[1],
            "email": r[2],
            "role": r[3],
            "is_banned": bool(r[4]),
        })
    return users

def ban_user(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = connect()
    cursor = conn.cursor()

    # delete related data first
    cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM app_settings WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM logs WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

def is_user_banned(email):
    u = get_user_by_email(email)
    return bool(u and u.get("is_banned"))

# -------------------------------------------------------------
# Logging
# -------------------------------------------------------------
def add_log(action, details="", user_id=None):
    conn = connect()
    cursor = conn.cursor()

    email = None
    if user_id:
        cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        u = cursor.fetchone()
        if u:
            email = u[0]

    cursor.execute("""
        INSERT INTO logs (user_id, email, action, details)
        VALUES (?, ?, ?, ?)
    """, (user_id, email, action, details))
    conn.commit()
    conn.close()

def get_logs():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, email, action, details, created_at
        FROM logs
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "user_id": r[1],
            "email": r[2],
            "action": r[3],
            "details": r[4],
            "created_at": r[5],
        })
    return logs

# -------------------------------------------------------------
# Task Functions (per-user isolated)
# -------------------------------------------------------------
def add_task(user_id, title, description="", category="", due_date=""):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title, description, category, due_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, title, description, category, due_date)
    )
    conn.commit()
    conn.close()

def get_tasks_by_user(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, category, due_date, status, created_at, updated_at
        FROM tasks
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_task(user_id, task_id, title, description, category, due_date, status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks SET
            title=?, description=?, category=?, due_date=?, status=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=? AND user_id=?
    """, (title, description, category, due_date, status, task_id, user_id))
    conn.commit()
    conn.close()

def update_task_status(user_id, task_id, status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET status=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=? AND user_id=?
    """, (status, task_id, user_id))
    conn.commit()
    conn.close()

def delete_task(user_id, task_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
    conn.commit()
    conn.close()

# -------------------------------------------------------------
# Per-User Settings
# -------------------------------------------------------------
def set_setting(user_id, key, value):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO app_settings (user_id, key, value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, key)
        DO UPDATE SET value=excluded.value
    """, (user_id, key, value))
    conn.commit()
    conn.close()

def get_setting(user_id, key, default=None):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT value FROM app_settings WHERE user_id=? AND key=?",
        (user_id, key)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return default

    val = row[0]

    # Boolean normalization for switches
    if isinstance(default, bool):
        s = str(val).strip().lower()
        if s in ("1", "true", "yes", "y", "on"):
            return True
        if s in ("0", "false", "no", "n", "off"):
            return False
        return default

    return val
