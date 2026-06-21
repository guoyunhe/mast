"""TUI module packages for YaST3 settings sections."""

from yast3.tui.modules.cron import CronModule
from yast3.tui.modules.git import GitModule
from yast3.tui.modules.hostname import HostnameModule
from yast3.tui.modules.hosts import HostsModule
from yast3.tui.modules.packages import PackagesModule
from yast3.tui.modules.repositories import RepositoriesModule
from yast3.tui.modules.ssh import SSHClientModule

__all__ = [
    "CronModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "PackagesModule",
    "RepositoriesModule",
    "SSHClientModule",
]