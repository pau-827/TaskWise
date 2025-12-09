import sys
from pathlib import Path

import flet as ft
from passlib.hash import bcrypt

# ------------------------------------------------------------
# Import SettingsPage + THEMES in a way that works:
# 1) python -m taskwise.pages.test_settings_page  (best)
# 2) python taskwise/pages/test_settings_page.py  (still works)
# ------------------------------------------------------------
try:
    # Works when run as a module
    from .settings_page import SettingsPage
    from taskwise.theme import THEMES
except ImportError:
    # Works when run as a script
    project_root = Path(__file__).resolve().parents[2]  # .../TaskWise
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from taskwise.pages.settings_page import SettingsPage
    from taskwise.theme import THEMES


# -----------------------------
# Fake DB for testing SettingsPage (matches current settings_page.py expectations)
# -----------------------------
class FakeDB:
    def __init__(self):
        self.users_by_id = {}

        # Seed a default user
        self.create_user(
            username="Guest",
            email="guest@example.com",
            password_plain="password123",
            name="Guest",
            role="user",
        )

    def get_user_by_id(self, user_id):
        return self.users_by_id.get(user_id)

    def get_user(self, user_id):
        return self.get_user_by_id(user_id)

    def get_user_by_username(self, username):
        for u in self.users_by_id.values():
            if u.get("username") == username:
                return u
        return None

    def get_user_by_email(self, email):
        for u in self.users_by_id.values():
            if u.get("email") == email:
                return u
        return None

    def update_user_password(self, user_id, new_hash):
        u = self.users_by_id.get(user_id)
        if not u:
            raise ValueError("User not found")
        u["password_hash"] = new_hash

    def delete_user(self, user_id):
        if user_id in self.users_by_id:
            del self.users_by_id[user_id]
        else:
            raise ValueError("User not found")

    def create_user(self, username, email, password_plain, name=None, role="user"):
        new_id = (max(self.users_by_id.keys()) + 1) if self.users_by_id else 1
        self.users_by_id[new_id] = {
            "id": new_id,
            "username": username,
            "name": name or username,
            "email": email,
            "role": role,
            "password_hash": bcrypt.hash(password_plain),
        }
        return new_id


# -----------------------------
# Fake AppState for testing
# -----------------------------
class FakeState:
    def __init__(self):
        self.db = FakeDB()
        self.theme_name = "Light Mode"

        base = {}
        try:
            base = (THEMES.get(self.theme_name) or {}).copy()
        except Exception:
            base = {}

        # Ensure expected keys exist
        self.colors = {
            "TEXT_PRIMARY": base.get("TEXT_PRIMARY", "#111111"),
            "TEXT_SECONDARY": base.get("TEXT_SECONDARY", "#666666"),
            "BUTTON_COLOR": base.get("BUTTON_COLOR", "#5b6cff"),
            "ERROR_COLOR": base.get("ERROR_COLOR", "#ff3b30"),
            "SUCCESS_COLOR": base.get("SUCCESS_COLOR", "#34c759"),
            "BORDER_COLOR": base.get("BORDER_COLOR", "#e0e0e0"),
            "BG_COLOR": base.get("BG_COLOR", "#fafafa"),
            "FORM_BG": base.get("FORM_BG", "#f5f5f5"),
        }

        self.user = None

    def set_theme(self, theme_name: str):
        self.theme_name = theme_name
        t = {}
        try:
            t = (THEMES.get(theme_name) or {}).copy()
        except Exception:
            t = {}

        self.colors.update(
            {
                "TEXT_PRIMARY": t.get("TEXT_PRIMARY", self.colors["TEXT_PRIMARY"]),
                "TEXT_SECONDARY": t.get("TEXT_SECONDARY", self.colors["TEXT_SECONDARY"]),
                "BUTTON_COLOR": t.get("BUTTON_COLOR", self.colors["BUTTON_COLOR"]),
                "ERROR_COLOR": t.get("ERROR_COLOR", self.colors["ERROR_COLOR"]),
                "SUCCESS_COLOR": t.get("SUCCESS_COLOR", self.colors["SUCCESS_COLOR"]),
                "BORDER_COLOR": t.get("BORDER_COLOR", self.colors["BORDER_COLOR"]),
                "BG_COLOR": t.get("BG_COLOR", self.colors["BG_COLOR"]),
                "FORM_BG": t.get("FORM_BG", self.colors["FORM_BG"]),
            }
        )
        print(f"Theme changed to: {theme_name}")

    def update(self):
        print("State update called")

    def go(self, view_name: str):
        print("Switch to:", view_name)

    def on_user_logout(self):
        self.user = None
        print("User logged out")


# -----------------------------
# Manual test runner (Flet app)
# -----------------------------
def main(page: ft.Page):
    page.title = "Settings Page Test"
    page.window_width = 1000
    page.window_height = 700

    state = FakeState()

    # Auto-login as the seeded user so you can test dialogs quickly
    seeded = state.db.get_user_by_email("guest@example.com")
    state.user = {
        "id": seeded["id"],
        "username": seeded["username"],
        "name": seeded.get("name") or seeded["username"],
        "email": seeded["email"],
        "role": seeded.get("role", "user"),
    }

    settings_page = SettingsPage(state)
    page.add(settings_page.view(page))


if __name__ == "__main__":
    # Preferred run:
    #   python -m taskwise.pages.test_settings_page
    # Still supported:
    #   python taskwise/pages/test_settings_page.py
    ft.app(target=main)
