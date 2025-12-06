# taskwise/pages/task_page.py
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
        # Navigation helpers (connect to Calendar + Settings)
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
        def badge(text: str) -> ft.Control:
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                bgcolor=C("BUTTON_COLOR"),
                border_radius=999,
                content=ft.Text(text, size=11, color=ft.Colors.WHITE),
            )

        def pill_button(label: str) -> ft.Control:
            active = (S.current_filter == label)

            def set_filter(e):
                S.current_filter = label
                S.update()

            return ft.Container(
                on_click=set_filter,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border_radius=999,
                bgcolor=C("BUTTON_COLOR") if active else C("BG_COLOR"),
                border=ft.border.all(1, C("BORDER_COLOR")),
                content=ft.Text(
                    label,
                    size=12,
                    color=ft.Colors.WHITE if active else C("TEXT_PRIMARY"),
                    weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL,
                ),
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

                        # CONNECT TO CALENDAR PAGE (shared state)
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
                    width=460,
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

                        # CONNECT TO CALENDAR PAGE (shared state)
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
                    width=460,
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
                    ft.ElevatedButton("Save Changes", on_click=save_changes, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
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
            return tasks

        def is_overdue(due_date_str: Optional[str], status: str) -> bool:
            if not due_date_str or status != "pending":
                return False
            dd = safe_parse_date(due_date_str)
            return bool(dd and dd < datetime.now().date())

        def build_task_card(t: tuple) -> ft.Control:
            task_id, title, desc, category, due_date, status, created_at = t

            overdue = is_overdue(due_date, status)
            bg = C("FORM_BG") if not overdue else ft.Colors.with_opacity(0.10, ft.Colors.RED)

            due_label = f"Due: {due_date}" if (due_date or "").strip() else "No due date"
            cat_label = (category or "").strip() or "No category"

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

            return ft.Container(
                bgcolor=bg,
                border_radius=14,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                content=ft.Row(
                    [
                        ft.Checkbox(value=(status == "completed"), on_change=toggle),
                        ft.Column(
                            [
                                ft.Text(
                                    title,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=C("TEXT_PRIMARY") if status == "pending" else C("TEXT_SECONDARY"),
                                ),
                                ft.Text(
                                    (desc or "No description").strip() or "No description",
                                    size=11,
                                    color=C("TEXT_SECONDARY"),
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(due_label, size=11, color=C("TEXT_SECONDARY")),
                                        ft.Text(f"Category: {cat_label}", size=11, color=C("TEXT_SECONDARY")),
                                    ],
                                    spacing=14,
                                ),
                            ],
                            spacing=4,
                            expand=True,
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
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

        def build_task_list() -> ft.Control:
            tasks = get_filtered_tasks()
            if not tasks:
                return ft.Container(
                    alignment=ft.alignment.center,
                    padding=20,
                    content=ft.Text("No tasks found in this category.", size=13, color=C("TEXT_SECONDARY")),
                )

            return ft.Column(
                [build_task_card(t) for t in tasks],
                spacing=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
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

            # category counts
            cat_counts = {c: 0 for c in CATEGORIES}
            for t in tasks:
                c = (t[3] or "").strip()
                if c in cat_counts:
                    cat_counts[c] += 1

            pie_sections = []
            for label, val in cat_counts.items():
                # keep visible slices; still represents distribution
                pie_sections.append(
                    ft.PieChartSection(
                        value=val if val > 0 else 1,
                        title=label,
                        radius=60,
                        title_style=ft.TextStyle(size=11, color=ft.Colors.WHITE),
                    )
                )

            donut = ft.PieChart(
                sections=pie_sections,
                center_space_radius=42,
                expand=True,
            )

            summary = ft.Container(
                bgcolor=C("FORM_BG"),
                border_radius=14,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=16,
                content=ft.Column(
                    [
                        ft.Text("Summary", size=16, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Container(height=8),
                        ft.Text(f"Total Tasks: {total}", size=12, color=C("TEXT_PRIMARY")),
                        ft.Text(f"Completed: {completed}", size=12, color=C("TEXT_PRIMARY")),
                        ft.Text(f"Overdue: {overdue}", size=12, color=C("TEXT_PRIMARY")),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Open Calendar",
                                    on_click=lambda e: go_calendar_today(),
                                    bgcolor=C("BUTTON_COLOR"),
                                    color=ft.Colors.WHITE,
                                ),
                                ft.ElevatedButton(
                                    "Open Settings",
                                    on_click=lambda e: go_settings(),
                                    bgcolor=C("BUTTON_COLOR"),
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=4,
                ),
            )

            return ft.Column(
                [
                    ft.Container(
                        expand=True,
                        bgcolor=C("FORM_BG"),
                        border_radius=14,
                        border=ft.border.all(1, C("BORDER_COLOR")),
                        padding=16,
                        content=donut,
                    ),
                    ft.Container(height=14),
                    summary,
                ],
                expand=True,
            )

        # ---------------------------
        # Build full page layout (no header here; app.py owns the header)
        # ---------------------------
        left_panel = ft.Container(
            expand=True,
            bgcolor=C("FORM_BG"),
            border_radius=18,
            border=ft.border.all(1, C("BORDER_COLOR")),
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Tasks", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ft.Container(expand=True),
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
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=12),
                    ft.Row(
                        [pill_button("All Tasks")] + [pill_button(x) for x in CATEGORIES],
                        spacing=10,
                        wrap=True,
                    ),
                    ft.Container(height=16),
                    ft.Container(expand=True, content=build_task_list()),
                    ft.Container(height=16),
                    ft.Row(
                        [
                            ft.FloatingActionButton(
                                icon=ft.Icons.ADD,
                                bgcolor=C("BUTTON_COLOR"),
                                foreground_color=ft.Colors.WHITE,
                                on_click=lambda e: show_add_task_dialog(),
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                expand=True,
                spacing=0,
            ),
        )

        right_panel = ft.Container(
            expand=True,
            padding=20,
            bgcolor=C("BG_COLOR"),
            content=build_analytics_panel(),
        )

        # Main board centered and maximized
        board = ft.Container(
            expand=True,
            bgcolor=C("BG_COLOR"),
            border_radius=18,
            border=ft.border.all(1, C("BORDER_COLOR")),
            padding=16,
            content=ft.Row(
                [
                    ft.Container(content=left_panel, expand=6),
                    ft.Container(width=18),
                    ft.Container(
                        width=1,
                        bgcolor=C("BORDER_COLOR"),
                        margin=ft.margin.symmetric(vertical=10),
                    ),
                    ft.Container(width=18),
                    ft.Container(content=right_panel, expand=4),
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

        return board
