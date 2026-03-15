import flet as ft
from datetime import datetime
from typing import Optional, List


# Mood options: label + emoji + color
MOODS = [
    ("Happy",     "😊", "#22C55E"),
    ("Calm",      "😌", "#06B6D4"),
    ("Neutral",   "😐", "#94A3B8"),
    ("Sad",       "😢", "#3B82F6"),
    ("Anxious",   "😰", "#F59E0B"),
    ("Angry",     "😠", "#EF4444"),
]

MOOD_LABELS  = [m[0] for m in MOODS]
MOOD_EMOJI   = {m[0]: m[1] for m in MOODS}
MOOD_COLOR   = {m[0]: m[2] for m in MOODS}


class JournalPage:
    """
    Journal page — left panel: entry list + search + new entry button.
                 — right panel: full editor (title, mood, content) with
                                auto-save on Save, delete confirm dialog.
    Follows the same no-flicker host pattern as TaskPage.
    """

    def __init__(self, state):
        self.state = state

        self._search_query: str = ""
        self._selected_id: Optional[int] = None  # which entry is open in editor

        # Stateful hosts (created once, content swapped)
        self._list_host:   Optional[ft.Container] = None
        self._editor_host: Optional[ft.Container] = None
        self._search_tf:   Optional[ft.TextField] = None

        # Loading guard
        self._is_loading: bool = False

        # Builder refs (set inside view())
        self._build_list   = None
        self._build_editor = None

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    @staticmethod
    def _mounted(ctrl) -> bool:
        return bool(ctrl is not None and getattr(ctrl, "page", None) is not None)

    def _safe_update(self, ctrl):
        if self._mounted(ctrl):
            ctrl.update()

    def _snack(self, page: ft.Page, text: str, color: str):
        page.snack_bar = ft.SnackBar(content=ft.Text(text), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    @staticmethod
    def _fmt_dt(s: str) -> str:
        """Pretty-print a stored timestamp."""
        try:
            dt = datetime.fromisoformat((s or "").strip().replace("Z", ""))
            return dt.strftime("%b %d, %Y  %I:%M %p")
        except Exception:
            return (s or "").strip()

    def _get_entries(self) -> List[tuple]:
        S = self.state
        if not S.user:
            return []
        entries = S.db.get_journals_by_user(S.user["id"])
        q = self._search_query.strip().lower()
        if q:
            entries = [
                e for e in entries
                if q in (e[1] or "").lower() or q in (e[2] or "").lower()
            ]
        return entries

    # --------------------------------------------------
    # Refresh helpers
    # --------------------------------------------------
    def _refresh_list(self, page: ft.Page):
        if self._list_host and self._build_list:
            self._list_host.content = self._build_list(page)
            self._safe_update(self._list_host)

    def _refresh_editor(self, page: ft.Page):
        if self._editor_host and self._build_editor:
            self._editor_host.content = self._build_editor(page)
            self._safe_update(self._editor_host)

    def _refresh_all(self, page: ft.Page):
        self._refresh_list(page)
        self._refresh_editor(page)

    # --------------------------------------------------
    # View
    # --------------------------------------------------
    def view(self, page: ft.Page) -> ft.Control:
        S  = self.state
        db = S.db

        def C(k: str) -> str:
            return S.colors.get(k, "#000000")

        CARD_BG  = S.colors.get("CARD_BG",  S.colors.get("FORM_BG", "#FFFFFF"))
        INPUT_BG = S.colors.get("INPUT_BG",  S.colors.get("BG_COLOR", "#FFFFFF"))

        # --------------------------------------------------
        # Small UI atoms
        # --------------------------------------------------
        def mood_badge(mood_label: str) -> ft.Control:
            if not mood_label or mood_label not in MOOD_EMOJI:
                return ft.Container()
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                border_radius=999,
                bgcolor=MOOD_COLOR.get(mood_label, C("BUTTON_COLOR")),
                content=ft.Text(
                    f"{MOOD_EMOJI[mood_label]}  {mood_label}",
                    size=11,
                    color="white",
                    weight=ft.FontWeight.W_600,
                ),
            )

        # --------------------------------------------------
        # Delete confirm
        # --------------------------------------------------
        def confirm_delete(journal_id: int):
            def close(e):
                dlg.open = False
                page.update()

            def do_delete(e):
                if not S.user:
                    return
                db.delete_journal(S.user["id"], journal_id)
                dlg.open = False
                page.update()
                # If the deleted entry was open, clear the editor
                if self._selected_id == journal_id:
                    self._selected_id = None
                self._snack(page, "Entry deleted.", C("SUCCESS_COLOR"))
                self._refresh_all(page)

            dlg = ft.AlertDialog(
                modal=True,
                bgcolor=C("FORM_BG"),
                title=ft.Text("Delete Entry", size=17, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                content=ft.Text("Are you sure you want to delete this journal entry?", color=C("TEXT_SECONDARY")),
                actions=[
                    ft.TextButton("Cancel", on_click=close),
                    ft.ElevatedButton("Delete", on_click=do_delete, bgcolor=C("ERROR_COLOR"), color="white"),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        # --------------------------------------------------
        # Entry list (left panel body)
        # --------------------------------------------------
        def build_entry_list(_page: ft.Page) -> ft.Control:
            entries = self._get_entries()

            if not entries:
                return ft.Container(
                    alignment=ft.alignment.center,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.BOOK_OUTLINED, size=44, color=C("TEXT_SECONDARY")),
                            ft.Text("No journal entries yet.", size=13, color=C("TEXT_SECONDARY")),
                            ft.Text("Hit ✦ New Entry to start writing.", size=12, color=C("TEXT_SECONDARY")),
                        ],
                    ),
                )

            cards = []
            for e in entries:
                # tuple: (id, title, content, mood, created_at, updated_at)
                eid, title, content, mood, created_at, updated_at = e
                is_selected = (eid == self._selected_id)

                preview = (content or "").strip().replace("\n", " ")
                preview = preview[:80] + "…" if len(preview) > 80 else preview

                def on_select(ev, _id=eid):
                    self._selected_id = _id
                    self._refresh_list(page)
                    self._refresh_editor(page)

                def on_delete(ev, _id=eid):
                    confirm_delete(_id)

                card = ft.Container(
                    border_radius=14,
                    bgcolor=C("BUTTON_COLOR") if is_selected else CARD_BG,
                    border=ft.border.all(
                        2 if is_selected else 1,
                        C("BUTTON_COLOR") if is_selected else C("BORDER_COLOR"),
                    ),
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    ink=True,
                    on_click=on_select,
                    shadow=ft.BoxShadow(blur_radius=8, color="#00000010", offset=ft.Offset(0, 4)),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text(
                                            title or "Untitled",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color="white" if is_selected else C("TEXT_PRIMARY"),
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Text(
                                            preview or "No content",
                                            size=11,
                                            color="white" if is_selected else C("TEXT_SECONDARY"),
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                mood_badge(mood) if not is_selected else ft.Container(),
                                                ft.Text(
                                                    self._fmt_dt(updated_at or created_at),
                                                    size=10,
                                                    color="white" if is_selected else C("TEXT_SECONDARY"),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                icon_color="white" if is_selected else C("ERROR_COLOR"),
                                tooltip="Delete",
                                on_click=on_delete,
                            ),
                        ],
                    ),
                )
                cards.append(card)

            return ft.ListView(expand=True, spacing=10, controls=cards)

        self._build_list = build_entry_list

        # --------------------------------------------------
        # Editor (right panel body)
        # --------------------------------------------------
        def build_editor(_page: ft.Page) -> ft.Control:
            # No entry selected
            if self._selected_id is None:
                return ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.EDIT_NOTE, size=52, color=C("TEXT_SECONDARY")),
                            ft.Text("Select an entry to read or edit it,", size=14, color=C("TEXT_SECONDARY")),
                            ft.Text("or create a new one with ✦ New Entry.", size=12, color=C("TEXT_SECONDARY")),
                        ],
                    ),
                )

            # Fetch the selected entry
            if not S.user:
                return ft.Text("Not logged in.", color=C("ERROR_COLOR"))

            entries = db.get_journals_by_user(S.user["id"])
            entry = next((e for e in entries if e[0] == self._selected_id), None)

            if not entry:
                # Entry was deleted externally — clear selection
                self._selected_id = None
                return ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Text("Entry not found.", color=C("TEXT_SECONDARY")),
                )

            eid, e_title, e_content, e_mood, e_created, e_updated = entry

            title_tf = ft.TextField(
                value=e_title or "",
                hint_text="Entry title (leave blank for auto-title)",
                bgcolor=INPUT_BG,
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
            )

            content_tf = ft.TextField(
                value=e_content or "",
                hint_text="Write anything here…",
                multiline=True,
                min_lines=10,
                max_lines=999,
                bgcolor=INPUT_BG,
                filled=True,
                border_color=C("BORDER_COLOR"),
                border_radius=12,
                color=C("TEXT_PRIMARY"),
                expand=True,
            )

            # Mood selector — row of pill buttons
            selected_mood_ref = {"value": e_mood or ""}

            mood_row_ref: dict = {"row": None}

            def build_mood_row():
                pills = []
                for label, emoji, color_hex in MOODS:
                    is_active = selected_mood_ref["value"] == label

                    def on_mood_click(ev, _label=label):
                        # Toggle off if clicking the already-selected mood
                        if selected_mood_ref["value"] == _label:
                            selected_mood_ref["value"] = ""
                        else:
                            selected_mood_ref["value"] = _label
                        # Rebuild just the mood row
                        if mood_row_ref["row"] and self._mounted(mood_row_ref["row"]):
                            mood_row_ref["row"].controls = build_mood_row()
                            mood_row_ref["row"].update()

                    pills.append(
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=999,
                            bgcolor=color_hex if is_active else CARD_BG,
                            border=ft.border.all(
                                2 if is_active else 1,
                                color_hex if is_active else C("BORDER_COLOR"),
                            ),
                            ink=True,
                            on_click=on_mood_click,
                            content=ft.Text(
                                f"{emoji}  {label}",
                                size=11,
                                color="white" if is_active else C("TEXT_PRIMARY"),
                                weight=ft.FontWeight.W_600,
                            ),
                        )
                    )
                return pills

            mood_row = ft.Row(spacing=8, wrap=True, controls=build_mood_row())
            mood_row_ref["row"] = mood_row

            # Timestamps
            created_label = ft.Text(
                f"Created  {self._fmt_dt(e_created)}",
                size=11,
                color=C("TEXT_SECONDARY"),
            )
            updated_label = ft.Text(
                f"Last saved  {self._fmt_dt(e_updated)}",
                size=11,
                color=C("TEXT_SECONDARY"),
            )

            def save(e):
                if not S.user or self._is_loading:
                    return
                self._is_loading = True
                try:
                    db.update_journal(
                        S.user["id"],
                        eid,
                        title_tf.value or "",
                        content_tf.value or "",
                        selected_mood_ref["value"],
                    )
                    self._snack(page, "Entry saved!", C("SUCCESS_COLOR"))
                    self._refresh_list(page)
                    # Refresh timestamp labels without rebuilding whole editor
                    now_str = datetime.now().strftime("%b %d, %Y  %I:%M %p")
                    updated_label.value = f"Last saved  {now_str}"
                    self._safe_update(updated_label)
                except Exception as ex:
                    self._snack(page, f"Save failed: {ex}", C("ERROR_COLOR"))
                finally:
                    self._is_loading = False

            def delete(e):
                confirm_delete(eid)

            return ft.Column(
                expand=True,
                spacing=14,
                controls=[
                    # Title row
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(expand=True, content=title_tf),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=C("ERROR_COLOR"),
                                tooltip="Delete entry",
                                on_click=delete,
                            ),
                        ],
                    ),
                    # Mood
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text("Mood", size=12, weight=ft.FontWeight.BOLD, color=C("TEXT_SECONDARY")),
                            mood_row,
                        ],
                    ),
                    ft.Divider(height=1, color=C("BORDER_COLOR")),
                    # Content — expand to fill remaining space
                    ft.Container(expand=True, content=content_tf),
                    ft.Divider(height=1, color=C("BORDER_COLOR")),
                    # Footer: timestamps + save button
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[created_label, updated_label],
                            ),
                            ft.ElevatedButton(
                                "Save",
                                icon=ft.Icons.SAVE_OUTLINED,
                                on_click=save,
                                bgcolor=C("BUTTON_COLOR"),
                                color="white",
                            ),
                        ],
                    ),
                ],
            )

        self._build_editor = build_editor

        # --------------------------------------------------
        # New entry action
        # --------------------------------------------------
        def new_entry(e):
            if not S.user or self._is_loading:
                return
            self._is_loading = True
            try:
                db.add_journal(S.user["id"], title="", content="", mood="")
                # Select the newest entry (first row after refresh, ordered by updated_at DESC)
                entries = db.get_journals_by_user(S.user["id"])
                if entries:
                    self._selected_id = entries[0][0]
            except Exception as ex:
                self._snack(page, f"Could not create entry: {ex}", S.colors.get("ERROR_COLOR", "#EF4444"))
            finally:
                self._is_loading = False
            self._refresh_all(page)

        # --------------------------------------------------
        # Search
        # --------------------------------------------------
        def on_search(ev):
            self._search_query = ev.control.value or ""
            self._refresh_list(page)

        if not self._search_tf:
            self._search_tf = ft.TextField(
                hint_text="Search entries…",
                prefix_icon=ft.Icons.SEARCH,
                bgcolor=INPUT_BG,
                filled=True,
                border_radius=14,
                border_color=C("BORDER_COLOR"),
                color=C("TEXT_PRIMARY"),
                content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
                on_change=on_search,
            )

        # --------------------------------------------------
        # Hosts — create once, swap content on refresh
        # --------------------------------------------------
        if not self._list_host:
            self._list_host = ft.Container(
                expand=True,
                padding=ft.padding.only(top=6),
                content=self._build_list(page),
            )
        else:
            self._list_host.content = self._build_list(page)

        if not self._editor_host:
            self._editor_host = ft.Container(
                expand=True,
                content=self._build_editor(page),
            )
        else:
            self._editor_host.content = self._build_editor(page)

        # --------------------------------------------------
        # Left panel
        # --------------------------------------------------
        left_panel = ft.Container(
            expand=True,
            bgcolor=S.colors.get("FORM_BG", "#FFFFFF"),
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
                            ft.Text("Journal", size=20, weight=ft.FontWeight.BOLD, color=C("TEXT_PRIMARY")),
                            ft.ElevatedButton(
                                "✦  New Entry",
                                on_click=new_entry,
                                bgcolor=C("BUTTON_COLOR"),
                                color="white",
                            ),
                        ],
                    ),
                    self._search_tf,
                    self._list_host,
                ],
            ),
        )

        # --------------------------------------------------
        # Right panel (editor)
        # --------------------------------------------------
        right_panel = ft.Container(
            expand=True,
            bgcolor=S.colors.get("FORM_BG", "#FFFFFF"),
            border_radius=18,
            border=ft.border.all(1, C("BORDER_COLOR")),
            padding=20,
            content=self._editor_host,
        )

        # --------------------------------------------------
        # Board
        # --------------------------------------------------
        return ft.Container(
            expand=True,
            bgcolor=S.colors.get("BG_COLOR", "#FFFFFF"),
            border_radius=18,
            border=ft.border.all(1, C("BORDER_COLOR")),
            padding=16,
            content=ft.Row(
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Container(expand=4, content=left_panel),
                    ft.Container(width=16),
                    ft.Container(width=1, bgcolor=C("BORDER_COLOR"), margin=ft.margin.symmetric(vertical=10)),
                    ft.Container(width=16),
                    ft.Container(expand=6, content=right_panel),
                ],
            ),
        )