import flet as ft
from taskwise.theme import THEMES
from passlib.hash import bcrypt


class SettingsPage:
    """
    SETTINGS PAGE (wireframe-friendly, fully updated for new db.py)
    """

    def __init__(self, state):
        self.S = state
        # ADDED: expose notifications dialog to header bell
        self._open_notification_dialog = None

    # ADDED: callable from app.py (header bell)
    def open_notifications(self):
        if callable(self._open_notification_dialog):
            self._open_notification_dialog()

    # FIX ADDED: aliases so app.py can call any of these names safely
    def open_notification_dialog(self):
        self.open_notifications()

    def show_notification_dialog(self):
        self.open_notifications()

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        # -----------------------------------------------------
        # COLOR HELPER
        # -----------------------------------------------------
        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        def refresh():
            S.update()

        # -----------------------------------------------------
        # SAFE USER FETCH (fixes KeyError: 'name' / 'email')
        # + Ensures we can show a real email by reloading user from DB
        # -----------------------------------------------------
        def get_user_profile() -> dict:
            """
            Returns a safe profile dict with keys:
            id, username, name, email, role
            """
            profile = {"id": None, "username": "Guest", "name": "Guest", "email": "Not signed in", "role": ""}

            if not S.user:
                return profile

            # Start with whatever is already in S.user
            if isinstance(S.user, dict):
                profile["id"] = S.user.get("id")
                profile["role"] = S.user.get("role", "")
                profile["username"] = S.user.get("username") or profile["username"]
                profile["name"] = S.user.get("name") or profile["username"] or profile["name"]
                profile["email"] = S.user.get("email") or profile["email"]

            # If email/name missing, try loading from DB using id (preferred) then username/email fallback
            try:
                user_row = None

                # Prefer id
                if profile["id"] is not None:
                    if hasattr(db, "get_user_by_id"):
                        user_row = db.get_user_by_id(profile["id"])
                    elif hasattr(db, "get_user"):
                        user_row = db.get_user(profile["id"])

                # Fallback: try username -> email lookup if methods exist
                if user_row is None and profile["username"] and hasattr(db, "get_user_by_username"):
                    user_row = db.get_user_by_username(profile["username"])

                if user_row is None and profile.get("email") not in (None, "", "Not signed in") and hasattr(db, "get_user_by_email"):
                    user_row = db.get_user_by_email(profile["email"])

                if user_row:
                    if isinstance(user_row, dict):
                        profile["id"] = user_row.get("id", profile["id"])
                        profile["email"] = user_row.get("email") or profile["email"]
                        profile["name"] = user_row.get("name") or user_row.get("username") or profile["name"]
                        profile["username"] = user_row.get("username") or profile["username"]
                        profile["role"] = user_row.get("role", profile["role"])
                    else:
                        # Expected common: (id, username/name, email, password_hash, role, ...)
                        profile["id"] = user_row[0] if len(user_row) > 0 else profile["id"]
                        if len(user_row) > 1 and user_row[1]:
                            profile["username"] = user_row[1]
                            profile["name"] = user_row[1]
                        if len(user_row) > 2 and user_row[2]:
                            profile["email"] = user_row[2]
                        if len(user_row) > 4 and user_row[4]:
                            profile["role"] = user_row[4]
            except Exception:
                pass

            return profile

        profile = get_user_profile()

        # -----------------------------------------------------
        # DIALOG CLOSE
        # -----------------------------------------------------
        def close_dialog(dlg):
            dlg.open = False
            page.update()

        # -----------------------------------------------------
        # ACCOUNT DETAILS DIALOG (make sure Name + Email always show)
        # -----------------------------------------------------
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

        # -----------------------------------------------------
        # NOTIFICATION SETTINGS (per-user)
        # -----------------------------------------------------
        def show_notification_dialog():
            p = get_user_profile()
            if not S.user or not p.get("id"):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please login first."),
                    bgcolor=C("ERROR_COLOR"),
                )
                page.snack_bar.open = True
                page.update()
                return

            user_id = p["id"]

            task_due = db.get_setting(user_id, "notify_task_due", True)
            task_created = db.get_setting(user_id, "notify_task_created", True)
            task_completed = db.get_setting(user_id, "notify_task_completed", False)

            task_due_switch = ft.Switch(value=task_due, active_color=C("BUTTON_COLOR"))
            task_created_switch = ft.Switch(value=task_created, active_color=C("BUTTON_COLOR"))
            task_completed_switch = ft.Switch(value=task_completed, active_color=C("BUTTON_COLOR"))

            def save_notifications(e):
                db.set_setting(user_id, "notify_task_due", task_due_switch.value)
                db.set_setting(user_id, "notify_task_created", task_created_switch.value)
                db.set_setting(user_id, "notify_task_completed", task_completed_switch.value)

                dlg.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Notification preferences saved."),
                    bgcolor=C("SUCCESS_COLOR"),
                )
                page.snack_bar.open = True
                page.update()

            notification_options = ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Task Due Soon", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Notify when tasks are near due date", size=11, color=C("TEXT_SECONDARY")),
                                ],
                            ),
                            task_due_switch,
                        ],
                    ),
                    ft.Divider(height=1, color=C("BORDER_COLOR")),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Task Created", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Notify when tasks are created", size=11, color=C("TEXT_SECONDARY")),
                                ],
                            ),
                            task_created_switch,
                        ],
                    ),
                    ft.Divider(height=1, color=C("BORDER_COLOR")),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Task Completed", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Notify when tasks are completed", size=11, color=C("TEXT_SECONDARY")),
                                ],
                            ),
                            task_completed_switch,
                        ],
                    ),
                ],
            )

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Notification Settings", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=480, padding=8, content=notification_options),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Save", on_click=save_notifications, bgcolor=C("BUTTON_COLOR"), color="white"),
                ],
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # ADDED: expose notifications dialog to header bell
        self._open_notification_dialog = lambda: show_notification_dialog()

        # -----------------------------------------------------
        # ✅ ADDED: DELETE ACCOUNT (ADMIN)
        # -----------------------------------------------------
        def confirm_delete_account():
            p = get_user_profile()
            if not S.user or not p.get("id"):
                page.snack_bar = ft.SnackBar(content=ft.Text("Please login first."), bgcolor=C("ERROR_COLOR"))
                page.snack_bar.open = True
                page.update()
                return

            if (p.get("role") or "").lower() != "admin":
                page.snack_bar = ft.SnackBar(content=ft.Text("Admin access required."), bgcolor=C("ERROR_COLOR"))
                page.snack_bar.open = True
                page.update()
                return

            def close_dlg(e):
                dlg.open = False
                page.update()

            def do_delete(e):
                try:
                    db.delete_user(p["id"])
                except Exception:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Delete failed."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                dlg.open = False
                page.update()

                try:
                    if hasattr(S, "on_user_logout"):
                        S.on_user_logout()
                    else:
                        S.user = None
                except Exception:
                    S.user = None

                page.snack_bar = ft.SnackBar(content=ft.Text("Account deleted."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Delete Account", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Text("This will permanently remove this account. Continue?", color=C("TEXT_SECONDARY")),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dlg),
                    ft.ElevatedButton("Delete", on_click=do_delete, bgcolor=C("ERROR_COLOR"), color="white"),
                ],
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # -----------------------------------------------------
        # CHANGE PASSWORD DIALOG (functional: fetch by id, get correct password hash)
        # -----------------------------------------------------
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

            def _extract_user_id_and_hash(user_obj, fallback_id):
                """
                Returns (user_id, password_hash) for dict or tuple.
                Supports common tuple layouts.
                """
                if isinstance(user_obj, dict):
                    uid = user_obj.get("id", fallback_id)
                    ph = user_obj.get("password_hash") or user_obj.get("password")
                    return uid, ph

                uid = user_obj[0] if len(user_obj) > 0 else fallback_id
                ph = user_obj[3] if len(user_obj) > 3 else None

                if not ph:
                    for v in user_obj:
                        if isinstance(v, str) and v.startswith("$2"):
                            ph = v
                            break

                return uid, ph

            def save(e):
                p = get_user_profile()
                if not S.user or not p.get("id"):
                    page.snack_bar = ft.SnackBar(content=ft.Text("Please login first."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user = None
                try:
                    if hasattr(db, "get_user_by_id"):
                        user = db.get_user_by_id(p["id"])
                    elif hasattr(db, "get_user"):
                        user = db.get_user(p["id"])
                except Exception:
                    user = None

                if not user:
                    email_lookup = (p.get("email") or "").strip()
                    if email_lookup and email_lookup != "Not signed in" and hasattr(db, "get_user_by_email"):
                        try:
                            user = db.get_user_by_email(email_lookup)
                        except Exception:
                            user = None

                if not user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account not found."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user_id, password_hash = _extract_user_id_and_hash(user, p["id"])

                if not password_hash:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Password data missing."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if not bcrypt.verify(current_tf.value or "", password_hash):
                    page.snack_bar = ft.SnackBar(content=ft.Text("Incorrect current password."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if (new_tf.value or "") != (confirm_tf.value or ""):
                    page.snack_bar = ft.SnackBar(content=ft.Text("Passwords do not match."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if not (new_tf.value or "").strip():
                    page.snack_bar = ft.SnackBar(content=ft.Text("Password cannot be empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                new_hash = bcrypt.hash(new_tf.value)

                try:
                    db.update_user_password(user_id, new_hash)
                except Exception:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Failed to update password."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                page.snack_bar = ft.SnackBar(content=ft.Text("Password updated!"), bgcolor=C("SUCCESS_COLOR"))
                dlg.open = False
                page.snack_bar.open = True
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Change Password", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=480,
                    height=170,
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

        # -----------------------------------------------------
        # LOGOUT (go back to main page)
        # -----------------------------------------------------
        def do_logout():
            if hasattr(S, "on_user_logout"):
                try:
                    S.on_user_logout()
                except Exception:
                    S.user = None
            else:
                S.user = None

            page.snack_bar = ft.SnackBar(content=ft.Text("Logged out."), bgcolor=C("SUCCESS_COLOR"))
            page.snack_bar.open = True
            page.update()

            def safe_go(name: str) -> bool:
                try:
                    if hasattr(S, "go"):
                        S.go(name)
                        return True
                except Exception:
                    return False
                return False

            for target in ("mainpage", "loginpage", "login", "startpage", "taskpage"):
                if safe_go(target):
                    break

            refresh()
            page.update()

        # -----------------------------------------------------
        # THEME DROPDOWN
        # -----------------------------------------------------
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

        # -----------------------------------------------------
        # USER DISPLAY
        # -----------------------------------------------------
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
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # ✅ pushes last item to far right
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
        # -----------------------------------------------------
        # LEFT PANEL
        # -----------------------------------------------------
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

        settings_stack = ft.Column(
            spacing=14,
            controls=[
                ft.Text("Preferences", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                tile(ft.Icons.PALETTE, "Theme", "Switch your look and feel", right_control=theme_dd),
                tile(
                    ft.Icons.NOTIFICATIONS,
                    "Notifications",
                    "Manage notification preferences",
                    on_click=lambda e: show_notification_dialog(),
                ),

                ft.Text("Account", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                tile(ft.Icons.PERSON, "Account", "View profile information", on_click=lambda e: show_account_dialog()),
                tile(ft.Icons.LOCK, "Change Password", "Update your password", on_click=lambda e: show_change_password_dialog()),
                tile(ft.Icons.LOGOUT, "Logout", "Sign out", on_click=lambda e: do_logout()),

                # ✅ ADDED: Admin section + tiles
                ft.Text("Admin", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                tile(ft.Icons.DELETE_FOREVER, "Delete Account", "Remove this account permanently", on_click=lambda e: confirm_delete_account()),
            ],
        )

        # ADDED: make settings panel scrollable
        settings_scroll = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                    ],
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
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=C("BUTTON_COLOR")),
                                        ft.Text("Enable notifications to stay informed.", size=12, color=C("TEXT_PRIMARY")),
                                    ]
                                ),
                            ],
                        ),
                    ),
                ],
            ),
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
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,  # ✅ makes both sides equal height
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
