# taskwise/app_state.py
from database import db
from datetime import datetime
from taskwise.theme import get_theme, THEMES


class AppState:

    def __init__(self):
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

        # Callbacks (set by TaskWiseApp)
        self._update_callback = None
        self._on_delete_account_callback = None
        self._badge_refresh_callback = None   # <-- NEW

    # -----------------------
    # update/render helpers
    # -----------------------
    def set_update_callback(self, fn):
        self._update_callback = fn

    def set_delete_account_callback(self, fn):
        self._on_delete_account_callback = fn

    def set_badge_refresh_callback(self, fn):      # <-- NEW
        self._badge_refresh_callback = fn

    def update(self):
        if self._update_callback:
            self._update_callback()

    def refresh_badge(self):                        # <-- NEW
        """Tell the header to recount and repaint the notification badge."""
        if self._badge_refresh_callback:
            self._badge_refresh_callback()

    def go(self, view_name: str):
        self.current_view = view_name
        self.update()

    # -----------------------
    # login/logout helpers
    # -----------------------
    def on_user_login(self, user: dict):
        self.user = user

        try:
            saved_theme = self.db.get_setting(self.user["id"], "theme_name", "Light Mode")
        except Exception:
            saved_theme = "Light Mode"

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

    def on_account_deleted(self):
        """Clears user state then fires the delete/logout callback to return to homepage."""
        self.user = None
        self.theme_name = "Light Mode"
        self.colors = get_theme("Light Mode")

        if self._on_delete_account_callback:
            self._on_delete_account_callback()

    # -----------------------
    # theme/settings helpers
    # -----------------------
    def set_theme(self, theme_name: str):
        if theme_name not in THEMES:
            theme_name = "Light Mode"

        self.theme_name = theme_name
        self.colors = get_theme(theme_name)

        if self.user:
            try:
                self.db.set_setting(self.user["id"], "theme_name", theme_name)
            except Exception:
                pass

        self.update()