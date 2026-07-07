"""GTK4 settings tab for Flatpak module."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.flatpak import remove_flatpak_pkexec
from yast3.core.i18n import _


class FlatpakSettingsTab(Gtk.Box):
    """Settings UI for dangerous Flatpak operations."""

    def __init__(self, parent_window: Gtk.ApplicationWindow, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.parent_window = parent_window

        self.append(Gtk.Box(vexpand=True))

        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bottom_row.set_halign(Gtk.Align.END)

        self.remove_btn = Gtk.Button(label=_("Remove Flatpak"))
        self.remove_btn.connect("clicked", self._on_remove_flatpak_clicked)
        bottom_row.append(self.remove_btn)

        self.append(bottom_row)

    def _on_remove_flatpak_clicked(self, _button: Gtk.Button) -> None:
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        confirm_dialog.set_property("secondary-text", _("Are you sure you want to remove Flatpak?"))
        confirm_dialog.connect("response", self._on_remove_confirm)
        confirm_dialog.present()

    def _on_remove_confirm(self, dialog: Gtk.MessageDialog, response_id: Gtk.ResponseType) -> None:
        dialog.destroy()
        if response_id != Gtk.ResponseType.YES:
            return

        try:
            remove_flatpak_pkexec()
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Flatpak removed successfully."))
            if hasattr(self.parent_window, "_refresh_state"):
                self.parent_window._refresh_state()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to remove Flatpak: {0}").format(str(e)),
            )

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
