"""Qt6 Flatpak package management widget."""

from __future__ import annotations

from typing import Literal

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from yast3.core.flatpak import (
    FlatpakPackage,
    list_flatpak_packages,
    search_flatpak_packages,
)
from yast3.core.i18n import _
from yast3.qt6.command.action import CommandAction


class FlatpakPackageManager(QWidget):
    """Manage Flatpak application packages."""

    DEFAULT_REMOTE = "flathub"
    DEFAULT_SCOPE: Literal["system", "user"] = "system"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.packages: list[FlatpakPackage] = []
        self.showing_search_results = False

        layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("org.example")
        self.search_input.returnPressed.connect(self.search)

        self.search_btn = QPushButton(_("Search"))
        self.search_btn.clicked.connect(self.search)

        self.reset_btn = QPushButton(_("Reset"))
        self.reset_btn.clicked.connect(self.reset_search)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_btn)
        search_row.addWidget(self.reset_btn)
        layout.addLayout(search_row)

        btn_layout = QHBoxLayout()
        self.install_action = CommandAction(
            text=_("Install Package"),
            running_text=_("Installing package..."),
            dialog_title=_("Install Flatpak Package"),
            command=["true"],
            success_output=_("Package installed successfully."),
            auto_close_on_success=True,
            parent=self,
        )
        self.install_action.triggered.disconnect(self.install_action.start_action)
        self.install_action.triggered.connect(self._on_install_triggered)
        self.install_action.action_finished.connect(self._on_install_finished)

        self.uninstall_action = CommandAction(
            text=_("Remove Package"),
            running_text=_("Removing package..."),
            dialog_title=_("Remove Flatpak Package"),
            command=["true"],
            success_output=_("Package removed successfully."),
            auto_close_on_success=True,
            parent=self,
        )
        self.uninstall_action.triggered.disconnect(self.uninstall_action.start_action)
        self.uninstall_action.triggered.connect(self._on_uninstall_triggered)
        self.uninstall_action.action_finished.connect(self._on_uninstall_finished)

        self.install_btn = QPushButton(self.install_action.text())
        self.install_btn.clicked.connect(self.install_action.trigger)
        self.install_action.changed.connect(self._sync_action_buttons)
        btn_layout.addWidget(self.install_btn)

        self.uninstall_btn = QPushButton(self.uninstall_action.text())
        self.uninstall_btn.clicked.connect(self.uninstall_action.trigger)
        self.uninstall_action.changed.connect(self._sync_action_buttons)
        btn_layout.addWidget(self.uninstall_btn)

        self.refresh_btn = QPushButton(_("Refresh"))
        self.refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([_("App ID"), _("Remote"), _("Scope")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 90)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_package_selected)
        layout.addWidget(self.table)

        self._sync_action_buttons()
        self.refresh()

    def refresh(self) -> None:
        self.load_packages()

    def _sync_action_buttons(self) -> None:
        self.install_btn.setText(self.install_action.text())
        self.install_btn.setEnabled(self.install_action.isEnabled())
        self.uninstall_btn.setText(self.uninstall_action.text())
        can_uninstall = self.uninstall_action.isEnabled() and not self.showing_search_results
        self.uninstall_btn.setEnabled(can_uninstall)

    def _selected_app_id(self) -> str:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.packages):
            return ""
        return self.packages[row].app_id

    def _selected_remote(self) -> str:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.packages):
            return self.DEFAULT_REMOTE
        remote = self.packages[row].remote.strip()
        return remote or self.DEFAULT_REMOTE

    def _selected_scope(self) -> Literal["system", "user"]:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.packages):
            return self.DEFAULT_SCOPE
        return self.packages[row].scope

    def _build_install_command(self, app_id: str, remote: str, scope: Literal["system", "user"]) -> list[str]:
        base = ["flatpak", "install", "-y", f"--{scope}", remote, app_id]
        if scope == "system":
            return ["pkexec", *base]
        return base

    def _build_uninstall_command(self, app_id: str, scope: Literal["system", "user"]) -> list[str]:
        base = ["flatpak", "uninstall", "-y", f"--{scope}", app_id]
        if scope == "system":
            return ["pkexec", *base]
        return base

    def _on_install_triggered(self) -> None:
        app_id = self._selected_app_id()
        remote = self._selected_remote()
        scope = self._selected_scope()

        if not app_id:
            QMessageBox.information(self, _("Information"), _("Please select a package from the list to install."))
            return

        self.install_action.command = self._build_install_command(app_id, remote, scope)
        self.install_action.start_action()

    def _on_uninstall_triggered(self) -> None:
        if self.showing_search_results:
            QMessageBox.information(
                self,
                _("Information"),
                _("Uninstall is only available in installed list mode. Click Refresh first."),
            )
            return

        app_id = self._selected_app_id()
        scope = self._selected_scope()
        if not app_id:
            QMessageBox.information(self, _("Information"), _("Please select an installed package from the list."))
            return

        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to remove package '{0}'?").format(app_id),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.uninstall_action.command = self._build_uninstall_command(app_id, scope)
        self.uninstall_action.start_action()

    def _on_install_finished(self, success: bool, error: str) -> None:
        if success:
            self.refresh()
            return

        if error:
            QMessageBox.critical(self, _("Error"), _("Failed to install package: {0}").format(error))

    def _on_uninstall_finished(self, success: bool, error: str) -> None:
        if success:
            self.refresh()
            return

        if error:
            QMessageBox.critical(self, _("Error"), _("Failed to remove package: {0}").format(error))

    def _on_package_selected(self) -> None:
        return

    def search(self) -> None:
        query = self.search_input.text().strip()
        remote = self.DEFAULT_REMOTE
        scope = self.DEFAULT_SCOPE

        if not query:
            QMessageBox.information(self, _("Information"), _("Please input a search keyword."))
            return

        try:
            app_ids = search_flatpak_packages(query, remote)
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to search packages: {0}").format(str(e)))
            return

        self.showing_search_results = True
        self.packages = [FlatpakPackage(app_id=app_id, remote=remote, scope=scope) for app_id in app_ids]
        self._populate_table()
        self._sync_action_buttons()

        if not app_ids:
            QMessageBox.information(self, _("Information"), _("No packages found."))

    def reset_search(self) -> None:
        self.search_input.clear()
        self.refresh()

    def load_packages(self) -> None:
        try:
            self.packages = list_flatpak_packages()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to load Flatpak packages: {0}").format(str(e)))
            self.packages = []

        self.showing_search_results = False
        self._populate_table()
        self._sync_action_buttons()

    def _populate_table(self) -> None:
        self.table.setRowCount(len(self.packages))
        for row, package in enumerate(self.packages):
            self.table.setItem(row, 0, QTableWidgetItem(package.app_id))
            self.table.setItem(row, 1, QTableWidgetItem(package.remote))
            self.table.setItem(row, 2, QTableWidgetItem(package.scope))
