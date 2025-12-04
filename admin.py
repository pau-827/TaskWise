import flet as ft
import db

def get_admin_page(page, PRIMARY_TEXT, SECONDARY_TEXT, BUTTON_COLOR, BG_COLOR, FORM_BG):
    logs = db.get_logs()

    log_items = []
    for log in logs:
        log_items.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"User ID: {log['user_id']}", color=PRIMARY_TEXT, size=12),
                        ft.Text(f"Email: {log['email']}", color=PRIMARY_TEXT, size=12),
                        ft.Text(f"Action: {log['action']}", color=PRIMARY_TEXT, size=12),
                        ft.Text(f"Details: {log['details']}", color=SECONDARY_TEXT, size=11),
                        ft.Text(f"Time: {log['created_at']}", color=SECONDARY_TEXT, size=11),
                    ],
                    spacing=2
                ),
                bgcolor=FORM_BG,
                padding=10,
                border_radius=10,
            )
        )

    # IMPORTANT FIX:
    # Column cannot both scroll AND expand;
    # also Containers cannot be both scrollable AND expandable inside a non-expand parent.
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Admin Panel", size=26, weight=ft.FontWeight.BOLD, color=PRIMARY_TEXT),
                ft.Container(
                    content=ft.ListView(
                        controls=log_items,
                        spacing=10,
                        expand=True
                    ),
                    expand=True
                )
            ],
            spacing=20,
            expand=True,
        ),
        padding=20,
        bgcolor=BG_COLOR,
        expand=True,
    )