import flet as ft
from datetime import datetime, date
from typing import Optional, List

from taskwise.theme import CATEGORIES  # ["Personal","Work","Study","Others","Bills"]


class TaskPage:
    """
    CONNECTED TASK PAGE (Fixed):
    - Pie chart empty when no tasks.
    - Pie chart updates with category + percentage when tasks change.
    - Search works without blinking (no full rebuild on each keystroke).
    - Replaces "..." menu with Edit/Delete icons.
    - Delete asks for confirmation.
    - Removes calendar icon beside delete icon on task cards.
    - Adds "..." menu on category row for sorting: Title, Due Date, Date Created, Custom.
    - Adds drag icon and enables drag-to-reorder tasks (Custom order).
    """

    def __init__(self, state):
        self.state = state
        self.search_query = ""

        # Stateful controls (avoid rebuild flicker)
        self._search_tf: Optional[ft.TextField] = None
        self._task_list_host: Optional[ft.Container] = None
        self._analytics_host: Optional[ft.Container] = None
        self._filter_chip_row: Optional[ft.Container] = None
        self._filter_pill: Optional[ft.Container] = None

        self._due_date_picker: Optional[ft.DatePicker] = None

        # ✅ add TimePicker (for due time)
        self._due_time_picker: Optional[ft.TimePicker] = None

        # small “movement” on refresh (rotate chart)
        self._chart_rotation = 0

        # Custom ordering (drag-to-reorder)
        self._custom_order_ids: List[int] = []

    # ---------------------------
    # Utilities
    # ---------------------------
    @staticmethod
    def _fmt_date(d: date) -> str:
        return d.strftime("%Y-%m-%d")

    @staticmethod
    def _fmt_time_12h(hour: int, minute: int) -> str:
        ampm = "AM" if hour < 12 else "PM"
        h12 = hour % 12
        if h12 == 0:
            h12 = 12
        return f"{h12}:{minute:02d} {ampm}"

    @staticmethod
    def _normalize_time_str(s: str) -> str:
        """
        Accepts:
          - HH:MM   (24h)
          - H:MM AM/PM  (12h)
        Returns 12h string: h:MM AM/PM, or "" if invalid.
        """
        s = (s or "").strip()
        if not s:
            return ""

        # already AM/PM?
        upper = s.upper()
        if "AM" in upper or "PM" in upper:
            try:
                dt = datetime.strptime(upper.replace("  ", " ").strip(), "%I:%M %p")
                return f"{dt.strftime('%I').lstrip('0') or '12'}:{dt.strftime('%M')} {dt.strftime('%p')}"
            except Exception:
                return ""

        # try 24h HH:MM
        try:
            hh, mm = s.split(":", 1)
            hour = int(hh)
            minute = int(mm)
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return TaskPage._fmt_time_12h(hour, minute)
        except Exception:
            pass

        return ""

    @staticmethod
    def _safe_parse_date(s: Optional[str]) -> Optional[date]:
        """
        Accepts:
          - YYYY-MM-DD
          - YYYY-MM-DD HH:MM
          - YYYY-MM-DD hh:MM AM/PM
          - YYYY-MM-DDTHH:MM
        Returns date or None.
        """
        try:
            s = (s or "").strip()
            if not s:
                return None

            # Strip time portion if present
            if " " in s:
                s = s.split(" ", 1)[0]
            if "T" in s:
                s = s.split("T", 1)[0]

            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    @staticmethod
    def _safe_parse_datetime(s: Optional[str]) -> Optional[datetime]:
        """
        Accepts:
          - YYYY-MM-DD
          - YYYY-MM-DD HH:MM
          - YYYY-MM-DD hh:MM AM/PM
          - YYYY-MM-DDTHH:MM
        Returns datetime or None.
        """
        try:
            s = (s or "").strip()
            if not s:
                return None

            # Normalize "T" separator
            s = s.replace("T", " ")

            # Try common formats (12h first so "1:18 PM" works)
            for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(s, fmt)
                    if fmt == "%Y-%m-%d":
                        # If only date, treat as end of day for due/overdue logic
                        return datetime(dt.year, dt.month, dt.day, 23, 59)
                    return dt
                except Exception:
                    continue

            # last attempt
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None
        except Exception:
            return None

    @staticmethod
    def _mounted(control: Optional[ft.Control]) -> bool:
        return bool(control is not None and getattr(control, "page", None) is not None)

    def _safe_update(self, control: Optional[ft.Control]):
        if self._mounted(control):
            control.update()

    # ---------------------------
    # Sorting / Ordering helpers
    # ---------------------------
    def _get_sort_mode(self) -> str:
        return getattr(self.state, "current_sort", "Custom")  # default to Custom

    def _set_sort_mode(self, mode: str):
        self.state.current_sort = mode

    def _ensure_custom_order(self, tasks: List[tuple]):
        """Ensure custom order list contains all task IDs (and only existing ones)."""
        ids = [t[0] for t in tasks]  # task_id at index 0
        current = [i for i in self._custom_order_ids if i in ids]
        missing = [i for i in ids if i not in current]
        self._custom_order_ids = current + missing

    def _sort_tasks(self, tasks: List[tuple]) -> List[tuple]:
        """Apply sort mode to tasks list."""
        mode = self._get_sort_mode()

        if mode == "Title (A-Z)":
            return sorted(tasks, key=lambda t: (t[1] or "").strip().lower())
        if mode == "Title (Z-A)":
            return sorted(tasks, key=lambda t: (t[1] or "").strip().lower(), reverse=True)

        if mode == "Due Date":

            def due_key(t):
                dt = self._safe_parse_datetime(t[4])  # due_date index 4
                return (dt is None, dt or datetime.max)

            return sorted(tasks, key=due_key)

        if mode == "Date Created":
            # created_at index 6 (string); parse if possible, otherwise keep stable
            def created_key(t):
                s = (t[6] or "").strip()
                try:
                    return datetime.fromisoformat(s.replace("Z", "+00:00"))
                except Exception:
                    return datetime.min

            return sorted(tasks, key=created_key, reverse=True)

        # Custom: use drag order
        self._ensure_custom_order(tasks)
        order_index = {tid: idx for idx, tid in enumerate(self._custom_order_ids)}
        return sorted(tasks, key=lambda t: order_index.get(t[0], 10**9))

    # ---------------------------
    # Data helpers
    # ---------------------------
    def _get_filtered_tasks(self) -> List[tuple]:
        S = self.state
        db = S.db

        if not S.user:
            return []

        tasks = db.get_tasks_by_user(S.user["id"])

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

        # apply sort
        tasks = self._sort_tasks(tasks)
        return tasks

    def _is_overdue(self, due_date_str: Optional[str], status: str) -> bool:
        if not due_date_str or (status or "").strip().lower() != "pending":
            return False
        dt = self._safe_parse_datetime(due_date_str)
        return bool(dt and dt < datetime.now())

    # ---------------------------
    # Refresh helpers (only update mounted controls)
    # ---------------------------
    def _refresh_task_list(self, page: ft.Page):
        if not self._mounted(self._task_list_host):
            return
        self._task_list_host.content = self._build_task_list(page)
        self._safe_update(self._task_list_host)

    def _refresh_analytics(self, page: ft.Page):
        if not self._mounted(self._analytics_host):
            return
        self._analytics_host.content = self._build_analytics_panel(page)
        self._safe_update(self._analytics_host)

    def _refresh_filter_ui(self, page: ft.Page):
        S = self.state
        current = getattr(S, "current_filter", "All Tasks")

        if self._mounted(self._filter_pill):
            self._filter_pill.content = ft.Text(current, size=11, color="white", weight=ft.FontWeight.W_600)
            self._safe_update(self._filter_pill)

        if self._mounted(self._filter_chip_row):
            self._filter_chip_row.content = self._build_filter_bar(page)
            self._safe_update(self._filter_chip_row)

    def _refresh_all(self, page: ft.Page):
        self._refresh_filter_ui(page)
        self._refresh_task_list(page)
        self._refresh_analytics(page)

    # ---------------------------
    # Search handler (no flicker)
    # ---------------------------
    def _on_search_change(self, e, page: ft.Page):
        self.search_query = e.control.value or ""
        self._refresh_task_list(page)

    # ---------------------------
    # View
    # ---------------------------
    def view(self, page: ft.Page) -> ft.Control:
        S = self.state
        db = S.db

        # Colors
        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        # Ensure DatePicker exists and is in overlay
        if not self._due_date_picker:
            self._due_date_picker = ft.DatePicker()
        if self._due_date_picker not in page.overlay:
            page.overlay.append(self._due_date_picker)

        # ✅ Ensure TimePicker exists and is in overlay
        if not self._due_time_picker:
            self._due_time_picker = ft.TimePicker()
        if self._due_time_picker not in page.overlay:
            page.overlay.append(self._due_time_picker)

        # ---------------------------
        # Navigation helpers
        # ---------------------------
        def go_calendar_today(e=None):
            today = datetime.now().date()
            S.selected_date = today
            S.cal_year = today.year
            S.cal_month = today.month
            S.go("calendarpage")

        def go_settings(e=None):
            S.go("settingspage")

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

        # ✅ FIX: add border_color option so we can force readable chips
        def small_tag(text: str, bgcolor: str, fg: str = "white", border_color: Optional[str] = None):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                border_radius=999,
                bgcolor=bgcolor,
                border=ft.border.all(1, border_color) if border_color else None,
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
        # Sort menu ("..." on category row)
        # ---------------------------
        def sort_menu_button():
            def set_sort(mode: str):
                def _h(e):
                    self._set_sort_mode(mode)
                    if mode == "Custom":
                        current_tasks = self._get_filtered_tasks()
                        self._ensure_custom_order(current_tasks)
                    self._refresh_task_list(page)

                return _h

            return ft.PopupMenuButton(
                icon=ft.Icons.MORE_HORIZ,
                icon_color=C("TEXT_PRIMARY"),
                tooltip="Sort / Options",
                items=[
                    ft.PopupMenuItem(text="Title (A-Z)", on_click=set_sort("Title (A-Z)")),
                    ft.PopupMenuItem(text="Title (Z-A)", on_click=set_sort("Title (Z-A)")),
                    ft.PopupMenuItem(text="Due Date", on_click=set_sort("Due Date")),
                    ft.PopupMenuItem(text="Date Created", on_click=set_sort("Date Created")),
                    ft.PopupMenuItem(text="Custom", on_click=set_sort("Custom")),
                ],
            )

        # ---------------------------
        # Delete confirm dialog
        # ---------------------------
        def confirm_delete(task_id: int):
            def close_dlg(e):
                dlg.open = False
                page.update()

            def do_delete(e):
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("No user logged in."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                db.delete_task(S.user["id"], task_id)
                self._custom_order_ids = [i for i in self._custom_order_ids if i != task_id]

                dlg.open = False
                page.update()

                page.snack_bar = ft.SnackBar(content=ft.Text("Task deleted!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

                self._refresh_all(page)

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Delete Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Text("Are you sure you want to delete this?", color=C("TEXT_SECONDARY")),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dlg),
                    ft.ElevatedButton("Delete", on_click=do_delete, bgcolor=C("ERROR_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

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
                value=self._fmt_date(S.selected_date) if S.selected_date else "",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            # ✅ Time field (12h)
            time_tf = ft.TextField(
                hint_text="Time (Pick From Clock)",
                read_only=True,
                value="",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def open_picker(e):
                initial = self._safe_parse_date(due_tf.value) or S.selected_date or datetime.now().date()
                self._due_date_picker.value = initial

                def on_change(ev):
                    picked = self._due_date_picker.value
                    if picked:
                        due_tf.value = self._fmt_date(picked)
                        S.selected_date = picked
                        S.cal_year = picked.year
                        S.cal_month = picked.month
                    else:
                        due_tf.value = ""
                    page.update()

                self._due_date_picker.on_change = on_change
                self._due_date_picker.open = True
                page.update()

            # ✅ Time picker open (set 12h AM/PM)
            def open_time_picker(e):
                def on_time_change(ev):
                    picked = self._due_time_picker.value
                    if picked:
                        time_tf.value = self._fmt_time_12h(picked.hour, picked.minute)
                    else:
                        time_tf.value = ""
                    page.update()

                self._due_time_picker.on_change = on_time_change
                self._due_time_picker.open = True
                page.update()

            def save_task(e):
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("No user logged in."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                title = (title_tf.value or "").strip()
                desc = (desc_tf.value or "").strip()
                cat = (category_dd.value or "").strip()

                due_date_part = (due_tf.value or "").strip()
                due_time_part = (time_tf.value or "").strip()

                due = due_date_part
                if due_date_part and due_time_part:
                    due = f"{due_date_part} {due_time_part}"

                if not title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Title is required."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                picked = self._safe_parse_date(due)
                if picked:
                    S.selected_date = picked
                    S.cal_year = picked.year
                    S.cal_month = picked.month

                db.add_task(S.user["id"], title, desc, cat, due)

                dialog.open = False
                page.update()

                page.snack_bar = ft.SnackBar(content=ft.Text("Task added!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

                if self._get_sort_mode() == "Custom":
                    current_tasks = self._get_filtered_tasks()
                    self._ensure_custom_order(current_tasks)

                self._refresh_all(page)

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
                                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_color=C("TEXT_PRIMARY"), on_click=open_picker),
                                ],
                                spacing=10,
                            ),
                            ft.Row(
                                [
                                    ft.Container(time_tf, expand=True),
                                    ft.IconButton(icon=ft.Icons.ACCESS_TIME, icon_color=C("TEXT_PRIMARY"), on_click=open_time_picker),
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
            (
                task_id,
                old_title,
                old_desc,
                old_category,
                old_due,
                old_status,
                old_created_at,
                old_updated_at,
            ) = task_row

            old_due_str = (old_due or "").strip()
            old_date_part = old_due_str
            old_time_part = ""

            if "T" in old_due_str:
                old_due_str = old_due_str.replace("T", " ")

            if " " in old_due_str:
                parts = old_due_str.split(" ")
                old_date_part = parts[0]
                old_time_part = " ".join(parts[1:]).strip()

            # normalize stored time to 12h for display
            old_time_part = self._normalize_time_str(old_time_part)

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
                value=(old_date_part or "").strip(),
                hint_text="Due Date (Pick From Calendar)",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            # ✅ Time field (12h)
            time_tf = ft.TextField(
                read_only=True,
                value=(old_time_part or "").strip(),
                hint_text="Time (Pick From Clock)",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def open_picker(e):
                initial = self._safe_parse_date(due_tf.value) or S.selected_date or datetime.now().date()
                self._due_date_picker.value = initial

                def on_change(ev):
                    picked = self._due_date_picker.value
                    if picked:
                        due_tf.value = self._fmt_date(picked)
                        S.selected_date = picked
                        S.cal_year = picked.year
                        S.cal_month = picked.month
                    else:
                        due_tf.value = ""
                    page.update()

                self._due_date_picker.on_change = on_change
                self._due_date_picker.open = True
                page.update()

            # ✅ Time picker open (set 12h AM/PM)
            def open_time_picker(e):
                def on_time_change(ev):
                    picked = self._due_time_picker.value
                    if picked:
                        time_tf.value = self._fmt_time_12h(picked.hour, picked.minute)
                    else:
                        time_tf.value = ""
                    page.update()

                self._due_time_picker.on_change = on_time_change
                self._due_time_picker.open = True
                page.update()

            def save_changes(e):
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("No user logged in."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                title = (title_tf.value or "").strip()
                desc = (desc_tf.value or "").strip()
                cat = (category_dd.value or "").strip()

                due_date_part = (due_tf.value or "").strip()
                due_time_part = (time_tf.value or "").strip()

                due = due_date_part
                if due_date_part and due_time_part:
                    due = f"{due_date_part} {due_time_part}"

                if not title:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Title cannot be empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                picked = self._safe_parse_date(due)
                if picked:
                    S.selected_date = picked
                    S.cal_year = picked.year
                    S.cal_month = picked.month

                db.update_task(S.user["id"], task_id, title, desc, cat, due, old_status)

                dialog.open = False
                page.update()

                page.snack_bar = ft.SnackBar(content=ft.Text("Task updated!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

                self._refresh_all(page)

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
                                    ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_color=C("TEXT_PRIMARY"), on_click=open_picker),
                                ],
                                spacing=10,
                            ),
                            ft.Row(
                                [
                                    ft.Container(time_tf, expand=True),
                                    ft.IconButton(icon=ft.Icons.ACCESS_TIME, icon_color=C("TEXT_PRIMARY"), on_click=open_time_picker),
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
        # Drag + drop reorder support
        # ---------------------------
        def _reorder_task(drag_task_id: int, target_task_id: int):
            if drag_task_id == target_task_id:
                return
            self._set_sort_mode("Custom")

            current_tasks = self._get_filtered_tasks()
            self._ensure_custom_order(current_tasks)

            ids = self._custom_order_ids[:]
            if drag_task_id not in ids or target_task_id not in ids:
                return

            ids.remove(drag_task_id)
            target_index = ids.index(target_task_id)
            ids.insert(target_index, drag_task_id)

            self._custom_order_ids = ids
            self._refresh_task_list(page)

        # ---------------------------
        # Task card
        # ---------------------------
        def build_task_card(t: tuple) -> ft.Control:
            task_id, title, desc, category, due_date, status, created_at, updated_at = t
            overdue = self._is_overdue(due_date, status)

            due_label = f"Due {due_date}" if (due_date or "").strip() else "No Due Date"
            cat_label = (category or "").strip() or "No Category"

            def toggle(e):
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("No user logged in."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return
                new_status = "completed" if status == "pending" else "pending"
                db.update_task_status(S.user["id"], task_id, new_status)
                self._refresh_all(page)

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
            if overdue:
                due_tag = small_tag(due_label, bgcolor=C("ERROR_COLOR"), fg="white")
            else:
                due_tag = small_tag(
                    due_label,
                    bgcolor="white",
                    fg=C("TEXT_PRIMARY"),
                    border_color=C("BORDER_COLOR"),
                )
            cat_tag = small_tag(cat_label, bgcolor=C("TEXT_PRIMARY"))

            drag_handle = ft.Draggable(
                group="task-reorder",
                data=str(task_id),
                content=ft.Icon(ft.Icons.DRAG_INDICATOR, color=C("TEXT_PRIMARY")),
                content_feedback=ft.Container(
                    padding=8,
                    bgcolor="#FFFFFF",
                    border_radius=10,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    content=ft.Row(
                        tight=True,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.DRAG_INDICATOR, color=C("TEXT_PRIMARY")),
                            ft.Text((title or "")[:24], size=12, color=C("TEXT_PRIMARY")),
                        ],
                    ),
                ),
            )

            card_body = ft.Container(
                bgcolor="#FFFFFF",
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
                                    ft.Row(spacing=8, controls=[cat_tag, due_tag, status_tag]),
                                ],
                            ),
                        ),
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    tooltip="Edit",
                                    icon_color=C("TEXT_PRIMARY"),
                                    on_click=lambda e: show_edit_task_dialog(t),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    tooltip="Delete",
                                    icon_color=C("ERROR_COLOR"),
                                    on_click=lambda e: confirm_delete(task_id),
                                ),
                                drag_handle,
                            ],
                        ),
                    ],
                ),
            )

            def on_hover(e: ft.HoverEvent):
                card_body.shadow = ft.BoxShadow(
                    blur_radius=18 if e.data == "true" else 10,
                    color="#00000018" if e.data == "true" else "#00000010",
                    offset=ft.Offset(0, 10 if e.data == "true" else 6),
                )
                if getattr(card_body, "page", None) is not None:
                    card_body.update()

            card_body.on_hover = on_hover

            def on_accept(e: ft.DragTargetEvent):
                try:
                    src = page.get_control(e.src_id)
                    drag_id = int(getattr(src, "data", "0"))
                except Exception:
                    return
                _reorder_task(drag_id, task_id)

            return ft.DragTarget(
                group="task-reorder",
                on_accept=on_accept,
                content=card_body,
            )

        # ---------------------------
        # Task list
        # ---------------------------
        def build_empty_tasks():
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

        def build_task_list_view(tasks: List[tuple]):
            if self._get_sort_mode() == "Custom":
                self._ensure_custom_order(tasks)

            controls = [build_task_card(t) for t in tasks]
            return ft.ListView(expand=True, spacing=10, controls=controls)

        self._build_task_list = lambda _page=page: (
            build_empty_tasks() if not self._get_filtered_tasks() else build_task_list_view(self._get_filtered_tasks())
        )

        # ---------------------------
        # Analytics panel
        # ---------------------------
        def build_analytics_panel():
            if not S.user:
                return ft.Container(
                    expand=True,
                    bgcolor=C("FORM_BG"),
                    border_radius=16,
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    padding=16,
                    content=ft.Text("No user logged in.", color=C("TEXT_SECONDARY")),
                )

            tasks = db.get_tasks_by_user(S.user["id"])
            total = len(tasks)

            completed = sum(1 for t in tasks if t[5] == "completed")
            now = datetime.now()
            overdue = sum(
                1
                for t in tasks
                if (t[5] == "pending" and self._safe_parse_datetime(t[4]) and self._safe_parse_datetime(t[4]) < now)
            )
            pending = total - completed
            progress = 0 if total == 0 else completed / total

            cat_counts = {c: 0 for c in CATEGORIES}
            for t in tasks:
                c = (t[3] or "").strip()
                if c in cat_counts:
                    cat_counts[c] += 1

            if total == 0:
                donut_content = ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.DONUT_LARGE_OUTLINED, size=42, color=C("TEXT_SECONDARY")),
                            ft.Text("No tasks yet.", size=13, color=C("TEXT_SECONDARY")),
                            ft.Text("Add a task to see the category mix.", size=12, color=C("TEXT_SECONDARY")),
                        ],
                    ),
                )
            else:
                self._chart_rotation = (self._chart_rotation + 18) % 360

                # ✅ FIX: use per-theme chart palette (fallback list if not defined)
                chart_palette = S.colors.get(
                    "CHART_COLORS",
                    ["#06B6D4", "#22C55E", "#F59E0B", "#EF4444", "#A855F7"],
                )

                pie_sections = []
                color_i = 0
                for label, val in cat_counts.items():
                    if val <= 0:
                        continue
                    pct = (val / total) * 100
                    pie_sections.append(
                        ft.PieChartSection(
                            value=val,
                            title=f"{label} {pct:.0f}%",
                            radius=62,
                            color=chart_palette[color_i % len(chart_palette)],
                            title_style=ft.TextStyle(size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        )
                    )
                    color_i += 1

                donut = ft.PieChart(
                    sections=pie_sections,
                    center_space_radius=44,
                    expand=True,
                    start_degree_offset=self._chart_rotation,
                )

                legend_rows = []
                for label, val in cat_counts.items():
                    if val <= 0:
                        continue
                    pct = (val / total) * 100
                    legend_rows.append(
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(label, size=12, color=C("TEXT_PRIMARY")),
                                ft.Text(f"{pct:.0f}%", size=12, color=C("TEXT_SECONDARY")),
                            ],
                        )
                    )

                donut_content = ft.Column(
                    expand=True,
                    spacing=10,
                    controls=[
                        ft.Container(expand=True, content=donut),
                        ft.Container(padding=ft.padding.only(top=4), content=ft.Column(spacing=4, controls=legend_rows)),
                    ],
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
                        donut_content,
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
                        # ✅ FIX: color should be a real color, not C("#147272")
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
                                    color=ft.Colors.BLACK,
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    "Open Settings",
                                    on_click=lambda e: go_settings(),
                                    bgcolor=C("BUTTON_COLOR"),
                                    color=ft.Colors.BLACK,
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                ),
            )

            return ft.Column(expand=True, spacing=14, controls=[donut_card, summary])

        self._build_analytics_panel = lambda _page=page: build_analytics_panel()

        # ---------------------------
        # Filter bar
        # ---------------------------
        def set_filter(label: str):
            def f(e):
                S.current_filter = label
                self._refresh_all(page)

            return f

        def build_filter_bar():
            current = getattr(S, "current_filter", "All Tasks")
            chips = [chip("All Tasks", current == "All Tasks", set_filter("All Tasks"))]
            for c in CATEGORIES:
                chips.append(chip(c, current == c, set_filter(c)))

            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.ListView(horizontal=True, spacing=10, controls=chips),
                    ),
                    sort_menu_button(),
                ],
            )

        self._build_filter_bar = lambda _page=page: build_filter_bar()

        # ---------------------------
        # Search TextField
        # ---------------------------
        if not self._search_tf:
            self._search_tf = ft.TextField(
                hint_text="Search tasks...",
                prefix_icon=ft.Icons.SEARCH,
                bgcolor="white",
                filled=True,
                border_radius=14,
                border_color=C("BORDER_COLOR"),
                color=C("TEXT_PRIMARY"),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
                on_change=lambda e: self._on_search_change(e, page),
            )

        # ---------------------------
        # Hosts
        # ---------------------------
        current_filter_label = getattr(S, "current_filter", "All Tasks")

        self._filter_pill = ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            border_radius=999,
            bgcolor=C("TEXT_PRIMARY"),
            content=ft.Text(current_filter_label, size=11, color="white", weight=ft.FontWeight.W_600),
        )

        self._filter_chip_row = ft.Container(height=48, content=self._build_filter_bar(page))
        self._task_list_host = ft.Container(expand=True, padding=ft.padding.only(top=6), content=self._build_task_list(page))
        self._analytics_host = ft.Container(expand=True, content=self._build_analytics_panel(page))

        # ---------------------------
        # Panels
        # ---------------------------
        left_panel = ft.Container(
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
                            self._filter_pill,
                        ],
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(expand=True, content=self._search_tf),
                            ft.IconButton(
                                icon=ft.Icons.CALENDAR_MONTH,
                                icon_color=C("TEXT_PRIMARY"),
                                tooltip="Open Calendar",
                                on_click=go_calendar_today,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.SETTINGS,
                                icon_color=C("TEXT_PRIMARY"),
                                tooltip="Open Settings",
                                on_click=go_settings,
                            ),
                        ],
                    ),
                    self._filter_chip_row,
                    self._task_list_host,
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

        right_panel = ft.Container(
            expand=True,
            padding=20,
            bgcolor=C("BG_COLOR"),
            content=self._analytics_host,
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
