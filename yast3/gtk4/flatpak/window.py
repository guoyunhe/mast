"""UI components for the Flatpak module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.flatpak import (
    install_flatpak_pkexec,
    is_flatpak_installed,
)
from yast3.core.i18n import _
from yast3.gtk4.flatpak.package_manager import FlatpakPackageManager
from yast3.gtk4.flatpak.remote_manager import FlatpakRemoteManager
from yast3.gtk4.flatpak.runtime_manager import FlatpakRuntimeManager
from yast3.gtk4.flatpak.settings import FlatpakSettingsTab


class FlatpakWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(960, 520)
        self.set_title(_("{} — YaST3").format(_("Flatpak")))

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(12)
        self.main_box.set_margin_end(12)

        self.install_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        install_title = Gtk.Label(label=_("Flatpak is not installed"))
        install_title.set_halign(Gtk.Align.START)
        self.install_btn = Gtk.Button(label=_("Install Flatpak"))
        self.install_btn.add_css_class("suggested-action")
        self.install_btn.connect("clicked", self._on_install_clicked)
        self.install_box.append(install_title)
        self.install_box.append(self.install_btn)
        self.main_box.append(self.install_box)

        self.manage_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.notebook = Gtk.Notebook()
        self.package_search_manager = FlatpakPackageManager(FlatpakPackageManager.MODE_SEARCH, self)
        self.package_installed_manager = FlatpakPackageManager(FlatpakPackageManager.MODE_INSTALLED, self)
        self.runtime_manager = FlatpakRuntimeManager(self)
        self.remote_manager = FlatpakRemoteManager(self)
        self.settings_tab = FlatpakSettingsTab(self)

        self.notebook.append_page(self.package_search_manager, Gtk.Label(label=_("Search")))
        self.notebook.append_page(self.package_installed_manager, Gtk.Label(label=_("Installed")))
        self.notebook.append_page(self.runtime_manager, Gtk.Label(label=_("Runtimes")))
        self.notebook.append_page(self.remote_manager, Gtk.Label(label=_("Remotes")))
        self.notebook.append_page(self.settings_tab, Gtk.Label(label=_("Settings")))

        self.manage_box.append(self.notebook)

        self.main_box.append(self.manage_box)
        self.set_child(self.main_box)

        self._refresh_state()

    def _refresh_state(self) -> None:
        installed = is_flatpak_installed()
        if installed:
            self.install_box.set_visible(False)
            self.manage_box.set_visible(True)
            self.package_search_manager.refresh()
            self.package_installed_manager.refresh()
            self.runtime_manager.load_runtimes()
            self.remote_manager.load_remotes()
        else:
            self.manage_box.set_visible(False)
            self.install_box.set_visible(True)

    def _on_install_clicked(self, _button: Gtk.Button) -> None:
        try:
            install_flatpak_pkexec()
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Flatpak installed successfully."))
            self._refresh_state()
        except Exception as e:
            self._show_message_dialog(
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to install Flatpak: {0}").format(str(e)),
            )

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, _r: d.destroy())
        dialog.present()
