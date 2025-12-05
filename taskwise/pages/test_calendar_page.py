import flet as ft
from calendar_page import CalendarPage

# Minimal fake DB so calendar can display tasks
class FakeDB:
    def get_all_tasks(self):
        # Preload some sample tasks for testing
        return [
            (1, "Pay Bills", "Electric + Water", "Bills", "2025-01-10", "pending", "2025-01-01"),
            (2, "Project Report", "Submit to professor", "Study", "2025-01-15", "completed", "2025-01-03"),
            (3, "Gym", "Leg day", "Personal", "2025-01-15", "pending", "2025-01-02"),
        ]

class FakeState:
    def __init__(self):
        self.db = FakeDB()
        self.current_view = "calendar"
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

        # Calendar state
        self.cal_year = 2025
        self.cal_month = 1
        self.selected_date = None

    def go(self, view_name):
        print("Switching to:", view_name)

def main(page: ft.Page):
    state = FakeState()
    page.title = "Calendar Page Test"
    cp = CalendarPage(state)
    page.add(cp.view(page))

ft.app(target=main)
