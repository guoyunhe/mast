"""Compatibility exports for Flatpak core helpers."""

import shutil
import subprocess

from yast3.core.flatpak.package import (
    FlatpakPackage,
    install_flatpak_package,
    list_flatpak_packages,
    uninstall_flatpak_package,
)
from yast3.core.flatpak.remote import (
    FlatpakRemote,
    add_flatpak_remote,
    delete_flatpak_remote,
    list_flatpak_remotes,
    modify_flatpak_remote_url,
)


def is_flatpak_installed() -> bool:
    """Check whether the flatpak executable is available."""
    return shutil.which("flatpak") is not None


def install_flatpak_pkexec() -> None:
    """Install Flatpak using zypper with root permissions."""
    _run_command(["zypper", "--non-interactive", "install", "-y", "flatpak"], use_pkexec=True)


def remove_flatpak_pkexec() -> None:
    """Remove Flatpak using zypper with root permissions."""
    _run_command(["zypper", "--non-interactive", "remove", "-y", "flatpak"], use_pkexec=True)


def _run_command(args: list[str], use_pkexec: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["pkexec", *args] if use_pkexec else args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(error)
    return result

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
    "uninstall_flatpak_package",
]
