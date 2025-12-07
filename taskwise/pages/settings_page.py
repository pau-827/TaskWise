import flet as ft
from taskwise.theme import THEMES


class SettingsPage:
    """
    SETTINGS PAGE (more engaging, still wireframe-friendly)
    - No header here. app.py owns the header.
    - Uses AppState:
        S.colors, S.theme_name, S.set_theme(...)
        S.user (dict with name/email) or None
        S.db.get_user_by_email(...)
        S.db.change_password(...)
        S.db.get_setting(...), S.db.set_setting(...)
    """

    def __init__(self, state):
        self.S = state

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        def refresh():
            S.update()

        # -----------------------------
        # Dialog helpers
        # -----------------------------
        def close_dialog(dlg):
            dlg.open = False
            page.update()

        def show_account_dialog():
            name = S.user.get("name") if S.user else ""
            email = S.user.get("email") if S.user else ""

            content = (
                ft.Text("Not signed in.", color=C("TEXT_SECONDARY"))
                if not S.user
                else ft.Column(
                    [
                        ft.Text(f"Name: {name}", color=C("TEXT_PRIMARY")),
                        ft.Text(f"Email: {email}", color=C("TEXT_SECONDARY")),
                    ],
                    spacing=6,
                    tight=True,
                )
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

        def hash_pw(s: str) -> str:
            if hasattr(S, "_hash_pw"):
                return S._hash_pw(s)
            import hashlib
            return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

        def show_notification_dialog():
            # Get current settings or defaults
            task_due = db.get_setting("notify_task_due", True) if hasattr(db, 'get_setting') else True
            task_created = db.get_setting("notify_task_created", True) if hasattr(db, 'get_setting') else True
            task_completed = db.get_setting("notify_task_completed", False) if hasattr(db, 'get_setting') else False

            task_due_switch = ft.Switch(value=task_due, active_color=C("BUTTON_COLOR"))
            task_created_switch = ft.Switch(value=task_created, active_color=C("BUTTON_COLOR"))
            task_completed_switch = ft.Switch(value=task_completed, active_color=C("BUTTON_COLOR"))

            def save_notifications(e):
                db.set_setting("notify_task_due", task_due_switch.value)
                db.set_setting("notify_task_created", task_created_switch.value)
                db.set_setting("notify_task_completed", task_completed_switch.value)
                
                dlg.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Notification preferences saved."), 
                    bgcolor=C("SUCCESS_COLOR")
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
                                    ft.Text("Task Due Soon", size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Get notified when tasks are approaching their due date", size=11, color=C("TEXT_SECONDARY")),
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
                                    ft.Text("Task Created", size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Get notified when new tasks are created", size=11, color=C("TEXT_SECONDARY")),
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
                                    ft.Text("Task Completed", size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Get notified when tasks are marked as complete", size=11, color=C("TEXT_SECONDARY")),
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
                content=ft.Container(
                    width=480,
                    padding=8,
                    content=notification_options,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Save", on_click=save_notifications, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def show_change_password_dialog():
            current_tf = ft.TextField(
                hint_text="Current Password",
                password=True,
                can_reveal_password=True,
                bgcolor="white",
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            new_tf = ft.TextField(
                hint_text="New Password",
                password=True,
                can_reveal_password=True,
                bgcolor="white",
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            confirm_tf = ft.TextField(
                hint_text="Confirm Password",
                password=True,
                can_reveal_password=True,
                bgcolor="white",
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

        def show_notification_dialog():
            # Get current settings or defaults
            task_due = db.get_setting("notify_task_due", True) if hasattr(db, 'get_setting') else True
            task_created = db.get_setting("notify_task_created", True) if hasattr(db, 'get_setting') else True
            task_completed = db.get_setting("notify_task_completed", False) if hasattr(db, 'get_setting') else False

            task_due_switch = ft.Switch(value=task_due, active_color=C("BUTTON_COLOR"))
            task_created_switch = ft.Switch(value=task_created, active_color=C("BUTTON_COLOR"))
            task_completed_switch = ft.Switch(value=task_completed, active_color=C("BUTTON_COLOR"))

            def save_notifications(e):
                db.set_setting("notify_task_due", task_due_switch.value)
                db.set_setting("notify_task_created", task_created_switch.value)
                db.set_setting("notify_task_completed", task_completed_switch.value)
                
                dlg.open = False
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Notification preferences saved."), 
                    bgcolor=C("SUCCESS_COLOR")
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
                                    ft.Text("Task Due Soon", size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Get notified when tasks are approaching their due date", size=11, color=C("TEXT_SECONDARY")),
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
                                    ft.Text("Task Created", size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Get notified when new tasks are created", size=11, color=C("TEXT_SECONDARY")),
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
                                    ft.Text("Task Completed", size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text("Get notified when tasks are marked as complete", size=11, color=C("TEXT_SECONDARY")),
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
                content=ft.Container(
                    width=480,
                    padding=8,
                    content=notification_options,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Save", on_click=save_notifications, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
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
        def soft_shadow():
            return ft.BoxShadow(blur_radius=14, color="#00000014", offset=ft.Offset(0, 8))

        def section_title(text: str):
            return ft.Text(text, size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY"))

        def tile(icon, title: str, subtitle: str = "", right_control: ft.Control | None = None, on_click=None):
            return ft.Container(
                border_radius=16,
                border=ft.border.all(1.5, C("BORDER_COLOR")),
                bgcolor="white",
                padding=ft.padding.symmetric(horizontal=16, vertical=14),
                ink=True,
                on_click=on_click,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=40,
                                    height=40,
                                    border_radius=12,
                                    bgcolor=ft.Colors.with_opacity(0.12, C("BUTTON_COLOR")),
                                    alignment=ft.alignment.center,
                                    content=ft.Icon(icon, color=C("BUTTON_COLOR")),
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                        ft.Text(subtitle, size=11, color=C("TEXT_SECONDARY")) if subtitle else ft.Container(),
                                    ],
                                ),
                            ],
                        ),
                        right_control if right_control else ft.Icon(ft.Icons.CHEVRON_RIGHT, color=C("TEXT_SECONDARY")),
                    ],
                ),
            )

        # Theme dropdown
        theme_dd = ft.Dropdown(
            value=S.theme_name if S.theme_name else "Light Mode",
            options=[
                ft.dropdown.Option("Light Mode"),
                ft.dropdown.Option("Dark Mode"),
                ft.dropdown.Option("Pink"),
            ],
            border=ft.InputBorder.NONE,
            filled=False,
            width=170,
            text_size=12,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
            on_change=lambda e: (S.set_theme(theme_dd.value), refresh()),
        )

        # Profile header
        user_name = (S.user.get("name") if S.user else "Guest").strip() if S.user else "Guest"
        user_email = (S.user.get("email") if S.user else "Not signed in").strip() if S.user else "Not signed in"
        status_text = "Signed in" if S.user else "Signed out"

        profile_card = ft.Container(
            border_radius=20,
            bgcolor="white",
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            padding=18,
            shadow=soft_shadow(),
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.CircleAvatar(
                        radius=26,
                        bgcolor=C("BUTTON_COLOR"),
                        content=ft.Text(user_name[:1].upper(), color="white", weight=ft.FontWeight.BOLD),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Text(user_name, size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ft.Text(user_email, size=11, color=C("TEXT_SECONDARY")),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        border_radius=999,
                                        bgcolor=ft.Colors.with_opacity(0.12, C("SUCCESS_COLOR") if S.user else C("ERROR_COLOR")),
                                        content=ft.Text(status_text, size=11, color=C("TEXT_PRIMARY")),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ACCOUNT_CIRCLE,
                        icon_color=C("TEXT_PRIMARY"),
                        tooltip="Account details",
                        on_click=lambda e: show_account_dialog(),
                    ),
                ],
            ),
        )

        # Left column (settings controls)
        settings_stack = ft.Column(
            spacing=14,
            controls=[
                section_title("Preferences"),
                tile(ft.Icons.PALETTE, "Theme", "Switch your look and feel", right_control=theme_dd),
                tile(ft.Icons.NOTIFICATIONS, "Notifications", "Manage your notification preferences", on_click=lambda e: show_notification_dialog()),
                section_title("Account"),
                tile(ft.Icons.PERSON, "Account", "View profile information", on_click=lambda e: show_account_dialog()),
                tile(ft.Icons.LOCK, "Change Password", "Update your login password", on_click=lambda e: show_change_password_dialog()),
                tile(ft.Icons.LOGOUT, "Logout", "Sign out of your session", on_click=lambda e: do_logout()),
            ],
        )

        left_panel = ft.Container(
            expand=True,
            border_radius=22,
            bgcolor=C("FORM_BG"),
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            padding=22,
            content=ft.Column(
                expand=True,
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                border_radius=999,
                                bgcolor=ft.Colors.with_opacity(0.12, C("BUTTON_COLOR")),
                                content=ft.Text("Manage your app", size=11, color=C("TEXT_PRIMARY")),
                            ),
                        ],
                    ),
                    profile_card,
                    ft.Container(height=2),
                    settings_stack,
                ],
            ),
        )

        # Right column (preview/info panel)
        preview_panel = ft.Container(
            expand=True,
            border_radius=22,
            bgcolor=C("FORM_BG"),
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            padding=22,
            content=ft.Column(
                expand=True,
                spacing=14,
                controls=[
                    ft.Text("Quick Tips", size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                    ft.Container(
                        border_radius=18,
                        bgcolor="white",
                        border=ft.border.all(1.5, C("BORDER_COLOR")),
                        padding=16,
                        shadow=soft_shadow(),
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(ft.Icons.TIPS_AND_UPDATES, color=C("BUTTON_COLOR")),
                                        ft.Text("Theme changes apply instantly.", size=12, color=C("TEXT_PRIMARY")),
                                    ],
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(ft.Icons.SECURITY, color=C("BUTTON_COLOR")),
                                        ft.Text("Use a strong password for your account.", size=12, color=C("TEXT_PRIMARY")),
                                    ],
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(ft.Icons.EVENT_NOTE, color=C("BUTTON_COLOR")),
                                        ft.Text("Set due dates so tasks show on the calendar.", size=12, color=C("TEXT_PRIMARY")),
                                    ],
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=C("BUTTON_COLOR")),
                                        ft.Text("Enable notifications to stay on top of tasks.", size=12, color=C("TEXT_PRIMARY")),
                                    ],
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=C("BUTTON_COLOR")),
                                        ft.Text("Enable notifications to stay on top of tasks.", size=12, color=C("TEXT_PRIMARY")),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Text("Current Theme", size=12, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                    ft.Container(
                        border_radius=18,
                        bgcolor="white",
                        border=ft.border.all(1.5, C("BORDER_COLOR")),
                        padding=16,
                        shadow=soft_shadow(),
                        content=ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    width=14,
                                    height=14,
                                    border_radius=99,
                                    bgcolor=C("BUTTON_COLOR"),
                                ),
                                ft.Text(S.theme_name or "Light Mode", size=13, color=C("TEXT_PRIMARY")),
                            ],
                        ),
                    ),
                ],
            ),
        )

        # Main board layout (2 columns)
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
            padding=ft.padding.all(18),
            content=board,
        )
