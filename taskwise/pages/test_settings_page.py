import flet as ft
from .settings_page import SettingsPage
from ..theme import THEMES

# ---- Fake DB for testing SettingsPage ----
class FakeDB:
    def __init__(self):
        # A simple in-memory 'database'
        self.users = {
            "guest@example.com": (1, "Guest", "guest@example.com", "hash123")
        }
        self.settings = {}

    def get_user_by_email(self, email):
        return self.users.get(email)

    def create_user(self, name, email, pw_hash):
        self.users[email] = (len(self.users)+1, name, email, pw_hash)

    def change_password(self, user_id, new_hash):
        for email, user in self.users.items():
            if user[0] == user_id:
                self.users[email] = (user_id, user[1], email, new_hash)

    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        print("Saved setting:", key, value)


# ---- Fake AppState for testing ----
class FakeState:
    def __init__(self):
        self.db = FakeDB()

        # default theme
        self.theme_name = "Light Mode"
        self.colors = THEMES[self.theme_name].copy()

        self.user = None
        self.current_view = "settings"

        self._update_callback = None

    def set_theme(self, theme_name):
        """Set the theme"""
        self.theme_name = theme_name
        if theme_name in THEMES:
            self.colors = THEMES[theme_name].copy()
            print(f"Theme changed to: {theme_name}")

    def update(self):
        """Trigger UI update"""
        print("State update called")

    def go(self, view_name):
        print("Switch to:", view_name)

    def _hash_pw(self, s):
        import hashlib
        return hashlib.sha256((s or "").encode()).hexdigest()


# ---- MAIN TESTER ----
def main(page: ft.Page):
    page.title = "Settings Page Test"
    page.window_width = 900
    page.window_height = 600

    state = FakeState()
    settings_page = SettingsPage(state)

    content = settings_page.view(page)
    page.add(content)


ft.app(target=main)
