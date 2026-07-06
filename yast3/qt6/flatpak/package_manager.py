"""Qt6 Flatpak package management widget."""

from __future__ import annotations

from typing import Literal, cast

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
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
    list_flatpak_remotes,
)
from yast3.core.i18n import _
from yast3.qt6.command.action import CommandAction


class FlatpakPackageManager(QWidget):
    """Manage Flatpak application packages."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.packages: list[FlatpakPackage] = []

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.app_id_input = QLineEdit()
        self.app_id_input.setPlaceholderText("org.example.App")
        form.addRow(_("App ID"), self.app_id_input)

        self.remote_combo = QComboBox()
        self.remote_combo.setEditable(True)
        self.remote_combo.addItem("flathub")
        form.addRow(_("Remote"), self.remote_combo)

        self.scope_combo = QComboBox()
        self.scope_combo.addItem(_("System"), "system")
        self.scope_combo.addItem(_("User"), "user")
        form.addRow(_("Scope"), self.scope_combo)

        layout.addLayout(form)

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

        hint = QLabel(_("Tip: select an installed package row to quickly remove it."))
        layout.addWidget(hint)

        self._sync_action_buttons()
        self.refresh()

    def refresh(self) -> None:
        self.load_remotes()
        self.load_packages()

    def _sync_action_buttons(self) -> None:
        self.install_btn.setText(self.install_action.text())
        self.install_btn.setEnabled(self.install_action.isEnabled())
        self.uninstall_btn.setText(self.uninstall_action.text())
        self.uninstall_btn.setEnabled(self.uninstall_action.isEnabled())

    def _current_scope(self) -> Literal["system", "user"]:
        value = str(self.scope_combo.currentData())
        return cast(Literal["system", "user"], "user" if value == "user" else "system")

    def _current_remote(self) -> str:
        return self.remote_combo.currentText().strip()

    def _current_app_id(self) -> str:
        return self.app_id_input.text().strip()

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
        app_id = self._current_app_id()
        remote = self._current_remote()
        scope = self._current_scope()

        if not app_id:
            QMessageBox.information(self, _("Information"), _("Please input a Flatpak app ID."))
            return
        if not remote:
            QMessageBox.information(self, _("Information"), _("Please input a Flatpak remote."))
            return

        self.install_action.command = self._build_install_command(app_id, remote, scope)
        self.install_action.start_action()

    def _on_uninstall_triggered(self) -> None:
        app_id = self._current_app_id()
        scope = self._current_scope()
        if not app_id:
            QMessageBox.information(self, _("Information"), _("Please select or input a Flatpak app ID."))
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
            self.load_packages()
            return

        if error:
            QMessageBox.critical(self, _("Error"), _("Failed to install package: {0}").format(error))

    def _on_uninstall_finished(self, success: bool, error: str) -> None:
        if success:
            self.load_packages()
            return

        if error:
            QMessageBox.critical(self, _("Error"), _("Failed to remove package: {0}").format(error))

    def _on_package_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.packages):
            return

        pkg = self.packages[row]
        self.app_id_input.setText(pkg.app_id)

        remote_index = self.remote_combo.findText(pkg.remote)
        if remote_index >= 0:
            self.remote_combo.setCurrentIndex(remote_index)
        elif pkg.remote:
            self.remote_combo.addItem(pkg.remote)
            self.remote_combo.setCurrentIndex(self.remote_combo.count() - 1)

        scope_index = self.scope_combo.findData(pkg.scope)
        if scope_index >= 0:
            self.scope_combo.setCurrentIndex(scope_index)

    def load_remotes(self) -> None:
        current = self._current_remote()
        self.remote_combo.blockSignals(True)
        self.remote_combo.clear()

        names = ["flathub"]
        try:
            remotes = list_flatpak_remotes()
            for remote in remotes:
                if remote.name not in names:
                    names.append(remote.name)
        except Exception:
            # Keep a default option even if remote listing fails.
            pass

        for name in names:
            self.remote_combo.addItem(name)

        if current:
            idx = self.remote_combo.findText(current)
            if idx >= 0:
                self.remote_combo.setCurrentIndex(idx)
            else:
                self.remote_combo.addItem(current)
                self.remote_combo.setCurrentIndex(self.remote_combo.count() - 1)

        self.remote_combo.blockSignals(False)

    def load_packages(self) -> None:
        try:
            self.packages = list_flatpak_packages()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to load Flatpak packages: {0}").format(str(e)))
            self.packages = []

        self.table.setRowCount(len(self.packages))
        for row, package in enumerate(self.packages):
            self.table.setItem(row, 0, QTableWidgetItem(package.app_id))
            self.table.setItem(row, 1, QTableWidgetItem(package.remote))
            self.table.setItem(row, 2, QTableWidgetItem(package.scope))
