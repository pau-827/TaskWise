# taskwise/theme.py

# Central theme registry
THEMES = {
    "Light Mode": {
        "BG_COLOR": "#F8F6F4",
        "FORM_BG": "#E3F4F4",
        "BUTTON_COLOR": "#D2E9E9",
        "HEADER_BG": "#F8F6F4",
        "TEXT_PRIMARY": "#4A707A",
        "TEXT_SECONDARY": "#6B8F97",
        "BORDER_COLOR": "#4A707A",
        "ERROR_COLOR": "#E53935",
        "SUCCESS_COLOR": "#4CAF50",
    },
    "Pink": {
        "BG_COLOR": "#FFD1D9",
        "FORM_BG": "#FF8FB0",
        "BUTTON_COLOR": "#FF4D84",
        "HEADER_BG": "#FF77A0",
        "TEXT_PRIMARY": "#4A0B1F",
        "TEXT_SECONDARY": "#7A2C3F",
        "BORDER_COLOR": "#4A0B1F",
        "ERROR_COLOR": "#E53935",
        "SUCCESS_COLOR": "#4CAF50",
    },
# taskwise/theme.py
    "Dark Mode": {
        # App backgrounds
        "BG_COLOR": "#0B1220",       # main app background
        "FORM_BG": "#0F1A2C",        # panels / inner containers
        "TEXT_PRIMARY": "#87BAC3",   # main readable text
        "TEXT_SECONDARY": "#8ABEB9", # secondary text (still visible)
        "BORDER_COLOR": "#B7E5CD",   # visible border on dark
        "BUTTON_COLOR": "#8ABEB9",   # primary buttons, selected states
        "SUCCESS_COLOR": "#22C55E",  # completed / success
        "ERROR_COLOR": "#EF4444",    # overdue / error
        "WARNING_COLOR": "#F59E0B",
        "INFO_COLOR": "#38BDF8",
        "HEADER_BG": "#0A1426",       # top bar background
        "HEADER_BORDER": "#22314B",   # optional, safe to have
    },
}



# ------------------------------
# Safe theme access helper
# ------------------------------
def get_theme(name: str):
    """
    Returns a *copy* of the theme so the app cannot accidentally
    mutate the original theme dictionary.
    Falls back to Light Mode if missing.
    """
    base = THEMES.get(name)
    if not base:
        base = THEMES["Light Mode"]

    # Return a copy to ensure immutability from the outside
    return base.copy()


# Task categories for dropdowns, filters, etc.
CATEGORIES = ["Personal", "Work", "Study", "Bills", "Others"]
