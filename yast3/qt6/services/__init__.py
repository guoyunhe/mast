"""Services module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.qt6.services.window import ServicesWindow


class ServicesModule(Module):
    window: ServicesWindow | None = None

    def __init__(self):
        super().__init__(_("Services"), ("preferences-system-services", "system-run"), "🧰")

    def launch(self) -> None:
        """Launch the services module window."""
        if self.window is None:
            self.window = ServicesWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["ServicesModule"]