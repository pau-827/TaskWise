import flet as ft
from taskwise.theme import THEMES


class SettingsPage:
    def __init__(self, state):
        self.S = state  # AppState

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        # Short color alias
        def C(k): 
            return S.colors[k]

        # ============================================================
        # HEADER
        # ============================================================
        def header():
            def nav(view): 
                return lambda e: S.go(view)

            def tab(label, key):
                active = (S.current_view == key)
                txt = f"✱ {label} ✱" if active else label
                return ft.TextButton(
                    txt, 
                    on_click=nav(key),
                    style=ft.ButtonStyle(color=C("TEXT_PRIMARY"))
                )

            return ft.Container(
                bgcolor=C("HEADER_BG"),
                padding=ft.padding.symmetric(horizontal=24, vertical=14),
                border=ft.border.only(bottom=ft.BorderSide(1, C("BORDER_COLOR"))),
                content=ft.Row(
                    [
                        ft.Text("TaskWise", size=18, weight="bold", color=C("TEXT_PRIMARY")),
                        ft.Row([tab("Tasks", "tasks"), tab("Calendar", "calendar"), tab("Settings", "settings")], spacing=8),
                        build_account_menu(),
                    ],
                    alignment="spaceBetween"
                ),
            )

        # ============================================================
        # ACCOUNT MENU (Login, Create Account, Logout)
        # ============================================================
        def build_account_menu():

            # --- LOGOUT ---
            def do_logout(e):
                S.user = None
                page.snack_bar = ft.SnackBar(content=ft.Text("Logged out"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                refresh()

            # --- LOGIN DIALOG ---
            def show_login():
                email = ft.TextField(label="Email", filled=True, bgcolor=C("BG_COLOR"), border_color=C("BORDER_COLOR"))
                pw = ft.TextField(
                    label="Password",
                    password=True,
                    can_reveal_password=True,
                    filled=True,
                    bgcolor=C("BG_COLOR"),
                    border_color=C("BORDER_COLOR")
                )

                def login(e):
                    em = (email.value or "").strip().lower()
                    row = db.get_user_by_email(em)

                    if not row:
                        page.snack_bar = ft.SnackBar(content=ft.Text("Account not found"), bgcolor=C("ERROR_COLOR"))
                        page.snack_bar.open = True
                        return

                    uid, uname, uemail, pw_hash = row
                    if S._hash_pw(pw.value or "") != pw_hash:
                        page.snack_bar = ft.SnackBar(content=ft.Text("Wrong password"), bgcolor=C("ERROR_COLOR"))
                        page.snack_bar.open = True
                        return

                    S.user = {"id": uid, "name": uname, "email": uemail}
                    dialog.open = False
                    page.update()
                    refresh()

                dialog = ft.AlertDialog(
                    modal=True,
                    bgcolor=C("FORM_BG"),
                    title=ft.Text("Login", size=18, weight="bold", color=C("TEXT_PRIMARY")),
                    content=ft.Column([email, pw], tight=True, spacing=10),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
                        ft.ElevatedButton("Login", on_click=login, bgcolor=C("BUTTON_COLOR"), color="white")
                    ]
                )

                page.overlay.append(dialog)
                dialog.open = True
                page.update()

            # --- CREATE ACCOUNT ---
            def show_create_account():
                name = ft.TextField(label="Name", filled=True, bgcolor=C("BG_COLOR"))
                email = ft.TextField(label="Email", filled=True, bgcolor=C("BG_COLOR"))
                pw = ft.TextField(
                    label="Password",
                    password=True,
                    can_reveal_password=True,
                    filled=True,
                    bgcolor=C("BG_COLOR")
                )

                def create(e):
                    nm = name.value.strip()
                    em = email.value.strip().lower()
                    pwv = pw.value.strip()

                    if not (nm and em and pwv):
                        page.snack_bar = ft.SnackBar(content=ft.Text("All fields required"), bgcolor=C("ERROR_COLOR"))
                        page.snack_bar.open = True
                        return

                    if db.get_user_by_email(em):
                        page.snack_bar = ft.SnackBar(content=ft.Text("Email already exists"), bgcolor=C("ERROR_COLOR"))
                        page.snack_bar.open = True
                        return

                    db.create_user(nm, em, S._hash_pw(pwv))

                    dialog.open = False
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account created!"), bgcolor=C("SUCCESS_COLOR"))
                    page.snack_bar.open = True
                    page.update()

                dialog = ft.AlertDialog(
                    modal=True,
                    bgcolor=C("FORM_BG"),
                    title=ft.Text("Create Account", size=18, weight="bold", color=C("TEXT_PRIMARY")),
                    content=ft.Column([name, email, pw], tight=True, spacing=10),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
                        ft.ElevatedButton("Create", on_click=create, bgcolor=C("BUTTON_COLOR"), color="white")
                    ]
                )

                page.overlay.append(dialog)
                dialog.open = True
                page.update()

            # --- CHANGE PASSWORD ---
            def show_change_password():
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("You must login first"), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    return

                cur = ft.TextField(label="Current Password", password=True, can_reveal_password=True)
                new1 = ft.TextField(label="New Password", password=True, can_reveal_password=True)
                new2 = ft.TextField(label="Confirm Password", password=True, can_reveal_password=True)

                def change(e):
                    row = db.get_user_by_email(S.user["email"])
                    uid, name, email, pw_hash = row

                    if S._hash_pw(cur.value or "") != pw_hash:
                        page.snack_bar = ft.SnackBar(content=ft.Text("Wrong current password"), bgcolor=C("ERROR_COLOR"))
                        page.snack_bar.open = True
                        return

                    if (new1.value or "") != (new2.value or ""):
                        page.snack_bar = ft.SnackBar(content=ft.Text("Passwords do not match"), bgcolor=C("ERROR_COLOR"))
                        page.snack_bar.open = True
                        return

                    db.change_password(uid, S._hash_pw(new1.value))
                    dialog.open = False
                    page.snack_bar = ft.SnackBar(content=ft.Text("Password updated!"), bgcolor=C("SUCCESS_COLOR"))
                    page.snack_bar.open = True
                    page.update()

                dialog = ft.AlertDialog(
                    modal=True,
                    bgcolor=C("FORM_BG"),
                    title=ft.Text("Change Password", size=18, weight="bold", color=C("TEXT_PRIMARY")),
                    content=ft.Column([cur, new1, new2], tight=True, spacing=10),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
                        ft.ElevatedButton("Update", on_click=change, bgcolor=C("BUTTON_COLOR"), color="white")
                    ]
                )

                page.overlay.append(dialog)
                dialog.open = True
                page.update()

            # Build account button
            if not S.user:
                return ft.PopupMenuButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    items=[
                        ft.PopupMenuItem(text="Login", on_click=lambda e: show_login()),
                        ft.PopupMenuItem(text="Create Account", on_click=lambda e: show_create_account()),
                    ]
                )

            return ft.PopupMenuButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                items=[
                    ft.PopupMenuItem(text=f"Signed in as {S.user['name']}"),
                    ft.PopupMenuItem(text="Change Password", on_click=lambda e: show_change_password()),
                    ft.PopupMenuItem(text="Logout", on_click=do_logout),
                ]
            )

        # Helper to close dialogs
        def close_dialog(d):
            d.open = False
            page.update()

        # ============================================================
        # THEME SELECTOR
        # ============================================================
        theme_picker = ft.Dropdown(
            value=S.theme_name,
            options=[ft.dropdown.Option(t) for t in THEMES.keys()],
            width=200,
            border_color=C("BORDER_COLOR"),
            bgcolor=C("BG_COLOR"),
            filled=True,
            color=C("TEXT_PRIMARY"),
        )

        def change_theme(e):
            S.theme_name = theme_picker.value
            S.colors = THEMES[theme_picker.value].copy()
            db.set_setting("theme_name", S.theme_name)
            refresh()

        theme_picker.on_change = change_theme

        # ============================================================
        # MAIN SETTINGS PANEL
        # ============================================================
        def settings_panel():
            return ft.Container(
                bgcolor=C("FORM_BG"),
                border_radius=16,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=24,
                expand=True,
                content=ft.Column(
                    [
                        ft.Text("Settings", size=20, weight="bold", color=C("TEXT_PRIMARY")),
                        ft.Container(height=12),

                        ft.Text("Theme", size=14, weight="bold", color=C("TEXT_PRIMARY")),
                        ft.Container(height=6),
                        theme_picker,
                    ],
                    spacing=10
                )
            )

        # ============================================================
        # Refresh UI
        # ============================================================
        def refresh():
            if S._update_callback:
                S._update_callback()
            page.update()

        # ============================================================
        # FINAL LAYOUT
        # ============================================================
        layout = ft.Column(
            [
                header(),
                ft.Container(
                    padding=20,
                    content=settings_panel(),
                    expand=True,
                )
            ],
            expand=True,
        )

        return layout
