import flet as ft
import db


def get_admin_page(
    page,
    PRIMARY_TEXT,
    SECONDARY_TEXT,
    BUTTON_COLOR,
    BG_COLOR,
    FORM_BG,
    on_logout=None,  # logout() from main (optional)
):
    logs = db.get_logs()

    # Load users (safe fallback to empty list)
    try:
        users = db.get_users()
    except Exception:
        users = []

    # Hide the admin account from the list
    filtered_users = []
    for u in users:
        role = ""
        email = ""
        if isinstance(u, dict):
            role = (u.get("role") or "").lower()
            email = (u.get("email") or "").lower()
        else:
            role = (u[3] or "").lower() if len(u) > 3 else ""
            email = (u[2] or "").lower() if len(u) > 2 else ""

        if role == "admin" or email == "admin@taskwise.com":
            continue
        filtered_users.append(u)

    # Quick snack message
    def show_message(text: str, color="red"):
        snack = ft.SnackBar(content=ft.Text(text), bgcolor=color, duration=2000)
        try:
            page.overlay.append(snack)
            snack.open = True
        except Exception:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

    # Rebuild the admin page (simple refresh)
    def refresh_admin():
        page.clean()
        page.add(
            get_admin_page(
                page,
                PRIMARY_TEXT,
                SECONDARY_TEXT,
                BUTTON_COLOR,
                BG_COLOR,
                FORM_BG,
                on_logout=on_logout,
            )
        )
        page.update()

    # Logout button behavior (use callback if provided)
    def do_logout(e=None):
        if callable(on_logout):
            on_logout()
            return
        try:
            page.session.clear()
        except Exception:
            pass
        page.clean()
        page.update()

    # Ban a user
    def ban_user(user_id: int):
        try:
            db.ban_user(int(user_id))
            try:
                db.add_log("BAN", f"Admin banned user_id={int(user_id)}", user_id=int(user_id))
            except Exception:
                pass
            show_message("User banned.", "green")
            refresh_admin()
        except Exception as ex:
            show_message(f"Ban failed: {ex}", "red")

    # Unban a user
    def unban_user(user_id: int):
        try:
            db.unban_user(int(user_id))
            try:
                db.add_log("UNBAN", f"Admin unbanned user_id={int(user_id)}", user_id=int(user_id))
            except Exception:
                pass
            show_message("Ban lifted.", "green")
            refresh_admin()
        except Exception as ex:
            show_message(f"Unban failed: {ex}", "red")

    # Confirm delete (dialog is added to page.overlay so it opens reliably)
    def confirm_delete(user_id: int):
        if user_id is None:
            show_message("Delete failed: invalid user id.", "red")
            return

        def do_delete(e):
            try:
                uid_int = int(user_id)

                try:
                    db.add_log("DELETE_USER", f"Admin deleted user_id={uid_int}", user_id=uid_int)
                except Exception:
                    pass

                db.delete_user(uid_int)

                dlg.open = False
                page.update()

                show_message("User deleted.", "green")
                refresh_admin()
            except Exception as ex:
                show_message(f"Delete failed: {ex}", "red")

        def close(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=FORM_BG,
            title=ft.Text("Delete user?", color=PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
            content=ft.Text("This will permanently remove the account.", color=SECONDARY_TEXT),
            actions=[
                ft.TextButton("Cancel", on_click=close),
                ft.ElevatedButton("Delete", on_click=do_delete, bgcolor="red", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12),
        )

        if dlg not in page.overlay:
            page.overlay.append(dlg)

        dlg.open = True
        page.update()

    # ---------------- USERS UI ----------------
    user_items = []
    # Show 1..n in the UI, but still use the real uid for actions
    for display_id, u in enumerate(filtered_users, start=1):
        if isinstance(u, dict):
            uid = u.get("id")
            name = u.get("name") or ""
            email = u.get("email") or ""
            role = u.get("role") or ""
            is_banned = bool(u.get("is_banned") or u.get("banned"))
        else:
            uid = u[0] if len(u) > 0 else None
            name = u[1] if len(u) > 1 else ""
            email = u[2] if len(u) > 2 else ""
            role = u[3] if len(u) > 3 else ""
            is_banned = bool(u[4]) if len(u) > 4 else False

        user_bg = ft.Colors.with_opacity(0.12, ft.Colors.RED) if is_banned else FORM_BG
        border_col = ft.Colors.RED if is_banned else ft.Colors.with_opacity(0.10, "black")
        title_col = ft.Colors.RED if is_banned else PRIMARY_TEXT
        status_text = "BANNED" if is_banned else ""

        action_btn = (
            ft.IconButton(
                icon=ft.Icons.LOCK_OPEN,
                tooltip="Lift ban",
                icon_color=PRIMARY_TEXT,
                on_click=(lambda e, _uid=uid: unban_user(_uid)),
            )
            if is_banned
            else ft.IconButton(
                icon=ft.Icons.BLOCK,
                tooltip="Ban user",
                icon_color="red",
                on_click=(lambda e, _uid=uid: ban_user(_uid)),
            )
        )

        user_items.append(
            ft.Container(
                bgcolor=user_bg,
                padding=10,
                border_radius=10,
                border=ft.border.all(1, border_col),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            expand=True,
                            spacing=2,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Text(f"User ID: {display_id}", color=title_col, size=12),
                                        ft.Text(
                                            status_text,
                                            color=ft.Colors.RED,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                ),
                                ft.Text(f"Name: {name}", color=PRIMARY_TEXT, size=12),
                                ft.Text(f"Email: {email}", color=PRIMARY_TEXT, size=12),
                                ft.Text(f"Role: {role}", color=SECONDARY_TEXT, size=11),
                            ],
                        ),
                        ft.Row(
                            spacing=6,
                            controls=[
                                action_btn,
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_FOREVER,
                                    tooltip="Delete user",
                                    icon_color="red",
                                    on_click=(lambda e, _uid=uid: confirm_delete(_uid)),
                                ),
                            ],
                        ),
                    ],
                ),
            )
        )

    # ---------------- LOGS UI ----------------
    log_items = []
    for log in logs:
        log_items.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"User ID: {log['user_id']}", color=PRIMARY_TEXT, size=12),
                        ft.Text(f"Email: {log['email']}", color=PRIMARY_TEXT, size=12),
                        ft.Text(f"Action: {log['action']}", color=PRIMARY_TEXT, size=12),
                        ft.Text(f"Details: {log['details']}", color=SECONDARY_TEXT, size=11),
                        ft.Text(f"Time: {log['created_at']}", color=SECONDARY_TEXT, size=11),
                    ],
                    spacing=2,
                ),
                bgcolor=FORM_BG,
                padding=10,
                border_radius=10,
            )
        )

    # ---------------- MAIN LAYOUT ----------------
    return ft.Container(
        padding=20,
        bgcolor=BG_COLOR,
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=14,
            controls=[
                # Top bar: logout + refresh
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.LOGOUT,
                                    tooltip="Logout",
                                    icon_color=PRIMARY_TEXT,
                                    on_click=do_logout,
                                ),
                                ft.Text(
                                    "Admin Panel",
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=PRIMARY_TEXT,
                                ),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh",
                            icon_color=PRIMARY_TEXT,
                            on_click=lambda e: refresh_admin(),
                        ),
                    ],
                ),
                ft.Row(
                    expand=True,
                    spacing=16,
                    controls=[
                        # Left: Users
                        ft.Container(
                            expand=True,
                            bgcolor=BG_COLOR,
                            content=ft.Column(
                                expand=True,
                                spacing=10,
                                controls=[
                                    ft.Text("Users", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                                    ft.Container(
                                        expand=True,
                                        content=ft.ListView(
                                            expand=True,
                                            spacing=10,
                                            controls=user_items
                                            if user_items
                                            else [ft.Text("No users found.", color=SECONDARY_TEXT, size=12)],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        # Right: Log history
                        ft.Container(
                            expand=True,
                            bgcolor=BG_COLOR,
                            content=ft.Column(
                                expand=True,
                                spacing=10,
                                controls=[
                                    ft.Text("Log History", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                                    ft.Container(
                                        expand=True,
                                        content=ft.ListView(
                                            expand=True,
                                            spacing=10,
                                            controls=log_items
                                            if log_items
                                            else [ft.Text("No logs found.", color=SECONDARY_TEXT, size=12)],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )
