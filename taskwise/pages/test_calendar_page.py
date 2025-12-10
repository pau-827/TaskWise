import flet as ft
from datetime import date
from taskwise.pages.calendar_page import CalendarPage


# Fake DB matching your real db.py shape + method name
class FakeDB:
    def get_tasks_by_user(self, user_id: int):
        # tuple shape:
        # (id, title, description, category, due_date, status, created_at, updated_at)
        return [
            (1, "Pay Bills", "Electric + Water", "Bills", "2025-01-10 8:30 AM", "pending", "2025-01-01", "2025-01-01"),
            (2, "Project Report", "Submit to professor", "Study", "2025-01-15 1:00 PM", "completed", "2025-01-03", "2025-01-03"),
            (3, "Gym", "Leg day", "Personal", "2025-01-15 6:00 PM", "pending", "2025-01-02", "2025-01-02"),
            (4, "Group Meeting", "Finalize slides", "Work", "2025-01-20", "pending", "2025-01-05", "2025-01-05"),
        ]


class FakeState:
    def __init__(self):
        self.db = FakeDB()

        # Simulate a logged-in user (CalendarPage checks this)
        self.user = {"id": 1, "name": "Test User", "email": "test@example.com", "role": "user"}

        self.colors = {
        "BG_COLOR": "#97C7C3",
        "FORM_BG": "#E3F4F4",
        "BUTTON_COLOR": "#97C7C3",
        "HEADER_BG": "#F8F6F4",
        "TEXT_PRIMARY": "#4A707A",
        "TEXT_SECONDARY": "#6B8F97",
        "BORDER_COLOR": "#4A707A",
        "ERROR_COLOR": "#E53935",
        "SUCCESS_COLOR": "#4CAF50",
        "CHART_COLORS": [ "#035477", "#A855F7"],
        "CHART_BG": "#E3F4F4",
        "CHART_TEXT": "#4A707A",
        }

        # Calendar state (CalendarPage will adjust these if needed)
        self.selected_date = date(2025, 1, 15)
        self.cal_year = 2025
        self.cal_month = 1

        # Will be set in main()
        self._rerender = None

    def update(self):
        # CalendarPage calls S.update() when navigating months/days
        if callable(self._rerender):
            self._rerender()

    def go(self, view_name: str):
        print("Switching to:", view_name)


def main(page: ft.Page):
    page.title = "Calendar Page Test"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#ffffff"
    page.padding = 0

    state = FakeState()
    cal = CalendarPage(state)

    def rerender():
        page.clean()
        page.add(cal.view(page))
        page.update()

    state._rerender = rerender
    rerender()


ft.app(target=main)
