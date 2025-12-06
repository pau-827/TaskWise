import flet as ft
from taskwise.app_state import AppState
from taskwise.pages.task_page import TaskPage
from taskwise.pages.calendar_page import CalendarPage
from taskwise.pages.settings_page import SettingsPage


class TaskWiseApp:
    def __init__(self, page: ft.Page):
        self.page = page

        # Shared state
        self.state = AppState()

        # Let state trigger rerenders
        self.state._update_callback = self.update_ui

        # Page modules
        self.task_page = TaskPage(self.state)
        self.calendar_page = CalendarPage(self.state)
        self.settings_page = SettingsPage(self.state)

        # Initial render
        self.update_ui()

    # ----------------------------
    # Header (shared on all pages)
    # ----------------------------
    def _header(self) -> ft.Control:
        C = self.state.colors

        def go(view_name: str):
            self.state.current_view = view_name
            self.state.update()

        def do_logout(e):
            self.state.user = None
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Logged out."), bgcolor=C["SUCCESS_COLOR"])
            self.page.snack_bar.open = True
            go("tasks")

        # Tabs
        def nav_button(label: str, view_name: str):
            active = self.state.current_view == view_name
            text = f"✱ {label} ✱" if active else label
            return ft.TextButton(
                text,
                on_click=lambda e: go(view_name),
                style=ft.ButtonStyle(color=C["TEXT_PRIMARY"]),
            )

        # Profile UI (username beside icon + dropdown)
        if self.state.user:
            user_label = ft.Text(
                self.state.user.get("name", ""),
                size=12,
                weight=ft.FontWeight.BOLD,
                color=C["TEXT_PRIMARY"]
            )
            profile_menu = ft.PopupMenuButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_color=C["TEXT_PRIMARY"],
                items=[
                    ft.PopupMenuItem(text="Logout", on_click=do_logout),
                ],
            )
            right = ft.Row([user_label, profile_menu], spacing=8)
        else:
            profile_menu = ft.PopupMenuButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_color=C["TEXT_PRIMARY"],
                items=[
                    # NOTE: Create Account removed (per your request)
                    ft.PopupMenuItem(text="Login", on_click=lambda e: go("settings")),
                ],
            )
            right = ft.Row([profile_menu], spacing=8)

        return ft.Container(
            bgcolor=C["HEADER_BG"],
            border=ft.border.only(bottom=ft.BorderSide(1, C["BORDER_COLOR"])),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            content=ft.Row(
                [
                    ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=C["TEXT_PRIMARY"]),
                    ft.Row(
                        [
                            nav_button("Tasks", "tasks"),
                            nav_button("Calendar", "calendar"),
                            nav_button("Settings", "settings"),
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
    # MAIN ROUTER / RENDERER
    # ---------------------------------------------------------
    def update_ui(self):
        """Switch UI based on state.current_view."""
        C = self.state.colors

        self.page.clean()
        self.page.bgcolor = C["BG_COLOR"]

        view = self.state.current_view

        if view == "tasks":
            body = self.task_page.view(self.page)
        elif view == "calendar":
            body = self.calendar_page.view(self.page)
        elif view == "settings":
            body = self.settings_page.view(self.page)
        else:
            body = ft.Text(f"Unknown page: {view}", color="red")

        # Main shell with centered/maximized spacing like your wireframes
        shell = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=C["BG_COLOR"],
            content=ft.Container(
                expand=True,
                margin=20,
                border_radius=18,
                bgcolor=C["BG_COLOR"],
                border=ft.border.all(1, C["BORDER_COLOR"]),
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


# -------------------------------------------------------------
# ENTRY POINT FOR MAIN.PY TO START THE ROUTER
# -------------------------------------------------------------
def run_taskwise_app(page: ft.Page):
    page.title = "TaskWise"
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    TaskWiseApp(page)