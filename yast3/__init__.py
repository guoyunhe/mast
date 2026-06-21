"""YaST3 - System configuration tool."""

# This package now serves as a namespace package that provides access to:
# - yast3.core: UI-independent core logic
# - yast3.qt6: Qt6 GUI application

import core
import qt6
import tui

__all__ = ["core", "qt6", "tui"]
