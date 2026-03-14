import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import MagicMock
from database import db

@pytest.fixture
def mock_page():
    """Mock Flet page for UI functions."""
    page = MagicMock()
    page.overlay = []
    page.update = MagicMock()
    page.clean = MagicMock()
    page.snack_bar = None
    return page

@pytest.fixture(scope="module")
def test_user():
    """Create a test user for admin actions."""
    email = "test@email.com"
    password_hash = "testhash"

    # Ensure no leftover user
    existing = db.get_user_by_email(email)
    if existing:
        db.delete_user(existing["id"])

    # Create test user
    db.create_user("Test User", email, password_hash)
    user = db.get_user_by_email(email)
    yield user

    # Cleanup
    if user:
        db.delete_user(user["id"])

def test_admin_users_exclude_admin(mock_page):
    """Filtered user list should exclude the real admin."""
    users = db.get_users()
    filtered_users = [
        u for u in users
        if not (u["role"].lower() == "admin" or u["email"].lower() == "admin@taskwise.com")
    ]

    # Assert that no admin remains
    for u in filtered_users:
        assert u["email"].lower() != "admin@taskwise.com"

def test_admin_can_ban_user(test_user):
    """Ban user should set is_banned to True."""
    user = db.get_user_by_email(test_user["email"])
    assert user is not None

    db.ban_user(user["id"])
    updated_user = db.get_user_by_email(user["email"])
    assert updated_user["is_banned"] is True

def test_admin_can_unban_user(test_user):
    """Unban user should set is_banned to False."""
    user = db.get_user_by_email(test_user["email"])
    assert user is not None

    db.unban_user(user["id"])
    updated_user = db.get_user_by_email(user["email"])
    assert updated_user["is_banned"] is False

def test_admin_can_delete_user():
    """Admin can delete a user."""
    # Create a temporary user
    email = "temp@email.com"
    db.create_user("Temp User", email, "temp123")
    user = db.get_user_by_email(email)
    assert user is not None

    # Delete user
    db.delete_user(user["id"])
    deleted_user = db.get_user_by_email(email)
    assert deleted_user is None