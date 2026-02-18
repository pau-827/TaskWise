# taskwise/app_state.py
from database import db
from datetime import datetime
from taskwise.theme import get_theme, THEMES


class AppState:

    def __init__(self):
        # db is the module; functions are called like:
        # db.get_setting(user_id, key, default)
        self.db = db

        # Default theme before login
        self.theme_name = "Light Mode"
        self.colors = get_theme(self.theme_name)

        # Auth
        self.user = None  # dict: {"id","username","role"}

        # UI navigation
        self.current_view = "tasks"
        self.current_filter = "All Tasks"

        # Calendar
        today = datetime.now().date()
        self.selected_date = today
        self.cal_year = today.year
        self.cal_month = today.month
        self.holidays_cache = {}

        # update() callback (set by TaskWiseApp)
        self._update_callback = None

    # -----------------------
    # update/render helpers
    # -----------------------
    def set_update_callback(self, fn):
        self._update_callback = fn

    def update(self):
        if self._update_callback:
            self._update_callback()

    def go(self, view_name: str):
        self.current_view = view_name
        self.update()

    # -----------------------
    # login/logout helpers
    # -----------------------
    def on_user_login(self, user: dict):
        self.user = user

        # Load per-user theme
        try:
            saved_theme = self.db.get_setting(self.user["id"], "theme_name", "Light Mode")
        except Exception:
            saved_theme = "Light Mode"

        # Fallback if theme no longer exists
        if saved_theme not in THEMES:
            saved_theme = "Light Mode"

        self.theme_name = saved_theme
        self.colors = get_theme(saved_theme)

        self.update()

    def on_user_logout(self):
        self.user = None

        self.theme_name = "Light Mode"
        self.colors = get_theme("Light Mode")

        self.update()

    # -----------------------
    # theme/settings helpers
    # -----------------------
    def set_theme(self, theme_name: str):

        if theme_name not in THEMES:
            theme_name = "Light Mode"

        self.theme_name = theme_name
        self.colors = get_theme(theme_name)

        # Persist to DB only if logged in
        if self.user:
            try:
                self.db.set_setting(self.user["id"], "theme_name", theme_name)
            except Exception:
                pass  # Silent fail — we don't want the UI to crash

        self.update()
