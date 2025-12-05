# db.py
import os
import sqlite3
from typing import Optional, List, Dict, Any

# Always save the database in the same folder as this db.py file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "taskwise.db")


def get_db_path() -> str:
    return DB_PATH


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Safe to call every app start. It won't recreate tables, only ensures they exist."""
    conn = _get_conn()
    cur = conn.cursor()

    # -------------------------
    # USERS TABLE
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # CREATE DEFAULT ADMIN ACCOUNT
    # -------------------------
    cur.execute("SELECT * FROM users WHERE email = 'admin@taskwise.com'")
    if not cur.fetchone():
        # bcrypt hash for password: admin12345
        pw_hash = "$2b$12$LQpC0kxrlEYwOYZb0s9XhOK5d0xH3sTk20CvdPet8.7t92WjU6Cxa"
        cur.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ('Administrator', 'admin@taskwise.com', ?, 'admin')
        """, (pw_hash,))

    # -------------------------
    # TASKS TABLE (scoped to user)
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT '',
            due_date TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # -------------------------
    # AUDIT LOGS TABLE (IAS)
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            email TEXT,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)

    # Useful indexes (performance + cleaner queries)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_created ON tasks(user_id, created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at)")

    conn.commit()
    conn.close()


# =========================================================
# LOGGING (IAS)
# =========================================================
def add_log(action: str, details: str = "", user_id: Optional[int] = None, email: Optional[str] = None) -> None:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (user_id, email, action, details) VALUES (?, ?, ?, ?)",
        (user_id, email, action, details),
    )
    conn.commit()
    conn.close()


def get_logs(limit: int = 200) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, email, action, details, created_at
        FROM logs
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# USERS
# =========================================================
def create_user(name: str, email: str, password_hash: str, role: str = "user") -> int:
    """
    Creates a user. Raises sqlite3.IntegrityError if email already exists.
    Returns new user_id.
    """
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, role),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    # Log after commit so user_id exists
    add_log("SIGNUP", details=f"Account created (role={role})", user_id=user_id, email=email)
    return user_id


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# =========================================================
# TASKS (USER-SCOPED)
# =========================================================
def add_task(user_id: int, title: str, description: str = "", category: str = "", due_date: str = "") -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tasks (user_id, title, description, category, due_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, title, description or "", category or "", due_date or ""),
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()

    add_log("TASK_ADD", details=f"Task created: id={task_id}, title={title}", user_id=user_id)
    return task_id


def get_tasks_by_user(user_id: int) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, description, category, due_date, status, created_at
        FROM tasks
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_user_password(email: str, new_hash: str):
    conn = _get_conn()
    conn.execute("UPDATE users SET password_hash=? WHERE email=?", (new_hash, email))
    conn.commit()
    conn.close()

def update_task(
    user_id: int,
    task_id: int,
    title: str,
    description: str = "",
    category: str = "",
    due_date: str = ""
) -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, category = ?, due_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (title, description or "", category or "", due_date or "", task_id, user_id),
    )
    changed = cur.rowcount
    conn.commit()
    conn.close()

    if changed:
        add_log("TASK_EDIT", details=f"Task updated: id={task_id}, title={title}", user_id=user_id)
    return changed


def delete_task(user_id: int, task_id: int) -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    changed = cur.rowcount
    conn.commit()
    conn.close()

    if changed:
        add_log("TASK_DELETE", details=f"Task deleted: id={task_id}", user_id=user_id)
    return changed


def toggle_task_status(user_id: int, task_id: int) -> Optional[str]:
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("SELECT status FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    new_status = "completed" if row["status"] == "pending" else "pending"

    cur.execute(
        """
        UPDATE tasks
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (new_status, task_id, user_id),
    )
    conn.commit()
    conn.close()

    add_log("TASK_STATUS", details=f"Task status changed: id={task_id}, status={new_status}", user_id=user_id)
    return new_status