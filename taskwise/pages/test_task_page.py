import flet as ft
from datetime import date

from taskwise.pages.task_page import TaskPage


class FakeDB:
    def __init__(self):
        self._next_id = 6
        self._tasks = [
            (1, "Pay Bills", "Electric + Water", "Bills", "2025-01-10 8:30 AM", "pending", "2025-01-01", "2025-01-01"),
            (2, "Project Report", "Submit to professor", "Study", "2025-01-15 1:00 PM", "completed", "2025-01-03", "2025-01-03"),
            (3, "Gym", "Leg day", "Personal", "2025-01-15 6:00 PM", "pending", "2025-01-02", "2025-01-02"),
            (4, "Client Call", "Weekly check-in", "Work", "2025-01-09 10:00 AM", "pending", "2025-01-02", "2025-01-02"),
            (5, "Buy Groceries", "Milk, eggs, rice", "Others", "2025-01-08", "pending", "2025-01-02", "2025-01-02"),
        ]

    def get_tasks_by_user(self, user_id: int):
        return list(self._tasks)

    def add_task(self, user_id, title, description="", category="", due_date=""):
        row = (
            self._next_id,
            title,
            description,
            category,
            due_date,
            "pending",
            "2025-01-06",
            "2025-01-06",
        )
        self._next_id += 1
        self._tasks.insert(0, row)

    def update_task(self, user_id, task_id, title, description, category, due_date, status):
        updated = []
        for t in self._tasks:
            if t[0] == task_id:
                updated.append((task_id, title, description, category, due_date, status, t[6], "2025-01-06"))
            else:
                updated.append(t)
        self._tasks = updated

    def update_task_status(self, user_id, task_id, status):
        updated = []
        for t in self._tasks:
            if t[0] == task_id:
                updated.append((t[0], t[1], t[2], t[3], t[4], status, t[6], "2025-01-06"))
            else:
                updated.append(t)
        self._tasks = updated

    def delete_task(self, user_id, task_id):
        self._tasks = [t for t in self._tasks if t[0] != task_id]


class FakeState:
    def __init__(self):
        self.db = FakeDB()

        # TaskPage needs user + id
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

        self.theme_name = "Light Mode"
        self.current_filter = "All Tasks"
        self.current_sort = "Custom"

        # Used when TaskPage jumps to calendar
        self.selected_date = date(2025, 1, 15)
        self.cal_year = 2025
        self.cal_month = 1

        self._rerender = None

    def update(self):
        if callable(self._rerender):
            self._rerender()

    def go(self, view):
        print("Switch view →", view)


def main(page: ft.Page):
    page.title = "Task Page Test"
    page.window_width = 1200
    page.window_height = 750
    page.padding = 0
    page.bgcolor = "#ffffff"

    state = FakeState()
    tp = TaskPage(state)

    def rerender():
        page.controls.clear()
        page.add(tp.view(page))
        page.update()

    state._rerender = rerender
    rerender()


ft.app(target=main)
