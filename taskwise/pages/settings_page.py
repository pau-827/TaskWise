import flet as ft
from taskwise.theme import THEMES
from passlib.hash import bcrypt


class SettingsPage:
    """
    Settings page (wireframe-friendly, updated for the current db.py)
    """

    def __init__(self, state):
        self.S = state

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        # -----------------------------
        # Theme color shortcut
        # -----------------------------
        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        def refresh():
            # ask TaskWiseApp to re-render using the callback
            if hasattr(S, "_update_callback") and callable(S._update_callback):
                S._update_callback()
            else:
                page.update()


        # -----------------------------
        # Get the current user safely
        # -----------------------------
        def get_user_profile() -> dict:
            # Default values when no user is logged in
            profile = {"id": None, "username": "Guest", "name": "Guest", "email": "Not signed in", "role": ""}

            if not S.user:
                return profile

            # Pull what we can from the session user object first
            if isinstance(S.user, dict):
                profile["id"] = S.user.get("id")
                profile["role"] = S.user.get("role", "")
                profile["username"] = S.user.get("username") or profile["username"]
                profile["name"] = S.user.get("name") or profile["username"] or profile["name"]
                profile["email"] = S.user.get("email") or profile["email"]

            # Try to refresh from DB (covers edge cases where session data is incomplete)
            try:
                user_row = None

                # Best option: fetch by id
                if profile["id"] is not None:
                    if hasattr(db, "get_user_by_id"):
                        user_row = db.get_user_by_id(profile["id"])
                    elif hasattr(db, "get_user"):
                        user_row = db.get_user(profile["id"])

                # Fallback: fetch by username
                if user_row is None and profile["username"] and hasattr(db, "get_user_by_username"):
                    user_row = db.get_user_by_username(profile["username"])

                # Fallback: fetch by email
                if (
                    user_row is None
                    and profile.get("email") not in (None, "", "Not signed in")
                    and hasattr(db, "get_user_by_email")
                ):
                    user_row = db.get_user_by_email(profile["email"])

                # Normalize whatever format the DB returns (dict or tuple)
                if user_row:
                    if isinstance(user_row, dict):
                        profile["id"] = user_row.get("id", profile["id"])
                        profile["email"] = user_row.get("email") or profile["email"]
                        profile["name"] = user_row.get("name") or user_row.get("username") or profile["name"]
                        profile["username"] = user_row.get("username") or profile["username"]
                        profile["role"] = user_row.get("role", profile["role"])
                    else:
                        profile["id"] = user_row[0] if len(user_row) > 0 else profile["id"]
                        if len(user_row) > 1 and user_row[1]:
                            profile["username"] = user_row[1]
                            profile["name"] = user_row[1]
                        if len(user_row) > 2 and user_row[2]:
                            profile["email"] = user_row[2]
                        if len(user_row) > 4 and user_row[4]:
                            profile["role"] = user_row[4]
            except Exception:
                # Keep UI stable even if DB lookup fails
                pass

            return profile

        profile = get_user_profile()

        # -----------------------------
        # Dialog close helper
        # -----------------------------
        def close_dialog(dlg):
            dlg.open = False
            page.update()

        # -----------------------------
        # Account details dialog
        # -----------------------------
        def show_account_dialog():
            p = get_user_profile()
            if not S.user:
                content = ft.Text("Not signed in.", color=C("TEXT_SECONDARY"))
            else:
                name_val = (p.get("name") or p.get("username") or "Unknown").strip() or "Unknown"
                email_val = (p.get("email") or "").strip() or "Unknown"
                content = ft.Column(
                    [
                        ft.Text(f"Name: {name_val}", color=C("TEXT_PRIMARY")),
                        ft.Text(f"Email: {email_val}", color=C("TEXT_SECONDARY")),
                    ],
                    spacing=6,
                )

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Account", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=420,
                    height=20,
                    content=content,
                    padding=8,
                ),
                actions=[ft.TextButton("Close", on_click=lambda e: close_dialog(dlg))],
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # -----------------------------
        # Delete account (password confirmation)
        # -----------------------------
        def confirm_delete_account():
            p = get_user_profile()
            if not S.user or not p.get("id"):
                page.snack_bar = ft.SnackBar(content=ft.Text("Please login first."), bgcolor=C("ERROR_COLOR"))
                page.snack_bar.open = True
                page.update()
                return

            password_field = ft.TextField(
                hint_text="Enter your password to confirm",
                password=True,
                can_reveal_password=True,
                filled=True,
                width=400,
            )

            def close_dlg(e):
                dlg.open = False
                page.update()

            def do_delete(e):
                # Require password input
                if not password_field.value or not password_field.value.strip():
                    page.snack_bar = ft.SnackBar(content=ft.Text("Please enter your password."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                # Pull the latest user record for verification
                user = None
                try:
                    if hasattr(db, "get_user_by_id"):
                        user = db.get_user_by_id(p["id"])
                    elif hasattr(db, "get_user"):
                        user = db.get_user(p["id"])
                except Exception:
                    pass

                if not user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account not found."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                # Extract password hash (supports dict or tuple returns)
                password_hash = None
                if isinstance(user, dict):
                    password_hash = user.get("password_hash") or user.get("password")
                else:
                    password_hash = user[3] if len(user) > 3 else None
                    if not password_hash:
                        for v in user:
                            if isinstance(v, str) and v.startswith("$2"):
                                password_hash = v
                                break

                # Validate password
                if not password_hash or not bcrypt.verify(password_field.value, password_hash):
                    page.snack_bar = ft.SnackBar(content=ft.Text("Incorrect password."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                # Delete the user and their related data
                try:
                    if hasattr(db, "delete_user"):
                        db.delete_user(p["id"])
                    else:
                        page.snack_bar = ft.SnackBar(content=ft.Text("Delete function not available."), bgcolor=C("ERROR_COLOR"))
                        page.snack_bar.open = True
                        page.update()
                        return
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Delete failed: {str(ex)}"), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                dlg.open = False
                page.update()

                # Logout / clear user state after delete
                try:
                    if hasattr(S, "on_user_logout"):
                        S.on_user_logout()
                except Exception:
                    S.user = None

                page.snack_bar = ft.SnackBar(content=ft.Text("Account deleted successfully."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

                # Try to navigate to a reasonable page name
                def safe_go(name: str) -> bool:
                    try:
                        if hasattr(S, "go"):
                            S.go(name)
                            return True
                    except Exception:
                        return False
                    return False

                for target in ("loginpage", "login", "startpage", "mainpage"):
                    if safe_go(target):
                        break

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Delete Account", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=450,
                    padding=8,
                    height=180,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text(
                                "⚠️ Warning: This action cannot be undone!",
                                color=C("ERROR_COLOR"),
                                weight=ft.FontWeight.BOLD,
                                size=14,
                            ),
                            ft.Text(
                                "All your data, tasks, and settings will be permanently deleted.",
                                color=C("TEXT_SECONDARY"),
                                size=12,
                            ),
                            ft.Divider(height=1, color=C("BORDER_COLOR")),
                            password_field,
                        ],
                    ),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dlg),
                    ft.ElevatedButton("Delete My Account", on_click=do_delete, bgcolor=C("ERROR_COLOR"), color="white"),
                ],
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # -----------------------------
        # Change password dialog
        # -----------------------------
        def show_change_password_dialog():
            current_tf = ft.TextField(
                hint_text="Current Password",
                password=True,
                can_reveal_password=True,
                filled=True,
            )
            new_tf = ft.TextField(
                hint_text="New Password",
                password=True,
                can_reveal_password=True,
                filled=True,
            )
            confirm_tf = ft.TextField(
                hint_text="Confirm Password",
                password=True,
                can_reveal_password=True,
                filled=True,
            )

            def toast(msg: str, color_key: str = "ERROR_COLOR"):
                page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=C(color_key))
                page.snack_bar.open = True
                page.update()

            def _extract_user_id_and_hash(user_obj, fallback_id):
                # dict format
                if isinstance(user_obj, dict):
                    uid = user_obj.get("id", fallback_id)
                    ph = user_obj.get("password_hash") or user_obj.get("password")
                    return uid, ph

                # tuple/list format
                uid = user_obj[0] if len(user_obj) > 0 else fallback_id

                # common index used in your code
                ph = user_obj[3] if len(user_obj) > 3 else None

                # fallback: find bcrypt hash in any column
                if not ph:
                    for v in user_obj:
                        if isinstance(v, str) and v.startswith("$2"):
                            ph = v
                            break

                return uid, ph

            def _update_password_in_db(user_id: int, new_hash: str) -> bool:
                """
                Tries common db function names.
                Return True if any update method works.
                """
                # Most likely in your project
                if hasattr(db, "update_user_password"):
                    db.update_user_password(user_id, new_hash)
                    return True

                # Common alternatives
                if hasattr(db, "update_password"):
                    db.update_password(user_id, new_hash)
                    return True

                if hasattr(db, "change_password"):
                    db.change_password(user_id, new_hash)
                    return True

                return False

            def save(e):
                p = get_user_profile()
                if not S.user or not p.get("id"):
                    toast("Please login first.")
                    return

                cur = (current_tf.value or "").strip()
                newp = (new_tf.value or "").strip()
                conf = (confirm_tf.value or "").strip()

                if not cur or not newp or not conf:
                    toast("Please fill in all password fields.")
                    return

                if newp != conf:
                    toast("Passwords do not match.")
                    return

                if len(newp) < 6:
                    toast("New password must be at least 6 characters.")
                    return

                # Fetch latest user row
                user = None
                try:
                    if hasattr(db, "get_user_by_id"):
                        user = db.get_user_by_id(p["id"])
                    elif hasattr(db, "get_user"):
                        user = db.get_user(p["id"])
                except Exception:
                    user = None

                # fallback by email
                if not user:
                    email_lookup = (p.get("email") or "").strip()
                    if email_lookup and email_lookup != "Not signed in" and hasattr(db, "get_user_by_email"):
                        try:
                            user = db.get_user_by_email(email_lookup)
                        except Exception:
                            user = None

                if not user:
                    toast("Account not found.")
                    return

                user_id, password_hash = _extract_user_id_and_hash(user, p["id"])
                if not password_hash:
                    toast("Password data missing.")
                    return

                # Verify current password
                try:
                    ok = bcrypt.verify(cur, password_hash)
                except Exception:
                    ok = False

                if not ok:
                    toast("Incorrect current password.")
                    return

                # Hash and save new password
                try:
                    new_hash = bcrypt.hash(newp)
                except Exception:
                    toast("Failed to hash password.")
                    return

                try:
                    updated = _update_password_in_db(int(user_id), new_hash)
                    if not updated:
                        toast("Password update function not found in db.py.")
                        return
                except Exception as ex:
                    toast(f"Failed to update password: {ex}")
                    return

                dlg.open = False
                page.update()
                toast("Password updated!", "SUCCESS_COLOR")

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Change Password", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=480,
                    padding=8,
                    content=ft.Column([current_tf, new_tf, confirm_tf], spacing=12),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Save", on_click=save, bgcolor=C("BUTTON_COLOR"), color="white"),
                ],
                shape=ft.RoundedRectangleBorder(radius=16),
            )

            page.overlay.append(dlg)
            dlg.open = True
            page.update()


        # -----------------------------
        # Theme dropdown
        # -----------------------------
        theme_dd = ft.Dropdown(
            value=getattr(S, "theme_name", None) or "Light Mode",
            options=[
                ft.dropdown.Option("Light Mode"),
                ft.dropdown.Option("Dark Mode"),
                ft.dropdown.Option("Pink"),
            ],
            border=ft.InputBorder.NONE,
            filled=False,
            width=170,
            on_change=lambda e: (S.set_theme(theme_dd.value), refresh()),
        )

        # -----------------------------
        # Profile card (top)
        # -----------------------------
        profile = get_user_profile()
        user_name = (profile.get("name") or profile.get("username") or "Guest").strip() or "Guest"
        user_email = (profile.get("email") or "").strip()
        signed_in = bool(S.user and profile.get("id"))

        display_email = user_email if signed_in and user_email and user_email != "Not signed in" else "Not signed in"

        profile_card = ft.Container(
            border_radius=20,
            bgcolor="white",
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            padding=18,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=14,
                        controls=[
                            ft.CircleAvatar(
                                radius=26,
                                bgcolor=C("BUTTON_COLOR"),
                                content=ft.Text((user_name[:1] if user_name else "G").upper(), color="white"),
                            ),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(user_name, size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text(display_email, size=11, color=C("TEXT_SECONDARY")),
                                ],
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ACCOUNT_CIRCLE,
                        icon_color=C("TEXT_PRIMARY"),
                        on_click=lambda e: show_account_dialog(),
                    ),
                ],
            ),
        )

        # -----------------------------
        # Tile component used in the left panel
        # -----------------------------
        def tile(icon, title, subtitle="", right_control=None, on_click=None):
            return ft.Container(
                border_radius=16,
                border=ft.border.all(1.5, C("BORDER_COLOR")),
                bgcolor="white",
                padding=14,
                ink=True,
                on_click=on_click,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=40,
                                    height=40,
                                    border_radius=12,
                                    bgcolor=ft.Colors.with_opacity(0.12, C("BUTTON_COLOR")),
                                    content=ft.Icon(icon, color=C("BUTTON_COLOR")),
                                    alignment=ft.alignment.center,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(title, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                        ft.Text(subtitle, size=11, color=C("TEXT_SECONDARY")),
                                    ]
                                ),
                            ],
                        ),
                        right_control or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=C("TEXT_SECONDARY")),
                    ],
                ),
            )

        # -----------------------------
        # Left panel content (logout removed)
        # -----------------------------
        settings_stack = ft.Column(
            spacing=14,
            controls=[
                ft.Text("Preferences", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                tile(ft.Icons.PALETTE, "Theme", "Switch your look and feel", right_control=theme_dd),

                ft.Text("Account", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                tile(ft.Icons.PERSON, "Account", "View profile information", on_click=lambda e: show_account_dialog()),
                tile(ft.Icons.LOCK, "Change Password", "Update your password", on_click=lambda e: show_change_password_dialog()),
                tile(ft.Icons.DELETE_FOREVER, "Delete Account", "Remove this account permanently", on_click=lambda e: confirm_delete_account()),
            ],
        )

        # -----------------------------
        # Right panel (tips)
        # -----------------------------
        preview_panel = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            bgcolor=C("FORM_BG"),
            padding=22,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Text("Quick Tips", size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                    ft.Container(
                        border_radius=18,
                        bgcolor="white",
                        border=ft.border.all(1.5, C("BORDER_COLOR")),
                        padding=16,
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.TIPS_AND_UPDATES, color=C("BUTTON_COLOR")),
                                        ft.Text("Theme changes apply instantly.", size=12, color=C("TEXT_PRIMARY")),
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.SECURITY, color=C("BUTTON_COLOR")),
                                        ft.Text("Use a strong password.", size=12, color=C("TEXT_PRIMARY")),
                                    ]
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.EVENT_NOTE, color=C("BUTTON_COLOR")),
                                        ft.Text("Set due dates so tasks appear on the calendar.", size=12, color=C("TEXT_PRIMARY")),
                                    ]
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

        # -----------------------------
        # Page layout
        # -----------------------------
        settings_scroll = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY"))],
                ),
                profile_card,
                settings_stack,
            ],
        )

        left_panel = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            bgcolor=C("FORM_BG"),
            padding=22,
            content=settings_scroll,
        )

        board = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(2, C("BORDER_COLOR")),
            bgcolor=C("BG_COLOR"),
            padding=22,
            content=ft.Row(
                expand=True,
                spacing=18,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Container(content=left_panel, expand=6),
                    ft.Container(content=preview_panel, expand=4),
                ],
            ),
        )

        return ft.Container(
            expand=True,
            bgcolor=C("BG_COLOR"),
            padding=18,
            content=board,
        )
