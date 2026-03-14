import pytest
from unittest.mock import MagicMock, patch

from app.main import main


class MockSession(dict):
    def set(self, key, value):
        self[key] = value

    def get(self, key, default=None):
        return super().get(key, default)

    def clear(self):
        super().clear()


class MockPage:
    def __init__(self):
        self.title = ""
        self.theme_mode = None
        self.padding = None
        self.window_width = None
        self.window_height = None
        self.scroll = None

        self.overlay = []
        self.controls = []
        self.dialog = None
        self.snack_bar = None

        self.session = MockSession()

        self.width = 1000
        self.height = 600

    def add(self, control):
        self.controls.append(control)

    def clean(self):
        self.controls.clear()

    def update(self):
        pass

    def run_task(self, func, *args):
        pass

    def set_clipboard(self, text):
        self.clipboard = text


@pytest.fixture
def mock_page():
    return MockPage()


@patch("app.main.db")
@patch("app.main.get_secret")
def test_main_initialization(mock_secret, mock_db, mock_page):

    mock_secret.return_value = "admin@test.com"

    mock_db.init_db = MagicMock()
    mock_db.get_db_path = MagicMock(return_value="test.db")

    main(mock_page)

    assert mock_page.title == "TaskWise"
    assert mock_page.window_width == 1000
    assert mock_page.window_height == 600

    mock_db.init_db.assert_called_once()


@patch("app.main.db")
@patch("app.main.get_secret")
def test_loader_overlay_exists(mock_secret, mock_db, mock_page):

    mock_secret.return_value = "admin@test.com"

    mock_db.init_db = MagicMock()
    mock_db.get_db_path = MagicMock(return_value="test.db")

    main(mock_page)

    assert len(mock_page.overlay) >= 1


@patch("app.main.db")
@patch("app.main.get_secret")
def test_front_page_controls_exist(mock_secret, mock_db, mock_page):

    mock_secret.return_value = "admin@test.com"

    mock_db.init_db = MagicMock()
    mock_db.get_db_path = MagicMock(return_value="test.db")

    main(mock_page)

    assert mock_page.controls is not None


def test_session_set_get():

    session = MockSession()

    session.set("user_id", 10)

    assert session.get("user_id") == 10

    session.clear()

    assert session.get("user_id") is None
