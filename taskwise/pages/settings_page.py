import flet as ft
from taskwise.theme import THEMES

class SettingsPage:
    """
    SETTINGS PAGE (wireframe-matched)
    - IMPORTANT: No header here. app.py already renders the header.
    - Layout: centered big board -> inner card -> list tiles
    - Theme dropdown: Light Mode / Dark Mode / Pink (uses your THEMES via AppState.set_theme)
    - Account row shows signed-in user (if any)
    - Change Password + Logout use TaskPage's shared auth dialogs if you exposed hashing in state.
      If your Database already has change_password(), it will work.
    """

    def __init__(self, state):
        self.S = state

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        # -----------------------------
        # Helpers
        # -----------------------------
        def refresh():
            S.update()

        # -----------------------------
        # Dialogs
        # -----------------------------
        def show_account_dialog():
            name = S.user.get("name") if S.user else ""
            email = S.user.get("email") if S.user else ""

            content = ft.Column(
                [
                    ft.Text("Not signed in.", color=C("TEXT_SECONDARY"))
                    if not S.user
                    else ft.Column(
                        [
                            ft.Text(f"Name: {name}", color=C("TEXT_PRIMARY")),
                            ft.Text(f"Email: {email}", color=C("TEXT_SECONDARY")),
                        ],
                        spacing=6,
                    ),
                ],
                tight=True,
                spacing=10,
            )

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Account", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=420, content=content, padding=8),
                actions=[ft.TextButton("Close", on_click=lambda e: close_dialog(dlg))],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def close_dialog(dlg):
            dlg.open = False
            page.update()

        def hash_pw(s: str) -> str:
            # uses TaskPage-provided hash wrapper if available
            if hasattr(S, "_hash_pw"):
                return S._hash_pw(s)
            import hashlib
            return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

        def show_change_password_dialog():
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
            confirm_tf = ft.TextField(
                hint_text="Confirm Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def save(e):
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Please login first."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                row = db.get_user_by_email(S.user["email"])
                if not row:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account not found."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user_id, name, em, pw_hash = row
                if hash_pw(current_tf.value or "") != pw_hash:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Current password is wrong."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if (new_tf.value or "") != (confirm_tf.value or ""):
                    page.snack_bar = ft.SnackBar(content=ft.Text("Passwords do not match."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if not (new_tf.value or "").strip():
                    page.snack_bar = ft.SnackBar(content=ft.Text("New password is empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                db.change_password(user_id, hash_pw(new_tf.value))
                dlg.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Password updated."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Change Password", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=420,
                    padding=8,
                    content=ft.Column([current_tf, new_tf, confirm_tf], spacing=12, tight=True),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Save", on_click=save, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def do_logout():
            S.user = None
            page.snack_bar = ft.SnackBar(content=ft.Text("Logged out."), bgcolor=C("SUCCESS_COLOR"))
            page.snack_bar.open = True
            refresh()
            page.update()

        # -----------------------------
        # UI building blocks
        # -----------------------------
        def tile(text_left: str, right_control: ft.Control | None = None, on_click=None):
            return ft.Container(
                height=52,
                border_radius=14,
                border=ft.border.all(1.5, C("BORDER_COLOR")),
                bgcolor=C("BG_COLOR"),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                ink=True,
                on_click=on_click,
                content=ft.Row(
                    [
                        ft.Text(text_left, size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        right_control if right_control else ft.Icon(ft.Icons.CHEVRON_RIGHT, color=C("TEXT_SECONDARY")),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

        # Theme dropdown (wireframe-like)
        theme_dd = ft.Dropdown(
            value=S.theme_name if S.theme_name else "Light Mode",
            options=[
                ft.dropdown.Option("Light Mode"),
                ft.dropdown.Option("Dark Mode"),
                ft.dropdown.Option("Pink"),
            ],
            border=ft.InputBorder.NONE,
            filled=False,
            width=160,
            text_size=12,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
            on_change=lambda e: (S.set_theme(theme_dd.value), refresh()),
        )

        # -----------------------------
        # Center board layout (maximized like wireframe)
        # -----------------------------
        inner_card = ft.Container(
            width=520,
            border_radius=18,
            border=ft.border.all(2, C("BORDER_COLOR")),
            bgcolor=C("FORM_BG"),
            padding=22,
            content=ft.Column(
                [
                    ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                    ft.Container(height=10),

                    # Inner list box
                    ft.Container(
                        border_radius=16,
                        border=ft.border.all(2, C("BORDER_COLOR")),
                        bgcolor=C("BG_COLOR"),
                        padding=16,
                        content=ft.Column(
                            [
                                tile("Theme", right_control=theme_dd),
                                ft.Container(height=12),
                                tile("Account", on_click=lambda e: show_account_dialog()),
                                ft.Container(height=12),
                                tile("Change Password", on_click=lambda e: show_change_password_dialog()),
                                ft.Container(height=12),
                                tile("Logout", on_click=lambda e: do_logout()),
                            ],
                            spacing=0,
                        ),
                    ),
                ],
                spacing=0,
            ),
        )

        board = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(2, C("BORDER_COLOR")),
            bgcolor=C("BG_COLOR"),
            padding=28,
            content=ft.Row(
                [inner_card],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        # Outer wrapper (NO HEADER)
        return ft.Container(
            expand=True,
            bgcolor=C("BG_COLOR"),
            padding=ft.padding.all(18),
            content=board,
        )