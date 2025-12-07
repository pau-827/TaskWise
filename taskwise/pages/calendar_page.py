# taskwise/pages/calendar_page.py
import flet as ft
from datetime import date, datetime, timedelta
from typing import Optional, Tuple


class CalendarPage:

    def __init__(self, state):
        self.S = state

    def view(self, page: ft.Page):
        S = self.S
        db = S.db

        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        TODAY = datetime.now().date()

        # ---------------------------
        # Helpers: date/time parsing
        # ---------------------------
        def fmt_date(d: date) -> str:
            return d.strftime("%Y-%m-%d")

        def pretty_long(d: date) -> str:
            return d.strftime("%B %d, %Y")

        def safe_parse_date(s: str) -> Optional[date]:
            try:
                s = (s or "").strip()
                if not s:
                    return None
                return datetime.strptime(s.split()[0], "%Y-%m-%d").date()
            except Exception:
                return None

        def safe_parse_time(s: str) -> Optional[Tuple[int, int]]:
            try:
                s = (s or "").strip()
                if not s:
                    return None
                parts = s.split()
                if len(parts) < 2:
                    return None
                hh, mm = parts[1].split(":")
                return int(hh), int(mm)
            except Exception:
                return None

        def due_date_only(due_str: str) -> str:
            d = safe_parse_date(due_str)
            return fmt_date(d) if d else ""

        def days_in_month(y: int, m: int) -> int:
            if m == 12:
                return 31
            return (date(y, m + 1, 1) - date(y, m, 1)).days

        def weekday_sun0(d: date) -> int:
            return (d.weekday() + 1) % 7  # Sunday=0..Saturday=6

        def month_abbr(m: int) -> str:
            return ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][m - 1]

        # ---------------------------
        # Normalize shared state
        # ---------------------------
        if isinstance(getattr(S, "selected_date", None), str):
            S.selected_date = safe_parse_date(S.selected_date) or TODAY

        if not isinstance(getattr(S, "selected_date", None), date):
            S.selected_date = TODAY

        if not getattr(S, "cal_year", None) or not getattr(S, "cal_month", None):
            S.cal_year = S.selected_date.year
            S.cal_month = S.selected_date.month

        # ---------------------------
        # PH Holidays (English)
        # ---------------------------
        def easter_sunday(y: int) -> date:
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
            while d.weekday() != 0:
                d -= timedelta(days=1)
            return d

        def ph_holidays_for_year(y: int) -> dict[str, str]:
            hol = {}

            def add(mm: int, dd: int, name: str):
                hol[fmt_date(date(y, mm, dd))] = name

            add(1, 1, "New Year's Day")
            add(4, 9, "Araw ng Kagitingan (Day of Valor)")
            add(5, 1, "Labor Day")
            add(6, 12, "Independence Day")
            add(8, 21, "Ninoy Aquino Day")
            hol[fmt_date(last_monday(y, 8))] = "National Heroes Day"
            add(11, 30, "Bonifacio Day")
            add(12, 25, "Christmas Day")
            add(12, 30, "Rizal Day")

            add(2, 25, "EDSA People Power Revolution Anniversary")
            add(11, 1, "All Saints' Day")
            add(11, 2, "All Souls' Day")
            add(12, 8, "Immaculate Conception of Mary")
            add(12, 31, "Last Day of the Year")

            easter = easter_sunday(y)
            hol[fmt_date(easter - timedelta(days=3))] = "Maundy Thursday"
            hol[fmt_date(easter - timedelta(days=2))] = "Good Friday"
            hol[fmt_date(easter - timedelta(days=1))] = "Black Saturday"
            return hol

        holidays = ph_holidays_for_year(S.cal_year)

        def holiday_name(d: date) -> str:
            return holidays.get(fmt_date(d), "")

        # ---------------------------
        # DB Tasks (user-safe)
        # ---------------------------
        def all_tasks():
            try:
                return db.get_all_tasks(S.user["id"])
            except TypeError:
                return db.get_all_tasks()

        def build_due_set(y: int, m: int) -> set[str]:
            out = set()
            for t in all_tasks():
                d = safe_parse_date((t[4] or "").strip())
                if d and d.year == y and d.month == m:
                    out.add(fmt_date(d))
            return out

        def tasks_for_date(d: date):
            ds = fmt_date(d)
            out = []
            for t in all_tasks():
                due = (t[4] or "").strip()
                if due_date_only(due) == ds:
                    out.append(t)

            def sort_key(tr):
                tm = safe_parse_time((tr[4] or "").strip())
                return tm if tm else (99, 99)

            out.sort(key=sort_key)
            return out

        def num_tasks_for_month(y: int, m: int) -> int:
            n = 0
            for t in all_tasks():
                d = safe_parse_date((t[4] or "").strip())
                if d and d.year == y and d.month == m:
                    n += 1
            return n

        def num_holidays_for_month(y: int, m: int) -> int:
            n = 0
            for k in holidays.keys():
                dd = safe_parse_date(k)
                if dd and dd.year == y and dd.month == m:
                    n += 1
            return n

        # ---------------------------
        # Relative label
        # ---------------------------
        def relative_label(target: date) -> str:
            diff = (target - TODAY).days
            if diff == 0:
                return "Today"
            if diff > 0:
                return f"{diff} day(s) left"
            return f"{abs(diff)} day(s) ago"

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
        # UI helpers (visibility)
        # ---------------------------
        def pill(text: str, bgcolor: str, fg: str = "white", border_color: Optional[str] = None):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=12, vertical=7),
                border_radius=999,
                bgcolor=bgcolor,
                border=ft.border.all(1, border_color) if border_color else None,
                content=ft.Text(text, size=11, color=fg, weight=ft.FontWeight.W_700),
            )

        def pill_light(text: str):
            return pill(text, bgcolor="white", fg=C("TEXT_PRIMARY"), border_color=C("BORDER_COLOR"))

        def mini_stat(label: str, value: str, icon):
            return ft.Container(
                padding=12,
                border_radius=14,
                bgcolor="white",
                border=ft.border.all(1, C("BORDER_COLOR")),
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=34,
                            height=34,
                            border_radius=10,
                            bgcolor=C("BUTTON_COLOR"),
                            alignment=ft.alignment.center,
                            content=ft.Icon(icon, size=18, color="white"),
                        ),
                        ft.Column(
                            spacing=1,
                            controls=[
                                ft.Text(label, size=11, color=C("TEXT_SECONDARY")),
                                ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ],
                        ),
                    ],
                ),
            )

        # ---------------------------
        # Calendar grid (NO ink ripple)
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
            cell = 48

            header_row = ft.Row(
                [
                    ft.Container(
                        width=cell,
                        height=24,
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

                bg = "white"
                border_col = C("BORDER_COLOR")
                num_col = C("TEXT_PRIMARY")

                if is_today and not is_selected:
                    bg = ft.Colors.with_opacity(0.16, C("BUTTON_COLOR"))

                if is_selected:
                    bg = C("BUTTON_COLOR")
                    border_col = C("BUTTON_COLOR")
                    num_col = "white"
                elif is_holiday:
                    bg = ft.Colors.with_opacity(0.10, C("ERROR_COLOR"))
                elif has_task:
                    bg = ft.Colors.with_opacity(0.10, C("SUCCESS_COLOR"))

                indicators = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Container(width=7, height=7, border_radius=99, bgcolor=C("ERROR_COLOR"))
                        if is_holiday
                        else ft.Container(width=7, height=7),
                        ft.Container(width=7, height=7, border_radius=99, bgcolor=C("SUCCESS_COLOR"))
                        if has_task
                        else ft.Container(width=7, height=7),
                    ],
                )

                outline = ft.border.all(2, C("BUTTON_COLOR")) if is_today and not is_selected else ft.border.all(1, border_col)

                cells.append(
                    ft.Container(
                        width=cell,
                        height=cell,
                        border_radius=12,
                        border=outline,
                        bgcolor=bg,
                        on_click=lambda e, dd=d: select_day(dd),
                        content=ft.Column(
                            expand=True,
                            spacing=0,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    alignment=ft.alignment.center,
                                    content=ft.Text(str(day), size=12, weight=ft.FontWeight.BOLD, color=num_col),
                                ),
                                ft.Container(height=14, alignment=ft.alignment.center, content=indicators),
                            ],
                        ),
                    )
                )

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
        # Left panel
        # ---------------------------
        def build_left_panel():
            d = S.selected_date
            hol = holiday_name(d)
            items = tasks_for_date(d)

            tasks_today = len(tasks_for_date(TODAY))
            tasks_month = num_tasks_for_month(S.cal_year, S.cal_month)
            hol_month = num_holidays_for_month(S.cal_year, S.cal_month)

            header_block = ft.Container(
                border_radius=18,
                border=ft.border.all(1, C("BORDER_COLOR")),
                bgcolor=ft.Colors.with_opacity(0.18, C("BUTTON_COLOR")),
                padding=18,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(pretty_long(d), size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                pill_light(relative_label(d)),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                pill(hol if hol else "No holiday", bgcolor=C("TEXT_PRIMARY"), fg="white"),
                                pill(f"{len(items)} task(s)", bgcolor=C("BUTTON_COLOR"), fg="white"),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(expand=True, content=mini_stat("Tasks Today", str(tasks_today), ft.Icons.TODAY)),
                                ft.Container(expand=True, content=mini_stat("This Month", str(tasks_month), ft.Icons.DATE_RANGE)),
                                ft.Container(expand=True, content=mini_stat("Holidays", str(hol_month), ft.Icons.FLAG)),
                            ],
                        ),
                    ],
                ),
            )

            def status_chip(status: str):
                if (status or "").strip().lower() == "completed":
                    return pill("Completed", bgcolor=C("SUCCESS_COLOR"), fg="white")
                return pill("Pending", bgcolor=C("BUTTON_COLOR"), fg="white")

            def category_chip(cat: str):
                return pill((cat or "None").strip(), bgcolor=C("TEXT_PRIMARY"), fg="white")

            def due_chip(due: str):
                due = (due or "").strip()
                if not due:
                    return pill_light("No due date")
                return pill_light(f"Due {due}")

            if not items:
                list_area = ft.Container(
                    expand=True,
                    border_radius=18,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    bgcolor="white",
                    padding=18,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.EVENT_BUSY, size=44, color=C("TEXT_SECONDARY")),
                            ft.Text("No tasks on this day.", size=12, color=C("TEXT_SECONDARY")),
                            ft.Text("Pick another date or add a task from Tasks.", size=11, color=C("TEXT_SECONDARY")),
                        ],
                    ),
                )
            else:
                cards = []
                for t in items:
                    tid, title, desc, cat, due, status, created = t
                    cards.append(
                        ft.Container(
                            padding=14,
                            border_radius=16,
                            border=ft.border.all(1, C("BORDER_COLOR")),
                            bgcolor="white",
                            shadow=ft.BoxShadow(blur_radius=10, color="#00000010", offset=ft.Offset(0, 6)),
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                    ft.Text(
                                        (desc or "No description").strip() or "No description",
                                        size=11,
                                        color=C("TEXT_SECONDARY"),
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Row(spacing=8, controls=[category_chip(cat), status_chip(status), due_chip(due)]),
                                ],
                            ),
                        )
                    )

                list_area = ft.Container(
                    expand=True,
                    border_radius=18,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    bgcolor="white",
                    padding=14,
                    content=ft.ListView(expand=True, spacing=10, controls=cards),
                )

            return ft.Container(
                expand=True,
                border_radius=22,
                border=ft.border.all(1, C("BORDER_COLOR")),
                bgcolor=C("FORM_BG"),
                padding=22,
                content=ft.Column(
                    expand=True,
                    spacing=14,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Calendar", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ],
                        ),
                        header_block,
                        ft.Text("Tasks On This Day", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        list_area,
                    ],
                ),
            )

        # ---------------------------
        # Right panel
        # ---------------------------
        def build_right_panel():
            y, m = S.cal_year, S.cal_month
            tasks_month = num_tasks_for_month(y, m)

            top_bar = ft.Container(
                border_radius=18,
                bgcolor=C("BUTTON_COLOR"),
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color="white", on_click=prev_month),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Text(month_abbr(m), size=13, weight=ft.FontWeight.BOLD, color="white"),
                                ft.Text(str(y), size=13, weight=ft.FontWeight.BOLD, color="white"),
                                pill(f"{tasks_month} due", bgcolor=ft.Colors.with_opacity(0.20, ft.Colors.WHITE), fg="white"),
                            ],
                        ),
                        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color="white", on_click=next_month),
                    ],
                ),
            )

            grid = ft.Container(
                expand=True,
                padding=16,
                border_radius=18,
                bgcolor="white",
                border=ft.border.all(1, C("BORDER_COLOR")),
                content=build_calendar_grid(),
            )

            legend = ft.Row(
                [
                    ft.Row([ft.Container(width=10, height=10, border_radius=99, bgcolor=C("ERROR_COLOR")),
                            ft.Text("Holiday", size=11, color=C("TEXT_SECONDARY"))], spacing=8),
                    ft.Row([ft.Container(width=10, height=10, border_radius=99, bgcolor=C("SUCCESS_COLOR")),
                            ft.Text("Has Tasks", size=11, color=C("TEXT_SECONDARY"))], spacing=8),
                    ft.Row([ft.Container(width=10, height=10, border_radius=99, bgcolor=C("BUTTON_COLOR")),
                            ft.Text("Selected", size=11, color=C("TEXT_SECONDARY"))], spacing=8),
                    ft.Row([ft.Container(width=10, height=10, border_radius=99, bgcolor="white", border=ft.border.all(2, C("BUTTON_COLOR"))),
                            ft.Text("Today", size=11, color=C("TEXT_SECONDARY"))], spacing=8),
                ],
                spacing=18,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            return ft.Container(
                expand=True,
                border_radius=22,
                border=ft.border.all(1, C("BORDER_COLOR")),
                bgcolor=C("FORM_BG"),
                padding=20,
                content=ft.Column(
                    expand=True,
                    spacing=12,
                    controls=[
                        top_bar,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Month View", size=13, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                pill(pretty_long(S.selected_date), bgcolor=C("TEXT_PRIMARY"), fg="white"),
                            ],
                        ),
                        grid,
                        legend,
                    ],
                ),
            )

        board = ft.Container(
            expand=True,
            border_radius=22,
            border=ft.border.all(1, C("BORDER_COLOR")),
            bgcolor=C("BG_COLOR"),
            padding=22,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Container(content=build_left_panel(), expand=5),
                    ft.Container(width=22),
                    ft.Container(content=build_right_panel(), expand=6),
                ],
            ),
        )

        return ft.Container(
            expand=True,
            bgcolor=C("BG_COLOR"),
            padding=ft.padding.all(18),
            content=board,
        )
