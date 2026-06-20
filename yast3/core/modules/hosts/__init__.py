"""Hosts file management core logic."""

from yast3.core.modules.hosts.hosts import (
    HostEntry,
    load_hosts,
    save_hosts,
)

__all__ = [
    "HostEntry",
    "load_hosts",
    "save_hosts",
]