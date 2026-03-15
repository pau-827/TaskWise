import flet as ft
from datetime import datetime, timedelta

from taskwise.app_state import AppState
from taskwise.pages.task_page import TaskPage
from taskwise.pages.calendar_page import CalendarPage
from taskwise.pages.journal_page import JournalPage
from taskwise.pages.settings_page import SettingsPage


class TaskWiseApp:
    def __init__(self, page: ft.Page, on_logout, user=None):
        self.page = page
        self.on_logout = on_logout

        # Pre-declare shell refs as None so update_ui() can guard against
        # being called by on_user_login() before the shell is built
        self._shell:           ft.Container = None
        self._body_host:       ft.Container = None
        self._header_ctrl:     ft.Container = None
        self._nav_refs:        dict         = {}
        self._bell_badge_dot:  ft.Container = None
        self._bell_badge_text: ft.Text      = None

        # Shared state
        self.state = AppState()
        self.state.set_update_callback(self.update_ui)
        self.state.set_delete_account_callback(self.on_logout)
        self.state.set_badge_refresh_callback(self._refresh_badge)

        # Apply logged-in user — triggers on_user_login → update_ui,
        # but the None guard in update_ui means it's a no-op until the shell exists
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
        self.taskpage     = TaskPage(self.state)
        self.calendarpage = CalendarPage(self.state)
        self.journalpage  = JournalPage(self.state)
        self.settingspage = SettingsPage(self.state)

        # -------------------------------------------------------
        # Persistent shell controls — built ONCE, never replaced
        # -------------------------------------------------------

        # Header (also populates _nav_refs, _bell_badge_dot, _bell_badge_text)
        self._header_ctrl = self._build_header()

        # Body host — only .content is swapped on navigation
        self._body_host = ft.Container(expand=True)

        # Full shell — added to page exactly once
        self._shell = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Container(
                expand=True,
                margin=20,
                border_radius=18,
                border=ft.border.all(1, self._c("BORDER_COLOR", "#E5E5E5")),
                content=ft.Column(
                    [
                        self._header_ctrl,
                        ft.Container(
                            expand=True,
                            padding=24,
                            content=ft.Container(
                                expand=True,
                                alignment=ft.alignment.center,
                                content=self._body_host,
                            ),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
        )

        # Default view
        self.state.current_view = "taskpage"

        # Paint the page once — no clean(), no repeated add()
        self.page.bgcolor               = self._c("BG_COLOR", "#FFFFFF")
        self._shell.bgcolor             = self._c("BG_COLOR", "#FFFFFF")
        self._shell.content.bgcolor     = self._c("BG_COLOR", "#FFFFFF")
        self.page.add(self._shell)

        self._swap_body()
        self._refresh_badge()
        self.page.update()

    # ----------------------------------------------------------
    # Tiny helpers
    # ----------------------------------------------------------
    def _c(self, key: str, fallback: str = "#000000") -> str:
        return self.state.colors.get(key, fallback)

    @staticmethod
    def _mounted(ctrl) -> bool:
        return bool(ctrl is not None and getattr(ctrl, "page", None) is not None)

    # ----------------------------------------------------------
    # Notification logic
    # ----------------------------------------------------------
    @staticmethod
    def _parse_due_datetime(due_str: str):
        s = (due_str or "").strip()
        if not s:
            return None
        s = s.replace("T", " ")
        for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
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
        S  = self.state
        db = getattr(S, "db", None)
        if not S.user or not db:
            return 0, []
        try:
            tasks = db.get_tasks_by_user(S.user["id"])
        except Exception:
            return 0, []

        now      = datetime.now()
        horizon  = now + timedelta(hours=24)
        due_soon = []
        for t in tasks:
            try:
                task_id, title, desc, category, due_date, status, created_at, updated_at = t
            except Exception:
                continue
            if (status or "").strip().lower() != "pending":
                continue
            dt = self._parse_due_datetime(due_date or "")
            if dt and dt <= horizon:
                due_soon.append((t, dt))

        due_soon.sort(key=lambda x: x[1])
        return len(due_soon), due_soon

    def _refresh_badge(self):
        """Update the bell badge count in-place — no full redraw."""
        count, _ = self._get_due_soon_tasks()
        if self._bell_badge_dot and self._bell_badge_text:
            self._bell_badge_dot.visible = count > 0
            self._bell_badge_text.value  = str(min(count, 99))
            if self._mounted(self._bell_badge_dot):
                self._bell_badge_dot.update()

    def _show_notifications_dialog(self):
        C  = self.state.colors
        db = getattr(self.state, "db", None)

        def color(key, fallback):
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
                    tight=True, spacing=8,
                    controls=[
                        ft.Text("No tasks due in the next 24 hours.", color=color("TEXT_PRIMARY", "#111111")),
                        ft.Text("You're all caught up.", size=12, color=color("TEXT_SECONDARY", "#666666")),
                    ],
                )
            else:
                rows = []
                for (t, dt) in items[:15]:
                    task_id, title, desc, category, due_date, status, created_at, updated_at = t
                    when = dt.strftime("%b %d, %Y %I:%M %p")
                    cat  = (category or "").strip() or "No Category"
                    rows.append(
                        ft.Container(
                            border_radius=12,
                            bgcolor="white",
                            border=ft.border.all(1, color("BORDER_COLOR", "#E5E5E5")),
                            padding=12,
                            content=ft.Column(
                                tight=True, spacing=4,
                                controls=[
                                    ft.Text(title or "Untitled", weight=ft.FontWeight.BOLD, color=color("TEXT_PRIMARY", "#111111")),
                                    ft.Row(spacing=10, controls=[
                                        ft.Text(f"Due: {when}", size=12, color=color("TEXT_SECONDARY", "#666666")),
                                        ft.Text(f"• {cat}",     size=12, color=color("TEXT_SECONDARY", "#666666")),
                                    ]),
                                ],
                            ),
                        )
                    )
                content = ft.Column(tight=True, spacing=10, controls=rows)

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=color("FORM_BG", "#F7F7F7"),
            title=ft.Text("Notifications", weight=ft.FontWeight.BOLD, color=color("TEXT_PRIMARY", "#111111")),
            content=ft.Container(
                width=520, height=420, padding=8,
                content=ft.ListView(expand=True, spacing=10, controls=[content]),
            ),
            actions=[ft.TextButton("Close", on_click=close_dialog)],
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    # ----------------------------------------------------------
    # Header — built once, mutated in-place on nav changes
    # ----------------------------------------------------------
    def _build_header(self) -> ft.Container:
        C = self.state.colors

        def color(key, fallback):
            return C.get(key, fallback)

        def do_logout(e):
            self.state.on_user_logout()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Logged out."),
                bgcolor=color("SUCCESS_COLOR", "#22C55E"),
            )
            self.page.snack_bar.open = True
            self.page.update()
            self.on_logout()

        def make_nav_btn(label: str, view_name: str) -> ft.TextButton:
            btn = ft.TextButton(
                label,
                on_click=lambda e, v=view_name: self._navigate(v),
                style=ft.ButtonStyle(color=color("TEXT_PRIMARY", "#111111")),
            )
            self._nav_refs[view_name] = btn
            return btn

        # Bell badge
        self._bell_badge_text = ft.Text("0", size=10, color="white", weight=ft.FontWeight.BOLD)
        self._bell_badge_dot  = ft.Container(
            visible=False,
            right=6, top=6,
            width=18, height=18,
            border_radius=9,
            bgcolor=color("ERROR_COLOR", "#EF4444"),
            alignment=ft.alignment.center,
            content=self._bell_badge_text,
        )

        bell_with_badge = ft.Stack(
            width=44, height=44,
            controls=[
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS_NONE,
                        icon_color=color("TEXT_PRIMARY", "#111111"),
                        tooltip="Notifications",
                        on_click=lambda e: self._show_notifications_dialog(),
                    ),
                ),
                self._bell_badge_dot,
            ],
        )

        if self.state.user:
            username = (self.state.user.get("username") or self.state.user.get("name") or "User").strip()
            right = ft.Row(
                [
                    ft.Text(username, size=12, weight=ft.FontWeight.BOLD, color=color("TEXT_PRIMARY", "#111111")),
                    ft.PopupMenuButton(
                        icon=ft.Icons.ACCOUNT_CIRCLE,
                        icon_color=color("TEXT_PRIMARY", "#111111"),
                        items=[ft.PopupMenuItem(text="Logout", on_click=do_logout)],
                    ),
                    bell_with_badge,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            right = ft.Row(
                [ft.Text("Guest", size=12, color=color("TEXT_PRIMARY", "#111111")), bell_with_badge],
                spacing=8,
            )

        return ft.Container(
            bgcolor=color("HEADER_BG", color("BG_COLOR", "#FFFFFF")),
            border=ft.border.only(bottom=ft.BorderSide(1, color("BORDER_COLOR", "#E5E5E5"))),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            content=ft.Row(
                [
                    ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=color("TEXT_PRIMARY", "#111111")),
                    ft.Row(
                        [
                            make_nav_btn("Tasks",    "taskpage"),
                            make_nav_btn("Journal",  "journalpage"),
                            make_nav_btn("Calendar", "calendarpage"),
                            make_nav_btn("Settings", "settingspage"),
                        ],
                        spacing=10,
                    ),
                    right,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _refresh_nav(self):
        """Update nav button labels in-place to show the active indicator."""
        labels = {
            "taskpage":     "Tasks",
            "journalpage":  "Journal",
            "calendarpage": "Calendar",
            "settingspage": "Settings",
        }
        current = self.state.current_view
        for view_name, btn in self._nav_refs.items():
            label    = labels.get(view_name, view_name)
            btn.text = f"✱ {label} ✱" if view_name == current else label
            if self._mounted(btn):
                btn.update()

    def _navigate(self, view_name: str):
        """Switch view without tearing down the shell."""
        self.state.current_view = view_name
        self._refresh_nav()
        self._swap_body()
        self._refresh_badge()

    # ----------------------------------------------------------
    # Body swap — only the inner content changes
    # ----------------------------------------------------------
    def _swap_body(self):
        view = self.state.current_view
        if view == "taskpage":
            body = self.taskpage.view(self.page)
        elif view == "calendarpage":
            body = self.calendarpage.view(self.page)
        elif view == "journalpage":
            body = self.journalpage.view(self.page)
        elif view == "settingspage":
            body = self.settingspage.view(self.page)
        else:
            body = ft.Text(f"Unknown page: {view}", color="red")

        self._body_host.content = body
        if self._mounted(self._body_host):
            self._body_host.update()

    # ----------------------------------------------------------
    # update_ui — called by state.update() / state.go()
    # Keeps the shell alive; only repaints what changed.
    # ----------------------------------------------------------
    def update_ui(self):
        # Guard: shell may not be built yet (called during on_user_login)
        if self._shell is None:
            return

        # Repaint backgrounds in case theme changed
        self.page.bgcolor               = self._c("BG_COLOR", "#FFFFFF")
        self._shell.bgcolor             = self._c("BG_COLOR", "#FFFFFF")
        self._shell.content.bgcolor     = self._c("BG_COLOR", "#FFFFFF")
        self._shell.content.border      = ft.border.all(1, self._c("BORDER_COLOR", "#E5E5E5"))
        self._header_ctrl.bgcolor       = self._c("HEADER_BG", self._c("BG_COLOR", "#FFFFFF"))
        self._header_ctrl.border        = ft.border.only(
            bottom=ft.BorderSide(1, self._c("BORDER_COLOR", "#E5E5E5"))
        )

        self._refresh_nav()
        self._swap_body()
        self._refresh_badge()

        if self._mounted(self._shell):
            self._shell.update()
        self.page.update()


def run_taskwise_app(page: ft.Page, on_logout, user=None):
    # Clean the page before mounting the app shell so the login screen
    # (or any previous view) doesn't linger underneath
    page.clean()
    page.title            = "TaskWise"
    page.window_maximized = True
    page.theme_mode       = ft.ThemeMode.LIGHT
    page.padding          = 0

    TaskWiseApp(page, on_logout, user=user)