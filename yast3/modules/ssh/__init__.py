"""SSH client configuration module package."""

from ...i18n import _
from ...module import Module

from .window import SSHWindow


class SSHClientModule(Module):
    window: SSHWindow | None = None

    def __init__(self):
        super().__init__(_("SSH Client"), ("network-server", "network"))

    def launch(self) -> None:
        """Launch the SSH client module window."""
        if self.window is None:
            self.window = SSHWindow()
            self.window.setWindowTitle(self.name + ' — ' + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ['SSHClientModule']