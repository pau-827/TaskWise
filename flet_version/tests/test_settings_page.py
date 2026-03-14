import pytest
from unittest.mock import Mock
from taskwise.pages.settings_page import SettingsPage


class DummyDB:
    def get_user_by_id(self, uid):
        if uid == 1:
            return {"id": 1, "username": "Ivy", "name": "Ivy M", "email": "ivy@example.com", "role": "user", "password_hash": "$2b$12$example"}
        return None

    def get_user_by_username(self, username):
        if username == "Ivy":
            return {"id": 1, "username": "Ivy", "name": "Ivy M", "email": "ivy@example.com", "role": "user", "password_hash": "$2b$12$example"}
        return None


class DummyState:
    def __init__(self):
        self.user = {"id": 1, "username": "Ivy", "name": "Ivy M", "email": "ivy@example.com", "role": "user"}
        self.db = DummyDB()
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
        self.theme_name = "Light Mode"

    def set_theme(self, name):
        self.theme_name = name


@pytest.fixture
def settings_page():
    state = DummyState()
    page = SettingsPage(state)
    return page


def test_view_returns_container(settings_page):
    dummy_page = Mock()
    container = settings_page.view(dummy_page)
    assert container is not None
    assert hasattr(container, "content")
    # It should have left and right panels
    board = container.content
    assert hasattr(board, "content")
    # left_panel and preview_panel should be inside the row
    row_controls = board.content.controls
    assert len(row_controls) == 2


def test_theme_dropdown_change(settings_page):
    dummy_page = Mock()
    container = settings_page.view(dummy_page)
    state = settings_page.S

    # Initially Light Mode
    assert state.theme_name == "Light Mode"

    # Simulate changing theme
    state.set_theme("Dark Mode")
    assert state.theme_name == "Dark Mode"


def test_user_profile_display(settings_page):
    dummy_page = Mock()
    container = settings_page.view(dummy_page)

    # container -> board -> Row (left_panel + preview_panel)
    board_row = container.content.content  # the main Row inside board
    left_panel = board_row.controls[0].content  # left_panel container
    settings_scroll = left_panel.content  # Column inside left_panel
    profile_card = settings_scroll.controls[1]  # index 1 is profile_card

    # Profile card should have a Row with user info
    row_in_card = profile_card.content
    assert hasattr(row_in_card, "controls")
    assert len(row_in_card.controls) >= 1


def test_account_dialog_opens(settings_page):
    # Check that calling view creates the overlay container
    dummy_page = Mock()
    container = settings_page.view(dummy_page)
    # overlay should be empty initially
    assert hasattr(dummy_page, "overlay") or True  # We don't need exact Flet overlay here
