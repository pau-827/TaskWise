import flet as ft
from datetime import date, datetime

class CalendarPage:
    def __init__(self, state):
        self.S = state

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        def C(k):
            return S.colors[k]

        # ------------------------------------------------------------
        # Helpers (taken from task_page)
        # ------------------------------------------------------------
        def fmt_date(d: date) -> str:
            return d.strftime("%Y-%m-%d")

        def safe_parse(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except:
                return None

        def weekday_sun0(d: date) -> int:
            # convert Monday=0..Sunday=6 → Sunday=0..Saturday=6
            return (d.weekday() + 1) % 7

        def days_in_month(y, m):
            if m == 12:
                return 31
            return (date(y, m + 1, 1) - date(y, m, 1)).days

        # Build due date set
        def build_due_set(y, m):
            result = set()
            for t in db.get_all_tasks():
                due = safe_parse((t[4] or "").strip())
                if due and due.year == y and due.month == m:
                    result.add(fmt_date(due))
            return result

        # Get tasks for a specific day
        def calendar_tasks_for_date(d: date):
            rows = []
            ds = fmt_date(d)
            for t in db.get_all_tasks():
                due = (t[4] or "").strip()
                if due == ds:
                    rows.append(t)
            return rows

        # ------------------------------------------------------------
        # Header
        # ------------------------------------------------------------
        def header():
            def nav(view):
                return lambda e: S.go(view)

            def tab(label, key):
                active = S.current_view == key
                text = f"✱ {label} ✱" if active else label
                return ft.TextButton(text, on_click=nav(key), style=ft.ButtonStyle(color=C("TEXT_PRIMARY")))

            return ft.Container(
                bgcolor=C("HEADER_BG"),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                border=ft.border.only(bottom=ft.BorderSide(1, C("BORDER_COLOR"))),
                content=ft.Row(
                    [
                        ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Row(
                            [
                                tab("Tasks", "tasks"),
                                tab("Calendar", "calendar"),
                                tab("Settings", "settings"),
                            ],
                            spacing=8
                        ),
                        ft.Container()  # empty right side
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
            )

        # ------------------------------------------------------------
        # Month Navigation
        # ------------------------------------------------------------
        YEAR = S.cal_year
        MONTH = S.cal_month
        TODAY = datetime.now().date()

        def prev_month(e):
            if S.cal_month == 1:
                S.cal_month = 12
                S.cal_year -= 1
            else:
                S.cal_month -= 1
            refresh()

        def next_month(e):
            if S.cal_month == 12:
                S.cal_month = 1
                S.cal_year += 1
            else:
                S.cal_month += 1
            refresh()

        # ------------------------------------------------------------
        # Calendar Grid
        # ------------------------------------------------------------
        def build_calendar():
            y = S.cal_year
            m = S.cal_month

            first = date(y, m, 1)
            dim = days_in_month(y, m)
            start_col = weekday_sun0(first)

            due_set = build_due_set(y, m)

            grid = []

            # header days
            weekday_labels = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
            grid.append(
                ft.Row(
                    [
                        ft.Text(d, size=12, weight=ft.FontWeight.BOLD, color=C("TEXT_SECONDARY"))
                        for d in weekday_labels
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                )
            )

            cells = []
            # blank days before the 1st
            for _ in range(start_col):
                cells.append(ft.Container(width=42, height=42))

            # actual days
            for day in range(1, dim + 1):
                current = date(y, m, day)
                ds = fmt_date(current)

                # highlight
                is_today = current == TODAY
                has_tasks = ds in due_set
                is_selected = (S.selected_date == ds)

                bg = None
                border = None

                if is_selected:
                    bg = C("BUTTON_COLOR")
                elif is_today:
                    bg = ft.Colors.with_opacity(0.1, C("BUTTON_COLOR"))
                elif has_tasks:
                    bg = ft.Colors.with_opacity(0.15, C("SUCCESS_COLOR"))

                def select_day(d=current):
                    return lambda e: open_day(d)

                cell = ft.Container(
                    width=42,
                    height=42,
                    alignment=ft.alignment.center,
                    bgcolor=bg,
                    border=ft.border.all(1, C("BORDER_COLOR")) if border else None,
                    border_radius=8,
                    on_click=select_day(),
                    content=ft.Text(
                        str(day),
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color="white" if is_selected else C("TEXT_PRIMARY"),
                    ),
                )

                cells.append(cell)

            # chunk into weeks
            rows = []
            row = []
            for c in cells:
                row.append(c)
                if len(row) == 7:
                    rows.append(ft.Row(row, alignment=ft.MainAxisAlignment.SPACE_AROUND))
                    row = []
            if row:
                rows.append(ft.Row(row, alignment=ft.MainAxisAlignment.SPACE_AROUND))

            return ft.Column(rows, spacing=6)

        # ------------------------------------------------------------
        # Day Task Viewer
        # ------------------------------------------------------------
        def open_day(d: date):
            S.selected_date = fmt_date(d)
            refresh()

        def build_day_tasks():
            if not S.selected_date:
                return ft.Container()

            d = safe_parse(S.selected_date)
            if not d:
                return ft.Container()

            items = calendar_tasks_for_date(d)

            if not items:
                return ft.Text("No tasks on this day.", size=14, color=C("TEXT_SECONDARY"))

            rows = []
            for t in items:
                tid, title, desc, cat, due, status, created = t
                rows.append(
                    ft.Container(
                        bgcolor=C("FORM_BG"),
                        padding=12,
                        border_radius=12,
                        border=ft.border.all(1, C("BORDER_COLOR")),
                        content=ft.Column(
                            [
                                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                ft.Text((desc or "").strip(), size=12, color=C("TEXT_SECONDARY")),
                                ft.Text(f"Category: {cat}", size=11, color=C("TEXT_SECONDARY")),
                            ]
                        )
                    )
                )

            return ft.Column(rows, spacing=10)

        # ------------------------------------------------------------
        # Main Layout
        # ------------------------------------------------------------
        def refresh():
            page.update()

        month_label = ft.Text(
            f"{date(YEAR, MONTH, 1).strftime('%B %Y')}",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=C("TEXT_PRIMARY")
        )

        body = ft.Row(
            [
                # Calendar column
                ft.Container(
                    expand=6,
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=prev_month),
                                    month_label,
                                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=next_month),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Container(height=12),
                            build_calendar(),
                        ]
                    )
                ),
                ft.Container(width=20),

                # Selected day tasks
                ft.Container(
                    expand=4,
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Text("Tasks on Selected Day", size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ft.Container(height=10),
                            build_day_tasks(),
                        ]
                    )
                ),
            ],
            expand=True,
        )

        wrapper = ft.Container(
            bgcolor=C("BG_COLOR"),
            content=ft.Column(
                [
                    header(),
                    ft.Container(padding=20, expand=True, content=body),
                ],
                expand=True,
            )
        )

        return wrapper