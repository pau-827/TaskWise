import flet as ft
from taskwise.theme import THEMES
from passlib.hash import bcrypt


class SettingsPage:
    """
    SETTINGS PAGE (wireframe-friendly, fully updated for new db.py)
    """

    def __init__(self, state):
        self.S = state

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
        # DIALOG CLOSE
        # -----------------------------------------------------
        def close_dialog(dlg):
            dlg.open = False
            page.update()

        # -----------------------------------------------------
        # ACCOUNT DETAILS DIALOG
        # -----------------------------------------------------
        def show_account_dialog():
            if not S.user:
                content = ft.Text("Not signed in.", color=C("TEXT_SECONDARY"))
            else:
                content = ft.Column(
                    [
                        ft.Text(f"Name: {S.user['name']}", color=C("TEXT_PRIMARY")),
                        ft.Text(f"Email: {S.user['email']}", color=C("TEXT_SECONDARY")),
                    ],
                    spacing=6,
                )

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Account", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=420, content=content, padding=8),
                actions=[ft.TextButton("Close", on_click=lambda e: close_dialog(dlg))],
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # -----------------------------------------------------
        # NOTIFICATION SETTINGS (fixed for per-user)
        # -----------------------------------------------------
        def show_notification_dialog():
            user_id = S.user["id"]

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

            # UI SECTION
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

        # -----------------------------------------------------
        # CHANGE PASSWORD DIALOG (fixed for bcrypt + new db)
        # -----------------------------------------------------
        def show_change_password_dialog():
            current_tf = ft.TextField(hint_text="Current Password", password=True, can_reveal_password=True, filled=True)
            new_tf = ft.TextField(hint_text="New Password", password=True, can_reveal_password=True, filled=True)
            confirm_tf = ft.TextField(hint_text="Confirm Password", password=True, can_reveal_password=True, filled=True)

            def save(e):
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Please login first."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user = db.get_user_by_email(S.user["email"])
                if not user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account not found."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if not bcrypt.verify(current_tf.value, user["password_hash"]):
                    page.snack_bar = ft.SnackBar(content=ft.Text("Incorrect current password."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if new_tf.value != confirm_tf.value:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Passwords do not match."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if not new_tf.value.strip():
                    page.snack_bar = ft.SnackBar(content=ft.Text("Password cannot be empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                # UPDATE PASSWORD IN DB
                new_hash = bcrypt.hash(new_tf.value)
                db.update_user_password(user["id"], new_hash)

                page.snack_bar = ft.SnackBar(content=ft.Text("Password updated!"), bgcolor=C("SUCCESS_COLOR"))
                dlg.open = False
                page.snack_bar.open = True
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Change Password", weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=420,
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
        # LOGOUT
        # -----------------------------------------------------
        def do_logout():
            S.user = None
            page.snack_bar = ft.SnackBar(content=ft.Text("Logged out."), bgcolor=C("SUCCESS_COLOR"))
            page.snack_bar.open = True
            refresh()
            page.update()

        # -----------------------------------------------------
        # THEME DROPDOWN
        # -----------------------------------------------------
        theme_dd = ft.Dropdown(
            value=S.theme_name or "Light Mode",
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
        user_name = S.user["name"] if S.user else "Guest"
        user_email = S.user["email"] if S.user else "Not signed in"

        profile_card = ft.Container(
            border_radius=20,
            bgcolor="white",
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            padding=18,
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.CircleAvatar(
                        radius=26,
                        bgcolor=C("BUTTON_COLOR"),
                        content=ft.Text(user_name[:1].upper(), color="white"),
                    ),
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(user_name, size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ft.Text(user_email, size=11, color=C("TEXT_SECONDARY")),
                        ],
                    ),
                    ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, on_click=lambda e: show_account_dialog()),
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
                                    width=40, height=40,
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
                tile(ft.Icons.NOTIFICATIONS, "Notifications", "Manage notification preferences",
                     on_click=lambda e: show_notification_dialog()),

                ft.Text("Account", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                tile(ft.Icons.PERSON, "Account", "View profile information", on_click=lambda e: show_account_dialog()),
                tile(ft.Icons.LOCK, "Change Password", "Update your password", on_click=lambda e: show_change_password_dialog()),
                tile(ft.Icons.LOGOUT, "Logout", "Sign out", on_click=lambda e: do_logout()),
            ],
        )

        left_panel = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(1.5, C("BORDER_COLOR")),
            bgcolor=C("FORM_BG"),
            padding=22,
            content=ft.Column(
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
            ),
        )

        # -----------------------------------------------------
        # RIGHT PANEL (unchanged, preview content)
        # -----------------------------------------------------
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
                                ft.Row(controls=[ft.Icon(ft.Icons.TIPS_AND_UPDATES, color=C("BUTTON_COLOR")),
                                                 ft.Text("Theme changes apply instantly.", size=12)]),
                                ft.Row(controls=[ft.Icon(ft.Icons.SECURITY, color=C("BUTTON_COLOR")),
                                                 ft.Text("Use a strong password.", size=12)]),
                                ft.Row(controls=[ft.Icon(ft.Icons.EVENT_NOTE, color=C("BUTTON_COLOR")),
                                                 ft.Text("Set due dates so tasks appear on the calendar.", size=12)]),
                                ft.Row(controls=[ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=C("BUTTON_COLOR")),
                                                 ft.Text("Enable notifications to stay informed.", size=12)]),
                            ],
                        ),
                    ),
                ],
            ),
        )

        # -----------------------------------------------------
        # MAIN LAYOUT
        # -----------------------------------------------------
        board = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(2, C("BORDER_COLOR")),
            bgcolor=C("BG_COLOR"),
            padding=22,
            content=ft.Row(
                expand=True,
                spacing=18,
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
