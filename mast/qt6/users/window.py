"""UI components for the Users & Groups module (Qt6)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _
from mast.qt6.users.user_manager import UserManager
from mast.qt6.users.group_manager import GroupManager


class UsersWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()

        self.resize(960, 640)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.users_tab = UserManager()
        self.tab_widget.addTab(self.users_tab, _("Users"))

        self.groups_tab = GroupManager()
        self.tab_widget.addTab(self.groups_tab, _("Groups"))

        self.users_tab.user_changed.connect(self._on_user_changed)
        self.groups_tab.group_changed.connect(self._on_group_changed)

    def closeEvent(self, _event) -> None:
        self.closed.emit()
        self.deleteLater()

    def _on_user_changed(self) -> None:
        self.groups_tab._load_data()

    def _on_group_changed(self) -> None:
        self.users_tab._load_data()