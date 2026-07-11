"""Snapshots module package - Qt6 GUI."""

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.qt6.snapshots.window import SnapshotsWindow


class SnapshotsModule(Module):
    window: SnapshotsWindow | None = None

    def __init__(self):
        super().__init__(_("Snapshots"), ("camera-photo", "document-save"), "📸")

    def launch(self) -> None:
        """Launch the snapshots module window."""
        if self.window is None:
            self.window = SnapshotsWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["SnapshotsModule"]
