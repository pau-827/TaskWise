# taskwise/theme.py

THEMES = {
    "Light Mode": {
        "BG_COLOR": "#97C7C3",
        "FORM_BG": "#E3F4F4",
        "BUTTON_COLOR": "#97C7C3",
        "HEADER_BG": "#F8F6F4",
        "TEXT_PRIMARY": "#4A707A",
        "TEXT_SECONDARY": "#6B8F97",
        "BORDER_COLOR": "#4A707A",
        "ERROR_COLOR": "#E53935",
        "SUCCESS_COLOR": "#4CAF50",

        # ✅ Chart colors that match teal/seafoam UI + enough for 5 categories
        "CHART_COLORS": ["#035477", "#2A9D8F", "#4A707A", "#F4A261", "#A855F7"],
        "CHART_BG": "#E3F4F4",
        "CHART_TEXT": "#4A707A",
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

        # ✅ Warm/pink-friendly chart colors
        "CHART_COLORS": ["#BE123C", "#FF4D84", "#EE6983", "#FFC4C4", "#CD2C58"],
        "CHART_BG": "#FF8FB0",
        "CHART_TEXT": "#4A0B1F",
    },

    "Dark Mode": {
        "BG_COLOR": "#23262B",
        "FORM_BG": "#3D4148",
        "TEXT_PRIMARY": "#959595",
        "TEXT_SECONDARY": "#707070",
        "BORDER_COLOR": "#707070",
        "BUTTON_COLOR": "#707070",
        "SUCCESS_COLOR": "#22C55E",
        "ERROR_COLOR": "#EF4444",
        "WARNING_COLOR": "#F59E0B",
        "INFO_COLOR": "#38BDF8",
        "HEADER_BG": "#0A1426",
        "HEADER_BORDER": "#22314B",
        "CHART_COLORS": ["#1B3C53", "#234C6A", "#456882", "#D2C1B6", "#715A5A"],
        "CHART_BG": "#3D4148",     
        "CHART_TEXT": "#E5E7EB",    
    },
}

def get_theme(name: str):
    base = THEMES.get(name) or THEMES["Light Mode"]
    return base.copy()

CATEGORIES = ["Personal", "Work", "Study", "Bills", "Others"]
