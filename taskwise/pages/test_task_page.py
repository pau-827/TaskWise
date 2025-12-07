import flet as ft
from task_page import TaskPage

# Minimal fake AppState just enough to run TaskPage UI
class FakeDB:
    def get_all_tasks(self):
        return []
    def add_task(self, *a):
        pass
    def update_task(self, *a):
        pass
    def update_task_status(self, *a):
        pass
    def delete_task(self, *a):
        pass

class FakeState:
    def __init__(self):
        self.db = FakeDB()
        self.current_view = "tasks"
        self.colors = {
            "BG_COLOR": "#ffffff",
            "FORM_BG": "#f5f5f5",
            "BUTTON_COLOR": "#4F46E5",
            "HEADER_BG": "#ffffff",
            "TEXT_PRIMARY": "#333333",
            "TEXT_SECONDARY": "#777777",
            "BORDER_COLOR": "#dddddd",
            "ERROR_COLOR": "#dc2626",
            "SUCCESS_COLOR": "#16a34a",
        }
        self.theme_name = "Light Mode"
        self.categories = ["Personal", "Work", "Study", "Bills", "Others"]
        self.current_filter = "All Tasks"
        self.user = {"name": "Guest", "email": "guest@example.com"}
        self._update_callback = None

    def go(self, view):
        print("Switch view →", view)

def main(page: ft.Page):
    state = FakeState()
    page.title = "Task Page Test"
    tp = TaskPage(state)
    page.add(tp.view(page))

ft.app(target=main)