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
    "Dark Mode": {
        "BG_COLOR": "#0F1115",
        "FORM_BG": "#1A1D24",
        "BUTTON_COLOR": "#2B303C",
        "HEADER_BG": "#10131A",
        "TEXT_PRIMARY": "#E7EEF7",
        "TEXT_SECONDARY": "#A9B6C6",
        "BORDER_COLOR": "#3A4150",
        "ERROR_COLOR": "#FF5C5C",
        "SUCCESS_COLOR": "#35C97E",
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
