import flet as ft
from passlib.hash import bcrypt
import db


def main(page: ft.Page):
    # ----------------------------------
    # INITIAL PAGE SETTINGS
    # ----------------------------------
    page.title = "TaskWise"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1000
    page.window_height = 600

    # Initialize SQLite DB
    db.init_db()
    print("USING DB:", db.get_db_path())

    # ----------------------------------
    # COLOR SCHEME
    # ----------------------------------
    BG_COLOR = "#F8F6F4"
    FORM_BG = "#E3F4F4"
    BUTTON_COLOR = "#D2E9E9"
    LIGHT_PINK = "#C4DFDF"

    PRIMARY_TEXT = "#4A707A"
    SECONDARY_TEXT = "#6B8F97"

    SUCCESS_GREEN = "#4CAF50"

    # ----------------------------------
    # UTIL: Snackbar message
    # ----------------------------------
    def show_message(text: str, color="red"):
        page.snack_bar = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # ----------------------------------
    # FORM FIELD (must be defined early)
    # ----------------------------------
    def styled_field(label, password=False):
        return ft.TextField(
            label=label,
            password=password,
            can_reveal_password=password,
            border_color=PRIMARY_TEXT,
            focused_border_color=PRIMARY_TEXT,
            label_style=ft.TextStyle(color=PRIMARY_TEXT, size=12),
            text_style=ft.TextStyle(color=PRIMARY_TEXT),
            bgcolor=FORM_BG,
            height=45,
            content_padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
        )

    # ----------------------------------
    # PAGE NAVIGATION
    # ----------------------------------
    def show_front_page():
        page.clean()
        page.add(front_page_view)

    def show_signup_page():
        page.clean()
        page.add(signup_view)

    def show_login_page():
        page.clean()
        page.add(login_view)

    def logout(e=None):
        # IAS Log: Logout
        try:
            db.add_log("LOGOUT", details="User logged out", user_id=page.session.get("user_id"))
        except Exception:
            pass

        page.session.clear()
        show_front_page()

    # ----------------------------------
    # DASHBOARD (Tasks/Calendar/Settings)
    # ----------------------------------
    def show_dashboard():
        user_id = page.session.get("user_id")
        user_name = page.session.get("user_name")
        role = page.session.get("user_role")

        if not user_id:
            show_front_page()
            return

        current_view = {"name": "tasks"}  # state container

        # ---------- Helpers ----------
        def valid_due_date(s: str) -> bool:
            s = (s or "").strip()
            if not s:
                return True
            parts = s.split("-")
            if len(parts) != 3:
                return False
            y, m, d = parts
            return (
                len(y) == 4
                and len(m) == 2
                and len(d) == 2
                and y.isdigit()
                and m.isdigit()
                and d.isdigit()
            )

        # ---------- Main body container ----------
        content = ft.Container(expand=True, padding=20)

        # ---------- Header ----------
        def header():
            def nav_button(label: str, view_key: str):
                return ft.Container(
                    content=ft.Text(label, color=PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    border_radius=18,
                    bgcolor=BUTTON_COLOR if current_view["name"] == view_key else "white",
                    border=ft.border.all(1, PRIMARY_TEXT),
                    on_click=lambda e: switch_view(view_key),
                )

            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                        ft.Row(
                            controls=[
                                nav_button("Tasks", "tasks"),
                                nav_button("Calendar", "calendar"),
                                nav_button("Settings", "settings"),
                            ],
                            spacing=10,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(f"{user_name} ({role})", color=PRIMARY_TEXT),
                                ft.Container(
                                    content=ft.Text("Logout", color=PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                    bgcolor=BUTTON_COLOR,
                                    padding=ft.padding.symmetric(horizontal=18, vertical=8),
                                    border_radius=20,
                                    on_click=logout,
                                ),
                            ],
                            spacing=12,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                bgcolor=BG_COLOR,
            )

        # ---------- Tasks UI ----------
        task_title = styled_field("Task Title")
        task_desc = styled_field("Description")
        task_cat = styled_field("Category")
        task_due = styled_field("Due Date (YYYY-MM-DD)")

        tasks_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

        def clear_task_fields():
            task_title.value = ""
            task_desc.value = ""
            task_cat.value = ""
            task_due.value = ""

        def close_dialog():
            if page.dialog:
                page.dialog.open = False
                page.update()

        def refresh_tasks():
            tasks_list.controls.clear()
            tasks = db.get_tasks_by_user(user_id)

            if not tasks:
                tasks_list.controls.append(
                    ft.Text("No tasks yet. Add your first task!", color=SECONDARY_TEXT, size=14)
                )
                page.update()
                return

            for t in tasks:
                is_done = t["status"] == "completed"

                def on_toggle(task_id=t["id"]):
                    def handler(e):
                        db.toggle_task_status(user_id, task_id)
                        refresh_tasks()
                    return handler

                def on_delete(task_id=t["id"]):
                    def handler(e):
                        db.delete_task(user_id, task_id)
                        show_message("Task deleted.", color=SUCCESS_GREEN)
                        refresh_tasks()
                    return handler

                def on_edit(task=t):
                    def handler(e):
                        open_edit_dialog(task)
                    return handler

                title_style = ft.TextStyle(
                    color=PRIMARY_TEXT if not is_done else SECONDARY_TEXT,
                    decoration=ft.TextDecoration.LINE_THROUGH if is_done else None,
                )

                tasks_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Checkbox(value=is_done, on_change=on_toggle()),
                                ft.Column(
                                    controls=[
                                        ft.Text(t["title"], size=16, weight=ft.FontWeight.BOLD, style=title_style),
                                        ft.Text(t["description"] or "No description", size=12, color=SECONDARY_TEXT),
                                        ft.Row(
                                            controls=[
                                                ft.Container(
                                                    content=ft.Text(
                                                        t["category"] or "No category", size=11, color="white"
                                                    ),
                                                    bgcolor=LIGHT_PINK,
                                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                                    border_radius=12,
                                                ),
                                                ft.Text(
                                                    f"Due: {t['due_date']}" if t["due_date"] else "",
                                                    size=11,
                                                    color=SECONDARY_TEXT,
                                                ),
                                            ],
                                            spacing=10,
                                        ),
                                    ],
                                    expand=True,
                                    spacing=4,
                                ),
                                ft.IconButton(icon=ft.Icons.EDIT, icon_color=PRIMARY_TEXT, on_click=on_edit()),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=on_delete()),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        bgcolor=FORM_BG,
                        padding=14,
                        border_radius=12,
                    )
                )

            page.update()

        def add_task(e):
            title = (task_title.value or "").strip()
            desc = (task_desc.value or "").strip()
            cat = (task_cat.value or "").strip()
            due = (task_due.value or "").strip()

            if not title:
                show_message("Task title is required.")
                return

            if not valid_due_date(due):
                show_message("Due date must be YYYY-MM-DD (or leave it blank).")
                return

            db.add_task(user_id, title, desc, cat, due)
            clear_task_fields()
            show_message("Task added!", color=SUCCESS_GREEN)
            refresh_tasks()

        def open_edit_dialog(task):
            edit_title = styled_field("Rename")
            edit_desc = styled_field("Description")
            edit_cat = styled_field("Category")
            edit_due = styled_field("Due Date (YYYY-MM-DD)")

            edit_title.value = task["title"]
            edit_desc.value = task["description"] or ""
            edit_cat.value = task["category"] or ""
            edit_due.value = task["due_date"] or ""

            def save_changes(e):
                title = (edit_title.value or "").strip()
                desc = (edit_desc.value or "").strip()
                cat = (edit_cat.value or "").strip()
                due = (edit_due.value or "").strip()

                if not title:
                    show_message("Task title is required.")
                    return

                if not valid_due_date(due):
                    show_message("Due date must be YYYY-MM-DD (or leave it blank).")
                    return

                db.update_task(user_id, task["id"], title, desc, cat, due)
                close_dialog()
                show_message("Task updated!", color=SUCCESS_GREEN)
                refresh_tasks()

            page.dialog = ft.AlertDialog(
                title=ft.Text("Edit Task"),
                content=ft.Column(
                    controls=[edit_title, edit_desc, edit_cat, edit_due],
                    tight=True,
                    spacing=10,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                    ft.ElevatedButton("Save", on_click=save_changes, bgcolor=BUTTON_COLOR, color=PRIMARY_TEXT),
                ],
            )
            page.dialog.open = True
            page.update()

        tasks_view = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Add Task", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                            task_title,
                            task_desc,
                            task_cat,
                            task_due,
                            ft.ElevatedButton(
                                "Add Task",
                                on_click=add_task,
                                bgcolor=BUTTON_COLOR,
                                color=PRIMARY_TEXT,
                                width=200,
                                height=40,
                            ),
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=FORM_BG,
                    padding=20,
                    border_radius=14,
                    width=360,
                ),
                ft.Container(width=18),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("My Tasks", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                            tasks_list,
                        ],
                        spacing=10,
                        expand=True,
                    ),
                    bgcolor=BG_COLOR,
                    padding=10,
                    border_radius=14,
                    expand=True,
                ),
            ],
            expand=True,
        )

        calendar_view = ft.Container(
            content=ft.Text("Calendar View — Coming Soon", size=24, color=PRIMARY_TEXT),
            alignment=ft.alignment.center,
            expand=True,
        )

        settings_view = ft.Container(
            content=ft.Text("Settings View — Coming Soon", size=24, color=PRIMARY_TEXT),
            alignment=ft.alignment.center,
            expand=True,
        )

        def switch_view(name: str):
            current_view["name"] = name
            render()

        def render():
            page.clean()
            page.add(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            header(),
                            ft.Container(content=content, expand=True, bgcolor=BG_COLOR),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                    bgcolor=BG_COLOR,
                )
            )

            if current_view["name"] == "tasks":
                content.content = tasks_view
                refresh_tasks()
            elif current_view["name"] == "calendar":
                content.content = calendar_view
            else:
                content.content = settings_view

            page.update()

        render()

    # ----------------------------------
    # SIGNUP & LOGIN LOGIC
    # ----------------------------------
    name_field = styled_field("Name")
    email_field = styled_field("Email")
    password_field = styled_field("Password", password=True)
    confirm_password_field = styled_field("Confirm Password", password=True)

    login_email_field = styled_field("Email")
    login_password_field = styled_field("Password", password=True)

    def handle_signup(e):
        name = (name_field.value or "").strip()
        email = (email_field.value or "").strip().lower()
        pw = password_field.value or ""
        pw2 = confirm_password_field.value or ""

        if not name or not email or not pw or not pw2:
            show_message("Please fill in all fields.")
            return

        if pw != pw2:
            show_message("Passwords do not match.")
            return

        if len(pw) < 8:
            show_message("Password must be at least 8 characters.")
            return

        try:
            existing = db.get_user_by_email(email)
            if existing:
                show_message("An account with this email already exists.")
                return

            pw_hash = bcrypt.hash(pw)
            db.create_user(name, email, pw_hash)  # SAVES TO DB

            show_message("Account created! You can now log in.", color=SUCCESS_GREEN)
            show_login_page()

        except Exception as ex:
            show_message(f"Signup failed: {ex}")


    def handle_login(e):
        email = (login_email_field.value or "").strip().lower()
        pw = login_password_field.value or ""

        if not email or not pw:
            show_message("Please enter email and password.")
            return

        try:
            user = db.get_user_by_email(email)
            if not user:
                show_message("Invalid email or password.")
                return

            if not bcrypt.verify(pw, user["password_hash"]):
                show_message("Invalid email or password.")
                return

            # Session
            page.session.set("user_id", user["id"])
            page.session.set("user_name", user["name"])
            page.session.set("user_role", user["role"])

            show_message(f"Welcome, {user['name']}!", color=SUCCESS_GREEN)
            show_dashboard()

        except Exception as ex:
            show_message(f"Login failed: {ex}")

    # ----------------------------------
    # HEADERS
    # ----------------------------------
    def create_front_header():
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text("Log In", size=13, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                                bgcolor="white",
                                padding=ft.padding.symmetric(horizontal=25, vertical=8),
                                border_radius=20,
                                on_click=lambda e: show_login_page(),
                            ),
                            ft.Container(
                                content=ft.Text("Sign Up", size=13, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                                border=ft.border.all(2, PRIMARY_TEXT),
                                padding=ft.padding.symmetric(horizontal=25, vertical=8),
                                border_radius=20,
                                on_click=lambda e: show_signup_page(),
                            ),
                        ],
                        spacing=15,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            bgcolor=BG_COLOR,
        )

    def create_header():
        return ft.Container(
            content=ft.Row(
                controls=[ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT)],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=10,
            bgcolor=BG_COLOR,
        )

    # ----------------------------------
    # LOGIN / SIGNUP SIDE PANELS
    # ----------------------------------
    signup_sidebar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Log In", size=12, weight=ft.FontWeight.BOLD, color="white"),
                    bgcolor=PRIMARY_TEXT,
                    padding=10,
                    border_radius=20,
                    width=90,
                    alignment=ft.alignment.center,
                    on_click=lambda e: show_login_page(),
                ),
                ft.Container(
                    content=ft.Text(
                        "Create\nAccount",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    border=ft.border.all(2, PRIMARY_TEXT),
                    padding=8,
                    border_radius=20,
                    width=90,
                    height=55,
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=15,
    )

    login_sidebar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Log In", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                    border=ft.border.all(2, PRIMARY_TEXT),
                    padding=10,
                    border_radius=20,
                    width=90,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text("Create\nAccount", size=11, weight=ft.FontWeight.BOLD, color="white"),
                    bgcolor=PRIMARY_TEXT,
                    padding=8,
                    border_radius=20,
                    width=90,
                    height=55,
                    alignment=ft.alignment.center,
                    on_click=lambda e: show_signup_page(),
                ),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=15,
    )

    # ----------------------------------
    # FRONT PAGE VIEW
    # ----------------------------------
    front_page_view = ft.Container(
        content=ft.Column(
            controls=[
                create_front_header(),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Welcome to TaskWise", size=48, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                            ft.Text(
                                "Organize your tasks efficiently and boost your productivity",
                                size=18,
                                color=SECONDARY_TEXT,
                            ),
                            ft.Container(height=30),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            "Get Started",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=PRIMARY_TEXT,
                                        ),
                                        bgcolor=BUTTON_COLOR,
                                        padding=ft.padding.symmetric(horizontal=40, vertical=15),
                                        border_radius=25,
                                        on_click=lambda e: show_signup_page(),
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            "Learn More",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=PRIMARY_TEXT,
                                        ),
                                        border=ft.border.all(2, PRIMARY_TEXT),
                                        padding=ft.padding.symmetric(horizontal=40, vertical=15),
                                        border_radius=25,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                            ),
                            ft.Container(height=50),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Icon(ft.Icons.TASK_ALT, size=50, color="white"),
                                                ft.Text("Task Management", size=16, weight=ft.FontWeight.BOLD, color="white"),
                                                ft.Text(
                                                    "Organize and prioritize\nyour daily tasks",
                                                    size=12,
                                                    color="#4A707A",
                                                    text_align=ft.TextAlign.CENTER,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10,
                                        ),
                                        bgcolor=LIGHT_PINK,
                                        padding=30,
                                        border_radius=15,
                                        width=250,
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Icon(ft.Icons.CALENDAR_MONTH, size=50, color="white"),
                                                ft.Text("Calendar View", size=16, weight=ft.FontWeight.BOLD, color="white"),
                                                ft.Text(
                                                    "Track deadlines and\nschedule events",
                                                    size=12,
                                                    color="#4A707A",
                                                    text_align=ft.TextAlign.CENTER,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10,
                                        ),
                                        bgcolor=LIGHT_PINK,
                                        padding=30,
                                        border_radius=15,
                                        width=250,
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=50, color="white"),
                                                ft.Text("Smart Reminders", size=16, weight=ft.FontWeight.BOLD, color="white"),
                                                ft.Text(
                                                    "Never miss important\ntasks again",
                                                    size=12,
                                                    color="#4A707A",
                                                    text_align=ft.TextAlign.CENTER,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10,
                                        ),
                                        bgcolor=LIGHT_PINK,
                                        padding=30,
                                        border_radius=15,
                                        width=250,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            spacing=0,
        ),
        bgcolor=BG_COLOR,
        expand=True,
    )

    # ----------------------------------
    # SIGNUP PAGE
    # ----------------------------------
    signup_view = ft.Container(
        content=ft.Column(
            controls=[
                create_header(),
                ft.Container(
                    content=ft.Text("← Back", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                    padding=ft.padding.only(left=20, top=5),
                    on_click=lambda e: show_front_page(),
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Create Account", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                                            name_field,
                                            email_field,
                                            password_field,
                                            confirm_password_field,
                                            ft.ElevatedButton(
                                                "Sign Up",
                                                on_click=handle_signup,
                                                bgcolor=BUTTON_COLOR,
                                                color=PRIMARY_TEXT,
                                                width=200,
                                                height=40,
                                            ),
                                        ],
                                        spacing=10,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    padding=25,
                                    bgcolor=FORM_BG,
                                    border_radius=10,
                                    width=300,
                                    height=380,
                                ),
                                bgcolor=LIGHT_PINK,
                                padding=25,
                                border_radius=15,
                            ),
                            signup_sidebar,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                ),
            ],
            spacing=0,
        ),
        bgcolor=BG_COLOR,
        expand=True,
    )

    # ----------------------------------
    # LOGIN PAGE
    # ----------------------------------
    login_view = ft.Container(
        content=ft.Column(
            controls=[
                create_header(),
                ft.Container(
                    content=ft.Text("← Back", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                    padding=ft.padding.only(left=20, top=5, bottom=5),
                    on_click=lambda e: show_front_page(),
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Login", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                                            login_email_field,
                                            login_password_field,
                                            ft.ElevatedButton(
                                                "Login",
                                                on_click=handle_login,
                                                bgcolor=BUTTON_COLOR,
                                                color=PRIMARY_TEXT,
                                                width=200,
                                                height=40,
                                            ),
                                            ft.Container(
                                                content=ft.Text("Sign up", size=11, color=PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
                                                on_click=lambda e: show_signup_page(),
                                            ),
                                        ],
                                        spacing=10,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    padding=25,
                                    bgcolor=FORM_BG,
                                    border_radius=10,
                                    width=300,
                                    height=350,
                                ),
                                bgcolor=LIGHT_PINK,
                                padding=25,
                                border_radius=15,
                            ),
                            login_sidebar,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                ),
            ],
            spacing=0,
        ),
        bgcolor=BG_COLOR,
        expand=True,
    )

    # Load front page first
    show_front_page()


ft.app(target=main)
