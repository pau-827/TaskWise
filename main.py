import flet as ft
from passlib.hash import bcrypt
from vault import get_secret  # secrets from .env / vault
import admin
import db
from taskwise.app import run_taskwise_app
from admin import get_admin_page


def main(page: ft.Page):
    # -----------------------------
    # Page setup
    # -----------------------------
    page.title = "TaskWise"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1000
    page.window_height = 600
    page.scroll = None

    # -----------------------------
    # Database startup
    # -----------------------------
    db.init_db()
    try:
        print("USING DB:", db.get_db_path())
    except:
        pass

    # -----------------------------
    # App secrets (safe defaults)
    # -----------------------------
    ADMIN_EMAIL = get_secret("ADMIN_EMAIL", "admin@taskwise.com")
    # Add more secrets here later if needed.

    # -----------------------------
    # Colors
    # -----------------------------
    BG_COLOR = "#F8F6F4"
    FORM_BG = "#E3F4F4"
    BUTTON_COLOR = "#D2E9E9"
    CARD_BG = "#C4DFDF"
    PRIMARY_TEXT = "#4A707A"
    SECONDARY_TEXT = "#6B8F97"
    SUCCESS_GREEN = "#4CAF50"

    # -----------------------------
    # Quick message popup
    # -----------------------------
    def show_message(text: str, color="red"):
        snack = ft.SnackBar(content=ft.Text(text), bgcolor=color, duration=2000)
        try:
            page.overlay.append(snack)
            snack.open = True
        except:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

    # -----------------------------
    # Reusable text field style
    # -----------------------------
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

    # -----------------------------
    # Small UI helpers
    # -----------------------------
    def pill(text, icon):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            bgcolor="white",
            border_radius=999,
            border=ft.border.all(1, "#D6E7E7"),
            content=ft.Row(
                tight=True,
                spacing=6,
                controls=[
                    ft.Icon(icon, size=16, color=PRIMARY_TEXT),
                    ft.Text(text, size=12, color=PRIMARY_TEXT, weight=ft.FontWeight.W_600),
                ],
            ),
        )

    def hover_button(text, filled=True, on_click=None):
        btn = ft.Container(
            content=ft.Text(text, size=15, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
            bgcolor=BUTTON_COLOR if filled else "white",
            border=None if filled else ft.border.all(2, PRIMARY_TEXT),
            padding=ft.padding.symmetric(horizontal=30, vertical=14),
            border_radius=16,
            ink=True,
            on_click=on_click,
            shadow=ft.BoxShadow(blur_radius=12, color="#00000010", offset=ft.Offset(0, 6)),
        )

        def on_hover(e: ft.HoverEvent):
            if e.data == "true":
                btn.shadow = ft.BoxShadow(blur_radius=20, color="#00000018", offset=ft.Offset(0, 10))
                if filled:
                    btn.bgcolor = "#C7E3E3"
            else:
                btn.shadow = ft.BoxShadow(blur_radius=12, color="#00000010", offset=ft.Offset(0, 6))
                btn.bgcolor = BUTTON_COLOR if filled else "white"
            page.update()

        btn.on_hover = on_hover
        return btn

    def feature_card(title, subtitle, icon):
        card = ft.Container(
            expand=True,
            bgcolor=CARD_BG,
            padding=22,
            border_radius=18,
            shadow=ft.BoxShadow(
                blur_radius=12,
                spread_radius=1,
                color="#00000010",
                offset=ft.Offset(0, 6),
            ),
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=64,
                        height=64,
                        border_radius=16,
                        bgcolor="#4A707A",
                        alignment=ft.alignment.center,
                        content=ft.Icon(icon, size=40, color="white"),
                    ),
                    ft.Text(
                        title,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="white",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        subtitle,
                        size=12,
                        color="#2F4F55",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

        def on_hover(e: ft.HoverEvent):
            if e.data == "true":
                card.bgcolor = "#BFE0E0"
                card.shadow = ft.BoxShadow(
                    blur_radius=20, spread_radius=2, color="#00000018", offset=ft.Offset(0, 10)
                )
            else:
                card.bgcolor = CARD_BG
                card.shadow = ft.BoxShadow(
                    blur_radius=12, spread_radius=1, color="#00000010", offset=ft.Offset(0, 6)
                )
            page.update()

        card.on_hover = on_hover
        return card

    # -----------------------------
    # Contact admin popup
    # -----------------------------
    def show_contact_admin_dialog(e=None):
        dlg = ft.AlertDialog(modal=True)
        page.dialog = dlg

        def close_dialog(_):
            dlg.open = False
            page.update()

        def copy_email(_):
            page.set_clipboard(ADMIN_EMAIL)
            show_message("Admin email copied to clipboard.", SUCCESS_GREEN)
            dlg.open = False
            page.update()

        dlg.title = ft.Text("Contact Admin", color=PRIMARY_TEXT, weight=ft.FontWeight.BOLD)
        dlg.content = ft.Column(
            tight=True,
            controls=[
                ft.Text("For account support, contact:", color=SECONDARY_TEXT),
                ft.Container(height=8),
                ft.Container(
                    padding=12,
                    bgcolor="white",
                    border_radius=12,
                    border=ft.border.all(1, "#D6E7E7"),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.MAIL_OUTLINE, color=PRIMARY_TEXT),
                            ft.Text(ADMIN_EMAIL, color=PRIMARY_TEXT, weight=ft.FontWeight.W_600),
                        ],
                    ),
                ),
            ],
        )
        dlg.actions = [
            ft.TextButton("Close", on_click=close_dialog),
            ft.ElevatedButton("Copy Email", on_click=copy_email, bgcolor=BUTTON_COLOR, color=PRIMARY_TEXT),
        ]

        dlg.open = True
        page.update()

    # -----------------------------
    # Switch into the main app UI
    # -----------------------------
    def switch_to_taskwise_app():
        try:
            page.views.clear()
        except:
            pass

        page.controls.clear()
        page.scroll = None
        page.padding = 0
        page.appbar = None
        page.navigation_bar = None
        page.floating_action_button = None
        page.drawer = None
        page.dialog = None

        try:
            page.overlay.clear()
        except:
            pass

        page.update()
        run_taskwise_app(page, on_logout=logout)

    # -----------------------------
    # Simple navigation helpers
    # -----------------------------
    def show_front_page():
        page.clean()
        page.add(front_page_view)

    def show_signup_page():
        page.clean()
        page.add(signup_view)

    def show_login_page():
        page.clean()
        page.add(login_view)

    def show_contact_admin_page():
        from contact_admin import contact_admin_page

        page.clean()
        ui = contact_admin_page(page, go_back_callback=show_front_page)
        page.add(ui)
        page.update()

    def logout(e=None):
        try:
            db.add_log("LOGOUT", "User logged out", page.session.get("user_id"))
        except:
            pass
        page.session.clear()
        show_front_page()

    # -----------------------------
    # Signup + login fields
    # -----------------------------
    name_field = styled_field("Name")
    email_field = styled_field("Email")
    password_field = styled_field("Password", password=True)
    confirm_password_field = styled_field("Confirm Password", password=True)

    login_email_field = styled_field("Email")
    login_password_field = styled_field("Password", password=True)

    # -----------------------------
    # Signup handler
    # -----------------------------
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
            created = db.create_user(name, email, pw_hash)
            if not created:
                show_message("Account creation failed. Try again.")
                return

            db.add_log("Signup", f"New user: {email}", None)

            show_message("Account created! You can now log in.", SUCCESS_GREEN)
            show_login_page()

        except Exception as ex:
            show_message(f"Signup failed: {ex}")

    # -----------------------------
    # Admin panel
    # -----------------------------
    def show_admin(e=None):
        page.clean()
        page.add(
            get_admin_page(
                page,
                PRIMARY_TEXT,
                SECONDARY_TEXT,
                BUTTON_COLOR,
                BG_COLOR,
                FORM_BG,
                on_logout=logout,  # logout callback
            )
        )
        page.update()

    # -----------------------------
    # Login handler
    # -----------------------------
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

            if user.get("is_banned"):
                show_message("Your account is banned. Contact admin.")
                return

            if not bcrypt.verify(pw, user["password_hash"]):
                show_message("Invalid email or password.")
                return

            page.session.set("user_id", user["id"])
            page.session.set("user_name", user["name"])
            page.session.set("user_role", user["role"])

            db.add_log("Login", f"{user['email']} logged in", user_id=user["id"])

            if user["role"] == "admin":
                print("ADMIN LOGIN → ADMIN PANEL")
                show_admin()
                return

            print("USER LOGIN → TASKWISE APP")
            run_taskwise_app(
                page,
                on_logout=logout,
                user={"id": user["id"], "username": user["name"], "role": user["role"]},
            )

        except Exception as ex:
            show_message(f"Login failed: {ex}")

    # -----------------------------
    # Header builders
    # -----------------------------
    def create_front_header():
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=22, vertical=10),
            bgcolor=BG_COLOR,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                ink=True,
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=22, vertical=8),
                                bgcolor="white",
                                on_click=lambda e: show_login_page(),
                                content=ft.Text("Log In", size=13, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                            ),
                            ft.Container(
                                ink=True,
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=22, vertical=8),
                                border=ft.border.all(2, PRIMARY_TEXT),
                                on_click=lambda e: show_signup_page(),
                                content=ft.Text("Sign Up", size=13, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def create_header():
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=22, vertical=10),
            bgcolor=BG_COLOR,
            content=ft.Row(
                controls=[ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT)],
            ),
        )

    # -----------------------------
    # Side panels
    # -----------------------------
    signup_sidebar = ft.Container(
        padding=15,
        content=ft.Column(
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Text("Log In", size=12, weight=ft.FontWeight.BOLD, color="white"),
                    bgcolor=PRIMARY_TEXT,
                    padding=10,
                    border_radius=20,
                    width=90,
                    alignment=ft.alignment.center,
                    ink=True,
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
        ),
    )

    login_sidebar = ft.Container(
        padding=15,
        content=ft.Column(
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                    ink=True,
                    on_click=lambda e: show_signup_page(),
                ),
            ],
        ),
    )

    # -----------------------------
    # Front page (scrollable)
    # -----------------------------
    front_page_view = ft.Container(
        expand=True,
        content=ft.Stack(
            expand=True,
            controls=[
                # Background gradient
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=["#F8F6F4", "#EAF6F6", "#F8F6F4"],
                    ),
                ),
                # Decorative circles
                ft.Container(
                    left=-220,
                    top=-170,
                    width=520,
                    height=520,
                    border_radius=999,
                    bgcolor="#D2E9E955",
                ),
                ft.Container(
                    right=-260,
                    top=40,
                    width=600,
                    height=600,
                    border_radius=999,
                    bgcolor="#C4DFDF55",
                ),
                # Main content
                ft.ListView(
                    expand=True,
                    spacing=0,
                    padding=0,
                    controls=[
                        create_front_header(),
                        ft.Container(
                            alignment=ft.alignment.top_center,
                            padding=ft.padding.symmetric(horizontal=32, vertical=20),
                            content=ft.Container(
                                width=1400,
                                content=ft.Column(
                                    spacing=24,
                                    controls=[
                                        # HERO
                                        ft.ResponsiveRow(
                                            columns=12,
                                            spacing=24,
                                            run_spacing=24,
                                            controls=[
                                                # LEFT
                                                ft.Container(
                                                    col={"xs": 12, "sm": 12, "md": 8, "lg": 8, "xl": 8},
                                                    content=ft.Column(
                                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                                        spacing=14,
                                                        controls=[
                                                            ft.Text(
                                                                "Plan Your Day Faster\nWith TaskWise",
                                                                size=46,
                                                                weight=ft.FontWeight.BOLD,
                                                                color=PRIMARY_TEXT,
                                                            ),
                                                            ft.Text(
                                                                "Create tasks, set deadlines, and stay on track with reminders that keep things simple.",
                                                                size=16,
                                                                color=SECONDARY_TEXT,
                                                            ),
                                                            ft.ResponsiveRow(
                                                                columns=12,
                                                                spacing=10,
                                                                run_spacing=10,
                                                                controls=[
                                                                    ft.Container(
                                                                        col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4},
                                                                        content=pill("Fast Setup", ft.Icons.FLASH_ON_OUTLINED),
                                                                    ),
                                                                    ft.Container(
                                                                        col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4},
                                                                        content=pill("Calendar View", ft.Icons.CALENDAR_MONTH_OUTLINED),
                                                                    ),
                                                                    ft.Container(
                                                                        col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4},
                                                                        content=pill("Smart Reminders", ft.Icons.NOTIFICATIONS_OUTLINED),
                                                                    ),
                                                                ],
                                                            ),
                                                            ft.Row(
                                                                spacing=14,
                                                                controls=[
                                                                    hover_button("Create Account", True, lambda e: show_signup_page()),
                                                                    hover_button("Contact Admin", False, lambda e: show_contact_admin_page()),
                                                                ],
                                                            ),
                                                            ft.Text(
                                                                "No credit card needed. Sign up takes under a minute.",
                                                                size=12,
                                                                color="#6E8D94",
                                                            ),
                                                        ],
                                                    ),
                                                ),
                                                # RIGHT PREVIEW CARD
                                                ft.Container(
                                                    col={"xs": 12, "sm": 12, "md": 4, "lg": 4, "xl": 4},
                                                    content=ft.Container(
                                                        padding=18,
                                                        border_radius=22,
                                                        bgcolor="white",
                                                        border=ft.border.all(1, "#D6E7E7"),
                                                        shadow=ft.BoxShadow(
                                                            blur_radius=16,
                                                            spread_radius=1,
                                                            color="#00000014",
                                                            offset=ft.Offset(0, 8),
                                                        ),
                                                        content=ft.Column(
                                                            spacing=12,
                                                            controls=[
                                                                ft.Row(
                                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                                    controls=[
                                                                        ft.Text(
                                                                            "Today",
                                                                            size=14,
                                                                            weight=ft.FontWeight.BOLD,
                                                                            color=PRIMARY_TEXT,
                                                                        ),
                                                                        ft.Container(
                                                                            padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                                                            border_radius=999,
                                                                            bgcolor=FORM_BG,
                                                                            content=ft.Text("3 Tasks", size=12, color=PRIMARY_TEXT),
                                                                        ),
                                                                    ],
                                                                ),
                                                                ft.Container(
                                                                    padding=12,
                                                                    border_radius=16,
                                                                    bgcolor=FORM_BG,
                                                                    content=ft.Column(
                                                                        spacing=10,
                                                                        controls=[
                                                                            ft.Row(
                                                                                spacing=10,
                                                                                controls=[
                                                                                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=SUCCESS_GREEN),
                                                                                    ft.Text("Finish activity plan", color=PRIMARY_TEXT, weight=ft.FontWeight.W_600),
                                                                                ],
                                                                            ),
                                                                            ft.Row(
                                                                                spacing=10,
                                                                                controls=[
                                                                                    ft.Icon(ft.Icons.SCHEDULE, color=PRIMARY_TEXT),
                                                                                    ft.Text("Review upcoming deadlines", color=PRIMARY_TEXT, weight=ft.FontWeight.W_600),
                                                                                ],
                                                                            ),
                                                                            ft.Row(
                                                                                spacing=10,
                                                                                controls=[
                                                                                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=PRIMARY_TEXT),
                                                                                    ft.Text("Set reminder for tomorrow", color=PRIMARY_TEXT, weight=ft.FontWeight.W_600),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ),
                                                                ft.Container(
                                                                    padding=12,
                                                                    border_radius=16,
                                                                    bgcolor="#F7FBFB",
                                                                    border=ft.border.all(1, "#E0EEEE"),
                                                                    content=ft.Row(
                                                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                                        controls=[
                                                                            ft.Text("Next reminder", size=12, color=SECONDARY_TEXT),
                                                                            ft.Text(
                                                                                "9:00 AM",
                                                                                size=12,
                                                                                color=PRIMARY_TEXT,
                                                                                weight=ft.FontWeight.BOLD,
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ),
                                                            ],
                                                        ),
                                                    ),
                                                ),
                                            ],
                                        ),
                                        ft.Container(height=20),
                                        # "What You Get" header
                                        ft.Row(
                                            controls=[
                                                ft.Container(
                                                    expand=True,
                                                    content=ft.Text(
                                                        "What You Get",
                                                        size=18,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=PRIMARY_TEXT,
                                                    ),
                                                ),
                                            ],
                                        ),
                                        # Feature Cards
                                        ft.ResponsiveRow(
                                            columns=12,
                                            spacing=22,
                                            run_spacing=22,
                                            controls=[
                                                ft.Container(
                                                    col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4},
                                                    content=feature_card(
                                                        "Task Management",
                                                        "Sort your work by priority and keep each day clear.",
                                                        ft.Icons.TASK_ALT,
                                                    ),
                                                ),
                                                ft.Container(
                                                    col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4},
                                                    content=feature_card(
                                                        "Calendar View",
                                                        "See deadlines and plans without digging through menus.",
                                                        ft.Icons.CALENDAR_MONTH,
                                                    ),
                                                ),
                                                ft.Container(
                                                    col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4},
                                                    content=feature_card(
                                                        "Smart Reminders",
                                                        "Get timely nudges so tasks do not slip through.",
                                                        ft.Icons.NOTIFICATIONS_ACTIVE,
                                                    ),
                                                ),
                                            ],
                                        ),
                                        ft.Container(height=18),
                                    ],
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    # -----------------------------
    # Signup view
    # -----------------------------
    signup_view = ft.Container(
        bgcolor=BG_COLOR,
        expand=True,
        content=ft.ListView(
            expand=True,
            padding=0,
            controls=[
                create_header(),
                ft.Container(
                    content=ft.Text("← Back", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                    padding=ft.padding.only(left=20, top=5),
                    on_click=lambda e: show_front_page(),
                ),
                ft.Container(
                    padding=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                bgcolor=CARD_BG,
                                padding=25,
                                border_radius=15,
                                content=ft.Container(
                                    width=320,
                                    padding=25,
                                    bgcolor=FORM_BG,
                                    border_radius=10,
                                    content=ft.Column(
                                        spacing=10,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                                    ),
                                ),
                            ),
                            signup_sidebar,
                        ],
                    ),
                ),
            ],
        ),
    )

    # -----------------------------
    # Login view
    # -----------------------------
    login_view = ft.Container(
        bgcolor=BG_COLOR,
        expand=True,
        content=ft.ListView(
            expand=True,
            padding=0,
            controls=[
                create_header(),
                ft.Container(
                    content=ft.Text("← Back", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                    padding=ft.padding.only(left=20, top=5, bottom=5),
                    on_click=lambda e: show_front_page(),
                ),
                ft.Container(
                    padding=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                bgcolor=CARD_BG,
                                padding=25,
                                border_radius=15,
                                content=ft.Container(
                                    width=320,
                                    padding=25,
                                    bgcolor=FORM_BG,
                                    border_radius=10,
                                    content=ft.Column(
                                        spacing=10,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                                    ),
                                ),
                            ),
                            login_sidebar,
                        ],
                    ),
                ),
            ],
        ),
    )

    # start at the landing page
    show_front_page()


ft.app(target=main, assets_dir="assets")
