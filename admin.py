import flet as ft
import db

def get_admin_page(page, PRIMARY_TEXT, SECONDARY_TEXT, BUTTON_COLOR, BG_COLOR, FORM_BG):
    logs = db.get_logs()

    # --- Users list (ban/delete icons) ---
    try:
        users = db.get_users()
    except Exception:
        users = []

    def show_message(text: str, color="red"):
        snack = ft.SnackBar(content=ft.Text(text), bgcolor=color, duration=2000)
        try:
            page.overlay.append(snack)
            snack.open = True
        except:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

    def refresh_admin():
        page.clean()
        page.add(get_admin_page(page, PRIMARY_TEXT, SECONDARY_TEXT, BUTTON_COLOR, BG_COLOR, FORM_BG))
        page.update()

    def ban_user(user_id: int):
        try:
            db.ban_user(user_id)
            show_message("User banned.", "green")
            refresh_admin()
        except Exception as ex:
            show_message(f"Ban failed: {ex}", "red")

    def unban_user(user_id: int):
        try:
            db.unban_user(user_id)
            show_message("Ban lifted.", "green")
            refresh_admin()
        except Exception as ex:
            show_message(f"Unban failed: {ex}", "red")

    def confirm_delete(user_id: int):
        def do_delete(_):
            try:
                db.delete_user(user_id)
                dlg.open = False
                page.update()
                show_message("User deleted.", "green")
                refresh_admin()
            except Exception as ex:
                show_message(f"Delete failed: {ex}", "red")

        def close(_):
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
        page.dialog = dlg
        dlg.open = True
        page.update()

    # ---------- USERS UI ----------
    user_items = []
    for u in users:
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
                                        ft.Text(f"{name}  (ID: {uid})", color=title_col, size=12, weight=ft.FontWeight.BOLD),
                                        ft.Text(status_text, color=ft.Colors.RED, size=12, weight=ft.FontWeight.BOLD),
                                    ],
                                ),
                                ft.Text(email, color=SECONDARY_TEXT, size=11),
                                ft.Text(f"Role: {role}", color=SECONDARY_TEXT, size=11),
                            ],
                        ),
                        ft.Row(
                            spacing=6,
                            controls=[
                                action_btn,
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
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

    # ---------- LOG HISTORY UI ----------
    log_items = []
    for log in logs:
        log_items.append(
            ft.Container(
                bgcolor=FORM_BG,
                padding=10,
                border_radius=10,
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
            )
        )

    # --- SEPARATED PANELS (LEFT = Log History, RIGHT = Users) ---
    logs_panel = ft.Container(
        expand=True,
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
                        controls=log_items if log_items else [ft.Text("No logs found.", color=SECONDARY_TEXT, size=12)],
                    ),
                ),
            ],
        ),
    )

    users_panel = ft.Container(
        expand=True,
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
                        controls=user_items if user_items else [ft.Text("No users found.", color=SECONDARY_TEXT, size=12)],
                    ),
                ),
            ],
        ),
    )

    # --- PAGE HEADER (Back + Refresh) ---
    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text("Admin Panel", size=26, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
            ft.Row(
                spacing=10,
                controls=[
                    ft.TextButton("Back", on_click=lambda e: page.go("/"), style=ft.ButtonStyle(color=PRIMARY_TEXT)),
                    ft.TextButton("Refresh", on_click=lambda e: refresh_admin(), style=ft.ButtonStyle(color=PRIMARY_TEXT)),
                ],
            ),
        ],
    )

    return ft.Container(
        padding=20,
        bgcolor=BG_COLOR,
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=14,
            controls=[
                header,
                ft.Row(
                    expand=True,
                    spacing=16,
                    controls=[
                        logs_panel,   # LEFT
                        users_panel,  # RIGHT
                    ],
                ),
            ],
        ),
    )
