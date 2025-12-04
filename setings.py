import flet as ft
from datetime import datetime, date
import sqlite3
import json
import urllib.request
import hashlib

# ----------------------------
# Theme Palettes
# Light Mode = your current colors
# Pink = stronger pink UI
# Dark = dark UI
# ----------------------------
THEMES = {
    "Light Mode": {
        "BG_COLOR": "#F8F6F4",
        "FORM_BG": "#E3F4F4",
        "BUTTON_COLOR": "#D2E9E9",
        "HEADER_BG": "#F8F6F4",
        "TEXT_PRIMARY": "#4A707A",
        "TEXT_SECONDARY": "#6B8F97",
        "BORDER_COLOR": "#4A707A",
        "ERROR_COLOR": "#E53935",
        "SUCCESS_COLOR": "#4CAF50",
    },
    "Pink": {
        "BG_COLOR": "#FFD1D9",
        "FORM_BG": "#FF8FB0",
        "BUTTON_COLOR": "#FF4D84",
        "HEADER_BG": "#FF77A0",
        "TEXT_PRIMARY": "#4A0B1F",
        "TEXT_SECONDARY": "#7A2C3F",
        "BORDER_COLOR": "#4A0B1F",
        "ERROR_COLOR": "#E53935",
        "SUCCESS_COLOR": "#4CAF50",
    },
    "Dark Mode": {
        "BG_COLOR": "#0F1115",
        "FORM_BG": "#1A1D24",
        "BUTTON_COLOR": "#2B303C",
        "HEADER_BG": "#10131A",
        "TEXT_PRIMARY": "#E7EEF7",
        "TEXT_SECONDARY": "#A9B6C6",
        "BORDER_COLOR": "#3A4150",
        "ERROR_COLOR": "#FF5C5C",
        "SUCCESS_COLOR": "#35C97E",
    },
}

CATEGORIES = ["Personal", "Work", "Study", "Bills", "Others"]


# ----------------------------
# Database
# ----------------------------
class Database:
    def __init__(self, db_name="taskwise.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Very simple local accounts
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    def add_task(self, title, description="", category="", due_date=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (title, description, category, due_date)
            VALUES (?, ?, ?, ?)
        """,
            (title, description, category, due_date),
        )
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return task_id

    def get_all_tasks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
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

    def update_task(self, task_id, title, description="", category="", due_date=""):
        conn = self.get_connection()
        cursor = conn.cursor()
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

    def delete_task(self, task_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def update_task_status(self, task_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
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
    def create_user(self, name, email, password_hash):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        conn.close()

    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return row

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


# ----------------------------
# App
# ----------------------------
class TaskWiseApp:
    def __init__(self):
        self.current_view = "tasks"
        self.current_filter = "All Tasks"
        self.db = Database()

        today = datetime.now().date()
        self.cal_year = today.year
        self.cal_month = today.month
        self.selected_date = today

        self.holidays_cache = {}

        # auth state
        self.user = None  # dict: {"id","name","email"}

        # theme state
        saved_theme = self.db.get_setting("theme_name", "Light Mode")
        if saved_theme not in THEMES:
            saved_theme = "Light Mode"
        self.theme_name = saved_theme
        self.colors = THEMES[self.theme_name].copy()

    # ---- PH Holidays (English) ----
    def _fetch_ph_holidays_english(self, year: int):
        if year in self.holidays_cache:
            return self.holidays_cache[year]

        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/PH"
        mapping = {}
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in data:
                d = item.get("date", "")
                name_en = item.get("name") or "Holiday"
                if d:
                    mapping.setdefault(d, []).append(name_en)
        except Exception:
            mapping = {}

        self.holidays_cache[year] = mapping
        return mapping

    def _hash_pw(self, pw: str) -> str:
        return hashlib.sha256((pw or "").encode("utf-8")).hexdigest()

    def main(self, page: ft.Page):
        # allow maximize space
        page.title = "TaskWise"
        page.window_maximized = True
        page.padding = 0

        # ---------------------------
        # Helpers using current theme colors
        # ---------------------------
        def C(k):  # color getter
            return self.colors[k]

        def apply_theme_to_page():
            page.bgcolor = C("BG_COLOR")
            page.update()

        def _fmt_date(d: date):
            return d.strftime("%Y-%m-%d")

        def _safe_parse_date(s: str):
            try:
                return datetime.strptime((s or "").strip(), "%Y-%m-%d").date()
            except Exception:
                return None

        def _month_name(m):
            return ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][m - 1]

        def _weekday_sun0(d: date):
            return (d.weekday() + 1) % 7

        def _days_in_month(y, m):
            if m == 12:
                return 31
            return (date(y, m + 1, 1) - date(y, m, 1)).days

        def _calendar_tasks_for_date(d: date):
            ds = _fmt_date(d)
            rows = []
            for t in self.db.get_all_tasks():
                _, title, desc, category, due_date, status, _ = t
                if (due_date or "").strip() == ds:
                    rows.append((title, status, category))
            return rows

        def _build_due_date_set_for_month(y: int, m: int):
            out = set()
            for t in self.db.get_all_tasks():
                due = (t[4] or "").strip()
                dd = _safe_parse_date(due)
                if dd and dd.year == y and dd.month == m:
                    out.add(_fmt_date(dd))
            return out

        # ---------------------------
        # Shared DatePicker (due date)
        # ---------------------------
        due_date_picker = ft.DatePicker()
        page.overlay.append(due_date_picker)

        # ---------------------------
        # Dropdown builder (category)
        # ---------------------------
        def category_dropdown(selected_value: str | None):
            value = selected_value if selected_value in CATEGORIES else None
            return ft.Dropdown(
                value=value,
                hint_text="Select Category",
                border_color=C("BORDER_COLOR"),
                bgcolor=C("BG_COLOR"),
                filled=True,
                color=C("TEXT_PRIMARY"),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                options=[ft.dropdown.Option(c) for c in CATEGORIES],
            )

        # ---------------------------
        # Auth dialogs (Login / Create Account / Change Password)
        # ---------------------------
        def show_login_dialog():
            email_tf = ft.TextField(
                hint_text="Email",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            pw_tf = ft.TextField(
                hint_text="Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def do_login(e):
                email = (email_tf.value or "").strip().lower()
                pw = pw_tf.value or ""
                row = self.db.get_user_by_email(email)
                if not row:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account not found."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user_id, name, em, pw_hash = row
                if self._hash_pw(pw) != pw_hash:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Wrong password."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                self.user = {"id": user_id, "name": name, "email": em}
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Logged in as {name}"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                update_view()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Login", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=420,
                    content=ft.Column([email_tf, pw_tf], spacing=12, tight=True),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Login", on_click=do_login, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def show_create_account_dialog():
            name_tf = ft.TextField(
                hint_text="Name",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            email_tf = ft.TextField(
                hint_text="Email",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            pw_tf = ft.TextField(
                hint_text="Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            pw2_tf = ft.TextField(
                hint_text="Confirm Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def do_create(e):
                name = (name_tf.value or "").strip()
                email = (email_tf.value or "").strip().lower()
                pw1 = pw_tf.value or ""
                pw2 = pw2_tf.value or ""

                if not name or not email or not pw1:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Please fill in all fields."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if pw1 != pw2:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Passwords do not match."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if self.db.get_user_by_email(email):
                    page.snack_bar = ft.SnackBar(content=ft.Text("Email already registered."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                self.db.create_user(name=name, email=email, password_hash=self._hash_pw(pw1))
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Account created. Please login."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Create Account", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=420,
                    content=ft.Column([name_tf, email_tf, pw_tf, pw2_tf], spacing=12, tight=True),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Sign Up", on_click=do_create, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def show_change_password_dialog():
            if not self.user:
                page.snack_bar = ft.SnackBar(content=ft.Text("Please login first."), bgcolor=C("ERROR_COLOR"))
                page.snack_bar.open = True
                page.update()
                return

            current_tf = ft.TextField(
                hint_text="Current Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            new_tf = ft.TextField(
                hint_text="New Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            new2_tf = ft.TextField(
                hint_text="Confirm New Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def do_change(e):
                row = self.db.get_user_by_email(self.user["email"])
                if not row:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account error."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user_id, name, em, pw_hash = row
                if self._hash_pw(current_tf.value or "") != pw_hash:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Current password is wrong."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if (new_tf.value or "") != (new2_tf.value or ""):
                    page.snack_bar = ft.SnackBar(content=ft.Text("New passwords do not match."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if not (new_tf.value or ""):
                    page.snack_bar = ft.SnackBar(content=ft.Text("New password is empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                self.db.change_password(user_id, self._hash_pw(new_tf.value))
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Password updated."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Change Password", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=420, content=ft.Column([current_tf, new_tf, new2_tf], spacing=12, tight=True)),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Update", on_click=do_change, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        # ---------------------------
        # Task dialogs (Edit/Add) with category dropdown + date picker linked to calendar
        # ---------------------------
        def show_edit_task_dialog(task_id, title, desc, category, due_date):
            edit_title = ft.TextField(
                value=title,
                hint_text="Rename",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            edit_description = ft.TextField(
                value=desc,
                hint_text="Description",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
                multiline=True,
                min_lines=2,
                max_lines=3,
            )

            edit_category_dd = category_dropdown(category)

            edit_due_date = ft.TextField(
                value=due_date,
                read_only=True,
                hint_text="Due date (click calendar)",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def open_date_picker(e):
                start = _safe_parse_date(edit_due_date.value) or self.selected_date
                due_date_picker.value = start

                def on_change(ev):
                    if due_date_picker.value:
                        chosen = due_date_picker.value
                        edit_due_date.value = _fmt_date(chosen)
                        self.selected_date = chosen
                        self.cal_year = chosen.year
                        self.cal_month = chosen.month
                        page.update()

                due_date_picker.on_change = on_change
                due_date_picker.open = True
                page.update()

            due_row = ft.Row(
                [
                    ft.Container(edit_due_date, expand=True),
                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_color=C("TEXT_PRIMARY"), on_click=open_date_picker),
                ],
                spacing=8,
            )

            def save(e):
                new_title = (edit_title.value or "").strip()
                if not new_title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Please enter a task title!"), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                self.db.update_task(
                    task_id=task_id,
                    title=new_title,
                    description=(edit_description.value or "").strip(),
                    category=(edit_category_dd.value or "").strip(),
                    due_date=(edit_due_date.value or "").strip(),
                )

                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Task updated."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                update_view()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Edit Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=460,
                    content=ft.Column([edit_title, edit_description, edit_category_dd, due_row], spacing=12, tight=True),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Save", on_click=save, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def show_add_task_dialog():
            title_tf = ft.TextField(
                hint_text="Task Title",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            desc_tf = ft.TextField(
                hint_text="Description",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
                multiline=True,
                min_lines=2,
                max_lines=3,
            )

            category_dd = category_dropdown("")

            due_tf = ft.TextField(
                value=_fmt_date(self.selected_date),
                read_only=True,
                hint_text="Due date (click calendar)",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def open_date_picker(e):
                start = _safe_parse_date(due_tf.value) or self.selected_date
                due_date_picker.value = start

                def on_change(ev):
                    if due_date_picker.value:
                        chosen = due_date_picker.value
                        due_tf.value = _fmt_date(chosen)
                        self.selected_date = chosen
                        self.cal_year = chosen.year
                        self.cal_month = chosen.month
                        page.update()

                due_date_picker.on_change = on_change
                due_date_picker.open = True
                page.update()

            due_row = ft.Row(
                [
                    ft.Container(due_tf, expand=True),
                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_color=C("TEXT_PRIMARY"), on_click=open_date_picker),
                ],
                spacing=8,
            )

            def add(e):
                title = (title_tf.value or "").strip()
                if not title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Please enter a task title!"), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                self.db.add_task(
                    title=title,
                    description=(desc_tf.value or "").strip(),
                    category=(category_dd.value or "").strip(),
                    due_date=(due_tf.value or "").strip(),
                )

                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Task added."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                update_view()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Add Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=460,
                    content=ft.Column([title_tf, desc_tf, category_dd, due_row], spacing=12, tight=True),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Add", on_click=add, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        # ---------------------------
        # Header: right-side popup (Login/Create Account) like your wireframe
        # ---------------------------
        def account_menu_button():
            if not self.user:
                return ft.PopupMenuButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    icon_color=C("TEXT_PRIMARY"),
                    items=[
                        ft.PopupMenuItem(text="Login", on_click=lambda e: show_login_dialog()),
                        ft.PopupMenuItem(text="Create Account", on_click=lambda e: show_create_account_dialog()),
                    ],
                )
            return ft.PopupMenuButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_color=C("TEXT_PRIMARY"),
                items=[
                    ft.PopupMenuItem(text=f"Signed in: {self.user['name']}"),
                    ft.PopupMenuItem(text="Logout", on_click=lambda e: do_logout()),
                ],
            )

        def do_logout():
            self.user = None
            page.snack_bar = ft.SnackBar(content=ft.Text("Logged out."), bgcolor=C("SUCCESS_COLOR"))
            page.snack_bar.open = True
            update_view()

        # ---------------------------
        # Header
        # ---------------------------
        def create_header():
            def navigate(view_name):
                def handler(e):
                    self.current_view = view_name
                    update_view()
                return handler

            def tab(label, view):
                is_active = self.current_view == view
                text = f"✱ {label} ✱" if is_active else label
                return ft.TextButton(text, on_click=navigate(view), style=ft.ButtonStyle(color=C("TEXT_PRIMARY")))

            return ft.Container(
                content=ft.Row(
                    [
                        ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Row([tab("Tasks", "tasks"), tab("Calendar", "calendar"), tab("Settings", "settings")], spacing=8),
                        account_menu_button(),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                bgcolor=C("HEADER_BG"),
                border=ft.border.only(bottom=ft.BorderSide(1, C("BORDER_COLOR"))),
            )

        # ---------------------------
        # Tasks list
        # ---------------------------
        def create_task_list():
            tasks = self.db.get_all_tasks()

            if self.current_filter != "All Tasks":
                wanted = self.current_filter.lower().strip()
                tasks = [t for t in tasks if (t[3] or "").strip().lower() == wanted]

            if not tasks:
                return ft.Container(
                    content=ft.Text("No tasks found in this category.", size=14, color=C("TEXT_SECONDARY")),
                    alignment=ft.alignment.center,
                    padding=20,
                )

            def is_overdue(due_date_str, status):
                if not due_date_str or status != "pending":
                    return False
                dd = _safe_parse_date(due_date_str)
                return bool(dd and dd < datetime.now().date())

            items = []
            for t in tasks:
                task_id, title, desc, category, due_date, status, created_at = t
                overdue = is_overdue(due_date, status)
                row_bg = C("FORM_BG") if not overdue else ft.Colors.with_opacity(0.10, ft.Colors.RED)

                def toggle_status(task_id, current_status):
                    def handler(e):
                        new_status = "completed" if current_status == "pending" else "pending"
                        self.db.update_task_status(task_id, new_status)
                        update_view()
                    return handler

                def delete_handler(task_id):
                    def handler(e):
                        self.db.delete_task(task_id)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Task deleted!"), bgcolor=C("SUCCESS_COLOR"))
                        page.snack_bar.open = True
                        update_view()
                    return handler

                def edit_handler(task_id, title, desc, category, due_date):
                    def handler(e):
                        show_edit_task_dialog(task_id, title, desc, category, due_date)
                    return handler

                due_label = f"Due: {due_date}" if (due_date or "").strip() else "No due date"
                cat_label = (category or "").strip() or "No category"

                card = ft.Container(
                    content=ft.Row(
                        [
                            ft.Checkbox(value=status == "completed", on_change=toggle_status(task_id, status)),
                            ft.Column(
                                [
                                    ft.Text(
                                        title,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=C("TEXT_PRIMARY") if status == "pending" else C("TEXT_SECONDARY"),
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(due_label, size=11, color=C("TEXT_SECONDARY")),
                                            ft.Container(width=12),
                                            ft.Text(f"Category: {cat_label}", size=11, color=C("TEXT_SECONDARY")),
                                        ],
                                        spacing=0,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_HORIZ,
                                icon_color=C("TEXT_SECONDARY"),
                                items=[
                                    ft.PopupMenuItem(text="Edit", on_click=edit_handler(task_id, title, desc, category, due_date)),
                                    ft.PopupMenuItem(text="Delete", on_click=delete_handler(task_id)),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=row_bg,
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    border=ft.border.all(1, C("BORDER_COLOR")),
                )
                items.append(card)

            return ft.Column(items, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # ---------------------------
        # Analytics
        # ---------------------------
        def build_stats():
            tasks = self.db.get_all_tasks()
            today = datetime.now().date()

            completed = sum(1 for t in tasks if t[5] == "completed")

            def overdue_task(t):
                due = (t[4] or "").strip()
                status = t[5]
                if not due or status != "pending":
                    return False
                dd = _safe_parse_date(due)
                return bool(dd and dd < today)

            overdue = sum(1 for t in tasks if overdue_task(t))

            def cat_count(name):
                return sum(1 for t in tasks if (t[3] or "").strip().lower() == name.lower())

            vals = {
                "Work": cat_count("work"),
                "Personal": cat_count("personal"),
                "Study": cat_count("study"),
                "Bills": cat_count("bills"),
                "Others": cat_count("others") + cat_count("other"),
            }
            return completed, overdue, vals

        def create_analytics_panel():
            completed, overdue, vals = build_stats()
            labels = list(vals.keys())
            values = [vals[k] for k in labels]
            if sum(values) == 0:
                values = [1] * len(labels)

            pie = ft.PieChart(
                sections=[ft.PieChartSection(value=values[i], title=labels[i]) for i in range(len(labels))],
                sections_space=2,
                center_space_radius=40,
                expand=True,
            )

            summary = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"{completed} tasks completed", size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Text(f"• {overdue} tasks overdue", size=12, color=C("TEXT_PRIMARY")),
                    ],
                    spacing=6,
                ),
                bgcolor=C("FORM_BG"),
                border_radius=12,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=12,
            )

            return ft.Column(
                [
                    ft.Container(
                        content=pie,
                        bgcolor=C("BG_COLOR"),
                        border_radius=12,
                        border=ft.border.all(1, C("BORDER_COLOR")),
                        padding=12,
                        height=280,
                    ),
                    ft.Container(height=12),
                    summary,
                ],
                expand=True,
            )

        # ---------------------------
        # Calendar view (PH holidays in English)
        # ---------------------------
        def create_calendar_view():
            holidays = self._fetch_ph_holidays_english(self.cal_year)
            due_set = _build_due_date_set_for_month(self.cal_year, self.cal_month)

            def set_selected(d: date):
                self.selected_date = d
                update_view()

            def prev_month(e):
                if self.cal_month == 1:
                    self.cal_year -= 1
                    self.cal_month = 12
                else:
                    self.cal_month -= 1
                self.selected_date = date(self.cal_year, self.cal_month, 1)
                update_view()

            def next_month(e):
                if self.cal_month == 12:
                    self.cal_year += 1
                    self.cal_month = 1
                else:
                    self.cal_month += 1
                self.selected_date = date(self.cal_year, self.cal_month, 1)
                update_view()

            sel = self.selected_date
            sel_str = _fmt_date(sel)
            sel_holidays = holidays.get(sel_str, [])
            sel_tasks = _calendar_tasks_for_date(sel)

            left_card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Calendar", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Container(height=10),
                        ft.Container(
                            bgcolor=C("FORM_BG"),
                            border_radius=16,
                            border=ft.border.all(1, C("BORDER_COLOR")),
                            padding=16,
                            expand=True,
                            content=ft.Column(
                                [
                                    ft.Text(f"{sel.strftime('%B')} {sel.day}", size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Container(height=10),
                                    ft.Container(
                                        bgcolor=C("BG_COLOR"),
                                        border_radius=12,
                                        border=ft.border.all(1, C("BORDER_COLOR")),
                                        padding=12,
                                        expand=True,
                                        content=ft.Column(
                                            [
                                                ft.Text("Holidays (Philippines)", size=12, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                                ft.Text("No holiday on this day." if not sel_holidays else "", size=12, color=C("TEXT_SECONDARY")),
                                                *[ft.Text(f"• {h}", size=12, color=C("TEXT_PRIMARY")) for h in sel_holidays],
                                                ft.Container(height=10),
                                                ft.Text("Tasks Due", size=12, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                                ft.Text("No tasks due on this day." if not sel_tasks else "", size=12, color=C("TEXT_SECONDARY")),
                                                *[ft.Text(f"• {t[0]} ({t[1]})", size=12, color=C("TEXT_PRIMARY")) for t in sel_tasks],
                                            ],
                                            spacing=6,
                                        ),
                                    ),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ),
                    ],
                    expand=True,
                ),
                expand=True,
            )

            first = date(self.cal_year, self.cal_month, 1)
            start_offset = _weekday_sun0(first)
            dim = _days_in_month(self.cal_year, self.cal_month)
            today = datetime.now().date()

            cells = []
            day_num = 1 - start_offset
            for _ in range(6):
                row = []
                for _ in range(7):
                    d = None
                    if 1 <= day_num <= dim:
                        d = date(self.cal_year, self.cal_month, day_num)

                    if d is None:
                        row.append(ft.Container(width=46, height=36))
                    else:
                        ds = _fmt_date(d)
                        is_sel = d == self.selected_date
                        is_today = d == today
                        is_holiday = ds in holidays
                        has_due = ds in due_set

                        bg = C("BUTTON_COLOR") if is_sel else C("BG_COLOR")
                        border = ft.border.all(1, C("BORDER_COLOR")) if (is_today or is_sel) else ft.border.all(
                            1, ft.Colors.with_opacity(0.15, C("BORDER_COLOR"))
                        )

                        holiday_dot = ft.Container(width=6, height=6, bgcolor=C("ERROR_COLOR"), border_radius=99) if is_holiday else ft.Container(width=6, height=6)
                        due_dot = ft.Container(width=6, height=6, bgcolor=C("SUCCESS_COLOR"), border_radius=99) if has_due else ft.Container(width=6, height=6)

                        row.append(
                            ft.Container(
                                width=46,
                                height=36,
                                bgcolor=bg,
                                border=border,
                                border_radius=10,
                                padding=ft.padding.symmetric(horizontal=8),
                                on_click=(lambda e, dd=d: set_selected(dd)),
                                content=ft.Row(
                                    [
                                        ft.Text(str(d.day), size=12, color=C("TEXT_PRIMARY"),
                                                weight=ft.FontWeight.BOLD if (is_holiday or is_sel) else ft.FontWeight.NORMAL),
                                        ft.Row([holiday_dot, due_dot], spacing=4),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            )
                        )

                    day_num += 1
                cells.append(ft.Row(row, spacing=10, alignment=ft.MainAxisAlignment.CENTER))

            cal_box = ft.Container(
                bgcolor=C("BG_COLOR"),
                border_radius=16,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=16,
                expand=True,
                content=ft.Column(
                    [
                        ft.Container(
                            bgcolor=C("BUTTON_COLOR"),
                            border_radius=14,
                            padding=ft.padding.symmetric(horizontal=10, vertical=10),
                            content=ft.Row(
                                [
                                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=C("TEXT_PRIMARY"), on_click=prev_month),
                                    ft.Text(f"{self.cal_month:02d}   {_month_name(self.cal_month)}   {self.cal_year}",
                                            size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=C("TEXT_PRIMARY"), on_click=next_month),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ),
                        ft.Container(height=12),
                        ft.Row(
                            [ft.Text(x, size=10, color=C("TEXT_SECONDARY"), width=46, text_align=ft.TextAlign.CENTER)
                             for x in ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Container(height=8),
                        *cells,
                        ft.Container(height=10),
                        ft.Row(
                            [
                                ft.Row([ft.Container(width=10, height=10, bgcolor=C("ERROR_COLOR"), border_radius=99),
                                        ft.Text("Holiday", size=11, color=C("TEXT_SECONDARY"))], spacing=6),
                                ft.Container(width=18),
                                ft.Row([ft.Container(width=10, height=10, bgcolor=C("SUCCESS_COLOR"), border_radius=99),
                                        ft.Text("Task Due", size=11, color=C("TEXT_SECONDARY"))], spacing=6),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            return ft.Container(
                bgcolor=C("BG_COLOR"),
                border_radius=18,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=18,
                expand=True,
                content=ft.Row(
                    [
                        ft.Container(content=left_card, expand=6),
                        ft.Container(width=26),
                        ft.Container(content=cal_box, expand=4),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    expand=True,
                ),
            )

        # ---------------------------
        # Settings view (wireframe style)
        # ---------------------------
        def create_settings_view():
            # big outer board
            def settings_row(title, trailing=None, on_click=None):
                item = ft.Container(
                    bgcolor=C("BG_COLOR"),
                    border_radius=12,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    content=ft.Row(
                        [
                            ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY"), expand=True),
                            trailing if trailing else ft.Icon(ft.Icons.CHEVRON_RIGHT, color=C("TEXT_SECONDARY")),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    on_click=on_click,
                )
                return item

            theme_dd = ft.Dropdown(
                value=self.theme_name,
                options=[ft.dropdown.Option("Light Mode"), ft.dropdown.Option("Dark Mode"), ft.dropdown.Option("Pink")],
                border_color=C("BORDER_COLOR"),
                bgcolor=C("BG_COLOR"),
                filled=True,
                color=C("TEXT_PRIMARY"),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
                width=180,
            )

            def apply_theme(e):
                chosen = theme_dd.value or "Light Mode"
                if chosen not in THEMES:
                    chosen = "Light Mode"
                self.theme_name = chosen
                self.colors = THEMES[chosen].copy()
                self.db.set_setting("theme_name", chosen)
                apply_theme_to_page()
                update_view()

            theme_dd.on_change = apply_theme

            # actions
            def account_action(e):
                if not self.user:
                    show_login_dialog()
                else:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Signed in as {self.user['name']}"), bgcolor=C("SUCCESS_COLOR"))
                    page.snack_bar.open = True
                    page.update()

            def logout_action(e):
                do_logout()

            return ft.Container(
                bgcolor=C("BG_COLOR"),
                border_radius=18,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=24,
                expand=True,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=520,
                            bgcolor=C("FORM_BG"),
                            border_radius=18,
                            border=ft.border.all(1, C("BORDER_COLOR")),
                            padding=20,
                            content=ft.Column(
                                [
                                    ft.Text("Settings", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Container(height=14),
                                    ft.Container(
                                        bgcolor=C("BG_COLOR"),
                                        border_radius=16,
                                        border=ft.border.all(1, C("BORDER_COLOR")),
                                        padding=18,
                                        content=ft.Column(
                                            [
                                                settings_row("Theme", trailing=theme_dd),
                                                ft.Container(height=10),
                                                settings_row("Account", on_click=account_action),
                                                ft.Container(height=10),
                                                settings_row("Change Password", on_click=lambda e: show_change_password_dialog()),
                                                ft.Container(height=10),
                                                settings_row("Logout", on_click=logout_action),
                                            ],
                                            spacing=0,
                                        ),
                                    ),
                                ],
                                spacing=0,
                            ),
                        )
                    ],
                ),
            )

        # ---------------------------
        # Main content area
        # ---------------------------
        content_area = ft.Container(expand=True)

        def update_view():
            # rebuild header to refresh login menu + theme colors
            header = create_header()

            if self.current_view == "tasks":
                def pill(text):
                    active = self.current_filter == text

                    def set_filter(e):
                        self.current_filter = text
                        update_view()

                    return ft.ElevatedButton(
                        text,
                        on_click=set_filter,
                        bgcolor=C("BUTTON_COLOR") if active else C("BG_COLOR"),
                        color=ft.Colors.WHITE if active else C("TEXT_PRIMARY"),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), side=ft.BorderSide(1, C("BORDER_COLOR"))),
                        height=34,
                    )

                left_panel = ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Text("Tasks", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ft.Container(height=10),
                            ft.Row(
                                [pill("All Tasks")] + [pill(c) for c in CATEGORIES],
                                spacing=10,
                                wrap=True,
                            ),
                            ft.Container(height=12),
                            ft.Container(content=create_task_list(), expand=True),
                            ft.Container(height=10),
                            ft.Row(
                                [
                                    ft.Container(expand=True),
                                    ft.FloatingActionButton(
                                        icon=ft.Icons.ADD,
                                        bgcolor=C("BUTTON_COLOR"),
                                        foreground_color=ft.Colors.WHITE,
                                        on_click=lambda e: show_add_task_dialog(),
                                    ),
                                    ft.Container(expand=True),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        expand=True,
                    ),
                )

                divider = ft.Container(width=2, bgcolor=C("BORDER_COLOR"), margin=ft.margin.symmetric(vertical=24))

                right_panel = ft.Container(expand=True, padding=20, content=create_analytics_panel())

                content_area.content = ft.Container(
                    bgcolor=C("BG_COLOR"),
                    border_radius=18,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    padding=14,
                    expand=True,
                    content=ft.Row([left_panel, divider, right_panel], expand=True, spacing=0),
                )

            elif self.current_view == "calendar":
                content_area.content = create_calendar_view()

            else:
                content_area.content = create_settings_view()

            # main frame
            main_container.content = ft.Column(
                [
                    header,
                    ft.Container(
                        bgcolor=C("BG_COLOR"),
                        padding=24,
                        expand=True,
                        content=ft.Container(expand=True, alignment=ft.alignment.center, content=content_area),
                    ),
                ],
                spacing=0,
                expand=True,
            )

            apply_theme_to_page()
            page.update()

        # ---------------------------
        # Main shell container
        # ---------------------------
        main_container = ft.Container(
            bgcolor=C("BG_COLOR"),
            border_radius=16,
            margin=20,
            expand=True,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK)),
        )
        page.add(main_container)

        # Initial render
        update_view()


def main(page: ft.Page):
    TaskWiseApp().main(page)


ft.app(target=main)
