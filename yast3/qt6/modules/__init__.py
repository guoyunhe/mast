"""Qt6 module packages for YaST3 settings sections."""

from yast3.qt6.modules.cron import CronModule
from yast3.qt6.modules.git import GitModule
from yast3.qt6.modules.hostname import HostnameModule
from yast3.qt6.modules.hosts import HostsModule
from yast3.qt6.modules.packages import PackagesModule
from yast3.qt6.modules.repositories import RepositoriesModule
from yast3.qt6.ssh import SSHClientModule

__all__ = [
    "CronModule",
    "GitModule",
    "HostnameModule",
    "HostsModule",
    "PackagesModule",
    "RepositoriesModule",
    "SSHClientModule",
]