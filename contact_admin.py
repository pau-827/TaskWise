import flet as ft

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
}

admins = [
    {"name": "Ivy Pauline B. Muit", "email": "ivmuit@my.cspc.edu.ph", "photo": "paupau.jpg"},
    {"name": "Ayelyn Janne F. Panliboton", "email": "aypanliboton@my.cspc.edu.ph", "photo": "ayelyn.jpg"},
    {"name": "Rhea Lizza B. Sanglay", "email": "rhsanglay@my.cspc.edu.ph", "photo": "reeya.jpg"},
]


def contact_admin_page(page: ft.Page, go_back_callback):
    page.title = "Contact Admin"
    theme = THEMES["Light Mode"]
    page.bgcolor = theme["BG_COLOR"]

    # HEADER
    header = ft.Column(
        [
            ft.Text("Contact Admins", size=28, weight="bold", color=theme["TEXT_PRIMARY"]),

            ft.TextButton(
                "← Back",
                on_click=lambda e: go_back_callback(),    # 💥 now REALLY calls main.py's function
                style=ft.ButtonStyle(
                    color=theme["TEXT_PRIMARY"],
                    padding=10
                ),
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    # ADMIN CARDS
    cards = []
    for admin in admins:
        cards.append(
            ft.Container(
                width=180,
                height=230,
                bgcolor=theme["FORM_BG"],
                border=ft.border.all(1, theme["BORDER_COLOR"]),
                border_radius=10,
                padding=10,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Image(admin["photo"], width=120, height=120, fit="cover"),
                        ft.Text(admin["name"], weight="bold", size=12, color=theme["TEXT_PRIMARY"]),
                        ft.Text(admin["email"], size=11, color=theme["TEXT_SECONDARY"]),
                    ],
                    spacing=6,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        )

    cards_centered = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Row(
            controls=cards,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

    # FOOTER
    footer = ft.Container(
        content=ft.Text("All rights reserved ©2025", color=theme["TEXT_SECONDARY"]),
        alignment=ft.alignment.center,
        padding=20
    )

    return ft.Column(
        expand=True,
        controls=[header, cards_centered, footer]
    )