import flet as ft
from datetime import datetime, date
from typing import Optional, List

from taskwise.theme import CATEGORIES  # ["Personal","Work","Study","Others","Bills"]


class TaskPage:
    """
    CONNECTED TASK PAGE:
    - Uses shared AppState (self.state) for:
        - theme colors (self.state.colors)
        - navigation (self.state.go("calendar"), self.state.go("settings"))
        - shared calendar state (selected_date, cal_year, cal_month)
        - shared database (self.state.db)
    - Due date uses DatePicker and syncs with Calendar page.
    - Category uses Dropdown options.
    """

    def __init__(self, state):
        self.state = state
        self.search_query = ""  # local UI state for searching

    def view(self, page: ft.Page) -> ft.Control:
        S = self.state
        db = S.db

        # ---------------------------
        # Colors
        # ---------------------------
        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        # ---------------------------
        # Date helpers
        # ---------------------------
        def fmt_date(d: date) -> str:
            return d.strftime("%Y-%m-%d")

        def safe_parse_date(s: Optional[str]) -> Optional[date]:
            try:
                s = (s or "").strip()
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None
            except Exception:
                return None

        # Shared DatePicker (reused by dialogs)
        due_date_picker = ft.DatePicker()
        if due_date_picker not in page.overlay:
            page.overlay.append(due_date_picker)

        # ---------------------------
        # Navigation helpers
        # ---------------------------
        def go_calendar_for_due(due_str: Optional[str]):
            dd = safe_parse_date(due_str)
            if not dd:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("No due date set for this task."),
                    bgcolor=C("ERROR_COLOR"),
                )
                page.snack_bar.open = True
                page.update()
                return

            S.selected_date = dd
            S.cal_year = dd.year
            S.cal_month = dd.month
            S.go("calendar")

        def go_calendar_today():
            today = datetime.now().date()
            S.selected_date = today
            S.cal_year = today.year
            S.cal_month = today.month
            S.go("calendar")

        def go_settings():
            S.go("settings")

        # ---------------------------
        # UI helpers
        # ---------------------------
        def chip(text: str, active: bool, on_click):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                border_radius=999,
                bgcolor=C("BUTTON_COLOR") if active else "white",
                border=ft.border.all(1, C("BORDER_COLOR")),
                ink=True,
                on_click=on_click,
                content=ft.Text(
                    text,
                    size=12,
                    color=ft.Colors.WHITE if active else C("TEXT_PRIMARY"),
                    weight=ft.FontWeight.BOLD if active else ft.FontWeight.W_600,
                ),
            )

        def small_tag(text: str, bgcolor: str, fg: str = "white"):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                border_radius=999,
                bgcolor=bgcolor,
                content=ft.Text(text, size=11, color=fg, weight=ft.FontWeight.W_600),
            )

        def category_dropdown(selected_value: Optional[str] = None) -> ft.Dropdown:
            val = selected_value if selected_value in CATEGORIES else None
            return ft.Dropdown(
                value=val,
                hint_text="Select Category",
                options=[ft.dropdown.Option(x) for x in CATEGORIES],
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
            )

        # ---------------------------
        # Dialogs: Add / Edit
        # ---------------------------
        def show_add_task_dialog():
            title_tf = ft.TextField(
                hint_text="Task Title",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            desc_tf = ft.TextField(
                hint_text="Description",
                multiline=True,
                min_lines=2,
                max_lines=4,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            category_dd = category_dropdown()

            due_tf = ft.TextField(
                hint_text="Due Date (Pick From Calendar)",
                read_only=True,
                value=fmt_date(S.selected_date) if S.selected_date else "",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def open_picker(e):
                initial = safe_parse_date(due_tf.value) or S.selected_date or datetime.now().date()
                due_date_picker.value = initial

                def on_change(ev):
                    picked = due_date_picker.value
                    if picked:
                        due_tf.value = fmt_date(picked)
                        S.selected_date = picked
                        S.cal_year = picked.year
                        S.cal_month = picked.month
                    else:
                        due_tf.value = ""
                    page.update()

                due_date_picker.on_change = on_change
                due_date_picker.open = True
                page.update()

            def save_task(e):
                title = (title_tf.value or "").strip()
                desc = (desc_tf.value or "").strip()
                cat = (category_dd.value or "").strip()
                due = (due_tf.value or "").strip()

                if not title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Title is required."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                picked = safe_parse_date(due)
                if picked:
                    S.selected_date = picked
                    S.cal_year = picked.year
                    S.cal_month = picked.month

                db.add_task(title, desc, cat, due)

                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Task added!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                S.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Add Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=480,
                    content=ft.Column(
                        [
                            title_tf,
                            desc_tf,
                            category_dd,
                            ft.Row(
                                [
                                    ft.Container(due_tf, expand=True),
                                    ft.IconButton(
                                        icon=ft.Icons.CALENDAR_MONTH,
                                        icon_color=C("TEXT_PRIMARY"),
                                        on_click=open_picker,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        tight=True,
                        spacing=12,
                    ),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Save", on_click=save_task, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def show_edit_task_dialog(task_row: tuple):
            task_id, old_title, old_desc, old_category, old_due, old_status, _ = task_row

            title_tf = ft.TextField(
                value=old_title,
                hint_text="Task Title",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            desc_tf = ft.TextField(
                value=old_desc or "",
                hint_text="Description",
                multiline=True,
                min_lines=2,
                max_lines=4,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            category_dd = category_dropdown(old_category)

            due_tf = ft.TextField(
                read_only=True,
                value=(old_due or "").strip(),
                hint_text="Due Date (Pick From Calendar)",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def open_picker(e):
                initial = safe_parse_date(due_tf.value) or S.selected_date or datetime.now().date()
                due_date_picker.value = initial

                def on_change(ev):
                    picked = due_date_picker.value
                    if picked:
                        due_tf.value = fmt_date(picked)
                        S.selected_date = picked
                        S.cal_year = picked.year
                        S.cal_month = picked.month
                    else:
                        due_tf.value = ""
                    page.update()

                due_date_picker.on_change = on_change
                due_date_picker.open = True
                page.update()

            def save_changes(e):
                title = (title_tf.value or "").strip()
                desc = (desc_tf.value or "").strip()
                cat = (category_dd.value or "").strip()
                due = (due_tf.value or "").strip()

                if not title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Title cannot be empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                picked = safe_parse_date(due)
                if picked:
                    S.selected_date = picked
                    S.cal_year = picked.year
                    S.cal_month = picked.month

                db.update_task(task_id, title, desc, cat, due)

                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Task updated!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                S.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Edit Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=480,
                    content=ft.Column(
                        [
                            title_tf,
                            desc_tf,
                            category_dd,
                            ft.Row(
                                [
                                    ft.Container(due_tf, expand=True),
                                    ft.IconButton(
                                        icon=ft.Icons.CALENDAR_MONTH,
                                        icon_color=C("TEXT_PRIMARY"),
                                        on_click=open_picker,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        tight=True,
                        spacing=12,
                    ),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton(
                        "Save Changes",
                        on_click=save_changes,
                        bgcolor=C("BUTTON_COLOR"),
                        color=ft.Colors.WHITE,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        # ---------------------------
        # Task list + analytics
        # ---------------------------
        def get_filtered_tasks() -> List[tuple]:
            tasks = db.get_all_tasks()

            current_filter = getattr(S, "current_filter", "All Tasks")
            if current_filter != "All Tasks":
                wanted = current_filter.lower().strip()
                tasks = [t for t in tasks if (t[3] or "").strip().lower() == wanted]

            q = (self.search_query or "").strip().lower()
            if q:
                def ok(t):
                    title = (t[1] or "").lower()
                    desc = (t[2] or "").lower()
                    return q in title or q in desc
                tasks = [t for t in tasks if ok(t)]

            return tasks

        def is_overdue(due_date_str: Optional[str], status: str) -> bool:
            if not due_date_str or status != "pending":
                return False
            dd = safe_parse_date(due_date_str)
            return bool(dd and dd < datetime.now().date())

        def build_task_card(t: tuple) -> ft.Control:
            task_id, title, desc, category, due_date, status, created_at = t
            overdue = is_overdue(due_date, status)

            base_bg = "white"
            highlight = ft.Colors.with_opacity(0.08, ft.Colors.RED) if overdue else ft.Colors.with_opacity(0.06, ft.Colors.BLACK)
            bg = highlight

            due_label = f"Due {due_date}" if (due_date or "").strip() else "No Due Date"
            cat_label = (category or "").strip() or "No Category"

            def toggle(e):
                new_status = "completed" if status == "pending" else "pending"
                db.update_task_status(task_id, new_status)
                S.update()

            def delete(e):
                db.delete_task(task_id)
                page.snack_bar = ft.SnackBar(content=ft.Text("Task deleted!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                S.update()

            def edit(e):
                show_edit_task_dialog(t)

            title_style = ft.TextStyle(
                size=14,
                weight=ft.FontWeight.BOLD,
                color=C("TEXT_PRIMARY") if status == "pending" else C("TEXT_SECONDARY"),
                decoration=ft.TextDecoration.LINE_THROUGH if status == "completed" else None,
            )

            status_tag = small_tag(
                "Completed" if status == "completed" else "Pending",
                bgcolor=C("SUCCESS_COLOR") if status == "completed" else C("BUTTON_COLOR"),
            )

            due_tag = small_tag(
                due_label,
                bgcolor=C("ERROR_COLOR") if overdue else C("BORDER_COLOR"),
                fg="white" if overdue else C("TEXT_PRIMARY"),
            )

            cat_tag = small_tag(cat_label, bgcolor=C("TEXT_PRIMARY"))

            card = ft.Container(
                bgcolor=base_bg,
                border_radius=14,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                shadow=ft.BoxShadow(blur_radius=10, color="#00000010", offset=ft.Offset(0, 6)),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Checkbox(value=(status == "completed"), on_change=toggle),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(title, style=title_style),
                                    ft.Text(
                                        (desc or "No description").strip() or "No description",
                                        size=11,
                                        color=C("TEXT_SECONDARY"),
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Row(
                                        spacing=8,
                                        controls=[cat_tag, due_tag, status_tag],
                                    ),
                                ],
                            ),
                        ),
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_HORIZ,
                            icon_color=C("TEXT_SECONDARY"),
                            items=[
                                ft.PopupMenuItem(text="Edit", on_click=edit),
                                ft.PopupMenuItem(text="Delete", on_click=delete),
                                ft.PopupMenuItem(text="Go To Calendar Date", on_click=lambda e, d=due_date: go_calendar_for_due(d)),
                            ],
                        ),
                    ],
                ),
            )

            def on_hover(e: ft.HoverEvent):
                if e.data == "true":
                    card.shadow = ft.BoxShadow(blur_radius=18, color="#00000018", offset=ft.Offset(0, 10))
                else:
                    card.shadow = ft.BoxShadow(blur_radius=10, color="#00000010", offset=ft.Offset(0, 6))
                page.update()

            card.on_hover = on_hover
            return card

        def build_task_list() -> ft.Control:
            tasks = get_filtered_tasks()
            if not tasks:
                return ft.Container(
                    alignment=ft.alignment.center,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.INBOX_OUTLINED, size=44, color=C("TEXT_SECONDARY")),
                            ft.Text("No tasks found in this category.", size=13, color=C("TEXT_SECONDARY")),
                            ft.Text("Add one using the + button below.", size=12, color=C("TEXT_SECONDARY")),
                        ],
                    ),
                )

            # ListView performs better than a scrollable Column
            return ft.ListView(
                expand=True,
                spacing=10,
                controls=[build_task_card(t) for t in tasks],
            )

        def build_analytics_panel() -> ft.Control:
            tasks = db.get_all_tasks()
            total = len(tasks)
            completed = sum(1 for t in tasks if t[5] == "completed")
            today = datetime.now().date()
            overdue = sum(
                1
                for t in tasks
                if t[5] == "pending" and safe_parse_date(t[4]) and safe_parse_date(t[4]) < today
            )
            pending = total - completed

            progress = 0 if total == 0 else completed / total

            # Category counts for donut (shows distribution even when empty)
            cat_counts = {c: 0 for c in CATEGORIES}
            for t in tasks:
                c = (t[3] or "").strip()
                if c in cat_counts:
                    cat_counts[c] += 1

            pie_sections = []
            for label, val in cat_counts.items():
                pie_sections.append(
                    ft.PieChartSection(
                        value=val if val > 0 else 1,
                        title=label,
                        radius=62,
                        title_style=ft.TextStyle(size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    )
                )

            donut = ft.PieChart(
                sections=pie_sections,
                center_space_radius=44,
                expand=True,
            )

            stat_card = lambda title, value, icon, color: ft.Container(
                padding=12,
                border_radius=14,
                bgcolor="white",
                border=ft.border.all(1, C("BORDER_COLOR")),
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=10,
                            bgcolor=color,
                            alignment=ft.alignment.center,
                            content=ft.Icon(icon, size=18, color="white"),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(title, size=11, color=C("TEXT_SECONDARY")),
                                ft.Text(str(value), size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ],
                        ),
                    ],
                ),
            )

            summary = ft.Container(
                bgcolor=C("FORM_BG"),
                border_radius=16,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=16,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Progress", size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                ft.Text(f"{int(progress*100)}%", size=12, color=C("TEXT_SECONDARY")),
                            ],
                        ),
                        ft.ProgressBar(value=progress, bgcolor="#DDEFEF", color=C("BUTTON_COLOR")),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(expand=True, content=stat_card("Total", total, ft.Icons.LIST_ALT, C("TEXT_PRIMARY"))),
                                ft.Container(expand=True, content=stat_card("Pending", pending, ft.Icons.SCHEDULE, C("BUTTON_COLOR"))),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Container(expand=True, content=stat_card("Completed", completed, ft.Icons.CHECK_CIRCLE, C("SUCCESS_COLOR"))),
                                ft.Container(expand=True, content=stat_card("Overdue", overdue, ft.Icons.ERROR_OUTLINE, C("ERROR_COLOR"))),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.ElevatedButton(
                                    "Open Calendar",
                                    on_click=lambda e: go_calendar_today(),
                                    bgcolor=C("BUTTON_COLOR"),
                                    color=ft.Colors.WHITE,
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    "Open Settings",
                                    on_click=lambda e: go_settings(),
                                    bgcolor=C("BUTTON_COLOR"),
                                    color=ft.Colors.WHITE,
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                ),
            )

            donut_card = ft.Container(
                expand=True,
                bgcolor=C("FORM_BG"),
                border_radius=16,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=16,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("Category Mix", size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Container(expand=True, content=donut),
                    ],
                ),
            )

            return ft.Column(
                expand=True,
                spacing=14,
                controls=[
                    donut_card,
                    summary,
                ],
            )

        # ---------------------------
        # Filter toolbar + search
        # ---------------------------
        def build_filter_bar() -> ft.Control:
            def set_filter(label: str):
                def f(e):
                    S.current_filter = label
                    S.update()
                return f

            current = getattr(S, "current_filter", "All Tasks")
            chips = [chip("All Tasks", current == "All Tasks", set_filter("All Tasks"))]
            for c in CATEGORIES:
                chips.append(chip(c, current == c, set_filter(c)))

            # Horizontal scroll chips: ListView(horizontal=True)
            return ft.Container(
                height=48,
                content=ft.ListView(
                    horizontal=True,
                    spacing=10,
                    controls=chips,
                ),
            )

        def build_search_row() -> ft.Control:
            search_tf = ft.TextField(
                hint_text="Search tasks...",
                prefix_icon=ft.Icons.SEARCH,
                bgcolor="white",
                filled=True,
                border_radius=14,
                border_color=C("BORDER_COLOR"),
                color=C("TEXT_PRIMARY"),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
                on_change=lambda e: self._set_search(e, S),
            )

            return ft.Row(
                spacing=10,
                controls=[
                    ft.Container(expand=True, content=search_tf),
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        icon_color=C("TEXT_PRIMARY"),
                        tooltip="Open Calendar",
                        on_click=lambda e: go_calendar_today(),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        icon_color=C("TEXT_PRIMARY"),
                        tooltip="Open Settings",
                        on_click=lambda e: go_settings(),
                    ),
                ],
            )

        # helper: search update
        # (kept separate so it stays clean)
        # ---------------------------
        def build_left_panel() -> ft.Control:
            return ft.Container(
                expand=True,
                bgcolor=C("FORM_BG"),
                border_radius=18,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=20,
                content=ft.Column(
                    expand=True,
                    spacing=12,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Tasks", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                                small_tag(getattr(S, "current_filter", "All Tasks"), bgcolor=C("TEXT_PRIMARY")),
                            ],
                        ),
                        build_search_row(),
                        build_filter_bar(),
                        ft.Container(
                            expand=True,
                            padding=ft.padding.only(top=6),
                            content=build_task_list(),
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.FloatingActionButton(
                                    icon=ft.Icons.ADD,
                                    bgcolor=C("BUTTON_COLOR"),
                                    foreground_color=ft.Colors.WHITE,
                                    on_click=lambda e: show_add_task_dialog(),
                                )
                            ],
                        ),
                    ],
                ),
            )

        # ---------------------------
        # Layout
        # ---------------------------
        left_panel = build_left_panel()

        right_panel = ft.Container(
            expand=True,
            padding=20,
            bgcolor=C("BG_COLOR"),
            content=build_analytics_panel(),
        )

        board = ft.Container(
            expand=True,
            bgcolor=C("BG_COLOR"),
            border_radius=18,
            border=ft.border.all(1, C("BORDER_COLOR")),
            padding=16,
            content=ft.Row(
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Container(expand=6, content=left_panel),
                    ft.Container(width=16),
                    ft.Container(width=1, bgcolor=C("BORDER_COLOR"), margin=ft.margin.symmetric(vertical=10)),
                    ft.Container(width=16),
                    ft.Container(expand=4, content=right_panel),
                ],
            ),
        )

        return board

    def _set_search(self, e, S):
        self.search_query = e.control.value or ""
        S.update()
