import pytest
from unittest.mock import MagicMock, patch

from taskwise.app_state import AppState


# -----------------------------
# Test: default state
# -----------------------------
@patch("taskwise.app_state.get_theme")
def test_default_initialization(mock_get_theme):

    mock_get_theme.return_value = {"bg": "white"}

    state = AppState()

    assert state.theme_name == "Light Mode"
    assert state.user is None
    assert state.current_view == "tasks"
    assert state.current_filter == "All Tasks"
    assert state.colors == {"bg": "white"}


# -----------------------------
# Test: navigation
# -----------------------------
def test_navigation_go():

    state = AppState()

    update_mock = MagicMock()
    state.set_update_callback(update_mock)

    state.go("calendar")

    assert state.current_view == "calendar"
    update_mock.assert_called_once()


# -----------------------------
# Test: user login loads theme
# -----------------------------
@patch("taskwise.app_state.get_theme")
@patch("taskwise.app_state.db")
def test_user_login_loads_theme(mock_db, mock_get_theme):

    mock_db.get_setting.return_value = "Dark Mode"
    mock_get_theme.return_value = {"bg": "black"}

    state = AppState()

    update_mock = MagicMock()
    state.set_update_callback(update_mock)

    user = {"id": 1, "username": "ivy", "role": "user"}

    state.on_user_login(user)

    assert state.user == user
    assert state.theme_name == "Dark Mode"
    assert state.colors == {"bg": "black"}

    update_mock.assert_called_once()


# -----------------------------
# Test: login fallback theme
# -----------------------------
@patch("taskwise.app_state.get_theme")
@patch("taskwise.app_state.db")
@patch("taskwise.app_state.THEMES", {"Light Mode": {}, "Dark Mode": {}})
def test_login_invalid_theme_fallback(mock_db, mock_get_theme):

    mock_db.get_setting.return_value = "Unknown Theme"
    mock_get_theme.return_value = {"bg": "white"}

    state = AppState()

    state.on_user_login({"id": 1})

    assert state.theme_name == "Light Mode"


# -----------------------------
# Test: logout resets state
# -----------------------------
@patch("taskwise.app_state.get_theme")
def test_user_logout(mock_get_theme):

    mock_get_theme.return_value = {"bg": "white"}

    state = AppState()

    state.user = {"id": 1}
    state.theme_name = "Dark Mode"

    update_mock = MagicMock()
    state.set_update_callback(update_mock)

    state.on_user_logout()

    assert state.user is None
    assert state.theme_name == "Light Mode"

    update_mock.assert_called_once()


# -----------------------------
# Test: set_theme persists to DB
# -----------------------------
@patch("taskwise.app_state.get_theme")
@patch("taskwise.app_state.db")
@patch("taskwise.app_state.THEMES", {"Light Mode": {}, "Dark Mode": {}})
def test_set_theme_persist(mock_db, mock_get_theme):

    mock_get_theme.return_value = {"bg": "black"}

    state = AppState()

    state.user = {"id": 1}

    update_mock = MagicMock()
    state.set_update_callback(update_mock)

    state.set_theme("Dark Mode")

    assert state.theme_name == "Dark Mode"

    mock_db.set_setting.assert_called_once_with(1, "theme_name", "Dark Mode")

    update_mock.assert_called_once()


# -----------------------------
# Test: invalid theme fallback
# -----------------------------
@patch("taskwise.app_state.get_theme")
@patch("taskwise.app_state.THEMES", {"Light Mode": {}})
def test_set_theme_invalid(mock_get_theme):

    mock_get_theme.return_value = {"bg": "white"}

    state = AppState()

    state.set_theme("Invalid Theme")

    assert state.theme_name == "Light Mode"
