import flet as ft
from task_page import TaskPage
from datetime import datetime

# Minimal fake AppState just enough to run TaskPage UI
class FakeDB:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
    
    def get_all_tasks(self):
        print(f"→ DB: get_all_tasks() returning {len(self.tasks)} tasks")
        return self.tasks
    
    def add_task(self, title, desc, category, due_date):
        task = (
            self.next_id,
            title,
            desc,
            category,
            due_date,
            "pending",
            datetime.now().isoformat()
        )
        self.tasks.append(task)
        print(f"✓ Task added: ID={self.next_id}, Title='{title}', Category='{category}', Due='{due_date}'")
        self.next_id += 1
    
    def update_task(self, task_id, title, desc, category, due_date):
        print(f"✓ Task updated: ID={task_id}")
        for i, t in enumerate(self.tasks):
            if t[0] == task_id:
                self.tasks[i] = (task_id, title, desc, category, due_date, t[5], t[6])
                break
    
    def update_task_status(self, task_id, status):
        print(f"✓ Status updated: ID={task_id} → {status}")
        for i, t in enumerate(self.tasks):
            if t[0] == task_id:
                self.tasks[i] = (t[0], t[1], t[2], t[3], t[4], status, t[6])
                break
    
    def delete_task(self, task_id):
        print(f"✓ Task deleted: ID={task_id}")
        self.tasks = [t for t in self.tasks if t[0] != task_id]

class FakeState:
    def __init__(self, page=None, task_page_instance=None):
        self.page = page
        self.task_page_instance = task_page_instance
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
        self.selected_date = None
        self.cal_year = None
        self.cal_month = None

    def go(self, view):
        print(f"→ Switch view to: {view}")
        
    def update(self):
        """This refreshes the entire task page view"""
        print("→ Updating UI - rebuilding task page...")
        if self.page and self.task_page_instance:
            # Clear and rebuild the entire page
            self.page.controls.clear()
            self.page.add(self.task_page_instance.view(self.page))
            self.page.update()

def main(page: ft.Page):
    state = FakeState(page)
    page.title = "Task Page Test"
    tp = TaskPage(state)
    state.task_page_instance = tp  # Link back for rebuilding
    page.add(tp.view(page))

ft.app(target=main)
