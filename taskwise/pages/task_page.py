import flet as ft
from datetime import datetime, date, time
from typing import Optional, List, Dict, Tuple

from taskwise.theme import CATEGORIES  # ["Personal","Work","Study","Others","Bills"]


class TaskPage:
    SORT_CUSTOM = "Custom"
    SORT_NAME = "Name"
    SORT_CREATED = "Created"
    SORT_DUE = "Due Date"

    def __init__(self, state):
        self.state = state
        self.search_query = ""

        # Persistent UI controls (prevents blinking / focus loss)
        self._search_tf: Optional[ft.TextField] = None
        self._task_list_host = ft.Container(expand=True)
        self._analytics_host = ft.Container(expand=True)
        self._filter_bar_host = ft.Container(height=48)
        self._filter_tag_text: Optional[ft.Text] = None
        self._sort_tag_text: Optional[ft.Text] = None

        # Shared pickers
        self._due_date_picker = ft.DatePicker()
        self._due_time_picker = ft.TimePicker()

        # cached visible ids (used for reorder)
        self._visible_task_ids: List[int] = []

    def view(self, page: ft.Page) -> ft.Control:
        S = self.state
        db = S.db

        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        # Defaults
        if not hasattr(S, "current_filter"):
            S.current_filter = "All Tasks"
        if not hasattr(S, "sort_mode"):
            S.sort_mode = self.SORT_CUSTOM
        if not hasattr(S, "task_order_ids"):
            S.task_order_ids = []

        # ---------------------------
        # Date/time helpers
        # ---------------------------
        def fmt_date(d: date) -> str:
            return d.strftime("%Y-%m-%d")

        def fmt_time(t: time) -> str:
            return f"{t.hour:02d}:{t.minute:02d}"

        def safe_parse_date(s: Optional[str]) -> Optional[date]:
            try:
                s = (s or "").strip()
                return datetime.strptime(s, "%Y-%m-%d").date() if s else None
            except Exception:
                return None

        def safe_parse_time(s: Optional[str]) -> Optional[time]:
            try:
                s = (s or "").strip()
                if not s:
                    return None
                hh, mm = s.split(":")
                return time(int(hh), int(mm))
            except Exception:
                return None

        def parse_due_datetime(due_str: Optional[str]) -> Tuple[Optional[date], Optional[time]]:
            s = (due_str or "").strip()
            if not s:
                return None, None
            parts = s.split()
            d = safe_parse_date(parts[0]) if parts else None
            t = safe_parse_time(parts[1]) if len(parts) > 1 else None
            return d, t

        def combine_due(d: Optional[date], t: Optional[time]) -> str:
            if not d:
                return ""
            if not t:
                return fmt_date(d)
            return f"{fmt_date(d)} {fmt_time(t)}"

        def due_date_only(due_str: Optional[str]) -> Optional[date]:
            d, _ = parse_due_datetime(due_str)
            return d

        # Ensure pickers exist once
        if self._due_date_picker not in page.overlay:
            page.overlay.append(self._due_date_picker)
        if self._due_time_picker not in page.overlay:
            page.overlay.append(self._due_time_picker)

        # ---------------------------
        # Navigation
        # ---------------------------
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
        def pill(text: str, bgcolor: str, fg: str = "white", border_color: Optional[str] = None) -> ft.Container:
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                border_radius=999,
                bgcolor=bgcolor,
                border=ft.border.all(1, border_color) if border_color else None,
                content=ft.Text(text, size=11, color=fg, weight=ft.FontWeight.W_700),
            )

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
        # Sort + order helpers
        # ---------------------------
        def get_current_filter() -> str:
            return getattr(S, "current_filter", "All Tasks") or "All Tasks"

        def get_sort_mode() -> str:
            return getattr(S, "sort_mode", self.SORT_CUSTOM) or self.SORT_CUSTOM

        def normalize_task_order(all_tasks_rows: List[tuple]):
            ids = [t[0] for t in all_tasks_rows]
            current = [i for i in S.task_order_ids if i in ids]
            missing = [i for i in ids if i not in current]
            S.task_order_ids = current + missing

        def try_persist_order():
            for idx, tid in enumerate(S.task_order_ids):
                try:
                    db.update_task_order(tid, idx, S.user["id"])
                except Exception:
                    return

        def is_overdue(due_str: Optional[str], status: str) -> bool:
            if status != "pending":
                return False
            d, t = parse_due_datetime(due_str)
            if not d:
                return False
            if not t:
                return d < datetime.now().date()
            due_dt = datetime(d.year, d.month, d.day, t.hour, t.minute)
            return due_dt < datetime.now()

        def sort_tasks(rows: List[tuple]) -> List[tuple]:
            mode = get_sort_mode()

            if mode == self.SORT_NAME:
                return sorted(rows, key=lambda t: (t[1] or "").lower().strip())

            if mode == self.SORT_CREATED:
                def k(t):
                    v = t[6]
                    try:
                        if isinstance(v, (int, float)):
                            return v
                        if isinstance(v, str) and v.strip():
                            return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
                    except Exception:
                        pass
                    return 0
                return sorted(rows, key=k, reverse=True)

            if mode == self.SORT_DUE:
                def k(t):
                    d = due_date_only(t[4])
                    return (1, d) if d else (0, date(9999, 12, 31))
                return sorted(rows, key=k)

            # Custom
            index_map: Dict[int, int] = {tid: i for i, tid in enumerate(S.task_order_ids)}
            return sorted(rows, key=lambda t: index_map.get(t[0], 10**9))

        def get_filtered_tasks() -> List[tuple]:
            tasks = db.get_all_tasks(S.user["id"])
            normalize_task_order(tasks)

            current_filter = get_current_filter()
            if current_filter != "All Tasks":
                wanted = current_filter.lower().strip()
                tasks = [t for t in tasks if (t[3] or "").strip().lower() == wanted]

            q = (self.search_query or "").strip().lower()
            if q:
                def ok(t):
                    return q in (t[1] or "").lower() or q in (t[2] or "").lower()
                tasks = [t for t in tasks if ok(t)]

            return sort_tasks(tasks)

        # ---------------------------
        # Refresh
        # ---------------------------
        def refresh():
            if self._filter_tag_text is not None:
                self._filter_tag_text.value = get_current_filter()
            if self._sort_tag_text is not None:
                self._sort_tag_text.value = f"Sort: {get_sort_mode()}"

            self._filter_bar_host.content = build_filter_bar()
            self._task_list_host.content = build_task_list()
            self._analytics_host.content = build_analytics_panel()
            page.update()

        # ---------------------------
        # Due controls
        # ---------------------------
        def build_due_controls(initial_due: str = "") -> tuple[ft.TextField, ft.TextField, ft.Row]:
            init_d, init_t = parse_due_datetime(initial_due)

            date_tf = ft.TextField(
                hint_text="Due Date",
                read_only=True,
                value=fmt_date(init_d) if init_d else "",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            time_tf = ft.TextField(
                hint_text="Due Time (Optional)",
                read_only=True,
                value=fmt_time(init_t) if init_t else "",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def open_date_picker(e):
                initial = init_d or getattr(S, "selected_date", None) or datetime.now().date()
                self._due_date_picker.value = initial

                def on_change(ev):
                    picked = self._due_date_picker.value
                    date_tf.value = fmt_date(picked) if picked else ""
                    if picked:
                        S.selected_date = picked
                        S.cal_year = picked.year
                        S.cal_month = picked.month
                    page.update()

                self._due_date_picker.on_change = on_change
                self._due_date_picker.open = True
                page.update()

            def open_time_picker(e):
                current_t = safe_parse_time(time_tf.value) or init_t or datetime.now().time().replace(second=0, microsecond=0)
                self._due_time_picker.value = current_t

                def on_change(ev):
                    picked = self._due_time_picker.value
                    time_tf.value = fmt_time(picked) if picked else ""
                    page.update()

                self._due_time_picker.on_change = on_change
                self._due_time_picker.open = True
                page.update()

            row = ft.Row(
                spacing=10,
                controls=[
                    ft.Container(expand=True, content=date_tf),
                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_color=C("TEXT_PRIMARY"), on_click=open_date_picker),
                    ft.Container(width=10),
                    ft.Container(width=160, content=time_tf),
                    ft.IconButton(icon=ft.Icons.ACCESS_TIME, icon_color=C("TEXT_PRIMARY"), on_click=open_time_picker),
                ],
            )

            return date_tf, time_tf, row

        # ---------------------------
        # Add/Edit dialogs
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
            default_due = fmt_date(S.selected_date) if getattr(S, "selected_date", None) else ""
            due_date_tf, due_time_tf, due_row = build_due_controls(default_due)

            def save_task(e):
                title = (title_tf.value or "").strip()
                if not title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Title is required."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                desc = (desc_tf.value or "").strip()
                cat = (category_dd.value or "").strip()

                d = safe_parse_date(due_date_tf.value)
                t = safe_parse_time(due_time_tf.value)
                due = combine_due(d, t)

                if d:
                    S.selected_date = d
                    S.cal_year = d.year
                    S.cal_month = d.month

                db.add_task(title, desc, cat, due, S.user["id"])

                # update ordering list
                try:
                    tasks_now = db.get_all_tasks(S.user["id"])
                    normalize_task_order(tasks_now)
                    try_persist_order()
                except Exception:
                    pass

                dialog.open = False
                page.update()
                page.snack_bar = ft.SnackBar(content=ft.Text("Task added!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                refresh()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Add Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=520, content=ft.Column([title_tf, desc_tf, category_dd, due_row], tight=True, spacing=12)),
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
            due_date_tf, due_time_tf, due_row = build_due_controls(old_due or "")

            def save_changes(e):
                title = (title_tf.value or "").strip()
                if not title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Title cannot be empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                desc = (desc_tf.value or "").strip()
                cat = (category_dd.value or "").strip()

                d = safe_parse_date(due_date_tf.value)
                t = safe_parse_time(due_time_tf.value)
                due = combine_due(d, t)

                if d:
                    S.selected_date = d
                    S.cal_year = d.year
                    S.cal_month = d.month

                db.update_task(task_id, title, desc, cat, due, S.user["id"])

                dialog.open = False
                page.update()
                page.snack_bar = ft.SnackBar(content=ft.Text("Task updated!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                refresh()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Edit Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=520, content=ft.Column([title_tf, desc_tf, category_dd, due_row], tight=True, spacing=12)),
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
        # Reorder logic (Custom only)
        # ---------------------------
        def apply_visible_reorder_to_global(visible_ids: List[int], old_index: int, new_index: int):
            if not visible_ids:
                return

            vis = visible_ids[:]
            if old_index < 0 or old_index >= len(vis):
                return
            new_index = max(0, min(new_index, len(vis) - 1))
            if old_index == new_index:
                return

            item = vis.pop(old_index)
            vis.insert(new_index, item)

            global_ids = S.task_order_ids[:]
            vis_set = set(visible_ids)

            # ensure global has all visible ids
            for tid in visible_ids:
                if tid not in global_ids:
                    global_ids.append(tid)

            positions = [i for i, tid in enumerate(global_ids) if tid in vis_set]
            if len(positions) < len(vis):
                global_ids = [tid for tid in global_ids if tid not in vis_set] + vis
            else:
                for pos, tid in zip(positions, vis):
                    global_ids[pos] = tid

            S.task_order_ids = global_ids

        def on_reorder(e: ft.OnReorderEvent):
            if get_sort_mode() != self.SORT_CUSTOM:
                page.snack_bar = ft.SnackBar(content=ft.Text("Switch sort to Custom to reorder tasks."), bgcolor=C("ERROR_COLOR"))
                page.snack_bar.open = True
                page.update()
                refresh()
                return

            old = e.old_index
            new = e.new_index
            if new > old:
                new -= 1

            apply_visible_reorder_to_global(self._visible_task_ids, old, new)
            try_persist_order()
            refresh()

        # ---------------------------
        # Task card (shows drag icon)
        # ---------------------------
        def build_task_card(t: tuple) -> ft.Control:
            task_id, title, desc, category, due_str, status, created_at = t
            overdue = is_overdue(due_str, status)

            title_style = ft.TextStyle(
                size=14,
                weight=ft.FontWeight.BOLD,
                color=C("TEXT_PRIMARY") if status == "pending" else C("TEXT_SECONDARY"),
                decoration=ft.TextDecoration.LINE_THROUGH if status == "completed" else None,
            )

            due_clean = (due_str or "").strip()
            due_label = f"Due {due_clean}" if due_clean else "No Due Date"
            cat_label = (category or "").strip() or "No Category"

            cat_tag = pill(cat_label, bgcolor=C("TEXT_PRIMARY"), fg="white")
            status_tag = pill(
                "Completed" if status == "completed" else "Pending",
                bgcolor=C("SUCCESS_COLOR") if status == "completed" else C("TEXT_PRIMARY"),
                fg="white",
            )
            due_tag = (
                pill(due_label, bgcolor=C("ERROR_COLOR"), fg="white")
                if overdue
                else pill(due_label, bgcolor="white", fg=C("TEXT_PRIMARY"), border_color=C("BORDER_COLOR"))
            )

            def toggle(e):
                new_status = "completed" if status == "pending" else "pending"
                db.update_task_status(task_id, new_status, S.user["id"])
                refresh()

            def edit(e):
                show_edit_task_dialog(t)

            def confirm_delete():
                def do_delete(ev):
                    confirm.open = False
                    page.update()
                    db.delete_task(task_id, S.user["id"])
                    S.task_order_ids = [x for x in S.task_order_ids if x != task_id]
                    try_persist_order()
                    page.snack_bar = ft.SnackBar(content=ft.Text("Task deleted!"), bgcolor=C("SUCCESS_COLOR"))
                    page.snack_bar.open = True
                    refresh()

                def cancel(ev):
                    confirm.open = False
                    page.update()

                confirm = ft.AlertDialog(
                    modal=True,
                    bgcolor=C("FORM_BG"),
                    title=ft.Text("Delete Task?", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                    content=ft.Text("Are you sure you want to delete this task? This action cannot be undone.", color=C("TEXT_SECONDARY")),
                    actions=[
                        ft.TextButton("Cancel", on_click=cancel),
                        ft.ElevatedButton("Delete", on_click=do_delete, bgcolor=C("ERROR_COLOR"), color=ft.Colors.WHITE),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    shape=ft.RoundedRectangleBorder(radius=16),
                )
                page.overlay.append(confirm)
                confirm.open = True
                page.update()

            drag_handle = ft.Container(
                width=28,
                height=48,  # same “feel” as the row height
                alignment=ft.alignment.center,
                padding=ft.padding.only(left=2, right=8),
                content=ft.Icon(
                    ft.Icons.DRAG_INDICATOR,
                    size=18,
                    color=C("TEXT_SECONDARY"),
                ),
            )


            return ft.Container(
                bgcolor="white",
                border_radius=14,
                border=ft.border.all(1, C("BORDER_COLOR")),
                padding=ft.padding.symmetric(horizontal=12, vertical=12),
                shadow=ft.BoxShadow(blur_radius=10, color="#00000010", offset=ft.Offset(0, 6)),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        drag_handle,
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
                                    ft.Row(spacing=8, controls=[cat_tag, due_tag, status_tag]),
                                ],
                            ),
                        ),
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=C("TEXT_SECONDARY"), tooltip="Edit", on_click=edit),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=C("ERROR_COLOR"), tooltip="Delete", on_click=lambda e: confirm_delete()),
                            ],
                        ),
                    ],
                ),
            )
        # ---------------------------
        # Task list (NO ReorderableDragStartListener)
        # ---------------------------
        def build_task_list() -> ft.Control:
            tasks = get_filtered_tasks()
            self._visible_task_ids = [t[0] for t in tasks]

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

            controls: List[ft.Control] = []
            for t in tasks:
                task_id = t[0]
                card = build_task_card(t)
                controls.append(
                    ft.Container(
                        key=str(task_id),            # stable key for reorder
                        margin=ft.margin.only(bottom=10),  # replaces spacing
                        content=card,
                    )
                )

            return ft.ReorderableListView(
                expand=True,
                on_reorder=on_reorder,
                controls=controls,
            )


        # ---------------------------
        # Analytics panel
        # ---------------------------
        def build_analytics_panel() -> ft.Control:
            tasks = db.get_all_tasks(S.user["id"])
            total = len(tasks)
            completed = sum(1 for t in tasks if t[5] == "completed")
            overdue = sum(1 for t in tasks if is_overdue(t[4], t[5]))
            pending = total - completed
            progress = 0 if total == 0 else completed / total

            cat_counts = {c: 0 for c in CATEGORIES}
            for t in tasks:
                c = (t[3] or "").strip()
                if c in cat_counts:
                    cat_counts[c] += 1

            if total == 0:
                donut_content = ft.Container(
                    alignment=ft.alignment.center,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.DONUT_SMALL_OUTLINED, size=44, color=C("TEXT_SECONDARY")),
                            ft.Text("No tasks yet.", size=13, color=C("TEXT_SECONDARY")),
                            ft.Text("Add a task to see category percentages.", size=12, color=C("TEXT_SECONDARY")),
                        ],
                    ),
                )
            else:
                pie_sections = []
                for label, val in cat_counts.items():
                    if val <= 0:
                        continue
                    pct = int(round((val / total) * 100))
                    pct = max(pct, 1)
                    pie_sections.append(
                        ft.PieChartSection(
                            value=val,
                            title=f"{label}\n{pct}%",
                            radius=62,
                            title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        )
                    )
                donut_content = ft.PieChart(sections=pie_sections, center_space_radius=44, expand=True)

            def stat_card(title, value, icon, color):
                return ft.Container(
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
                                ft.Text(f"{int(progress * 100)}%", size=12, color=C("TEXT_SECONDARY")),
                            ],
                        ),
                        ft.ProgressBar(value=progress, bgcolor="#DDEFEF", color=C("#DDEFEF")),
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
                                ft.ElevatedButton("Open Calendar", on_click=lambda e: go_calendar_today(), bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE, expand=True),
                                ft.ElevatedButton("Open Settings", on_click=lambda e: go_settings(), bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE, expand=True),
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
                        ft.Container(expand=True, content=donut_content),
                    ],
                ),
            )

            return ft.Column(expand=True, spacing=14, controls=[donut_card, summary])

        # ---------------------------
        # Filter bar + "..." sort menu
        # ---------------------------
        def build_filter_bar() -> ft.Control:
            def set_filter(label: str):
                def handler(e):
                    S.current_filter = label
                    refresh()
                return handler

            def set_sort(mode: str):
                def handler(e):
                    S.sort_mode = mode
                    refresh()
                return handler

            current = get_current_filter()
            chips = [chip("All Tasks", current == "All Tasks", set_filter("All Tasks"))]
            for c in CATEGORIES:
                chips.append(chip(c, current == c, set_filter(c)))

            chips_scroller = ft.ListView(horizontal=True, spacing=10, controls=chips, expand=True)

            sort_menu = ft.PopupMenuButton(
                icon=ft.Icons.MORE_HORIZ,
                icon_color=C("TEXT_PRIMARY"),
                tooltip="Sort options",
                items=[
                    ft.PopupMenuItem(text="Sort: Custom (Drag Order)", on_click=set_sort(self.SORT_CUSTOM)),
                    ft.PopupMenuItem(text="Sort: Name", on_click=set_sort(self.SORT_NAME)),
                    ft.PopupMenuItem(text="Sort: Created", on_click=set_sort(self.SORT_CREATED)),
                    ft.PopupMenuItem(text="Sort: Due Date", on_click=set_sort(self.SORT_DUE)),
                ],
            )

            return ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[chips_scroller, sort_menu])

        # ---------------------------
        # Search row
        # ---------------------------
        def on_search_change(e: ft.ControlEvent):
            self.search_query = e.control.value or ""
            refresh()

        def build_search_row() -> ft.Control:
            if self._search_tf is None:
                self._search_tf = ft.TextField(
                    hint_text="Search tasks...",
                    prefix_icon=ft.Icons.SEARCH,
                    bgcolor="white",
                    filled=True,
                    border_radius=14,
                    border_color=C("BORDER_COLOR"),
                    color=C("TEXT_PRIMARY"),
                    content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    on_change=on_search_change,
                    autofocus=False,
                )
            return ft.Row(
                spacing=10,
                controls=[
                    ft.Container(expand=True, content=self._search_tf),
                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_color=C("TEXT_PRIMARY"), tooltip="Open Calendar", on_click=lambda e: go_calendar_today()),
                    ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=C("TEXT_PRIMARY"), tooltip="Open Settings", on_click=lambda e: go_settings()),
                ],
            )

        # ---------------------------
        # Left panel
        # ---------------------------
        def build_left_panel() -> ft.Control:
            if self._filter_tag_text is None:
                self._filter_tag_text = ft.Text(get_current_filter(), size=11, color="white", weight=ft.FontWeight.W_700)
            if self._sort_tag_text is None:
                self._sort_tag_text = ft.Text(f"Sort: {get_sort_mode()}", size=11, color="white", weight=ft.FontWeight.W_700)

            selected_filter_pill = ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                border_radius=999,
                bgcolor=C("TEXT_PRIMARY"),
                content=self._filter_tag_text,
            )

            selected_sort_pill = ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                border_radius=999,
                bgcolor=C("TEXT_PRIMARY"),
                content=self._sort_tag_text,
            )

            self._filter_bar_host.content = build_filter_bar()
            if self._task_list_host.content is None:
                self._task_list_host.content = build_task_list()

            sort_hint = ft.Text(
                "Tip: Set Sort to Custom to drag and reorder tasks.",
                size=11,
                color=C("TEXT_SECONDARY"),
            )

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
                                ft.Row(spacing=8, controls=[selected_filter_pill, selected_sort_pill]),
                            ],
                        ),
                        build_search_row(),
                        self._filter_bar_host,
                        sort_hint,
                        ft.Container(expand=True, padding=ft.padding.only(top=6), content=self._task_list_host),
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
        if self._analytics_host.content is None:
            self._analytics_host.content = build_analytics_panel()

        left_panel = build_left_panel()
        right_panel = ft.Container(expand=True, padding=20, bgcolor=C("BG_COLOR"), content=self._analytics_host)

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

        refresh()
        return board
