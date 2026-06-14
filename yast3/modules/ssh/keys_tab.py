"""Keys tab component for the SSH module."""

from __future__ import annotations

import os
import stat

from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import (
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from yast3.i18n import _
from yast3.modules.ssh.ssh import SSH_CONFIG_DIR


class KeyPair:
    """Represents an SSH key pair (private + public key)."""
    def __init__(self, name: str):
        self.name = name
        self.private_path = os.path.join(SSH_CONFIG_DIR, name)
        self.public_path = os.path.join(SSH_CONFIG_DIR, name + '.pub')
        self.has_private = os.path.exists(self.private_path)
        self.has_public = os.path.exists(self.public_path)
        self.key_type = self._detect_type()
        self.size = self._get_size()
        self.permissions = self._get_permissions()

    def _detect_type(self) -> str:
        """Detect key type from public or private key file."""
        # Try public key first
        if self.has_public:
            return self._detect_key_type(self.public_path)
        # Fall back to private key
        if self.has_private:
            return self._detect_key_type(self.private_path)
        return 'Unknown'

    def _detect_key_type(self, filepath: str) -> str:
        """Detect SSH key type from file content."""
        try:
            with open(filepath, 'r') as f:
                first_line = f.readline().strip()
            
            if first_line.startswith('-----BEGIN RSA PRIVATE KEY-----'):
                return 'RSA'
            elif first_line.startswith('-----BEGIN DSA PRIVATE KEY-----'):
                return 'DSA'
            elif first_line.startswith('-----BEGIN EC PRIVATE KEY-----'):
                return 'EC'
            elif first_line.startswith('-----BEGIN OPENSSH PRIVATE KEY-----'):
                return 'OpenSSH'
            elif first_line.startswith('ssh-rsa '):
                return 'RSA'
            elif first_line.startswith('ssh-dss '):
                return 'DSA'
            elif first_line.startswith('ecdsa-sha2-'):
                return 'EC'
            elif first_line.startswith('ssh-ed25519 '):
                return 'Ed25519'
            else:
                return 'Unknown'
        except Exception:
            return 'Unknown'

    def _get_size(self) -> str:
        """Get key size information."""
        if self.has_public:
            try:
                file_stat = os.stat(self.public_path)
                return f"{file_stat.st_size} bytes"
            except Exception:
                pass
        if self.has_private:
            try:
                file_stat = os.stat(self.private_path)
                return f"{file_stat.st_size} bytes"
            except Exception:
                pass
        return "N/A"

    def _get_permissions(self) -> str:
        """Get file permissions."""
        if self.has_private:
            try:
                file_stat = os.stat(self.private_path)
                return stat.filemode(file_stat.st_mode)
            except Exception:
                pass
        if self.has_public:
            try:
                file_stat = os.stat(self.public_path)
                return stat.filemode(file_stat.st_mode)
            except Exception:
                pass
        return "???"

    def get_public_key_content(self) -> str | None:
        """Get the content of the public key file."""
        if self.has_public:
            try:
                with open(self.public_path, 'r') as f:
                    return f.read().strip()
            except Exception:
                return None
        return None


class KeysTab(QWidget):
    """Keys tab for displaying SSH key files."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()
        self.load_keys()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Button bar
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton(_("Refresh"))
        self.refresh_btn.clicked.connect(self.load_keys)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Keys table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            _("Name"), _("Type"), _("Size"), _("Permissions"), _("Actions")
        ])
        
        # Column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 180)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 100)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 120)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

    def load_keys(self) -> None:
        """Load SSH keys from ~/.ssh/ directory."""
        self.table.setRowCount(0)

        try:
            files = os.listdir(SSH_CONFIG_DIR)
        except FileNotFoundError:
            QMessageBox.warning(self, _("Error"), _("{0} directory not found.").format(SSH_CONFIG_DIR))
            return
        except PermissionError:
            QMessageBox.warning(self, _("Error"), _("Cannot read {0} directory.").format(SSH_CONFIG_DIR))
            return

        # Find private key files (without .pub extension)
        private_keys = set()
        for filename in files:
            filepath = os.path.join(SSH_CONFIG_DIR, filename)
            if os.path.isdir(filepath) or filename in ('known_hosts', 'config', 'authorized_keys'):
                continue
            
            # Skip public key files - we'll match them with their private keys
            if filename.endswith('.pub'):
                continue
            
            # Check if it looks like a key file
            if filename.endswith(('_rsa', '_dsa', '_ecdsa', '_ed25519')) or \
               filename.startswith('id_'):
                private_keys.add(filename)

        # Also check for .pub files that might not have corresponding private keys
        public_keys = set()
        for filename in files:
            if filename.endswith('.pub'):
                base_name = filename[:-4]  # Remove .pub
                filepath = os.path.join(SSH_CONFIG_DIR, filename)
                if os.path.isfile(filepath) and base_name not in private_keys:
                    public_keys.add(base_name)

        # Combine and create key pairs
        all_keys = sorted(private_keys.union(public_keys))
        key_pairs = [KeyPair(name) for name in all_keys]

        # Populate table
        self.table.setRowCount(len(key_pairs))
        for row, key_pair in enumerate(key_pairs):
            # Name with status icons
            status_text = key_pair.name
            if key_pair.has_private and key_pair.has_public:
                status_text += " ✓✓"
            elif key_pair.has_private:
                status_text += " (priv)"
            elif key_pair.has_public:
                status_text += " (pub)"
            
            self.table.setItem(row, 0, QTableWidgetItem(status_text))
            self.table.setItem(row, 1, QTableWidgetItem(key_pair.key_type))
            self.table.setItem(row, 2, QTableWidgetItem(key_pair.size))
            self.table.setItem(row, 3, QTableWidgetItem(key_pair.permissions))

            # Actions - copy public key button
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            copy_btn = QPushButton(_("Copy Public Key"))
            copy_btn.setStyleSheet("""
                QPushButton {
                    padding: 4px 12px;
                    font-size: 12px;
                }
            """)
            copy_btn.clicked.connect(lambda checked, kp=key_pair: self.copy_public_key(kp))
            copy_btn.setEnabled(key_pair.has_public)
            action_layout.addWidget(copy_btn)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            self.table.setCellWidget(row, 4, action_widget)

    def copy_public_key(self, key_pair: KeyPair) -> None:
        """Copy public key content to clipboard."""
        content = key_pair.get_public_key_content()
        if content:
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            QMessageBox.information(self, _("Success"), _("Public key copied to clipboard."))
        else:
            QMessageBox.warning(self, _("Error"), _("Cannot read public key file."))