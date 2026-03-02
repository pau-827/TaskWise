import flet as ft
from database import db


def get_admin_page(
    page,
    PRIMARY_TEXT,
    SECONDARY_TEXT,
    BUTTON_COLOR,
    BG_COLOR,
    FORM_BG,
    on_logout=None,
):
    # -----------------------------
    # ✅ Pink Admin Theme (override incoming colors)
    # -----------------------------
    PINK_BG = "#FFF1F6"
    PINK_SOFT = "#FFE4EF"
    PINK_CARD = "#FFD1E3"
    PINK_STRONG = "#FF4D8D"
    PINK_DARK = "#8A2E54"
    TEXT_DARK = "#3A2A33"
    TEXT_MUTED = "#6C5A65"
    WHITE = "white"

    # override passed palette so the whole admin page matches front page
    BG_COLOR = PINK_BG
    FORM_BG = "#FFF7FA"
    BUTTON_COLOR = PINK_STRONG
    PRIMARY_TEXT = PINK_DARK
    SECONDARY_TEXT = TEXT_MUTED

    # -----------------------------
    # Data
    # -----------------------------
    logs = db.get_logs()

    try:
        users = db.get_users()
    except Exception:
        users = []

    # Remove the admin account from the user list
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

    # -----------------------------
    # Helpers
    # -----------------------------
    def show_message(text: str, color=PINK_STRONG):
        snack = ft.SnackBar(content=ft.Text(text, color="white"), bgcolor=color, duration=2200)
        try:
            page.overlay.append(snack)
            snack.open = True
        except Exception:
            page.snack_bar = snack
            page.snack_bar.open = True
        page.update()

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

    def ban_user(user_id: int):
        try:
            db.ban_user(int(user_id))
            try:
                db.add_log("BAN", f"Admin banned user_id={int(user_id)}", user_id=int(user_id))
            except Exception:
                pass
            show_message("User banned.", PINK_STRONG)
            refresh_admin()
        except Exception as ex:
            show_message(f"Ban failed: {ex}", "#E11D48")

    def unban_user(user_id: int):
        try:
            db.unban_user(int(user_id))
            try:
                db.add_log("UNBAN", f"Admin unbanned user_id={int(user_id)}", user_id=int(user_id))
            except Exception:
                pass
            show_message("Ban lifted.", "#16A34A")
            refresh_admin()
        except Exception as ex:
            show_message(f"Unban failed: {ex}", "#E11D48")

    def confirm_delete(user_id: int):
        if user_id is None:
            show_message("Delete failed: invalid user id.", "#E11D48")
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

                show_message("User deleted.", "#E11D48")
                refresh_admin()
            except Exception as ex:
                show_message(f"Delete failed: {ex}", "#E11D48")

        def close(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=WHITE,
            title=ft.Text("Delete User?", color=PRIMARY_TEXT, weight=ft.FontWeight.BOLD),
            content=ft.Text("This will permanently remove the account and data.", color=SECONDARY_TEXT),
            actions=[
                ft.TextButton("Cancel", on_click=close),
                ft.ElevatedButton("Delete", on_click=do_delete, bgcolor="#E11D48", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=14),
        )

        if dlg not in page.overlay:
            page.overlay.append(dlg)

        dlg.open = True
        page.update()

    # -----------------------------
    # ✅ UI helpers (pink + nicer spacing)
    # -----------------------------
    def section_title(text: str, icon):
        return ft.Row(
            spacing=10,
            controls=[
                ft.Container(
                    width=34,
                    height=34,
                    border_radius=12,
                    bgcolor=PINK_SOFT,
                    alignment=ft.alignment.center,
                    content=ft.Icon(icon, color=PINK_STRONG, size=18),
                ),
                ft.Text(text, size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
            ],
        )

    def soft_card(content, padding=16):
        return ft.Container(
            border_radius=18,
            bgcolor=WHITE,
            border=ft.border.all(1, "#FFD6E6"),
            padding=padding,
            shadow=ft.BoxShadow(blur_radius=14, color="#00000010", offset=ft.Offset(0, 8)),
            content=content,
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        )

    # -----------------------------
    # UI State (search + tabs)
    # -----------------------------
    search_tf = ft.TextField(
        hint_text="Search users by name or email...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=WHITE,
        filled=True,
        border_radius=14,
        border_color="#FFD6E6",
        focused_border_color=PINK_STRONG,
        color=TEXT_DARK,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
    )

    tab = ft.Tabs(
        selected_index=0,
        indicator_color=PINK_STRONG,
        label_color=PRIMARY_TEXT,
        unselected_label_color=SECONDARY_TEXT,
        tabs=[
            ft.Tab(text="Users"),
            ft.Tab(text="Logs"),
        ],
    )

    # -----------------------------
    # Build user cards (filtered by search)
    # -----------------------------
    def build_user_cards():
        q = (search_tf.value or "").strip().lower()

        to_render = []
        for u in filtered_users:
            if isinstance(u, dict):
                name = (u.get("name") or "").strip()
                email = (u.get("email") or "").strip()
            else:
                name = (u[1] if len(u) > 1 else "").strip()
                email = (u[2] if len(u) > 2 else "").strip()

            text = f"{name} {email}".lower()
            if q and q not in text:
                continue
            to_render.append(u)

        cards = []
        for display_id, u in enumerate(to_render, start=1):
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

            badge = ft.Container()
            if is_banned:
                badge = ft.Container(
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    border_radius=999,
                    bgcolor="#FFE4E6",
                    border=ft.border.all(1, "#FDA4AF"),
                    content=ft.Text("BANNED", size=11, color="#E11D48", weight=ft.FontWeight.BOLD),
                )

            action_btn = (
                ft.IconButton(
                    icon=ft.Icons.LOCK_OPEN,
                    tooltip="Lift ban",
                    icon_color="#16A34A",
                    on_click=(lambda e, _uid=uid: unban_user(_uid)),
                )
                if is_banned
                else ft.IconButton(
                    icon=ft.Icons.BLOCK,
                    tooltip="Ban user",
                    icon_color="#E11D48",
                    on_click=(lambda e, _uid=uid: ban_user(_uid)),
                )
            )

            avatar_bg = PINK_STRONG if not is_banned else "#F472B6"

            card = soft_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            expand=True,
                            spacing=14,
                            controls=[
                                ft.CircleAvatar(
                                    radius=22,
                                    bgcolor=avatar_bg,
                                    content=ft.Text((name[:1] or "U").upper(), color="white", weight=ft.FontWeight.BOLD),
                                ),
                                ft.Column(
                                    expand=True,
                                    spacing=4,
                                    controls=[
                                        ft.Row(
                                            spacing=10,
                                            controls=[
                                                ft.Text(name or "Unnamed", size=14, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                                badge,
                                            ],
                                        ),
                                        ft.Text(email or "No email", size=12, color=TEXT_MUTED),
                                        ft.Row(
                                            spacing=10,
                                            controls=[
                                                ft.Container(
                                                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                                    border_radius=999,
                                                    bgcolor=PINK_SOFT,
                                                    border=ft.border.all(1, "#FFD6E6"),
                                                    content=ft.Text(f"ID: {display_id}", size=11, color=PINK_DARK, weight=ft.FontWeight.W_600),
                                                ),
                                                ft.Container(
                                                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                                    border_radius=999,
                                                    bgcolor="#FFF7FA",
                                                    border=ft.border.all(1, "#FFD6E6"),
                                                    content=ft.Text(f"Role: {role or 'user'}", size=11, color=PINK_DARK, weight=ft.FontWeight.W_600),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=6,
                            controls=[
                                action_btn,
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    tooltip="Delete user",
                                    icon_color="#E11D48",
                                    on_click=(lambda e, _uid=uid: confirm_delete(_uid)),
                                ),
                            ],
                        ),
                    ],
                ),
                padding=16,
            )

            def _hover(e, c=card):
                if e.data == "true":
                    c.scale = 1.01
                else:
                    c.scale = 1.0
                page.update()

            card.on_hover = _hover
            cards.append(card)

        if not cards:
            return [
                soft_card(
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.PEOPLE_OUTLINED, size=44, color=TEXT_MUTED),
                            ft.Text("No users found.", size=13, color=TEXT_MUTED),
                        ],
                    ),
                    padding=20,
                )
            ]
        return cards

    # -----------------------------
    # Build log cards
    # -----------------------------
    def build_log_cards():
        cards = []
        for log in logs:
            action = (log.get("action") or "").strip().upper()

            accent = PINK_STRONG
            if "DELETE" in action:
                accent = "#E11D48"
            elif "BAN" in action:
                accent = "#E11D48"
            elif "UNBAN" in action:
                accent = "#16A34A"

            cards.append(
                soft_card(
                    ft.Row(
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Container(
                                width=10,
                                height=10,
                                border_radius=99,
                                bgcolor=accent,
                                margin=ft.margin.only(top=6),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=4,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(action or "ACTION", size=13, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                            ft.Text(str(log.get("created_at") or ""), size=11, color=TEXT_MUTED),
                                        ],
                                    ),
                                    ft.Text(f"User ID: {log.get('user_id')}", size=12, color=TEXT_MUTED),
                                    ft.Text(f"Email: {log.get('email')}", size=12, color=TEXT_MUTED),
                                    ft.Text(f"Details: {log.get('details')}", size=12, color=TEXT_MUTED),
                                ],
                            ),
                        ],
                    ),
                    padding=16,
                )
            )

        if not cards:
            return [
                soft_card(
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=44, color=TEXT_MUTED),
                            ft.Text("No logs found.", size=13, color=TEXT_MUTED),
                        ],
                    ),
                    padding=20,
                )
            ]
        return cards

    # -----------------------------
    # Main content host (switch by tab)
    # -----------------------------
    content_host = ft.Container(expand=True)

    def render():
        if tab.selected_index == 0:
            content_host.content = ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    section_title("Users", ft.Icons.PEOPLE_OUTLINED),
                    ft.Container(expand=True, content=ft.ListView(expand=True, spacing=10, controls=build_user_cards())),
                ],
            )
        else:
            content_host.content = ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    section_title("Log History", ft.Icons.RECEIPT_LONG_OUTLINED),
                    ft.Container(expand=True, content=ft.ListView(expand=True, spacing=10, controls=build_log_cards())),
                ],
            )
        page.update()

    def on_search_change(e):
        if tab.selected_index == 0:
            render()

    def on_tab_change(e):
        render()

    search_tf.on_change = on_search_change
    tab.on_change = on_tab_change

    # -----------------------------
    # Header (top section)
    # -----------------------------
    header = soft_card(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            width=44,
                            height=44,
                            border_radius=14,
                            bgcolor=PINK_STRONG,
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color="white"),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Admin Panel", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                ft.Text("Manage users and review system logs.", size=12, color=TEXT_MUTED),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh",
                            icon_color=PINK_DARK,
                            on_click=lambda e: refresh_admin(),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            tooltip="Logout",
                            icon_color=PINK_DARK,
                            on_click=do_logout,
                        ),
                    ],
                ),
            ],
        ),
        padding=18,
    )

    # first render
    render()

    # -----------------------------
    # Page layout
    # -----------------------------
    return ft.Container(
        expand=True,
        bgcolor=BG_COLOR,
        padding=18,
        content=ft.Column(
            expand=True,
            spacing=14,
            controls=[
                header,
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(expand=True, content=search_tf),
                        ft.Container(width=260, content=tab),
                    ],
                ),
                ft.Container(
                    expand=True,
                    border_radius=22,
                    bgcolor=FORM_BG,
                    border=ft.border.all(1, "#FFD6E6"),
                    padding=18,
                    content=content_host,
                ),
            ],
        ),
    )