import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from passlib.hash import bcrypt

import database.db as db


# -----------------------------
# Use a temporary test database
# -----------------------------
TEST_DB = "test_taskwise.db"


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Override DB name
    db.DB_NAME = TEST_DB

    # Create fresh database
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    db.init_db()

    yield

    # Cleanup after tests
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# -----------------------------
# User Tests
# -----------------------------
def test_create_user():
    password = bcrypt.hash("test123")

    result = db.create_user(
        "Test User",
        "test@email.com",
        password
    )

    assert result == True


def test_get_user_by_email():
    user = db.get_user_by_email("test@email.com")

    assert user is not None
    assert user["email"] == "test@email.com"


def test_get_user_by_id():
    user = db.get_user_by_email("test@email.com")
    user2 = db.get_user_by_id(user["id"])

    assert user2["id"] == user["id"]


# -----------------------------
# Ban / Unban Tests
# -----------------------------
def test_ban_user():
    user = db.get_user_by_email("test@email.com")

    db.ban_user(user["id"])

    banned = db.is_user_banned("test@email.com")

    assert banned == True


def test_unban_user():
    user = db.get_user_by_email("test@email.com")

    db.unban_user(user["id"])

    banned = db.is_user_banned("test@email.com")

    assert banned == False


# -----------------------------
# Task Tests
# -----------------------------
def test_add_task():
    user = db.get_user_by_email("test@email.com")

    db.add_task(user["id"], "Test Task", "Testing", "School", "2026-03-20")

    tasks = db.get_tasks_by_user(user["id"])

    assert len(tasks) > 0
    assert tasks[0][1] == "Test Task"


def test_delete_task():
    user = db.get_user_by_email("test@email.com")

    tasks = db.get_tasks_by_user(user["id"])
    task_id = tasks[0][0]

    db.delete_task(user["id"], task_id)

    tasks_after = db.get_tasks_by_user(user["id"])

    assert all(t[0] != task_id for t in tasks_after)


# -----------------------------
# Settings Tests
# -----------------------------
def test_set_and_get_setting():
    user = db.get_user_by_email("test@email.com")

    db.set_setting(user["id"], "theme", "dark")

    value = db.get_setting(user["id"], "theme")

    assert value == "dark"


# -----------------------------
# Log Tests
# -----------------------------
def test_add_log():
    user = db.get_user_by_email("test@email.com")

    db.add_log("TEST_ACTION", "Testing logs", user["id"])

    logs = db.get_logs()

    assert any(log["action"] == "TEST_ACTION" for log in logs)
    
# -----------------------------
# Title Input Tests
# -----------------------------
def test_auto_untitled_task():
    user = db.get_user_by_email("test@email.com")

    db.add_task(user["id"], "", "", "", "")
    db.add_task(user["id"], "", "", "", "")

    tasks = db.get_tasks_by_user(user["id"])

    titles = [t[1] for t in tasks]

    assert "Untitled" in titles