# taskwise/database.py
import sqlite3

class Database:
    def __init__(self, db_name="taskwise.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Very simple local accounts
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Tasks table with user_id foreign key
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'pending',
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )

        # Settings
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    # ---- tasks ----
    def add_task(self, title, description="", category="", due_date="", user_id=None):
        if user_id is None:
            raise ValueError("user_id is required to add a task")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (title, description, category, due_date, user_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (title, description, category, due_date, user_id),
        )
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return task_id

    def get_all_tasks(self, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            cursor.execute(
                """
                SELECT id, title, description, category, due_date, status, created_at
                FROM tasks
                WHERE user_id = ?
                ORDER BY created_at DESC
            """,
                (user_id,),
            )
        else:
            # Fallback for backward compatibility
            cursor.execute(
                """
                SELECT id, title, description, category, due_date, status, created_at
                FROM tasks
                ORDER BY created_at DESC
            """
            )
        
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_task(self, task_id, title, description="", category="", due_date="", user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # If user_id is provided, ensure the task belongs to that user
        if user_id is not None:
            cursor.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, category = ?, due_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """,
                (title, description, category, due_date, task_id, user_id),
            )
        else:
            cursor.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, category = ?, due_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (title, description, category, due_date, task_id),
            )
        
        conn.commit()
        conn.close()

    def delete_task(self, task_id, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        else:
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        conn.commit()
        conn.close()

    def update_task_status(self, task_id, status, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            cursor.execute(
                """
                UPDATE tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """,
                (status, task_id, user_id),
            )
        else:
            cursor.execute(
                """
                UPDATE tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (status, task_id),
            )
        
        conn.commit()
        conn.close()

    # ---- users ----
    def create_user(self, name, email, password_hash, role='user'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, role),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password_hash, role, created_at FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'password_hash': row[3],
                'role': row[4],
                'created_at': row[5]
            }
        return None

    def change_password(self, user_id, new_password_hash):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
        conn.commit()
        conn.close()

    # ---- settings ----
    def set_setting(self, key, value):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO app_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        conn.commit()
        conn.close()

    def get_setting(self, key, default=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
