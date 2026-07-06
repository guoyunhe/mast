"""Flatpak package management core logic."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal


@dataclass
class FlatpakPackage:
    """Represents an installed Flatpak application."""

    app_id: str
    remote: str
    scope: Literal["system", "user"] = "system"


def list_flatpak_packages() -> list[FlatpakPackage]:
    """List installed Flatpak applications."""
    if not _is_flatpak_installed():
        return []

    result = _run_command(["flatpak", "list", "--app", "--columns=application,origin,installation"])

    packages: list[FlatpakPackage] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 1:
            continue

        app_id = parts[0].strip()
        remote = parts[1].strip() if len(parts) > 1 else ""
        installation = parts[2].strip().lower() if len(parts) > 2 else "system"
        scope: Literal["system", "user"] = "user" if "user" in installation else "system"

        if app_id:
            packages.append(FlatpakPackage(app_id=app_id, remote=remote, scope=scope))

    return packages


def search_flatpak_packages(query: str, remote: str = "flathub") -> list[str]:
    """Search application IDs from a Flatpak remote."""
    normalized_query = query.strip().lower()
    normalized_remote = remote.strip()
    if not normalized_query:
        raise ValueError("Search query is required.")
    if not normalized_remote:
        raise ValueError("Flatpak remote is required.")
    app_ids = list_remote_flatpak_packages(normalized_remote)
    return [app_id for app_id in app_ids if normalized_query in app_id.lower()]


def list_remote_flatpak_packages(remote: str = "flathub") -> list[str]:
    """List all application IDs from a Flatpak remote."""
    normalized_remote = remote.strip()
    if not normalized_remote:
        raise ValueError("Flatpak remote is required.")
    if not _is_flatpak_installed():
        return []

    result = _run_command(["flatpak", "remote-ls", "--app", "--columns=application", normalized_remote])

    app_ids: list[str] = []
    seen: set[str] = set()
    for raw_line in result.stdout.splitlines():
        app_id = raw_line.strip()
        if not app_id or app_id in seen:
            continue

        seen.add(app_id)
        app_ids.append(app_id)

    return app_ids


def install_flatpak_package(
    app_id: str,
    remote: str = "flathub",
    scope: Literal["system", "user"] = "system",
) -> None:
    """Install a Flatpak application from a remote."""
    normalized_app = app_id.strip()
    normalized_remote = remote.strip()
    if not normalized_app:
        raise ValueError("Flatpak app id is required.")
    if not normalized_remote:
        raise ValueError("Flatpak remote is required.")

    args = ["flatpak", "install", "-y", f"--{scope}", normalized_remote, normalized_app]
    _run_command(args, use_pkexec=scope == "system")


def uninstall_flatpak_package(app_id: str, scope: Literal["system", "user"] = "system") -> None:
    """Uninstall a Flatpak application."""
    normalized_app = app_id.strip()
    if not normalized_app:
        raise ValueError("Flatpak app id is required.")

    args = ["flatpak", "uninstall", "-y", f"--{scope}", normalized_app]
    _run_command(args, use_pkexec=scope == "system")


def _run_command(args: list[str], use_pkexec: bool = False) -> subprocess.CompletedProcess[str]:
    command = ["pkexec", *args] if use_pkexec else args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(error)
    return result


def _is_flatpak_installed() -> bool:
    return shutil.which("flatpak") is not None
