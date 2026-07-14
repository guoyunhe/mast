"""About dialog for YaST3 GTK4 application."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core import GITHUB_URL, __version__, get_license_text
from yast3.core.i18n import _


def show_about_dialog(parent: Gtk.Window) -> None:
    license_text = get_license_text()

    dialog = Gtk.AboutDialog(
        transient_for=parent,
        modal=True,
        program_name="YaST3",
        version=__version__,
        website=GITHUB_URL,
        website_label=_("GitHub"),
        license=license_text,
    )
    dialog.present()