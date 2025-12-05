import flet as ft
from taskwise.app_state import AppState
from taskwise.pages.task_page import TaskPage
from taskwise.pages.calendar_page import CalendarPage
from taskwise.pages.settings_page import SettingsPage


class TaskWiseApp:
    def __init__(self, page: ft.Page):
        self.page = page

        # Create shared state
        self.state = AppState()

        # Attach update callback to state
        self.state._update_callback = self.update_ui

        # Create page modules
        self.task_page = TaskPage(self.state)
        self.calendar_page = CalendarPage(self.state)
        self.settings_page = SettingsPage(self.state)

        # Initial load
        self.update_ui()

    # ---------------------------------------------------------
    # MAIN ROUTER / RENDERER
    # ---------------------------------------------------------
    def update_ui(self):
        """Switch UI based on state.current_view."""
        self.page.clean()  # clear old UI

        view = self.state.current_view

        if view == "tasks":
            ui = self.task_page.view(self.page)

        elif view == "calendar":
            ui = self.calendar_page.view(self.page)

        elif view == "settings":
            ui = self.settings_page.view(self.page)

        else:
            ui = ft.Text(f"Unknown page: {view}", color="red")

        self.page.add(ui)
        self.page.update()


# -------------------------------------------------------------
# ENTRY POINT FOR MAIN.PY TO START THE ROUTER
# -------------------------------------------------------------
def run_taskwise_app(page: ft.Page):
    page.title = "TaskWise"
    page.window_width = 1000
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.LIGHT

    TaskWiseApp(page)