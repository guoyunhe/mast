"""SSH Hosts module - Qt6 GUI."""

from yast3.qt6.modules.ssh.hosts.manager import HostManager
from yast3.qt6.modules.ssh.hosts.tab import HostsTab

__all__ = ["HostsTab", "HostManager"]