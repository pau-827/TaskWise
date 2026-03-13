import flet as ft

THEMES = {
    "Pink Mode": {
        "BG_TOP": "#FFF1F6",
        "BG_MID": "#FFE6F0",
        "BG_BOT": "#FFF7FB",
        "CARD_BG": "#FFFFFF",
        "CARD_BORDER": "#FFD1E3",
        "SOFT": "#FFE4EF",
        "SOFT_2": "#FFF7FA",
        "ACCENT": "#FF4D8D",
        "ACCENT_DARK": "#8A2E54",
        "TEXT_DARK": "#3A2A33",
        "TEXT_MUTED": "#6C5A65",
        "SHADOW": "#00000012",
    },
}

admins = [
    {"name": "Ivy Pauline B. Muit", "email": "ivmuit@my.cspc.edu.ph", "photo": "paupau.jpg"},
    {"name": "Ayelyn Janne F. Panliboton", "email": "aypanliboton@my.cspc.edu.ph", "photo": "ayelyn.jpg"},
    {"name": "Rhea Lizza B. Sanglay", "email": "rhsanglay@my.cspc.edu.ph", "photo": "reeya.jpg"},
]


def contact_admin_page(page: ft.Page, go_back_callback):
    page.title = "Contact Admins"
    theme = THEMES["Pink Mode"]
    page.bgcolor = theme["BG_TOP"]

    # ---------- helpers ----------
    def snack(msg: str):
        sb = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=theme["ACCENT_DARK"],
            duration=2500,
        )
        try:
            page.overlay.append(sb)
            sb.open = True
        except Exception:
            page.snack_bar = sb
            page.snack_bar.open = True
        page.update()

    def copy_email(email: str):
        try:
            page.set_clipboard(email)
            snack("Email copied to clipboard.")
        except Exception:
            snack("Copy failed. Please try again.")

    def send_email(email: str):
        # Works on desktop/mobile when mail client exists
        try:
            page.launch_url(f"mailto:{email}")
        except Exception:
            snack("Unable to open email app on this device.")

    def pill_button(text: str, icon, filled: bool, on_click):
        bg = theme["ACCENT"] if filled else "white"
        fg = "white" if filled else theme["ACCENT_DARK"]
        border = None if filled else ft.border.all(1, theme["CARD_BORDER"])

        btn = ft.Container(
            ink=True,
            on_click=on_click,
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            border_radius=999,
            bgcolor=bg,
            border=border,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(blur_radius=18, color=theme["SHADOW"], offset=ft.Offset(0, 10)),
            content=ft.Row(
                tight=True,
                spacing=10,
                controls=[
                    ft.Icon(icon, size=18, color=fg),
                    ft.Text(text, size=13, weight=ft.FontWeight.W_700, color=fg),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=fg),
                ],
            ),
        )

        def on_hover(e: ft.HoverEvent):
            if e.data == "true":
                btn.scale = 1.02
                btn.shadow = ft.BoxShadow(blur_radius=26, color="#0000001A", offset=ft.Offset(0, 14))
                if filled:
                    btn.bgcolor = "#FF2F78"
            else:
                btn.scale = 1.0
                btn.shadow = ft.BoxShadow(blur_radius=18, color=theme["SHADOW"], offset=ft.Offset(0, 10))
                btn.bgcolor = theme["ACCENT"] if filled else "white"
            page.update()

        btn.on_hover = on_hover
        return btn

    # ---------- header ----------
    header = ft.Container(
        padding=ft.padding.only(left=22, right=22, top=18, bottom=12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=theme["ACCENT_DARK"]),
                ft.Container(
                    ink=True,
                    border_radius=999,
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    bgcolor="white",
                    border=ft.border.all(1, theme["CARD_BORDER"]),
                    on_click=lambda e: go_back_callback(),
                    content=ft.Row(
                        tight=True,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.ARROW_BACK, size=18, color=theme["ACCENT_DARK"]),
                            ft.Text("Back", size=13, weight=ft.FontWeight.W_700, color=theme["ACCENT_DARK"]),
                        ],
                    ),
                ),
            ],
        ),
    )

    # ---------- title + actions ----------
    title_block = ft.Container(
        padding=ft.padding.only(left=22, right=22, top=8, bottom=6),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Text("Contact Admins", size=40, weight=ft.FontWeight.BOLD, color=theme["ACCENT_DARK"]),
                ft.Text(
                    "Use the options below to reach the right person faster.",
                    size=14,
                    color=theme["TEXT_MUTED"],
                ),
            ],
        ),
    )

    # optional global actions (copies/sends the FIRST admin email as a convenience)
    top_actions = ft.Container(
        padding=ft.padding.only(left=22, right=22, top=8, bottom=10),
        alignment=ft.alignment.center,
        content=ft.Row(
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            controls=[
                pill_button(
                    "Copy Email",
                    ft.Icons.CONTENT_COPY,
                    True,
                    lambda e: copy_email(admins[0]["email"]) if admins else snack("No admins found."),
                ),
                pill_button(
                    "Send Email",
                    ft.Icons.MAIL_OUTLINE,
                    False,
                    lambda e: send_email(admins[0]["email"]) if admins else snack("No admins found."),
                ),
            ],
        ),
    )

    # ---------- admin cards ----------
    def admin_card(admin: dict):
        # photo container
        avatar = ft.Container(
            width=110,
            height=110,
            border_radius=22,
            bgcolor=theme["SOFT"],
            border=ft.border.all(1, theme["CARD_BORDER"]),
            alignment=ft.alignment.center,
            content=ft.Image(src=admin["photo"], width=110, height=110, fit=ft.ImageFit.COVER),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

        card = ft.Container(
            padding=18,
            border_radius=22,
            bgcolor=theme["CARD_BG"],
            border=ft.border.all(1, theme["CARD_BORDER"]),
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(blur_radius=18, color=theme["SHADOW"], offset=ft.Offset(0, 12)),
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    avatar,
                    ft.Text(admin["name"], size=14, weight=ft.FontWeight.BOLD, color=theme["TEXT_DARK"], text_align=ft.TextAlign.CENTER),
                    ft.Text(admin["email"], size=12, color=theme["TEXT_MUTED"], text_align=ft.TextAlign.CENTER),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            pill_button("Copy Email", ft.Icons.CONTENT_COPY, True, lambda e: copy_email(admin["email"])),
                            pill_button("Email", ft.Icons.MAIL_OUTLINE, False, lambda e: send_email(admin["email"])),
                        ],
                    ),
                ],
            ),
        )

        def on_hover(e: ft.HoverEvent):
            if e.data == "true":
                card.scale = 1.02
                card.bgcolor = theme["SOFT_2"]
                card.shadow = ft.BoxShadow(blur_radius=28, color="#0000001A", offset=ft.Offset(0, 16))
            else:
                card.scale = 1.0
                card.bgcolor = theme["CARD_BG"]
                card.shadow = ft.BoxShadow(blur_radius=18, color=theme["SHADOW"], offset=ft.Offset(0, 12))
            page.update()

        card.on_hover = on_hover
        return card

    cards_grid = ft.Container(
        padding=ft.padding.only(left=22, right=22, top=16),
        alignment=ft.alignment.center,
        content=ft.ResponsiveRow(
            columns=12,
            spacing=18,
            run_spacing=18,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4}, content=admin_card(a))
                for a in admins
            ],
        ),
    )

    # ---------- footer ----------
    footer = ft.Container(
        padding=ft.padding.only(top=18, bottom=50),
        alignment=ft.alignment.center,
        content=ft.Text("All rights reserved ©2025", size=12, color=theme["TEXT_MUTED"]),
    )

    # ---------- background + layout ----------
    # lively pink background with floating circles
    background = ft.Stack(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[theme["BG_TOP"], theme["BG_MID"], theme["BG_BOT"]],
                ),
            ),
            ft.Container(left=-220, top=-180, width=520, height=520, border_radius=999, bgcolor="#FF4D8D22"),
            ft.Container(right=-260, top=40, width=600, height=600, border_radius=999, bgcolor="#FF4D8D18"),
            ft.Container(left=120, bottom=-280, width=520, height=520, border_radius=999, bgcolor="#FF4D8D14"),
        ],
    )

    content = ft.ListView(
        expand=True,
        spacing=0,
        padding=0,
        controls=[
            header,
            title_block,
            top_actions,
            cards_grid,
            footer,
        ],
    )

    return ft.Container(
        expand=True,
        content=ft.Stack(
            expand=True,
            controls=[
                background,
                content,
            ],
        ),
    )