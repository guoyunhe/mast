"""GTK4 Flatpak runtime management widget."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.flatpak import FlatpakRuntime, list_flatpak_runtimes, uninstall_flatpak_runtime
from yast3.core.i18n import _


class FlatpakRuntimeManager(Gtk.Box):
    """Manage installed Flatpak runtimes."""

    PAGE_SIZE = 100

    def __init__(self, parent_window: Gtk.ApplicationWindow, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.parent_window = parent_window

        self.runtimes: list[FlatpakRuntime] = []
        self.filtered_runtimes: list[FlatpakRuntime] = []
        self.page = 0

        self._build_layout()
        self.load_runtimes()

    def _build_layout(self) -> None:
        search_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("org.example.Platform")
        self.search_entry.connect("activate", self._on_search_clicked)
        search_row.append(self.search_entry)

        self.search_btn = Gtk.Button(label=_("Search"))
        self.search_btn.connect("clicked", self._on_search_clicked)
        search_row.append(self.search_btn)

        self.reset_btn = Gtk.Button(label=_("Reset"))
        self.reset_btn.connect("clicked", self._on_reset_clicked)
        search_row.append(self.reset_btn)
        self.append(search_row)

        action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.remove_btn = Gtk.Button(label=_("Remove Runtime"))
        self.remove_btn.connect("clicked", self._on_remove_clicked)
        action_row.append(self.remove_btn)

        self.refresh_btn = Gtk.Button(label=_("Refresh Runtimes"))
        self.refresh_btn.connect("clicked", self._on_refresh_clicked)
        action_row.append(self.refresh_btn)
        action_row.append(Gtk.Box(hexpand=True))
        self.append(action_row)

        self.list_store = Gtk.ListStore(str, str, str, str, str, str, str)
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)
        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        for title, index in [
            (_("Runtime ID"), 0),
            (_("Name"), 1),
            (_("Description"), 2),
            (_("Version"), 3),
            (_("Branch"), 4),
            (_("Remote"), 5),
            (_("Scope"), 6),
        ]:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=index)
            column.set_resizable(True)
            self.tree_view.append_column(column)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.append(scrolled)

        pager_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.prev_btn = Gtk.Button(label=_("Prev"))
        self.prev_btn.connect("clicked", self._on_prev_clicked)
        pager_row.append(self.prev_btn)

        self.page_label = Gtk.Label(label="1/1")
        pager_row.append(self.page_label)

        self.next_btn = Gtk.Button(label=_("Next"))
        self.next_btn.connect("clicked", self._on_next_clicked)
        pager_row.append(self.next_btn)
        pager_row.append(Gtk.Box(hexpand=True))
        self.append(pager_row)

    def load_runtimes(self) -> None:
        try:
            self.runtimes = list_flatpak_runtimes()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to load Flatpak runtimes: {0}").format(str(e)),
            )
            self.runtimes = []

        self.filtered_runtimes = self._filter_runtimes(self.runtimes, self.search_entry.get_text().strip())
        self.page = 0
        self._populate_table()

    def _selected_runtime(self) -> FlatpakRuntime | None:
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            return None

        path = model.get_path(tree_iter)
        index = int(path.to_string())
        page_items = self._page_items()
        if 0 <= index < len(page_items):
            return page_items[index]
        return None

    def _on_remove_clicked(self, _button: Gtk.Button) -> None:
        runtime = self._selected_runtime()
        if runtime is None:
            self._show_message_dialog(
                Gtk.MessageType.INFO,
                _("Information"),
                _("Please select an installed runtime from the list."),
            )
            return

        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        confirm_dialog.set_property(
            "secondary-text",
            _("Are you sure you want to remove runtime '{0}'?").format(runtime.runtime_id),
        )
        confirm_dialog.connect("response", self._on_remove_confirm, runtime)
        confirm_dialog.present()

    def _on_remove_confirm(self, dialog: Gtk.MessageDialog, response_id: Gtk.ResponseType, runtime: FlatpakRuntime) -> None:
        dialog.destroy()
        if response_id != Gtk.ResponseType.YES:
            return

        try:
            uninstall_flatpak_runtime(runtime.runtime_id, runtime.scope)
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Runtime removed successfully."))
            self.load_runtimes()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to remove runtime: {0}").format(str(e)),
            )

    def _on_search_clicked(self, _widget) -> None:
        self.filtered_runtimes = self._filter_runtimes(self.runtimes, self.search_entry.get_text().strip())
        self.page = 0
        self._populate_table()

    def _on_reset_clicked(self, _button: Gtk.Button) -> None:
        self.search_entry.set_text("")
        self.filtered_runtimes = list(self.runtimes)
        self.page = 0
        self._populate_table()

    def _on_refresh_clicked(self, _button: Gtk.Button) -> None:
        self.load_runtimes()

    def _on_prev_clicked(self, _button: Gtk.Button) -> None:
        if self.page <= 0:
            return
        self.page -= 1
        self._populate_table()

    def _on_next_clicked(self, _button: Gtk.Button) -> None:
        total_pages = self._total_pages(len(self.filtered_runtimes))
        if self.page + 1 >= total_pages:
            return
        self.page += 1
        self._populate_table()

    def _page_items(self) -> list[FlatpakRuntime]:
        start = self.page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        return self.filtered_runtimes[start:end]

    def _populate_table(self) -> None:
        self.list_store.clear()
        for runtime in self._page_items():
            self.list_store.append(
                [
                    runtime.runtime_id,
                    runtime.name,
                    runtime.description,
                    runtime.version,
                    runtime.branch,
                    runtime.remote,
                    runtime.scope,
                ]
            )

        total_pages = self._total_pages(len(self.filtered_runtimes))
        self.page_label.set_text(f"{self.page + 1}/{total_pages}")
        self.prev_btn.set_sensitive(self.page > 0)
        self.next_btn.set_sensitive(self.page + 1 < total_pages)

    def _total_pages(self, total_rows: int) -> int:
        if total_rows <= 0:
            return 1
        return (total_rows + self.PAGE_SIZE - 1) // self.PAGE_SIZE

    def _filter_runtimes(self, runtimes: list[FlatpakRuntime], query: str) -> list[FlatpakRuntime]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            return list(runtimes)

        return [
            runtime
            for runtime in runtimes
            if normalized_query in runtime.runtime_id.lower()
            or normalized_query in runtime.name.lower()
            or normalized_query in runtime.description.lower()
            or normalized_query in runtime.version.lower()
            or normalized_query in runtime.branch.lower()
            or normalized_query in runtime.remote.lower()
        ]

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()
