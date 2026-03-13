import flet as ft
from passlib.hash import bcrypt
import asyncio  # ✅ ADDED

from app.admin import get_admin_page
from app.vault import get_secret
from app.contact_admin import contact_admin_page

from database import db
from taskwise.app import run_taskwise_app


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
    # ✅ LOADING TIME SETTINGS (EDIT THESE)
    # -----------------------------
    APP_LOADING_SECONDS = 2.0     # loader when app opens
    LOGIN_LOADING_SECONDS = 2.0   # loader after login click

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

    # -----------------------------
    # Colors (existing)
    # -----------------------------
    BG_COLOR = "#F8F6F4"
    FORM_BG = "#E3F4F4"
    BUTTON_COLOR = "#D2E9E9"
    CARD_BG = "#C4DFDF"
    PRIMARY_TEXT = "#4A707A"
    SECONDARY_TEXT = "#6B8F97"
    SUCCESS_GREEN = "#4CAF50"

    # -----------------------------
    # ✅ PINK FRONT PAGE THEME (new)
    # -----------------------------
    PINK_BG = "#FFF1F6"
    PINK_SOFT = "#FFE4EF"
    PINK_CARD = "#FFD1E3"
    PINK_STRONG = "#FF4D8D"
    PINK_DARK = "#8A2E54"
    TEXT_DARK = "#3A2A33"
    TEXT_MUTED = "#6C5A65"

    # -----------------------------
    # ✅ GLOBAL LOADER OVERLAY (PERSISTS ACROSS VIEWS)
    # -----------------------------
    loader_overlay = ft.Container(
        visible=False,
        expand=True,
        bgcolor="#00000055",
        alignment=ft.alignment.center,
        content=ft.Container(
            padding=20,
            border_radius=16,
            bgcolor="white",
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Loading, please wait...", size=12, color=PRIMARY_TEXT),
                ],
            ),
        ),
    )
    _is_loading = False

    def show_loader():
        nonlocal _is_loading
        _is_loading = True
        loader_overlay.visible = True
        page.update()

    def hide_loader():
        nonlocal _is_loading
        _is_loading = False
        loader_overlay.visible = False
        page.update()

    if loader_overlay not in page.overlay:
        page.overlay.append(loader_overlay)

    # -----------------------------
    # Quick message popup (with suggestions)
    # -----------------------------
    def show_message(text: str, color="red", suggestion: str = None):
        full_text = text if not suggestion else f"{text}\n\nSuggestion: {suggestion}"
        snack = ft.SnackBar(content=ft.Text(full_text), bgcolor=color, duration=4000)
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
    # ✅ Small UI helpers (UPDATED TO PINK THEME)
    # -----------------------------
    def pill(text, icon):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            bgcolor="white",
            border_radius=999,
            border=ft.border.all(1, PINK_CARD),
            content=ft.Row(
                tight=True,
                spacing=6,
                controls=[
                    ft.Icon(icon, size=16, color=PINK_STRONG),
                    ft.Text(text, size=12, color=TEXT_DARK, weight=ft.FontWeight.W_600),
                ],
            ),
        )

    def hover_button(text, filled=True, on_click=None):
        btn = ft.Container(
            content=ft.Text(
                text,
                size=15,
                weight=ft.FontWeight.BOLD,
                color=("white" if filled else PINK_DARK),
            ),
            bgcolor=(PINK_STRONG if filled else "white"),
            border=None if filled else ft.border.all(2, PINK_STRONG),
            padding=ft.padding.symmetric(horizontal=28, vertical=14),
            border_radius=16,
            ink=True,
            on_click=on_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(blur_radius=14, color="#00000012", offset=ft.Offset(0, 7)),
        )

        def on_hover(e: ft.HoverEvent):
            if e.data == "true":
                btn.scale = 1.02
                btn.shadow = ft.BoxShadow(blur_radius=22, color="#0000001A", offset=ft.Offset(0, 11))
                if filled:
                    btn.bgcolor = "#FF2F78"
            else:
                btn.scale = 1.0
                btn.shadow = ft.BoxShadow(blur_radius=14, color="#00000012", offset=ft.Offset(0, 7))
                btn.bgcolor = (PINK_STRONG if filled else "white")
            page.update()

        btn.on_hover = on_hover
        return btn

    # ✅ UPDATED: feature card is pink + modern + hover animation
    def feature_card(title, subtitle, icon):
        card = ft.Container(
            expand=True,
            padding=20,
            border_radius=18,
            bgcolor="white",
            border=ft.border.all(1, PINK_CARD),
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(blur_radius=14, color="#00000010", offset=ft.Offset(0, 8)),
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=54,
                        height=54,
                        border_radius=16,
                        bgcolor=PINK_SOFT,
                        alignment=ft.alignment.center,
                        content=ft.Icon(icon, size=28, color=PINK_STRONG),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            ft.Text(subtitle, size=12, color=TEXT_MUTED),
                        ],
                    ),
                ],
            ),
        )

        def on_hover(e: ft.HoverEvent):
            if e.data == "true":
                card.bgcolor = "#FFF7FA"
                card.scale = 1.02
                card.shadow = ft.BoxShadow(blur_radius=22, color="#0000001A", offset=ft.Offset(0, 12))
            else:
                card.bgcolor = "white"
                card.scale = 1.0
                card.shadow = ft.BoxShadow(blur_radius=14, color="#00000010", offset=ft.Offset(0, 8))
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
    # Simple navigation helpers
    # -----------------------------
    def show_front_page():
        page.clean()
        page.add(build_front_page_view())
        page.run_task(front_page_animate_in)

    def show_signup_page():
        page.clean()
        page.add(signup_view)

    def show_login_page():
        page.clean()
        page.add(login_view)

    def show_contact_admin_page():
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
            show_message("Please fill in all fields.", suggestion="Double-check that you entered your name, email, and both passwords.")
            return

        if pw != pw2:
            show_message("Passwords do not match.", suggestion="Make sure both password fields are identical.")
            return

        if len(pw) < 8:
            show_message("Password must be at least 8 characters.", suggestion="Try adding numbers or symbols for stronger security.")
            return

        try:
            if db.get_user_by_email(email):
                show_message("Email is already registered.", suggestion="Try logging in instead, or use a different email.")
                return

            pw_hash = bcrypt.hash(pw)
            created = db.create_user(name, email, pw_hash)
            if not created:
                show_message("Account creation failed. Try again.", suggestion="Check your internet connection or try a different email.")
                return

            db.add_log("Signup", f"New user: {email}", None)
            show_message("Account created! You can now log in.", SUCCESS_GREEN, suggestion="Click 'Log In' to access your account.")
            show_login_page()

        except Exception as ex:
            show_message(f"Signup failed: {ex}", suggestion="Please retry or contact admin if the issue persists.")

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
                on_logout=logout,
            )
        )
        page.update()

    # -----------------------------
    # ✅ Login handler WITH LOADER
    # -----------------------------
    async def handle_login_async(e):
        nonlocal _is_loading
        if _is_loading:
            return

        email = (login_email_field.value or "").strip().lower()
        pw = login_password_field.value or ""

        if not email or not pw:
            show_message("Please enter email and password.", suggestion="Both fields are required to log in.")
            return

        show_loader()
        await asyncio.sleep(LOGIN_LOADING_SECONDS)

        try:
            user = db.get_user_by_email(email)

            if not user:
                hide_loader()
                show_message("Invalid email or password.", suggestion="Check for typos or sign up if you don’t have an account.")
                return

            if user.get("is_banned"):
                hide_loader()
                show_message("Your account is banned. Contact admin.", suggestion="Use the 'Contact Admin' option for support.")
                return

            if not bcrypt.verify(pw, user["password_hash"]):
                hide_loader()
                show_message("Invalid email or password.", suggestion="Try resetting your password if you forgot it.")
                return

            page.session.set("user_id", user["id"])
            page.session.set("user_name", user["name"])
            page.session.set("user_role", user["role"])

            db.add_log("Login", f"{user['email']} logged in", user_id=user["id"])

            if user["role"] == "admin":
                show_admin()
                hide_loader()
                return

            run_taskwise_app(
                page,
                on_logout=logout,
                user={"id": user["id"], "username": user["name"], "role": user["role"]},
            )

            hide_loader()

        except Exception as ex:
            hide_loader()
            show_message(f"Login failed: {ex}", suggestion="Please retry or contact admin if the issue persists.")

    # -----------------------------
    # Header builders
    # -----------------------------
    def create_front_header():
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=22, vertical=10),
            bgcolor=PINK_BG,  # ✅ pink
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=PINK_DARK),
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                ink=True,
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=22, vertical=8),
                                bgcolor="white",
                                border=ft.border.all(1, PINK_CARD),
                                on_click=lambda e: show_login_page(),
                                content=ft.Text("Log In", size=13, weight=ft.FontWeight.BOLD, color=PINK_DARK),
                            ),
                            ft.Container(
                                ink=True,
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=22, vertical=8),
                                bgcolor=PINK_STRONG,
                                on_click=lambda e: show_signup_page(),
                                content=ft.Text("Sign Up", size=13, weight=ft.FontWeight.BOLD, color="white"),
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
    # Side panels (unchanged)
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
    # ✅ FRONT PAGE (PINK + LIVELY + ANIMATED)
    # -----------------------------
    hero_wrap = ft.Container()
    right_card_wrap = ft.Container()
    features_wrap = ft.Container()

    hero_wrap.opacity = 0.0
    hero_wrap.offset = ft.Offset(0, 0.06)
    hero_wrap.animate_opacity = ft.Animation(350, ft.AnimationCurve.EASE_OUT)
    hero_wrap.animate_offset = ft.Animation(350, ft.AnimationCurve.EASE_OUT)

    right_card_wrap.opacity = 0.0
    right_card_wrap.offset = ft.Offset(0, 0.06)
    right_card_wrap.animate_opacity = ft.Animation(430, ft.AnimationCurve.EASE_OUT)
    right_card_wrap.animate_offset = ft.Animation(430, ft.AnimationCurve.EASE_OUT)

    features_wrap.opacity = 0.0
    features_wrap.offset = ft.Offset(0, 0.06)
    features_wrap.animate_opacity = ft.Animation(560, ft.AnimationCurve.EASE_OUT)
    features_wrap.animate_offset = ft.Animation(560, ft.AnimationCurve.EASE_OUT)

    async def front_page_animate_in():
        await asyncio.sleep(0.05)
        hero_wrap.opacity = 1.0
        hero_wrap.offset = ft.Offset(0, 0)
        page.update()

        await asyncio.sleep(0.08)
        right_card_wrap.opacity = 1.0
        right_card_wrap.offset = ft.Offset(0, 0)
        page.update()

        await asyncio.sleep(0.10)
        features_wrap.opacity = 1.0
        features_wrap.offset = ft.Offset(0, 0)
        page.update()

    def build_front_page_view():
        w = page.width or 1000
        pad_x = 16 if w < 700 else 32
        hero_size = 34 if w < 700 else 48
        hero_sub = 14 if w < 700 else 16

        hero_left = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=14,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=999,
                    bgcolor=PINK_SOFT,
                    border=ft.border.all(1, "#FFC1D9"),
                    content=ft.Row(
                        tight=True,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.AUTO_AWESOME, size=18, color=PINK_STRONG),
                            ft.Text("A cute way to stay on track", size=12, color=PINK_DARK, weight=ft.FontWeight.W_700),
                        ],
                    ),
                ),
                ft.Text(
                    "Plan Your Day Faster\nWith TaskWise",
                    size=hero_size,
                    weight=ft.FontWeight.BOLD,
                    color=PINK_DARK,
                ),
                ft.Text(
                    "Create tasks, set deadlines, and keep your week organized with a clean calendar and simple reminders.",
                    size=hero_sub,
                    color=TEXT_MUTED,
                ),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=10,
                    run_spacing=10,
                    controls=[
                        ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=pill("Fast Setup", ft.Icons.FLASH_ON_OUTLINED)),
                        ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=pill("Calendar View", ft.Icons.CALENDAR_MONTH_OUTLINED)),
                        ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=pill("Smart Reminders", ft.Icons.NOTIFICATIONS_OUTLINED)),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    wrap=True,
                    controls=[
                        hover_button("Create Account", True, lambda e: show_signup_page()),
                        hover_button("Contact Admin", False, lambda e: show_contact_admin_page()),
                    ],
                ),
                ft.Text("Sign up takes under a minute.", size=12, color=TEXT_MUTED),
            ],
        )

        preview_card = ft.Container(
            padding=18,
            border_radius=22,
            bgcolor="white",
            border=ft.border.all(1, PINK_CARD),
            shadow=ft.BoxShadow(blur_radius=18, spread_radius=1, color="#00000012", offset=ft.Offset(0, 10)),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        width=34,
                                        height=34,
                                        border_radius=12,
                                        bgcolor=PINK_SOFT,
                                        alignment=ft.alignment.center,
                                        content=ft.Icon(ft.Icons.CALENDAR_MONTH, color=PINK_STRONG),
                                    ),
                                    ft.Column(
                                        spacing=1,
                                        controls=[
                                            ft.Text("Today", size=13, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                            ft.Text("Quick glance", size=11, color=TEXT_MUTED),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                border_radius=999,
                                bgcolor=PINK_SOFT,
                                border=ft.border.all(1, "#FFC1D9"),
                                content=ft.Text("3 Tasks", size=12, color=PINK_DARK, weight=ft.FontWeight.W_700),
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=12,
                        border_radius=16,
                        bgcolor="#FFF7FA",
                        border=ft.border.all(1, "#FFE0EC"),
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(spacing=10, controls=[ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=PINK_STRONG),
                                                            ft.Text("Finish activity plan", color=TEXT_DARK, weight=ft.FontWeight.W_600)]),
                                ft.Row(spacing=10, controls=[ft.Icon(ft.Icons.SCHEDULE, color=PINK_DARK),
                                                            ft.Text("Review upcoming deadlines", color=TEXT_DARK, weight=ft.FontWeight.W_600)]),
                                ft.Row(spacing=10, controls=[ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=PINK_DARK),
                                                            ft.Text("Set reminder for tomorrow", color=TEXT_DARK, weight=ft.FontWeight.W_600)]),
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=12,
                        border_radius=16,
                        bgcolor="white",
                        border=ft.border.all(1, "#FFE0EC"),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Next reminder", size=12, color=TEXT_MUTED),
                                ft.Text("9:00 AM", size=12, color=PINK_DARK, weight=ft.FontWeight.BOLD),
                            ],
                        ),
                    ),
                ],
            ),
        )

        hero_wrap.content = hero_left
        right_card_wrap.content = preview_card

        features_wrap.content = ft.Column(
            spacing=14,
            controls=[
                ft.Text("What You Get", size=18, weight=ft.FontWeight.BOLD, color=PINK_DARK),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=18,
                    run_spacing=18,
                    controls=[
                        ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=feature_card(
                            "Task Management",
                            "Keep your plans simple and easy to follow.",
                            ft.Icons.TASK_ALT,
                        )),
                        ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=feature_card(
                            "Calendar View",
                            "See deadlines without digging through pages.",
                            ft.Icons.CALENDAR_MONTH,
                        )),
                        ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=feature_card(
                            "Smart Reminders",
                            "Stay notified so you do not miss tasks.",
                            ft.Icons.NOTIFICATIONS_ACTIVE,
                        )),
                    ],
                ),
            ],
        )

        return ft.Container(
            expand=True,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        expand=True,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[PINK_BG, "#FFE6F0", "#FFF7FB"],
                        ),
                    ),
                    ft.Container(left=-260, top=-190, width=520, height=520, border_radius=999, bgcolor="#F200FF"),
                    ft.Container(right=-280, top=60, width=600, height=600, border_radius=999, bgcolor="#FF0000AA"),
                    ft.Container(left=140, bottom=-280, width=520, height=520, border_radius=999, bgcolor="#FF00BF1F"),
                    ft.Container(right=100, bottom=-280, width=520, height=520, border_radius=999, bgcolor="#3474211F"),
                    ft.ListView(
                        expand=True,
                        spacing=0,
                        padding=0,
                        controls=[
                            create_front_header(),
                            ft.Container(
                                alignment=ft.alignment.top_center,
                                padding=ft.padding.symmetric(horizontal=pad_x, vertical=22),
                                content=ft.Container(
                                    width=1200,
                                    content=ft.Column(
                                        spacing=22,
                                        controls=[
                                            ft.ResponsiveRow(
                                                columns=12,
                                                spacing=22,
                                                run_spacing=22,
                                                controls=[
                                                    ft.Container(col={"xs": 12, "sm": 12, "md": 8}, content=hero_wrap),
                                                    ft.Container(col={"xs": 12, "sm": 12, "md": 4}, content=right_card_wrap),
                                                ],
                                            ),
                                            ft.Divider(height=10, color=ft.Colors.with_opacity(0.18, PINK_DARK)),
                                            features_wrap,
                                            ft.Container(height=10),
                                            ft.Container(
                                                alignment=ft.alignment.center,
                                                padding=ft.padding.only(bottom=18),
                                                content=ft.Text(
                                                    "TaskWise keeps your day clear, cute, and organized.",
                                                    size=12,
                                                    color=TEXT_MUTED,
                                                ),
                                            ),
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
                                                on_click=lambda e: page.run_task(handle_login_async, e),
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

    # -----------------------------
    # ✅ SHOW LOADER WHEN APP OPENS
    # -----------------------------
    async def app_boot():
        show_loader()
        await asyncio.sleep(APP_LOADING_SECONDS)
        hide_loader()
        show_front_page()

    page.run_task(app_boot)


ft.app(target=main, assets_dir="assets")