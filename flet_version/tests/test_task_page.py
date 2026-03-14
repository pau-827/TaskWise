import pytest
from datetime import date, datetime, timedelta

from taskwise.pages.task_page import TaskPage


class MockState:
    def __init__(self):
        self.db = None
        self.user = {"id": 1}
        self.current_filter = "All Tasks"
        self.current_sort = "Custom"
        self.colors = {}


@pytest.fixture
def page():
    return TaskPage(MockState())


# -----------------------------
# Test: date formatting
# -----------------------------
def test_fmt_date(page):

    d = date(2025, 3, 10)

    assert page._fmt_date(d) == "2025-03-10"


# -----------------------------
# Test: time formatting
# -----------------------------
def test_fmt_time_12h(page):

    assert page._fmt_time_12h(13, 5) == "1:05 PM"
    assert page._fmt_time_12h(0, 0) == "12:00 AM"
    assert page._fmt_time_12h(12, 30) == "12:30 PM"


# -----------------------------
# Test: normalize time
# -----------------------------
def test_normalize_time(page):

    assert page._normalize_time_str("13:30") == "1:30 PM"
    assert page._normalize_time_str("1:30 PM") == "1:30 PM"
    assert page._normalize_time_str("") == ""


# -----------------------------
# Test: safe parse date
# -----------------------------
def test_safe_parse_date(page):

    d = page._safe_parse_date("2025-03-10")

    assert isinstance(d, date)
    assert d.year == 2025
    assert d.month == 3
    assert d.day == 10


# -----------------------------
# Test: safe parse datetime
# -----------------------------
def test_safe_parse_datetime(page):

    dt = page._safe_parse_datetime("2025-03-10 1:30 PM")

    assert isinstance(dt, datetime)
    assert dt.year == 2025
    assert dt.month == 3
    assert dt.day == 10


# -----------------------------
# Test: overdue detection
# -----------------------------
def test_is_overdue(page):

    past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    assert page._is_overdue(past, "pending") is True


def test_not_overdue(page):

    future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    assert page._is_overdue(future, "pending") is False


# -----------------------------
# Test: sorting
# -----------------------------
def test_sort_tasks_title(page):

    page.state.current_sort = "Title (A-Z)"

    tasks = [
        (1, "Banana", "", "", "", "", "", ""),
        (2, "Apple", "", "", "", "", "", ""),
    ]

    sorted_tasks = page._sort_tasks(tasks)

    assert sorted_tasks[0][1] == "Apple"
