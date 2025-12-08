import flet as ft
from datetime import datetime, timedelta

from taskwise.app_state import AppState
from taskwise.pages.task_page import TaskPage
from taskwise.pages.calendar_page import CalendarPage
from taskwise.pages.settings_page import SettingsPage


class TaskWiseApp:
    def __init__(self, page: ft.Page, on_logout, user=None):
        self.page = page
        self.on_logout = on_logout

        # Shared state
        self.state = AppState()
        self.state.set_update_callback(self.update_ui)

        # Apply logged-in user (safe)
        user = user or {}
        self.state.on_user_login(
            {
                "id": user.get("id"),
                "username": user.get("username"),
                "name": user.get("name") or user.get("username") or "User",
                "email": user.get("email") or "Not signed in",
                "role": user.get("role"),
            }
        )

        # Pages
        self.taskpage = TaskPage(self.state)
        self.calendarpage = CalendarPage(self.state)
        self.settingspage = SettingsPage(self.state)

        # Default view
        self.state.current_view = "taskpage"

        # Render
        self.update_ui()

    # ----------------------------
    # Notification helpers
    # ----------------------------
    @staticmethod
    def _parse_due_datetime(due_str: str):
        s = (due_str or "").strip()
        if not s:
            return None

        s = s.replace("T", " ")

        for fmt in (
            "%Y-%m-%d %I:%M %p",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(s, fmt)
                if fmt == "%Y-%m-%d":
                    return datetime(dt.year, dt.month, dt.day, 23, 59)
                return dt
            except Exception:
                continue

        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None

    def _get_due_soon_tasks(self):
        S = self.state
        db = getattr(S, "db", None)
        if not S.user or not db:
            return 0, []

        try:
            tasks = db.get_tasks_by_user(S.user["id"])
        except Exception:
            return 0, []

        now = datetime.now()
        horizon = now + timedelta(hours=24)

        due_soon = []
        for t in tasks:
            try:
                task_id, title, desc, category, due_date, status, created_at, updated_at = t
            except Exception:
                continue

            if (status or "").strip().lower() != "pending":
                continue

            dt = self._parse_due_datetime(due_date or "")
            if not dt:
                continue

            if dt <= horizon:
                due_soon.append((t, dt))

        due_soon.sort(key=lambda x: x[1])
        return len(due_soon), due_soon

    def _show_notifications_dialog(self):
        C = self.state.colors
        db = getattr(self.state, "db", None)

        def color(key: str, fallback: str):
            return C.get(key, fallback)

        def close_dialog(e=None):
            dlg.open = False
            self.page.update()

        if not self.state.user or not db:
            content = ft.Text("Please login first.", color=color("TEXT_SECONDARY", "#666666"))
        else:
            count, items = self._get_due_soon_tasks()
            if count == 0:
                content = ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        ft.Text("No tasks due in the next 24 hours.", color=color("TEXT_PRIMARY", "#111111")),
                        ft.Text("You’re all caught up.", size=12, color=color("TEXT_SECONDARY", "#666666")),
                    ],
                )
            else:
                rows = []
                for (t, dt) in items[:15]:
                    task_id, title, desc, category, due_date, status, created_at, updated_at = t
                    when = dt.strftime("%b %d, %Y %I:%M %p")
                    cat = (category or "").strip() or "No Category"

                    rows.append(
                        ft.Container(
                            border_radius=12,
                            bgcolor="white",
                            border=ft.border.all(1, color("BORDER_COLOR", "#E5E5E5")),
                            padding=12,
                            content=ft.Column(
                                tight=True,
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        title or "Untitled",
                                        weight=ft.FontWeight.BOLD,
                                        color=color("TEXT_PRIMARY", "#111111"),
                                    ),
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Text(
                                                f"Due: {when}",
                                                size=12,
                                                color=color("TEXT_SECONDARY", "#666666"),
                                            ),
                                            ft.Text(
                                                f"• {cat}",
                                                size=12,
                                                color=color("TEXT_SECONDARY", "#666666"),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        )
                    )

                content = ft.Column(tight=True, spacing=10, controls=rows)

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=color("FORM_BG", "#F7F7F7"),
            title=ft.Text(
                "Notifications",
                weight=ft.FontWeight.BOLD,
                color=color("TEXT_PRIMARY", "#111111"),
            ),
            content=ft.Container(
                width=520,
                height=420,
                padding=8,
                content=ft.ListView(expand=True, spacing=10, controls=[content]),
            ),
            actions=[ft.TextButton("Close", on_click=close_dialog)],
            shape=ft.RoundedRectangleBorder(radius=16),
        )

        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _open_notification_settings(self):
        try:
            if hasattr(self.settingspage, "show_notification_dialog"):
                self.settingspage.show_notification_dialog()
                return
        except Exception:
            pass

        self._show_notifications_dialog()

    # ----------------------------
    # HEADER (UPDATED)
    # ----------------------------
    def _header(self) -> ft.Control:
        C = self.state.colors

        def color(key: str, fallback: str):
            return C.get(key, fallback)

        def go(view_name: str):
            self.state.go(view_name)

        def do_logout(e):
            self.state.on_user_logout()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Logged out."),
                bgcolor=color("SUCCESS_COLOR", "#22C55E"),
            )
            self.page.snack_bar.open = True
            self.page.update()
            self.on_logout()

        def nav_button(label: str, view_name: str):
            active = self.state.current_view == view_name
            text = f"✱ {label} ✱" if active else label
            return ft.TextButton(
                text,
                on_click=lambda e: go(view_name),
                style=ft.ButtonStyle(color=color("TEXT_PRIMARY", "#111111")),
            )

        notif_count, _ = self._get_due_soon_tasks()

        bell_icon = ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS_NONE,
            icon_color=color("TEXT_PRIMARY", "#111111"),
            tooltip="Notifications",
            on_click=lambda e: self._show_notifications_dialog(),
        )

        bell_with_badge = ft.Stack(
            width=44,
            height=44,
            controls=[
                ft.Container(alignment=ft.alignment.center, content=bell_icon),
                ft.Container(
                    visible=notif_count > 0,
                    right=6,
                    top=6,
                    width=18,
                    height=18,
                    border_radius=9,
                    bgcolor=color("ERROR_COLOR", "#EF4444"),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        str(min(notif_count, 99)),
                        size=10,
                        color="white",
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
            ],
        )

        # ----------------------------
        # UPDATED HERE ↓↓↓
        # Move bell AFTER username + profile icon
        # ----------------------------
        if self.state.user:
            username = (
                self.state.user.get("username")
                or self.state.user.get("name")
                or "User"
            ).strip()

            user_label = ft.Text(
                username,
                size=12,
                weight=ft.FontWeight.BOLD,
                color=color("TEXT_PRIMARY", "#111111"),
            )

            profile_menu = ft.PopupMenuButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_color=color("TEXT_PRIMARY", "#111111"),
                items=[ft.PopupMenuItem(text="Logout", on_click=do_logout)],
            )

            # NEW ORDER: name → profile → bell
            right = ft.Row(
                [
                    user_label,
                    profile_menu,
                    bell_with_badge,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            right = ft.Row(
                [
                    ft.Text("Guest", size=12, color=color("TEXT_PRIMARY", "#111111")),
                    bell_with_badge,
                ],
                spacing=8,
            )

        return ft.Container(
            bgcolor=color("HEADER_BG", color("BG_COLOR", "#FFFFFF")),
            border=ft.border.only(bottom=ft.BorderSide(1, color("BORDER_COLOR", "#E5E5E5"))),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            content=ft.Row(
                [
                    ft.Text(
                        "TaskWise",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=color("TEXT_PRIMARY", "#111111"),
                    ),
                    ft.Row(
                        [
                            nav_button("Tasks", "taskpage"),
                            nav_button("Calendar", "calendarpage"),
                            nav_button("Settings", "settingspage"),
                        ],
                        spacing=10,
                    ),
                    right,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # ---------------------------------------------------------
    # MAIN ROUTER
    # ---------------------------------------------------------
    def update_ui(self):
        C = self.state.colors

        def color(key: str, fallback: str):
            return C.get(key, fallback)

        self.page.clean()
        self.page.bgcolor = color("BG_COLOR", "#FFFFFF")

        view = self.state.current_view

        if view == "taskpage":
            body = self.taskpage.view(self.page)
        elif view == "calendarpage":
            body = self.calendarpage.view(self.page)
        elif view == "settingspage":
            body = self.settingspage.view(self.page)
        else:
            body = ft.Text(f"Unknown page: {view}", color="red")

        shell = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=color("BG_COLOR", "#FFFFFF"),
            content=ft.Container(
                expand=True,
                margin=20,
                border_radius=18,
                bgcolor=color("BG_COLOR", "#FFFFFF"),
                border=ft.border.all(1, color("BORDER_COLOR", "#E5E5E5")),
                content=ft.Column(
                    [
                        self._header(),
                        ft.Container(
                            expand=True,
                            padding=24,
                            content=ft.Container(
                                expand=True,
                                alignment=ft.alignment.center,
                                content=body,
                            ),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
        )

        self.page.add(shell)
        self.page.update()


def run_taskwise_app(page: ft.Page, on_logout, user=None):
    page.title = "TaskWise"
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    TaskWiseApp(page, on_logout, user=user)