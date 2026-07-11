"""UI components for the Snapshots module (TUI)."""

from __future__ import annotations

import subprocess

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Static

from yast3.core.i18n import _
from yast3.core.snapshots import (
    SnapshotEntry,
    build_snapshot_create_command,
    build_snapshot_delete_command,
    list_snapshots,
)


class SnapshotsWindow(Screen):
    """TUI window for managing snapper snapshots."""

    CSS = """
    Screen {
        height: 100%;
    }

    .action-row {
        height: 3;
        padding-left: 1;
        padding-right: 1;
        margin-bottom: 1;
    }

    .message {
        height: 3;
        padding-left: 1;
        color: yellow;
    }

    .error {
        color: red;
    }

    .success {
        color: green;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
        ("r", "reload", "Refresh"),
        ("c", "create_snapshot", "Create"),
        ("d", "delete_snapshot", "Delete"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.snapshots: list[SnapshotEntry] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(classes="action-row"):
            yield Input(placeholder=_("Snapshot description"), id="description-input")
            yield Button(_("Create"), id="create-btn")
            yield Button(_("Delete"), id="delete-btn")
            yield Button(_("Refresh"), id="refresh-btn")

        yield DataTable(id="snapshots-table")
        yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        table = self.query_one("#snapshots-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(
            _("Number"),
            _("Type"),
            _("Date"),
            _("User"),
            _("Description"),
            _("Cleanup"),
        )

        self.load_snapshots()

    def show_message(self, message: str, error: bool = False, success: bool = False) -> None:
        msg_widget = self.query_one("#message", Static)
        msg_widget.update(message)
        msg_widget.remove_class("error", "success")
        if error:
            msg_widget.add_class("error")
        elif success:
            msg_widget.add_class("success")

    def load_snapshots(self) -> None:
        try:
            self.snapshots = list_snapshots()
            self.populate_table()
        except Exception as error:
            self.show_message(
                _("Error: Failed to load snapshots: {0}").format(str(error)),
                error=True,
            )

    def populate_table(self) -> None:
        table = self.query_one("#snapshots-table", DataTable)
        table.clear()

        for snapshot in self.snapshots:
            table.add_row(
                str(snapshot.number),
                snapshot.snapshot_type,
                snapshot.date,
                snapshot.user,
                snapshot.description,
                snapshot.cleanup,
            )

        self.update_action_buttons()

    def selected_snapshot(self) -> SnapshotEntry | None:
        table = self.query_one("#snapshots-table", DataTable)
        row = table.cursor_row
        if row < 0 or row >= len(self.snapshots):
            return None
        return self.snapshots[row]

    def update_action_buttons(self) -> None:
        self.query_one("#delete-btn", Button).disabled = self.selected_snapshot() is None

    def on_data_table_row_highlighted(self, _event: DataTable.RowHighlighted) -> None:
        self.update_action_buttons()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "create-btn":
            self.action_create_snapshot()
        elif button_id == "delete-btn":
            self.action_delete_snapshot()
        elif button_id == "refresh-btn":
            self.action_reload()

    def action_reload(self) -> None:
        self.load_snapshots()

    def action_create_snapshot(self) -> None:
        description_input = self.query_one("#description-input", Input)
        description = description_input.value.strip()
        if not description:
            self.show_message(_("Description cannot be empty."), error=True)
            return

        command = build_snapshot_create_command(description)
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except Exception as error:
            self.show_message(
                _("Error: Failed to execute command: {0}").format(str(error)),
                error=True,
            )
            return

        if result.returncode == 0:
            description_input.value = ""
            self.show_message(_("Snapshot created successfully."), success=True)
            self.load_snapshots()
            return

        error_text = (result.stdout or result.stderr or _("Unknown error")).strip()
        self.show_message(error_text, error=True)

    def action_delete_snapshot(self) -> None:
        snapshot = self.selected_snapshot()
        if snapshot is None:
            self.show_message(_("Please select a snapshot."), error=True)
            return

        command = build_snapshot_delete_command(snapshot.number)
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except Exception as error:
            self.show_message(
                _("Error: Failed to execute command: {0}").format(str(error)),
                error=True,
            )
            return

        if result.returncode == 0:
            self.show_message(
                _("Snapshot #{0} deleted successfully.").format(snapshot.number),
                success=True,
            )
            self.load_snapshots()
            return

        error_text = (result.stdout or result.stderr or _("Unknown error")).strip()
        self.show_message(error_text, error=True)
