# taskwise/app_state.py
from datetime import datetime
from taskwise.database import Database
from taskwise.theme import THEMES


class AppState:
    """
    Shared application state. Pages receive an AppState instance
    and use it for DB access, theme colors, user, calendar state, etc.
    """

    def __init__(self):
        self.db = Database()

        # theme
        saved_theme = self.db.get_setting("theme_name", "Light Mode")
        if saved_theme not in THEMES:
            saved_theme = "Light Mode"
        self.theme_name = saved_theme
        self.colors = THEMES[self.theme_name].copy()

        # auth
        self.user = None  # dict: {"id","name","email"}

        # UI navigation
        self.current_view = "tasks"
        self.current_filter = "All Tasks"

        # calendar
        today = datetime.now().date()
        self.selected_date = today
        self.cal_year = today.year
        self.cal_month = today.month
        self.holidays_cache = {}

        # callback used by app.py to re-render
        self._update_callback = None

    def set_update_callback(self, fn):
        self._update_callback = fn

    def update(self):
        """Force UI refresh (used by pages and app shell)."""
        if self._update_callback:
            self._update_callback()

    def go(self, view_name: str):
        self.current_view = view_name
        self.update()

    def set_theme(self, theme_name: str):
        if theme_name not in THEMES:
            theme_name = "Light Mode"
        self.theme_name = theme_name
        self.colors = THEMES[theme_name].copy()
        self.db.set_setting("theme_name", theme_name)
        self.update()