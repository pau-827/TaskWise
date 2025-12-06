import flet as ft
from passlib.hash import bcrypt
import admin
import db
from taskwise.app import run_taskwise_app 


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
    # SNACKBAR FIXED
    # ----------------------------------
    def show_message(text: str, color="red"):
        snack = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=color,
            duration=2000,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # ----------------------------------
    # FORM FIELD
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
    # NAVIGATION HELPERS
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
        try:
            db.add_log("LOGOUT", details="User logged out", user_id=page.session.get("user_id"))
        except:
            pass
        page.session.clear()
        show_front_page()

    # ----------------------------------
    # SIGNUP LOGIC
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
            if db.get_user_by_email(email):
                show_message("Email is already registered.")
                return

            pw_hash = bcrypt.hash(pw)
            db.create_user(name, email, pw_hash)

            show_message("Account created! You can now log in.", SUCCESS_GREEN)
            show_login_page()

        except Exception as ex:
            show_message(f"Signup failed: {ex}")

    # ----------------------------------
    # ADMIN PANEL
    # ----------------------------------
    def show_admin():
        page.clean()
        logs = db.get_logs()

        log_list = ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"User ID: {log['user_id']}"),
                            ft.Text(f"Email: {log['email']}"),
                            ft.Text(f"Action: {log['action']}"),
                            ft.Text(f"Details: {log['details']}"),
                            ft.Text(f"Time: {log['created_at']}"),
                        ]
                    ),
                    bgcolor=FORM_BG,
                    padding=10,
                    border_radius=10,
                )
                for log in logs
            ],
            expand=True,
            spacing=10,
        )

        page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Admin Panel", size=22, weight="bold"),
                            ft.TextButton("Back", on_click=lambda e: show_front_page()),
                        ],
                        alignment="spaceBetween",
                    ),
                    ft.Container(log_list, expand=True),
                ],
                expand=True,
            )
        )
        page.update()

    # ----------------------------------
    # LOGIN LOGIC (FIXED)
    # ----------------------------------
    def handle_login(e):
        email = (login_email_field.value or "").strip().lower()
        pw = login_password_field.value or ""

        if not email or not pw:
            show_message("Please enter email and password.")
            return

        try:
            user = db.get_user_by_email(email)
            print("DEBUG USER RECORD:", user)
            print("INPUT PASSWORD:", pw)
            print("HASH IN DB:", user["password_hash"])
            print("VERIFY RESULT:", bcrypt.verify(pw, user["password_hash"]))


            if not user:
                show_message("Invalid email or password.")
                return

            # ✔ FIXED password verification
            if not bcrypt.verify(pw, user["password_hash"]):
                show_message("Invalid email or password.")
                return

            # ✔ Save session
            page.session.set("user_id", user["id"])
            page.session.set("user_name", user["name"])
            page.session.set("user_role", user["role"])

            # ✔ ADMIN REDIRECT (fixed)
            if user["role"] == "admin":
                print("ADMIN LOGIN → ADMIN PANEL")
                show_admin()
                return

            # ✔ USER REDIRECT (modular TaskWise)
            print("USER LOGIN → TASKWISE APP")
            run_taskwise_app(page)

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
    # FRONT PAGE VIEW (YOUR ORIGINAL UI)
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
                                            "Contact Admin",
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
    # SIGNUP VIEW (YOUR ORIGINAL)
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
    # LOGIN VIEW (YOUR ORIGINAL)
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

    # Start at main landing page
    show_front_page()


ft.app(target=main)