# taskwise/pages/calendar_page.py
import flet as ft
from datetime import date, datetime, timedelta


class CalendarPage:
    """
    Calendar (maximized + PH holidays)
    - No header here (app.py already renders header).
    - Uses shared AppState:
        S.selected_date (date)
        S.cal_year / S.cal_month
        S.db.get_all_tasks() (uses due_date)
    - Philippine holidays (English) are computed locally (no web, no extra DB needed).
    """

    def __init__(self, state):
        self.S = state

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        # ---------------------------
        # Date helpers
        # ---------------------------
        def fmt_date(d: date) -> str:
            return d.strftime("%Y-%m-%d")

        def safe_parse(s: str):
            try:
                s = (s or "").strip()
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None
            except Exception:
                return None

        def weekday_sun0(d: date) -> int:
            return (d.weekday() + 1) % 7  # Sunday=0..Saturday=6

        def days_in_month(y: int, m: int) -> int:
            if m == 12:
                return 31
            return (date(y, m + 1, 1) - date(y, m, 1)).days

        def month_abbr(m: int) -> str:
            return ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][m - 1]

        # ---------------------------
        # Normalize shared state
        # ---------------------------
        if isinstance(S.selected_date, str):
            S.selected_date = safe_parse(S.selected_date) or datetime.now().date()

        if not isinstance(S.selected_date, date):
            S.selected_date = datetime.now().date()

        if not getattr(S, "cal_year", None) or not getattr(S, "cal_month", None):
            S.cal_year = S.selected_date.year
            S.cal_month = S.selected_date.month

        TODAY = datetime.now().date()

        # ---------------------------
        # PH Holidays (English)
        # - Includes common regular holidays + special days
        # - Includes Holy Week dates computed from Easter (Maundy Thursday + Good Friday + Black Saturday)
        # - Eid holidays vary yearly; those are not computed here.
        # ---------------------------
        def easter_sunday(y: int) -> date:
            # Anonymous Gregorian algorithm (Meeus/Jones/Butcher)
            a = y % 19
            b = y // 100
            c = y % 100
            d = b // 4
            e = b % 4
            f = (b + 8) // 25
            g = (b - f + 1) // 3
            h = (19 * a + b - d - g + 15) % 30
            i = c // 4
            k = c % 4
            l = (32 + 2 * e + 2 * i - h - k) % 7
            m = (a + 11 * h + 22 * l) // 451
            month = (h + l - 7 * m + 114) // 31
            day = ((h + l - 7 * m + 114) % 31) + 1
            return date(y, month, day)

        def last_monday(y: int, m: int) -> date:
            d = date(y, m, days_in_month(y, m))
            while d.weekday() != 0:  # Monday
                d -= timedelta(days=1)
            return d

        def ph_holidays_for_year(y: int) -> dict[str, str]:
            hol = {}

            def add(mm: int, dd: int, name: str):
                hol[fmt_date(date(y, mm, dd))] = name

            # Regular holidays (commonly observed)
            add(1, 1, "New Year's Day")
            add(4, 9, "Araw ng Kagitingan (Day of Valor)")
            add(5, 1, "Labor Day")
            add(6, 12, "Independence Day")
            add(8, 21, "Ninoy Aquino Day")
            hol[fmt_date(last_monday(y, 8))] = "National Heroes Day"  # last Monday of August
            add(11, 30, "Bonifacio Day")
            add(12, 25, "Christmas Day")
            add(12, 30, "Rizal Day")

            # Common special (non-working) holidays (often observed)
            add(2, 25, "EDSA People Power Revolution Anniversary")
            add(11, 1, "All Saints' Day")
            add(11, 2, "All Souls' Day")
            add(12, 8, "Immaculate Conception of Mary")
            add(12, 31, "Last Day of the Year")

            # Holy Week (computed)
            easter = easter_sunday(y)
            maundy = easter - timedelta(days=3)
            good_friday = easter - timedelta(days=2)
            black_saturday = easter - timedelta(days=1)

            hol[fmt_date(maundy)] = "Maundy Thursday"
            hol[fmt_date(good_friday)] = "Good Friday"
            hol[fmt_date(black_saturday)] = "Black Saturday"

            return hol

        holidays = ph_holidays_for_year(S.cal_year)

        def holiday_name(d: date) -> str:
            return holidays.get(fmt_date(d), "")

        # ---------------------------
        # Task helpers
        # ---------------------------
        def build_due_set(y: int, m: int) -> set:
            result = set()
            for t in db.get_all_tasks():
                dd = safe_parse((t[4] or "").strip())
                if dd and dd.year == y and dd.month == m:
                    result.add(fmt_date(dd))
            return result

        def tasks_for_date(d: date):
            ds = fmt_date(d)
            out = []
            for t in db.get_all_tasks():
                if (t[4] or "").strip() == ds:
                    out.append(t)
            return out

        # ---------------------------
        # Refresh
        # ---------------------------
        def refresh():
            holidays.clear()
            holidays.update(ph_holidays_for_year(S.cal_year))
            S.update()

        # ---------------------------
        # Month nav
        # ---------------------------
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

        # ---------------------------
        # Calendar grid (bigger + fills space)
        # ---------------------------
        def select_day(d: date):
            S.selected_date = d
            S.cal_year = d.year
            S.cal_month = d.month
            refresh()

        def build_calendar_grid():
            y, m = S.cal_year, S.cal_month
            first = date(y, m, 1)
            dim = days_in_month(y, m)
            start_col = weekday_sun0(first)

            due_set = build_due_set(y, m)

            weekday_labels = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

            # Bigger cells
            cell = 44

            header_row = ft.Row(
                [
                    ft.Container(
                        width=cell,
                        height=22,
                        alignment=ft.alignment.center,
                        content=ft.Text(lbl, size=10, weight=ft.FontWeight.BOLD, color=C("TEXT_SECONDARY")),
                    )
                    for lbl in weekday_labels
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            cells = []
            for _ in range(start_col):
                cells.append(ft.Container(width=cell, height=cell))

            for day in range(1, dim + 1):
                d = date(y, m, day)
                ds = fmt_date(d)
                hol = holiday_name(d)

                is_selected = (S.selected_date == d)
                is_today = (d == TODAY)
                has_task = ds in due_set
                is_holiday = bool(hol)

                bg = None
                txt_color = C("TEXT_PRIMARY")

                if is_selected:
                    bg = C("BUTTON_COLOR")
                    txt_color = ft.Colors.WHITE
                elif is_holiday:
                    bg = ft.Colors.with_opacity(0.12, C("ERROR_COLOR"))
                elif has_task:
                    bg = ft.Colors.with_opacity(0.12, C("SUCCESS_COLOR"))
                elif is_today:
                    bg = ft.Colors.with_opacity(0.10, C("BUTTON_COLOR"))

                # Tiny dot indicator (holiday/task) inside cell
                dot_row = ft.Row(
                    [
                        ft.Container(
                            width=6,
                            height=6,
                            border_radius=99,
                            bgcolor=C("ERROR_COLOR") if is_holiday else None,
                        )
                        if is_holiday
                        else ft.Container(width=6, height=6),
                        ft.Container(
                            width=6,
                            height=6,
                            border_radius=99,
                            bgcolor=C("SUCCESS_COLOR") if has_task else None,
                        )
                        if has_task
                        else ft.Container(width=6, height=6),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                )

                cells.append(
                    ft.Container(
                        width=cell,
                        height=cell,
                        border_radius=10,
                        border=ft.border.all(1, C("BORDER_COLOR")),
                        bgcolor=bg,
                        ink=True,
                        on_click=lambda e, dd=d: select_day(dd),
                        content=ft.Column(
                            [
                                ft.Container(
                                    alignment=ft.alignment.center,
                                    expand=True,
                                    content=ft.Text(str(day), size=12, weight=ft.FontWeight.BOLD, color=txt_color),
                                ),
                                ft.Container(height=12, alignment=ft.alignment.center, content=dot_row),
                            ],
                            spacing=0,
                            expand=True,
                        ),
                    )
                )

            # chunk into weeks
            rows = []
            row = []
            for c in cells:
                row.append(c)
                if len(row) == 7:
                    rows.append(ft.Row(row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
                    row = []
            if row:
                while len(row) < 7:
                    row.append(ft.Container(width=cell, height=cell))
                rows.append(ft.Row(row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

            return ft.Column([header_row, ft.Container(height=8)] + rows, spacing=8)

        # ---------------------------
        # Left panel (date + holiday + tasks)
        # ---------------------------
        def build_left_panel():
            d = S.selected_date
            ds_human = d.strftime("%B %d, %Y")
            hol = holiday_name(d)

            items = tasks_for_date(d)

            header_block = ft.Container(
                border_radius=16,
                border=ft.border.all(1, C("BORDER_COLOR")),
                bgcolor=ft.Colors.with_opacity(0.20, C("BUTTON_COLOR")),
                padding=16,
                content=ft.Column(
                    [
                        ft.Text(ds_human, size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Text(hol if hol else "No holiday", size=12, color=C("TEXT_SECONDARY")),
                    ],
                    spacing=6,
                ),
            )

            if not items:
                list_area = ft.Container(
                    expand=True,
                    border_radius=16,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    bgcolor=C("BG_COLOR"),
                    padding=16,
                    alignment=ft.alignment.center,
                    content=ft.Text("No tasks on this day.", size=12, color=C("TEXT_SECONDARY")),
                )
            else:
                cards = []
                for t in items:
                    tid, title, desc, cat, due, status, created = t
                    cards.append(
                        ft.Container(
                            padding=14,
                            border_radius=14,
                            border=ft.border.all(1, C("BORDER_COLOR")),
                            bgcolor=C("FORM_BG"),
                            content=ft.Column(
                                [
                                    ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text((desc or "No description").strip(), size=11, color=C("TEXT_SECONDARY")),
                                    ft.Text(
                                        f"Category: {(cat or 'None').strip()} • Status: {status}",
                                        size=10,
                                        color=C("TEXT_SECONDARY"),
                                    ),
                                ],
                                spacing=6,
                            ),
                        )
                    )

                list_area = ft.Container(
                    expand=True,
                    border_radius=16,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    bgcolor=C("BG_COLOR"),
                    padding=14,
                    content=ft.Column(cards, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True),
                )

            return ft.Container(
                expand=True,
                border_radius=22,
                border=ft.border.all(2, C("BORDER_COLOR")),
                bgcolor=C("FORM_BG"),
                padding=22,
                content=ft.Column(
                    [
                        ft.Text("Calendar", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Container(height=12),
                        header_block,
                        ft.Container(height=14),
                        list_area,
                    ],
                    spacing=0,
                    expand=True,
                ),
            )

        # ---------------------------
        # Right panel (month selector + big calendar)
        # ---------------------------
        def build_right_panel():
            y, m = S.cal_year, S.cal_month

            top_bar = ft.Container(
                border_radius=16,
                bgcolor=C("BUTTON_COLOR"),
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                content=ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=ft.Colors.WHITE, on_click=prev_month),
                        ft.Row(
                            [
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=10,
                                    bgcolor=ft.Colors.with_opacity(0.20, ft.Colors.WHITE),
                                    content=ft.Text(str(m).zfill(2), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ),
                                ft.Text(month_abbr(m), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(str(y), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ],
                            spacing=10,
                        ),
                        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=ft.Colors.WHITE, on_click=next_month),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            grid = ft.Container(
                expand=True,
                padding=16,
                border_radius=16,
                bgcolor=C("BG_COLOR"),
                border=ft.border.all(2, C("BORDER_COLOR")),
                content=build_calendar_grid(),
            )

            legend = ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(width=10, height=10, border_radius=99, bgcolor=C("ERROR_COLOR")),
                            ft.Text("Holiday", size=11, color=C("TEXT_SECONDARY")),
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            ft.Container(width=10, height=10, border_radius=99, bgcolor=C("SUCCESS_COLOR")),
                            ft.Text("Has Tasks", size=11, color=C("TEXT_SECONDARY")),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=18,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            return ft.Container(
                expand=True,
                border_radius=22,
                border=ft.border.all(2, C("BORDER_COLOR")),
                bgcolor=C("FORM_BG"),
                padding=20,
                content=ft.Column(
                    [
                        top_bar,
                        ft.Container(height=12),
                        grid,
                        ft.Container(height=10),
                        legend,
                    ],
                    spacing=0,
                    expand=True,
                ),
            )

        # ---------------------------
        # Board (MAXIMIZED)
        # ---------------------------
        board = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(2, C("BORDER_COLOR")),
            bgcolor=C("BG_COLOR"),
            padding=26,
            content=ft.Row(
                [
                    ft.Container(content=build_left_panel(), expand=5),
                    ft.Container(width=26),
                    ft.Container(content=build_right_panel(), expand=6),
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

        # Outer wrapper: fill window and keep center padding like wireframe
        return ft.Container(
            expand=True,
            bgcolor=C("BG_COLOR"),
            padding=ft.padding.all(18),
            content=board,
        )
