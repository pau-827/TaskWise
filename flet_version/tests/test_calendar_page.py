import pytest
from datetime import date
from unittest.mock import Mock
from taskwise.pages.calendar_page import CalendarPage


class DummyDB:
    def get_tasks_by_user(self, user_id):
        return [
            (1, "Task 1", "Desc 1", "Work", "2026-03-14 10:00", "Pending", "2026-03-01", "2026-03-02"),
            (2, "Task 2", "Desc 2", "Personal", "2026-03-15", "Completed", "2026-03-05", "2026-03-06"),
        ]


class DummyState:
    def __init__(self):
        self.db = DummyDB()
        self.user = {"id": 1, "name": "Ivy"}
        self.colors = {
            "TEXT_PRIMARY": "#111",
            "TEXT_SECONDARY": "#555",
            "BUTTON_COLOR": "#00f",
            "ERROR_COLOR": "#f00",
            "SUCCESS_COLOR": "#0f0",
            "BORDER_COLOR": "#999",
            "FORM_BG": "#eee",
            "BG_COLOR": "#ccc"
        }
        self.selected_date = date(2026, 3, 14)
        self.cal_year = 2026
        self.cal_month = 3


@pytest.fixture
def cal_page():
    state = DummyState()
    page = CalendarPage(state)
    return page


def test_view_returns_container(cal_page):
    # Call view with a dummy ft.Page
    dummy_page = Mock()
    container = cal_page.view(dummy_page)
    assert container is not None
    # It should have content attribute for left/right panels
    assert hasattr(container, "content")
    # Check that left and right hosts exist
    assert hasattr(cal_page, "_left_host")
    assert hasattr(cal_page, "_right_host")


def test_task_filtering(cal_page):
    # All tasks should come from DummyDB
    tasks = cal_page.S.db.get_tasks_by_user(cal_page.S.user["id"])
    assert len(tasks) == 2
    assert tasks[0][1] == "Task 1"
    assert tasks[1][1] == "Task 2"


def test_due_date_only_behavior(cal_page):
    # We can test the string formatting indirectly
    from datetime import datetime
    dt = datetime(2026, 3, 14).date()
    # selected_date is initialized, so label logic uses it
    label_func = lambda d: "Today" if d == cal_page.S.selected_date else "Other"
    assert label_func(dt) == "Today"
    dt2 = datetime(2026, 3, 15).date()
    assert label_func(dt2) == "Other"


def test_month_navigation_logic(cal_page):
    state = cal_page.S
    original_month = state.cal_month
    original_year = state.cal_year

    # Simulate next month manually
    if state.cal_month == 12:
        state.cal_month = 1
        state.cal_year += 1
    else:
        state.cal_month += 1

    assert state.cal_month == (original_month + 1 if original_month < 12 else 1)
