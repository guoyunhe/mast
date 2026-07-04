from yast3.core.distro import read_os_release
from yast3.core.repositories.repos import RepoEntry

os_release = read_os_release()

distro = os_release.get("PRETTY_NAME", "openSUSE Tumbleweed").replace(" ", "_")

third_party_repos = [
    # http://packman.links2linux.org/
    RepoEntry(
        filename="packman.repo",
        id="packman",
        name="Packman",
        enabled=True,
        autorefresh=True,
        baseurl=f"http://ftp.gwdg.de/pub/linux/misc/packman/suse/{distro}/",
        gpgkey=f"http://ftp.gwdg.de/pub/linux/misc/packman/suse/{distro}/repodata/repomd.xml.key",
        gpgcheck=True,
        priority=70, # opi project recommends 70 for packman repo
    ),
    RepoEntry(
        filename="nvidia.repo",
        id="nvidia",
        name="NVIDIA",
        enabled=True,
        autorefresh=True,
        baseurl=f"http://download.nvidia.com/opensuse/{distro.replace("_", "/").lower()}/",
        gpgkey=f"http://download.nvidia.com/opensuse/{distro.replace("_", "/").lower()}/repodata/repomd.xml.key",
        gpgcheck=True,
        priority=120,
    ),
]