"""Flatpak management helpers."""

from yast3.core.flatpak.package import (
    FlatpakPackage,
    install_flatpak_package,
    list_flatpak_packages,
    search_flatpak_packages,
    uninstall_flatpak_package,
)
from yast3.core.flatpak.flatpak import (
    install_flatpak_pkexec,
    is_flatpak_installed,
    remove_flatpak_pkexec,
)
from yast3.core.flatpak.remote import (
    FlatpakRemote,
    add_flatpak_remote,
    delete_flatpak_remote,
    list_flatpak_remotes,
    modify_flatpak_remote_url,
)

__all__ = [
    "FlatpakPackage",
    "FlatpakRemote",
    "add_flatpak_remote",
    "delete_flatpak_remote",
    "install_flatpak_pkexec",
    "install_flatpak_package",
    "is_flatpak_installed",
    "list_flatpak_packages",
    "list_flatpak_remotes",
    "modify_flatpak_remote_url",
    "remove_flatpak_pkexec",
    "search_flatpak_packages",
    "uninstall_flatpak_package",
]
