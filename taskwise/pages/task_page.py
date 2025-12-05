# taskwise/pages/task_page.py
import flet as ft
from datetime import datetime, date
from typing import Optional, Callable, List

# TaskPage: migrated exactly from your original setings.py (Option 1)
# Part 1: imports, class, state setup, helpers, header, auth/account dialogs

class TaskPage:
    def __init__(self, state):
        """
        state: taskwise.app_state.AppState
        Expect state to expose:
          - db : Database instance with methods used in original file
          - colors : dict of theme colors (keys used: BG_COLOR, FORM_BG, BUTTON_COLOR, HEADER_BG, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR, ERROR_COLOR, SUCCESS_COLOR)
          - theme_name, set_theme(), go(view_name), selected_date, cal_year, cal_month, holidays_cache, user, current_view, current_filter, set_update_callback / _update_callback
        """
        self.state = state

    def view(self, page: ft.Page):
        """
        Returns an ft.Control representing the Tasks page.
        This method contains references to helper functions defined below.
        The page object is used for overlays (dialogs, datepicker), snackbars and updating.
        """
        S = self.state
        db = S.db

        # Color lookup
        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        # ---------------------------
        # Date / Calendar helpers
        # ---------------------------
        def _fmt_date(d: date) -> str:
            return d.strftime("%Y-%m-%d")

        def _safe_parse_date(s: Optional[str]) -> Optional[date]:
            try:
                if not s:
                    return None
                return datetime.strptime(s.strip(), "%Y-%m-%d").date()
            except Exception:
                return None

        def _month_name(m: int) -> str:
            return ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][m - 1]

        def _weekday_sun0(d: date) -> int:
            # return weekday with Sunday = 0
            return (d.weekday() + 1) % 7

        def _days_in_month(y: int, m: int) -> int:
            if m == 12:
                return 31
            return (date(y, m + 1, 1) - date(y, m, 1)).days

        def _calendar_tasks_for_date(d: date) -> List[tuple]:
            ds = _fmt_date(d)
            rows = []
            for t in db.get_all_tasks():
                # db.get_all_tasks returns tuples: (id, title, description, category, due_date, status, created_at)
                _, title, desc, category, due_date, status, _ = t
                if (due_date or "").strip() == ds:
                    rows.append((title, status, category))
            return rows

        def _build_due_date_set_for_month(y: int, m: int) -> set:
            out = set()
            for t in db.get_all_tasks():
                due = (t[4] or "").strip()
                dd = _safe_parse_date(due)
                if dd and dd.year == y and dd.month == m:
                    out.add(_fmt_date(dd))
            return out

        # ---------------------------
        # Shared DatePicker (used for editing/adding tasks)
        # ---------------------------
        # Keep a single DatePicker instance so dialogs reuse it.
        due_date_picker = ft.DatePicker()
        if due_date_picker not in page.overlay:
            page.overlay.append(due_date_picker)

        # ---------------------------
        # Category dropdown helper
        # ---------------------------
        # Use categories from state (if present) or fallback list
        FALLBACK_CATEGORIES = ["Personal", "Work", "Study", "Bills", "Others"]
        CATEGORIES = getattr(S, "categories", FALLBACK_CATEGORIES)

        def category_dropdown(selected_value: Optional[str] = None) -> ft.Dropdown:
            value = selected_value if selected_value in CATEGORIES else None
            return ft.Dropdown(
                value=value,
                hint_text="Select Category",
                border_color=C("BORDER_COLOR"),
                bgcolor=C("BG_COLOR"),
                filled=True,
                color=C("TEXT_PRIMARY"),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                options=[ft.dropdown.Option(c) for c in CATEGORIES],
            )

        # ---------------------------
        # Authentication / Account helpers (Login/Create/Change PW)
        # These create dialogs appended to page.overlay when used.
        # ---------------------------
        def _hash_pw_raw(s: str) -> str:
            # lightweight hash wrapper to mirror original behavior
            # original used hashlib - replicate same deterministic function
            import hashlib
            return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

        # Expose a wrapper on state to reuse in settings_page if needed
        if not hasattr(S, "_hash_pw"):
            S._hash_pw = _hash_pw_raw

        def show_login_dialog():
            email_tf = ft.TextField(
                hint_text="Email",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            pw_tf = ft.TextField(
                hint_text="Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def do_login(e):
                email = (email_tf.value or "").strip().lower()
                pw = pw_tf.value or ""
                row = db.get_user_by_email(email)
                if not row:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account not found."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user_id, name, em, pw_hash = row
                if S._hash_pw(pw) != pw_hash:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Wrong password."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                S.user = {"id": user_id, "name": name, "email": em}
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Logged in as {name}"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                # trigger a render through state callback if present
                if hasattr(S, "_update_callback") and S._update_callback:
                    S._update_callback()
                page.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Login", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=420, content=ft.Column([email_tf, pw_tf], spacing=12, tight=True)),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Login", on_click=do_login, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def show_create_account_dialog():
            name_tf = ft.TextField(
                hint_text="Name",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            email_tf = ft.TextField(
                hint_text="Email",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            pw_tf = ft.TextField(
                hint_text="Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def do_create(e):
                name = (name_tf.value or "").strip()
                email = (email_tf.value or "").strip().lower()
                pw = pw_tf.value or ""
                if not (name and email and pw):
                    page.snack_bar = ft.SnackBar(content=ft.Text("All fields required."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                existing = db.get_user_by_email(email)
                if existing:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Email already taken."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                db.create_user(name, email, S._hash_pw(pw))
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Account created!"), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Create Account", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=420, content=ft.Column([name_tf, email_tf, pw_tf], spacing=12, tight=True)),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Create", on_click=do_create, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def show_change_password_dialog():
            current_tf = ft.TextField(
                hint_text="Current Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            new_tf = ft.TextField(
                hint_text="New Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            new2_tf = ft.TextField(
                hint_text="Confirm Password",
                password=True,
                can_reveal_password=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )

            def do_change(e):
                if not S.user:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Not signed in."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                row = db.get_user_by_email(S.user["email"])
                if not row:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Account error."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                user_id, name, em, pw_hash = row
                if S._hash_pw(current_tf.value or "") != pw_hash:
                    page.snack_bar = ft.SnackBar(content=ft.Text("Current password is wrong."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if (new_tf.value or "") != (new2_tf.value or ""):
                    page.snack_bar = ft.SnackBar(content=ft.Text("New passwords do not match."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                if not (new_tf.value or "").strip():
                    page.snack_bar = ft.SnackBar(content=ft.Text("New password is empty."), bgcolor=C("ERROR_COLOR"))
                    page.snack_bar.open = True
                    page.update()
                    return

                db.change_password(user_id, S._hash_pw(new_tf.value))
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Password updated."), bgcolor=C("SUCCESS_COLOR"))
                page.snack_bar.open = True
                page.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Change Password", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(width=420, content=ft.Column([current_tf, new_tf, new2_tf], spacing=12, tight=True)),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Update", on_click=do_change, bgcolor=C("BUTTON_COLOR"), color=ft.Colors.WHITE),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        # ---------------------------
        # Account popup button used in header
        # ---------------------------
        def account_menu_button():
            if not S.user:
                return ft.PopupMenuButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    icon_color=C("TEXT_PRIMARY"),
                    items=[
                        ft.PopupMenuItem(text="Login", on_click=lambda e: show_login_dialog()),
                        ft.PopupMenuItem(text="Create Account", on_click=lambda e: show_create_account_dialog()),
                    ],
                )
            return ft.PopupMenuButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_color=C("TEXT_PRIMARY"),
                items=[
                    ft.PopupMenuItem(text=f"Signed in: {S.user.get('name','')}"),
                    ft.PopupMenuItem(text="Logout", on_click=lambda e: do_logout()),
                ],
            )

        def do_logout():
            S.user = None
            page.snack_bar = ft.SnackBar(content=ft.Text("Logged out."), bgcolor=C("SUCCESS_COLOR"))
            page.snack_bar.open = True
            if hasattr(S, "_update_callback") and S._update_callback:
                S._update_callback()
            page.update()

        # ---------------------------
        # Header builder
        # ---------------------------
        def create_header():
            def navigate(view_name: str) -> Callable:
                def handler(e):
                    S.go(view_name)
                return handler

            def tab(label: str, view: str):
                is_active = (S.current_view == view)
                text = f"✱ {label} ✱" if is_active else label
                return ft.TextButton(text, on_click=navigate(view), style=ft.ButtonStyle(color=C("TEXT_PRIMARY")))

            return ft.Container(
                content=ft.Row(
                    [
                        ft.Text("TaskWise", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                        ft.Row([tab("Tasks", "tasks"), tab("Calendar", "calendar"), tab("Settings", "settings")], spacing=8),
                        account_menu_button(),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                bgcolor=C("HEADER_BG"),
                border=ft.border.only(bottom=ft.BorderSide(1, C("BORDER_COLOR"))),
            )

        # ---------------------------
        # End of Part 1
        # Next: Part 2 will include create_task_list(), toggles, delete/edit handlers and building of left panel
        # ---------------------------

        # Return a wrapper container for now; the next parts will overwrite its content in update/render.
        wrapper = ft.Container(expand=True)
        # Save references onto self for use in other parts (when merged)
        self._page = page
        self._wrapper = wrapper
        self._create_header = create_header
        self._category_dropdown = category_dropdown
        self._due_date_picker = due_date_picker
        self._helpers = {
            "fmt_date": _fmt_date,
            "safe_parse": _safe_parse_date,
            "build_due_set": _build_due_date_set_for_month,
            "calendar_tasks_for_date": _calendar_tasks_for_date,
            "days_in_month": _days_in_month,
            "weekday_sun0": _weekday_sun0,
        }
        
        # --- Part 2: Task list UI (create_task_list + left panel) ---

        # retrieve stored refs
        page = self._page
        wrapper = self._wrapper
        create_header = self._create_header
        category_dropdown = self._category_dropdown
        due_date_picker = self._due_date_picker
        helpers = self._helpers

        # ---------------------------
        # create_task_list() - builds the vertical list of task cards
        # ---------------------------
        def create_task_list():
            tasks = db.get_all_tasks()
            # db.get_all_tasks returns list of tuples:
            # (id, title, description, category, due_date, status, created_at)

            # Apply filter
            current_filter = getattr(S, "current_filter", "All Tasks")
            if current_filter != "All Tasks":
                wanted = current_filter.lower().strip()
                tasks = [t for t in tasks if (t[3] or "").strip().lower() == wanted]

            if not tasks:
                return ft.Container(
                    content=ft.Text("No tasks found in this category.", size=14, color=C("TEXT_SECONDARY")),
                    alignment=ft.alignment.center,
                    padding=20,
                )

            def is_overdue(due_date_str, status):
                if not due_date_str or status != "pending":
                    return False
                dd = helpers["safe_parse"](due_date_str)
                return bool(dd and dd < datetime.now().date())

            items = []
            for t in tasks:
                task_id, title, desc, category, due_date, status, created_at = t
                overdue = is_overdue(due_date, status)
                row_bg = C("FORM_BG") if not overdue else ft.Colors.with_opacity(0.10, ft.Colors.RED)

                # Toggle completion
                def toggle_status(task_id, current_status):
                    def handler(e):
                        new_status = "completed" if current_status == "pending" else "pending"
                        db.update_task_status(task_id, new_status)
                        # request a re-render
                        if hasattr(S, "_update_callback") and S._update_callback:
                            S._update_callback()
                    return handler

                # Delete handler
                def delete_handler(task_id):
                    def handler(e):
                        db.delete_task(task_id)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Task deleted!"), bgcolor=C("SUCCESS_COLOR"))
                        page.snack_bar.open = True
                        if hasattr(S, "_update_callback") and S._update_callback:
                            S._update_callback()
                    return handler

                # Edit handler — correctly calls the dialog stored on self
                def edit_handler(task_id, t, d, c, due):
                    def handler(e):
                        self._show_edit_task_dialog(task_id, t, d, c, due)
                    return handler

                due_label = f"Due: {due_date}" if (due_date or "").strip() else "No due date"
                cat_label = (category or "").strip() or "No category"

                card = ft.Container(
                    content=ft.Row(
                        [
                            ft.Checkbox(value=(status == "completed"), on_change=toggle_status(task_id, status)),
                            ft.Column(
                                [
                                    ft.Text(
                                        title,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=C("TEXT_PRIMARY") if status == "pending" else C("TEXT_SECONDARY"),
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(due_label, size=11, color=C("TEXT_SECONDARY")),
                                            ft.Container(width=12),
                                            ft.Text(f"Category: {cat_label}", size=11, color=C("TEXT_SECONDARY")),
                                        ],
                                        spacing=0,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_HORIZ,
                                icon_color=C("TEXT_SECONDARY"),
                                items=[
                                    ft.PopupMenuItem(text="Edit", on_click=edit_handler(task_id, title, desc, category, due_date)),
                                    ft.PopupMenuItem(text="Delete", on_click=delete_handler(task_id)),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=row_bg,
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    border=ft.border.all(1, C("BORDER_COLOR")),
                )
                items.append(card)

            return ft.Column(items, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # ---------------------------
        # Analytics panel placeholder (detailed in Part 3)
        # create_analytics_panel() will be defined in Part 3
        # ---------------------------

        # ---------------------------
        # Left panel builder (includes filters, the list, and add button)
        # ---------------------------
        def build_left_panel():
            # pill filter buttons
            def pill(label):
                active = getattr(S, "current_filter", "All Tasks") == label

                return ft.Container(
                    content=ft.Text(label, color=C("TEXT_PRIMARY")),
                    padding=ft.padding.symmetric(horizontal=18, vertical=8),
                    border_radius=20,
                    bgcolor=C("BUTTON_COLOR") if active else C("BG_COLOR"),
                    border=ft.border.all(1, C("BORDER_COLOR")),
                    on_click=lambda e: set_filter(label),
                )

            def set_filter(label):
                S.current_filter = label
                if S._update_callback:
                    S._update_callback()

            return ft.Container(
                expand=True,
                padding=20,
                border_radius=16,
                border=ft.border.all(1, C("BORDER_COLOR")),
                bgcolor=C("FORM_BG"),
                content=ft.Column(
                    [
                        ft.Text("Tasks", size=20, weight="bold", color=C("TEXT_PRIMARY")),
                        ft.Container(height=10),
                        ft.Row(
                            [pill("All Tasks")] + [pill(c) for c in CATEGORIES],
                            spacing=10,
                            wrap=True,
                        ),
                        ft.Container(height=20),
                        ft.Container(content=create_task_list(), expand=True),
                        ft.Container(height=20),
                        ft.Row(
                            [
                                ft.FloatingActionButton(
                                    icon=ft.Icons.ADD,
                                    bgcolor=C("BUTTON_COLOR"),
                                    foreground_color="white",
                                    on_click=lambda e: self._show_add_task_dialog(),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    expand=True,
                ),
            )
            return left_panel

        # store builders onto self so Part3/Part4 can use them
        self._create_task_list = create_task_list
        self._build_left_panel = build_left_panel

        # populate wrapper with a minimal layout now; Part 3 & 4 will replace with full layout
        header = create_header()
        placeholder_body = ft.Container(content=ft.Text("Loading tasks..."), padding=24, expand=True)
        wrapper.content = ft.Column([header, placeholder_body], expand=True)
        # ensure page bgcolor
        page.bgcolor = C("BG_COLOR")
        page.update()
        
# --- Part 3: Analytics Panel + Right Panel ---

        # Retrieve helpers
        create_task_list = self._create_task_list
        build_left_panel = self._build_left_panel
        fmt_date = helpers["fmt_date"]
        safe_parse = helpers["safe_parse"]
        build_due_set = helpers["build_due_set"]
        calendar_tasks_for_date = helpers["calendar_tasks_for_date"]
        days_in_month = helpers["days_in_month"]
        weekday_sun0 = helpers["weekday_sun0"]

        # ------------------------------------------------------------
        # ANALYTICS PANEL (Right Side)
        # ------------------------------------------------------------
        def create_analytics_panel():
            tasks = db.get_all_tasks()

            # Count categories
            categories = ["Personal", "Work", "Study", "Bills", "Others"]
            cat_counts = {c: 0 for c in categories}

            for t in tasks:
                cat = (t[3] or "").strip()
                if cat in cat_counts:
                    cat_counts[cat] += 1

            # Donut chart values
            values = list(cat_counts.values())
            labels = list(cat_counts.keys())

            donut = ft.PieChart(
                sections=[
                    ft.PieChartSection(
                        value=values[i] if values[i] > 0 else 1,      # Avoid invisible slices
                        title=labels[i],
                        radius=min(page.width, page.height) * 0.06,
                        title_style=ft.TextStyle(size=12, color="white"),
                    )
                    for i in range(len(labels))
                ],
                center_space_radius=40,
                expand=True,
            )

            # Count Completed & Overdue
            completed = sum(1 for t in tasks if t[5] == "completed")
            today = datetime.now().date()
            overdue = sum(
                1 for t in tasks
                if t[5] == "pending" and helpers["safe_parse"](t[4]) and helpers["safe_parse"](t[4]) < today
            )

            summary_card = ft.Container(
                bgcolor=C("FORM_BG"),
                padding=18,
                border_radius=12,
                border=ft.border.all(1, C("BORDER_COLOR")),
                content=ft.Column(
                    [
                        ft.Text(f"{completed} tasks completed", weight="bold", size=14),
                        ft.Text(f"• {overdue} tasks overdue", size=11, color=C("TEXT_SECONDARY")),
                    ],
                    spacing=4,
                )
            )

            return ft.Column(
                [
                    ft.Container(
                        bgcolor=C("FORM_BG"),
                        padding=20,
                        border_radius=16,
                        border=ft.border.all(1, C("BORDER_COLOR")),
                        content=donut,
                        expand=True,
                    ),
                    ft.Container(height=20),
                    summary_card
                ],
                expand=True
            )

        # ------------------------------------------------------------
        # RIGHT PANEL WRAPPER
        # ------------------------------------------------------------
        def build_right_panel():
            return ft.Container(
                expand=True,
                padding=20,
                content=create_analytics_panel(),
            )

        self._build_right_panel = build_right_panel

        # ------------------------------------------------------------
        # After building both side panels, compose the full layout
        # (BUT the actual dialogs are still missing — added in Part 4)
        # ------------------------------------------------------------
        header = create_header()

        def update_page():
            # Build left + right panels together
            left_panel = build_left_panel()
            right_panel = build_right_panel()

            body = ft.Row(
                [
                    ft.Container(content=left_panel, expand=6),
                    ft.VerticalDivider(width=1, color=C("BORDER_COLOR")),
                    ft.Container(content=right_panel, expand=4),
                ],
                expand=True,
            )

            wrapper.content = ft.Column(
                [
                    header,
                    ft.Container(
                        bgcolor=C("BG_COLOR"),
                        padding=24,
                        expand=True,
                        content=body,
                    )
                ],
                spacing=0,
                expand=True,
            )

            page.bgcolor = C("BG_COLOR")
            page.update()

        # register update callback for TaskWiseApp (state)
        S._update_callback = update_page

        # initial render
        update_page()
        
# --- Part 4: Add Task Dialog + Edit Task Dialog ---

        # ------------------------------------------------------------
        # ADD TASK DIALOG
        # ------------------------------------------------------------
        def show_add_task_dialog():
            title_tf = ft.TextField(
                label="Title",
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            desc_tf = ft.TextField(
                label="Description",
                multiline=True,
                min_lines=3,
                max_lines=5,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            category_dd = category_dropdown()
            due_tf = ft.TextField(
                label="Due Date",
                read_only=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
                suffix=ft.IconButton(
                    icon=ft.Icons.CALENDAR_MONTH,
                    icon_color=C("TEXT_SECONDARY"),
                    on_click=lambda e: due_date_picker.pick_date(),
                ),
            )

            # When the user picks a date from the picker
            def on_date_change(e):
                due_tf.value = fmt_date(due_date_picker.value) if due_date_picker.value else ""
                page.update()

            due_date_picker.on_change = on_date_change

            # Save handler
            def save_task(e):
                title = (title_tf.value or "").strip()
                desc = (desc_tf.value or "").strip()
                cat = category_dd.value or ""
                due = (due_tf.value or "").strip()

                if not title:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Title is required."),
                        bgcolor=C("ERROR_COLOR"),
                    )
                    page.snack_bar.open = True
                    page.update()
                    return

                db.add_task(title, desc, cat, due)
                dialog.open = False

                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Task added!"),
                    bgcolor=C("SUCCESS_COLOR"),
                )
                page.snack_bar.open = True

                if S._update_callback:
                    S._update_callback()

                page.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Add Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=420,
                    content=ft.Column(
                        [
                            title_tf,
                            desc_tf,
                            category_dd,
                            due_tf,
                        ],
                        spacing=12,
                        tight=True,
                    ),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton(
                        "Save",
                        on_click=save_task,
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

        # ------------------------------------------------------------
        # EDIT TASK DIALOG
        # ------------------------------------------------------------
        def show_edit_task_dialog(task_id, old_title, old_desc, old_category, old_due):
            title_tf = ft.TextField(
                label="Title",
                value=old_title,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            desc_tf = ft.TextField(
                label="Description",
                value=old_desc,
                multiline=True,
                min_lines=3,
                max_lines=5,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
            )
            category_dd = category_dropdown(old_category)
            due_tf = ft.TextField(
                label="Due Date",
                value=old_due,
                read_only=True,
                bgcolor=C("BG_COLOR"),
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
                suffix=ft.IconButton(
                    icon=ft.Icons.CALENDAR_MONTH,
                    icon_color=C("TEXT_SECONDARY"),
                    on_click=lambda e: due_date_picker.pick_date(),
                ),
            )

            def on_date_change(e):
                due_tf.value = fmt_date(due_date_picker.value) if due_date_picker.value else ""
                page.update()

            due_date_picker.on_change = on_date_change

            # SAVE CHANGES
            def save_changes(e):
                title = (title_tf.value or "").strip()
                desc = (desc_tf.value or "").strip()
                cat = category_dd.value or ""
                due = (due_tf.value or "").strip()

                if not title:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Title cannot be empty."),
                        bgcolor=C("ERROR_COLOR"),
                    )
                    page.snack_bar.open = True
                    page.update()
                    return

                db.update_task(task_id, title, desc, cat, due)
                dialog.open = False

                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Task updated!"),
                    bgcolor=C("SUCCESS_COLOR"),
                )
                page.snack_bar.open = True

                if S._update_callback:
                    S._update_callback()

                page.update()

            def close(e):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Edit Task", size=18, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Container(
                    width=420,
                    content=ft.Column(
                        [
                            title_tf,
                            desc_tf,
                            category_dd,
                            due_tf,
                        ],
                        spacing=12,
                        tight=True,
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

        # ------------------------------------------------------------
        # Expose dialog functions to outer scope (so Part 2 can call them)
        # ------------------------------------------------------------
        self._show_add_task_dialog = show_add_task_dialog
        self._show_edit_task_dialog = show_edit_task_dialog

        return wrapper
